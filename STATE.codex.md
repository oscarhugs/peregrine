# STATE (Codex)

_Codex writes only this file. Claude writes `STATE.md` (which holds the Codex queue). Read both on "start"._

_Last updated: 2026-09-26_

## In progress

- Voice tool PR #1 is awaiting Oscar's review/merge; production voice acceptance awaits his recording. Charts are complete on `codex/charts-tool` and ready for PR review.

## Done (newest first; Claude moves these into the queue status in STATE.md)

- 2026-09-26 — Built the chart/deal-diagram CLI with six types, paper/night themes, six fictional example specs, MP4 and still output, documentation, and tests. Rendered all six MP4s locally at 1920×1080/30 fps (4–6 s); five tests pass.
- 2026-09-26 — Added the portable Sexy Canvas guide at `MA Channel/methods/sexy-canvas/`; it is internal-only and must never be named or exposed in published channel materials.
- 2026-09-26 — Added reproducible Python requirements for the chart and document tools plus pinned GPU-only Chatterbox voice requirements; local `MA Channel/.venv` is gitignored.

## Notes/decisions

- SEC highlighter: use the existing browser for HTML rendering and visual QA; do not add Playwright or download a second Chromium runtime.
- Charts: example figures are fictional and labeled as such; replace values and source before publication. Optional brand fonts are absent locally, so the tested renders use Windows fallbacks.
- Resource preference: Oscar does not want full CPU saturation. Keep renders sequential and limit encoder threads (charts FFmpeg defaults to one); use low process priority for longer local jobs.
