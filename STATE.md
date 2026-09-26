# STATE

_Last updated: 2026-09-26_

## In progress

- **Deal Postmortem** (M&A faceless channel, `MA Channel/`): Week 1 Claude parts done; user still owes `CHANNEL_SETUP.md` (Google account/channel, branding, tools, voice recording).
- **Pilot 001 Red Lobster** (`MA Channel/videos/001-red-lobster/`): sources collected + audited (13 verified), `dossier.md` done, `script.md` draft 1 (~1,900 words ≈ 12.5 min) humanized and fact-checked (`factcheck.md`: 0 wrong, all fixes applied). `packaging.md` done (internal canvas, 20 titles → test set #1/#2/#3, 3 thumbnail concepts, text-only drafts in `thumbs/`). **Waiting on Oscar:** review the script + fill the 2 `> OSCAR:` notes (sections 03, 06). Then: storyboarder → publish pass → source/generate thumbnail hero images.

## Next up

- **[Codex queue]** (Claude maintains this list; Codex reports progress in `STATE.codex.md`): do in order, one per session:
  1. `MA Channel/tools/voice/CODEX_TASK.md`: own-voice narration tool (Chatterbox, runs on Colab/RunPod)
  2. `MA Channel/tools/charts/CODEX_TASK.md`: animated branded charts/deal diagrams
  3. `MA Channel/tools/doc_highlighter/CODEX_TASK.md`: SEC filing highlighter (needs `SEC_USER_AGENT` in `MA Channel/.env`)
  4. (later) video assembler: brief comes after Claude defines the storyboard format in Week 2
- Red Lobster pilot: after Oscar's review, run storyboarder (Sonnet) → write video-assembler Codex brief from the storyboard schema → editor publish pass → 3 thumbnails.
- Need from Oscar: email for SEC_USER_AGENT (in `MA Channel/.env`) to fetch the 2014 Darden/ARCP 8-Ks and confirm the $2.1B / $1.5B figures (currently sourced to the Starboard proxy).
- ZoomInfo lead work: see `Zoominfo Scraper/STATE.md` (own repo, own state file).

## Recently done

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
- User's laptop: no NVIDIA GPU (Intel UHD 620, 8 GB RAM), so GPU work (voice, local models) runs on RunPod/Colab.
