# PIPE-SLIDES C5 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 05:23 |
| 任務代號 | PIPE-SLIDES C5 |
| 觸發 Commit | C5 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 確認 C4 後，下達 C5 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C5 — P4 Wire / BE-Refactor；tasks §8 C5（plan U11）

### 執行命令（tasks §8 C5）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py 實作 run_phase4（`# === [PIPE-SLIDES C5 START/END] ===` 包裹）：
   呼 `rag_indexer.index(sections=ctx.rag_sections, section_summaries=…, rag_tree_path, title/translated_title…)`
   （resume run_phase4 同範式）；四產物；≥3 門檻；異常拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready；零 A 軌 rag_processor import
③ tests 追加 mock 接線測試（傳參正確、失敗拋不吞）
- 物理防線：僅兩檔；嚴禁 import 舊 A 軌 rag_processor

### 驗收（§6.5）
- pytest + grep 'rag_processor' slide_pipeline.py → 0

### TODO 同步
- C5 ✅、C6 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C5_執行.md（暫存、不入版控）

### §8 baron 命令
- git add：兩檔 + 2 .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C5_msg.txt

### 停止
- 產出 C5_執行.md 後立即停止；不續 C6、不自發 commit/push
