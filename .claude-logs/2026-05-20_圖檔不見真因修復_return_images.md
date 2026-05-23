# 2026-05-20 「圖檔不見」真因修復：MinerU return_images=true + ZIP-first 取圖

只動 `processor/pdf_processor.py`。未改 metadata_extractor / pipeline_core /
paper_manager / web_server / 其他。

## 真因（已 curl 實證）
MinerU 3.1.6 `/file_parse` 的 `return_images` 預設 **False**——不顯式設
`true` 則回傳 ZIP 不含圖。curl 對照：加 `return_images=true` → ZIP 537KB
含 11 張圖；不加 → ZIP 15KB 僅 markdown。先前所有「task_id 抓到但 GCP
無目錄 / scp 落空」皆為此真因之下游症狀。

## 修改

### A. POST MinerU 加 return_images=true（process()）
form-data boolean 用字串 `"true"`（與既有 return_md/response_format_zip 一致）。

### B. _copy_images 改 ZIP-first，scp 降為 fallback
ZIP 內現已含 `_tmp/{MINERU_PAPER_NAME}/auto/images/`，直接 copytree；
僅該目錄不存在時才退回既有 server 端 scp / 本地 copytree（向後相容、
不破壞既有部署）。順序確認：`process()` 既有流程為 解ZIP → 搬 md →
**_copy_images** → `rmtree(_tmp)`，故 ZIP-first 取得到圖（在 rmtree 前）。

## 修正 diff（git diff processor/pdf_processor.py，本次相關片段）

```diff
@@ process() requests.post data @@
                     data={
                         "return_md": "true",
                         "response_format_zip": "true",
-                        "backend": "pipeline"
+                        "backend": "pipeline",
+                        # MinerU 3.1.6 預設 return_images=False，不設則 ZIP 無圖
+                        "return_images": "true",
                     },
@@ def _copy_images @@
-        """複製 MinerU 解析出的圖片目錄（雙模式，best-effort，永不 raise）。
-
-        MinerU 端子目錄名用 self.MINERU_PAPER_NAME（固定 "original"，因
-        web_server 一律以 original.pdf 送 MinerU），與本機 paper_name
-        （pdf_path.stem）無關——後者僅用於本機 markdown 檔名。
-
-        MINERU_HOST 有值 → 遠端模式：scp（無 task_id 時退回 ssh ls -t）。
-        MINERU_HOST 為空 → 本地/bind-mount 模式：MINERU_OUTPUT_DIR 視為
-        本機可讀路徑，用 shutil.copytree 複製（無 task_id 時取最新子目錄）。
-        """
+        """複製 MinerU 解析出的圖片目錄（best-effort，永不 raise）。
+
+        優先序：
+        1. **ZIP 自帶圖**：return_images=true 後 ZIP 內已含
+           _tmp/{MINERU_PAPER_NAME}/auto/images/，直接 copytree，無需 scp。
+        2. Fallback（向後相容，僅 #1 無圖時）：MinerU server 端取圖——
+           MINERU_HOST 有值 → scp（無 task_id 時退回 ssh ls -t）；
+           MINERU_HOST 為空 → 本地 MINERU_OUTPUT_DIR copytree。
+
+        MinerU 端子目錄名用 self.MINERU_PAPER_NAME（固定 "original"，因
+        web_server 一律以 original.pdf 送 MinerU），與本機 paper_name
+        （pdf_path.stem）無關——後者僅用於本機 markdown 檔名。
+        須在 rmtree(_tmp) 之前呼叫（process() 既有順序已滿足）。
+        """
         try:
             dst = str(output_dir / "images")
             mineru_name = self.MINERU_PAPER_NAME

+            # ── 第一優先：ZIP 內已含圖（return_images=true）──
+            tmp_images = output_dir / "_tmp" / mineru_name / "auto" / "images"
+            if tmp_images.is_dir():
+                shutil.copytree(tmp_images, dst, dirs_exist_ok=True)
+                n = len([p for p in Path(dst).iterdir() if p.is_file()])
+                self.logger.info(f"[copy_images] 從 ZIP 取得 {n} 張圖")
+                return
+            self.logger.info(
+                f"[copy_images] _tmp 無圖（{tmp_images}）→ 退回 server 端取圖"
+            )
+
             if self.MINERU_HOST:
                 ... （既有 scp / 本地 fallback 完全保留，未改一行）...
```

> 既有 scp 遠端模式、ssh ls -t 退回、本地 MINERU_OUTPUT_DIR copytree、
> 各既有/上輪時間軸 log 全數保留；只在最前面加一個 ZIP-first early-return。

## D. 驗證
1. **py_compile**：`processor/pdf_processor.py` 通過。
2. **pytest**：`tests/test_metadata_extractor.py` → 18 passed, 3 skipped
   （無回歸）。
3. **dry-run（scripts/diagnose_mineru.py）情境 d**（= OrcStack 現況：
   200 + 含圖 ZIP，但 server 端**無**對應 task 目錄）：
   - 修復前：`out/images 內容: (空)`
   - **修復後：`out/images 內容: ['fig1.jpg', 'fig2.jpg']`**（從 ZIP 取得，
     不依賴 server 端）→ 真因修復實證成立。
   - markdown 仍正常、無 raise、scp 不再是必要路徑。
4. **OrcStack 端到端待跑**（本環境無金鑰/真 MinerU，無法在此跑）：
   上傳 800-vdc → 預期
   - `output/1/800-vdc-.../images/` 有 11 張 .jpg
   - `_images_info.md` 非空（image_caption 自然成功）
   - 中欄文件看得到圖
   - `logs/pipeline.log` 出現 `[copy_images] 從 ZIP 取得 11 張圖`
   （`tail -f logs/pipeline.log` 觀察；上輪時間軸 log 已就緒）

## E. 推薦 commit message

```
fix(pdf_processor): MinerU 加 return_images=true 並改 ZIP-first 取圖

真因：MinerU 3.1.6 /file_parse 的 return_images 預設 False，未顯式
設 true 時回傳 ZIP 不含圖（curl 實證：true→537KB/11圖；無→15KB 僅 md），
導致 _copy_images 永遠落到脆弱的 server 端 scp，task_id 對不到目錄即無圖。

- process() POST data 補 "return_images": "true"
- _copy_images 改優先從 ZIP 解出的 _tmp/{MINERU_PAPER_NAME}/auto/images
  直接 copytree（在既有 rmtree(_tmp) 之前），server 端 scp/本地
  copytree 降為僅在 ZIP 無圖時的向後相容 fallback，邏輯與既有部署相容

dry-run（diagnose_mineru 情境 d，server 端無目錄）：修復前 images 空、
修復後取得全部圖。py_compile 通過；metadata 測試 18 passed 無回歸。
僅動 processor/pdf_processor.py。
```

## 風險
- ZIP-first 對「MINERU_HOST 遠端部署」亦生效（ZIP 本來就在回應裡，與
  HOST 設定無關）→ 多數情況不再走 scp，連帶免除 scp/port-22 依賴；
  scp 路徑僅在 return_images 仍無圖（異常）時觸發，行為與舊版等價。
- `n = len([... Path(dst).iterdir() ...])` 僅統計用於 log，不影響流程。
- 未改 rmtree 時機/既有 fallback/其他檔案，回歸面極小。
