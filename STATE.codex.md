# STATE (Codex)

_Codex writes only this file. Claude writes `STATE.md` (which holds the Codex queue). Read both on "start"._

_Last updated: 2026-09-26_

## In progress

- Voice tool owner-voice acceptance check: local GPU smoke test passed on the Codex Lenovo Legion RTX 2060 (6 GB) using a synthetic, non-owner reference. Rerun with Oscar's recording and listen before production use.

## Done (newest first; Claude moves these into the queue status in STATE.md)

- 2026-09-26 — Built the Chatterbox narration CLI, reference selector, Colab/RunPod run paths, and sample script. Five CPU-side tests and a real local GPU render passed; the sample output is 48 kHz mono PCM with a timing manifest. The synthetic-reference sample peaked at 0.999 and measured -18.75 LUFS after peak limiting against a -16 LUFS target.
- 2026-09-26 — Added the portable Sexy Canvas guide at `MA Channel/methods/sexy-canvas/`; it is internal-only and must never be named or exposed in published channel materials.
- 2026-09-26 — Added reproducible Python requirements for the chart and document tools plus pinned GPU-only Chatterbox voice requirements; local `MA Channel/.venv` is gitignored.

## Notes/decisions

- Voice: `chatterbox-tts==0.1.7` requires `torch==2.6.0` and `torchaudio==2.6.0`. This install also needs `setuptools<81` for Perth's `pkg_resources` import. The script parser removes `[S25]`-style source IDs from the current pilot.
- Hardware correction: Oscar uses two laptops. This Codex Lenovo Legion has an RTX 2060; the separate Claude laptop has no NVIDIA GPU. Local GPU testing is possible here.
- SEC highlighter: use the existing browser for HTML rendering and visual QA; do not add Playwright or download a second Chromium runtime.
