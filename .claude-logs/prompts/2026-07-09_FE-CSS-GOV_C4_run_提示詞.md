# 2026-07-09 — FE-CSS-GOV C4 run 提示詞

> **收到時間**：2026-07-09 10:31（UTC+8）
> **任務代號**：FE-CSS-GOV C4
> **觸發 commit**：C4
> **相關產出檔案**：`static/css/{globals,layout,content,chat}.css`（B 類 13 元件級變數遷檔）+ `design/docs/css-architecture.md`（Token 歸屬表）+ baton 執行報告 `2026-07-09_FE-CSS-GOV_Tokens_C4_執行.md`
> **觸發情境**：baron 確認 C3 執行報告後下達 C4（Token Slimming）——globals `:root` B 類 13 元件級變數（`--btn-*`×6/`--gap-btn-*`×3/`--toolbar-h`/`--rail-w`/`--chat-pad-x`/`--pad-panel`）剪下遷至各消費元件檔頂 `:root`（依 grep 消費對象核定）、包 `@layer components`、加「元件級·非主題調校面」註；globals `:root` 僅留 A 類全域 token；變數名/值 100% 不變；css-architecture 補 Token 歸屬表；四鐵防線（嚴禁 themes/index.html/JS/py）。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 10:31 |
| **任務代號** | FE-CSS-GOV C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 確認 C3 執行報告後，下達第四個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C4_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C4。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 當前 Commit：C4 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan_v1 / tasks / 前端 SOP 手冊 /
static/css/{globals,layout,content,chat}.css / design/docs/css-architecture.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：static/css/{globals,layout,content,chat}.css + css-architecture.md；嚴禁後端/JS/themes/index.html。
2. 變數名稱與值零改動：遷移 B 類 100% 保持原名原值（防 themes/JS/CSS 解析斷裂）。
3. 版控：C4 git 追蹤 4 css + 1 docs + 5 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與變數物理搬遷
1. 備份 5 檔 → archive/2026-07-09_FE-CSS-GOV_C4_*.bak
2. 元件級變數局部化：從 globals `:root` 剪下 B 類 13 變數（tasks L115-116）→ 遷各消費元件檔頂 `:root`（layout：btn×6+gap×3+toolbar-h+rail-w；chat：chat-pad-x；content：pad-panel，依 grep 實核）；元件檔頂 `:root` 包 `@layer components { }` 防洩露 + 「元件級·非主題調校面」註；globals `:root` 只留 A 類全域 token
3. 文獻：css-architecture 新增「Token 歸屬表」（A/B 類定義位置 SSOT 地圖）
4. 驗收：tasks §6.4；全網頁 E2E 按鈕/工具列/聊天框間距視覺零變

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C4 → ✅；C5 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_Tokens_C4_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 4 css + css-architecture + 5 .bak；msg /tmp/FE-CSS-GOV_C4_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C5 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：globals `:root` B 類 13 元件級變數遷至消費元件檔頂 `:root`（包 @layer components + 註）、globals 僅留 A 類、變數名/值零改、css-architecture Token 歸屬表
- §6.4 驗收：globals :root 僅 A 類、各變數唯一定義、var() 解析零破、grep 對帳
- 是否 commit / push：否（baron 手動）；⚠️ 按鈕/工具列/聊天框間距視覺 E2E 屬 baron 核查

## 後續引用

C5（Sidebar Scope）由 baron 另下獨立提示詞觸發。
