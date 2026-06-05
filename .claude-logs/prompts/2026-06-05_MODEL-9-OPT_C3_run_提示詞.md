`````markdown
# 2026-06-05 — MODEL-9-OPT C3 Run（Unit Tests 限流與重試契約測試）提示詞

> **收到時間**：2026-06-05 17:50（UTC+8）
> **任務代號**：MODEL-9-OPT C3（BE-Refactor）
> **觸發 commit**：C3（限流與重試契約測試）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_MODEL-9-OPT_C3_執行.md`
> **觸發情境**：baron 確認 C2 後下達 C3——新建 `tests/test_embedding_retry.py` 4 測試（mock `client.models.embed_content`）：A embed_query 429 退避 / B embed_image 503 重試 / C embed_documents 批次降級逐筆保序 / D Semaphore 併發上限；`# === [MODEL-9-OPT C3 START/END] ===` 包裹。僅新建測試檔；執行報告暫存 baton 不入 Git；TODO C3✅/C4 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 17:50 |
| 任務代號 | MODEL-9-OPT C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_tasks.md |
| 觸發情境 | baron 確認上一個階段後，下達本次執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_MODEL-9-OPT_C3_run_提示詞.md + 更新 INDEX。

你現在扮演 Claude Code，執行單一 Commit C3。

### 任務資訊
- 任務編碼 MODEL-9-OPT / Commit C3 / BE-Refactor
- Tasks：baton/2026-06-05_MODEL-9-OPT_..._tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C3）
1. 物理防線：僅新建/編輯 tests/test_embedding_retry.py；嚴禁碰 config.py/settings.py/其他碼。
2. `# === [MODEL-9-OPT C3 START/END] ===` 包裹全測試內容。
3. 新建檔無須 .bak。
4. 核心：mock client.models.embed_content 拋 429/503，驗 embed_query/embed_image 退避；驗 embed_documents 批次失敗降級逐筆保序 + warning；驗高併發 embed_query 受 EMBEDDING_MAX_CONCURRENT 限流。
5. 測試：pytest test_embedding_retry（4 passed）+ test_embedding_normalize/llm_retry/tiling_paragraph 全綠。
6. SOP：test 檔靜態 logging/database 檢測（無裸 commit）。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C3 → ✅；C4 → 🟡 WIP；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_MODEL-9-OPT_C3_執行.md；套用 template_execution。

### §8 baron 命令
git add tests/test_embedding_retry.py + TODO + prompts；msg 寫 /tmp/MODEL-9-OPT_C3_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C3_執行.md + 更新 TODO 後立即停止；不續跑 C4、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：tests/test_embedding_retry.py 4 測試（429 退避 / 503 重試 / 批次降級保序 / Semaphore 限流）
- 測試：4 passed + 既有 embedding/retry/tiling 不退化
- 報告：baton/2026-06-05_MODEL-9-OPT_C3_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C2（EmbeddingModel Semaphore+retry 重構）；C3 驗證其契約；下一步 C4 Checkout 收官歸檔由 baron 另行下達。
`````
