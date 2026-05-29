# 2026-05-29 — RAG-13-HOTFIX-1 Check 提示詞

> **收到時間**：2026-05-29 14:44
> **任務代號**：RAG-13-HOTFIX-1 Check
> **觸發 commit**：RAG-13-HOTFIX-1-Check
> **相關產出檔案**：.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md
> **觸發情境**：所有 Commit 執行完畢且核對無誤，baron 下達 Conformance 驗收與歸檔收官指令

---

## 完整提示詞

```
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | 2026-05-29 14:44                                             |
| **任務代號**     | RAG-13-HOTFIX-1 Check                                        |
| **觸發 Commit**  | RAG-13-HOTFIX-1-Check                                        |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md     |
| **觸發情境**     | 所有 Commit 執行完畢且核對無誤，baron 下達 Conformance 驗收與歸檔收官指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**
1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。
2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目：
   `- 2026-05-29 | RAG-13-HOTFIX-1 | check | Conformance 驗收與收官歸檔提示詞`
   超過 15 筆則刪除最舊一筆。
3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md`」，然後繼續執行後續步驟。
---
你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作。
### 📋 任務資訊
- **任務編碼**：RAG-13-HOTFIX-1
- **Plan 路徑**：`.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_hotfix.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md
  ```
### 📖 強制讀檔清單
請在開始驗收前，必須完整閱讀以下文件（按順序）：
```
CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/TODO.md                                   # 任務狀態（已自動載入）
.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_hotfix.md # 原始規格
.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md # Commit 拆分與驗收條件
.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md # 實際 C1 執行結果
```
---
### ✅ Conformance 驗收流程
**第一步：產出 Conformance 驗收報告**
請依據 `template_execution.md` 模板產出您的 Check 報告，寫入 `.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_Check_執行.md`，並在報告中確實包含以下交叉核對內容：
#### 1. 目標規格合規性
* 驗證自訂主題過多觸發垂直滾動條時，選單內部滾動（滾輪、拖拽等）是否已正常運作，不再觸發關閉。
#### 2. 測試計畫合規性
* **舊裸回調移除**：`grep -n "addEventListener.*scroll.*closePopups, true"` 為 0 matches。
* **新 guard 存在**：`grep -n "e.target.closest.*ctx-popup"` 確實命中。
* **resize listener 未動**：`grep -n "addEventListener.*resize.*closePopups"` 確實命中。
* **pytest 單元測試**：包含 `test_rag13_hotfix1_scroll_intercept.py` 2 項測試通過，且全量 pytest 正常。
#### 3. 不可動清單合規性
* 驗證 `web_server.py` 所有後端路由與 `pipeline_core.py` 業務代碼皆 ✅ 未觸碰。
#### 4. 提示詞歸檔稽核
* 執行 `ls .claude-logs/prompts/ | grep "RAG-13-HOTFIX-1"`，確認 `tasks`、`C1_run` 及 `Check` 提示詞物理實體均存在。
---
### 🗃️ 收官自動化動作（全部合規後才執行）
**第一步：更新 TODO.md**
將本任務從「進行中」移至「已完成」：
1. 在 `## ✅ 已完成` 區塊，新增以下已完成表格（將 Commit 關聯）：
   ```markdown
   ### Phase RAG-13 Commit RAG-13-HOTFIX-1 — 緊急熱修復：自訂主題下拉選單捲軸無作用修復
   
   | Commit | 內容 | Hash |
   |---|---|---|
   | C1 | `static/index.html` scroll handler ctx-popup 過濾 + `tests/test_rag13_hotfix1_scroll_intercept.py` 新增 | `待 baron 回填` |
   | Check | Conformance 驗收與 baton/ 全量歸檔 | `待 baron 回填` |
   ```
2. 從 `## 🟡 進行中 / ⬜ 未開始` 區塊**移除**本任務 `RAG-13-HOTFIX-1` 的所有條目。
3. 更新 `## 索引（依類別）` 底部，將 `RAG-13-HOTFIX-1` 標記為 ✅。
4. **歷史全量 Hash 審計與自愈補填**：強制執行 `git log`，自動將 `TODO.md` 頂部所有已完成任務殘留的 `待 baron 回填` 佔位符全部替換為真實 Git Hash，完成歷史自愈與 Single Source of Truth 對齊。
**第二步：物理移出與歸檔 baton/ 暫存文件**
執行以下指令，將 `baton/` 下本任務的所有暫存檔完整移至對應的正式目錄中：
```bash
# 1. 物理移動計畫檔（重新命名為 _v1.0.md 並搬移至 hotfixes/）
mv .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_hotfix.md \
   .claude-logs/hotfixes/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_hotfix_v1.0.md
# 2. 物理移動拆分清單檔（tasks）
mv .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md \
   .claude-logs/tasks/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md
# 3. 物理移動 C1 執行報告
mv .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md \
   .claude-logs/executions/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md
# 4. 物理移動 Check 執行報告 (也就是你本次產出的執行報告)
mv .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_Check_執行.md \
   .claude-logs/executions/2026-05-29_RAG-13-HOTFIX-1_Check_執行.md
```
**第三步：將所有歸檔檔案加入 Git 追蹤**
```bash
git add .claude-logs/hotfixes/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_hotfix_v1.0.md
git add .claude-logs/tasks/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md
git add .claude-logs/executions/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md
git add .claude-logs/executions/2026-05-29_RAG-13-HOTFIX-1_Check_執行.md
git add .claude-logs/prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md
git add .claude-logs/TODO.md
```
**第四步：確認 baton/ 目錄純淨度**
```bash
ls .claude-logs/baton/
# 期望只剩：README.md 與其他尚未開始的任務暫存檔
```
---
### 🛑 停止指令
**完成 TODO.md 更新與 baton/ 歸檔、`git add` 後必須立即停止所有工具呼叫。**
嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`（全部歸檔文件將由 baron 手動執行最終的 Check 階段 Commit）
- ❌ 修改任何已搬移至 `executions/`、`hotfixes/` 或 `tasks/` 的文件（已封存審計）
```

---

## 執行結果摘要

- ✅ Conformance 驗收通過（4 個維度全合規）
- ✅ baton/ 全量歸檔完成（hotfix.md + tasks.md + C1_執行.md + Check_執行.md）
- ✅ TODO.md 更新（RAG-13-HOTFIX-1 移至 ✅ 已完成）
- ✅ git add 清單備妥，等待 baron 手動 commit
