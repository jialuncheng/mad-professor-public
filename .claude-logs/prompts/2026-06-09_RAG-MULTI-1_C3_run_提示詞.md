# RAG-MULTI-1 C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 |
| 任務代號 | RAG-MULTI-1 C3 |
| 觸發 Commit | C3 |
| 工作流類別 | BE-Refactor（C3 為提示詞純文字、無 .py）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_tasks.md` |
| 觸發情境 | baron 確認 C2 落地，下達 C3 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：RAG-MULTI-1 / Commit：C3 / 工作流類別：BE-Refactor（提示詞純文字）
- Tasks 路徑：`.claude-logs/baton/2026-06-09_RAG-MULTI-1_..._tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / framework / tasks.md（§8 C3）/ logging SOP / database SOP / template_execution

### 執行命令（依 tasks §8 C3、對齊 plan v3 §2 U5）
① 改前備份 prompt/ai/ai_character_prompt.txt → archive/2026-06-09_RAG-MULTI-1_C3_ai_character_prompt.txt.bak。
② ai_character_prompt.txt「3. 引用源頭」段（L17-23）段末加禁令（`# === [RAG-MULTI-1 C3] ===` 標）：
   「僅以《文件名》「章節」標註來源；嚴禁輸出 [1]、[2] 等純數字引用標記（系統未提供對應編號清單、指向虛空、屬無效引用）。」
   保留既有「標註來源章節 / 逐一標出 / 綜合多段 1-2 段」語意。
③ 共載檢查（plan v3 §8.1 點3）：`grep -nE '\[1\]|\[N\]|引用' prompt/ai/ai_explain_prompt.txt`；無反向 [N] → 不動該檔；確有則一併禁；報告貼 grep 結果。
- 物理防線：只動 ai_character_prompt.txt 引用段；不動 rag_retriever/任何 .py/context 格式/explain_prompt 無關語意。

### SOP 核查
C3 純提示詞、無 .py → logging/database SOP 不適用、跳過（合規）。

### 同步更新 TODO
- C3 ✅、C4 🟡 WIP；git log 自癒回填殘留「待 baron 回填」。

### 產出規格
- 執行報告 `baton/2026-06-09_RAG-MULTI-1_C3_執行.md`（暫存 baton、嚴禁 mv/git add、baton 不入 git、C5 才歸檔）；套 template_execution；§5 貼 explain_prompt grep。

### §8 baron 執行命令
- git add：ai_character_prompt.txt [+ explain_prompt 若有改] + .bak + TODO + 2 prompts（baton 執行報告不 git add）。
- msg 草稿寫 `/tmp/RAG-MULTI-1_C3_msg.txt`，`docs(prompt)` 前綴、署名 Claude Opus 4.8 (1M context)。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C4、不改 .py/context/其他檔、不新建 test_rag_multi.py、不 mv/git add baton、不自發 commit/push。
