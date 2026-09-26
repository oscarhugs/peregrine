# Codex task: storyboard → rough-cut video assembler

Paste this whole file into Codex. It depends on `tools/voice`, `tools/charts`, and `tools/doc_highlighter` (build those first, or stub their calls).

## Goal
Build `tools/renderer/`: a Python CLI that turns `videos/<slug>/storyboard.json` + `vo/` narration into a **rough-cut MP4** plus a **timeline a human can polish in DaVinci Resolve**. It gets the video about 80% of the way there; a human does the final pass (that's also a YouTube authenticity requirement).

## Constraints
- The owner's laptop is weak (Intel UHD 620, 8 GB RAM, no NVIDIA GPU). Use **FFmpeg** driven from Python (subprocess, or `ffmpeg-python`). No Remotion, no headless browser, no MoviePy for the full timeline (too slow and memory-hungry at 14 min). Render per beat, then concat.
- Python 3.11, pinned `tools/renderer/requirements.txt`. FFmpeg on PATH (`winget install ffmpeg`).
- Never commit renders: gitignore `videos/*/build/` and `videos/*/final/`.

## Inputs
1. `videos/<slug>/storyboard.json`. The schema is in `.claude/agents/storyboarder.md`. Each beat has `id` ("03-02"), `section`, `vo`, `est_sec`, `visual{type, brief, prompt, search, chart_spec, doc{source, quote}}`, `on_screen_text`, `source`, and `music` (tension | build | release | silence).
2. `videos/<slug>/vo/manifest.json` from `tools/voice`. It lists one WAV per section, with duration and text. **If it's missing**, fall back to `est_sec` with silent audio, so the cut still renders before the voice exists.
3. Assets in `videos/<slug>/assets/`, named by beat id: `03-02.mp4|.mov|.png|.jpg`. Optional `assets/music/<cue>.mp3`.
4. Brand: `brand/BRAND.md` (colors, fonts in `brand/fonts/`), `brand/watermark_150.png`.

## Beat timing
- Within each section, distribute the section WAV's duration across its beats in proportion to `vo` word count.
- Optional `--align`: use `faster-whisper` (CPU, `small.en`, int8) word timestamps to snap each beat's start to the first word of its `vo`. Fuzzy-match the text; if matching fails, fall back to proportional and warn.

## Visuals by type
| type | how |
|---|---|
| `chart` | call `tools/charts/render.py` with `chart_spec` → cache in `assets/_gen/<id>.mp4` |
| `doc_highlight` | call `tools/doc_highlighter/highlight.py --video` with `doc.source` (resolve the local file via `sources/INDEX.md`) + `doc.quote` → `assets/_gen/<id>.mp4` |
| `title_card` | generate: Paper background, DM Serif Display, Signal Red underline |
| `stock`, `archival`, `photo`, `ai_image`, `ai_motion`, `map` | use `assets/<id>.*` if present. Stills get a slow Ken Burns (1.00→1.08 zoom, random pan direction, seeded by id). Videos are trimmed or looped to the beat length |
| missing asset | **placeholder card**: Night background, beat id + type + `brief` in Inter. The render never fails because an asset is missing |

- Fit the visual to its beat duration. Crossfade 8 frames between beats, and do a hard cut at section boundaries.
- `on_screen_text`: lower-third in Anton, Ink on a Paper bar, in at +0.3 s, out 0.3 s before the beat ends.
- `source`: small Inter line bottom-left ("Source: S25 · Chapter 11 declaration"). Take the label from `sources/INDEX.md`.
- Watermark bottom-right at 60% opacity.

## Audio
- Concatenate the section WAVs; add 0.6 s of silence between sections.
- Music: one bed per contiguous run of the same `music` cue. Duck it under the VO (about -18 dB relative, sidechain or a volume envelope) and fade 1 s on cue changes. `silence` = no music. Missing music file = skip it.
- Master to -14 LUFS integrated, true peak -1 dB.

## Outputs (`videos/<slug>/build/`)
1. `rough_cut.mp4`: 1920×1080, 30 fps, H.264 CRF 20, AAC 192k. With `--preview`: 1280×720, `-preset ultrafast`, for quick checks on the laptop.
2. `captions.srt`: from the VO text and the beat timings (Whisper word timings when `--align` is used). Max 42 characters per line, 2 lines. Not burned in by default; add `--burn-captions` as an option.
3. `timeline.fcpxml`: importable into DaVinci Resolve, with V1 visuals, V2 text overlays, A1 VO, and A2 music, all pointing at the real files (OpenTimelineIO + its FCPXML adapter is fine).
4. `assets_todo.md`: a checklist of every beat still on a placeholder, showing id, type, `brief`, and `search`/`prompt`. This is the human's shopping list.

## CLI
```
python tools/renderer/render.py videos/<slug> [--preview] [--align] [--burn-captions] [--only 03] [--todo-only]
```
- `--only 03` renders one section. `--todo-only` writes `assets_todo.md` and exits.
- Cache per-beat clips by hash (visual file mtime + duration + overlay text) so re-runs only redo changed beats.

## Done when
- `videos/_test/` (reuse the voice tool's test script, plus a hand-written 6-beat storyboard.json using at least 4 visual types) renders `rough_cut.mp4` in `--preview` mode with no real assets (placeholders plus silent audio).
- `python tools/renderer/render.py "videos/001-red-lobster" --preview --todo-only` produces a sensible `assets_todo.md`.
- The FCPXML opens in DaVinci Resolve (free) with all four tracks. Say so in the PR if you couldn't test this.
- A README of 40 lines or fewer covering setup, the CLI, and the asset naming convention.
