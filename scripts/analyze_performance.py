#!/usr/bin/env python3
"""API-PERF C5 (U7) — Pipeline 效能日誌分析 CLI（零外部第三方依賴）。

流式解析結構化 JSON 日誌（每行一筆，含 event 為 performance_metric / pipeline_finished /
rag_finished 的 (phase, stage) 二維鍵計時），輸出 ASCII 統計報表：
  - 各 doc_type 平均處理耗時（依 pipeline_finished）
  - 各 (phase, stage) 效能剖析：樣本數 / 平均 / 最大 / 標準差（依 performance_metric）
  - P4 異步 RAG 獨立耗時統計（依 rag_finished，不併入主鏈）

僅使用標準庫（json / argparse / statistics / collections）。

用法：
  python scripts/analyze_performance.py                 # 預設讀 logs/pipeline.log
  python scripts/analyze_performance.py --log <path>
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict


def _stat_row(values):
    """回傳 (count, mean, max, stddev)；空集合回 (0,0,0,0)。"""
    if not values:
        return 0, 0.0, 0.0, 0.0
    n = len(values)
    mean = statistics.mean(values)
    mx = max(values)
    sd = statistics.pstdev(values) if n > 1 else 0.0
    return n, mean, mx, sd


def parse_log(path):
    """流式逐行解析 JSON 日誌，回傳聚合結構。非 JSON 行 / 無關 event 直接略過。"""
    # (phase, stage) -> [duration,...]
    stage_durations = defaultdict(list)
    # doc_type -> [pipeline_finished duration,...]
    doctype_total = defaultdict(list)
    # rag_status -> [duration,...]
    rag_durations = defaultdict(list)

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except (ValueError, TypeError):
                continue  # 非 JSON 行（純文字 console 行）略過
            if not isinstance(rec, dict):
                continue
            event = rec.get("event")
            if event == "performance_metric":
                phase = rec.get("phase", "?")
                stage = rec.get("stage", "?")
                dur = rec.get("duration_seconds")
                if isinstance(dur, (int, float)):
                    stage_durations[(phase, stage)].append(float(dur))
            elif event == "pipeline_finished":
                dt = rec.get("doc_type", "?")
                dur = rec.get("duration_seconds")
                if isinstance(dur, (int, float)):
                    doctype_total[dt].append(float(dur))
            elif event == "rag_finished":
                status = rec.get("rag_status", "?")
                dur = rec.get("duration_seconds")
                if isinstance(dur, (int, float)):
                    rag_durations[status].append(float(dur))

    return stage_durations, doctype_total, rag_durations


def render_report(stage_durations, doctype_total, rag_durations):
    lines = []
    lines.append("=" * 64)
    lines.append("  API-PERF 效能剖析報表 (U7 performance_metric 分析)")
    lines.append("=" * 64)

    # 1. 各 doc_type 主鏈平均耗時（pipeline_finished）
    lines.append("\n[1] 各 doc_type 主鏈 (P1-P3) 平均耗時")
    lines.append("-" * 64)
    lines.append(f"{'doc_type':<16}{'樣本':>6}{'平均(s)':>12}{'最大(s)':>12}{'標準差':>12}")
    if doctype_total:
        for dt in sorted(doctype_total):
            n, mean, mx, sd = _stat_row(doctype_total[dt])
            lines.append(f"{dt:<16}{n:>6}{mean:>12.3f}{mx:>12.3f}{sd:>12.3f}")
    else:
        lines.append("（無 pipeline_finished 樣本）")

    # 2. 各 (phase, stage) 效能剖析（performance_metric）
    lines.append("\n[2] 各 (phase, stage) 效能剖析")
    lines.append("-" * 64)
    lines.append(f"{'phase':<6}{'stage':<22}{'樣本':>6}{'平均(s)':>10}{'最大(s)':>10}{'標準差':>10}")
    if stage_durations:
        for (phase, stage) in sorted(stage_durations):
            n, mean, mx, sd = _stat_row(stage_durations[(phase, stage)])
            lines.append(f"{phase:<6}{stage:<22}{n:>6}{mean:>10.3f}{mx:>10.3f}{sd:>10.3f}")
    else:
        lines.append("（無 performance_metric 樣本）")

    # 3. P4 異步 RAG 獨立統計（rag_finished、不併主鏈）
    lines.append("\n[3] P4 異步 RAG 獨立耗時 (rag_finished)")
    lines.append("-" * 64)
    lines.append(f"{'rag_status':<16}{'樣本':>6}{'平均(s)':>12}{'最大(s)':>12}{'標準差':>12}")
    if rag_durations:
        for status in sorted(rag_durations):
            n, mean, mx, sd = _stat_row(rag_durations[status])
            lines.append(f"{status:<16}{n:>6}{mean:>12.3f}{mx:>12.3f}{sd:>12.3f}")
    else:
        lines.append("（無 rag_finished 樣本）")

    lines.append("=" * 64)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="analyze_performance",
        description="API-PERF U7 Pipeline 效能日誌分析（零外部依賴）",
    )
    parser.add_argument(
        "--log", default="logs/pipeline.log",
        help="結構化 JSON 日誌路徑（預設 logs/pipeline.log）",
    )
    args = parser.parse_args(argv)

    try:
        stage_durations, doctype_total, rag_durations = parse_log(args.log)
    except FileNotFoundError:
        print(f"找不到日誌檔: {args.log}")
        return 1

    print(render_report(stage_durations, doctype_total, rag_durations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
