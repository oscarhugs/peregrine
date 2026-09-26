# Verified EDGAR examples

Both examples were fetched from public SEC filing URLs on 2026-09-26 using the
highlighter's declared User-Agent. The contact value lives only in the ignored
`MA Channel/.env`; it is not needed to inspect these committed outputs.

| Output | Filing | Passage checked |
| --- | --- | --- |
| `l3harris_2026_8k.png` and `.mp4` | [L3Harris Form 8-K, filed 2026-08-17](https://www.sec.gov/Archives/edgar/data/202058/000020205826000066/hrs-20260816.htm) | "The SMS and CSD segments comprise approximately 80% of the Company's total revenue." |
| `mcgraw_hill_2026_def14a.png` | [McGraw Hill DEF 14A, filed 2026-06-25](https://www.sec.gov/Archives/edgar/data/1951070/000119312526282816/d145263ddef14a.htm) | "As of June 4, 2026, Platinum retains ownership and control of approximately 86.4% of the voting power of the Company's outstanding common stock" |

The CLI matched each quote to one visible passage, preserving the `80%` and
`86.4%` figures. The PNGs were visually checked for quote placement and clean
line boundaries. The optional 8-K video is H.264, 1920×1080, 30 fps, 180
frames, and 6 seconds.
