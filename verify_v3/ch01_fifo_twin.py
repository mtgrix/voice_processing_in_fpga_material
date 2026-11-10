#!/usr/bin/env python3
"""verify_v3/ch01_fifo_twin.py
Cycle-accurate Python twin of rtl/v3/ch01_avalon_fifo.v and rtl/v3/ch01_fifo_out.v:
- AvalonFifoTwin: models 256 x 32-bit RAM FIFO with wrap-bit pointers,
  4-state unpacker FSM (ST_IDLE, ST_FETCH, ST_UNPACK0, ST_UNPACK1),
  Avalon-MM waitrequest, overflow sticky flag, and total samples fill level.
- FifoOutTwin: models 512 x 16-bit RAM return FIFO (ST sink -> MM read).
- Generates cycle-by-cycle stimulus and expected files for Verilog testbenches:
  * verify_v3/tb_ch01_fifo_stim.txt
  * verify_v3/tb_ch01_fifo_expected.txt
  * verify_v3/tb_ch01_fifo_out_stim.txt
  * verify_v3/tb_ch01_fifo_out_expected.txt
"""

import os
import random

class AvalonFifoTwin:
    def __init__(self, depth_words=256):
        self.depth_words = depth_words
        self.mem = [0] * depth_words
        self.wr_ptr = 0
        self.rd_ptr = 0
        self.ovf_sticky = 0

        # Unpacker FSM states
        self.ST_IDLE = 0
        self.ST_FETCH = 1
        self.ST_UNPACK0 = 2
        self.ST_UNPACK1 = 3
        self.st_state = self.ST_IDLE

        self.holding_word = 0
        self.mem_rdata = 0

    @property
    def words_used(self):
        return (self.wr_ptr - self.rd_ptr) & ((2 * self.depth_words) - 1)

    @property
    def fifo_empty(self):
        return self.wr_ptr == self.rd_ptr

    @property
    def fifo_full(self):
        return self.words_used == self.depth_words

    @property
    def waitrequest(self):
        return 1 if self.fifo_full else 0

    @property
    def unpacker_samples(self):
        if self.st_state == self.ST_UNPACK0:
            return 2
        elif self.st_state == self.ST_UNPACK1:
            return 1
        elif self.st_state == self.ST_FETCH:
            return 2
        return 0

    @property
    def fill_level_samples(self):
        return (self.words_used * 2) + self.unpacker_samples

    def step(self, mm_write, mm_writedata, st_ready):
        """Simulate one clock edge of rtl/v3/ch01_avalon_fifo.v.
        Returns (waitrequest, st_valid, st_data, state, fill_level) observed
        after the posedge clk update.
        """
        prev_fifo_empty = self.fifo_empty
        prev_fifo_full = self.fifo_full
        prev_rd_addr = self.rd_ptr & (self.depth_words - 1)
        prev_wr_addr = self.wr_ptr & (self.depth_words - 1)

        # 1. Next state of unpacker FSM
        next_state = self.st_state
        next_holding = self.holding_word
        inc_rd = False

        if self.st_state == self.ST_IDLE:
            if not prev_fifo_empty:
                next_state = self.ST_FETCH
                inc_rd = True
        elif self.st_state == self.ST_FETCH:
            next_holding = self.mem_rdata
            next_state = self.ST_UNPACK0
        elif self.st_state == self.ST_UNPACK0:
            if st_ready:
                next_state = self.ST_UNPACK1
        elif self.st_state == self.ST_UNPACK1:
            if st_ready:
                if not prev_fifo_empty:
                    next_state = self.ST_FETCH
                    inc_rd = True
                else:
                    next_state = self.ST_IDLE

        # 2. Synchronous RAM registered read
        next_mem_rdata = self.mem[prev_rd_addr]

        # 3. Synchronous RAM write
        if mm_write:
            if not prev_fifo_full:
                self.mem[prev_wr_addr] = mm_writedata & 0xFFFFFFFF
                self.wr_ptr = (self.wr_ptr + 1) & ((2 * self.depth_words) - 1)
            else:
                self.ovf_sticky = 1

        # 4. Advance unpacker registers
        if inc_rd:
            self.rd_ptr = (self.rd_ptr + 1) & ((2 * self.depth_words) - 1)
        self.st_state = next_state
        self.holding_word = next_holding
        self.mem_rdata = next_mem_rdata

        # 5. Output signals after clock edge
        st_valid = 1 if self.st_state in (self.ST_UNPACK0, self.ST_UNPACK1) else 0
        if self.st_state == self.ST_UNPACK0:
            st_data = self.holding_word & 0xFFFF
        elif self.st_state == self.ST_UNPACK1:
            st_data = (self.holding_word >> 16) & 0xFFFF
        else:
            st_data = 0
        waitrequest = 1 if self.fifo_full else 0
        fill = self.fill_level_samples
        state = self.st_state

        return waitrequest, st_valid, st_data, state, fill


class FifoOutTwin:
    def __init__(self, depth_words=512):
        self.depth_words = depth_words
        self.mem = [0] * depth_words
        self.wr_ptr = 0
        self.rd_ptr = 0
        self.rdata_reg = 0

    @property
    def words_used(self):
        return (self.wr_ptr - self.rd_ptr) & ((2 * self.depth_words) - 1)

    @property
    def fifo_empty(self):
        return self.wr_ptr == self.rd_ptr

    @property
    def fifo_full(self):
        return self.words_used == self.depth_words

    @property
    def st_ready(self):
        return 0 if self.fifo_full else 1

    def step(self, st_valid, st_data, mm_read):
        """Simulate one clock edge of rtl/v3/ch01_fifo_out.v."""
        ready_before = self.st_ready
        empty_before = self.fifo_empty
        mm_waitrequest_out = 1 if (mm_read and empty_before) else 0

        # Push to FIFO
        if st_valid and ready_before:
            wr_addr = self.wr_ptr & (self.depth_words - 1)
            self.mem[wr_addr] = st_data & 0xFFFF
            self.wr_ptr = (self.wr_ptr + 1) & ((2 * self.depth_words) - 1)

        # Pop from FIFO
        if mm_read and not empty_before:
            rd_addr = self.rd_ptr & (self.depth_words - 1)
            self.rdata_reg = self.mem[rd_addr]
            self.rd_ptr = (self.rd_ptr + 1) & ((2 * self.depth_words) - 1)

        # Visible signals after clock edge
        st_ready_out = self.st_ready
        mm_readdata_out = self.rdata_reg & 0xFFFF
        words_used_out = self.words_used

        return st_ready_out, mm_waitrequest_out, mm_readdata_out, words_used_out


def generate_fifo_in_test(seed=20261110):
    """Generate cycle-by-cycle stimulus and expected output for ch01_avalon_fifo."""
    random.seed(seed)
    twin = AvalonFifoTwin(depth_words=256)

    stim_list = []    # (mm_write, writedata, st_ready)
    trace_list = []   # (cycle, mm_write, writedata, waitrequest, st_valid, st_ready, st_data, state, fill)

    # 1. Phase 1: Directed 8-cycle sequence (write, fetch, unpack0 stall, unpack1, back-to-back word)
    directed = [
        (1, 0x00020001, 1), # 0: write word 0
        (0, 0x00000000, 1), # 1: idle, FSM IDLE -> FETCH
        (0, 0x00000000, 0), # 2: stall, FSM FETCH -> UNPACK0, st_data = 1
        (0, 0x00000000, 0), # 3: stall, FSM UNPACK0 stays, st_data = 1
        (1, 0x00040003, 1), # 4: back-to-back write, UNPACK0 -> UNPACK1, st_data = 2
        (0, 0x00000000, 1), # 5: UNPACK1 -> FETCH (direct fetch!)
        (0, 0x00000000, 1), # 6: FETCH -> UNPACK0, st_data = 3
        (0, 0x00000000, 1), # 7: UNPACK0 -> UNPACK1, st_data = 4
    ]

    for c, (w, wd, rdy) in enumerate(directed):
        wreq, vld, data, st, fill = twin.step(w, wd, rdy)
        stim_list.append((w, wd, rdy))
        trace_list.append((c, w, wd, wreq, vld, rdy, data, st, fill))

    # 2. Phase 2: Capacity saturation sequence (fill 256 words with st_ready=0)
    # We already have 0 words in RAM (both words 0 and 1 were unpacked).
    # Write 255 words:
    curr_c = len(stim_list)
    for i in range(255):
        wd = ((0x1000 + i*2 + 1) << 16) | (0x1000 + i*2)
        wreq, vld, data, st, fill = twin.step(1, wd, 0)
        stim_list.append((1, wd, 0))
        trace_list.append((curr_c, 1, wd, wreq, vld, 0, data, st, fill))
        curr_c += 1

    # Word 256: fills RAM to 256 words
    wd = 0x20012000
    wreq, vld, data, st, fill = twin.step(1, wd, 0)
    stim_list.append((1, wd, 0))
    trace_list.append((curr_c, 1, wd, wreq, vld, 0, data, st, fill))
    curr_c += 1

    # Overflow write attempt while waitrequest = 1
    wd = 0xDEADBEEF
    wreq, vld, data, st, fill = twin.step(1, wd, 0)
    stim_list.append((1, wd, 0))
    trace_list.append((curr_c, 1, wd, wreq, vld, 0, data, st, fill))
    curr_c += 1

    # Drain 10 words
    for _ in range(10):
        wreq, vld, data, st, fill = twin.step(0, 0, 1)
        stim_list.append((0, 0, 1))
        trace_list.append((curr_c, 0, 0, wreq, vld, 1, data, st, fill))
        curr_c += 1

    # 3. Phase 3: Pseudorandom stream of 250 words (500 samples)
    words_to_send = [(((i * 2 + 1) & 0xFFFF) << 16) | ((i * 2) & 0xFFFF) for i in range(250)]
    w_idx = 0
    while w_idx < len(words_to_send):
        do_write = (random.random() < 0.8)
        rdy = 1 if (random.random() < 0.6) else 0
        wd = words_to_send[w_idx] if do_write else 0

        # Note: waitrequest status before posedge tells if write will succeed
        full_before = twin.fifo_full
        wreq, vld, data, st, fill = twin.step(do_write, wd, rdy)
        if do_write and not full_before:
            w_idx += 1

        stim_list.append((1 if do_write else 0, wd, rdy))
        trace_list.append((curr_c, 1 if do_write else 0, wd, wreq, vld, rdy, data, st, fill))
        curr_c += 1

    # 4. Phase 4: Drain completely until empty
    while not twin.fifo_empty or twin.st_state != twin.ST_IDLE:
        wreq, vld, data, st, fill = twin.step(0, 0, 1)
        stim_list.append((0, 0, 1))
        trace_list.append((curr_c, 0, 0, wreq, vld, 1, data, st, fill))
        curr_c += 1

    return stim_list, trace_list


def generate_fifo_out_test(seed=20261110):
    """Generate cycle-by-cycle stimulus and expected output for ch01_fifo_out."""
    random.seed(seed + 1)
    twin = FifoOutTwin(depth_words=512)

    stim_list = []    # (st_valid, st_data, mm_read)
    trace_list = []   # (cycle, st_valid, st_data, mm_read, st_ready, mm_waitrequest, mm_readdata, words_used)

    # 1. Single push and pop
    # Cycle 0: push 0x0F01
    rdy, wreq, rdata, used = twin.step(1, 0x0F01, 0)
    stim_list.append((1, 0x0F01, 0))
    trace_list.append((0, 1, 0x0F01, 0, rdy, wreq, rdata, used))

    # Cycle 1: read it
    rdy, wreq, rdata, used = twin.step(0, 0, 1)
    stim_list.append((0, 0, 1))
    trace_list.append((1, 0, 0, 1, rdy, wreq, rdata, used))

    # Cycle 2: read while empty (waitrequest asserted)
    rdy, wreq, rdata, used = twin.step(0, 0, 1)
    stim_list.append((0, 0, 1))
    trace_list.append((2, 0, 0, 1, rdy, wreq, rdata, used))

    curr_c = 3
    # 2. Fill FIFO to capacity (512 words)
    for i in range(512):
        sdata = (0x1000 + i) & 0xFFFF
        rdy, wreq, rdata, used = twin.step(1, sdata, 0)
        stim_list.append((1, sdata, 0))
        trace_list.append((curr_c, 1, sdata, 0, rdy, wreq, rdata, used))
        curr_c += 1

    # Cycle: write while full (st_ready = 0)
    rdy, wreq, rdata, used = twin.step(1, 0xDEAD, 0)
    stim_list.append((1, 0xDEAD, 0))
    trace_list.append((curr_c, 1, 0xDEAD, 0, rdy, wreq, rdata, used))
    curr_c += 1

    # 3. Read out 300 words with random valid and read signals (>= 200 random vectors)
    for i in range(300):
        vld = 1 if (random.random() < 0.4) else 0
        sdata = (0x5000 + i) & 0xFFFF if vld else 0
        rd = 1 if (random.random() < 0.7) else 0
        rdy, wreq, rdata, used = twin.step(vld, sdata, rd)
        stim_list.append((vld, sdata, rd))
        trace_list.append((curr_c, vld, sdata, rd, rdy, wreq, rdata, used))
        curr_c += 1

    # 4. Drain remaining words
    while not twin.fifo_empty:
        rdy, wreq, rdata, used = twin.step(0, 0, 1)
        stim_list.append((0, 0, 1))
        trace_list.append((curr_c, 0, 0, 1, rdy, wreq, rdata, used))
        curr_c += 1

    return stim_list, trace_list


def write_test_files(out_dir="verify_v3"):
    os.makedirs(out_dir, exist_ok=True)

    # 1. Avalon-MM to Avalon-ST Input FIFO files
    in_stim, in_trace = generate_fifo_in_test()
    stim_in_path = os.path.join(out_dir, "tb_ch01_fifo_stim.txt")
    exp_in_path = os.path.join(out_dir, "tb_ch01_fifo_expected.txt")

    with open(stim_in_path, "w") as f:
        for w, wd, rdy in in_stim:
            f.write(f"{w} {wd:08x} {rdy}\n")

    with open(exp_in_path, "w") as f:
        for c, w, wd, wreq, vld, rdy, data, st, fill in in_trace:
            f.write(f"{c} {w} {wd:08x} {wreq} {vld} {rdy} {data:04x} {st} {fill}\n")

    print(f"Generated {len(in_stim)} cycles for Input FIFO: {stim_in_path}, {exp_in_path}")

    # 2. Return Path Output FIFO files
    out_stim, out_trace = generate_fifo_out_test()
    stim_out_path = os.path.join(out_dir, "tb_ch01_fifo_out_stim.txt")
    exp_out_path = os.path.join(out_dir, "tb_ch01_fifo_out_expected.txt")

    with open(stim_out_path, "w") as f:
        for vld, sdata, rd in out_stim:
            f.write(f"{vld} {sdata:04x} {rd}\n")

    with open(exp_out_path, "w") as f:
        for c, vld, sdata, rd, rdy, wreq, rdata, used in out_trace:
            f.write(f"{c} {vld} {sdata:04x} {rd} {rdy} {wreq} {rdata:04x} {used}\n")

    print(f"Generated {len(out_stim)} cycles for Output FIFO: {stim_out_path}, {exp_out_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    write_test_files(script_dir)
