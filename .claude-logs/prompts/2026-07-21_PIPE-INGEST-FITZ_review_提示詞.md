# PIPE-INGEST-FITZ review 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-INGEST-FITZ（F6、born-digital 文字層快速道 + 連字修復）
- **階段**：plan review（v1 → v2 定稿）
- **來源**：baron 轉交外部 review 建議 + 六 OQ 拍板

---

## 提示詞原文

```
review下面建議
如果沒問題
update plan

對於 `2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md` 的架構與流程評估、代碼掃描結果以及 Open Questions 的答覆如下：

### 一、 架構與流程評估 (Architectural & Process Audit)

*   **設計高度合規，邊界清晰**：
    該 plan 完美遵循了 `section_engine` 設計紀律。將「文字層閘門」與「連字修復」均上置於 `litedoc_pipeline` 呼叫端（P1 流程內），徹底避免了下沉污染 A 軌共用處理器（`PDFProcessor` / `pipeline_core`）的問題，確保了 B 軌影子管線的隔離安全性。
*   **同形 Markdown 契約相容性**：
    Fitz 輸出的 Markdown 檔必須嚴格遵循 **MinerU 同形契約**：使用 `\n\n` 作為段落分隔符，並以標準 `#` 與 `##` 作為標題。這使得下游的 `TilingProcessor` 與 `ingestion_engine` 能在完全零感知的狀況下無縫對接。
*   **實作細節提醒 (圖片命名與防衝突)**：
    使用 PyMuPDF 的 `doc.extract_image(xref)` 提取圖片時，寫入 `images/` 的檔名建議格式化為 `page_{page_idx}_{xref}.{ext}`，以確保跨頁圖片寫入時的唯一性與防衝突。
*   **連字修復防誤殺 (數字縮寫/版本號)**：
    為了防範諸如 `1st -> fist`、`v1 -> vfi` 的誤殺：
    1.  修復窗口除了限制為 `[a-z][^a-zA-Z\s][a-z]`（或包含字首邊界 `\b`）外，必須在修復前對單字進行正則排查：若單字匹配數字縮寫（如 `\b\d+(st|nd|rd|th|s)?\b`）或常見版本號（如 `v\d+`），則一律不予替換。
    2.  替換後需進行輕量詞形檢查（例如優先載入系統字典 `/usr/share/dict/words`，並內建一組常見連字字彙集作 fallback 兜底），僅在替換後單字為有效英文單字時才採信，否則 fail-open 保留原樣。

---

### 二、 Open Questions 拍板方案 (OQ1 - OQ6)

| 問題 | 拍板方案 | 理由 |
|---|---|---|
| **Q1：連字修復落點** | ✅ **litedoc P1 共用步（獨立純函式模組，於 P1 ②後③前接線）** | 連字壞字是 PDF 字型 ToUnicode 映射的共病，在 MinerU 與 Fitz 路徑均會出現。放此位置能讓兩來源同享修復，且完全不影響 `md_cleaner` 等 A 軌不可動檔案。 |
| **Q2：修復策略保守度** | ✅ **小寫+異常字元+小寫雙向窗口 ＋ `fi/fl/ff/ffi/ffl` 替換 ＋ 詞形雙重檢查（系統字典 + 內建兜底集），不確定保留原樣。** | 漏修僅是局部字元噪音，誤殺則會改壞正確文本。保守策略能將誤殺率控制在接近零的水平。 |
| **Q3：閘門判定門檻** | ✅ **`LITEDOC_FITZ_MIN_CHARS_PER_PAGE=150`，以中位數（Median）判定。** | 網頁列印 born-digital PDF 每頁字數遠超此值，而掃描 PDF 則為 0。中位數能有效抵抗封面或尾頁等稀疏頁面的干擾。 |
| **Q4：FITZ 預設開關** | ✅ **`LITEDOC_FITZ_ENABLED` 預設為 `True`。** | litedoc 目前仍處於 B 軌影子管線，預設開啟可最大化影子軌 E2E 驗證的曝光率，若有異常可隨時透過 env 設為 `False` 秒級關回。 |
| **Q5：Fitz 失敗策略** | ✅ **Fail-open 退回 MinerU（Warning + `exc_info=True` 記錄，不阻斷攝入）。** | 既存的 MinerU（`PDFProcessor`）是可靠的備援，直抽解析器的任何失敗都不應導致文獻攝入流程中斷。 |
| **Q6：混合型 PDF 處置** | ✅ **不做單頁混合模式，由中位數閘門整份二擇一。** | litedoc 文獻大宗均為單一類型。單頁混合會重新引入多套座標系對位與拼接的複雜度，違反 YAGNI。 |
```

---

## 備註

- review 判定：無結構性缺失；架構評估肯認閘門/修復上置呼叫端之隔離設計。
- 兩實作細則回灌 plan §2：① 同形契約明確化（`\n\n` 段落分隔 + 標準 `#`/`##`）＋圖片命名 `page_{page_idx}_{xref}.{ext}` 防衝突；② 連字防誤殺雙閘強化（替換前數字縮寫/版本號正則排查 + 替換後系統字典優先/內建兜底集詞形檢查）。
- 六 OQ 全數拍板採納 plan v1 推薦方案（無翻案）。
- 產出：plan v1 → v2 定稿（§2/§9/§99.2 對應更新）。
