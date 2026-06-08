# RAG-MULTI-1 C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 |
| 任務代號 | RAG-MULTI-1 C1 |
| 觸發 Commit | C1 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_tasks.md` |
| 觸發情境 | baron 確認 tasks 拆分（與 plan v3 完全一致），下達 C1 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：RAG-MULTI-1 / Commit：C1 / 工作流類別：BE-Refactor
- Tasks 路徑：`.claude-logs/baton/2026-06-09_RAG-MULTI-1_..._tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / framework / tasks.md（§8 C1）/ logging SOP / database SOP / template_execution

### 執行命令（依 tasks §8 C1）
① 改前備份 settings.py → archive/2026-06-09_RAG-MULTI-1_C1_settings.py.bak。
② settings.py 於 L59 RAG_MULTI_TOP_K 鄰近、`# === [RAG-MULTI-1 C1 START/END] ===` 包裹新增：
   `RAG_MULTI_FLOOR_K = int(os.getenv("RAG_MULTI_FLOOR_K", "2"))`
   `RAG_MULTI_MAX_CHUNKS = int(os.getenv("RAG_MULTI_MAX_CHUNKS", "15"))`
   保留 RAG_MULTI_TOP_K（C2 才廢）、不動 RAG_SCORE_THRESHOLD。
- 三防線：物理（不刪 TOP_K/不動 THRESHOLD/不動 rag_retriever 等）/ 測試（§6.1 grep+import 2/15+pytest）/ 不自發 commit。

### SOP 核查（BE-Refactor 強制）
- logging：grep logger.error/format_exc settings.py → 無命中（合規）。
- database：grep `.commit()` settings.py → 無命中（合規）。

### 同步更新 TODO
- C1 ✅、C2 🟡 WIP；git log 自癒回填殘留「待 baron 回填」。

### 產出規格
- 執行報告 `baton/2026-06-09_RAG-MULTI-1_C1_執行.md`（暫存 baton、**嚴禁 mv/git add**、baton 不入 git、C5 Checkout 才歸檔）；套 template_execution。
- §5.3 SOP 核查貼 grep（無命中貼「無命中（合規）」）。

### §8 baron 執行命令
- git add：settings.py + .bak + TODO + 2 prompts（baton 執行報告不 git add）。
- msg 草稿寫 `/tmp/RAG-MULTI-1_C1_msg.txt`，`refactor(rag)` 前綴、署名 Claude Opus 4.8 (1M context)。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C2、不改 rag_retriever/ai_character_prompt/TOP_K/THRESHOLD/其他檔、不 mv/git add baton、不自發 commit/push。
