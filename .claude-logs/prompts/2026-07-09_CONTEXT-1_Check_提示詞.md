# 2026-07-09 CONTEXT-1 Check 提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：Check / C5 Checkout（階段 5-6 Conformance 驗收與收官歸檔）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-09

---

## 原始提示詞（逐字）

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 01:27 |
| **任務代號** | CONTEXT-1 Check |
| **觸發 Commit** | CONTEXT-1-Check |
| **相關產出檔案** | 所有執行報告與本案暫存文件（見下方清單） |
| **觸發情境** | C1-C4 全部執行完畢，baron 下達 Conformance 驗收與 C5 checkout 收官歸檔指令。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-09_CONTEXT-1_Check_提示詞.md`
   格式依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-09_CONTEXT-1_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作。

### 📋 任務資訊

- **任務編碼**：CONTEXT-1
- **Plan 路徑**：.claude-logs/plans/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md
- **Tasks 路徑**：.claude-logs/tasks/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md
  .claude-logs/baton/2026-07-08_CONTEXT-1_C2_執行.md
  .claude-logs/baton/2026-07-08_CONTEXT-1_C3_執行.md
  .claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：

```

CLAUDE.md                                                                           # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                    # 工作流規範（已自動載入）
.claude-logs/TODO.md                                                                # 任務狀態（已自動載入）
.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md   # 原始規格（驗收基準）
.claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md   # Commit 拆分與驗收條件
.claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md                                  # C1 執行結果
.claude-logs/baton/2026-07-08_CONTEXT-1_C2_執行.md                                  # C2 執行結果
.claude-logs/baton/2026-07-08_CONTEXT-1_C3_執行.md                                  # C3 執行結果
.claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md                                  # C4 執行結果

```

---

### ✅ Conformance 驗收流程

**第一步：讀檔並交叉比對**
核對 目標規格（plan §2）、驗收條件（tasks §6）、不可動清單（tasks §7）、以及以下特化維度：
1. **提示詞歸檔稽核**：檢查 `.claude-logs/prompts/` 下本案產出的所有提示詞歸檔（plan, tasks, C1-C4 runs, check）是否皆已實體存在且已用 `git add` 納入 git，若發現為 untracked 請在收官階段手動 add。
2. **msg.txt 草稿完整性**：確認各執行報告 §8 有完整 commit message 草稿展示（含 `cat > /tmp/...`）。
3. **跨 Commit 累加分析**：檢查全部 Commit 疊加是否 100% 覆蓋了 `plan §2` 中的 U1-U7 改動，且無業務程式碼改動（DOC-Refactor）。

**第二步：產出 Conformance 驗收報告**
套用模板結構，在回覆中完整展示驗收表格。若全部合規，在此繼續執行下方收官動作；若不合規，立即中斷並報告。

---

### 🗃️ 收官自動化動作（全部合規後才執行）

**第一步：更新 TODO.md（雙層寫入）**
1. 在 `archive/TODO_done_archive.md` 追加本任務的完成表格。
2. 在 `TODO.md` 的 `## ✅ 已完成（索引）` 區新增一行 pointer 索引，格式依 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 雙層表述新規定。
3. 從 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始` 區塊移除本任務條目，並同步將底部類別索引設為 ✅。

> ℹ️ **歷史全量 Hash 審計與自愈補填（雙源）**：完成上述雙層寫入的當下，你必須強制執行 `git log`，對 **`TODO.md` 索引行 + `archive/TODO_done_archive.md`** 進行全量審計，將先前 C1-C4 已提交的真實 Git Commit Hash 對位回填，替換掉所有 `待 baron 回填` 佔位符。

**第二步：歸檔 baton/ 暫存文件**
將 `baton/` 下所有本任務的暫存文件移至正式目錄，並逐一執行顯式 `git add`（嚴禁 `git add .`）：

```bash
# 搬移 plan
mv .claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md \
   .claude-logs/plans/
git add .claude-logs/plans/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md

# 搬移 tasks
mv .claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md \
   .claude-logs/tasks/
git add .claude-logs/tasks/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md

# 搬移 C1-C4 執行報告
mv .claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md .claude-logs/executions/
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C1_執行.md
mv .claude-logs/baton/2026-07-08_CONTEXT-1_C2_執行.md .claude-logs/executions/
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C2_執行.md
mv .claude-logs/baton/2026-07-08_CONTEXT-1_C3_執行.md .claude-logs/executions/
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C3_執行.md
mv .claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md .claude-logs/executions/
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C4_執行.md
```

**第三步：確認 baton/ 狀態**
執行 `ls .claude-logs/baton/`，確認本任務相關暫存檔已全數清空移出。
*(註：原本已在 `baton/` 的 long-term 檔案如 `context_engineering_governance_audit.md` 規格源、README.md、PDF、PIPE-SPEC 等依規定維持長駐不碰。)*

**第四步：檢查相關提示詞歸檔是否已入 git**
列出並確認本案產出的 prompts 目錄下所有提示詞歸檔（包含本 check 提示詞）及 `prompts/INDEX.md` 都已執行 `git add` 納入 git 追蹤範圍。若有漏掉，請對應執行 `git add < prompts 提示詞路徑 >`。

**第五步：commit 前 staged 自檢（白名單自檢）**
執行 `git diff --cached --name-only`，與本任務 C1-C5 宣告改動檔及 `.bak` 備份檔之聯集進行逐項對比，確保多一檔/少一檔即停。

**第六步：產出並保存 checkout 執行報告**
在 `executions/` 下直接新建產出 `executions/2026-07-08_CONTEXT-1_checkout_執行.md`（套用 `template_execution.md` 模板），報告必須記錄 Conformance 結果、**第五步 staged 自檢輸出**、baton 歸檔確認。此報告本身也必須於本 Commit 中 `git add`。

---

### 📝 §8 baron 執行命令格式要求

在 `executions/2026-07-08_CONTEXT-1_checkout_執行.md` 的 `## §8 baron 執行命令` 中，必須提供以下內容，將 msg 寫入 `/tmp/CONTEXT-1_C5_msg.txt`，並將本 checkout 執行報告也一併 `git add`：

```bash
# 1. 歸檔與狀態自檢已完成（報告 §3 中已列出）

# 2. git add 清單（收官歸檔所有檔案，逐檔顯式列名，嚴禁 git add .）
git add .claude-logs/TODO.md
git add .claude-logs/archive/TODO_done_archive.md
git add .claude-logs/plans/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md
git add .claude-logs/tasks/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C1_執行.md
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C2_執行.md
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C3_執行.md
git add .claude-logs/executions/2026-07-08_CONTEXT-1_C4_執行.md
git add .claude-logs/executions/2026-07-08_CONTEXT-1_checkout_執行.md
git add .claude-logs/prompts/2026-07-07_CONTEXT-1_plan_提示詞.md
git add .claude-logs/prompts/2026-07-08_CONTEXT-1_Tasks_提示詞.md
git add .claude-logs/prompts/2026-07-08_CONTEXT-1_C1_run_提示詞.md
git add .claude-logs/prompts/2026-07-09_CONTEXT-1_C2_run_提示詞.md
git add .claude-logs/prompts/2026-07-09_CONTEXT-1_C3_run_提示詞.md
git add .claude-logs/prompts/2026-07-09_CONTEXT-1_C4_run_提示詞.md
git add .claude-logs/prompts/2026-07-09_CONTEXT-1_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/CONTEXT-1_C5_msg.txt）
cat > /tmp/CONTEXT-1_C5_msg.txt << 'EOF'
DOC-Refactor: CONTEXT-1 C5 — Checkout（收官歸檔）

1. 執行 Conformance 五維度檢驗，確認目標規格、測試條件、不可動清單皆完全合規。
2. 搬移暫存於 baton/ 下的 plan, tasks 及各執行報告至正式治理目錄。
3. 檢查並歸檔本案相關的所有 Prompts 提示詞檔案。
4. 完成 TODO.md 自「進行中」移除之結案更新，並對 TODO.md 索引行及歸檔檔進行 Hash 補填自癒。
5. 產出並保存 checkout 收官執行報告。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/CONTEXT-1_C5_msg.txt
```

---

### 🛑 停止指令

**完成 TODO.md 更新與 baton/ 歸檔並產出 checkout 執行報告後，必須立即停止所有工具呼叫。**

嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`（baron 手動回填本 C5 hash 後由 baron 執行最終 commit）
- ❌ 修改已歸檔到 executions/ 的任何執行報告
- ❌ 修改 plans/ 或 tasks/ 下已歸檔的文件
````

---

## 上下文（承接對話）

1. C1（`1219a87`）/ C2（`44f6d00`）/ C3（`3c19213`）已 ship、C4 已執行完畢（baron 確認），下達本 Check / C5 Checkout。
2. 本提示詞：Conformance 驗收（plan §2 U1–U7 覆蓋 / tasks §6 / 不可動 §7 / 提示詞歸檔稽核 / msg 完整性）→ 全綠後收官——TODO 雙層結案（**dogfood C3 新流程**：完整表格追加 TODO_done_archive.md + TODO 索引行 + 移除 active + 類別索引）+ hash 雙源自癒 + baton 一次性 mv/git add 歸檔 + staged 自檢 + checkout 執行報告直落 executions/；產完即停。

## 產出

- Conformance 驗收報告（回覆內展示）
- TODO.md 結案（雙層）+ `archive/TODO_done_archive.md` 追加 CONTEXT-1 表格
- baton → plans/tasks/executions 歸檔 + 逐檔 git add + staged 自檢
- `executions/2026-07-08_CONTEXT-1_checkout_執行.md`
