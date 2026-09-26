# Codex task: animated chart and deal-diagram library

Paste this whole file into Codex.

## Goal
Build `tools/charts/`: a Python CLI that renders **branded animated charts as MP4 clips** (1920×1080, 30 fps, 4–10 s) from small JSON specs. These are the channel's signature visuals: stock collapses, debt loads, price paid vs. value later.

## Brand (from `brand/BRAND.md`)
- Colors: Paper `#EDEAE3` bg, Ink `#111111`, Signal Red `#C8102E` (the one accent), Deal Yellow `#F2C230` (dollar figures only), Night `#0E0E10` for the dark variant.
- Fonts: Inter (labels), DM Serif Display (titles), Anton (big numbers), loaded from `brand/fonts/` with fallbacks Arial / Georgia / Impact.
- Style: minimal. No gridlines except a faint baseline, direct labels instead of legends, source line bottom-left in small Inter ("Source: Company 10-K, 2019").
- Every spec accepts `"theme": "paper" | "night"`.

## Chart types (spec `type`)
1. `line_reveal`: a line draws left→right over time (stock price, revenue). Optional `annotations: [{x, label}]` that pop in with a red dot + label as the line reaches them (e.g. "Deal announced").
2. `bar_compare`: 2–5 bars grow in, value counts up (e.g. "Price paid $11.1B" vs "Written down $8.8B").
3. `number_counter`: one huge number counts up/down with a caption ("$1.5B" → "sold the buildings").
4. `stacked_debt`: a stacked bar that builds equity + debt layers (LBO structure), with labels.
5. `deal_flow`: a node diagram. Boxes (companies, funds, lenders) appear, then arrows animate between them with labels ("sells real estate $1.5B", "leases it back"). Layout from spec: `nodes: [{id, label, x, y}]`, `edges: [{from, to, label, delay}]`.
6. `timeline`: horizontal timeline, events appear one by one.

## Tech
- matplotlib + `FuncAnimation` → ffmpeg (or Pillow frames → ffmpeg). No heavy frameworks. ffmpeg on PATH is required; document the Windows install (`winget install ffmpeg`).
- `python tools/charts/render.py spec.json` → MP4 next to the `out` path in the spec. Also `--still` for a single PNG frame (thumbnail/QA).
- Easing: ease-out-cubic on all reveals. Hold the final frame 1.5 s.

## Done when
- `tools/charts/examples/` has one spec per type with made-up but realistic numbers, and running `python tools/charts/render.py tools/charts/examples/*.json` produces 6 MP4s.
- A short README lists the spec fields for each type.
