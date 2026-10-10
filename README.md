# Quantumult X V1.8：自动聚合规则实验

本仓库用于对 **Quantumult X V1.7** 已经使用的公开分流规则进行自动获取、去重、冲突审计和发布。**不包含用户的机场订阅、节点密码、MITM 证书、Rewrite 私人数据。**

## 核心设计

- 原版：`75` 份非广告公开规则订阅，另有一份 Advertising 完整版。
- 试验版：`74` 份 blackmatrix7 等公开专项规则 → GitHub Actions 生成 `BeforeTikTok.list`（10份来源）和 `AfterTikTok.list`（64份来源）。
- TikTok 的 `Semporia/TikTok-Unlock` 规则**仍然独立引用原始地址**，不打包、转载或修改其内容。
- 广告完整版仍单独引用原始地址。
- 本来在 TikTok 前的规则继续在前，本来在后的继续在后；输出每条规则的第三字段为 V1.7 真实使用的策略名。
- 只删除一模一样的重复规则。不同策略对同一域名的匹配项都按原顺序保留，记录于 `reports/conflicts.csv`。
- 下载失败、规则格式不支持或单个聚合文件超出 18 MiB：构建直接报错，GitHub Actions 不提交这次生成物。

本项目的目标是**减少远程资源订阅条目、便于更新维护**，并非证明客户端匹配速度、耗电和内存会下降。V1.7 原有跨域名规则重叠问题也不会凭聚合自动解决。

## 1. 建立 GitHub 仓库

1. 在 GitHub 新建一个**公开**仓库，例如 `qx-rule-aggregator`，默认分支为 `main`。公开仅用于发布规则；不要上传任何个人配置。
2. 解压项目包，确认 `.github/workflows/update-rules.yml`、`sources.json`、`scripts/aggregate.py` 仍在原来的相对位置。
3. 推荐在文件夹中运行（Windows Terminal / Git Bash 均可）：

```bash
git init -b main
git add .
git commit -m "init: qx rules aggregation"
git remote add origin https://github.com/你的用户名/qx-rule-aggregator.git
git push -u origin main
```

如创建仓库时勾选了初始化 README，应先 `git clone` 再将文件复制进仓库，避免历史分叉。也可以通过 GitHub 网页 Upload files 上传解压后的内容，需确保隐藏的 `.github` 工作流目录没有遗漏。

## 2. 首次运行自动构建

进入仓库 **Actions → 更新 Quantumult X 聚合规则 → Run workflow**。首次运行会连接外部规则源并生成：

```text
rules/BeforeTikTok.list
rules/AfterTikTok.list
reports/README.md
reports/summary.json
reports/conflicts.csv
```

检查工作流状态为绿色成功，以及两个 `.list` 文件包含真实规则。以后工作流按 Cron 自动执行，也可以随时手动运行。默认约每3个日历日检查一次；由于 Cron 的 `*/3` 按每月日期计数，间隔并不严格等于72小时。

如果提示 GitHub Actions 没有推送权限，在 **Settings → Actions → General → Workflow permissions** 检查写权限，并确认仓库/组织是否允许工作流写入。若组织限制无法调整，需将发布方案改为专用分支或人工发布。

## 3. 在 Quantumult X 中使用

**先等 GitHub Actions 首次成功，再替换 Quantumult X 中的 `[filter_remote]`。** 推荐先备份设备上已经稳定的 V1.7。仅将该段改为下方结构：

```ini
[filter_remote]
# 广告完整版本：保留原有拒绝策略
https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/QuantumultX/Advertising/Advertising.list, tag=广告域名-完整版, force-policy=reject, update-interval=604800, opt-parser=false, enabled=true

# TikTok 之前的规则
https://cdn.jsdelivr.net/gh/你的用户名/qx-rule-aggregator@main/rules/BeforeTikTok.list, tag=V1.8-前段分流, update-interval=259200, opt-parser=false, enabled=true

# TikTok 原项目独立订阅，保留 V1.7 的策略及优先位置
https://cdn.jsdelivr.net/gh/Semporia/TikTok-Unlock@master/Quantumult-X/TikTok.list, tag=TikTok专项分流-Semporia, force-policy=TikTok服务, update-interval=604800, opt-parser=false, enabled=true

# TikTok 之后的规则
https://cdn.jsdelivr.net/gh/你的用户名/qx-rule-aggregator@main/rules/AfterTikTok.list, tag=V1.8-后段分流, update-interval=259200, opt-parser=false, enabled=true

# 原有内置局域网规则
FILTER_LAN, tag=局域网, force-policy=direct, inserted-resource=true, enabled=true
```

**两条自建聚合规则不能添加 `force-policy`**：因为文件内每条规则已指定具体策略，强制覆盖会造成所有业务误分流。`[policy]`、`[filter_local]`、`[rewrite_remote]`、`[mitm]`、`[server_remote]` 一律沿用手机上的 V1.7 配置。

本项目提供仅供**本地电脑**运行的替换程序：

```bash
python scripts/local_replace.py \
  --input "QuantumultX_V1.7_私人配置.conf" \
  --output "QuantumultX_V1.8_私人测试.conf" \
  --user 你的用户名 --repo qx-rule-aggregator
```

Windows PowerShell 可以将整条命令写成一行，避免反斜线续行不兼容。该程序不上传数据，输入与输出不能使用同一文件，仍须检查生成后的 `[filter_remote]` 段是否正确。

**禁止把上述私人输入或输出配置提交到 GitHub。**

## 4. 实测与回退

依次验证以下项目的实际活动日志和 App 使用情况：微信/拼多多/腾讯；抖音/TikTok；ChatGPT、Gemini；Google、Microsoft；YouTube/Netflix；Steam 国区；GitHub；普通海外网页。同时观察广告拦截是否仍然正常。

如果出现某些服务分流错误：保留日志截图，立即切回 V1.7；分析报告中的重叠规则与上游更新时间，再决定修改 `sources.json`。不应盲目将 `ChinaMaxNoMedia`、`Global` 等大型合集加入已有规则里。

## 5. 后续增加规则

修改 `sources.json`，按照希望的优先顺序把源插在 `前段` 或 `后段`（必须所有 `前段` 都排在 `后段` 之前）。每个源示例：

```json
{
  "tag": "示例软件",
  "url": "https://cdn.jsdelivr.net/gh/公开仓库/分支/路径/Example.list",
  "policy": "默认代理",
  "segment": "后段"
}
```

目前只允许 jsDelivr 或 `raw.githubusercontent.com` 的公开 HTTPS 地址。必须是真正的 Quantumult X 原生分流规则，不得混入 URL Rewrite / JavaScript / 节点配置。

## 6. 测试与局限

```bash
python -m unittest discover -s tests -v
python scripts/aggregate.py --manifest sources.json --out-dir rules --report reports
```

第一条不联网；第二条需下载所有上游源。本试验包已经通过离线单元测试，**尚未完成 GitHub Actions 实际运行，也没有完成 Quantumult X 真机聚合规则命中测试**。当前工作环境不能直接联网下载 jsDelivr 原始资源，正式两份 `.list` 须由仓库工作流生成。

## 7. 开源许可证与安全

blackmatrix7/ios_rule_script 仓库声明 GPL-2.0。聚合生成的规则属于来源于该项目的衍生组合，公开发布时应遵守 GPL-2.0 的要求并保留上游来源及许可证。本项目附带 `LICENSE` 及 `NOTICE.md`，但如有其他第三方源，仍需逐项检查许可证。

Semporia/TikTok-Unlock 未提供明确的 GitHub 许可证声明，所以本项目**不重新发布其文件**；Quantumult X 直接引用其上游 URL。这样不会改变你已验证可用的 TikTok 解锁策略。

`.gitignore` 仅提供额外防护，不能替代人工保密检查。不要把机场订阅令牌、节点密钥、MITM 私钥、私人配置、访问令牌或 Cookie 加入仓库。

---

## V1.8.1：已验证版本的自动更新安全保护（2026-10-10）

你已在设备上验证 V1.8 的六项日常测试均通过。V1.8.1 **不会改变** `rules/BeforeTikTok.list`、`rules/AfterTikTok.list`、TikTok 分流、广告规则、Quantumult X 手机配置或 MITM；只增强 GitHub Actions 的发布前检查。

### 需要新增或覆盖的文件

- 覆盖 `.github/workflows/update-rules.yml`：聚合成功之后执行发布审计，失败时不提交，并保存审计报告为 Actions Artifact。
- 新增 `scripts/audit_rules.py`：检测 SHA256、文件大小、策略组名称、前后版本规则规模及首选策略变化。
- 新增 `config/policies.json`：列出 V1.8 中有效的策略名称（不含节点和个人配置）。
- 新增 `tests/test_audit_rules.py`：回归测试和故障场景测试。

其他所有文件都可以不修改，特别是 `sources.json`、`scripts/aggregate.py` 和两份已发布规则文件。

### GitHub 网页升级步骤

1. 打开仓库的 **Code** 页面，选择 `main` 分支。
2. 将上述4个文件按照**原目录结构**上传或更新。其中 `.github/workflows/update-rules.yml` 可以通过 **Add file → Create new file** 创建（Windows 可能隐藏以 `.` 开头的目录）。
3. 打开 **Actions → 更新 Quantumult X 聚合规则 → Run workflow**，首次测试保持 `approve_routing_changes=false`。
4. 当工作流成功且出现 `reports/audit.md`，说明安全审计已接入。
5. 如果工作流失败，打开运行页面查看「保留本次报告供失败排查」步骤的 Artifact 下载并阅读 `reports/audit.md`；**切勿因为更新失败而删除手机里的旧规则**。

### 如何处理未来的自动更新告警

- `策略组未定义`、文件哈希错误、首次引入覆盖几乎全部流量的规则：应先修复源代码或上游引用，不提供一键放行。
- 规则条数变化超过 ±15%、同一匹配条件的首选策略发生变化：默认阻止发布。先阅读 Actions Artifact 的 `reports/audit.md` 和 `reports/conflicts.csv`，核验路由意图后，手动运行时才勾选 `approve_routing_changes`。
- 目前已有的 238 处精确条件跨策略重叠**不会自动删除**，仍保留现有顺序。未来新出现的“后缀包含”、“关键词重叠”和 IP 范围重叠尚不能全部自动判别。

### 重要限制

- 自动更新的 GitHub Actions Cron `17 3 */3 * *` 不是严格每72小时，而是按每月的第1、4、7……天执行。
- 远程 CDN 分支资源可能有缓存延迟；校验确保**本次生成文件与本次报告一致**，并不保证同一时刻所有上游资源处于相同版本。
- 这些是代码与构建层的安全检查，不代表真实访问速度、广告拦截率或各服务解锁能力的证明。
- 仓库只包含公开规则源。不要向仓库提交 MITM 私钥、密码、机场订阅链接或其他个人凭据。
