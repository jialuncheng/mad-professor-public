# 2026-07-12 — SEC-XSS C2 run 提示詞

> **收到時間**：2026-07-12 04:33（UTC+8）
> **任務代號**：SEC-XSS C2
> **觸發 commit**：C2
> **相關產出檔案**：`static/index.html`（renderMarkdownWithMath 注入消毒）+ `tests/test_sec_xss_guard.py`（追加接線守衛）+ baton 執行報告 `2026-07-12_SEC-XSS_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2（Markdown Sanitize）——`renderMarkdownWithMath` 於 `marked.parse(t)` 後、KaTeX 回填（步驟 7）前插入一行 `html = DOMPurify.sanitize(html);`；**管線原樣隨遷鐵律**（code/math/img 佔位抽取步驟 1-5 與回填步驟 7 一字不改）；守衛測試追加「源碼中 sanitize 呼叫位於 marked.parse 後、KaTeX 回填前」斷言；§6.2+§6.4 + 全套件綠燈；一處覆蓋 6 個 markdown innerHTML sink。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-12 04:33 |
| **任務代號** | SEC-XSS C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | .claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md |
| **觸發情境** | baron 確認 C1 成功，下達 C2 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-12_SEC-XSS_C2_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C2。

### 📋 任務資訊
- 任務編碼：SEC-XSS / 當前 Commit：C2 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md

### 🏢 修改邊界與限制
1. 唯一修改：static/index.html（消毒注入）+ tests/test_sec_xss_guard.py。
2. **管線原樣隨遷鐵律**：code/math/img 佔位抽取（步驟 1-5）與回填（步驟 7）一字不改；僅 marked.parse 後、KaTeX 回填前插一行消毒。
3. 版控：2 檔 + 2 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令
1. 備份 2 檔 → archive/2026-07-12_SEC-XSS_C2_*.bak
2. renderMarkdownWithMath：L323 `let html = marked.parse(t);` 後、步驟 7 回填前插 `html = DOMPurify.sanitize(html);`
3. 守衛測試追加：源碼中 marked.parse 後、KaTeX 渲染前呼叫 DOMPurify.sanitize
4. §6.2+§6.4 驗收 + 全套件綠燈；LaTeX 論文渲染不退化

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C2 → ✅；C3 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-12_SEC-XSS_C2_執行.md`（baton、不入 git）；§1–§8（§4 展示前後碼+PUA 佔位安全保留原因）。
- §8：git add 2 檔 + 2 .bak；msg /tmp/SEC-XSS_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C3 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ `renderMarkdownWithMath` L330 插 `html = DOMPurify.sanitize(html);`（marked.parse 後、KaTeX 回填前）＝一處覆蓋 6 sink；管線鐵律守恆（diff 僅 +5 行〔4 註解+1 消毒〕·步驟 1-5/7 一字不改·PUA 哨兵純文字節點保留）
- ✅ 守衛 +1 接線位置斷言（執行期修正：`katex.renderToString` 裸串誤匹配頂部註解 → `return ` 前綴鎖真呼叫點·紅→綠）
- ✅ 守衛 5 passed；全套件 712→**713 passed** 零回歸；C1 hash `d5ef6b6` 自癒
- ⚠️ baron E2E：LaTeX 論文渲染不退化 + `<img onerror>` 消毒驗證
- commit/push：否（baron 手動·4 檔）

## 後續引用

C3（Sources & Meta Hardening）由 baron 另下獨立提示詞觸發。
