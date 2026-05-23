# 2026-05-19 「pro7les」字元污染：NFKC ligature 正規化（保守修復）

只動字元處理，無業務邏輯變更。

## 修改位置
processor/pdf_processor.py：
- 新增 `import unicodedata`
- process() 內、CONTROL_CHAR_PATTERN.sub 之後、write_text 之前，新增一行：
  `md_text = unicodedata.normalize('NFKC', md_text)`
（採規格推薦的保守版；位置就在既有控制字元清理處，MinerU 分支；slides 走 Vision 不經此處）

僅 1 檔變更：processor/pdf_processor.py（py_compile 通過）。

## 能修哪類問題（已實證）
真 ligature 相容字元（Unicode U+FB00–FB06 等）→ NFKC 自動拆解：
  proﬁles→profiles、ﬁnal→final、eﬃcient→efficient、conﬁg→config、ﬂow→flow、staﬀ→staff
（已用 python 實測輸出確認）

## 不能修哪類問題（重要、誠實說明）
使用者回報的實際症狀「pro7les」是 MinerU 把 ﬁ **誤判成數字 7**，
markdown 抽取階段就已寫成錯誤的 '7' 字元，**不是 U+FBxx ligature codepoint**。
NFKC 對 'pro7les' 無能為力（實測 'pro7les' → 'pro7les' 不變）。
→ 本次修復**無法修復該篇 title 的 pro7les**，只能修「MinerU 有保留真 ligature 字元」的情境。
不做硬編字典（7→fi、7nal→final…）：'7' 太常見，context-aware 替換風險高、維護累（符合規格⑤）。

## NFKC 副作用
NFKC 也會把全形→半形、其他相容字元正規化（例：'Ａ１'→'A1'）。
對學術／新聞 markdown 多半可接受且通常更乾淨；CJK 相容形罕見於正文，風險低。
此步只在 MinerU pdf2md 輸出上做一次，不影響翻譯／RAG 等後續業務邏輯。

## 是否需要 reprocess 既有論文
- 既有論文 markdown 已是 MinerU 當時輸出；pdf2md 有快取（_check_stage_exists 見 {paper}.md 即跳過），
  不會自動重新 NFKC。
- 若既有污染是「真 ligature」型：刪除該論文重傳 / 重跑 pdf2md 才會套用 NFKC。
- 若是「數字 7」型（如本案 pro7les）：reprocess 也沒用（MinerU 同 bug）。
- 建議：**不做大規模 reprocess**；新上傳自動受惠 NFKC；數字 7 型屬 MinerU 上游問題。

## 為何 ﬁ 會變數字 7（分析，非結論）
推測為 MinerU 內部對 ﬁ ligature 字形的 OCR/字元映射誤判 fallback 成形近字（7）。
無法從本專案端可靠還原（已是有效但錯誤的數字）。修復方向應為：
(a) 升級 MinerU（不在本專案範圍）；(b) 驗證 MinerU 3.x 是否已修；(c) 接受該品質問題。

## 建議
1. 本次 NFKC 修「真 ligature」類，屬低風險淨改善，保留。
2. 「pro7les」這類數字 7 污染需另循 MinerU 版本升級驗證；本專案端不做硬編替換。
3. 既有資料維持現狀，不重跑；測試資料本就會清。
4. 後續若升級 MinerU，建議用同一篇 PDF 比對 title 是否仍有 7 取代 fi。

## 驗證
- py_compile processor/pdf_processor.py：通過。
- NFKC 行為以 python 實測（ligature 全部正確拆解；pro7les 不變；全形副作用示例）。
- ⚠ 完整 runtime（實際跑 MinerU pipeline 看 title）此環境無法執行（無 MinerU 服務／sqlalchemy／dotenv）；
  使用者於正式環境上傳含 ﬁ ligature 的 PDF 驗證 title 不再殘留 ligature 字元即可。
- 待確認：上傳 PDF 原檔內 fi 是 ligature 還是分開字元（可 hexdump 第一頁文字）；
  若原檔即為 ligature 且 MinerU 保留 → NFKC 生效；若 MinerU 已轉 7 → 本修復無效（如上）。

## 疑慮
1. 本修復**不解決使用者回報的 pro7les 實例**（數字 7 型），僅修真 ligature；已明確標示，避免誤期待。
2. NFKC 全形→半形副作用對中文新聞/網頁多半無害，但若未來有刻意保留全形的需求需重新評估（目前無此需求）。
