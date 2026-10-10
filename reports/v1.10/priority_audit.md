# V1.10.2 潜在覆盖与优先级复核

- 域名跨策略候选：1701对
- IP跨策略候选：82对
- P1人工复核候选：601对
- P2观察候选：1182对
- 去重后候选规则对：1783对

## 人工复核样例（前30条）

| 级别 | 关系 | A规则及策略 | B规则及策略 |
|---|---|---|---|
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST,download.microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST,ntservicepack.microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST-SUFFIX,dl.delivery.mp.microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST-SUFFIX,microsoftonline.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST-SUFFIX,s-microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST-SUFFIX,update.microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → 分流-微软服务 | HOST-SUFFIX,windowsupdate.microsoft.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,weibo → direct | HOST-SUFFIX,freechinaweibo.com → 分流-海外通用 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,weibo → direct | HOST-SUFFIX,freeweibo.com → 分流-海外通用 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,weibo → direct | HOST-SUFFIX,weiboleak.com → 分流-海外通用 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,weibo → direct | HOST-SUFFIX,whatsonweibo.com → 分流-海外通用 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,avtb → 分流-海外通用 | HOST-SUFFIX,eqoavtbu.com → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,porn → 分流-海外通用 | HOST-SUFFIX,empornium.me → direct |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,aliyun → direct | HOST-SUFFIX,github-avatars.oss-cn-hongkong.aliyuncs.com → 分流-开发平台 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,aliyun → direct | HOST-SUFFIX,gitlab-assets.oss-cn-hongkong.aliyuncs.com → 分流-开发平台 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,baidu → direct | HOST-SUFFIX,baidu.jp → 分流-海外通用 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,copilot.microsoft.com → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,gateway.bingviz.microsoft.net → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,gateway.bingviz.microsoftapp.net → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,location.microsoft.com → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,self.events.data.microsoft.com → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST-SUFFIX,api.microsoftapp.net → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST-SUFFIX,bing-shopping.microsoft-falcon.io → 分流-AI服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,bg.v4.a.dl.ws.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,bg4.v4.a.dl.ws.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,developer.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,docs.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,download.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,download.visualstudio.microsoft.com → 分流-微软服务 |
| P1-人工复核 | 关键词/域名 | HOST-KEYWORD,microsoft → direct | HOST,fs.microsoft.com → 分流-微软服务 |

## 优先人工复核：文件顺序中直连先于专项代理的域名覆盖

- 此类候选：18对（文件顺序，不是实际客户端命中顺序）

| 直连规则 | 随后的代理规则 | 代理策略 | 来源 |
|---|---|---|---|
| HOST,csgo.wmsj.cn | HOST-SUFFIX,csgo.wmsj.cn | 分流-游戏平台 | SteamCN → Steam |
| HOST,dl.steam.clngaa.com | HOST-SUFFIX,dl.steam.clngaa.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,dl.steam.ksyna.com | HOST-SUFFIX,dl.steam.ksyna.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,dota2.wmsj.cn | HOST-SUFFIX,dota2.wmsj.cn | 分流-游戏平台 | SteamCN → Steam |
| HOST,st.dl.bscstorage.net | HOST-SUFFIX,st.dl.bscstorage.net | 分流-游戏平台 | SteamCN → Steam |
| HOST,st.dl.eccdnx.com | HOST-SUFFIX,st.dl.eccdnx.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,st.dl.pinyuncloud.com | HOST-SUFFIX,st.dl.pinyuncloud.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,steampipe.steamcontent.tnkjmec.com | HOST-SUFFIX,steamcontent.tnkjmec.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,steampowered.com.8686c.com | HOST-SUFFIX,steampowered.com.8686c.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,steamstatic.com.8686c.com | HOST-SUFFIX,steamstatic.com.8686c.com | 分流-游戏平台 | SteamCN → Steam |
| HOST,wmsjsteam.com | HOST-SUFFIX,wmsjsteam.com | 分流-游戏平台 | SteamCN → Steam |
| HOST-SUFFIX,cm.steampowered.com | HOST-SUFFIX,steampowered.com | 分流-游戏平台 | SteamCN → Steam |
| HOST-SUFFIX,steamchina.com | HOST-SUFFIX,cdn-ali.content.steamchina.com | 分流-游戏平台 | SteamCN → Steam |
| HOST-SUFFIX,steamchina.com | HOST-SUFFIX,cdn-qc.content.steamchina.com | 分流-游戏平台 | SteamCN → Steam |
| HOST-SUFFIX,steamchina.com | HOST-SUFFIX,cdn-ws.content.steamchina.com | 分流-游戏平台 | SteamCN → Steam |
| HOST-SUFFIX,in.th | HOST-SUFFIX,bx.in.th | 分流-海外通用 | 腾讯全家桶直连 → Proxy |
| HOST-SUFFIX,qcloud.com | HOST-SUFFIX,shortconn.im.qcloud.com | 分流-海外通用 | 腾讯全家桶直连 → Proxy |
| HOST-SUFFIX,mi.com | HOST-SUFFIX,c.mi.com | 分流-海外通用 | 小米 → Proxy |

以上关系不代表错误；如SteamCN在Steam代理规则前，可能是有意设置的国内CDN直连例外。

## 分析边界

- 仅静态候选，不代表Quantumult X真实规则命中或匹配优化优先级。
- 不包含前置Advertising、独立TikTok、用户本地规则；关键词及通配符只检查已列域名样例。
- 仅标注人工复核优先级，不自动删改规则，不增加发布阻断条件。
- 完整来源及行号参见CSV；IP包含可能是共享CDN的正常现象。
