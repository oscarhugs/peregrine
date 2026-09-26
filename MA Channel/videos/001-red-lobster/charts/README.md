# Chart specs — 001 Red Lobster

27 of the storyboard's 28 chart beats have a spec here (`<beat-id>.json`). One beat is skipped (see below). Validated with:

```
python tools/charts/render.py videos/001-red-lobster/charts/*.json --still
```

All 27 pass validation and render without overflow (spot-checked 00-02, 03-05, 03-11, 04-11, 05-16, 06-04, 06-07, 06-08, 06-20, 06-21, 07-02, 01-04, 01-05).

Every beat's storyboard `chart_spec` used shapes the actual render tool doesn't support (e.g. multi-value `number_counter.sequence`, per-bar `unit`, pixel-space `deal_flow` coordinates, `edge.delay` up to 1.5, single-bar `bar_compare`). Specs below are re-mapped to the real schema in `tools/charts/README.md`, keeping the same numbers and narrative intent.

| beat | type | what it shows | number source (factcheck.md row) |
|---|---|---|---|
| 00-02 | number_counter | $11M shrimp loss morphs into $190.5M 2023 rent bill | rows 1, 2 |
| 00-06 | number_counter | 17x — rent bill vs. shrimp loss | row 4 (calc) |
| 01-04 | timeline | 1968 founding, 1970 General Mills acquisition | rows 5, 6 |
| 01-05 | timeline | adds 1995 Darden Restaurants spin-off | rows 5, 6, 7 |
| 01-08 | number_counter | 64M guests/year at time of bankruptcy | row 9 |
| 01-09 | number_counter | 20% of North American lobster tails | row 10 |
| 02-02 | **skipped** | Darden stock vs. peer index, 2013 | no verified time series in dossier/factcheck — only the Dec 2013 5.6% stake disclosure (row 12) is sourced, not a price index; inventing index values would violate the numbers-only-from-sources rule |
| 03-05 | deal_flow | Darden → Golden Gate ($2.1B) → ARCP ($1.5B real estate) | rows 14, 15 |
| 03-09 | number_counter | $2.1B price paid for Red Lobster | row 14 (mapped to number_counter — storyboard's single-bar `bar_compare` isn't valid, tool requires 2-5 bars) |
| 03-10 | bar_compare | $2.1B price paid vs. $1.5B real estate sold | rows 14, 15 |
| 03-11 | bar_compare | adds $0.6B implied remainder for the restaurant business | rows 14, 15, 16 (calc) |
| 04-03 | number_counter | $575M Thai Union investment, 2016 | row 20 |
| 04-05 | number_counter | Thai Union's 47% common equity stake | row 22 (mapped to number_counter — storyboard's single-bar `bar_compare` isn't valid) |
| 04-06 | bar_compare | 47% common equity + 100% preferred equity | row 22 |
| 04-11 | line_reveal | Guest count 2019→2023, -30% | row 23 (only the two verified endpoints are plotted — the storyboard's intermediate index points 92/80/74 aren't sourced, so they're omitted rather than invented) |
| 05-06 | number_counter | $11M cost of Endless Shrimp | row 1 |
| 05-15 | number_counter | ~$100M cash on hand, May 2023 | row 31 (mapped to number_counter — storyboard's single-point `line_reveal` isn't valid, tool requires 2+ points) |
| 05-16 | line_reveal | Cash drains from ~$100M to under $30M, ~6 months | row 32 (endpoint plotted at the source's stated bound, $30M — the source says "less than $30 million," not an exact figure; the on-screen number should be read as that ceiling) |
| 05-18 | number_counter | $530M Thai Union write-off, Jan 2024 | row 35 |
| 06-02 | number_counter | $11M shrimp loss, reprised | row 1 |
| 06-04 | number_counter | $190.5M 2023 lease obligations | row 2 (mapped to number_counter — same single-bar issue as 03-09/04-05) |
| 06-07 | bar_compare | $190.5M total rent vs. $64M on underperforming stores | rows 2, 39 |
| 06-08 | bar_compare | $11M shrimp loss vs. $64M underperformer rent (~6x) | rows 1, 39, 40 (calc) |
| 06-15 | timeline | 2014 sale-leaseback → 2023, nine years of rising rent | rows 14, 2 (calc — the "nine years" framing) |
| 06-20 | deal_flow | Red Lobster pays Darden once (2014) and the landlord every year | narrative diagram, no disputed numbers |
| 06-21 | timeline | 2016 Golden Gate sells stake to Thai Union, 2020 full exit | rows 20, 21 |
| 06-22 | number_counter | $530M Thai Union write-off, recap | row 35 — near-duplicate of 05-18 (same number, same source); kept as its own file since the beat replays later in the script |
| 07-02 | number_counter | $2.1B price paid morphs to $1.5B real estate sold | rows 14, 15 |

## Notes

- All 28 chart beats set `"theme": "paper"` explicitly in the storyboard (including section 00 and 05), so every spec here uses `paper`, overriding the default night-for-cold-open/collapse rule per the "unless the storyboard says otherwise" clause.
- `source` fields are short human labels, never S-numbers: `Chapter 11 declaration (J. Tibus), 2024` (S25), `Starboard Value DEFC14A proxy statement, Aug 2014` (S05), `Thai Union statement, reported by Restaurant Dive, Jan 2024` (S24). The render tool prepends its own "Source: " — don't include that prefix in the JSON `source` field (an earlier draft double-prefixed this; fixed).
- Avoid two literal `$` signs in one text field (title/caption/label) — matplotlib's mathtext parses paired `$...$` as math and mangles the text (found and fixed on 05-16's title, which originally read "From ~$100M to under $30M").
- `bar_compare` needs 2-5 bars and `line_reveal` needs 2+ points; several storyboard beats (03-09, 04-05, 05-15, 06-04) called for a single value and were remapped to `number_counter` instead of being forced into an invalid shape.
- 02-02 is the only fully skipped beat.

## Validation

Rendered with system Python 3.14 (no `.venv` existed in `MA Channel/`; `matplotlib`/`numpy` installed directly). All 27 specs pass `render.py --still` with no errors. Stills only were rendered per instructions — no MP4s.
