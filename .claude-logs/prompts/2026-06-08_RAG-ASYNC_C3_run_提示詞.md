`````markdown
# 2026-06-08 — RAG-ASYNC C3 Run（Chunk Build·Strategy B 分塊與 size-cap）提示詞

> **收到時間**：2026-06-08 04:41（UTC+8）
> **任務代號**：RAG-ASYNC C3（BE-Refactor·階段 4 執行）
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 C2 合約報告後，下達 C3 RAG 分塊與 size-cap 機制開發指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 04:41 | 任務 RAG-ASYNC C3 | 觸發 Commit C3 | 依據 tasks §8 C3 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C3_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C3（BE-Refactor·新模組）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / logging SOP / database SOP / settings.py

### 執行命令（依 tasks §8 C3 具體實作細節）
1. 物理防線（§7 不可動）；2. 測試防線（§6.3 grep + pytest test_rag_indexer）；3. 文件防線（不自發 commit）；
4. 新建檔頂部加 # === [RAG-ASYNC] === 標記。

### 備份
僅新增 processor/rag_indexer.py + tests/test_rag_indexer.py、免 cp；若誤改既存檔即補 .bak。

### 改動（依 tasks §4.3/§8 C3）
- 新建 processor/rag_indexer.py（禁 import rag_processor）：
  - build_chunk_markdown(sections, section_summaries, doc_type)：DFS 走訪 section 樹、每節點 Stage 1 組「# {chunk_key}\nContext: {doc_type} > {title}\nChapter Summary: {summary}（缺則略）\n\n{內文}」。
  - Stage 2 size-cap：內文超 EMBEDDING_MAX_TOKENS_PER_ITEM → 遞迴子切（保段落邊界 + 小 overlap）、每子塊重貼前綴。
  - 自實作 _is_chunk_meaningful 等價（≥3 + email/phone/url 保留、純數字/markdown 噪聲過濾）。
  - 本 commit 僅至「產出 chunk 文件清單」、不嵌入。
- 新建 tests/test_rag_indexer.py：多塊 / Strategy B 格式 + summary 缺降級 / size-cap 子切 + 子塊重貼前綴 + 小節點不觸發 / 門檻 ≥3 + email 保留。

### Git 可入庫
processor/rag_indexer.py + tests/test_rag_indexer.py；baton（含 _執行.md）C7 前不 git add。

### TODO 同步 + Hash 自癒
C3 → ✅；C4 → 🟡 WIP；git log 回填佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C3_執行.md（暫存、不 git add）；§5 貼 pytest + SOP；§8 git add 清單 + msg（/tmp/RAG-ASYNC_C3_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C4、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 新增：processor/rag_indexer.py（Strategy B + size-cap + 自實作 filter、零 import rag_processor）+ tests/test_rag_indexer.py
- 驗收：grep（rag_processor 0 命中 / Strategy B + size-cap 命中）+ pytest test_rag_indexer 全綠
- 報告：baton/…_C3_執行.md（暫存、不 git add）
- 是否動業務代碼：新增模組（無既存改動）；是否 commit：否（待 baron）

## 後續引用

C3 chunk-md 生成落地（Strategy B header augment + size-cap 二段子切 + 自實作門檻、零 import rag_processor）；下一步 C4（向量落庫 + ④ conformance：embed/FAISS/paper_chunks/index_meta/RagDbSpec + rag_retriever 讀取驗證）。
`````
