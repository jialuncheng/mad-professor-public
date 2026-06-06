`````markdown
# 2026-06-06 — RESUME-P3 META-HOTFIX-1 文件撰寫提示詞（P1 Meta 渲染進文件 header）

> **收到時間**：2026-06-06（UTC+8）
> **任務代號**：RESUME-P3 META-HOTFIX-1（BE-Hotfix 文件撰寫·plan 階段）
> **觸發情境**：經追查確認 P1 抽的 meta（姓名/電話/email/領域）只流到 DB（`ctx.raw_metadata` 旁路終點＝web_server 寫庫）、`run_phase3` 渲染端從不消費 → final 沒有 meta header。INFRA-4 屬遠期合約轉正、且明確排除 render 缺口。baron 拍板「先做 HEADER-HOTFIX：run_phase3 加組 header、走現有旁路、讓 resume final 立刻有 meta」，下令產 hotfix 文件存 baton/。

---

## 完整提示詞

````
HEADER-HOTFIX（run_phase3 加組 header、走現有旁路）讓 resume final 立刻有 meta

針對以上面內容做一個hotfix
存檔路徑baton/

依據
template_hotfix.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

詳細說明原因
程式碼也加入
包含commit
````

---

## 上文脈絡（root cause 已 grep 鋼證）

- P1 抽 meta 放兩處：`IngestionMetadataSpec.title`（姓名）+ `ctx.raw_metadata`（domain/phone/email、L194-196）。
- raw_metadata 旁路終點＝DB：P2 讀 domain（L332）、web_server L655-656 寫 `Paper.metadata_json`；**run_phase3 從不讀**。
- `run_phase3` 只渲染 section body、無 header 組裝 → final 無姓名 h1、無 meta。
- baron 決策：治標——在 run_phase3 寫出前加 `_render_meta_header`，**讀現有 ctx.raw_metadata 旁路 + ctx.ingestion.title** 組 header、prepend final；不動凍結合約（合約轉正屬 INFRA-4 遠期）。

## 執行結果摘要

- 產出：`baton/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md`（依 template_hotfix、含詳細真因 + 完整 helper + diff + commit msg）
- 性質：plan 階段文件（不動業務代碼）；Run 由 baron 後續獨立提示詞觸發
- 是否動 .py：否；是否 commit：否

## 後續引用

修法＝pipelines/ 私有 `_render_meta_header`（讀 raw_metadata 旁路 + ingestion.title、hard-break 防 RAG-10 軟換行）+ run_phase3 prepend final_zh/en；`# === [RESUME-P3 META-HOTFIX-1 START/END] ===` 包裹；改 B軌輸出 → 須重捕 resume golden；INFRA-4 之後把讀取源由 raw_metadata 轉 spec.meta。
`````
