from collections import defaultdict

from .simple_png import Canvas, BLUE, GRID, PALETTE


def plot_experiment_matrix(rows, out='results/figures/figure_01_experiment_matrix.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 01: Experiment Matrix Coverage')
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    security = ['none', 'auth', 'encryption', 'full']
    reps = defaultdict(set)
    for r in rows:
        reps[(r['method'], r['scale'], r['security'])].add(r['run_index'])

    x0, y0 = 220, 110
    cw, ch = 70, 50
    for mi, m in enumerate(methods):
        c.text(30, y0 + mi * (len(scales) * ch + 30), m)
        for si, s in enumerate(scales):
            y = y0 + mi * (len(scales) * ch + 30) + si * ch
            c.text(150, y + 15, s)
            for qi, sec in enumerate(security):
                x = x0 + qi * cw
                key = (m, s, sec)
                rep_n = len(reps.get(key, []))
                shade = min(220, 60 + rep_n * 25)
                color = (40, 80, 160) if rep_n else GRID
                color = (max(0, color[0] - shade // 5), max(0, color[1] - shade // 8), min(255, color[2] + shade // 3)) if rep_n else GRID
                c.rect(x, y, x + cw - 4, y + ch - 6, color)
                c.rect(x, y, x + cw - 4, y + ch - 6, (255, 255, 255), fill=False)
                c.text(x + 8, y + 18, str(rep_n))
                if mi == 0 and si == 0:
                    c.text(x + 3, y - 20, sec[:8])
    c.text(40, 660, 'Cell value = repetitions completed for each method/scale/security combination')
    c.save_png(out)
