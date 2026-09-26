# Storyboard rough-cut renderer

Python 3.11 and FFmpeg/FFprobe on PATH are required. From `MA Channel/` on
Windows, run `py -3.11 -m venv .venv`, activate with
`.\.venv\Scripts\Activate.ps1`, then run
`python -m pip install -r tools/renderer/requirements.txt`. Optional CPU word
alignment: `python -m pip install -r tools/renderer/requirements-align.txt`
(downloads `small.en` on first `--align` use; it may take time on the other laptop).

```powershell
python tools/renderer/render.py videos/_test --preview
python tools/renderer/render.py videos/001-red-lobster --todo-only --preview
python tools/renderer/render.py videos/001-red-lobster --only 03 --preview
```

`storyboard.json` supplies the beats. Put licensed images or video in
`videos/<slug>/assets/` using the beat ID, e.g. `03-02.png`, `.jpg`, `.mp4`, or
`.mov`. Optional music files are `assets/music/tension.mp3`, `build.mp3`, and
`release.mp3`. Local source PDFs/HTML for document highlights belong in
`sources/raw/S25...pdf` (not committed). Charts and document clips are cached
under ignored `assets/_gen/`; failed generation becomes a labeled placeholder.

The ignored `build/` folder contains `rough_cut.mp4`, `captions.srt`,
`timeline.fcpxml`, and `assets_todo.md`. `--preview` renders 1280×720 with one
FFmpeg encoding thread; default is 1920×1080. Missing VO uses estimated beat
timings and silence. `--align` attempts CPU `small.en` word timing and warns
before falling back. `--burn-captions` burns SRT into the MP4. The XML points
to generated clips, lower-third PNGs, section VO, and a music bed; relink media
if moved, and verify the import in DaVinci before editing.
