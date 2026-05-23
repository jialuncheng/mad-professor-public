# 2026-05-20 清除 AI_professor_chat.py 內 5 處「論文」殘留

只動 `AI_professor_chat.py`（5 處 in-place 文案替換）。未動 prompt 檔、
未動 router/character/explain 邏輯本身、未動其他 .py。

## Diff
```diff
@@ class AIProfessorChat:
-    """AI對話助手 - 學術論文智能問答系統"""
+    """AI對話助手 - 文件智能問答系統"""

@@ set_paper_context
-            self.logger.info(f"已設置論文上下文: {paper_id}")
+            self.logger.info(f"已設置文件上下文: {paper_id}")
         except ...:
-            self.logger.error(f"設置論文上下文失敗: {str(e)}")
+            self.logger.error(f"設置文件上下文失敗: {str(e)}")

@@ _prepare_final_messages context_type map
             context_type = {
                 "page_content_analysis": "當前頁面內容",
-                "macro_retrieval": "論文概要",
-                "rag_retrieval": "相關論文段落"
+                "macro_retrieval": "文件概要",
+                "rag_retrieval": "相關文件段落"
             }.get(function_name, "參考資訊")
```
5 行修改、0 結構變動。

## 影響範圍
- 「文件概要」/「相關文件段落」**會注入 final_query**（line 244–245
  `context_type` 字典）→ AI 看到的 user message 標頭由「論文概要 / 相關
  論文段落」變「文件概要 / 相關文件段落」。對 AI 對履歷/新聞/簡報的稱呼
  一致性有實質影響。
- docstring（line 13）/ logger 訊息（line 42/45）僅內部，AI 看不到，
  但與整體去學術化方向一致。

## 驗證
- `py_compile AI_professor_chat.py`：**OK**
- `grep -c '論文' AI_professor_chat.py`：**0**（全清）
- `pytest tests/test_metadata_extractor.py -q`：**18 passed, 3 skipped**（無回歸）

## 推薦 commit message（單獨 commit）
```
fix(AI_professor_chat): 清除 5 處「論文」殘留，去學術化

繼前輪 prompt 措辭去學術化（router / character / explain / summary）
之後，AI_professor_chat.py 自身內仍有 5 處「論文」字面常數：
- class docstring（line 13）
- set_paper_context 兩條 logger 訊息（42 / 45）
- _prepare_final_messages 內 context_type 對應字典（244 / 245）：
  「論文概要 / 相關論文段落」

替換為「文件」對應字串。其中 context_type 兩條會實際拼入 final_query
（system message 之後的 user message 標頭），對 AI 對履歷/新聞/簡報
等非學術文件的稱呼一致性有實質影響；docstring 與 logger 僅內部，但
與整體去學術化方向一致。

未動 prompt 檔（character / explain / router / summary 等前輪已修）；
未動 router/character/explain 的呼叫鏈或邏輯；未動其他 .py。

py_compile 通過；grep 「論文」殘留 0；metadata 測試 18 passed 3 skipped
無回歸。
```

## 不可動清單（已遵守）
- prompt 檔（前輪已修）：未動
- router/character/explain 邏輯：未動（僅替換字面常數）
- 其他 .py / 前端 / 後端：未動
- 未引入新檔案 / 新 CDN
- **未 git add / 未 commit**
