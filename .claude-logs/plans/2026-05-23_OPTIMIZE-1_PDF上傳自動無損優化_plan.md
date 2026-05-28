# OPTIMIZE-1 PDF上傳自動無損優化 plan

> 本計畫旨在重構 PDF 上傳與優化流程，實現使用者先選類型再選檔案上傳的 1-Step 一字步體驗。在前端 100% 挪用與復用既有 HTML/CSS 樣式（#confirm-modal 與 #doc-type-dropdown），僅翻轉事件控制流（Control Flow）為事前選擇，避免誤觸上傳與流量浪費。檔案上傳時，後端第一時間對 PDF 進行無損垃圾回收與資料流壓縮，採用暫存寫入＋原子覆寫（Atomic Overwrite）寫入安全防線，同時完全刪除簡報自動偵測以釋放 CPU，並依 Logging/Database SOP 進行結構化性能日誌記錄與降級保護。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：
  1. **舊流程 UX 與資源痛點**：舊流程為「先盲目上傳 ➜ 伺服器分析 ➜ 使用者再確認」，選錯檔案無法中途取消，被迫大檔案上傳造成網路流量與磁碟資源浪費。
  2. **效能瓶頸與寫入風險**：上傳時調用 CPU 密集的簡報自動偵測 (`is_slides_pdf`)；PyMuPDF 的 In-place Save 在 Disk Full/中斷時存在原檔損毀風險；且原日誌設計使用了非標準的 `pdf_optimize` 事件名並缺失 `duration_seconds` 指標，違反 Logging SOP。
- **解法**：
  1. **前端 100% 版型復用與控制流翻轉**：100% 保留並復用既有 UI/CSS，不建立新 HTML，直接挪用原 `#confirm-modal` 與 `#doc-type-dropdown` 下拉選單。點擊上傳按鈕時，直接顯示類型選擇 Modal。若使用者點錯而按 ESC 或點取消，Modal 安全隱藏，不彈原生選檔，零網路請求，無痛退出；選定類型並點確定後，前端自動喚起原生選檔，一次性將 `file` 和 `doc_type` 提交上傳。
  2. **後端徹底簡化**：後端直接收到 `doc_type`，**徹底刪除無價值的背景自動偵測邏輯**以釋放伺服器 CPU。
  3. **原子無損優化核心（Atomic Overwrite）**：使用 PyMuPDF (`garbage=3, deflate=True, clean=True`) 對上傳後的 PDF 進行無損壓縮，採用「寫入 `.tmp.pdf` 暫存檔 ➜ 正常結束後原子替換原檔（`tmp_path.replace(pdf_path)`）」的安全防線，防範寫入中斷損毀。
  4. **日誌 SOP 合規化**：性能指標日誌使用標準的 `"event": "performance_metric"` 且 `"stage": "pdf_optimize"` 標籤，並記錄執行耗時的實測 `"duration_seconds": float` 指標。
- **影響**：影響前端 UI `static/index.html` 的事件監聽與後端 `web_server.py` 的 `/api/papers/upload` 接收與優化邏輯。無資料庫 Schema 變動。

---

## §2 目標規格

1. **前端 Modal 控制流翻轉規格**：
   - 使用者點擊「上傳文件」時，不直接彈出選檔視窗，而是直接彈出原有的毛玻璃風格 Modal，保留下拉選單。
   - 按下 **ESC** 鍵或點擊「取消」時，Modal 安全隱藏，**絕不喚起原生選檔視窗，不發送任何網路請求**。
   - 選擇類型並確定後，Modal 關閉並**自動喚起**原生選檔。選定檔案後，將 `file` 與 `doc_type` 封裝在 `FormData` 中一次性 POST 提交至 `/api/papers/upload`。
2. **API 簡化與自動偵測移除規格**：
   - 上傳與類型指定合併為單一 POST 端點。
   - **徹底刪除 `SlidesProcessor.is_slides_pdf` 自動偵測程式碼**。
   - 任務狀態直通 `processing` 狀態，不再經過 `waiting_confirm`。
3. **原子無損壓縮（Atomic Overwrite）安全規格**：
   - 核心優化參數使用 PyMuPDF 無損優化：`garbage=3, deflate=True, clean=True`，100% 保持文字與嵌入圖片原始畫質。
   - **寫入安全防線**：`fitz` 優化結果先寫入臨時暫存檔 `*.tmp.pdf`。寫入完成且正常關閉後，再調用系統 `replace` 原子替換原檔，防止因寫入中斷損毀原檔。
   - **防禦性容錯**：全部優化流程包裹於 `try...except` 中，遇任何錯誤（如壞檔）優雅降級保留原始上傳檔案，防範系統崩潰。
4. **雙 SOP 日誌合規規格**：
   - 性能指標日誌必須指定 `"event": "performance_metric"` 且 `"stage": "pdf_optimize"`。
   - 必須在無損優化前後使用 `time.time()` 計時，並在日誌的 `extra_fields` 中記錄實測的 `"duration_seconds": round(duration, 2)`。
   - 錯誤日誌必須使用 `logger.error("...", exc_info=True)`，確保異常堆疊格式符合 Loki 規範。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈（必須指出確切的檔案與行數，並附帶 `grep` 核查證據）：

- **`web_server.py`**：
  - `upload_paper L432-480`：現狀下直接 `wb` 寫入，且包含極其耗時的自動偵測：
    ```python
    # 儲存上傳的 PDF
    with open(pdf_path, 'wb') as f:
        f.write(content)
    # 偵測是否為簡報
    suggested = await loop.run_in_executor(
        None, SlidesProcessor.is_slides_pdf, str(pdf_path)
    )
    ```
- **`static/index.html`**：
  - `upload-btn L3193-3241`：現狀下點擊直接觸發 `input.click()` 彈出選檔，隨後立即發起 POST 請求盲目上傳檔案，收到 response 後才呼叫 `showConfirmModal` 彈出 Modal 確認類型。

### §3.1 grep 鋼鐵證據

```bash
# 檢測 web_server.py 寫檔與自動偵測邏輯
grep -n -C 5 "with open(pdf_path" web_server.py
# 輸出：
# 457:    with open(pdf_path, 'wb') as f:
# 458:        f.write(content)
# 460:    # 偵測是否為簡報，供前端預選文件類型
# 463:        suggested = await loop.run_in_executor(
# 464:            None, SlidesProcessor.is_slides_pdf, str(pdf_path)
# 465:        )

# 檢測前端上傳按鈕之 click handler 與 showConfirmModal 的連動關係
grep -n -C 5 "document.getElementById('upload-btn').addEventListener" static/index.html
# 輸出：
# 3193:document.getElementById('upload-btn').addEventListener('click', (e) => {
# 3194:  e.stopImmediatePropagation();
# 3195:  const input = document.createElement('input');
# 3196:  input.type = 'file';
# 3197:  input.accept = '.pdf';
# ...
# 3232:      showConfirmModal(paperId, data.suggested_doc_type, btn, file.name);
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `models.py` 的資料庫 Schema（維持資料庫表結構 100% 穩定，不新增排隊與任務表）
- [ ] 圖片與字型檔案的內部結構（嚴禁進行有損影像降採樣或字型子集化重組，以防 Regress 後續 Vision 辨識）
- [ ] `/api/papers/{paper_id}/status` 的基本 SSE 接口傳回格式（必須維持向下相容）
- [ ] `pipeline_core.py` 內部的各處理器邏輯（壓縮優化僅發生在上傳寫檔後，不觸碰後段處理器的業務細節）

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| database SOP 手冊 | `.claude-logs/sop/2026-05-23_database_SOP_手冊.md` |
| logging SOP 手冊 | `.claude-logs/sop/2026-05-23_logging_SOP_手冊.md` |
| 專案進度管控框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  - 在 `tests/test_pdf_optimize.py` 中新增 `test_optimize_pdf_lossless_success`：建立合法 fitz 文件，測試原子覆寫成功、體積縮減、結構可正常讀取。
  - 新增 `test_optimize_pdf_lossless_corrupted_fallback`：寫入髒資料，驗證 `try...except` 降級成功且原檔案安全無損。
  - 新增 `test_upload_paper_one_step`：模擬單一上傳 API 調用，傳入 `file` 與 `doc_type`，驗證無須 confirm 即可自動啟動 RAG Pipeline 並進入 `processing` 狀態。

### §6.2 手動端到端（E2E）驗證流程

1. 點擊「上傳文件」，驗證先跳出類型選擇彈窗。
2. 點選「取消」或按 **ESC**，驗證視窗關閉，沒有原生檔案視窗彈出，零網路請求。
3. 點選「學術論文」或「個人履歷」，彈出檔案視窗，選定後上傳.
4. 觀察日誌確認：
   - 自動偵測 `is_slides_pdf` 沒有被調用（完全避開 CPU 耗時）。
   - 輸出包含 `"event": "performance_metric"` 與 `"stage": "pdf_optimize"` 的結構化 JSON 日誌。
   - 日誌中精確包含實測的 `"duration_seconds"` 耗時指標。
5. 驗證左側欄直接進入 `processing` 進度條渲染，且 PDF 體積已縮減。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| 優化處理應在 FastAPI 主執行緒還是 `run_in_executor` 線程池中調用？ | `run_in_executor` 中調用 | 雖然無損優化耗時極短（數十到數百毫秒），但對於大檔案（如 100MB 書籍）仍可能產生短暫 CPU/IO 佔用。使用 `run_in_executor` 執行可完全避免阻塞 FastAPI 主事件迴圈，防禦高併發效能下降。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 OPTIMIZE-1 PDF上傳自動無損優化 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 OPTIMIZE-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-05-27)：**重大改版**。融合人類負責人（baron）回饋進行深度架構與 UX 重構：
  1. **前端 100% 版型復用與挪用**：完全不刪除、不重建 HTML，直接挪用原 `#confirm-modal` 和 `#doc-type-dropdown` 下拉選單版型。
  2. **事件控制流（Control Flow）翻轉**：調整事件監聽，點擊上傳按鈕先顯示 Modal（支援 ESC 與取消，零請求無痛關閉），選型並點確定後才自動喚起原生選檔並一次性提交。
  3. **自動偵測刪除**：彻底刪除無價值的背景自動偵測 `is_slides_pdf`，解放伺服器 CPU。
  4. **原子級覆寫（Atomic Overwrite）**：使用 PyMuPDF 優化結果先寫入 `.tmp.pdf` 暫存檔，正常結束後再原子替換（`tmp_path.replace(pdf_path)`），防範因寫入中斷損毀原檔。
  5. **Logging SOP 合規**：性能監控日誌使用 `"event": "performance_metric"` 且 `"stage": "pdf_optimize"` 標籤，並記錄執行耗時的實測 `"duration_seconds": float` 指標。
- v1 (2026-05-26)：初版建立，依據 `templates/template_plan.md` 定義初版 PDF 上傳優化計畫。
