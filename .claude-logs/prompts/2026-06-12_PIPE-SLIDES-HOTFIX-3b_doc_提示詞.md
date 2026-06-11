# PIPE-SLIDES-HOTFIX-3b hotfix 文件產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-12（HOTFIX-3 上線後 baron 前端 QA ALi 簡報）|
| 任務代號 | PIPE-SLIDES-HOTFIX-3b |
| 觸發情境 | baron 發現 top-level bullet 凸排（`•` 跑到比標題更左）；診斷確認 index.html L79 全域 reset 把 top-level ul/ol padding 歸零、HOTFIX-3 二只修了巢狀 ul ul；確認改 base 一處不動 themes 後，命令產 hotfix |

## 正文（原文）
針對以上面內容做一個 hotfix 文件、存檔路徑 baton/
依據 template_hotfix.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
詳細說明原因、程式碼也加入文件、包含 commit

## 決策軌跡
- 真因：static/index.html L79 全域 reset `ul { padding: 0 }` 歸零 top-level ul/ol 縮排 + list-style:outside → bullet 凸到內容框左外側（落進 #paper-content space-8 左 padding）
- HOTFIX-3 二只加了 ul ul（巢狀）padding-left、漏 top-level → 第一層 bullet 仍凸排
- 修法：base 一處把 HOTFIX-3 list-indent 規則從「只巢狀」擴成「含 top-level」（#paper-content ul/ol + ul ul/ol ol/ul ol/ol ul）
- 不動 themes：主題 0 命中 list、縮排=結構歸主檔（principles.md）、base 一處含自訂主題受益
