"""Renders the Deal Postmortem logo assets: avatar (800x800), banner (2560x1440), watermark (150x150).

Mark: a stock-price line that climbs, then flatlines like a heart monitor, inside a square. Brand colors per BRAND.md.
    python brand/make_logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PAPER, INK, RED, DARK = (237, 234, 227), (17, 17, 17), (200, 16, 46), (14, 14, 16)


def font(size, names=("fonts/DMSerifDisplay-Regular.ttf", "C:/Windows/Fonts/georgiab.ttf")):
    for n in names:
        p = Path(n) if Path(n).is_absolute() else HERE / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def mark(size, bg=INK, line=PAPER):
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    s = size / 100
    # chart climbs, spikes, crashes, then flatlines (the "postmortem")
    pts = [(12, 70), (24, 62), (32, 66), (42, 50), (50, 56), (58, 30), (64, 78), (70, 58), (74, 58), (88, 58)]
    d.line([(x * s, y * s) for x, y in pts], fill=line, width=max(2, int(6 * s)), joint="curve")
    d.line([(74 * s, 58 * s), (88 * s, 58 * s)], fill=RED, width=max(2, int(6 * s)))
    d.ellipse([(86 * s, 55 * s), (92 * s, 61 * s)], fill=RED)
    return img


def avatar():
    mark(800).save(HERE / "avatar_800.png")


def watermark():
    mark(150).save(HERE / "watermark_150.png")


def banner():
    W, H = 2560, 1440
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # safe area for all devices: 1546x423 centered
    m = mark(260)
    img.paste(m, (W // 2 - 700, H // 2 - 130))
    f = font(150)
    d.text((W // 2 - 400, H // 2 - 120), "Deal Postmortem", font=f, fill=INK)
    fs = font(52, ("fonts/Inter-Regular.ttf", "C:/Windows/Fonts/arial.ttf"))
    d.text((W // 2 - 396, H // 2 + 60), "The deals behind the companies you know.", font=fs, fill=INK)
    d.rectangle([0, H - 24, W, H], fill=RED)
    img.save(HERE / "banner_2560x1440.png")


if __name__ == "__main__":
    avatar()
    watermark()
    banner()
    print("wrote avatar_800.png, watermark_150.png, banner_2560x1440.png")
