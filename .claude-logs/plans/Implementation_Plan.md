# 專案進度管控框架實作計畫 · Mad Professor

> 本文件為 **Mad Professor 專案進度管控框架 (Project Progress Control Framework)** 的落地實作計畫。
> 格式與技術嚴謹度全面看齊 `design/docs/` 的 UI 設計系統規格。
> 旨在為專案建立鋼鐵般的進度管控、命名規範與 Regression 防線。

---

## 系統總覽與運作流向

專案進度管控框架的核心是 **Plan-Execution 雙軌保證制**。所有的開發均在獨立的 `worktree` 中進行，並在 `.claude-logs` 中留下完整的軌跡：

```
      【TODO.md】(狀態: ⬜ 未開始)
            │
            ▼
     1. 撰寫計畫 ──> 【YYYY-MM-DD_Phase_X_Commit_Y_plan.md】 (狀態: 🔵 plan 中)
            │
            ▼ (獲得人類核准)
     2. 隔離開發 ──> 【實作業務代碼與新增 pytest】 (狀態: 🟡 WIP)
            │
            ▼ (通過 100% 單元與手動 E2E 測試)
     3. 產出報告 ──> 【YYYY-MM-DD_Phase_X_Commit_Y-Z_執行.md】 (狀態: ✅ done)
            │
            ▼
      【TODO.md】(回填落地 Commit Hash)
```

---

## User Review Required

> [!IMPORTANT]
> 1. **全套規範與範本已預先產出**：為保證您可以第一時間體驗此框架，我們已依據 `design/docs` 的最高工程美學，直接在您的工作區中建立了 **`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`** 規範文件以及 **計畫、執行、熱修復** 三大範本檔。
> 2. **不可動清單與驗證防線**：我們將「不可動清單」與「端到端驗證」強制納入執行報告的標準範本中，這是一套能夠有效避免 Regression 的防呆防線。
> 3. **無縫繼承既有歷史**：命名、狀態（⬜/🔵/🟡/✅）與編碼（如 `RAG-1`）完全無縫繼承您在 `.claude-logs` 中的既有風格。

---

## Proposed Changes (交付檔案清單)

以下檔案已全部在 `.claude-logs` 目錄中產出，無任何外部依賴與破壞性改動：

### 專案管理組件 (Project Management Component)

#### [NEW] [PROJECT_PROGRESS_CONTROL_FRAMEWORK.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md)
* **角色**：框架總綱與硬規則。
* **內容摘要**：
  - TODO 與已完成清單的寫入與回填規則。
  - `[Module]-[N]`（如 `RAG-1`、`CHAT-3b`）的 New / Modify / Bugfix 編碼機制。
  - 計畫檔 (`_plan.md`)、執行檔 (`_執行.md`) 與熱修復檔 (`_hotfix.md`) 的結構契約。
  - SPEC 技術規格書與指南手冊（如新增 `doc_type` 手冊）的必備結構與版本維護規範。
  - 不可動清單與防 Regression 黃金三角。

#### [NEW] [template_plan.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/templates/template_plan.md)
* **角色**：新功能或修改計畫檔範本。
* **內容摘要**：含 TL;DR、現況盤點、問題與證據、設計方案、變動風險評估、驗證計畫、不可動清單與開放問題 (Open Questions)。

#### [NEW] [template_execution.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/templates/template_execution.md)
* **角色**：修改執行報告檔範本。
* **內容摘要**：含落地 Commit 表格、diff stat、修改真因、檔案修法、不可動清單遵守狀態打勾、pytest 與手動 E2E 驗證結果、Rollback 回退指引。

#### [NEW] [template_hotfix.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/.claude-logs/templates/template_hotfix.md)
* **角色**：緊急熱修復紀錄檔範本。
* **內容摘要**：含阻斷現象描述、第一手 Traceback 堆疊、真因診斷、最小侵入式修法 (Minimal diff)、單元測試驗證與安全備案還原。

---

## Verification Plan (驗證計畫)

為驗證本框架的工程品質，我們執行了以下三層驗證：

### 1. 靜態語意與 Markdown 檢查
- **驗證方式**：確保所有新建文件皆符合 GitHub Markdown 標準，無損毀連結，且結構清晰。
- **預期結果**：檔案完美生成，文字流暢，排版大氣。

### 2. 目錄結構稽核
- **驗證方式**：檢查檔案是否完美落入指定的 `.claude-logs` 與 `.claude-logs/templates` 目錄。
- **預期結果**：
  ```
  .claude-logs/
  ├── PROJECT_PROGRESS_CONTROL_FRAMEWORK.md  (已落地)
  └── templates/
      ├── template_plan.md                   (已落地)
      ├── template_execution.md              (已落地)
      └── template_hotfix.md                 (已落地)
  ```

### 3. 人類負責人審閱（Manual Verification）
- **驗證方式**：請您直接點擊上述連結或開啟對應檔案，確認格式、邏輯深度與排版是否完美符合您的預期。
