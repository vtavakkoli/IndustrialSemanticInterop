from __future__ import annotations

import os
from pathlib import Path


def setup_matplotlib() -> None:
    import matplotlib

    os.environ.setdefault("MPLBACKEND", "Agg")
    matplotlib.use("Agg", force=True)

    from matplotlib import rcParams, font_manager

    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = [
        "DejaVu Sans",
        "Liberation Sans",
        "Noto Sans",
        "Arial",
        "sans-serif",
    ]
    rcParams["axes.unicode_minus"] = True
    rcParams["figure.dpi"] = 140
    rcParams["savefig.dpi"] = 160
    rcParams["savefig.bbox"] = "tight"
    rcParams["text.usetex"] = False

    cache_dir = Path(matplotlib.get_cachedir())
    for stale in cache_dir.glob("fontlist-v*.json"):
        try:
            stale.unlink()
        except OSError:
            pass
    try:
        font_manager._load_fontmanager(try_read_cache=False)
    except Exception:
        pass
