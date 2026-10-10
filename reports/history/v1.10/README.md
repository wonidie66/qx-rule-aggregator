# V1.10 发布历史与基线

本目录用来长期保存**每次发生实质变动并成功提交**的 V1.10 规则与审计更新记录。此功能从 V1.10.2 的仓库整理版本开始启用，**不伪造此前每次运行的独立快照**。

## 启用前的已发布基线（2026-10-10）

| 指标 | 仓库已发布数据 |
|---|---:|
| 来源文件数 | 105 |
| 聚合规则条数 | 22019 |
| 精确条件跨策略重叠 | 539 |
| 域名覆盖候选对 | 1701 |
| IP 网段覆盖候选对 | 82 |
| 前段规则 SHA256 | `32eb3327c3424e8a80f53356ccd5daf9b0b168957bfdf290318f533f1942ff45` |
| 后段规则 SHA256 | `cac056952e3db5fe2eee9857a2a1e31ef25ac5539c2cfef8406417c2b3c33a04` |

目前完整的 [规则报告](../../v1.10/README.md)、[审计报告](../../v1.10/audit.md)、[优先级审核](../../v1.10/priority_audit.md) 均已保留在仓库。

### 此前已确认的成功运行

- [Actions 稳定更新，2026-10-10 07:44 UTC](https://github.com/wonidie66/qx-rule-aggregator/actions/runs/38035473494)
- [Actions 稳定更新，2026-10-10 07:49 UTC](https://github.com/wonidie66/qx-rule-aggregator/actions/runs/38035732783)
- [Actions 稳定更新，2026-10-10 07:50 UTC](https://github.com/wonidie66/qx-rule-aggregator/actions/runs/38035803318)

上述是**运行记录，不代表每次都改变了规则**；具体历史规则与文件变化可通过 [Git 提交历史](https://github.com/wonidie66/qx-rule-aggregator/commits/main/) 追溯。

## 今后如何保存

- 新增 `updates.md`：更新索引；不会每次空运行都追加。
- 新增 `runs/run-<GitHub Run ID>.md`：逐次 Markdown 快照；包括时间、Actions 运行链接、规则总数、前后段 SHA256、变更文件及报告摘要。
- 快照在成功执行发布前安全审计后，与当前规则及报告**同一个 Git 提交**上传。推送失败则历史文件也不会进入 `main`。
- 需要回溯完整规则内容时，以 Git 提交历史为准；不要依赖仅保留7天的 Actions Artifact。

旧版本（V1.8 和 V1.9）规则及报告在各自原目录长期保留，见 [版本维护索引](../../../docs/版本与维护索引.md)。
