`````markdown
# 2026-06-06 — RESUME-P3 HEADING-HOTFIX-1 文件撰寫提示詞（B軌標題層級遞迴深度修復）

> **收到時間**：2026-06-06（UTC+8）
> **任務代號**：RESUME-P3 HEADING-HOTFIX-1（BE-Hotfix 文件撰寫·plan 階段）
> **觸發情境**：baron 經 log/前端截圖比對發現 B軌履歷標題「過大、只有一個層級」；經 grep 鋼證定位 `_restore_one_section` 取錯欄位（level 恆=1 短路），baron 拍板「直接用遞迴深度 depth 推算」，下令產出 hotfix 文件存 baton/。

---

## 完整提示詞

````
直接用遞迴深度 depth 推算

針對以上面內容做一個hotfix
存檔路徑 baton/

依據
template_hotfix.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

詳細說明原因
程式碼也加入
````

---

## 上文脈絡（root cause 已 grep 鋼證）

- 症狀（baron 前端截圖）：B軌履歷「工作經歷」與子層「AI 生物電子健康科技 - CTO」同為巨大 h1、無階層。
- 定位：`pipelines/resume_pipeline.py:562` `level = int(sec.get("level") or sec.get("heading_level") or 1)`。
- 真因（dump processed JSON 鋼證）：`level` 欄恆=1（扁平死欄）、`heading_level` 才帶真實深度（頂層=2/子=3/孫=4，且 = 2+樹深度）；`or` 短路先取到 1 → 永不讀 heading_level → 全標題塌成 `#`(h1)。
- baron 決策：**不依賴資料欄位**，直接由 `_restore_one_section` 遞迴深度 `depth` 推算層級（頂層 h2、每下潛 +1、上限 h6）。

## 執行結果摘要

- 產出：`baton/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md`（依 template_hotfix、含詳細真因 + 完整修法程式碼）
- 性質：plan 階段文件（不動業務代碼）；Run 由 baron 後續獨立提示詞觸發
- 是否動 .py：否；是否 commit：否

## 後續引用

修法＝遞迴深度推算 `level = min(2 + depth, 6)`、`# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` 包裹；改 B軌輸出→須與既有 hotfix 合併重捕 resume golden。
`````
