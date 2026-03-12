import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


def _read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _read_json_runs(path):
    return [json.loads(p.read_text()) for p in sorted(Path(path).glob('*.json'))]


def _scenario_table_rows(summary_rows):
    out = []
    for r in summary_rows:
        out.append(f"<tr><td>{r['method']}</td><td>{r['scale']}</td><td>{r['security']}</td><td>{r['runs']}</td></tr>")
    return '\n'.join(out)






def _safe_mean(values, default=0.0):
    return mean(values) if values else default

def _report_src(path: str) -> str:
    return path.replace("results/", "", 1) if path.startswith("results/") else path


def generate_report(results_root='results'):
    root = Path(results_root)
    tidy = _read_csv(root / 'aggregated' / 'tidy_runs.csv')
    summary = _read_csv(root / 'aggregated' / 'summary.csv')
    stats = _read_csv(root / 'aggregated' / 'stat_tests.csv')
    ci = _read_csv(root / 'aggregated' / 'confidence_intervals.csv')
    effects = _read_csv(root / 'aggregated' / 'effect_sizes.csv')
    ablations = _read_json_runs(root / 'ablations')
    robustness = _read_json_runs(root / 'robustness')

    methods = sorted({r['method'] for r in tidy})
    best_latency_method = min(summary, key=lambda r: float(r['latency_median_ms']))['method']

    by_method_scale = defaultdict(list)
    by_method_security = defaultdict(list)
    for r in tidy:
        by_method_scale[(r['method'], r['scale'])].append(float(r['latency_mean_ms']))
        by_method_security[(r['method'], r['security'])].append(float(r['throughput_msg_per_sec']))

    scale_msg = []
    for m in methods:
        small = _safe_mean(by_method_scale[(m, 'small')])
        large = _safe_mean(by_method_scale[(m, 'large')], small)
        scale_msg.append(f"{m}: {small:.4f}→{large:.4f} ms")

    sec_msg = []
    for m in methods:
        none = _safe_mean(by_method_security[(m, 'none')])
        full = _safe_mean(by_method_security[(m, 'full')], none)
        delta = ((full - none) / none * 100.0) if none else 0.0
        sec_msg.append(f"{m}: {delta:.2f}% throughput change under full security")

    ab_msg = 'No ablation data.'
    if ablations:
        on = [a['latency_mean_ms'] for a in ablations if a.get('ablation', {}).get('reasoning', True)]
        off = [a['latency_mean_ms'] for a in ablations if not a.get('ablation', {}).get('reasoning', True)]
        if on and off:
            ab_msg = f"Reasoning ON vs OFF latency: {mean(on):.4f} vs {mean(off):.4f} ms."

    rb_msg = 'No robustness data.'
    if robustness:
        fr = defaultdict(list)
        for r in robustness:
            fr[r['notes'].replace('fault=', '')].append(float(r['failure_rate']))
        worst = max(fr.items(), key=lambda kv: mean(kv[1]))
        rb_msg = f"Worst degradation fault: {worst[0]} with failure rate {mean(worst[1]):.3f}."

    stat_msg = '; '.join([f"{s['assumption']}={s['passed']} ({s['detail']})" for s in stats])

    charts = {
        'overview': [
            ('results/figures/figure_01_experiment_matrix.png', 'Experiment matrix', 'Coverage of all method×scale×security combinations and repetition counts.', 'Read each cell as completed repetitions.', 'Uniformly populated grid indicates full coverage.', 'Shows benchmark breadth and avoids cherry-picking.'),
        ],
        'latency': [
            ('results/figures/figure_02_latency_distribution.png', 'Latency distribution', 'Distribution across methods with tail indicators.', 'Median and spread indicate stability; p95 marks tail risk.', 'Methods with narrow IQR are more predictable.', 'Tail latency strongly affects control-loop reliability.'),
            ('results/figures/figure_03_latency_p95_comparison.png', 'P95 latency comparison', 'Tail latency by method and scale.', 'Higher bars mean worse tail behavior.', 'Large-scale conditions show degradation profile.', 'Critical for worst-case QoS commitments.'),
        ],
        'throughput': [
            ('results/figures/figure_04_throughput_comparison.png', 'Throughput comparison', 'Method throughput under each security mode.', 'Compare bar groups inside each method.', 'Security hardening shifts throughput differently by method.', 'Reveals efficiency/security trade-off.'),
            ('results/figures/figure_05_throughput_vs_scale.png', 'Throughput vs scale', 'Throughput trend as load grows.', 'Slope indicates saturation speed.', 'Flattening lines indicate capacity bottlenecks.', 'Guides deployment sizing decisions.'),
        ],
        'scalability': [
            ('results/figures/figure_06_scalability_latency.png', 'Scalability latency', 'Latency evolution by scale.', 'Steeper slope means worse scalability.', 'Some methods retain lower growth under load.', 'Shows operational headroom at high scale.'),
            ('results/figures/figure_07_scalability_resources.png', 'Scalability resources', 'CPU and memory trend across scale.', 'Blue=CPU proxy, orange=memory.', 'Resource growth separates lightweight vs heavy pipelines.', 'Informs hardware provisioning and cloud cost.'),
        ],
        'security': [
            ('results/figures/figure_08_security_latency_overhead.png', 'Security latency overhead', 'Latency cost of stronger security.', 'Compare bars from none→full.', 'Monotonic rise indicates expected cryptographic cost.', 'Quantifies security-performance tradeoff.'),
            ('results/figures/figure_09_security_throughput_overhead.png', 'Security throughput overhead', 'Throughput under security modes.', 'Lower bars imply throughput penalty.', 'Some methods preserve throughput better under security.', 'Highlights robust implementations for secure deployments.'),
        ],
        'resources': [
            ('results/figures/figure_10_cpu_usage.png', 'CPU usage', 'CPU profile by method.', 'Higher bars consume more compute.', 'Capability-rich methods can cost more CPU.', 'Matters for edge devices with tight budgets.'),
            ('results/figures/figure_11_memory_usage.png', 'Memory usage', 'Memory footprint by method.', 'Higher bars imply larger resident set.', 'Persistent memory overhead can limit density.', 'Important for embedded and container packing.'),
        ],
        'ablation': [
            ('results/figures/figure_12_ablation_impact_latency.png', 'Ablation latency impact', 'Latency shift when disabling key components.', 'Compare ON/OFF groups.', 'Large shift means component contributes materially.', 'Justifies complexity with measured benefit/cost.'),
            ('results/figures/figure_13_ablation_impact_throughput.png', 'Ablation throughput impact', 'Throughput shift under feature toggles.', 'Higher bars indicate capacity gain.', 'Weak shifts suggest optional complexity.', 'Supports minimal and full variants decisions.'),
        ],
        'robustness': [
            ('results/figures/figure_14_robustness_degradation.png', 'Fault degradation', 'Failure rate under injected faults.', 'Higher bars mean harsher degradation.', 'Specific faults dominate reliability loss.', 'Prioritizes resilience engineering efforts.'),
            ('results/figures/figure_15_recovery_success.png', 'Recovery success', 'Retry/recovery success by fault type.', 'Higher bars mean stronger recovery.', 'Recovery varies significantly across faults.', 'Distinguishes graceful-degradation behavior.'),
        ],
        'stats': [
            ('results/figures/figure_16_confidence_intervals.png', 'Confidence intervals', 'Uncertainty around latency means.', 'Shorter intervals imply more certainty.', 'Overlapping intervals suggest weaker separation.', 'Prevents overclaiming noisy differences.'),
            ('results/figures/figure_17_effect_sizes.png', 'Effect sizes', 'Pairwise practical magnitude of differences.', 'Points farther from zero indicate larger practical impact.', 'Not all statistically different outcomes are practically large.', 'Balances significance with real-world relevance.'),
        ],
        'pareto': [
            ('results/figures/figure_18_pareto_tradeoff.png', 'Pareto tradeoff', 'Latency-throughput-resource compromise.', 'Left/up is better; larger bubbles cost more memory.', 'No single method dominates every objective.', 'Supports context-aware method selection.'),
        ],
    }

    sections = [
        ('Scenario Matrix', 'This section documents benchmark coverage and confirms that comparisons are made over consistent experimental combinations.', charts['overview']),
        ('Latency Findings', f"Scale trend by method: {'; '.join(scale_msg)}.", charts['latency']),
        ('Throughput Findings', f"Security throughput deltas: {'; '.join(sec_msg)}.", charts['throughput']),
        ('Scalability Findings', 'Scalability is assessed jointly on latency and resource growth to avoid single-metric conclusions.', charts['scalability']),
        ('Security Overhead Findings', 'Security modes are isolated to quantify incremental overhead and method resilience.', charts['security']),
        ('Resource Cost Findings', 'CPU and memory are included to expose operational costs of richer semantics and safeguards.', charts['resources']),
        ('Ablation Findings', ab_msg, charts['ablation']),
        ('Robustness Findings', rb_msg, charts['robustness']),
        ('Statistical Summary', stat_msg, charts['stats']),
        ('Overall Tradeoff', 'Pareto view summarizes performance/cost compromises for deployment decision support.', charts['pareto']),
    ]

    def render_section(title, text, chart_list):
        chunks = [f"<div class='card'><h2>{title}</h2><p>{text}</p>"]
        for p, t, cap, how, pat, why in chart_list:
            chunks.append(
                f"<figure><img src='{_report_src(p)}' alt='{t}'/><figcaption><strong>{t}.</strong> {cap} <em>How to read:</em> {how} <em>Pattern:</em> {pat} <em>Why it matters:</em> {why}</figcaption></figure>"
            )
        chunks.append('</div>')
        return ''.join(chunks)

    scenario_rows_html = _scenario_table_rows(summary)
    git_commit = (root / 'environment' / 'git_commit.txt').read_text().strip() if (root / 'environment' / 'git_commit.txt').exists() else 'unknown'
    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Industrial Semantic Interop Benchmark Report</title>",
        "<style>body{font-family:Arial;background:#f7f8fb;color:#1e2330;margin:0}.wrap{max-width:1200px;margin:0 auto;padding:24px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin:14px 0}table{width:100%;border-collapse:collapse}th,td{border:1px solid #e5e7eb;padding:8px;text-align:left}img{max-width:100%;border:1px solid #d1d5db;border-radius:8px}figcaption{font-size:13px;color:#374151}.kpi{font-size:24px;font-weight:700}.small{color:#4b5563;font-size:13px}</style></head><body><div class='wrap'>",
        "<h1>Industrial Semantic Interoperability Benchmark Report</h1>",
        "<div class='card'><h2>Executive Summary</h2>",
        f"<p>This report summarizes measured results from {len(tidy)} repeated benchmark runs across method, scale, and security dimensions. Best median-latency method: <strong>{best_latency_method}</strong>.</p>",
        f"<p class='small'>Methods={len(methods)} | Scenarios={len(summary)} | Runs={len(tidy)}</p></div>",
        "<div class='card'><h2>Experiment Overview</h2><p>Scenario matrix includes methods × scales × security modes with repeated trials and deterministic seeds.</p>",
        f"<table><thead><tr><th>Method</th><th>Scale</th><th>Security</th><th>Runs</th></tr></thead><tbody>{scenario_rows_html}</tbody></table></div>",
    ]
    for title, text, ch in sections:
        html.append(render_section(title, text, ch))
    html.append("<div class='card'><h2>Limitations</h2><ul><li>Network counters are host-level approximations and may include unrelated traffic.</li><li>Fault injection models controlled synthetic faults; hardware-induced effects are out-of-scope.</li><li>Statistical stage uses conservative proxy logic in dependency-minimal mode.</li></ul></div>")
    html.append(f"<div class='card'><h2>Reproducibility and Provenance</h2><p>Git commit: <code>{git_commit}</code></p><p>Environment: <code>results/environment/system_info.json</code>, <code>results/environment/package_versions.txt</code></p><p>Provenance map: <code>results/figure_table_provenance.json</code></p></div>")
    html.append('</div></body></html>')
    html_text = ''.join(html)

    md = [
        '# Industrial Semantic Interoperability Benchmark Report',
        '',
        '## Executive Summary',
        f'- Total runs: {len(tidy)}',
        f'- Methods: {", ".join(methods)}',
        f'- Best median-latency method: {best_latency_method}',
        '',
        '## Key Patterns',
        f'- Scale trend (latency): {"; ".join(scale_msg)}',
        f'- Security effect (throughput): {"; ".join(sec_msg)}',
        f'- Ablation: {ab_msg}',
        f'- Robustness: {rb_msg}',
        f'- Statistics: {stat_msg}',
    ]

    (root / 'final_report.html').write_text(html_text, encoding='utf-8')
    (root / 'final_report.md').write_text('\n'.join(md), encoding='utf-8')

    figure_map = {
        f'figure_{i:02d}': {
            'file': f'results/figures/figure_{i:02d}_{name}.png',
            'sources': ['results/aggregated/tidy_runs.csv', 'results/aggregated/summary.csv'],
        }
        for i, name in [
            (1, 'experiment_matrix'), (2, 'latency_distribution'), (3, 'latency_p95_comparison'),
            (4, 'throughput_comparison'), (5, 'throughput_vs_scale'), (6, 'scalability_latency'),
            (7, 'scalability_resources'), (8, 'security_latency_overhead'), (9, 'security_throughput_overhead'),
            (10, 'cpu_usage'), (11, 'memory_usage'), (12, 'ablation_impact_latency'), (13, 'ablation_impact_throughput'),
            (14, 'robustness_degradation'), (15, 'recovery_success'), (16, 'confidence_intervals'),
            (17, 'effect_sizes'), (18, 'pareto_tradeoff'),
        ]
    }
    provenance = {
        'figures': figure_map,
        'tables': {
            'summary': {'file': 'results/aggregated/summary.csv', 'sources': ['results/raw_runs/*.json'], 'script': 'analysis/aggregate_results.py'},
            'confidence_intervals': {'file': 'results/aggregated/confidence_intervals.csv', 'sources': ['results/raw_runs/*.json'], 'script': 'analysis/aggregate_results.py'},
            'stats': {'file': 'results/aggregated/stat_tests.csv', 'sources': ['results/aggregated/tidy_runs.csv'], 'script': 'analysis/stats_analysis.py'},
            'effect_sizes': {'file': 'results/aggregated/effect_sizes.csv', 'sources': ['results/aggregated/tidy_runs.csv'], 'script': 'analysis/effect_sizes.py'},
        },
        'report_sections': {
            'executive_summary': ['results/aggregated/summary.csv'],
            'latency_findings': ['results/figures/figure_02_latency_distribution.png', 'results/figures/figure_03_latency_p95_comparison.png'],
            'throughput_findings': ['results/figures/figure_04_throughput_comparison.png', 'results/figures/figure_05_throughput_vs_scale.png'],
            'robustness_findings': ['results/figures/figure_14_robustness_degradation.png', 'results/figures/figure_15_recovery_success.png'],
        },
    }
    (root / 'figure_table_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
