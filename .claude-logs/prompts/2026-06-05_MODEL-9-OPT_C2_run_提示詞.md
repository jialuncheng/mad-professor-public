`````markdown
# 2026-06-05 — MODEL-9-OPT C2 Run（Embedding Resilience Core 限流與退避框架重構）提示詞

> **收到時間**：2026-06-05 17:39（UTC+8）
> **任務代號**：MODEL-9-OPT C2（BE-Refactor）
> **觸發 commit**：C2（限流與退避框架重構）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_MODEL-9-OPT_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2——`config.py` EmbeddingModel 引入 `_api_semaphore=threading.Semaphore(EMBEDDING_MAX_CONCURRENT)` + `embed_query/embed_image/_embed_batch(新)/_embed_one` 套 `@retry_call` + `with semaphore` 包 API；`embed_documents` 改批次呼 `_embed_batch`、失敗降級 `_embed_one`、移除手動 `time.sleep` linear；429 觀測 log；同步 `tiling_processor.py` 過時註解。僅改 config.py + tiling_processor.py；改前 .bak；執行報告暫存 baton 不入 Git；TODO C2✅/C3 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 17:39 |
| 任務代號 | MODEL-9-OPT C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_tasks.md |
| 觸發情境 | baron 確認上一個階段後，下達本次執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_MODEL-9-OPT_C2_run_提示詞.md + 更新 INDEX。

你現在扮演 Claude Code，執行單一 Commit C2。

### 任務資訊
- 任務編碼 MODEL-9-OPT / Commit C2 / BE-Refactor
- Tasks：baton/2026-06-05_MODEL-9-OPT_..._tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C2）
1. 物理防線：僅改 config.py + processor/tiling_processor.py；嚴禁碰 settings.py 或其他碼。
2. `# === [MODEL-9-OPT C2 START/END] ===` 包裹。
3. 備份：cp config.py / tiling_processor.py → archive .bak。
4. 核心：EmbeddingModel 加 `_api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)`；embed_query/embed_image/_embed_batch(新)/_embed_one 套 `@retry_call` + `with self._api_semaphore:` 包 API；embed_documents 改批次呼 _embed_batch + 失敗降級 _embed_one、移除手動 sleep/for；429 觀測 log；tiling_processor.py block_embeddings 上方註解改述指數退避。
5. 測試：grep _api_semaphore/Semaphore + @retry_call + (time.sleep|for attempt 0 命中) + tiling 註解；pytest test_embedding_normalize / test_llm_retry / test_tiling_paragraph。
6. SOP：config.py logging（logger.error 須 exc_info=True）/ database（無裸 commit、交易內無 API）。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C2 → ✅；C3 → 🟡 WIP；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_MODEL-9-OPT_C2_執行.md；套用 template_execution。

### §8 baron 命令
git add config.py + tiling_processor.py + 二 .bak；msg 寫 /tmp/MODEL-9-OPT_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C2_執行.md + 更新 TODO 後立即停止；不續跑 C3、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：config.py EmbeddingModel Semaphore + @retry_call 全面裝飾 + embed_documents 批次降級重構 + 429 log；tiling_processor.py 註解同步
- 測試：grep（time.sleep/for attempt 0 命中）+ test_embedding_normalize / test_llm_retry / test_tiling_paragraph + SOP
- 報告：baton/2026-06-05_MODEL-9-OPT_C2_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C1（EMBEDDING_MAX_CONCURRENT 設定）；C2 為核心重構、消費該設定；下一步 C3（test_embedding_retry 4 測試）由 baron 另行下達。
`````
