"""Select a clean 10–20 second Chatterbox prompt from a longer voice recording."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_DIR = Path(__file__).resolve().parent / "reference"


def select_clip(audio, sample_rate: int, seconds: int = 15):
    import numpy as np

    frame_samples = round(sample_rate * 0.02)
    usable = len(audio) // frame_samples * frame_samples
    if usable < sample_rate * 10:
        raise ValueError("Reference recording must contain at least 10 seconds of audio")
    frames = audio[:usable].reshape(-1, frame_samples)
    rms = np.sqrt(np.mean(frames * frames, axis=1))
    threshold = max(10 ** (-42 / 20), float(np.percentile(rms, 90)) * 0.12)
    voiced = rms > threshold
    active = np.flatnonzero(voiced)
    if not len(active):
        raise ValueError("No speech detected in reference recording")
    start_frame, end_frame = int(active[0]), int(active[-1] + 1)
    window = min(seconds * 50, end_frame - start_frame)
    if window < 500:
        raise ValueError("Less than 10 seconds of speech available after silence trimming")
    best_start = start_frame
    best_score = float("-inf")
    for first in range(start_frame, end_frame - window + 1, 25):
        last = first + window
        segment = rms[first:last]
        speech_fraction = float(np.mean(voiced[first:last]))
        volume = float(np.mean(segment))
        variance = float(np.std(segment))
        clip_fraction = float(np.mean(np.abs(frames[first:last]) >= 0.98))
        edge_energy = float(np.mean(rms[first:first + 5]) + np.mean(rms[last - 5:last]))
        score = speech_fraction * 4 + volume - variance - clip_fraction * 10 - edge_energy
        if score > best_score:
            best_score, best_start = score, first
    first_sample = best_start * frame_samples
    last_sample = min((best_start + window) * frame_samples, len(audio))
    return audio[first_sample:last_sample]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_DIR / "me_full.wav")
    parser.add_argument("--output", type=Path, default=DEFAULT_DIR / "me_ref.wav")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Recording not found: {args.input}")
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is required to convert the recording to mono 24 kHz WAV")
    try:
        import soundfile as sf
    except ImportError:
        parser.error("soundfile is required; install tools/voice/requirements.txt")
    with tempfile.TemporaryDirectory() as temp_dir:
        converted = Path(temp_dir) / "converted.wav"
        command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                   "-i", str(args.input), "-ac", "1", "-ar", "24000", "-c:a", "pcm_s24le", str(converted)]
        subprocess.run(command, check=True)
        audio, rate = sf.read(converted, dtype="float32")
    clip = select_clip(audio, rate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, clip, 24000, subtype="PCM_24")
    print(f"Wrote {args.output} ({len(clip) / 24000:.1f}s, mono 24 kHz)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
