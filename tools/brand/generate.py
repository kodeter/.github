#!/usr/bin/env python3
"""Extract the official Kodeter mark and build the organization banner.

Source of truth: the organization avatar already set on github.com/kodeter
(black plate, white geometric K). This script reuses that shape instead of
inventing a new one.

Inputs
  assets/logo-source.png   downloaded copy of the org avatar (460x460)

Outputs
  ../images/logo.png       the mark alone, white on transparent, tightly cropped
  ../images/profile.png    the org avatar, unchanged, for reference
  ../images/banner.png     2000x1000 header for the organization profile README

Run from this folder:
  python3 generate.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2000, 1000

INK_TOP = (6, 8, 10)
INK_BOTTOM = (13, 16, 19)
GRID = (26, 29, 33)
GRID_STRONG = (38, 43, 48)
STEEL = (150, 163, 174)
STEEL_DIM = (58, 66, 74)
TEXT = (245, 247, 249)
MUTED = (166, 176, 185)
AMBER = (240, 170, 44)
AMBER_DIM = (120, 86, 28)

FONT_DIR = "/home/lendra/.fonts/IBM Plex"
MONO_DIR = "/home/lendra/.fonts/Jetbrains"

WORDS = "KODETER"
CAPTION = "an open community for people who build and ship software"
TAGS = "CODE  ·  INFRA  ·  DOCS  ·  MENTORING"

HERE = os.path.dirname(os.path.abspath(__file__))


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, xy, text, fnt, fill, tracking, anchor="la"):
    x, y = xy
    total = sum(draw.textlength(ch, font=fnt) for ch in text) + tracking * (len(text) - 1)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="l" + anchor[1])
        x += draw.textlength(ch, font=fnt) + tracking
    return total


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((w, h), Image.BILINEAR)


def radial_glow(size, center, radius, color, strength=0.5):
    w, h = size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    cx, cy = center
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        v = int(255 * strength * (1 - t) ** 2)
        d.ellipse([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72], fill=v)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.25))
    glow = Image.new("RGB", (w, h), color)
    return glow, layer


def extract_mark(source_path):
    """White shape of the org logo on a transparent ground, tightly cropped."""
    src = Image.open(source_path).convert("L")
    mask = src.point(lambda v: 255 if v > 150 else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit(f"no mark found in {source_path}")
    mask = mask.crop(box)
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    out.putalpha(mask)
    white = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    white.putalpha(mask)
    return white


def paste_mark(img, mark, cx, cy, height):
    ratio = height / mark.height
    size = (max(1, int(mark.width * ratio)), height)
    scaled = mark.resize(size, Image.LANCZOS)
    img.alpha_composite(scaled, (int(cx - size[0] / 2), int(cy - size[1] / 2)))


def build_banner(path, mark):
    img = vertical_gradient((W, H), INK_TOP, INK_BOTTOM).convert("RGBA")
    glow, mask = radial_glow((W, H), (1450, 400), 880, (30, 36, 44), 0.85)
    img = Image.composite(glow, img, mask)

    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W + 1, 40):
        gd.line([(x, 0), (x, H)], fill=GRID + (95,), width=1)
    for y in range(0, H + 1, 40):
        gd.line([(0, y), (W, y)], fill=GRID + (95,), width=1)
    for x in range(0, W + 1, 200):
        gd.line([(x, 0), (x, H)], fill=GRID_STRONG + (130,), width=1)
    for y in range(0, H + 1, 200):
        gd.line([(0, y), (W, y)], fill=GRID_STRONG + (130,), width=1)
    img = Image.alpha_composite(img, grid)

    field = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(field)

    base_y = 810
    left, right = 1230, 1900
    cols = 26
    step = (right - left) / (cols - 1)
    heights = []
    for i in range(cols):
        t = i / (cols - 1)
        wave = (
            math.sin(t * math.pi * 3.1 + 0.6) * 0.5
            + math.sin(t * math.pi * 8.7 + 1.9) * 0.28
            + math.sin(t * math.pi * 17.3 + 0.2) * 0.14
        )
        heights.append(70 + abs(wave) * 430)

    fd.line([(left - 40, base_y), (right + 40, base_y)], fill=STEEL_DIM + (170,), width=2)
    pts = []
    for i, hgt in enumerate(heights):
        x = left + i * step
        y = base_y - hgt
        hot = (i * 7) % 11 in (0, 3, 6)
        fd.line(
            [(x, base_y), (x, y)],
            fill=(AMBER if hot else STEEL_DIM) + (215 if hot else 160,),
            width=3 if hot else 2,
        )
        fd.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(AMBER if hot else STEEL) + (240,))
        pts.append((x, y))
    fd.line(pts, fill=STEEL + (85,), width=2, joint="curve")

    thr = base_y - 255
    for x in range(left - 60, right + 60, 22):
        fd.line([(x, thr), (x + 12, thr)], fill=AMBER_DIM + (185,), width=2)

    cal_x = right + 76
    fd.line([(cal_x, base_y - 520), (cal_x, base_y)], fill=STEEL_DIM + (170,), width=2)
    for i in range(8):
        y = base_y - i * 65
        fd.line([(cal_x, y), (cal_x + (16 if i % 2 == 0 else 9), y)], fill=STEEL_DIM + (170,), width=2)

    img = Image.alpha_composite(img, field)

    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fg)

    mono_s = font(f"{MONO_DIR}/JetBrainsMono-Regular.ttf", 24)
    mono_xs = font(f"{MONO_DIR}/JetBrainsMono-Regular.ttf", 20)
    mono_t = font(f"{MONO_DIR}/JetBrainsMono-Medium.ttf", 21)
    word = font(f"{FONT_DIR}/IBMPlexSans-Bold.ttf", 168)
    cap = font(f"{FONT_DIR}/IBMPlexSans-Light.ttf", 38)

    fd.text((150, 150), "ORG", font=mono_s, fill=AMBER)
    tracked(fd, (150 + 74, 150), "· INDONESIA · EST 2024", mono_s, STEEL, 3)

    tracked(fd, (150, 232), WORDS, word, TEXT, 20)
    fd.rectangle([150, 452, 150 + 128, 456], fill=AMBER)
    fd.text((150, 492), CAPTION, font=cap, fill=MUTED)
    tracked(fd, (150, 578), TAGS, mono_t, STEEL, 3)

    fd.text((150, 872), "FIG. 01", font=mono_xs, fill=STEEL)
    tracked(fd, (150 + 92, 872), "· PROFILE SIGNAL", mono_xs, STEEL_DIM, 2)

    tracked(fd, (right - 128, thr - 34), "THRESHOLD", mono_xs, AMBER_DIM, 2)

    tracked(fd, (W - 150, 872), "SNAPSHOT 2026", mono_xs, STEEL_DIM, 2, anchor="ra")

    for cx, cy in ((150, 96), (W - 150, 96), (150, H - 60), (W - 150, H - 60)):
        fd.line([(cx - 13, cy), (cx + 13, cy)], fill=STEEL_DIM + (170,), width=1)
        fd.line([(cx, cy - 13), (cx, cy + 13)], fill=STEEL_DIM + (170,), width=1)

    img = Image.alpha_composite(img, fg)

    # Official mark, white on the ink ground.
    paste_mark(img, mark, 1660, 250, 158)
    return img.convert("RGB")


def main():
    images = os.path.normpath(os.path.join(HERE, "..", "..", "images"))
    assets = os.path.join(HERE, "assets")
    os.makedirs(images, exist_ok=True)

    source = os.path.join(assets, "logo-source.png")
    mark = extract_mark(source)

    mark.save(os.path.join(images, "logo.png"), "PNG", optimize=True)
    Image.open(source).convert("RGB").save(
        os.path.join(images, "profile.png"), "PNG", optimize=True
    )

    banner = build_banner(os.path.join(images, "banner.png"), mark)
    banner.save(os.path.join(images, "banner.png"), "PNG", optimize=True)

    assert banner.size == (W, H), banner.size
    for name, min_size in (("banner.png", 20000), ("logo.png", 800), ("profile.png", 2000)):
        p = os.path.join(images, name)
        assert os.path.getsize(p) > min_size, name
        print(f"{name}: {Image.open(p).size} {os.path.getsize(p) // 1024} KB")


if __name__ == "__main__":
    main()
