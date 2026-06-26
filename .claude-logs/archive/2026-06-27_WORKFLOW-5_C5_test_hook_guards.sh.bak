#!/usr/bin/env bash
# === [WORKFLOW-5 C4] hook guards 乾跑/單元測試 ===
# 用法: bash test_hook_guards.sh [truncation|dirty_reset|all]
#   truncation  — 測 pre_tool_guard.sh 截斷守衛（C4）
#   dirty_reset — 測 dirty_reset_guard.sh（C5 補；本檔 C4 階段為佔位）
#   all         — 全部
# 測試以 python3 建 fixture + 組 JSON + subprocess 呼叫守衛 + 斷言（環境無 jq）。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:-all}"

truncation_tests() {
python3 - "$HERE/pre_tool_guard.sh" <<'PY'
import sys, os, json, subprocess, tempfile, shutil
guard = sys.argv[1]
fails = 0

def run(payload):
    p = subprocess.run(["bash", guard], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.stdout.strip()

def is_deny(out):
    try:
        return json.loads(out).get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    except Exception:
        return False

def check(name, payload, want_deny):
    global fails
    out = run(payload)
    ok = (is_deny(out) == want_deny) and (out == "" if not want_deny else True)
    print(("PASS" if ok else "FAIL") + ": " + name + ("" if ok else "  -> " + repr(out)))
    if not ok:
        fails += 1

tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "ref"))
big = os.path.join(tmp, "ref", "WORKFLOW_SOP.md")
open(big, "w").write("\n".join("line %d" % i for i in range(200)))   # 200 lines

check("T1 Write truncate protected 200->3",
      {"tool_name": "Write", "tool_input": {"file_path": big, "content": "a\nb\nc"}}, True)
check("T2 truncate + BYPASS sentinel -> allow",
      {"tool_name": "Write", "tool_input": {"file_path": big, "content": "a // BYPASS_TRUNCATION_GUARD"}}, False)
check("T3 out-of-scope .py -> allow",
      {"tool_name": "Write", "tool_input": {"file_path": os.path.join(tmp, "foo.py"), "content": "x"}}, False)
check("T4 new protected file (no on-disk) -> allow",
      {"tool_name": "Write", "tool_input": {"file_path": os.path.join(tmp, "ref", "NEW.md"), "content": "x"}}, False)
check("T5 small shrink 200->180 -> allow",
      {"tool_name": "Write", "tool_input": {"file_path": big, "content": "\n".join(["l"] * 180)}}, False)
check("T6 Edit remove >50 lines -> deny",
      {"tool_name": "Edit", "tool_input": {"file_path": big,
       "old_string": "\n".join("line %d" % i for i in range(120)), "new_string": "line 0"}}, True)
check("T7 Edit small remove -> allow",
      {"tool_name": "Edit", "tool_input": {"file_path": big,
       "old_string": "line 0\nline 1\nline 2", "new_string": "line 0"}}, False)
check("T8 malformed JSON path missing -> fail-open allow",
      {"tool_name": "Write", "tool_input": {"content": "x"}}, False)

shutil.rmtree(tmp)
print("---")
print("TRUNCATION: %d failed" % fails)
sys.exit(1 if fails else 0)
PY
}

dirty_reset_tests() {
  echo "dirty_reset tests: 由 C5 補入（本 C4 階段為佔位）"
  return 0
}

rc=0
case "$MODE" in
  truncation) truncation_tests || rc=$? ;;
  dirty_reset) dirty_reset_tests || rc=$? ;;
  all) truncation_tests || rc=$?; dirty_reset_tests || rc=$? ;;
  *) echo "usage: $0 [truncation|dirty_reset|all]"; exit 2 ;;
esac
exit $rc
