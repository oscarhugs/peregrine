# Filing receipts highlighter

Render a quoted passage from a local PDF/HTML file or SEC EDGAR URL as a 1920×1080 PNG. `--video` adds a 6-second, 30 fps MP4 with a full-page zoom and left-to-right marker wipe. The CLI uses the **installed Chrome or Edge** for HTML printing, not Playwright or another browser download. Install `MA Channel/requirements.txt` in Python 3.11; FFmpeg on `PATH` is needed only for `--video` (`winget install ffmpeg` on Windows).

```powershell
python tools/doc_highlighter/highlight.py --input filing.pdf --quote "The exact passage to show on screen" --out tools/doc_highlighter/out/receipt.png --label "8-K · Example Co. · 2025" --video
python tools/doc_highlighter/highlight.py --url https://www.sec.gov/Archives/edgar/data/.../filing.htm --quote "The exact passage to show on screen" --out tools/doc_highlighter/out/receipt.png --label "DEF 14A · Example Co. · 2025"
```

For SEC URLs, put `SEC_USER_AGENT="Your Name contact@example.com"` in the ignored `MA Channel/.env` file. Use a real email you monitor; no special Gmail account is needed. The CLI makes one filing request per invocation (plus any SEC-only redirects) and locally caps request starts at five per second; do not run simultaneous EDGAR jobs from the other laptop. A quote is highlighted only when its words and numeric values match after case, non-numeric punctuation, whitespace, and word-separating hyphen normalization. Fuzzy results are suggestions only: if the passage is missing or repeated, the CLI fails and prints up to three closest passages. Verify the quote, label, and source before publication; `--label` is recommended because filing headers vary.

The highlighter renders HTML through the existing browser's print-to-PDF feature, then uses PyMuPDF to locate visible words and rasterize them at 2×. It crops the matched lines plus roughly two lines of context, applies a ~60% Deal Yellow marker, and places the receipt on Paper with a small source label. Generated scratch media belongs in ignored `out/`; committed examples should contain only verified public filings and outputs.

Two verified live EDGAR outputs and their source links are in [examples/README.md](examples/README.md).
