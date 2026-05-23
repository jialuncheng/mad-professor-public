# 跨文件 RAG 檢索與翻譯管道實作計畫 (Phase 2)

本計畫為兩步走（Two-Step）實作的**第二階段 (Phase 2)**。本階段專注於完成雙語摘要翻譯管道的無縫同步，以及基於標籤（Hashtag）邊界劃定的跨文件 RAG 混合檢索與智慧問答路由邏輯。

---

## User Review Required

> [!IMPORTANT]
> **第二階段連動與依賴說明**：
> 本計畫完全依賴 **第一階段 (Phase 1)** 完成的資料庫欄位及標籤存取機制。
> 在第一階段完成後，資料庫中已能儲存使用者的 `user_tags`（標籤陣列）。
> 第二階段將在此基礎上，實作問答解析、向量庫多重檢索合併、以及雙語翻譯管道同步。

---

## Open Questions

> [!NOTE]
> **全域 RAG Context 限制**：
> 當使用者在對話框輸入標籤（如 `#plant 說明光合作用機制`）時，若匹配的文獻有 10 幾篇，全數拉取 FAISS 向量片段會瞬間撐爆 LLM 的 Context Window。
> 我們目前規劃：在檢索時採用「全域 Merge-Sort」機制，將所有文件撈出的相似度片段混合後，統一依 L2-normalized score 排序，僅篩選出分數最高的前 $N$ 個 (預設 $N=7$) 片段。您是否同意此篩選限制數量？

---

## Proposed Changes

### 1. 雙語摘要同步管道 (Translation & Processing Pipeline)

#### [MODIFY] [metadata_extractor.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/processor/metadata_extractor.py)
* **`_ALL_FIELDS` 擴充**：
  * 新增 `"translated_abstract"` 欄位以支援雙語摘要儲存。

#### [MODIFY] [pipeline_core.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/pipeline_core.py)
* **在中譯翻譯階段後同步寫入 metadata**：
  * 當翻譯處理完畢後，從 `self.translate_processor.translated_abstract` 取出中文翻譯摘要，寫入 `self._metadata["translated_abstract"]`，使 DB upsert 能完整儲存雙語摘要。

---

### 2. 向量檢索與問答路由 (RAG & Chat Routing)

#### [MODIFY] [paper_manager.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/paper_manager.py)
* **新增 `list_paper_uuids_by_tag(session, owner_id: int, tag: str) -> list[str]`**：
  * 掃描該 owner 所有狀態為 `done` 的 `Paper.metadata_json`，篩選並回傳含有指定標籤的所有 `paper_uuid` 列表。
* **新增 `parse_query_hashtag(owner_id: int, query: str) -> tuple[Optional[str], str]`**：
  * 比對資料庫中該 owner 所有已存在的標籤。如果 `query` 開頭為匹配之 `#標籤名 `，則回傳 `(標籤名, 剩餘乾淨問題)`；否則回傳 `(None, query)`。
  * *排序防禦*：依標籤字串長度**由長到短排序**後匹配，避免 `#complex` 誤攔截 `#complex system`。

#### [MODIFY] [rag_retriever.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/rag_retriever.py)
* **新增 `retrieve_multi_with_context(owner_id: int, query: str, paper_ids: list[str], top_k: int = 7) -> str`**：
  * 併行/依序對這組 `paper_ids` 的 FAISS 向量庫進行相似度檢索。
  * 收集所有符合門檻的 candidate chunks。
  * **全域 Merge-Sort**：統一依相似度 score 降序排列，只挑選全域前 `top_k` 個 chunks，防止 Prompt 爆炸。
  * 格式化輸出統合的 RAG context（例如 `## 摘自文件《{paper_title}》`），讓 LLM 能夠清晰標註並引用多個文件來源。

#### [MODIFY] [AI_professor_chat.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/AI_professor_chat.py)
* **整合標籤解析與跨文件檢索**：
  * 在 `process_query_stream()` 入口處，呼叫 `paper_manager.parse_query_hashtag` 分離出 `tag` 與 `cleaned_query`。
  * 如果偵測到標籤，透過 `list_paper_uuids_by_tag` 抓出所有帶標籤的 papers。
  * 路由：若只有單一文件符合，沿用既有的單篇 `_get_rag_context`；若有多篇，調用 `self.retriever.retrieve_multi_with_context` 進行跨庫合併檢索。
  * 將 `cleaned_query` 傳入決策器，避免 LLM 被 `#` 前綴干擾意圖判斷。

---

## Verification Plan

### Automated Tests
- 新增 `tests/test_hashtag_parser.py` 單元測試：
  * 驗證 `#complex system` 能被精準解析出 `complex system`，且後面緊接的 query 能被正確分離。
  * 驗證長標籤匹配優先順序（`#complex system` 不會被 `#complex` 攔截）。
- 新增 `tests/test_multi_retriever.py` 檢索測試：
  * 驗證 `retrieve_multi_with_context` 跨向量庫 RAG 能在全域 Merge-Sort 後，精準回傳最高分數的前 $N$ 個 chunks。

### Manual Verification
1. 在對話框輸入：`#complex system 請說明同構性。`，驗證 AI 對話是否成功在 RAG 檢索中撈取兩篇標有該 Tag 的文獻段落，並給出正確的對照答覆。
2. 上傳一篇全新的中文論文，待處理完成後，切換語言為中文，驗證中譯摘要是否已成功由翻譯管道提取並渲染於工具列上。
