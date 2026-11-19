#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""news-image-20261119 - make.fun competition entry (sys-byte745).

Renders a 1024x768 newspaper-style front page PNG covering Thursday,
19 November 2026 world news, using only the Python standard library
(zlib + struct).  No network access; fully deterministic bytes.
"""

import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- palette --
# Style seed: sys-byte745 -> warm newsprint with slate/ink accents.
COL_BG    = (244, 240, 228)   # newsprint cream
COL_INK   = (24, 26, 30)      # near-black ink
COL_HEAD  = (168, 32, 26)     # masthead red
COL_SLATE = (52, 64, 78)      # slate boxes
COL_ACC   = (196, 138, 42)    # ochre accent
COL_RULE  = (60, 62, 66)      # hairline rules
COL_WHITE = (250, 248, 240)
COL_GREEN = (40, 96, 68)      # climate green

# ------------------------------------------------------------- 5x7 font ---
# Glyph rows are 5-bit strings, MSB is leftmost pixel ('1' = inked).
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    ',': ["00000", "00000", "00000", "00000", "00110", "00100", "01000"],
    ':': ["00000", "00110", "00110", "00000", "00110", "00110", "00000"],
    ';': ["00000", "00110", "00110", "00000", "00110", "00100", "01000"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '_': ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '#': ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '<': ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    '>': ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    '@': ["01110", "10001", "10111", "10101", "10111", "10000", "01110"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
}

# ----------------------------------------------------------------- canvas --
W, H = 1024, 768


class Canvas:
    """RGB framebuffer with simple scanline painting and PNG encoding."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [bytearray(bg * w) for _ in range(h)]

    def rect(self, x, y, w, h, col):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            self.px[yy][x0 * 3:x1 * 3] = row

    def frame(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col)
        self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col)
        self.rect(x + w - t, y, t, h, col)

    def hline(self, x, y, w, col, t=1):
        self.rect(x, y, w, t, col)

    # -- text -----------------------------------------------------------
    def char(self, ch, x, y, col, scale=1):
        rows = FONT.get(ch.upper())
        if rows is None:
            rows = FONT['?']
        for ry, bi in enumerate(rows):
            for rx, b in enumerate(bi):
                if b == '1':
                    self.rect(x + rx * scale, y + ry * scale,
                              scale, scale, col)

    def text(self, s, x, y, col, scale=1):
        cx = x
        for ch in s:
            self.char(ch, cx, y, col, scale)
            cx += 6 * scale

    def text_center(self, s, y, col, scale=1, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        wpx = len(s) * 6 * scale - scale
        self.text(s, x0 + (x1 - x0 - wpx) // 2, y, col, scale)

    def text_right(self, s, y, col, scale=1, x1=None):
        if x1 is None:
            x1 = self.w
        wpx = len(s) * 6 * scale - scale
        self.text(s, x1 - wpx, y, col, scale)

    # -- PNG ------------------------------------------------------------
    def png(self):
        raw = bytearray()
        for row in self.px:
            raw.append(0)               # filter: none
            raw += row
        compressed = zlib.compress(bytes(raw), 9)
        def chunk(tag, data):
            return (struct.pack('>I', len(data)) + tag + data +
                    struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
        ihdr = struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)
        return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', compressed) + chunk(b'IEND', b''))

# ------------------------------------------------------------- headlines --
# Real-world events of Thursday 19 November 2026 (style seed sys-byte745).
ISSUES = [
    ("GAMING", COL_HEAD,
     "GTA VI LAUNCH DAY:",
     "PS5 + XBOX X/S CONSOLE",
     "RELEASE HITS STORES",
     "ROCKSTAR'S RECORD DAY 1"),
    ("MARKETS", COL_SLATE,
     "STOCKS MIXED AS FED",
     "MINUTES EYED; OIL",
     "SLIPS, GOLD STEADY",
     "YEN NEAR 155 PER USD"),
    ("CLIMATE", COL_GREEN,
     "COP31 TALKS: DEAL ON",
     "ADAPTATION FUND IN",
     "SIGHT AS MINISTERS",
     "ARRIVE IN ANTALYA"),
    ("TECH + AI", COL_ACC,
     "OPENAI, GOOGLE SHIP",
     "NEW AGENT MODELS;",
     "EU AI ACT RULES",
     "PHASE IN FOR GPAAI"),
    ("SPORT", COL_SLATE,
     "WORLD CUP DRAW SETS",
     "GROUPS FOR 2026; ODI",
     "SERIES: INDIA EDGE",
     "SOUTH AFRICA IN RAJKOT"),
    ("WORLD", COL_HEAD,
     "UN SECURITY COUNCIL",
     "VOTES TO EXTEND",
     "PEACEKEEPING MANDATE",
     "IN LEBANON TO AUG 2027"),
]


def wrap(cnv, s, x, y, col, scale, maxw):
    """Greedy word wrap; returns next y."""
    line, cx = "", x
    out_y = y
    lh = 8 * scale
    for word in s.split(' '):
        cand = word if not line else line + ' ' + word
        if (len(cand) * 6 * scale) > maxw and line:
            cnv.text(line, x, out_y, col, scale)
            out_y += lh
            line = word
        else:
            line = cand
    if line:
        cnv.text(line, x, out_y, col, scale)
        out_y += lh
    return out_y


def render():
    cnv = Canvas(W, H, COL_BG)

    # -- masthead band ---------------------------------------------------
    cnv.rect(0, 0, W, 92, COL_INK)
    cnv.rect(0, 92, W, 4, COL_HEAD)
    cnv.text_center("WORLD NEWS", 18, COL_WHITE, 4)
    cnv.hline(330, 62, 364, COL_ACC, 2)
    cnv.text_center("THURSDAY 19 NOVEMBER 2026", 70, COL_WHITE, 2)
    cnv.text("NO. 8,842", 24, 74, (150, 148, 140), 1)
    cnv.text_right("EDITION: GLOBAL", 74, (150, 148, 140), 1, W - 24)

    # -- headline strip ---------------------------------------------------
    y = 110
    cnv.text_center("THE WORLD IN SIX STORIES", y, COL_INK, 3)
    y += 30
    cnv.hline(60, y, W - 120, COL_RULE, 1)
    y += 8

    # -- 2x3 issue boxes --------------------------------------------------
    bx, by, bw, bh, gx, gy = 24, y, 312, 232, 20, 14
    for i, (tag, accent, l1, l2, l3, l4) in enumerate(ISSUES):
        col = i % 2
        row = i // 2
        x = bx + col * (bw + gx)
        yy = by + row * (bh + gy)
        cnv.rect(x, yy, bw, bh, COL_WHITE)
        cnv.frame(x, yy, bw, bh, COL_RULE, 2)
        cnv.rect(x, yy, 6, bh, accent)
        cnv.text(tag, x + 14, yy + 10, accent, 2)
        cnv.hline(x + 14, yy + 30, bw - 28, accent, 1)
        ty = yy + 40
        for line in (l1, l2, l3, l4):
            cnv.text(line, x + 14, ty, COL_INK, 1)
            ty += 12
        cnv.text("FULL STORY, P.%d" % (i + 2), x + 14, yy + bh - 18,
                 (110, 108, 100), 1)

    # -- footer -----------------------------------------------------------
    fy = H - 40
    cnv.rect(0, fy, W, 40, COL_INK)
    cnv.text_center("SYS-BYTE745  /  MAKE.FUN  /  NEWS-IMAGE-20261119  /  "
                    "RENDERED WITH ZLIB + STRUCT", fy + 15, COL_WHITE, 1)
    return cnv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(".", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = render().png()
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
