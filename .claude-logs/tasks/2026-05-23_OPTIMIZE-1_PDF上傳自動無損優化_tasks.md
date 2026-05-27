# OPTIMIZE-1 PDF上傳自動無損優化 — Tasks

> 本文件為 OPTIMIZE-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md` v2 計畫產出，含 2 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `utils/pdf_optimizer.py`（Atomic Overwrite 無損優化工具函數）/ `tests/test_pdf_optimize.py`（2 個單元測試） |
| **修改檔案** | 2 個 + 2 bak | `web_server.py`（刪除 is_slides_pdf 自動偵測 + 加 run_in_executor 優化調用 + doc_type 直通）/ `static/index.html`（Phase-Shift 事件控制流翻轉：挪用既有 `#confirm-modal` + `#doc-type-dropdown`，零新增 HTML/CSS）；各附 `.bak` 備份（強制 git add） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（OPTIMIZE-1 v2 WIP 更新）/ `prompts/INDEX.md`（v2 Tasks 條目） |
| **Commits** | 3 個 | C1 → C2 → C3 |
| **baton 歸檔** | 1 次 | C3 收官：將 baton/ 下的 plan + tasks + C1/C2 執行報告一次性 mv 歸檔至正式目錄並 git add（C1/C2 執行中暫存 baton/，C3 才移出） |

---

## §1 TL;DR（概要）

- **挑戰**：
  1. **舊上傳流程 UX 痛點**：舊流程「先盲目上傳 → 伺服器分析 → 使用者再確認」，選錯檔無法中途取消，造成網路與磁碟資源浪費。
  2. **效能瓶頸與日誌違規**：上傳端點調用耗時的 `is_slides_pdf` 自動偵測；`fitz` In-place save 存在寫入損毀風險；原 `event: "pdf_optimize"` 日誌標籤違反 Logging SOP（需改為 `event: "performance_metric" + stage: "pdf_optimize"`），且缺失 `duration_seconds` 耗時指標。
- **解法**：
  - C1 — Implement Core Optimization Module with Atomic Overwrite（實作無損優化核心與單元測試）：新建隔離工具函數 `utils/pdf_optimizer.py`，採用「暫存盤寫入 + `os.replace()` 原子覆寫」防線，使用 `time.time()` 計時，依 Logging SOP 輸出 `event: "performance_metric"`, `stage: "pdf_optimize"`, `duration_seconds` 性能日誌，完整 `try/except` 優雅降級，配套 2 個 pytest。
  - C2 — Integrate 1-Step Upload in Web Server & Frontend（整合一字步上傳端點與前台 UI）：後端刪除 `is_slides_pdf` 自動偵測，`upload_paper` 接受 `doc_type` FormData 直通 pipeline，以 `run_in_executor` 非阻塞調用優化器；前端採 **Phase-Shift 事件控制流翻轉**——100% 挪用既有 `#confirm-modal` + `#doc-type-dropdown`，零新增 HTML/CSS：攔截 `#upload-btn` click → 顯示既有 Modal → Cancel/ESC 僅關閉零網路請求 → 點確定 → 讀取 `doc-type-dropdown.dataset.value` → 動態建立 `<input type="file">` → 選檔後 `FormData` POST。
- **影響範圍**：`web_server.py`（後端上傳邏輯）+ `static/index.html`（前端上傳 UI）+ 新建 `utils/pdf_optimizer.py` + `tests/test_pdf_optimize.py`；無資料庫 Schema 變動；`pipeline_core.py` / `paper_manager.py` / `processor/*.py` 零改動。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `web_server.py` L457–465 | `with open(pdf_path, 'wb') as f: f.write(content)` 後直接調用 `is_slides_pdf` CPU 耗時偵測 | 無壓縮；自動偵測 CPU 浪費；需接受 `doc_type` 直通 pipeline |
| `static/index.html` 上傳按鈕 | 點擊直接彈原生檔案視窗 | 無類型選擇步驟；選錯無法取消 |
| `utils/pdf_optimizer.py` | 不存在 | 需新建 Atomic Overwrite 無損優化模組 |
| `tests/test_pdf_optimize.py` | 不存在 | 需新建 2 個單元測試 |

---

## §3 觀察問題

### 問題 #1：上傳後無任何壓縮 + In-place save 損毀風險

- **證據**：`web_server.py:457` — `with open(pdf_path, 'wb') as f:` 直接寫入原始 PDF（依 plan §3.1 grep 核查）
- **影響**：大型 PDF 以原始體積存磁碟；`fitz` In-place save 在 Disk Full / 斷電場景會寫壞原檔。

### 問題 #2：`is_slides_pdf` 自動偵測拖慢上傳

- **證據**：`web_server.py:463–465` — `await loop.run_in_executor(None, SlidesProcessor.is_slides_pdf, str(pdf_path))`（plan §3.1 grep）
- **影響**：每次上傳都調用視覺模型偵測，耗時數秒，且結果最終要由使用者確認，完全無價值。

### 問題 #3：日誌格式違反 Logging SOP

- **規範**：Logging SOP §4 — 效能監控日誌必須使用 `"event": "performance_metric"` + `"stage": "<phase>"`，不得自訂 `"event"` 值；必須含 `"duration_seconds": float`
- **影響**：自訂 `event` 導致 `analyze_performance.py` 統計腳本與雲端 Log-based Metrics 篩選失效。

---

## §4 設計方案

### §4.1 C1 — utils/pdf_optimizer.py（Atomic Overwrite 核心）

```python
import fitz  # pymupdf
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def optimize_pdf_lossless(pdf_path) -> bool:
    """
    Atomic lossless PDF optimization using PyMuPDF.
    1. Write optimized content to <name>.tmp.pdf
    2. os.replace() for atomic overwrite (crash-safe)
    Params: garbage=3 (GC + compact + dedup + clean xref), deflate=True, clean=True
    Returns True on success, False on graceful degradation (original retained).
    """
    pdf_path = Path(pdf_path)
    tmp_path = pdf_path.with_suffix(".tmp.pdf")
    t0 = time.time()
    try:
        original_size = pdf_path.stat().st_size
        doc = fitz.open(str(pdf_path))
        doc.save(str(tmp_path), garbage=3, deflate=True, clean=True)
        doc.close()
        tmp_path.replace(pdf_path)   # atomic overwrite — crash-safe
        optimized_size = pdf_path.stat().st_size
        duration = round(time.time() - t0, 2)
        saved_bytes = original_size - optimized_size
        saved_pct = round(saved_bytes / original_size * 100, 1) if original_size > 0 else 0.0
        logger.info(
            f"PDF losslessly optimized: {pdf_path.name}",
            extra={
                "extra_fields": {
                    "event": "performance_metric",
                    "stage": "pdf_optimize",
                    "file": pdf_path.name,
                    "original_bytes": original_size,
                    "optimized_bytes": optimized_size,
                    "saved_bytes": saved_bytes,
                    "saved_pct": saved_pct,
                    "duration_seconds": duration,
                }
            },
        )
        return True
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)   # clean up partial tmp
        logger.warning(
            f"PDF optimization failed, retaining original: {pdf_path.name}",
            extra={"extra_fields": {"file": pdf_path.name}},
            exc_info=True,
        )
        return False
```

**Logging SOP 合規要點**：
- `logger = logging.getLogger(__name__)` — 模組級命名空間（SOP §1 鐵律二）
- `"event": "performance_metric"` + `"stage": "pdf_optimize"` — 不自訂 event（SOP §4）
- `"duration_seconds": round(..., 2)` — float 耗時，無 "秒" 字樣（SOP §4）
- `exc_info=True` in `logger.warning` — 結構化 Stacktrace（SOP §3；優化失敗為非致命，用 WARNING）

### §4.2 C2 — web_server.py 整合 + frontend Phase-Shift（挪用既有 Modal，真實行號版）

> 🚨 **Hard Constraint**：嚴禁新增任何 CSS 樣式；允許補一個 `<button>` 使用既有 `modal-btn` class（零新樣式），並微調兩個既有 `data-*` 屬性值。

**後端 `web_server.py`**：

1. `upload_paper` 函數簽名加 `doc_type: str = Form(...)` 參數（從 FormData 接收）。
2. **刪除** `is_slides_pdf` 相關代碼（約 5 行，`suggested = await loop.run_in_executor(...)` 整塊）。
3. 在 `with open(pdf_path, 'wb') as f:` 區塊後插入非阻塞優化調用：
   ```python
   await loop.run_in_executor(None, optimize_pdf_lossless, str(pdf_path))
   ```
4. 直接使用傳入的 `doc_type` 啟動 pipeline，跳過 `waiting_confirm` 狀態。
5. import 補充：`from utils.pdf_optimizer import optimize_pdf_lossless`（置於檔案頂部 utils import 區）。

**前端 `static/index.html`（Phase-Shift 事件控制流翻轉，真實行號）**：

> **核心設計**：挪用既有 `#confirm-modal`（**真實 L1287**）+ `#doc-type-dropdown`（**真實 L1291**），零新增 CSS 樣式。

**Step A — Modal HTML 微調（兩點，補足取消出口 + 解鎖 ESC）**：

1. 定位 `#confirm-modal`（**真實 L1287**），將 `data-no-esc="true"` 與 `data-no-mask-close="true"` 修改為 `data-no-esc="false"` 與 `data-no-mask-close="false"`，解鎖 ESC 關閉阻擋。
2. 定位 `.modal-actions` 按鈕區（**約 L1298**），在 `#confirm-ok-btn` **之前**前插一個取消按鈕：
   ```html
   <button id="confirm-cancel-btn" class="modal-btn">取消</button>
   ```
   使用既有 `modal-btn` class，**零新增 CSS**。

**Step B — 事件控制流翻轉（Phase-Shift）**：

3. **攔截** `#upload-btn` addEventListener（**真實 L3193**）：移除原本直接觸發 `<input type="file">` 的邏輯，改為顯示 `#confirm-modal`（`modal.classList.add('show')` 或等效呼叫）。
4. **取消路徑**：綁定 `#confirm-cancel-btn` click 與 ESC 鍵 → 僅 `modal.classList.remove('show')` 關閉 Modal，**不**觸發原生 `<input type="file">`，**不**發送任何網路請求。
5. **確定路徑**：攔截 `#confirm-ok-btn` click（**真實 L3343**）→ 讀取 `#doc-type-dropdown.dataset.value` 取得 `doc_type` → 隱藏 Modal → **動態建立** `<input type="file" accept=".pdf">` → `.click()` 觸發原生選檔視窗：
   ```js
   const docType = document.querySelector('#doc-type-dropdown').dataset.value;
   modal.classList.remove('show');
   const input = document.createElement('input');
   input.type = 'file';
   input.accept = '.pdf';
   input.onchange = async (e) => {
     const form = new FormData();
     form.append('file', e.target.files[0]);
     form.append('doc_type', docType);
     await fetch('/api/papers/upload', { method: 'POST', body: form });
   };
   input.click();
   ```
6. **不刪除** `waiting_confirm` UI 區塊 HTML 與 `showConfirmModal` 骨架（見 §7 不可動清單）；既有在途任務顯示邏輯不受影響。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `tmp_path.replace(pdf_path)` 若 tmp 跨磁碟分區失敗 | 🟡 中 | 同目錄 `.tmp.pdf` 與原檔在同一分區，`os.replace` 即 atomic rename，無跨區問題 |
| `run_in_executor` 下 `fitz.open` 多線程安全性 | 🟢 低 | 每次上傳獨立 `fitz.open`/`close`，無共享 doc 物件，線程安全 |
| 前端刪除 `waiting_confirm` UI 後既有在途任務顯示異常 | 🟡 中 | pipeline_core 狀態機仍有 `waiting_confirm` 邏輯（不觸碰），只是新上傳跳過；舊任務不受影響 |
| `doc_type` FormData 欄位缺失時後端 500 | 🟡 中 | FastAPI `Form(...)` 若缺失自動 422 Unprocessable，前端 Modal 強制選擇後才觸發，用戶無法跳過 |
| fitz/pymupdf 未安裝 | 🟢 低 | 現有 PDF 流程已使用 fitz，C1 pytest 若 import 失敗立即可見 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 新檔物理存在
ls -la utils/pdf_optimizer.py
# 期望：存在，非空

# 函數定義存在
grep -n "def optimize_pdf_lossless" utils/pdf_optimizer.py
# 期望：有命中

# Atomic Overwrite 防線存在
grep -n "tmp_path.replace" utils/pdf_optimizer.py
# 期望：有命中（atomic overwrite）

# Logging SOP 合規：performance_metric event
grep -n '"event": "performance_metric"' utils/pdf_optimizer.py
# 期望：有命中

# Logging SOP 合規：stage: pdf_optimize
grep -n '"stage": "pdf_optimize"' utils/pdf_optimizer.py
# 期望：有命中

# Logging SOP 合規：duration_seconds 耗時
grep -n '"duration_seconds"' utils/pdf_optimizer.py
# 期望：有命中

# Logging SOP 合規：exc_info=True（warning 路徑）
grep -n "exc_info=True" utils/pdf_optimizer.py
# 期望：有命中

# 暫存檔清理防線
grep -n "unlink" utils/pdf_optimizer.py
# 期望：有命中（tmp cleanup on failure）

# pytest 通過
pytest tests/test_pdf_optimize.py -v
# 期望：2 passed
```

### §6.2 C2 驗收

```bash
# is_slides_pdf 已刪除
grep -n "is_slides_pdf" web_server.py
# 期望：0 命中（完全刪除）

# run_in_executor 優化調用存在
grep -n "optimize_pdf_lossless" web_server.py
# 期望：有命中（upload_paper 函數內）

# doc_type Form 參數存在
grep -n "doc_type.*Form" web_server.py
# 期望：有命中

# 前端 Phase-Shift：confirm-cancel-btn 存在（L1298 插入）
grep -n "confirm-cancel-btn" static/index.html
# 期望：有命中（取消按鈕已插入）

# ESC 解鎖：data-no-esc="false"
grep -n 'data-no-esc="false"' static/index.html
# 期望：有命中（已改 false）

# confirm-ok-btn 攔截 + doc-type-dropdown 讀取（真實 L3343 區域）
grep -n "confirm-ok-btn\|doc-type-dropdown\|createElement.*input" static/index.html
# 期望：有多命中（Phase-Shift 攔截邏輯存在）

# API 簽名確認：上傳端點仍存在
grep -n "async def upload_paper" web_server.py
# 期望：有命中（函數仍存在）

# SSE 介面未改動
grep -n "async def.*status" web_server.py
# 期望：命中（status endpoint 未移除）

# 所有 pytest 通過（含 C1 + 新 test_upload_paper_one_step）
pytest tests/ -v
# 期望：全通過（至少 3 個新 test + 既有全部）
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **`models.py` 資料庫 Schema**：純磁碟層優化，不可修改任何資料庫表結構
- [ ] **圖片畫質與字型結構**：嚴禁有損圖片降採樣或字型子集化重組（`fitz.save` 只用 `garbage/deflate/clean`）
- [ ] **`/api/papers/{paper_id}/status` SSE 接口回傳格式**：必須維持向下相容
- [ ] **`pipeline_core.py` 內部處理器邏輯**：壓縮優化只在上傳寫檔後，不觸碰後段處理器業務細節
- [ ] **`paper_manager.py` / `processor/*.py`**：全部不動
- [ ] **`web_server.py` 的 `confirm_type` endpoint（可保留）**：只保留不刪，僅新流程不經此路徑
- [ ] **既有的 `waiting_confirm` HTML 結構及 `showConfirmModal` 樣式骨架**：C2 Phase-Shift 只攔截事件控制流，嚴禁刪除或破壞既有 `waiting_confirm` 相關 HTML 元素及 `showConfirmModal` 函數骨架（既有在途任務顯示依賴這些結構）
- [ ] **主 repo 目錄**：嚴禁讀寫 worktree 父目錄

---

## §8 推薦 Commit 拆分

### C1 — Implement Core Optimization Module with Atomic Overwrite（實作無損優化核心與單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增：`utils/pdf_optimizer.py` / `tests/test_pdf_optimize.py` |
| **安全性** | 🟢 高 — 純新建模組，不觸碰任何既有業務代碼；完整 Atomic Overwrite + try/except 防禦；Logging SOP 合規 |
| **可逆性** | 🟢 高 — `git revert C1` 直接刪除兩個新建檔案；零副作用 |
| **驗收 grep 條件** | 見 §6.1：`grep '"event": "performance_metric"'` ✅ / `grep '"stage": "pdf_optimize"'` ✅ / `grep '"duration_seconds"'` ✅ / `grep "tmp_path.replace"` ✅ / `pytest tests/test_pdf_optimize.py -v` → 2 passed |
| **依賴關係** | 無前置 Commit |
| **具體實作細節** | 1. 新建 `utils/pdf_optimizer.py`：依 §4.1 完整代碼實作 `optimize_pdf_lossless(pdf_path) -> bool`。關鍵邏輯：`tmp_path = pdf_path.with_suffix(".tmp.pdf")` → `fitz.open` → `doc.save(str(tmp_path), garbage=3, deflate=True, clean=True)` → `doc.close()` → `tmp_path.replace(pdf_path)`（原子覆寫）→ 計算 `saved_bytes` / `saved_pct` / `duration` → `logger.info(msg, extra={"extra_fields": {"event": "performance_metric", "stage": "pdf_optimize", "duration_seconds": ..., ...}})`。except 路徑：`tmp_path.unlink(missing_ok=True)` + `logger.warning(msg, extra={"extra_fields": {"file": ...}}, exc_info=True)` + `return False`。2. 新建 `tests/test_pdf_optimize.py`：`test_optimize_pdf_lossless_success` — 用 `fitz.open()` 在 `tmp_path` 建立最小合法 PDF，呼叫 `optimize_pdf_lossless()`，assert 回傳 True + 檔案可 `fitz.open()` 讀取 + 無 `.tmp.pdf` 殘留。`test_optimize_pdf_lossless_corrupted_fallback` — 寫入 `b"not a pdf"` 至 `tmp_path`，呼叫 `optimize_pdf_lossless()`，assert 回傳 False + 不拋 exception + 原始檔案內容仍為 `b"not a pdf"`（降級保留）。3. 寫入 `baton/2026-05-23_OPTIMIZE-1_C1_執行.md` 執行報告（含 pytest 截圖 + §6.1 grep 結果）。|

---

### C2 — Integrate 1-Step Upload in Web Server & Frontend（整合一字步上傳端點與前台 UI）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`web_server.py`（upload_paper 邏輯重構）/ `static/index.html`（Phase-Shift 事件翻轉 + Modal HTML 微調：data-no-esc/data-no-mask-close 改 false + 插入 confirm-cancel-btn，零新增 CSS）；備份：`web_server.py.bak` + `static/index.html.bak`（**兩個 .bak 強制 git add**） |
| **安全性** | 🟡 中 — 修改前端 UI 與後端上傳入口；但 `confirm_type` 端點保留（舊流程不斷），`pipeline_core.py` 零改動；優化失敗靜默降級；前端 ESC/取消零網路請求 |
| **可逆性** | 🟢 高 — `git revert C2` 完全還原；`.bak` 備份輔助確認回滾；C1 模組獨立可保留 |
| **驗收 grep 條件** | 見 §6.2：`grep -n "is_slides_pdf" web_server.py` → 0 命中 ✅ / `grep -n "optimize_pdf_lossless" web_server.py` 有命中 ✅ / `grep -n "doc_type.*Form" web_server.py` 有命中 ✅ / `grep -n "confirm-cancel-btn" static/index.html` 有命中（取消按鈕存在）✅ / `grep -n 'data-no-esc="false"' static/index.html` 有命中（ESC 解鎖）✅ / `pytest tests/ -v` 全通過 ✅ |
| **依賴關係** | 前置 C1（`utils/pdf_optimizer.py` 必須先存在） |
| **具體實作細節** | 1. 備份：`cp web_server.py web_server.py.bak && cp static/index.html static/index.html.bak`（兩個 .bak 必須 git add）。2. `web_server.py` 頂部 import 補：`from utils.pdf_optimizer import optimize_pdf_lossless`（置於既有 utils import 區域）。3. 定位 `upload_paper` 函數（plan §3.1 grep：L432–480），函數簽名中加入 `doc_type: str = Form(...)` 參數。4. 找到並**完整刪除** `suggested = await loop.run_in_executor(None, SlidesProcessor.is_slides_pdf, str(pdf_path))` 整塊及相關 `SlidesProcessor` 使用代碼（plan §3.1 L460–465 區域）。5. 在 `with open(pdf_path, 'wb') as f: f.write(content)` 區塊結束後插入：`await loop.run_in_executor(None, optimize_pdf_lossless, str(pdf_path))`（非阻塞調用）。6. 使用傳入的 `doc_type` 直接啟動 pipeline（替換原本依賴 `confirm_type` 的邏輯），任務狀態直通 `processing`。7. 🚨 **`static/index.html` Phase-Shift（真實行號）**：（a）**Step A1** 定位 `#confirm-modal`（**真實 L1287**），將 `data-no-esc="true"` 改 `false`、`data-no-mask-close="true"` 改 `false`；（b）**Step A2** 定位 `.modal-actions` 按鈕區（**約 L1298**），在 `#confirm-ok-btn` 前插入 `<button id="confirm-cancel-btn" class="modal-btn">取消</button>`（使用既有 class，零新增 CSS）；（c）**Step B1** 定位 `#upload-btn` addEventListener（**真實 L3193**），移除直接觸發 `<input type="file">` 邏輯，改為 `confirmModal.classList.add('show')` 顯示既有 Modal；（d）**Step B2** 綁定 `#confirm-cancel-btn` click 與 ESC 事件 → 僅 `modal.classList.remove('show')`，零網路請求；（e）**Step B3** 攔截 `#confirm-ok-btn` click（**真實 L3343**）：`const docType = document.querySelector('#doc-type-dropdown').dataset.value; modal.classList.remove('show'); const input = document.createElement('input'); input.type='file'; input.accept='.pdf'; input.onchange = async(e) => { const form = new FormData(); form.append('file', e.target.files[0]); form.append('doc_type', docType); await fetch('/api/papers/upload', {method:'POST', body:form}); }; input.click();`；（f）**保留** `waiting_confirm` HTML 結構與 `showConfirmModal` 函數骨架，不刪除。8. 新增 `test_upload_paper_one_step`：mock FastAPI TestClient，一次性 POST `file + doc_type`，assert HTTP 200 + 任務直接進入 `processing` 狀態。9. 執行 `pytest tests/ -v` 確認全通過。10. 寫入 `baton/2026-05-23_OPTIMIZE-1_C2_執行.md` 執行報告（含 §6.2 grep 截圖 + E2E 手動驗證說明）。|

---

### C3 — Final Archiving and TODO Sync（收官歸檔與 TODO 結案同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`TODO.md`（OPTIMIZE-1 從 WIP 移入 ✅ 已完成 + 索引更新）/ `prompts/INDEX.md`（C3 提示詞條目）；搬移（`mv` + `git add`）：`baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md` ➜ `plans/` / `baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` ➜ `tasks/` / `baton/2026-05-23_OPTIMIZE-1_C1_執行.md` ➜ `executions/` / `baton/2026-05-23_OPTIMIZE-1_C2_執行.md` ➜ `executions/` |
| **安全性** | 🟢 高 — 純文件搬移與進度變更，100% 零 runtime 影響 |
| **可逆性** | 🟢 高 — `git reset` 或 `git revert` 可立即完全復原 |
| **驗收 grep 條件** | `ls -la .claude-logs/baton/` ➜ 僅剩 README.md（合規）✅ `ls -la .claude-logs/plans/*PDF上傳自動無損優化_plan.md` ➜ 物理存在 ✅ `ls -la .claude-logs/tasks/*PDF上傳自動無損優化_tasks.md` ➜ 物理存在 ✅ `grep -n "OPTIMIZE-1" .claude-logs/TODO.md` ➜ WIP 列表已移出、已登載於頂部 `## ✅ 已完成` 表格中 ✅ |
| **依賴關係** | 前置 C2（必須等前後端整合與單元測試均 100% 通過且執行報告寫完） |
| **具體實作細節** | 1. **物理搬移**：`mv .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md .claude-logs/plans/`；`mv .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md .claude-logs/tasks/`；`mv .claude-logs/baton/2026-05-23_OPTIMIZE-1_C1_執行.md .claude-logs/executions/`；`mv .claude-logs/baton/2026-05-23_OPTIMIZE-1_C2_執行.md .claude-logs/executions/`。2. **結案 TODO.md**：從 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 完整移除 OPTIMIZE-1 條目；在頂部 `## ✅ 已完成` 新增表格「OPTIMIZE-1 PDF上傳自動無損優化」，含 C1/C2/C3 三行（Commit代號 / 內容簡述 / Hash 留空給 baron 回填）；同步更新最底部 `## 索引（依類別）` 中 OPTIMIZE 欄位狀態改為 `✅`。3. **git add 清單**：`git add .claude-logs/plans/*OPTIMIZE-1* .claude-logs/tasks/*OPTIMIZE-1* .claude-logs/executions/*OPTIMIZE-1* .claude-logs/TODO.md .claude-logs/prompts/INDEX.md`。4. 寫入 `baton/2026-05-23_OPTIMIZE-1_C3_執行.md`（本 Commit 的執行報告），注意：C3 執行報告本身在 `git add` 時必須連同搬移後的文件一起納入（C3 執行報告放在 executions/ 直接寫入，不走 baton/）。 |

---

## §9 Open Questions

無。（plan §7 Open Question「優化應在哪個執行緒」已由 baron 決策採 `run_in_executor` 方案，避免阻塞 FastAPI 主事件迴圈；tasks 拆分階段無新增問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 OPTIMIZE-1 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 OPTIMIZE-1 的 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動業務代碼（tasks 階段只能 view/grep/文件編輯）；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複計畫書設計脈絡，不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-05-27)：初版拆分完成（C1 核心模組 + C2 web_server 整合，依 plan v1）
- v2 (2026-05-27)：**協同優化與一字步重構版（含 §0.5 baton 歸檔修正為 0 次）**。依 plan v2 重大改版：C1 加入 Atomic Overwrite 防線（暫存盤寫入 + `os.replace` 原子覆寫）、Logging SOP 合規修正（`event: performance_metric` + `stage: pdf_optimize` + `duration_seconds`）、`logger.warning` 降級日誌補 `exc_info=True`；C2 重構為 1-Step Upload（前端一字步類型選擇 Modal + 後端刪除 `is_slides_pdf` + `run_in_executor` 非阻塞優化 + `doc_type` FormData 直通 pipeline）。
- v3 (2026-05-27)：**真實行號鋼鐵定位 + 三大前端合規防線版（baron Hard Constraint）**。補入 baron 核實的真實行號：`#confirm-modal`=L1287 / `#doc-type-dropdown`=L1291 / `#upload-btn` click=L3193 / `#confirm-ok-btn` click=L3343（全面替換錯誤假設行號 L1045/L1049/L2238/L1492）。新增 Step A「Modal HTML 微調」：（A1）`data-no-esc/data-no-mask-close` 改 false 解鎖 ESC；（A2）在 `.modal-actions`（L1298）插入 `confirm-cancel-btn`（使用既有 `modal-btn` class，零新增 CSS）。§4.2、§6.2、§7、§8 C2 全量同步更新；§0.5、§1 TL;DR 說明修正。
- v4 (2026-05-27)：**追加 C3 收官歸檔 Commit**。新增 C3 — Final Archiving and TODO Sync（收官歸檔與 TODO 結案同步）：baton/ 四檔 mv 至正式目錄 + TODO.md 結案 + 索引 ✅ 更新。§0.5 Commits 數更正為 3 個、baton 歸檔更正為「1 次（C3 收官）」；§8 追加 C3 六維度表格。
