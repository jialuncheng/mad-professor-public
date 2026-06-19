# PIPE-LITEDOC-HOTFIX-1 doc 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 |
| 任務代號 | PIPE-LITEDOC-HOTFIX-1 |
| 階段 | doc 產出（hotfix 文件、baton 暫存待 Run）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC-HOTFIX-1_hotfix.md` |
| 工作流類別 | BE-Hotfix |

## 正文（原文摘要）
針對 litedoc 雙缺陷（① 標題與 meta 重複 ② 日文/簡體未翻譯）做一個 hotfix 文件、存 baton/。
- 依據：template_hotfix.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
- 詳細說明原因；程式碼 diff 寫進文件；包含 commit 草稿。
- 經多輪分析收斂之三鎖：
  (1) 簡體絕不可給 `zh*` 字串（四處 `startswith("zh")` gate 會復活 bug）
  (2) 偵測器放 section_engine 共用（book 也要）、二元「是不是繁中」+ 取內文樣本不取封面
  (3) 扉頁保留 + 原文層剝標題回聲（理由＝chrome 分層 + academic-family 共用結構、非 A 軌 golden 0%）

## 偏差註記
- doc-only：程式碼 diff 寫進文件、不動實檔（.py 未改）、含 commit 草稿、存 baton 待 Run。
