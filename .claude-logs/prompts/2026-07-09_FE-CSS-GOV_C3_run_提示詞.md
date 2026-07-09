# 2026-07-09 — FE-CSS-GOV C3 run 提示詞

> **收到時間**：2026-07-09 10:29（UTC+8）
> **任務代號**：FE-CSS-GOV C3
> **觸發 commit**：C3
> **相關產出檔案**：`static/themes/{kahn,kandinsky,mies,nara}.css`（去重）+ `static/css/{content,layout,globals}.css`（承接 base/token）+ `design/docs/theme-guide.md`（契約改寫）+ baton 執行報告 `2026-07-09_FE-CSS-GOV_Theme_C3_執行.md`
> **觸發情境**：baron 確認 C2 執行報告後下達 C3（Theme Dedup）——4 主題白名單外結構屬性去重上移（同值直移 base／異值 token 化 globals tokens 層）、確保白名單外結構屬性行數歸 0、theme-guide 契約重寫（白名單+必備 token 覆寫+unlayered 優先級）、主題 unlayered 鐵律不變、僅首尾插入不重排。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 10:29 |
| **任務代號** | FE-CSS-GOV C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 確認 C2 執行報告後，下達第三個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C3_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C3。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 當前 Commit：C3 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan_v1 / tasks / 前端 SOP 手冊 /
static/themes/{kahn,kandinsky,mies,nara}.css / static/css/{content,layout,globals}.css / design/docs/theme-guide.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：static/themes 4 檔 + static/css/{content,layout,globals}.css + theme-guide.md；嚴禁後端/JS/index.html。
2. 4 主題檔嚴禁包入 @layer、必須 unlayered。
3. 版控：C3 git 追蹤 4 主題 + 3 主檔 + 1 文檔 + 8 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 8 檔 → archive/2026-07-09_FE-CSS-GOV_C3_*.bak
2. 主題結構屬性去重上移：審查 4 主題白名單外屬性（margin/padding/width/height/display/position/border-width…）；4 主題同值→直搬對應主檔 base 層並於主題刪除；4 主題異值→globals tokens 層建 CSS 變數（如 --divider-w）、主檔讀變數、主題僅留覆寫值；確保去重後白名單外結構屬性行數=0
3. 文獻：重寫 theme-guide.md（白名單〔色票/字族/外觀〕+必備 Tokens 覆寫清單+自訂主題 unlayered 優先級+開發說明）
4. 驗收：tasks §6.3；視覺 E2E 4 主題切換線寬/字級/間距 100% 等價

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C3 → ✅；C4 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_Theme_C3_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 4 主題 + 3 主檔 + theme-guide + 8 .bak；msg /tmp/FE-CSS-GOV_C3_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C4 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：4 主題白名單外結構屬性去重上移（同值直搬 base／異值 token 化）、白名單外結構屬性行數歸 0、theme-guide 契約重寫、4 主題維持 unlayered
- §6.3 驗收：白名單外結構屬性=0、token 對照、主題 unlayered=0、視覺等價
- 是否 commit / push：否（baron 手動）；⚠️ 4 主題切換線寬/字級/間距視覺 E2E 屬 baron 核查

## 後續引用

C4（Token Slimming）由 baron 另下獨立提示詞觸發。
