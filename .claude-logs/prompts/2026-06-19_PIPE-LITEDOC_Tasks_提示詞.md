# PIPE-LITEDOC Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 01:00 |
| 任務代號 | PIPE-LITEDOC Tasks |
| 觸發 Commit | PIPE-LITEDOC-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md` |
| 觸發情境 | baron 同意 plan v3 規格、下達任務拆分指令 |
| 工作流類別 | BE-Refactor（tasks 階段）|

## 正文（原文摘要）
扮演 Claude Code、將 PIPE-LITEDOC plan v3 拆為可執行 Commit 清單。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / master plan v10 / SPEC / database SOP / logging SOP / plan / template_tasks / template_execution
- 允許新建/修改：`pipelines/litedoc_pipeline.py`(新) / `tests/test_litedoc_pipeline.py`(新) / `pipelines/__init__.py`(僅註冊 import) / `pipelines/section_engine.py`(**僅純加法 render_meta_header_html**)
- 嚴禁改：A 軌全部 / resume / slides / contracts 凍結合約欄位
- 自主拆分、不給 commit 建議;最後 Commit 必為 Checkout（僅 Checkout 才 mv baton→正式目錄 + git add、中間 commit 報告留 baton 嚴禁 add）;各中間 commit 產執行報告（template_execution）
- **必體現兩修正**：① U2.1 DocAnalyzer 映射（doc_type 非 news/web→'web' 扁平 prompt、防 fallback academic）② U5c/U6 translated_title 雙語標題鏈（is_zh→title / 分段→取頂層 title slot 譯後 / 一鍵→title 單元翻一次）
- §0.5 成果盤點置開頭;§8 每 Commit 六維度表;§1 TL;DR 中文括號命名
- 同步 TODO（高優先最前、⬜ + Commit 清單）
- 停止：產 tasks + 更新 TODO 後立即停;嚴禁產 _執行.md / 動業務代碼 / 自發 commit

## 偏差註記
- plan v3：U1-U9 + U2.1（DocAnalyzer 映射）+ U5b（render_meta_header_html 純加法·首 commit）+ U5c（translated_title 三路徑）;§9 七 OQ 全 🟢;Q7 meta header HTML formatter update 不另開、排首 commit。
- code 草案（reviewer 提供）屬本階段參考、不入 plan;tasks §8 實作細節可援引。
