`````markdown
# 2026-06-08 — RAG-ASYNC C6 Run（Wire P4·P3 旁路封存與 P4 改呼新模組）提示詞

> **收到時間**：2026-06-08 06:44（UTC+8）
> **任務代號**：RAG-ASYNC C6（BE-Refactor·階段 4 執行）
> **觸發 commit**：C6
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 C5 報告後，下達 C6 P3 旁路封存與 P4 接線指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 06:44 | 任務 RAG-ASYNC C6 | 觸發 Commit C6 | 依據 tasks §8 C6 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C6_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C6（BE-Refactor·P3 旁路 + P4 接線）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / logging SOP / database SOP / resume_pipeline.py / test_resume_pipeline.py

### 執行命令（依 tasks §8 C6 具體實作細節）
1. 物理防線（§7 不可動：rag_processor 整檔/rag_retriever/pipeline_core/④格式/run_phase1）；2. 測試防線（§6.6 grep + 全套件 pytest）；3. 文件防線（不自發 commit）；
4. 既有檔修改區塊 # === [RAG-ASYNC C6 START/END] === 包裹。

### 備份
cp resume_pipeline.py / test_resume_pipeline.py → archive/…_C6_….bak

### 改動
- run_phase3：附加封存「譯後 section 結構」（title/level/content/children）至 ctx 旁路屬性（ctx.rag_sections）；不改既有 final_zh/final_en 組裝與輸出；is_zh/degraded fallback 單一容器降級。
- run_phase4：移除 `from processor.rag_processor import RagProcessor`（L73）；改呼 processor.rag_indexer.index（輸入 ctx 旁路譯後 section 結構 + ctx.glossary_ready.section_summaries + doc_type）；不再讀 ctx.bilingual.final_zh_path 當切塊輸入；交付 RagDbSpec 不變；paper_db_id None 降級沿用。
- test_resume_pipeline.py：run_phase4 grep 0 rag_processor / mock 驗 chunks ≥ 20（多 section）/ P4 零 LLM（spy）/ RagDbSpec 交付。

### Git 可入庫
archive/ 2 .bak + resume_pipeline.py + test_resume_pipeline.py；baton（含 _執行.md）C7 前不 git add。

### TODO 同步 + Hash 自癒
C6 → ✅；C7 → 🟡 WIP；git log 回填佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C6_執行.md（暫存、不 git add）；§5 貼 pytest + SOP；§8 git add 清單 + msg（/tmp/RAG-ASYNC_C6_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C7、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（run_phase3 旁路封存 ctx.rag_sections + run_phase4 改呼 rag_indexer、砍 rag_processor import）+ test_resume_pipeline.py；各 .bak
- 驗收：grep（rag_processor 0 命中 / rag_indexer 命中 / 不餵 final_zh_path）+ 全套件 pytest + SOP
- 報告：baton/…_C6_執行.md（暫存、不 git add）
- 是否動業務代碼：是（run_phase3/run_phase4）；是否 commit：否（待 baron）

## 後續引用

C6 P4 接線完成（B 軌全鏈無 rag_processor 依賴、chunks 退化修復）；下一步 C7（Checkout 收官 + baton 一次性歸檔）。
`````
