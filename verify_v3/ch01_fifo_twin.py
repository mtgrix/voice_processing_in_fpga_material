#!/usr/bin/env python3
"""verify_v3/ch01_fifo_twin.py
Cycle-accurate Python twin of rtl/v3/ch01_avalon_fifo.v:
- Models 256 x 32-bit RAM FIFO with wrap-bit pointers.
- Models unpacker state machine (ST_IDLE, ST_FETCH, ST_UNPACK0, ST_UNPACK1).
- Tracks Avalon-ST valid/ready handshake and Avalon-MM waitrequest.
- Computes total_samples_used (0..512) and CSR status flags.
"""

class AvalonFifoTwin:
    def __init__(self, depth_words=256):
        self.depth_words = depth_words
        self.mem = [0] * depth_words
        self.wr_ptr = 0
        self.rd_ptr = 0
        self.ovf_sticky = 0

        # Unpacker state
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
        # Full when wr_ptr and rd_ptr have opposite wrap bits and identical lower bits
        return self.words_used == self.depth_words

    @property
    def waitrequest(self):
        return self.fifo_full

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

    def clock(self, mm_write, mm_writedata, st_ready):
        """Simulate one clock edge."""
        # 1. State machine transition based on current state
        st_data = 0
        st_valid = 0

        if self.st_state in (self.ST_UNPACK0, self.ST_UNPACK1):
            st_valid = 1
            if self.st_state == self.ST_UNPACK0:
                st_data = self.holding_word & 0xFFFF
            else:
                st_data = (self.holding_word >> 16) & 0xFFFF

        # Next state computation
        next_state = self.st_state
        next_holding = self.holding_word
        inc_rd = False

        if self.st_state == self.ST_IDLE:
            if not self.fifo_empty:
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
                if not self.fifo_empty:
                    next_state = self.ST_FETCH
                    inc_rd = True
                else:
                    next_state = self.ST_IDLE

        # RAM read port (synchronous registered read)
        rd_addr = self.rd_ptr & (self.depth_words - 1)
        next_mem_rdata = self.mem[rd_addr]

        # Avalon-MM write port
        if mm_write:
            if not self.fifo_full:
                wr_addr = self.wr_ptr & (self.depth_words - 1)
                self.mem[wr_addr] = mm_writedata & 0xFFFFFFFF
                self.wr_ptr = (self.wr_ptr + 1) & ((2 * self.depth_words) - 1)
            else:
                self.ovf_sticky = 1

        # Advance unpacker registers
        if inc_rd:
            self.rd_ptr = (self.rd_ptr + 1) & ((2 * self.depth_words) - 1)
        self.st_state = next_state
        self.holding_word = next_holding
        self.mem_rdata = next_mem_rdata

        return st_data, st_valid, self.waitrequest, self.fill_level_samples
