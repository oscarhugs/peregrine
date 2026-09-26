# Codex task: voice generation tool (Chatterbox, own-voice clone)

Paste this whole file into Codex.

## Goal
Build `tools/voice/` in this repo: a CLI that turns a video script into narration WAVs in the channel owner's cloned voice, using **Chatterbox TTS** (Resemble AI, **MIT license**: commercial use OK). Do not use XTTS-v2 (non-commercial CPML) or F5-TTS pretrained weights (CC-BY-NC).

## Constraints
- The owner's laptop has **no NVIDIA GPU** (Intel UHD 620, 8 GB RAM). The tool must run on a **rented GPU** (RunPod or Google Colab). Provide both:
  1. `voice.py`: the CLI (runs anywhere with CUDA; falls back to CPU with a warning).
  2. `colab_voice.ipynb`: a notebook that clones the repo (or uploads files), installs deps, runs `voice.py`, and zips the outputs for download.
  3. `RUNPOD.md`: short steps for running it on a RunPod PyTorch template.
- Python 3.11. Pin versions in `tools/voice/requirements.txt` (`chatterbox-tts`, `torchaudio`, `pydub` or `soundfile`, `pyloudnorm`).
- `tools/voice/reference/` and `tools/voice/out/` must be gitignored (the owner's voice must never be pushed).

## Input
- Reference audio: `tools/voice/reference/me_full.wav` (3–5 min). Add a `prepare_reference.py` that trims silence, converts to mono 24 kHz, and cuts the best clean 10–20 s clip → `reference/me_ref.wav` (Chatterbox needs a short clip).
- Script: `videos/<slug>/script.md`. Sections start with `## ` headings. Narration is plain paragraphs. Ignore lines starting with `>` (editor notes), `[VISUAL: ...]` / `[SOURCE: ...]` bracket tags, and HTML comments.

## Behavior
- Split each section into sentence chunks (≤ ~250 chars, never mid-sentence) and synthesize each with the reference voice. Expose `--exaggeration` (default 0.4) and `--cfg-weight` (default 0.5).
- Stitch chunks with 150 ms gaps (350 ms between paragraphs), then loudness-normalize to **-16 LUFS**, 48 kHz WAV.
- Output: `videos/<slug>/vo/NN_<section-slug>.wav`, plus `vo/manifest.json` listing each file, its duration, and the text (the video assembler uses this for timing and captions).
- `--section N` re-renders a single section; `--dry-run` prints the chunks without synthesizing.
- Cache per-chunk audio by a hash of (text + settings) so re-runs after small script edits only redo changed chunks.

## Done when
- `python tools/voice/voice.py videos/_test/script.md --dry-run` works locally without a GPU.
- The Colab notebook produces `vo/` + `manifest.json` for `videos/_test/script.md` (create a 2-section, ~150-word test script about any historic merger).
- The README in `tools/voice/` explains the three run modes in under 30 lines.
