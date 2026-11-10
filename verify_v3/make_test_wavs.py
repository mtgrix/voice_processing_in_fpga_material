#!/usr/bin/env python3
"""verify_v3/make_test_wavs.py
Generate crafted WAV test files:
1. mini_speech.wav: tiny valid 16kHz mono 16-bit file (8 samples) for hex dump walk-through.
2. edge_list_chunk.wav: valid audio with LIST/INFO chunk placed BEFORE data chunk.
3. edge_odd_chunk.wav: valid audio with an odd-sized metadata chunk (with 1-byte padding).
4. edge_wrong_rate.wav: invalid sample rate (44100 Hz).
5. edge_stereo.wav: invalid channel count (2 channels, stereo).
6. edge_truncated.wav: corrupted file where data chunk is shorter than header claims.
"""
import os
import struct
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def write_mini_speech():
    # 8 samples: 0, 100, -200, 300, -400, 500, -600, 700
    samples = np.array([0, 100, -200, 300, -400, 500, -600, 700], dtype=np.int16)
    raw_data = samples.tobytes()
    data_size = len(raw_data) # 16 bytes
    
    # fmt chunk: 16 bytes
    # AudioFormat=1, NumChannels=1, SampleRate=16000, ByteRate=32000, BlockAlign=2, BitsPerSample=16
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 16000, 32000, 2, 16)
    data_chunk = struct.pack("<4sI", b"data", data_size) + raw_data
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    
    path = os.path.join(DATA_DIR, "mini_speech.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

def write_edge_list_chunk():
    # 160 samples (1 hop) of 100 Hz sine
    t = np.arange(160) / 16000.0
    samples = (10000 * np.sin(2 * np.pi * 100 * t)).astype(np.int16)
    raw_data = samples.tobytes() # 320 bytes
    
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 16000, 32000, 2, 16)
    
    # LIST INFO chunk: 4 bytes 'INFO', subchunk 'INAM' (Title: "DE10")
    # subchunk 'INAM' has size 5 bytes (including null terminator) -> odd size!
    # With padding, INAM chunk takes 8 + 5 + 1 = 14 bytes
    # Entire LIST chunk content: 'INFO' (4 bytes) + 'INAM' (4) + len=6 (4) + "DE10\0\0" (6 bytes)
    list_content = b"INFO" + struct.pack("<4sI", b"INAM", 6) + b"DE10\0\0"
    list_chunk = struct.pack("<4sI", b"LIST", len(list_content)) + list_content
    
    data_chunk = struct.pack("<4sI", b"data", len(raw_data)) + raw_data
    riff_size = 4 + len(fmt_chunk) + len(list_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    
    path = os.path.join(DATA_DIR, "edge_list_chunk.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + list_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

def write_edge_odd_chunk():
    # An auxiliary chunk 'JUNK' with odd length 13 bytes, followed by 1 pad byte 0x00
    samples = np.array([1000, -1000, 2000, -2000], dtype=np.int16)
    raw_data = samples.tobytes() # 8 bytes
    
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 16000, 32000, 2, 16)
    junk_data = b"Hello DE10-Std" # 14 bytes -> let's make it 13 bytes: "Hello DE10-St"
    junk_data_odd = b"Hello DE10-St" # 13 bytes
    junk_chunk = struct.pack("<4sI", b"JUNK", 13) + junk_data_odd + b"\x00" # pad byte
    data_chunk = struct.pack("<4sI", b"data", len(raw_data)) + raw_data
    
    riff_size = 4 + len(fmt_chunk) + len(junk_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    
    path = os.path.join(DATA_DIR, "edge_odd_chunk.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + junk_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

def write_edge_wrong_rate():
    # 44100 Hz rate
    samples = np.array([100, -100], dtype=np.int16)
    raw_data = samples.tobytes()
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 44100, 88200, 2, 16)
    data_chunk = struct.pack("<4sI", b"data", len(raw_data)) + raw_data
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    path = os.path.join(DATA_DIR, "edge_wrong_rate.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

def write_edge_stereo():
    # Stereo (2 channels)
    samples = np.array([100, 200, -100, -200], dtype=np.int16) # 2 stereo frames
    raw_data = samples.tobytes()
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 2, 16000, 64000, 4, 16)
    data_chunk = struct.pack("<4sI", b"data", len(raw_data)) + raw_data
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    path = os.path.join(DATA_DIR, "edge_stereo.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

def write_edge_truncated():
    # Claims 1000 bytes, but provides only 16 bytes
    samples = np.array([100, -100, 200, -200, 300, -300, 400, -400], dtype=np.int16) # 16 bytes
    raw_data = samples.tobytes()
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 16000, 32000, 2, 16)
    data_chunk = struct.pack("<4sI", b"data", 1000) + raw_data # only 16 bytes!
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    riff_header = struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
    path = os.path.join(DATA_DIR, "edge_truncated.wav")
    with open(path, "wb") as f:
        f.write(riff_header + fmt_chunk + data_chunk)
    print(f"Created {path} ({os.path.getsize(path)} bytes)")

if __name__ == "__main__":
    write_mini_speech()
    write_edge_list_chunk()
    write_edge_odd_chunk()
    write_edge_wrong_rate()
    write_edge_stereo()
    write_edge_truncated()
