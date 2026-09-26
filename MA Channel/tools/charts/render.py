"""Render Deal Postmortem chart specs to 1920x1080 MP4 or final-frame PNG."""

from __future__ import annotations

import argparse
import glob
import json
import math
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "brand" / "fonts"
FPS = 30
DPI = 120
SIZE = (16, 9)
HOLD = 1.5
PAPER = "#EDEAE3"
INK = "#111111"
RED = "#C8102E"
YELLOW = "#F2C230"
NIGHT = "#0E0E10"
KINDS = {"line_reveal", "bar_compare", "number_counter", "stacked_debt", "deal_flow", "timeline"}


def font(name: str) -> FontProperties:
    files = {
        "label": ("Inter-Regular.ttf", "arial.ttf"),
        "bold": ("Inter-Bold.ttf", "arialbd.ttf"),
        "title": ("DMSerifDisplay-Regular.ttf", "georgiab.ttf"),
        "number": ("Anton-Regular.ttf", "impact.ttf"),
    }
    branded, windows = files[name]
    for path in (FONTS / branded, Path("C:/Windows/Fonts") / windows):
        if path.is_file():
            return FontProperties(fname=str(path))
    return FontProperties(family="DejaVu Sans", weight="bold" if name != "label" else "normal")


LABEL = font("label")
BOLD = font("bold")
TITLE = font("title")
NUMBER = font("number")


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 - (1 - value) ** 3


def reveal(progress: float, start: float, end: float) -> float:
    return ease((progress - start) / (end - start))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def number(value: object, field: str, *, minimum: float | None = None) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value),
            f"{field} must be a finite number")
    value = float(value)
    require(minimum is None or value >= minimum, f"{field} must be at least {minimum}")
    return value


def text(value: object, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be nonempty text")
    return value.strip()


def validate(spec: dict) -> dict:
    require(isinstance(spec, dict), "spec must be a JSON object")
    kind = spec.get("type")
    require(isinstance(kind, str) and kind in KINDS,
            f"type must be one of: {', '.join(sorted(KINDS))}")
    require(spec.get("theme", "paper") in ("paper", "night"), "theme must be paper or night")
    text(spec.get("title"), "title")
    text(spec.get("source"), "source")
    text(spec.get("out"), "out")
    duration = number(spec.get("duration", 5), "duration")
    require(4 <= duration <= 10, "duration must be 4-10 seconds")
    for field in ("prefix", "suffix"):
        require(isinstance(spec.get(field, ""), str), f"{field} must be text")
    decimals = spec.get("decimals", 0)
    require(isinstance(decimals, int) and not isinstance(decimals, bool) and 0 <= decimals <= 3,
            "decimals must be 0-3")
    if kind == "line_reveal":
        points = spec.get("points")
        require(isinstance(points, list) and len(points) >= 2, "points needs at least two entries")
        xs = [number(item.get("x"), "point.x") for item in points if isinstance(item, dict)]
        ys = [number(item.get("y"), "point.y", minimum=0) for item in points if isinstance(item, dict)]
        require(len(xs) == len(points) and len(ys) == len(points), "each point needs x and y")
        require(all(a < b for a, b in zip(xs, xs[1:])), "point.x values must increase")
        require(max(ys) > 0, "at least one point.y must be positive")
        annotations = spec.get("annotations", [])
        require(isinstance(annotations, list), "annotations must be a list")
        for item in annotations:
            require(isinstance(item, dict), "annotation must be an object")
            x = number(item.get("x"), "annotation.x")
            require(xs[0] <= x <= xs[-1], "annotation.x must be inside the point range")
            text(item.get("label"), "annotation.label")
    elif kind == "bar_compare":
        bars = spec.get("bars")
        require(isinstance(bars, list) and 2 <= len(bars) <= 5, "bars needs 2-5 entries")
        for item in bars:
            require(isinstance(item, dict), "bar must be an object")
            text(item.get("label"), "bar.label")
            number(item.get("value"), "bar.value", minimum=0)
        require(any(item["value"] > 0 for item in bars), "at least one bar.value must be positive")
        highlight = spec.get("highlight", 0)
        require(isinstance(highlight, int) and not isinstance(highlight, bool) and 0 <= highlight < len(bars),
                "highlight must be a zero-based bar index")
    elif kind == "number_counter":
        number(spec.get("from"), "from")
        number(spec.get("to"), "to")
        text(spec.get("caption"), "caption")
    elif kind == "stacked_debt":
        layers = spec.get("layers")
        require(isinstance(layers, list) and 2 <= len(layers) <= 4, "layers needs 2-4 entries")
        for item in layers:
            require(isinstance(item, dict), "layer must be an object")
            text(item.get("label"), "layer.label")
            number(item.get("value"), "layer.value", minimum=0)
        require(sum(item["value"] for item in layers) > 0, "layer total must be positive")
    elif kind == "deal_flow":
        nodes, edges = spec.get("nodes"), spec.get("edges")
        require(isinstance(nodes, list) and 2 <= len(nodes) <= 5, "nodes needs 2-5 entries")
        require(isinstance(edges, list) and len(edges) >= 1, "edges needs at least one entry")
        ids = set()
        for item in nodes:
            require(isinstance(item, dict), "node must be an object")
            node_id = text(item.get("id"), "node.id")
            require(node_id not in ids, f"duplicate node.id: {node_id}")
            ids.add(node_id)
            text(item.get("label"), "node.label")
            require(0.12 <= number(item.get("x"), "node.x") <= 0.88, "node.x must be 0.12-0.88")
            require(0.22 <= number(item.get("y"), "node.y") <= 0.75, "node.y must be 0.22-0.75")
        for item in edges:
            require(isinstance(item, dict), "edge must be an object")
            require(item.get("from") in ids and item.get("to") in ids and item["from"] != item["to"],
                    "edge endpoints must be distinct existing node ids")
            text(item.get("label"), "edge.label")
            require(0 <= number(item.get("delay", 0), "edge.delay") <= 1,
                    "edge.delay must be 0-1")
    elif kind == "timeline":
        events = spec.get("events")
        require(isinstance(events, list) and 2 <= len(events) <= 6, "events needs 2-6 entries")
        for item in events:
            require(isinstance(item, dict), "event must be an object")
            text(item.get("date"), "event.date")
            text(item.get("label"), "event.label")
    return spec


def palette(spec: dict) -> tuple[str, str, str]:
    if spec.get("theme", "paper") == "night":
        return NIGHT, PAPER, "#626267"
    return PAPER, INK, "#AAA69E"


def fmt(value: float, spec: dict) -> str:
    decimals = spec.get("decimals", 0)
    return f"{spec.get('prefix', '')}{value:,.{decimals}f}{spec.get('suffix', '')}"


def money_color(spec: dict, foreground: str) -> str:
    return YELLOW if spec.get("theme") == "night" and spec.get("prefix") == "$" else foreground


def label(ax, x: float, y: float, value: str, *, color: str, size=21, weight=False,
          align="center", vertical="center", alpha=1.0, family=None) -> None:
    ax.text(x, y, value, color=color, fontsize=size, fontproperties=family or (BOLD if weight else LABEL),
            ha=align, va=vertical, alpha=alpha, linespacing=1.2)


def draw_line(ax, spec: dict, progress: float, fg: str, faint: str) -> None:
    points = spec["points"]
    xs = np.array([item["x"] for item in points], dtype=float)
    ys = np.array([item["y"] for item in points], dtype=float)
    left, right, bottom, top = 0.10, 0.90, 0.24, 0.76
    scaled_x = left + (xs - xs[0]) / (xs[-1] - xs[0]) * (right - left)
    scaled_y = bottom + ys / max(ys) * (top - bottom)
    ax.plot([left, right], [bottom, bottom], color=faint, linewidth=1.3)
    label(ax, left, bottom - 0.055, str(int(xs[0]) if xs[0].is_integer() else xs[0]),
          color=fg, size=18, align="left")
    label(ax, right, bottom - 0.055, str(int(xs[-1]) if xs[-1].is_integer() else xs[-1]),
          color=fg, size=18, align="right")
    line_progress = ease(progress)
    draw_to = left + (right - left) * line_progress
    visible = scaled_x <= draw_to
    plot_x = list(scaled_x[visible])
    plot_y = list(scaled_y[visible])
    if plot_x and draw_to < right:
        plot_x.append(draw_to)
        plot_y.append(float(np.interp(draw_to, scaled_x, scaled_y)))
    if len(plot_x) >= 2:
        ax.plot(plot_x, plot_y, color=RED, linewidth=6, solid_capstyle="round")
    endpoint_alpha = reveal(line_progress, 0.88, 1.0)
    if endpoint_alpha > 0:
        label(ax, right - 0.01, min(0.83, scaled_y[-1] + 0.12), fmt(ys[-1], spec),
              color=money_color(spec, fg), size=32, weight=True, align="right",
              alpha=endpoint_alpha)
    for annotation in spec.get("annotations", []):
        x = left + (annotation["x"] - xs[0]) / (xs[-1] - xs[0]) * (right - left)
        fraction = (x - left) / (right - left)
        opacity = reveal(line_progress, max(0, fraction - 0.04), max(0.04, fraction))
        if opacity > 0:
            y = float(np.interp(x, scaled_x, scaled_y))
            ax.plot(x, y, "o", color=RED, markersize=12, alpha=opacity)
            label(ax, x, min(0.86, y + 0.09), annotation["label"], color=fg,
                  size=18, weight=True, alpha=opacity)


def draw_bars(ax, spec: dict, progress: float, fg: str, faint: str) -> None:
    bars = spec["bars"]
    max_value = max(item["value"] for item in bars)
    left, right, base, height = 0.10, 0.90, 0.28, 0.47
    ax.plot([left, right], [base, base], color=faint, linewidth=1.3)
    slot = (right - left) / len(bars)
    width = min(0.12, slot * 0.58)
    for index, item in enumerate(bars):
        center = left + slot * (index + 0.5)
        growth = reveal(progress, index * 0.08, min(1, index * 0.08 + 0.66))
        bar_height = height * item["value"] / max_value * growth
        color = RED if index == spec.get("highlight", 0) else fg
        ax.add_patch(Rectangle((center - width / 2, base), width, bar_height, color=color))
        value_color = money_color(spec, fg)
        label(ax, center, base + bar_height + 0.045, fmt(item["value"] * growth, spec),
              color=value_color, size=25, weight=True)
        label(ax, center, base - 0.07, textwrap.fill(item["label"], width=15),
              color=fg, size=18, weight=True, vertical="top")


def draw_counter(ax, spec: dict, progress: float, fg: str) -> None:
    value = spec["from"] + (spec["to"] - spec["from"]) * ease(progress)
    label(ax, 0.5, 0.52, fmt(value, spec), color=money_color(spec, fg), size=125, family=NUMBER)
    label(ax, 0.5, 0.31, spec["caption"], color=fg, size=29, weight=True)
    ax.plot([0.35, 0.65], [0.37, 0.37], color=RED, linewidth=6)


def draw_stack(ax, spec: dict, progress: float, fg: str, faint: str) -> None:
    layers = spec["layers"]
    total = sum(item["value"] for item in layers)
    x, y, width, height = 0.36, 0.25, 0.28, 0.53
    ax.plot([0.28, 0.72], [y, y], color=faint, linewidth=1.3)
    cursor = y
    for index, item in enumerate(layers):
        growth = reveal(progress, index / len(layers), (index + 1) / len(layers))
        segment = height * item["value"] / total * growth
        color = RED if "debt" in item["label"].lower() else fg
        ax.add_patch(Rectangle((x, cursor), width, segment, color=color))
        if segment > 0.06:
            inside = (NIGHT if color == PAPER else
                      YELLOW if spec.get("theme") == "night" and spec.get("prefix") == "$" and color == RED
                      else PAPER)
            label(ax, x + width / 2, cursor + segment / 2, fmt(item["value"] * growth, spec),
                  color=inside, size=24, weight=True)
        label(ax, x + width + 0.04, cursor + max(segment, 0.03) / 2,
              item["label"], color=fg, size=22, weight=True, align="left")
        cursor += segment
    if progress >= 1:
        label(ax, 0.5, 0.83, f"Total {fmt(total, spec)}", color=money_color(spec, fg),
              size=28, weight=True)


def edge_ends(first: dict, second: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    dx, dy = second["x"] - first["x"], second["y"] - first["y"]
    if abs(dx) >= abs(dy):
        sign = 1 if dx > 0 else -1
        return (first["x"] + sign * 0.095, first["y"]), (second["x"] - sign * 0.095, second["y"])
    sign = 1 if dy > 0 else -1
    return (first["x"], first["y"] + sign * 0.055), (second["x"], second["y"] - sign * 0.055)


def draw_flow(ax, spec: dict, progress: float, fg: str, faint: str) -> None:
    nodes = {item["id"]: item for item in spec["nodes"]}
    for index, item in enumerate(spec["nodes"]):
        opacity = reveal(progress, index * 0.08, index * 0.08 + 0.25)
        if opacity <= 0:
            continue
        ax.add_patch(FancyBboxPatch((item["x"] - 0.095, item["y"] - 0.055), 0.19, 0.11,
                                    boxstyle="round,pad=0.01,rounding_size=0.015",
                                    facecolor="none", edgecolor=fg, linewidth=2.2, alpha=opacity))
        label(ax, item["x"], item["y"], textwrap.fill(item["label"], width=14),
              color=fg, size=19, weight=True, alpha=opacity)
    for item in spec["edges"]:
        growth = reveal(progress, 0.35 + 0.5 * item.get("delay", 0),
                        0.50 + 0.5 * item.get("delay", 0))
        if growth <= 0:
            continue
        start, end = edge_ends(nodes[item["from"]], nodes[item["to"]])
        tip = (start[0] + (end[0] - start[0]) * growth,
               start[1] + (end[1] - start[1]) * growth)
        ax.add_patch(FancyArrowPatch(start, tip, arrowstyle="-|>", mutation_scale=22,
                                     color=RED, linewidth=3.2))
        if growth > 0.65:
            label(ax, (start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.09,
                  textwrap.fill(item["label"], width=20), color=fg, size=16,
                  weight=True, alpha=(growth - 0.65) / 0.35)


def draw_timeline(ax, spec: dict, progress: float, fg: str, faint: str) -> None:
    events = spec["events"]
    xs = np.linspace(0.12, 0.88, len(events))
    baseline = 0.49
    ax.plot([0.10, 0.90], [baseline, baseline], color=faint, linewidth=2)
    extent = 0.10 + 0.80 * ease(progress)
    ax.plot([0.10, extent], [baseline, baseline], color=RED, linewidth=4)
    for index, (x, item) in enumerate(zip(xs, events)):
        opacity = ease((extent - x) / 0.02)
        if opacity <= 0:
            continue
        ax.plot(x, baseline, "o", markersize=13, color=RED, alpha=opacity)
        above = index % 2 == 0
        label(ax, x, 0.65 if above else 0.31, item["date"], color=RED,
              size=19, weight=True, alpha=opacity)
        label(ax, x, 0.59 if above else 0.37, textwrap.fill(item["label"], width=14),
              color=fg, size=18, weight=True, alpha=opacity)


def draw(ax, spec: dict, progress: float) -> None:
    background, foreground, faint = palette(spec)
    ax.clear()
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_axis_off()
    ax.set_facecolor(background)
    label(ax, 0.07, 0.91, spec["title"], color=foreground, size=38,
          align="left", family=TITLE)
    ax.plot([0.07, 0.14], [0.855, 0.855], color=RED, linewidth=5)
    label(ax, 0.07, 0.065, f"Source: {spec['source']}", color=foreground,
          size=15, align="left")
    kind = spec["type"]
    if kind == "line_reveal":
        draw_line(ax, spec, progress, foreground, faint)
    elif kind == "bar_compare":
        draw_bars(ax, spec, progress, foreground, faint)
    elif kind == "number_counter":
        draw_counter(ax, spec, progress, foreground)
    elif kind == "stacked_debt":
        draw_stack(ax, spec, progress, foreground, faint)
    elif kind == "deal_flow":
        draw_flow(ax, spec, progress, foreground, faint)
    elif kind == "timeline":
        draw_timeline(ax, spec, progress, foreground, faint)


def render(path: Path, still: bool) -> Path:
    spec = validate(json.loads(path.read_text(encoding="utf-8")))
    out = (path.parent / spec["out"]).resolve()
    require(out.suffix.lower() == ".mp4", "out must end in .mp4")
    target = out.with_suffix(".png") if still else out
    target.parent.mkdir(parents=True, exist_ok=True)
    background, _, _ = palette(spec)
    fig = plt.figure(figsize=SIZE, dpi=DPI, facecolor=background)
    ax = fig.add_axes((0, 0, 1, 1))
    try:
        if still:
            draw(ax, spec, 1.0)
            fig.savefig(target, dpi=DPI, facecolor=background)
        else:
            frames = round(spec.get("duration", 5) * FPS)
            active = spec.get("duration", 5) - HOLD

            def update(frame: int):
                draw(ax, spec, min(1.0, (frame / FPS) / active))

            movie = FuncAnimation(fig, update, frames=frames, interval=1000 / FPS,
                                  repeat=False)
            movie.save(target, writer=FFMpegWriter(fps=FPS, codec="libx264",
                       extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]), dpi=DPI)
    finally:
        plt.close(fig)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("specs", nargs="+", help="JSON specs; glob patterns accepted")
    parser.add_argument("--still", action="store_true", help="Save final-frame PNG instead of MP4")
    args = parser.parse_args()
    paths = [Path(match) for pattern in args.specs for match in (glob.glob(pattern) or [pattern])]
    for path in paths:
        try:
            result = render(path, args.still)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            parser.error(f"{path}: {exc}")
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
