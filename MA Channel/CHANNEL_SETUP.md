# Week 1 — Channel setup checklist (you do these; I can't create accounts)

## 1. Create the channel (≈20 min)
- [ ] Use a **new Google account dedicated to the channel** (keeps it independent of Peregrine and easy to hand off or sell later).
- [ ] YouTube → Create a channel → **Name:** `Deal Postmortem` → **Handle:** `@DealPostmortem` (available as of 2026-09-25; claim it now).
- [ ] Studio → Settings → Channel → Advanced: country = United States, not made for kids.
- [ ] Verify the phone number (unlocks custom thumbnails and videos > 15 min).

## 2. Branding (files in `brand/`)
- [ ] Profile picture: `brand/avatar_800.png`
- [ ] Banner: `brand/banner_2560x1440.png`
- [ ] Video watermark: `brand/watermark_150.png` (display: entire video)
- [ ] Optional now, better later: install the brand fonts (see `brand/BRAND.md`) and re-run `python brand/make_logo.py`.

## 3. Channel description (paste)
> Every company you know was shaped by a deal. Deal Postmortem takes apart the acquisitions, mergers, and buyouts behind famous brands: what was paid, how it was financed, what went right, what went wrong, and who walked away rich.
>
> Documentaries built from primary sources: merger filings, annual reports, court records. No hype, no agenda. Just the deal.
>
> New episode every week.

**Keywords (Studio → Settings → Channel):** mergers and acquisitions, private equity, business documentary, leveraged buyout, corporate history, company collapse, business case study, finance explained

## 4. Upload defaults (Studio → Settings → Upload defaults)
- [ ] Category: **Education** (or News & Politics for timely deals)
- [ ] Description template:
  ```
  {one-line hook}

  Chapters:
  {chapters}

  Sources:
  {sources}

  Deal Postmortem explains how deals work. Nothing here is investment advice.
  ```
- [ ] Comments: hold potentially inappropriate comments for review.

## 5. Tool accounts
| Tool | Plan | Needed by |
|---|---|---|
| **RunPod** (or Google Colab Pro) | pay-as-you-go GPU, ~$0.30–0.70/h | Week 2 (voice): your laptop has no NVIDIA GPU |
| Image generation (ChatGPT/OpenAI images or Midjourney) | existing ChatGPT plan works to start | Week 2 |
| Veo or Kling (AI motion b-roll) | pay-as-you-go | Week 2 |
| Storyblocks (stock video) + Epidemic Sound (music) | monthly | Week 2 |
| DaVinci Resolve (free) or CapCut | free | Week 2 |

Put any API keys in a local `MA Channel/.env` file (it's gitignored). **Never paste keys into chat.**

## 6. Record your voice reference (≈15 min)
Needed by Codex's voice tool (`tools/voice/CODEX_TASK.md`).
- [ ] Quiet room, soft furnishings, phone or USB mic 15–20 cm from your mouth, no music or fans.
- [ ] Read **3–5 minutes** of documentary-style narration in the tone you want (calm, confident). Any Wikipedia article about a merger works.
- [ ] Export WAV (or high-quality M4A) → save as `tools/voice/reference/me_full.wav`. The folder is gitignored, so your voice stays off GitHub.
