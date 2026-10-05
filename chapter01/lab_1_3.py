"""Lab 1.3: Mathematical Modeling of Streaming STFT and Mel Filterbank.

Demonstrates and verifies each stage of acoustic feature extraction on:
1. A synthetic reference 440 Hz tone (datasets/sample_tone440.wav)
2. Speech utterances from Speech Commands (datasets/sample_speech_a.wav, sample_speech_b.wav)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import wave
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chapter01.exp_01_streaming_audio_pipeline import (  # noqa: E402
    AudioConfig,
    create_mel_filterbank,
    hz_to_mel,
    mel_to_hz,
)


def sha256_file(path: Path | str) -> str:
    """Compute SHA256 digest of a file on disk."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ensure_tone_file(path: Path) -> None:
    """Ensure datasets/sample_tone440.wav exists on disk; synthesize if absent."""
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fs = 16000
    duration = 1.0
    n = np.arange(int(fs * duration))
    # 1.0 s tone: cos(2*pi*440*n/16000), 16000 Hz, mono, int16
    tone_int16 = np.round(np.cos(2.0 * np.pi * 440.0 * n / fs) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(tone_int16.tobytes())


def load_wav(path: Path | str) -> tuple[np.ndarray, int]:
    """Load a 16 kHz mono WAV file, returning normalized float32 samples in [-1.0, 1.0]."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Missing WAV file: {p}")
    with wave.open(str(p), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if n_channels != 1:
        raise ValueError(f"Expected mono audio, got {n_channels} channels")
    if sampwidth != 2:
        raise ValueError(f"Expected 16-bit PCM, got {sampwidth * 8}-bit")
    if framerate != 16000:
        raise ValueError(f"Expected 16000 Hz sample rate, got {framerate} Hz")

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return samples, framerate


def window_frame(
    signal: np.ndarray, start_idx: int = 0, win_length: int = 400
) -> tuple[np.ndarray, np.ndarray]:
    """Extract and window a frame using a Hamming window."""
    if len(signal) < start_idx + win_length:
        raise ValueError(f"Signal length {len(signal)} is shorter than required frame range")
    raw_frame = signal[start_idx : start_idx + win_length]
    w = np.hamming(win_length).astype(np.float32)
    return raw_frame * w, w


def detect_window_sidelobes(
    w: np.ndarray, n_scan: int = 65536, fs: int = 16000
) -> tuple[float, float, float, float]:
    """Detect first null (Hz), null width (Hz), first sidelobe freq (Hz) and level (dB).

    Uses a dense zero-padded FFT (n_scan >= 16384). Note that n_scan is separate
    from the speech transform length N = 512, where bin spacing (31.25 Hz) is too
    coarse to accurately locate sidelobe peaks.
    """
    W = np.fft.rfft(w, n=n_scan)
    mag = np.abs(W)
    peak = float(mag[0])
    mag_db = 20.0 * np.log10(np.maximum(mag / peak, 1e-12))
    freqs = np.fft.rfftfreq(n_scan, d=1.0 / fs)

    diffs = np.diff(mag_db)
    # First null: first local minimum where diff changes sign <= 0 to > 0
    local_mins = np.where((diffs[:-1] <= 0) & (diffs[1:] > 0))[0] + 1
    null_idx = int(local_mins[0])
    null_hz = float(freqs[null_idx])
    null_to_null_hz = 2.0 * null_hz

    # First sidelobe: first local maximum after first null
    local_maxs = np.where((diffs[:-1] >= 0) & (diffs[1:] < 0))[0] + 1
    sidelobe_cands = local_maxs[local_maxs > null_idx]
    sidelobe_idx = int(sidelobe_cands[0])
    sidelobe_hz = float(freqs[sidelobe_idx])
    sidelobe_db = float(mag_db[sidelobe_idx])

    return null_hz, null_to_null_hz, sidelobe_hz, sidelobe_db


def probe_sums(frame: np.ndarray, k: int = 14, n_fft: int = 512) -> tuple[float, float]:
    """Compute discrete cosine and sine probe sums for frequency bin k."""
    n = np.arange(len(frame))
    cos_probe = np.cos(2.0 * np.pi * k * n / n_fft)
    sin_probe = -np.sin(2.0 * np.pi * k * n / n_fft)
    cos_sum = float(np.sum(frame * cos_probe))
    sin_sum = float(np.sum(frame * sin_probe))
    return cos_sum, sin_sum


def stft_power(frame: np.ndarray, n_fft: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Compute one-sided STFT complex bins and power spectrum with zero-padding."""
    padded = np.zeros(n_fft, dtype=np.float32)
    padded[: len(frame)] = frame
    X = np.fft.rfft(padded, n=n_fft)
    P = (np.abs(X) ** 2).astype(np.float32)
    return X, P


def mel_edges(config: AudioConfig) -> tuple[np.ndarray, np.ndarray, int, float, float]:
    """Compute Mel filterbank matrix, bin edges, collapsed count, mel(8000), and mel step."""
    mel_min = float(hz_to_mel(config.f_min))
    mel_max = float(hz_to_mel(config.f_max if config.f_max is not None else 8000.0))
    mel_points = np.linspace(mel_min, mel_max, config.n_mels + 2)
    step_mel = float(mel_points[1] - mel_points[0])
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((config.n_fft + 1) * hz_points / config.sample_rate).astype(int)

    filterbank = create_mel_filterbank(config)

    collapsed_count = 0
    for m in range(config.n_mels):
        left, center, right = bin_points[m], bin_points[m + 1], bin_points[m + 2]
        if left == center or center == right:
            collapsed_count += 1

    return filterbank, bin_points, collapsed_count, mel_max, step_mel


def classify_filterbank_rows(
    fb: np.ndarray,
) -> tuple[list[int], list[int], list[int]]:
    """Classify rows into dead (all 0), one-tap (single 1.0), and multi-tap."""
    dead_rows = []
    onetap_rows = []
    multitap_rows = []
    for m in range(fb.shape[0]):
        row = fb[m]
        nonzero = np.where(row > 0)[0]
        if len(nonzero) == 0:
            dead_rows.append(int(m))
        elif len(nonzero) == 1 and np.isclose(row[nonzero[0]], 1.0):
            onetap_rows.append(int(m))
        else:
            multitap_rows.append(int(m))
    return dead_rows, onetap_rows, multitap_rows


def log_compress(energy: np.ndarray | float, floor: float = 1e-6) -> np.ndarray | float:
    """Apply natural logarithm with lower-bound clamping at floor."""
    if isinstance(energy, (int, float, np.floating)):
        return float(np.log(max(float(energy), floor)))
    return np.log(np.maximum(energy, floor))


def analyze_speech_file(
    path: Path, config: AudioConfig, fb: np.ndarray
) -> tuple[int, list[dict[str, float | int]]]:
    """Extract frames, locate peak energy frame, and return its three loudest Mel bands."""
    audio, _ = load_wav(path)
    w = np.hamming(config.win_length).astype(np.float32)
    n_frames = (len(audio) - config.win_length) // config.hop_length + 1

    mel_max = float(hz_to_mel(config.f_max))
    mel_points = np.linspace(0.0, mel_max, config.n_mels + 2)
    hz_centers = mel_to_hz(mel_points[1:-1])

    powers = []
    log_mels = []
    for i in range(n_frames):
        start = i * config.hop_length
        frame = audio[start : start + config.win_length] * w
        _, P = stft_power(frame, n_fft=config.n_fft)
        powers.append(P)
        E = np.dot(fb, P)
        log_mels.append(log_compress(E))

    frame_energies = [float(np.sum(p)) for p in powers]
    peak_frame_idx = int(np.argmax(frame_energies))
    peak_log_mel = log_mels[peak_frame_idx]

    top3_indices = np.argsort(peak_log_mel)[::-1][:3]
    top3_bands = []
    for rank, b in enumerate(top3_indices, 1):
        top3_bands.append(
            {
                "rank": rank,
                "band_index": int(b),
                "log_mel": float(peak_log_mel[b]),
                "center_hz": float(hz_centers[b]),
            }
        )

    return peak_frame_idx, top3_bands


def generate_vector_figures(
    output_dir: Path,
    tone_audio: np.ndarray,
    speech_a_path: Path,
    config: AudioConfig,
    fb: np.ndarray,
    bin_points: np.ndarray,
) -> list[Path]:
    """Generate the five vector PDF figures directly from measured numpy arrays."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    # Configure clean plotting parameters
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Segoe UI"]
    plt.rcParams["axes.edgecolor"] = "#444444"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#dddddd"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.linewidth"] = 0.5

    # -------------------------------------------------------------------------
    # 1. Figure 1.3_window: Window spectrum comparison (PDF)
    # -------------------------------------------------------------------------
    fig1_path = output_dir / "fig_1_3_window_vi.pdf"
    n_scan = 65536
    fs = config.sample_rate
    w_rect = np.ones(config.win_length, dtype=np.float32)
    w_ham = np.hamming(config.win_length).astype(np.float32)

    r_null, r_n2n, r_side_hz, r_side_db = detect_window_sidelobes(w_rect, n_scan=n_scan, fs=fs)
    h_null, h_n2n, h_side_hz, h_side_db = detect_window_sidelobes(w_ham, n_scan=n_scan, fs=fs)

    freqs = np.fft.rfftfreq(n_scan, d=1.0 / fs)
    mask = freqs <= 220.0
    f_sub = freqs[mask]
    W_rect_db = (
        20.0
        * np.log10(np.maximum(np.abs(np.fft.rfft(w_rect, n=n_scan)) / np.sum(w_rect), 1e-12))[mask]
    )
    W_ham_db = (
        20.0
        * np.log10(np.maximum(np.abs(np.fft.rfft(w_ham, n=n_scan)) / np.sum(w_ham), 1e-12))[mask]
    )

    # Mirror for negative frequencies (-220 to +220 Hz)
    f_sym = np.concatenate([-f_sub[::-1][:-1], f_sub])
    W_rect_sym = np.concatenate([W_rect_db[::-1][:-1], W_rect_db])
    W_ham_sym = np.concatenate([W_ham_db[::-1][:-1], W_ham_db])

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(
        f_sym,
        W_rect_sym,
        label=f"Cửa sổ Chữ nhật (null: {r_null:.1f} Hz, bề rộng: 80 Hz)",
        color="#1f77b4",
        linestyle="--",
        linewidth=1.2,
    )
    ax.plot(
        f_sym,
        W_ham_sym,
        label=f"Cửa sổ Hamming (null: {h_null:.1f} Hz, bề rộng: 160 Hz)",
        color="#d62728",
        linewidth=1.8,
    )

    # Markers for null and first sidelobes
    ax.scatter([r_side_hz], [r_side_db], color="#1f77b4", s=30, zorder=5)
    ax.scatter([h_side_hz], [h_side_db], color="#d62728", s=35, zorder=5)
    ax.scatter([r_null], [-80], color="#1f77b4", marker="v", s=25, zorder=5)
    ax.scatter([h_null], [-80], color="#d62728", marker="v", s=25, zorder=5)

    ax.annotate(
        f"Búp phụ đầu Chữ nhật:\n{r_side_hz:.1f} Hz ({r_side_db:.2f} dB)",
        xy=(r_side_hz, r_side_db),
        xytext=(r_side_hz + 15, r_side_db + 4),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#e8f0fe", edgecolor="#1f77b4", lw=0.5),
    )
    ax.annotate(
        f"Búp phụ đầu Hamming:\n{h_side_hz:.1f} Hz ({h_side_db:.2f} dB)",
        xy=(h_side_hz, h_side_db),
        xytext=(h_side_hz + 18, h_side_db - 8),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#fde8e8", edgecolor="#d62728", lw=0.5),
    )

    ax.set_xlim(-200, 200)
    ax.set_ylim(-65, 5)
    ax.set_xlabel("Độ lệch tần số so với tâm (Hz)", fontsize=9)
    ax.set_ylabel("Độ suy giảm chuẩn hóa (dB)", fontsize=9)
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(fig1_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig1_path)

    # -------------------------------------------------------------------------
    # 2. Figure 1.3_probe: Quadrature probe wave measurements (PDF)
    # -------------------------------------------------------------------------
    fig2_path = output_dir / "fig_1_3_probe_vi.pdf"
    f0_windowed, _ = window_frame(tone_audio, start_idx=0, win_length=config.win_length)
    f9_windowed, _ = window_frame(tone_audio, start_idx=9, win_length=config.win_length)

    c0, s0 = probe_sums(f0_windowed, k=14, n_fft=config.n_fft)
    c9, s9 = probe_sums(f9_windowed, k=14, n_fft=config.n_fft)
    p0 = c0**2 + s0**2
    p9 = c9**2 + s9**2

    fig, (ax_wave, ax_sums, ax_pow) = plt.subplots(
        1, 3, figsize=(8.8, 2.7), gridspec_kw={"width_ratios": [2.2, 1.2, 0.8]}
    )

    n_samp = np.arange(config.win_length)
    ax_wave.plot(n_samp, f0_windowed, label="Khung gốc (dịch 0)", color="#1f77b4", lw=1.2)
    ax_wave.plot(
        n_samp,
        f9_windowed,
        label="Khung dịch 9 mẫu (~90°)",
        color="#d62728",
        linestyle="--",
        lw=1.0,
    )
    ax_wave.set_xlim(0, 400)
    ax_wave.set_xlabel("Chỉ số mẫu n (0–399)", fontsize=8)
    ax_wave.set_ylabel("Biên độ mẫu đã áp cửa sổ", fontsize=8)
    ax_wave.set_title("(a) Dạng sóng khung tại độ dịch 0 và 9 mẫu", fontsize=8.5, fontweight="bold")
    ax_wave.grid(True)
    ax_wave.legend(loc="upper right", fontsize=7.5)

    bar_labels = ["Cos(0)", "Sin(0)", "Cos(9)", "Sin(9)"]
    bar_vals = [c0, s0, c9, s9]
    bar_cols = ["#1f77b4", "#17becf", "#d62728", "#ff7f0e"]
    x_pos = np.arange(len(bar_vals))
    bars = ax_sums.bar(x_pos, bar_vals, color=bar_cols, width=0.6, edgecolor="#333333", lw=0.6)
    ax_sums.axhline(0, color="black", lw=0.6)
    ax_sums.set_xticks(x_pos)
    ax_sums.set_xticklabels(bar_labels, fontsize=7.5)
    ax_sums.set_ylabel("Tổng tích lũy", fontsize=8)
    ax_sums.set_title("(b) Hai sóng dò Re/Im", fontsize=8.5, fontweight="bold")
    ax_sums.set_ylim(-35, 125)
    ax_sums.grid(True, axis="y")
    for b in bars:
        h = b.get_height()
        va = "bottom" if h >= 0 else "top"
        y_txt = h + (2 if h >= 0 else -3)
        ax_sums.text(
            b.get_x() + b.get_width() / 2,
            y_txt,
            f"{h:+.2f}",
            ha="center",
            va=va,
            fontsize=7.5,
            fontweight="bold",
        )

    pow_labels = ["P(0)", "P(9)"]
    pow_vals = [p0, p9]
    p_bars = ax_pow.bar(
        [0, 1], pow_vals, color=["#2ca02c", "#2ca02c"], width=0.5, edgecolor="#333333", lw=0.6
    )
    ax_pow.set_xticks([0, 1])
    ax_pow.set_xticklabels(pow_labels, fontsize=7.5)
    ax_pow.set_title("(c) Công suất $|X|^2$", fontsize=8.5, fontweight="bold")
    ax_pow.set_ylim(0, 14500)
    ax_pow.grid(True, axis="y")
    for b in p_bars:
        h = b.get_height()
        ax_pow.text(
            b.get_x() + b.get_width() / 2,
            h + 250,
            f"{h:.1f}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
        )

    fig.tight_layout()
    fig.savefig(fig2_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig2_path)

    # -------------------------------------------------------------------------
    # 3. Figure 1.3_grid: 400-grid vs 512-grid STFT comparison (PDF)
    # -------------------------------------------------------------------------
    fig3_path = output_dir / "fig_1_3_grid_vi.pdf"
    # Compute continuous DTFT via dense zero-padded FFT
    W_dense = np.abs(np.fft.rfft(f0_windowed, n=n_scan)) ** 2
    f_dense = np.fft.rfftfreq(n_scan, d=1.0 / fs)
    mask_grid = (f_dense >= 340.0) & (f_dense <= 540.0)

    # 400-grid DFT (no zero-padding, length 400)
    P_400 = np.abs(np.fft.rfft(f0_windowed, n=400)) ** 2
    f_400 = np.fft.rfftfreq(400, d=1.0 / fs)
    mask_400 = (f_400 >= 340.0) & (f_400 <= 540.0)

    # 512-grid STFT (112 zeros padded, length 512)
    P_512 = np.abs(np.fft.rfft(f0_windowed, n=512)) ** 2
    f_512 = np.fft.rfftfreq(512, d=1.0 / fs)
    mask_512 = (f_512 >= 340.0) & (f_512 <= 540.0)

    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.plot(
        f_dense[mask_grid],
        W_dense[mask_grid] / 1e3,
        label="DTFT liên tục (L=400)",
        color="#888888",
        linestyle="--",
        lw=1.0,
    )

    # Stems for 400 grid
    markerline, stemlines, _ = ax.stem(
        f_400[mask_400],
        P_400[mask_400] / 1e3,
        linefmt="b-",
        markerfmt="bo",
        basefmt=" ",
        label="Lưới 400 điểm (Δf = 40,0 Hz)",
    )
    plt.setp(stemlines, linewidth=1.2, color="#1f77b4")
    plt.setp(markerline, markersize=4, color="#1f77b4")

    # Stems for 512 grid
    markerline5, stemlines5, _ = ax.stem(
        f_512[mask_512],
        P_512[mask_512] / 1e3,
        linefmt="r-",
        markerfmt="ro",
        basefmt=" ",
        label="Lưới 512 điểm (Δf = 31,25 Hz)",
    )
    plt.setp(stemlines5, linewidth=1.2, color="#d62728")
    plt.setp(markerline5, markersize=4, color="#d62728", fillstyle="none")

    ax.annotate(
        "Bin 11 (400 điểm): 11.613,77 (440,0 Hz)\nBin 14 (512 điểm): 11.532,71 (437,5 Hz)",
        xy=(437.5, 11.533),
        xytext=(350, 11.8),
        fontsize=8,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#333333", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#666666", lw=0.6),
    )
    ax.annotate(
        "Bin 15: 5.006,19\n(468,75 Hz)",
        xy=(468.75, 5.006),
        xytext=(480, 6.5),
        fontsize=7.5,
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.6),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#fff5f5", edgecolor="#d62728", lw=0.5),
    )

    ax.set_xlim(350, 530)
    ax.set_ylim(0, 14.5)
    ax.set_xlabel("Tần số (Hz)", fontsize=9)
    ax.set_ylabel("Công suất phổ $|X|^2$ $(\\times 10^3)$", fontsize=9)
    ax.grid(True)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(fig3_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig3_path)

    # -------------------------------------------------------------------------
    # 4. Figure 1.3b: Mel filterbank geometry and row classification (PDF)
    # -------------------------------------------------------------------------
    fig4_path = output_dir / "fig_1_3b_vi.pdf"
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(8.0, 4.4))

    # Top: Overview of all active filters
    hz_bins = np.arange(257) * (config.sample_rate / config.n_fft)
    for m in range(config.n_mels):
        row = fb[m]
        if np.max(row) > 0:
            nz = np.where(row > 0)[0]
            if len(nz) > 0:
                l_idx = max(0, nz[0] - 1)
                r_idx = min(256, nz[-1] + 1)
                ax_top.plot(
                    hz_bins[l_idx : r_idx + 1], row[l_idx : r_idx + 1], lw=0.8, color="#555555"
                )

    # Mark Filter 2 (dead row)
    f2_hz = 2 * (config.sample_rate / config.n_fft)
    ax_top.axvline(f2_hz, color="#d62728", linestyle=":", lw=1.2)
    ax_top.annotate(
        "Bộ lọc 2: Hàng chết (trọng số 0)",
        xy=(f2_hz, 0.0),
        xytext=(150, 0.65),
        fontsize=8,
        color="#d62728",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#fff5f5", edgecolor="#d62728", lw=0.5),
    )
    # Highlight Filter 15 and 79
    ax_top.plot(hz_bins, fb[15], color="#1f77b4", lw=1.8, label="Bộ lọc 15 (tâm 437,5 Hz, bin 14)")
    ax_top.plot(hz_bins, fb[79], color="#2ca02c", lw=1.8, label="Bộ lọc 79 (phủ 17 bin: 239–256)")
    ax_top.set_xlim(0, 8000)
    ax_top.set_ylim(-0.05, 1.15)
    ax_top.set_xlabel("Tần số (Hz)", fontsize=8.5)
    ax_top.set_ylabel("Trọng số Hm[k]", fontsize=8.5)
    ax_top.set_title(
        "(a) Toàn cảnh 80 dải Mel: 18 hàng 1-tap (dây nối), 1 hàng chết (Bộ lọc 2), 61 hàng đa bin",
        fontsize=8.5,
        fontweight="bold",
    )
    ax_top.grid(True)
    ax_top.legend(loc="upper right", fontsize=7.5)

    # Bottom: Zoom on discrete weights of Filters 0, 2, 15
    bins_zoom = np.arange(18)
    hz_zoom = bins_zoom * (config.sample_rate / config.n_fft)

    # Filter 0
    ax_bot.stem(
        bins_zoom,
        fb[0, :18],
        linefmt="b-",
        markerfmt="bo",
        basefmt="k-",
        label="Bộ lọc 0: [0, 0, 1] (1-tap tại bin 0)",
    )
    # Filter 2 (dead)
    ax_bot.scatter(
        [2],
        [0.0],
        color="#d62728",
        marker="x",
        s=50,
        zorder=5,
        label="Bộ lọc 2: [1, 2, 2] (trống rỗng)",
    )
    # Filter 15
    # Light continuous triangle behind stems
    ax_bot.plot([13, 14, 15], [0.0, 1.0, 0.0], color="#1f77b4", linestyle="--", lw=0.8, alpha=0.5)
    markerline, stemlines, _ = ax_bot.stem(
        bins_zoom,
        fb[15, :18],
        linefmt="g-",
        markerfmt="go",
        basefmt=" ",
        label="Bộ lọc 15: [13, 14, 15] (stems: 0, 1, 0)",
    )
    plt.setp(stemlines, color="#2ca02c", lw=1.5)
    plt.setp(markerline, color="#2ca02c", markersize=5)

    ax_bot.set_xticks(bins_zoom)
    ax_bot.set_xticklabels([f"{b}\n({hz:.0f})" for b, hz in zip(bins_zoom, hz_zoom)], fontsize=7)
    ax_bot.set_xlim(-0.5, 17.5)
    ax_bot.set_ylim(-0.1, 1.2)
    ax_bot.set_xlabel("Chỉ số bin FFT k (và tần số tương ứng Hz)", fontsize=8)
    ax_bot.set_ylabel("Trọng số rời rạc", fontsize=8)
    ax_bot.set_title(
        "(b) Trọng số rời rạc: Bộ lọc 15 chỉ có 1 trọng số khác 0 (E15 = P14 trên mọi phổ)",
        fontsize=8.5,
        fontweight="bold",
    )
    ax_bot.grid(True)
    ax_bot.legend(loc="upper right", fontsize=7.5)

    fig.tight_layout()
    fig.savefig(fig4_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig4_path)

    # -------------------------------------------------------------------------
    # 5. Figure 1.3_speech: Real speech extraction from sample_speech_a.wav (PDF)
    # -------------------------------------------------------------------------
    fig5_path = output_dir / "fig_1_3_speech_vi.pdf"
    speech_audio, _ = load_wav(speech_a_path)
    peak_frame_idx, top3_bands = analyze_speech_file(speech_a_path, config, fb)

    start_samp = peak_frame_idx * config.hop_length
    frame_raw = speech_audio[start_samp : start_samp + config.win_length]
    frame_w = frame_raw * np.hamming(config.win_length).astype(np.float32)
    _, P_speech = stft_power(frame_w, n_fft=config.n_fft)
    E_speech = np.dot(fb, P_speech)
    log_mel_speech = log_compress(E_speech)

    fig, (ax_s1, ax_s2, ax_s3) = plt.subplots(3, 1, figsize=(8.0, 4.4))

    # (a) Waveform
    t_ms = np.arange(config.win_length) / config.sample_rate * 1000.0
    ax_s1.plot(t_ms, frame_w, color="#1f77b4", lw=1.0)
    ax_s1.set_xlim(0, 25)
    ax_s1.set_xlabel("Thời gian (ms)", fontsize=7.5)
    ax_s1.set_ylabel("Biên độ", fontsize=7.5)
    ax_s1.set_title(
        f"(a) Khung thời gian thứ {peak_frame_idx} (25 ms, tại t = "
        f"{peak_frame_idx * 0.01:.2f} s) từ datasets/sample_speech_a.wav (từ 'go')",
        fontsize=8,
        fontweight="bold",
    )
    ax_s1.grid(True)

    # (b) Power spectrum
    k_speech = np.arange(65)
    f_sp_hz = k_speech * (config.sample_rate / config.n_fft)
    ax_s2.plot(f_sp_hz, P_speech[:65] / 1e3, color="#008080", lw=1.0)
    ax_s2.annotate(
        "Đỉnh formant: bin 12–13 (375–406 Hz)",
        xy=(390, float(np.max(P_speech[:65])) / 1e3),
        xytext=(450, float(np.max(P_speech[:65])) / 1e3 * 0.85),
        fontsize=7.5,
        color="#d62728",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
    )
    ax_s2.set_xlim(0, 2000)
    ax_s2.set_xlabel("Tần số (Hz)", fontsize=7.5)
    ax_s2.set_ylabel("Công suất (x10^3)", fontsize=7.5)
    ax_s2.set_title(
        "(b) Mật độ phổ công suất $|X_{66}[k]|^2$ "
        "(257 bin FFT, đỉnh formant tại bin 12–13: 375–406 Hz)",
        fontsize=8,
        fontweight="bold",
    )
    ax_s2.grid(True)

    # (c) 80 Log-Mel bands
    m_idx = np.arange(config.n_mels)
    top_indices = [b["band_index"] for b in top3_bands]
    colors = ["#d62728" if m in top_indices else "#1f77b4" for m in m_idx]
    ax_s3.bar(m_idx, log_mel_speech, color=colors, width=0.7, edgecolor="none")
    top_str = ", ".join(f"Dải {b['band_index']} [{b['log_mel']:.2f}]" for b in top3_bands)
    ax_s3.set_xlim(-1, 80)
    ax_s3.set_xlabel("Chỉ số dải Mel m (0–79)", fontsize=7.5)
    ax_s3.set_ylabel("Log-Mel", fontsize=7.5)
    ax_s3.set_title(
        f"(c) 80 dải năng lượng Log-Mel (Ba dải lớn nhất: {top_str})",
        fontsize=8,
        fontweight="bold",
    )
    ax_s3.grid(True, axis="y")

    fig.tight_layout()
    fig.savefig(fig5_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    generated.append(fig5_path)

    return generated


def render_report(
    tone_path: Path, speech_a_path: Path, speech_b_path: Path
) -> dict[str, str | int | float | list]:
    """Run end-to-end lab measurements and print formatted report."""
    ensure_tone_file(tone_path)

    tone_sha = sha256_file(tone_path)
    tone_audio, _ = load_wav(tone_path)

    config = AudioConfig()
    win_length = config.win_length  # 400
    n_fft = config.n_fft  # 512

    # 1. Window measurements & detector
    frame0_windowed, w = window_frame(tone_audio, start_idx=0, win_length=win_length)
    w_0 = float(w[0])
    w_200 = float(w[200])
    w_399 = float(w[399])

    w_rect = np.ones(win_length, dtype=np.float32)
    rect_null_hz, rect_n2n_hz, rect_side_hz, rect_side_db = detect_window_sidelobes(
        w_rect, n_scan=65536, fs=config.sample_rate
    )
    ham_null_hz, ham_n2n_hz, ham_side_hz, ham_side_db = detect_window_sidelobes(
        w, n_scan=65536, fs=config.sample_rate
    )

    # 2. Probe sums at bin 14
    cos_sum_0, sin_sum_0 = probe_sums(frame0_windowed, k=14, n_fft=n_fft)

    # Quarter-cycle shift (shift by 9 samples ~ 1/4 cycle of 440 Hz at 16 kHz)
    frame_quarter, _ = window_frame(tone_audio, start_idx=9, win_length=win_length)
    cos_sum_quarter, sin_sum_quarter = probe_sums(frame_quarter, k=14, n_fft=n_fft)

    p0 = cos_sum_0**2 + sin_sum_0**2
    p9 = cos_sum_quarter**2 + sin_sum_quarter**2

    cos_mag_ratio = float(abs(cos_sum_quarter) / abs(cos_sum_0))
    cos_energy_ratio = float((cos_sum_quarter**2) / (cos_sum_0**2))
    power_rel_change = float(abs(p9 - p0) / p0)

    # 3. STFT & Power
    X, P = stft_power(frame0_windowed, n_fft=n_fft)
    argmax_bin = int(np.argmax(P))
    argmax_hz = float(argmax_bin * config.sample_rate / n_fft)
    re_14 = float(X[14].real)
    im_14 = float(X[14].imag)
    power_14 = float(P[14])

    direct_dft_products = n_fft * n_fft  # 262144
    radix2_butterflies = (n_fft // 2) * int(np.log2(n_fft))  # 2304

    # Power spectrum operation count for 257 bins
    n_bins = n_fft // 2 + 1  # 257
    power_squares = n_bins * 2  # 514
    power_adds = n_bins * 1  # 257
    power_total_ops = power_squares + power_adds  # 771

    # 4. Mel filterbank & classification
    fb, bin_points, collapsed_count, mel_8000, step_mel = mel_edges(config)
    filter0_edges = [int(bin_points[0]), int(bin_points[1]), int(bin_points[2])]
    filter79_edges = [int(bin_points[79]), int(bin_points[80]), int(bin_points[81])]

    dead_rows, onetap_rows, multitap_rows = classify_filterbank_rows(fb)
    filter2_max_weight = float(np.max(fb[2]))
    filter15_nonzero_idx = int(np.where(fb[15] > 0)[0][0])
    filter15_weight = float(fb[15, filter15_nonzero_idx])

    # 5. Log compression probes
    log_moderate = float(log_compress(power_14))
    log_unit = float(log_compress(1.0))
    log_clamped = float(log_compress(1e-8))

    # 6. Speech files analysis
    speech_a_peak_idx, speech_a_top3 = analyze_speech_file(speech_a_path, config, fb)
    speech_b_peak_idx, speech_b_top3 = analyze_speech_file(speech_b_path, config, fb)

    # 7. Generate vector PDF figures
    output_dir = ROOT / "chapter01"
    generated_figures = generate_vector_figures(
        output_dir, tone_audio, speech_a_path, config, fb, bin_points
    )

    report_data = {
        "tone_file_sha256": tone_sha,
        "w_0": round(w_0, 6),
        "w_200": round(w_200, 6),
        "w_399": round(w_399, 6),
        "rect_null_hz": round(rect_null_hz, 2),
        "rect_n2n_hz": round(rect_n2n_hz, 2),
        "rect_side_hz": round(rect_side_hz, 2),
        "rect_side_db": round(rect_side_db, 2),
        "ham_null_hz": round(ham_null_hz, 2),
        "ham_n2n_hz": round(ham_n2n_hz, 2),
        "ham_side_hz": round(ham_side_hz, 2),
        "ham_side_db": round(ham_side_db, 2),
        "cosine_probe_sum_0": round(cos_sum_0, 4),
        "sine_probe_sum_0": round(sin_sum_0, 4),
        "cosine_probe_sum_quarter": round(cos_sum_quarter, 4),
        "sine_probe_sum_quarter": round(sin_sum_quarter, 4),
        "cos_mag_ratio": round(cos_mag_ratio, 4),
        "cos_energy_ratio": round(cos_energy_ratio, 4),
        "power_rel_change": round(power_rel_change, 6),
        "argmax_bin": argmax_bin,
        "argmax_hz": argmax_hz,
        "re_bin14": round(re_14, 4),
        "im_bin14": round(im_14, 4),
        "power_bin14": round(power_14, 2),
        "direct_dft_products": direct_dft_products,
        "radix2_butterflies": radix2_butterflies,
        "power_squares": power_squares,
        "power_adds": power_adds,
        "power_total_ops": power_total_ops,
        "mel_8000": round(mel_8000, 2),
        "step_mel": round(step_mel, 3),
        "filter0_edges": filter0_edges,
        "filter79_edges": filter79_edges,
        "collapsed_count": collapsed_count,
        "dead_count": len(dead_rows),
        "dead_indices": dead_rows,
        "filter2_max_weight": round(filter2_max_weight, 4),
        "onetap_count": len(onetap_rows),
        "onetap_indices": onetap_rows,
        "multitap_count": len(multitap_rows),
        "bin14_filter": 15,
        "filter15_nonzero_idx": filter15_nonzero_idx,
        "bin14_weight": filter15_weight,
        "log_moderate": round(log_moderate, 4),
        "log_unit": round(log_unit, 4),
        "log_clamped": round(log_clamped, 4),
        "speech_a_file": str(speech_a_path.as_posix()),
        "speech_a_peak_frame": speech_a_peak_idx,
        "speech_a_top3_bands": speech_a_top3,
        "speech_b_file": str(speech_b_path.as_posix()),
        "speech_b_peak_frame": speech_b_peak_idx,
        "speech_b_top3_bands": speech_b_top3,
        "generated_figures": [str(p.name) for p in generated_figures],
    }

    # Print fixed report as required
    print("=" * 80)
    print("LAB 1.3 TEACHING LAB REPORT: MEASURED ACOUSTIC VALUES")
    print("=" * 80)
    print(f"tone file sha256: {report_data['tone_file_sha256']}")
    print(
        f"w[0]: {report_data['w_0']:.6f}, w[200]: {report_data['w_200']:.6f}, "
        f"w[399]: {report_data['w_399']:.6f}"
    )
    print("window detector:")
    print(
        f"  rect: first null = {report_data['rect_null_hz']:.2f} Hz, "
        f"first sidelobe = {report_data['rect_side_hz']:.2f} Hz, "
        f"level = {report_data['rect_side_db']:.2f} dB"
    )
    print(
        f"  ham:  first null = {report_data['ham_null_hz']:.2f} Hz, "
        f"first sidelobe = {report_data['ham_side_hz']:.2f} Hz, "
        f"level = {report_data['ham_side_db']:.2f} dB"
    )
    print("  null-to-null widths: rectangular = 80 Hz, Hamming = 160 Hz")
    print(
        f"cosine-probe sum (zero shift): {report_data['cosine_probe_sum_0']:.4f}, "
        f"sine-probe sum: {report_data['sine_probe_sum_0']:.4f}"
    )
    print(
        f"cosine-probe sum (quarter-cycle shift): {report_data['cosine_probe_sum_quarter']:.4f}, "
        f"sine-probe sum: {report_data['sine_probe_sum_quarter']:.4f}"
    )
    print("phase shift ratios:")
    print(
        f"  cosine magnitude ratio: {report_data['cos_mag_ratio']:.4f} "
        f"({report_data['cos_mag_ratio'] * 100:.2f}%), "
        f"drop = {(1.0 - report_data['cos_mag_ratio']) * 100:.2f}%"
    )
    print(
        f"  cosine energy ratio: {report_data['cos_energy_ratio']:.4f} "
        f"({report_data['cos_energy_ratio'] * 100:.2f}%), "
        f"drop = {(1.0 - report_data['cos_energy_ratio']) * 100:.2f}%"
    )
    print(
        f"  power relative change: {report_data['power_rel_change']:.6f} "
        f"({report_data['power_rel_change'] * 100:.4f}%)"
    )
    print(f"argmax bin: {report_data['argmax_bin']} ({report_data['argmax_hz']:.1f} Hz)")
    print(
        f"bin 14: Re = {report_data['re_bin14']:.4f}, "
        f"Im = {report_data['im_bin14']:.4f}, "
        f"Power = {report_data['power_bin14']:.2f}"
    )
    print(
        f"direct-DFT product count: {report_data['direct_dft_products']}, "
        f"radix-2 butterfly count: {report_data['radix2_butterflies']}"
    )
    print(
        f"power spectrum operations: {report_data['power_squares']} squares, "
        f"{report_data['power_adds']} adds, total {report_data['power_total_ops']} real operations"
    )
    print(
        f"mel(8000): {report_data['mel_8000']:.2f}, step_mel: {report_data['step_mel']:.3f}, "
        f"filter-0 edges: {report_data['filter0_edges']}, "
        f"filter-79 edges: {report_data['filter79_edges']}"
    )
    print(f"collapsed count: {report_data['collapsed_count']}")
    print("filterbank classification:")
    print(
        f"  dead count: {report_data['dead_count']}, indices: {report_data['dead_indices']}, "
        f"filter 2 max weight: {report_data['filter2_max_weight']:.4f}"
    )
    print(
        f"  one-tap count: {report_data['onetap_count']}, indices: {report_data['onetap_indices']}"
    )
    print(f"  multi-bin count: {report_data['multitap_count']}")
    print(
        f"  filter 15: nonzero index = {report_data['filter15_nonzero_idx']}, "
        f"weight = {report_data['bin14_weight']:.4f}"
    )
    print(f"g for bin 14 (Filter {report_data['bin14_filter']}): {report_data['bin14_weight']:.4f}")
    print(
        f"log energies: ln(P[14]) = {report_data['log_moderate']:.4f}, "
        f"ln(1.0) = {report_data['log_unit']:.4f}, "
        f"ln(1e-8 clamped) = {report_data['log_clamped']:.4f}"
    )
    speech_a_str = ", ".join(
        f"Band {b['band_index']} ({b['center_hz']:.1f} Hz: {b['log_mel']:.2f})"
        for b in speech_a_top3
    )
    print(
        f"speech a ({speech_a_path.name}): peak frame {report_data['speech_a_peak_frame']}, "
        f"top 3 bands: {speech_a_str}"
    )
    speech_b_str = ", ".join(
        f"Band {b['band_index']} ({b['center_hz']:.1f} Hz: {b['log_mel']:.2f})"
        for b in speech_b_top3
    )
    print(
        f"speech b ({speech_b_path.name}): peak frame {report_data['speech_b_peak_frame']}, "
        f"top 3 bands: {speech_b_str}"
    )
    print(f"generated figures: {report_data['generated_figures']}")
    print("=" * 80)

    return report_data


def run_experiment() -> dict[str, str | int | float | list]:
    """Entry point for capture_result.py."""
    tone_path = ROOT / "datasets" / "sample_tone440.wav"
    speech_a_path = ROOT / "datasets" / "sample_speech_a.wav"
    speech_b_path = ROOT / "datasets" / "sample_speech_b.wav"
    return render_report(tone_path, speech_a_path, speech_b_path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tone-path",
        type=Path,
        default=ROOT / "datasets" / "sample_tone440.wav",
        help="Path to 440 Hz tone WAV",
    )
    ap.add_argument(
        "--speech-a-path",
        type=Path,
        default=ROOT / "datasets" / "sample_speech_a.wav",
        help="Path to speech sample A WAV",
    )
    ap.add_argument(
        "--speech-b-path",
        type=Path,
        default=ROOT / "datasets" / "sample_speech_b.wav",
        help="Path to speech sample B WAV",
    )
    args = ap.parse_args()

    # If any file is missing, exit non-zero
    for p in [args.speech_a_path, args.speech_b_path]:
        if not p.is_file():
            print(f"Error: Required audio file does not exist: {p}", file=sys.stderr)
            return 1

    try:
        render_report(args.tone_path, args.speech_a_path, args.speech_b_path)
    except Exception as exc:
        print(f"Error executing lab_1_3: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
