# PIPE-RESUME C5 — Shadow DB Fidelity 執行報告

---

**任務代號**：PIPE-RESUME C5（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C5
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C5)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C4 後；`web_server.py` `run_pipeline_shadow` C8-hotfix 影子寫庫的 `meta_dict` 僅含最小 title + translated_abstract，DB `metadata_json` 保真不足（履歷 candidate_name/domain/phone/email 未寫入）。
- **完成狀態**：C5 改影子寫庫 `meta_dict` **優先讀 `ctx.raw_metadata`（C2 P1 寫入的整包原始 metadata）** → `dict(ctx.raw_metadata)` 組 `Paper.metadata_json`（對齊 A 軌 `upsert_paper(self._metadata)` 保真）；`title` 沿用 `ctx.ingestion.title`（已自帶 (測試)、C2）；`translated_abstract` 補入；**`ctx.raw_metadata` 為空時防禦性 fallback** 退回最小 meta_dict。`# === [PIPE-RESUME v9 C5 START/END] ===` 包裹（疊於 C8-hotfix 內）。**僅呼叫既有 `upsert_paper`、無裸 commit**；A 軌 `run_pipeline` 本體 byte 不動。

> **測試狀態**：C5 確定性失敗 **0 個新增**——穩定 3 失敗＝1 環境性（`test_settings_log_format_default_auto`）+ 2 C3 carryover（`_raw_meta`、待 C6）。另觀察到 `test_tiling_paragraph.py` 在**全套件負載下偶發 flaky**（兩次全套件跑各失敗**不同**的 tiling 子測試、隔離整檔 7 passed），與 C5（web_server 影子區塊）**零關係**、屬既存環境性 flaky（詳 §5.3）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C5 | `run_pipeline_shadow` 影子寫庫改讀 `ctx.raw_metadata` 組 metadata_json（保真）+ title 沿用 + fallback | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C5_web_server.py.bak` | `run_pipeline_shadow` C8-hotfix 區塊 meta_dict 改讀 ctx.raw_metadata + fallback（v9 C5 標記）|

> ⚠️ `.bak` 須在 C5 `git add` 清單（§8）。**執行報告本體不 git add**（依指令）。

---

## §4 修法說明

### §4.1 `web_server.py` `run_pipeline_shadow` — 影子寫庫保真（v9 C5 標記、疊於 C8-hotfix）
```python
# === [PIPE-RESUME v9 C5 START] ===
_title_val = ctx.ingestion.title if ctx.ingestion else paper_id_shadow   # 已自帶 (測試)（C2）
_tabs_val = ctx.glossary_ready.translated_abstract if ctx.glossary_ready else ''
if ctx.raw_metadata:
    meta_dict = dict(ctx.raw_metadata)                       # 整包原始 metadata → metadata_json 保真
    meta_dict['title'] = {'value': _title_val, 'source': 'pipeline', 'confidence': 'high'}
    meta_dict['translated_abstract'] = {'value': _tabs_val, 'source': 'pipeline', 'confidence': 'high'}
else:
    meta_dict = { 'title': {...}, 'translated_abstract': {...} }  # 防禦性 fallback（保 title 顯示）
# === [PIPE-RESUME v9 C5 END] ===
paper_manager.upsert_paper(str(OUTPUT_DIR), owner_id, paper_id_shadow,
    {...final_paths...}, metadata=meta_dict, domain=..., doc_type=doc_type,
    original_filename=f"{original_filename or paper_id} (測試)")
```
**設計**：
- **保真**：`dict(ctx.raw_metadata)`（C2 寫入：candidate_name/domain/phone/email + confidence/source）→ `Paper.metadata_json`，對齊 A 軌 `upsert_paper(self._metadata)`。
- **title 沿用**：覆寫 `meta_dict['title']` 為 `ctx.ingestion.title`（已含 (測試)），確保前端列表顯示帶測試標記。
- **fallback**：`ctx.raw_metadata` 空（極端/非 resume 路未寫）→ 退回最小 meta_dict（守衛）。
- **database SOP**：僅組 dict + 呼叫既有 `upsert_paper`（內部自管 session/交易）；**本區塊無裸 `.commit()`/`SessionLocal().begin()`**；寫庫不含 LLM/Embedding。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M web_server.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C5_web_server.py.bak
# （baton/ 報告 + prompts/ + TODO.md 另計；唯一 .py 變動＝web_server.py）
```

### §5.2 §6.5 驗收 + SOP
```
web_server.py 語法 OK
grep ctx.raw_metadata：:655 if ctx.raw_metadata / :656 dict(ctx.raw_metadata)
v9 C5 新增區塊：無裸 commit / SessionLocal()/session.begin（✅ 僅組 dict、寫庫委派 upsert_paper）
test_pipe_scaffold：5 passed
```

### §5.3 全套件（含 flaky 釐清）
```bash
$ pytest tests/ -q   （兩次）
# 第一次：4 failed —— env + 2 C3 carryover + test_tiling_paragraph::test_sentence_level_when_under_threshold
# 第二次：4 failed —— env + 2 C3 carryover + test_tiling_paragraph::test_env_override_paragraph_threshold（不同子測試）
$ pytest tests/test_tiling_paragraph.py -q  → 7 passed（隔離整檔通過）
$ pytest tests/test_tiling_paragraph.py::test_sentence_level_when_under_threshold → 1 passed（隔離通過）
```
**flaky 裁定**：`test_tiling_paragraph.py`（MODEL-3 tiling，每測試耗時 ~14s）在**全套件負載下偶發失敗**——兩次全套件跑失敗的是**不同**子測試、隔離整檔/單測皆通過 → **負載/時序型 flaky、與 C5（web_server 影子區塊）零關係**、屬既存環境性。**C5 唯一 .py 改動為 web_server，與 tiling 無任何耦合**（grep `web_server|raw_metadata|ctx.` 於 test_tiling_paragraph.py 0 命中）。
**C5 確定性失敗 = 0 新增**；穩定失敗＝1 環境性（log_format）+ 2 C3 carryover（_raw_meta、待 C6）。

### §5.4 SOP 一致性核查（BE-Refactor）
- **logging 檢測**：C5 v9 區塊無新增 `logger.error`/`traceback.format_exc`（合規）。
- **database 檢測**：C5 v9 區塊無裸 `.commit()`/`SessionLocal().begin()`；寫庫委派既有 `upsert_paper`（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| A 軌 `run_pipeline`（web_server.py）本體 | [x] ✅ byte 不動（C5 僅改 C8-hotfix 影子區塊）|
| `pipeline_core.py` / `paper_manager.py`（僅呼叫 upsert_paper）/ `processor/*` | [x] ✅ 未觸碰 |
| `pipelines/*`（context/resume_pipeline/contracts 等）| [x] ✅ 未變更（C5 僅讀 ctx.raw_metadata）|
| `models.py` / `db.py` | [x] ✅ 未觸碰（寫庫委派 upsert_paper）|
| `tests/*` | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：C5 執行報告暫存 baton/、不入版控，待 C7 收官歸檔。
- **下一步**：tasks.md C6 — Unit Tests（追加 v9 契約測試；**修復 C3 的 2 個 _raw_meta 測試紅燈**、改用 ctx.raw_metadata）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（代碼 + .bak + TODO/prompts；執行報告本體不 add）
git add web_server.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C5_web_server.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C5_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C5_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C5_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C5 — Shadow DB Fidelity (影子寫庫讀 raw_metadata 保真)

於 web_server.py 的影子測試寫庫區塊中，改由 ctx.raw_metadata 讀取並組裝
完整的 metadata_json 寫入 DB，藉此對齊 A 軌資料庫保真度；同時將 title 沿用
P1 已加綴 "(測試)" 的值。全變更以大改版註解包裹，無裸 commit 交易。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C5 代碼變更與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C5 限改 web_server.py 影子區塊；嚴禁動 A 軌/自動 commit；執行報告不入 git；無裸 commit |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C5 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C5 執行完畢——`run_pipeline_shadow` 影子寫庫改讀 ctx.raw_metadata 組 metadata_json（對齊 A 軌保真）+ title 沿用 ctx.ingestion.title（含 (測試)）+ 空值 fallback；無裸 commit、A 軌不動。確定性失敗 0 新增（穩定 1 環境性 + 2 C3 carryover）；test_tiling_paragraph 全套件偶發 flaky 經查與 C5 零關係（隔離 7 passed、每跑失敗子測試不同）。
