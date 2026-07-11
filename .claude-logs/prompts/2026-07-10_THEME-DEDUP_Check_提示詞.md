# 2026-07-10 — THEME-DEDUP Check 提示詞

> **收到時間**：2026-07-10 07:41（UTC+8）
> **任務代號**：THEME-DEDUP Check（checkout 收官）
> **相關產出檔案**：TODO 雙層結案 + baton 歸檔（plan/tasks/C1–C4 報告）+ `executions/2026-07-10_THEME-DEDUP_checkout_執行.md`
> **觸發情境**：C4 ship 完畢、baron 下達 Conformance 驗收與 checkout 收官——五維度驗收（plan §2 目標 U1-U8 對照表／tasks §6 驗收／不可動〔含 apple/google chrome 原樣〕／提示詞歸檔+版控稽核／msg 草稿）→ 全綠後 TODO 結案+hash 自癒 → baton 一次性 mv 歸檔 → baton 乾淨檢驗 → 直產 checkout 執行報告（含 staged 白名單自檢）→ §8 commit 指令 → 停。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 07:41 |
| **任務代號** | THEME-DEDUP Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton/ 之 C0–C4 執行報告清單（⚠️ C0 報告實不存在·見摘要） |
| **觸發情境** | C4 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）

你現在扮演 Claude Code，對 THEME-DEDUP 執行 Conformance 驗收、全合規後收官歸檔 checkout。

### ✅ Conformance 驗收流程
五維度：目標規格（plan §2·U1-U8 對照表）/ 驗收條件（tasks §6·grep+常駐腳本全綠）/ 不可動（tasks §7·尤其後端/index.html 零觸/apple-google chrome 原樣/themes unlayered）/ 提示詞歸檔與版控稽核（ls+git status·untracked 者本階段 git add）/ msg 草稿完整性（C0–C4 §8）→ 產驗收報告（🟢 收官／🔴 停）

### 🗃️ 收官自動化（全合規後）
1. TODO 更新＋hash 自癒（git log 回填 C0–C4 真實 hash、移除進行中區、索引標 ✅）
2. baton 歸檔：mv plan→plans/、tasks→tasks/、C0-C4 報告→executions/ + 逐檔 git add
3. baton 乾淨檢驗（僅剩 README+長駐）
4. 直產 checkout 執行報告（executions/·含 Conformance 總驗+staged 自檢輸出）

### 📝 §8 checkout commit 指令（逐檔 add·禁廣義；msg /tmp/THEME-DEDUP_checkout_msg.txt）
### 🛑 停止：完成後立即停；嚴禁自發 commit/push、改歸檔目錄文件
````

---

## 執行結果摘要

- ⚠️ **兩處提示詞 stale 修正**：① 讀檔清單列 `Baseline_C0_執行.md`——**實不存在**（C0 由 baron 直接 commit `2380420`、無獨立報告；C1 報告 §1 已記載此 deviation）→ C0 驗收以 git 實證替代；② §8 列 `C0_run_提示詞.md`——不存在（C0 無 run 提示詞）→ add 清單修正為實存 7 份。③ TODO 結案格式依 framework §2.5 v5 雙層結構（完整表→done_archive + 一行索引）、非提示詞所述「TODO 內新增表格」（framework 為 SSOT·同 FE-CSS-GOV 先例）。
- ✅ Conformance 五維度全綠（含常駐腳本收官重跑 EXIT 0）→ TODO 雙層結案 + C4/checkout 外全 hash 自癒 → baton 歸檔（plan+tasks+C1–C4 報告 6 檔）→ baton 乾淨 → checkout 報告直產 executions/
- THEME-DEDUP 全案結案

## 後續引用

無（全案完結）；後續若掛 hook（Q_hook 另議）／上傳 label 正名（BE 微任務）由 baron 另開。
