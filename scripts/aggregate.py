#!/usr/bin/env python3
"""Quantumult X 公开规则聚合器：保持 V1.7 源顺序、策略、附加参数；失败不发布。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

ALLOWED_TYPES = {
    'HOST', 'HOST-SUFFIX', 'HOST-KEYWORD', 'HOST-WILDCARD', 'USER-AGENT',
    'IP-CIDR', 'IP6-CIDR', 'IP-ASN', 'GEOIP', 'PROCESS-NAME',
    'SRC-IP', 'DST-PORT', 'SRC-PORT',
}
MAX_SINGLE_BYTES = 10 * 1024 * 1024
MAX_OUTPUT_BYTES = 18 * 1024 * 1024
EXPECTED_HOSTS = {'cdn.jsdelivr.net', 'raw.githubusercontent.com'}
VALID_POLICY = re.compile(r'^[\w\u3400-\u9fff\- .]+$', re.U)


class AggregationError(RuntimeError):
    pass


def fetch_text(url: str) -> str:
    """只获取公开 HTTPS 规则；限制返回体尺寸，失败会重试。"""
    u = urlparse(url)
    if u.scheme != 'https' or u.hostname not in EXPECTED_HOSTS or u.username or u.password:
        raise AggregationError(f'不允许的资源地址: {url}')
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'QX-Rule-Aggregator/1.0',
                'Accept': 'text/plain',
            })
            with urllib.request.urlopen(req, timeout=35) as res:
                # 禁止把来自不可信跳转的结果当成公开规则资源。
                dest = urlparse(res.geturl())
                if dest.scheme != 'https' or dest.hostname not in EXPECTED_HOSTS:
                    raise AggregationError(f'下载重定向到未授权主机: {dest.hostname}')
                data = res.read(MAX_SINGLE_BYTES + 1)
                if len(data) > MAX_SINGLE_BYTES:
                    raise AggregationError(f'单文件超过10 MiB限制: {url}')
            return data.decode('utf-8-sig')
        except (OSError, UnicodeError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt != 2:
                time.sleep(2 ** attempt)
    raise AggregationError(f'资源获取失败: {url}: {last_error}')


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or not isinstance(data.get('sources'), list):
        raise AggregationError('sources.json 格式错误或版本不支持')
    sources = data['sources']
    if not sources:
        raise AggregationError('不能生成空规则源')
    seen = set()
    for i, item in enumerate(sources, 1):
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in ('tag','url','policy')):
            raise AggregationError(f'第{i}条源字段不完整')
        if item['url'] in seen:
            raise AggregationError(f'同一远程URL重复订阅: {item["url"]}')
        seen.add(item['url'])
        if item.get('segment') not in ('前段', '后段'):
            raise AggregationError(f'第{i}条规则未指定正确的聚合分段')
        if not VALID_POLICY.fullmatch(item['policy']) or ',' in item['policy']:
            raise AggregationError(f'非法策略名: {item["policy"]!r}')
        url = urlparse(item['url'])
        if url.scheme != 'https' or url.hostname not in EXPECTED_HOSTS or url.username or url.password:
            raise AggregationError(f'非可信公开规则URL: {item["url"]}')
    if [i['segment'] for i in sources] != sorted((i['segment'] for i in sources), key=lambda x: {'前段': 0, '后段': 1}[x]):
        raise AggregationError('规则分段顺序错误：前段必须排在后段之前')
    if not any(x['segment']=='前段' for x in sources) or not any(x['segment']=='后段' for x in sources):
        raise AggregationError('两个规则分段都必须有上游规则')
    return sources


def canonical_rule(line: str, policy: str, tag: str, lineno: int) -> tuple[str, str, str]:
    """原规则第三字段通常是上游策略：覆盖为当前V1.7实际 force-policy。"""
    fields = [p.strip() for p in line.split(',')]
    if len(fields) < 3 or not fields[0] or not fields[1] or not fields[2]:
        raise AggregationError(f'{tag} 第{lineno}行格式异常: {line[:160]}')
    kind = fields[0].upper()
    if kind not in ALLOWED_TYPES:
        raise AggregationError(f'{tag} 第{lineno}行存在未审查规则类型 {kind}；拒绝静默丢弃')
    # 其余字段原样保留，如 no-resolve；不冒险进行泛化或后缀归并。
    out = ','.join([kind, fields[1], policy] + fields[3:])
    return out, kind, fields[1].lower()


def parse_source(text: str, src: dict) -> list[tuple[str, str, str, int]]:
    result = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(('#',';','//')):
            continue
        if line.startswith('[') or line.startswith('!'):
            raise AggregationError(f'{src["tag"]} 第{lineno}行不是 Quantumult X 纯规则列表')
        rule, kind, value = canonical_rule(line, src['policy'], src['tag'], lineno)
        result.append((rule,kind,value,lineno))
    if not result:
        raise AggregationError(f'规则源内容为空: {src["tag"]}')
    return result


def aggregate(sources: list[dict], fetch: Callable[[str],str]):
    """返回列表文本与报告。严格保留原始源顺序和源内规则顺序。"""
    contents = [None] * len(sources)
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch,src['url']):i for i,src in enumerate(sources)}
        for future in as_completed(futures):
            i = futures[future]
            try:
                contents[i] = parse_source(future.result(), sources[i])
            except Exception as exc:
                raise AggregationError(f'资源 {sources[i]["tag"]} 获取或解析失败: {exc}') from exc

    output = {
        '前段': [
            '# Quantumult X V1.8 分流聚合：前段（在 TikTok 独立规则之前）',
            '# 每条规则自带策略；不得在远程订阅上指定 force-policy。',
            '# 保留 V1.7 原始先后顺序，不包括广告、TikTok 独立规则。',
        ],
        '后段': [
            '# Quantumult X V1.8 分流聚合：后段（在 TikTok 独立规则之后）',
            '# 每条规则自带策略；不得在远程订阅上指定 force-policy。',
            '# 保留 V1.7 原始先后顺序，不包括广告、TikTok 独立规则。',
        ],
    }
    # 仅删除同一条规则（含策略和修饰符）的完全重复。不同策略同名规则全部保留。
    exact_seen = set()
    selector_first = {}
    collisions = []
    stats = []
    total_in = total_deduped = 0
    for src, rules in zip(sources, contents):
        dest = output[src['segment']]
        dest.extend(['', f'# 来源：{src["tag"]} | 策略：{src["policy"]}'])
        kept = 0
        for rule, kind, value, line_num in rules:
            total_in += 1
            if rule in exact_seen:
                total_deduped += 1
                continue
            exact_seen.add(rule)
            selector = (kind, value)
            if selector in selector_first and selector_first[selector]['policy'] != src['policy']:
                old = selector_first[selector]
                collisions.append({
                    '类型':'完全相同的匹配条件、不同策略',
                    '匹配类型':kind,'匹配值':value,
                    '先出现策略':old['policy'],'先出现来源':old['tag'],
                    '后出现策略':src['policy'],'后出现来源':src['tag'],
                    '处理':'保留原始顺序；不自动改变策略',
                })
            selector_first.setdefault(selector, {'policy':src['policy'], 'tag':src['tag']})
            dest.append(rule)
            kept += 1
        stats.append({'来源':src['tag'],'策略':src['policy'],'原始条数':len(rules),'保留条数':kept})
    texts = {segment:'\n'.join(lines)+'\n' for segment, lines in output.items()}
    sizes = {segment:len(content.encode('utf-8')) for segment,content in texts.items()}
    for segment,size in sizes.items():
        if size > MAX_OUTPUT_BYTES:
            raise AggregationError(f'{segment}文件 {size} 字节，超过18 MiB上限。请进一步分拆。')
    size = sum(sizes.values())
    report = {
        '来源文件数':len(sources),'规则原始总数':total_in,
        '移除完全重复规则数':total_deduped,
        '输出规则总数':total_in - total_deduped,
        '输出文件字节数':size,
        'sha256':{seg:hashlib.sha256(data.encode('utf-8')).hexdigest() for seg,data in texts.items()},
        '各段字节数':sizes,
        '各来源统计':stats,
        '完全相同条件但策略不同的冲突':collisions,
        '重要说明':'未进行HOST与HOST-SUFFIX、关键词等覆盖关系的自动归并；需要结合客户端实际命中日志人工核验。',
    }
    return texts, report


def save_reports(report: dict, report_dir: Path):
    report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/'summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    output = [
        '# 聚合规则审计报告','',
        f'- 上游规则源：{report["来源文件数"]} 份',
        f'- 原始规则条数：{report["规则原始总数"]}',
        f'- 完全重复并删除：{report["移除完全重复规则数"]}',
        f'- 输出规则条数：{report["输出规则总数"]}',
        f'- 输出文件字节数：{report["输出文件字节数"]}',
        f'- 相同匹配条件但策略不同：{len(report["完全相同条件但策略不同的冲突"])} 处',
        '',
        '## 设计边界',
        '- 保留全部不同策略的重复条件，按 V1.7 原先顺序排列，首个命中者的优先级不变。',
        '- 除完全相同行外，不自动合并 HOST/后缀/关键词/IP 网段，避免误删例外。',
        '- 同一域名被宽泛后缀/关键词覆盖的问题仍需在 Quantumult X 中实测。',
        '- 不处理广告、Rewrite、节点、订阅凭据与 MITM 私钥。',
        '', '## 来源明细','',
        '| 来源 | 策略 | 原始 | 保留 |','|---|---|---:|---:|',
    ]
    for s in report['各来源统计']:
        output.append(f'| {s["来源"]} | {s["策略"]} | {s["原始条数"]} | {s["保留条数"]} |')
    output.extend(['','## 精确条件冲突','',
                   '详细情况见 `conflicts.csv`，未进行自动策略覆盖。'])
    (report_dir/'README.md').write_text('\n'.join(output)+'\n',encoding='utf-8')
    keys = ['类型','匹配类型','匹配值','先出现策略','先出现来源','后出现策略','后出现来源','处理']
    with (report_dir/'conflicts.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=keys)
        writer.writeheader()
        writer.writerows(report['完全相同条件但策略不同的冲突'])


def main(argv=None):
    parser=argparse.ArgumentParser(description='自动聚合 Quantumult X 公开分流资源')
    parser.add_argument('--manifest',default='sources.json')
    parser.add_argument('--out-dir',default='rules')
    parser.add_argument('--report',default='reports')
    args=parser.parse_args(argv)
    try:
        sources=load_manifest(Path(args.manifest))
        contents,report=aggregate(sources,fetch_text)
        # 只有全部下载、解析、检查成功后才落盘写最终规则，失败由Actions保留前一版本。
        output_dir=Path(args.out_dir)
        output_dir.mkdir(parents=True,exist_ok=True)
        save_reports(report,Path(args.report))
        for segment, content in contents.items():
            filename = 'BeforeTikTok.list' if segment == '前段' else 'AfterTikTok.list'
            (output_dir/filename).write_text(content, encoding='utf-8')
        print(f'聚合成功：{report["来源文件数"]}份源，{report["输出规则总数"]}条规则，移除重复{report["移除完全重复规则数"]}条。')
        print(f'精确条件跨策略冲突：{len(report["完全相同条件但策略不同的冲突"])}；请查看 reports/conflicts.csv')
        return 0
    except Exception as exc:
        print(f'聚合失败；不会发布不完整版本：{exc}',file=sys.stderr)
        return 1

if __name__=='__main__':
    sys.exit(main())
