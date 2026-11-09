<!-- About 简介（推送后填写到仓库 About 栏）：
基金申请助手：立项依据/研究内容/创新点/技术路线/可行性框架搭建、预算表编制规范、评审视角模拟自查，一套组合拳。声明：评审偏好因资助机构而异，内容仅供参考。 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-grant
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, grant, funding, proposal, budget, nsfc -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="lhg-grant — 基金申请助手">
</p>

> **一句话介绍**：基金申请助手：立项依据/研究内容/创新点/技术路线/可行性框架搭建、预算表编制规范、评审视角模拟自查，一套组合拳。声明：评审偏好因资助机构而异，内容仅供参考。

**一键安装**：在 Claude Code 里运行

```bash
/plugin marketplace add lhg-plugs/lhg-grant
/plugin install lhg-grant@lhg-plugs
```

## 它能帮你做出什么

- **冒烟全绿**：`python3 smoke_test.py` 45 项全部通过（JSON 合法、frontmatter 完整、命令/skill/agent 齐全）。

## 它是什么

`lhg-grant` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **3 个命令**（小白入口）：`budget` 预算表编制专项、`grant` 基金申请主流程、`review-sim` 评审模拟
- **3 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：lhg-budget-plan, lhg-grant-frame, lhg-reviewer-view
- **3 个专家 agent**：budget-checker, grant-writer, reviewer-sim
- **2 个 hooks**（`hooks/`：post_write_budget_warn.py, pre_submit_grant.py），关键操作前自动把关

## 为什么是它

不是一个 prompt，而是一套互相兜底的机制：

1. **硬门，不是提醒**：hooks 在关键操作前自动拦截或警告（见 `hooks/`），而不是只在文档里写一句"请注意"。
2. **方法论沉淀在 skill 里**：流程、检查清单、口径都写在 `skills/` 的方法论里，命令只是入口；换个 agent 平台也能复用同一套做法。
3. **可验，不是可信**：`fixtures/` 备有坏/好对照用例，`smoke_test.py` 一键验证，规则有没有生效、自己跑一遍就知道。

## 快速上手

```bash
# 1. 安装（Claude Code 里运行）
/plugin marketplace add lhg-plugs/lhg-grant
/plugin install lhg-grant@lhg-plugs

# 2. 基金申请主流程：选题→申请书框架→分节写作→评审视角自检→预算表编制，低频刚需一
/lhg-grant:grant "小样本学习方法研究" "国自然面上"
```

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-grant:budget` | 预算表编制专项：科目规范校验、常见错配排查、超限预警，预算与研究内容对齐。 | `/lhg-grant:budget ./my-grant` |
| `/lhg-grant:grant` | 基金申请主流程：选题→申请书框架→分节写作→评审视角自检→预算表编制，低频刚需一次搞定。 | `/lhg-grant:grant "小样本学习方法研究" "国自然面上"` |
| `/lhg-grant:review-sim` | 评审模拟：按立项依据/研究内容/创新点/研究基础四维打分，输出模拟评审意见与修改清单。 | `/lhg-grant:review-sim ./my-grant` |

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你需要预算表编制专项时 → 用 `/lhg-grant:budget`
- 你需要基金申请主流程时 → 用 `/lhg-grant:grant`
- 你需要评审模拟时 → 用 `/lhg-grant:review-sim`

**什么时候不用：**

- 你只需要其中一个零散能力时 → 本插件是成套流程，单点需求用更轻量的 skill 更合适
- 你希望 AI 完全自由发挥、不接受任何自查与硬门时 → 它的规则审计与 hooks 会介入（可关，但那就别装它）
- 本插件内容仅供参考，不承诺中标率。研究基础、代表作、预算必须真实，
- 你的场景不在上面命令表覆盖范围内时 → 先看命令表，没有对应命令就别硬套

## 目录结构

```
lhg-grant/
├── smoke_test.py          # 一键冒烟测试
├── ATTRIBUTION.md         # 灵感来源与许可声明
├── LICENSE                # MIT
├── README.md              # 本文件
├── .claude-plugin/
├── agents/
├── commands/
├── fixtures/
├── hooks/
├── scripts/
├── skills/
```

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（本次实测 45 项全部通过）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-grant/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

同门插件见 [lhg-plugs](https://github.com/lhg-plugs)，86 个插件的完整矩阵在 [marketplace](https://github.com/lhg-plugs/marketplace) 维护。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
