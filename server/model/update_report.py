"""
Update docs/REPORT.md results section with latest metrics and figure links.

Usage:
  python server/model/update_report.py --metrics server/model/metrics/metrics.json --report docs/REPORT.md

This script replaces the content between markers:
  <!-- AUTO-RESULTS:START -->
  ...
  <!-- AUTO-RESULTS:END -->
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

START = "<!-- AUTO-RESULTS:START -->"
END = "<!-- AUTO-RESULTS:END -->"


def format_markdown(metrics: dict) -> str:
    overall = metrics.get('overall_accuracy')
    per_class = metrics.get('per_class', {})
    lines = []
    if overall is not None:
        lines.append(f"- Overall accuracy: {overall:.4f} ({overall*100:.2f}%)")
    if per_class:
        lines.append("\nPer-class metrics:")
        lines.append("")
        lines.append("| Class | Precision | Recall | F1 | Support |")
        lines.append("|---|---:|---:|---:|---:|")
        for cls, m in per_class.items():
            prec = m.get('precision', 0.0)
            rec = m.get('recall', 0.0)
            f1 = m.get('f1', 0.0)
            sup = m.get('support', 0)
            lines.append(f"| {cls} | {prec:.3f} | {rec:.3f} | {f1:.3f} | {sup} |")
    lines.append("\nFigures (latest):")
    lines.append("- Confusion matrix: `server/model/metrics/confusion_matrix.png`")
    lines.append("- Class distribution pie: `server/model/metrics/class_distribution_pie.png`")
    lines.append("- Per-class accuracy bar: `server/model/metrics/per_class_accuracy_bar.png`")
    return "\n".join(lines) + "\n"


def update_report(report_path: Path, new_md: str) -> None:
    src = report_path.read_text(encoding='utf-8')
    if START in src and END in src:
        prefix, rest = src.split(START, 1)
        _, suffix = rest.split(END, 1)
        updated = f"{prefix}{START}\n{new_md}{END}{suffix}"
    else:
        # If markers missing, append a new section at the end
        updated = src.rstrip() + "\n\n## Auto-generated results\n\n" + START + "\n" + new_md + END + "\n"
    report_path.write_text(updated, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metrics', type=Path, default=Path('server/model/metrics/metrics.json'))
    ap.add_argument('--report', type=Path, default=Path('docs/REPORT.md'))
    args = ap.parse_args()

    if not args.metrics.exists():
        raise SystemExit(f"Metrics file not found: {args.metrics}")
    metrics = json.loads(args.metrics.read_text(encoding='utf-8'))
    md = format_markdown(metrics)
    update_report(args.report, md)
    print(f"Report updated: {args.report}")


if __name__ == '__main__':
    main()
