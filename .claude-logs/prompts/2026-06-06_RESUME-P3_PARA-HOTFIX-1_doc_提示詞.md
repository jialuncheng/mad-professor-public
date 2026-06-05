`````markdown
# 2026-06-06 — RESUME-P3 PARA-HOTFIX-1 文件撰寫提示詞（B軌正文段落邊界正規化）

> **收到時間**：2026-06-06（UTC+8）
> **任務代號**：RESUME-P3 PARA-HOTFIX-1（BE-Hotfix 文件撰寫·plan 階段）
> **觸發情境**：baron 比對 A軌/B軌渲染發現 B軌正文「兩段黏在一起」、A軌有段落留白；經 grep 鋼證定位 A軌靠 `_write_to_md` 補 `\n\n` + `_preserve_pipe_table` 單 `\n`→`\n\n`，B軌兩者皆無；baron 拍板「移植 A軌 `_preserve_pipe_table` 邏輯進 pipelines/、不耦合 A軌 class」，下令產 hotfix 文件存 baton/。

---

## 完整提示詞

````
在 B軌 _restore_one_section 處理 text item 時，對譯文套用「段落邊界正規化」——把 A軌 _preserve_pipe_table 的邏輯移植進 pipelines/（pipe-table-safe 的單 \n→\n\n），不耦合 A軌 class（符合既有原則）。約一個小函式 + 一處呼叫，加 1 個測試。

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

- 症狀：B軌履歷正文兩段黏一起（無空行）、A軌段落有留白。
- A軌機制：① `_write_to_md`（L585-587）每塊補 `content + "\n\n"`；② `_preserve_pipe_table`（L629）`re.sub(r'(?<!\|)(?<!\n)\n(?![\n\|])', '\n\n', text)` 把段內單 `\n`→`\n\n`（pipe table rows 保留）。
- B軌缺漏：`_restore_one_section` 只把譯文 append、`_restore_sections_markdown` 只在不同 part 間放 `\n\n`，**段內單 `\n` 完全不處理** → CommonMark soft break → 黏一起；且 RESUME-P3 C2 為 resume 停用 Translator U4，無任何換行升級。
- baron 決策：移植 A軌 `_preserve_pipe_table` 邏輯為 pipelines/ 私有 helper（不耦合 A軌 class），在 `_restore_one_section` 處理 text item 時套用。

## 執行結果摘要

- 產出：`baton/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md`（依 template_hotfix、含詳細真因 + 完整修法程式碼 + commit msg）
- 性質：plan 階段文件（不動業務代碼）；Run 由 baron 後續獨立提示詞觸發
- 是否動 .py：否；是否 commit：否

## 後續引用

修法＝pipelines/ 私有 `_normalize_paragraph_breaks`（pipe-table-safe 單 `\n`→`\n\n`）+ `_restore_one_section` text item 套用；`# === [RESUME-P3 PARA-HOTFIX-1 START/END] ===` 包裹；改 B軌輸出 → 須重捕 resume golden。
`````
