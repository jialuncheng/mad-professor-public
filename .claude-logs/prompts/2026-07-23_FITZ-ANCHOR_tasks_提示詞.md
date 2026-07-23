# 2026-07-23 — FITZ-ANCHOR Tasks 提示詞

> **收到時間**：2026-07-23 11:04（UTC+8）
> **任務代號**：FITZ-ANCHOR Tasks
> **觸發 commit**：FITZ-ANCHOR-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`
> **觸發情境**：baron 同意 FITZ-ANCHOR plan v2 規格（六 OQ 全拍板），下達階段 2 任務拆分指令。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-23 11:04 |
| **任務代號** | FITZ-ANCHOR Tasks |
| **觸發 Commit** | FITZ-ANCHOR-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：`FITZ-ANCHOR`
- **工作流類別**：`BE-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md         # 專案進度管控框架（已自動載入）
.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md  # 本次拆分的依據 plan（v1）
.claude-logs/plans/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md  # 規劃前置 plan
.claude-logs/tasks/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md  # 前置 hotfix
.claude-logs/tasks/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md  # 前置 hotfix
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
.claude-logs/templates/template_tasks.md                       # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md                   # 執行報告模板
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）
- **嚴禁讀寫授權範圍外檔案**（授權範圍由 plan 工作目錄與不可動清單條款定義）
- **嚴禁改動業務代碼**（此階段僅能閱讀與分析，不寫入代碼）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，Checkout 收官階段才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）

在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本任務的全量產出：

```markdown
## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | — |
| **修改檔案** | 5 個 | `processor/fitz_processor.py`（U3 寫端移除、U4 容差去重、U5 比例重複門檻） / `pipelines/litedoc_pipeline.py`（U1 錨定前移、U2 標題回注、U3 hints 讀端與參數清理） / `pipelines/section_engine.py`（U6 相似度守衛） / `tests/test_fitz_processor.py`（U4/U5/U3 移除測試） / `tests/test_litedoc_pipeline.py`（U1/U2/U3 移除/U6 測試） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Checkout Commit代號> |
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + executions/ + tasks/ + git add |
```

### ⚙️ Commit 拆分與執行報告原則

1. **請不要在產出的 tasks.md 中給予具體的 commit 數量限制或指定具體拆分方式**。請由你作為執行者，依據 plan 的規格及代碼依賴關係，彈性規劃出最優的原子 Commit 清單。
2. **各開發階段必須產生報告**：對於每個開發 commit，必須依據 `template_execution.md` 產生執行報告，暫存於 `baton/` 目錄中。
3. **最後一個 Commit 必須為 Checkout（收官）**：
   - 命名為收官代號（如 `C_CHECKOUT` 或 `OP-CHECKOUT`）。
   - 此 Checkout 階段**才准執行 baton 搬移與歸檔**：將暫存於 `.claude-logs/baton/` 的 `_plan.md`、`_tasks.md` 與所有中間過程之 `_執行.md` 搬移（`mv`）至正式的 `plans/`、`tasks/` 與 `executions/` 目錄，並產生最終 the `checkout_執行.md` 報告後，統一執行 `git add` 歸檔。
   - 所有中間開發 commit 均**嚴禁**搬移 or 歸檔 these baton 文件。
4. **可逆與最小干擾**：每個 Commit 應為獨立可測試 the 最小單元。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit 必須包含以下六維度表格：

```markdown
### <Commit代號> — <Commit名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案，中間階段僅限變更的業務代碼、測試代碼與其 .bak，暫存之執行報告不得列入> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep 條件** | <具體驗收指令，如：grep -n "..." <檔案> # 期望：有命中> |
| **依賴關係** | <前置 Commit 或「無前置」> |
| **具體實作細節** | <逐步說明每個檔案 the 具體改法，含關鍵代碼邏輯，對齊 plan 與 design_spec 要求> |
```

### 📝 §1 TL;DR 中文括號命名要求

`## §1 TL;DR（概要）` 章節中，每個 Commit 引用必須含中文括號命名（例：`C1 — Fitz Geometry Refinement（Fitz 幾何整形與容差去重）`）。

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目（狀態設為 `🟡 WIP`，子任務按 commit 拆分列點）：

```markdown
- 🟡 **FITZ-ANCHOR LLM 錨定前移與 fitz 幾何整形**（`.claude-logs/plans/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：無
```

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`（暫存於 baton/ 內）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：
- ❌ 繼續產出任何 `_執行.md`（執行階段需等後續執行提示詞）
- ❌ 改動任何業務代碼（此階段只能進行 view / grep / 文件編輯，不修改代碼）
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ tasks.md 已產出：`baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`（C1 幾何整形 / C2 錨定前移+回注+sidecar 退場 / C_CHECKOUT）
- TODO.md 已同步新增 🟡 WIP 條目
- 業務代碼零改動、無 commit（依階段 2 鐵律）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
