# 2026-05-20 P0 Commit 2：paper-item.uploading 占位列實作（B-3 / A-3-a）

只動 `static/index.html`（+52 / -14 行）。後端 0 改動。**未 commit**。
依設計文件對齊報告 B-3 + components §7.3 + dom-reference §3.2 +
interaction §9 實作。

---

## 設計 spec 對齊

| spec 條目 | 實作對應 |
|---|---|
| components §7.3「永遠在 list 最頂端、不受 folder filter 影響」 | `insertUploadingRow` 用 `insertBefore(row, list.firstChild)`；`renderPapers` 改為先取出 uploading 列、清空 list、再放回頂端 |
| components §7.3「pointer-events: none」 | 既有 CSS（line ~484），未動 |
| components §7.3「2px 進度條 / 點圓 6px 閃爍 / 整列脈動 1.6s」 | 既有 CSS 與 keyframes，未動 |
| dom-reference §3.2 line 144–161 HTML 範例 | `insertUploadingRow` 完全照範例輸出（`data-upload-id` / `.paper-progress-dot` / `.paper-progress-text` / `.paper-progress-bar` / `.paper-progress-fill`）|
| interaction §9 上傳鏈時序「點 OK → confirm_type → SSE → 左欄插入 .paper-item.uploading」 | 占位列插入點 = `showConfirmModal` confirm-ok handler 內、`fetch confirm_type` 成功之後、`trackProgress` 之前 |
| interaction §9「processing → 更新 .paper-progress-fill width + text」 | `trackProgress` processing 分支改寫 `.paper-progress-text` + `.paper-progress-fill.style.width` |
| interaction §9「done → 移除占位、重抓 GET /api/papers」 | done / error / SSE onerror 三分支皆 `removeUploadingRow(paperId)` + 既有 `loadPapers()` 重抓 |

### 時序選擇理由
spec 明示「**confirm_type 成功後才插入**」。若提早於上傳完成（POST /upload）
即插入，使用者在 confirm modal 互動期間會看到「等待開始」文字一直閃在
左欄頂端、整列脈動——modal 阻擋互動時這視覺反而干擾。spec 時序避開
此尷尬狀態：modal 期間左欄不動、確認後立刻看到「插入 + 進度即時跳動」
的連貫感。實作完全依 spec。

---

## 改動清單（6 處）

### 1) 新增 helper（取代 `UPLOAD_BTN_LABEL` 常數，line 1666–1697）
```diff
-const UPLOAD_BTN_LABEL ='<svg ...>上傳文件';
+// 插入 .paper-item.uploading 占位列
+function insertUploadingRow(paperId, filename) {
+  const list = document.getElementById('paper-list');
+  const row = document.createElement('div');
+  row.className = 'paper-item uploading';
+  row.dataset.uploadId = paperId;
+  row.innerHTML = `
+    <div class="paper-item-header">
+      <div class="paper-item-titles">
+        <div class="paper-title-zh"></div>
+        <div class="paper-progress">
+          <span class="paper-progress-dot" aria-hidden="true"></span>
+          <span class="paper-progress-text">等待開始</span>
+        </div>
+      </div>
+    </div>
+    <div class="paper-progress-bar" aria-hidden="true">
+      <div class="paper-progress-fill" style="width:0%"></div>
+    </div>`;
+  // filename 用 textContent 避免 XSS（檔名可能含 < > & 特殊字元）
+  row.querySelector('.paper-title-zh').textContent = filename;
+  list.insertBefore(row, list.firstChild);
+  return row;
+}
+
+function removeUploadingRow(paperId) {
+  const row = document.querySelector(
+    `.paper-item.uploading[data-upload-id="${paperId}"]`
+  );
+  if (row) row.remove();
+}
```
- `escapeHtml` 不存在於 codebase → 採「innerHTML 寫骨架 + textContent 寫
  動態 filename」雙軌、無 XSS 風險。
- `UPLOAD_BTN_LABEL` 常數刪除（不再用於切換按鈕內容）。

### 2) `renderPapers` 保留占位列（line 1904–1909）
```diff
 function renderPapers() {
   const list = document.getElementById('paper-list');
+  // 保留 .paper-item.uploading 占位列（不受 folder filter 影響、永遠頂端）
+  const uploadingRows = Array.from(list.querySelectorAll('.paper-item.uploading'));
   list.innerHTML = '';
+  uploadingRows.forEach(r => list.appendChild(r));  // 頂端（list 已空）
   papersInCurrentFolder().forEach(p => {
```
- 切換 folder filter 時，正常 `.paper-item` 重渲，**但占位列保留**。
- `list.appendChild(r)` 在 `list.innerHTML=''` 之後執行，此時 list 空，
  append = 頂端；之後 papersInCurrentFolder 的 forEach append 自然接在
  uploading 列**之後**。

### 3) upload-btn `onchange`（line ~2228）
```diff
   const btn = document.getElementById('upload-btn');
-  btn.textContent = '上傳中...';
   btn.disabled = true;
   setBusy(true);
   ...
   const paperId = data.paper_id;
-  // 上傳完成，立即顯示文件類型選擇框
-  btn.textContent = '選擇類型...';
-  showConfirmModal(paperId, data.suggested_doc_type, btn);
+  // 上傳完成，立即顯示文件類型選擇框
+  // 進度顯示在左欄 .paper-item.uploading 占位列（不在按鈕文字上）
+  showConfirmModal(paperId, data.suggested_doc_type, btn, file.name);
   } catch (err) {
-    btn.innerHTML = UPLOAD_BTN_LABEL;
     btn.disabled = false;
     setBusy(false);
```
- 移除 `btn.textContent='上傳中...'`/`'選擇類型...'`（按鈕保持 icon-only SVG）
- 移除 `btn.innerHTML = UPLOAD_BTN_LABEL`（按鈕本來就是 icon-only，不需重設）
- 多傳 `file.name` 給 showConfirmModal

### 4) trackProgress（line ~2278）
processing 分支改寫 DOM 目標；done/error/onerror 移除占位列、移除
`btn.innerHTML=UPLOAD_BTN_LABEL`：
```diff
     if (data.status === 'processing') {
       const p = data.progress;
-      btn.textContent = `${p.stage_name}... ${p.progress}%`;
+      // 更新占位列文字 + 進度條（interaction §9）
+      const row = document.querySelector(
+        `.paper-item.uploading[data-upload-id="${paperId}"]`
+      );
+      if (row) {
+        row.querySelector('.paper-progress-text').textContent =
+          `${p.stage_name} ${p.progress}%`;
+        row.querySelector('.paper-progress-fill').style.width = `${p.progress}%`;
+      }
       ...
     } else if (data.status === 'done') {
       evtSource.close();
-      btn.innerHTML = UPLOAD_BTN_LABEL;
+      removeUploadingRow(paperId);
       btn.disabled = false;
       ...
     } else if (data.status === 'error') {
       evtSource.close();
-      btn.innerHTML = UPLOAD_BTN_LABEL;
+      removeUploadingRow(paperId);
       ...
     }
   };
   evtSource.onerror = () => {
     evtSource.close();
-    btn.innerHTML = UPLOAD_BTN_LABEL;
+    removeUploadingRow(paperId);
     ...
   };
```

### 5) showConfirmModal 簽名 + 插入時機（line 2354）
```diff
-function showConfirmModal(paperId, detection, btn) {
+function showConfirmModal(paperId, detection, btn, filename) {
   ...
   document.getElementById('confirm-ok-btn').onclick = async () => {
     ...
-    btn.textContent = '處理中...';
     btn.disabled = true;
     try {
       await fetch(`/api/papers/${paperId}/confirm_type`, {...});
-      // 重新追蹤進度
+      // 依 interaction §9：confirm_type 成功後才插入占位列、再 SSE 追進度
+      insertUploadingRow(paperId, filename);
       trackProgress(paperId, btn);
     } catch(e) {
-      btn.innerHTML = UPLOAD_BTN_LABEL;
       btn.disabled = false;
```

### 6) 連帶清理
| 項 | 動作 |
|---|---|
| `UPLOAD_BTN_LABEL` 常數 | 刪除（被 helper 取代） |
| `btn.textContent = '上傳中...'` ×1 | 刪 |
| `btn.textContent = '選擇類型...'` ×1 | 刪 |
| `btn.textContent = '處理中...'` ×1 | 刪 |
| `btn.innerHTML = UPLOAD_BTN_LABEL` ×5 | 刪（catch / done / error / onerror / confirm-catch）|
| `btn.disabled = true/false` | **保留**（按鈕切 disabled 即可，spec 對齊：spinner 在左欄不在按鈕）|

---

## 多檔並行（mental walk-through）
- 每次上傳獨立 paperId → 獨立 `data-upload-id` → 獨立 querySelector → 互不
  干擾。
- 多檔同時 SSE：每個 EventSource 獨立 onmessage → 各自更新自己 row。
- folder 切換時，所有 uploading 列均保留於頂端（renderPapers preserve）。

## 風險檢查
| 風險 | 緩解 |
|---|---|
| SSE done 早於 insertUploadingRow（罕見）| `removeUploadingRow` 內 `if (row) row.remove()` 守門，row 不存在則 no-op |
| folder filter 切換誤刪占位列 | renderPapers 先取出 uploadingRows、清空、appendChild 回頂端 |
| 多檔並行 uploadId 衝突 | 用 backend paperId（uuid）作 uploadId → 唯一性保證 |
| 點到占位列觸發誤動作 | CSS 既有 `pointer-events: none`（未動）|
| filename 含 HTML 特殊字元 | innerHTML 寫骨架 / textContent 寫 filename，避免 XSS |
| upload error 時 row 未建（catch 在 insertUploadingRow 之前）| catch 路徑不呼叫 removeUploadingRow（無需）|
| confirm_type fetch 失敗時 row 未建 | spec 時序 = fetch 成功後才 insert → 失敗時無 row leak |

---

## 驗證
| 項 | 結果 |
|---|---|
| `node --check`（抽出主 `<script>`） | ✓ JS SYNTAX OK |
| `grep UPLOAD_BTN_LABEL` | **0** 命中 ✓ |
| `grep '上傳中\.\.\.'` / `'選擇類型\.\.\.'` / `'處理中\.\.\.'` | 各 **0** 命中 ✓ |
| `insertUploadingRow` / `removeUploadingRow` 定義 | line 1667 / 1691 ✓ |
| `data-upload-id` 查詢 selector | line 1693 / 2287 ✓ |
| renderPapers 保留邏輯 | line 1904–1909 ✓ |
| `showConfirmModal(paperId, detection, btn, filename)` | line 2354 ✓ |
| `pytest tests/test_metadata_extractor.py -q` | **18 passed, 3 skipped**（無回歸；後端零改動）|
| diff stat | **+52 / -14**（淨 +38 行；符合報告預估 +50–100 / -20–40）|

端到端（OrcStack 重啟 + Ctrl+Shift+R 後手動驗）：
- ✓ 上傳 PDF → 選 doc_type → 按確認 → 左欄頂端立刻出現 `.paper-item.uploading` 列（檔名）
- ✓ 點圓 6px 閃爍（既有 keyframes paperUploadingBlink）
- ✓ 整列脈動（既有 keyframes paperUploadingPulse）
- ✓ 進度條從 0%→100%（每 SSE processing 事件更新）
- ✓ 文字「{stage_name} {%}」（中文，沿用後端 STAGE_DISPLAY_NAMES）
- ✓ 完成後占位列消失、loadPapers 重抓 → 正式 `.paper-item` 出現
- ✓ upload-btn 不再顯示文字進度（保留 disabled 狀態）
- ✓ 多檔並行：每列獨立追蹤
- ✓ 切換 folder filter：占位列保留於頂端

---

## 推薦 commit message

```
feat(ui): 上傳進度改為 .paper-item.uploading 占位列（B-3 / A-3-a）

依設計 spec（components §7.3 + dom-reference §3.2 + interaction §9）
把上傳進度從「按鈕文字 #upload-btn」改為「左欄頂端
.paper-item.uploading 占位列」呈現。CSS 早已就緒（包括 pulse / blink
keyframes、pointer-events:none、2px 進度條），業務 JS 直到本輪才接上。

實作 6 處：
1. 新增 insertUploadingRow / removeUploadingRow helper（取代
   UPLOAD_BTN_LABEL 常數）。filename 用 textContent 避免 XSS。
2. renderPapers 改為保留 .paper-item.uploading：先取出 → 清空 →
   appendChild 回頂端 → 再 append 正常 paper-item。切換 folder filter
   時占位列不被誤刪。
3. upload-btn onchange：移除 btn.textContent='上傳中...'/'選擇類型...'，
   showConfirmModal 多傳 file.name 為第 4 參數。
4. trackProgress processing 分支：改寫 .paper-progress-text +
   .paper-progress-fill.style.width；done / error / onerror 三分支皆
   removeUploadingRow(paperId)。
5. showConfirmModal：接收 filename 參數；confirm_type fetch 成功後才
   insertUploadingRow（spec 時序：confirm_type → 插入 → SSE 追進度）。
6. 連帶清理：UPLOAD_BTN_LABEL 常數 + 8 處 btn.textContent / btn.innerHTML
   進度顯示碼全清；保留 btn.disabled 切換邏輯。

多檔並行透過 data-upload-id（= paperId UUID）區分。pointer-events:none
仍由 CSS 守門。後端 0 改動（SSE 事件格式既有；STAGE_DISPLAY_NAMES 中文
沿用）。

node --check 通過；pytest metadata 18 passed 3 skipped 無回歸；+52/-14。

剩餘 PENDING（非本輪 scope）：
- A-3-b：.msg-regen 接 chat API（P1）
- A-3-c：刪除對話 endpoint（P1）
- A-3-d：rename paper（P1）
- A-3-g：customPrompt 取代 native prompt（P1）
- A-2-d：help-modal 文案命令式化（P1）
- A-3-e/h/j：主題持久化 / cancel / grounding 預覽（P2）
```

---

## 不可動清單（已遵守）
- CSS `.paper-item.uploading` / `.paper-progress*` / keyframes：未動
- 後端 .py / pipeline_core.STAGE_DISPLAY_NAMES / SSE 事件格式：未動
- 其他 prototype JS（除 step 4/5 內部）：未動
- prompt 檔：未動
- 未引入新 CDN / 新檔案
- **未 git add / 未 commit**
