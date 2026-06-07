`````markdown
# 2026-06-08 — RAG-ASYNC C4 Run（Vector Persist·向量落庫與 ④ conformance）提示詞

> **收到時間**：2026-06-08 05:32（UTC+8）
> **任務代號**：RAG-ASYNC C4（BE-Refactor·階段 4 執行）
> **觸發 commit**：C4
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 C3 索引生成層報告後，下達 C4 向量庫落庫與合約相容測試指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 05:32 | 任務 RAG-ASYNC C4 | 觸發 Commit C4 | 依據 tasks §8 C4 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C4_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C4（BE-Refactor·向量落庫 + ④ conformance）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / logging SOP / database SOP / rag_indexer.py / test_rag_indexer.py

### 執行命令（依 tasks §8 C4 具體實作細節）
1. 物理防線（§7 不可動）；2. 測試防線（§6.4 grep + pytest test_rag_indexer 含 conformance）；3. 文件防線（不自發 commit）；
4. 既有檔修改區塊 # === [RAG-ASYNC C4 START/END] === 包裹。

### 備份
cp rag_indexer.py / test_rag_indexer.py → archive/…_C4_….bak

### 改動
- rag_indexer.py 加 index(...) -> RagDbSpec：build_chunk_markdown → MarkdownHeaderTextSplitter 切 → is_chunk_meaningful 過濾 → EmbeddingModel 批量 1 次 → FAISS.from_documents(MAX_INNER_PRODUCT) save_local(vectors_dir) → paper_chunks 批量 session.execute(insert)（交易外 embedding、極短交易、paper_db_id None 降級僅 FAISS+meta）→ 自寫 index_meta.json（model/dim/chunks_total）→ RagDbSpec。禁 import rag_processor（含 write_index_meta_json、自實作）。
- SOP：embedding/LLM 在 session.begin() 外、無裸 commit、logger.error 須 exc_info。
- test_rag_indexer.py 加 conformance：B 軌產 vector store → rag_retriever.load_vector_store 讀回 + 召回非空 + index_meta 鍵齊全 + paper_db_id=None 降級僅 FAISS。

### Git 可入庫
archive/ 2 .bak + rag_indexer.py + test_rag_indexer.py；baton（含 _執行.md）C7 前不 git add。

### TODO 同步 + Hash 自癒
C4 → ✅；C5 → 🟡 WIP；git log 回填佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C4_執行.md（暫存、不 git add）；§5 貼 pytest + SOP（database 交易外/無裸 commit、logging exc_info）；§8 git add 清單 + msg（/tmp/RAG-ASYNC_C4_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C5、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：rag_indexer.py（加 index 落庫：split/filter/embed/FAISS/paper_chunks/index_meta/RagDbSpec、零 import rag_processor）+ test_rag_indexer.py（加 conformance）；各 .bak
- 驗收：grep（FAISS/index_meta/paper_chunks/RagDbSpec 命中、rag_processor 0 import）+ pytest 含 conformance（rag_retriever 讀回召回）+ SOP（embedding 交易外/無裸 commit/exc_info）
- 報告：baton/…_C4_執行.md（暫存、不 git add）
- 是否動業務代碼：是（新模組擴充）；是否 commit：否（待 baron）

## 後續引用

C4 向量落庫 + ④ conformance 落地（B 軌 vector store byte 相容 rag_retriever）；下一步 C5（P2 統一六步 section_summaries 產出 + 三安全鎖）。
`````
