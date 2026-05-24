# 2026-05-20 RAG 檢索失敗修復（tuple unpack → 單值賦值）

只動 `AI_professor_chat.py` 一處（兩行：`context, _ = …` → `context = …`、
`return context` → `return context or ""`）。未動 rag_retriever / ai_core /
web_server / 前端 / 其他 .py。

## 真因（轉述）
`rag_retriever.retrieve_with_context(...) -> str`（line 85）回字串：
成功 join、失敗回 `""`。但 caller `AI_professor_chat._get_rag_context` 寫成
`context, _ = self.retriever.retrieve_with_context(...)`——對字串做 tuple
unpack：
- 成功（非空 str）→ 試圖解多字元 `'a','b',...` 成 2 個 → `too many values`
- 失敗（`""`）→ 0 字元 → **`not enough values to unpack (expected 2, got 0)`**
炸後 `except` 把錯誤吞掉、回 `""` → AI 沒拿到 RAG 上下文 →「我手邊沒有
這篇文本的詳細內容」。

## grep 結果（全 repo callers）
```
AI_professor_chat.py:204:            context, _ = self.retriever.retrieve_with_context(  ← 唯一 caller（本次修）
rag_retriever.py:85:    def retrieve_with_context(self, query: str, paper_id: str, top_k: int = 5) -> str:  ← 定義
```
**只 1 個 caller、1 個定義。無其他需處理的 caller。**

## 修改 diff（AI_professor_chat.py:204–207）
```diff
@@ class AIProfessorChat:
                 return ""
             if not self.retriever.is_ready():
                 return ""
-            context, _ = self.retriever.retrieve_with_context(
+            context = self.retriever.retrieve_with_context(
                 query=query, paper_id=paper_id, top_k=5
             )
-            return context
+            return context or ""
         except Exception as e:
             self.logger.error(f"RAG檢索失敗: {str(e)}")
             return ""
```
- `context, _ = …` → `context = …`：與 retriever 簽名 `-> str` 一致。
- `return context` → `return context or ""`：caller 既有契約是「總是回字串」，
  顯式保證 None/空也回 `""`（與 except 路徑等價、call site 不需再判 None）。

## 驗證
- **py_compile** `AI_professor_chat.py`：通過。
- **pytest** `tests/test_metadata_extractor.py -q`：**18 passed, 3 skipped**
  （metadata 測試與此 module 無關，符合預期不變；該 module 無單元測試）。
- **端到端**（待 OrcStack 重啟）：開任一 paper → 問問題 → 預期
  `logs/chat.log` 不再出現「RAG檢索失敗: not enough values to unpack」；
  AI 應能引用文章具體內容回答，而非「我手邊沒有這篇文本的詳細內容」。

## 推薦 commit message
```
fix(AI_professor_chat): _get_rag_context 改單值賦值，修 RAG 檢索失敗

rag_retriever.retrieve_with_context 簽名與行為皆為 `-> str`（成功 join、
失敗 ""），但 AI_professor_chat._get_rag_context 寫成 tuple unpack
`context, _ = …`：對字串解包必炸——
- 失敗時 "" 解 0 字元 → not enough values to unpack (expected 2, got 0)
- 成功時非空 str 解多字元 → too many values to unpack
炸後 except 吞錯、回 ""，AI 取不到 RAG 上下文 → 一直回「我手邊沒有
這篇文本的詳細內容」。

修法：caller 改單值賦值，並 `return context or ""` 保證契約：
  context = self.retriever.retrieve_with_context(...)
  return context or ""

grep 全 repo：retrieve_with_context 僅此 1 caller + 1 定義；無其他需動。
不動 rag_retriever（簽名/行為一致）；未動 ai_core / web_server / 前端 /
其他 .py。

py_compile 通過；metadata 測試 18 passed 3 skipped 無回歸。
端到端待 OrcStack 重啟：log 不再報 RAG 檢索失敗、AI 能引用文章具體內容。
```

## 不可動清單（已遵守）
- rag_retriever.py：未動（簽名與行為對齊「回字串」，caller 端錯）
- ai_core.py / web_server.py / 前端 / 其他 .py：未動
- 未引入新檔案 / 新 CDN
