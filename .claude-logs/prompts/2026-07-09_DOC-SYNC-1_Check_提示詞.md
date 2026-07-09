# 2026-07-09 — DOC-SYNC-1 Check 提示詞

> **收到時間**：2026-07-09 07:59（UTC+8）
> **任務代號**：DOC-SYNC-1 Check（checkout）
> **觸發 commit**：checkout
> **相關產出檔案**：baton C1 執行報告 → 歸檔 executions/；直產 `executions/2026-07-09_DOC-SYNC-1_checkout_執行.md`
> **觸發情境**：C1（Docs Truth Sync）ship 完畢，baron 下達 Conformance 驗收與 checkout 收官；五維度驗收 + baton 一次性歸檔 + TODO 雙層結案 + 鐵律 checkout 報告（含 staged 白名單自檢 + C1 四項 deviation 裁決）。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 07:59 |
| **任務代號** | DOC-SYNC-1 Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton C1 執行報告 |
| **觸發情境** | C1 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_DOC-SYNC-1_Check_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行 Conformance 驗收，全部合規後收官歸檔 + checkout。

### ✅ Conformance 驗收（五維度）
目標規格（plan §2 U1–U5）/ 驗收條件（tasks §6）/ 不可動清單（tasks §7·尤 dropdown-popup 零碰+零代碼）/ 提示詞歸檔與版控稽核（實體+git add）/ msg.txt 草稿完整性 → 產驗收報告。

### 🗃️ 收官自動化
1. 更新 TODO + hash 自癒（C1 真實 hash + 殘留佔位；active 移除、索引標 ✅）。
2. mv baton 過程檔（plan/tasks/C1 報告）→ plans//tasks//executions/ + 逐檔 git add。
3. 確認 baton 僅剩 README + 長駐檔。
4. **直產 checkout 報告**（WORKFLOW_SOP §3 鐵律）：`executions/…_checkout_執行.md`，含 Conformance 總驗 + `git diff --cached` staged 白名單自檢輸出。

### 📝 §8 checkout 命令
git add checkout 報告 + prompts（Tasks/C1/Check·⚠️ 逐檔）+ TODO.md；msg /tmp/DOC-SYNC-1_checkout_msg.txt；baron 手動 commit。

### 🛑 停止指令
完成 TODO 更新、baton 搬移、直產報告、輸出命令後立即停止。嚴禁：自發 git commit/push / 改已歸檔目錄。
````

---

## 執行結果摘要

- ✅ 完成狀態：Conformance 五維度全綠（U1–U5；C1 四項 deviation 裁決為「同 U 目標之量測/同源修正」、准）→ baton 一次性歸檔 + TODO 雙層結案 + hash 自癒 + 鐵律 checkout 報告直產
- 是否 commit / push：否（baron 手動）

## 後續引用

DOC-SYNC-1 全案結案；FE-CSS-GOV（deep-doc：ownership map / @layer 原則 / theme-guide 契約改寫）為後續候選、地圖已對齊現況。
