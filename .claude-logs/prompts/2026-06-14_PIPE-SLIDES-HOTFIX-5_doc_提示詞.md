# PIPE-SLIDES-HOTFIX-5（B2 過場頁）文件產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 |
| 任務代號 | PIPE-SLIDES-HOTFIX-5（B2 過場頁·HOTFIX-4 對有標題過場頁抓不到）|
| 工作流 | BE-Hotfix（需 logging/database SOP §5 核查）|
| 觸發情境 | Ch37 簡報 page-32「過場投影片 (Transition Slide)」未被踢除;Vision 給了標題 → HOTFIX-4 跳過條件「is_blank 且 title+content 皆空」不成立（title 非空）→ 漏網 |

## 正文（原文）
B2 過場頁（HOTFIX-4 對有標題的過場頁抓不到）
針對以上面內容做一個 hotfix 文件、存檔路徑 baton/
依據 template_hotfix.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
詳細說明原因、程式碼也加入文件、包含 commit

## 診斷軌跡
- 現象：Ch37 page-32 生態球過場頁未踢除（baron 掃描發現「空白頁沒踢」）
- 真因：Vision 把過場頁轉錄成有標題單位（title="過場投影片 (Transition Slide)"、markdown_content=""、figure_description="生態球…"）;HOTFIX-4 跳過條件要求 is_blank=true **且 title 與 content 皆空** → title 非空 → 不跳;舊三欄全空規則因 figure_description 非空亦不跳
- 修法：① 放寬跳過＝「is_blank 且 markdown_content 空」（容許 title/figure_description 非空，過場頁特徵＝有裝飾圖+可能標題但無條列正文）② Vision prompt 釐清「純過場/章節分隔頁即使有『過場/Transition』標題仍 is_blank=true」;保留「含真實圖表/資料/條列正文→is_blank=false」防誤殺真圖頁
- 範圍：純後端 slide_pipeline.py P1（prompt + 跳過邏輯）;RAG/渲染/四路零碰;改 Vision prompt → slides golden 須重捕（搭既有待捕批次：HOTFIX-1/1b/2/3/3b/3c/3d/4 + META-NORM C3/C4）
- 偏差註記：commit 簽名一律當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
