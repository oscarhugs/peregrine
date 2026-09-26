"""Thumbnail generator for Deal Postmortem (1280x720).

Two templates from brand/BRAND.md:
  A  "editorial": paper background, hero image, 2-4 words of black serif text, red underline on one word
  B  "collapse":  dark background, hero image, huge white condensed text, yellow dollar figure, red down-arrow

Usage:
    python tools/thumbnails/make_thumb.py spec.json            # one spec or a list of specs
Spec fields:
    template: "A" | "B"
    text:     "They Sold The Building"      (keep to 2-4 words)
    underline: "Sold"                        (A only, optional)
    figure:   "$1.5B"                        (B only, optional)
    figure_prev: "$11M"                      (B only, optional: smaller white figure above, struck through in red)
    arrow:    "down" | "up" | "none"         (B only, default "down")
    hero:     path to a PNG/JPG (transparent PNG cut-outs look best); optional
    hero_side: "right" | "left"              (default right)
    out:      output path
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "brand" / "fonts"

PAPER = (237, 234, 227)
INK = (17, 17, 17)
RED = (200, 16, 46)
YELLOW = (242, 194, 48)
DARK = (14, 14, 16)
WHITE = (250, 250, 247)

# Brand fonts (OFL, drop the TTFs into brand/fonts/) with Windows fallbacks for drafts.
FONTS = {
    "serif": ["DMSerifDisplay-Regular.ttf", "C:/Windows/Fonts/georgiab.ttf"],
    "condensed": ["Anton-Regular.ttf", "C:/Windows/Fonts/impact.ttf"],
    "sans": ["Inter-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"],
}


def font(kind, size):
    for name in FONTS[kind]:
        p = Path(name) if Path(name).is_absolute() else FONT_DIR / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def paper_texture():
    img = Image.new("RGB", (W, H), PAPER)
    noise = Image.effect_noise((W, H), 18).convert("L").filter(ImageFilter.GaussianBlur(0.6))
    return Image.blend(img, Image.merge("RGB", (noise,) * 3), 0.06)


def place_hero(canvas, hero_path, side, max_w, max_h):
    if not hero_path:
        return
    hero = Image.open(hero_path).convert("RGBA")
    hero.thumbnail((max_w, max_h), Image.LANCZOS)
    x = W - hero.width - 40 if side == "right" else 40
    y = (H - hero.height) // 2
    shadow = Image.new("RGBA", hero.size, (0, 0, 0, 0))
    shadow.putalpha(hero.getchannel("A").point(lambda a: int(a * 0.35)))
    canvas.paste(shadow.filter(ImageFilter.GaussianBlur(14)), (x + 12, y + 16), shadow.filter(ImageFilter.GaussianBlur(14)))
    canvas.paste(hero, (x, y), hero)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def fit_text(draw, text, kind, max_w, max_h, start=190, min_size=60):
    size = start
    while size > min_size:
        fnt = font(kind, size)
        lines = wrap(draw, text, fnt, max_w)
        h = len(lines) * size * 1.05
        if h <= max_h and all(draw.textlength(l, font=fnt) <= max_w for l in lines):
            return fnt, lines, size
        size -= 6
    fnt = font(kind, min_size)
    return fnt, wrap(draw, text, fnt, max_w), min_size


def hand_underline(draw, x0, x1, y, width=12):
    # slightly wavy marker stroke
    pts = [(x0 + i * (x1 - x0) / 8, y + (4 if i % 2 else -2)) for i in range(9)]
    draw.line(pts, fill=RED, width=width, joint="curve")


def template_a(spec):
    img = paper_texture().convert("RGBA")
    side = spec.get("hero_side", "right")
    place_hero(img, spec.get("hero"), side, 640, 620)
    d = ImageDraw.Draw(img)
    text_x = 70 if side == "right" else W - 650
    fnt, lines, size = fit_text(d, spec["text"], "serif", 580, 520)
    y = (H - len(lines) * size * 1.05) / 2
    target = (spec.get("underline") or "").lower()
    for line in lines:
        d.text((text_x, y), line, font=fnt, fill=INK)
        if target:
            x = text_x
            for word in line.split():
                w = d.textlength(word, font=fnt)
                if word.lower().strip(".,!?") == target:
                    hand_underline(d, x, x + w, y + size * 1.0)
                x += w + d.textlength(" ", font=fnt)
        y += size * 1.05
    # series bug
    d.rectangle([0, H - 14, W, H], fill=RED)
    return img


def down_arrow(d, x, y, s):
    d.polygon([(x, y), (x + s, y), (x + s, y + s * 1.2), (x + s * 1.6, y + s * 1.2),
               (x + s * 0.5, y + s * 2.4), (x - s * 0.6, y + s * 1.2), (x, y + s * 1.2)], fill=RED)


def up_arrow(d, x, y, s):
    d.polygon([(x, y + s * 2.4), (x + s, y + s * 2.4), (x + s, y + s * 1.2), (x + s * 1.6, y + s * 1.2),
               (x + s * 0.5, y), (x - s * 0.6, y + s * 1.2), (x, y + s * 1.2)], fill=RED)


def template_b(spec):
    img = Image.new("RGBA", (W, H), DARK)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W * 0.45, -200, W + 300, H + 200], fill=(120, 10, 20, 150))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(120)))
    side = spec.get("hero_side", "right")
    place_hero(img, spec.get("hero"), side, 620, 640)
    d = ImageDraw.Draw(img)
    text_x = 60 if side == "right" else W - 660
    top = 70
    if spec.get("figure_prev"):
        fprev = font("condensed", 96)
        d.text((text_x, top), spec["figure_prev"], font=fprev, fill=WHITE)
        pw = d.textlength(spec["figure_prev"], font=fprev)
        d.line([(text_x - 8, top + 64), (text_x + pw + 8, top + 52)], fill=RED, width=12)
        top += 125
    if spec.get("figure"):
        ffig = font("condensed", 150)
        d.text((text_x, top), spec["figure"], font=ffig, fill=YELLOW)
        arrow = {"down": down_arrow, "up": up_arrow}.get(spec.get("arrow", "down"))
        if arrow:
            arrow(d, text_x + d.textlength(spec["figure"], font=ffig) + 30, top + 20, 50)
        top += 190
    fnt, lines, size = fit_text(d, spec["text"].upper(), "condensed", 600, H - top - 60, start=170)
    y = top
    for line in lines:
        d.text((text_x, y), line, font=fnt, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        y += size * 1.05
    return img


def render(spec):
    img = template_a(spec) if spec.get("template", "A").upper() == "A" else template_b(spec)
    out = Path(spec["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=92)
    print(f"wrote {out}")


if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for s in data if isinstance(data, list) else [data]:
        render(s)
