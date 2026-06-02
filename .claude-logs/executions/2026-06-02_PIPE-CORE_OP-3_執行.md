# PIPE-CORE OP-3 — Orchestrator 四 Phase DAG 調度 執行報告

---

**任務代號**：PIPE-CORE OP-3
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md` §8 OP-3
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：OP-2（`effb155`）已 ship，`pipelines/` 有 contracts/context/base_strategy/factory；無指揮層。
- **完成狀態**：✅ OP-3 完整落地且全綠。新建 `pipelines/orchestrator.py`（宣告式四 Phase DAG + 交接點驗證 + reading_ready/rag_status + Early Emit/Checkpoint/P4 派發掛點 + shadow 貫穿）；更新 `__init__.py` 匯出；`tests/test_pipe_core.py` 追加 6 項（共 20 全綠）。`grep doc_type==` **0 命中**（三層解耦自證）。**零既有業務代碼改動**。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-3 | `orchestrator.py` 四 Phase DAG 指揮層 + 測試追加（20 pytest）+ grep doc_type== 0 命中 | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/orchestrator.py` | — | Orchestrator 四 Phase DAG（宣告式 `_PHASES` + 交接點驗證 + P4 容錯 + shadow + OrchestratorError） |
| 修改 | `pipelines/__init__.py` | — | 匯出 Orchestrator / OrchestratorError |
| 修改 | `tests/test_pipe_core.py` | `.claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak` | 追加 6 Orchestrator 測試 |
| 新建 | `.claude-logs/prompts/2026-06-02_PIPE-CORE_OP-3_run_提示詞.md` | — | OP-3 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-3 提示詞 |
| 修改 | `.claude-logs/TODO.md` | — | PIPE-CORE OP-3 → ✅ / OP-4 → 🟡 WIP |

> ⚠️ **.bak 強制納入**：`.claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak` 已於 §8 git add 清單包含。
> ⚠️ 本報告自身（baton/）**不入** §8 git add 清單（baton 暫存鐵律）。

---

## §4 修法說明

### §4.1 `pipelines/orchestrator.py` — 四 Phase DAG 指揮層
- **宣告式 Phase 序列** `_PHASES = [(P1, "run_phase1", "ingestion", IngestionMetadataSpec), (P2,...), (P3,...)]`——純資料宣告、迴圈推進，**零 doc_type 字面量分支**（三層解耦自證）。
- `Orchestrator.run(ctx)`：① `PipelineFactory.get_strategy(ctx.doc_type)` 取策略（零分支）；② shadow 命名貫穿（`paper_id` 尾綴 `_shadow`，SPEC §3.5）；③ 迴圈推進 P1→P3，每 Phase 呼叫 `strategy.run_phaseN` → **交接點型別斷言**（不符 → 拋 `OrchestratorError` 中止）→ 寫 `ctx.<欄位>` → Checkpoint 掛點；P1 後 Early Emit 掛點；P3 後 `ctx.reading_ready=True`（R4.1）；④ P4 非阻塞派發（injectable `dispatch_p4`、預設同步樁）+ 容錯（失敗僅 `rag_status='failed'` + warning、不阻主鏈、不影響 reading_ready，R4.2）。
- **交接點① R1.1**：禁 Abstract/LCC/Glossary 由合約 `extra='forbid'`（OP-1）結構保證；Orchestrator 層再加合約型別斷言雙重防護。
- **P1–P3 失敗語意**：以 `OrchestratorError(phase, reason)` 拋出表達「FAILED、中止」，**不修改 OP-1 的 `context.py`**（避免越出 OP-3 範圍新增 status 欄位；失敗狀態由例外承載、reading_ready 維持 False）。

```python
_PHASES = [
    (PhaseEnum.P1, "run_phase1", "ingestion", IngestionMetadataSpec),
    (PhaseEnum.P2, "run_phase2", "glossary_ready", GlossaryReadySpec),
    (PhaseEnum.P3, "run_phase3", "bilingual", BilingualMarkdownSpec),
]
for phase, runner_name, field, expected in _PHASES:
    result = getattr(strategy, runner_name)(ctx)
    if not isinstance(result, expected):
        raise OrchestratorError(phase, "交接點驗證失敗：...")
    setattr(ctx, field, result)
    if phase is PhaseEnum.P3: ctx.reading_ready = True
```

### §4.2 `tests/test_pipe_core.py` — 追加 6 Orchestrator 測試
DAG 順序 P1→P4 + reading_ready/rag_status 解鎖 / 交接點型別攔截（錯型別 → OrchestratorError、reading_ready 仍 False）/ P4 失敗不阻主鏈（reading_ready True、rag_status='failed'、不上拋）/ shadow 命名貫穿 / Early Emit+Checkpoint 掛點觸發序 / NullStrategy 路 NotImplementedError。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s pipelines/orchestrator.py pipelines/__init__.py tests/test_pipe_core.py
?? pipelines/orchestrator.py
 M pipelines/__init__.py
 M tests/test_pipe_core.py
# baton/ 報告 gitignored，未列入（合規）
```

### §5.2 三層解耦自證 + 全測試（全綠）
```bash
$ grep -nE "doc_type ==" pipelines/orchestrator.py
（無輸出）→ ✅ 0 命中（Orchestrator 零 doc_type 業務分支）

$ ./venv/bin/python -c "from pipelines import Orchestrator, OrchestratorError; print('import OK')"
import OK

$ ./venv/bin/python -m pytest tests/test_pipe_core.py -v
... (20 items)
tests/test_pipe_core.py::test_orchestrator_dag_order_and_unlocks PASSED
tests/test_pipe_core.py::test_orchestrator_handoff_validation_blocks PASSED
tests/test_pipe_core.py::test_orchestrator_p4_failure_does_not_block_reading PASSED
tests/test_pipe_core.py::test_orchestrator_shadow_naming_propagates PASSED
tests/test_pipe_core.py::test_orchestrator_early_emit_and_checkpoint_hooks PASSED
tests/test_pipe_core.py::test_orchestrator_nullstrategy_raises PASSED
========================= 20 passed in 0.02s =========================
```

### §5.3 既有測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/ -q
1 failed, 432 passed, 3 skipped in 36.89s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-3 迴歸**：`.env:54 LOG_FORMAT=json` 覆寫測試 `"auto"` 預設斷言。OP-3 僅新增 `orchestrator.py` + 改 `__init__`/測試，**未動 `settings.py`/`utils/`**。432 passed 含 OP-3 新增 6 項。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger.error|logger.exception|traceback.format_exc" pipelines/orchestrator.py`）：無 `logger.error` 手動拼接；P4 容錯用 `logger.warning(..., exc_info=True)`（warning 級、合規——RAG 失敗為可容忍非致命，R4.2）。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/orchestrator.py`）：無命中（合規）——指揮層零 DB 操作（RAG/DB 落庫屬 RAG-ASYNC plan）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 舊單體 | [x] ✅ 未觸碰 |
| `web_server.py` 上傳/派發入口 | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更（零 DB） |
| `processor/*` 既有模組 | [x] ✅ 未接線 |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |
| **Orchestrator 禁 doc_type 業務分支** | [x] ✅ `grep doc_type==` 0 命中（宣告式 `_PHASES` 推進） |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-4 收官一併 `mv` + `git add` 歸檔至 `executions/`，**OP-3 階段嚴禁移動**。
- **下一步**：tasks_v2 §8 OP-4（Checkout / 收官歸檔）——一次性 `mv` plan_v2→`plans/`、tasks_v2→`tasks/`、OP-1~OP-4 報告→`executions/` + `git add` + TODO ✅。
- **骨架完成度**：三層解耦空骨架（合約/狀態/策略/指揮）至此齊備；五路具體策略 how 屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK；P4 真正 BackgroundTasks 屬 RAG-ASYNC（本骨架已留 injectable `dispatch_p4` 介面）。
- **消化歸檔之 baton 檔**：無（OP-4 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 已列）
# cp tests/test_pipe_core.py .claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak
# 2. git add 清單（含 .bak 備份；排除 baton/ 暫存報告與 tasks 檔）
git add pipelines/orchestrator.py
git add pipelines/__init__.py
git add tests/test_pipe_core.py
git add .claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak
git add .claude-logs/prompts/2026-06-02_PIPE-CORE_OP-3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/PIPE-CORE_OP-3_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-CORE_OP-3_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-CORE OP-3 — Orchestrator 四 Phase DAG 調度

1. 新建 pipelines/orchestrator.py：宣告式 _PHASES 推進 P1→P4（零 doc_type 字面量分支）。
2. 交接點型別驗證（① R1.1 由合約 extra=forbid 結構保證）；P1–P3 失敗拋 OrchestratorError 中止。
3. P3 後 reading_ready 解鎖（R4.1）；P4 非阻塞派發掛點 + 容錯（失敗僅 rag_status=failed、
   不阻主鏈、不影響 reading_ready，R4.2）；shadow 命名貫穿。
4. pipelines/__init__.py 匯出 Orchestrator；tests/test_pipe_core.py 追加 6 測試（共 20 全綠）；
   grep doc_type== 0 命中；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-CORE OP-3 Orchestrator 指揮層落地與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-4 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-4 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-4 前不入版控；Orchestrator 禁 doc_type 分支 |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-3 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-3 執行——`pipelines/orchestrator.py` 宣告式四 Phase DAG（`_PHASES` 推進、零 doc_type 分支）+ 交接點型別驗證（P1–P3 失敗拋 OrchestratorError）+ P3 後 reading_ready 解鎖 + P4 非阻塞派發掛點與容錯（R4.2）+ shadow 命名貫穿 + Early Emit/Checkpoint 掛點；`__init__.py` 匯出；`tests/test_pipe_core.py` 追加 6 測試共 20 全綠；`grep doc_type==` 0 命中；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發）；零業務代碼改動；P1–P3 失敗以例外承載、不改 OP-1 context.py（避免越界）；修改測試檔前 .bak 備份；TODO OP-3→✅ / OP-4→🟡 WIP。
