# STATE

_Last updated: 2026-09-25_

## In progress

- **Deal Postmortem** (M&A faceless channel, `MA Channel/`): Week 1 in progress. Claude's parts are done (brand kit, thumbnail templates, trend miner + first report, Codex voice brief). Waiting on the user (`CHANNEL_SETUP.md`: create channel, upload branding, tool accounts, voice recording) and Codex (`tools/voice/CODEX_TASK.md`).

## Next up

- Deal Postmortem Week 2: pilot video #1 end-to-end. Pick from PLAN.md ideas #1–3 (JAB 'secretly owns your breakfast', Red Lobster sale-leaseback, HP–Autonomy). Claude writes prompts/ templates + dossier → script → storyboard.
- ZoomInfo lead work: see `Zoominfo Scraper/STATE.md` (own repo, own state file).

## Recently done

- 2026-09-25 — MA Channel: pulled YouTube data for 15 benchmark channels + 12 M&A/PE searches (yt-dlp), thumbnail analysis, wrote research + execution plan.
- 2026-09-25 — Deal Postmortem decisions: independent brand, own voice via Chatterbox (MIT; XTTS/F5 are non-commercial), neutral stance, name Deal Postmortem.
- 2026-09-25 — ZoomInfo scraper: full 606-contact list captured with full emails (486 leads); OCR pipelines for older screenshot batches finished. Details in `Zoominfo Scraper/STATE.md`.
- 2026-09-24 — Created `CLAUDE.md` and `STATE.md` for cross-session memory.

## Notes/decisions

- Repo contains `Website Scrapes/`, `Zoominfo Scraper/` (gitignored here; it has its own repo at github.com/oscarhugs/zoominfo-scraper), and `screenshot-to-code/` (has its own `CLAUDE.md`).
- MA Channel split: Claude = ideas/research/script/storyboard/thumbnail concepts; Codex = code (trend miner, renderer, charts, SEC doc highlighter). 1 high-quality video/week max (YouTube inauthentic-content policy).
- User's laptop: no NVIDIA GPU (Intel UHD 620, 8 GB RAM), so GPU work (voice, local models) runs on RunPod/Colab.
