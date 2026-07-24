# FITZ-HOTFIX-5 Checkout 執行報告 — 成果收官歸檔

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-HOTFIX-5 Checkout |
| **工作流類別** | BE-Hotfix（收官階段） |
| **狀態** | Completed (Checkout)（Git hash 待 baron 回填） |
| **HOTFIX-5 hash** | `000ac52` |
| **執行日期** | 2026-07-24 |

---

## §1 Conformance 驗收結果

| 維度 | 規格 | 結果 | 證據 |
|---|---|---|---|
| **P3 出口補中和** | `run_phase3` 尾段、扉頁 prepend 前中和 zh_text/en_text | 🟢 | litedoc:1161·`test_section_mode_revived_bare_tags_neutralized` |
| **扉頁豁免** | `paper-header-meta` div 未被反引號包裹 | 🟢 | `test_header_meta_div_exempt`（zh+en） |
| **冪等·行數不變** | 重跑相等·前後行數全等·不誤傷 `a<b` | 🟢 | `test_neutralize_idempotent_and_line_invariant` |
| **whole 模式對稱** | zh/en 雙側 body 皆補中和 | 🟢 | `test_whole_mode_both_sides_neutralized` |
| **測試全綠** | 基線 1021+ 零新 fail | 🟢 | **1025 passed, 3 skipped** |
| **不可動清單** | K1 本體/image_filter/fitz_processor/md_cleaner/section_engine/ingestion_engine/rag_indexer/前端 | 🟢 | `b783824..HEAD` 僅動 litedoc+test+2 bak |
| **SOP §5** | logging exc_info / 無裸 commit | 🟢 | 無 error/exception·無 `.commit()` |
| **提示詞歸檔** | run/Check | 🟢 | 實 2 份就位 |

**驗收結論**：全數 🟢 合規，准予收官。

**跨 Phase 豁免**：FITZ-HOTFIX-5 屬 litedoc P3 **單一階段內**之出口補中和（承 P1 K1、同軌），非 producer/consumer 跨 Phase 資料 handoff，依 WORKFLOW_SOP §7.2 得豁免跨 Phase 整合測試。

## §2 提示詞歸檔稽核

```
$ ls .claude-logs/prompts/ | grep "FITZ-HOTFIX-5"
2026-07-24_FITZ-HOTFIX-5_Check_提示詞.md
2026-07-24_FITZ-HOTFIX-5_run_提示詞.md
```

- 實 **2** 份（run/Check）全部就位、全數納入 checkout git add。

## §3 baton 歸檔確認

**mv 搬移（Phase 3 一次性、標準 `mv` 非 `git mv`）**：

| 來源（baton/） | 目的地 |
|---|---|
| `..._FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md` | `.claude-logs/hotfixes/` |
| `..._FITZ-HOTFIX-5_執行.md` | `.claude-logs/executions/` |

```
$ ls .claude-logs/baton/ | grep FITZ-HOTFIX-5
（無輸出——本案任務檔已全數歸檔、baton 僅餘長駐 spec 與影子 PDF）
```

## §4 對 baron §8 清單之更正（留痕）

Checkout 白名單依實際 git 狀態校正（CHECKOUT-GUARD 白名單鐵律：declared == staged）：

1. **路徑更正**：baron §8 之裸 `TODO.md`／`archive/TODO_done_archive.md` → 實為 `.claude-logs/TODO.md`／`.claude-logs/archive/TODO_done_archive.md`。
2. **剔除 2 `.bak`**：2 個 `.bak` 已於 **HOTFIX-5(`000ac52`) commit 落地**（`git ls-files` 確認 tracked、`b783824..HEAD` diff 含之）→ checkout 不再重複 `git add`（否則產生無 staged 條目之空宣告、破壞 declared==staged）；審計存檔已在版控中。
3. **剔除代碼檔**：`pipelines/litedoc_pipeline.py`／`tests/test_litedoc_pipeline.py` 已於 HOTFIX-5 落地 → 不在 checkout 集。
4. **剔除跨任務髒檔**：`SEC-HARDEN`/`SOP-COMPLY`/`PROJECT-REVIEW` 三提示詞屬他任務未追蹤/修改檔 → 逐檔顯式 add、嚴禁 `git add .claude-logs/prompts/` 掃入。

## §5 staged-set 自檢（`git diff --cached --name-only` 實貼）

（見下方終端輸出——須完全等於 §7 宣告之 8 檔白名單，多一檔／少一檔即停。）

## §6 不可動清單遵守

- [x] `b783824..HEAD`（HOTFIX-5 commit）僅動 `litedoc_pipeline.py`+測試+2 `.bak`；`_neutralize_inline_html` 本體/K1 P1 接線/K2/K3/U1-U6/image_filter/fitz_processor/md_cleaner/section_engine/ingestion_engine/rag_indexer/前端/A 軌**零改**。
- [x] 收官階段純文件搬移 + TODO/archive/INDEX 治理更新，零業務代碼改動。

## §7 銜接（baton 消化 → commit 映射）

| 歸檔檔 | 對應 commit |
|---|---|
| `hotfixes/..._hotfix.md` | checkout（待 baron 回填） |
| `executions/..._執行.md` | checkout（內容對應 HOTFIX-5 `000ac52`） |
| `executions/..._checkout_執行.md` | checkout |

**checkout 宣告白名單（8 檔）**：

```
.claude-logs/hotfixes/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md
.claude-logs/executions/2026-07-24_FITZ-HOTFIX-5_執行.md
.claude-logs/executions/2026-07-24_FITZ-HOTFIX-5_checkout_執行.md
.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-5_run_提示詞.md
.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-5_Check_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
```

## §8 baron 執行命令

```bash
# 1. baton 搬移已完成（報告 §3 已列出）；2 .bak 與代碼已於 HOTFIX-5 落地、checkout 不重複 add

# 2. git add 歸檔清單（8 檔·⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`）
git add .claude-logs/hotfixes/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md
git add .claude-logs/executions/2026-07-24_FITZ-HOTFIX-5_執行.md
git add .claude-logs/executions/2026-07-24_FITZ-HOTFIX-5_checkout_執行.md
git add .claude-logs/prompts/2026-07-24_FITZ-HOTFIX-5_run_提示詞.md
git add .claude-logs/prompts/2026-07-24_FITZ-HOTFIX-5_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-5_checkout_msg.txt）

# 4. baron 手動執行（先核 git diff --cached --name-only == 8 檔白名單）
git commit -F /tmp/FITZ-HOTFIX-5_checkout_msg.txt
```
