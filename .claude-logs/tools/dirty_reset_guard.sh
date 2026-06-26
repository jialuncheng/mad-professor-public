#!/usr/bin/env bash
# === [WORKFLOW-5 C5] DIRTY-RESET 守衛 (SessionEnd · Observable Fault Only) ===
# C1 實測裁定：SessionEnd hook **不能 block** session 終止（官方文件 Decision Control 表未列）。
#   故本守衛為 plan §9 Q2「路徑 B」——僅「可觀測故障」：偵測到即 stderr 警告 + exit 0，
#   不阻止 session 結束（亦不輸出 {"decision":"block"}）。
# 觸發條件（**非「baton 非空」**，避免跨 session 中途結束誤報）：
#   baton/ 仍有某任務暫存檔，且該任務於 TODO active 區塊之 Checkout 子項已標 ✅／[x]
#   （＝ 已 Checkout 卻未歸檔 = 真正的 dirty-reset）。任務 WIP（Checkout 未 ✅）一律不警告。
# 解析（C1 修正·環境無 jq）：python3 解析 baton 檔名 → 任務代號，並解析 TODO.md 區塊狀態。
# fail-open：任何異常一律 exit 0（SessionEnd 本就不能 block，純求不噴錯、不中斷收尾）。
# 專案根：優先 $CLAUDE_PROJECT_DIR，否則由腳本位置 ../../ 推得。

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
exec python3 -c '
import sys, os, glob
try:
    root = sys.argv[1]
    baton = os.path.join(root, ".claude-logs", "baton")
    todo = os.path.join(root, ".claude-logs", "TODO.md")
    if not os.path.isdir(baton) or not os.path.isfile(todo):
        sys.exit(0)
    files = [os.path.basename(f) for f in glob.glob(os.path.join(baton, "*.md"))
             if os.path.basename(f) != "README.md"]
    if not files:
        sys.exit(0)
    # baton 檔名 -> 任務代號（格式 <YYYY-MM-DD>_<TASKCODE>_...）
    codes = set()
    for fn in files:
        parts = fn.split("_")
        if len(parts) >= 2:
            codes.add(parts[1])
    lines = open(todo, encoding="utf-8", errors="replace").read().splitlines()
    CHECK = chr(0x2705)  # 白底勾 emoji
    def checkout_done(code):
        n = len(lines)
        i = 0
        while i < n:
            ln = lines[i]
            if ln.startswith("- ") and ("**" in ln) and (code in ln):
                j = i + 1
                while j < n and (lines[j].startswith("  ") or lines[j].strip() == ""):
                    sub = lines[j]
                    if ("Checkout" in sub) and ("[x]" in sub or CHECK in sub):
                        return True
                    j += 1
            i += 1
        return False
    dirty = sorted(c for c in codes if checkout_done(c))
    if dirty:
        sys.stderr.write("[DIRTY-RESET][observable] baton 仍有已 Checkout 但未歸檔之任務: "
                         + ", ".join(dirty)
                         + " -- 請於 Checkout 階段將 baton 暫存檔 mv 至正式目錄 (plans/ tasks/ executions/) 並 git add。"
                         + " (SessionEnd 無法阻擋結束，本訊息僅為可觀測警告)\n")
    sys.exit(0)
except Exception:
    sys.exit(0)
' "$ROOT"
