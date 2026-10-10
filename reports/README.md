# 聚合规则审计报告

- 上游规则源：74 份
- 原始规则条数：22391
- 完全重复并删除：1453
- 输出规则条数：20938
- 输出文件字节数：783152
- 相同匹配条件但策略不同：238 处

## 设计边界
- 保留全部不同策略的重复条件，按 V1.7 原先顺序排列，首个命中者的优先级不变。
- 除完全相同行外，不自动合并 HOST/后缀/关键词/IP 网段，避免误删例外。
- 同一域名被宽泛后缀/关键词覆盖的问题仍需在 Quantumult X 中实测。
- 不处理广告、Rewrite、节点、订阅凭据与 MITM 私钥。

## 来源明细

| 来源 | 策略 | 原始 | 保留 |
|---|---|---:|---:|
| OpenAI | AI服务 | 35 | 35 |
| Claude | AI服务 | 3 | 3 |
| Gemini | AI服务 | 13 | 13 |
| YouTube | YouTube视频 | 196 | 196 |
| Netflix | 流媒体解锁 | 1158 | 1158 |
| Disney | 流媒体解锁 | 174 | 174 |
| PrimeVideo | 流媒体解锁 | 18 | 18 |
| HBOUSA | 流媒体解锁 | 12 | 12 |
| Twitch | YouTube视频 | 21 | 21 |
| 抖音国内 | direct | 13 | 13 |
| Telegram | 默认代理 | 40 | 40 |
| Twitter | 默认代理 | 33 | 33 |
| Instagram | 默认代理 | 4 | 4 |
| Reddit | 默认代理 | 8 | 8 |
| Discord | 默认代理 | 29 | 29 |
| Spotify | 默认代理 | 30 | 30 |
| GitHub | 默认代理 | 31 | 31 |
| GitLab | 默认代理 | 6 | 6 |
| Developer | 默认代理 | 70 | 68 |
| Scholar | 学术资源 | 231 | 231 |
| GoogleDrive | 默认代理 | 8 | 8 |
| Google | 默认代理 | 711 | 704 |
| AppleTV | 流媒体解锁 | 9 | 9 |
| AppleMusic | Apple服务 | 10 | 10 |
| Apple | Apple服务 | 1881 | 1873 |
| Copilot | AI服务 | 51 | 20 |
| Microsoft | Microsoft服务 | 712 | 712 |
| SteamCN | direct | 17 | 17 |
| Steam | 游戏服务 | 62 | 62 |
| BiliBili国内 | direct | 127 | 127 |
| 百度国内 | direct | 251 | 251 |
| 微博国内 | direct | 4 | 4 |
| Notion | 默认代理 | 6 | 6 |
| Dropbox | 默认代理 | 17 | 17 |
| Pinterest | 默认代理 | 23 | 23 |
| Facebook | 默认代理 | 570 | 567 |
| GoogleVoice | 默认代理 | 1 | 0 |
| 拼多多直连 | direct | 3 | 3 |
| 腾讯全家桶直连 | direct | 2523 | 2522 |
| 微信直连 | direct | 43 | 32 |
| 腾讯视频直连 | direct | 51 | 50 |
| 支付宝 | direct | 21 | 21 |
| 京东 | direct | 249 | 249 |
| 美团 | direct | 7 | 7 |
| 闲鱼 | direct | 16 | 16 |
| 中国银联 | direct | 16 | 16 |
| 小红书 | direct | 4 | 4 |
| 知乎 | direct | 7 | 7 |
| 快手 | direct | 678 | 678 |
| 爱奇艺 | direct | 62 | 62 |
| 优酷 | direct | 37 | 37 |
| 网易云音乐 | direct | 30 | 30 |
| 高德地图 | direct | 9 | 9 |
| 携程 | direct | 29 | 29 |
| 钉钉 | direct | 11 | 11 |
| 小米 | direct | 157 | 157 |
| 中国知网 | direct | 17 | 17 |
| 万方数据 | direct | 2 | 2 |
| Gitee | direct | 2 | 2 |
| Bing | Microsoft服务 | 9 | 0 |
| OneDrive | Microsoft服务 | 17 | 6 |
| Docker | 默认代理 | 7 | 5 |
| Slack | 默认代理 | 11 | 11 |
| LINE | 默认代理 | 24 | 23 |
| Pixiv | 默认代理 | 8 | 8 |
| PayPal | 默认代理 | 248 | 248 |
| Amazon | 默认代理 | 209 | 209 |
| 12306 | direct | 15 | 15 |
| 滴滴出行 | direct | 25 | 25 |
| 饿了么 | direct | 13 | 13 |
| 豆瓣 | direct | 3 | 3 |
| 雪球 | direct | 11 | 11 |
| Proxy | 默认代理 | 7479 | 6849 |
| China | direct | 3753 | 3018 |

## 精确条件冲突

详细情况见 `conflicts.csv`，未进行自动策略覆盖。
