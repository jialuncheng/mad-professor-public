# PIPE-CORE OP-1 — 合約與狀態層 執行報告

---

**任務代號**：PIPE-CORE OP-1
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md` §8 OP-1
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：工作區在 GOLDEN-BASELINE Check（`c0c64e9`）之後；`pipelines/` 目錄不存在、無三層解耦骨架。
- **完成狀態**：✅ OP-1 完整落地且全綠。新建 `pipelines/` 套件合約層 + 狀態層（`contracts.py` 四份凍結 Pydantic v2 子模型 + `context.py` PipelineContext + `__init__.py`）+ `tests/test_pipe_core.py`（8 pytest 全綠）。**零既有業務代碼改動**（舊 `pipeline_core.py` / `web_server.py` / `models.py` / `processor/*` 全未觸；新目錄物理共存、runtime 不接流量）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `pipelines/contracts.py` 四凍結合約 + `pipelines/context.py` PipelineContext + `tests/test_pipe_core.py`（8 pytest） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/__init__.py` | — | 套件入口，匯出 contracts + context |
| 新建 | `pipelines/contracts.py` | — | 四份凍結 Phase 交接合約（PIPE-SPEC §1.1） |
| 新建 | `pipelines/context.py` | — | PipelineContext + PhaseEnum（唯一狀態通道） |
| 新建 | `tests/test_pipe_core.py` | — | 契約測試 8 項（frozen / R1.1 禁欄位 / 必填 / Context 預設） |
| 新建 | `.claude-logs/prompts/2026-06-02_PIPE-CORE_OP-1_run_提示詞.md` | — | OP-1 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-1 提示詞 + 時間排序 |
| 修改 | `.claude-logs/TODO.md` | — | PIPE-CORE OP-1 → ✅ / OP-2 → 🟡 WIP；Hash 自癒 GOLDEN-BASELINE Check `c0c64e9` |

> OP-1 全為新建檔案、零既有檔案修改，故**無 .bak 備份（合規）**。
> ⚠️ 本報告自身（baton/）及任何 baton/ 暫存檔**不入** §8 git add 清單（baton 暫存鐵律）。

---

## §4 修法說明

### §4.1 `pipelines/contracts.py` — 四份凍結 Phase 交接合約
Pydantic v2（專案 `pydantic 2.13.4`）`model_config = ConfigDict(frozen=True, extra="forbid")`：
- **`IngestionMetadataSpec`（合約① P1→P2）**：`title`/`authors`/`venue`/`doi`/`source_lang`/`tiles`。**`extra="forbid"` 於 schema 層保證 R1.1**——傳入 `abstract`/`lcc`/`glossary` 任一即 `ValidationError`（P1 越界攔截）。
- **`GlossaryReadySpec`（合約② P2→P3）**：`abstract`/`lcc`/`glossary`/`translated_abstract`（必填）+ `chapter_summaries`（Book、可選）。
- **`BilingualMarkdownSpec`（合約③ P3→P4）**：`final_zh_path`/`final_en_path`/`translated_abstract`（沿用）+ `rag_tree_json`（可選）。
- **`RagDbSpec`（合約④ P4→外部）**：`vectors_path`/`paper_chunk_count`/`index_meta`。

```python
class IngestionMetadataSpec(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")  # ← R1.1：禁 Abstract/LCC/Glossary
    title: str
    source_lang: str
    ...
```

### §4.2 `pipelines/context.py` — PipelineContext 狀態載體
`PhaseEnum`（P1/P2/P3/P4）+ `PipelineContext`（Pydantic）：調度元欄位 `doc_type`/`paper_id`/`shadow`/`phase`/`reading_ready`/`rag_status`（`Literal['pending','ready','failed']`）+ 四合約欄位（`ingestion`/`glossary_ready`/`bilingual`/`rag`，預設 None）。Context 可變（狀態隨 Phase 推進），承載的合約子模型凍結。

### §4.3 `tests/test_pipe_core.py` — 契約測試（8 項）
覆蓋：Ingestion 合法建構 / R1.1 禁欄位 ValidationError / GlossaryReady 缺 translated_abstract FAIL / 合法建構 / 三合約 frozen 不可變 / Context 預設 None+phase+rag_status / Context 承載凍結合約 + phase 推進 / rag_status 非法 Literal 拒絕。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s pipelines/ tests/test_pipe_core.py
?? pipelines/
?? tests/test_pipe_core.py
# baton/ 報告 gitignored，未列入（合規）
```

### §5.2 OP-1 契約測試（全綠）
```bash
$ ./venv/bin/python -c "from pipelines.contracts import *; from pipelines.context import *; print('import OK')"
import OK

$ ./venv/bin/python -m pytest tests/test_pipe_core.py -v
tests/test_pipe_core.py::test_ingestion_valid_construct PASSED
tests/test_pipe_core.py::test_ingestion_rejects_abstract_lcc_glossary PASSED
tests/test_pipe_core.py::test_glossary_ready_requires_translated_abstract PASSED
tests/test_pipe_core.py::test_glossary_ready_valid PASSED
tests/test_pipe_core.py::test_contracts_are_frozen PASSED
tests/test_pipe_core.py::test_context_defaults PASSED
tests/test_pipe_core.py::test_context_carries_frozen_contract_and_phase_advances PASSED
tests/test_pipe_core.py::test_rag_status_rejects_invalid_literal PASSED
========================= 8 passed in 0.02s =========================
```

### §5.3 既有測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/ -q
1 failed, 420 passed, 3 skipped in 40.65s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-1 迴歸**：`.env:54 LOG_FORMAT=json` 覆寫測試斷言的 `"auto"` 預設值。OP-1 僅新增 `pipelines/` + `tests/test_pipe_core.py`，**未動 `settings.py`/`utils/`**，與該測試無關（同 GOLDEN-BASELINE OP-2 已記錄之既有環境落差）。420 passed 含 OP-1 新增 8 項。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger.error|traceback.format_exc" pipelines/*.py`）：無命中（合規）——合約/狀態純資料模型，無 logging。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/*.py`）：無命中（合規）——零 DB 操作，Context/合約為記憶體 Pydantic 模型。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 舊單體（11-stage / process / 可變 dict） | [x] ✅ 未觸碰 |
| `web_server.py` 上傳/派發入口 | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更（合約為記憶體 Pydantic、零 DB） |
| `processor/*` 既有模組 | [x] ✅ 未接線 |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |
| Orchestrator 禁 doc_type 分支 | [x] ✅ 不適用（OP-1 無 orchestrator，屬 OP-3） |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-4 收官一併 `mv` + `git add` 歸檔至 `executions/`，**OP-1 階段嚴禁移動**。
- **下一步**：tasks_v2 §8 OP-2（工廠與策略基類）——`base_strategy.py`（DocumentStrategy ABC + NullStrategy）+ `factory.py`（get_strategy 註冊 + 降級）；修改 `tests/test_pipe_core.py` 前須 `.bak` 備份。
- **消化歸檔之 baton 檔**：無（OP-4 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（OP-1 全為新建檔案，無備份）
# 2. git add 清單（排除 baton/ 暫存報告與 tasks 檔）
git add pipelines/contracts.py
git add pipelines/context.py
git add pipelines/__init__.py
git add tests/test_pipe_core.py
git add .claude-logs/prompts/2026-06-02_PIPE-CORE_OP-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/PIPE-CORE_OP-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-CORE_OP-1_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-CORE OP-1 — 合約與狀態層

1. 新建 pipelines/ 套件（與舊 pipeline_core.py 物理共存、零既有代碼改動）。
2. pipelines/contracts.py 四份凍結 Pydantic v2 合約（IngestionMetadataSpec extra=forbid
   保證 R1.1 禁 Abstract/LCC/Glossary / GlossaryReadySpec / BilingualMarkdownSpec / RagDbSpec）。
3. pipelines/context.py PipelineContext + PhaseEnum 類型安全狀態載體（取代可變 dict 黑盒）。
4. tests/test_pipe_core.py 8 pytest 全綠（frozen / R1.1 攔截 / 必填 / Context 預設）；既有測試零迴歸。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-CORE OP-1 合約與狀態層落地與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-4 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-4 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-4 前不入版控；嚴禁本報告自身入 git add |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-1 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-1 執行——`pipelines/contracts.py` 四份凍結 Pydantic v2 合約（IngestionMetadataSpec `extra='forbid'` 保證 R1.1）+ `pipelines/context.py` PipelineContext/PhaseEnum + `pipelines/__init__.py` + `tests/test_pipe_core.py` 8 pytest 全綠；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發、非 OP-1）；零業務代碼改動；TODO OP-1→✅ / OP-2→🟡 WIP，Hash 自癒 GOLDEN-BASELINE Check `c0c64e9`。
