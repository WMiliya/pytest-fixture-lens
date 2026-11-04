"""Generate README/assets from the demo report.

Requires Pillow. Run from the repository root:

    python scripts/make_assets.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
REPORT = ROOT / "examples" / "demo_project" / "report.json"

BG = "#0b1020"
PANEL = "#121a2b"
LINE = "#243049"
TEXT = "#e6edf7"
MUTED = "#93a4bd"
ACCENT = "#7dd3fc"
GOOD = "#34d399"
WARN = "#fbbf24"
PURPLE = "#c4b5fd"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    t = tuple(int(top[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(bottom[i : i + 2], 16) for i in (1, 3, 5))
    for y in range(height):
        k = y / max(1, height - 1)
        color = tuple(int(t[c] + (b[c] - t[c]) * k) for c in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    return img


def chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color: str) -> int:
    f = font(20, bold=True)
    w = int(draw.textlength(text, font=f)) + 32
    draw.rounded_rectangle([x, y, x + w, y + 40], radius=20, outline=color, width=2)
    draw.text((x + 16, y + 8), text, font=f, fill=color)
    return w + 12


def make_banner() -> None:
    img = gradient((1280, 640), "#182444", BG)
    draw = ImageDraw.Draw(img)
    for x in range(40, 1280, 48):
        for y in range(40, 640, 48):
            draw.ellipse([x, y, x + 2, y + 2], fill="#1f2b47")

    draw.text((80, 150), "FixtureLens", font=font(86, bold=True), fill=TEXT)
    draw.text((84, 260), "See which pytest fixtures your tests", font=font(32), fill=MUTED)
    draw.text((84, 302), "build, reuse, and pay for.", font=font(32), fill=MUTED)

    x = 84
    for label, color in [("offline HTML", ACCENT), ("JSON", GOOD), ("pytest plugin", PURPLE)]:
        x += chip(draw, x, 380, label, color)

    draw.text(
        (84, 500), "Setup hotspots · dependency graph · reuse counts", font=font(24), fill=MUTED
    )

    cx, cy, r = 980, 300, 150
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT, width=14)
    draw.line([cx + 105, cy + 105, cx + 220, cy + 220], fill=ACCENT, width=24)
    nodes = [(cx - 60, cy - 40), (cx + 40, cy - 70), (cx + 10, cy + 50)]
    for a, b in [(0, 1), (1, 2), (0, 2)]:
        draw.line([nodes[a], nodes[b]], fill="#3b4a6b", width=6)
    for i, (nx, ny) in enumerate(nodes):
        color = [GOOD, WARN, PURPLE][i]
        draw.ellipse([nx - 22, ny - 22, nx + 22, ny + 22], fill=PANEL, outline=color, width=6)

    img.save(ASSETS / "banner.png", optimize=True)
    img.save(ASSETS / "social-preview.png", optimize=True)


def make_logo() -> None:
    img = Image.new("RGB", (512, 512), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([16, 16, 496, 496], radius=96, fill=PANEL, outline=LINE, width=4)
    cx, cy, r = 230, 230, 120
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT, width=18)
    draw.line([cx + 85, cy + 85, cx + 170, cy + 170], fill=ACCENT, width=28)
    nodes = [(cx - 45, cy - 30), (cx + 35, cy - 55), (cx + 5, cy + 45)]
    for a, b in [(0, 1), (1, 2), (0, 2)]:
        draw.line([nodes[a], nodes[b]], fill="#3b4a6b", width=8)
    for i, (nx, ny) in enumerate(nodes):
        color = [GOOD, WARN, PURPLE][i]
        draw.ellipse([nx - 20, ny - 20, nx + 20, ny + 20], fill=BG, outline=color, width=7)
    img.save(ASSETS / "logo.png", optimize=True)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect x="16" y="16" width="480" height="480" rx="96"
        fill="#121a2b" stroke="#243049" stroke-width="4"/>
  <circle cx="230" cy="230" r="120" fill="none" stroke="#7dd3fc" stroke-width="18"/>
  <line x1="315" y1="315" x2="400" y2="400"
        stroke="#7dd3fc" stroke-width="28" stroke-linecap="round"/>
  <line x1="185" y1="200" x2="265" y2="175" stroke="#3b4a6b" stroke-width="8"/>
  <line x1="265" y1="175" x2="235" y2="275" stroke="#3b4a6b" stroke-width="8"/>
  <line x1="185" y1="200" x2="235" y2="275" stroke="#3b4a6b" stroke-width="8"/>
  <circle cx="185" cy="200" r="20" fill="#0b1020" stroke="#34d399" stroke-width="7"/>
  <circle cx="265" cy="175" r="20" fill="#0b1020" stroke="#fbbf24" stroke-width="7"/>
  <circle cx="235" cy="275" r="20" fill="#0b1020" stroke="#c4b5fd" stroke-width="7"/>
</svg>
"""
    (ASSETS / "logo.svg").write_text(svg, encoding="utf-8")


def card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, label: str, value: str) -> None:
    draw.rounded_rectangle([x, y, x + w, y + 110], radius=16, fill=PANEL, outline=LINE)
    draw.text((x + 20, y + 18), label.upper(), font=font(16, bold=True), fill=MUTED)
    draw.text((x + 20, y + 48), value, font=font(34, bold=True), fill=TEXT)


def make_report_preview() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    summary = data["summary"]
    fixtures = sorted(data["fixtures"], key=lambda f: f["total_exclusive_ms"], reverse=True)

    img = gradient((1600, 1000), "#182444", BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "FixtureLens", font=font(40, bold=True), fill=TEXT)
    draw.text((60, 92), "Demo report · offline HTML preview", font=font(22), fill=MUTED)

    labels = [
        ("Tests", str(summary["tests"])),
        ("Fixtures", str(summary["fixtures"])),
        ("Exclusive setup", f"{summary['setup_exclusive_ms']:.1f} ms"),
        ("Reused setups", str(summary["reused_setups"])),
    ]
    x = 60
    for label, value in labels:
        card(draw, x, 150, 350, label, value)
        x += 380

    draw.rounded_rectangle([60, 300, 980, 930], radius=18, fill=PANEL, outline=LINE)
    draw.text((90, 330), "Setup hotspots", font=font(28, bold=True), fill=TEXT)
    headers = ["Fixture", "Scope", "Setups", "Reused", "Exclusive"]
    xs = [90, 330, 510, 650, 790]
    for header, hx in zip(headers, xs, strict=True):
        draw.text((hx, 390), header, font=font(18, bold=True), fill=MUTED)
    y = 440
    for f in fixtures[:6]:
        draw.text((xs[0], y), f["name"], font=font(22, mono=True), fill=TEXT)
        draw.text((xs[1], y), f["scope"], font=font(22), fill=ACCENT)
        draw.text((xs[2], y), str(f["setup_count"]), font=font(22), fill=TEXT)
        draw.text((xs[3], y), str(f["reuse_count"]), font=font(22), fill=GOOD)
        draw.text((xs[4], y), f"{f['total_exclusive_ms']:.1f} ms", font=font(22), fill=TEXT)
        draw.line([90, y + 40, 950, y + 40], fill=LINE, width=2)
        y += 64

    draw.rounded_rectangle([1020, 300, 1540, 930], radius=18, fill=PANEL, outline=LINE)
    draw.text((1050, 330), "Dependency graph", font=font(28, bold=True), fill=TEXT)
    by_key = {f["key"]: f for f in fixtures}
    positions = {}
    depths = {}

    def depth(key: str) -> int:
        if key in depths:
            return depths[key]
        f = by_key.get(key)
        if not f or not f["dependencies"]:
            depths[key] = 0
        else:
            depths[key] = 1 + max(depth(d) for d in f["dependencies"])
        return depths[key]

    for f in fixtures:
        depth(f["key"])
    columns: dict[int, list[dict]] = {}
    for f in fixtures:
        columns.setdefault(depths[f["key"]], []).append(f)
    node_w, node_h, col_gap = 140, 54, 150
    for d, items in columns.items():
        for i, f in enumerate(items):
            positions[f["key"]] = (1060 + d * col_gap, 430 + i * 120)
    for f in fixtures:
        x2, y2 = positions[f["key"]]
        for dep in f["dependencies"]:
            if dep not in positions:
                continue
            x1, y1 = positions[dep]
            draw.line(
                [x1 + node_w, y1 + node_h // 2, x2, y2 + node_h // 2], fill="#3b4a6b", width=4
            )
    scope_color = {"session": PURPLE, "module": ACCENT, "function": GOOD, "class": WARN}
    for f in fixtures:
        x, y = positions[f["key"]]
        color = scope_color.get(f["scope"], MUTED)
        draw.rounded_rectangle(
            [x, y, x + node_w, y + node_h], radius=12, fill=BG, outline=color, width=3
        )
        draw.text((x + 12, y + 14), f["name"][:12], font=font(18, mono=True), fill=TEXT)

    img.save(ASSETS / "report-preview.png", optimize=True)


def terminal_frame(lines: list[str], cursor: bool = False) -> Image.Image:
    img = Image.new("RGB", (960, 540), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([30, 30, 930, 510], radius=18, fill="#0f1626", outline=LINE, width=2)
    for i, color in enumerate(["#f87171", "#fbbf24", "#34d399"]):
        draw.ellipse([60 + i * 28, 58, 76 + i * 28, 74], fill=color)
    draw.text((480, 52), "pytest --fixture-lens", font=font(18), fill=MUTED)
    y = 110
    for line in lines:
        color = TEXT
        if line.startswith("$"):
            color = ACCENT
        elif "report:" in line:
            color = GOOD
        elif "passed" in line:
            color = GOOD
        draw.text((60, y), line, font=font(22, mono=True), fill=color)
        y += 34
    if cursor:
        draw.rectangle([60, y, 74, y + 24], fill=ACCENT)
    return img


def make_demo_gif() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    s = data["summary"]
    frames = [
        terminal_frame(["$ pytest --fixture-lens"], cursor=True),
        terminal_frame(["$ pytest --fixture-lens", "collected 8 items"]),
        terminal_frame(["$ pytest --fixture-lens", "collected 8 items", "", "........"]),
        terminal_frame(
            [
                "$ pytest --fixture-lens",
                "collected 8 items",
                "",
                "........",
                "",
                "--------------- FixtureLens ---------------",
            ]
        ),
        terminal_frame(
            [
                "$ pytest --fixture-lens",
                "collected 8 items",
                "",
                "........",
                "",
                "--------------- FixtureLens ---------------",
                f"{s['tests']} tests · {s['fixtures']} fixtures · "
                f"{s['setup_exclusive_ms']:.1f} ms exclusive setup",
            ]
        ),
        terminal_frame(
            [
                "$ pytest --fixture-lens",
                "collected 8 items",
                "",
                "........",
                "",
                "--------------- FixtureLens ---------------",
                f"{s['tests']} tests · {s['fixtures']} fixtures · "
                f"{s['setup_exclusive_ms']:.1f} ms exclusive setup",
                f"{s['reused_setups']} reused setups",
                "report: .fixturelens/report.html",
            ]
        ),
        terminal_frame(
            [
                "$ pytest --fixture-lens",
                "",
                "Open .fixturelens/report.html",
                "",
                "✓ hotspots",
                "✓ dependency graph",
                "✓ reuse counts",
                "✓ per-test setup events",
            ]
        ),
    ]
    frames[0].save(
        ASSETS / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[900, 700, 700, 700, 900, 1400, 1800],
        loop=0,
        optimize=True,
    )


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    make_banner()
    make_logo()
    make_report_preview()
    make_demo_gif()
    print("wrote assets:", ", ".join(p.name for p in sorted(ASSETS.iterdir())))


if __name__ == "__main__":
    main()
