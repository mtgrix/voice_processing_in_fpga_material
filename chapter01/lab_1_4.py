#!/usr/bin/env python3
"""lab_1_4.py -- Measure hardware storage, sparse filterbank, and latency bounds.

Reproduces all architectural quantities for Section 1.4:
- Frame fill time (25 ms) and hop interval (10 ms)
- Ring buffer storage vs. 36-kilobit Block RAM tile (1600 B / 4608 B = 34.7%)
- Sparse Mel filterbank storage (used_weight_bytes) vs dense expectation (82240 B)
- Arithmetic operations per frame (multiplies, adds) and per second
- Comparison against cited Jetson Orin Nano Super dense INT8 TOPS rating
- One-second framing boundary (98 frames, last window 15520--15920, 80 tail samples)
- Batch delay scaling ((B - 1) * 10 ms)
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chapter01.exp_01_streaming_audio_pipeline import (  # noqa: E402
    AudioConfig,
    create_mel_filterbank,
)
from chapter01.lab_1_3 import classify_filterbank_rows  # noqa: E402


def compute_ring_buffer_stats(
    win_length: int = 400, bytes_per_sample: int = 4
) -> dict[str, float | int]:
    """Compute ring buffer byte size and percentage of one 36-kilobit BRAM block."""
    ring_bytes = win_length * bytes_per_sample
    one_bram_bytes = (36 * 1024) // 8  # 4608 bytes
    ring_percent = (ring_bytes / one_bram_bytes) * 100.0

    bram_blocks = 144
    all_bram_bytes = bram_blocks * one_bram_bytes
    all_bram_kib = all_bram_bytes // 1024
    datasheet_bram_kbit = bram_blocks * 36

    return {
        "ring_bytes": ring_bytes,
        "one_bram_bytes": one_bram_bytes,
        "ring_percent_of_one_bram": round(ring_percent, 1),
        "bram_blocks": bram_blocks,
        "all_bram_bytes": all_bram_bytes,
        "all_bram_kib": all_bram_kib,
        "datasheet_bram_kbit": datasheet_bram_kbit,
    }


def compute_filterbank_storage_and_ops(
    fb: np.ndarray,
) -> dict[str, int]:
    """Compute dense vs sparse storage and arithmetic operations per frame.

    Counting rules:
    - Dead row (all zeros): 0 weights, 0 multiplies, 0 adds, 0 bytes.
    - One-tap row (single positive weight 1.0): 0 multiplies, 0 adds, 4 bytes (int32 bin index).
    - Multi-bin row (k positive weights): k multiplies, k - 1 adds,
      k * (4 bytes float32 + 4 bytes int32) = 8k bytes.
    """
    dead_rows, onetap_rows, multitap_rows = classify_filterbank_rows(fb)

    dense_bytes = fb.shape[0] * fb.shape[1] * 4  # 80 * 257 * 4 = 82240
    dense_products = fb.shape[0] * fb.shape[1]  # 20560

    used_weight_bytes = 0
    multiply_per_frame = 0
    add_per_frame = 0

    for _m in onetap_rows:
        used_weight_bytes += 4  # one int32 index

    for m in multitap_rows:
        row = fb[m]
        k = int(np.sum(row > 0))
        multiply_per_frame += k
        add_per_frame += k - 1
        used_weight_bytes += k * 8

    return {
        "dense_bytes": dense_bytes,
        "dense_products_per_frame": dense_products,
        "used_weight_bytes": used_weight_bytes,
        "multiply_per_frame": multiply_per_frame,
        "add_per_frame": add_per_frame,
        "dead_count": len(dead_rows),
        "onetap_count": len(onetap_rows),
        "multitap_count": len(multitap_rows),
    }


def compute_throughput_and_framing(
    multiply_per_frame: int,
    sample_rate: int = 16000,
    win_length: int = 400,
    hop_length: int = 160,
) -> dict[str, float | int]:
    """Compute workload rate, hardware scale quotients, and 1-second boundary frames."""
    multiply_per_second = multiply_per_frame * 100

    cited_sparse_int8_tops = 67
    cited_power_ceiling_w = 25
    halved_sparse_tops = 33.5  # dense INT8 arithmetic

    quotient_mac_as_one = (33.5e12) / multiply_per_second
    quotient_mac_as_two = (33.5e12) / (2 * multiply_per_second)

    dsp48e2_cited = 1248

    # 1-second framing
    last_start = ((sample_rate - win_length) // hop_length) * hop_length
    last_end = last_start + win_length
    frames_in_one_second = (last_start // hop_length) + 1
    tail_samples = sample_rate - last_end
    batch8_delay_ms = (8 - 1) * 10

    return {
        "multiply_per_second": multiply_per_second,
        "cited_sparse_int8_tops": cited_sparse_int8_tops,
        "cited_power_ceiling_w": cited_power_ceiling_w,
        "halved_sparse_tops": halved_sparse_tops,
        "quotient_mac_as_one": quotient_mac_as_one,
        "quotient_mac_as_two": quotient_mac_as_two,
        "dsp48e2_cited": dsp48e2_cited,
        "frames_in_one_second": frames_in_one_second,
        "last_start": last_start,
        "last_end": last_end,
        "tail_samples": tail_samples,
        "batch8_delay_ms": batch8_delay_ms,
    }


def generate_figures(
    output_dir: Path,
    fb: np.ndarray,
    used_weight_bytes: int,
    dense_bytes: int,
    multiply_per_second: int,
    halved_sparse_tops: float,
) -> list[Path]:
    """Generate vector PDFs for Section 1.4: BRAM, Mel bank storage, and throughput comparison."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Segoe UI"]
    plt.rcParams["axes.edgecolor"] = "#444444"
    plt.rcParams["axes.linewidth"] = 0.8

    # -------------------------------------------------------------------------
    # 1. Figure 1.4_bram: One 36 kbit BRAM block with 1600 bytes marked
    # -------------------------------------------------------------------------
    fig1_path = output_dir / "fig_1_4_bram_vi.pdf"
    fig, ax = plt.subplots(figsize=(6.8, 1.8))
    # Full block rectangle: 4608 bytes
    ax.barh(
        [0],
        [4608],
        color="#f0f0f0",
        edgecolor="#333333",
        height=0.5,
        linewidth=1.0,
        label="Dung lượng 1 khối BRAM 36 kbit (4.608 bytes)",
    )
    # Ring buffer occupancy: 1600 bytes
    ax.barh(
        [0],
        [1600],
        color="#1f77b4",
        edgecolor="#114477",
        height=0.5,
        linewidth=1.0,
        label="Đệm vòng 400 mẫu FP32: 1.600 bytes (34,7%)",
    )

    ax.text(
        800,
        0,
        "1.600 bytes\n(34,7%)",
        ha="center",
        va="center",
        color="white",
        fontsize=8.5,
        fontweight="bold",
    )
    ax.text(
        3104,
        0,
        "Phần còn lại của khối này:\n3.008 bytes (65,3%)",
        ha="center",
        va="center",
        color="#444444",
        fontsize=8,
    )

    ax.set_xlim(0, 4800)
    ax.set_ylim(-0.5, 0.8)
    ax.set_xlabel("Dung lượng bộ nhớ (Bytes)", fontsize=8.5)
    ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.35), fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(fig1_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig1_path)

    # -------------------------------------------------------------------------
    # 2. Figure 1.4_bank: Filter 0, 2, 15 stems + storage comparison bar
    # -------------------------------------------------------------------------
    fig2_path = output_dir / "fig_1_4_bank_vi.pdf"
    fig, (ax_stems, ax_bars) = plt.subplots(
        1, 2, figsize=(7.6, 2.4), gridspec_kw={"width_ratios": [1.4, 0.8]}
    )

    bins_zoom = np.arange(18)
    # Stems for filter 0, 2, 15
    ax_stems.stem(
        bins_zoom,
        fb[0, :18],
        linefmt="b-",
        markerfmt="bo",
        basefmt="k-",
        label="Bộ lọc 0: mũi nhọn tại bin 0",
    )
    ax_stems.scatter(
        [2],
        [0.0],
        color="#d62728",
        marker="x",
        s=45,
        zorder=5,
        label="Bộ lọc 2: hàng chết (trống rỗng)",
    )
    ax_stems.stem(
        bins_zoom,
        fb[15, :18],
        linefmt="g-",
        markerfmt="go",
        basefmt="k-",
        label="Bộ lọc 15: mũi nhọn tại bin 14",
    )
    ax_stems.set_xlim(-0.5, 17.5)
    ax_stems.set_ylim(-0.1, 1.2)
    ax_stems.set_xlabel("Chỉ số bin phổ $k$ (0–17)", fontsize=8)
    ax_stems.set_ylabel("Trọng số $g_m[k]$", fontsize=8)
    ax_stems.set_title("(a) Trọng số rời rạc ba bộ lọc tiêu biểu", fontsize=8.5, fontweight="bold")
    ax_stems.grid(True, linestyle="--", alpha=0.5)
    ax_stems.legend(loc="upper right", fontsize=6.8)

    # Storage bar: 82240 vs used_weight_bytes
    x_pos = [0, 1]
    y_vals = [dense_bytes, used_weight_bytes]
    bars = ax_bars.bar(x_pos, y_vals, color=["#999999", "#2ca02c"], width=0.55)
    ax_bars.set_xticks(x_pos)
    ax_bars.set_xticklabels(
        ["Ma trận dày\n(Kỳ vọng)", "Trọng số thực dùng\n(Mô hình sổ sách)"], fontsize=8
    )
    ax_bars.set_ylabel("Dung lượng (Bytes)", fontsize=8)
    ax_bars.set_title("(b) So sánh dung lượng lưu trữ", fontsize=8.5, fontweight="bold")
    ax_bars.set_ylim(0, 95000)
    for b, val in zip(bars, y_vals, strict=False):
        ax_bars.text(
            b.get_x() + b.get_width() / 2.0,
            val + 2000,
            f"{val:,} B",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
        )
    ax_bars.grid(True, linestyle="--", alpha=0.5, axis="y")

    fig.tight_layout()
    fig.savefig(fig2_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig2_path)

    # -------------------------------------------------------------------------
    # 3. Figure 1.4_rate: Two bars that do not share an axis
    # -------------------------------------------------------------------------
    fig3_path = output_dir / "fig_1_4_rate_vi.pdf"
    fig, (ax_fe, ax_gpu) = plt.subplots(
        1, 2, figsize=(7.6, 2.7), gridspec_kw={"width_ratios": [1, 1]}
    )

    # Left: Mel FP32 multiply/s (not whole frontend)
    ax_fe.bar([0], [multiply_per_second / 1e3], color="#1f77b4", width=0.45)
    ax_fe.set_xticks([0])
    ax_fe.set_xticklabels(
        ["407 nhân/khung $\\times$ 100 khung/s\n(Chỉ tính phép nhân Mel)"], fontsize=7.5
    )
    ax_fe.set_ylabel("Nghìn phép nhân FP32 / giây", fontsize=8)
    ax_fe.set_title("(a) Tốc độ nhân ma trận Mel (FP32)", fontsize=8.5, fontweight="bold")
    ax_fe.text(
        0,
        (multiply_per_second / 1e3) + 2.0,
        f"{multiply_per_second:,} nhân/s\n({multiply_per_second / 1e3:.1f} nghìn/s)",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
    )
    ax_fe.set_ylim(0, 100)
    ax_fe.grid(True, linestyle="--", alpha=0.5, axis="y")

    # Right: Jetson Orin Nano Super INT8 TOPS
    # Show published 67 sparse TOPS and halved 33.5 dense TOPS
    ax_gpu.bar(
        [0],
        [67],
        color="#ffe5cc",
        edgecolor="#ff7f0e",
        linestyle="--",
        linewidth=1.2,
        width=0.45,
        label="Công bố: 67 sparse TOPS (25 W)",
    )
    ax_gpu.bar(
        [0],
        [halved_sparse_tops],
        color="#ff7f0e",
        width=0.45,
        label="Quy đổi sách: 33,5 dense TOPS (67/2)",
    )
    ax_gpu.set_xticks([0])
    ax_gpu.set_xticklabels(["NVIDIA Jetson Orin Nano Super\n(Trần công suất 25 W)"], fontsize=7.5)
    ax_gpu.set_ylabel("Định mức INT8 TOPS ($10^{12}$ ops/s)", fontsize=8)
    ax_gpu.set_title("(b) Định mức tính toán GPU (INT8)", fontsize=8.5, fontweight="bold")
    ax_gpu.text(
        0,
        67 + 1.5,
        "67 TOPS (sparse)",
        ha="center",
        va="bottom",
        fontsize=7.5,
        fontweight="bold",
        color="#b35400",
    )
    ax_gpu.text(
        0,
        halved_sparse_tops / 2.0,
        "33,5 dense TOPS\n($33,5 \\times 10^{12}$ ops/s)",
        ha="center",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="white",
    )
    ax_gpu.set_ylim(0, 80)
    ax_gpu.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax_gpu.legend(loc="upper left", fontsize=7.0)

    fig.suptitle(
        "Đối chiếu quy mô: Khác biệt bậc độ lớn $\\sim 10^8$ lần (33,5 TOPS vs 40.700 FP32 nhân/s)",
        fontsize=8.5,
        fontstyle="italic",
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(fig3_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig3_path)

    return generated


def run_experiment() -> dict[str, float | int]:
    """Execute all calculations, generate figures, print exact keys, and return metrics."""
    cfg = AudioConfig()
    fb = create_mel_filterbank(cfg)

    # Row assertions
    dead_rows, onetap_rows, multitap_rows = classify_filterbank_rows(fb)
    assert len(dead_rows) + len(onetap_rows) + len(multitap_rows) == 80
    assert dead_rows == [2]
    nz_15 = np.where(fb[15] > 0)[0]
    assert len(nz_15) == 1 and nz_15[0] == 14 and np.isclose(fb[15, 14], 1.0)

    # Calculations
    bram_stats = compute_ring_buffer_stats(cfg.win_length)
    fb_stats = compute_filterbank_storage_and_ops(fb)
    rate_stats = compute_throughput_and_framing(
        fb_stats["multiply_per_frame"],
        sample_rate=cfg.sample_rate,
        win_length=cfg.win_length,
        hop_length=cfg.hop_length,
    )

    # Generate figures
    output_dir = Path(__file__).resolve().parent
    generate_figures(
        output_dir,
        fb,
        used_weight_bytes=fb_stats["used_weight_bytes"],
        dense_bytes=fb_stats["dense_bytes"],
        multiply_per_second=int(rate_stats["multiply_per_second"]),
        halved_sparse_tops=float(rate_stats["halved_sparse_tops"]),
    )

    # Aggregate result
    res: dict[str, float | int] = {}
    res.update(bram_stats)
    res.update(fb_stats)
    res.update(rate_stats)

    # Print exact keys, one per line
    print(f"ring_bytes={res['ring_bytes']}")
    print(f"one_bram_bytes={res['one_bram_bytes']}")
    print(f"ring_percent_of_one_bram={res['ring_percent_of_one_bram']}")
    print(f"bram_blocks={res['bram_blocks']}")
    print(f"all_bram_bytes={res['all_bram_bytes']}")
    print(f"all_bram_kib={res['all_bram_kib']}")
    print(f"datasheet_bram_kbit={res['datasheet_bram_kbit']}")
    print(f"dense_bytes={res['dense_bytes']}")
    print(f"dense_products_per_frame={res['dense_products_per_frame']}")
    print(f"used_weight_bytes={res['used_weight_bytes']}")
    print(f"multiply_per_frame={res['multiply_per_frame']}")
    print(f"add_per_frame={res['add_per_frame']}")
    print(f"multiply_per_second={res['multiply_per_second']}")
    print("cited rating, not measured by this lab.")
    print(f"cited_sparse_int8_tops={res['cited_sparse_int8_tops']}")
    print(f"cited_power_ceiling_w={res['cited_power_ceiling_w']}")
    print(f"halved_sparse_tops={res['halved_sparse_tops']}")
    print(f"quotient_mac_as_one={res['quotient_mac_as_one']:.2f}")
    print(f"quotient_mac_as_two={res['quotient_mac_as_two']:.2f}")
    print(f"dsp48e2_cited={res['dsp48e2_cited']}")
    print(f"frames_in_one_second={res['frames_in_one_second']}")
    print(f"last_start={res['last_start']}")
    print(f"last_end={res['last_end']}")
    print(f"tail_samples={res['tail_samples']}")
    print(f"batch8_delay_ms={res['batch8_delay_ms']}")
    print(f"dead_count={res['dead_count']}")
    print(f"onetap_count={res['onetap_count']}")
    print(f"multitap_count={res['multitap_count']}")

    return res


if __name__ == "__main__":
    run_experiment()
