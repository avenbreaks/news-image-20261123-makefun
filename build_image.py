#!/usr/bin/env python3
"""Compose the entry image for make.fun news-image-20261123.

Builds a 1024x1024 newspaper-front-page image summing up the world news
of Monday 23 November 2026, from four AI-generated news-style photos
(hero + three story photos) and one drawn stat panel. Deterministic:
same inputs -> same bytes (PNG is written with fixed settings; the
entry itself is shipped as a JPEG copy of this render).

Sources (all verified against live news on 23 Nov 2026, ~00:20 UTC):
- Russian cargo ship still on fire off Finland after a drone attack
  in the Baltic (Reuters/BBC).
- At least 14 people missing after a Russian drone hit a building in
  the Kyiv region (Reuters, quoting Zelenskiy).
- Iran strikes US military bases in Bahrain as the Strait of Hormuz
  conflict widens (Dunya News / Observer Voice).
- COP31: Turkiye's final draft omits the words 'fossil fuels'
  (Observer Voice / Daily Jagran).
- Seven bodies recovered, 50 missing after a factory fire in
  Indonesia (Jagran Josh).
- Ticker: South Korea's education minister quits over an AI exam-
  cheating scandal (BBC); Nepal PM Balendra Shah in Delhi for talks
  with Modi; India posts a record 720/9d in the Wellington Test;
  UN talks on lethal AI weapons to continue.
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "news-image-20261123-work"))  # photos live in the sibling work dir

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

W = H = 1024
PAPER = (246, 241, 230)
INK = (22, 22, 22)
RED = (178, 34, 34)
NAVY = (18, 38, 66)
GRAY = (90, 86, 78)
WHITE = (255, 255, 255)
DARKBAND = (16, 24, 38)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning list of lines fitting max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_text(draw, xy, text, fnt, color, max_w, leading, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += leading
    return y


def cover_crop(im, tw, th):
    """Center-crop image to target aspect, then resize (Lanczos)."""
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def kicker_chip(draw, x, y, text, fnt, bg=RED, fg=WHITE):
    tw = draw.textlength(text, font=fnt) + 18
    th = fnt.size + 12
    draw.rectangle([x, y, x + tw, y + th], fill=bg)
    draw.text((x + 9, y + 6), text, font=fnt, fill=fg)
    return tw


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- Masthead -----------------------------------------------------
    d.rectangle([0, 0, W, 8], fill=RED)
    d.text((W // 2, 26), "THE WORLD IN ONE IMAGE",
           font=font(SERIF_BLACK, 46), fill=INK, anchor="ma")
    d.text((W // 2, 82), "MONDAY, 23 NOVEMBER 2026",
           font=font(SANS_BOLD, 19), fill=RED, anchor="ma")
    d.line([24, 116, W - 24, 116], fill=INK, width=2)
    d.line([24, 121, W - 24, 121], fill=INK, width=1)

    # ---- Hero photo ---------------------------------------------------
    hero = Image.open(os.path.join(
        WORK, "media-generation-hero-ship-fire-0-95264ac1-af9d-4977-a782-8cf1303fbf2f.webp"
    )).convert("RGB")
    hero = cover_crop(hero, 976, 420)
    img.paste(hero, (24, 132))
    # bottom gradient scrim for the headline
    scrim = Image.new("RGBA", (976, 190), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for i in range(190):
        a = int(200 * (i / 189) ** 1.6)
        sd.line([(0, 190 - i), (976, 190 - i)], fill=(8, 10, 16, a))
    img.paste(scrim, (24, 132 + 420 - 190), scrim)
    d = ImageDraw.Draw(img, "RGBA")
    kicker_chip(d, 40, 148, "WAR AT SEA", font(SANS_BLACK, 17))
    d.text((40, 392), "BALTIC BLAZE",
           font=font(SERIF_BLACK, 64), fill=WHITE)
    fit_text(d, (40, 462),
             "Russian cargo ship still burning off Finland after a drone "
             "attack — the war spills into the Baltic.",
             font(SANS_BOLD, 21), WHITE, 940, 27, max_lines=2)

    # ---- Story grid 2x2 ----------------------------------------------
    gx, gy = 24, 576
    cw, ch, gap = 480, 176, 16
    cards = [
        ("media-generation-kyiv-building-0-1732638c-6e34-4706-a6de-ee218dda18b4.webp",
         "UKRAINE", "Drone hits Kyiv homes — 14 missing",
         "Rescuers search the rubble after a Russian drone strike on a "
         "building in the Kyiv region."),
        ("media-generation-hormuz-strait-0-70013b5f-678a-4c1d-a5e7-1654a2ef8719.webp",
         "THE GULF", "Iran strikes US bases in Bahrain",
         "Tehran hits back as the Strait of Hormuz conflict widens "
         "across the Gulf."),
        ("media-generation-cop31-summit-0-64bbd130-72e9-4ab5-b179-2c09dce9695d.webp",
         "CLIMATE", "COP31 draft drops “fossil fuels”",
         "Türkiye’s final text omits the words behind global warming; "
         "the talks stall."),
        (None, "DISASTER", "Factory fire in Indonesia",
         "Seven bodies recovered and 50 people missing after a blaze at "
         "an Indonesian factory."),
    ]
    for i, (photo, kick, head, body) in enumerate(cards):
        cx = gx + (i % 2) * (cw + gap)
        cy = gy + (i // 2) * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=WHITE,
                    outline=(200, 192, 172), width=1)
        tx = cx + 14
        if photo:
            ph = cover_crop(
                Image.open(os.path.join(WORK, photo)).convert("RGB"),
                168, ch)
            img.paste(ph, (cx, cy))
            tx = cx + 168 + 14
            tw = cw - 168 - 28
        else:
            # drawn stat panel: big red number block
            d.rectangle([cx, cy, cx + 168, cy + ch], fill=RED)
            d.text((cx + 84, cy + 52), "50",
                   font=font(SANS_BLACK, 72), fill=WHITE, anchor="ma")
            d.text((cx + 84, cy + 128), "MISSING",
                   font=font(SANS_BLACK, 20), fill=WHITE, anchor="ma")
            tx = cx + 168 + 14
            tw = cw - 168 - 28
        d.text((tx, cy + 12), kick, font=font(SANS_BLACK, 15), fill=RED)
        fit_text(d, (tx, cy + 36), head, font(SERIF_BOLD, 23), INK,
                 tw, 27, max_lines=2)
        fit_text(d, (tx, cy + 96), body, font(SANS, 16), (74, 70, 62),
                 tw, 21, max_lines=3)

    # ---- Footer ticker ------------------------------------------------
    fy = 946
    d.rectangle([0, fy, W, H], fill=DARKBAND)
    d.text((24, fy + 10), "ALSO TODAY",
           font=font(SANS_BLACK, 16), fill=(255, 176, 66))
    fit_text(d, (24, fy + 32),
             "Seoul minister quits over AI exam-cheating scandal  ·  Nepal PM "
             "in Delhi for talks with Modi  ·  India posts record 720/9 in the "
             "Wellington Test  ·  UN to keep talking on lethal AI weapons",
             font(SANS, 15), (226, 230, 238), W - 48, 19, max_lines=2)

    out_png = os.path.join(HERE, "entry-preview.png")
    img.save(out_png, "PNG", optimize=True)
    print("wrote", out_png, os.path.getsize(out_png), "bytes")


if __name__ == "__main__":
    main()
