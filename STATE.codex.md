# STATE (Codex)

_Codex writes only this file. Claude writes `STATE.md` (which holds the Codex queue). Read both on "start"._

_Last updated: 2026-09-26_

## In progress

- Voice tool owner-voice acceptance: local GPU smoke test passed on the Codex Lenovo Legion RTX 2060 (6 GB) using a synthetic reference. Rerun with Oscar's recording and listen before production use.

## Done (newest first; Claude moves these into the queue status in STATE.md)

- 2026-09-26 — Built the FFmpeg storyboard rough-cut CLI with beat caching, placeholder/asset checklist, chart and document adapters, section VO timing, captions, preview MP4, and four-lane FCPXML. Seven tests pass; six-beat preview and pilot `--todo-only` pass. DaVinci import remains untested because Resolve is not installed here.
- 2026-09-26 — Built and live-validated the SEC receipt highlighter on L3Harris's 2026 8-K and McGraw Hill's 2026 DEF 14A. Committed both verified PNG examples and a six-second 8-K MP4 to `codex/doc-highlighter` / PR #3. Contact details remain only in ignored local `.env`.
- 2026-09-26 — Built the Chatterbox narration CLI, reference selector, Colab/RunPod run paths, and sample script. Five CPU-side tests and a real local GPU render passed; the sample output is 48 kHz mono PCM with a timing manifest. The synthetic-reference sample peaked at 0.999 and measured -18.75 LUFS after peak limiting against a -16 LUFS target.
- 2026-09-26 — Built the chart/deal-diagram CLI with six types, paper/night themes, six fictional example specs, MP4 and still output, documentation, and tests. Rendered all six MP4s locally at 1920×1080/30 fps (4–6 s); five tests pass.
- 2026-09-26 — Added the portable Sexy Canvas guide at `MA Channel/methods/sexy-canvas/`; it is internal-only and must never be named or exposed in published channel materials.
- 2026-09-26 — Added reproducible Python requirements for the chart and document tools plus pinned GPU-only Chatterbox voice requirements; local `MA Channel/.venv` is gitignored.

## Notes/decisions

- Voice: `chatterbox-tts==0.1.7` requires `torch==2.6.0` and `torchaudio==2.6.0`. This install also needs `setuptools<81` for Perth's `pkg_resources` import. The script parser removes `[S25]`-style source IDs from the current pilot.
- Hardware correction: Oscar uses two laptops. This Codex Lenovo Legion has an RTX 2060; the separate Claude laptop has no NVIDIA GPU. Local GPU testing is possible here.
- SEC highlighter: use the existing browser for HTML rendering and visual QA; do not add Playwright or download a second Chromium runtime.
- SEC highlighter: installed Chrome prints local HTML with network resources blocked; SEC requests use a declared User-Agent, SEC-only redirects, and a local cross-process rate cap. Fuzzy passages are suggestions only; automatic highlights require normalized exact words and numeric values.
- Charts: example figures are fictional and labeled as such; replace values and source before publication. Optional brand fonts are absent locally, so the tested renders use Windows fallbacks.
- Resource preference: Oscar does not want full CPU saturation. Keep renders sequential and limit encoder threads (charts FFmpeg defaults to one); use low process priority for longer local jobs.
- Renderer: the `_test` preview's synthetic voice plus silence measures -15.1 LUFS and -1.0 dBTP after AAC against a -14/-1 target; final mastering still needs a listening and loudness check with owner VO. Generated media remains ignored.
