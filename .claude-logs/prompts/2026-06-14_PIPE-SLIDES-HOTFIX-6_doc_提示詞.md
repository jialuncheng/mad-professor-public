# PIPE-SLIDES-HOTFIX-6 文件產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 |
| 任務代號 | PIPE-SLIDES-HOTFIX-6（殘留母片日期單頁清除 + golden 重捕說明回溯更正）|
| 工作流 | BE-Hotfix（+ DOC 回溯更正）|
| 觸發情境 | ① baron 發現 Ch37 都市農業頁殘留母片日期 `2026/4/28`（全檔唯一日期行、為該頁唯一 content）→ `_strip_master_date` 因 hit_pages<2 早退漏網、P3 譯重排;② 釐清 `golden_baseline.py capture slides` 捕 A 軌（PipelineCore）非 B 軌（slide_pipeline）→ 先前 8 份 hotfix 文件「slides golden 須重捕」為 A/B 軌混淆誤述、須回溯更正 |

## 正文（原文）
開 PIPE-SLIDES-HOTFIX-6 的 hotfix 文件 + 把已歸檔的那幾份 hotfix 文件裡「golden 須重捕」那句加個更正註記
針對以上面內容做一個 hotfix 文件、存檔路徑 baton/
依據 template_hotfix.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
詳細說明原因、程式碼也加入文件、包含 commit

## 診斷與決策軌跡
- 證據：final_zh 全檔唯一日期行 L393 `2026/4/28`、為「都市農業」頁唯一 content（slide-head 後、下一圖前）
- 真因：`_strip_master_date` 要求 hit_pages≥2 才洗；本輪 Vision 僅此頁把母片頁尾日期吐成獨立 content 行 → hit_pages=1 < 2 → 早退不洗 → P3 把 `4/28/2026` 譯重排成 `2026/4/28`
- 修法①（code）：`_strip_master_date` 加「整頁 content 僅純日期行 → 清空」單頁 pass（無論幾頁、運行 P1 譯前；真內容頁日期與其他行並存則 all() False 不清）
- 修法②（doc 回溯更正）：`capture slides` 捕 A 軌（PipelineCore/slides_processor、正本基準）、非 B 軌（slide_pipeline）→ B 軌 hotfix 不需 A 軌 golden 重捕、驗證走影子 E2E；8 份 hotfix 文件（HOTFIX-1/1b/2/3/3c/3d/4/5）「golden 須重捕」加更正註記作廢；RAG-12-HOTFIX-1「零 golden 重捕」正確不改
- 偏差註記：commit 簽名一律 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
