# RAG-MULTI-1 C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 |
| 任務代號 | RAG-MULTI-1 C2 |
| 觸發 Commit | C2 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_tasks.md` |
| 觸發情境 | baron 確認 C1 落地，下達 C2 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：RAG-MULTI-1 / Commit：C2 / 工作流類別：BE-Refactor
- Tasks 路徑：`.claude-logs/baton/2026-06-09_RAG-MULTI-1_..._tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / framework / tasks.md（§8 C2）/ logging SOP / database SOP / template_execution

### 執行命令（依 tasks §8 C2、`# === [RAG-MULTI-1 C2 START/END] ===` 包裹）
① 改前備份 rag_retriever.py + settings.py（2 .bak）。
② `rag_retriever.py:7` import 去 RAG_MULTI_TOP_K、加 RAG_MULTI_FLOOR_K, RAG_MULTI_MAX_CHUNKS。
③ `retrieve_multi_with_context`：
   - L251-252 `top_k=RAG_MULTI_TOP_K` → `cap = top_k if top_k is not None else RAG_MULTI_MAX_CHUNKS`（top_k 簽名保留、語意 cap override）。
   - 重寫 L286-287 選取段為每篇保底演算法：
     `N = len(paper_ids)`；`effective_floor = min(RAG_MULTI_FLOOR_K, max(1, cap // N))`；
     分組各取前 effective_floor（不足全拿）→ floored + selected；
     N>cap 極端按各篇最高分取前 cap 篇各 1；
     全域補位 pool = 候選 − selected、按 score 降序補到 cap；
     top_chunks = floored + 補位、最終 score 降序。
   - context 格式 L296-300 不變；chosen= log 保留。
④ settings.py 移除 RAG_MULTI_TOP_K。
⑤ 更新既有 tests/test_phase2_p2_2_hashtag_routing.py（若斷言舊 top-k=7、否則不動）。
⚠️ 不可動：單篇 retrieve_with_context / RAG_SCORE_THRESHOLD 門檻 / context 格式 / shadow 不過濾 / 索引層。

### SOP 核查（BE-Refactor）
- logging：grep logger.error rag_retriever.py（既有 warning 不動、本次不新增 error）。
- database：grep `.commit()` rag_retriever.py → 無命中（合規、純記憶體檢索）。

### 同步更新 TODO
- C2 ✅、C3 🟡 WIP；git log 自癒回填殘留「待 baron 回填」。

### 產出規格
- 執行報告 `baton/2026-06-09_RAG-MULTI-1_C2_執行.md`（暫存 baton、嚴禁 mv/git add、baton 不入 git、C5 才歸檔）；套 template_execution；§4 含保底演算法關鍵片段+公式；§6 逐項打勾（單篇/threshold/context/shadow）。

### §8 baron 執行命令
- git add：rag_retriever.py + settings.py + 2 .bak +（受影響測試）+ TODO + 2 prompts（baton 執行報告不 git add）。
- msg 草稿寫 `/tmp/RAG-MULTI-1_C2_msg.txt`，`refactor(rag)` 前綴、署名 Claude Opus 4.8 (1M context)。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C3、不改單篇/threshold/context/shadow/ai_character_prompt/其他檔、不新建 test_rag_multi.py（C4 才建）、不 mv/git add baton、不自發 commit/push。
