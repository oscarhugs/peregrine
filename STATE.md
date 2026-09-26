# STATE

_Last updated: 2026-09-26_

## In progress

- **Deal Postmortem** (M&A faceless channel, `MA Channel/`): Week 1 Claude parts done; user still owes `CHANNEL_SETUP.md` (Google account/channel, branding, tools, voice recording).
- **Pilot 001 Red Lobster** (`MA Channel/videos/001-red-lobster/`): script **draft 4 approved content-wise** (2,112 words ≈ 14 min): humanized, fact-checked, cold open rewritten per packaging (the $11M vs $190M contrast in the first 10 s), Oscar's practitioner takes added to §03 and §06 (drafted by Claude, approved by Oscar; "cash went to the deal" softened). `packaging.md` done (lead title: "Red Lobster Lost $11M on Shrimp. Its Rent Was $190M."). Left off: storyboard + publish.md done; waiting on hero images and Codex tools.

## Next up

- **[Codex queue]** (Claude maintains this list; Codex reports progress in `STATE.codex.md`): do in order, one per session:
  1. `MA Channel/tools/voice/CODEX_TASK.md`: own-voice narration tool (Chatterbox, runs on Colab/RunPod)
  2. `MA Channel/tools/charts/CODEX_TASK.md`: animated branded charts/deal diagrams
  3. `MA Channel/tools/doc_highlighter/CODEX_TASK.md`: SEC filing highlighter (needs `SEC_USER_AGENT` in `MA Channel/.env`)
  4. `MA Channel/tools/renderer/CODEX_TASK.md`: storyboard.json + vo → rough-cut MP4, SRT, DaVinci FCPXML, assets_todo.md (FFmpeg, laptop-friendly)
- **Pilot 001 next:** 1) Oscar makes hero images per `videos/001-red-lobster/thumbs/HERO_PROMPTS.md` → Claude renders finals (T2 needs a "RENT DUE" overlay added to make_thumb.py); 2) write end card once ep 002 topic is picked; 3) wait for Codex tools (voice → charts → doc_highlighter → renderer) to render. Oscar: record voice reference once the voice tool lands.
- Need from Oscar: email for SEC_USER_AGENT (in `MA Channel/.env`) to fetch the 2014 Darden/ARCP 8-Ks and confirm the $2.1B / $1.5B figures (currently sourced to the Starboard proxy).
- ZoomInfo lead work: see `Zoominfo Scraper/STATE.md` (own repo, own state file).

## Recently done

- 2026-09-26 — Pilot 001: storyboard.json (133 beats, ~14 min, 13 doc quotes verified verbatim), publish.md (3 titles, description, sources, pinned comment, tags), renderer Codex brief (queue #4), thumbnail specs + hero prompts; make_thumb.py got figure_prev + arrow options.
- 2026-09-26 — Red Lobster pilot: 13 verified sources, dossier, script (4 drafts: humanized, fact-checked, packaging-tuned, practitioner takes), packaging + thumbnail drafts. Squad agents created. STATE split per agent (STATE.codex.md + .gitattributes union merge; Codex on codex/* branches with PRs).
- 2026-09-25 — MA Channel: pulled YouTube data for 15 benchmark channels + 12 M&A/PE searches (yt-dlp), thumbnail analysis, wrote research + execution plan.
- 2026-09-25 — Deal Postmortem decisions: independent brand, own voice via Chatterbox (MIT; XTTS/F5 are non-commercial), neutral stance, name Deal Postmortem.
- 2026-09-25 — ZoomInfo scraper: full 606-contact list captured with full emails (486 leads); OCR pipelines for older screenshot batches finished. Details in `Zoominfo Scraper/STATE.md`.
- 2026-09-24 — Created `CLAUDE.md` and `STATE.md` for cross-session memory.

## Notes/decisions

- Repo contains `Website Scrapes/`, `Zoominfo Scraper/` (gitignored here; it has its own repo at github.com/oscarhugs/zoominfo-scraper), and `screenshot-to-code/` (has its own `CLAUDE.md`).
- MA Channel split: Claude = ideas/research/script/storyboard/thumbnail concepts; Codex = code (trend miner, renderer, charts, SEC doc highlighter). 1 high-quality video/week max (YouTube inauthentic-content policy).
- Codex works in this repo too (cloud or a clone on the other computer). It follows `AGENTS.md`. **State is split to avoid merge conflicts:** Claude writes only `STATE.md`, Codex writes only `STATE.codex.md`; both read both on start. Codex works on `codex/<task>` branches → PR → Oscar merges. Claude works on `main`.
- Tooling decisions (2026-09-26): installed MarkItDown (docs→markdown, used with targeted search) and the `humanizer` skill (`.claude/skills/humanizer`, blader/humanizer MIT); run it on every script and description before review. Ponytail goes in Codex only. Skipped: caveman, Jev/Laya, claude-mem, taste-skill/impeccable/awesome-design-md (web UI design; `brand/BRAND.md` covers our design system). Task Observer: revisit after the pilot.
- Squad in `.claude/agents/` (source-fetcher=Haiku; analyst, fact-checker, storyboarder, editor=Sonnet). Lesson: Haiku fetchers wrote summaries from memory when downloads failed, so audit every source file (tool output only, >2 KB, verbatim) before the analyst uses it.
- Packaging uses the internal method in `MA Channel/methods/sexy-canvas/` (canvas → mechanic line → energies → blacklist → 4 U's titles). Internal only; never referenced in published material. Deal Postmortem blacklist: never name a firm as "the killer" in titles/thumbnails, no overclaiming the verdict.
- Token budget (2026-09-26 /usage: Opus 77%, Haiku 15%, Sonnet 8%): start a fresh session per phase; Opus only writes/decides/orchestrates; delegate audits and long reads to Sonnet/Haiku; quick tool questions go to a Sonnet session.
- User's laptop: no NVIDIA GPU (Intel UHD 620, 8 GB RAM), so GPU work (voice, local models) runs on RunPod/Colab.
