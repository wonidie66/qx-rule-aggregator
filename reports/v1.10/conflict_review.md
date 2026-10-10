# V1.10 规则重叠分类与人工复核报告

- 当前规则：22019 条，上游来源：105 份
- 跨策略重叠记录：539 条
- 独立精确选择器：530 个

- 直连与代理重叠：94
- 拦截与放行重叠：0
- 不同代理策略重叠：445
- 同策略重复（报告异常）：0

## 重叠最多的来源组合

| 优先来源 → 后续来源 | 策略方向 | 重叠记录 |
|---|---|---:|
| Scholar → China | 分流-学术科研 → direct | 58 |
| Facebook → Proxy | 分流-国际社交 → 分流-海外通用 | 42 |
| Microsoft → Xbox | 分流-微软服务 → 分流-游戏平台 | 37 |
| Microsoft → Proxy | 分流-微软服务 → 分流-海外通用 | 33 |
| Developer → Apple | 分流-海外通用 → 分流-苹果服务 | 26 |
| Telegram → Proxy | 分流-国际社交 → 分流-海外通用 | 23 |
| Amazon → Proxy | 分流-跨境购物 → 分流-海外通用 | 22 |
| Microsoft → China | 分流-微软服务 → direct | 21 |
| Pinterest → Proxy | 分流-国际社交 → 分流-海外通用 | 21 |
| Twitter → Proxy | 分流-国际社交 → 分流-海外通用 | 21 |
| LINE → Proxy | 分流-国际社交 → 分流-海外通用 | 20 |
| GitHub → Proxy | 分流-开发平台 → 分流-海外通用 | 19 |
| Dropbox → Proxy | 分流-云办公 → 分流-海外通用 | 16 |
| YouTube → Proxy | 分流-视频直播 → 分流-海外通用 | 13 |
| Wikipedia → Proxy | 分流-学术科研 → 分流-海外通用 | 12 |
| Apple → Proxy | 分流-苹果服务 → 分流-海外通用 | 9 |
| Disney → Proxy | 分流-流媒体解锁 → 分流-海外通用 | 9 |
| PrimeVideo → Amazon | 分流-流媒体解锁 → 分流-跨境购物 | 9 |
| AppleTV → Apple | 分流-流媒体解锁 → 分流-苹果服务 | 8 |
| Netflix → Proxy | 分流-流媒体解锁 → 分流-海外通用 | 8 |
| Scholar → Proxy | 分流-学术科研 → 分流-海外通用 | 8 |
| Discord → Proxy | 分流-国际社交 → 分流-海外通用 | 7 |
| GoogleDrive → Google | 分流-云办公 → 分流-海外通用 | 6 |
| Steam → Proxy | 分流-游戏平台 → 分流-海外通用 | 6 |
| Apple → China | 分流-苹果服务 → direct | 5 |
| Copilot → Proxy | 分流-AI服务 → 分流-海外通用 | 5 |
| Docker → Proxy | 分流-开发平台 → 分流-海外通用 | 5 |
| PrimeVideo → Proxy | 分流-流媒体解锁 → 分流-海外通用 | 5 |
| Twitch → Proxy | 分流-视频直播 → 分流-海外通用 | 5 |
| Instagram → Proxy | 分流-国际社交 → 分流-海外通用 | 4 |

## 直连与代理交叉样例（最多60条）

| 选择器 | 优先策略 | 后续策略 | 来源 |
|---|---|---|---|
| HOST-SUFFIX,cnki.net | 分流-学术科研 | direct | Scholar → 中国知网 |
| HOST-SUFFIX,wanfangdata.com.cn | 分流-学术科研 | direct | Scholar → 万方数据 |
| HOST-SUFFIX,nintendoswitch.cn | direct | 分流-游戏平台 | 腾讯全家桶直连 → Nintendo |
| HOST-SUFFIX,nintendoswitch.com.cn | direct | 分流-游戏平台 | 腾讯全家桶直连 → Nintendo |
| HOST-SUFFIX,tap.io | direct | 分流-海外通用 | TapTap → Proxy |
| HOST-SUFFIX,taptap.tw | direct | 分流-海外通用 | TapTap → Proxy |
| HOST,download.microsoft.com | 分流-微软服务 | direct | Microsoft → China |
| HOST,steamcommunity-a.akamaihd.net | 分流-游戏平台 | direct | Steam → China |
| HOST-SUFFIX,aaplimg.com | 分流-苹果服务 | direct | Apple → China |
| HOST-SUFFIX,acm.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,acs.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,aiaa.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,aip.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,akadns.net | 分流-苹果服务 | direct | Apple → China |
| HOST-SUFFIX,ams.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,annualreviews.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,aps.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,ascelibrary.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,asm.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,asme.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,astm.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,beatsbydre.com | 分流-苹果服务 | direct | Apple → China |
| HOST-SUFFIX,bmj.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,cambridge.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,cas.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,clarivate.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,cqvip.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,ebscohost.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,emerald.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,engineeringvillage.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,hotmail.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,icevirtuallibrary.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,ieee.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,images-amazon.com | 分流-跨境购物 | direct | Amazon → China |
| HOST-SUFFIX,imf.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,iop.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,jamanetwork.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,jhu.edu | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,jstor.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,karger.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,libguides.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,madsrevolution.net | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,me.com | 分流-苹果服务 | direct | Apple → China |
| HOST-SUFFIX,microsoftonline.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,mpg.de | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,msauth.net | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,msecnd.net | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,msocdn.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,myilibrary.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,mzstatic.com | 分流-苹果服务 | direct | Apple → China |
| HOST-SUFFIX,nature.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,oecd-ilibrary.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,office.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,office.net | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,office365.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,onenote.net | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,osapublishing.org | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,oup.com | 分流-学术科研 | direct | Scholar → China |
| HOST-SUFFIX,outlook.com | 分流-微软服务 | direct | Microsoft → China |
| HOST-SUFFIX,ovid.com | 分流-学术科研 | direct | Scholar → China |

## 审计边界

- 按生成规则中的完全相同类型和匹配值统计，并非实际访问日志或域名匹配模拟
- 同一匹配项可以产生多条冲突记录；首选策略指聚合文件自身顺序，不涵盖前置 Advertising、独立 TikTok 及 filter_local
- 未检测不同 HOST/HOST-SUFFIX/KEYWORD、IP 网段的包含关系；不自动删除或调整任何规则
