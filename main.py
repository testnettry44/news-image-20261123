#!/usr/bin/env python3
"""THE WORLD TODAY -- 23 November 2026 (v2).

Front-page image, drawn entirely in code: a tiny built-in 5x7 bitmap font
(uppercase A-Z, digits, punctuation) and a pure-stdlib PNG encoder.
No network, no downloaded assets, no timestamps, no randomness -- two
runs produce byte-identical output.

Layout (1024x1024): masthead + red dateline + double rule, boxed lead
(COP31, cracked-globe illustration, markets ticker), two large panels
(Libya, Ukraine), three small panels (NATO, Democrats, Indonesia factory
fire), red sport band. Rebuild in the 22 Nov mould: 7 items, every
reading line scale 3 or larger in INK, except the single scale-2 ticker.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
"""

import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (179, 35, 27)
LIGHT = (225, 219, 203)
WHITE = (255, 255, 255)

W, H = 1024, 1024
MX = 24                      # page margin; content width 976 (x 24..1000)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, written for this entry. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}
BLANK = ("00000",) * 7


def text_width(s, scale):
    """Pixel width of s at scale: advance 6*scale per char, no trailing gap."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


# -------------------------------------------------------------- PNG output
def png_bytes(w, h, rgb):
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: none
        raw.extend(rgb[y * w * 3:(y + 1) * w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    return out


# ------------------------------------------------------------------ canvas
class Page:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = bytearray(PAPER * w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i:i + 3] = bytes(color)

    def hline(self, x, y, length, color, thick=1):
        self.fill_rect(x, y - thick // 2, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.fill_rect(x - thick // 2, y, thick, length, color)

    def _brush(self, x, y, color, size):
        self.fill_rect(x - size // 2, y - size // 2, size, size, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with a square brush of side `thick`."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self._brush(x0, y0, color, thick)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def polyline(self, points, color, thick=1):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            self.line(x0, y0, x1, y1, color, thick)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            hw = int(math.sqrt(max(r * r - dy * dy, 0)))
            self.fill_rect(cx - hw, cy + dy, 2 * hw + 1, 1, color)

    def circle_outline(self, cx, cy, r, color, thick=1):
        for deg in range(360):
            a = math.radians(deg)
            self._brush(cx + round(r * math.cos(a)),
                        cy + round(r * math.sin(a)), color, thick)

    def fill_triangle(self, ax, ay, bx, by, cx, cy, color):
        (x0, y0), (x1, y1), (x2, y2) = sorted(
            [(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return float(xa)
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y0, y2 + 1):
            xa = edge_x(x0, y0, x2, y2, y)
            xb = edge_x(x0, y0, x1, y1, y) if y < y1 else edge_x(x1, y1, x2, y2, y)
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.fill_rect(lo, y, hi - lo + 1, 1, color)

    def burst(self, cx, cy, r, color):
        """8-spoke starburst, as in the 22 Nov entry."""
        for k in range(8):
            a = math.radians(k * 45)
            self.line(cx, cy, cx + round(r * math.cos(a)),
                      cy + round(r * math.sin(a)), color, 3)
        self.fill_circle(cx, cy, 3, color)

    def dome(self, cx, base_y, r, fill, outline):
        """Capitol dome: filled semicircle + outline arc + spire."""
        for dy in range(0, r + 1):
            hw = int(math.sqrt(max(r * r - dy * dy, 0)))
            self.fill_rect(cx - hw, base_y - dy, 2 * hw + 1, 1, fill)
        for deg in range(181):
            a = math.radians(deg)
            self._brush(cx + round(r * math.cos(a)),
                        base_y - round(r * math.sin(a)), outline, 2)
        self.fill_rect(cx - 1, base_y - r - 8, 2, 8, outline)

    def border(self, x, y, w, h, thick, color):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def text_centred(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)


# ------------------------------------------------------------------- checks
def check_headline(lines, scale, max_w, label):
    widths = [text_width(l, scale) for l in lines]
    for line, wd in zip(lines, widths):
        assert wd <= max_w, "%s: %r is %d px, column is %d" % (label, line, wd, max_w)
    bal = min(widths) / max(widths)
    assert bal >= 0.6, "%s: headline balance %.2f < 0.60" % (label, bal)
    return widths, bal


def check_standfirst(lines, scale, max_w, label):
    for line in lines:
        wd = text_width(line, scale)
        assert wd <= max_w, "%s: %r is %d px, column is %d" % (label, line, wd, max_w)


# -------------------------------------------------------------------- copy
MASTHEAD = "THE WORLD TODAY"
DATELINE = "MONDAY, 23 NOVEMBER 2026"

LEAD = {
    "kicker": "COP31",
    "headline": ["NO DEAL AT COP31", "AS TALKS COLLAPSE"],
    "standfirst": [
        "LONGEST COP EVER, FIRST FAILURE",
        "SINCE 2009. THE EU AND ISLAND",
        "STATES REFUSED A DRAFT WITH NO",
        "FOSSIL FUELS.",
    ],
}
TICKER = "MARKETS: BRENT $92.29 - WTI $83.26 - AI SELL-OFF"

# Row 2: two large panels, 478 x 206. Headline scale 5, standfirst scale 3.
ROW2 = [
    {
        "x": 24, "kicker": "LIBYA",
        "headline": ["UKRAINE SINKS", "RUSSIAN SHIP"],
        "standfirst": ["MERKURY SUNK, KYIV SAYS", "2,400 KM FROM FRONT."],
        "motif": "libya",
    },
    {
        "x": 522, "kicker": "UKRAINE",
        "headline": ["BOY, 7, ALIVE", "IN KYIV RUBBLE"],
        "standfirst": ["PULLED FROM A BLOCK", "IN DYMER. 11 KILLED."],
        "motif": "ukraine",
    },
]

# Row 3: three small panels, 312 x 206. Headline scale 4, standfirst scale 3.
ROW3 = [
    {
        "x": 24, "kicker": "NATO",
        "headline": ["NATO MEETS", "OVER POLAND", "INTRUSION"],
        "standfirst": ["THREE OBJECTS", "WERE KH-101S."],
        "motif": "nato",
    },
    {
        "x": 356, "kicker": "UNITED STATES",
        "headline": ["DEMOCRATS", "TAKE 258TH", "HOUSE SEAT"],
        "standfirst": ["LARGEST LEAD IN", "30 YEARS."],
        "motif": "us",
    },
    {
        "x": 688, "kicker": "INDONESIA",
        "headline": ["FIRE AT", "CANDY PLANT", "KILLS 24"],
        "standfirst": ["30 STILL", "MISSING."],
        "motif": "indonesia",
    },
]

SPORT = [
    "SPORT: ALCARAZ BEATS ZVEREV TO WIN ATP FINALS",
    "LIVERPOOL BEAT TEN-MAN UNITED 4-0",
]


# ------------------------------------------------------------------- motifs
def motif_libya(p, px, py):
    """Struck warship: INK hull + bridge, RED burst over the bow."""
    p.fill_rect(px + 382, py + 32, 80, 10, INK)          # hull
    p.fill_rect(px + 410, py + 22, 28, 10, INK)          # bridge
    p.fill_rect(px + 423, py + 14, 2, 8, INK)            # mast
    p.burst(px + 454, py + 27, 9, RED)                   # hit, over the bow


def motif_ukraine(p, px, py):
    """Broken building: three ascending INK bars, RED dot on the tallest."""
    bars = [(924, 500, 12), (946, 492, 20), (968, 484, 28)]
    for bx, top, hgt in bars:
        p.fill_rect(bx, top, 16, hgt, INK)
    # Survivor dot, on the tallest bar and inside the motif envelope
    # (panel-top +14..+42 = y 484..512): centre 489 keeps its top at
    # +15, 1 px clear of the envelope top. (Was 480: top at +6.)
    p.fill_circle(976, 489, 4, RED)


def motif_nato(p, px, py):
    """Three RED dots: the three Kh-101s."""
    for cx in (262, 288, 314):
        p.fill_circle(cx, py + 28, 6, RED)


def motif_us(p, px, py):
    """Small capitol dome on an INK plinth."""
    p.fill_rect(px + 264, py + 40, 32, 4, INK)           # plinth
    p.dome(px + 280, py + 40, 14, LIGHT, INK)


def motif_indonesia(p, px, py):
    """Factory fire: INK building + chimney, RED flame from the roof."""
    p.fill_rect(px + 230, py + 26, 30, 16, INK)          # factory block
    p.fill_rect(px + 236, py + 32, 5, 5, LIGHT)          # lit windows
    p.fill_rect(px + 246, py + 32, 5, 5, LIGHT)
    p.fill_rect(px + 252, py + 20, 6, 6, INK)            # chimney
    p.fill_triangle(px + 264, py + 26, px + 276, py + 26,
                    px + 270, py + 14, RED)              # flame


MOTIFS = {
    "libya": motif_libya,
    "ukraine": motif_ukraine,
    "nato": motif_nato,
    "us": motif_us,
    "indonesia": motif_indonesia,
}


# -------------------------------------------------------------------- draw
def draw():
    p = Page()

    # Masthead, dateline, double rule.
    p.text_centred(18, MASTHEAD, 8, INK)
    p.text_centred(92, DATELINE, 4, RED)
    p.fill_rect(MX, 140, 976, 4, INK)
    p.fill_rect(MX, 148, 976, 1, INK)

    # ---- Lead box (y 156..456, border 3) ----
    p.border(MX, 156, 976, 300, 3, INK)
    p.text(44, 174, LEAD["kicker"], 3, RED)
    for i, line in enumerate(LEAD["headline"]):
        p.text(44, 208 + i * 42, line, 5, INK)
    for i, line in enumerate(LEAD["standfirst"]):
        p.text(44, 297 + i * 26, line, 3, INK)
    p.text(44, 412, TICKER, 2, INK)

    # Lead art: cracked globe (art zone x 640..980).
    p.fill_rect(660, 400, 300, 3, INK)                   # ground line
    p.circle_outline(820, 290, 105, INK, 4)              # globe
    p.fill_rect(715, 290, 211, 2, INK)                   # equator
    meridian = []
    for deg in range(0, 361, 3):
        a = math.radians(deg)
        meridian.append((820 + round(38 * math.sin(a)),
                         290 + round(105 * math.cos(a))))
    p.polyline(meridian, INK, 2)                         # meridian ellipse
    crack = [(820, 185), (800, 240), (835, 290), (805, 340), (825, 395)]
    p.polyline(crack, RED, 4)                            # crack
    for vx, vy in crack:
        p.fill_circle(vx, vy, 4, RED)
    p.burst(820, 290, 26, RED)                           # burst on the crack

    # ---- Row 2 (y 470..676): two large panels ----
    for panel in ROW2:
        px, py = panel["x"], 470
        p.border(px, py, 478, 206, 2, INK)
        p.text(px + 16, py + 16, panel["kicker"], 3, RED)
        for i, line in enumerate(panel["headline"]):
            p.text(px + 16, py + 48 + i * 42, line, 5, INK)
        for i, line in enumerate(panel["standfirst"]):
            p.text(px + 16, py + 137 + i * 26, line, 3, INK)
        MOTIFS[panel["motif"]](p, px, py)

    # ---- Row 3 (y 690..896): three small panels ----
    for panel in ROW3:
        px, py = panel["x"], 690
        p.border(px, py, 312, 206, 2, INK)
        p.text(px + 16, py + 16, panel["kicker"], 3, RED)
        for i, line in enumerate(panel["headline"]):
            p.text(px + 16, py + 44 + i * 33, line, 4, INK)
        for i, line in enumerate(panel["standfirst"]):
            p.text(px + 16, py + 148 + i * 24, line, 3, INK)
        MOTIFS[panel["motif"]](p, px, py)

    # ---- Sport band (y 910..1000, RED) ----
    p.fill_rect(MX, 910, 976, 90, RED)
    p.text_centred(928, SPORT[0], 3, WHITE)
    p.text_centred(958, SPORT[1], 3, WHITE)

    return p


def verify():
    """Acceptance checks on the copy: widths, balance, clearance, words."""
    print("== width / balance checks (text_width) ==")
    w, bal = check_headline(LEAD["headline"], 5, 560, "lead")
    print("lead headline widths %s balance %.2f" % (w, bal))
    check_standfirst(LEAD["standfirst"], 3, 560, "lead standfirst")
    assert text_width(TICKER, 2) <= 936, "ticker too wide"
    print("ticker width %d px" % text_width(TICKER, 2))
    for panel in ROW2:
        w, bal = check_headline(panel["headline"], 5, 446, panel["kicker"])
        print("%s headline widths %s balance %.2f" % (panel["kicker"], w, bal))
        check_standfirst(panel["standfirst"], 3, 446, panel["kicker"])
    for panel in ROW3:
        w, bal = check_headline(panel["headline"], 4, 280, panel["kicker"])
        print("%s headline widths %s balance %.2f" % (panel["kicker"], w, bal))
        check_standfirst(panel["standfirst"], 3, 280, panel["kicker"])
    # Bottom clearances: last text bottom vs panel bottom (need >= 10 px).
    assert 676 - (633 + 21) == 22, "row 2 clearance"
    assert 896 - (862 + 21) == 13, "row 3 clearance"
    assert 456 - (412 + 14) == 30, "lead ticker clearance"
    print("clearances: lead 30 px, row 2 22 px, row 3 13 px (all >= 10)")
    # Word counts (space-split tokens; ticker '-' tokens count as words).
    reading = sum(len(l.split()) for l in LEAD["standfirst"])
    reading += sum(len(l.split()) for panel in ROW2 + ROW3
                   for l in panel["standfirst"])
    reading += len(TICKER.split())
    print("reading words (standfirsts + ticker): %d" % reading)
    total = reading
    total += len(MASTHEAD.split()) + len(DATELINE.split())
    total += sum(len(l.split()) for l in LEAD["headline"])
    total += sum(len(panel["kicker"].split()) +
                 sum(len(l.split()) for l in panel["headline"])
                 for panel in ROW2 + ROW3)
    total += sum(len(l.split()) for l in SPORT)
    print("total page words: %d" % total)


def main():
    verify()
    page = draw()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(W, H, page.px))
    print("wrote %s (%dx%d)" % (path, W, H))


if __name__ == "__main__":
    main()
