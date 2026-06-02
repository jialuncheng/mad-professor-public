# GOLDEN-BASELINE OP-2 — 自動化 Regression Diff 比對腳本開發 執行報告

---

**任務代號**：GOLDEN-BASELINE OP-2
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` §8 OP-2
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：OP-1 已 commit（`3be0b0d`），`tools/golden_baseline.py` 僅有 `capture`；baron 已於其 MinerU 機器實跑 `capture --all`，五路 `golden/<doc_type>/` 三維度快照（D1_zh/D1_en/D2_rag_tree/D3_recall + manifest）齊備並入版控。無 `diff` 子命令、無比對引擎、無 `tests/test_golden_baseline.py`。
- **完成狀態**：✅ **OP-2 完整落地且全綠驗證**（不同於 OP-1 受 MinerU 阻擋——OP-2 比對引擎為純檔案運算，不需 MinerU/網路）。
  - `tools/golden_baseline.py` 新增 `diff` 子命令 + 三維度比對引擎（D1 結構樹 / D2 譯文相似度 / D3 RAG Jaccard）+ checksum 防竄改 + 影子雜訊正規化 + 紅綠燈裁決 + 雙格式報告。
  - 新建 `tests/test_golden_baseline.py`（18 pytest 全綠）。
  - **自比對歸零實測**：五路 golden vs golden 全 PASS（零偽陽性）；負向竄改候選 → 正確 FAIL。
  - 業務代碼零改動（`pipeline_core.py` / `rag_retriever.py` / `web_server.py` / `models.py` / `processor/*` 全未觸）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-2 | `golden_baseline.py` diff 三維度比對引擎 + `tests/test_golden_baseline.py`（18 pytest）+ 五路自比對歸零 PASS | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `tools/golden_baseline.py` | `.claude-logs/archive/2026-06-02_GOLDEN-BASELINE_OP-2_golden_baseline.py.bak` | 新增 `diff` 子命令 + 三維度比對引擎 + 正規化/checksum/裁決/雙格式報告 |
| 新建 | `tests/test_golden_baseline.py` | — | 比對引擎單元測試 18 項（合成資料、不需 MinerU） |
| 新建 | `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md` | — | OP-2 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-2 提示詞 + 時間排序 |
| 修改 | `.claude-logs/TODO.md` | — | OP-1 → ✅（baron 已實跑存盤）、OP-2 → ✅、OP-3 → 🟡 WIP |
| 新建（暫存 baton/） | `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md` | — | 本報告（gitignored，OP-3 收官才歸檔） |

> ⚠️ **.bak 強制納入**：`.claude-logs/archive/2026-06-02_GOLDEN-BASELINE_OP-2_golden_baseline.py.bak` 已於 §8 `git add` 清單包含（審計存檔）。

---

## §4 修法說明

### §4.1 `tools/golden_baseline.py` — diff 子命令與三維度比對引擎
依 plan v2 §2.5.2 diff 流程實作，核心設計（均為純函式、便於單元測試）：
- **正規化** `_normalize_text`：剝離 ` (測試)`／`_shadow`／時間戳（`_TS_RE`），使候選與黃金等價比對（plan v2 §2.5.2 步驟 4）。
- **D1 結構樹** `_build_structure_tree` + `_diff_d1`：萃取 heading 階層 / table 行列 / list 項數 / image alt，zh+en 雙語比對，任一結構增刪/不符即退化（plan v2 §2 U3 D1）。
- **D2 相似度** `_diff_d2`：遞迴收集 rag_tree sections 譯文，逐 Section `difflib` ratio，min < `_D2_SIM_THRESHOLD`（0.95）或 Section 數不符即退化。
- **D3 Jaccard** `_diff_d3`：逐 query 比對 top-k 命中 `content_sha256` 集合 Jaccard，< `_D3_JACCARD_THRESHOLD`（0.90）/ query 缺漏 / 命中縮減即退化。
- **裁決** `_aggregate_verdict`：全 PASS→`PASS`；任一 FAIL→`FAIL`；FAIL + `--improvement`→`IMPROVEMENT_PENDING_REVIEW`（plan v2 §2 U4 改善豁免）。
- **防竄改** `_verify_manifest`：比對前校驗 golden manifest SHA-256，不符即拋例外拒比對（plan v2 §2.5.2 步驟 2）。
- **雙格式報告**：`diff_report.json` + `diff_report.md` → `report/golden_baseline/<doc_type>_<ts>/`（plan v2 §2 U3）。
- **門檻常數**：`_D2_SIM_THRESHOLD=0.95` / `_D3_JACCARD_THRESHOLD=0.90`（plan v2 §7 Q2 保守起始值，實測校準後待 baron 核准寫死）。

```python
def _aggregate_verdict(d1, d2, d3, improvement):
    fails = [n for n, r in (("D1", d1), ("D2", d2), ("D3", d3)) if r["degraded"]]
    if not fails:
        return "PASS"
    return "IMPROVEMENT_PENDING_REVIEW" if improvement else "FAIL"
```

### §4.2 `tests/test_golden_baseline.py` — 比對引擎單元測試（18 項）
合成資料覆蓋：D1 相同/heading 刪/table 行差/alt 不符；正規化剝雜訊等價；D2 相同/Section 數不符/低相似；D3 相同/命中縮減/query 缺漏/低重疊；裁決三分支（PASS/FAIL/IMPROVEMENT）；manifest 竄改偵測；缺基準 fail-fast。**不需 MinerU / 真實 golden 快照**。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s tools/golden_baseline.py tests/test_golden_baseline.py
 M tools/golden_baseline.py
?? tests/test_golden_baseline.py
# baton/ 報告 gitignored，未列入（合規）
```

### §5.2 單元測試 + 自比對歸零（全綠）
```bash
$ ./venv/bin/python -m py_compile tools/golden_baseline.py        # compile OK

$ ./venv/bin/python -m pytest tests/test_golden_baseline.py -q
..................                                              [100%]
18 passed in 0.02s

# 自比對歸零（五路 golden vs golden → 零偽陽性）：
$ for d in academic book slides resume litedoc; do golden_baseline diff $d --candidate golden/$d; done
  academic → verdict=PASS
  book     → verdict=PASS
  slides   → verdict=PASS
  resume   → verdict=PASS
  litedoc  → verdict=PASS

# 負向驗證（竄改候選 D1 刪 heading）→ 正確紅燈：
$ golden_baseline diff resume --candidate /tmp/cand_resume   # 竄改候選 → verdict=FAIL

# 雙格式報告產出確認：report/golden_baseline/<doc_type>_<ts>/{diff_report.json, diff_report.md} ✓
```

### §5.3 既有單元測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/ -q
1 failed, 412 passed, 3 skipped in 39.83s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-2 迴歸**：該測試斷言 `settings.LOG_FORMAT` 預設為 `"auto"`，但 baron 置入的 `.env:54` 設 `LOG_FORMAT=json`，env 覆寫預設 → `'json'`。OP-2 僅改 `tools/golden_baseline.py`（新增函式）+ 新建測試檔，**未動 `settings.py` / `utils/`**（`git diff --stat HEAD -- settings.py utils/` 空），且 `test_logging_config.py` 未 import `golden_baseline`。屬既有環境配置與測試預設值落差，與本次無關。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger.error|logger.exception|traceback.format_exc" tools/golden_baseline.py`）：`logger.error(..., exc_info=True)` 於 `cmd_capture` / `cmd_diff` 各 1 處（含 exc_info=True，合規）；無 `traceback.format_exc` 手動拼接（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)" tools/golden_baseline.py`）：無命中（合規）——diff 引擎純檔案運算、零 DB 操作。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 11-stage 與 `_get_stage_output_path` | [x] ✅ 未觸碰 |
| `rag_retriever.py` `retrieve_with_context` 簽名與演算法 | [x] ✅ 未變更 |
| `delete_paper` / `list_papers` / `get_paper` API | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更（diff 零 DB 操作） |
| `web_server.py` 業務代碼 | [x] ✅ 未觸碰 |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |
| 已凍結 `golden/`（只讀比對、未覆寫） | [x] ✅ 未變更 |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-3 收官以 `mv` + `git add` 一併歸檔至 `executions/`，**OP-2 階段嚴禁移動**。
- **下一步**：tasks.md §8 OP-3（Checkout / 收官歸檔）——一次性 `mv` plan→`plans/`、tasks→`tasks/`、OP-1/OP-2/OP-3 三報告→`executions/` + `git add` + TODO ✅。
- **未來新核心接入**：`diff` 目前以 `--candidate <快照目錄>` 比對（自比對歸零已驗）；PIPE-CORE 新核心落地後，shadow 候選產物收集為同格式快照即可接入比對（plan v2 §2.5.2 步驟 3）。
- **消化歸檔之 baton 檔**：無（OP-3 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（.bak 強制納入）
git add .claude-logs/archive/2026-06-02_GOLDEN-BASELINE_OP-2_golden_baseline.py.bak
# 2. git add 清單（嚴禁包含 baton/ 下的執行報告！）
git add tools/golden_baseline.py
git add tests/test_golden_baseline.py
git add .claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/GOLDEN-BASELINE_OP-2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/GOLDEN-BASELINE_OP-2_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: GOLDEN-BASELINE OP-2 — 自動化 Regression Diff 比對腳本開發

1. 在 tools/golden_baseline.py 中實作 diff 子命令與三維度比對引擎
   （D1 結構樹 / D2 譯文相似度 / D3 RAG Jaccard）。
2. 實作 manifest checksum 防竄改、影子/(測試)/時間戳噪聲正規化、紅綠燈裁決彙總。
3. 比對輸出機器可讀 diff_report.json 與人類可讀 diff_report.md 雙格式報告。
4. 新建 tests/test_golden_baseline.py（18 pytest），覆蓋三維度比對、正規化、
   裁決三分支、checksum 竄改、缺基準 fail-fast。
5. 實測五路自比對歸零全 PASS（零偽陽性）、負向竄改候選 FAIL；既有測試零迴歸
   （唯一失敗 test_settings_log_format_default_auto 為 .env LOG_FORMAT=json 環境誘發、非本次迴歸）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 GOLDEN-BASELINE OP-2 比對引擎實作與全綠驗收，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-3 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-3 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-3 前不入版控 |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-2 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-2 執行——`tools/golden_baseline.py` 新增 `diff` 三維度比對引擎（D1 結構樹/D2 相似度 0.95/D3 Jaccard 0.90）+ 正規化 + checksum 防竄改 + 紅綠燈裁決 + 雙格式報告；新建 `tests/test_golden_baseline.py` 18 pytest 全綠；五路自比對歸零 PASS（零偽陽性）+ 負向竄改 FAIL；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發、非 OP-2）；TODO OP-1→✅（baron 已實跑存盤 commit 3be0b0d）/ OP-2→✅ / OP-3→🟡 WIP；`tools/golden_baseline.py` 修改前已備份 .bak。
