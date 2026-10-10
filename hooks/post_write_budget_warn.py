#!/usr/bin/env python3
"""lhg-grant 警告级 hook：写预算文件时，若科目不在白名单内，提醒修正。

触发：PostToolUse / Write|Edit。只看文件名含 budget/预算 的 markdown 文件。
检查：表格中的科目列，对照科目白名单（与 grant_audit.py 共用同一口径）。

逃生：LHG_GRANT_HOOKS_OFF=1 关闭本 hook（与硬门共用一个开关）。
设计原则：只做提醒（additionalContext），从不拦截；内部出错 fail-open。
零第三方依赖。
"""

import json
import os
import re
import sys

SUBJECTS = {
    "设备费", "材料费", "测试化验加工费", "燃料动力费",
    "差旅费", "会议费", "国际合作与交流费",
    "出版/文献/信息传播/知识产权事务费",
    "出版文献信息传播知识产权事务费",
    "劳务费", "专家咨询费", "间接费用", "管理费",
    "人员费", "绩效支出",
}
ROW_RE = re.compile(r"^\s*\|([^|]*)\|([^|]*)\|")


def norm(s):
    return s.strip().replace(" ", "").replace("／", "/").replace("、", "/")


NORMED = {norm(s) for s in SUBJECTS}


def main() -> int:
    if os.environ.get("LHG_GRANT_HOOKS_OFF") == "1":
        return 0
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    fp = tool_input.get("file_path", "") or ""
    base = os.path.basename(fp).lower()
    if not (fp.lower().endswith((".md", ".markdown"))
            and ("budget" in base or "预算" in base)):
        return 0  # 非预算文件：快速放行
    if not os.path.isfile(fp):
        return 0

    try:
        with open(fp, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception:
        return 0

    bad = []
    for ln in lines:
        m = ROW_RE.match(ln)
        if not m:
            continue
        subj = m.group(1).strip()
        if not subj or "科目" in subj or "---" in subj or "合计" in subj:
            continue
        if norm(subj) not in NORMED:
            bad.append(subj)
    if not bad:
        return 0

    out = {"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext":
            "lhg-grant 提醒：预算文件 %s 中发现 %d 个非标准科目（%s），"
            "评审视角下科目错配是硬伤，建议跑 /lhg-grant:budget 核查改法。"
            % (os.path.basename(fp), len(bad), "、".join(bad[:5]))}}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
