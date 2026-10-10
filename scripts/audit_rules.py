#!/usr/bin/env python3
"""聚合规则发布前审计：禁止未经审核的分流变化，保留上一次成功规则。"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

FILES = ('BeforeTikTok.list', 'AfterTikTok.list')
RULE_TYPES = frozenset({
    'HOST', 'HOST-SUFFIX', 'HOST-KEYWORD', 'HOST-WILDCARD', 'USER-AGENT',
    'IP-CIDR', 'IP6-CIDR', 'IP-ASN', 'GEOIP', 'PROCESS-NAME',
    'SRC-IP', 'DST-PORT', 'SRC-PORT',
})

class AuditError(RuntimeError):
    pass


def text_from_head(path: str) -> str | None:
    """读取当前 HEAD 的已发布文件，不修改工作区。"""
    proc = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True, text=True,
                          encoding='utf-8', errors='replace', check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout


def parse_rule_text(content: str, filename: str, allowed: set[str]):
    """静态检查纯 Quantumult X 规则，并计算按文件原顺序的首个匹配策略。"""
    rules = []
    for number, raw in enumerate(content.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        if line.startswith('[') or '://' in line:
            raise AuditError(f'{filename}:{number} 混入配置节或 URL')
        parts = [x.strip() for x in line.split(',')]
        if len(parts) < 3 or parts[0] not in RULE_TYPES or not parts[1]:
            raise AuditError(f'{filename}:{number} 存在非法规则类型或缺少匹配项')
        if parts[2] not in allowed:
            raise AuditError(f'{filename}:{number} 策略组未定义：{parts[2]}')
        if not all(parts[:3]):
            raise AuditError(f'{filename}:{number} 规则核心字段为空')
        rules.append((parts[0], parts[1].lower(), parts[2], line))
    if not rules:
        raise AuditError(f'{filename} 内容为空')
    return rules


def first_policies(rule_sets):
    """仅比较精确匹配条件的首选策略；不宣称检测所有通配符/后缀重叠。"""
    mapping = {}
    for group in rule_sets:
        for kind, match, policy, line in group:
            mapping.setdefault((kind, match), policy)
    return mapping


def risky_selectors(rule_sets):
    """只把明显会覆盖几乎所有流量的规则视为高风险。"""
    risk = []
    for group in rule_sets:
        for kind, match, policy, line in group:
            if ((kind in ('HOST-SUFFIX','HOST','HOST-WILDCARD') and match in
                 ('.', '*', 'com', 'net', 'org', 'cn', 'io')) or
                (kind == 'HOST-KEYWORD' and match in ('.', '*')) or
                (kind == 'IP-CIDR' and match in ('0.0.0.0/0', '0/0')) or
                (kind == 'IP6-CIDR' and match in ('::/0', '0::/0'))):
                risk.append(line)
    return risk


def check_generated(outdir: Path, report_dir: Path, policy_file: Path,
                    max_delta_percent: float, approve_changes: bool,
                    head_reader=text_from_head, head_rule_prefix='rules', head_report_prefix='reports', report_version='V1.8.1'):
    allowed = set(json.loads(policy_file.read_text(encoding='utf-8'))['allowed_policies'])
    summary = json.loads((report_dir / 'summary.json').read_text(encoding='utf-8'))
    actual = []
    previous = []
    issues = []
    notes = []
    for group, name in zip(('前段','后段'),FILES):
        filename = outdir / name
        raw = filename.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != summary['sha256'][group]:
            issues.append(f'{name} SHA256 与构建报告不一致')
        if len(raw) != summary['各段字节数'][group]:
            issues.append(f'{name} 字节数与构建报告不一致')
        actual.append(parse_rule_text(raw.decode('utf-8-sig'),name,allowed))
        base_content = head_reader(f'{head_rule_prefix}/{name}')
        previous.append(parse_rule_text(base_content,name+'[HEAD]',allowed) if base_content else [])
    total = sum(map(len,actual))
    if total != summary['输出规则总数']:
        issues.append(f'规则总数不一致：实际{total}，报告{summary["输出规则总数"]}')
    if total < 1_000:
        issues.append(f'规则数量异常偏低：{total}')
    old_total = sum(map(len, previous))
    current_mapping = first_policies(actual)
    previous_mapping = first_policies(previous)
    changed = [(kind, match, before, current_mapping[(kind,match)])
               for (kind, match), before in previous_mapping.items()
               if (kind, match) in current_mapping and current_mapping[(kind,match)] != before]
    removed = [(kind,match) for kind,match in previous_mapping if (kind,match) not in current_mapping]
    added = [(kind,match) for kind,match in current_mapping if (kind,match) not in previous_mapping]
    delta = ((total - old_total) / old_total * 100) if old_total else 0
    if old_total:
        if abs(delta) > max_delta_percent and not approve_changes:
            issues.append(f'规则总量变化 {delta:+.2f}% 超过阈值 ±{max_delta_percent:g}%')
        if changed and not approve_changes:
            issues.append(f'{len(changed)} 个相同匹配条件的首选策略发生变化')
        if removed and len(removed) > max(200, int(len(previous_mapping) * 0.10)) and not approve_changes:
            issues.append(f'消失的匹配条件过多：{len(removed)}')
    else:
        notes.append('未发现已发布的 HEAD 规则，属于首次构建：无法进行前后版本回归比较')
    old_risk = set(risky_selectors(previous))
    new_risk = sorted(set(risky_selectors(actual)) - old_risk)
    if new_risk:
        issues.append(f'出现 {len(new_risk)} 条新增的极宽范围危险规则（即使批准变更也禁止自动发布）')

    old_summary_text = head_reader(f'{head_report_prefix}/summary.json')
    current_conflicts = len(summary['完全相同条件但策略不同的冲突'])
    if old_summary_text:
        try:
            old_conflicts = len(json.loads(old_summary_text)['完全相同条件但策略不同的冲突'])
            if current_conflicts > old_conflicts + max(30, int(old_conflicts * .20)) and not approve_changes:
                issues.append(f'冲突数量从 {old_conflicts} 增至 {current_conflicts}，增幅超出审核阈值')
        except (KeyError, ValueError, TypeError) as exc:
            notes.append(f'上一次冲突报告不能解析：{exc}')

    rows = [
        f'# {report_version} 规则发布安全审计', '',
        f'- 本次规则条数：{total}',
        f'- 上次已发布规则条数：{old_total if old_total else "无可比版本"}',
        f'- 数量变化：{delta:+.2f}%' if old_total else '- 数量变化：不适用',
        f'- 精确匹配条件首选策略变化：{len(changed)}',
        f'- 新增精确匹配条件：{len(added)}',
        f'- 消失精确匹配条件：{len(removed)}',
        f'- 本次跨策略重复条件：{current_conflicts}',
        f'- 新出现极宽范围规则：{len(new_risk)}',
        f'- 人工批准变化：{"是" if approve_changes else "否"}',
        '',
        '**重要限制：** 仅检查相同类型、相同匹配项下的首个策略，无法完整判断后缀、关键词、通配符及 IP 网段包含关系。',
        '',
        '## 需关注的问题',
    ]
    rows.extend(f'- {msg}' for msg in (issues or ['未触发阻止发布条件']))
    if notes:
        rows.extend(['', '## 提示'] + [f'- {msg}' for msg in notes])
    if changed:
        rows.extend(['','## 首选策略变动示例'] +
                    [f'- `{kind},{match}`：`{before}` → `{after}`'
                     for kind,match,before,after in changed[:30]])
    if removed:
        rows.extend(['','## 匹配条件减少示例'] +
                    [f'- `{kind},{match}`' for kind,match in removed[:20]])
    if new_risk:
        rows.extend(['','## 新增高风险规则'] + [f'- `{rule}`' for rule in new_risk[:30]])
    report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir / 'audit.md').write_text('\n'.join(rows) + '\n',encoding='utf-8')
    return issues


def main():
    parser=argparse.ArgumentParser(description='聚合规则变更审计')
    parser.add_argument('--out-dir', default='rules')
    parser.add_argument('--report', default='reports')
    parser.add_argument('--policy-file', default='config/policies.json')
    parser.add_argument('--max-delta-percent', type=float, default=15)
    parser.add_argument('--approve-changes', action='store_true')
    parser.add_argument('--report-version', default='V1.8.1')
    parser.add_argument('--head-rule-prefix', default='rules')
    parser.add_argument('--head-report-prefix', default='reports')
    args=parser.parse_args()
    try:
        issues=check_generated(Path(args.out_dir),Path(args.report),Path(args.policy_file),
                               args.max_delta_percent,args.approve_changes,
                               head_rule_prefix=args.head_rule_prefix,
                               head_report_prefix=args.head_report_prefix, report_version=args.report_version)
        if issues:
            print('发现规则更新风险：\n' + '\n'.join('- '+x for x in issues),file=sys.stderr)
            print('请查看 reports/audit.md；已阻止提交，保留上次已发布版本。',file=sys.stderr)
            return 1
        print('发布前审计通过；未发现阻断条件。')
        return 0
    except (AuditError, OSError, ValueError, KeyError, UnicodeError) as exc:
        print(f'审计异常；不发布新规则：{exc}',file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
