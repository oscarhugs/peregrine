"""Trend miner: finds outlier videos (views far above their channel's median) in business/M&A.

Usage:
    pip install yt-dlp
    python tools/trend_miner/mine.py            # uses config.json next to this file
    python tools/trend_miner/mine.py --quick    # channels only, skip searches

Writes research/trends/YYYY-MM-DD.csv and YYYY-MM-DD.md (top outliers, M&A-relevant first).
"""
import argparse
import csv
import datetime as dt
import json
import statistics
import sys
from pathlib import Path

import yt_dlp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT_DIR = ROOT / "research" / "trends"
YDL_OPTS = {"extract_flat": True, "quiet": True, "no_warnings": True, "ignoreerrors": True}


def fetch(url, limit):
    with yt_dlp.YoutubeDL({**YDL_OPTS, "playlistend": limit}) as ydl:
        info = ydl.extract_info(url, download=False)
    return [e for e in (info or {}).get("entries") or [] if e]


def row(e, channel, median, source):
    views = e.get("view_count") or 0
    return {
        "title": e.get("title"),
        "channel": channel,
        "views": views,
        "channel_median": int(median) if median else "",
        "outlier_x": round(views / median, 1) if median else "",
        "minutes": round((e.get("duration") or 0) / 60),
        "source": source,
        "url": f"https://www.youtube.com/watch?v={e.get('id')}",
    }


def mine_channels(cfg):
    rows, medians = [], {}
    for handle in cfg["channels"]:
        entries = [e for e in fetch(f"https://www.youtube.com/@{handle}/videos", cfg["uploads_per_channel"])
                   if e.get("view_count") and (e.get("duration") or 0) >= cfg["min_duration_sec"]]
        if not entries:
            print(f"  ! no data for @{handle}", file=sys.stderr)
            continue
        median = statistics.median(e["view_count"] for e in entries)
        name = entries[0].get("channel") or handle
        medians[name] = median
        rows += [row(e, name, median, f"channel:@{handle}") for e in entries]
        print(f"  @{handle}: {len(entries)} videos, median {median:,.0f}", file=sys.stderr)
    return rows, medians


def mine_queries(cfg, medians):
    rows = []
    for q in cfg["queries"]:
        for e in fetch(f"ytsearch{cfg['results_per_query']}:{q}", cfg["results_per_query"]):
            if (e.get("duration") or 0) < cfg["min_duration_sec"] or not e.get("view_count"):
                continue
            ch = e.get("channel")
            rows.append(row(e, ch, medians.get(ch), f"search:{q}"))
        print(f"  search '{q}' done", file=sys.stderr)
    return rows


def is_ma(title, keywords):
    t = (title or "").lower()
    return any(k in t for k in keywords)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip search queries")
    args = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))

    rows, medians = mine_channels(cfg)
    if not args.quick:
        rows += mine_queries(cfg, medians)

    dedup = {}
    for r in rows:
        dedup.setdefault(r["url"], r)
    rows = list(dedup.values())
    for r in rows:
        r["ma_relevant"] = is_ma(r["title"], cfg["ma_keywords"])
    rows.sort(key=lambda r: (-(r["outlier_x"] or 0), -r["views"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.date.today().isoformat()
    csv_path = OUT_DIR / f"{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    thr = cfg["outlier_threshold"]
    outliers = [r for r in rows if r["outlier_x"] and r["outlier_x"] >= thr]
    big_search = sorted([r for r in rows if not r["outlier_x"] and r["views"] >= 1_000_000],
                        key=lambda r: -r["views"])
    lines = [f"# Trend report {stamp}", "",
             f"Outliers = views >= {thr}x the channel's median (last {cfg['uploads_per_channel']} uploads).", ""]
    for label, subset in [("M&A-relevant outliers", [r for r in outliers if r["ma_relevant"]]),
                          ("Other outliers (steal the format, not the topic)", [r for r in outliers if not r["ma_relevant"]][:25]),
                          ("1M+ search hits from other channels", big_search[:25])]:
        lines += [f"## {label}", "", "| x | views | min | channel | title |", "|---|---|---|---|---|"]
        for r in subset:
            title = (r["title"] or "").replace("|", "/")
            lines.append(f"| {r['outlier_x'] or '-'} | {r['views']:,} | {r['minutes']} | {r['channel']} | [{title}]({r['url']}) |")
        lines.append("")
    md_path = OUT_DIR / f"{stamp}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {csv_path} and {md_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
