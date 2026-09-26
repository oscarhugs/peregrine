"""Render Markdown narration to section WAVs using the owner's Chatterbox voice."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


CHANNEL_ROOT = Path(__file__).resolve().parents[2]
REFERENCE = CHANNEL_ROOT / "tools" / "voice" / "reference" / "me_ref.wav"
CACHE = CHANNEL_ROOT / "tools" / "voice" / "out" / "cache"
MODEL_VERSION = "chatterbox-tts-0.1.7"
TAG = re.compile(r"\[(?:VISUAL|SOURCE):[^\]]*\]|\[S\d+\]", re.IGNORECASE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SPACE = re.compile(r"\s+")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[\"'“‘(]*[A-Z0-9])")
ABBREVIATIONS = {"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "e.g.", "i.e.", "u.s.", "u.k."}


@dataclass
class Paragraph:
    text: str
    chunks: list[str]


@dataclass
class Section:
    number: int
    title: str
    paragraphs: list[Paragraph]

    @property
    def text(self) -> str:
        return "\n\n".join(paragraph.text for paragraph in self.paragraphs)

    @property
    def filename(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        return f"{self.number:02d}_{slug or 'section'}.wav"


def sentence_chunks(paragraph: str, limit: int = 250) -> list[str]:
    """Group whole sentences; an unusually long sentence is kept intact."""
    boundaries = []
    start = 0
    for match in SENTENCE_END.finditer(paragraph):
        candidate = paragraph[start : match.start()].strip()
        if candidate.lower().split()[-1] in ABBREVIATIONS:
            continue
        boundaries.append(candidate)
        start = match.end()
    boundaries.append(paragraph[start:].strip())
    chunks: list[str] = []
    for sentence in filter(None, boundaries):
        if chunks and len(chunks[-1]) + 1 + len(sentence) <= limit:
            chunks[-1] += " " + sentence
        else:
            chunks.append(sentence)
    return chunks


def parse_script(path: Path) -> list[Section]:
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = COMMENT.sub("", path.read_text(encoding="utf-8"))
    sections: list[Section] = []
    current: Section | None = None
    lines: list[str] = []

    def finish_paragraph() -> None:
        nonlocal lines
        if current is not None and lines:
            cleaned = SPACE.sub(" ", " ".join(lines)).strip()
            if cleaned:
                current.paragraphs.append(Paragraph(cleaned, sentence_chunks(cleaned)))
        lines = []

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            finish_paragraph()
            current = Section(len(sections) + 1, stripped[3:].strip(), [])
            sections.append(current)
        elif not stripped:
            finish_paragraph()
        elif stripped.startswith((">", "#", "[VISUAL:", "[SOURCE:")):
            finish_paragraph()
        elif current is not None:
            cleaned = TAG.sub("", stripped).strip()
            if cleaned:
                lines.append(cleaned)
    finish_paragraph()
    return [section for section in sections if section.paragraphs]


def cache_key(text: str, reference_hash: str, exaggeration: float, cfg_weight: float) -> str:
    payload = json.dumps(
        {"model": MODEL_VERSION, "text": text, "reference_sha256": reference_hash,
         "exaggeration": exaggeration, "cfg_weight": cfg_weight},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def render_section(section: Section, model: object, reference_hash: str, args: argparse.Namespace, out_dir: Path) -> dict:
    import numpy as np
    import pyloudnorm as pyln
    import soundfile as sf
    from scipy.signal import resample_poly

    CACHE.mkdir(parents=True, exist_ok=True)
    audio_parts = []
    chunk_times = []
    sample_rate = model.sr
    elapsed = 0.0
    previous_paragraph = False
    for paragraph in section.paragraphs:
        if previous_paragraph:
            gap = np.zeros(round(sample_rate * 0.350), dtype=np.float32)
            audio_parts.append(gap)
            elapsed += len(gap) / sample_rate
        for chunk_index, chunk in enumerate(paragraph.chunks):
            if chunk_index:
                gap = np.zeros(round(sample_rate * 0.150), dtype=np.float32)
                audio_parts.append(gap)
                elapsed += len(gap) / sample_rate
            key = cache_key(chunk, reference_hash, args.exaggeration, args.cfg_weight)
            cached = CACHE / f"{key}.wav"
            if cached.exists():
                audio, rate = sf.read(cached, dtype="float32")
                if rate != sample_rate:
                    raise ValueError(f"Cache sample-rate mismatch: {cached}")
            else:
                wav = model.generate(chunk, audio_prompt_path=str(REFERENCE),
                                     exaggeration=args.exaggeration, cfg_weight=args.cfg_weight)
                audio = wav.detach().cpu().numpy().squeeze().astype(np.float32)
                if audio.ndim != 1 or len(audio) == 0:
                    raise ValueError(f"Invalid model audio for: {chunk!r}")
                sf.write(cached, audio, sample_rate, subtype="PCM_24")
            chunk_times.append({"start": round(elapsed, 3), "end": round(elapsed + len(audio) / sample_rate, 3), "text": chunk})
            audio_parts.append(audio)
            elapsed += len(audio) / sample_rate
        previous_paragraph = True
    stitched = np.concatenate(audio_parts)
    if sample_rate != 48000:
        from math import gcd
        divisor = gcd(sample_rate, 48000)
        stitched = resample_poly(stitched, 48000 // divisor, sample_rate // divisor)
    meter = pyln.Meter(48000)
    loudness = meter.integrated_loudness(stitched)
    if not np.isfinite(loudness):
        raise ValueError(f"Cannot measure loudness for section {section.number}")
    normalized = pyln.normalize.loudness(stitched, loudness, -16.0)
    peak = float(np.max(np.abs(normalized)))
    if peak > 0.999:
        normalized *= 0.999 / peak
        print(f"Warning: section {section.number} peak limited; loudness may be below -16 LUFS", file=sys.stderr)
    out_file = out_dir / section.filename
    sf.write(out_file, normalized, 48000, subtype="PCM_24")
    return {"section": section.number, "title": section.title, "file": out_file.name,
            "duration": round(len(normalized) / 48000, 3), "text": section.text, "chunks": chunk_times}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="videos/<slug>/script.md")
    parser.add_argument("--section", type=int, help="One-based section number to render")
    parser.add_argument("--dry-run", action="store_true", help="Print chunks without importing Chatterbox")
    parser.add_argument("--exaggeration", type=float, default=0.4)
    parser.add_argument("--cfg-weight", type=float, default=0.5)
    args = parser.parse_args()
    if not 0 <= args.exaggeration <= 1 or not 0 <= args.cfg_weight <= 1:
        parser.error("--exaggeration and --cfg-weight must be between 0 and 1")
    try:
        sections = parse_script(args.script)
    except FileNotFoundError as exc:
        parser.error(f"Script not found: {exc}")
    if not sections:
        parser.error("Script has no narrated ## sections")
    if args.section is not None:
        sections = [section for section in sections if section.number == args.section]
        if not sections:
            parser.error("--section is outside the narrated section range")
    for section in sections:
        for paragraph in section.paragraphs:
            for chunk in paragraph.chunks:
                if len(chunk) > 250:
                    print(f"Warning: section {section.number} has a {len(chunk)}-character sentence kept intact", file=sys.stderr)
                if args.dry_run:
                    print(f"[{section.number:02d} {section.title}] {chunk}")
    if args.dry_run:
        return 0
    if not REFERENCE.is_file():
        parser.error(f"Reference missing: {REFERENCE}; run prepare_reference.py first")
    try:
        import torch
        from chatterbox.tts import ChatterboxTTS
    except ImportError as exc:
        parser.error(f"Voice dependencies missing: {exc}; install tools/voice/requirements.txt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("Warning: CUDA unavailable; Chatterbox CPU rendering will be slow", file=sys.stderr)
    model = ChatterboxTTS.from_pretrained(device=device)
    reference_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    out_dir = args.script.resolve().parent / "vo"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    prior = {}
    if args.section is not None and manifest_path.exists():
        prior = {item["section"]: item for item in json.loads(manifest_path.read_text(encoding="utf-8"))["sections"]}
    for section in sections:
        print(f"Rendering {section.number:02d} {section.title}")
        prior[section.number] = render_section(section, model, reference_hash, args, out_dir)
    manifest_path.write_text(json.dumps({"sample_rate": 48000, "target_lufs": -16,
                                        "sections": [prior[n] for n in sorted(prior)]},
                                       indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
