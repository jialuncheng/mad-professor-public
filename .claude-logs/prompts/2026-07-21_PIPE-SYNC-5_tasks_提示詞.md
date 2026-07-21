# PIPE-SYNC-5 Tasks 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-SYNC-5（PIPE-INGEST＋GLOSSARY-TERMMAP 回灌母 plan v10→v11、PIPE-SPEC v8→v9、含 F7 門檻更正）
- **階段**：階段 2（tasks 拆分）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 08:15 |
| **任務代號** | PIPE-SYNC-5 Tasks |
| **觸發 Commit** | PIPE-SYNC-5-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：夾帶本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：`PIPE-SYNC-5`
- **工作流類別**：`DOC-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md`

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md         # 專案進度管控框架（已自動載入）
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md  # 本次拆分的依據 plan（v1）
.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md  # 回灌目標：SPEC v8（長駐）
.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md  # 回灌目標：母 plan v10（已版控）
.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 回灌目標：design spec（暫存）
.claude-logs/templates/template_tasks.md                       # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md                   # 執行報告模板
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）
- **嚴禁讀寫授權範圍外檔案**（授權範圍由 plan 工作目錄與不可動清單條款定義）
- **嚴禁改動業務與測試代碼**（本任務為 `DOC-Refactor`、業務代碼屬不可動清單、執行中僅修改指定之 3 份文件）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，Checkout 收官階段才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）

在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本任務的全量產出：

```markdown
## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | — |
| **修改檔案** | 3 個 | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（更至 v9） / `.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md` / `.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Checkout Commit代號> |
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + executions/ + tasks/ + git add |
```

### ⚙️ Commit 拆分與執行報告原則

1. **請不要在產出的 tasks.md 中給予具體的 commit 數量限制或指定具體拆分方式**。請由你作為執行者，依據 plan 的規格（D1-D6 SPEC 更正、U7-U8 母 plan 就地註解、F7 門檻值修訂等）及文件依賴關係，彈性規劃出最優的原子 Commit 清單。
2. **各開發階段必須產生報告**：對於每個開發 commit，必須依據 `template_execution.md` 產生執行報告，暫存於 `baton/` 目錄中。
3. **最後一個 Commit 必須為 Checkout（收官）**：
   - 命名為收官代號（如 `C_CHECKOUT` 或 `OP-CHECKOUT`）。
   - 此 Checkout 階段**才准執行 baton 搬移與歸檔**：將暫存於 `.claude-logs/baton/` 的 `_plan.md`、`_tasks.md` 與所有中間過程之 `_執行.md` 搬移（`mv`）至正式的 `plans/`、`tasks/` 與 `executions/` 目錄，並產生最終的 `checkout_執行.md` 報告後，統一執行 `git add` 歸檔。
   - 所有中間開發 commit 均**嚴禁**搬移或歸檔這些 baton 文件。
4. **可逆與最小干擾**：每個 Commit 應為獨立可測試的最小單元（本案雖然皆為文件修改，但仍應遵循獨立 commit 規範）。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit 必須包含以下六維度表格：

```markdown
### <Commit代號> — <Commit名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案，中間階段僅限變更的文件與其 .bak，暫存之執行報告不得列入> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep 條件** | <具體驗收指令，如：grep -n "..." <檔案> # 期望：有命中> |
| **依賴關係** | <前置 Commit 或「無前置」> |
| **具體實作細節** | <逐步說明每個檔案的具體改法，HTML 註解包裹標記，對齊 plan 與 design_spec 要求> |
```

### 📝 §1 TL;DR 中文括號命名要求

`## §1 TL;DR（概要）` 章節中，每個 Commit 引用必須含中文括號命名（例：`C1 — Spec & Plan Backfill（規格書與母計畫回灌）`）。

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目（狀態設為 `🟡 WIP`，子任務按 commit 拆分列點）：

```markdown
- 🟡 **PIPE-SYNC-5 PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC**（`.claude-logs/plans/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_plan.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：無
```

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md`（暫存於 baton/ 內）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：
- ❌ 繼續產出任何 `_執行.md`（執行階段需等後續執行提示詞）
- ❌ 改動任何業務或測試代碼（此階段只能進行 view / grep / 文件編輯，不修改代碼）
- ❌ 自發執行 `git commit` 或 `git push`
