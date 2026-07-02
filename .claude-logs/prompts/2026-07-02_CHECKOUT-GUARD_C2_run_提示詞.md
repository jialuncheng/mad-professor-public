# 2026-07-02 — CHECKOUT-GUARD C2 run 提示詞

> **收到時間**：2026-07-02 16:42（UTC+8）
> **任務代號**：CHECKOUT-GUARD C2
> **觸發 commit**：C2
> **相關產出檔案**：三模板（template_prompt_for_run / template_prompt_for_check / template_execution）+ baton 執行報告 `2026-07-02_CHECKOUT-GUARD_Template_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2（Template Propagation）；三模板 §8 加「逐檔·禁廣義 add」+ check 收官新增 staged 自檢步驟 + check mandate checkout 報告；既有結構零改、3 .bak 備份、baton 過程檔嚴禁 git add。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 16:42 |
| **任務代號** | CHECKOUT-GUARD C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | .claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md |
| **觸發情境** | baron 確認 C1 執行報告後，下達第二個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-02_CHECKOUT-GUARD_C2_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C2。

### 📋 任務資訊
- 任務編碼：CHECKOUT-GUARD / 當前 Commit：C2 / 工作流：DOC-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / plan_v1 / tasks

### 🛠️ 執行命令與檔案限制
1. 物理防線：修改三模板 template_prompt_for_run / template_prompt_for_check / template_execution。
2. 測試防線：執行 tasks §6.2（三模板加註、check 新增自檢與 mandate 報告、既有結構零變更）。
3. 版控限制：C2 git 追蹤僅三模板 + 3 .bak；baton 過程檔嚴禁 git add、不列入 §8。

### 💾 備份規則
cp 三模板 → archive/2026-07-02_CHECKOUT-GUARD_C2_<檔名>.bak

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C2 → ✅；checkout → 🟡 WIP。
- git log 掃描回填「待 baron 回填」佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_Template_C2_執行.md`（baton、不入 git）；套 template_execution；含 §1–§8。
- §8：git add 三模板 + 3 .bak；commit message /tmp/CHECKOUT-GUARD_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 checkout / 改未列入細節的檔 / 自發 git commit / push。
````

---

## 執行結果摘要

- ✅ 完成狀態：三模板 §8 加「逐檔·禁廣義 add」+ check 收官新增 staged 自檢步驟 + check mandate `_checkout_執行.md`
- §6.2 驗收：run/execution §8 警語、check 自檢步驟 + mandate 報告、既有結構未動 全綠
- 改動檔案數：3 修改 + 3 備份；baton 執行報告 1（不入 git）
- 是否 commit / push：否（baron 手動、§8 提供草稿）

## 後續引用

checkout（收官歸檔）由 baron 另下獨立提示詞觸發。
