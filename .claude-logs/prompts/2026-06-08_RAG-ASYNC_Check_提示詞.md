`````markdown
# 2026-06-08 — RAG-ASYNC Check（C7 Checkout·Conformance 驗收與一次性歸檔）提示詞

> **收到時間**：2026-06-08 06:57（UTC+8）
> **任務代號**：RAG-ASYNC Check（C7 收官）
> **觸發 commit**：RAG-ASYNC-Check
> **相關產出檔案**：plan_v2 / tasks / C1-C6 執行報告（baton）
> **觸發情境**：C1-C6 全 ship，baron 下達 Conformance 驗收與 C7 收官歸檔指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 06:57 | 任務 RAG-ASYNC Check | 觸發 Commit RAG-ASYNC-Check | 依據 plan_v2/tasks/C1-C6 報告 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep）
寫入 prompts/2026-06-08_RAG-ASYNC_Check_提示詞.md + 更新 INDEX。

你扮演 Claude Code，對 RAG-ASYNC 執行 Conformance 驗收 + C7 收官歸檔。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v2 / tasks / C1-C6 執行報告

### Conformance 五維度
- 目標規格（plan_v2 §2 U1-U6 對 C1-C6 報告完成狀態）
- 驗收條件（tasks §6 grep+pytest 於 C1-C6 §5）
- 不可動清單（tasks §7 / 報告 §6 未觸碰）
- 提示詞稽核（ls prompts | grep RAG-ASYNC：plan/tasks/C1-C6 run/Check 齊全）
- msg 完整性（各報告 §8 含 cat>/tmp + 草稿全文）

### 收官（全合規後）
1. TODO：移入 ✅ 完成表（C1-C7 + hash 待回填、git log 全量自癒）+ 移除 active + 索引 ✅。
2. 產 baton/2026-06-08_RAG-ASYNC_C7_執行.md（Conformance 報告）。
3. baton 一次性 mv：plan_v2→plans//tasks→tasks//C1-C7 報告→executions/ + git add。
4. baton 乾淨度（剩 README.md）。
5. msg 寫 /tmp/RAG-ASYNC_C7_msg.txt。

### 🛑 停止
完成 TODO + mv + msg 後立即停止；不自發 commit/push；不改已歸檔報告。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- Conformance 五維度全綠（U1-U6、tasks §6、不可動清單、提示詞稽核、msg 完整）
- 收官：TODO 結案（C1-C7 完成表 + hash 自癒）+ baton 一次性歸檔（plan_v2/tasks/C1-C7 → plans//tasks//executions/）
- 是否動業務代碼：否；是否 commit：否（待 baron）

## 後續引用

RAG-ASYNC 全案結案——P4 升格 B 軌共用真理源（rag_indexer 全重寫零 import rag_processor + Strategy B + size-cap）+ P2 統一六步 section_summaries + 規格同步（含修 §1.3 P3 doc-drift）；chunks=1 退化修復、B 軌全鏈零 A 軌依賴。⚠️ C6 動 context.py（第 3 檔、plan D4 ctx 旁路）已請 baron 核可。
`````
