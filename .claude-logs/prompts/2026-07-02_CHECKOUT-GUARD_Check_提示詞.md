# 2026-07-02 — CHECKOUT-GUARD Check 提示詞

> **收到時間**：2026-07-02 17:37（UTC+8）
> **任務代號**：CHECKOUT-GUARD Check（checkout）
> **觸發 commit**：checkout
> **相關產出檔案**：baton C1/C2 執行報告 → 歸檔 executions/；新產 `executions/2026-07-02_CHECKOUT-GUARD_checkout_執行.md`（首次 dogfood checkout 執行報告鐵律）
> **觸發情境**：C1（Rule Authoring）+ C2（Template Propagation）ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令；五維度驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 17:37 |
| **任務代號** | CHECKOUT-GUARD Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton C1 執行報告 + baton C2 執行報告 |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-02_CHECKOUT-GUARD_Check_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行 Conformance 驗收，全部合規後收官歸檔 + checkout。

### ✅ Conformance 驗收（五維度）
目標規格（plan §2 U1–U6）/ 驗收條件（tasks §6）/ 不可動清單（tasks §7）/ 提示詞歸檔與版控稽核（prompts 實體 + git add）/ msg.txt 草稿完整性 → 產驗收報告。

### 🗃️ 收官自動化
1. 更新 TODO.md：移至 ✅ 已完成〔### 流程治理〕、新增完成表、hash 自癒〔C1/C2/checkout + 殘留佔位〕、active 移除、索引標 ✅。
2. mv baton 過程檔 → plans//tasks//executions/ + git add（逐檔）。
3. 確認 baton/ 只剩 README.md。

### 📝 §8 checkout 命令
git add prompts〔Tasks/C1/C2/Check·⚠️ 逐檔·禁廣義 add〕 + TODO.md；commit message /tmp/CHECKOUT-GUARD_checkout_msg.txt；baron 手動 commit。

### 🛑 停止指令
完成 TODO 更新、baton 搬移、輸出 checkout 命令後立即停止。嚴禁：自發 git commit/push / 改已歸檔目錄 / 改業務代碼。
````

---

## 執行結果摘要

- ✅ 完成狀態：Conformance 五維度全綠 → TODO 結案（C1/C2/checkout hash 回填）+ §7.2 純 DOC 豁免
- **首次 dogfood**：依 C1 已立之「checkout 執行報告鐵律」，產 `executions/2026-07-02_CHECKOUT-GUARD_checkout_執行.md`（含 staged 自檢輸出）
- baton：本任務 4 過程檔 mv → plans//tasks//executions/、baton 僅剩 README.md
- 是否 commit / push：否（baron 手動、§8 提供草稿）

## 後續引用

CHECKOUT-GUARD 全案結案；收官 git-add 白名單鐵律 + checkout 報告鐵律自即日對所有工作流生效。
