# 2026-07-09 — FE-CSS-GOV C5 run 提示詞

> **收到時間**：2026-07-09 18:13（UTC+8）
> **任務代號**：FE-CSS-GOV C5
> **觸發 commit**：C5
> **相關產出檔案**：`static/index.html`（左欄 HTML 純加法補 `.sb-*` class）+ `static/css/sidebar.css`（ID 後代式→單級 class）+ `design/docs/{components,dom-reference,css-architecture}.md`（前綴表建置 + 左欄 class 記載）+ baton 執行報告 `2026-07-09_FE-CSS-GOV_Scope_C5_執行.md`
> **觸發情境**：baron 確認 C4 執行報告後下達 C5（Sidebar Scope）——`#sidebar`/`#sidebar-bottom`/`#paper-list`/`#folder-tree` 18 行 ID 後代選擇器收斂為 `.sb-*` 前綴單級 class；HTML 純加法補 class（原 class/id 全保留、DOM id 與 JS 契約 27+ class 零改名）；css-architecture 建前綴表 + components/dom-reference 左欄記載同步；四鐵防線（嚴禁後端/index.html L1610+ JS）。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 18:13 |
| **任務代號** | FE-CSS-GOV C5 |
| **觸發 Commit** | C5 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 確認 C4 執行報告後，下達第五個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C5_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C5。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 當前 Commit：C5 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan_v1 / tasks / 前端 SOP 手冊 /
static/index.html / static/css/sidebar.css / design/docs/{components,dom-reference,css-architecture}.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：static/index.html（限左欄 HTML class 純加法）+ static/css/sidebar.css + components/dom-reference/css-architecture.md；嚴禁後端、嚴禁 index.html L1610+ script JS。
2. DOM ID 與 JS class 零刪改：DOM id 零改；27+ JS 契約 class（.collapsed/.sb-row 等）零改名；HTML 僅「新增」單級 class 供 CSS 選擇器、不動既有屬性。
3. 版控：C5 git 追蹤 index.html + sidebar.css + 3 docs + 5 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與左欄作用域收斂
1. 備份 5 檔 → archive/2026-07-09_FE-CSS-GOV_C5_*.bak
2. 收斂左欄 ID 後代規則：審 sidebar.css 中 `#sidebar`/`#sidebar-bottom`/`#paper-list`/`#folder-tree` 18 行後代選擇器；index.html 左欄標籤純加法補 `.sb-*` 單級 class（原 class/id 全留）；sidebar.css 後代規則改 `.sb-*` 單級並刪 ID 後代式；`.sb-row` 家族沿用
3. 文獻：css-architecture 建「前綴表」登記 `.sb-*`；components/dom-reference 左欄小節 class 記載同步
4. 驗收：tasks §6.5——左欄 ID 後代式=0、JS 契約 class 命中守恆、getElementById 全解析、E2E 資料夾展開/選中/bottom popup

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C5 → ✅；C6 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_Scope_C5_執行.md`（baton、不入 git）；§1–§8。
- §8：git add index.html + sidebar.css + 3 docs + 5 .bak；msg /tmp/FE-CSS-GOV_C5_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C6 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⚠️ **執行期 baron 拍板 re-scope→C5–C7 併為一**：grep 全掃反證「36 行需收斂」為高估——chrome `#`-選擇器落五類（A 容器自身 ID／B 內容渲染白名單／C 自身狀態式／D 跨欄共用語意 class·ID-scope 正當／E 私有可收斂），**唯一該物理收斂＝E 類 `.sb-row` 6 行**；C6/C7 grep 後零乾淨收斂（全 A/B/C/D）。
- ✅ 完成狀態：`.sb-row` 卸 `#sidebar-bottom` 前綴為單級 class（HTML 免改·class 已在）+ css-architecture §5 作用域白名單全量表（A/B/C/D/E 五類 + 鐵則）+ dom-reference/components 同步；index.html/layout/content/chat/globals/themes 全零 diff
- 實際 git add 8 檔（sidebar.css + 3 docs + 4 .bak；非原 index.html+5 .bak）；D 類 `.title`/`.toolbar-actions`/`.h-title` 正當 ID-scope 保留

## 後續引用

C6/C7 已併入本 C5；下一步 = checkout 收官（本 session 續接、不中斷）。THEME-DEDUP 為收官後結構去重續集。
