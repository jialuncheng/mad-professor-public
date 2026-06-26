# Baton 機制說明手冊

> 本文件為跨 AI 工具單向交接暫存區（baton/）的權威說明書。

---

## §0 改版規則

- 改版觸發：Baton 流程變動或版控排除規則調整
- 完整治理規格 → §99

---

## §1 Baton 機制核心原理

Baton（接力棒）是為了解決多個 AI 工具（如 Antigravity、Claude Code、Claude Design）協作時跨 Session 資訊傳遞、Context 污染以及 Git 工作區污染而設計的暫存交接機制。

### §1.1 暫存區隔離原理

- **平時為空**：在沒有進行跨工具任務時，`baton/` 目錄內僅保留本 `README.md`。
- **排除版控**：透過根目錄的 `.gitignore` 設定 `baton/*` 排除，除本 `README.md` 外，所有位於 `baton/` 內的文件在傳輸期均**不入 Git 版本控制**，防範未成熟的 plan 或任務拆分污染 Git 歷史。

---

## §2 交接與歸檔流程（ClawVM 3-Phase Writeback 形式化）

> 本流程依 ClawVM 論文「validated writeback」精神，將 baton 歸檔形式化為**三相交易（3-Phase Transaction）**：Staging → Deterministic Validation → Scoped Commit。
> **核心鐵律——非破壞性寫入（Non-destructive）**：歸檔嚴禁覆寫 / 截斷正式目錄既有內容；衝突時改用 append / merge / 新版本命名。此為 WORKFLOW-5 唯一**不可繞過**的保證（驗證在 `mv` 前確定性執行）。

### Phase 1 — Staging（暫存區寫入）
發起方產出文件後，一律命名並暫存於：
`baton/<YYYY-MM-DD>_<任務編碼>_<描述>_<計畫/任務>.md`

- **時機鐵律（對帳 WORKFLOW_SOP §3）**：Run 階段產物一律留 `baton/`、**嚴禁 mv 或 git add**；歸檔僅於 Checkout 階段執行。
- baron 啟動接收方 Session 時，於提示詞明確指引讀取指定的 `baton/` 暫存檔（人類交接環節）。

### Phase 2 — Deterministic Validation（歸檔前確定性自檢）
在 Phase 3 的 `mv` 之前，接收方**必須**對每份待歸檔暫存檔逐項自檢；**任一項不通過即暫停歸檔、回報 baron**（不靠提示詞自報，靠執行期 SOP 查核）：

| 檢查維度 | 通過條件 |
|---|---|
| **Provenance（溯源）** | 檔名含任務代號 + 內容頂部元數據塊齊備，可回溯來源 commit / session |
| **Schema（結構）** | 套用對應 template（plan / tasks / execution）之必備章節齊備（§0 / §99 等） |
| **Non-destructive（非破壞性）** | 正式目錄目標路徑**無同名既有檔**，或已確認採 append / 新版本命名；**嚴禁覆寫 / 截斷既有檔** |
| **Scope（範疇）** | 歸檔目標目錄正確（plans/ ／ tasks/ ／ executions/ ／ hotfixes/ …，依 WORKFLOW_SOP §2） |

### Phase 3 — Scoped Commit（驗證通過後一次性歸檔）
- **時機鐵律（對帳 WORKFLOW_SOP §3）**：**僅 Checkout 階段**一次性 `mv` + `git add`，還原 `baton/` 為空。
- **安全移動指令**：因檔案被 gitignore 排除，**絕對禁止** `git mv`（會引發 `fatal: bad source`）。必須用標準 `mv` 移位後 `git add` 納入版控：
  ```bash
  # 範例（驗證通過後）
  mv .claude-logs/baton/<暫存檔案>.md .claude-logs/plans/<歸檔名稱>.md
  git add .claude-logs/plans/<歸檔名稱>.md
  ```
- **追溯性鏈結（Traceability / Audit Trail）**：接收方必須在歸檔任務 `_執行.md` 的 `§7 銜接` 章節，**寫明被消化歸檔之 baton 檔名與對應 Git commit hash 映射**。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 規範跨 AI 工具單向文件交接暫存機制，隔離 Git 版控污染，並透過安全歸檔建立 Audit Trail |
| **用途** | 當跨 AI 工具傳導 plan/tasks 時，開發者與 AI 必須查閱此機制規格以進行歸檔 |
| **權威源** | 本檔 §1–§2 |
| **引用方** | CLAUDE.md §3（工作目錄硬規則）/ 階段 6 收官提示詞 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁在歸檔時使用 `git mv` 命令；必須在 `_執行.md` 中寫明消化暫存檔與 Hash 映射 |
| **改版觸發條件** | baton 檔案流向變更 / 版控過濾規則調整 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留作為協作交接基準，不予刪除 |
| **重複防護** | 本檔為 baton 唯一的權威源，CLAUDE.md 僅作 §3 工作目錄規則下的概要引用 |

### §99.2 Revision 歷程

- v2 (2026-06-26)：WORKFLOW-5 C2——§2 形式化為 ClawVM 3-Phase Writeback（Staging → Deterministic Validation → Scoped Commit）；新增 Phase 2 確定性自檢四維度（Provenance / Schema / Non-destructive / Scope）+ 非破壞性寫入核心鐵律；對帳 WORKFLOW_SOP §3「Run 嚴禁 mv、Checkout 才歸檔」一次性 mv 鐵律；保留 git mv 禁令與 Audit Trail
- v1 (2026-05-26)：初版發布，對齊計畫書 r11/v11 關於 `mv + git add` 安全移動指令規範
