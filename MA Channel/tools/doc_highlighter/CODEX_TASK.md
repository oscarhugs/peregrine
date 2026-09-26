# Codex task: SEC filing "receipts" highlighter

Paste this whole file into Codex.

## Goal
Build `tools/doc_highlighter/`: given a **SEC EDGAR filing URL** (or a local PDF/HTML) and a **quote**, produce a clean branded image, plus an optional short zoom-in MP4, of that passage with the quote highlighted. The video uses these as proof on screen: "Here's what they actually told shareholders."

## Behavior
- Input via CLI: `python tools/doc_highlighter/highlight.py --url <edgar-url> --quote "exact or near-exact text" --out videos/<slug>/assets/doc_01.png [--video]`
- Fetch HTML filings from sec.gov with a proper User-Agent header (SEC requires `Name email` format; read it from `.env` as `SEC_USER_AGENT`) and stay under 10 requests/second.
- Render the page region with Playwright (Chromium headless) at 2× scale. Locate the quote with fuzzy matching (whitespace/hyphenation tolerant, e.g. `rapidfuzz`) and wrap it in a highlight: Deal Yellow `#F2C230` at ~60% opacity, like a real marker.
- Crop to the paragraph plus ~2 lines of context above and below. Put it on a Paper `#EDEAE3` 1920×1080 canvas with a subtle drop shadow and slight rotation (±1°). Add a small label bottom-left: form type, company, date (e.g. "DEFM14A · Red Lobster Seafood Co. · 2014"), parsed from the filing header when possible or passed via `--label`.
- `--video`: a 6 s MP4 (1920×1080, 30 fps): start on the full-page view, ease-in zoom to the paragraph, and the highlight "wipes" across the quote left→right.
- Also support local PDFs (PyMuPDF: search the text, draw the highlight, render the page region).
- If the quote isn't found, fail with the 3 closest matches so a human can fix it. **Never highlight the wrong text.**

## Done when
- Works on 2 real public filings (pick any recent 8-K and DEF 14A from EDGAR full-text search) with quotes of your choice; outputs are committed to `tools/doc_highlighter/examples/`.
- README with setup (`pip install`, `playwright install chromium`) and usage.
