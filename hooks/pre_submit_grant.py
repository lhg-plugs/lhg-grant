#!/usr/bin/env python3
"""lhg-grant 硬门：提交/导出前跑申请书审计，有 blocker 则拦截。

触发：PreToolUse / Bash。只在"申请书项目目录"里生效：
目录下有 grant.yaml，或 application/ 下有 01-*.md。
拦截的命令：pandoc（导出排版）与 git commit（提交）。

逃生方式（按推荐度排序）：
  1. 修掉 blocker 后再导出/提交（推荐）。
  2. 紧急情况：LHG_GRANT_HOOKS_OFF=1（单次豁免本次 hook）。
  3. /plugin disable lhg-grant（整个插件停用，hooks 不再触发）。

设计原则：脚本内部出错一律 fail-open 直接放行；
非申请书目录、非目标命令 0 开销放行。零第三方依赖。
"""

import json
import os
import re
import subprocess
import sys

AUDIT_TIMEOUT = 60
TARGET_RE = re.compile(r"(^|[;&|])\s*pandoc\b")
COMMIT_RE = re.compile(r"(^|[;&|])\s*git\s+.*\bcommit\b")


def is_grant_dir(d):
    if os.path.isfile(os.path.join(d, "grant.yaml")):
        return True
    app = os.path.join(d, "application")
    if os.path.isdir(app):
        return any(fn.startswith("01-") for fn in os.listdir(app))
    return False


def main() -> int:
    if os.environ.get("LHG_GRANT_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not (TARGET_RE.search(command) or COMMIT_RE.search(command)):
        return 0  # 非目标命令：快速放行

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not is_grant_dir(project_dir):
        return 0  # 非申请书目录：放行

    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(plugin_root, "scripts", "audit", "grant_audit.py")
    if not os.path.isfile(script):
        return 0  # 审计脚本缺失：fail-open

    try:
        proc = subprocess.run(
            [sys.executable, script, "--target", project_dir, "--format", "json"],
            capture_output=True, text=True, timeout=AUDIT_TIMEOUT)
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except Exception:
        return 0  # 审计跑不起来：fail-open

    blockers = [f for f in data.get("findings", [])
                if f.get("severity") == "blocker"]
    if not blockers:
        return 0

    lines = [
        "提交/导出被 lhg-grant 硬门拦截：审计发现 %d 个 blocker（申请书硬伤），修完再继续。"
        % len(blockers), "",
    ]
    for f in blockers[:10]:
        lines.append("- [%s] %s %s" % (f.get("rule_id"), f.get("file"), f.get("title")))
    if len(blockers) > 10:
        lines.append("…另有 %d 个，完整清单请跑 /lhg-grant:review-sim" % (len(blockers) - 10))
    lines += ["", "修复方式：运行 /lhg-grant:budget 与 /lhg-grant:review-sim 按报告逐条修复；",
              "紧急豁免（单次）：LHG_GRANT_HOOKS_OFF=1"]
    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "\n".join(lines)}}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
