# RAG-MULTI-1 Check（C5 Checkout 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 |
| 任務代號 | RAG-MULTI-1 Check（C5）|
| 觸發 Commit | RAG-MULTI-1-Check（C5 Checkout）|
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | C1-C4 執行報告（baton/）|
| 觸發情境 | C1-C4 全部 commit 完畢，baron 下達 Conformance 驗收與收官指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：RAG-MULTI-1 / Checkout（C5）
- Plan：baton/2026-06-09_RAG-MULTI-1_..._plan_v3.md（+ v1/v2）；Tasks：baton/..._tasks.md
- 執行報告：baton/ C1/C2/C3/C4 執行.md

### Conformance 三維度（+提示詞稽核 + msg 完整性）
1. 目標規格（plan v3 §2 U1-U7）逐項對應 C1-C4 報告（尤 U2 演算法/U5 禁[N]/U6 單篇/U7 shadow）。
2. 驗收條件（tasks §6.1-§6.5）每條 grep/pytest 在報告 §5 通過（C4 11 測試、全套件 546 passed）。
3. 不可動清單（tasks §7）全報告 §6 標 ✅（單篇/threshold/context 格式/shadow/索引）。
4. 提示詞稽核：`ls prompts/ | grep RAG-MULTI-1` plan/Tasks/C1-C4 run/Check 齊全。
5. msg 完整性：各報告 §8 含 msg 草稿。

### 收官動作（全綠後）
1. TODO：新增 `### BE-Refactor RAG-MULTI-1` 完成表（C1 `5b9477a`/C2 `82b95b1`/C3 `b5f9ce4`/C4-C5 待回填）+ 自 active 移除 + 索引 ✅ + 全量 hash 自癒。
2. baton 一次性 mv + git add：plan v1/v2/v3 → plans/ + tasks → tasks/ + C1-C4 報告 → executions/。
3. 確認 baton 無 RAG-MULTI-1 殘留。
4. C5 報告直寫 executions/（不過 baton）+ git add。
5. msg 草稿寫 `/tmp/RAG-MULTI-1_C5_msg.txt`（refactor(rag) 前綴、署名 Claude Opus 4.8 (1M context)）。

### 停止指令
完成 TODO/baton 歸檔/C5 報告後立即停止；不自發 commit/push、不改已歸檔文件、不碰 .py。
