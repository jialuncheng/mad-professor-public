# 2026-05-27 — WORKFLOW-2 C1 Run 提示詞

> **收到時間**：2026-05-27 01:10
> **任務代號**：WORKFLOW-2 C1
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_Tasks_執行.md`、`.claude-logs/baton/2026-05-27_WORKFLOW-2_C1_執行.md`
> **觸發情境**：baron 審查 tasks 合規，下達 C1 模板重構並要求補回上階段 Tasks 執行報告之雙報告指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 01:10 |
| **任務代號** | WORKFLOW-2 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-05-26_WORKFLOW-2_Tasks_執行.md<br>.claude-logs/baton/2026-05-27_WORKFLOW-2_C1_執行.md |
| **觸發情境** | baron 審查 tasks 合規，下達 C1 模板重構並要求補回上階段 Tasks 執行報告之雙報告指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-05-27_WORKFLOW-2_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的「### DOC-Refactor 系列」下補登新條目，並在「## 依時間排序」首行插入新條目。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-05-27_WORKFLOW-2_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit：C1 — R1 五大提示詞模板自愈歸檔防線。

### 📋 任務資訊

- **任務編碼**：WORKFLOW-2
- **當前 Commit 代號**：C1
- **工作流類別**：DOC-Refactor
- **Tasks 路徑**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md / baton/tasks.md / templates/template_execution.md

### 🛠️ C1 執行命令與具體實作細節

1. 備份 5 個舊模板到 archive/（cp，各加 .bak 副檔名）
2. 在五個 template_prompt_for_*.md 提示詞本體最頂端（緊接元數據審計塊後），插入「第一步：主動歸檔本提示詞」強制指令區塊
3. 找到末段 `## 提示詞歸檔指令` 改為 `## 備援提示詞歸檔指令（baron 手動參考）`，加注釋說明

### ⚠️ 補發上階段結果：本輪必須產出兩份執行報告

#### 執行報告一：補 Tasks 階段執行報告
- 檔名：`.claude-logs/baton/2026-05-26_WORKFLOW-2_Tasks_執行.md`
- 套用 template_execution.md；記錄 Tasks 拆分成果

#### 執行報告二：本階段 C1 執行報告
- 檔名：`.claude-logs/baton/2026-05-27_WORKFLOW-2_C1_執行.md`
- 套用 template_execution.md；含真實 git status + §6.1 驗收腳本結果

### 🔄 同步更新 TODO.md 狀態

C1 完成後標記 ✅，C2 標記 🟡 WIP。

### 🛑 停止指令

產出兩份執行報告並更新 TODO.md 後立即停止。
嚴禁：繼續執行 C2 / 動業務代碼 / git commit / git push
```

---

## 執行結果摘要

- ✅ 完成：5 個提示詞模板重構（插入「第一步」強制歸檔區塊 + 末段備援標題更新）
- ✅ 完成：archive/ 備份 5 份 .bak 文件
- ✅ 完成：產出 `baton/2026-05-26_WORKFLOW-2_Tasks_執行.md`（Tasks 階段補發）
- ✅ 完成：產出 `baton/2026-05-27_WORKFLOW-2_C1_執行.md`（C1 執行報告）
- ✅ 完成：TODO.md C1 標記 ✅ / C2 標記 🟡 WIP
- 改動檔案：5 個模板 + 5 份 .bak + 2 份執行報告 + TODO.md
- 業務代碼：零改動
- commit / push：由 baron 手動執行
