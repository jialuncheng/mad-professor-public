# 2026-07-18 — SOP-COMPLY Check 提示詞

> **收到時間**：2026-07-18 07:17（UTC+8）
> **任務代號**：SOP-COMPLY Check
> **觸發 commit**：SOP-COMPLY checkout（收官歸檔）
> **相關產出檔案**：`.claude-logs/executions/2026-07-18_SOP-COMPLY_checkout_執行.md`
> **觸發情境**：C1–C3 全數 ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令——五維度驗收全綠後執行 TODO 雙層結案 + hash 自癒 + baton 一次性 mv 歸檔 + 6 提示詞入版控 + staged 白名單自檢 + 直產 checkout 執行報告。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-18 07:17 |
| **任務代號** | SOP-COMPLY Check |
| **觸發 Commit** | SOP-COMPLY-Check |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_SOP-COMPLY_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_SOP-COMPLY_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 Checkout 動作。

### 📋 任務資訊

- **任務編碼**：`SOP-COMPLY`
- **Plan 路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md
  .claude-logs/baton/2026-07-18_SOP-COMPLY_C2_執行.md
  .claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/TODO.md                                           # 任務狀態（已自動載入）
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md  # 原始規格
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md  # Commit 拆分與驗收條件
.claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md            # C1 執行報告
.claude-logs/baton/2026-07-18_SOP-COMPLY_C2_執行.md            # C2 執行報告
.claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md            # C3 執行報告
```

---

### ✅ Conformance 驗收流程

**第一步：產出 Conformance 驗收報告**
依據目標規格（C1-C3 落地情況）、測試計畫驗收條件、不可動清單與提示詞歸檔狀態，交叉核對並在回覆中產出 Conformance 驗收報告表格（依 `template_prompt_for_check.md` 第二步格式）。

**提示詞歸檔稽核要求**：
- 執行 `ls .claude-logs/prompts/ | grep "SOP-COMPLY"` 確認本任務相關的所有提示詞檔案（plan、tasks、C1-C3 run、Check 提示詞共 6 份）是否都已確實建立於物理目錄中。

---

### 🗃️ 收官自動化動作（全部合規後才執行）

**第一步：更新 TODO.md 與雙源 Hash 自癒補填**
1. 在 `archive/TODO_done_archive.md` 的程式碼品質/SOP合規分類下**追加**本任務的完成表格。
2. 執行 `git log -n 10` 讀取先前 C1-C3 已經由 baron 手動提交落地的真實 Commit Hash。
3. 自動將 `TODO.md` 的 `## ✅ 已完成（索引）` 索引行（pointer 格式）與 `archive/TODO_done_archive.md` 中表格的 `待 baron 回填` 佔位符，**全部替換為真實的 Git Commit Hash**。
4. 從 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始` 中**移除**本任務條目，並更新底部類別索引。

**第二步：搬移並歸檔 baton/ 暫存文件**
執行以下搬移指令，將暫存於 `baton/` 的文件歸檔至正式目錄，並寫入 git add 清單中：

```bash
# 搬移 Plan
mv .claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md .claude-logs/plans/

# 搬移 Tasks
mv .claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md .claude-logs/tasks/

# 搬移 C1-C3 執行報告
mv .claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md .claude-logs/executions/
mv .claude-logs/baton/2026-07-18_SOP-COMPLY_C2_執行.md .claude-logs/executions/
mv .claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md .claude-logs/executions/
```

**第三步：確認 baton/ 只剩 README.md**
執行 `ls .claude-logs/baton/` 確保該目錄已被淨空，僅剩 `README.md`。

**第四步：檢查並將 prompts/ 下本任務提示詞全部納入 git add**
檢查並確保 `.claude-logs/prompts/INDEX.md` 與本任務相關的 6 個提示詞歸檔檔案已被確實 `git add` 納入版控中。

**第五步：staged 自檢與 checkout 報告產出**
1. 產出並將 `executions/2026-07-18_SOP-COMPLY_checkout_執行.md` 寫入（套用 `template_execution.md` 輕量格式，註明 Conformance 驗收通過、§7.2 純後端無 handoff 顯式豁免）。
2. 在 commit 前執行 `git diff --cached --name-only` 自檢暫存集合，確保**僅包含**本任務宣告歸檔的檔案（plan + tasks + 4份執行報告 + prompts/INDEX.md + 6個 prompts 歸檔檔 + TODO.md + archive/TODO_done_archive.md），**嚴禁**混入其他任務或跨任務未追蹤檔案。

**第六步：產生 `/tmp/SOP-COMPLY_checkout_msg.txt`**
將 checkout 階段的 commit message 寫入 `/tmp/SOP-COMPLY_checkout_msg.txt`，並展示於報告 §8.2 中。

---

### 📝 §8 baron 執行命令格式要求

請在 `checkout_執行.md` 的 `## §8 baron 執行命令` 中列出以下指令：

```bash
# 1. 搬移暫存檔已完成（報告 §3 已列出）

# 2. git add 歸檔清單（⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A`）
git add .claude-logs/plans/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md
git add .claude-logs/tasks/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md
git add .claude-logs/executions/2026-07-18_SOP-COMPLY_C1_執行.md
git add .claude-logs/executions/2026-07-18_SOP-COMPLY_C2_執行.md
git add .claude-logs/executions/2026-07-18_SOP-COMPLY_C3_執行.md
git add .claude-logs/executions/2026-07-18_SOP-COMPLY_checkout_執行.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_plan_提示詞.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_tasks_提示詞.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_C1_run_提示詞.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_C2_run_提示詞.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_C3_run_提示詞.md
git add .claude-logs/prompts/2026-07-18_SOP-COMPLY_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add TODO.md
git add archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/SOP-COMPLY_checkout_msg.txt）
cat > /tmp/SOP-COMPLY_checkout_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY checkout — 成果收官歸檔（成果歸檔與移出暫存）

1. Conformance 總驗收通過，完成日誌品質合規清帳（25 處補 exc_info，吞例外修正）與資料庫 begin 事務改造（自持/借用共 13 處）。
2. 將暫存於 baton/ 的 plan、tasks、C1-C3 執行報告搬移歸檔至正式目錄。
3. 歸檔與納入版控 6 個階段的 prompts 提示詞及 INDEX.md 索引。
4. TODO.md 進行雙層結案更新（移至已完成索引，archive 追加完成明細表，完成歷史 hash 自動補填）。
EOF

# 4. baron 手動執行
git commit -F /tmp/SOP-COMPLY_checkout_msg.txt
```

---

### 🛑 停止指令

**產出 `checkout_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`（必須等待 baron 核對暫存集無誤後手動 commit）
- ❌ 修改任何已歸檔的正式歷史文件
````

---

## 執行結果摘要

- （執行完成後回填）

## 後續引用

- 無
