# FITZ-HOTFIX-1 C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：FITZ-HOTFIX-1 C_CHECKOUT
**執行日期**：2026-07-22
**依據規劃**：`.claude-logs/plans/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_plan.md`（v4、已歸檔）
**次級參考**：`.claude-logs/tasks/2026-07-21_FITZ-HOTFIX-1_..._tasks.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆）。

- **目標規格（plan v4 八刀 R1-R8）**：R1 圖框內文字排除／R2 複合 key 救標題（列印 PDF 通案）／R3 三級 `###`／R5 nav link-tiling（C1 `e8d57a6`）；R6 `meta_values` 純加法兜底＋時序前移／R7 數字短行清理（C2 `a666a11`）；R4 譯題餵 `_title_bare`／R8 P3 單點過濾＋雙語對稱（C3 `e6f3e44`）——**八刀全數落地** ✅。
- **測試計畫（tasks §6）**：各 commit 驗收 grep 全實貼；920→933→958→967→**968**（含 §7.2）逐 commit 遞增、0 failed；checkout 階段 fresh 重跑 **968 passed, 3 skipped** 再確認。
- **§7.2 跨 Phase 整合測試（Checkout 必驗）**：`tests/test_litedoc_pipeline.py::test_seam_fitz_hotfix1_r1_to_r8_end_to_end` **存在且通過**——真實 born-digital PDF（含列印頁首 chrome＋三級標題＋圖框黏字＋nav 行＋meta 行＋`53 82 Share`＋垃圾圖與內容圖）→ **真 FitzProcessor**（key-changing transform：PDF→md）→ **真 md_cleaner／連字修復／R7** → **真 `_build_tiles`（R6 meta_values）** → **真 `run_phase3`（R4/R8）** 端到端，逐項斷言八刀不變式。**正面達標、不適用豁免**（本案跨 P1↔P3 且有 md→tiles→full_text 資料 handoff）。
- **不可動清單**：C1-C3 §6 全項打勾——`processor/pdf_processor.py`／`pipeline_core`／`section_engine`／`rag_indexer`／`contracts`／`image_filter` 本體零改；**`web_server.py` git diff 零**（防重已由 SHADOW-HOTFIX-2 落地）；resume／slides／book／academic 零碰；旗標語意零改。
- **SOP 一致性核查**：三 commit 雙 grep 全數合規（新增日誌點皆為 debug 審計或含 `exc_info=True` 之 warning；全程零 DB）。
- **提示詞歸檔稽核**：tasks／C1-C3 run／Check **5 份俱在** ✅（另診斷與 plan 1 份併入版控、共 6 份）。

### ⚠️ Checkout 階段補齊 §7.2 整合測試（誠實留痕）

tasks §6.4 原規劃「§7.2 整合測試於 C3 或 Checkout 前補齊」，C3 未及（該 commit 已於 §7 銜接明記待補）。本次 Check 首先查證——`grep "def test_seam"` 確認既有三支 seam 測試（PIPE-LITEDOC C7／PIPE-INGEST-FITZ C3／LANG-DETECT）**均不涵蓋 R1-R8 新行為**。依 `WORKFLOW_SOP §7.2`「Checkout Conformance 必驗…缺此測試之多 Phase 任務**不得判 🟢 通過**」，且本案非「純文檔／外部強依賴」豁免情形，故於收官前**補寫並通過**該測試（967→968 passed）。因此本 checkout commit 含一份測試代碼變更（`tests/test_litedoc_pipeline.py` + 其 `.bak`），已於 §4 staged 清單顯式列名。

### ⚠️ 兩處 plan↔代碼落差（grep 更正、全程留痕）

1. **R4 web_server 防重**：plan v4 §2 稱「`web_server.py:776`、**無防重**」為 stale——實測 `web_server.py:775` 早由 **PIPE-RESUME SHADOW-HOTFIX-2** 落地 `endswith(" (測試)")` 守衛。真因重判為 LLM 回**後綴變體**（全形／空格差異）致半形 endswith 失配。故 R4 收斂為**單一 P3 端治本**、`web_server.py` 入不可動清單並實測零 diff（tasks §3 問題 #4 已記）。
2. **R3 連帶缺陷**：R3 落地後**既有回歸測試攔下** `_heading_sizes` 之 body 字級判定缺陷（列印 chrome 於短文件字元量可壓過真正文 → body 誤判 → 真正文被推升第三級誤判 `###`）。修法：正文字級**只由非 band 行決定**、候選字級仍由全體行枚舉（保留落頂 band 之真標題、不毀 R2）；已加 `test_body_size_from_non_band_lines_only` 守門（C1 報告 §4 詳載）。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor Refinement（Fitz 處理器標題救回與結構修復） | `e8d57a6` |
| C2 | P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理） | `a666a11` |
| C3 | P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂） | `e6f3e44` |
| C_CHECKOUT | 收官歸檔（本 commit、含 §7.2 整合測試補齊） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：plan → `plans/`、tasks → `tasks/`、C1-C3 執行報告 → `executions/` ×3。

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC v9／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec／litedoc_shadow_artifacts 與樣本 PDF／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**17 檔**（16 檔先行 staged＋本報告）；C1-C3 之 8 個 `.bak` 已隨各自 commit 入版控、本次 no-op 不入 staged（與宣告一致）；**checkout 階段新增之 §7.2 測試與其 `.bak` 顯式列入**；診斷與 plan 提示詞依前例併入：

```
.claude-logs/TODO.md
.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_checkout_test_litedoc_pipeline.py.bak
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-21_FITZ-HOTFIX-1_C1_執行.md
.claude-logs/executions/2026-07-21_FITZ-HOTFIX-1_C2_執行.md
.claude-logs/executions/2026-07-21_FITZ-HOTFIX-1_C3_執行.md
.claude-logs/executions/2026-07-21_FITZ-HOTFIX-1_checkout_執行.md
.claude-logs/plans/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_plan.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C1_run_提示詞.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C2_run_提示詞.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C3_run_提示詞.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_Check_提示詞.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_tasks_提示詞.md
.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_診斷與plan_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/tasks/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md
tests/test_litedoc_pipeline.py
```

已剔除（維持未 staged、跨任務混檔禁令）：SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）、`2026-07-10_PROJECT-REVIEW_審查_提示詞.md`（他任務）、影子 PDF 與長駐 baton 檔。

---

## §5 TODO 雙層結案

- `TODO.md`：active 條目移除；✅ 索引頂部 pointer（`e8d57a6`…`e6f3e44`、3 commits、checkout 待回填→隨下次 hash 自癒補）；類別索引新增 `### FITZ-HOTFIX-1 (✅ 已完成·fitz 路標題救回與雜訊通則)`。
- `archive/TODO_done_archive.md`：頂部追加完成表格（C1-C3 hash 已填）＋修法依據＋三則 ⚠️ 註（§7.2 補齊時點／兩處 plan↔代碼落差／baron 影子 E2E 硬判清單）。
- 歷史 hash 自癒：本 session 各 C 階段已逐次回填；本次掃描雙源無殘留佔位符。

---

## §7 銜接

- **baron 影子 E2E**（plan §8.2 硬判）：① 真跑機 log 驗 `grep "img-filter"` DROP 紀錄；② 重傳 `SpaceX & the Sentient Sun.pdf` 走影子軌——標題＝正確系譯題且**恰一個 `(測試)`**、PDF `/Title` 同步正確；結構＝`#` + `##`×4 + `###`×3（section mode、P2 摘要/滑窗/RAG 粒度回魂）；扉頁後零 meta 重播、零 `53 82 Share`/`561`、零 nav 行、零圖表黏字段落；垃圾小圖消失、內容圖含 hero 全在；③ **R8 短文靶**：另傳 <15k 短文（whole mode）驗垃圾圖同樣被濾（雙通道同享之 E2E 證）；④ 第二樣本（另一站列印 PDF）泛化 + 掃描樣本退 MinerU 回歸。
- **後續銜接**：本案八刀契約（FitzProcessor 四刀／`meta_values` 純加法／R7 清洗／R4 譯題／R8 雙語對稱不變式）待 **PIPE-SYNC-6** 一併回灌 PIPE-SPEC 與母 plan（與 PIPE-INGEST-FITZ／LANG-DETECT 契約同批、PIPE-SYNC-5 plan §9 Q1 拍板留下一波）。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/FITZ-HOTFIX-1_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/FITZ-HOTFIX-1_checkout_msg.txt`。）
