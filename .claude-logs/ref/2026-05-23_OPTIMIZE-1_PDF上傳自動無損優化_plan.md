# 2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md

本文件為 **Mad Professor 專案 PDF 上傳自動無損優化 (OPTIMIZE-1)** 的落地實作計畫。本計畫嚴格看齊 `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 規範，建立於背景自動運作的 PDF 無損優化壓縮機制，保障系統 I/O、儲存與網路傳輸效能。

---

## 1. TL;DR (技術與問題概述)

* **問題**：使用者上傳的 PDF 檔案體積大時（如 30-100MB 的學術手冊或書籍），會大幅拖慢網路傳輸（特別是與 MinerU 節點的 SCP/SSH 拷貝）與伺服器載入時間，並佔用大量伺服器硬碟儲存空間。
* **根因**：目前 PDF 上傳後直接原封不動儲存於磁碟，未進行任何垃圾回收、重複物件清理或資料流壓縮。
* **解法**：在 `web_server.py` 的上傳儲存階段，第一時間引入基於 `pymupdf` (fitz) 的極速背景無損優化。透過垃圾回收及 stream deflate 壓縮，可大幅縮小體積 30% ~ 90%，對使用者完全透明，且 100% 不降低影像與文字的識別品質（不進行降低解析度或有損壓縮，確保後續 Vision 辨識 100% 精確）。
* **受影響範圍**：上傳 API (`/api/papers/upload`) 中的儲存邏輯。對前端與其他管線處理透明。
* **相依性**：無（使用既有 `pymupdf` 庫）。

---

## 2. 現況盤點

* **關鍵 Class/Method 與調用路徑**：
  - `web_server.py:431-480` [upload_paper](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/web_server.py#L431-L480)：接收 `file: UploadFile` 後，讀取 bytes 寫入 PDF 檔案：
    ```python
    with open(pdf_path, 'wb') as f:
        f.write(content)
    ```
  - 此端點為同步/非同步混合（FastAPI 執行緒管理），優化 PDF 應在儲存檔案後、或者在儲存的同時進行。

---

## 3. 觀察到的問題與證據

* **證據**：在 `web_server.py:457-458` 行中，檔案以 `wb` 模式直接寫入未加優化。大型書籍的 PDF 未經壓縮，體積動輒 50MB-100MB。
* **缺點**：
  - 拖慢遠端主機的傳輸時間（SCP 拷貝大型檔案很慢）。
  - 佔用伺服器儲存。
  - 大檔案常包含未被引用的無用 PDF 物件、重疊的字型或冗餘的元數據。

---

## 4. 設計方案

* **優化實現邏輯**：
  在 `web_server.py` 的 `upload_paper` 函式中，當 PDF 寫入磁碟後，立刻呼叫優化函式：
  ```python
  def optimize_pdf_lossless(pdf_path: Path) -> int:
      """無損優化 PDF 檔案，返回優化後的檔案大小 (bytes)"""
      doc = fitz.open(pdf_path)
      # garbage=3: 垃圾回收，移除未使用物件，合併重複物件
      # deflate=True: 對 stream 進行無損壓縮
      # clean=True: 清理頁面內容樹
      doc.save(pdf_path, garbage=3, deflate=True, clean=True, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)
      doc.close()
      return pdf_path.stat().st_size
  ```
* **安全防護機制**：
  - 使用 `try...except Exception as e` 保護，若優化過程發生任何錯誤，**優雅降級**（僅輸出 warning log 並保留原始上傳檔案），絕不阻塞上傳的主流程，確保極致的穩定性。
  - **不進行任何有損影像壓縮**（如降低解析度或降低 JPEG 畫質），保證後續的 Vision 影像辨識（履歷、簡報、圖片 Caption）的特徵提取與文字識別率（OCR）處於 100% 最高品質。
  - **不進行字型子集化（Font Subsetting）重組**，避免本就損毀或格式特殊的 PDF 在重組字型時產生文字編碼錯亂（Mojibake/亂碼）的風險。

---

## 5. 變動風險與相容性評估

* **破壞性變更 (Breaking Changes)**：無。
* **衝擊評估**：
  - 檔案大小通常可縮水 30% 到 90%。
  - 數位簽章（Digital Signature）會因物件重組而失效（對於閱讀與 RAG 分析無副作用）。
  - 100% 向後相容，不會影響任何前端狀態或 DB 格式。

---

## 6. 測試與端到端（E2E）驗證計畫

* **Pytest 單元測試**：
  - 撰寫 `tests/test_pdf_optimize.py`。
  - 建立一個包含重複物件或未 deflate stream 的測試 PDF。
  - 呼叫優化函式，驗證檔案體積確實減小，且優化後的 PDF 仍能被 `fitz` 正確打開並讀取文字，無失真。
* **手動驗證步驟**：
  - 上傳一個較大的 PDF（例如大於 5MB 的學術論文）。
  - 檢查伺服器儲存的 `output/{owner_id}/{paper_id}/{paper_id}.pdf` 實體檔案大小，與原始檔案大小比對，確認體積確實縮減。
  - 開啟文件閱讀器與 AI 對話，確認文字渲染正確、圖表清晰、且問答正常。

---

## 7. 不可做 / 不可動清單

* **不可動清單**：
  - **嚴禁使用有損壓縮（Lossy Compression）**（如將解析度降到 150 DPI 以下，或將 JPEG 壓縮率調得太高），以防止影響 Vision 模型解析度。
  - **嚴禁動用第三方字型修改工具**，防範字元映射損毀。
  - **嚴禁干涉加密文件的無損保存**，對於有密碼或權限限制的 PDF 應跳過優化或保留原加密狀態。

> [!IMPORTANT]
> **日誌與資料庫規範約束：**
> 本計畫之實作如有需要寫入資料庫或輸出日誌（Logging），必須嚴格遵循 [ref/2026-05-23_database_SOP_手冊.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/ref/2026-05-23_database_SOP_手冊.md) 與 [ref/2026-05-23_logging_SOP_手冊.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/ref/2026-05-23_logging_SOP_手冊.md) 的規定，特別是「極短交易與防斷線自癒」、「標準交易語意管理（自動 Commit/Rollback）」以及「異常堆疊（Exception）與 logger 規範」。

---

## 8. 開放問題 (Open Questions)

* 目前無開放問題，此優化設計與 `QUEUE-1` 完美相容。
