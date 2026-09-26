"""Create a branded SEC filing receipt from a PDF, HTML file, or EDGAR URL."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pymupdf
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from rapidfuzz import fuzz


CHANNEL = Path(__file__).resolve().parents[2]
PAPER = "#EDEAE3"
INK = "#111111"
YELLOW = (242, 194, 48, 153)
SIZE = (1920, 1080)
FPS = 30
DURATION = 6
SCALE = 2
MAX_DOWNLOAD = 30 * 1024 * 1024
EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
TOKENS = re.compile(r"[a-z0-9]+")
NUMBERS = re.compile(r"(?<![a-z0-9])\$?\s*\d[\d,]*(?:\.\d+)?%?", re.IGNORECASE)


@dataclass(frozen=True)
class Match:
    page: int
    start: int
    end: int
    score: float
    excerpt: str
    exact: bool


def tokenize(value: str) -> list[str]:
    return TOKENS.findall(value.casefold().replace("\u00ad", ""))


def numeric_signature(value: str) -> list[str]:
    return [match.group().replace(" ", "").replace(",", "") for match in NUMBERS.finditer(value)]


def browser() -> Path:
    choices = (
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    )
    for path in choices:
        if path.is_file():
            return path
    raise RuntimeError("Installed Chrome or Edge not found; HTML rendering needs an existing browser")


def sec_host(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in {"sec.gov", "www.sec.gov"}


def throttle_sec() -> None:
    """Cap this machine's SEC request starts at five per second across processes."""
    lock = Path(tempfile.gettempdir()) / "deal-postmortem-sec-rate.lock"
    with lock.open("a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            stream.seek(0)
            prior = float(stream.read().decode("ascii") or "0")
            time.sleep(max(0, prior + 0.2 - time.time()))
            stream.seek(0)
            stream.truncate()
            stream.write(str(time.time()).encode("ascii"))
            stream.flush()
        finally:
            stream.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def fetch_edgar(url: str, destination: Path) -> Path:
    if not sec_host(url):
        raise ValueError("--url must be an HTTPS sec.gov filing URL")
    if not urlparse(url).path.lower().startswith("/archives/edgar/data/"):
        raise ValueError("--url must point to a filing under /Archives/edgar/data/")
    load_dotenv(CHANNEL / ".env")
    user_agent = os.getenv("SEC_USER_AGENT", "").strip()
    if not EMAIL.search(user_agent) or len(user_agent.split()) < 2:
        raise ValueError("Set SEC_USER_AGENT='Name contact@example.com' in MA Channel/.env before fetching SEC filings")
    current = url
    for _ in range(4):
        throttle_sec()
        response = requests.get(current,
                                headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
                                timeout=30, stream=True, allow_redirects=False)
        try:
            if 300 <= response.status_code < 400:
                next_url = urljoin(current, response.headers.get("Location", ""))
                if not sec_host(next_url):
                    raise ValueError("SEC redirect left sec.gov; refusing to follow it")
                current = next_url
                continue
            response.raise_for_status()
            is_pdf = "pdf" in response.headers.get("Content-Type", "").lower() or current.lower().endswith(".pdf")
            target = destination / ("filing.pdf" if is_pdf else "filing.html")
            size = 0
            with target.open("wb") as stream:
                for part in response.iter_content(chunk_size=65536):
                    size += len(part)
                    if size > MAX_DOWNLOAD:
                        raise ValueError("Filing exceeds 30 MB safety limit")
                    stream.write(part)
            return target
        finally:
            response.close()
    raise ValueError("Too many SEC redirects")


def print_html(path: Path, destination: Path) -> Path:
    output = destination / "printed.pdf"
    profile = destination / "browser-profile"
    # Keep the filing's visible inline styling, but block scripts and all network resources.
    safe = destination / "offline.html"
    policy = (b'<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
              b'style-src \'unsafe-inline\'; img-src data:">')
    source = path.read_bytes()
    if re.search(br"<head[^>]*>", source, flags=re.IGNORECASE):
        source = re.sub(br"(<head[^>]*>)", lambda found: found.group(1) + policy,
                        source, count=1, flags=re.IGNORECASE)
    else:
        source = policy + source
    safe.write_bytes(source)
    command = [str(browser()), "--headless", "--no-first-run", "--disable-extensions",
               f"--user-data-dir={profile}", "--no-pdf-header-footer", "--timeout=10000",
               f"--print-to-pdf={output}", safe.resolve().as_uri()]
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 0
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=90, creationflags=flags, check=False)
    if result.returncode != 0 or not output.is_file():
        details = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"Installed browser could not print HTML to PDF: {details}")
    return output


def page_units(page: pymupdf.Page) -> list[tuple[str, tuple]]:
    return [(token, word) for word in page.get_text("words", sort=True)
            for token in tokenize(word[4])]


def candidates(document: pymupdf.Document, quote: str) -> tuple[list[Match], dict[int, list[tuple[str, tuple]]]]:
    desired = tokenize(quote)
    if len(desired) < 4:
        raise ValueError("Quote is too short for a safe match; use at least four words")
    query = " ".join(desired)
    query_numbers = numeric_signature(quote)
    anchors = sorted(range(len(desired)), key=lambda index: len(desired[index]), reverse=True)[:4]
    ranked: list[Match] = []
    all_units: dict[int, list[tuple[str, tuple]]] = {}
    for page_number, page in enumerate(document):
        units = page_units(page)
        all_units[page_number] = units
        positions: set[int] = set()
        for index, (token, _) in enumerate(units):
            for anchor in anchors:
                wanted = desired[anchor]
                if token == wanted or (len(wanted) >= 6 and token[:5] == wanted[:5]):
                    start = index - anchor
                    if 0 <= start < len(units):
                        positions.add(start)
        for start in positions:
            best: Match | None = None
            for width in (len(desired) - 1, len(desired), len(desired) + 1):
                end = start + width
                if width < 4 or end > len(units):
                    continue
                passage = " ".join(token for token, _ in units[start:end])
                score = fuzz.ratio(query, passage)
                source_words = " ".join(word[4] for index, (_, word) in enumerate(units[start:end])
                                        if index == 0 or word != units[start + index - 1][1])
                exact = ([token for token, _ in units[start:end]] == desired
                         and numeric_signature(source_words) == query_numbers)
                if best is None or (exact, score) > (best.exact, best.score):
                    best = Match(page_number, start, end, score, passage, exact)
            if best is not None:
                ranked.append(best)
    ranked.sort(key=lambda item: (item.exact, item.score), reverse=True)
    distinct: list[Match] = []
    for item in ranked:
        if not any(item.page == prior.page and
                   max(0, min(item.end, prior.end) - max(item.start, prior.start)) >=
                   min(item.end - item.start, prior.end - prior.start) * 0.5
                   for prior in distinct):
            distinct.append(item)
        if len(distinct) >= 10:
            break
    return distinct, all_units


def closest_lines(document: pymupdf.Document, quote: str) -> list[str]:
    options = []
    for page in document:
        for block in page.get_text("blocks"):
            phrase = " ".join(block[4].split())
            if phrase:
                options.append((fuzz.partial_ratio(quote.casefold(), phrase.casefold()), phrase))
    options.sort(reverse=True)
    return [item[1][:170] for item in options[:3]]


def choose_match(document: pymupdf.Document, quote: str) -> tuple[Match, list[tuple[str, tuple]]]:
    ranked, all_units = candidates(document, quote)
    best = ranked[0] if ranked else None
    second = ranked[1] if len(ranked) > 1 else None
    if best is None or not best.exact or (second and second.exact):
        nearby = [f"{item.score:.1f}%: {item.excerpt[:170]}" for item in ranked[:3]]
        if len(nearby) < 3:
            nearby.extend(closest_lines(document, quote)[:3 - len(nearby)])
        message = "Quote not safely matched. Three closest passages:\n" + "\n".join(
            f"  {index}. {passage}" for index, passage in enumerate(nearby, 1))
        raise ValueError(message)
    return best, all_units[best.page]


def regions(page: pymupdf.Page, units: list[tuple[str, tuple]], match: Match) -> tuple[pymupdf.Rect, list[pymupdf.Rect]]:
    selected = units[match.start:match.end]
    selected_keys = {(word[5], word[6]) for _, word in selected}
    line_rects: dict[tuple[int, int], pymupdf.Rect] = {}
    for word in page.get_text("words", sort=True):
        key = (word[5], word[6])
        box = pymupdf.Rect(word[:4])
        line_rects[key] = line_rects[key] | box if key in line_rects else box
    keys = sorted(line_rects, key=lambda key: (line_rects[key].y0, line_rects[key].x0))
    selected_indices = [index for index, key in enumerate(keys) if key in selected_keys]
    if not selected_indices:
        raise ValueError("Matched words have no visible page coordinates")
    first = max(0, min(selected_indices) - 2)
    last = min(len(keys), max(selected_indices) + 3)
    context = [line_rects[key] for key in keys[first:last]]
    area = context[0]
    for box in context[1:]:
        area |= box
    crop = (area + (-20, -12, 20, 12)) & page.rect
    # Narrow each highlighted line to the selected words, not surrounding text.
    highlights = []
    for key in selected_keys:
        boxes = [pymupdf.Rect(word[:4]) for _, word in selected if (word[5], word[6]) == key]
        box = boxes[0]
        for other in boxes[1:]:
            box |= other
        highlights.append(box)
    highlights.sort(key=lambda box: (box.y0, box.x0))
    return crop, highlights


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    options = (CHANNEL / "brand" / "fonts" / "Inter-Regular.ttf",
               Path("C:/Windows/Fonts/arial.ttf"))
    for path in options:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def infer_label(document: pymupdf.Document, fallback: str) -> str:
    header = "\n".join(document[index].get_text()[:6000]
                       for index in range(min(2, len(document))))
    form = re.search(r"\b(?:FORM\s+)?(8-K|DEF\s*14A|DEFM14A)\b", header, re.IGNORECASE)
    company = (re.search(r"COMPANY CONFORMED NAME\s*:\s*([^\n]+)", header, re.IGNORECASE)
               or re.search(r"^([^\n]{3,90}?)\s*[-–]\s*Form\s+(?:8-K|DEF\s*14A|DEFM14A)",
                            header, re.IGNORECASE | re.MULTILINE))
    date = re.search(r"\b(?:FILED AS OF DATE|Date of Report)\s*:?\s*([^\n]{0,30})", header,
                     re.IGNORECASE)
    year = re.search(r"\b(20\d{2})\b", date.group(1) if date else header[:2000])
    if form and company:
        pieces = [form.group(1).upper().replace(" ", ""), company.group(1).strip()]
        if year:
            pieces.append(year.group(1))
        return " · ".join(pieces)
    return fallback


def page_images(page: pymupdf.Page, highlights: list[pymupdf.Rect]) -> tuple[Image.Image, Image.Image, tuple[int, int]]:
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False)
    plain = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    layer = Image.new("RGBA", plain.size)
    marker = ImageDraw.Draw(layer)
    for box in highlights:
        xy = (round(box.x0 * SCALE) - 3, round(box.y0 * SCALE) + 1,
              round(box.x1 * SCALE) + 3, round(box.y1 * SCALE) - 1)
        marker.rounded_rectangle(xy, radius=4, fill=YELLOW)
    bounds = (round(min(box.x0 for box in highlights) * SCALE),
              round(max(box.x1 for box in highlights) * SCALE))
    return plain, layer, bounds


def snap_crop_to_gaps(plain: Image.Image, crop: pymupdf.Rect) -> pymupdf.Rect:
    """Avoid showing clipped slivers of neighboring lines at crop edges."""
    x0 = max(0, round(crop.x0 * SCALE))
    x1 = min(plain.width, round(crop.x1 * SCALE))

    def clear_edge(point: float, direction: int) -> float:
        target = round(point * SCALE)
        for distance in range(81):
            row = target + direction * distance
            if row < 2 or row + 3 > plain.height:
                continue
            strip = plain.crop((x0, row - 2, x1, row + 3)).convert("L")
            if sum(strip.histogram()[:220]) == 0:
                return row / SCALE
        return point

    return pymupdf.Rect(crop.x0, clear_edge(crop.y0, -1), crop.x1,
                        clear_edge(crop.y1, 1))


def background(label: str) -> Image.Image:
    canvas = Image.new("RGB", SIZE, PAPER)
    shadow = Image.new("RGBA", SIZE)
    ImageDraw.Draw(shadow).rounded_rectangle((137, 138, 1783, 922), radius=5,
                                             fill=(0, 0, 0, 55))
    canvas.paste(shadow.filter(ImageFilter.GaussianBlur(16)), (0, 0),
                 shadow.filter(ImageFilter.GaussianBlur(16)))
    draw = ImageDraw.Draw(canvas)
    draw.text((137, 965), label, font=font(24), fill=INK)
    return canvas


def compose(plain: Image.Image, layer: Image.Image, crop: pymupdf.Rect,
            bounds: tuple[int, int], label: str, seconds: float, base: Image.Image) -> Image.Image:
    zoom = min(1.0, max(0.0, (seconds - 0.3) / 2.4)) ** 3  # ease-in cubic
    full = (0.0, 0.0, float(plain.width), float(plain.height))
    close = (crop.x0 * SCALE, crop.y0 * SCALE, crop.x1 * SCALE, crop.y1 * SCALE)
    window = tuple(round(a + (b - a) * zoom) for a, b in zip(full, close))
    wipe = 1 - (1 - min(1.0, max(0.0, (seconds - 2.7) / 1.8))) ** 3
    marked = plain.copy()
    if wipe > 0:
        limit = round(bounds[0] + (bounds[1] - bounds[0]) * wipe)
        if limit > 0:
            portion = layer.crop((0, 0, limit, layer.height))
            marked.paste(portion, (0, 0), portion)
    excerpt = marked.crop(window)
    excerpt = ImageOps.contain(excerpt, (1610, 730), method=Image.Resampling.LANCZOS)
    card = Image.new("RGBA", (1640, 760), "#FFFFFF")
    card.paste(excerpt, ((1640 - excerpt.width) // 2, (760 - excerpt.height) // 2))
    rotated = card.rotate(0.6, resample=Image.Resampling.BICUBIC, expand=True)
    frame = base.copy()
    frame.paste(rotated, ((SIZE[0] - rotated.width) // 2,
                          138 + (760 - rotated.height) // 2), rotated)
    return frame


def make_video(plain: Image.Image, layer: Image.Image, crop: pymupdf.Rect,
               bounds: tuple[int, int], label: str, output: Path) -> None:
    import shutil

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg not found on PATH")
    command = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "1920x1080", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-threads", "1",
               str(output)]
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 0
    base = background(label)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               creationflags=flags)
    try:
        assert process.stdin is not None
        for frame in range(DURATION * FPS):
            image = compose(plain, layer, crop, bounds, label, frame / FPS, base)
            process.stdin.write(image.tobytes())
        process.stdin.close()
        assert process.stderr is not None
        error = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait() != 0:
            raise RuntimeError(f"FFmpeg failed: {error[-500:]}")
    except BaseException:
        process.kill()
        process.wait()
        raise


def render(source: Path, quote: str, output: Path, label: str | None, video: bool,
           fallback_label: str | None = None) -> tuple[Path, Path | None]:
    with tempfile.TemporaryDirectory(prefix="doc-highlighter-") as directory:
        temporary = Path(directory)
        if source.suffix.lower() in (".html", ".htm"):
            source = print_html(source, temporary)
        elif source.suffix.lower() != ".pdf":
            raise ValueError("Input must be a PDF or HTML file")
        with pymupdf.open(source) as document:
            label = label or infer_label(document, fallback_label or f"Document · {source.stem}")
            match, units = choose_match(document, quote)
            page = document[match.page]
            crop, highlights = regions(page, units, match)
            plain, layer, bounds = page_images(page, highlights)
            crop = snap_crop_to_gaps(plain, crop)
            output.parent.mkdir(parents=True, exist_ok=True)
            base = background(label)
            still = compose(plain, layer, crop, bounds, label, DURATION, base)
            still.save(output)
            movie = output.with_suffix(".mp4") if video else None
            if movie is not None:
                make_video(plain, layer, crop, bounds, label, movie)
            return output, movie


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    origin = parser.add_mutually_exclusive_group(required=True)
    origin.add_argument("--url", help="HTTPS sec.gov filing URL")
    origin.add_argument("--input", type=Path, help="Local PDF or HTML file")
    parser.add_argument("--quote", required=True, help="Exact or near-exact passage, at least four words")
    parser.add_argument("--out", required=True, type=Path, help="1920x1080 PNG output")
    parser.add_argument("--label", help="Form · Company · Year; recommended when filing header is unclear")
    parser.add_argument("--video", action="store_true", help="Also write a same-name six-second MP4")
    args = parser.parse_args()
    try:
        if args.out.suffix.lower() != ".png":
            raise ValueError("--out must end in .png")
        with tempfile.TemporaryDirectory(prefix="edgar-download-") as directory:
            source = fetch_edgar(args.url, Path(directory)) if args.url else args.input
            if not source.is_file():
                raise ValueError(f"Input not found: {source}")
            fallback = (f"SEC filing · {Path(urlparse(args.url).path).name}" if args.url
                        else f"Document · {source.stem}")
            still, movie = render(source, args.quote, args.out, args.label, args.video, fallback)
        print(still)
        if movie:
            print(movie)
    except (OSError, RuntimeError, ValueError, requests.RequestException) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
