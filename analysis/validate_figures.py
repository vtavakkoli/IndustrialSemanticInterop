from __future__ import annotations

import json
from pathlib import Path


def validate_readable_text(fig_path: str = 'results/figures/figure_02_latency_distribution.png', out_json: str = 'results/figures/font_validation.json') -> dict:
    try:
        from .mpl_config import setup_matplotlib
        setup_matplotlib()
        from matplotlib import font_manager, rcParams, ft2font
    except Exception:
        result = {
            'status': 'skipped',
            'reason': 'matplotlib not available in current environment',
            'figure_checked': fig_path,
        }
        Path(out_json).write_text(json.dumps(result, indent=2), encoding='utf-8')
        return result

    family = rcParams.get('font.sans-serif', ['DejaVu Sans'])[0]
    font_path = font_manager.findfont(font_manager.FontProperties(family=family), fallback_to_default=True)
    ft = ft2font.FT2Font(font_path)

    check_text = 'Latency μs -1'
    missing = []
    for ch in check_text:
        if ch == ' ':
            continue
        if ft.get_char_index(ord(ch)) == 0:
            missing.append(ch)

    p = Path(fig_path)
    exists = p.exists()
    size_ok = p.stat().st_size > 10_000 if exists else False

    result = {
        'figure_checked': fig_path,
        'figure_exists': exists,
        'figure_size_bytes': p.stat().st_size if exists else 0,
        'font_family_requested': family,
        'font_file_resolved': font_path,
        'missing_glyphs_in_test_string': missing,
        'unicode_minus_enabled': bool(rcParams.get('axes.unicode_minus', False)),
        'status': 'pass' if exists and size_ok and not missing else 'fail',
    }

    out = Path(out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    if result['status'] != 'pass':
        raise RuntimeError(f"Figure text validation failed: {result}")
    return result
