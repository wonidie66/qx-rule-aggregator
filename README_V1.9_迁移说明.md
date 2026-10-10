# Quantumult X V1.9：策略命名规范化和规则扩充（并行测试）

**重要：此包仅用于扩展现有公开仓库，不要将包含 MITM 私钥的完整配置上传到 GitHub。**

## 迁移原则

- 保留稳定版本 `sources.json`、`rules/BeforeTikTok.list`、`rules/AfterTikTok.list` 与 `update-rules.yml`，继续支持 V1.8。
- 新规则独立使用 `sources_v19.json` 和 `rules/v1.9/`，可随时回退。
- 正式启用 V1.9 前，需要在 GitHub Actions 中运行 `更新 Quantumult X V1.9 分类规则（测试）`，确认文件生成与审计通过。
- 本次不改变广告完整规则、资源解析器、原 MITM 证书、自动优选容差100ms、低频检测参数。
- TikTok 继续单独引用 Semporia 项目，默认不启用旧式 MITM 换区重写。
- 与先前 V1.8 对比，规则来源从74份增加到83份；新增：CSDN, BaiDuTieBa, SFExpress, Himalaya, Huawei, HuYa, JueJin, Wikipedia, LinkedIn。

## 需上传到你的 qx-rule-aggregator 仓库的文件

```
.github/workflows/update-v19.yml        # 新增：仅手动触发的V1.9工作流
sources_v19.json                        # 新增：不影响旧版规则源清单
config/policies_v19.json                # 新增：V1.9允许的策略组
scripts/audit_rules.py                  # 替换：保持旧版默认，新增版本目录及报告标题参数
scripts/aggregate.py                    # 替换：保持旧版默认，新增版本号参数
tests/test_v19_pipeline.py              # 新增：迁移校验
templates/QuantumultX_V1.9_无证书模板.conf # 可选上传：公开模板无私钥
```

**不要上传私人版 `.conf` 文件。**

## 启用步骤

1. 先备份手机上已验证的 V1.8 配置及 GitHub 仓库当前内容。
2. 将上述6个关键文件上传到 `main`，注意保留 `.github/workflows/` 完整路径。
3. 打开 GitHub Actions，运行 `更新 Quantumult X V1.9 分类规则（测试）`，首次不要勾选人工批准变更。
4. 检查 `rules/v1.9/BeforeTikTok.list`、`rules/v1.9/AfterTikTok.list` 和 `reports/v1.9/audit.md` 已生成。
5. 使用单独下载的**私人版完整配置**测试，先填入个人订阅地址；不要直接覆盖旧 V1.8 配置。
6. 检查手动节点组、AI、TikTok、抖音、广告与国内直连，然后再测新增国际社交/开发/云办公策略。
7. 如发现分流异常，切回 V1.8；原有仓库规则文件未被覆盖。

## 命名体系

- `节点-`：选择节点或故障备用。
- `地区-`：按国家地区选择节点。
- `分流-`：按服务类别分配出口。

国内常用 App 仍使用 `direct` 而不是新增无用策略组。

## 审计边界

- 审计脚本对 V1.9 使用各自版本目录的前一次发布内容作为基线。
- 仅能识别精确条件相同的策略变化和已列举的宽泛危险规则，不能完整识别子域名包含或 IP 网段重叠。
- 首次发布没有 V1.9 旧版基线，会生成提醒；务必检查结果后才迁移。
- 此版暂不自动定时发布，在真机验收后再考虑给 V1.9 工作流添加定期触发。

## 注意

- 原有稳定工作流自动更新也可能在不同时间修改仓库，V1.9 工作流发布时会尝试安全同步最新 `main`。
- 不使用 `git push --force`。
- 规则聚合源可能包含 GPL 许可内容，仓库需按上游许可提供相应授权与来源说明。
