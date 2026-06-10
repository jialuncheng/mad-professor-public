# PIPE-SLIDES-HOTFIX-1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 06:30 |
| 任務代號 | PIPE-SLIDES-HOTFIX-1 HOTFIX-1 |
| 觸發 Commit | HOTFIX-1 |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md` |
| 觸發情境 | baron A/B 軌同件實測簡報發現三缺陷，下達緊急修補執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES-HOTFIX-1 / HOTFIX-1 / BE-Hotfix；依據 baton hotfix.md「熱修復修法」

### 執行命令
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② 依 hotfix.md 落地（`# === [PIPE-SLIDES-HOTFIX-1 HOTFIX-1 START/END] ===` 包裹、F1/F2/F4 區塊）：
   F1 `_strip_title_echo`（P1 原文層去標題回聲、cap 2）+ units 構造套用
   F2 封面譯題穿 raw_metadata 旁路 + run_phase4 translated_title + 影子 (測試) 綴
   F4 移植 `_normalize_paragraph_breaks`（pipe-table-safe）+ zh/en 渲染對稱套用
   F3 顯式不修（決策已記 hotfix.md）
③ 補 4 回歸測試
- 物理防線：僅兩檔；嚴禁改共用元件/A 軌；SOP §5.2 無裸 commit

### 驗收
- pytest tests/test_slide_pipeline.py -v 全綠（24+4）+ 全套件不退化 + SOP grep

### 收官自動化（全綠後）
- mv hotfix.md → hotfixes/ + 執行報告 → executions/ + git add；兩份 `2026-06-01_PIPE*` 規格書長駐 baton 嚴禁動
- TODO：完成表 + 索引 ✅ + git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES-HOTFIX-1_HOTFIX-1_執行.md（暫存→隨收官移出）

### §8 baron 命令
- git add：兩檔 + 2 .bak + run 提示詞 + INDEX + TODO；msg → /tmp/PIPE-SLIDES-HOTFIX-1_msg.txt

### 停止
- 產出執行報告 + TODO 更新後立即停止；不自發 commit/push
