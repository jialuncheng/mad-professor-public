# RAG-ASYNC-HOTFIX-2 HOTFIX-2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 16:06 |
| 任務代號 | RAG-ASYNC-HOTFIX-2 HOTFIX-2 |
| 觸發 Commit | HOTFIX-2 |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md` |
| 觸發情境 | baron 下達 RAG-ASYNC-HOTFIX-2 緊急熱修復執行指令 |

---

## 正文（原始提示詞全文）

### 任務資訊
- 任務編碼：RAG-ASYNC-HOTFIX-2
- 當前 Commit 代號：HOTFIX-2
- 工作流類別：BE-Hotfix
- Hotfix 規劃路徑：`.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md`

### 強制讀檔清單
- CLAUDE.md / WORKFLOW_SOP.md（自動載入）
- `.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md`（執行依據 §熱修復修法）
- logging_SOP / database_SOP 手冊

### 執行命令與代碼修改註解包裹要求
1. 修改 `pipelines/resume_pipeline.py` 與 `processor/rag_indexer.py` 既有碼，必須以
   `# === [RAG-ASYNC-HOTFIX-2 HOTFIX-2 START] === / END` 包裹。
2. 物理防線：嚴禁修改 `rag_processor.py`、`rag_retriever.py` 等檢索/載入端，B 軌僅補產旁路 json 檔。
3. 測試防線：新增並執行 4 測試（`test_build_rag_tree_keymap_matches_chunk_header`、`test_rag_tree_node_has_translated_content`、`test_run_phase4_writes_rag_tree`、`test_rag_tree_consumed_by_retriever`），pytest 通過。

### 備份規則
修改既有檔案前備份至 archive/（resume_pipeline / rag_indexer / test_rag_indexer / test_resume_pipeline 四份 .bak）。

### 同步更新 TODO.md + 歷史 Hash 自癒
- 新增 `### BE-Hotfix RAG-ASYNC-HOTFIX-2` 完成表格（Hash 待 baron 回填）。
- 自 active 列表移除本 Hotfix；索引標 ✅。
- git log 掃描自癒回填所有殘留「待 baron 回填」。

### 收官歸檔（一次性移出 baton/）
- `mv baton/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md hotfixes/`
- 執行報告直接寫 `executions/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_執行.md`（套 template_execution）。

### §8 baron 執行命令格式
- git add 清單（4 業務/測試碼 + 4 備份 + 歸檔計畫 + 執行報告 + TODO + 2 prompts）。
- commit message 草稿含 Co-Authored-By 署名、寫入 `/tmp/RAG-ASYNC-HOTFIX-2_msg.txt`。

### 停止指令
產出執行報告 + TODO/歸檔後立即停止；嚴禁自發 git commit / push。
