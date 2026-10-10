#!/usr/bin/env python3
"""仅在自己的电脑上运行；把现有私有配置中的[filter_remote]替换为聚合订阅。"""
import argparse
import re
from pathlib import Path


def replace(source: str, username: str, repository: str, branch: str = 'main') -> str:
    if not all(re.fullmatch(r'[A-Za-z0-9_.-]+',part) for part in (username,repository,branch)):
        raise ValueError('GitHub 用户名、仓库和分支名仅允许字母、数字、点、横线、下划线')
    base=f'https://cdn.jsdelivr.net/gh/{username}/{repository}@{branch}/rules'
    before_url=f'{base}/BeforeTikTok.list'
    after_url=f'{base}/AfterTikTok.list'
    start=re.search(r'^\[filter_remote\]\s*$',source,re.M)
    if not start: raise ValueError('没有找到 [filter_remote]')
    nxt=re.search(r'^\[[^\]]+\]\s*$',source[start.end():],re.M)
    if not nxt: raise ValueError('没有找到 [filter_remote] 下一个配置段，拒绝猜测')
    end=start.end()+nxt.start()
    section=source[start.end():end]
    adverts=[]; tiktok=[]; builtins=[]
    for line in section.splitlines():
        trim=line.strip()
        if trim.startswith('https://') and 'Advertising/Advertising.list' in trim and 'force-policy=reject' in trim:
            adverts.append(trim)
        elif trim.startswith('https://') and 'Semporia/TikTok-Unlock' in trim and 'force-policy=TikTok服务' in trim:
            tiktok.append(trim)
        elif trim.startswith('FILTER_'):
            builtins.append(trim)
    if len(adverts)!=1 or len(tiktok)!=1 or not builtins:
        raise ValueError('无法唯一确定广告完整版和内置规则；拒绝自动替换')
    lines=['[filter_remote]', '# 广告完整版单独保留，仍优先拒绝广告请求', adverts[0],
        '# TikTok之前的10份公开专项分流规则聚合；不设置 force-policy',
        f'{before_url}, tag=V1.8-前段分流, update-interval=259200, opt-parser=false, enabled=true',
        '# TikTok 解锁沿用原有 Semporia 资源，优先级位置不变',tiktok[0],
        '# TikTok之后的64份公开专项分流规则聚合；不设置 force-policy',
        f'{after_url}, tag=V1.8-后段分流, update-interval=259200, opt-parser=false, enabled=true',
        '# Quantumult X 内置规则保留原位置',*builtins,'']
    return source[:start.start()]+ '\n'.join(lines) + source[end:]


def main():
    p=argparse.ArgumentParser(description='本地安全替换 Quantumult X 分流规则资源，不改证书或节点')
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--user',required=True)
    p.add_argument('--repo',required=True)
    p.add_argument('--branch',default='main')
    a=p.parse_args()
    inpath=Path(a.input).resolve(); outpath=Path(a.output).resolve()
    if inpath==outpath: p.error('必须指定不同的输出文件，避免覆盖原配置')
    text=inpath.read_text(encoding='utf-8-sig')
    out=replace(text,a.user,a.repo,a.branch)
    outpath.write_text(out,encoding='utf-8')
    print(f'已生成本地私有配置：{outpath}')
    print('请勿将生成的.conf文件上传到公开GitHub仓库。')

if __name__=='__main__':main()
