# WORKFLOW-1 設計歷程 — 流程簡化與文件治理

> 記錄 WORKFLOW-1 從提案到收官的關鍵設計演進，供後續任務改版參考。

---

## §0 改版規則

- 本檔為靜態歸檔文件，不再改版
- 完整治理規格 → §99

---

## §1 任務概要

| 項目 | 內容 |
|---|---|
| 任務代號 | WORKFLOW-1 |
| 執行日期 | 2026-05-25 ~ 2026-05-26 |
| 工作流類別 | DOC-Refactor |
| Commits | C1 / C1.5 / C2 / C3 / C4 / C5（共 6 個） |
| Git Hash 範圍 | `1a0394c`（C1）→ C5 hash（baron 回填） |

---

## §2 Plan 版本演進（v1 → v11）

| 版本 | 重點異動 |
|---|---|
| v1–v4 | 初版提案；流程六階段雛形；確認 DOC-Refactor 工作流 |
| v5–v7 | 引入 §0/§99 拆分式結構規格；GOVERNANCE_OVERVIEW 長度硬約束（≤ 60 行） |
| v8–v9 | C2+C3 最初設計；提示詞模板五大類規格確立 |
| v10 | 補入元數據審計塊規格（五欄表格）；§8 baron 手動 commit 命令格式 |
| v11（r11）| **關鍵決策**：階段 2 拆 tasks 時強制同步 TODO.md（r11 核心新增）；tasks §0.5 成果盤點標準化 |

---

## §3 關鍵設計決策

### §3.1 mv + git add 安全指令（絕不 git mv）

**問題背景**：baton/ 目錄被 `.gitignore` 排除（`baton/*`），用 `git mv` 移動 baton 下的暫存檔案時，git 會拋出 `fatal: not under version control` 錯誤。

**決策（Option A）**：
- 永遠使用系統 `mv` 命令移動 baton 文件
- 移動後用 `git add <目的路徑>` 追蹤新位置
- `baton/README.md` 透過 `!baton/README.md` gitignore 例外規則入版控

**影響**：所有 template_prompt_for_check.md、收官 SOP、baton/README.md 均明文標示此規則。

---

### §3.2 Lazy Hash Backfill（Hash 遞補策略）

**問題背景**：Claude Code 執行時不知道最終 commit hash（baron 手動 commit 後才有）。

**決策**：
- 執行報告（_執行.md）產出時，hash 欄位填 `待 baron 回填`
- Baron 手動 commit 後，回填正確 hash 至報告
- C5 收官前無需強制回填，C5 執行報告可使用 `git log` 確認歷史 hash

**效益**：解耦 hash 知識與執行報告產出時機，避免 AI 猜測錯誤 hash。

---

### §3.3 C2 + C3 一起 Commit（Squash）

**原計畫**：C2（Templates & Overview）和 C3（Prompt Templates）分兩個 commit。

**實際執行**：Baron 將兩次 Claude Code 工作的 git add 一次 commit，導致 C2 和 C3 共用 hash `365aa5d`。

**結論**：兩份執行報告（C2_執行.md / C3_執行.md）均已記錄 hash `365aa5d`；TODO.md 已更新為「C2 & C3」合併條目。此為合法操作，無需特殊處理。

---

### §3.4 元數據審計塊（Metadata Audit Block）

**設計目的**：讓 Claude Code 在每次收到執行提示詞時，先填寫五欄標準元數據，形成 Audit Trail。

**五欄格式**：
| 欄位 | 說明 |
|---|---|
| 收到時間 | YYYY-MM-DD（日期即可，不需精確時間） |
| 任務代號 | 如 WORKFLOW-1 C4 |
| 觸發 Commit | 本次執行對應的 Commit 代號 |
| 相關產出檔案 | 預期新建/修改的檔案清單 |
| 觸發情境 | 簡述任務背景與前置條件 |

**落地位置**：`template_prompt_for_run.md` 頂部。

---

### §3.5 Bootstrap First Principle（C1 最小化）

**原則**：C1 只包含 session 啟動時自動載入的最核心文件，不摻雜工具或模板。

**C1 範圍**：CLAUDE.md + WORKFLOW_SOP.md + PROJECT_PROGRESS_CONTROL_FRAMEWORK.md + .gitignore baton 排除規則。

**C1.5 補充**：因 r11 新增「拆 tasks 時同步 TODO.md」規則，需要對 C1 的三個文件做規格對齊，拆為獨立 C1.5，避免 C1 過重。

---

## §4 六 Commits 產出清單

| Commit | Hash | 主要產出 |
|---|---|---|
| C1 | `1a0394c` | CLAUDE.md 重構 / WORKFLOW_SOP.md 新建 / framework §0/§9/§99 / .gitignore |
| C1.5 | `e0c7a17` | r11 規格對齊（CLAUDE.md §1.4 / WORKFLOW_SOP.md §3 / framework §9.2）+ TODO.md 自舉 |
| C2 & C3 | `365aa5d` | 5 模板重構/新建 / GOVERNANCE_OVERVIEW.md / baton/README.md / 5 提示詞模板 |
| C4 | `ad0be4e` | CACHE_OPTIMIZATION_SOP.md / report/.gitkeep |
| C5 | `待 baron 回填` | TODO.md 收官 / 設計歷程.md / 全部 baton 歸檔 / prompts/INDEX.md |

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | 記錄 WORKFLOW-1 設計演進與關鍵決策，供後續任務改版參考 |
| 用途 | 靜態歸檔，不入自動載入路徑 |
| 權威源 | 本檔 §1–§4 |
| 引用方 | 無（純歸檔） |
| 被引用方 | `<由 Antigravity 自動掃描注入>` |
| 約束事項 | 靜態歸檔，不改版 |
| 刪除條件 | 不刪（長期歸檔） |
| 重複防護 | 各 Commit 細節見對應 _執行.md；本檔僅記錄跨 Commit 設計決策 |

### §99.2 Revision 歷程

- v1 (2026-05-26)：初版（C5 收官時產出）
