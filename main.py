#!/usr/bin/env python3
"""THE WORLD TODAY - MONDAY, 23 NOVEMBER 2026.

A newspaper front page summing up the day's world news, drawn entirely
in code. Pure Python 3 standard library: a hand-built 5x7 bitmap font
(uppercase, digits, punctuation) and a hand-rolled PNG encoder (zlib,
fixed settings). No network, no assets, no timestamps, no randomness:
two runs write byte-identical output.

Invocation (per the kit's competition.yaml / starter):
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
In the grader the output dir is /output.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (158, 27, 27)
GREY = (96, 90, 78)

# ---------------------------------------------------------------- font ----
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 cells per char, 1 gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            if not cur:
                cur = word
            elif len(cur) + 1 + len(word) <= max_chars:
                cur += " " + word
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, colour):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(colour) * (w * h))

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def hline(self, x, y, w, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.fill_rect(x, y, thick, h, colour)

    def draw_text(self, x, y, text, scale, colour):
        """Draw text left-aligned at (x, y); returns width drawn."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.fill_rect(
                            cx + c * scale, y + r * scale, scale, scale, colour
                        )
            cx += 6 * scale
        return cx - x - scale if text else 0

    def draw_text_centred(self, y, text, scale, colour, cx=512):
        w = text_width(text, scale)
        self.draw_text(cx - w // 2, y, text, scale, colour)


# -------------------------------------------------------------- stories ----
LEAD_KICKER = "LEAD STORY - COP31 CLIMATE TALKS, ANTALYA, TURKEY"
LEAD_HEADLINE = ("CLIMATE SUMMIT COLLAPSES", "IN FOSSIL FUEL ROW")
LEAD_BODY = (
    "COP31 TALKS IN ANTALYA COLLAPSED ON SUNDAY WITH NO DEAL - THE LONGEST "
    "COP IN HISTORY AND THE FIRST TO FAIL SINCE COPENHAGEN 2009. THE EU, "
    "SMALL ISLAND STATES AND OTHERS REFUSED A DRAFT WITH NO MENTION OF "
    "FOSSIL FUELS. REUTERS SAYS SAUDI ARABIA LED THE RESISTANCE. PRESIDENT "
    "MURAT KURUM SAID NO CONSENSUS AND NO NEW TEXT WOULD BE OFFERED."
)

# (kicker, headline, body) - grid stories in priority order.
STORIES = [
    (
        "MIDDLE EAST",
        "HOUTHIS CLAIM STRIKE ON SAUDI OIL REFINERY",
        "YEMEN'S HOUTHIS SAID THEY HIT THE RABIGH REFINERY. DAMAGE "
        "UNCONFIRMED. IRAN SAID TWO MORE TANKERS CAUGHT FIRE NEAR HORMUZ "
        "AFTER HITTING MINES.",
    ),
    (
        "UKRAINE",
        "BOY, 7, PULLED ALIVE FROM KYIV RUBBLE",
        "RESCUERS RACED TO FIND PEOPLE UNDER A FIVE-STOREY BLOCK IN DYMER, "
        "45 KM NORTH OF KYIV. AT LEAST 11 KILLED. A BOY, 7, WAS PULLED "
        "ALIVE. 11 UNACCOUNTED FOR.",
    ),
    (
        "NATO",
        "NATO IN EMERGENCY SESSION OVER POLAND",
        "NATO MEETS IN BRUSSELS TODAY AFTER THREE RUSSIAN OBJECTS ENTERED "
        "POLISH AIRSPACE. POLAND SAID DEBRIS SHOWED ALL THREE WERE KH-101 "
        "CRUISE MISSILES.",
    ),
    (
        "UNITED STATES",
        "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE '92",
        "DEMOCRATS WON A 258TH HOUSE SEAT AS CHUCK HUBBARD BEAT VIRGINIA "
        "FOXX IN NORTH CAROLINA AFTER A RECOUNT - THE LARGEST MAJORITY IN "
        "OVER THREE DECADES.",
    ),
    (
        "MARKETS",
        "STOCKS SLUMP, OIL HOLDS NEAR $92 ON WAR FEARS",
        "OIL AND SHARES FELL AS AN AI SELL-OFF SPREAD. BRENT FELL TO $92.29, "
        "WTI TO $83.26. SOUTH KOREA'S TECH MARKET FELL 4% AFTER THE NASDAQ "
        "PLUNGED 10%.",
    ),
    (
        "PACIFIC",
        "DEEP 6.5 QUAKE STRIKES OFF VANUATU",
        "A MAGNITUDE 6.5 QUAKE STRUCK OFF VANUATU AT 02:40 UTC, 601 KM DEEP. "
        "NO CASUALTIES OR DAMAGE, NO TSUNAMI WARNING, THE USGS SAID.",
    ),
    (
        "HEALTH",
        "AI TO READ BREAST SCANS OF 700,000 WOMEN",
        "THE NHS BEGAN THE WORLD'S LARGEST AI BREAST-SCREENING TRIAL. "
        "NEARLY 700,000 WOMEN AGED 50-71 AT 30 SITES WILL HAVE SCANS READ "
        "BY AI, NOT A SECOND HUMAN.",
    ),
    (
        "SPORT",
        "ALCARAZ DETHRONES ZVEREV FOR ATP FINALS CROWN",
        "ALCARAZ BEAT WORLD NO. 1 ZVEREV 6-2, 7-6 (9-7) TO WIN THE ATP "
        "FINALS, SAVING THREE SET POINTS. LIVERPOOL BEAT TEN-MAN UNITED "
        "4-0.",
    ),
]

SIDEBAR_KICKER = "CULTURE - OKINAWA, JAPAN"
SIDEBAR_HEADLINE = "SHURI CASTLE RISES AGAIN AFTER SEVEN YEARS"
SIDEBAR_BODY = (
    "THE RESTORED MAIN HALL OF SHURI CASTLE IN OKINAWA, DESTROYED BY FIRE "
    "IN 2019, OPENS TODAY AFTER A SEVEN-YEAR REBUILD. A COMPLETION "
    "CEREMONY WAS HELD ON SUNDAY."
)


# ----------------------------------------------------------------- png ----
def png_bytes(canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        off = y * canvas.w * 3
        raw += canvas.px[off:off + canvas.w * 3]

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return bytes(out)


# -------------------------------------------------------------- layout ----
def draw_page():
    cv = Canvas(W, H, PAPER)
    mx = 30                      # side margin
    cw = W - 2 * mx              # content width: 964

    # Masthead.
    cv.draw_text_centred(20, "THE WORLD TODAY", 9, INK)
    cv.hline(mx, 92, cw, INK, 2)
    cv.draw_text_centred(100, "MONDAY, 23 NOVEMBER 2026", 3, INK)
    cv.hline(mx, 128, cw, INK, 5)
    cv.hline(mx, 133, cw, INK, 1)

    # Lead story, full width.
    y = 144
    cv.draw_text(mx, y, LEAD_KICKER, 2, RED)
    y = 164
    for line in LEAD_HEADLINE:
        cv.draw_text(mx, y, line, 4, INK)
        y += 34
    y = 238
    for line in wrap(LEAD_BODY, 80):
        cv.draw_text(mx, y, line, 2, INK)
        y += 16
    cv.hline(mx, 328, cw, INK, 2)

    # Grid: 2 columns x 4 rows.
    col_w = (cw - 24) // 2      # 470
    row_h = 136
    grid_y = 340
    for i, (kicker, headline, body) in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = mx + col * (col_w + 24)
        gy = grid_y + row * row_h
        cv.draw_text(x, gy, kicker, 2, RED)
        hy = gy + 18
        for line in wrap(headline, 26):
            cv.draw_text(x, hy, line, 3, INK)
            hy += 29
        by = gy + 74
        for line in wrap(body, 39):
            cv.draw_text(x, by, line, 2, GREY)
            by += 15
        if col == 0:
            cv.vline(x + col_w + 12, gy, row_h - 8, GREY, 1)
        if row < 3:
            cv.hline(mx, gy + row_h - 2, cw, GREY, 1)

    # Sidebar: Shuri Castle, full width.
    sy = 900
    cv.hline(mx, sy - 6, cw, INK, 2)
    cv.draw_text(mx, sy, SIDEBAR_KICKER, 2, RED)
    cv.draw_text(mx, sy + 20, SIDEBAR_HEADLINE, 3, INK)
    by = sy + 54
    for line in wrap(SIDEBAR_BODY, 80):
        cv.draw_text(mx, by, line, 2, GREY)
        by += 16

    # Footer.
    cv.draw_text_centred(1006, "ALL STORIES REPORTED ON MONDAY 23 NOVEMBER 2026", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
