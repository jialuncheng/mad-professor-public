`````markdown
# 2026-06-06 — VISION-HOTFIX-1 文件撰寫提示詞（Vision 轉錄 temperature 確定化）

> **收到時間**：2026-06-06（UTC+8）
> **任務代號**：VISION-HOTFIX-1（BE-Hotfix 文件撰寫·plan 階段）
> **觸發情境**：分析 golden capture 發現 Vision pdf2md 每次輸出抖動（13126/13233/13281 chars）；grep 鋼證根因＝`llm/client.py` `chat_with_images` 的 `GenerateContentConfig` **沒設 temperature** → 吃 Gemini 預設 ~1.0（高溫採樣）。baron 拍板「開小 hotfix：chat_with_images 加 temperature 參數、ResumeProcessor 傳 0」讓忠實轉錄確定化。存 baton/、依 template_hotfix、含詳細原因 + 程式碼 + commit。

---

## 完整提示詞

````
開一張小 hotfix（chat_with_images 加 temperature 參數、ResumeProcessor 傳 0）讓 Vision 轉錄變穩
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

- 症狀：Vision pdf2md 每次重捕輸出 13126/13233/13281 chars（~1.2% 抖動）→ golden 非固定靶。
- 根因：`llm/client.py:308` `chat_with_images` `config = GenerateContentConfig(system_instruction=...)` **無 temperature** → Gemini 預設 ~1.0；`resume_processor.py:157` 呼叫也沒傳。轉錄任務卻在高溫採樣。
- 唯一呼叫者：`resume_processor.py:157`（grep 證、加參數零波及）。共用：`ResumeProcessor.parse` A軌 pdf2md + B軌 run_phase1 都用。
- baron 決策：`chat_with_images` 加 `temperature` 參數（預設 None 向後相容）+ ResumeProcessor 傳 0（經 settings `LLM_VISION_TEMPERATURE` 預設 0.0）。

## 執行結果摘要

- 產出：`baton/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md`（依 template_hotfix、含詳細真因 + 完整 diff + commit msg）
- 性質：plan 階段文件（不動業務代碼）；Run 由 baron 後續觸發
- 是否動 .py：否；是否 commit：否

## 後續引用

修法＝settings `LLM_VISION_TEMPERATURE`(0.0) + `chat_with_images` 加 `temperature` 參數注入 GenerateContentConfig + ResumeProcessor 傳值；`# === [VISION-HOTFIX-1 START/END] ===` 包裹；⚠️ 共用改動、Vision 輸出改變 → A軌 golden + B軌 P1 都變、須重捕 resume golden（且自此可重現）。
`````
