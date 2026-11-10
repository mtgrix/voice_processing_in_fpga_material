#!/usr/bin/env python3
"""
verify_v3/ch02_fsm_twin.py

Python twin and test vector generator for 5-state control FSM (ch02_fsm_binary & ch02_fsm_onehot):
- States:
  0: IDLE
  1: LOAD
  2: CALC
  3: DRAIN
  4: DONE
- Transitions:
  IDLE  -> (start) ? LOAD : IDLE
  LOAD  -> (load_done) ? CALC : LOAD
  CALC  -> (calc_done) ? DRAIN : CALC
  DRAIN -> (drain_done) ? DONE : DRAIN
  DONE  -> IDLE (unconditional next cycle)
- Outputs (observed AFTER posedge clk):
  busy, load_en, calc_en, drain_en, done_pulse, state_num (0..4)
- Generates >= 500 test cycles covering all branches, stalls, and resets.
- Writes:
  * verify_v3/tb_ch02_fsm_stim.txt (rst_n, start, load_done, calc_done, drain_done)
  * verify_v3/tb_ch02_fsm_expected.txt (c, rst_n, busy, load_en, calc_en, drain_en, done_pulse, state_num)
"""

import os
import random

class FsmTwin:
    IDLE = 0
    LOAD = 1
    CALC = 2
    DRAIN = 3
    DONE = 4
    
    def __init__(self):
        self.state = self.IDLE
        
    def step(self, rst_n, start, load_done, calc_done, drain_done):
        if not rst_n:
            self.state = self.IDLE
            return (0, 0, 0, 0, 0, self.IDLE)
            
        curr_state = self.state
        
        # Next state logic
        next_state = curr_state
        if curr_state == self.IDLE:
            if start:
                next_state = self.LOAD
        elif curr_state == self.LOAD:
            if load_done:
                next_state = self.CALC
        elif curr_state == self.CALC:
            if calc_done:
                next_state = self.DRAIN
        elif curr_state == self.DRAIN:
            if drain_done:
                next_state = self.DONE
        elif curr_state == self.DONE:
            next_state = self.IDLE
            
        # Register updates on posedge clk
        self.state = next_state
        
        # Outputs observed after posedge clk (Moore outputs of current state)
        busy = 1 if self.state != self.IDLE else 0
        load_en = 1 if self.state == self.LOAD else 0
        calc_en = 1 if self.state == self.CALC else 0
        drain_en = 1 if self.state == self.DRAIN else 0
        done_pulse = 1 if self.state == self.DONE else 0
        state_num = self.state
        
        return (busy, load_en, calc_en, drain_en, done_pulse, state_num)

def run_fsm_simulation(num_cycles=500, seed=123):
    random.seed(seed)
    twin = FsmTwin()
    
    stim_lines = []
    exp_lines = []
    
    for c in range(num_cycles):
        if c < 4:
            rst_n = 0
            start = 0
            load_done = 0
            calc_done = 0
            drain_done = 0
        elif c == 50 or c == 150:
            # Asynchronous reset pulse test
            rst_n = 0
            start = 0
            load_done = 0
            calc_done = 0
            drain_done = 0
        else:
            rst_n = 1
            # Random control inputs
            start = 1 if (random.random() < 0.35) else 0
            load_done = 1 if (random.random() < 0.30) else 0
            calc_done = 1 if (random.random() < 0.25) else 0
            drain_done = 1 if (random.random() < 0.30) else 0
            
        busy, load_en, calc_en, drain_en, done_pulse, state_num = twin.step(
            rst_n, start, load_done, calc_done, drain_done
        )
        
        stim_lines.append(f"{rst_n} {start} {load_done} {calc_done} {drain_done}\n")
        exp_lines.append(f"{c} {rst_n} {busy} {load_en} {calc_en} {drain_en} {done_pulse} {state_num}\n")
        
    out_dir = "." if os.path.basename(os.getcwd()) == "verify_v3" else "verify_v3"
    os.makedirs(out_dir, exist_ok=True)
    stim_path = os.path.join(out_dir, "tb_ch02_fsm_stim.txt")
    exp_path = os.path.join(out_dir, "tb_ch02_fsm_expected.txt")
    
    with open(stim_path, "w", newline="\n") as f:
        f.writelines(stim_lines)
    with open(exp_path, "w", newline="\n") as f:
        f.writelines(exp_lines)
        
    print(f"FSM simulation completed {num_cycles} cycles.")
    print(f"Wrote {stim_path} and {exp_path} successfully.")

if __name__ == "__main__":
    run_fsm_simulation()
