# WORKFLOW-1 流程簡化與文件治理 — Tasks

> 本文件為 WORKFLOW-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`（v11）產出，含 6 個 Commit（C1–C5/C1.5）。

---

## §0 來源

- 改版觸發：baton plan §1.1–§1.19 規格變動
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 13 個 | `ref/WORKFLOW_SOP.md` / `ref/GOVERNANCE_OVERVIEW.md` / `baton/README.md` / `templates/template_plan.md` / `templates/template_file_governance.md` / `templates/template_specification.md` / `templates/template_prompt_for_plan.md` / `templates/template_prompt_for_tasks.md` / `templates/template_prompt_for_run.md` / `templates/template_prompt_for_sop.md` / `templates/template_prompt_for_check.md` / `sop/CACHE_OPTIMIZATION_SOP.md` / `archive/WORKFLOW-1_設計歷程.md` |
| **修改檔案** | 5 個 | `CLAUDE.md`（大型重構）/ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（補 §9 + §0/§99）/ `templates/template_tasks.md`（補 §0.5 + §0/§99 重構）/ `templates/template_execution.md`（補元數據塊 + §0/§99）/ `.gitignore`（收尾 unstaged 修改）|
| **目錄初始化** | 1 個 | `report/`（空目錄 + `.gitkeep`）|
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 6 個 | C1 Bootstrap Core → C1.5 Core Spec Align & TODO Bootstrap → C2 Templates & Overview → C3 Prompt Templates → C4 SOP & Diagnostics → C5 收官 |
| **baton 歸檔** | 2 次 | C5 收官：`mv` baton plan → `plans/` + `git add`；`mv` baton tasks（本檔）→ `tasks/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：現有工作流缺乏標準化 Session 啟動約束——CLAUDE.md 無 @path 自動載入、WORKFLOW_SOP.md 不存在、模板無 §0/§99 拆分式結構、6 個階段提示詞模板全部缺失——導致每次 Claude Code session 須手工重複說明規則，且無統一提示詞格式
- **解法**：依 §1.18 Bootstrap First 原則，C1 先落地自動載入核心；C1.5 對齊核心規格並在 TODO.md 中自舉初始化任務狀態；C2 補完模板與引導文件；C3 補完 5 個提示詞模板；C4 補完 SOP 與診斷目錄；C5 收官歸檔
- **影響範圍**：100% DOC-Refactor（文件改動），零業務代碼改動
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 |
|---|---|---|
| `CLAUDE.md` | 存在，舊格式（§0 無 @path 引用；§2 = 互動流程契約，非工作流類別判定） | @path 自動載入機制；§2 工作流類別判定；§1 核心規範與契約整合；§3 工作目錄硬規則含 baton 暫存規則 |
| `ref/WORKFLOW_SOP.md` | **不存在** | 五類工作流定義 / SOP 核查 / 命名規則等全部缺失 |
| `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` | 存在，§1–§8 舊格式，無 §0/§99 拆分式，無 §9 補充條款 | §9（§9.1–§9.4 引用方式）/ §0 改版規則 / §99 治理規格 |
| `ref/GOVERNANCE_OVERVIEW.md` | **不存在** | 治理框架 entry point 缺失 |
| `baton/README.md` | **不存在** | baton 機制無說明文件 |
| `templates/template_plan.md` | **不存在** | 純規格 plan 模板缺失 |
| `templates/template_file_governance.md` | **不存在** | §99 治理表標準範本缺失 |
| `templates/template_specification.md` | **不存在** | API/Schema 規格模板缺失 |
| `templates/template_tasks.md` | 存在，舊格式（無 §0/§99；無 §0.5 成果盤點；§8 無六維度） | §0/§99 結構；§0.5 成果盤點；§8 六維度 commit 拆分格式 |
| `templates/template_execution.md` | 存在，舊格式（無頂部元數據塊；無 §0/§99；無 §8 baron 執行命令） | 頂部元數據塊；§8 baron 執行命令（git add 清單 + /tmp 草稿）；§0/§99 |
| `templates/template_prompt_for_*.md`（5 個） | **全部不存在** | 各階段提示詞格式每次從零撰寫 |
| `sop/CACHE_OPTIMIZATION_SOP.md` | **不存在** | 快取友善度評分流程 SOP 缺失 |
| `.gitignore` | 有 baton 排除規則，但存在 unstaged 修改未收尾 | 需 `git add .gitignore` 收尾 |

---

## §3 觀察問題

### 問題 #1：WORKFLOW_SOP.md 不存在——工作流判定無標準來源
- **證據**：`ls .claude-logs/ref/` → 無 `WORKFLOW_SOP.md`
- **影響**：Claude Code 每次 session 無法透過 @path 自動載入工作流規則

### 問題 #2：CLAUDE.md 無 @path 自動載入機制
- **證據**：`grep "@.claude-logs" CLAUDE.md` → 0 命中
- **影響**：session 啟動後仍需提示詞手工指定要讀哪些文件

### 問題 #3：template_tasks.md 缺少 §0/§99 + §0.5 成果盤點
- **證據**：`grep -c "^## §0\|^## §0\.5\|^## §99" .claude-logs/templates/template_tasks.md` → 0 命中
- **影響**：tasks 文件格式不統一；缺成果量化；§8 commit 拆分無六維度約束

### 問題 #4：5 個提示詞模板全部缺失
- **證據**：`ls .claude-logs/templates/template_prompt_for_*.md` → 無文件
- **影響**：baron 每次手工撰寫提示詞；格式不一致；無停止指令約束

### 問題 #5：.gitignore 有 unstaged 修改（已有 baton 排除規則但未收入版控）
- **證據**：`git status -s .gitignore` → ` M .gitignore`
- **影響**：baton/ 下本 tasks 檔案目前不受版控保護，但 .gitignore 的意圖尚未正式 commit

---

## §4 設計方案

### §4.1 C1 — Bootstrap Core（自動載入核心）

嚴格依 §1.18.1 第一順位原則，C1 只含自動載入核心文件，嚴禁混入模板或 SOP。

1. **`CLAUDE.md`** 重構（per §1.5）：
   - §0 改版規則（極簡靜態 3 行，含 @path 引用清單）
   - §1 session 啟動必讀：改為 @path 引用（`@.claude-logs/ref/WORKFLOW_SOP.md` / `@.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` / `@.claude-logs/TODO.md` / `@.claude-logs/baton/*.md`）
   - §2 核心規範與契約（整合舊 §1 核心規範 + 舊 §2 互動流程契約，扁平化；保留既有規則語意）
   - §3 工作流類別判定（新增 ASCII 流程圖 + 五類表格；依 §1.6 五類定義）
   - §4 工作目錄硬規則（唯一目錄 / 嚴禁主 repo / 違規 revert；**執行中文件必須先放 baton/**；動態內容禁用）
   - §5 跨環境同步（保留既有內容）
   - §6 任務代號（保留既有內容）
   - §99 治理規格
   - 硬約束：≤ 200 行；零動態內容（無任務名 / hash / 具體日期）

2. **`ref/WORKFLOW_SOP.md`** 新建（per §1.6，完整版）：
   - §0 改版規則（極簡靜態）
   - §1 五類工作流定義（FE-Refactor / BE-Refactor / DOC-Refactor / FE-Hotfix / BE-Hotfix，每類含觸發條件 / 必讀 SOP / 套用 template / 驗收要求）
   - §2 文書類別釐清（plan vs tasks vs execution 語意邊界）
   - §3 強制觸發鏈（六階段，引用 baton plan §1.1；各階段輸入 / 輸出 / 中斷點）
   - §4 驗證分級（核心 3 項（人人必跑）+ 進階 5 項（特定觸發條件）+ grep 關鍵字定義）
   - §5 SOP 一致性核查（per §1.14：logging grep / database grep / 違規處理 / 雙工具共用規則）
   - §6 命名規則（per §1.13 表格）
   - §99 治理規格

3. **`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`** 補充（per §1.8）：
   - 頂部插入 §0 改版規則（3 行，不改現有 §1–§8 章節編號）
   - 末尾附加 §9 補充條款（§9.1 引用 CLAUDE.md §4 工作目錄硬規則；§9.2 引用 baton plan §1.1 六階段工作流；§9.3 引用 baton plan §1.3 文件用途範疇；§9.4 被引用方掃描規則說明）
   - 末尾附加 §99 治理規格

4. **`.gitignore`** 收尾：`git add .gitignore`（現有 unstaged 修改包含 baton 排除規則，已正確）

### §4.2 C2 — Templates & Overview（模板與引導）

依 §1.18.1 第二順位。

1. **`templates/template_plan.md`** 新建（per §1.10.1）：§0 改版規則；§1 TL;DR（挑戰/解法/影響）；§2 目標規格；§3 現況與證據（含 grep 佔位符）；§4 不可動清單；§5 規格依據；§6 驗證計畫（含 pytest 指令與 E2E）；§7 Open Questions；§99 治理規格
2. **`templates/template_file_governance.md`** 新建（per §1.10.5）：§99 治理表標準範本，10 欄（目的 / 用途 / 權威源 / 引用方 / 被引用方 / 約束事項 / 改版觸發 / 改版規則 / 刪除條件 / 重複防護）；被引用方欄固定為 `<由 Antigravity 自動掃描注入>` 佔位符
3. **`templates/template_specification.md`** 新建（per §1.10.6）：§0 用途；§1 介面定義；§2 行為合約；§3 邊界條件；§4 變動歷程；§99 治理規格
4. **`templates/template_tasks.md`** 重構（per §1.10.2）：前插 §0 改版規則（3 行）；在舊 TL;DR 前插 `## §0.5 成果盤點`（表格）；標題改為 `## §1 TL;DR（概要）`；§2–§7 保留語意、更新標號格式；§8 commit 拆分改為六維度 per-OP 表格（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）；§9 Open Questions；末尾加 §99 治理規格
5. **`templates/template_execution.md`** 更新（per §1.10.3）：頂部加元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / commit 留空 / 狀態）；§1–§7 保留語意；加 §8 baron 執行命令（`git add` 清單 + commit message 草稿寫入 `/tmp/<task>_msg.txt` + `git commit -F` 指令）；末尾加 §0/§99
6. **`ref/GOVERNANCE_OVERVIEW.md`** 新建（per §0.5.7）：≤50 行；純指針；8 個章節各 2–3 行（工作流 / 文件用途範疇 / 工作目錄硬規則與核心規範契約 / baton 機制 / 模板規格 / SOP 核查 / 快取評分 / 任務生命週期），每章節指向各權威源的語意標題錨點（不用章節編號，防 cache invalidation）；維護責任在 §99

### §4.3 C3 — Prompt Templates（提示詞模板）

5 個新文件（`templates/template_prompt_for_*.md`），依 §1.10.7–§1.10.11：

| 文件 | 核心必含（per §1.10） |
|---|---|
| `template_prompt_for_plan.md` | 任務編碼 + 強制讀檔清單 + 撰寫原則（純規格、無 Why）+ 產出規格（plans/）+ 停止指令（產 plan.md 即停） |
| `template_prompt_for_tasks.md` | 任務編碼 + 工作流類別 + 成果盤點約束（§0.5）+ 六維度 §8 約束 + 產出規格（baton/→tasks/）+ 停止指令（產 tasks.md 即停） |
| `template_prompt_for_run.md` | 元數據審計塊 + 單一 Commit 指定 + 任務執行命令（引用 §8 實作細節 / §7 不可動清單 / §6 測試計畫）+ 產出規格（baton/→executions/）+ baron 手動執行命令草稿區塊 + 停止指令 |
| `template_prompt_for_sop.md` | SOP 領域名稱 + 強制讀檔清單 + 撰寫原則（規範性、可 grep 化）+ 產出規格（sop/）+ 停止指令 |
| `template_prompt_for_check.md` | Conformance 驗收指示（逐項交叉比對 plan §2 目標規格 + tasks §6 測試計畫 + executions 結果）+ 收官自動化動作（`mv + git add` 歸檔；TODO 更新）+ 停止指令（完成歸檔即停、嚴禁 git commit）|

### §4.4 C4 — SOP & Diagnostics（領域 SOP 與診斷目錄）

依 §1.18.1 第三順位。

1. **`sop/CACHE_OPTIMIZATION_SOP.md`** 新建（per §1.15）：§0 改版規則；§1 評分算法（靜態前綴檢測，100/50/0 三級）；§2 排除名單（TODO.md / prompts/ / report/）；§3 評分結果存放（`report/<YYYY-MM-DD>_CACHE_FRIENDLINESS_REPORT.md`）；§4 觸發時機；§5 第一輪評分範圍（4 個文件）；§99 治理規格
2. **`report/.gitkeep`** 新建：目錄初始化，確保 `report/` 納入版控、工具可寫入報告

### §4.5 C5 — 收官（Closure）

1. **`archive/WORKFLOW-1_設計歷程.md`** 新建：整理 v1→v4-final-r4-v6-r10 演進摘要（從 baton plan §99.2 Revision 歷程提煉，每版 1–2 行重點）
2. **baton plan → plans/**：`mv .claude-logs/baton/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md .claude-logs/plans/` + `git add .claude-logs/plans/...`
3. **baton tasks → tasks/**：`mv .claude-logs/baton/2026-05-26_WORKFLOW-1_流程簡化與文件治理_tasks.md .claude-logs/tasks/` + `git add .claude-logs/tasks/...`
4. **`TODO.md`** 更新：WORKFLOW-1 從 🟡 WIP 移至 ✅ 完成；各 Commit 代號列表；hash 欄全部標「待 baron 回填」
5. **`prompts/INDEX.md`** 更新：補入本任務各階段歸檔提示詞條目（若有）

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| CLAUDE.md 重構後 @path 路徑錯誤 | 🟡 中 | C1 完成後執行驗收 B（grep 確認 @path 語法正確）再 commit |
| CLAUDE.md 超過 200 行 | 🟡 中 | §2 核心規範與契約整合（扁平化）可大幅縮短；執行前 `wc -l` 確認 |
| template_tasks.md 重構後舊格式 tasks 文件產生歧義 | 🟢 低 | 歷史命名不溯及既往；只改模板，不改既有 tasks/*.md 內容 |
| framework §0 插入干擾 Prompt Cache | 🟢 低 | §0 為 3 行極簡靜態，插入後整體 cache prefix 位移極小 |
| `mv + git add` 歸檔若 baton 檔案已被 gitignore 則 git add 無效 | 🟡 中 | C5 執行前確認 baton plan/tasks 實際處於 untracked 狀態（非 staged）；若有問題使用 `git add -f` 強制加入 |

---

## §6 測試計畫

DOC-Refactor 工作流，無 `.py` 改動，跳過 §1.14 logging / database SOP grep 核查。

### §6.1 C1 驗收

```bash
# A：WORKFLOW_SOP.md 存在且含 6 個必要章節
find .claude-logs/ref/ -name "WORKFLOW_SOP.md" -q && \
  grep -c "^## §1\|^## §2\|^## §3\|^## §4\|^## §5\|^## §6" .claude-logs/ref/WORKFLOW_SOP.md
# 期望：找到文件；計數 = 6

# B：CLAUDE.md 含 @path 引用
grep -c "@\.claude-logs/ref/WORKFLOW_SOP\.md\|@\.claude-logs/ref/PROJECT_PROGRESS" CLAUDE.md
# 期望：≥ 2

# C：CLAUDE.md 含工作流類別判定相關章節
grep -n "工作流類別判定\|FE-Refactor\|BE-Refactor\|DOC-Refactor" CLAUDE.md | head -5
# 期望：有命中

# D：CLAUDE.md 零動態內容
grep -n "WORKFLOW-1\|2026-0\|commit.*hash\|今天\|今日" CLAUDE.md
# 期望：0 命中

# E：CLAUDE.md ≤ 200 行
wc -l CLAUDE.md
# 期望：≤ 200

# F：framework §9 與 §99 存在
grep -c "^## §9\b\|^## §99\b" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
# 期望：2

# G：業務代碼無改動
git diff --cached --name-only | grep -E "\.py$|\.html$|\.css$|\.js$"
# 期望：0 命中
```

### §6.1.5 C1.5 驗收

```bash
# A：WORKFLOW_SOP.md 與 PROJECT_PROGRESS_CONTROL_FRAMEWORK.md 已對齊 r11 規格
grep -E "同步更新.*TODO\.md|todo_s2" .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
# 期望：有命中且包含 r11 新增之 TODO.md 同步規則

# B：TODO.md 已存在且包含本任務所有 Commit (C1-C5/C1.5) 的 WIP 狀態
grep -A 8 "WORKFLOW-1" .claude-logs/TODO.md
# 期望：包含 C1 且狀態為 done，包含 C1.5 至 C5 且狀態為 WIP

# C：業務代碼無改動
git diff --cached --name-only | grep -E "\.py$|\.html$|\.css$|\.js$"
# 期望：0 命中
```

### §6.2 C2 驗收

```bash
# A：6 個新增/更新模板存在
for f in template_plan.md template_file_governance.md template_specification.md \
          template_tasks.md template_execution.md; do
  [ -f ".claude-logs/templates/$f" ] && echo "✅ $f" || echo "❌ $f"
done
[ -f ".claude-logs/ref/GOVERNANCE_OVERVIEW.md" ] && echo "✅ GOVERNANCE_OVERVIEW.md" || echo "❌"

# B：template_tasks.md 含 §0 / §0.5 / §99
grep -c "^## §0 \|^## §0\.5\|^## §99" .claude-logs/templates/template_tasks.md
# 期望：3

# C：template_execution.md 含元數據塊與 §8 baron 執行命令
grep -n "任務代號\|執行日期\|baron 執行命令\|/tmp/" .claude-logs/templates/template_execution.md | head -5
# 期望：有命中

# D：GOVERNANCE_OVERVIEW.md ≤ 60 行
wc -l .claude-logs/ref/GOVERNANCE_OVERVIEW.md
# 期望：≤ 60
```

### §6.3 C3 驗收

```bash
# A：5 個 prompt 模板全部存在
for f in template_prompt_for_plan.md template_prompt_for_tasks.md \
          template_prompt_for_run.md template_prompt_for_sop.md \
          template_prompt_for_check.md; do
  [ -f ".claude-logs/templates/$f" ] && echo "✅ $f" || echo "❌ $f"
done

# B：每個模板含停止指令關鍵字
grep -l "停止\|即停\|嚴禁.*繼續" .claude-logs/templates/template_prompt_for_*.md | wc -l
# 期望：5

# C：template_prompt_for_check.md 含 Conformance / mv + git add 關鍵字
grep -n "Conformance\|合規\|mv.*git add\|git add.*mv" .claude-logs/templates/template_prompt_for_check.md | head -5
# 期望：有命中
```

### §6.4 C4 驗收

```bash
# A：CACHE_OPTIMIZATION_SOP.md 存在且含 §0/§99 + 評分算法關鍵字
find .claude-logs/sop/ -name "CACHE_OPTIMIZATION_SOP.md" -q && \
  grep -c "^## §0\b\|^## §99\b\|評分算法\|排除名單" .claude-logs/sop/CACHE_OPTIMIZATION_SOP.md
# 期望：找到文件；計數 ≥ 4

# B：report/ 目錄存在
[ -d ".claude-logs/report" ] && echo "✅ report/ 存在" || echo "❌"
```

### §6.5 C5 驗收

```bash
# A：baton/ 只剩 README.md
ls .claude-logs/baton/
# 期望：只有 README.md

# B：plan 已進入 plans/
find .claude-logs/plans/ -name "*WORKFLOW-1*plan*v4*" | head -3
# 期望：有命中

# C：tasks 已進入 tasks/
find .claude-logs/tasks/ -name "*WORKFLOW-1*tasks*" | head -3
# 期望：有命中

# D：TODO.md 顯示 WORKFLOW-1 完成
grep -A 3 "WORKFLOW-1" .claude-logs/TODO.md | head -8
# 期望：出現 ✅ 完成
```

---

## §7 不可動清單

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` / `design/*` / `tests/*` — 100% 不動
- [ ] **主 repo 目錄**（worktree 父目錄 `~/mad-professor-public/`）— 嚴禁讀寫
- [ ] **既有 100+ 歷史 `.claude-logs/` 文件**（plans/ / tasks/ / executions/ / sop/ / prompts/）— 不改、不重命名、不刪除
- [ ] **既有業務 commit 歷史** — 不 amend、不 force push
- [ ] **`prompts/README.md`**（提示詞歸檔規範）— 不動（C5 只改 `prompts/INDEX.md`）
- [ ] **`templates/template_hotfix.md`** — §1.10.4 明確「維持既有規格」，不動

---

## §8 推薦 Commit 拆分

### C1 — Bootstrap Core（自動載入核心）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `CLAUDE.md`（大型重構）/ `ref/WORKFLOW_SOP.md`（新建完整版）/ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（補 §9 + §0/§99）/ `.gitignore`（收尾 unstaged 修改）|
| **安全性** | 🟢 高 — 100% 文件改動；零 runtime 影響；CLAUDE.md 重構只影響 AI 讀檔行為 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；4 個文件獨立 |
| **驗收 grep 條件** | §6.1 A–G 全部通過（7 項）|
| **依賴關係** | 無前置；本 Commit 是後續所有 Commit 的前提（§1.18.2 Bootstrap First 強制）|
| **具體實作細節** | 1. `git add .gitignore`（收尾 unstaged baton 排除規則）；2. 依 §1.5 重構 `CLAUDE.md`：保留 §1 核心規範與契約語意（整合舊 §1 + §2）；改 §1 session啟動為 @path 引用區塊；新增 §3 工作流類別判定 ASCII 流程圖 + 五類表格；更新 §4 工作目錄硬規則（含 baton 暫存規則 + 動態內容禁用）；末尾加 §0 改版規則 3 行 + §99；全文 ≤ 200 行；3. 新建 `ref/WORKFLOW_SOP.md`（§0/§99 拆分式；§1 五類各含觸發/SOP/template/驗收；§2 文書類別；§3 六階段強制觸發鏈；§4 驗證分級 3+5；§5 logging/database grep 核查規則；§6 命名規則表格）；4. 在 `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 頂部插入 §0（3 行靜態）；末尾附加 §9（§9.1 引用 CLAUDE.md §4；§9.2 引用 baton plan §1.1；§9.3 引用 baton plan §1.3；§9.4 被引用方掃描規則）+ §99 |

---

### C1.5 — Core Spec Align & TODO Bootstrap（核心規格與 TODO 自舉）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `CLAUDE.md` / `ref/WORKFLOW_SOP.md` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（規格升級對齊 r11）+ `TODO.md`（初始化寫入並對齊狀態）|
| **安全性** | 🟢 高 — 100% 文件與狀態對齊；零業務代碼影響 |
| **可逆性** | 🟢 高 — `git revert C1.5` 完全回滾 |
| **驗收 grep 條件** | §6.1.5 A–C 全部通過（3 項）|
| **依賴關係** | 依賴 C1（必須在 C1 落地完成後，將核心文件對齊升級至計畫書 r11 規格，並初始化自舉 TODO）|
| **具體實作細節** | 1. 依計畫書 r11 規格升級 `CLAUDE.md`、`ref/WORKFLOW_SOP.md`（更新 `階段 2` 產出含有更新 TODO.md，更新 `階段 6` 收官動作）與 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（更新 `§9.2` 與 `§9.3`），確保核心文件對齊最新流程；2. 在根目錄 `TODO.md` 初始化 `WORKFLOW-1` 任務狀態，新增本任務的所有 commit (C1-C5/C1.5) 任務清單，並將 `C1` 標記為 `✅ done`，將本 `C1.5` 登記為 `🟡 WIP`。|

---

### C2 — Templates & Overview（模板與引導）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_plan.md`（新建）/ `templates/template_file_governance.md`（新建）/ `templates/template_specification.md`（新建）/ `templates/template_tasks.md`（重構）/ `templates/template_execution.md`（更新）/ `ref/GOVERNANCE_OVERVIEW.md`（新建）/ `baton/README.md`（新建）|
| **安全性** | 🟢 高 — 純模板 + 文件；歷史 tasks/executions/plans 內容不受影響 |
| **可逆性** | 🟢 高 — 3 新建直接刪除；2 更新可 git revert；baton/README.md 可刪除 |
| **驗收 grep 條件** | §6.2 A–D 全部通過（4 項）|
| **依賴關係** | 依賴 C1（WORKFLOW_SOP.md 需存在供 template_tasks.md §99 引用）|
| **具體實作細節** | 1. 新建 `template_plan.md`（§0 3 行；§1 TL;DR；§2 目標規格；§3 現況與證據含 grep 佔位；§4 不可動清單；§5 規格依據；§6 驗證計畫含 pytest + E2E；§7 Open Questions；§99 治理規格）；2. 新建 `template_file_governance.md`（§99 治理表 10 欄範本；被引用方 = `<由 Antigravity 自動掃描注入>`；每欄含填寫說明）；3. 新建 `template_specification.md`（§0 用途；§1 介面定義；§2 行為合約；§3 邊界條件；§4 變動歷程；§99 治理規格）；4. 重構 `template_tasks.md`（前插 §0 改版規則；§0.5 成果盤點表格；標題改 `## §1 TL;DR（概要）`；更新 §2–§7 標號；§8 改六維度表格 per-OP；§9 Open Questions；末尾 §99）；5. 更新 `template_execution.md`（頂部插入元數據塊：任務代號/執行日期/依據/commit 留空/狀態；加 §8 baron 執行命令：git add 清單 + /tmp/msg.txt + `git commit -F`；末尾加 §0 改版規則 3 行 + §99）；6. 新建 `GOVERNANCE_OVERVIEW.md`（≤50 行；8 章節純指針；依 §0.5.7 規格；使用語意標題錨點非章節號）；7. 新建 `baton/README.md`（目錄用途；命名格式；交接流程 A–C + Traceability 要求；版控規則） |

---

### C3 — Prompt Templates（提示詞模板）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 5 個新文件：`templates/template_prompt_for_{plan,tasks,run,sop,check}.md` |
| **安全性** | 🟢 高 — 純新增；不覆蓋任何既有文件 |
| **可逆性** | 🟢 高 — `git rm` 5 個文件即可完全回滾 |
| **驗收 grep 條件** | §6.3 A–C 全部通過（3 項）|
| **依賴關係** | 依賴 C2（template_tasks.md / template_execution.md 需先就位供模板引用）|
| **具體實作細節** | 每個模板均含：(a) 文件用途說明行；(b) 最小必含清單（per §1.10.7–§1.10.11 各自規格）；(c) 套用變數佔位符 `<任務編碼>` / `<工作流類別>` / `<plan路徑>` / `<tasks路徑>` / `<執行.md清單>` 等；(d) 明確停止指令段落；(e) 提示詞歸檔指令行（依 `prompts/README.md`）。`template_prompt_for_run.md` 額外含元數據審計塊模板 + baron 手動執行命令草稿。`template_prompt_for_check.md` 額外含 Conformance 驗收清單格式 + 收官自動化動作（`mv + git add` 歸檔；TODO 更新；嚴禁 git commit） |

---

### C4 — SOP & Diagnostics（領域 SOP 與診斷目錄）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `sop/CACHE_OPTIMIZATION_SOP.md`（新建）/ `report/.gitkeep`（目錄初始化）|
| **安全性** | 🟢 高 — 純新增；不影響任何既有文件 |
| **可逆性** | 🟢 高 — 刪除 2 個文件即可完全回滾 |
| **驗收 grep 條件** | §6.4 A–B 全部通過（2 項）|
| **依賴關係** | 依賴 C1（WORKFLOW_SOP.md §5 SOP 核查規則需就位；CACHE_OPTIMIZATION_SOP 引用之）|
| **具體實作細節** | 1. 新建 `sop/CACHE_OPTIMIZATION_SOP.md`（§0 改版規則；§1 評分算法三級：100 分-黃牌-紅牌；§2 排除名單：TODO.md / prompts/ / report/；§3 評分結果存放路徑規格；§4 觸發時機：週級 + baron 手動；§5 第一輪評分範圍 4 個文件；§99 治理規格）；2. `mkdir -p .claude-logs/report && touch .claude-logs/report/.gitkeep`（確保目錄被 git 追蹤）|

---

### C5 — 收官（Closure）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `archive/WORKFLOW-1_設計歷程.md`（新建）/ baton plan → `plans/`（mv + git add）/ baton tasks → `tasks/`（mv + git add）/ `TODO.md`（更新）/ `prompts/INDEX.md`（更新）|
| **安全性** | 🟢 高 — 純文件歸檔與狀態更新 |
| **可逆性** | 🟢 高 — `git revert C5` 回滾 TODO/INDEX 更新；mv 操作可用 mv 反向 |
| **驗收 grep 條件** | §6.5 A–D 全部通過（4 項）|
| **依賴關係** | 必須在 C1–C4 全部 commit 完成且 baron 確認 §6.1–§6.4 驗收通過後才執行 |
| **具體實作細節** | 1. 新建 `archive/WORKFLOW-1_設計歷程.md`（從 baton plan §99.2 Revision 歷程提煉 v1→r10 演進摘要）；2. `mv .claude-logs/baton/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md .claude-logs/plans/ && git add .claude-logs/plans/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`；3. `mv .claude-logs/baton/2026-05-26_WORKFLOW-1_流程簡化與文件治理_tasks.md .claude-logs/tasks/ && git add .claude-logs/tasks/2026-05-26_WORKFLOW-1_流程簡化與文件治理_tasks.md`；4. 更新 `TODO.md`：WORKFLOW-1 由 🟡 WIP 移至 ✅ 完成 + C1–C5 Commit 代號列表 + hash 欄「待 baron 回填」；5. 更新 `prompts/INDEX.md`：補入本任務相關提示詞條目 |

---

## §9 Open Questions

無。（plan §4 已標記「無」，所有設計決策已在 baton plan §1.1–§1.19 明確定義。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | WORKFLOW-1 流程簡化與文件治理的 Commit 拆分清單（階段 2 產出） |
| **用途** | baron 審核後交 Claude Code 按序執行 C1–C5；Antigravity 階段 5 驗證時引用 §6 驗收條件 |
| **引用方** | `.claude-logs/baton/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`（v10）|
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動業務代碼；嚴禁讀寫主 repo 目錄；嚴禁跨 Commit 混合不同優先級文件（§1.18.2）；嚴禁自動 git commit / push |
| **改版觸發條件** | baton plan 規格更新 / Commit 範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄；不整檔重寫 |
| **刪除條件** | C5 收官完成後（本檔 mv 到 `tasks/` 後即從 baton/ 消失）|
| **重複防護** | §8 實作細節不重複 baton plan 的設計脈絡；§6 驗收條件不重複 §4 設計方案 |

### §99.2 Revision 歷程

- **v1 (2026-05-26)**：依 baton plan v4-final-r4-v6-r8 產出 C1–C5 初版
- **v3 (2026-05-26)**：配合計畫書 v11 重大流程優化改寫：
  · 插入新原子 Commit `C1.5` 對齊核心規格與自舉 `TODO.md`，並調整 Commit 總數至 6 個。
  · 在 `§6` 測試計畫中新增 `§6.1.5` C1.5 的自動化驗收與 grep 指令。
  · 於 `§8` 推薦 Commit 拆分中，補齊 C1.5 的六維度細節與 TODO 初始化自舉實作指令。

- **v2 (2026-05-26)**：依 baton plan 更新至 r10 重寫：(1) 移除 C3 `template_prompt_for_closure.md`（r9 已併入 `template_prompt_for_check.md`）；(2) CLAUDE.md §1 改為「核心規範與契約」（r10 整合）；(3) baton 歸檔指令由 `git mv` 改為 `mv + git add`（r10 安全化）；(4) GOVERNANCE_OVERVIEW.md 更新為 8 章節（含「核心規範與契約」錨點）；(5) §0.5 成果盤點數字更新（C 類 8 個模板，非 9 個）
