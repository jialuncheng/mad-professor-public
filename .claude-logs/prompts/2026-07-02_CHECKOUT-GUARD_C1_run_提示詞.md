# 2026-07-02 — CHECKOUT-GUARD C1 run 提示詞

> **收到時間**：2026-07-02 16:38（UTC+8）
> **任務代號**：CHECKOUT-GUARD C1
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/ref/WORKFLOW_SOP.md`（§3 立鐵律）+ baton 執行報告 `2026-07-02_CHECKOUT-GUARD_Rule_C1_執行.md`
> **觸發情境**：baron 確認 tasks 後下達 C1（Rule Authoring）執行指令；WORKFLOW_SOP §3 新增「收官 git-add 白名單鐵律 + checkout 執行報告鐵律」+ §99.2 v6，五類定義本體零改、.bak 備份、baton 過程檔嚴禁 git add。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 16:38 |
| **任務代號** | CHECKOUT-GUARD C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md |
| **觸發情境** | baron 確認 tasks 規格，下達第一個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-02_CHECKOUT-GUARD_C1_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼：CHECKOUT-GUARD / 當前 Commit：C1 / 工作流：DOC-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / plan_v1 / tasks

### 🛠️ 執行命令與檔案限制
1. 物理防線：修改目標＝`.claude-logs/ref/WORKFLOW_SOP.md`。
2. 測試防線：執行 tasks §6.1（新增兩鐵律、五類定義本體零改）。
3. 版控限制：C1 git 追蹤僅 WORKFLOW_SOP.md + .bak；baton 過程檔嚴禁 git add、不列入 §8。

### 💾 備份規則
`cp .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak`

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C1 → ✅；C2 → 🟡 WIP。
- git log 掃描，將 TODO「待 baron 回填」佔位替換為真實 hash。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_Rule_C1_執行.md`（baton、不入 git）；套 template_execution；含 §1–§8。
- §8：git add WORKFLOW_SOP.md + .bak；commit message /tmp/CHECKOUT-GUARD_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C2 / 改未列入細節的檔 / 自發 git commit / push。
````

---

## 執行結果摘要

- ✅ 完成狀態：WORKFLOW_SOP §3 新增「收官 git-add 白名單鐵律 + checkout 執行報告鐵律」+ §99.2 v6
- §6.1 驗收：兩鐵律命中、禁廣義 add + staged 自檢關鍵字、checkout 報告鐵律、五類定義 §1.1-§1.5 未動 全綠
- 改動檔案數：1 修改（WORKFLOW_SOP.md）+ 1 備份（.bak）；baton 執行報告 1（不入 git）
- 是否 commit / push：否（baron 手動、§8 提供草稿）

## 後續引用

C2（三模板落地）由 baron 另下獨立提示詞觸發。
