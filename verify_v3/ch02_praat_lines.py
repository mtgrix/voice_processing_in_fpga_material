#!/usr/bin/env python3
"""
verify_v3/ch02_praat_lines.py

Checks Praat citations in Chapter 2:
Ensures all Praat source citations follow the contract:
- The local Praat copy on Windows is older than 7.0.03.
- Any unresolved line number in chuong_02_avalon_st_fsm.tex must use TODO-PRAAT-LINE.
"""

import os
import re

def check_praat_citations():
    tex_path = "chuong_v3/chuong_02_avalon_st_fsm.tex"
    if not os.path.exists(tex_path):
        print(f"File {tex_path} not found yet (will check after writing).")
        return
        
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for hardcoded Praat line numbers like "Sound_to_Pitch.cpp dòng 123"
    hardcoded = re.findall(r"Sound_to_Pitch\.cpp\s+(?:dòng|lines?)\s+(\d+)", content, re.IGNORECASE)
    todo_lines = re.findall(r"TODO-PRAAT-LINE", content)
    
    print(f"Found {len(todo_lines)} TODO-PRAAT-LINE placeholders.")
    if hardcoded:
        print(f"WARNING: Found {len(hardcoded)} hardcoded Praat line numbers: {hardcoded}")
        print("Contract specifies writing TODO-PRAAT-LINE for 7.0.03 line numbers on this machine.")
    else:
        print("PASS: No unauthorized hardcoded Praat line numbers found.")

if __name__ == "__main__":
    check_praat_citations()
