# 2026-07-02 — FE-PERF-1 checkout run 提示詞

> **收到時間**：2026-07-02 02:44（UTC+8）
> **任務代號**：FE-PERF-1 checkout
> **觸發 commit**：checkout
> **相關產出檔案**：`baton/…_SOP手冊_C1_執行.md` + `baton/…_WORKFLOW回填_C2_執行.md`（收官歸檔至 executions/）
> **觸發情境**：C1（`60cd126`）+ C2（`70bfb48`）ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令；五維度驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 02:44 |
| **任務代號** | FE-PERF-1 checkout |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton C1 執行報告 + baton C2 執行報告 |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-02_FE-PERF-1_checkout_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行 Conformance 驗收，全部合規後收官歸檔 + checkout。

### 📋 任務資訊
- 任務編碼：FE-PERF-1 / Plan / Tasks / C1·C2 執行報告清單

### ✅ Conformance 驗收（五維度）
目標規格（plan §2 U1–U7）/ 驗收條件（tasks §6）/ 不可動清單（tasks §7）/ 提示詞歸檔與版控稽核（prompts 實體 + git add）/ msg.txt 草稿完整性 → 產驗收報告。

### 🗃️ 收官自動化
1. 更新 TODO.md：移至 ✅ 已完成、新增 DOC-Refactor 完成表、hash 自癒（C1/C2 真實 hash + 殘留佔位）、active 移除、索引標 ✅。
2. mv baton 過程檔 → plans//tasks//executions/ + git add。
3. 確認 baton/ 僅剩 README.md。

### 📝 §8 checkout 命令
git add prompts（Tasks/C1/C2/checkout）+ TODO.md；commit message /tmp/FE-PERF-1_checkout_msg.txt；baron 手動 commit。

### 🛑 停止指令
完成 TODO 更新、baton 搬移、輸出 checkout 命令後立即停止。嚴禁：自發 git commit/push / 改已歸檔目錄 / 改業務代碼。
````

---

## 執行結果摘要

- ✅ 完成狀態：Conformance 五維度全綠 → TODO 結案（C1 `60cd126` / C2 `70bfb48` 回填）+ baton 一次性歸檔 + §7.2 純 DOC 豁免
- baton：本任務 4 過程檔 mv → plans//tasks//executions/、baton 僅剩 README.md
- 是否 commit / push：否（baron 手動、§8 提供草稿）

## 後續引用

FE-PERF-1 全案結案；稽核 7 條之實修屬另案（未觸發）。
