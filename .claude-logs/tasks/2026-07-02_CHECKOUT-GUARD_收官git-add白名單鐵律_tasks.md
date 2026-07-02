# CHECKOUT-GUARD 收官 git-add 白名單鐵律 — Tasks

> 本文件為 CHECKOUT-GUARD 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`（內部 v2、§9 六 OQ + 範圍補強 + Q6 全定案）產出，含 3 個 Commit（C1 → C2 → checkout）。
> 工作流：DOC-Refactor。**純文件、零業務代碼、零 runtime。**

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | 無（皆改既有規範/模板；本任務過程檔為 baton 暫存） |
| **修改檔案** | 4 個 | `ref/WORKFLOW_SOP.md`（§3 立兩鐵律+§99.2 v6）/ `templates/template_prompt_for_run.md`（§8 註）/ `templates/template_prompt_for_check.md`（收官 staged 自檢+git add 註+checkout 報告 mandate）/ `templates/template_execution.md`（§8 註） |
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md`（本階段即時 🟡 WIP、checkout 轉 ✅）/ `prompts/INDEX.md`（已於歸檔同步） |
| **Commits** | 3 個 | C1 → C2 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` plan_v1 → `plans/` + tasks → `tasks/` + C1/C2 執行報告 → `executions/` + `git add`（4 份 .bak 於 C1/C2 各自 commit 就地 git add、不在此列） |

---

## §1 TL;DR（概要）

- **挑戰**：收官/commit 期的 `git add` 步驟（WORKFLOW_SOP §3、三份模板 §8）**未禁廣義 `git add`、無 commit 前 staged 自檢**（FE-PERF-1 混檔根因）；且 checkout 輪**未 mandate 產出/保存執行報告**（template_execution L126 已假設存在、template_prompt_for_check 未要求）。
- **解法**：拆 3 原子 commit——
  - **C1 — Rule Authoring（WORKFLOW_SOP §3 立收官鐵律）**：新增「收官 git-add 白名單鐵律」+「checkout 執行報告鐵律」+ §99.2 v6。
  - **C2 — Template Propagation（三模板落地）**：run/check/execution §8 加「逐檔·禁廣義 add」+ check 收官新增「commit 前 staged 自檢」步驟 + check mandate 產出 `_checkout_執行.md`。
  - **checkout — 成果收官歸檔（成果歸檔與移出暫存）**：Conformance 驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。
- **影響範圍**：100% DOC-Refactor / 零業務代碼 / 零 runtime / 零 golden。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `ref/WORKFLOW_SOP.md §3` | L103-105 三鐵律（.bak/baton/一次性歸檔） | 無「git-add 逐檔白名單 + staged 自檢」、無「checkout 必產報告」 |
| `templates/template_prompt_for_run.md §8`（L116-126） | `git add <逐檔>` 範式 | 無「禁廣義 add」明文 |
| `templates/template_prompt_for_check.md`（216 行） | 收官 mv+git add 逐檔（L160-173）、驗 baton 乾淨（L177） | 無 commit 前 staged 自檢、無禁廣義 add、未 mandate 產 checkout 報告 |
| `templates/template_execution.md`（§8 L124 / L126） | §8 逐檔 git add；L126 假設「Check 執行報告」存在 | §8 無禁廣義 add；與 check 模板未 mandate 產出之落差 |

---

## §3 觀察問題

### 問題 #1：廣義 git add 掃入跨任務未追蹤檔
- **證據**：`file:///.claude-logs/ref/WORKFLOW_SOP.md#L105`（收官歸檔鐵律未限 add 範圍）；FE-PERF-1 混檔實例（WF5 未追蹤歸檔掃入 `60cd126`、`pre-fe-rebuild` 重寫淨化）。
- **影響**：commit 邊界跨任務污染，需歷史重寫善後。

### 問題 #2：checkout 輪未 mandate 產出執行報告
- **證據**：`template_execution.md#L126` 假設 Check 執行報告存在，但 `template_prompt_for_check.md` 第二步只列輸入報告清單（L54-58）+ inline Conformance 報告（L96-121）、未要求寫 `executions/…_checkout_執行.md`。
- **影響**：checkout 收官結果常僅存於對話、未落地版控，審計軌跡缺失。

---

## §4 設計方案

### §4.1 C1 — Rule Authoring（WORKFLOW_SOP §3 立收官鐵律）
`ref/WORKFLOW_SOP.md §3 強制規則`，於既有三鐵律（.bak/baton/一次性歸檔）後**新增兩條**：
- **收官 git-add 白名單鐵律**：`git add` 一律逐檔顯式列名，**嚴禁** `git add .`／`git add -A`／`git add <目錄>`；**commit 前**必以 `git diff --cached --name-only` 自檢 staged 集合，須**完全等於**該 commit 宣告清單（＝各執行報告 §3 變動檔 + §8 git add 清單〔含 .bak〕之聯集），**多/少一檔即停、不得 commit**；跨任務未追蹤檔不得混入。（反例錨：FE-PERF-1 混檔 → `pre-fe-rebuild` 重寫淨化。）
- **checkout 執行報告鐵律**：checkout 輪**必產並保存** `executions/<date>_<任務編碼>_checkout_執行.md`，含 Conformance 五維度驗收結果 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit 指令。
- §99.2 加 Revision v6。**§1/§2/§4–§7 本體不動**。

### §4.2 C2 — Template Propagation（三模板落地）
- `template_prompt_for_run.md §8`：git add 段加一行「**逐檔顯式、禁 `git add .`／`-A`／`<目錄>`**」。
- `template_execution.md §8`：git add 段加同一行警語。
- `template_prompt_for_check.md`：① 收官自動化動作**新增「commit 前 staged 自檢」步驟**（貼 `git diff --cached --name-only` 對照宣告清單、不符即停）；② mv+git add 段加「逐檔、禁廣義 add」；③ **新增 mandate**：收官須產出並保存 `executions/<date>_<任務>_checkout_執行.md`（形式沿用 Check 執行報告輕量慣例·Q6）。

### §4.3 checkout — 成果收官歸檔
Conformance 驗收（U1-U6 / §6 grep / 不可動）+ §7.2 純 DOC 顯式豁免 + baton 一次性歸檔（plan→plans/、tasks→tasks/、C1/C2 執行報告→executions/、+ git add）+ TODO 結案（🟡→✅、完成表 + 索引）+ hash 自癒。
> 註：本任務 checkout 依本提示詞「checkout 階段不另產執行報告」之當前流程執行；U5「checkout 必產報告」鐵律於本案 C1/C2 落地後，**自下一個任務起生效**（本案為立規者、不溯及自身 checkout）。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 誤動 WORKFLOW_SOP §1–§7 本體 | 🟢 低 | C1 只在 §3 新增兩條 + §99.2；§6.1 grep 驗五類定義字數不變 |
| 誤動三模板既有結構 | 🟢 低 | C2 只在 §8/收官段新增；§6.2 grep 驗既有段落錨點仍在 |
| 與 WORKFLOW-5 hook 守衛混淆 | 🟢 低 | plan §99.1 已明列正交（git-add 範圍 vs truncation/dirty-reset）；tasks 不重述 |
| checkout 報告鐵律溯及自身致悖論 | 🟢 低 | §4.3 明訂本案立規者不溯及、自下一任務生效 |
| baton 過程檔提前 git add | 🟢 低 | §8 各 commit 影響範圍明列 baton 報告不入 git；唯 checkout 一次性歸檔 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
F=.claude-logs/ref/WORKFLOW_SOP.md
grep -nE "收官 git-add 白名單鐵律|逐檔|git add \.|git diff --cached" "$F"   # 期望：新鐵律 + 禁廣義 + 自檢命中
grep -n "checkout.*必產.*執行報告\|checkout 執行報告鐵律" "$F"              # 期望：checkout 報告鐵律命中
grep -n "v6 (2026-07-02)" "$F"                                             # 期望：§99.2 v6
grep -cE "^### §1\.[1-5]" "$F"                                             # 期望：=5（五類定義未動）
```

### §6.2 C2 驗收
```bash
grep -nE "逐檔|git add \.|-A|目錄" .claude-logs/templates/template_prompt_for_run.md      # run §8 警語
grep -nE "逐檔|git add \.|-A|目錄" .claude-logs/templates/template_execution.md           # execution §8 警語
grep -nE "git diff --cached --name-only|staged 自檢" .claude-logs/templates/template_prompt_for_check.md  # check 自檢步驟
grep -n "_checkout_執行.md\|checkout.*執行報告" .claude-logs/templates/template_prompt_for_check.md        # check mandate 報告
# 既有結構未動抽驗
grep -c "Conformance 驗收流程" .claude-logs/templates/template_prompt_for_check.md         # 期望：維持既有
grep -c "三個防線\|三防線" .claude-logs/templates/template_prompt_for_run.md               # 期望：維持既有
```

### §6.3 checkout 驗收
```bash
git diff --stat   # 期望：僅 WORKFLOW_SOP.md + 3 模板 + 4 .bak + 歸檔 plans//tasks//executions/；零 .py/static
ls .claude-logs/plans/2026-07-02_CHECKOUT-GUARD*  .claude-logs/tasks/2026-07-02_CHECKOUT-GUARD*  .claude-logs/executions/2026-07-02_CHECKOUT-GUARD*
grep -n "CHECKOUT-GUARD" .claude-logs/TODO.md     # 期望：✅ 完成表 + 索引、active 已移除
pytest tests/ -q                                  # 期望：基線 passed（LOG_FORMAT env flake 除外）
```

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 100% 不動。
- [ ] **`WORKFLOW_SOP.md` §1/§2/§4–§7**（五類定義 / 文書類別 / 驗證分級 / SOP 核查 / 接縫契約）— 僅允許 §3 新增兩鐵律 + §99.2 加 Revision。
- [ ] **三模板既有結構**：template_prompt_for_run 三防線/TODO 自癒/停止段、template_prompt_for_check Conformance 五維度定義/WORKFLOW-4 U5 減負段、template_execution §1–§7 — 僅允許 §8/收官段新增註與步驟。
- [ ] **WORKFLOW-5 hook 腳本**（`tools/pre_tool_guard.sh` / `dirty_reset_guard.sh` / `test_hook_guards.sh`）— 不碰（本案不做 hook）。
- [ ] **主 repo 目錄業務碼 / `.py` / `tests/` / golden** — 純 DOC 零觸發。
- [ ] **baton 暫存報告** — Run 嚴禁 mv/git add，唯 checkout 一次性歸檔。

---

## §8 推薦 Commit 拆分

### C1 — Rule Authoring（WORKFLOW_SOP §3 立收官鐵律）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/ref/WORKFLOW_SOP.md`（§3 新增兩鐵律 + §99.2 v6）+ 備份 `.claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak`。〔另產 `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_Rule_C1_執行.md`、**暫存 baton、不入本 commit git 追蹤**〕 |
| **安全性** | 🟢 高 — 純新增兩條規則 + Revision、五類定義本體零改。 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；.bak 可 `git show` 追溯。 |
| **驗收 grep 條件** | 見 §6.1。 |
| **依賴關係** | 無前置。 |
| **具體實作細節** | ① 改動前 `cp` 備份 WORKFLOW_SOP.md → archive/`..._C1_WORKFLOW_SOP.md.bak`。② §3 強制規則於「收官歸檔鐵律」條之後新增：**（a）收官 git-add 白名單鐵律**——`git add` 逐檔顯式、嚴禁 `git add .`／`-A`／`<目錄>`；commit 前以 `git diff --cached --name-only` 自檢 staged 集合＝該 commit 宣告清單（各執行報告 §3+§8 聯集），多/少一檔即停；跨任務未追蹤檔不得混入；反例錨 FE-PERF-1 混檔→`pre-fe-rebuild` 重寫。**（b）checkout 執行報告鐵律**——checkout 輪必產並保存 `executions/<date>_<任務>_checkout_執行.md`（Conformance 五維度 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit）。③ §99.2 頂部加 `v6 (2026-07-02)：CHECKOUT-GUARD C1——§3 新增收官 git-add 白名單鐵律 + checkout 執行報告鐵律（治 FE-PERF-1 混檔 + checkout 漏產報告；五類定義/命名/§7 零改）`。④ 嚴禁改 §1/§2/§4–§7 任何文字。 |

### C2 — Template Propagation（三模板落地）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `templates/template_prompt_for_run.md` + `templates/template_prompt_for_check.md` + `templates/template_execution.md` + 三份對應 `.bak`（archive/）。〔另產 `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_Template_C2_執行.md`、**暫存 baton、不入 git**〕 |
| **安全性** | 🟢 高 — 純模板文字新增、零 runtime。 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾；3 .bak 可追溯。 |
| **驗收 grep 條件** | 見 §6.2。 |
| **依賴關係** | 前置 C1（模板落地引用 §3 鐵律、須先立）。 |
| **具體實作細節** | ① 三檔改動前各 `cp` 備份 → archive/`2026-07-02_CHECKOUT-GUARD_C2_<檔名>.bak`。② `template_prompt_for_run.md §8 baron 執行命令格式要求`（L116-126）git add 段前/後加一行「⚠️ 逐檔顯式列名，禁 `git add .`／`git add -A`／`git add <目錄>`（防掃入他任務未追蹤檔·WORKFLOW_SOP §3 收官 git-add 白名單鐵律）」。③ `template_execution.md §8`（L124 git add 清單處）加同一行警語。④ `template_prompt_for_check.md`：（a）「🗃️ 收官自動化動作」在 mv+git add 之後、commit 之前，新增一步「**commit 前 staged 自檢**」——`git diff --cached --name-only` 對照本任務宣告清單、**不符即停不 commit**；（b）mv+git add 段加「逐檔、禁廣義 add」註；（c）新增 mandate 段「**收官須產出並保存 `executions/<date>_<任務>_checkout_執行.md`**（Conformance 五維度 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit；形式沿用 Check 執行報告輕量慣例）」。⑤ 嚴禁改三模板既有 Conformance 五維度定義/三防線/§1–§7 結構。 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`+`git add`：`baton/…_plan_v1.md`→`plans/`、`baton/…_tasks.md`→`tasks/`、`baton/…_Rule_C1_執行.md`+`…_Template_C2_執行.md`→`executions/`；修改 `TODO.md`。〔C1 WORKFLOW_SOP+.bak、C2 三模板+3 .bak 已於各自 commit 版控、不在此重列〕 |
| **安全性** | 🟢 高 — 純文件搬移 + TODO 更新。 |
| **可逆性** | 🟢 高 — 歸檔為 `mv` 可反向；TODO `git revert` 可回滾。 |
| **驗收 grep 條件** | 見 §6.3。 |
| **依賴關係** | 前置 C1 + C2 全部 ship。 |
| **具體實作細節** | ① Conformance 驗收：目標規格 U1-U6 逐項核（引 C1/C2 §6 grep）；不可動清單逐項打勾（git diff 證零業務碼、五類定義/三模板結構未動）；提示詞稽核（plan/Tasks/C1/C2/checkout 提示詞入 git）。② **§7.2 顯式豁免**：純 DOC-Refactor、無 code handoff（同 WORKFLOW-3/4/5、FE-PERF-1 立規者先例）、checkout 報告明載。③ **git add 逐檔**（dogfood 新鐵律：即使鐵律自下一任務生效，本 checkout 亦逐檔 add、禁廣義 add、commit 前 `git diff --cached --name-only` 自檢）。④ baton 一次性歸檔（上列 mv + git add）。⑤ TODO 結案：active 移除、頂部新增 `### DOC-Refactor CHECKOUT-GUARD …` ✅ 完成表（C1/C2/checkout + hash）、同步索引。⑥ hash 自癒：回填各 commit 前 7 碼。⑦ 本 checkout 依當前流程不另產 `_執行.md`（U5 自下一任務生效）。 |

---

## §9 Open Questions

無。（plan v2 §9 六 OQ + 範圍補強 + Q6 已於審核中全數 🟢 定案，見 plan §9.1。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 CHECKOUT-GUARD 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 CHECKOUT-GUARD executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混不同優先級文件；嚴禁自動 git commit / push；baton 報告唯 checkout 歸檔 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計脈絡引 plan、全局硬規則引 CLAUDE.md/WORKFLOW_SOP |

### §99.2 Revision 歷程

- v1 (2026-07-02)：初版拆分——依 plan v2 拆 3 commit〔C1 WORKFLOW_SOP §3 立收官 git-add 白名單鐵律 + checkout 執行報告鐵律 + §99.2 v6 / C2 三模板〔run/check/execution §8 git add 註 + check 收官 staged 自檢步驟 + check mandate checkout 報告〕 / checkout 收官〕；純 DOC-Refactor、§7.2 顯式豁免、同步 TODO 🟡 WIP。
