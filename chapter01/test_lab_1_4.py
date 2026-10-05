"""Tests for chapter01/lab_1_4.py and Section 1.4 study materials."""

from __future__ import annotations

import pytest

from chapter01.exp_01_streaming_audio_pipeline import AudioConfig, create_mel_filterbank
from chapter01.lab_1_3 import classify_filterbank_rows
from chapter01.lab_1_4 import (
    ROOT,
    compute_filterbank_storage_and_ops,
    compute_ring_buffer_stats,
    compute_throughput_and_framing,
)


def test_ring_buffer_identities() -> None:
    """Verifies ring buffer sizing, single BRAM capacity, and full device BRAM total."""
    stats = compute_ring_buffer_stats()
    assert stats["ring_bytes"] == 1600
    assert stats["one_bram_bytes"] == 4608
    assert stats["bram_blocks"] == 144
    assert stats["all_bram_bytes"] == 663552
    assert stats["all_bram_kib"] == 648
    assert stats["datasheet_bram_kbit"] == 5184
    assert stats["ring_percent_of_one_bram"] == pytest.approx(34.7, abs=0.05)


def test_filterbank_storage_and_ops_split() -> None:
    """Classifies rows of fresh filterbank and verifies dense vs sparse storage and ops."""
    config = AudioConfig()
    fb = create_mel_filterbank(config)
    dead_rows, onetap_rows, multitap_rows = classify_filterbank_rows(fb)

    assert len(dead_rows) == 1
    assert dead_rows == [2]
    assert len(onetap_rows) == 18
    assert len(multitap_rows) == 61
    assert len(dead_rows) + len(onetap_rows) + len(multitap_rows) == 80

    fb_stats = compute_filterbank_storage_and_ops(fb)
    assert fb_stats["dense_bytes"] == 82240
    assert fb_stats["dense_products_per_frame"] == 20560
    assert fb_stats["used_weight_bytes"] == 3328
    assert fb_stats["multiply_per_frame"] == 407
    assert fb_stats["add_per_frame"] == 346
    assert fb_stats["dead_count"] == 1
    assert fb_stats["onetap_count"] == 18
    assert fb_stats["multitap_count"] == 61


def test_throughput_and_framing_identities() -> None:
    """Verifies cited ratings, quotients, framing boundary, and batch delay."""
    rates = compute_throughput_and_framing(multiply_per_frame=407)
    assert rates["multiply_per_second"] == 40700
    assert rates["cited_sparse_int8_tops"] == 67
    assert rates["cited_power_ceiling_w"] == 25
    assert rates["halved_sparse_tops"] == 33.5
    assert rates["quotient_mac_as_one"] == pytest.approx(823095823.10, rel=1e-5)
    assert rates["quotient_mac_as_two"] == pytest.approx(411547911.55, rel=1e-5)
    assert rates["dsp48e2_cited"] == 1248
    assert rates["frames_in_one_second"] == 98
    assert rates["last_start"] == 15520
    assert rates["last_end"] == 15920
    assert rates["tail_samples"] == 80
    assert rates["batch8_delay_ms"] == 70


def test_forbidden_substrings_in_sec_1_4_files() -> None:
    """sec_1_4_vi.tex and all fig_1_4*.tex files must not contain forbidden phrases."""
    target_files = [
        ROOT / "chapter01" / "sec_1_4_vi.tex",
        ROOT / "chapter01" / "fig_1_4a_vi.tex",
        ROOT / "chapter01" / "fig_1_4b_vi.tex",
        ROOT / "chapter01" / "fig_1_4_tail_vi.tex",
    ]

    forbidden = [
        "one millionth",
        "0 ns",
        "0~ns",
        "5--15",
        "5–15",
        "200 MHz",
        "200~MHz",
        "preserving energy",
        "bảo toàn năng lượng",
        "What it proves",
        "chứng minh",
        "Zero DDR",
        "zero DDR",
        "GROUNDBREAKING",
        "exceptional efficiency",
        "absolute latency",
        "Hann",
        "V-0",
    ]

    for p in target_files:
        if not p.is_file():
            pytest.skip(f"File {p.name} not found yet")
        content = p.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in content, f"Forbidden term {term!r} found in {p.name}"


def test_sec_1_4_vi_counts_and_omissions() -> None:
    """Verifies that multiply_per_frame (407) is present in sec_1_4_vi.tex and 117120 is absent."""
    tex_path = ROOT / "chapter01" / "sec_1_4_vi.tex"
    if not tex_path.is_file():
        pytest.skip("sec_1_4_vi.tex not found yet")
    content = tex_path.read_text(encoding="utf-8")

    assert "407" in content, "Expected multiply_per_frame 407 in sec_1_4_vi.tex"
    assert "117120" not in content, "Forbidden 117120 found in sec_1_4_vi.tex"
    assert "117,120" not in content, "Forbidden 117,120 found in sec_1_4_vi.tex"
