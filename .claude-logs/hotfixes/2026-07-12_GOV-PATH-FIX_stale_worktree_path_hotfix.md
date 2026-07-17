# GOV-PATH-FIX hotfix — 治理文件殘留已刪除 worktree 路徑校正

> **警示**：本文件為 **hotfix 形式的 DOC-Refactor** 紀錄，修正 CONTEXT-1 C2 更新 CLAUDE.md §3 時漏改之 3 個下游治理檔（仍硬編已刪除 worktree `hopeful-yalow-902c50`）。
> **修復原則**：只校正 stale 路徑、對齊唯一權威源 `CLAUDE.md §3`，不改任何治理規格語意；歷史檔（prompts/executions/tasks/plans/hotfixes/archive）依 WORKFLOW_SOP §2「歷史命名不溯及既往」**不動**。
> **工作流**：DOC-Refactor（純治理文件、零業務碼）；§5 SOP 核查（logging/database）**不適用**（非後端）。
> **暫存**：本文件依指示暫存 `baton/`；治理檔實檔未於本階段改動，diff 僅記錄於本文件供 baron 落地。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **GOV-PATH-FIX-hotfix** | `待 baron 回填` | `docs(governance): 校正 3 下游治理檔殘留已刪除 worktree 路徑（對齊 CLAUDE.md §3 主 repo）` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：每次 baron/Antigravity 依 `template_prompt_for_tasks.md` 產生「Tasks 階段提示詞」，其「🏢 工作目錄硬規則」都會複製出**已刪除的 worktree 路徑** `.claude/worktrees/hopeful-yalow-902c50/` 作為「唯一合法工作目錄」，並附「嚴禁讀寫主 repo 目錄」——與現行權威源 `CLAUDE.md §3`（主 repo 就地為唯一合法工作目錄）**直接矛盾**。
- **受災範圍**：治理導航與提示詞生成——Claude Code 每次收 Tasks 提示詞都需人工判定「路徑是 stale、依 CLAUDE.md §3 主 repo 就地」（本 session SEC-XSS / SEC-HARDEN 均已如此標注）。另有 framework §9.1 與 GOVERNANCE_OVERVIEW.md 之導航連結全指向失效路徑。
- **首發訊號**（本 session 稽核）：
  ```
  $ grep -rln "hopeful-yalow-902c50" .claude-logs/templates/ .claude-logs/ref/
  .claude-logs/templates/template_prompt_for_tasks.md      # 元凶：每產一次 Tasks 提示詞複製一次
  .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md    # §9.1 硬編
  .claude-logs/ref/GOVERNANCE_OVERVIEW.md                   # 6 條 file:/// 死路徑連結
  ```

### 2. 真因診斷 (Root Cause)

- **技術細節**：`CONTEXT-1 C2`（CLAUDE.md v5，2026-07-09）將 `CLAUDE.md §3` 之「唯一合法工作目錄」由已刪除 worktree 更新為**主 repo 雙視圖**（Server / Mac OrbStack），但**未同步 3 個下游引用檔**：
  - `template_prompt_for_tasks.md:67`——**元凶**，模板硬編路徑 → 每次生成 Tasks 提示詞即再生 stale 路徑（自我複製、持續污染）。
  - `framework §9.1`（L282）——補充條款重點句硬編路徑（§9.1 本應「不重寫、只引用 CLAUDE.md §3」，卻抄了已失效的具體路徑）。
  - `GOVERNANCE_OVERVIEW.md`（L15/18/21/24/30/36）——6 條 `file:///Users/…/worktrees/hopeful-yalow-902c50/…` 絕對路徑導航連結，全失效。
- **定位程式碼**：
  - `.claude-logs/templates/template_prompt_for_tasks.md#L67`
  - `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md#L282`
  - `.claude-logs/ref/GOVERNANCE_OVERVIEW.md#L15,L18,L21,L24,L30,L36`
- **權威源（已正確、作為對齊基準）**：`CLAUDE.md:89`（§3）——
  `唯一合法工作目錄：主 repo 根目錄 ~/mad-professor-public/（Server 視圖 … ; Mac OrbStack 視圖 …）`

---

## 熱修復修法 (Minimal Hotfix)

**原則**：對齊 `CLAUDE.md §3`（唯一權威源）；引用式改為「詳見 CLAUDE.md §3、不重寫」；GOVERNANCE_OVERVIEW 導航改**相對路徑**（env-agnostic、免絕對 worktree 前綴）。

### `template_prompt_for_tasks.md` — 工作目錄硬規則對齊（L66-70）
```diff
 ### 🏢 工作目錄硬規則（必遵守）

-- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
-- **嚴禁讀寫主 repo 目錄**（worktree 父目錄）
+- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）
+- **嚴禁讀寫授權範圍外檔案**（授權範圍由各任務 plan / tasks 工作目錄條款定義）
 - **嚴禁改動業務代碼**（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`）
-- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，C5 收官後才 mv + git add 歸檔）
+- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，checkout 收官後才 mv + git add 歸檔）
```

### `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` — §9.1 重點句去硬編（L282）
```diff
 ### §9.1 工作目錄硬規則

 詳見 `CLAUDE.md §3 工作目錄硬規則`（唯一權威源、本節不重寫）。
-重點：唯一合法工作目錄 `.claude/worktrees/hopeful-yalow-902c50/`；baton/ 暫存規則；違規 baron 有權直接 revert。
+重點：唯一合法工作目錄＝主 repo 根目錄（詳見 CLAUDE.md §3、雙視圖 Server / Mac OrbStack）；baton/ 暫存規則；違規 baron 有權直接 revert。
```

### `GOVERNANCE_OVERVIEW.md` — 6 導航連結改相對路徑（L15/18/21/24/30/36）
```diff
-詳見 [WORKFLOW_SOP.md](file:///Users/…/worktrees/hopeful-yalow-902c50/.claude-logs/ref/WORKFLOW_SOP.md) 的 `## §1 五類工作流定義` 及 `## §3 六階段強制觸發鏈`。
+詳見 [WORKFLOW_SOP.md](WORKFLOW_SOP.md) 的 `## §1 五類工作流定義` 及 `## §3 六階段強制觸發鏈`。
 …（§2/§6 同法）…
-詳見 [WORKFLOW_SOP.md](file:///…/hopeful-yalow-902c50/.claude-logs/ref/WORKFLOW_SOP.md) 的 `## §2 文書類別` 及 `## §6 命名規則`。
+詳見 [WORKFLOW_SOP.md](WORKFLOW_SOP.md) 的 `## §2 文書類別` 及 `## §6 命名規則`。
-詳見 [CLAUDE.md](file:///…/hopeful-yalow-902c50/CLAUDE.md) 的 `## §3 …`。
+詳見 [CLAUDE.md](../../CLAUDE.md) 的 `## §3 …`。
-詳見 [README.md](file:///…/hopeful-yalow-902c50/.claude-logs/baton/README.md)。
+詳見 [README.md](../baton/README.md)。
-詳見 [WORKFLOW_SOP.md](file:///…/hopeful-yalow-902c50/.claude-logs/ref/WORKFLOW_SOP.md) 的 `## §5 SOP 一致性核查機制`。
+詳見 [WORKFLOW_SOP.md](WORKFLOW_SOP.md) 的 `## §5 SOP 一致性核查機制`。
-詳見 [PROJECT_PROGRESS_CONTROL_FRAMEWORK.md](file:///…/hopeful-yalow-902c50/.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md)。
+詳見 [PROJECT_PROGRESS_CONTROL_FRAMEWORK.md](PROJECT_PROGRESS_CONTROL_FRAMEWORK.md)。
```
> 相對路徑基準＝`GOVERNANCE_OVERVIEW.md` 所在 `.claude-logs/ref/`：同層 `WORKFLOW_SOP.md` / `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`；`CLAUDE.md` → `../../CLAUDE.md`；`baton/README.md` → `../baton/README.md`。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
# 純治理文件改動、不影響 runtime；pytest 不受影響（確認基線不退化即可）
$ ./venv/bin/python -m pytest tests/ -q     # 期望：715 passed 級別不變
```

### 2. 本地驗證（DOC 專項）
```bash
# (a) 3 個活躍源不再殘留死 worktree（歷史檔不在此範圍、刻意保留）
$ grep -rln "hopeful-yalow-902c50" .claude-logs/templates/ .claude-logs/ref/
（期望：空輸出）

# (b) template 對齊權威源、GOVERNANCE_OVERVIEW 相對連結可解析
$ grep -n "唯一合法工作目錄" .claude-logs/templates/template_prompt_for_tasks.md
$ grep -n "file:///" .claude-logs/ref/GOVERNANCE_OVERVIEW.md    # 期望：無死絕對路徑
```

---

## 回退與備案

```bash
git revert <GOV-PATH-FIX-hotfix Hash>     # 純文件、單一提交、完全可逆
```

---

## §5 SOP 一致性核查

**不適用**——本任務為 DOC-Refactor（純治理文件），不涉後端代碼 / logging / database；WORKFLOW_SOP §5 僅對 BE-Refactor / BE-Hotfix 強制。

---

## §7.2 跨 Phase 整合測試豁免

純文件、單一治理檔群、無跨 Phase 資料 handoff，依 WORKFLOW_SOP §7.2 顯式豁免。

---

## §8 baron 執行命令（§1.3：baron 手動執行）

```bash
# 1. 備份 3 個受災治理檔（.bak 鐵律·納入本 commit git add）
cp .claude-logs/templates/template_prompt_for_tasks.md .claude-logs/archive/2026-07-12_GOV-PATH-FIX_template_prompt_for_tasks.md.bak
cp .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md .claude-logs/archive/2026-07-12_GOV-PATH-FIX_framework.md.bak
cp .claude-logs/ref/GOVERNANCE_OVERVIEW.md .claude-logs/archive/2026-07-12_GOV-PATH-FIX_GOVERNANCE_OVERVIEW.md.bak

# 2. git add 清單（逐檔顯式，禁 `git add .` / `-A` / `<目錄>`）
git add .claude-logs/templates/template_prompt_for_tasks.md
git add .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
git add .claude-logs/ref/GOVERNANCE_OVERVIEW.md
git add .claude-logs/archive/2026-07-12_GOV-PATH-FIX_template_prompt_for_tasks.md.bak
git add .claude-logs/archive/2026-07-12_GOV-PATH-FIX_framework.md.bak
git add .claude-logs/archive/2026-07-12_GOV-PATH-FIX_GOVERNANCE_OVERVIEW.md.bak

# 3. commit message 草稿
cat > /tmp/GOV-PATH-FIX_msg.txt << 'EOF'
docs(governance): 校正 3 下游治理檔殘留已刪除 worktree 路徑

- template_prompt_for_tasks.md：工作目錄硬規則對齊 CLAUDE.md §3 主 repo（元凶·每產 Tasks 提示詞複製死路徑）
- framework §9.1：重點句去硬編 worktree、改「詳見 CLAUDE.md §3」
- GOVERNANCE_OVERVIEW.md：6 導航連結改相對路徑、去死絕對 worktree 前綴

真因：CONTEXT-1 C2 更新 CLAUDE.md §3 為主 repo 雙視圖時漏改此 3 下游引用檔；
歷史檔依 WORKFLOW_SOP §2 不溯及既往、不動。
EOF

# 4. commit 前自檢（staged 須等於上方 6 檔）
# git diff --cached --name-only

# 5. baron 手動執行
git commit -F /tmp/GOV-PATH-FIX_msg.txt
```

> 註：本 hotfix 文件（本檔）暫存 `baton/`；依 WORKFLOW_SOP §3 baton 鐵律，須待收官（Checkout）階段 `mv .claude-logs/baton/2026-07-12_GOV-PATH-FIX_..._hotfix.md .claude-logs/hotfixes/` + `git add`，不在上方文件 commit 內夾帶。

---

## Revision（文件審查軌跡）

- v1（2026-07-12）：初版——3 檔校正（template 對齊 CLAUDE.md §3 / framework §9.1 去硬編 / GOVERNANCE_OVERVIEW 相對連結）+ 真因（CONTEXT-1 C2 漏改下游）+ commit 草稿；歷史檔不溯及既往。
