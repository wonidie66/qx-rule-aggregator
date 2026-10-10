# 聚合规则审计报告

- 上游规则源：83 份
- 原始规则条数：22683
- 完全重复并删除：1327
- 输出规则条数：21356
- 输出文件字节数：894064
- 相同匹配条件但策略不同：448 处

## 设计边界
- 保留全部不同策略的重复条件，按 V1.7 原先顺序排列，首个命中者的优先级不变。
- 除完全相同行外，不自动合并 HOST/后缀/关键词/IP 网段，避免误删例外。
- 同一域名被宽泛后缀/关键词覆盖的问题仍需在 Quantumult X 中实测。
- 不处理广告、Rewrite、节点、订阅凭据与 MITM 私钥。

## 来源明细

| 来源 | 策略 | 原始 | 保留 |
|---|---|---:|---:|
| OpenAI | 分流-AI服务 | 35 | 35 |
| Claude | 分流-AI服务 | 3 | 3 |
| Gemini | 分流-AI服务 | 13 | 13 |
| YouTube | 分流-视频直播 | 196 | 196 |
| Netflix | 分流-流媒体解锁 | 1158 | 1158 |
| Disney | 分流-流媒体解锁 | 174 | 174 |
| PrimeVideo | 分流-流媒体解锁 | 18 | 18 |
| HBOUSA | 分流-流媒体解锁 | 12 | 12 |
| Twitch | 分流-视频直播 | 21 | 21 |
| 抖音国内 | direct | 13 | 13 |
| Telegram | 分流-国际社交 | 40 | 40 |
| Twitter | 分流-国际社交 | 33 | 33 |
| Instagram | 分流-国际社交 | 4 | 4 |
| Reddit | 分流-国际社交 | 8 | 8 |
| Discord | 分流-国际社交 | 29 | 29 |
| Spotify | 分流-海外通用 | 30 | 30 |
| GitHub | 分流-开发平台 | 31 | 31 |
| GitLab | 分流-开发平台 | 6 | 6 |
| Developer | 分流-海外通用 | 70 | 70 |
| Scholar | 分流-学术科研 | 231 | 231 |
| GoogleDrive | 分流-云办公 | 8 | 8 |
| Google | 分流-海外通用 | 711 | 710 |
| AppleTV | 分流-流媒体解锁 | 9 | 9 |
| AppleMusic | 分流-苹果服务 | 10 | 10 |
| Apple | 分流-苹果服务 | 1881 | 1873 |
| Copilot | 分流-AI服务 | 51 | 20 |
| Microsoft | 分流-微软服务 | 712 | 712 |
| SteamCN | direct | 17 | 17 |
| Steam | 分流-游戏平台 | 62 | 62 |
| BiliBili国内 | direct | 127 | 127 |
| 百度国内 | direct | 251 | 251 |
| 微博国内 | direct | 4 | 4 |
| Notion | 分流-云办公 | 6 | 6 |
| Dropbox | 分流-云办公 | 17 | 17 |
| Pinterest | 分流-国际社交 | 23 | 23 |
| Facebook | 分流-国际社交 | 570 | 567 |
| GoogleVoice | 分流-海外通用 | 1 | 0 |
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
| Bing | 分流-微软服务 | 9 | 0 |
| OneDrive | 分流-微软服务 | 17 | 6 |
| Docker | 分流-开发平台 | 7 | 7 |
| Slack | 分流-云办公 | 11 | 11 |
| LINE | 分流-国际社交 | 24 | 23 |
| Pixiv | 分流-海外通用 | 8 | 8 |
| PayPal | 分流-海外通用 | 248 | 248 |
| Amazon | 分流-海外通用 | 209 | 209 |
| 12306 | direct | 15 | 15 |
| 滴滴出行 | direct | 25 | 25 |
| 饿了么 | direct | 13 | 13 |
| 豆瓣 | direct | 3 | 3 |
| 雪球 | direct | 11 | 11 |
| CSDN | direct | 22 | 22 |
| BaiDuTieBa | direct | 32 | 32 |
| SFExpress | direct | 20 | 20 |
| Himalaya | direct | 18 | 18 |
| Huawei | direct | 160 | 160 |
| HuYa | direct | 4 | 0 |
| JueJin | direct | 12 | 12 |
| Wikipedia | 分流-学术科研 | 12 | 12 |
| LinkedIn | 分流-国际社交 | 12 | 12 |
| Proxy | 分流-海外通用 | 7479 | 7035 |
| China | direct | 3753 | 2952 |

## 精确条件冲突

详细情况见 `conflicts.csv`，未进行自动策略覆盖。
