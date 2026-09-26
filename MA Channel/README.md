# Deal Postmortem — faceless M&A documentary channel

| File | What |
|---|---|
| `RESEARCH.md` | market research: benchmark channels, title/thumbnail formulas, YouTube policy |
| `PLAN.md` | pipeline, Claude/Codex split, roadmap, decisions |
| `CHANNEL_SETUP.md` | Week 1 manual checklist (accounts, branding upload, voice recording) |
| `brand/` | brand kit (`BRAND.md`), logo/banner/avatar generator |
| `methods/sexy-canvas/` | internal marketing/copy method; never reference its source or terminology in published material |
| `tools/trend_miner/` | weekly outlier-video report → `research/trends/` |
| `tools/thumbnails/` | Template A/B thumbnail generator |
| `tools/voice/` | own-voice narration (Chatterbox). Codex builds it from `CODEX_TASK.md` |
| `videos/<NNN-slug>/` | one folder per episode: dossier, script, storyboard, vo, assets, thumbs, final |

```bash
pip install -r requirements.txt
```
```bash
python tools/trend_miner/mine.py
```
```bash
python tools/thumbnails/make_thumb.py tools/thumbnails/samples.json
```
```bash
python brand/make_logo.py
```
