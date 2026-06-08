# RAG-ASYNC-HOTFIX-3 HOTFIX-3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 16:30 |
| 任務代號 | RAG-ASYNC-HOTFIX-3 HOTFIX-3 |
| 觸發 Commit | HOTFIX-3 |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md` |
| 觸發情境 | baron 下達 RAG-ASYNC-HOTFIX-3 緊急熱修復執行指令（#1 已落地、slot key/summary_key 依賴滿足） |

---

## 正文（原始提示詞全文）

### 任務資訊
- 任務編碼：RAG-ASYNC-HOTFIX-3
- 當前 Commit 代號：HOTFIX-3
- 工作流類別：BE-Hotfix
- Hotfix 規劃路徑：`.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md`

### 強制讀檔清單
- CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
- `.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md`（執行依據 §熱修復修法）
- logging_SOP / database_SOP 手冊

### 執行命令與代碼修改註解包裹要求
1. 修改 `pipelines/resume_pipeline.py` 既有碼，必須以
   `# === [RAG-ASYNC-HOTFIX-3 HOTFIX-3 START] === / END` 包裹。
2. 物理防線：en 主路（`elif sections and not degraded`）/ degraded / `zh_text=full_text` byte 不變；
   `_collect_render_slots`/`_collect_rag_sections` 僅複用不改；嚴禁改 rag_processor/rag_retriever/rag_indexer/config/pipeline_core；
   僅允許改 `pipelines/resume_pipeline.py`（is_zh 分支）+ `tests/test_resume_pipeline.py`。
3. 測試防線：新增 3 測試（`test_p3_zh_source_builds_per_section`、`test_p3_zh_no_section_falls_back_single`、`test_p3_zh_summary_attaches`），pytest 通過；既有 is_zh + en 主路全綠。
4. SOP 核查：database 無裸 commit；logging 本分支無新增 logger.error、既有含 exc_info=True。

### 備份規則
修改既有檔案前備份至 archive/（resume_pipeline / test_resume_pipeline 兩份 .bak）。

### 同步更新 TODO.md + 歷史 Hash 自癒
- 新增 `### BE-Hotfix RAG-ASYNC-HOTFIX-3` 完成表格（Hash 待 baron 回填）。
- 自 active 列表移除本 Hotfix；索引 RAG-ASYNC 段標 ✅。
- git log 掃描自癒回填殘留「待 baron 回填」（無明確 commit 者依 §1.7 不臆測）。

### 收官歸檔（一次性移出 baton/）
- `mv baton/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md hotfixes/`
- 執行報告直接寫 `executions/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_執行.md`（套 template_execution）。

### §8 baron 執行命令格式
- git add 清單（業務碼 + 測試碼 + 2 備份 + 歸檔計畫 + 執行報告 + TODO + 2 prompts）。
- commit message 草稿含 Co-Authored-By 署名（Claude Opus 4.8 (1M context)）、寫入 `/tmp/RAG-ASYNC-HOTFIX-3_msg.txt`。

### ⚠️ 運維提醒（執行報告 §10）
zh 來源履歷 chunk 邊界改變（單一容器→per-section）→ 衝擊 zh 來源 golden D2/D3；en byte 不變。
zh 來源履歷 golden 須重捕（`tools/golden_baseline.py capture resume --force`、en 不需）；baron 運維、非 commit。

### 停止指令
產出執行報告 + TODO/歸檔後立即停止；嚴禁自發 git commit / push。
