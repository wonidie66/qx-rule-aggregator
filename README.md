# Quantumult X 公开规则聚合与安全审计

本仓库的**当前维护版本为 V1.10 / V1.10.2**：105份公开规则源聚合为两份 Quantumult X 远程分流文件；独立保留上游 TikTok 专项分流与 Advertising 完整版。本仓库**不存放机场订阅、节点账号、MITM 私钥或任何私人配置**。

## 当前使用入口

| 用途 | 路径 |
|---|---|
| 规则源清单（105份） | [sources_v110.json](sources_v110.json) |
| 策略白名单 | [config/policies_v110.json](config/policies_v110.json) |
| 前段公开规则 | [rules/v1.10/BeforeTikTok.list](rules/v1.10/BeforeTikTok.list) |
| 后段公开规则 | [rules/v1.10/AfterTikTok.list](rules/v1.10/AfterTikTok.list) |
| V1.10 完整构建报告 | [reports/v1.10/README.md](reports/v1.10/README.md) |
| V1.10.2 覆盖审计 | [reports/v1.10/priority_audit.md](reports/v1.10/priority_audit.md) |
| 更新日志（追加记录） | [reports/history/v1.10/README.md](reports/history/v1.10/README.md)（历史基线与后续自动更新记录） |
| 历史版本与维护索引 | [docs/版本与维护索引.md](docs/版本与维护索引.md) |

## 自动更新与校验

- **稳定更新**：[.github/workflows/update-v110.yml](.github/workflows/update-v110.yml)：定时/手动执行、规则下载、分类审计、风险校验、发布与变更存档；出现高风险错误时拒绝覆盖已发布规则。
- **PR 回归测试**：[.github/workflows/validate-v110.yml](.github/workflows/validate-v110.yml)：测试源码/策略更改、静态分析和发布机制。
- 正常更新约每三个日历日执行一次，但不是严格72小时；没有内容变化时不创建无意义提交。
- 发布后 GitHub Actions 的运行历史可用于查看完整执行日志。长期保存的变更摘要会写入 `reports/history/v1.10/`；完整规则与报告的每次变更可通过 Git 提交历史追溯。

## 客户端注意事项

在手机中使用以下两个远程规则链接，并保留原有 Advertising 完整版及 Semporia TikTok 独立规则，**两份聚合文件不得添加 `force-policy`**，因为每条规则已有自己的策略字段。

```text
https://cdn.jsdelivr.net/gh/wonidie66/qx-rule-aggregator@main/rules/v1.10/BeforeTikTok.list
https://cdn.jsdelivr.net/gh/wonidie66/qx-rule-aggregator@main/rules/v1.10/AfterTikTok.list
```

手机策略组名称需与文件中的 `分流-*` 等名称一致。已有的私人节点与 MITM 证书应继续在手机原配置中维护，**不要提交到公开仓库**。

## 版本保留原则

- 旧版本：`rules/BeforeTikTok.list`（V1.8）、`rules/v1.9/` 及其 `reports/`、`sources*.json`、`config/policies*.json` 暂时保留，供回退与既有测试使用。
- 旧版聚合工作流不再自动执行，以免误更新已经退役的历史规则路径。
- 旧版程序、模板、测试与 Markdown 不删，以避免破坏历史测试和维护依据。
- 详情见 [历史索引](docs/版本与维护索引.md)。[V1.8 原版完整说明](docs/V1.8_原始仓库说明_完整存档.md)已存档，原始语义与配置示例完整保留。

## 安全说明

聚合依赖第三方公开规则，请遵守各上游源许可证；详情见 [LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md)。上游域名列表并不保证与 Quantumult X 在设备上的真实命中完全一致，`reports/v1.10/` 的风险分级只是人工复核线索，**不能自动视为故障证据**。
