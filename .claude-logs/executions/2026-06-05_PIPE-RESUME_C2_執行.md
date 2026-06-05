# PIPE-RESUME C2 — P1 + Context 執行報告

---

**任務代號**：PIPE-RESUME C2（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C2
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C1（三規格同步、待 baron commit）後；`PipelineContext` 無 `raw_metadata` 欄；`run_phase1` 寫 `self._raw_meta`（實例死路）、無影子標題後綴。
- **完成狀態**：① `pipelines/context.py` `PipelineContext` 加 `raw_metadata: Dict[str, Any] = {}`（補 `Dict,Any` import）；② `run_phase1` 結束前將整包 `meta`（Stage A 合併結構含 confidence/source）+ regex 抽出 phone/email 寫 `ctx.raw_metadata`，**過渡期保留 `self._raw_meta` 雙寫**（C2 後 P2 仍可運作）；③ 影子後綴——`title` 解出後若 `ctx.paper_id.endswith('_shadow')` → `f"{title} (測試)"`。全變更 `# === [PIPE-RESUME v9 C2 START/END] ===` 包裹。pipelines+resume **40 passed**、全套件 **480 passed**。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | `context.py` 加 `raw_metadata` 欄 + `run_phase1` 寫入（雙寫 self._raw_meta）+ `_shadow` title 加綴 (測試) | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/context.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C2_context.py.bak` | `PipelineContext` 加 `raw_metadata` 欄（v9 C2 標記）+ `Dict,Any` import |
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C2_resume_pipeline.py.bak` | `run_phase1` ⑦ 段：影子後綴 + ctx.raw_metadata 寫入（v9 C2 標記）|

> ⚠️ 二份 `.bak` 須在 C2 `git add` 清單（§8）。**執行報告本體不 git add**（依指令）。

---

## §4 修法說明

### §4.1 `pipelines/context.py` — `raw_metadata` 旁路欄
`# === [PIPE-RESUME v9 C2 START/END] ===` 包裹（接原批次 C2 區塊後）：
```python
raw_metadata: Dict[str, Any] = {}   # DB 持久化旁路欄（PIPE-SPEC §1.1.1）；P1 寫整包原始 metadata
```
import 補 `Dict, Any`；預設 `{}` → 前向相容既有 PIPE-CORE/SCAFFOLD 測試（25 passed 不破）。

### §4.2 `pipelines/resume_pipeline.py` — run_phase1 ⑦ 段
```python
self._raw_meta = {"phone": phone, "email": email, "domain": domain}  # 過渡期雙寫（C3 移除）
# === [PIPE-RESUME v9 C2 START] ===
if ctx.paper_id.endswith("_shadow"):
    title = f"{title} (測試)"                       # 影子標題後綴（不入內容、不污染 Golden Diff）
ctx.raw_metadata = dict(meta)                        # 整包原始 metadata（含 confidence/source）
ctx.raw_metadata["phone"] = {"value": phone, "source": "regex", "confidence": "high"}
ctx.raw_metadata["email"] = {"value": email, "source": "regex", "confidence": "high"}
# === [PIPE-RESUME v9 C2 END] ===
```
**設計**：
- **影子後綴不污染內容**：`title` 在下游僅流向 DB title 與 Early Emit（P2 用 source_lang／P3 讀 `.md` full_text／P4 用 bilingual），故 (測試) 只影響列表顯示、不入 final_zh 內容與 Golden Diff。Flip 時隨 web_server 影子開關與本包裹一併移除（母 plan v11 Cleanup）。
- **raw_metadata 對齊 A 軌保真**：`dict(meta)` 為 Stage A 合併結構（含 candidate_name/domain + confidence/source）+ regex phone/email；供 C5 影子寫庫組 `Paper.metadata_json`（對齊 A 軌 `upsert_paper(self._metadata)`）。
- **雙寫過渡**：`self._raw_meta` 保留 → C2 後未改的 P2（`run_phase2:287` 讀 `self._raw_meta`）仍正常；C3 才切換讀 `ctx.raw_metadata` 並廢實例暫存 → 每 commit 獨立可運作可逆。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/context.py
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C2_context.py.bak
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C2_resume_pipeline.py.bak
# （baton/ 報告 + prompts/ + TODO.md 另計；無其他越界變動）
```

### §5.2 §6.2 驗收輸出
```
raw_metadata 預設= {}          # context 欄位生效
raw_metadata 可寫= {...phone...} # 可寫入
_shadow 判定= True
# grep：context.py:62 raw_metadata 欄；resume_pipeline.py:171-172 影子後綴、176-178 ctx.raw_metadata 寫入
```

pipelines + resume 測試（防 Regression）：
```
40 passed in 0.64s   # test_pipe_core + test_pipe_scaffold + test_resume_pipeline
```
全套件：
```
1 failed, 480 passed, 3 skipped in 46.35s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C2 Regression）
```

### §5.3 SOP 一致性核查（BE-Refactor）
- **logging 檢測**：C2 無新增 `logger.error`/`traceback.format_exc`（合規）。
- **database 檢測**：C2 無 DB 操作（context 純欄位、run_phase1 ⑦ 無 commit/session.begin）（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py`（A 軌）/ `web_server.py` / `paper_manager.py` / `processor/*` | [x] ✅ 未觸碰 |
| `pipelines/contracts.py` 四凍結合約 | [x] ✅ 未變更（raw_metadata 走 PipelineContext 非合約欄）|
| `pipelines/base_strategy.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更 |
| `run_phase2/3/4`（P2/P3/P4） | [x] ✅ 未觸碰（C2 僅改 run_phase1 ⑦ 段 + context 欄）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：C2 執行報告暫存 baton/、不入版控，待 C7 收官歸檔 executions/。
- **下一步**：tasks.md C3 — P2 步序與讀取對齊（`run_phase2` ①摘要→②LCC 互換 + 改讀 `ctx.raw_metadata` + 廢 `self._raw_meta`）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 二份 .bak）

# 2. git add 清單（代碼 + .bak + TODO/prompts；執行報告本體不 add）
git add pipelines/context.py
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C2_context.py.bak
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C2_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C2_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C2 — P1 + Context (raw_metadata 基建欄與影子標題後綴)

於 PipelineContext 新增 raw_metadata 基建欄位承載原始元數據，
並在 run_phase1 結束前寫入（同時保留 self._raw_meta 作為 C2 過渡雙寫）；
若檢測到 paper_id 帶有 _shadow 後綴，則在標題後綴追加 "(測試)"，
以此對齊影子列表顯示。全變更以大改版註解包裹，通過 E2E 既有驗收。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C2 代碼變更與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C2 限改 context.py + resume_pipeline.py(P1)；嚴禁自動 commit；執行報告不入 git |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C2 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C2 執行完畢——`PipelineContext.raw_metadata` 旁路欄 + `run_phase1` 寫整包 metadata（雙寫 self._raw_meta 過渡）+ `_shadow` title 加綴 (測試)；v9 C2 標記包裹。pipelines+resume 40 passed、全套件 480 passed（唯一 failed 為既存環境性、非 Regression）。
