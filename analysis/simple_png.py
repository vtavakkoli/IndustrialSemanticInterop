from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRID = (220, 224, 230)
BLUE = (76, 120, 168)
ORANGE = (245, 133, 24)
GREEN = (84, 162, 75)
RED = (228, 87, 86)
PURPLE = (177, 122, 161)
TEAL = (114, 183, 178)

PALETTE = [BLUE, ORANGE, GREEN, RED, PURPLE, TEAL]


class Canvas:
    def __init__(self, width: int = 1200, height: int = 700, bg=WHITE):
        self.w = width
        self.h = height
        self.pixels = [[bg for _ in range(width)] for _ in range(height)]

    def _set(self, x: int, y: int, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.pixels[y][x] = color

    def rect(self, x0: int, y0: int, x1: int, y1: int, color, fill=True):
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        xa, xb = max(0, xa), min(self.w - 1, xb)
        ya, yb = max(0, ya), min(self.h - 1, yb)
        if xa > xb or ya > yb:
            return
        if fill:
            for y in range(ya, yb + 1):
                row = self.pixels[y]
                for x in range(xa, xb + 1):
                    row[x] = color
        else:
            for x in range(xa, xb + 1):
                self._set(x, ya, color)
                self._set(x, yb, color)
            for y in range(ya, yb + 1):
                self._set(xa, y, color)
                self._set(xb, y, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color, width: int = 1):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for wx in range(-width // 2, width // 2 + 1):
                for wy in range(-width // 2, width // 2 + 1):
                    self._set(x0 + wx, y0 + wy, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx: int, cy: int, r: int, color, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if (fill and d <= r * r) or (not fill and abs(d - r * r) < r * 1.5):
                    self._set(x, y, color)

    def text(self, x: int, y: int, txt: str, color=BLACK, scale: int = 1):
        for i, ch in enumerate(txt[:120]):
            v = ord(ch)
            for bit in range(7):
                if (v >> bit) & 1:
                    self.rect(x + i * 6 * scale, y + bit * scale, x + i * 6 * scale + scale, y + bit * scale + scale, color)

    def axes(self, margin_left=120, margin_right=60, margin_top=70, margin_bottom=120):
        x0, y0 = margin_left, self.h - margin_bottom
        x1, y1 = self.w - margin_right, margin_top
        self.line(x0, y0, x1, y0, BLACK, 2)
        self.line(x0, y0, x0, y1, BLACK, 2)
        return x0, y0, x1, y1

    def save_png(self, path: str):
        raw = bytearray()
        for row in self.pixels:
            raw.append(0)
            for r, g, b in row:
                raw.extend((r, g, b))

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack('!IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)
        png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(png)


def scale_points(values, min_px, max_px, low=None, high=None):
    if not values:
        return []
    vmin = min(values) if low is None else low
    vmax = max(values) if high is None else high
    if math.isclose(vmin, vmax):
        return [(min_px + max_px) // 2 for _ in values]
    return [int(min_px + (v - vmin) / (vmax - vmin) * (max_px - min_px)) for v in values]
