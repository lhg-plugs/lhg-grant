#!/usr/bin/env python3
"""lhg-grant 申请书自查审计脚本：缺项 / 关键词 / 预算科目错配 / 超限 / 格式规范。

申请书目录约定：
    grant/
    ├── grant.yaml            # 可选（项目名称/资助机构/budget_limit 申请金额上限）
    ├── application/
    │   ├── 01-abstract.md    # 摘要（含关键词）
    │   ├── 02-basis.md       # 立项依据
    │   ├── 03-content.md     # 研究内容
    │   ├── 04-innovation.md # 创新点（独立成节）
    │   ├── 05-route.md       # 技术路线
    │   ├── 06-feasibility.md # 可行性分析（含风险预案）
    │   └── 07-budget.md     # 预算表（markdown 表格：科目|金额|说明）
    └── references.md         # 可选

用法：
    python3 grant_audit.py --target <申请书目录> [--format json|text]
退出码：有 blocker → 1；否则 → 0。纯 Python 标准库，零第三方依赖。
"""

import argparse
import json
import os
import re
import sys

REQUIRED_FILES = [
    ("01-abstract.md", "摘要"),
    ("02-basis.md", "立项依据"),
    ("03-content.md", "研究内容"),
    ("04-innovation.md", "创新点"),
    ("05-route.md", "技术路线"),
    ("06-feasibility.md", "可行性分析"),
    ("07-budget.md", "预算表"),
]

# 预算科目白名单（通用口径，具体以当年申报通知为准）
SUBJECTS = {
    "设备费", "材料费", "测试化验加工费", "燃料动力费",
    "差旅费", "会议费", "国际合作与交流费",
    "出版/文献/信息传播/知识产权事务费",
    "出版文献信息传播知识产权事务费",
    "劳务费", "专家咨询费", "间接费用", "管理费",
    "人员费", "绩效支出",
}

CITE_RE = re.compile(r"\[@[^\]]+\]|\[[1-9]\d*\]")
BUDGET_ROW_RE = re.compile(r"^\s*\|([^|]*)\|([^|]*)\|")


def F(rule_id, severity, title, file, detail):
    return {"rule_id": rule_id, "severity": severity, "title": title,
            "file": file, "detail": detail}


def tok_count(text):
    return len(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", text))


def norm_subject(s):
    s = s.strip().replace(" ", "").replace("／", "/").replace("、", "/")
    return s


class Ctx:
    def __init__(self, target):
        self.target = target
        self.app_dir = os.path.join(target, "application")
        self.files = {}   # relpath -> text
        if os.path.isdir(self.app_dir):
            for fn in sorted(os.listdir(self.app_dir)):
                if fn.lower().endswith((".md", ".markdown")):
                    p = os.path.join(self.app_dir, fn)
                    try:
                        with open(p, encoding="utf-8") as f:
                            self.files["application/" + fn] = f.read()
                    except Exception:
                        pass
        self.yaml = {}
        yp = os.path.join(target, "grant.yaml")
        if os.path.isfile(yp):
            try:
                with open(yp, encoding="utf-8") as f:
                    for ln in f:
                        m = re.match(r"^\s*([A-Za-z_]+|[\u4e00-\u9fff]+)\s*:\s*(.+?)\s*$", ln)
                        if m:
                            v = m.group(2).strip().strip('"').strip("'")
                            self.yaml[m.group(1)] = v
            except Exception:
                pass

    def get(self, fname):
        return self.files.get("application/" + fname, "")


# ---------------------------------------------------------------- 规则
def r_sections(ctx):
    missing = []
    for fname, label in REQUIRED_FILES:
        text = ctx.get(fname)
        if tok_count(text) < 50:
            missing.append(label)
    if missing:
        return [F("GT-SEC-001", "blocker", "申请书缺项", "application/",
                   "以下部分缺失或近乎空白：%s" % "、".join(missing))]
    return []


def r_keywords(ctx):
    text = ctx.get("01-abstract.md")
    if tok_count(text) < 50:
        return []
    if not re.search(r"关键词|key\s*words?", text, re.I):
        return [F("GT-KW-001", "warning", "摘要缺关键词", "application/01-abstract.md",
                   "摘要未给出关键词行（格式如：关键词：A；B；C）")]
    return []


def parse_budget(ctx):
    """解析 07-budget.md 的表格行 → [(科目, 金额, 行号)]。"""
    text = ctx.get("07-budget.md")
    rows = []
    for i, ln in enumerate(text.split("\n")):
        m = BUDGET_ROW_RE.match(ln)
        if not m:
            continue
        subj = m.group(1).strip()
        amt_raw = re.sub(r"[^0-9.]", "", m.group(2))
        if re.search(r"科目|金额|---", subj + m.group(2)):
            continue
        if "合计" in subj:
            continue
        try:
            amt = float(amt_raw) if amt_raw else 0.0
        except ValueError:
            amt = 0.0
        rows.append((subj, amt, i + 1))
    return rows


def r_budget_subject(ctx):
    findings = []
    for subj, amt, lineno in parse_budget(ctx):
        if not subj:
            continue
        if norm_subject(subj) not in {norm_subject(s) for s in SUBJECTS}:
            findings.append(F("GT-BDG-001", "blocker", "预算科目错配",
                              "application/07-budget.md",
                              "第 %d 行科目“%s”不在白名单内，请改用标准科目名" % (lineno, subj)))
    return findings[:10]


def r_budget_limit(ctx):
    limit_raw = ctx.yaml.get("budget_limit", "")
    try:
        limit = float(re.sub(r"[^0-9.]", "", str(limit_raw)))
    except ValueError:
        limit = 0
    if not limit:
        return []
    total = sum(amt for _, amt, _ in parse_budget(ctx))
    if total > limit:
        return [F("GT-BDG-002", "blocker", "预算超限预警",
                   "application/07-budget.md",
                   "预算总额 %.0f 元超过 grant.yaml 上限 %.0f 元（超 %.0f 元）"
                   % (total, limit, total - limit))]
    return []


def r_budget_total_row(ctx):
    text = ctx.get("07-budget.md")
    if tok_count(text) < 50:
        return []
    if "合计" not in text:
        return [F("GT-BDG-003", "warning", "预算表缺合计行",
                   "application/07-budget.md", "预算表缺少“合计”行，请补充并核对加总")]
    return []


def r_basis_cite(ctx):
    text = ctx.get("02-basis.md")
    if tok_count(text) < 50:
        return []
    if not CITE_RE.search(text):
        return [F("GT-FMT-001", "warning", "立项依据无引用",
                   "application/02-basis.md",
                   "立项依据未发现引用标记，现状与局限的每条论断都应跟引用")]
    return []


def r_innovation_thin(ctx):
    text = ctx.get("04-innovation.md")
    if tok_count(text) < 50:
        return []
    n = tok_count(text)
    if n < 120:
        return [F("GT-INN-001", "warning", "创新点表述空泛",
                   "application/04-innovation.md",
                   "创新点章节仅约 %d 词，疑似空话堆砌，请按“陈述+证据”格式充实" % n)]
    return []


def r_feasibility_risk(ctx):
    text = ctx.get("06-feasibility.md")
    if tok_count(text) < 50:
        return []
    if not re.search(r"风险|备选|预案|不确定", text):
        return [F("GT-RVW-001", "warning", "可行性缺风险预案",
                   "application/06-feasibility.md",
                   "可行性分析未提及风险与备选方案，评审会质疑可信度")]
    return []


RULES = [
    ("GT-SEC-001", "申请书缺项", "blocker", r_sections),
    ("GT-KW-001", "摘要缺关键词", "warning", r_keywords),
    ("GT-BDG-001", "预算科目错配", "blocker", r_budget_subject),
    ("GT-BDG-002", "预算超限预警", "blocker", r_budget_limit),
    ("GT-BDG-003", "预算表缺合计行", "warning", r_budget_total_row),
    ("GT-FMT-001", "立项依据无引用", "warning", r_basis_cite),
    ("GT-INN-001", "创新点表述空泛", "warning", r_innovation_thin),
    ("GT-RVW-001", "可行性缺风险预案", "warning", r_feasibility_risk),
]


def is_grant_dir(d):
    if os.path.isfile(os.path.join(d, "grant.yaml")):
        return True
    app = os.path.join(d, "application")
    if os.path.isdir(app):
        return any(fn.startswith("01-") for fn in os.listdir(app))
    return False


def audit(target):
    ctx = Ctx(target)
    findings = []
    for rule_id, title, severity, fn in RULES:
        try:
            findings.extend(fn(ctx) or [])
        except Exception as e:
            findings.append(F(rule_id, "warning", title + "（规则执行异常）",
                              target, str(e)[:120]))
    summary = {"rules_run": len(RULES),
               "blocker": sum(1 for f in findings if f["severity"] == "blocker"),
               "warning": sum(1 for f in findings if f["severity"] == "warning"),
               "files_checked": len(ctx.files)}
    return {"summary": summary, "findings": findings}


def main():
    ap = argparse.ArgumentParser(description="lhg-grant 申请书自查审计")
    ap.add_argument("--target", required=True, help="申请书目录")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    args = ap.parse_args()

    if not os.path.isdir(args.target):
        print("目标目录不存在：%s" % args.target, file=sys.stderr)
        return 2

    result = audit(args.target)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["summary"]
        print("lhg-grant 审计报告：%s" % args.target)
        print("规则 %d 条 | blocker %d | warning %d | 文件 %d" %
              (s["rules_run"], s["blocker"], s["warning"], s["files_checked"]))
        print("-" * 60)
        for f in result["findings"]:
            mark = "⛔" if f["severity"] == "blocker" else "⚠️"
            print("%s [%s][%s] %s\n    %s" %
                  (mark, f["severity"], f["rule_id"], f["title"], f["detail"]))
        if not result["findings"]:
            print("✅ 未发现问题，可以进入评审模拟。")
    return 1 if result["summary"]["blocker"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
