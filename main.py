#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026, in one image.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the
world news of Saturday 21 November 2026: masthead and date, lead story,
two sub-leads, a dotted world map with numbered flashpoints, a grid of
short stories, and an IN BRIEF strip.

Standard library only. No network, no files read, no timestamps, no
randomness: every run writes byte-identical output.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   ->  out/entry.png
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (176, 32, 32)
GREY = (107, 101, 88)
LIGHT = (214, 207, 190)
FAINT = (150, 143, 126)

# ---------------------------------------------------------------- font ----
# Hand-built 5x7 bitmap glyphs. Each glyph is seven rows of five cells;
# '#' is ink, '.' is blank. Only the characters used by the page are here.
# All page text is set in capitals, so only capitals are defined.

GLYPHS = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
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
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

BLANK = (".....",) * 7


def glyph(ch):
    return GLYPHS.get(ch, BLANK)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_words(text, max_chars):
    """Greedy word wrap to lines of at most max_chars characters."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Page:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                xa = max(x, 0)
                xb = min(x + w, self.w)
                if xb > xa:
                    i = (yy * self.w + xa) * 3
                    self.px[i:i + (xb - xa) * 3] = bytes(color) * (xb - xa)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - 1) ** 2 <= d <= r * r:
                    self.set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            rows = glyph(ch)
            for ry in range(7):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s.upper(), scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)

    def text_right(self, x1, y, s, scale, color):
        self.text(x1 - text_width(s.upper(), scale), y, s, scale, color)

    def block(self, x, y, lines, scale, color, leading=None):
        if leading is None:
            leading = 7 * scale + 2
        for line in lines:
            self.text(x, y, line, scale, color)
            y += leading
        return y


# ----------------------------------------------------------- world map ----
# Land as ellipses in (longitude, latitude) space. Each tuple is
# (centre lon, centre lat, lon radius, lat radius). Rough on purpose:
# a dotted newspaper map, not a survey chart.
LAND_BLOBS = [
    (-100, 52, 30, 16), (-95, 34, 24, 11), (-88, 19, 9, 7),
    (-122, 44, 11, 9), (-62, 58, 14, 9), (-42, 74, 9, 5),
    (-58, -6, 12, 11), (-64, -20, 10, 13), (-70, -34, 6, 9),
    (10, 52, 17, 7), (19, 62, 11, 5), (26, 44, 8, 5),
    (-2, 54, 3, 3), (138, 37, 4, 6), (172, -41, 3, 4),
    (16, 12, 17, 13), (20, -10, 14, 13), (33, -24, 8, 8),
    (46, 6, 8, 6), (47, -19, 3, 5),
    (58, 56, 28, 11), (88, 52, 24, 11), (78, 22, 12, 10),
    (101, 16, 10, 8), (114, 36, 14, 9), (135, 36, 8, 8),
    (140, 60, 14, 7), (168, 65, 10, 6), (45, 25, 11, 8),
    (104, -4, 8, 6), (135, -25, 14, 8),
]

MAP_X0, MAP_X1 = 24, 1000
MAP_Y0, MAP_Y1 = 478, 612
MAP_LAT_TOP, MAP_LAT_BOT = 78.0, -58.0


def map_xy(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) \
        * (MAP_Y1 - MAP_Y0)
    return int(x), int(y)


def on_land(lon, lat):
    for cx, cy, rx, ry in LAND_BLOBS:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1.0:
            return True
    return False


# Numbered flashpoints on the map: (number, lon, lat).
MARKERS = [
    (1, 30.5, 50.5),    # Kyiv
    (2, 16.0, 54.0),    # Poland
    (3, 46.7, 24.6),    # Riyadh
    (4, 34.5, 31.5),    # Gaza
    (5, 30.5, 37.5),    # Antalya (nudged NW so its disc clears Gaza's)
    (6, 4.4, 50.9),     # Brussels
    (7, -77.0, -12.0),  # Lima
    (8, 106.9, 47.9),   # Ulaanbaatar
    (9, 127.0, 37.5),   # Seoul
    (10, 15.3, -4.3),   # Kinshasa
    (11, -77.0, 38.9),  # Washington
    (12, 139.7, 35.7),  # Tokyo
]


def draw_map(page):
    lon = -180.0
    while lon <= 180.0:
        lat = MAP_LAT_TOP
        while lat >= MAP_LAT_BOT:
            if on_land(lon, lat):
                x, y = map_xy(lon, lat)
                page.rect(x, y, 3, 3, INK)
            lat -= 5.0
        lon += 3.0
    # Ocean labels.
    page.text(*map_xy(-152, -2), "PACIFIC", 1, FAINT)
    page.text(*map_xy(-38, 6), "ATLANTIC", 1, FAINT)
    page.text(*map_xy(72, -28), "INDIAN", 1, FAINT)
    # Numbered markers.
    for num, m_lon, m_lat in MARKERS:
        x, y = map_xy(m_lon, m_lat)
        page.disc(x, y, 6, RED)
        page.ring(x, y, 6, INK)
        label = str(num)
        page.text(x - text_width(label, 1) // 2, y - 3, label, 1, PAPER)


# -------------------------------------------------------------- stories ----
LEAD_KICKER = "LEAD - UKRAINE"
LEAD_HEAD = ["RUSSIA'S BIGGEST BARRAGE", "HITS KYIV'S BRIDGES"]
LEAD_DECK = [
    "MORE THAN 400 DRONES AND 110 MISSILES HIT UKRAINE OVERNIGHT, KILLING",
    "AT LEAST EIGHT AND WOUNDING DOZENS. THREE BRIDGES ACROSS THE DNIPRO",
    "IN KYIV WERE DAMAGED AND POWER WAS CUT. A DOUBLE-TAP STRIKE ON",
    "KRYVYI RIH KILLED A BOY OF SEVEN AND A PARAMEDIC AGED 20.",
]

SUB_LEADS = [
    ("POLAND", "MISSILES LAND IN POLAND",
     ["TWO MISSILES AND A SUSPECTED DRONE",
      "CAME DOWN IN EASTERN POLAND.",
      "PM TUSK: DELIBERATE PROVOCATION.",
      "NATO: GRAVE VIOLATION."]),
    ("CLIMATE - ANTALYA", "COP31 IN OVERTIME: NO DEAL",
     ["DRAFT DEAL DROPS ALL MENTION OF",
      "FOSSIL FUELS AFTER SAUDI OBJECTIONS.",
      "THIRD TEXT DUE SATURDAY; FIRST TO",
      "ADMIT 1.5C OVERSHOOT LIKELY."]),
]

# (kicker, headline line 1, headline line 2)
GRID = [
    ("3 - RIYADH", "THREE HOUTHI MISSILES", "FIRED AT RIYADH DOWNED"),
    ("4 - GAZA", "ISRAELI STRIKES KILL SIX", "IN GAZA DESPITE CEASEFIRE"),
    ("MARKETS", "S&P 500 AND DOW SLIDE", "INTO CORRECTION"),
    ("ANTHROPIC", "RECORD $81BN IPO OPENS", "HIGH, THEN FADES FAST"),
    ("6 - UK AND EU", "UK AND EU SIGN BIGGEST", "POST-BREXIT RESET"),
    ("GEN Z", "GEN Z PROTESTS SWEEP 25", "EUROPEAN COUNTRIES"),
    ("7 - PERU", "MAG 6.9 QUAKE SHAKES", "PERU'S ANDES, FELT IN LIMA"),
    ("THE HAGUE", "WORLD COURT: MYANMAR", "GUILTY OF GENOCIDE"),
    ("11 - FBI", "FBI PROBES SUSPECTED HACK", "OF ITS CRIME DATABASE"),
    ("HEALTH", "PANCREATIC CANCER PILL:", "TUMOURS GONE IN 1 IN 12"),
    ("8 - MONGOLIA", "MONGOLIA'S PRESIDENT OUT;", "EARLY VOTE IN MONTHS"),
    ("ESTONIA", "ESTONIA TO SHUT FIVE", "RUSSIA BORDER CROSSINGS"),
    ("SPAIN", "SPAIN HEADS TO 29 NOV", "VOTE AS RIGHT GAINS"),
    ("10 - EBOLA", "EBOLA CHILD DEATHS SOAR", "IN CONGO, WHO WARNS"),
    ("9 - KOREA", "SOUTH KOREA'S FIRST HOME", "CHOLERA CASE IN 10 YEARS"),
    ("12 - JAPAN", "JAPAN CORE INFLATION AT", "YEAR HIGH; NIKKEI DOWN 5%"),
    ("11 - USA", "US LOSES MEASLES", "ELIMINATION STATUS"),
    ("GULF", "IEA: IRAN WAR IS BIGGEST", "OIL SHOCK ON RECORD"),
    ("UKRAINE AID", "KYIV NEEDS $115BN IN 2027,", "ZELENSKYY SAYS"),
    ("SHENZHEN", "AFTER XI-PUTIN-TRUMP", "SUMMIT, NO BREAKTHROUGH"),
    ("TURKEY", "COURT BARS JAILED ISTANBUL", "MAYOR FROM 2028 RACE"),
]

BRIEF = [
    "BUKELE SEEKS THIRD TERM",
    "LUFTHANSA TO CUT 1,000 JOBS",
    "EMBASSIES DAMAGED IN KYIV",
    "PAKISTAN: 22 MILITANTS KILLED",
    "KOREA: RETRIAL FOR EX-PM HAN",
    "FRANCOPHONIE DELAYS VOTE",
    "NEPAL PM TO VISIT INDIA",
    "SAUDI-JAPAN OIL DEAL AGREED",
]


# -------------------------------------------------------------- drawing ----
def draw(page):
    page.rect(0, 0, W, H, PAPER)

    # ---- masthead ----
    page.text_center(10, "THE WORLD TODAY", 6, INK)
    page.hline(24, 60, W - 48, INK, 3)
    page.text_center(68, "SATURDAY 21 NOVEMBER 2026", 3, RED)
    page.text_center(96, "THE WORLD IN ONE PAGE - EVERY STORY THAT MATTERED TODAY",
                     2, GREY)
    page.hline(24, 116, W - 48, INK, 1)

    # ---- lead story ----
    y = 126
    page.text(24, y, LEAD_KICKER, 2, RED)
    page.text_right(W - 24, y, "KYIV - 21 NOV", 2, GREY)
    y += 22
    for line in LEAD_HEAD:
        page.text(24, y, line, 4, INK)
        y += 34
    y += 4
    for line in LEAD_DECK:
        page.text(24, y, line, 2, INK)
        y += 17
    page.hline(24, y + 4, W - 48, INK, 1)

    # ---- sub-leads: two columns ----
    col_w = (W - 48 - 24) // 2
    sub_y = y + 16
    for i, (kicker, head, body) in enumerate(SUB_LEADS):
        x = 24 + i * (col_w + 24)
        page.text(x, sub_y, kicker, 2, RED)
        hy = sub_y + 20
        for line in wrap_words(head, 26):
            page.text(x, hy, line, 3, INK)
            hy += 25
        by = hy + 2
        for line in body:
            page.text(x, by, line, 2, INK)
            by += 16
        if i == 0:
            page.vline(x + col_w + 12, sub_y, by - sub_y, LIGHT, 1)
    map_label_y = sub_y + 148

    # ---- map ----
    page.text(24, map_label_y, "THE WORLD AT A GLANCE - 21 NOVEMBER 2026",
              2, INK)
    page.text_right(W - 24, map_label_y, "NUMBERED: THE DAY'S FLASHPOINTS",
                    2, GREY)
    draw_map(page)
    legend_y = MAP_Y1 + 8
    page.text(24, legend_y,
              "1 KYIV   2 POLAND   3 RIYADH   4 GAZA   5 ANTALYA   6 BRUSSELS",
              1, GREY)
    page.text(24, legend_y + 10,
              "7 LIMA   8 ULAANBAATAR   9 SEOUL   10 KINSHASA   11 WASHINGTON   12 TOKYO",
              1, GREY)
    page.hline(24, legend_y + 24, W - 48, INK, 1)

    # ---- story grid: 3 columns x 7 rows ----
    grid_y = legend_y + 36
    row_h = 43
    col_xs = [24, 352, 680]
    col_w = 320
    for idx, (kicker, h1, h2) in enumerate(GRID):
        row, col = divmod(idx, 3)
        x = col_xs[col]
        gy = grid_y + row * row_h
        page.text(x, gy, kicker, 1, RED)
        page.text(x, gy + 9, h1, 2, INK)
        page.text(x, gy + 24, h2, 2, INK)
        if col < 2:
            page.vline(x + col_w + 8, gy + 2, row_h - 10, LIGHT, 1)
    brief_y = grid_y + 7 * row_h + 4
    page.hline(24, brief_y, W - 48, INK, 3)

    # ---- IN BRIEF strip ----
    brief_y += 10
    page.text(24, brief_y, "IN BRIEF", 2, RED)
    page.text_right(W - 24, brief_y, "SATURDAY 21 NOVEMBER 2026", 2, GREY)
    brief_y += 22
    per_line = 4
    for start in range(0, len(BRIEF), per_line):
        chunk = BRIEF[start:start + per_line]
        line = "  \u2022  ".join(chunk)
        page.text(24, brief_y, line, 1, INK)
        brief_y += 12
    page.hline(24, brief_y + 2, W - 48, INK, 1)


# ------------------------------------------------------------ png out -----
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(page, path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += page.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = Page(W, H, PAPER)
    draw(page)
    write_png(page, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
