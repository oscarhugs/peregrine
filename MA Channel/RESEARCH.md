# M&A Faceless Channel — Research (2026-09-25)

Raw data lives in `research/`:
- `channel_top_videos.txt`: top 12 videos for each of 15 benchmark channels, with views and the **outlier multiple** (video views ÷ channel median).
- `ma_search_top_videos.txt`: the top 70 long-form results across 12 M&A/PE search queries.
- `thumbnails_*.jpg`: contact sheets of the top thumbnails.
- `pull_youtube_data.py`: the script that pulled everything (yt-dlp, no API key). Re-run it to refresh.

---

## 1. Faceless channels already doing millions of views

| Channel | Format | Median views/video | Biggest hit |
|---|---|---|---|
| **ColdFusion** | calm documentary, 20–30 min | 807K | Theranos, 12M · WeWork "$47B Disaster", 5.4M |
| **How Money Works** | punchy systems explainer, 10–15 min | 741K | "How The Wolf of Wall Street Scam Actually Worked", 4.8M |
| **Economics Explained** | macro explainer | 667K | "MIT Predicted Society Will Collapse in 2040", 14M |
| **Modern MBA** | deep industry case study, 25–50 min | 600K | "Fried Chicken Wars: The Fall of KFC", 3.5M |
| **Business Casual** | animated business history | 576K | Rockefeller, 5.6M · J.P. Morgan, 5.2M |
| **Company Man** | 11-minute rigid template | 342K | "The Decline of Chuck E. Cheese's…What Happened?", 6.4M |
| **Logically Answered** | tech/business failures | 179K | "From $10B To Nothing: How Wish.com Lost Everything", 1.8M |
| **MagnatesMedia** | cinematic doc, 15–78 min | 170K (recent 20: **642K**) | "The Secret Chinese Company That Owns Everything", 12M |
| **FINAiUS** | finance power documentaries | 691K | "Empire of Shadows" (richest family), 9.2M · Jamie Dimon, 4M |
| **Wall Street Millennial** | skeptical finance | 100K | Richard Branson, 1.6M |

**M&A / private-equity specific hits** (search sweep):
- GEN, "How Private Equity Turns Your Favorite Channels Into Slop": **5.1M**
- More Perfect Union, "Private Equity's Ruthless Takeover of…Housing": **3.9M**
- Wendover, "How Private Equity Consumed America": **2.7M**
- Bloomberg Originals, "How Private Equity Ate Britain": **2.3M**
- MagnatesMedia, "The INSANE Reason That Yahoo! Lost Everything": **1.8M**
- GEN, "How Private Equity Killed Fast Food": **1.6M**
- Morning Brew, "I started a plumbing company to sell it to private equity": **1.6M**
- Atrioc, "The 5 Dumbest Company Buyouts in History": **1.3M**
- Logically Answered, "AT&T's $180 Billion Debt Disaster…What Happened?": **930K**
- Mentour Now, "Boeing's Downfall — the McDonnell Douglas Merger": **625K**

**Takeaway:** the market is proven. PE and "deal gone wrong" stories reliably hit 1–5M views, yet **no faceless channel owns M&A as its core identity**. Existing channels cover it occasionally, and the PE-specific channels (GEN, More Perfect Union) are political/advocacy. That leaves room for a channel with an insider's view of deals.

---

## 2. Reverse-engineered: what's working

### Topics people click
1. **Beloved or familiar brand + decline.** Chuck E. Cheese, Pizza Hut, KFC, Toys R Us, Red Lobster. Nostalgia does the marketing.
2. **A hidden owner / villain.** "The Secret Company That Owns Everything" (12M) and "How PE Consumed America." Viewers love learning that one entity controls things they use.
3. **Huge dollar figure + loss.** "$47B disaster", "$10B to nothing", "$180B debt disaster". The number *is* the hook.
4. **It affects YOU.** Vets, hospitals, housing, fast food, YouTube channels. PE videos that touch viewers' daily lives outperform abstract finance.
5. **Titan biographies.** Rockefeller, J.P. Morgan, Buffett, Icahn, Milken. These are evergreen, and M&A is literally their story.

### Title formulas (with proof)
| Formula | Example & views |
|---|---|
| The Decline of **[Brand]**…What Happened? | Chuck E. Cheese, 6.4M |
| How Private Equity **[Killed/Consumed/Ate] [Thing]** | Consumed America, 2.7M · Killed Fast Food, 1.6M |
| The Secret Company That Owns **[Everything/X]** | 12M |
| **[Brand]** — The $**[N]** Billion Disaster | WeWork, 5.4M |
| From $**[N]** Billion To Nothing: How **[Brand]** Lost Everything | Wish, 1.8M · Dollar Shave Club, 1.3M |
| The Dark Truth / Disturbing History of **[Brand]** | Coca-Cola, 7.6M |
| The (Overdue) Collapse Of **[X]** | Short-term rentals, 3.9M |
| Why **[Brand]** Can't Survive | Crumbl, 2.2M |

### Thumbnail psychology (see `research/thumbnails_*.jpg`)
1. **The brand logo is the hero.** Coca-Cola, Pizza Hut, WeWork, and Yahoo thumbnails are basically a giant logo, because recognition works in 0.2 seconds.
2. **2–4 words of huge text that add *emotion*, not the title:** "DARK TRUTH", "What Happened??", "EXPOSED!", "Don't Trust Them.", "We Give Up".
3. **The acquirer as a visual metaphor.** The best PE thumbnails put the Blackstone logo *onto* the victim: a flag stuck in a burger, a credit card in a shredder, a hand working puppet strings over brand logos, a Toys R Us gravestone. **This is the key M&A device: buyer + victim in one image.**
4. **Two proven palettes:** (a) red/black high contrast with fire and red arrows (Magnates, Logically Answered); (b) premium editorial: light-gray paper texture, black serif text, one red hand-drawn underline (GEN, Wendover, Bloomberg). The editorial look signals "trustworthy journalism" and suits an advisory brand.
5. **Decay cues:** fire, a gravestone, a red down arrow, a cracked logo, an "X" badge.
6. **A real face with eye contact** when the story has a person (Holmes, SBF, Buffett). Use real photos, never AI-faked faces of real people (see compliance).
7. **Series consistency.** Company Man uses an identical template across 400 videos. Viewers recognize the series before they read it.

### Format and length
- The winners run **12–30 min**; flagship docs run 40–78 min. MagnatesMedia's median views *tripled* once it went long and cinematic.
- The structure is consistent: cold-open hook (stakes + number) → the "golden age" → **the deal** → the turn → the collapse → who got rich / who got hurt → lesson.

---

## 3. Platform rules (critical for an AI-powered channel)
- **July 15, 2025:** YouTube renamed "repetitious content" to **"inauthentic content"**. Mass-produced, templated, low-originality AI videos get demonetized, and detection is now at the **channel level**. In January 2026, 16 channels with 35M combined subscribers were terminated.
- **Allowed:** faceless channels with original scripts, real analysis, and a consistent style. AI help with scripts, thumbnails, and non-impersonating voiceover does **not** need disclosure.
- **Must disclose** ("Altered content" toggle): realistic AI footage of real people or real events, and cloned voices of real people.
- **Implication:** the machine must produce **1 excellent video per week, not 5 generic ones.** Human review at script and final cut is mandatory. Our moat is original deal analysis: reading the actual merger proxy, the price paid, the write-down, the debt load.

## 4. Money
- Business/finance RPM: roughly **$8–19 per 1,000 views** (finance up to ~$25). These are directional industry figures, not guarantees.
- Illustration: 500K views/month × $10 RPM ≈ **$5K/month** in AdSense, plus sponsors (fintech, data rooms, investing apps pay well for this audience).
- YouTube Partner Program requires 1,000 subscribers + 4,000 watch hours (12 months). Long docs build watch hours fast.
- **Strategic upside for Peregrine:** the audience includes business owners and executives. A channel run by a firm with real M&A expertise can double as deal-flow and brand building ("thinking of selling? — link in description").

## Sources
- Channel and video stats: pulled directly from YouTube via yt-dlp on 2026-09-25 (`research/`).
- [Top Faceless Business Case Study Channels 2026 — OverseerOS](https://www.overseeros.com/blog/top-faceless-business-case-study-youtube-channels)
- [Faceless Creators Take a Hit As YouTube Cracks Down on AI Slop — Hollywood Reporter](https://www.hollywoodreporter.com/business/digital/faceless-creators-youtube-ai-damage-1236617586/)
- [YouTube Monetization Policy Changes 2026 timeline — AIR Media-Tech](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline)
- [YouTube channel monetization policies — YouTube Help](https://support.google.com/youtube/answer/1311392?hl=en)
- [Disclosing altered or synthetic content — YouTube Blog](https://blog.youtube/news-and-events/disclosing-ai-generated-content/)
- [Highest-paying YouTube niches 2026 — vidIQ](https://vidiq.com/blog/post/most-profitable-youtube-niches/)
- [YouTube RPM Finance Niche 2026 — OutlierKit](https://outlierkit.com/blog/youtube-rpm-finance-niche)
- [ElevenLabs API pricing](https://elevenlabs.io/blog/weve-lowered-api-agents-pricing-and-introduced-pay-as-you-go)
- [AI Video API pricing 2026 (Veo, Kling) — BuildMVPFast](https://www.buildmvpfast.com/api-costs/ai-video)
- [Form DEFM14A dataset — sec-api.io](https://sec-api.io/datasets/form-defm14a-files) · [EdgarTools](https://edgartools.readthedocs.io/en/latest/guides/proxystatement-data-object-guide/)
- [Thumbnail psychology — SkySnail](https://skysnail.io/blog/youtube-thumbnail-psychology)
