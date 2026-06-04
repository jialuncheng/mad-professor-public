`````markdown
# 2026-06-04 — PIPE-RESUME C5 Run 提示詞

> **收到時間**：2026-06-04 19:52（UTC+8）
> **任務代號**：PIPE-RESUME C5
> **觸發 commit**：C5（P4 Async RAG — 門檻 ≥3 技能詞保護）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C5_執行.md`
> **觸發情境**：baron 確認 C4 已手動提交（Checkout 含 C1-C4），下達 C5 執行指令——實作 `run_phase4`：讀 `ctx.bilingual.final_zh_path` → `RagProcessor()._create_vector_store`（vectors_path + paper_db_id）→ `_is_chunk_meaningful`(doc_type=resume ≥3) → `replace_paper_chunks` 批量寫庫 → 讀 `index_meta.json` → 交付 `RagDbSpec`；錯誤僅 `logger.warning(exc_info=True)` 拋出由 Orchestrator 標 rag_status='failed' 不阻主鏈。產報告暫存 baton/、同步 TODO.md（C5 ✅ / C6 WIP + Hash 自癒）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-04 19:52` |
| **任務代號** | `PIPE-RESUME C5` |
| **觸發 Commit** | `C5` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | baron 確認 C4 已手動提交，下達 C5 執行指令（當前 Checkout Commit 含 C1 至 C4）。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_PIPE-RESUME_C5_run_提示詞.md`（依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行、超 15 刪最舊）。
3. 回覆「✅ 提示詞已歸檔：...」後續執行。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit。

### 📋 任務資訊
- **任務編碼**：`PIPE-RESUME` / **當前 Commit**：`C5` / **工作流**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令與代碼修改規則
依 tasks §8 C5。物理防線（§7）/ 測試防線（§6.5 + §6.7 SOP）/ 文件防線（§1.3 不自發 commit）/ C5 START/END 包裹。
**P4 Async RAG 實作約束**：
- 輸入：run_phase4 唯一輸入為 P3 中文 Markdown 路徑 `ctx.bilingual.final_zh_path`。
- 向量化：實例化 `RagProcessor`、呼叫 `_create_vector_store`（傳 final_zh_path + `paper_manager.vectors_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)`）。
- 過濾與寫入：內部自動 `_is_chunk_meaningful`(doc_type="resume"、≥3、保 email/phone/url、不改演算法) + `paper_manager.replace_paper_chunks` 批量寫入。
- DB 交易邊界：寫入不含 LLM/Embedding；以 `paper_manager.get_paper_db_id(ctx.owner_id, ctx.paper_id)` INT id 為 `paper_db_id`；None 則優雅降級（log warning、跳過 DB 寫）。
- 載入與交付：讀 vectors 下 `index_meta.json` 轉 Dict + `chunks_total`（=`paper_chunk_count`），交付 `RagDbSpec(vectors_path, paper_chunk_count, index_meta)`。
- 錯誤隔離：P4 內部異常僅 `logger.warning(..., exc_info=True)` 並拋出，交 Orchestrator 設 `rag_status='failed'`、絕不阻 `reading_ready`。

### 💾 備份規則
`cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C5_resume_pipeline.py.bak`

### 🔄 同步更新 TODO.md（必做、即時）
C5 → ✅（待 baron 回填）；C6 → 🟡 WIP；歷史 Hash 自癒（含 C4 hash 回填）。

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C5_執行.md`（暫存 baton/、不入版控）；套用 template_execution。

### 📝 §8 baron 執行命令
git add resume_pipeline.py + .bak；msg 寫 /tmp/PIPE-RESUME_C5_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出 C5_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`pipelines/resume_pipeline.py` `run_phase4` 實作（RagProcessor._create_vector_store + _is_chunk_meaningful ≥3 + replace_paper_chunks + index_meta.json → RagDbSpec）
- 測試：§6.5 grep + §6.7 SOP（DB 交易邊界 / logging exc_info）+ 既有全套件防 Regression
- 報告：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C5_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C4（P3）。本階段 C5 實作 P4（四 Phase 全落地）；下一步 C6 單元測試由 baron 另行下達。
`````
