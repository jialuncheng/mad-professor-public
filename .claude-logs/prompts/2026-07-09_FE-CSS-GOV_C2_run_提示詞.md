# 2026-07-09 — FE-CSS-GOV C2 run 提示詞

> **收到時間**：2026-07-09 10:08（UTC+8）
> **任務代號**：FE-CSS-GOV C2
> **觸發 commit**：C2
> **相關產出檔案**：`static/css/{globals,layout,sidebar,content,chat,overlays}.css`（層化）+ `design/docs/{principles,css-architecture}.md` + baton 執行報告 `2026-07-09_FE-CSS-GOV_Layer_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2（Layer Cascade）——globals 宣告 `@layer reset,tokens,base,components;` 並三分包裹、5 檔整檔 `@layer components` 包裹、print+themes+自訂主題 unlayered、非 print `!important`(1 條) 個案處理、principles 補 @layer+unlayered 紀律+margin-flow、css-architecture 層序節；四鐵防線+僅首尾插入不重排。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 10:08 |
| **任務代號** | FE-CSS-GOV C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 確認 C1 執行報告後，下達第二個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C2_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C2。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 當前 Commit：C2 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：static/css 除 print 外 6 檔 + principles.md + css-architecture.md；嚴禁後端/JS/themes。
2. print.css 與 themes/*.css 必須 unlayered。
3. 僅首行插 `@layer components {`、尾行插 `}`；嚴禁重排既有縮排。
4. 版控：C2 git 追蹤 6 css + 2 docs + 8 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 8 檔 → archive/2026-07-09_FE-CSS-GOV_C2_*.bak
2. globals 首行 `@layer reset, tokens, base, components;`；內容三分包 reset/tokens/base；5 檔整檔 `@layer components { }` 包裹
3. 消除非 print `!important`（原 index.html:1260 display:none·現於 layout.css）：提升同層特異度替代並移除；不可行則保留+css-architecture 白名單記錄
4. 文獻：principles 補 @layer 層序+主檔系 unlayered 禁令+作用域前綴+**margin-flow 模型**；css-architecture 層序節
5. 驗收：tasks §6.2（層宣告=1、五檔 wrap、print/themes unlayered、rail 收合+主題切換+自訂主題上傳）

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C2 → ✅；C3 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_Layer_C2_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 6 css + 2 docs + 8 .bak；msg /tmp/FE-CSS-GOV_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C3 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：globals `@layer reset,tokens,base,components;`+三分包裹、layout/sidebar/content/chat/overlays 整檔 components 包裹、print+themes unlayered、非 print `!important` 個案處置、principles 三節（@layer/unlayered/margin-flow）+ css-architecture 層序節
- §6.2 驗收：層宣告=1、五檔 wrap grep、print/themes unlayered=0、brace 守恆
- 是否 commit / push：否（baron 手動）；⚠️ rail 收合/主題切換/自訂主題上傳 E2E 屬 baron 核查

## 後續引用

C3（Theme Dedup）由 baron 另下獨立提示詞觸發。
