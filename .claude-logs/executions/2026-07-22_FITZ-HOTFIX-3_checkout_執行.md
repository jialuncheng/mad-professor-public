# FITZ-HOTFIX-3 C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：FITZ-HOTFIX-3 C_CHECKOUT
**執行日期**：2026-07-23
**依據規劃**：`.claude-logs/hotfixes/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆）。

- **目標規格（修法 K1/K2/K3）**：
  - **K1** 同位去重——`_collect_page` per-page `seen_lines` + `dedup_key`（文字+座標+字級）；救 NHK text-stroke ×4 重繪遭 md_cleaner 浮水印誤殺；**每頁獨立不干涉跨頁 R2**（測試守衛）✅
  - **K2** chrome 線索回收——`_URL_RE`/`_assemble` 回收 `chrome_urls`/`parse` 落 `{pdf_file.stem}_source_hints.json`；litedoc `_load_source_hints` 三級 stem 定位（**paper_id 拼接零命中**）；`hints` **於 `[:_META_INPUT_CHARS]` 截斷之後拼接**（截斷窗斷言守衛）✅
  - **K3** full_text meta 歸零——`_strip_meta_source_lines` 雙判據（sidecar spans ∪ R6 值比對整行相等）；**接線 L969（K3）< L973（echo-strip）< L983（R8）**（順序斷言守衛）；圖片行歸 R8 不碰 ✅
- **測試計畫（§regression）**：HOTFIX-3 專屬 25 測試（`-k` 匹配）全綠；checkout 階段 fresh 全套件 **993 passed, 3 skipped** 再確認（基線 978 + 15）。
- **§7.2 跨 Phase 整合測試**：本 hotfix 為受災點單點修正（K1 fitz 收行去重／K2 chrome 回收與 hint 注入／K3 P3 行級淨化）；FITZ-HOTFIX-1 收官已建之 `test_seam_fitz_hotfix1_r1_to_r8_end_to_end`（真實 PDF→P1→P3 全鏈）於本次 fresh 全套件**續行通過**。**依 WORKFLOW_SOP §7.2 屬「純後端無新 code handoff」豁免**；另本案以 `test_bilingual_text_meta_symmetry`／`test_k3_precedes_echo_strip_and_r8` 正面守住對稱不變式與接線順序。
- **不可動清單**：`processor/md_cleaner.py`（浮水印規則本體）／`pipelines/image_filter.py`／`pipelines/ingestion_engine.py`／`processor/rag_indexer.py`／`pipelines/section_engine.py`／cover-prompt 六欄／`web_server.py` — **git diff 全數零** ✅；A 軌／resume／slides／HOTFIX-1 八刀／HOTFIX-2 兩刀語意零改。
- **SOP 一致性核查**：logging 僅既有 `fitz_processor:171`（C1 解析失敗、含 `exc_info=True`），K2/K3 新增 fail-open 皆 `warning + exc_info=True`；database 零 `.commit()`（本案零 DB）✅。
- **提示詞歸檔稽核**：診斷與 plan／run／Check **3 份俱在** ✅。

### ⚠️ 一處提示詞↔權威源落差（依 WORKFLOW_SOP §2 更正、承 HOTFIX-2 前例）

Check 提示詞第二步指示 `mv ... .claude-logs/tasks/`（稱「充當 tasks.md」），但 `WORKFLOW_SOP §2`（文書歸屬**唯一權威源**）明定「緊急修補紀錄 → `hotfixes/`」，且既有 **6 份 `*_hotfix.md` 全數位於 `hotfixes/`**（含上一輪 FITZ-HOTFIX-2）。依權威源置於 `hotfixes/`（與 HOTFIX-2 處置一致、留痕慣例延續）。**若 baron 另有考量欲改回 `tasks/`，一行 `mv` 即可調整。**

### ⚠️ 一處既有測試 spy 對齊（K2 純加法簽名擴充連帶）

K2 為 `_extract_litedoc_metadata` 增 `hints=""` 純加法參數；既有 C2 時序測試 `test_metadata_extraction_precedes_assemble` 之 spy 硬編單參數簽名 → 與新簽名失配。將 spy 簽名對齊為 `(self, markdown_text, hints="")`（**斷言本體零動**、僅簽名相容）。此變更含於 HOTFIX-3 commit（`8733d98`）之 `tests/test_litedoc_pipeline.py`。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3 | Overlap Dedup, Chrome Hint & Meta Zeroing（同位重繪去重、chrome 線索回收與 full_text meta 歸零） | `8733d98` |
| C_CHECKOUT | 收官歸檔（本 commit） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：
- `_hotfix.md` → **`hotfixes/`**（依 WORKFLOW_SOP §2 權威源、見 §1 落差）
- `_執行.md` → `executions/`

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC v9／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec／litedoc_shadow_artifacts／樣本 PDF 與截圖／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**9 檔**（8 檔先行 staged＋本報告）；`.bak` ×4 與**代碼/測試本體**已隨 HOTFIX-3（`8733d98`）入版控、本次 no-op 不入 staged（與宣告一致）：

```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-22_FITZ-HOTFIX-3_執行.md
.claude-logs/executions/2026-07-22_FITZ-HOTFIX-3_checkout_執行.md
.claude-logs/hotfixes/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-3_Check_提示詞.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-3_run_提示詞.md
.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-3_診斷與plan_提示詞.md
.claude-logs/prompts/INDEX.md
```

已剔除（維持未 staged、跨任務混檔禁令）：SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）、`2026-07-10_PROJECT-REVIEW_審查_提示詞.md`（他任務）、影子 PDF／截圖與長駐 baton 檔。

---

## §5 TODO 雙層結案

- `TODO.md`：✅ 索引頂部 pointer（`8733d98`、1 commit、checkout 待回填→隨下次 hash 自癒補）；類別索引 `### FITZ-HOTFIX-3`；本案單發 hotfix、**未曾進 active 區**故無須移除。
- `archive/TODO_done_archive.md`：頂部追加完成表格（HOTFIX-3 hash `8733d98` 已填）＋修法依據＋四則 ⚠️ 註（hotfix 歸屬 §2 更正／C2 spy 對齊／baron 影子 E2E 硬判／契約回灌留 PIPE-SYNC-6）。
- 歷史 hash 自癒：本 session HOTFIX-3 run 階段已回填 FITZ-HOTFIX-2 checkout `18eb19f`（雙源）；本次掃描雙源僅餘本 checkout 自身佔位符（正常、待下輪）。

---

## §7 銜接

- **baron 影子 E2E**（hotfix §驗證）：① 重傳 NHK 樣本——標題＝「ドジャース 大谷翔平 二刀流復帰戦で先頭打者HR 投げては4勝目」系譯題＋恰一個 `(測試)`、**publisher=NHK**、date=2026-05-21、authors=0（誠實空）；log 驗 `[md_cleaner] 移除浮水印` **不再命中標題**；② SpaceX 回歸——標題／21 圖／meta 各項不退化＋**`shadow_en.md` grep `MARC ANDREESSEN`／`JUN 15` 歸零**、zh/en meta 行雙零對稱（K3 治癒點）。
- **契約回灌**：K1（同位去重）／K2（chrome 線索回收＋截斷後拼接）／K3（full_text meta 歸零＋**族群鐵律「凡對 tiles 做的淨化必問 full_text」**、full_text 處理鏈順序不變式「行號基準 K3 → 文字基準 echo-strip → 圖片行 R8」）併入 **PIPE-SYNC-6** 批次——與 PIPE-INGEST-FITZ／LANG-DETECT／FITZ-HOTFIX-1 八刀／HOTFIX-2 兩刀同批回灌 PIPE-SPEC 與母 plan，**待影子 E2E 綠燈、契約穩定後開**（避免回灌後又被 hotfix 推翻）。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/FITZ-HOTFIX-3_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/FITZ-HOTFIX-3_checkout_msg.txt`。）
