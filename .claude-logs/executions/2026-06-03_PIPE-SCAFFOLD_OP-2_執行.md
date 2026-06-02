# PIPE-SCAFFOLD OP-2 — 派發點二納管 + 雙軌測試套件 執行報告

---

**任務代號**：PIPE-SCAFFOLD OP-2
**執行日期**：2026-06-03
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md`
**次級參考**：`.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md` §8 OP-2
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：OP-1（`13c1dcb`）已 ship（`SHADOW_LAUNCH_ENABLED` + `run_pipeline_shadow` + 派發點一閘門）；派發點二（confirm_type）尚未納管、無測試、OP-1 區塊未加標記。
- **完成狀態**：✅ OP-2 完整落地且全綠。`web_server.py` confirm_type（派發點二）加旗標閘門 + OP-1 三處 / OP-2 一處 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解包裹；`settings.py` 旗標加標記；新建 `tests/test_pipe_scaffold.py`（5 pytest 全綠）。**A 軌 `run_pipeline` 本體 byte-for-byte 相同**（逐行 diff 驗證）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-2 | confirm_type 派發點二閘門 + OP-1/OP-2 註解標記 + `tests/test_pipe_scaffold.py`（5 pytest） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak` | confirm_type 派發點二閘門（L811-819）+ OP-1 三處標記包裹（派發點一/影子單元）+ OP-2 派發點二標記 |
| 修改 | `settings.py` | `.claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak` | OP-1 旗標處 `=== [PIPE-SCAFFOLD OP-1 START/END] ===` 標記包裹 |
| 新建 | `tests/test_pipe_scaffold.py` | — | 雙軌派發 scaffolding 測試（5 項） |
| 新建 | `.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md` | — | OP-2 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-2 提示詞 |
| 修改 | `.claude-logs/TODO.md` | — | PIPE-SCAFFOLD OP-2 → ✅ / OP-3 → 🟡 WIP |

> ⚠️ **.bak 強制納入**：`settings.py.bak` + `web_server.py.bak` 已於 §8 git add 清單包含。
> ⚠️ 本報告自身（baton/）**不入** §8 git add 清單（baton 暫存鐵律）。

---

## §4 修法說明（含註解包裹行號）

### §4.1 `web_server.py` — 派發點二閘門 + 雙層註解標記
- **OP-2 派發點二閘門**（`confirm_type` 內、A 軌 `add_task(run_pipeline,...)` 之後）：
  - 包裹標記：`# === [PIPE-SCAFFOLD OP-2 START] 派發點二閘門 ===` … `# === [PIPE-SCAFFOLD OP-2 END] ===`（現 L811-819）
  ```python
  # === [PIPE-SCAFFOLD OP-2 START] 派發點二閘門 ===
  if settings.SHADOW_LAUNCH_ENABLED:
      background_tasks.add_task(
          run_pipeline_shadow, current_user.id, paper_id, pdf_path, request.doc_type,
          original_filename
      )
  # === [PIPE-SCAFFOLD OP-2 END] ===
  ```
- **OP-1 補標**（本階段順手包裹、利於 Flip 下線）：
  - 派發點一閘門（`upload_paper` 內）：`[PIPE-SCAFFOLD OP-1 START] 派發點一閘門` … `END`
  - 影子 B 軌派發單元：`[PIPE-SCAFFOLD OP-1 START] 影子 B 軌派發單元` … `END`（包住整個 `run_pipeline_shadow`）
- **A 軌零侵入**：`run_pipeline` 本體與 `PipelineCore.process` 調用逐行 diff 與 OP-2 前基線 **byte-for-byte 相同**（§5.2）。

### §4.2 `settings.py` — 旗標標記包裹
`SHADOW_LAUNCH_ENABLED` 以 `# === [PIPE-SCAFFOLD OP-1 START] 影子雙軌派發旗標 ===` … `# === [PIPE-SCAFFOLD OP-1 END] ===` 包裹。

### §4.3 `tests/test_pipe_scaffold.py` — 雙軌測試（5 項）
直接呼叫 async endpoint / 影子單元（繞過 HTTP/auth/DB），以 Fake BackgroundTasks 記錄派發決策（不實跑 pipeline）：① `run_pipeline_shadow` 四重隔離（`_shadow` task_key + ` (測試)` 標題 + 不碰 A 軌鍵）；② 派發點二旗標 false → 單軌（僅 `run_pipeline`）；③ 旗標 true → 雙軌（`run_pipeline` + `run_pipeline_shadow`）；④ 派發點一/二閘門標記存在（源碼自檢）；⑤ A 軌 `run_pipeline` 本體 + `PipelineCore(on_progress)` 仍在。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git diff --stat web_server.py settings.py
 settings.py   |  2 ++
 web_server.py | 17 +++++++++++++++--
# 2 deletions 為 OP-1 派發點一閘門「註解」改寫為 START/END 標記（非 A 軌本體）
```

### §5.2 A 軌 run_pipeline 本體 byte-for-byte 不變（逐行 diff）
```bash
$ awk '/^async def run_pipeline\(/{f=1} f{print} /論文處理失敗:/{if(f)exit}' web_server.py > /tmp/rp_now.txt
$ awk '...同一段...' <OP-2 .bak 基線> > /tmp/rp_base.txt
$ diff /tmp/rp_now.txt /tmp/rp_base.txt
（無輸出）→ ✅ A 軌 run_pipeline 本體 byte-for-byte 相同
$ grep -c "PIPE-SCAFFOLD OP-1 START|...END|OP-2 START|...END" web_server.py settings.py
web_server.py:6   settings.py:2   # 標記齊全（OP-1×4 web + OP-2×2 web + OP-1×2 settings）
```

### §5.3 OP-2 雙軌測試 + 既有測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/test_pipe_scaffold.py -v
tests/test_pipe_scaffold.py::test_run_pipeline_shadow_isolation PASSED
tests/test_pipe_scaffold.py::test_dispatch_flag_false_single_track PASSED
tests/test_pipe_scaffold.py::test_dispatch_flag_true_dual_track PASSED
tests/test_pipe_scaffold.py::test_dispatch_point_one_gate_present PASSED
tests/test_pipe_scaffold.py::test_a_track_run_pipeline_untouched PASSED
========================= 5 passed in 0.66s =========================

$ ./venv/bin/python -m pytest tests/ -q
1 failed, 437 passed, 3 skipped in 37.75s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-2 迴歸**：`.env:54 LOG_FORMAT=json` 覆寫測試 `"auto"` 預設斷言。OP-2 在 `settings.py` 僅替 `SHADOW_LAUNCH_ENABLED` 加標記、未動 `LOG_FORMAT`。437 passed 含 OP-2 新增 5 項。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（本次新增段）：派發點二閘門無 logging；`run_pipeline_shadow`（OP-1 既有）`logger.error(exc_info=True)`（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)"` 本次新增段）：無命中（合規）——派發點二閘門零 DB 操作。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| A 軌 `run_pipeline` 本體與 `PipelineCore.process` 調用 | [x] ✅ byte-for-byte 相同（逐行 diff 驗證） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API | [x] ✅ 未觸碰 |
| `processing_tasks`（L52）`(owner, paper_id)` 鍵語意 | [x] ✅ 未改（影子衍生 `_shadow` 新鍵） |
| 前端 `static/index.html` | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更 |
| `pipeline_core.py` 舊單體 | [x] ✅ 未觸碰 |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-3 收官一併 `mv` + `git add` 歸檔至 `executions/`，**OP-2 階段嚴禁移動**。
- **下一步**：tasks_v3 §8 OP-3（Checkout / 收官歸檔）——一次性 `mv` plan_v3→`plans/`、tasks_v3→`tasks/`、OP-1~OP-3 報告→`executions/`（保留 `_v3`）+ `git add` + TODO ✅。
- **階段二（移／Flip）仍不在本任務**：屬 PIPE-FLIP plan（五路全通 + Golden Diff 0% 觸發）；OP-1/OP-2 的 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 標記即為 Flip 下線時的精準定位錨點。
- **消化歸檔之 baton 檔**：無（OP-3 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 已列）
# cp settings.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak
# cp web_server.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak
# 2. git add 清單（含 .bak；排除 baton/ 暫存報告與 tasks 檔）
git add settings.py
git add web_server.py
git add tests/test_pipe_scaffold.py
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak
git add .claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/PIPE-SCAFFOLD_OP-2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-SCAFFOLD_OP-2_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-SCAFFOLD OP-2 — 派發點二納管 + 雙軌測試套件

1. web_server.py confirm_type 派發點二新增 SHADOW_LAUNCH_ENABLED 閘門控制。
2. 補標 OP-1 修改區塊（旗標 / 派發點一閘門 / 影子單元）與 OP-2 派發點二區塊
   === [PIPE-SCAFFOLD OP-N START/END] === 註解包裹，作為 Flip 下線精準錨點。
3. 新建 tests/test_pipe_scaffold.py（5 pytest）：影子四重隔離、旗標 false 單軌 /
   true 雙軌、閘門標記自檢、A 軌本體未改寫。
4. A 軌 run_pipeline 本體逐行 diff byte-for-byte 相同；全域 tests/ 零迴歸
   （唯一失敗為 .env LOG_FORMAT=json 環境誘發、非本次）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-SCAFFOLD OP-2 派發點二納管 + 雙軌測試 + 註解標記落地與驗收 |
| **用途** | 暫存於 baton/；OP-3 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-3 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-3 前不入版控；A 軌本體 byte 不動 |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-2 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-03)：OP-2 執行——`web_server.confirm_type` 派發點二旗標閘門納管（U4）+ OP-1 三處（旗標/派發點一/影子單元）與 OP-2 一處（派發點二）`=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解包裹（Flip 下線錨點）+ `settings.py` 旗標標記；新建 `tests/test_pipe_scaffold.py` 5 pytest 全綠（影子四重隔離 / 旗標 false 單軌 / true 雙軌 / 閘門標記自檢 / A 軌本體未改）；A 軌 `run_pipeline` 本體逐行 diff byte-for-byte 相同；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發）；修改既有檔案前 `.bak` 備份；TODO OP-2→✅ / OP-3→🟡 WIP。
