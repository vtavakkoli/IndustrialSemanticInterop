from pathlib import Path


def write_svg_bar(path, title, labels, values, unit=""):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    max_v = max(values) if values else 1
    width, height = 900, 420
    bar_w = max(20, int((width - 120) / max(len(values), 1)))
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
             f"<text x='20' y='30' font-size='18'>{title}</text>"]
    for i, (l, v) in enumerate(zip(labels, values)):
        h = int((v / max_v) * 280) if max_v else 0
        x = 60 + i * bar_w
        y = 340 - h
        parts.append(f"<rect x='{x}' y='{y}' width='{bar_w-4}' height='{h}' fill='#4C78A8'/>")
        parts.append(f"<text x='{x}' y='360' font-size='10'>{l}</text>")
        parts.append(f"<text x='{x}' y='{y-4}' font-size='10'>{v:.3f}{unit}</text>")
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def write_svg_scatter(path, title, points):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 420
    xs = [p[0] for p in points] or [1]
    ys = [p[1] for p in points] or [1]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    def sx(x): return 60 + int((x - minx) / (maxx - minx + 1e-9) * 780)
    def sy(y): return 340 - int((y - miny) / (maxy - miny + 1e-9) * 260)
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
             f"<text x='20' y='30' font-size='18'>{title}</text>"]
    for x, y, label in points:
        parts.append(f"<circle cx='{sx(x)}' cy='{sy(y)}' r='4' fill='#F58518'/>")
        parts.append(f"<text x='{sx(x)+6}' y='{sy(y)-2}' font-size='9'>{label}</text>")
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")
