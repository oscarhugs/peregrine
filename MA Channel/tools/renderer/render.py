"""Assemble a storyboard and section narration into a reviewable rough cut."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont
from rapidfuzz import fuzz


CHANNEL = Path(__file__).resolve().parents[2]
FPS = 30
PAUSE = 18  # 0.6 seconds
FADE = 8
PAPER = "#EDEAE3"
INK = "#111111"
NIGHT = "#0E0E10"
RED = "#C8102E"
VIDEO_EXT = (".mp4", ".mov")
IMAGE_EXT = (".png", ".jpg", ".jpeg")


@dataclass
class Beat:
    raw: dict
    frames: int = 0
    start: int = 0
    base: Path | None = None
    baked: Path | None = None
    overlay: Path | None = None
    placeholder_reason: str | None = None
    word_times: list[tuple[float, float]] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def section(self) -> str:
        return self.raw["section"]

    @property
    def visual(self) -> dict:
        return self.raw["visual"]

    def field(self, key: str, default: str = "") -> str:
        return str(self.raw.get(key) or self.visual.get(key) or default)


@dataclass
class Section:
    name: str
    beats: list[Beat]
    frames: int = 0
    start: int = 0
    wav: Path | None = None
    audio: Path | None = None


def run(command: list[str], *, cwd: Path | None = None) -> None:
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 0
    environment = os.environ.copy()
    environment.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                       MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, creationflags=flags,
                            env=environment, check=False)
    if result.returncode:
        raise RuntimeError(f"{' '.join(command[:4])} failed: {result.stderr[-1400:]}")


def ffmpeg(*args: str) -> None:
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
         "-filter_complex_threads", "1", *args])


def probe_duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                            capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def ftime(frames: int) -> str:
    return f"{frames}/{FPS}s"


def sec(frames: int) -> str:
    return f"{frames / FPS:.6f}"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def write_if_changed(path: Path, content: str) -> None:
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = {
        "serif": [CHANNEL / "brand/fonts/DMSerifDisplay-Regular.ttf", Path("C:/Windows/Fonts/georgiab.ttf")],
        "condensed": [CHANNEL / "brand/fonts/Anton-Regular.ttf", Path("C:/Windows/Fonts/impact.ttf")],
        "sans": [CHANNEL / "brand/fonts/Inter-Regular.ttf", Path("C:/Windows/Fonts/arial.ttf")],
    }
    for path in candidates[name]:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def paragraphs(draw: ImageDraw.ImageDraw, value: str, box: tuple[int, int, int, int],
               face: ImageFont.FreeTypeFont, fill: str, spacing: int = 10) -> None:
    left, top, right, bottom = box
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=face) > right - left:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    line_height = (face.getbbox("Ag")[3] - face.getbbox("Ag")[1]) + spacing
    for index, line in enumerate(lines):
        y = top + index * line_height
        if y + line_height > bottom:
            break
        draw.text((left, y), line, font=face, fill=fill)


def card(beat: Beat, target: Path, size: tuple[int, int], placeholder: bool) -> None:
    width, height = size
    image = Image.new("RGB", size, NIGHT if placeholder else PAPER)
    draw = ImageDraw.Draw(image)
    scale = width / 1920
    if placeholder:
        draw.rectangle((0, height - round(22 * scale), width, height), fill=RED)
        draw.text((round(100 * scale), round(180 * scale)),
                  f"{beat.id}  /  {beat.visual['type'].upper()}",
                  font=font("sans", round(34 * scale)), fill=PAPER)
        paragraphs(draw, beat.visual.get("brief", "Asset needed"),
                   (round(100 * scale), round(290 * scale), width - round(100 * scale),
                    height - round(120 * scale)), font("serif", round(64 * scale)), PAPER)
    else:
        title = beat.field("on_screen_text") or beat.visual.get("brief", beat.section)
        paragraphs(draw, title, (round(100 * scale), round(280 * scale),
                                width - round(100 * scale), height - round(160 * scale)),
                   font("serif", round(96 * scale)), INK, round(20 * scale))
        draw.rectangle((round(100 * scale), height - round(150 * scale),
                        round(460 * scale), height - round(136 * scale)), fill=RED)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def source_index(video: Path) -> dict[str, dict[str, str]]:
    index = video / "sources/INDEX.md"
    if not index.is_file():
        return {}
    sources = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 7 and re.fullmatch(r"S\d+", cells[0]):
            sources[cells[0]] = {"title": cells[2], "url": cells[5], "file": cells[6]}
    return sources


def source_label(beat: Beat, sources: dict[str, dict[str, str]]) -> str:
    source = beat.field("source") or str(beat.visual.get("doc", {}).get("source", ""))
    if not source:
        return ""
    title = sources.get(source, {}).get("title", "")
    return textwrap.shorten(f"Source: {source} · {title}", width=84, placeholder="…")


def overlay_image(beat: Beat, sources: dict[str, dict[str, str]], target: Path,
                  size: tuple[int, int], lower_third: bool = False) -> None:
    width, height = size
    scale = width / 1920
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if lower_third:
        text = beat.field("on_screen_text")
        draw.rounded_rectangle((round(96 * scale), height - round(232 * scale),
                                width - round(96 * scale), height - round(122 * scale)),
                               radius=round(5 * scale), fill=PAPER)
        draw.rectangle((round(96 * scale), height - round(232 * scale),
                        round(108 * scale), height - round(122 * scale)), fill=RED)
        paragraphs(draw, text, (round(145 * scale), height - round(217 * scale),
                                width - round(125 * scale), height - round(125 * scale)),
                   font("condensed", round(58 * scale)), INK)
    else:
        label = source_label(beat, sources)
        if label:
            draw.text((round(45 * scale), height - round(57 * scale)), label,
                      font=font("sans", round(25 * scale)), fill=PAPER)
        watermark = CHANNEL / "brand/watermark_150.png"
        if watermark.is_file():
            with Image.open(watermark) as original:
                mark = original.convert("RGBA")
                side = round(92 * scale)
                mark.thumbnail((side, side))
                mark.putalpha(mark.getchannel("A").point(lambda alpha: round(alpha * 0.6)))
                image.alpha_composite(mark, (width - mark.width - round(30 * scale),
                                             height - mark.height - round(24 * scale)))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def find_asset(video: Path, beat: Beat) -> Path | None:
    for suffix in (*VIDEO_EXT, *IMAGE_EXT):
        path = video / "assets" / f"{beat.id}{suffix}"
        if path.is_file():
            return path
    return None


def normalize_chart(beat: Beat, output: Path, duration: float) -> dict:
    spec = dict(beat.visual.get("chart_spec") or {})
    kind = spec.get("type")
    if not kind:
        raise ValueError("no chart_spec")
    spec.update(title=beat.field("on_screen_text") or beat.visual.get("brief", beat.id),
                source=str(spec.get("source_line", "Storyboard source")),
                duration=min(10, max(4, duration)), out=output.name)
    if kind == "number_counter" and "sequence" in spec:
        sequence = spec["sequence"]
        if len(sequence) < 2:
            raise ValueError("number sequence needs two values")
        spec["from"], spec["to"] = sequence[0]["value"], sequence[-1]["value"]
        spec["caption"] = sequence[-1]["label"]
        if abs(spec["to"]) >= 1_000_000:
            spec["from"] /= 1_000_000
            spec["to"] /= 1_000_000
            spec["prefix"], spec["suffix"] = "$", "M"
            spec["decimals"] = 1
    elif kind == "line_reveal" and "series" in spec:
        if len(spec["series"]) != 1:
            raise ValueError("multi-series line chart is not supported by charts tool")
        spec["points"] = [{"x": index, "y": value}
                          for index, value in enumerate(spec["series"][0]["values"])]
    elif kind == "bar_compare" and len(spec.get("bars", [])) < 2:
        raise ValueError("single-bar comparison cannot be rendered without inventing data")
    elif kind == "deal_flow":
        nodes = [dict(item) for item in spec.get("nodes", [])]
        for item in nodes:
            if item["x"] > 1:
                item["x"] = min(0.88, max(0.12, item["x"] / 1000))
            if item["y"] > 1:
                item["y"] = min(0.75, max(0.22, item["y"] / 600))
        spec["nodes"] = nodes
        spec["edges"] = [dict(item, delay=min(1, item.get("delay", 0)))
                         for item in spec.get("edges", [])]
    return spec


def doc_origin(video: Path, beat: Beat, sources: dict[str, dict[str, str]]) -> tuple[str, str]:
    source_id = beat.visual.get("doc", {}).get("source", "")
    item = sources.get(source_id, {})
    raw = video / "sources/raw"
    for suffix in (".pdf", ".html", ".htm"):
        for path in raw.glob(f"{source_id}*{suffix}"):
            if path.is_file():
                return "--input", str(path)
    listed = video / "sources" / item.get("file", "")
    if listed.is_file() and listed.suffix.lower() in (".pdf", ".html", ".htm"):
        return "--input", str(listed)
    url = item.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname in ("sec.gov", "www.sec.gov") and \
            parsed.path.startswith("/Archives/edgar/data/"):
        return "--url", url
    raise ValueError(f"no local PDF/HTML for {source_id}; place it in sources/raw/")


def visual_source(video: Path, beat: Beat, sources: dict[str, dict[str, str]],
                  build: Path, size: tuple[int, int]) -> Path:
    override = find_asset(video, beat)
    if override:
        return override
    kind = beat.visual["type"]
    generated = video / "assets/_gen"
    generated.mkdir(parents=True, exist_ok=True)
    if kind == "title_card":
        target = build / "cards" / f"{beat.id}-{digest((beat.raw, size))}.png"
        if not target.is_file():
            card(beat, target, size, False)
        return target
    if kind == "chart":
        target = generated / f"{beat.id}.mp4"
        spec = normalize_chart(beat, target, beat.frames / FPS)
        data = json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
        spec_path = generated / f"{beat.id}.json"
        changed = not spec_path.exists() or spec_path.read_text(encoding="utf-8") != data
        write_if_changed(spec_path, data)
        if changed or not target.is_file():
            run([sys.executable, str(CHANNEL / "tools/charts/render.py"), str(spec_path)])
        return target
    if kind == "doc_highlight":
        target = generated / f"{beat.id}.mp4"
        flag, origin = doc_origin(video, beat, sources)
        quote = beat.visual.get("doc", {}).get("quote", "")
        key = digest((flag, origin, quote))
        stamp = generated / f"{beat.id}.hash"
        if not target.is_file() or not stamp.is_file() or stamp.read_text() != key:
            run([sys.executable, str(CHANNEL / "tools/doc_highlighter/highlight.py"),
                 flag, origin, "--quote", quote, "--out", str(target.with_suffix(".png")),
                 "--video", "--label", source_label(beat, sources) or beat.id])
            write_if_changed(stamp, key)
        return target
    raise ValueError("asset missing")


def available_without_render(video: Path, beat: Beat,
                             sources: dict[str, dict[str, str]]) -> str | None:
    if find_asset(video, beat) or beat.visual["type"] == "title_card":
        return None
    if beat.visual["type"] == "chart":
        try:
            normalize_chart(beat, Path(f"{beat.id}.mp4"), float(beat.raw.get("est_sec", 5)))
            return None
        except (KeyError, TypeError, ValueError) as exc:
            return str(exc)
    if beat.visual["type"] == "doc_highlight":
        try:
            doc_origin(video, beat, sources)
            return None
        except ValueError as exc:
            return str(exc)
    return "asset missing"


def todo_markdown(beats: list[Beat]) -> str:
    lines = ["# Assets still needed", "", "Generated charts and title cards are not listed.", ""]
    missing = [beat for beat in beats if beat.placeholder_reason]
    for beat in missing:
        visual = beat.visual
        lines.extend([f"- [ ] **{beat.id} · {visual['type']}** — {visual.get('brief', '')}",
                      f"  - Reason: {beat.placeholder_reason}"])
        for key in ("search", "prompt"):
            if visual.get(key):
                lines.append(f"  - {key.title()}: {visual[key]}")
        if visual.get("doc"):
            lines.append(f"  - Document: {visual['doc'].get('source', '')} — {visual['doc'].get('quote', '')}")
    if not missing:
        lines.append("No placeholder assets remain.")
    return "\n".join(lines) + "\n"


def load_sections(video: Path, only: str | None) -> list[Section]:
    path = video / "storyboard.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data.get("beats")
    if not isinstance(raw, list) or not raw:
        raise ValueError("storyboard.json needs a nonempty beats list")
    selected = [Beat(item) for item in raw if not only or item["section"].startswith(only)]
    if not selected:
        raise ValueError(f"No beats in section {only}")
    ids = [beat.id for beat in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("Beat IDs must be unique")
    sections = [Section(name, list(group)) for name, group in
                itertools.groupby(selected, key=lambda beat: beat.section)]
    if len({section.name for section in sections}) != len(sections):
        raise ValueError("Sections must be contiguous in storyboard order")
    return sections


def allocate(total: int, weights: list[int]) -> list[int]:
    total = max(total, len(weights) * (FADE + 4))
    weights = [max(1, item) for item in weights]
    available = total - len(weights) * (FADE + 4)
    raw = [available * weight / sum(weights) for weight in weights]
    floors = [math.floor(item) for item in raw]
    for index in sorted(range(len(raw)), key=lambda item: raw[item] - floors[item], reverse=True)[:available - sum(floors)]:
        floors[index] += 1
    return [item + FADE + 4 for item in floors]


def map_narration(video: Path, sections: list[Section]) -> None:
    manifest = video / "vo/manifest.json"
    entries = []
    if manifest.is_file():
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("sections", [])
    by_title = {str(item.get("title", "")).strip().casefold(): item for item in entries}
    for section in sections:
        title = re.sub(r"^\d+\s*", "", section.name).strip().casefold()
        item = by_title.get(title) or by_title.get(section.name.casefold())
        if item:
            path = video / "vo" / item.get("file", "")
            if path.is_file():
                section.wav = path
                section.frames = max(1, round(probe_duration(path) * FPS))
        if not section.wav:
            section.frames = sum(max(FADE + 4, round(float(beat.raw.get("est_sec", 5)) * FPS))
                                 for beat in section.beats)
        weights = [len(re.findall(r"\b\w+\b", beat.raw.get("vo", "")))
                   for beat in section.beats]
        frames = allocate(section.frames, weights) if section.wav else [
            max(FADE + 4, round(float(beat.raw.get("est_sec", 5)) * FPS))
            for beat in section.beats]
        section.frames = sum(frames)
        for beat, count in zip(section.beats, frames):
            beat.frames = count
    cursor = 0
    for index, section in enumerate(sections):
        section.start = cursor
        for beat in section.beats:
            beat.start = cursor
            cursor += beat.frames
        if index < len(sections) - 1:
            cursor += PAUSE


def align_narration(sections: list[Section]) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Warning: --align needs optional faster-whisper; using proportional timing", file=sys.stderr)
        return
    if not any(section.wav for section in sections):
        print("Warning: --align has no section WAVs; using estimated timing", file=sys.stderr)
        return
    try:
        model = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=1,
                             num_workers=1)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Warning: could not load small.en ({exc}); using proportional timing",
              file=sys.stderr)
        return
    for section in sections:
        if not section.wav or len(section.beats) == 1:
            continue
        try:
            segments, _ = model.transcribe(str(section.wav), language="en", beam_size=1,
                                           word_timestamps=True)
            heard = [(word.word, word.start, word.end)
                     for segment in segments for word in (segment.words or [])]
            tokens = [re.sub(r"[^a-z0-9]", "", item[0].lower()) for item in heard]
            found: list[tuple[int, int]] = []
            cursor = 0
            for beat in section.beats:
                wanted = [re.sub(r"[^a-z0-9]", "", word.lower())
                          for word in beat.raw.get("vo", "").split()]
                wanted = [word for word in wanted if word]
                prefix = wanted[:min(7, len(wanted))]
                choices = [(fuzz.ratio(" ".join(prefix), " ".join(tokens[i:i + len(prefix)])), i)
                           for i in range(cursor, max(cursor, len(tokens) - len(prefix) + 1))]
                score, start = max(choices, default=(0, 0))
                if score < 80:
                    raise ValueError(f"{beat.id}: first words did not match transcription")
                found.append((start, min(len(heard), start + len(wanted))))
                cursor = max(cursor + 1, found[-1][1])
            boundaries = [0] + [round(heard[start][1] * FPS) for start, _ in found[1:]] + [section.frames]
            if any(b - a < FADE + 4 for a, b in zip(boundaries, boundaries[1:])):
                raise ValueError("aligned beats overlap or are too short")
            section.frames = boundaries[-1]
            for beat, (a, b), (first, last) in zip(section.beats,
                                                   zip(boundaries, boundaries[1:]), found):
                beat.frames = b - a
                beat.word_times = [(word[1], word[2]) for word in heard[first:last]]
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"Warning: {section.name}: alignment failed ({exc}); using proportional timing",
                  file=sys.stderr)
    cursor = 0
    for index, section in enumerate(sections):
        section.start = cursor
        for beat in section.beats:
            beat.start = cursor
            cursor += beat.frames
        if index < len(sections) - 1:
            cursor += PAUSE


def clip_signature(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return str(path.resolve()), stat.st_mtime_ns, stat.st_size


def render_beat(video: Path, beat: Beat, last_in_section: bool, build: Path,
                sources: dict[str, dict[str, str]], size: tuple[int, int],
                preview: bool) -> None:
    try:
        origin = visual_source(video, beat, sources, build, size)
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        beat.placeholder_reason = str(exc)
        origin = build / "cards" / f"{beat.id}-{digest((beat.raw, size, 'placeholder'))}.png"
        if not origin.is_file():
            card(beat, origin, size, True)
        print(f"Warning: {beat.id}: {beat.placeholder_reason}; using placeholder", file=sys.stderr)
    length = beat.frames + (0 if last_in_section else FADE)
    text = beat.field("on_screen_text") if beat.visual["type"] != "title_card" else ""
    key = digest((clip_signature(origin), beat.id, length, size, text,
                  source_label(beat, sources), preview))
    cache = build / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    base = cache / f"{beat.id}-{key}-base.mp4"
    watermark = cache / f"{beat.id}-{key}-mark.png"
    if not watermark.is_file():
        overlay_image(beat, sources, watermark, size)
    width, height = size
    if not base.is_file():
        motion = origin.suffix.lower() in VIDEO_EXT
        input_args = (["-stream_loop", "-1", "-i", str(origin)] if motion else
                      ["-loop", "1", "-framerate", str(FPS), "-i", str(origin)])
        if motion or beat.visual["type"] in ("title_card", "doc_highlight", "chart") or beat.placeholder_reason:
            fit = (f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                   f"crop={width}:{height},fps={FPS},setsar=1")
        else:
            seed = int(hashlib.sha256(beat.id.encode()).hexdigest()[:4], 16)
            xpan = (seed % 5) / 8
            ypan = ((seed // 5) % 5) / 8
            step = 0.08 / max(1, length)
            fit = (f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                   f"crop={width}:{height},"
                   f"zoompan=z='min(zoom+{step:.8f},1.08)':"
                   f"x='(iw-iw/zoom)*{xpan:.3f}':y='(ih-ih/zoom)*{ypan:.3f}':"
                   f"d=1:s={width}x{height}:fps={FPS},setsar=1")
        ffmpeg(*input_args, "-loop", "1", "-framerate", str(FPS), "-i", str(watermark),
               "-filter_complex", f"[0:v]{fit},format=rgba[v];"
               "[v][1:v]overlay=0:0:format=auto,format=yuv420p[out]",
               "-map", "[out]", "-frames:v", str(length), "-an", "-c:v", "libx264",
               "-preset", "ultrafast" if preview else "veryfast", "-crf", "20",
               "-pix_fmt", "yuv420p", "-r", str(FPS), str(base))
    beat.base = base
    beat.baked = base
    if text and beat.frames > 2 * round(0.3 * FPS):
        overlay = cache / f"{beat.id}-{key}-text.png"
        if not overlay.is_file():
            overlay_image(beat, sources, overlay, size, True)
        beat.overlay = overlay
        baked = cache / f"{beat.id}-{key}-baked.mp4"
        if not baked.is_file():
            stop = max(0.31, beat.frames / FPS - 0.3)
            ffmpeg("-i", str(base), "-loop", "1", "-framerate", str(FPS),
                   "-i", str(overlay), "-filter_complex",
                   f"[0:v][1:v]overlay=0:0:enable='between(t,0.3,{stop:.4f})':"
                   "format=auto,format=yuv420p[out]", "-map", "[out]",
                   "-frames:v", str(length), "-an", "-c:v", "libx264",
                   "-preset", "ultrafast" if preview else "veryfast", "-crf", "20",
                   "-pix_fmt", "yuv420p", "-r", str(FPS), str(baked))
        beat.baked = baked


def section_video(section: Section, build: Path, preview: bool) -> Path:
    target = build / "sections" / f"{re.sub(r'[^a-z0-9]+', '-', section.name.lower()).strip('-')}.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    clips = [beat.baked for beat in section.beats]
    if any(clip is None for clip in clips):
        raise ValueError("A beat has no rendered clip")
    key = digest([(clip.name, clip.stat().st_mtime_ns) for clip in clips])
    stamp = target.with_suffix(".hash")
    if target.is_file() and stamp.is_file() and stamp.read_text() == key:
        return target
    if len(clips) == 1:
        ffmpeg("-i", str(clips[0]), "-frames:v", str(section.frames),
               "-c:v", "copy", "-an", str(target))
    else:
        graph = [f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[i{i}]"
                 for i in range(len(clips))]
        elapsed = 0
        previous = "i0"
        for index in range(1, len(clips)):
            elapsed += section.beats[index - 1].frames
            output = f"x{index}"
            graph.append(f"[{previous}][i{index}]xfade=transition=fade:"
                         f"duration={FADE / FPS:.9f}:offset={elapsed / FPS:.9f}[{output}]")
            previous = output
        inputs = [piece for clip in clips for piece in ("-i", str(clip))]
        ffmpeg(*inputs, "-filter_complex", ";".join(graph), "-map", f"[{previous}]",
               "-frames:v", str(section.frames), "-an", "-c:v", "libx264",
               "-preset", "ultrafast" if preview else "veryfast", "-crf", "20",
               "-pix_fmt", "yuv420p", "-r", str(FPS), str(target))
    write_if_changed(stamp, key)
    return target


def concat_list(paths: list[Path], target: Path, codec: str) -> None:
    listing = target.with_suffix(".txt")
    write_if_changed(listing, "".join(f"file '{path.resolve().as_posix()}'\n" for path in paths))
    if codec == "video":
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-c:v", "copy",
               "-an", str(target))
    else:
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-ar", "48000",
               "-ac", "1", "-c:a", "pcm_s16le", str(target))


def silent_wav(path: Path, frames: int) -> None:
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", sec(frames),
               "-ac", "1", "-c:a", "pcm_s16le", str(path))


def audio_tracks(video: Path, sections: list[Section], build: Path) -> tuple[Path, Path]:
    directory = build / "audio"
    directory.mkdir(parents=True, exist_ok=True)
    voice_parts: list[Path] = []
    music_parts: list[Path] = []
    for section_index, section in enumerate(sections):
        voice = directory / f"voice_{section_index:02d}_{section.frames}.wav"
        if section.wav:
            signature = digest((clip_signature(section.wav), section.frames))
            stamp = voice.with_suffix(".hash")
            if not voice.is_file() or not stamp.is_file() or stamp.read_text() != signature:
                ffmpeg("-i", str(section.wav), "-af", "aresample=48000,apad",
                       "-t", sec(section.frames), "-ar", "48000", "-ac", "1",
                       "-c:a", "pcm_s16le", str(voice))
                write_if_changed(stamp, signature)
        else:
            silent_wav(voice, section.frames)
        section.audio = voice
        voice_parts.append(voice)
        for run_index, (cue, grouped) in enumerate(itertools.groupby(section.beats,
                                                    key=lambda beat: beat.field("music", "silence"))):
            beats = list(grouped)
            frames = sum(beat.frames for beat in beats)
            track = video / "assets/music" / f"{cue}.mp3"
            present = cue != "silence" and track.is_file()
            cue_name = re.sub(r"[^a-z0-9]+", "-", cue.lower()).strip("-") or "silence"
            part = directory / f"music_{section_index:02d}_{run_index:02d}_{frames}_{cue_name}_{'source' if present else 'silent'}.wav"
            if present:
                signature = digest((clip_signature(track), frames))
                stamp = part.with_suffix(".hash")
                if not part.is_file() or not stamp.is_file() or stamp.read_text() != signature:
                    fade_start = max(0, frames / FPS - 1)
                    ffmpeg("-stream_loop", "-1", "-i", str(track), "-af",
                           f"volume=-18dB,afade=t=in:st=0:d=1,"
                           f"afade=t=out:st={fade_start:.4f}:d=1,aresample=48000",
                           "-t", sec(frames), "-ar", "48000", "-ac", "1",
                           "-c:a", "pcm_s16le", str(part))
                    write_if_changed(stamp, signature)
            else:
                if cue != "silence":
                    print(f"Warning: music cue {cue!r} has no assets/music/{cue}.mp3; skipping",
                          file=sys.stderr)
                silent_wav(part, frames)
            music_parts.append(part)
        if section_index < len(sections) - 1:
            pause = directory / "pause_0.6s.wav"
            silent_wav(pause, PAUSE)
            voice_parts.append(pause)
            music_parts.append(pause)
    voice_track = directory / "voice_track.wav"
    music_track = directory / "music_track.wav"
    concat_list(voice_parts, voice_track, "audio")
    concat_list(music_parts, music_track, "audio")
    return voice_track, music_track


def video_track(sections: list[Section], build: Path, size: tuple[int, int], preview: bool) -> Path:
    pieces = []
    for index, section in enumerate(sections):
        pieces.append(section_video(section, build, preview))
        if index < len(sections) - 1:
            gap = build / "sections" / f"pause_0.6s_{size[0]}x{size[1]}.mp4"
            if not gap.is_file():
                ffmpeg("-f", "lavfi", "-i",
                       f"color=c={NIGHT}:s={size[0]}x{size[1]}:r={FPS}",
                       "-frames:v", str(PAUSE), "-an", "-c:v", "libx264",
                       "-preset", "ultrafast" if preview else "veryfast", "-crf", "20",
                       "-pix_fmt", "yuv420p", str(gap))
            pieces.append(gap)
    target = build / "video_noaudio.mp4"
    concat_list(pieces, target, "video")
    return target


def caption_groups(value: str) -> list[tuple[str, int, int]]:
    words = value.split()
    lines: list[tuple[str, int, int]] = []
    current: list[str] = []
    first = 0
    for index, word in enumerate(words):
        candidate = " ".join(current + [word])
        if current and len(candidate) > 42:
            lines.append((" ".join(current), first, index))
            current = [word]
            first = index
        else:
            current.append(word)
    if current:
        lines.append((" ".join(current), first, len(words)))
    return [("\n".join(line[0] for line in lines[i:i + 2]), lines[i][1],
             lines[min(i + 1, len(lines) - 1)][2]) for i in range(0, len(lines), 2)]


def srt_time(frames: int) -> str:
    milliseconds = round(frames * 1000 / FPS)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_captions(sections: list[Section], target: Path) -> None:
    entries = []
    serial = 1
    for section in sections:
        for beat in section.beats:
            groups = caption_groups(beat.raw.get("vo", ""))
            if not groups:
                continue
            total_words = max(1, len(beat.raw.get("vo", "").split()))
            for caption, first, last in groups:
                if len(beat.word_times) == total_words:
                    begin = section.start + round(beat.word_times[first][0] * FPS)
                    end = section.start + round(beat.word_times[last - 1][1] * FPS)
                else:
                    begin = beat.start + round(beat.frames * first / total_words)
                    end = beat.start + round(beat.frames * last / total_words)
                end = max(begin + 1, min(beat.start + beat.frames, end))
                entries.extend([str(serial), f"{srt_time(begin)} --> {srt_time(end)}",
                                caption, ""])
                serial += 1
    write_if_changed(target, "\n".join(entries))


def write_fcpxml(sections: list[Section], music: Path, target: Path,
                 size: tuple[int, int]) -> None:
    total = sections[-1].start + sections[-1].frames
    root = ET.Element("fcpxml", version="1.10")
    resources = ET.SubElement(root, "resources")
    ET.SubElement(resources, "format", id="r1", name=f"FFVideoFormat{size[1]}p30",
                  frameDuration="1/30s", width=str(size[0]), height=str(size[1]))
    ids: dict[Path, str] = {}

    def asset(path: Path, duration: int, video: bool) -> str:
        path = path.resolve()
        if path not in ids:
            ref = f"r{len(ids) + 2}"
            attrs = {"id": ref, "name": path.name, "src": path.as_uri(),
                     "start": "0s", "duration": ftime(duration),
                     "hasVideo": "1" if video else "0",
                     "hasAudio": "0" if video else "1"}
            if video:
                attrs["format"] = "r1"
            else:
                attrs.update(audioSources="1", audioChannels="1", audioRate="48000")
            ET.SubElement(resources, "asset", attrs)
            ids[path] = ref
        return ids[path]

    event = ET.SubElement(root, "event", name="Deal Postmortem")
    project = ET.SubElement(event, "project", name="Rough cut")
    sequence = ET.SubElement(project, "sequence", format="r1", duration=ftime(total),
                             audioLayout="stereo", audioRate="48k")
    spine = ET.SubElement(sequence, "spine")
    for section_index, section in enumerate(sections):
        for beat in section.beats:
            if beat.base is None:
                raise ValueError(f"{beat.id} has no base clip for FCPXML")
            ET.SubElement(spine, "asset-clip", name=beat.id,
                          ref=asset(beat.base, beat.frames, True), offset=ftime(beat.start),
                          start="0s", duration=ftime(beat.frames))
            if beat.overlay and beat.frames > 18:
                ET.SubElement(spine, "asset-clip", name=f"{beat.id} lower third",
                              ref=asset(beat.overlay, beat.frames - 18, True), lane="1",
                              offset=ftime(beat.start + 9), start="0s",
                              duration=ftime(beat.frames - 18))
        if section.audio:
            ET.SubElement(spine, "asset-clip", name=f"{section.name} narration",
                          ref=asset(section.audio, section.frames, False), lane="-1",
                          offset=ftime(section.start), start="0s", duration=ftime(section.frames),
                          audioRole="dialogue")
        if section_index < len(sections) - 1:
            ET.SubElement(spine, "gap", name="Section pause", offset=ftime(section.start + section.frames),
                          duration=ftime(PAUSE))
    ET.SubElement(spine, "asset-clip", name="Music bed", ref=asset(music, total, False),
                  lane="-2", offset="0s", start="0s", duration=ftime(total), audioRole="music")
    ET.indent(root, space="  ")
    target.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def rough_cut(video: Path, voice: Path, music: Path, captions: Path,
              target: Path, frames: int, preview: bool, burn_captions: bool) -> None:
    filters = "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=0,"
    filters += "loudnorm=I=-14:TP=-1:LRA=11[a]"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
               "-filter_complex_threads", "1", "-i", str(video), "-i", str(voice),
               "-i", str(music), "-filter_complex", filters, "-map", "0:v",
               "-map", "[a]"]
    if burn_captions:
        command += ["-vf", "subtitles=captions.srt", "-c:v", "libx264", "-crf", "20",
                    "-preset", "ultrafast" if preview else "veryfast"]
    else:
        command += ["-c:v", "copy"]
    command += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-t", sec(frames), str(target)]
    run(command, cwd=captions.parent)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="videos/<slug> directory")
    parser.add_argument("--preview", action="store_true", help="720p ultrafast encode")
    parser.add_argument("--align", action="store_true", help="CPU small.en word alignment")
    parser.add_argument("--burn-captions", action="store_true")
    parser.add_argument("--only", help="section prefix, e.g. 03")
    parser.add_argument("--todo-only", action="store_true", help="write assets_todo.md only")
    args = parser.parse_args()
    try:
        video = args.video.resolve()
        sections = load_sections(video, args.only)
        beats = [beat for section in sections for beat in section.beats]
        sources = source_index(video)
        build = video / "build"
        build.mkdir(exist_ok=True)
        todo = build / "assets_todo.md"
        if args.todo_only:
            for beat in beats:
                beat.placeholder_reason = available_without_render(video, beat, sources)
            write_if_changed(todo, todo_markdown(beats))
            print(f"{todo} ({sum(bool(beat.placeholder_reason) for beat in beats)} missing beats)")
            return 0
        import shutil
        for executable in ("ffmpeg", "ffprobe"):
            if not shutil.which(executable):
                raise RuntimeError(f"{executable} is required on PATH")
        map_narration(video, sections)
        if args.align:
            align_narration(sections)
        size = (1280, 720) if args.preview else (1920, 1080)
        for section in sections:
            for index, beat in enumerate(section.beats):
                render_beat(video, beat, index == len(section.beats) - 1,
                            build, sources, size, args.preview)
        write_if_changed(todo, todo_markdown(beats))
        captions = build / "captions.srt"
        write_captions(sections, captions)
        video_path = video_track(sections, build, size, args.preview)
        voice, music = audio_tracks(video, sections, build)
        total = sections[-1].start + sections[-1].frames
        write_fcpxml(sections, music, build / "timeline.fcpxml", size)
        output = build / "rough_cut.mp4"
        rough_cut(video_path, voice, music, captions, output, total, args.preview,
                  args.burn_captions)
        print(f"{output}\n{captions}\n{build / 'timeline.fcpxml'}\n{todo}")
        return 0
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
