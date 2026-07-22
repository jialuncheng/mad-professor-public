# FITZ-HOTFIX-2 C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：FITZ-HOTFIX-2 C_CHECKOUT
**執行日期**：2026-07-22
**依據規劃**：`.claude-logs/hotfixes/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆）。

- **目標規格（hotfix 修法 K1/K2）**：
  - **K1** 行界收窄——`_collect_header_srcs` 只計 meta 型塊 `max(end)`（L444），舊「全部塊 `max(end)`」**零殘留**；`_HEADER_META_TYPES = set(_META_TYPES) | {"title"}`（L371）**緊鄰 `_META_TYPES` 定義**、與 `mark_meta_lines` 同源（防常數漂移、測試守衛）；無 meta 型塊 → `set()`（規則③自然停用）✅
  - **K2** 對稱恢復——`_load_header_srcs` 三級定位（L674 主路 PDF stem／L676 備路 glob／`set()` fail-open）；**`paper_id` 拼 sidecar 零命中**（影子軌 `_shadow` 陷阱已避）；複用同一 `_collect_header_srcs` 注入 `make_figure_filter`、兩通道規則③必同步 ✅
- **測試計畫（hotfix §regression）**：HOTFIX-2 專屬 10 測試全通過（`-k "K1 or K2 or HeaderBoundary or SidecarLocation"` → 10 passed）；checkout 階段 fresh 全套件 **978 passed, 3 skipped** 再確認（基線 968 + 10）。
- **§7.2 跨 Phase 整合測試**：本 hotfix 為**單檔行為修正**（`litedoc_pipeline` 內 K1 判定函式 + K2 呼叫端注入），無新增跨 Phase 資料 handoff；且 FITZ-HOTFIX-1 收官已建之 `test_seam_fitz_hotfix1_r1_to_r8_end_to_end` 端到端測試於本次 fresh 全套件中**續行通過**（涵蓋 P1→P3 全鏈）。**依 WORKFLOW_SOP §7.2 屬「無新 code handoff」之豁免情形**；另本案已以 `test_bilingual_symmetry_under_rule3` 正面守住雙語對稱不變式。
- **不可動清單**：`pipelines/image_filter.py`（三規則本體/門檻/工廠簽名）／`processor/fitz_processor.py`／`pipelines/ingestion_engine.py`／`pipelines/section_engine.py`／`processor/rag_indexer.py`／`web_server.py` — **git diff 全數零** ✅；A 軌／resume／slides／book 零碰；旗標語意零改。
- **SOP 一致性核查**：logging 無 `logger.error`（K2 兩處 fail-open 皆 `warning + exc_info=True`）；database 零 `.commit()`（本案零 DB）✅。
- **提示詞歸檔稽核**：診斷與 plan／run／Check **3 份俱在** ✅。

### ⚠️ 兩處提示詞↔實況落差（依權威源更正、誠實留痕）

1. **`_plan.md` 從未存在**：Check 提示詞之強制讀檔清單與 §8 `git add` 列有
   `plans/2026-07-22_FITZ-HOTFIX-2_..._plan.md`，實查（`find` 全庫 + `git log --all`）**該檔從未建立**。
   本案為 **BE-Hotfix** 工作流——依 `WORKFLOW_SOP §1.5` 套用 `template_hotfix`、**只產一份 `_hotfix.md`**（兼 plan 與 tasks 之職），與 INDEX 診斷階段記述（「產出 `baton/..._hotfix.md`〔套 template_hotfix〕」）一致。提示詞該行係 BE-Refactor checkout 模板沿用。**處置**：staged 清單不含 plan（無檔可加）。

2. **hotfix 檔歸屬更正 `tasks/` → `hotfixes/`**：提示詞第二步指示 `mv ... .claude-logs/tasks/`，
   但 `WORKFLOW_SOP §2`（文書歸屬**唯一權威源**）明定「緊急修補紀錄 → `hotfixes/`」，
   且既有 **5 份 `*_hotfix.md` 全數位於 `hotfixes/`**（PIPE-SLIDES-HOTFIX-6／RAG-12-HOTFIX-1／
   PIPE-LITEDOC-HOTFIX-1／SEC-SECRET／GOV-PATH-FIX）；`tasks/` 內含 hotfix 字樣者皆為
   `_tasks.md` 型文件、非 `_hotfix.md`。提示詞該行亦係 BE-Refactor 模板沿用（tasks→tasks/）。
   **處置**：依權威源置於 `hotfixes/`（已對齊 5 份前例），§4 staged 清單據此列名。
   若 baron 另有考量欲改回 `tasks/`，一行 `mv` 即可調整。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-2 | Header Boundary Narrowing & Bilingual Figure Symmetry（報頭行界收窄與雙語圖片對稱） | `53feed8` |
| C_CHECKOUT | 收官歸檔（本 commit） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：
- `_hotfix.md` → **`hotfixes/`**（依 WORKFLOW_SOP §2 權威源、見 §1 落差 2）
- `_執行.md` → `executions/`
- `_plan.md` → **無此檔**（BE-Hotfix 只產 `_hotfix.md`、見 §1 落差 1）

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC v9／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec／litedoc_shadow_artifacts／v1-v3 影子樣本 PDF 與截圖／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**9 檔**（8 檔先行 staged＋本報告）；`.bak` ×2 與**代碼/測試本體**已隨 HOTFIX-2（`53feed8`）入版控、本次 no-op 不入 staged（與宣告一致）：

```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-22_FITZ-HOTFIX-2_執行.md
.claude-logs/executions/2026-07-22_FITZ-HOTFIX-2_checkout_執行.md
.claude-logs/hotfixes/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_Check_提示詞.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_run_提示詞.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_診斷與plan_提示詞.md
.claude-logs/prompts/INDEX.md
```

已剔除（維持未 staged、跨任務混檔禁令）：SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）、`2026-07-10_PROJECT-REVIEW_審查_提示詞.md`（他任務）、影子 PDF／截圖與長駐 baton 檔。

---

## §5 TODO 雙層結案

- `TODO.md`：✅ 索引頂部 pointer（`53feed8`、1 commit、checkout 待回填→隨下次 hash 自癒補）；類別索引 `### FITZ-HOTFIX-2 (✅ 已完成·報頭行界收窄與雙語圖片對稱)`；本案為單發 hotfix、**未曾進 active 區**故無須移除。
- `archive/TODO_done_archive.md`：頂部追加完成表格（HOTFIX-2 hash `53feed8` 已填）＋修法依據＋四則 ⚠️ 註（既有測試契約更新／banner 拍板甲＝保留／baron 影子 E2E 硬判／契約回灌留 PIPE-SYNC-6）。
- 歷史 hash 自癒：本 session HOTFIX-2 run 階段已回填 FITZ-HOTFIX-1 checkout `f5a3ec6`（雙源）；本次掃描雙源僅餘本 checkout 自身佔位符（正常、待下輪）。

---

## §7 銜接

- **baron 影子 E2E**（hotfix §驗證）：v3 樣本重傳——**封面大圖（cover art）與 Falcon 9 駁船降落照片回歸可見**；頭像／logo／分隔線仍被濾（規則①③兜底）；後端 log 規則③ DROP 筆數顯著下降且**不再命中內容圖**；**`final_en` 與 `final_zh` 圖片數相等**（v3 修前 en21 vs zh19、修後應相等）。
- **契約回灌**：K1（報頭行界＝meta 型塊末行）／K2（雙通道同一 header_srcs 之對稱結構性保證）併入 **PIPE-SYNC-6** 批次——與 PIPE-INGEST-FITZ／LANG-DETECT／FITZ-HOTFIX-1 八刀同批回灌 PIPE-SPEC 與母 plan，**待影子 E2E 綠燈、契約穩定後開**（避免回灌後又被 hotfix 推翻、PIPE-INGEST-FITZ 即前車之鑑）。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/FITZ-HOTFIX-2_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/FITZ-HOTFIX-2_checkout_msg.txt`。）
