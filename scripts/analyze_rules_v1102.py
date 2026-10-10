#!/usr/bin/env python3
"""V1.10.2 只读分流审计：规则类型、静态覆盖候选、版本差异。"""
import argparse
import csv
import fnmatch
import hashlib
import ipaddress
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

FIELDS = ['级别','关系','A规则','A策略','A来源','A位置','B规则','B策略','B来源','B位置','说明']

def read(path, section, offset=0):
    items, source = [], '未知来源'
    for n, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        s = raw.strip()
        if s.startswith('# 来源：'):
            source = s.split('来源：', 1)[1].split('|', 1)[0].strip()
        if not s or s.startswith(('#',';','//')):
            continue
        p = [x.strip() for x in s.split(',')]
        if len(p) < 3 or not all(p[:3]):
            raise ValueError(f'{path}:{n} 规则格式异常')
        items.append(dict(kind=p[0],value=p[1].lower(),policy=p[2],source=source,
                          where=f'{section}:{n}',order=offset+len(items)))
    if not items:
        raise ValueError(f'{path} 无有效规则')
    return items

def overlap(a,b,relation,note):
    if a['policy'] == b['policy']:
        return None
    priority = ('P1-人工复核' if ('reject' in (a['policy'],b['policy']) or
                'direct' in (a['policy'],b['policy'])) else 'P2-观察')
    return dict(zip(FIELDS,[priority,relation,a['kind']+','+a['value'],a['policy'],
                            a['source'],a['where'],b['kind']+','+b['value'],
                            b['policy'],b['source'],b['where'],note]))

def analyze(before,after):
    rules = read(before,'前段')
    rules += read(after,'后段',len(rules))
    types = Counter(r['kind'] for r in rules)
    domains = [r for r in rules if r['kind'] in ('HOST','HOST-SUFFIX')]
    suffixes = defaultdict(list)
    for r in domains:
        if r['kind'] == 'HOST-SUFFIX':
            suffixes[r['value']].append(r)
    domain,iprows = [],[]
    for r in domains:
        labels = r['value'].split('.')
        for start in range(0 if r['kind']=='HOST' else 1,len(labels)):
            for p in suffixes.get('.'.join(labels[start:]),[]):
                if r['order']==p['order']:
                    continue
                row = overlap(r,p,'域名/父级后缀','包含关系，非实际命中结论')
                if row:
                    domain.append(row)
    for r in rules:
        if r['kind']=='HOST-KEYWORD' and len(r['value'])>=3:
            for p in domains:
                if r['value'] in p['value']:
                    row=overlap(r,p,'关键词/域名','只检查已列明域名')
                    if row:
                        domain.append(row)
        if r['kind']=='HOST-WILDCARD':
            for p in domains:
                if fnmatch.fnmatchcase(p['value'],r['value']):
                    row=overlap(r,p,'通配符/域名','fnmatch近似，非客户端语义')
                    if row:
                        domain.append(row)
    for family,type_name in [(4,'IP-CIDR'),(6,'IP6-CIDR')]:
        nets=[]
        for r in rules:
            if r['kind']!=type_name:
                continue
            net=ipaddress.ip_network(r['value'],strict=False)
            if net.version!=family:
                raise ValueError(f'{r["where"]}: IP类型不匹配')
            nets.append((net,r))
        nets.sort(key=lambda v:(int(v[0].network_address),v[0].prefixlen))
        active=[]
        for net,r in nets:
            start=int(net.network_address)
            active=[(n,p) for n,p in active if int(n.broadcast_address)>=start]
            for n,p in active:
                if n.overlaps(net):
                    row=overlap(r,p,'IP网段交集','共享网段不表示策略错误')
                    if row:
                        iprows.append(row)
            active.append((net,r))
    return types,domain,iprows

def key(row):
    values=sorted([(row['A规则'],row['A策略']),(row['B规则'],row['B策略'])])
    return hashlib.sha256(json.dumps([row['关系'],values],ensure_ascii=False).encode()).hexdigest()

def save(before,after,report):
    types,domains,ips=analyze(before,after)
    report.mkdir(parents=True,exist_ok=True)
    for name,rows in [('domain_overlap.csv',domains),('ip_overlap.csv',ips)]:
        with (report/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    total=sum(types.values())
    md=['# V1.10.2 规则类型统计','',f'总规则数：{total}','',
        '| 类型 | 数量 | 比例 |','|---|---:|---:|']
    md += [f'| {name} | {count} | {count/total:.2%} |' for name,count in types.most_common()]
    (report/'rule_types.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    rows=domains+ips
    signatures=sorted({key(r) for r in rows})
    levels=Counter(r['级别'] for r in rows)
    old=subprocess.run(['git','show','HEAD:reports/v1.10/priority_audit.json'],
                       capture_output=True,text=True,check=False)
    previous=None
    if old.returncode==0:
        try:
            previous=set(json.loads(old.stdout)['signatures'])
        except (ValueError,KeyError,TypeError):
            pass
    added=set(signatures)-previous if previous is not None else set()
    removed=previous-set(signatures) if previous is not None else set()
    data=dict(version='V1.10.2',rule_count=total,rule_types=dict(types),
              domain_candidates=len(domains),ip_candidates=len(ips),
              risk_levels=dict(levels),unique_pairs=len(signatures),signatures=signatures,
              baseline_found=previous is not None,
              added_candidates=len(added) if previous is not None else None,
              removed_candidates=len(removed) if previous is not None else None)
    (report/'priority_audit.json').write_text(
        json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# V1.10.2 潜在覆盖与优先级复核','',
        f'- 域名跨策略候选：{len(domains)}对',f'- IP跨策略候选：{len(ips)}对',
        f'- P1人工复核候选：{levels["P1-人工复核"]}对',
        f'- P2观察候选：{levels["P2-观察"]}对',
        f'- 去重后候选规则对：{len(signatures)}对','',
        '## 人工复核样例（前30条）','',
        '| 级别 | 关系 | A规则及策略 | B规则及策略 |','|---|---|---|---|']
    for r in sorted(rows,key=lambda x:(x['级别'],x['关系']))[:30]:
        md.append(f'| {r["级别"]} | {r["关系"]} | {r["A规则"]} → {r["A策略"]} | {r["B规则"]} → {r["B策略"]} |')
    md += ['','## 分析边界','','- 仅静态候选，不代表Quantumult X真实规则命中或匹配优化优先级。',
           '- 不包含前置Advertising、独立TikTok、用户本地规则；关键词及通配符只检查已列域名样例。',
           '- 仅标注人工复核优先级，不自动删改规则，不增加发布阻断条件。',
           '- 完整来源及行号参见CSV；IP包含可能是共享CDN的正常现象。']
    (report/'priority_audit.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    diff=('没有已发布V1.10.2分析基线，首次运行。' if previous is None else
          f'相较上版：新增{len(added)}对候选，减少{len(removed)}对候选。')
    (report/'rule_analysis_diff.md').write_text(
        '# V1.10.2 静态分析差异\n\n'+diff+'\n',encoding='utf-8')
    print(f'规则{total}条；域名候选{len(domains)}对，IP候选{len(ips)}对；{diff}')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--after',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    save(a.before,a.after,a.report)
