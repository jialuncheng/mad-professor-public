# 2026-05-20 router prompt：多 doc_type 重寫

只動 `prompt/ai/ai_router_prompt.txt` 一個檔（純文字檔，caller 每次呼叫
動態 read_file，**改完不需重啟**）。未動 `AI_professor_chat.py` 或任何
.py / 前端 / 其他 prompt。

## 真因（轉述）
原 prompt 全為「論文」「學術」設計，doc_type ∈ {news, slides, technical,
book, web} 時 router 看不到熟悉學術詞 → 對任何稍微不像論文細節的問題都
判 `direct_answer` → 跳過 RAG → AI 沒拿到文件內容 → 回「我手邊沒有這份
文件」。

實證：DeHunt 履歷問「請分析這位候選人職涯主要的領域變化」→ direct_answer。

## 修改前後對比（git diff）
```diff
@@
 系統狀態: {paper_status}
-當前論文：{paper_title}
+當前文件：{paper_title}

 請輸出 JSON，包含以下欄位：

 1. "function": 回答策略，從以下選項選一個
-   - "direct_answer": 直接回答，或問題與學術無關
-   - "page_content_analysis": 用戶提到「當前頁面」「這一段」等指代當前可見內容
-   - "macro_retrieval": 與論文整體相關、涉及論文結構、較寬泛的提問
-   - "rag_retrieval": 涉及論文細節或關鍵概念
+   - "direct_answer": 純閒聊、打招呼、與當前文件完全無關的一般問題
+   - "page_content_analysis": 用戶提到「當前頁面」「這一段」「這張圖」等指代當前可見內容
+   - "macro_retrieval": 對文件整體架構、章節組成、核心主旨的提問
+   - "rag_retrieval": 對文件內容的任何具體提問（包含人物、事件、細節、概念、論述、數據、推論等）

 2. "query": 用於檢索的完整中文問題
    - 若用戶問題省略主語或語境，根據對話歷史補充完整
    - 若有拼寫錯誤，根據上下文糾正

-選擇策略指南：
-- 若系統狀態是「無論文加載」，一律選 "direct_answer"
+判斷原則：
+- 若系統狀態是「無文件加載」，一律選 "direct_answer"
+- 若有文件加載，**預設選 "rag_retrieval"**——除非問題明顯是閒聊、打招呼、
+  或與當前文件完全無關，否則都應從文件中尋找答案。
+- 文件類型多元（論文、履歷、簡報、新聞、報告等），任何針對文件內容
+  的具體提問（包括分析、總結、評論、比較）都應透過檢索文件內容來回答。
+- 範例：
+  - 「請分析這位候選人的職涯變化」→ rag_retrieval
+  - 「這篇文章的重點是什麼」→ macro_retrieval（整體主旨）
+  - 「第三頁說了什麼」→ page_content_analysis
+  - 「作者主張什麼」→ rag_retrieval
+  - 「請比較 A 和 B」→ rag_retrieval
+  - 「請列出所有提到的公司」→ rag_retrieval
+  - 「你好」「謝謝」→ direct_answer
```
diff stat：~10 行修改 + 12 行新增（範例與 default 規則）。29 行 → 41 行。

## 驗證
- **4 個 format vars 全在**（`grep` 確認）：
  `{conversation_history}`（line 4）、`{query}`（line 7）、
  `{paper_status}`（line 9）、`{paper_title}`（line 10）。
- **`{{ }}` escape 保留**（line 40：`{{"function": ..., "query": ...}}`）。
- **`.format(**4 keys)` 實測通過**：以
  `{conversation_history='[hist]', query='[q]', paper_status='已加載',
  paper_title='[title]'}` 套版 → 899 字、無 KeyError；尾段 JSON 範本正確
  輸出為 `{"function": "選擇的功能", "query": "優化後的查詢"}`。
- **caller 對齊**（AI_professor_chat.py:141–144）：傳入 4 個 kwargs
  `query / paper_status / paper_title / conversation_history`——與 prompt
  變數名完全一致。
- 端到端（待 OrcStack 重啟，prompt 每次 read_file 即時生效）：
  - DeHunt 履歷「請分析這位候選人職涯主要的領域變化」→ 預期 router 判
    `rag_retrieval` → log 看到「決策結果: {'function': 'rag_retrieval',
    ...}」→ AI 引用履歷具體內容。
  - ALi 簡報「這份策略框架的核心觀點」→ 預期 `macro_retrieval` 或
    `rag_retrieval`。
  - 「你好」→ 仍 `direct_answer`。

## 推薦 commit message
```
fix(prompt): router prompt 多 doc_type 重寫，預設走 rag_retrieval

原 prompt 全用「論文/學術/論文整體/論文細節/關鍵概念」字眼，當
doc_type ∈ {news, slides, technical, book, web} 時 LLM router 對任何
非「論文細節」的問題都判 direct_answer → 跳過 RAG → AI 無文件上下文
→「我手邊沒有這份文件」。

實證：DeHunt 履歷「請分析這位候選人職涯主要的領域變化」→ direct_answer。

重寫：
- 「論文」→「文件」（含「無論文加載」→「無文件加載」、「當前論文」→
  「當前文件」）
- function 描述去學術化：rag_retrieval 涵蓋「人物/事件/細節/概念/論述/
  數據/推論」；macro_retrieval 涵蓋「整體架構/章節/核心主旨」
- 加「預設 rag_retrieval」原則：有文件時除非明顯閒聊/無關，否則一律
  從文件檢索
- 列舉 7 條範例（履歷分析、文章重點、頁面指代、作者主張、AB 比較、
  列舉公司、你好/謝謝）涵蓋多 doc_type

維持 4 個 format vars（{conversation_history} / {query} / {paper_status}
/ {paper_title}）與 {{ }} escape；caller AI_professor_chat.py 不需動。
prompt 為純文字檔每次呼叫即時讀，**不需重啟 web_server**。

實測：python str.format(4 kwargs) 通過、無 KeyError；29→41 行。
端到端待 OrcStack 重啟：履歷/簡報/新聞應走 rag_retrieval / macro_retrieval；
「你好」仍 direct_answer。
```

## 不可動清單（已遵守）
- AI_professor_chat.py：未動（簽名/format keys 完全相容）
- 其他 .py：未動
- 前端：未動
- 其他 prompt 檔：未動
