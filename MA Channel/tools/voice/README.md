# Own-voice narration

Requires Python 3.11, FFmpeg, and a recording you own or have permission to clone. GPU rendering is recommended. [Chatterbox](https://github.com/resemble-ai/chatterbox) is MIT licensed.

1. Local preview: from `MA Channel/`, run `py -3.11 tools/voice/voice.py videos/_test/script.md --dry-run`. No model or GPU is needed.
2. Lenovo Legion GPU: create `tools/voice/.venv` with Python 3.11, install Torch/Torchaudio 2.6.0 from the [CUDA 12.4 index](https://docs.pytorch.org/get-started/previous-versions/), then install `tools/voice/requirements.txt`. Put `me_full.wav` in `tools/voice/reference/`; run `prepare_reference.py`, then `voice.py videos/<slug>/script.md` with that venv's Python. Use `--reference path/to/clip.wav` to test another voice.
3. Colab: open `tools/voice/colab_voice.ipynb`, choose a GPU runtime, upload your recording, and run the cells. It downloads a ZIP containing `vo/` and `manifest.json`.
4. RunPod: follow `RUNPOD.md`, then run `python tools/voice/prepare_reference.py` and `python tools/voice/voice.py videos/<slug>/script.md`.

Legion setup from the repo root (PowerShell):

```powershell
uv venv "MA Channel\tools\voice\.venv" --python 3.11
uv pip install --python "MA Channel\tools\voice\.venv\Scripts\python.exe" torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
uv pip install --python "MA Channel\tools\voice\.venv\Scripts\python.exe" -r "MA Channel\tools\voice\requirements.txt"
```

Scripts use `## ` section headings and plain paragraphs. Editor lines (`>`), HTML comments, visual/source tags, and `[S25]`-style source IDs are excluded from speech. Output is 48 kHz mono PCM WAV at a target of -16 LUFS, with a JSON timing manifest that records actual loudness and peak. Peak limiting can leave a section below the target. `--section N` rerenders only a one-based section; unchanged chunks reuse the ignored cache. A sentence over 250 characters is kept whole with a warning.

Reference audio and generated WAVs are ignored by Git. Review the script, reference clip, and every rendered section before production use.
