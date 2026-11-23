#!/usr/bin/env python3
"""Generate the Kodeter brand assets: banner and logo.

Source of truth: the organization avatar already set on github.com/kodeter
(black plate, white geometric K). This script reuses that shape instead of
inventing a new one, and the banner style follows the same rules as the mark:
pure black and white, hard edges, one geometric gesture.

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

from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H = 2000, 1000

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREY_20 = (51, 51, 51)
GREY_35 = (89, 89, 89)
GREY_55 = (140, 140, 140)

FONT_DIR = "/home/lendra/.fonts/IBM Plex"
MONO_DIR = "/home/lendra/.fonts/Jetbrains"
GEOMETRIC = "/usr/share/fonts/julietaula-montserrat-fonts"

WORDS = "KODETER"
CAPTION = "an open community for people who build and ship software"

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


def extract_mark(source_path):
    """White shape of the org logo on a transparent ground, tightly cropped."""
    src = Image.open(source_path).convert("L")
    mask = src.point(lambda v: 255 if v > 150 else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit(f"no mark found in {source_path}")
    mask = mask.crop(box)
    white = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    white.putalpha(mask)
    return white


def paste_mark(img, mark, cx, cy, height):
    ratio = height / mark.height
    size = (max(1, int(mark.width * ratio)), height)
    scaled = mark.resize(size, Image.LANCZOS)
    img.alpha_composite(scaled, (int(cx - size[0] / 2), int(cy - size[1] / 2)))
    return size


def polyline(draw, points, fill, width):
    draw.line(points, fill=fill, width=width, joint="curve")


def build_banner(path, mark):
    img = Image.new("RGBA", (W, H), BLACK + (255,))

    # Diagonal construction lines at the arm angles of the mark, right side only.
    lines = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines)
    for offset in (-420, -140, 140, 420):
        ld.line([(1240 + offset, 0), (1240 + offset + 780, 780)], fill=GREY_20 + (255,), width=2)
        ld.line([(1240 + offset, H), (1240 + offset - 780, 220)], fill=GREY_20 + (255,), width=2)
    clip = Image.new("L", (W, H), 0)
    ImageDraw.Draw(clip).rectangle([1236, 0, W, H], fill=255)
    lines.putalpha(ImageChops.multiply(lines.getchannel("A"), clip))
    img = Image.alpha_composite(img, lines)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # The mark sits in a black plate on the right, mirroring the org avatar.
    plate_x, plate_y, plate = 1360, 140, 520
    d.rectangle([plate_x, plate_y, plate_x + plate, plate_y + plate], fill=BLACK + (255,))
    d.rectangle(
        [plate_x, plate_y, plate_x + plate, plate_y + plate], outline=GREY_20 + (255,), width=3
    )
    img = Image.alpha_composite(img, layer)

    paste_mark(img, mark, plate_x + plate / 2, plate_y + plate / 2, 360)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Baseline and cap-height rules for the wordmark block.
    d.line([(150, 742), (1180, 742)], fill=GREY_35 + (255,), width=2)
    d.line([(150, 232), (1180, 232)], fill=GREY_20 + (255,), width=2)

    # Type block, left aligned, matching the mark's flat geometry.
    word = font(f"{GEOMETRIC}/Montserrat-ExtraBold.otf", 196)
    tracked(d, (150, 236), WORDS, word, WHITE, 6)

    rule_y = 500
    d.rectangle([150, rule_y, 150 + 150, rule_y + 8], fill=WHITE)

    cap = font(f"{GEOMETRIC}/Montserrat-Light.otf", 34)
    d.text((150, 548), CAPTION, font=cap, fill=GREY_55)
    # Monospace annotations, the only typographic contrast to the geometric sans.
    mono_s = font(f"{MONO_DIR}/JetBrainsMono-Regular.ttf", 22)
    mono_xs = font(f"{MONO_DIR}/JetBrainsMono-Regular.ttf", 18)
    mono_m = font(f"{MONO_DIR}/JetBrainsMono-Medium.ttf", 20)

    tracked(d, (150, 150), "ORG", mono_m, WHITE, 3)
    tracked(d, (150 + 66, 150), "· INDONESIA · EST 2024", mono_s, GREY_55, 3)

    tracked(d, (150, 786), "CODE  ·  INFRA  ·  DOCS  ·  MENTORING", mono_s, GREY_55, 3)

    d.text((150, 872), "FIG. 01", font=mono_xs, fill=GREY_35)
    tracked(d, (150 + 84, 872), "· PROFILE MARK", mono_xs, GREY_35, 2)

    tracked(d, (W - 150, 872), "KODETER.ORG", mono_xs, GREY_35, 2, anchor="ra")

    # Corner registration marks, same weight as the plate outline.
    for cx, cy in ((150, 96), (W - 150, 96), (150, H - 60), (W - 150, H - 60)):
        d.line([(cx - 16, cy), (cx + 16, cy)], fill=GREY_20 + (255,), width=2)
        d.line([(cx, cy - 16), (cx, cy + 16)], fill=GREY_20 + (255,), width=2)

    img = Image.alpha_composite(img, layer).convert("RGB")
    img.save(path, "PNG", optimize=True)
    return img


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

    assert banner.size == (W, H), banner.size
    for name, min_size in (("banner.png", 20000), ("logo.png", 800), ("profile.png", 2000)):
        p = os.path.join(images, name)
        assert os.path.getsize(p) > min_size, name
        print(f"{name}: {Image.open(p).size} {os.path.getsize(p) // 1024} KB")


if __name__ == "__main__":
    main()
