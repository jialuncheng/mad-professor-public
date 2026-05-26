# 2026-05-27 — WORKFLOW-2 C2 提示詞

> **收到時間**：2026-05-27 02:58
> **任務代號**：WORKFLOW-2 C2
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-05-27_WORKFLOW-2_C2_執行.md`
> **觸發情境**：baron 審查 C1 執行報告無誤並已手動 Commit，下達 C2 Check 模板 Conformance 維度升級（追加維度四提示詞歸檔 + 維度五 msg.txt 草稿完整性）與 TODO.md 歷史 Hash 自癒回填指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 02:58 |
| **任務代號** | WORKFLOW-2 C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | .claude-logs/baton/2026-05-27_WORKFLOW-2_C2_執行.md |
| **觸發情境** | baron 審查 C1 執行報告無誤並已手動 Commit，下達 C2 Check 模板 Conformance 維度升級與 TODO.md 歷史 Hash 自癒回填指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-05-27_WORKFLOW-2_C2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的「### DOC-Refactor 系列」下補登新條目，並在「## 依時間排序」首行插入新條目。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-05-27_WORKFLOW-2_C2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit：`C2 — R2 Check 模板 Conformance 維度四+五`。

### 📋 任務資訊

- **任務編碼**：WORKFLOW-2
- **當前 Commit 代號**：C2
- **工作流類別**：DOC-Refactor
- **Tasks 路徑**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md  # 本次執行的依據 tasks
.claude-logs/templates/template_prompt_for_check.md    # 本次要修改的目標模板
.claude-logs/templates/template_execution.md           # 執行報告模板（套用結構）


### 🛠️ C2 執行命令與具體實作細節

請依 `tasks.md §8 C2` 具體實作細節，擴充 Check 模板的驗收維度：

1. **備份舊模板**：
   修改前，必須先備份舊模板檔案到 `archive/`：
   `cp templates/template_prompt_for_check.md .claude-logs/archive/2026-05-27_WORKFLOW-2_C2_template_prompt_for_check.md.bak`

2. **追加兩個 Conformance 驗收維度**：
   打開 `templates/template_prompt_for_check.md`，在 `### ✅ Conformance 驗收流程` 底下的 Conformance 交叉比對表格（現有目標規格 / 驗收條件 / 不可動清單 3 行）末行之後，追加以下兩行新維度：
   - **第一行（維度四）**：
     `| **提示詞歸檔** | \`.claude-logs/prompts/\` 物理目錄 | 執行 \`ls .claude-logs/prompts/ \| grep "<任務編碼>"\`，確認 plan / tasks / run(s) / check 各階段 .md 實體存在；若缺失則立即補建自癒後繼續 |`
   - **第二行（維度五）**：
     `| **msg.txt 草稿完整性** | 本任務各執行報告 §8 | 確認每份執行報告 §8 含完整 msg.txt 草稿展示（含 \`cat > /tmp/...\` 寫入指令 + 草稿全文）；缺失則列出清單要求補完 |`

3. **追加例外處理說明**：
   在表格下方的說明段落中，追加以下自癒例外處理條款：
   > **若維度四（提示詞歸檔）缺失**：Claude Code 必須立即補建缺失提示詞 .md 物理檔案，補完後繼續收官；**若維度五（草稿完整性）不合規**：列出缺失 §8 msg.txt 展示的執行報告，要求 baron 確認後收官。

---

### 💾 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-05-27_WORKFLOW-2_C2_執行.md`（暫存 baton/）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態標記為 `Completed (Commit C2)`，任務代號為 `WORKFLOW-2 C2`）
- §1 至 §4 詳細說明 C2 變更
- §5.1 貼上 `git status -s` 真實輸出
- §5.2 貼上 tasks.md §6.2 驗收腳本之實測 grep 輸出

---

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出 C2 執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自癒填入：**

1. **WIP 狀態更新**：
   - 將本任務 `WORKFLOW-2` 下的 C2 標記為 ✅ 已完成
   - 將下一個 Commit C3 標記為 🟡 WIP

2. **歷史已完成 Hash 掃描與自癒回填（最關鍵）**：
   - 呼叫讀取工具或執行 `git log`，獲取 Git 歷史紀錄中以下已完成任務對應的真實 Commit Hash：
     - **WORKFLOW-1 C5** 的收官 Commit Hash
     - **TODO-HOTFIX-1**、**TODO-HOTFIX-1b**、**TODO-HOTFIX-1 Check** 的手動 Commit Hash
   - 將 `TODO.md` 頂部 `## ✅ 已完成` 區塊下，這兩個任務表格中所有 `待 baron 回填` 的佔位符，全部自動替換回填為讀取出的真實 Git Commit Hash

---

### 🛑 停止指令

**產出 `C2_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 C3 或後續 Commit
- ❌ 修改任何未列入本 Commit 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
```

---

## 執行結果摘要

- ✅ 第一步歸檔完成：本檔案
- ✅ `template_prompt_for_check.md`：新增維度四（提示詞歸檔）+ 維度五（msg.txt 草稿完整性）+ 自癒例外處理條款
- ✅ TODO.md：C2 標記 ✅、C3 標記 🟡 WIP；歷史 hash 自癒回填（WORKFLOW-1 C5 + TODO-HOTFIX-1 系列）
- ✅ C2 執行報告：`baton/2026-05-27_WORKFLOW-2_C2_執行.md`

## 後續引用

- C3 Run 提示詞（待建）：`.claude-logs/prompts/2026-05-27_WORKFLOW-2_C3_run_提示詞.md`
