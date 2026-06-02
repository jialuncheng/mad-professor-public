# PIPE-SCAFFOLD OP-1 — 旗標 + 影子派發單元 + 派發點一 執行報告

---

**任務代號**：PIPE-SCAFFOLD OP-1
**執行日期**：2026-06-03
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md`
**次級參考**：`.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md` §8 OP-1
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：PIPE-CORE 已 ship（`pipelines/` Orchestrator 骨架）；`web_server.py` 派發層單軌（`upload_paper` 僅拋 `run_pipeline`）、`settings.py` 無 `SHADOW_LAUNCH_ENABLED`。
- **完成狀態**：✅ OP-1 完整落地。`settings.py` 新增 `SHADOW_LAUNCH_ENABLED`（預設 False）；`web_server.py` **附加** `run_pipeline_shadow` 影子派發單元 + `upload_paper`（派發點一）旗標閘門。**A 軌 `run_pipeline`（L493-527）本體與 `PipelineCore.process` 調用 byte 不動**（git diff：59 insertions / **0 deletions**）。旗標預設 false → 100% 等同現行單軌、線上 0 風險。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `settings.SHADOW_LAUNCH_ENABLED`（預設 false）+ `web_server.run_pipeline_shadow` 附加單元 + 派發點一閘門（A 軌 byte 不動） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `settings.py` | `.claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_settings.py.bak` | 新增 `SHADOW_LAUNCH_ENABLED` env（預設 false、+10 行） |
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_web_server.py.bak` | 附加 `run_pipeline_shadow` 單元（L541）+ `upload_paper` 派發點一閘門（L485）；A 軌本體 byte 不動（+49 行 / 0 刪除） |
| 新建 | `.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-1_run_提示詞.md` | — | OP-1 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-1 提示詞 |
| 修改 | `.claude-logs/TODO.md` | — | PIPE-SCAFFOLD OP-1 → ✅ / OP-2 → 🟡 WIP |

> ⚠️ **.bak 強制納入**：`settings.py.bak` + `web_server.py.bak` 已於 §8 git add 清單包含（審計存檔）。
> ⚠️ 本報告自身（baton/）**不入** §8 git add 清單（baton 暫存鐵律）。
> ℹ️ **OP-1 不含測試檔**：雙軌測試 `tests/test_pipe_scaffold.py` 屬 OP-2（tasks §8）；OP-1 驗收以 import/compile/grep/diff/迴歸為據。

---

## §4 修法說明

### §4.1 `settings.py` — SHADOW_LAUNCH_ENABLED 旗標（plan v3 U1）
末尾新增 env 讀取（對齊既有 `os.getenv(...).lower() in (...)` 風格）：
```python
SHADOW_LAUNCH_ENABLED = os.getenv("SHADOW_LAUNCH_ENABLED", "false").lower() in (
    "1", "true", "yes",
)
```
預設 false → dual-dispatch 為零作用惰性插入點。

### §4.2 `web_server.py` — 影子派發單元 + 派發點一閘門（plan v3 §2.7.1/2.7.2、U2/U3/U4）
- **附加** `async def run_pipeline_shadow(...)`（L541，置於 A 軌 `run_pipeline` 之後、SSE 區之前）：① `paper_id_shadow = f"{paper_id}_shadow"` 衍生獨立 `task_key`（與 A 軌不碰撞）；② 寫獨立 `processing_tasks[shadow_key]`，`_original_filename` 加 ` (測試)` 後綴（四重隔離④）；③ 委派 B 軌新核心 `from pipelines import Orchestrator, PipelineContext` → `Orchestrator().run(ctx)`（`shadow=True`）；④ 異常 `logger.error(..., exc_info=True)` 標 error、**不影響 A 軌正本**（U2）。
- **派發點一閘門**（`upload_paper` A 軌 `add_task(run_pipeline,...)` 之後、L485）：
```python
if settings.SHADOW_LAUNCH_ENABLED:
    background_tasks.add_task(
        run_pipeline_shadow, current_user.id, paper_id, str(pdf_path), doc_type, file.filename
    )
```
- **A 軌零侵入**：`run_pipeline`（L493-527）與 `PipelineCore.process`（L509）本體完全未動（git diff 0 deletions）。
- **惰性說明**：B 軌委派新核心，骨架期無具體策略註冊 → NullStrategy；旗標 false 時本單元永不觸發，待 PIPE-RESUME 註冊策略後才開旗標（plan v3 §7 Q1）。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git diff --stat web_server.py settings.py
 settings.py   | 10 ++++++++++
 web_server.py | 49 +++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 59 insertions(+)   # 0 deletions → A 軌 byte 不動
```

### §5.2 OP-1 驗收（全綠）
```bash
$ ./venv/bin/python -c "import settings; print(settings.SHADOW_LAUNCH_ENABLED)"
False                                    # 旗標預設 false（U1）

$ ./venv/bin/python -m py_compile settings.py web_server.py
compile OK

$ grep -nE "def run_pipeline\b|PipelineCore\(on_progress|def run_pipeline_shadow" web_server.py
493:async def run_pipeline(...)          # A 軌本體保留
509:        pipeline = PipelineCore(on_progress=on_progress)   # A 軌核心調用保留
541:async def run_pipeline_shadow(...)   # 影子單元存在

$ git diff web_server.py | grep -E "^-" | grep -v "^---"
（無輸出）→ ✅ 0 刪除行（純附加、A 軌 byte 不動）
```

### §5.3 既有測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/ -q
1 failed, 432 passed, 3 skipped in 37.16s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-1 迴歸**：`.env:54 LOG_FORMAT=json` 覆寫測試 `"auto"` 預設斷言。OP-1 在 `settings.py` 僅**新增** `SHADOW_LAUNCH_ENABLED`，**未動 `LOG_FORMAT`**；`web_server.py` 純附加。屬既有環境配置落差，與本次無關（同前序 OP 已記錄）。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger.error|logger.exception|traceback.format_exc" web_server.py` 本次新增段）：`run_pipeline_shadow` 異常用 `logger.error(..., exc_info=True)`（合規）；無 `traceback.format_exc` 手動拼接。
- **database 檢測**（`grep -nE "\.commit\(\)"` 本次新增段）：無命中（合規）——`run_pipeline_shadow` 零 DB 寫入（僅記憶體 `processing_tasks` + 委派 Orchestrator）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| A 軌 `run_pipeline`（L493-527）本體與 `PipelineCore.process`（L509）調用 | [x] ✅ byte 不動（git diff 0 deletions） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API | [x] ✅ 未觸碰 |
| `processing_tasks`（L52）`(owner, paper_id)` 鍵語意 | [x] ✅ 未改（影子僅衍生 `_shadow` 新鍵） |
| 前端 `static/index.html` | [x] ✅ 未觸碰（靠 ` (測試)` 標題區分） |
| `models.py` 既有 Schema | [x] ✅ 未變更 |
| `pipeline_core.py` 舊單體 | [x] ✅ 未觸碰 |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-3 收官一併 `mv` + `git add` 歸檔至 `executions/`，**OP-1 階段嚴禁移動**。
- **下一步**：tasks_v3 §8 OP-2（派發點二納管 + 雙軌測試）——retry/confirm（L756）同構加旗標閘門 + 新建 `tests/test_pipe_scaffold.py`（旗標 false 單軌等價 / true 雙軌不碰撞 / 派發點二覆蓋 / A 軌本體 grep 斷言）；修改 `web_server.py` 前須 `.bak` 備份。
- **消化歸檔之 baton 檔**：無（OP-3 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 已列）
# cp settings.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_settings.py.bak
# cp web_server.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_web_server.py.bak
# 2. git add 清單（含 .bak；排除 baton/ 暫存報告與 tasks 檔）
git add settings.py
git add web_server.py
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_settings.py.bak
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-1_web_server.py.bak
git add .claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/PIPE-SCAFFOLD_OP-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-SCAFFOLD_OP-1_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-SCAFFOLD OP-1 — 旗標 + 影子派發單元 + 派發點一

1. settings.py 新增 SHADOW_LAUNCH_ENABLED 環境變數（預設為 false）。
2. web_server.py 附加 run_pipeline_shadow 影子派發單元，封裝 _shadow 與 (測試) 標題、
   委派 B 軌新核心 Orchestrator，異常不影響 A 軌正本。
3. upload_paper（派發點一）新增旗標閘門，旗標 true 時額外派發 B 軌（惰性插入）。
4. A 軌 run_pipeline 既有同步邏輯本體與 PipelineCore.process 調用全程 byte 不動
   （git diff 59 insertions / 0 deletions）；旗標預設 false → 100% 等同現行單軌、線上 0 風險。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-SCAFFOLD OP-1 旗標 + 影子派發單元 + 派發點一落地與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-3 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-3 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-3 前不入版控；A 軌本體 byte 不動 |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-1 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-03)：OP-1 執行——`settings.SHADOW_LAUNCH_ENABLED`（預設 false）+ `web_server.run_pipeline_shadow` 附加影子派發單元（`_shadow` 四重隔離 + ` (測試)` 標題 + 委派 Orchestrator + 異常不影響 A 軌）+ `upload_paper` 派發點一旗標閘門；A 軌 `run_pipeline` 本體 byte 不動（git diff 59 insertions / 0 deletions）；旗標預設 false 線上 0 風險；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發）；修改既有檔案前 `.bak` 備份；TODO OP-1→✅ / OP-2→🟡 WIP。
