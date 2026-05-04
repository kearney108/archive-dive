#!/usr/bin/env python3
"""
Generate a vol banner PNG for archive-dive.
Design: kearney108 system — lapis duotone plate + cream text section.

Usage:
    python gen_banner.py PLATE_URL VOL_INT MONTH_UPPER YEAR OUTPUT

Example:
    python gen_banner.py https://upload.wikimedia.org/wikipedia/commons/... 2 JUNE 2026 vol-02-banner.png
"""

import io
import os
import sys
import subprocess
import urllib.request


def pip(*pkgs):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *pkgs])


try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pip("Pillow")
    from PIL import Image, ImageDraw, ImageFont


# --- Design tokens ---
LAPIS = (31,  71,  152)   # #1F4798
CREAM = (244, 239, 230)   # #F4EFE6
INK   = (26,  24,  20)    # #1A1814

BANNER_W = 1280
PLATE_H  = 210
TEXT_H   = 300
BANNER_H = PLATE_H + TEXT_H

YEAR_ROMAN = {
    "2025": "MMXXV",  "2026": "MMXXVI", "2027": "MMXXVII",
    "2028": "MMXXVIII", "2029": "MMXXIX", "2030": "MMXXX",
}
VOL_ROMAN = [
    "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
]

FONT_URLS = {
    "CormorantUpright-Bold.ttf":
        "https://github.com/CatharsisFonts/Cormorant/raw/master/fonts/ttf/CormorantUpright-Bold.ttf",
    "FragmentMono-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/fragmentmono/FragmentMono-Regular.ttf",
    "Newsreader-Italic.ttf":
        "https://github.com/google/fonts/raw/main/ofl/newsreader/Newsreader-Italic%5Bopsz%2Cwght%5D.ttf",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "archive-dive/1.0 (kearney108)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def ensure_fonts(font_dir: str) -> dict:
    os.makedirs(font_dir, exist_ok=True)
    paths = {}
    for name, url in FONT_URLS.items():
        path = os.path.join(font_dir, name)
        if not os.path.exists(path):
            print(f"  downloading {name} ...")
            try:
                with open(path, "wb") as f:
                    f.write(fetch(url))
            except Exception as e:
                print(f"  warning: {name} failed ({e}) — using fallback")
                path = None
        paths[name] = path
    return paths


def get_font(path, size: int):
    if path and os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def duotone(img: Image.Image) -> Image.Image:
    """Map black -> lapis, white -> cream."""
    gray = img.convert("L")
    r_lut = [round(LAPIS[0] + (CREAM[0] - LAPIS[0]) * i / 255) for i in range(256)]
    g_lut = [round(LAPIS[1] + (CREAM[1] - LAPIS[1]) * i / 255) for i in range(256)]
    b_lut = [round(LAPIS[2] + (CREAM[2] - LAPIS[2]) * i / 255) for i in range(256)]
    r, g, b = gray.convert("RGB").split()
    return Image.merge("RGB", (r.point(r_lut), g.point(g_lut), b.point(b_lut)))


def gen_banner(plate_url: str, vol: int, month: str, year: str, output: str):
    repo_root = os.path.dirname(os.path.abspath(__file__))
    font_dir  = os.path.join(repo_root, ".fonts")

    print("ensuring fonts ...")
    fonts = ensure_fonts(font_dir)
    f_meta  = get_font(fonts.get("FragmentMono-Regular.ttf"),  14)
    f_title = get_font(fonts.get("CormorantUpright-Bold.ttf"), 68)
    f_tag   = get_font(fonts.get("Newsreader-Italic.ttf"),     21)

    # --- Plate ---
    print(f"fetching plate ...")
    plate = Image.open(io.BytesIO(fetch(plate_url))).convert("RGB")
    plate = duotone(plate)
    # Scale to banner width
    scale = BANNER_W / plate.width
    plate = plate.resize((BANNER_W, int(plate.height * scale)), Image.LANCZOS)
    # Crop from slight top-bias
    crop_top = max(0, int(plate.height * 0.08))
    plate = plate.crop((0, crop_top, BANNER_W, crop_top + PLATE_H))

    # --- Text section ---
    text_img = Image.new("RGB", (BANNER_W, TEXT_H), CREAM)
    draw = ImageDraw.Draw(text_img)

    vol_str = VOL_ROMAN[vol] if vol < len(VOL_ROMAN) else str(vol)
    yr_str  = YEAR_ROMAN.get(str(year), str(year))
    meta    = f"ARCHIVE-DIVE.  /  VOL. {vol_str}  ·  {month.upper()}  ·  {yr_str}  ·  108"

    draw.text((48, 28),  meta,                                                        font=f_meta,  fill=INK)
    draw.text((44, 54),  "What Surfaced This Month",                                  font=f_title, fill=INK)
    draw.text((50, 172), "⁂  papers nobody cited, datasets nobody re-ran, specimens nobody re-examined.",
              font=f_tag, fill=INK)

    # --- Composite ---
    banner = Image.new("RGB", (BANNER_W, BANNER_H), CREAM)
    banner.paste(plate,    (0, 0))
    banner.paste(text_img, (0, PLATE_H))
    banner.save(output, "PNG", optimize=True)
    print(f"wrote {output}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit("usage: gen_banner.py PLATE_URL VOL MONTH YEAR OUTPUT")
    _, plate_url, vol, month, year, output = sys.argv
    gen_banner(plate_url, int(vol), month, year, output)
