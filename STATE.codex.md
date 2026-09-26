# STATE (Codex)

_Codex writes only this file. Claude writes `STATE.md` (which holds the Codex queue). Read both on "start"._

_Last updated: 2026-09-26_

## In progress

- Voice tool GPU acceptance check: CLI, reference preparation, Colab notebook, RunPod instructions, and local tests are implemented on `codex/voice-tool`; run the `_test` notebook on a GPU after merge to verify real Chatterbox output and `manifest.json`.

## Done (newest first; Claude moves these into the queue status in STATE.md)

- 2026-09-26 — Built the Chatterbox narration CLI, reference selector, Colab/RunPod run paths, and sample script; local dry-run and five CPU-side tests pass.
- 2026-09-26 — Added the portable Sexy Canvas guide at `MA Channel/methods/sexy-canvas/`; it is internal-only and must never be named or exposed in published channel materials.
- 2026-09-26 — Added reproducible Python requirements for the chart and document tools plus pinned GPU-only Chatterbox voice requirements; local `MA Channel/.venv` is gitignored.

## Notes/decisions

- Voice: `chatterbox-tts==0.1.7` requires `torch==2.6.0` and `torchaudio==2.6.0`; GPU model loading was not attempted on the Intel laptop. The script parser also removes `[S25]`-style source IDs from the current pilot.
- SEC highlighter: use the existing browser for HTML rendering and visual QA; do not add Playwright or download a second Chromium runtime.
