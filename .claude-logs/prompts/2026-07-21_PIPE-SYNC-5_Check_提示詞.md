# PIPE-SYNC-5 Check（Checkout 收官）階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-SYNC-5（PIPE-INGEST＋GLOSSARY-TERMMAP 回灌母 plan/PIPE-SPEC + F7 門檻更正）
- **階段**：階段 5/6（Conformance 驗收 + Checkout 收官歸檔）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 11:00 |
| **任務代號** | PIPE-SYNC-5 Check |
| **觸發 Commit** | PIPE-SYNC-5-Check |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行 any 讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 Checkout 動作。

### 📋 任務資訊

- **任務編碼**：`PIPE-SYNC-5`
- **Plan 路徑**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-07-21_PIPE-SYNC-5_C1_執行.md
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/TODO.md                                           # 任務狀態（已自動載入）
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md  # 原始規格
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md  # Commit 拆分與驗收條件
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_C1_執行.md            # C1 執行報告
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

---

### ✅ Conformance 驗收流程

**第一步：產出 Conformance 驗收報告**
依據目標規格（包含 `ingestion_engine` §1.2.6 契約與 Roster 補登、`build_termmap` 事前定案算法與術語 align 預設開關補登、母 plan 表 ✅ 及文字改版對齊、以及 `design_spec` F7 面積門檻 100k 修正）、測試計畫驗收條件、不可動清單與提示詞歸檔狀態，交叉核對並在回覆中產出 Conformance 驗收報告表格（依 `template_prompt_for_check.md` 第二步格式）。

**提示詞歸檔稽核要求**：
- 執行 `ls .claude-logs/prompts/ | grep "PIPE-SYNC-5"` 確認本任務相關的所有提示詞檔案（tasks、C1 run、Check 提示詞共 3 份）是否都已確實建立於物理目錄中。

---

### 🗃️ 收官自動化動作（全部合規後才執行）

**第一步：Tasks.md 的 §8 更正為「C1 合併版」**
1. **在搬移 `tasks.md` 之前，你必須先對該暫存檔進行修改**：編輯 `.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md`，確認其 `## §8 推薦 Commit 拆分` 章節，已正確且完整地將所有回灌與修改工作（SPEC、母 Plan、Design Spec）收攏至 `C1 — Spec & Plan Backfill（規格書與母計畫回灌）` 的實作細節中，並確認沒有其他無效的分離 commit，以防日後對照困惑。

**第二步：更新 TODO.md 與雙源 Hash 自癒補填**
1. 在 `archive/TODO_done_archive.md` 的策略管線/回灌與文件治理分類下**追加**本任務的完成表格。
2. 執行 `git log -n 5` 讀取先前 C1 已經由 baron 手動提交落地的真實 Commit Hash。
3. 自動將 `TODO.md` 的 `## ✅ 已完成（索引）` 索引行（pointer 格式）與 `archive/TODO_done_archive.md` 中表格的 `待 baron 回填` 佔位符，**全部替換為真實的 Git Commit Hash**。
4. 從 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始` 中**移除**本任務條目，並更新底部類別索引。

**第三步：搬移並歸檔 baton/ 暫存文件**
執行以下搬移指令，將暫存於 `baton/` 的文件歸檔至正式目錄，並寫入 git add 清單中：

```bash
# 搬移 Plan
mv .claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md .claude-logs/plans/

# 搬移更正後的 Tasks
mv .claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md .claude-logs/tasks/

# 搬移 C1 執行報告
mv .claude-logs/baton/2026-07-21_PIPE-SYNC-5_C1_執行.md .claude-logs/executions/
```

**第四步：確認 baton/ 內本案任務檔案已被清除**
執行 `ls .claude-logs/baton/` 確保除影子 PDF 外，無本案殘留文件。

**第五步：檢查並將 prompts/ 下本任務提示詞全部納入 git add**
檢查並確保 `.claude-logs/prompts/INDEX.md` 與本任務相關的 3 個提示詞歸檔檔案已被確實 `git add` 納入版控中。

**第六步：staged 自檢與 checkout 報告產出**
1. 產出並將 `executions/2026-07-21_PIPE-SYNC-5_checkout_執行.md` 寫入（套用 `template_execution.md` 輕量格式，註明 Conformance 驗收通過、§7.2 純文件無代碼與測試 handoff 豁免）。
2. 在 commit 前執行 `git diff --cached --name-only` 自檢暫存集合，確保**僅包含**本任務宣告歸檔的檔案（既有修改文件、各 commit 備份的 3 個 `.bak`、plan + tasks + 2 份執行報告 + prompts/INDEX.md + 3 個 prompts 歸檔檔 + TODO.md + archive/TODO_done_archive.md），並剔除無關檔案。

**第七步：產生 `/tmp/PIPE-SYNC-5_checkout_msg.txt`**
將 checkout 階段 the commit message 寫入 `/tmp/PIPE-SYNC-5_checkout_msg.txt`，並展示於報告 §8.2 中。

---

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 搬移暫存檔與 Tasks 修正已完成（報告 §3 已列出）

# 2. git add 歸檔清單（⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A`）
git add .claude-logs/plans/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md
git add .claude-logs/tasks/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md
git add .claude-logs/executions/2026-07-21_PIPE-SYNC-5_C1_執行.md
git add .claude-logs/executions/2026-07-21_PIPE-SYNC-5_checkout_執行.md
git add .claude-logs/prompts/2026-07-21_PIPE-SYNC-5_tasks_提示詞.md
git add .claude-logs/prompts/2026-07-21_PIPE-SYNC-5_C1_run_提示詞.md
git add .claude-logs/prompts/2026-07-21_PIPE-SYNC-5_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_specification.md.bak
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_plan_v10.md.bak
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_design_spec.md.bak
git add TODO.md
git add archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SYNC-5_checkout_msg.txt）
cat > /tmp/PIPE-SYNC-5_checkout_msg.txt << 'EOF'
DOC-Refactor: PIPE-SYNC-5 checkout — 成果收官歸檔（成果歸檔與移出暫存）

1. Conformance 總驗收通過，完成 PIPE-INGEST 與 GLOSSARY-TERMMAP 落地規格回灌，修復母 plan v10、PIPE-SPEC v8 檔之歷史 doc-drift。
2. 同步修正 design_spec F7 門檻為實測校正後之面積比對（area < 100000）以防後續誤導。
3. 修正 tasks.md §8 為「C1 合併版」，並將暫存於 baton/ 的 plan、tasks、C1 執行報告搬移歸檔至正式目錄。
4. 歸檔與納入版控 3 個階段的 prompts 提示詞、INDEX.md 及 3 份文件 .bak 備份。
5. TODO.md 進行雙層結案更新（移至已完成索引，archive 追加完成明細表，完成歷史 hash 自動補填）。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SYNC-5_checkout_msg.txt
```

---

### 🛑 停止指令

**產出 `checkout_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`（必須等待 baron 核對暫存集無誤後手動 commit）
- ❌ 修改任何已歸檔的正式歷史文件
