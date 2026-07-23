# FITZ-HOTFIX-4 Checkout 執行報告 — 成果收官歸檔

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-HOTFIX-4 Checkout |
| **工作流類別** | BE-Hotfix（收官階段） |
| **狀態** | Completed (Checkout)（Git hash 待 baron 回填） |
| **HOTFIX-4 hash** | `5756219` |
| **執行日期** | 2026-07-24 |

---

## §1 Conformance 驗收結果

| 維度 | 規格/要求 | 結果 | 證據 |
|---|---|---|---|
| **K1** 裸 HTML 中和 | 標籤族反引號包裹·code span 不重包·`a<b` 不誤判·行數不變·DocAnalyzer 前 | 🟢 | `_neutralize_inline_html`·`TestHOTFIX4_K1`(6)·Browsers 段落防吞 |
| **K2** 報頭集原封基準 | K3 刪行前預算 `_pristine_header_srcs`·傳 `_filter_source_figures`·None 兜底 | 🟢 | `run_phase3`·`TestHOTFIX4_K2_HeaderSrcsBasis`(3) |
| **雙語圖片對稱** | whole+section 模式 `_figs(en)==_figs(zh)`·界外圖雙側存活 | 🟢 | `TestHOTFIX4_K2_BilingualSymmetryE2E`(2) |
| **測試全綠** | 基線 1010+ 零新 fail | 🟢 | **1021 passed, 3 skipped** |
| **不可動清單** | image_filter/fitz_processor/md_cleaner/section_engine/ingestion_engine/rag_indexer/前端/A 軌 | 🟢 | git status 零改 |
| **SOP §5** | logging exc_info / 無裸 commit | 🟢 | 無 error/exception·無 `.commit()` |
| **提示詞歸檔** | run/Check | 🟢 | 實 3 份（含 plan 階段診斷書） |

**驗收結論**：全數 🟢 合規，准予收官。

**跨 Phase 豁免**：FITZ-HOTFIX-4 屬 litedoc P1（K1 清洗）+ P3（K2 過濾）**同軌內修補**，非 producer/consumer 跨 Phase 資料 handoff，依 WORKFLOW_SOP §7.2 得豁免跨 Phase 整合測試；惟 K2 仍實作雙語圖片對稱 E2E（whole+section）驗收接縫不變式。

## §2 提示詞歸檔稽核

```
$ ls .claude-logs/prompts/ | grep "FITZ-HOTFIX-4"
2026-07-23_FITZ-HOTFIX-4_診斷與plan_提示詞.md
2026-07-24_FITZ-HOTFIX-4_Check_提示詞.md
2026-07-24_FITZ-HOTFIX-4_run_提示詞.md
```

- 實 **3** 份（稽核要求 2 份 run/Check + 額外 plan 階段 `診斷與plan`）全部就位、全數納入 checkout git add。

## §3 baton 歸檔確認

**mv 搬移（Phase 3 一次性、標準 `mv` 非 `git mv`）**：

| 來源（baton/） | 目的地 |
|---|---|
| `..._FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md` | `.claude-logs/hotfixes/` |
| `..._FITZ-HOTFIX-4_執行.md` | `.claude-logs/executions/` |

```
$ ls .claude-logs/baton/ | grep FITZ-HOTFIX-4
（無輸出——本案任務檔已全數歸檔、baton 僅餘長駐 spec 與影子 PDF）
```

## §4 對 baron §8 清單之更正（留痕）

Checkout 白名單依實際 git 狀態校正（CHECKOUT-GUARD 白名單鐵律：declared == staged）：

1. **路徑更正**：baron §8 之裸 `TODO.md`／`archive/TODO_done_archive.md` → 實為 `.claude-logs/TODO.md`／`.claude-logs/archive/TODO_done_archive.md`。
2. **剔除 2 `.bak`**：2 個 `.bak` 已於 **HOTFIX-4(`5756219`) commit 落地**（`git ls-files` 確認 tracked、`505ce1e..HEAD` diff 含之）→ checkout 不再重複 `git add`（否則產生無 staged 條目之空宣告、破壞 declared==staged）；審計存檔已在版控中。
3. **剔除代碼檔**：`pipelines/litedoc_pipeline.py`／`tests/test_litedoc_pipeline.py` 已於 HOTFIX-4 落地 → 不在 checkout 集。
4. **補列漏檔**：baron §8 漏列 plan 階段 `2026-07-23_FITZ-HOTFIX-4_診斷與plan_提示詞.md`（本任務未追蹤 prompt、應一併入版控）→ 補入白名單（共 3 提示詞）。
5. **剔除跨任務髒檔**：`SEC-HARDEN`/`SOP-COMPLY`/`PROJECT-REVIEW` 三提示詞屬他任務未追蹤/修改檔 → 逐檔顯式 add、嚴禁 `git add .claude-logs/prompts/` 掃入。

## §5 staged-set 自檢（`git diff --cached --name-only` 實貼）

（見下方終端輸出——須完全等於 §7 宣告之 9 檔白名單，多一檔／少一檔即停。）

## §6 不可動清單遵守

- [x] `505ce1e..HEAD`（HOTFIX-4 commit）僅動 `litedoc_pipeline.py`+測試+2 `.bak`；image_filter/fitz_processor/md_cleaner/section_engine/ingestion_engine/rag_indexer/前端/A 軌**零改**。
- [x] 收官階段純文件搬移 + TODO/archive/INDEX 治理更新，零業務代碼改動。

## §7 銜接（baton 消化 → commit 映射）

| 歸檔檔 | 對應 commit |
|---|---|
| `hotfixes/..._hotfix.md` | checkout（待 baron 回填） |
| `executions/..._執行.md` | checkout（內容對應 HOTFIX-4 `5756219`） |
| `executions/..._checkout_執行.md` | checkout |

**checkout 宣告白名單（9 檔）**：

```
.claude-logs/hotfixes/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md
.claude-logs/executions/2026-07-24_FITZ-HOTFIX-4_執行.md
.claude-logs/executions/2026-07-24_FITZ-HOTFIX-4_checkout_執行.md
.claude-logs/prompts/2026-07-23_FITZ-HOTFIX-4_診斷與plan_提示詞.md
.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_run_提示詞.md
.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_Check_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
```

## §8 baron 執行命令

```bash
# 1. baton 搬移已完成（報告 §3 已列出）；2 .bak 與代碼已於 HOTFIX-4 落地、checkout 不重複 add

# 2. git add 歸檔清單（9 檔·⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`）
git add .claude-logs/hotfixes/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md
git add .claude-logs/executions/2026-07-24_FITZ-HOTFIX-4_執行.md
git add .claude-logs/executions/2026-07-24_FITZ-HOTFIX-4_checkout_執行.md
git add .claude-logs/prompts/2026-07-23_FITZ-HOTFIX-4_診斷與plan_提示詞.md
git add .claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_run_提示詞.md
git add .claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-4_checkout_msg.txt）

# 4. baron 手動執行（先核 git diff --cached --name-only == 9 檔白名單）
git commit -F /tmp/FITZ-HOTFIX-4_checkout_msg.txt
```
