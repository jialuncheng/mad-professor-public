# PIPE-INGEST-FITZ C1 — Fitz Processor（Fitz 直抽處理器）執行報告

---

**任務代號**：PIPE-INGEST-FITZ C1
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md` §8 C1
**上游 plan**：同名 `_plan.md`（v2、六 OQ 拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §1 基準與完成狀態

- 基準 commit：`2e03c2c`（IMG-FILTER checkout）
- 完成狀態：代碼與測試已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 純加法零接線：`grep -rn "fitz_processor" pipelines/ web_server.py pipeline_core.py` → **零命中**（全鏈 runtime 零變化）

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor（Fitz 直抽處理器） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `processor/fitz_processor.py` | 新增 | `FitzProcessor(PDFParser)` 第二 impl + `median_page_chars` 閘門輔助（253 行） |
| `tests/test_fitz_processor.py` | 新增 | 16 測試、fitz 程式化生成 fixture（零網路零 MinerU） |

（全新檔、無 `.bak`；baton 暫存之 plan/tasks/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

**真因**：litedoc 大宗 born-digital PDF（有完整文字層）一律繞道外部解析服務——慢、佔推理通道、OCR 噪音；`PDFParser` ABC 本為「換 impl」而設、卻僅有一個 impl。

**修法（三機制）**：

1. **字級分群推導標題**：第一趟逐頁收集每行 `(text, max span size, bbox, block)`；全文以「**各字級承載的總字元數**」定正文字級（正文以字量壓倒標題、抗頻次平手——初版用 `statistics.mode` 在 H1/正文行數平手時誤判、已以字元權重法取代並由測試鎖住）；明顯大於正文（+1.0pt 容差）的字級由大到小取前兩群 → `#`／`##`；超長行（>150 字元）即使大字級也不判標題（防大字級段落誤判）。
2. **座標區塊排序（閱讀序）**：每頁組裝項目 `(y0, x0, markdown)`——文字行依 `(y0, x0)` 排序後、標題獨立成塊、同 block 連續正文行以空格併段；圖項目以 `get_image_rects` 首矩形座標插入同一序列；最終依 `(y0, x0)` 排序輸出、段落間以 `\n\n` 分隔（MinerU 同形契約）。
3. **跨頁重複頂/底帶剝除**：行落於頁高 8% 頂帶或 92% 底帶者取「數字歸一 key」（`\d+`→`#`、令 `Page 1 of 2`/`Page 2 of 2` 同形）；同 key 出現於 ≥2 頁即判列印頁首尾、組裝時剝除。單頁文件不啟用（無重複基準）。

**圖檔**：`doc.extract_image(xref)` 抽原生 bytes、**僅 PNG/JPEG 落地** `images/page_{page_idx}_{xref}.{ext}`（跨頁唯一防覆寫、與 `image_filter` stdlib 尺寸解析同基準）；單圖失敗 warning 跳過（best-effort、依 ABC 契約）。**全檔零 `fitz.metadata` 讀取**（AST 測試守門）。失敗語意：檔案不存在 `FileNotFoundError`、解析錯誤統一 `PDFParseError`（`raise ... from exc`）。

## §5 測試結果

```
tests/test_fitz_processor.py 16 passed in 0.16s
（ABC 契約 4 / 同形 md 5 / 圖檔 2 / 零 metadata AST 1 / median_page_chars 4）

全套件：847 passed, 3 skipped, 3 warnings in 54.83s   ← 基線 831 + 新增 16、零回歸
```

驗收 grep（§6.1 全項）：

```
grep -n "class FitzProcessor(PDFParser)" processor/fitz_processor.py
  62:class FitzProcessor(PDFParser):
grep -n "PDFParseError" processor/fitz_processor.py
  26 import / 82 re-raise 白名單 / 88 統一包裝 raise ... from exc
grep -n "page_{" processor/fitz_processor.py
  250:            fname = f"page_{page_idx}_{xref}.{ext}"
.metadata 代碼層 → 零命中（AST 測試 TestNoFileMetadata 守門；docstring 提及不算）
grep -rn "fitz_processor" pipelines/ web_server.py pipeline_core.py → 零命中（C1 零接線）
```

SOP 一致性核查（§6.4）：

```
logging：grep logger.error → 僅 fitz_processor.py:85（含 exc_info=True ✅）；
         另 logger.warning（單圖跳過）亦含 exc_info=True；零 traceback.format_exc
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/pdf_processor.py` / `processor/md_cleaner.py` — byte 不動（`git status` 無此二檔）
- [x] `pipelines/litedoc_pipeline.py` — 零接線（C3 才接）
- [x] 零 `fitz.metadata` 讀取（AST 測試守門）
- [x] 圖檔限 PNG/JPEG + `page_{page_idx}_{xref}.{ext}` 命名
- [x] 零新第三方依賴（PyMuPDF 既 pin `requirements.txt:26`）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C2 — Ligature Repair（連字修復純函式）**（與 C1 獨立、純加法零接線）；待 baron ship C1 後另下 C2 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（本 commit 全新增檔、無須備份）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST-FITZ_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST-FITZ_C1_msg.txt
```
