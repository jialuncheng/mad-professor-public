# 2026-07-10 — THEME-DEDUP Tasks 提示詞

> **收到時間**：2026-07-10 05:53（UTC+8）
> **任務代號**：THEME-DEDUP
> **階段**：階段 2 — Tasks（commit 拆分、不動業務代碼）
> **相關產出檔案**：`.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md` + TODO.md 同步 🟡 WIP
> **觸發情境**：baron 同意 plan v7（全 OQ 定案）後下達任務拆分——自行設計最小可逆原子 commits；**C0 必為 Baseline**（5 支自訂主題原樣入版控、嚴禁夾正規化）；末 commit 必為 checkout；各階段產執行報告暫存 baton；文獻/工具同步硬綁定（嚴禁累積至收官）；§0.5 成果盤點置頂 + §8 六維度表 + §1 中文括號命名。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 05:53 |
| **任務代號** | THEME-DEDUP Tasks |
| **觸發 Commit** | THEME-DEDUP-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-10_THEME-DEDUP_Tasks_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：THEME-DEDUP / 工作流：FE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md（已載入）/ plan v7 / template_tasks / template_execution / 前端 SOP 手冊

### 🏢 工作目錄與修改邊界
- 唯一合法工作目錄：`.claude/worktrees/hopeful-yalow-902c50/`；嚴禁讀寫主 repo
- 修改邊界：static/themes/ 主題檔 + static/css/ 與 design/docs/ 文檔樣式表 + 新增 .claude-logs/tools/check_css_governance.py
- 鐵防線：嚴禁後端業務代碼（.py 僅限 tools/ 檢查腳本、不可碰 web_server.py）；嚴禁 static/index.html
- 執行中產出先放 baton/、checkout 才 mv + git add

### 📊 §0.5 成果盤點約束（置文件開頭·全量產出表）

### ⚙️ Commit 拆分與執行限制原則
- 不提供預設 Commit 建議（自行設計最佳最小可逆原子路線）
- **C0 必為 Baseline Commit**：5 支自訂主題（apple/corbusier/fuller/google/gropius）原樣 commit 入版控鎖基線、嚴禁含任何正規化修改
- 末 commit 必為 checkout
- 各階段（除 checkout）產執行報告 → baton/2026-07-10_THEME-DEDUP_<名稱>_<階段>_執行.md（套 template_execution）
- 文獻與工具同步硬綁定（工具 commit 伴首次測試報告；主題 commit 伴 theme-guide 對應章節；嚴禁累積至收官）
- checkout 才 mv plan/tasks/執行報告歸檔 + git add

### 📋 §8 六維度表（每 Commit：影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作細節）
### 📝 §1 TL;DR 中文括號命名（如 C0 — Theme Baseline（導入原始自訂主題））

### 🔄 同步更新 TODO.md：🔴 高優先最前新增 THEME-DEDUP 🟡 條目（C0 WIP、依賴 FE-CSS-GOV）

### 📁 產出：baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md（套 template_tasks）

### 🛑 停止：產出 tasks + TODO 後立即停止；嚴禁產 _執行.md / 動主題或 CSS 代碼 / 自發 commit·push
````

---

## 執行結果摘要

- ⚠️ **工作目錄 deviation**：提示詞稱唯一合法目錄為 worktree `hopeful-yalow-902c50`——該 worktree 已刪除（CONTEXT-1 C2 已更新 CLAUDE.md §3 為主 repo 雙視圖）→ 依 CLAUDE.md §3 v5 於主 repo 就地執行（同 RESCUE-1 C1 先例、tasks 內記載）
- ✅ 產出 tasks：6 commits（C0 Baseline → C1 Token & Base 立基 → C2 內建 4 支正規化+theme-guide 凍結規格 → C3 上傳 5 支正規化 → C4 模板+契約腳本 → checkout）；§0.5 盤點/§1 中文括號/§8 六維度/驗收條款齊備
- ✅ TODO 同步：⬜ THEME-DEDUP stub 升級為 🟡 WIP 條目（C0 WIP）

## 後續引用

C0 Run 由 baron 另下獨立提示詞觸發（階段 4·每 OP 中斷）。
