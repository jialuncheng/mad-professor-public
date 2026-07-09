# 2026-07-09 — FE-CSS-GOV C1 run 提示詞

> **收到時間**：2026-07-09 09:48（UTC+8）
> **任務代號**：FE-CSS-GOV C1
> **觸發 commit**：C1
> **相關產出檔案**：`static/css/{globals,layout,sidebar,content,chat,overlays,print}.css`（新 7）+ `static/index.html`（CSS 遷出+7 link）+ `design/docs/css-architecture.md`（新）+ `design/docs/README.md` + baton 執行報告 `2026-07-09_FE-CSS-GOV_Split_C1_執行.md`
> **觸發情境**：baron 確認 tasks 後下達 C1（File Split）——inline `<style>`（1,354 行）**零改寫等價**拆 7 關注點檔、`<link>` 序載入、對帳（partition+brace 平衡+`{` 守恆）；docs 配套 css-architecture.md 初版+README；四鐵防線（JS 邏輯/DOM id/27+ 契約 class/渲染管線）。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 09:48 |
| **任務代號** | FE-CSS-GOV C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 確認 tasks 規格，下達第一個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C1_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 當前 Commit：C1 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / plan_v1（v2）/ tasks / FE SOP / static/index.html / design/docs/README.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：index.html（CSS 遷出+link）/ 新增 static/css/ 7 檔 / 新增 css-architecture.md / 改 README.md；嚴禁後端 Python 與 JS 邏輯。
2. 零改寫等價搬遷：嚴禁改任何 CSS 規則/選擇器/屬性值；7 檔選擇器總量+代碼量＝原 inline 等價。
3. 版控限制：C1 git 追蹤僅 index.html + README + 7 css + css-architecture + 2 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 index.html + README.md → archive/2026-07-09_FE-CSS-GOV_C1_*.bak
2. CSS 等價拆分：建 static/css/、依 tasks §4.1 錨段映射剪貼至 7 檔、index.html `<style>`→7 `<link>`（globals 首/print 末/#theme-link 殿後）
3. 文獻配套：css-architecture.md 初版（七檔職責表+載入序+歸屬決策樹）+ README 目錄連結
4. 驗收：tasks §6.1（選擇器對帳、三軌×4 主題 smoke）

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C1 → ✅；C2 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_Split_C1_執行.md`（baton、不入 git）；§1–§8（§5 附 SOP §4 自評）。
- §8：git add 上列 12 檔；msg /tmp/FE-CSS-GOV_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C2 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：inline CSS 零改寫拆 7 檔（腳本切分+三重不變式對帳：partition/brace 平衡/`{` 守恆）、index.html 7 link 載入序、css-architecture.md 初版+README
- §6.1 驗收：`<style>`=0、7 檔、對帳等價、node --check script 未傷
- 是否 commit / push：否（baron 手動）；⚠️ 三軌×4 主題視覺 E2E 屬 baron 核查

## 後續引用

C2（Layer Cascade）由 baron 另下獨立提示詞觸發。
