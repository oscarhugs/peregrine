import sys, json, yt_dlp
chans = ["MagnatesMedia","companyman114","ModernMBA","ColdFusion","wallstreetmillennial","LogicallyAnswered","HowMoneyWorks","BusinessCasual","Newsthink","EconomicsExplained","PolyMatter","BarelySociable","Fern-TV","TheSwedishInvestor","MoneyMacro"]
queries = ["worst acquisition in history","private equity destroyed","hostile takeover documentary","merger disaster documentary","leveraged buyout explained","how private equity bought","biggest merger failure","corporate raider documentary","why this acquisition failed","billion dollar acquisition mistake","private equity rollup","activist investor takeover"]
opts={"extract_flat":True,"quiet":True,"ignoreerrors":True}
out={"channels":{},"search":{}}
for c in chans:
    try:
        with yt_dlp.YoutubeDL({**opts,"playlistend":400}) as y:
            info=y.extract_info(f"https://www.youtube.com/@{c}/videos",download=False)
        out["channels"][c]=[{"t":e.get("title"),"v":e.get("view_count"),"d":e.get("duration"),"id":e.get("id")} for e in (info.get("entries") or []) if e]
        print(c,len(out["channels"][c]),file=sys.stderr)
    except Exception as ex: print(c,"ERR",ex,file=sys.stderr)
for q in queries:
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info=y.extract_info(f"ytsearch40:{q}",download=False)
        out["search"][q]=[{"t":e.get("title"),"v":e.get("view_count"),"d":e.get("duration"),"ch":e.get("channel"),"id":e.get("id")} for e in (info.get("entries") or []) if e]
        print(q,len(out["search"][q]),file=sys.stderr)
    except Exception as ex: print(q,"ERR",ex,file=sys.stderr)
json.dump(out, open("data2.json","w"), indent=1)
