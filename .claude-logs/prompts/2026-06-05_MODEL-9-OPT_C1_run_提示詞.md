`````markdown
# 2026-06-05 — MODEL-9-OPT C1 Run（Settings Knob 限流參數初始化）提示詞

> **收到時間**：2026-06-05 17:33（UTC+8）
> **任務代號**：MODEL-9-OPT C1（BE-Refactor）
> **觸發 commit**：C1（Settings Knob 限流參數初始化）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_MODEL-9-OPT_C1_執行.md`
> **觸發情境**：baron 確認 Tasks 後下達 C1——僅改 `settings.py` 新增 `EMBEDDING_MAX_CONCURRENT=int(os.getenv(...,"5"))`（緊鄰 LLM_MAX_CONCURRENT、`# === [MODEL-9-OPT C1 START/END] ===` 包裹）；純新增常數、C2 才消費、行為等價。改前 .bak；執行報告暫存 baton 不入 Git；TODO C1✅/C2 WIP + hash 自癒；msg 寫 /tmp、baron 手動 commit。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 17:33 |
| 任務代號 | MODEL-9-OPT C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_tasks.md |
| 觸發情境 | baron 確認上一個階段後，下達本次執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_MODEL-9-OPT_C1_run_提示詞.md + 更新 INDEX。

你現在扮演 Claude Code，執行單一 Commit C1。

### 任務資訊
- 任務編碼 MODEL-9-OPT / Commit C1 / BE-Refactor
- Tasks：baton/2026-06-05_MODEL-9-OPT_..._tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C1）
1. 物理防線：僅改 settings.py；嚴禁碰 config.py/llm/retry.py/其他業務碼。
2. `# === [MODEL-9-OPT C1 START/END] ===` 包裹。
3. 備份：cp settings.py → archive/2026-06-05_MODEL-9-OPT_C1_settings.py.bak
4. 測試：grep EMBEDDING_MAX_CONCURRENT（預設 5）+ grep MODEL-9-OPT C1 + pytest test_embedding_normalize。
5. SOP：settings.py logger.error / .commit() 靜態檢測（預期無命中）。
6. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C1 → ✅；C2 → 🟡 WIP；掃 git log 回填所有「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_MODEL-9-OPT_C1_執行.md；套用 template_execution（元數據塊 + §1-§8）。

### §8 baron 命令
git add settings.py + .bak；msg 寫 /tmp/MODEL-9-OPT_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C1_執行.md + 更新 TODO 後立即停止；不續跑 C2、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：settings.py 新增 EMBEDDING_MAX_CONCURRENT（預設 5、env 可調、C1 標記包裹）
- 測試：grep 驗收 + test_embedding_normalize 不退化 + SOP 無命中
- 報告：baton/2026-06-05_MODEL-9-OPT_C1_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 MODEL-9-OPT tasks v1；C1 為純設定參數、C2（config.py EmbeddingModel Semaphore+retry 重構）消費之；下一步 C2 由 baron 另行下達。
`````
