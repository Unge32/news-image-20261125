#!/usr/bin/env python3
"""THE ATLAS LEDGER - Wednesday 25 November 2026.
Fresh renderer for news-image-20261125. Draws a 1024x1024 broadsheet
from stories.json (34-38 stories, all first reported 25 Nov 2026,
8 regions). Pure PIL, no network, deterministic output.
"""
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 32
CONTENT_W = W - 2 * MARGIN

PAPER = (246, 241, 229)
INK = (22, 21, 19)
RED = (178, 28, 28)
RED_DK = (140, 20, 20)
GRAY = (107, 101, 88)
RULE = (60, 56, 48)
GOLD = (146, 90, 16)
BLUE = (29, 78, 160)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_NOTO_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to max pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and truncate with ellipsis to max_lines."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


def draw_centered(draw, y, text, fnt, fill, x0=MARGIN, x1=W - MARGIN):
    w_ = draw.textlength(text, font=fnt)
    x = x0 + (x1 - x0 - w_) / 2
    draw.text((x, y), text, font=fnt, fill=fill)
    return y


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)
    return y + width


# ---------------------------------------------------------------- map
# Equirectangular dotted world map. Grid 64 cols (lon -180..180) x
# 32 rows (lat 78N..-58S). Land defined by span rules per row band.
def _land(r, c):
    # North America (incl. Alaska/Canada/US/Mexico/Central Am.)
    if 2 <= r <= 4 and 2 <= c <= 14:
        return True
    if 5 <= r <= 7 and 3 <= c <= 15:
        return True
    if 8 <= r <= 9 and 5 <= c <= 15:
        return True
    if 10 <= r <= 12 and 8 <= c <= 14:
        return True
    if r == 13 and 10 <= c <= 13:
        return True
    # Greenland
    if 1 <= r <= 3 and 17 <= c <= 19:
        return True
    # South America
    if 14 <= r <= 16 and 12 <= c <= 17:
        return True
    if 17 <= r <= 19 and 13 <= c <= 16:
        return True
    if 20 <= r <= 22 and 14 <= c <= 15:
        return True
    if r == 23 and c == 15:
        return True
    # Europe
    if 4 <= r <= 5 and 29 <= c <= 34:
        return True
    if 6 <= r <= 8 and 29 <= c <= 36:
        return True
    if r == 9 and 30 <= c <= 34:
        return True
    # Africa
    if 9 <= r <= 11 and 30 <= c <= 38:
        return True
    if 12 <= r <= 15 and 31 <= c <= 37:
        return True
    if 16 <= r <= 18 and 32 <= c <= 36:
        return True
    if r == 19 and 33 <= c <= 35:
        return True
    # Middle East / Arabia
    if 9 <= r <= 11 and 37 <= c <= 40:
        return True
    # Asia (Russia / Central / China / India)
    if 2 <= r <= 4 and 36 <= c <= 58:
        return True
    if 5 <= r <= 7 and 37 <= c <= 57:
        return True
    if 8 <= r <= 10 and 38 <= c <= 54:
        return True
    if 9 <= r <= 11 and 42 <= c <= 48:
        return True  # India
    if 11 <= r <= 12 and 44 <= c <= 50:
        return True  # SE Asia mainland
    # Japan
    if 6 <= r <= 8 and 56 <= c <= 57:
        return True
    # Indonesia / PNG islands
    if 13 <= r <= 14 and 47 <= c <= 55:
        return True
    # Australia
    if 20 <= r <= 23 and 49 <= c <= 56:
        return True
    # New Zealand
    if 23 <= r <= 24 and 58 <= c <= 59:
        return True
    return False


def lonlat_to_xy(lon, lat, x0, y0, w_, h_):
    fx = (lon + 180.0) / 360.0
    fy = (78.0 - lat) / 136.0
    return x0 + fx * w_, y0 + fy * h_


def draw_dot_map(draw, x0, y0, w_, h_):
    cols, rows = 64, 32
    cw, ch = w_ / cols, h_ / rows
    for r in range(rows):
        if r % 2 == 1:
            continue
        for c in range(cols):
            if _land(r, c):
                cx = x0 + (c + 0.5) * cw
                cy = y0 + (r + 0.5) * ch
                rad = 1.2
                draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                             fill=(120, 112, 96))


# ------------------------------------------------------- illustrations
def illo_summit(draw, x0, y0, w_, h_):
    """Flags + podium: diplomacy/summit story."""
    sky = (214, 196, 160)
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=sky)
    draw.rectangle([x0, y0 + h_ * 0.72, x0 + w_, y0 + h_], fill=(122, 94, 60))
    # flag poles
    for i, col in enumerate([(178, 28, 28), (29, 78, 160), (22, 21, 19),
                             (146, 90, 16), (34, 120, 70)]):
        fx = x0 + w_ * (0.14 + i * 0.18)
        draw.line([(fx, y0 + h_ * 0.16), (fx, y0 + h_ * 0.72)],
                  fill=INK, width=3)
        draw.polygon([(fx, y0 + h_ * 0.16), (fx + 26, y0 + h_ * 0.22),
                      (fx, y0 + h_ * 0.30)], fill=col)
    # podium + figures
    px = x0 + w_ * 0.5
    draw.rectangle([px - 34, y0 + h_ * 0.62, px + 34, y0 + h_ * 0.72],
                   fill=(70, 60, 44))
    for dx, col in [(-52, (29, 78, 160)), (0, (178, 28, 28)),
                    (52, (34, 120, 70))]:
        cx = px + dx
        draw.ellipse([cx - 11, y0 + h_ * 0.42, cx + 11, y0 + h_ * 0.58],
                     fill=(232, 200, 160))
        draw.polygon([(cx - 16, y0 + h_ * 0.72), (cx, y0 + h_ * 0.56),
                      (cx + 16, y0 + h_ * 0.72)], fill=col)


def illo_markets(draw, x0, y0, w_, h_):
    """Candlestick chart + rising arrow: markets/economy story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(18, 24, 38))
    # grid
    for gy in range(1, 4):
        yy = y0 + h_ * gy / 4
        draw.line([(x0 + 8, yy), (x0 + w_ - 8, yy)],
                  fill=(48, 58, 80), width=1)
    candles = [(0.10, 0.55, 0.42), (0.24, 0.48, 0.60), (0.38, 0.62, 0.44),
               (0.52, 0.40, 0.58), (0.66, 0.50, 0.30), (0.80, 0.34, 0.46)]
    for fx, lo, hi in candles:
        cx = x0 + w_ * fx
        up = hi < lo
        col = (46, 160, 90) if up else (210, 60, 50)
        draw.line([(cx, y0 + h_ * hi), (cx, y0 + h_ * (lo + 0.14))],
                  fill=col, width=2)
        draw.rectangle([cx - 7, y0 + h_ * hi, cx + 7, y0 + h_ * lo],
                       fill=col)
    # rising arrow
    pts = [(x0 + w_ * 0.06, y0 + h_ * 0.78), (x0 + w_ * 0.34, y0 + h_ * 0.52),
           (x0 + w_ * 0.52, y0 + h_ * 0.62), (x0 + w_ * 0.94, y0 + h_ * 0.14)]
    draw.line(pts, fill=(250, 200, 60), width=5)
    ax, ay = pts[-1]
    draw.polygon([(ax, ay - 12), (ax + 16, ay + 2), (ax - 2, ay + 12)],
                 fill=(250, 200, 60))


def illo_chip(draw, x0, y0, w_, h_):
    """Semiconductor chip + circuit traces: tech story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(12, 30, 44))
    # circuit traces
    for i in range(6):
        yy = y0 + h_ * (0.12 + i * 0.15)
        draw.line([(x0 + 6, yy), (x0 + w_ * 0.30, yy)], fill=(40, 110, 130),
                  width=2)
        draw.ellipse([x0 + w_ * 0.30 - 3, yy - 3, x0 + w_ * 0.30 + 3,
                      yy + 3], fill=(60, 190, 220))
        draw.line([(x0 + w_ - 6, yy), (x0 + w_ * 0.70, yy)],
                  fill=(40, 110, 130), width=2)
        draw.ellipse([x0 + w_ * 0.70 - 3, yy - 3, x0 + w_ * 0.70 + 3,
                      yy + 3], fill=(60, 190, 220))
    cx, cy = x0 + w_ / 2, y0 + h_ / 2
    s = min(w_, h_) * 0.34
    for k in range(5):
        off = -s / 2 + k * s / 4
        draw.line([(cx + off, cy - s / 2 - 10), (cx + off, cy - s / 2)],
                  fill=(200, 210, 220), width=3)
        draw.line([(cx + off, cy + s / 2), (cx + off, cy + s / 2 + 10)],
                  fill=(200, 210, 220), width=3)
        draw.line([(cx - s / 2 - 10, cy + off), (cx - s / 2, cy + off)],
                  fill=(200, 210, 220), width=3)
        draw.line([(cx + s / 2, cy + off), (cx + s / 2 + 10, cy + off)],
                  fill=(200, 210, 220), width=3)
    draw.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                   fill=(30, 60, 90), outline=(200, 210, 220), width=3)
    isz = s * 0.45
    draw.rectangle([cx - isz, cy - isz, cx + isz, cy + isz],
                   fill=(60, 190, 220))
    draw.text((cx - 8, cy - 12), "AI", font=font(F_SANS_B, 22),
              fill=(12, 30, 44))


def illo_storm(draw, x0, y0, w_, h_):
    """Storm cloud + lightning + waves: weather/disaster story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(52, 64, 84))
    # clouds
    for cx, cy, r in [(0.30, 0.34, 26), (0.48, 0.28, 32), (0.66, 0.36, 24),
                      (0.20, 0.42, 20), (0.80, 0.44, 18)]:
        draw.ellipse([x0 + w_ * cx - r, y0 + h_ * cy - r * 0.7,
                      x0 + w_ * cx + r, y0 + h_ * cy + r * 0.7],
                     fill=(210, 214, 220))
    # lightning
    lx = x0 + w_ * 0.52
    draw.polygon([(lx, y0 + h_ * 0.44), (lx - 14, y0 + h_ * 0.66),
                  (lx - 2, y0 + h_ * 0.66), (lx - 12, y0 + h_ * 0.88),
                  (lx + 10, y0 + h_ * 0.62), (lx - 2, y0 + h_ * 0.62)],
                 fill=(250, 200, 60))
    # waves
    for wy in (0.82, 0.90):
        yy = y0 + h_ * wy
        for k in range(5):
            xx = x0 + w_ * (0.05 + k * 0.19)
            draw.arc([xx, yy - 8, xx + 26, yy + 8], 180, 360,
                     fill=(120, 190, 230), width=3)


def illo_rocket(draw, x0, y0, w_, h_):
    """Rocket launch + stars: space/science story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(10, 14, 34))
    for sx, sy in [(0.12, 0.16), (0.30, 0.08), (0.55, 0.20), (0.78, 0.10),
                   (0.90, 0.30), (0.22, 0.34), (0.68, 0.38), (0.40, 0.26)]:
        draw.ellipse([x0 + w_ * sx - 2, y0 + h_ * sy - 2,
                      x0 + w_ * sx + 2, y0 + h_ * sy + 2], fill=(255, 255, 255))
    # moon
    draw.ellipse([x0 + w_ * 0.78, y0 + h_ * 0.06, x0 + w_ * 0.94,
                  y0 + h_ * 0.24], fill=(220, 220, 200))
    cx = x0 + w_ * 0.5
    # flame
    draw.polygon([(cx - 12, y0 + h_ * 0.66), (cx + 12, y0 + h_ * 0.66),
                  (cx, y0 + h_ * 0.92)], fill=(250, 160, 40))
    draw.polygon([(cx - 6, y0 + h_ * 0.66), (cx + 6, y0 + h_ * 0.66),
                  (cx, y0 + h_ * 0.82)], fill=(250, 220, 90))
    # body
    draw.polygon([(cx - 16, y0 + h_ * 0.66), (cx - 16, y0 + h_ * 0.34),
                  (cx, y0 + h_ * 0.18), (cx + 16, y0 + h_ * 0.34),
                  (cx + 16, y0 + h_ * 0.66)], fill=(235, 235, 230))
    draw.ellipse([cx - 7, y0 + h_ * 0.30, cx + 7, y0 + h_ * 0.44],
                 fill=(29, 78, 160))
    draw.polygon([(cx - 16, y0 + h_ * 0.52), (cx - 30, y0 + h_ * 0.68),
                  (cx - 16, y0 + h_ * 0.68)], fill=(178, 28, 28))
    draw.polygon([(cx + 16, y0 + h_ * 0.52), (cx + 30, y0 + h_ * 0.68),
                  (cx + 16, y0 + h_ * 0.68)], fill=(178, 28, 28))
    # smoke
    for sx, sy, r in [(0.34, 0.86, 16), (0.48, 0.92, 20), (0.64, 0.88, 15)]:
        draw.ellipse([x0 + w_ * sx - r, y0 + h_ * sy - r * 0.6,
                      x0 + w_ * sx + r, y0 + h_ * sy + r * 0.6],
                     fill=(200, 200, 200))


def illo_ballot(draw, x0, y0, w_, h_):
    """Ballot box + check: election/politics story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(232, 222, 198))
    bx, by = x0 + w_ * 0.5, y0 + h_ * 0.56
    draw.rectangle([bx - 52, by - 8, bx + 52, by + 52], fill=(178, 28, 28))
    draw.rectangle([bx - 60, by - 20, bx + 60, by - 8], fill=(140, 20, 20))
    draw.rectangle([bx - 16, by - 20, bx + 16, by - 14], fill=(22, 21, 19))
    # ballot going in
    draw.polygon([(bx - 22, by - 62), (bx + 22, by - 62), (bx + 14, by - 22),
                  (bx - 14, by - 22)], fill=(255, 255, 255),
                 outline=INK)
    draw.line([(bx - 12, by - 48), (bx + 4, by - 34), (bx + 14, by - 54)],
              fill=(34, 120, 70), width=4)
    # check seal
    draw.ellipse([x0 + w_ * 0.80, y0 + h_ * 0.10, x0 + w_ * 0.94,
                  y0 + h_ * 0.30], fill=(34, 120, 70))
    draw.line([(x0 + w_ * 0.83, y0 + h_ * 0.20),
               (x0 + w_ * 0.86, y0 + h_ * 0.25),
               (x0 + w_ * 0.92, y0 + h_ * 0.14)], fill=(255, 255, 255),
              width=4)


def illo_stadium(draw, x0, y0, w_, h_):
    """Stadium + ball: sport story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(24, 90, 52))
    # stands
    draw.polygon([(x0, y0 + h_ * 0.42), (x0 + w_, y0 + h_ * 0.42),
                  (x0 + w_ * 0.88, y0 + h_ * 0.10),
                  (x0 + w_ * 0.12, y0 + h_ * 0.10)], fill=(200, 200, 190))
    for k in range(9):
        xx = x0 + w_ * (0.16 + k * 0.085)
        draw.ellipse([xx - 4, y0 + h_ * 0.22, xx + 4, y0 + h_ * 0.30],
                     fill=(178, 28, 28) if k % 2 else (29, 78, 160))
    # pitch lines
    draw.line([(x0 + w_ * 0.5, y0 + h_ * 0.42),
               (x0 + w_ * 0.5, y0 + h_)], fill=(255, 255, 255), width=2)
    draw.ellipse([x0 + w_ * 0.42, y0 + h_ * 0.62, x0 + w_ * 0.58,
                  y0 + h_ * 0.86], outline=(255, 255, 255), width=2)
    # ball
    cx, cy = x0 + w_ * 0.5, y0 + h_ * 0.74
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 255, 255),
                 outline=INK)
    draw.polygon([(cx - 5, cy - 5), (cx + 5, cy - 5), (cx, cy + 6)],
                 fill=INK)


def illo_quake(draw, x0, y0, w_, h_):
    """Cracked earth + tilted buildings: quake/disaster story."""
    draw.rectangle([x0, y0, x0 + w_, y0 + h_], fill=(228, 210, 180))
    gy = y0 + h_ * 0.66
    draw.rectangle([x0, gy, x0 + w_, y0 + h_], fill=(150, 120, 84))
    # buildings (one tilted)
    draw.rectangle([x0 + w_ * 0.10, y0 + h_ * 0.30, x0 + w_ * 0.30, gy],
                   fill=(90, 84, 76))
    draw.polygon([(x0 + w_ * 0.42, gy), (x0 + w_ * 0.58, y0 + h_ * 0.22),
                  (x0 + w_ * 0.66, y0 + h_ * 0.28),
                  (x0 + w_ * 0.52, gy)], fill=(120, 112, 100))
    draw.rectangle([x0 + w_ * 0.72, y0 + h_ * 0.38, x0 + w_ * 0.90, gy],
                   fill=(70, 64, 58))
    # windows
    for bx in (0.14, 0.20, 0.76, 0.82):
        for by in (0.38, 0.48):
            draw.rectangle([x0 + w_ * bx, y0 + h_ * by, x0 + w_ * bx + 8,
                            y0 + h_ * by + 8], fill=(250, 220, 90))
    # crack
    draw.line([(x0 + w_ * 0.5, gy), (x0 + w_ * 0.46, gy + 14),
               (x0 + w_ * 0.54, gy + 26), (x0 + w_ * 0.48, y0 + h_)],
              fill=(40, 30, 22), width=4)


ILLOS = {
    "summit": illo_summit,
    "markets": illo_markets,
    "chip": illo_chip,
    "storm": illo_storm,
    "rocket": illo_rocket,
    "ballot": illo_ballot,
    "stadium": illo_stadium,
    "quake": illo_quake,
}


# ---------------------------------------------------------------- layout
def draw_globe_mark(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=3)
    draw.ellipse([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r],
                 outline=RED, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=RED, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 0, 360,
             fill=RED, width=2)


def render(data, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = data["total"]
    regions = data["regions"]
    countries = data["countries"]

    # ---- top micro-bar
    f_micro = font(F_SANS_B, 12)
    d.text((MARGIN, 8), "THE ATLAS LEDGER  •  WORLD DESK",
           font=f_micro, fill=INK)
    right = "WEDNESDAY EDITION  •  25 NOV 2026"
    d.text((W - MARGIN - d.textlength(right, font=f_micro), 8), right,
           font=f_micro, fill=INK)
    rule(d, 26, width=3)

    # ---- masthead: THE ATLAS LEDGER + globe mark
    f_mast = font(F_SERIF, 56)
    title = "THE ATLAS LEDGER"
    tw = d.textlength(title, font=f_mast)
    gx = MARGIN + 30
    draw_globe_mark(d, gx, 58, 21)
    tx = (W - tw) / 2 + 12
    d.text((tx, 30), title, font=f_mast, fill=INK)
    # ATLAS tag under globe
    f_tag = font(F_SANS_B, 10)
    d.text((gx - 16, 82), "ATLAS", font=f_tag, fill=RED)
    rule(d, 94, width=2)

    # ---- kicker
    f_kick = font(F_SANS_B, 21)
    draw_centered(d, 100, "T H E   W O R L D   I N   O N E   D A Y",
                  f_kick, RED)

    # ---- giant headline: the date
    f_head = font(F_SERIF, 50)
    draw_centered(d, 124, "Wednesday 25 November 2026", f_head, INK)

    # ---- badge: story + region count
    f_badge = font(F_SANS_B, 18)
    badge = ("%d STORIES  •  %d REGIONS  •  %d ATLAS BUREAUS  •  "
             "ALL DATED 25 NOVEMBER 2026"
             % (total, regions, data.get("bureaus", regions)))
    bw = d.textlength(badge, font=f_badge) + 36
    bx0 = (W - bw) / 2
    d.rounded_rectangle([bx0, 180, bx0 + bw, 206], radius=13, fill=RED)
    d.text((bx0 + 18, 185), badge, font=f_badge, fill=(255, 255, 255))

    # ---- 3 red sub-headlines
    y = 214
    f_subtag = font(F_SANS_B, 10)
    f_sub = font(F_SERIF, 20)
    f_subdek = font(F_SANS, 12)
    col_w = (CONTENT_W - 2 * 18) / 3
    for i, s in enumerate(data["subheads"]):
        x0 = MARGIN + i * (col_w + 18)
        d.text((x0, y), s["bureau"], font=f_subtag, fill=RED)
        yy = y + 12
        for ln in fit_lines(d, s["headline"], f_sub, col_w, 2):
            d.text((x0, yy), ln, font=f_sub, fill=RED_DK)
            yy += 21
        for ln in fit_lines(d, s["dek"], f_subdek, col_w, 2):
            d.text((x0, yy), ln, font=f_subdek, fill=INK)
            yy += 13
    rule(d, 298, width=1, fill=RULE)

    # ---- UTC timeline strip
    y = 304
    f_tl_lab = font(F_SANS_B, 11)
    d.text((MARGIN, y), "THE DAY SO FAR  —  UTC", font=f_tl_lab, fill=INK)
    y += 15
    tl = data["timeline"]
    seg = CONTENT_W / len(tl)
    f_time = font(F_SANS_B, 13)
    f_tl = font(F_SANS, 10)
    for i, t in enumerate(tl):
        x0 = MARGIN + i * seg
        d.text((x0 + 2, y), t["time"], font=f_time, fill=RED)
        yy = y + 16
        for ln in fit_lines(d, t["label"], f_tl, seg - 8, 1):
            d.text((x0 + 2, yy), ln, font=f_tl, fill=INK)
            yy += 12
    rule(d, 350, width=1, fill=RULE)

    # ---- The Day in Numbers
    y = 356
    f_num_lab = font(F_SANS_B, 11)
    d.text((MARGIN, y), "THE DAY IN NUMBERS", font=f_num_lab, fill=INK)
    y += 14
    stats = [
        (str(total), "STORIES, ALL DATED TODAY"),
        (str(regions), "REGIONS, 8 ATLAS BUREAUS"),
        (str(countries), "COUNTRIES ON THE DATELINE"),
        (data["marquee"]["number"], data["marquee"]["label"]),
    ]
    box_w = (CONTENT_W - 3 * 10) / 4
    f_num = font(F_SERIF, 30)
    f_numcap = font(F_SANS_B, 9)
    for i, (num, cap) in enumerate(stats):
        x0 = MARGIN + i * (box_w + 10)
        d.rectangle([x0, y, x0 + box_w, y + 44], outline=RULE, width=1)
        nw = d.textlength(num, font=f_num)
        d.text((x0 + (box_w - nw) / 2, y + 3), num, font=f_num, fill=RED_DK)
        for j, ln in enumerate(fit_lines(d, cap, f_numcap, box_w - 10, 2)):
            d.text((x0 + 5, y + 32 + j * 10), ln, font=f_numcap, fill=GRAY)
    y = y + 44 + 6
    rule(d, y, width=1, fill=RULE)

    # ---- 3 hero stories with sharp illustrations
    y += 8
    f_hero_tag = font(F_SANS_B, 10)
    f_hero = font(F_SERIF, 19)
    f_herodek = font(F_SANS, 12)
    hero_w = (CONTENT_W - 2 * 14) / 3
    hero_h = 96
    top = y
    for i, s in enumerate(data["heroes"]):
        x0 = MARGIN + i * (hero_w + 14)
        ILLOS[s["illo"]](d, x0, y, hero_w, hero_h)
        yy = y + hero_h + 6
        d.text((x0, yy), s["bureau"], font=f_hero_tag, fill=RED)
        yy += 12
        for ln in fit_lines(d, s["headline"], f_hero, hero_w, 3):
            d.text((x0, yy), ln, font=f_hero, fill=INK)
            yy += 20
        for ln in fit_lines(d, s["dek"], f_herodek, hero_w, 2):
            d.text((x0, yy), ln, font=f_herodek, fill=(48, 44, 38))
            yy += 13
    y = top + hero_h + 6 + 12 + 3 * 20 + 2 * 13 + 6
    rule(d, y, width=1, fill=RULE)

    # ---- grid of 10 stories
    y += 8
    f_grid_tag = font(F_SANS_B, 9)
    f_grid = font(F_SERIF, 15)
    f_griddek = font(F_SANS, 11)
    grid = data["grid"]
    gcol_w = (CONTENT_W - 24) / 2
    row_h = 29
    for i, s in enumerate(grid):
        gx = MARGIN + (i % 2) * (gcol_w + 24)
        gy = y + (i // 2) * row_h
        d.text((gx, gy), s["bureau"], font=f_grid_tag, fill=RED)
        head = s["headline"]
        max_hw = gcol_w - 118 - 4
        while d.textlength(head, font=f_grid) > max_hw and len(head) > 4:
            head = head[:-1]
        if head != s["headline"]:
            head = head.rstrip() + "..."
        d.text((gx + 118, gy), head, font=f_grid, fill=INK)
        for ln in fit_lines(d, s["dek"], f_griddek, gcol_w, 1):
            d.text((gx, gy + 15), ln, font=f_griddek, fill=(48, 44, 38))
    y = y + 5 * row_h + 4
    rule(d, y, width=1, fill=RULE)

    # ---- numbered list: the rest of the day
    y += 6
    f_list_lab = font(F_SANS_B, 11)
    rest = total - 16
    d.text((MARGIN, y), "THE REST OF THE DAY  —  %d MORE STORIES" % rest,
           font=f_list_lab, fill=INK)
    y += 15
    f_list = font(F_SANS, 11)
    f_list_b = font(F_SANS_B, 11)
    listed = data["listed"]
    lcol_w = (CONTENT_W - 24) / 2
    lrow = 12
    for i, s in enumerate(listed):
        lx = MARGIN + (i % 2) * (lcol_w + 24)
        ly = y + (i // 2) * lrow
        num = "%d." % (17 + i)
        d.text((lx, ly), num, font=f_list_b, fill=RED)
        nw = d.textlength(num + " ", font=f_list_b)
        head = s["headline"]
        while d.textlength(head, font=f_list) > lcol_w - nw - 4 and len(head) > 4:
            head = head[:-1]
        if head != s["headline"]:
            head = head.rstrip() + "..."
        d.text((lx + nw, ly), head, font=f_list, fill=INK)
    y = y + ((len(listed) + 1) // 2) * lrow + 4

    # ---- dotted world map strip
    map_h = 50
    d.text((MARGIN, y), "WHERE THE DAY HAPPENED", font=f_list_lab, fill=INK)
    y += 12
    draw_dot_map(d, MARGIN, y, 620, map_h)
    # red dots for story locations
    all_stories = (data["subheads"] + data["heroes"] + data["grid"]
                   + data["listed"])
    for s in all_stories:
        if "lat" in s and "lon" in s:
            px, py = lonlat_to_xy(s["lon"], s["lat"], MARGIN, y, 620, map_h)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED,
                      outline=(255, 255, 255))
    # map caption right side
    cap_x = MARGIN + 640
    f_cap = font(F_SANS, 11)
    f_cap_b = font(F_SANS_B, 11)
    d.text((cap_x, y + 2), "RED DOTS MARK", font=f_cap_b, fill=RED)
    cap_lines = fit_lines(d, "the dateline of every story on "
                          "this page — from Jiuquan to Canberra, "
                          "Seoul to São Paulo.", f_cap, 300, 4)
    yy = y + 16
    for ln in cap_lines:
        d.text((cap_x, yy), ln, font=f_cap, fill=INK)
        yy += 13
    y = y + map_h + 6
    rule(d, y, width=2)

    # ---- DATE CHECK footer (black band)
    y += 6
    d.rectangle([0, y, W, y + 28], fill=INK)
    f_foot = font(F_SANS_B, 12)
    foot = ("DATE CHECK — Every story here was first reported Wednesday "
            "25 November 2026. No 24 November story. — ATLAS")
    draw_centered(d, y + 7, foot, f_foot, (255, 255, 255), x0=0, x1=W)

    img.save(out_path, optimize=True)
    return out_path


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    out = os.path.join(HERE, "entry.png")
    render(data, out)
    size = os.path.getsize(out)
    print("wrote %s %d bytes" % (out, size))
    assert size <= 1048576, "entry.png over 1 MiB: %d" % size
    im = Image.open(out)
    assert im.size == (1024, 1024), "wrong size: %s" % (im.size,)


if __name__ == "__main__":
    main()
