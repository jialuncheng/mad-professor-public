# PIPE-INGEST-FITZ C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：PIPE-INGEST-FITZ C_CHECKOUT
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/plans/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md`（v2、已歸檔）
**次級參考**：`.claude-logs/tasks/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆）。

- **目標規格（plan v2 §2 八項）**：FitzProcessor `PDFParser` 第二 impl＋MinerU 同形 .md 硬契約（`\n\n`/`#`/`##`/圖 PNG-JPEG `page_{page_idx}_{xref}` 防衝突/座標閱讀序/跨頁頂底帶剝除）（C1）／meta 純正文**零 `fitz.metadata`**（AST 測試守門）／連字修復雙閘＋行數不變式（C2）／litedoc P1 中位數閘門 fail-open＋②'修復步接線、③-⑦ 零動（C3）／三常數 env 可調、flag off byte 等價／範圍圍籬（A 軌、他路零碰）／零新依賴——全數 ✅。
- **測試計畫（tasks §6）**：各 commit 驗收 grep 全實貼；831→847→869→875 passed、逐 commit 0 failed；checkout 階段 fresh 重跑 **875 passed, 3 skipped** 再確認。
- **§7.2 跨 Phase 整合測試（Checkout 必驗）**：`tests/test_litedoc_pipeline.py::test_seam_fitz_ingest_key_changing_integration` **存在且通過**——實體 born-digital PDF（H1＋連字損毀＋跨頁頁首 URL＋400×300 圖）→ 真 FitzProcessor → 真 MarkdownCleaner → 真 repair（行數不變式斷言）→ **修復前行號建判型 sidecar** → 真 `_build_tiles`（真 ingestion_engine＋image_filter＋tiling bypass）：連字已修、頁首已剪、title 行界分離未移位、圖穿透 image_filter KEEP、正文零損。**正面達標、無需豁免**（key-changing＝真實 PDF→md 轉換）。
- **不可動清單**：C1-C3 §6 全項打勾（`pdf_processor`/`md_cleaner`/`resume`/`slide` 四檔 git diff 零；P1 ③-⑦、cover-prompt 純正文、`classify_source_lang` 零動；零 `fitz.metadata`；零新依賴）。
- **SOP 一致性核查**：三 commit 雙 grep 全數合規（logging 零違規 `logger.error`、新增 warning 皆含 `exc_info=True`；本案全程零 DB）。
- **提示詞歸檔稽核**：tasks／C1-C3 run／Check **5 份俱在** ✅（另 plan／review 2 份依收官前例併入版控、共 7 份）。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor（Fitz 直抽處理器） | `3cc3850` |
| C2 | Ligature Repair（連字修復純函式） | `ff7bf3f` |
| C3 | Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線） | `801f969` |
| C_CHECKOUT | 收官歸檔（本 commit） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：plan → `plans/`、tasks → `tasks/`、C1-C3 執行報告 → `executions/` ×3。

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec〔後續 LANG-DETECT／PIPE-SYNC-5 種子〕／litedoc_shadow_artifacts 與樣本 PDF／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**16 檔**（15 檔先行 staged＋本報告）；`.bak` ×4（C3）已隨 `801f969` 入版控、本次 no-op 不入 staged（與宣告一致）；plan／review 2 份 plan 階段提示詞依前例併入：

```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-21_PIPE-INGEST-FITZ_C1_執行.md
.claude-logs/executions/2026-07-21_PIPE-INGEST-FITZ_C2_執行.md
.claude-logs/executions/2026-07-21_PIPE-INGEST-FITZ_C3_執行.md
.claude-logs/executions/2026-07-21_PIPE-INGEST-FITZ_checkout_執行.md
.claude-logs/plans/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C1_run_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C2_run_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C3_run_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_Check_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_plan_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_review_提示詞.md
.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_tasks_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/tasks/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md
```

已剔除（維持未 staged、跨任務混檔禁令）：SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）、`2026-07-10_PROJECT-REVIEW_審查_提示詞.md`（他任務）、影子 PDF 與長駐 baton 檔。

---

## §5 TODO 雙層結案

- `TODO.md`：active 條目移除；✅ 索引頂部 pointer（`3cc3850`…`801f969`、3 commits、checkout 待回填→隨下次 hash 自癒補）；類別索引新增 `### PIPE-INGEST-FITZ (✅ 已完成·born-digital 文字層快速道)`。
- `archive/TODO_done_archive.md`：頂部追加完成表格（C1-C3 hash 已填）＋修法依據＋影子 E2E 詳步驟註記。
- 歷史 hash 自癒：本 session 已回填 IMG-FILTER checkout `2e03c2c`（C1 階段）；本次掃描雙源無其他殘留佔位符。

---

## §7 銜接

- **baron 影子 E2E**（plan §8.2）：① 重傳 `SpaceX & the Sentient Sun.pdf`——後端 log 驗**閘門判定 born-digital → fitz 直抽**（路由審計行）、23 頁全文完整（無跨頁截斷）、`Pro1les`/`;rst`/`de1ning` 類連字消失、publisher=a16z（正文 URL 直抽、非 OCR `AI6Z`）；② IMG-FILTER 續效：3 垃圾 DROP／20 內容 KEEP；③ 掃描（無文字層）樣本驗閘門退 MinerU、產出鏈正常；④ `LITEDOC_FITZ_ENABLED=false` 重傳驗應急關回與現行一致。
- **後續銜接**（design spec §3.1）：**LANG-DETECT**（F4、cover-prompt +language 欄、義文進場前必做）→ **PIPE-SYNC-5 回灌案**（母 plan v10→v11、PIPE-SPEC v8→v9：ingestion_engine／build_termmap 契約章＋spec F7 門檻更正＋**本案 FitzProcessor／閘門契約新章**）。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/PIPE-INGEST-FITZ_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/PIPE-INGEST-FITZ_checkout_msg.txt`。）
