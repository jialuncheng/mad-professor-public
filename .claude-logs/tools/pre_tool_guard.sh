#!/usr/bin/env bash
# === [WORKFLOW-5 C4] PreToolUse 截斷守衛 (Truncation Guard) ===
# 目的：攔截對治理真理源（plans/ sop/ ref/ CLAUDE.md TODO.md）的「異常截斷」寫入。
# 機制（C1 實測修正）：攔截＝exit 0 + stdout JSON permissionDecision=deny（**非 exit 2**）；
#                       放行＝exit 0 且不輸出 JSON。
# 解析（C1 實測修正）：環境無 jq → 用 python3 解析 stdin PreToolUse JSON。
# 威脅範圍（plan §1 Threat Model）：本守衛為「防誤觸減速帶」，agent 可用 sentinel
#   `// BYPASS_TRUNCATION_GUARD` 自我授權放行；不防「agent 決定截斷」。不可繞過之保證僅在 baton 3-Phase。
# 容錯：任何解析/IO 異常一律 fail-open（exit 0、無 JSON）—— hook 絕不把人鎖在外。
#
# 判定：僅 Write/Edit + 路徑命中保護集才檢查；on-disk 既有檔，行數驟降 >50% 且 >50 行 → deny。
#   - Write：比 tool_input.content 新行數 vs 現檔行數。
#   - Edit ：比 old_string 與 new_string 之淨移除行數 vs 現檔行數。
#   - 新檔（on-disk 不存在）→ 無可截斷 → 放行。

exec python3 -c '
import sys, json, os
SENTINEL = "BYPASS_TRUNCATION_GUARD"
PROTECT = ("CLAUDE.md", "TODO.md", "/plans/", "/sop/", "/ref/")
MIN_SHRINK_LINES = 50
SHRINK_RATIO = 0.5

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason}}))
    sys.exit(0)

try:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    path = ti.get("file_path", "") or ""
    if tool not in ("Write", "Edit"):
        sys.exit(0)
    if not any(p in path for p in PROTECT):
        sys.exit(0)
    blob = " ".join(str(ti.get(k, "")) for k in ("content", "new_string", "old_string"))
    if SENTINEL in blob:
        sys.exit(0)
    if not os.path.isfile(path):
        sys.exit(0)
    cur_lines = open(path, encoding="utf-8", errors="replace").read().count(chr(10)) + 1
    if tool == "Write":
        new_lines = (ti.get("content", "") or "").count(chr(10)) + 1
        shrink = cur_lines - new_lines
        if shrink > MIN_SHRINK_LINES and shrink > SHRINK_RATIO * cur_lines:
            deny("Truncation guard: Write shrinks " + path + " from " + str(cur_lines) + " to " + str(new_lines) + " lines (>50%). If this is a legitimate refactor, add // " + SENTINEL + " to the content to override.")
    else:
        old_s = ti.get("old_string", "") or ""
        new_s = ti.get("new_string", "") or ""
        removed = old_s.count(chr(10)) - new_s.count(chr(10))
        if removed > MIN_SHRINK_LINES and removed > SHRINK_RATIO * cur_lines:
            deny("Truncation guard: Edit removes ~" + str(removed) + " lines from " + path + " (>50% of " + str(cur_lines) + "). If legitimate, add // " + SENTINEL + " to new_string to override.")
    sys.exit(0)
except SystemExit:
    raise
except Exception:
    sys.exit(0)
'
