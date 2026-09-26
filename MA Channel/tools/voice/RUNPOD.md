# RunPod voice rendering

1. Launch a RunPod PyTorch GPU template with Python 3.11 and a persistent volume. In its terminal, run `git clone https://github.com/oscarhugs/peregrine.git && cd peregrine/MA\ Channel`.
2. Create the environment: `python3.11 -m venv .venv && . .venv/bin/activate && pip install -r tools/voice/requirements.txt`. Install FFmpeg if missing (`apt-get update && apt-get install -y ffmpeg`).
3. Upload your own recording to `tools/voice/reference/me_full.wav` and the approved script to `videos/<slug>/script.md`. Keep both off Git.
4. Run `python tools/voice/prepare_reference.py` and `python tools/voice/voice.py videos/<slug>/script.md`. Check `videos/<slug>/vo/manifest.json` and listen to every WAV.
5. Download `videos/<slug>/vo/`, then stop the pod. Reference recordings, cached chunks, and narration live in ignored paths; do not commit them.
