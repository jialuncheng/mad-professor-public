# GLOSSARY-TERMMAP plan review 提示詞

- 日期：2026-07-19
- 來源：baron（轉發外部 review：代碼掃描核查 + Q1 歷史追溯 + 六 OQ 拍板）
- 階段：plan review（v1 → v2 定稿）

## 原文摘要

> review下面建議 / 如果沒問題 / update plan

review 內容：
1. **代碼掃描**：無結構性缺失；§4 term_key 三方同函式錨定完備；§6 純加法護欄清晰。
2. **Q1 歷史追溯**：早退 `if existing: return existing` 原始動因＝省 `extract_terms` 同步 LLM 呼叫之**域級成本快取閘門**（假設「LCC 域有詞＝術語庫已建成」）；忽略新文件長尾 → 域被首份文件寫入後所有後續同域文件跳過自癒、飛輪第一步停轉 → 判定「優化過度的設計缺陷」。
3. **六 OQ 拍板**：Q1 缺陷廢除〔已知∪未知分流〕/ Q2 settings 翻轉 true / Q3 6000 / Q4 附論併案〔純加法、受阻可剝離〕/ Q5 專名+高頻術語 / Q6 三路分開落地——全數採納推薦。

## 處置

歷史聲稱經本地查核：GLOSSARY-CORE plan v2 無逐字動因，但三路 P2 docstring「query_cascade→**缺詞** extract_terms→upsert」（resume:336/slides:489）為「缺詞才抽」成本閘門意圖之文本錨、與追溯一致 → 採信。plan 更新至 v2（§3 補早退動因 / §9 六 OQ 拍板留痕 / §99.2 v2）。
