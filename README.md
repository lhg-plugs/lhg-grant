<!-- About 简介（推送后填写到仓库 About 栏）：
基金申请助手：申请书框架→写作→评审模拟→预算表编制 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-grant
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, grant, funding, proposal -->

# lhg-grant：基金申请助手，申请书到预算表一次搞定

> ## 重要声明
>
> **评审偏好因资助机构而异**：国自然、科技部重点研发、省基金、企业横向的
> 评审侧重点各不相同。本插件给的是**通用底线框架**（立项依据/研究内容/
> 创新点/技术路线/可行性/预算），具体指南、限项、格式要求**以当年申报通知为准**。
>
> 本插件**内容仅供参考，不承诺中标率**。研究基础、代表作、预算必须真实，
> 虚构前期成果、夸大预算、冒用他人成果的请求一律拒绝。

> **一句话介绍**：给 AI 编程助手装上"基金申请流水线"——选题→申请书六件套框架→分节写作→评审视角模拟打分→预算表编制规范，8 条确定性审计规则，低频刚需一次搞定。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-grant
> /plugin install lhg-grant@lhg-plugs
> ```

## 它是什么

`lhg-grant` 是一个 Claude Code 插件（plugin 为主、skill 为辅），面向科研人的
低频刚需：一年写一两次申请书，每次都手生。本插件把申请书写作变成流水线——
框架、评审视角、预算规范一次配齐。

- **3 个命令**（小白入口）：`grant` 全流程（选题→框架→写作→评审自检→预算），
  `budget` 预算表编制专项，`review-sim` 评审模拟打分
- **3 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：
  申请书框架、预算科目规范、评审打分视角
- **3 个专家 agent**：申请书写作专家、评审模拟专家、预算核查专家
- **2 个 hooks**：提交/导出前审计拦截（硬门，可一键豁免）、写预算文件时
  非标准科目提醒（警告级）
- **8 条确定性审计规则**：纯 Python、零第三方依赖

## 3 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-grant:grant` | 选题→申请书框架→分节写作→评审自检→预算表，全流程 | `/lhg-grant:grant "小样本学习方法研究" "国自然面上"` |
| `/lhg-grant:budget` | 预算表编制：科目规范、错配排查、超限预警 | `/lhg-grant:budget ./my-grant` |
| `/lhg-grant:review-sim` | 评审模拟：四维打分+一票否决排查+修改清单 | `/lhg-grant:review-sim ./my-grant` |

## 目录结构

```
lhg-grant/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 3 个命令：grant / budget / review-sim
├── skills/                  # 3 个平台中立 skill（申请书框架/预算规范/评审视角）
├── agents/                  # 3 个专家 agent（grant-writer / reviewer-sim / budget-checker）
├── hooks/                   # 提交前审计拦截 + 预算科目提醒（均可一键关闭）
├── scripts/audit/           # 确定性审计：grant_audit.py（零第三方依赖）
├── fixtures/                # 好/坏申请书对照用例
├── smoke_test.py            # 冒烟测试
├── ATTRIBUTION.md           # 灵感来源声明
└── LICENSE                  # MIT
```

## 申请书目录约定

```
my-grant/
├── grant.yaml           # 项目名称/资助机构/申请金额上限（可选，有它 hook 识别更准）
├── application/
│   ├── 01-abstract.md   # 摘要（含关键词）
│   ├── 02-basis.md       # 立项依据
│   ├── 03-content.md     # 研究内容
│   ├── 04-innovation.md # 创新点（独立成节）
│   ├── 05-route.md       # 技术路线
│   ├── 06-feasibility.md # 可行性分析（含风险预案）
│   └── 07-budget.md     # 预算表（markdown 表格）
└── references.md        # 参考文献（可选）
```

## 什么时候用 / 什么时候不用（FAQ）

**Q：国自然和省基金的写法一样吗？**
A：**框架通用，侧重不同**。本插件给的是通用底线（六件套+预算规范），
具体到申报书模板、限项、字数、评审权重，**以当年申报通知为准**。
建议先把申报通知喂给 AI，再跑流程。

**Q：能保证中标吗？**
A：**不能，也不承诺**。本插件提高的是"不因缺项/预算错配/逻辑硬伤被毙"的概率，
科学问题本身的价值才是中标的决定因素，任何"包中"的说法都是不诚实的。

**Q：评审权重是你们定的吗？**
A：插件里用的是通用经验权重（立项依据 30/研究内容 30/创新点 20/研究基础 20），
**不代表任何机构的实际评审标准**，只用于定位短板。真实权重以各机构通知为准。

**Q：预算科目口径每年会变吗？**
A：会。各机构的科目口径、比例上限（如间接费用、绩效支出比例）每年可能调整，
编预算前务必核对当年申报通知的预算编制说明。审计脚本的白名单是通用口径。

**Q：一定要用 Claude Code 吗？**
A：`skills/` 下的方法论是平台中立的纯 Markdown，可直接搬到豆包、Workbuddy
等 agent 平台用。只有 commands/agents/hooks 需要 Claude Code。

## 自迭代

- 每个 skill 末尾有「自检与反馈」节：质检门 + 标准冒烟用例 + 一键提 issue。
- 发现规则误报/漏报、方法论不合理：到本仓库提 issue（标题带对应 skill 前缀，
  如 `[lhg-budget-plan]`），附资助机构与场景描述。

## 更多插件

lhg-plugs「小白专家插件」组织级索引（含全部插件矩阵）：
https://github.com/lhg-plugs/marketplace

## 出品：刘洪光

刘洪光（https://github.com/lhg-skills）出品，lhg-plugs「小白专家插件」系列之一。
灵感来源见 [ATTRIBUTION.md](./ATTRIBUTION.md)（借鉴思路，实现与文案均为原创）。
