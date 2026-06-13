# FE-RHYTHM-UNIFY plan 產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 |
| 任務代號 | FE-RHYTHM-UNIFY（閱讀視圖垂直節奏統一）|
| 工作流 | FE-Refactor |
| 觸發情境 | 連續節奏點修（3c/FE-RHYTHM-1/擬 FE-RHYTHM-2）盤點後確認：無硬衝突、但疊床架屋（逐交界補丁、根因 margin-bottom-only + reset 歸零清單 margin 未治、打地鼠 + 同視覺兩機制）；baron 選 (A) 一次性統一重構、收編 FE-RHYTHM-1/2 |

## 正文（原文）
(A) 我開「閱讀視圖垂直節奏統一」FE-Refactor 的 plan（盤點所有交界 + 設計單一模型 + 三軌驗證 + 收編 FE-RHYTHM-1/2）
針對上面內容做一個 plan、baton/
依據 template/template_plan.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
不用給 commit 建議

## 決策軌跡
- 審計結論：① 無打架（各 :has/+ 補丁打不同交界、特異度級聯、管線層在 CSS 前、不交火）② 有疊床架屋（p→p/p→list/list→p/h→h… 逐交界 bespoke 規則、根因未治→打地鼠；promote `**X**`→### vs `X：` 純段落 = 同視覺兩機制）
- 根因：base 垂直節奏只用 margin-bottom（p 無 margin-top）+ index.html:79 reset 歸零 ul/ol margin、四主題 0 補 → 節奏天生不對稱、每交界要 bespoke
- (A) 統一模型（如 flow `* + *` margin-top 制 + 少數緊貼對覆寫）取代逐交界補丁、收編 FE-RHYTHM-1/2、止血打地鼠；plan 級 FE-Refactor、純 base CSS、不動 themes 間距、chat（.msg-ai）不波及、須驗三軌×四主題
- 不收編：3c 箭頭硬換行/清單項收緊（markdown 層、與 CSS 節奏正交）、3d、promote（內容正規化、另一關注）
