# PIPE-INGEST plan review 提示詞

- 日期：2026-07-18
- 來源：baron（轉發外部 review、含四項代碼掃描 #A-#D 與六 OQ 拍板）
- 階段：plan review（v1 → v2 定稿）

## 原文摘要

> review下面建議 / 如果沒問題 / update plan

外部 review 內容：
1. **#A** `section_engine.py:237` `if content:` 證實 figure 靜默丟棄 → plan figure `content` 補鍵設計正確
2. **#B** `litedoc_pipeline.py:494` 證實 section 模式譯題撈第一個 title slot → 廢除 `_extract_translated_title`、P1 title 唯一源正確
3. **#C** `doc_analyzer.py:58-62` 證實先 heading-fix 寫回、後同檔判型 → doc_structure 行號與 md 快照吻合
4. **#D** `tiling_processor.py:255` 證實 tiling 自動補 index/part/tiling_method → 引擎只需產基礎 blocks

六 OQ 拍板：Q1 不開旗標（constraints 局部治理）/ Q2 獨立 `pipelines/ingestion_engine.py` / Q3 caption 沿用現況 / Q4 廢除 slot 撈題 / Q5 移除 `_detect_source_lang` / Q6 resume 遷移登記 TODO 候選（book 開案時評估）——全數採納推薦方案。

## 處置

四項代碼聲稱經本地 grep 複驗全數吻合；plan 更新至 v2（§2 增 dead code 目標 / §3 補 #C #D 證據 / §5 行號漂移 🟡→🟢 / §9 拍板留痕 / §99.2 v2）。
