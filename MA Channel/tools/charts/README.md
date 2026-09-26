# Animated charts

From `MA Channel/`, install `requirements.txt` into Python 3.11 and put FFmpeg on `PATH` (`winget install ffmpeg` on Windows). Render one or several JSON specs:

```powershell
python tools/charts/render.py tools/charts/examples/*.json
python tools/charts/render.py tools/charts/examples/deal_flow.json --still
```

The CLI expands globs on Windows and renders specs one at a time; FFmpeg encoding is capped at one thread to keep CPU use modest. Each spec needs `type`, `title`, `source`, and `out`; `theme` is `paper` (default) or `night`, and `duration` is 4–10 seconds (default 5). `out` is an `.mp4` path relative to the spec file; `--still` writes a same-name `.png` at the final frame. Video is H.264 MP4, 1920×1080, 30 fps, with ease-out-cubic reveals and a 1.5-second final hold. The source line is always bottom-left. Examples use fictional data and say so; replace both numbers and source before publication.

| `type` | Additional fields |
|---|---|
| `line_reveal` | `points: [{x, y}, ...]` with increasing numeric `x` and nonnegative `y`; optional `annotations: [{x, label}]` at numeric x positions. |
| `bar_compare` | `bars: [{label, value}, ...]` (2–5, nonnegative); optional zero-based `highlight` index (default 0). |
| `number_counter` | Numeric `from`, `to`, and `caption`. |
| `stacked_debt` | `layers: [{label, value}, ...]` (2–4, nonnegative), in bottom-to-top order. A label containing “debt” gets the red layer. |
| `deal_flow` | `nodes: [{id, label, x, y}]` (2–5), `edges: [{from, to, label, delay}]`; positions are normalized frame coordinates (`x` 0.12–0.88, `y` 0.22–0.75); `delay` is 0–1 (default 0), controlling edge order after nodes appear. |
| `timeline` | `events: [{date, label}, ...]` (2–6), in display order. |

Value charts (`line_reveal`, `bar_compare`, `number_counter`, `stacked_debt`) also accept `prefix` and `suffix` strings plus `decimals` (0–3, default 0). Use `prefix: "$"` for dollar amounts; night-theme dollar figures render in Deal Yellow. Keep titles, source lines, node labels, and annotation labels concise so they fit the frame. Brand fonts load from `brand/fonts/` when present, otherwise Windows Arial/Georgia/Impact fallbacks are used.
