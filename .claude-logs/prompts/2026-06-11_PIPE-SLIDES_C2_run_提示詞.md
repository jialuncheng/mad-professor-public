# PIPE-SLIDES C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 04:05 |
| 任務代號 | PIPE-SLIDES C2 |
| 觸發 Commit | C2 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 確認 C1 後，下達 C2 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C2 — P1 Vision Ingestion / BE-Refactor；tasks §8 C2（plan U1-U4）

### 執行命令（tasks §8 C2）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py 實作 run_phase1 + 私有群（`# === [PIPE-SLIDES C2 START/END] ===` 包裹）：
   - `_render_pages`：fitz get_pixmap 逐頁存 images/page-{N}.png、空白頁跳過（演算法自建、嚴禁 import A 軌 slides_processor）
   - `_transcribe_page`：Vision、temperature=settings.LLM_VISION_TEMPERATURE、忠實轉錄 prompt（含 cell 禁 ###）；條件滾動（Q1：「(續)」/cont'd/表格截斷才注入前頁、預設關、其餘並行）
   - `_detect_cover`：第 1 頁判定→metadata 入 raw_metadata／title fallback 檔名
   - `_dedupe_headers`：Q2 短行 ≤20 字 ≥60% 非封面頁剔除、log 清單
   - 每頁=section、tiles=processed JSON、source_lang 啟發式、影子 (測試) 後綴 → IngestionMetadataSpec
③ tests 追加 C2 mock 測試（封面兩路/去重/空白頁/滾動預設關/存圖檔名/temp 接線）
- 物理防線：僅兩檔；零 A 軌 import

### 驗收（§6.2）
- grep：LLM_VISION_TEMPERATURE / get_pixmap / slides_processor import=0；pytest 5+ 測試綠 + 全套件

### TODO 同步
- C2 ✅、C3 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C2_執行.md（暫存、不入版控）

### §8 baron 命令
- git add：兩檔 + 2 .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C2_msg.txt

### 停止
- 產出 C2_執行.md 後立即停止；不續 C3、不自發 commit/push
