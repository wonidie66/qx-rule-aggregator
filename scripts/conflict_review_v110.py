#!/usr/bin/env python3
"""V1.10 安全审计辅助报告：只分析精确选择器的策略重叠，不修改规则。"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = ('匹配类型', '匹配值', '先出现策略', '后出现策略', '先出现来源', '后出现来源')


def classify(a: str, b: str) -> str:
    if a == 'reject' or b == 'reject':
        return '拦截与放行重叠'
    if (a == 'direct') != (b == 'direct'):
        return '直连与代理重叠'
    if a != b:
        return '不同代理策略重叠'
    return '同策略重复（报告异常）'


def analyze(summary: dict) -> dict:
    rows = summary.get('完全相同条件但策略不同的冲突')
    if not isinstance(rows, list):
        raise ValueError('缺少有效的精确条件冲突列表')
    by_type = Counter()
    pair_counts = Counter()
    by_selector = defaultdict(list)
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k] for k in REQUIRED):
            raise ValueError(f'冲突记录#{index}字段缺失或格式错误')
        kind = classify(row['先出现策略'], row['后出现策略'])
        by_type[kind] += 1
        pair = (row['先出现来源'], row['后出现来源'], row['先出现策略'], row['后出现策略'])
        pair_counts[pair] += 1
        by_selector[(row['匹配类型'], row['匹配值'].lower())].append(row)
    top = sorted(pair_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:30]
    return {
        'schema_version': 1,
        'summary': {
            '上游规则源': summary.get('来源文件数'),
            '输出规则条数': summary.get('输出规则总数'),
            '跨策略重叠记录数': len(rows),
            '涉及独立选择器数': len(by_selector),
            '各类重叠数': {k: by_type.get(k, 0) for k in (
                '直连与代理重叠', '拦截与放行重叠',
                '不同代理策略重叠', '同策略重复（报告异常）')},
        },
        'top_pairs': [
            {'优先来源': k[0], '后续来源': k[1], '首选策略': k[2], '后续策略': k[3], '记录数': n}
            for k, n in top
        ],
        'direct_proxy_examples': [
            {'匹配类型': row['匹配类型'], '匹配值': row['匹配值'],
             '优先': row['先出现策略'], '后续': row['后出现策略'],
             '优先来源': row['先出现来源'], '后续来源': row['后出现来源']}
            for row in rows
            if classify(row['先出现策略'], row['后出现策略']) == '直连与代理重叠'
        ][:60],
        'boundaries': [
            '按生成规则中的完全相同类型和匹配值统计，并非实际访问日志或域名匹配模拟',
            '同一匹配项可以产生多条冲突记录；首选策略指聚合文件自身顺序，不涵盖前置 Advertising、独立 TikTok 及 filter_local',
            '未检测不同 HOST/HOST-SUFFIX/KEYWORD、IP 网段的包含关系；不自动删除或调整任何规则',
        ],
    }


def markdown(report: dict) -> str:
    s = report['summary']
    lines = [
        '# V1.10 规则重叠分类与人工复核报告', '',
        f'- 当前规则：{s["输出规则条数"]} 条，上游来源：{s["上游规则源"]} 份',
        f'- 跨策略重叠记录：{s["跨策略重叠记录数"]} 条',
        f'- 独立精确选择器：{s["涉及独立选择器数"]} 个', '',
    ]
    lines.extend(f'- {k}：{n}' for k, n in s['各类重叠数'].items())
    lines.extend(['', '## 重叠最多的来源组合', '',
                  '| 优先来源 → 后续来源 | 策略方向 | 重叠记录 |',
                  '|---|---|---:|'])
    for p in report['top_pairs']:
        left = p['优先来源'].replace('|', '\\|')
        right = p['后续来源'].replace('|', '\\|')
        lines.append(
            f'| {left} → {right} | {p["首选策略"]} → {p["后续策略"]} | {p["记录数"]} |'
        )
    lines.extend(['', '## 直连与代理交叉样例（最多60条）', '',
                  '| 选择器 | 优先策略 | 后续策略 | 来源 |',
                  '|---|---|---|---|'])
    for p in report['direct_proxy_examples']:
        selector = (p['匹配类型'] + ',' + p['匹配值']).replace('|', '\\|')
        lines.append(
            f'| {selector} | {p["优先"]} | {p["后续"]} | {p["优先来源"]} → {p["后续来源"]} |'
        )
    lines.extend(['', '## 审计边界', ''])
    lines.extend(f'- {line}' for line in report['boundaries'])
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='生成不改变分流行为的 V1.10 冲突分析报告')
    parser.add_argument('--summary', default='reports/v1.10/summary.json')
    parser.add_argument('--out-dir', default='reports/v1.10')
    opts = parser.parse_args()
    report = analyze(json.loads(Path(opts.summary).read_text(encoding='utf-8')))
    out = Path(opts.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'conflict_review.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'conflict_review.md').write_text(markdown(report), encoding='utf-8')
    print(f'冲突分类报告生成：{report["summary"]["跨策略重叠记录数"]} 条记录、'
          f'{report["summary"]["涉及独立选择器数"]} 个独立选择器')


if __name__ == '__main__':
    main()
