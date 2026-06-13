# RAG-12-HOTFIX-1 文件產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 |
| 任務代號 | RAG-12-HOTFIX-1（圖片 alt 內 LaTeX 破版）|
| 工作流 | FE-Hotfix |
| 觸發情境 | baron 掃 Ch37_Plant-Nutrition_shadow（B 軌簡報）發現「空白頁沒踢除 + 後續排版全部錯誤」；經多輪證據診斷鎖定真因＝氮循環圖(page-30)圖說 alt 含 LaTeX `$N_2$`/`$\text{NH}_4^+$`/`$\text{NO}_3^-$` → renderMarkdownWithMath 步驟 7 把 KaTeX HTML 注入 `alt="..."` → 炸 `<img>` + 級聯吞掉後續;A 軌/履歷正常（無 LaTeX 圖說）證 CSS 無辜 |

## 正文（原文）
RAG-12-HOTFIX-1（圖片 alt 內 LaTeX 破版）
針對以上面內容做一個 hotfix 文件、存檔路徑 baton/
依據 template_hotfix.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
詳細說明原因、程式碼也加入文件、包含 commit

## 診斷軌跡（鎖定真因）
- 現象：baron 報「空白頁沒踢除 + 後續排版全部錯誤」（Ch37 植物營養 B 軌）
- 排除：① FE-RHYTHM-UNIFY CSS 無辜（A 軌/履歷走同一 renderMarkdownWithMath+CSS、正常 → 4 次確認）② 空白頁（過場投影片）非結構崩壞主因（source markdown 結構乾淨、38 slide-head 全閉合）
- 真因：氮循環圖 figure_description 含 LaTeX → 整段塞進 `![alt](url)` 之 alt；renderMarkdownWithMath 步驟 4 抽 alt 內 `$...$` → 步驟 7 katex.renderToString 的 `<span class="katex">...`（含 `"`/`<>`）回填進 `alt="..."` → 引號提前閉合、`<img>` 炸穿、後續 HTML 全吞 → 級聯破版
- 修法：抽 math 前先保護 markdown 圖片整段（同 code 佔位手法）、marked.parse 前還原 → alt 內 `$` 永不進 math 管線（留字面、不可見、無害）；純前端 index.html、通用（解所有文體圖說含 `$`）、零後端/golden
- 範圍：本次只開 B1;B2（過場頁 HOTFIX-4 對有標題頁抓不到）baron 擱置另議
- 偏差註記：commit 簽名一律當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
