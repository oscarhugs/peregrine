# Own-voice narration

Requires Python 3.11, FFmpeg, and a recording you own or have permission to clone. GPU rendering is recommended. [Chatterbox](https://github.com/resemble-ai/chatterbox) is MIT licensed.

1. Local preview: from `MA Channel/`, run `python tools/voice/voice.py videos/_test/script.md --dry-run`. No model or GPU is needed.
2. Colab: open `tools/voice/colab_voice.ipynb`, choose a GPU runtime, upload your recording, and run the cells. It downloads a ZIP containing `vo/` and `manifest.json`.
3. RunPod: follow `RUNPOD.md`, then run `python tools/voice/prepare_reference.py` and `python tools/voice/voice.py videos/<slug>/script.md`.

Scripts use `## ` section headings and plain paragraphs. Editor lines (`>`), HTML comments, visual/source tags, and `[S25]`-style source IDs are excluded from speech. Output is 48 kHz mono PCM WAV at a target of -16 LUFS, with a JSON timing manifest. `--section N` rerenders only a one-based section; unchanged chunks reuse the ignored cache. A sentence over 250 characters is kept whole with a warning.

Reference audio and generated WAVs are ignored by Git. Review the script, reference clip, and every rendered section before production use.
