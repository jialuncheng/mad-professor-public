# Claude Code 啟動指引

> 💡 **session 啟動第一件事**：讀 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（框架本體）。
> 本檔僅為「最關鍵規則 + 文件索引」、所有細節指向框架 / `prompts/README.md` / 既有 `_plan.md` 既有 `_執行.md`。

---

## 0. session 啟動必讀（依序）

1. `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` — 框架本體（plan-execution 雙軌、任務生命週期、§6 提示詞歸檔規範）
2. `.claude-logs/prompts/README.md` — 提示詞歸檔規則（命名 / 格式 / 觸發條件）
3. `.claude-logs/TODO.md` — 當前任務狀態真理源（🟡 WIP / 🔵 候選 / ✅ 完成）

---

## 1. 核心規範

### 1.1 plan-execution 雙軌制
- **plan 階段**：嚴禁動業務代碼、只 view / grep / 文件編輯
- **execution 階段**：依 plan 落地、最小可逆 commit、附 pytest + E2E 驗證

### 1.2 提示詞歸檔（框架 §6）
- 流程：先歸檔到 `.claude-logs/prompts/` → 再執行 → 同步 `INDEX.md`
- 觸發：命令動詞（請執行 / 撰寫 / 修正）/ 長度 > 500 字 / 結構化區塊（═══ 或 ## 第X步）
- 模糊時優先歸檔；敏感資訊（API key / 密碼 / email）打碼後再寫入
- 細節規範見 `.claude-logs/prompts/README.md`

### 1.3 不 commit / push
- auto-classifier 阻擋 Claude Code 直接 commit / push
- 所有 commit / push 由 baron 手動執行
- Claude Code 只負責：備好改動 + 寫 commit message 草稿（存到 `/tmp/msg.txt`）+ 列出 `git add` 清單

### 1.4 TODO 維護
- ship 後**立即同步**：🟡 WIP → ✅ 完成（多 commit 任務待全部 ship）
- 不累積技術債、不追溯刪除

---

## 2. 互動流程契約

### 2.1 plan 階段必產出 Q1-QN 表
- 凡 plan 文件、§Open Questions 章節必含「問題 + 推薦答案 + 理由」三欄
- baron 過目 / 修改後才進 execution

### 2.2 不確定先問
- 設計決策模糊時、停下來問 baron、不擅自下結論
- 邊界情況（如 schema 變動 / 新依賴 / 跨任務影響）強制詢問

### 2.3 提案用 grep 證據
- 任何「既有 codebase 是 X」「既有 endpoint 是 Y」必附 grep 命令 + 真實行號
- 不靠記憶 / 不憑感覺

### 2.4 警戒行銷話術
- 「30-50x 提速」「100% 正確率」「無痛升級」等保持懷疑
- 用 grep / pytest 驗證後才採納

### 2.5 多輪 review 累積補強
- 重要 plan（如 logging refactor / RAG-1 UI Fixes）走 v1 → v2 → v3 → v4 累積補強
- 每輪 review 修正前一版漏點、不一次 ship

---

## 3. 工作目錄

.claude-logs/             # 全目錄入版控、跨環境同步
├── ref/                  # 必讀核心（極簡）：框架本體、WORKFLOW_SOP 索引
├── sop/                  # 領域 SOP（logging / database / 模型 / 未來新增）
├── revision_plans/       # 改版規劃書（任務輸入規格、由 baron / Antigravity / Claude Design 產出）
├── plans/                # 執行計劃（_plan.md / _可行性評估.md、由 Claude Code 產出）
├── executions/           # 執行報告（_執行.md、ship 後產出）
├── hotfixes/             # 緊急修補報告（_hotfix.md）
├── templates/            # 模板（template_plan / template_execution / template_hotfix / 未來新增）
├── prompts/              # 提示詞資料庫（README + INDEX + 歷史歸檔）
├── baton/                # 跨 AI 工具交接棒（WORKFLOW-1-0 後生效、平時為空）
├── archive/              # 過期文件暫存（手動移入、定期清理）
├── tools/                # 工具腳本（cleanup_push.sh 等）
└── TODO.md               # 任務狀態真理源

`.gitignore` 規則：

- `.claude-logs/` 全目錄不排除
- `**/.DS_Store` 永久排除

文件歸屬規則：
- 改版規劃書 → `revision_plans/`（任務的「Why + What」、長期保留）
- 執行計劃 → `plans/`（任務的「How」、ship 後可歸 archive）
- 執行報告 → `executions/`（任務的「What was done」、ship 後可歸 archive）
- SOP → `sop/`（領域規範、長期保留）
- 必讀核心 → `ref/`（框架本體、極簡、跨任務必讀）

---

## 4. 跨環境同步

| 環境 | 路徑 |
| --- | --- |
| Claude Code Server worktree | `/home/baroncheng/mad-professor-public/.claude/worktrees/{hash}/` |
| Mac OrbStack | `~/mad-professor-public/` |
| Docker / GCP 正式機 | TBD |

- 共同 upstream：`origin/gemini-refactor`（SoT）
- 同步：`git pull origin gemini-refactor`

---

## 5. 任務代號

- 格式：`<TYPE>-N`、子代號 `R1 / B1 / C1 / P2-1` 等
- 新類型自然增長、沿用 git log + `.claude-logs/` 既有風格
- 既有範例：`MODEL-3 B1/B2/B3` / `MODEL-8 C1/C2/C3` / `RAG-1 R1/R2/R3` / `RAG-1 P2-1` / `LOGGING-1/2/3`

---

**END** — 任何超出本檔範圍的規範、查 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`