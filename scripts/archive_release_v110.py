#!/usr/bin/env python3
"""为每次成功准备发布的 V1.10 规则/报告变更生成追加式 Markdown 记录。

在规则构建、安全审计通过且 git add rules/v1.10 reports/v1.10 后调用；
只能在存在实际暂存变更时执行，且与本次规则和报告一起提交。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

TITLE = """# V1.10 规则与审计发布日志

此处保留每次**产生实际文件变更并进入 Git 提交**的 V1.10 更新记录。
无内容变更的定时运行只出现在 GitHub Actions 运行历史中，不重复生成快照。
每条记录的专属 Markdown 文件不会覆盖，以便长期追溯版本、规则哈希与报告指标。

| 发布准备时间（UTC） | Actions 运行 | 变更类型 | 规则总数 | SHA256（前段/后段前12位） | 文件变更数 |
|---|---|---|---:|---|---:|
"""


def staged_changes() -> list[str]:
    proc = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--', 'rules/v1.10/', 'reports/v1.10/'],
        capture_output=True, text=True, encoding='utf-8', check=True)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def build_snapshot(summary: dict, changed: list[str], run_id: str, run_number: str,
                   repository: str, when: datetime):
    if not changed:
        raise ValueError('没有暂存的规则/报告变化，不应记录空发布')
    if not re.fullmatch(r'[0-9]+', run_id) or not re.fullmatch(r'[0-9]+', run_number):
        raise ValueError('非法 Actions 运行编号')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('非法仓库路径')
    if when.tzinfo is None:
        raise ValueError('发布时刻必须包含时区')
    rule_count = summary['输出规则总数']
    source_count = summary['来源文件数']
    old_sha = summary['sha256']
    front, back = old_sha['前段'], old_sha['后段']
    if (not isinstance(rule_count, int) or rule_count < 1 or
        not isinstance(source_count, int) or source_count < 1 or
        not all(re.fullmatch(r'[a-f0-9]{64}', s) for s in (front, back))):
        raise ValueError('规则统计和哈希数据异常')
    conflict_count = len(summary['完全相同条件但策略不同的冲突'])
    changed = sorted(set(changed))
    # 严格限制索引来源，防止意外把仓库中其他文件当作已发布更新。
    if any(not (p.startswith('rules/v1.10/') or p.startswith('reports/v1.10/')) for p in changed):
        raise ValueError('尝试记录非当前版本变更')
    kind = '规则与报告更新' if any(p.startswith('rules/v1.10/') for p in changed) else '仅报告更新'
    at = when.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    url = f'https://github.com/{repository}/actions/runs/{run_id}'
    filename = f'run-{run_id}.md'
    row = (f'| {at} | [#{run_number}]({url}) | {kind} | {rule_count:,} | '
           f'`{front[:12]}` / `{back[:12]}` | {len(changed)} |\n')
    snapshot = [
        f'# V1.10 发布记录 · GitHub Actions #{run_number}', '',
        f'- 记录时间：{at}',
        f'- 工作流运行：[{run_id}]({url})',
        f'- 变更类型：{kind}',
        f'- 上游规则源：{source_count} 份',
        f'- 已聚合规则：{rule_count:,} 条',
        f'- 跨策略精确条件冲突记录：{conflict_count} 条',
        '- 发布前校验：V1.10 审计步骤已通过，才执行此存档程序。',
        f'- 前段 SHA256：`{front}`',
        f'- 后段 SHA256：`{back}`',
        '',
        '## 本次变更文件',
        '',
        *[f'- `{path}`' for path in changed],
        '',
        '## 追溯与回退',
        '',
        f'- [此轮 GitHub Actions 记录]({url})',
        f'- [仓库提交历史](https://github.com/{repository}/commits/main/)',
        '- 完整规则及报告的历史内容，可在包含本快照的发布提交中回溯。',
        '- 这里是成功发布的预提交存档；若后续 Git 推送被远端拒绝，本快照不会进入 main。',
        '- 切勿将私人 Quantumult X 配置、MITM 私钥或节点订阅上传到公开仓库。',
        '',
    ]
    return filename, row, '\n'.join(snapshot)


def save(history: Path, summary_path: Path, changed: list[str], run_id: str,
         run_number: str, repository: str, when: datetime) -> Path:
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    name, row, snapshot = build_snapshot(summary, changed, run_id, run_number, repository, when)
    history.mkdir(parents=True, exist_ok=True)
    snap_dir = history / 'runs'
    snap_dir.mkdir(parents=True, exist_ok=True)
    path = snap_dir / name
    if path.exists():
        raise ValueError(f'此运行已保存历史快照：{path}')
    index = history / 'updates.md'
    existing = index.read_text(encoding='utf-8') if index.exists() else TITLE
    if f'/actions/runs/{run_id}' in existing:
        raise ValueError('此运行编号已存在于更新索引')
    # 先生成独立记录，再追加索引，二者与本次规则变化同一个 Git commit 发布。
    path.write_text(snapshot, encoding='utf-8')
    index.write_text(existing.rstrip('\n') + '\n' + row, encoding='utf-8')
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description='保留每次成功发布的 V1.10 更新历史')
    parser.add_argument('--summary', type=Path, default=Path('reports/v1.10/summary.json'))
    parser.add_argument('--history', type=Path, default=Path('reports/history/v1.10'))
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--run-number', required=True)
    parser.add_argument('--repository', required=True)
    options = parser.parse_args()
    changed = staged_changes()
    if not changed:
        print('没有实质规则/报告变更，不记录空运行。')
        return
    path = save(options.history, options.summary, changed, options.run_id,
                options.run_number, options.repository, datetime.now(timezone.utc))
    print(f'已保存永久更新快照：{path}')


if __name__ == '__main__':
    main()
