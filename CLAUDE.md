# Claude Code 啟動指引

> session 入口：核心規範與契約 / 工作流類別判定 / 工作目錄硬規則

---

## §0 session 啟動必讀（@path 自動載入）

@.claude-logs/ref/WORKFLOW_SOP.md
@.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
@.claude-logs/TODO.md
@.claude-logs/baton/*.md

- 改版觸發：§1–§5 任一規範變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 核心規範與契約

### §1.1 plan-execution 雙軌制
- **plan 階段**：嚴禁動業務代碼、只 view / grep / 文件編輯
- **execution 階段**：依 plan 落地、最小可逆 commit、附 pytest + E2E 驗證

### §1.2 提示詞歸檔（細節見 `prompts/README.md`）
- 觸發：命令動詞（請執行 / 撰寫 / 修正）/ 長度 > 500 字 / 結構化區塊（═══ 或 ## 第X步）
- 流程：先歸檔到 `.claude-logs/prompts/` → 再執行 → 同步 `INDEX.md`
- 敏感資訊（API key / 密碼 / email）打碼後再寫入；模糊時優先歸檔

### §1.3 不 commit / push
- auto-classifier 阻擋 Claude Code 直接 commit / push
- 所有 commit / push 由 baron 手動執行
- Claude Code 只負責：備好改動 + 寫 commit message 草稿（`/tmp/msg.txt`）+ 列出 `git add` 清單

### §1.4 TODO 維護
- 拆 tasks 時同步更新：於 TODO.md 新增任務條目、設 🟡 WIP（per WORKFLOW_SOP §3 階段 2）
- ship 後**立即同步**：🟡 WIP → ✅ 完成（多 commit 任務待全部 ship）
- 不累積技術債、不追溯刪除

### §1.5 plan 必產出 Open Questions 表
- 凡 plan 文件 §Open Questions 章節必含「問題 + 推薦答案 + 理由」三欄
- baron 過目 / 修改後才進 execution

### §1.6 不確定先問
- 設計決策模糊時、停下來問 baron、不擅自下結論
- 邊界情況（schema 變動 / 新依賴 / 跨任務影響）強制詢問

### §1.7 提案用 grep 證據
- 任何「既有 codebase 是 X」「既有 endpoint 是 Y」必附 grep 命令 + 真實行號
- 不靠記憶 / 不憑感覺

### §1.8 警戒行銷話術
- 「30-50x 提速」「100% 正確率」「無痛升級」等保持懷疑
- 用 grep / pytest 驗證後才採納

### §1.9 多輪 review 累積補強
- 重要 plan 走 v1 → v2 → v3 → v4 累積補強
- 每輪 review 修正前一版漏點、不一次 ship

---

## §2 工作流類別判定

```
改動範圍？
  ├── 僅 .md / 文件 / 配置           → DOC-Refactor
  ├── 前端（static/ HTML/CSS/JS）
  │   ├── 緊急                        → FE-Hotfix
  │   └── 一般                        → FE-Refactor
  └── 後端（.py 業務邏輯）
      ├── 緊急                        → BE-Hotfix
      └── 一般                        → BE-Refactor
```

| 工作流 | 必讀 SOP | 套用 template |
|---|---|---|
| FE-Refactor | — | template_plan + template_tasks + template_execution |
| BE-Refactor | logging_SOP + database_SOP | template_plan + template_tasks + template_execution |
| DOC-Refactor | — | template_plan + template_tasks + template_execution |
| FE-Hotfix | — | template_hotfix |
| BE-Hotfix | logging_SOP + database_SOP | template_hotfix |

細節定義 → `ref/WORKFLOW_SOP.md §1`

---

## §3 工作目錄硬規則

**唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`

- 嚴禁讀寫主 repo 目錄（worktree 父目錄）
- 嚴禁改動業務代碼（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`）
- 違規：baron 有權直接 revert、不通知
- **baton/ 暫存**：plan / tasks / 執行報告 在收官前一律暫存 `baton/`（不入 Git 版控）

```
.claude-logs/
├── ref/          # session 必讀核心（@path 自動載入）
├── sop/          # 領域 SOP（BE-Refactor / BE-Hotfix 強制）
├── plans/        # 改版規劃（baron / Antigravity / Claude Design 產出）
├── tasks/        # commit 拆分清單（Claude Code 階段 2）
├── executions/   # 執行報告（Claude Code 階段 4）
├── hotfixes/     # 緊急修補
├── templates/    # 模板（template_plan / tasks / execution / hotfix / prompt_for_*）
├── prompts/      # 提示詞歸檔
├── baton/        # 跨 AI 交接暫存（平時為空）
├── archive/      # 過期文件暫存
├── tools/        # 工具腳本
├── report/       # 工具產出報告
└── TODO.md       # 任務狀態真理源
```

`.gitignore`：`baton/*` 不入版控；`!baton/README.md` 例外入版控

文件歸屬判定 → `ref/WORKFLOW_SOP.md §2`

---

## §4 跨環境同步

| 環境 | 路徑 | 分支 |
|---|---|---|
| Claude Code Server worktree | `~/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/` | `gemini-refactor` |
| Mac OrbStack | `~/mad-professor-public/` | `gemini-refactor` |
| GCP 正式機 | TBD | TBD |

同步：`git pull origin gemini-refactor`

---

## §5 任務代號

- 格式：`<TYPE>-N`、子代號 `R1 / B1 / C1 / P2-1` 等
- 新類型自然增長、沿用 git log + `.claude-logs/` 既有風格
- 既有範例：`MODEL-3 B1/B2/B3` / `MODEL-8 C1/C2/C3` / `RAG-1 R1/R2/R3` / `LOGGING-1/2/3`

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | Claude Code session 入口；核心規範與契約 / 工作流類別判定 / 工作目錄硬規則 |
| 用途 | session 啟動自動載入；所有 Claude Code 操作的第一規則來源 |
| 權威源 | 本檔 §1–§5 |
| 引用方 | ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md |
| 被引用方 | `<由 Antigravity 自動掃描注入>` |
| 約束事項 | 嚴禁含動態內容（當前任務名 / hash / 變動數字）；≤ 200 行 |
| 改版觸發條件 | §1–§5 任一規範變動 |
| 改版規則 | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| 刪除條件 | 不刪（永久必讀核心） |
| 重複防護 | 工作流定義唯一源在 WORKFLOW_SOP.md；工作目錄規則唯一源在本檔 §3 |

### §99.2 Revision 歷程

- v3 (2026-05-26)：WORKFLOW-1 C1.5——§1.4 TODO 維護補入拆 tasks 時同步更新規則（對齊 plan r11）
- v2 (2026-05-26)：WORKFLOW-1 C1——補 @path 自動載入、核心規範與契約整合（§1 = 原§1 + §2 合併）、工作流類別判定（§2）、工作目錄硬規則含 baton 暫存（§3）、§0 / §99 拆分式結構
- v1 (2026-05-19)：初版
