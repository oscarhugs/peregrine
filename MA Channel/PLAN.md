# M&A Faceless Channel — Build & Execution Plan

Read `RESEARCH.md` first. This file is the plan to execute.

## 1. Positioning

**Channel concept:** *Every great company story is really a deal story.* Documentaries about the acquisitions, buyouts, and mergers behind the brands people know: who bought what, what they paid, how they financed it, and who got rich or ruined.

- **Edge vs. competitors:** we read the primary documents (merger proxies, 10-Ks, bankruptcy filings) and explain deal mechanics (LBO debt, sale-leasebacks, dividend recaps, write-downs) that general channels skip. Real analysis is also what keeps us safe under YouTube's inauthentic-content rules.
- **Tone:** premium editorial rather than clickbait-rage. We are not anti-PE activists; we explain how deals work, both the disasters and the genius moves. Advisors, founders, and finance professionals are high-RPM viewers.
- **Working names** (check handle availability): see §8.
- **Format:** 1 flagship documentary per week (18–30 min), plus 2–3 Shorts cut from each.

## 2. Content pillars (the "new ideas" engine)

The winning formula from the research: **familiar brand + hidden buyer/villain + giant dollar number + consequence to the viewer**. We apply it to deals nobody has done well yet:

| Pillar | Formula | Share |
|---|---|---|
| **Deal Autopsies** | "[Buyer] paid $X for [Brand]. Then it collapsed." | 40% |
| **Who Secretly Owns It** | "The secret company that owns your [breakfast/vet/dentist]" | 25% |
| **The Roll-Up** | "How private equity is buying every [plumber/vet/car wash]" | 20% |
| **Genius Deals / Titans** | "The $1B deal that made $X", dealmaker biographies | 15% |

### First 15 video ideas (verify every fact in research; figures below are hooks to check)
1. **The Company That Secretly Owns Your Breakfast.** JAB Holding (Keurig Dr Pepper, Panera, Krispy Kreme, Pret…). Mirrors MagnatesMedia's 12M "secret company" format.
2. **Red Lobster Wasn't Killed by Endless Shrimp.** The 2014 Golden Gate sale-leaseback → 2024 bankruptcy.
3. **HP Paid $11 Billion for a Company Worth Almost Nothing.** Autonomy, the write-down, and the fraud trial.
4. **The "Merger of Equals" That Wasn't.** Daimler–Chrysler.
5. **Quaker Bought Snapple for $1.7B and Sold It for $300M.**
6. **Microsoft's $7 Billion Nokia Mistake.**
7. **Why Private Equity Is Buying Every Vet Clinic in America.** Ties into the proven "PE touches your life" hits.
8. **The Roll-Up Buying Every Plumber and HVAC Company.** This extends Morning Brew's 1.6M hit, told from the deal side.
9. **Kraft Heinz: How 3G's Cost-Cutting Machine Broke.** The ~$15B write-down.
10. **The Hedge Fund Manager Who Owned Sears Until It Died.** Eddie Lampert.
11. **Bayer Paid $63 Billion for Monsanto. Then Came the Lawsuits.**
12. **Boeing's Real Problem Started With One Merger.** McDonnell Douglas (proven at 625K on a non-business channel).
13. **eBay Bought Skype for $2.6B. Microsoft Paid $8.5B for It.**
14. **The $1 Billion Deal Everyone Laughed At.** Instagram. A "genius deal" counterweight.
15. **Toys R Us: Anatomy of an LBO.** Crowded topic; only do this one with a clearly better deal-mechanics angle.

**Idea engine rule:** every new idea must score ≥ 3 out of 4 on (famous brand · dollar figure · villain/twist · affects the viewer), and the concept must have a proven outlier (≥ 3× channel median) somewhere on YouTube. The trend miner (below) automates the second check.

## 3. The content machine: pipeline and who does what

```
[1 Trend miner] → [2 Idea scoring] → [3 Research dossier] → [4 Script] → [5 Storyboard]
   → [6 Asset generation: VO · visuals · charts · docs] → [7 Assembly/edit] → [8 Thumbnail+title]
   → [9 Publish] → [10 Analytics → feeds back into 1]
```

| # | Stage | Output | Best tool | Why |
|---|---|---|---|---|
| 1 | **Trend miner** | weekly CSV of outlier videos (views ÷ channel median) in business/M&A | **Codex** builds it (Python + yt-dlp; extend `research/pull_youtube_data.py`) | Straight code/automation |
| 2 | **Idea scoring** | ranked idea list + 3 title angles each | **Claude** | Judgment, angle-finding, applying the formula to new territory |
| 3 | **Research dossier** | `dossier.md`: timeline, deal terms, financials, quotes, **every claim with a source URL** | **Claude** (web search + SEC EDGAR via EdgarTools) | Long-document reading (proxies, 10-Ks) and synthesis are Claude's strength |
| 4 | **Script** | 3,000–4,500 words, beat-by-beat, with a cited fact table | **Claude** writes · **human** approves | Long-form narrative voice and pacing; human pass adds the insider take |
| 5 | **Storyboard** | `storyboard.json`: one row per 5–10 s beat (VO line, visual type, prompt/search term, on-screen text, source) | **Claude** | Turning narrative into shot lists is a reasoning task |
| 6a | **Voiceover** | WAV per section | **Chatterbox** (open source, MIT) cloned from your own voice, run locally | $0; needs a GPU (or a rented GPU at ~$0.50/h) |
| 6b | **AI images / b-roll** | stills + 3–6 s motion clips | Image model (OpenAI gpt-image via Codex, Midjourney, or Flux) + Veo/Kling for motion | Claude doesn't generate images; Codex/OpenAI tooling does |
| 6c | **Charts, maps, deal diagrams** | animated charts (stock price, debt load, deal structure) | **Codex** builds a Remotion/matplotlib template library | Code-generated visuals are reusable, and this is our signature look |
| 6d | **Document shots** | highlighted screenshots of real SEC filings/headlines | **Codex** script (render PDF/HTML filing → crop → yellow highlight) | Signature visual: "the receipts" |
| 6e | **Stock/archival** | real footage of brands and places | Storyblocks/Pexels + fair-use news clips (short, commented on) | Real footage beats AI for real companies |
| 7 | **Assembly** | rough cut from storyboard | **Codex** builds the auto-assembler (Remotion or FFmpeg: VO + visuals + captions + music) → **human** polishes in DaVinci/CapCut | Automation gets ~80% there; a human pass keeps it "authentic" |
| 8 | **Thumbnail + title** | 3 thumbnail concepts × 3 titles | **Claude** writes concepts + prompts → image model renders → finish in Photoshop/Canva → YouTube "Test & Compare" A/B | Concept is judgment; rendering is image tooling |
| 9 | **Publish** | description, chapters, sources list, tags, pinned comment | **Claude** drafts · human uploads | Upload manually at first |
| 10 | **Analytics loop** | weekly CTR/retention review → update formula | **Claude** analyzes a YouTube Studio export | Feeds step 1–2 |

**Split in one line:** *Claude = brain* (ideas, research, script, storyboard, thumbnail concepts, QA, analysis). *Codex = factory* (scrapers, render pipeline, chart/document templates, API glue for ElevenLabs/image/video). Either can write code; splitting it this way uses both subscriptions in parallel and plays to each one's strengths.

### Human checkpoints (non-negotiable, ~3–5 h/week)
1. Approve the idea + title.
2. Script review: fact-check the cited table, add 1–2 insider observations per video (this is what makes it original).
3. Final cut review + the "Altered content" disclosure decision.

## 4. Thumbnail system
- **Template A — "Deal Autopsy" (editorial):** light paper texture, the victim brand's logo/product big, the **acquirer's logo physically attached to it** (flag, price tag, puppet strings, shredder), 2–4 words of black text with one red underline. Example: a Red Lobster plate with a sale-leaseback price tag — "They Sold The Building."
- **Template B — "Collapse" (high contrast):** dark background, huge logo cracked or on fire, red down-arrow, the dollar number in yellow ("$11B → $0").
- Always: ≤ 4 words, readable at phone size, one focal object, no AI-fabricated faces of real people (use licensed/real photos or silhouettes).
- Test 3 variants on every upload with YouTube's Test & Compare.

## 5. Compliance guardrails (bake into the pipeline)
- One high-effort video per week. **No mass production.** Vary structure and visuals; avoid a single rigid template voice across every video.
- Every factual claim in the script links to a source in `dossier.md`. Use "alleged" for anything litigated. Companies and PE firms are litigious, so defamation risk is real.
- Disclose via the "Altered content" toggle whenever realistic AI imagery depicts real events or people. Never clone a real person's voice.
- Clips of news/archival footage: short, transformative, commented on (fair use). Prefer licensed stock.
- Keep the voice consistent: one licensed ElevenLabs voice or your own clone.

## 6. Costs (per month, 4 videos)
| Item | Est. |
|---|---|
| Voice (local Chatterbox) | $0 (optional rented GPU ~$5–10) |
| AI video (Veo 3.1 Lite ~$0.05/s; ~2 min of motion per video) | ~$25–50 |
| Image generation | $10–30 |
| Stock footage + music (Storyblocks, Epidemic) | ~$45 |
| Claude + Codex | existing subscriptions |
| **Total** | **~$80–135/mo** |

Revenue illustration: 500K monthly views × ~$10 RPM ≈ $5K/mo in AdSense plus sponsors. Expect 3–9 months before monetization; not guaranteed.

## 7. Execution roadmap

### Week 1 — Foundation
- [x] Channel name: **Deal Postmortem** (@DealPostmortem).
- [x] Brand kit: `brand/BRAND.md`, logo/avatar/banner/watermark, thumbnail templates A & B (`tools/thumbnails/`).
- [x] Repo structure.
- [x] Trend miner (`tools/trend_miner/`). First report: `research/trends/2026-09-25.md`. Built by Claude since it was 80% done during research.
- [x] Voice tool brief for Codex (`tools/voice/CODEX_TASK.md`). Laptop has no NVIDIA GPU → runs on RunPod/Colab.
- [ ] **You:** everything in `CHANNEL_SETUP.md` (create channel, upload branding, tool accounts, record 3–5 min voice reference).
- [ ] **Codex:** build `tools/voice/` from `CODEX_TASK.md`.
- [ ] Optional: install brand fonts into `brand/fonts/` and re-run `brand/make_logo.py`.

### Week 2 — Pilot video #1 end-to-end (manual-heavy on purpose)
- [ ] Pick from ideas #1–3. Claude builds the dossier → script → storyboard.
- [ ] Generate VO + visuals; hand-edit the first cut. Log where the time went.
- [ ] Thumbnail: 3 variants.

### Weeks 3–4 — Automate the pain points
- [ ] Codex: storyboard.json → auto rough-cut renderer (Remotion/FFmpeg + captions).
- [ ] Codex: chart/deal-diagram template library + SEC-document highlighter.
- [ ] Claude: lock prompt templates for dossier, script, storyboard, and thumbnail concepts (as Claude skills/commands in this repo).
- [ ] Publish videos #1–2.

### Month 2–3 — Cadence
- [ ] 1 flagship/week + Shorts. Weekly analytics review (CTR target > 5%, 30-s retention > 70%).
- [ ] Double down on whichever pillar wins; kill the ones that underperform.

### Repo structure
```
MA Channel/
  RESEARCH.md  PLAN.md
  research/             # benchmark data (done)
  tools/
    trend_miner/        # Codex
    renderer/           # Codex — Remotion/FFmpeg assembler
    charts/             # Codex — chart + deal-diagram templates
    doc_highlighter/    # Codex — SEC filing screenshots
  prompts/              # Claude — dossier/script/storyboard/thumbnail templates
  videos/
    001-<slug>/
      dossier.md  script.md  storyboard.json  vo/  assets/  thumbs/  final/
```

## 8. Decisions (locked 2026-09-25)
1. **Independent** brand (not Peregrine-branded).
2. **Voice: clone the user's own voice with an open-source model** (no YouTube disclosure needed for your own voice). The license must allow commercial use:
   - **Chatterbox** (Resemble AI, MIT): zero-shot cloning from ~5–10 s of audio, emotion control. **Primary pick.**
   - **OpenVoice V2** (MIT): fallback.
   - **Avoid for a monetized channel:** XTTS-v2 (CPML, non-commercial, and Coqui has shut down so no license is available) and F5-TTS (weights CC-BY-NC).
   - Codex task: wrap Chatterbox in a local script `tools/voice/` (script section → WAV, chunked, loudness-normalized). Record 2–5 min of clean reference audio.
3. **Neutral** explainer stance on PE and dealmakers.
4. Channel name: pending user pick from the shortlist below. Handles returned 404 (likely free) on 2026-09-25: @TermSheet, @DueDiligence, @TheTakeover, @DealPostmortem, @WhoBoughtIt, @PaperLBO. Taken: DealAutopsy, TheBuyout, ClosingTable, TheDealRoom, BuyoutFiles, ExitMultiple, PremiumPaid.
