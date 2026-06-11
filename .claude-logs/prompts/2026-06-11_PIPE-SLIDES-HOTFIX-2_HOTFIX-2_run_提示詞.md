# PIPE-SLIDES-HOTFIX-2 HOTFIX-2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 19:35 |
| 任務代號 | PIPE-SLIDES-HOTFIX-2 HOTFIX-2 |
| 觸發 Commit | HOTFIX-2 |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md` |
| 觸發情境 | baron 審查通過 HOTFIX-2 規格，下達緊急修補執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES-HOTFIX-2 / HOTFIX-2 / BE-Hotfix；依據 baton hotfix.md

### 執行命令（`# === [PIPE-SLIDES-HOTFIX-2 HOTFIX-2 START/END] ===` 包裹）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py 三點：
   - **B** `_safe_alt`（`][()`→全形、換行/連續空白→單空格）+ 兩處 alt 渲染套用（_page_source_md EN / _deliver ZH）
   - **E** `_DATE_LINE_RE` + `_strip_master_date`（純日期行 ≥2 頁剔）+ run_phase1 緊接 _dedupe_headers 後呼叫
   - **F** `_normalize_paragraph_breaks` regex `(?![\n\|])`→`(?![\n\|]|\s*(?:[-*+•]|\d+[.、])\s|\s*-\s)`
③ tests 補 3 測試（hf2b alt 轉義 / hf2e 日期剔除 / hf2f tight list 維持）
- 物理防線：僅兩檔、不建新檔；SOP §5.2 無裸 commit

### 驗收
- pytest tests/test_slide_pipeline.py -v 全綠（32 passed）+ 全套件不退化 + SOP grep（format_exc/logger.error/裸 commit 無命中）

### TODO 同步
- BE-Hotfix PIPE-SLIDES-HOTFIX-2 標 ✅ done；git log hash 自癒

### 收官自動化（全綠後）
- mv hotfix.md → hotfixes/ + 執行報告 → executions/；長駐 PIPE-SPEC 嚴禁動

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_執行.md（暫存→隨收官移出）

### §8 baron 命令
- git add：兩檔 + 2 .bak + run 提示詞 + INDEX + TODO + hotfixes/ + executions/；msg → /tmp/PIPE-SLIDES-HOTFIX-2_msg.txt

### 停止
- 移出歸檔 + 產執行報告後立即停止；不自發 commit/push
