# CHECKOUT-GUARD 收官 git-add 白名單鐵律 plan

> 目的：從流程層面根治「收官/commit 期廣義 `git add` 掃入跨任務未追蹤檔」之混檔——立「逐檔白名單 git-add 鐵律 + commit 前 staged-set 自檢」，寫入唯一權威源 WORKFLOW_SOP §3 與執行載體 template_prompt_for_check.md。純 DOC-Refactor、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：現行收官流程的 `git add` 步驟（`template_prompt_for_check.md §133 收官自動化` + `WORKFLOW_SOP §3 收官歸檔鐵律`）**未禁止廣義 `git add .`／`-A`／`git add <目錄>`，且 commit 前無 staged 內容自檢**。FE-PERF-1 收官時，WORKFLOW-5 一批未追蹤歸檔檔因此被掃入 FE-PERF-1 C1（`60cd126`）→ 跨任務混檔（事後靠未 push 之歷史重寫才淨化）。
- **解法**：新增「收官 git-add 白名單鐵律」——(a) 收官/Run 的 `git add` **一律逐檔顯式列名**、**嚴禁** `git add .`／`git add -A`／`git add <目錄>`；(b) **commit 前必跑 staged-set 自檢**：`git diff --cached --name-only` 對照執行報告宣告之檔案清單，**多一檔／少一檔即停、不得 commit**。規範入唯一權威源 `WORKFLOW_SOP §3 強制規則`，執行步驟入 `template_prompt_for_check.md`。
- **影響**：純 `.md`——`ref/WORKFLOW_SOP.md`（§3 + §99.2）+ 三份模板 `templates/template_prompt_for_run.md`（Run §8）/ `template_prompt_for_check.md`（收官步驟 + checkout 報告 mandate）/ `template_execution.md`（§8 輕註）；**零業務代碼、零 runtime、零 schema**。
- **附帶治本**：一併消弭「checkout 輪有時未產執行報告」之制度落差（`template_execution.md` L126 已假設 Check 執行報告存在、但 `template_prompt_for_check.md` 未 mandate 產出）——見 U6。

---

## §2 目標規格

本案「最終狀態」目標規格（可 grep 檢驗）：

- **U1 — WORKFLOW_SOP §3 立鐵律**：`ref/WORKFLOW_SOP.md §3 強制規則` 新增一條「**收官 git-add 白名單鐵律**」，明文兩點：① `git add` 逐檔顯式列名、**嚴禁** `git add .`／`git add -A`／`git add <目錄>`；② **commit 前** 以 `git diff --cached --name-only` 自檢 staged 集合，須**完全等於**該 commit 宣告之檔案清單（多/少一檔即停）。§0/§99 改版觸發相容、§99.2 加 Revision。
- **U2 — 所有 git-add 命令產生點落註**：於**三份模板**之 git add 段一律加「**逐檔顯式、嚴禁 `git add .`／`-A`／`git add <目錄>`**」警語——① `templates/template_prompt_for_run.md §8`（Run 階段 commit 命令產生點）② `templates/template_prompt_for_check.md`（收官）③ `templates/template_execution.md §8`（執行報告 commit 命令段）；其中 **template_prompt_for_check 收官自動化額外新增「commit 前 staged 自檢」步驟**（貼 `git diff --cached --name-only` 對照宣告清單、不符即停之範式）。
- **U3 — 白名單來源明確**：規範明訂「宣告清單」＝各執行報告 §3 變動檔案清單 + §8 git add 清單（含 `.bak`）之聯集；跨任務未追蹤檔（他任務 baton/prompts 等）**不得**出現在 staged 集合。
- **U4 — 誠實範例錨定**：規範附一句反例錨點——FE-PERF-1 混檔事件（WF5 未追蹤歸檔被掃入 `60cd126`、以 `pre-fe-rebuild` 備份後歷史重寫淨化）作為「為何立此鐵律」之 worked anchor。
- **U5 — checkout 必產並保存執行報告**：規範明訂 checkout（收官）輪**必產** `executions/<date>_<任務編碼>_checkout_執行.md`（或 `_Check_執行.md`），內容含 **Conformance 五維度驗收結果** + **staged-set 自檢輸出**（`git diff --cached --name-only` 實貼、綁定 U1/U2）+ baton 歸檔確認 + §8 一行 commit 指令；消弭 `template_execution.md`（L126 已假設「Check 執行報告」存在）與 `template_prompt_for_check.md`（未 mandate 產出/保存）之落差，根治「checkout 輪有時未產報告」。
- **U6 — 純 DOC 無迴歸**：全案零 `.py`/`static/` 業務碼 diff（`git diff --stat` 僅命中 `ref/WORKFLOW_SOP.md` + `templates/template_prompt_for_run.md` + `templates/template_prompt_for_check.md` + `templates/template_execution.md`）；既有 pytest 基線維持。

### §2.5 候選方案（Diverse Rollout）

> 「防混檔要靠什麼強度」屬易踩過度工程/過度放任的決策，故填本節。

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有流程衝擊 / 強制力） |
|---|---|---|
| **方案 A（選定）** | 純文件鐵律（WORKFLOW_SOP §3）+ template_prompt_for_check 自檢步驟；baron/Claude 手動遵循 `git diff --cached` 對照 | 輕量、零部署、沿用既有 SOP 機制；強制力＝discretion + 自檢步驟（agent/baron 須主動跑）；與現行手動 commit 流程零摩擦 |
| 方案 B（否決·列 backlog） | git `pre-commit` hook（或延伸 WORKFLOW-5 harness hook）自動阻擋 staged 集合含白名單外檔 | 強制力最高〔不可繞過〕、呼應 WORKFLOW-5「跨出純文件用 harness enforcement」哲學；但需各環境部署 `.git/hooks`（不隨版控、跨環境成本）+ 白名單如何餵給 hook 未解；對「baron 手動 commit」場景過重 |
| 方案 C（否決） | 不立規、靠收官時警覺 | 零成本、但正是本次混檔的現狀；discretion 已被證明不足（FE-PERF-1 實例） |

- **選定理由**：方案 A 用**既有純文件 SOP 機制 + 一步自檢**即可堵住本次缺口，零部署、與手動 commit 流程相容；staged-set 自檢範式已於本次 `fe_rebuild.py` 的 `commit_exact` 實證有效。
- **否決留痕**：B（hook enforcement）強度最高但部署/白名單餵入成本高，**列 backlog**——若純文件鐵律後仍再犯，再升級（同 WORKFLOW-5 對其他守衛之演進路徑）；C（放任）＝現狀、已否決。

---

## §3 現況與證據

- **`templates/template_prompt_for_run.md`**：
  - `§8 baron 執行命令格式要求`（L116-126）：`git add <檔案 A/B>` + `.bak`（逐檔範式），但**同樣無「禁廣義 add」明文**——Run 中間 commit（C1/C2…）亦可能因圖省事 `git add .` 掃入他任務未追蹤檔（baron review 補之範圍缺口）。
- **`templates/template_prompt_for_check.md`**（216 行）：
  - `§133 收官自動化動作`：`mv` + `git add <逐檔>`（L160-173 範式已逐檔），但**無「commit 前 staged 自檢」步驟、無「禁廣義 add」明文**。
  - `§177 第三步`：只驗「baton/ 只剩 README.md」，未驗 staged 集合。
  - **未 mandate 產出/保存 checkout 執行報告**：第二步僅列「輸入」執行報告清單（C1/C2…、L54-58）與「產出 Conformance 驗收報告」（L96-121，inline），**未要求寫 `executions/…_checkout_執行.md`**。
- **`ref/WORKFLOW_SOP.md §3 強制規則`**：
  - L103 `.bak 備份鐵律`、L104 `baton/ 暫存鐵律`、L105 `收官歸檔鐵律`（「一次性 mv + git add」）——**皆未涵蓋「git add 逐檔白名單 + staged 自檢」**。
- **`templates/template_execution.md`**：
  - L47 `.bak 須入 git add`、L124 `§8 baron 執行命令`（`git add [檔案 A/B]` 逐檔）——同樣無「禁廣義 add / staged 自檢」。
  - **L126 已假設「Check 執行報告」存在**（「Check 執行報告的 §8 僅保留一行 commit 指令」）→ 與 `template_prompt_for_check.md` 未 mandate 產出之落差＝「checkout 有時沒產報告」制度根因（U5 治本）。
- **反例事件（本案動因）**：FE-PERF-1 收官，WORKFLOW-5 未追蹤歸檔檔（executions C1–C7 + plan + tasks + Tasks 提示詞）被掃入 FE-PERF-1 C1 `60cd126`；經 `pre-fe-rebuild` 備份後歷史重寫（`fe_rebuild.py` 守衛 + 逐顆 `git add --` + `commit_exact` staged 斷言）淨化為乾淨邊界。

### §3.1 grep 鋼鐵證據

```bash
$ grep -nE "git add|收官歸檔鐵律|一次性" .claude-logs/ref/WORKFLOW_SOP.md
103:- .bak 備份鐵律：… git add 清單中強制包含 …
105:- 收官歸檔鐵律：… 一次性 mv + git add 歸檔至正式目錄
# → 無「逐檔白名單 / 禁 git add . / staged 自檢」字樣（缺口）
$ grep -nE "git add .|-A|staged|diff --cached" .claude-logs/templates/template_prompt_for_check.md
# → 無命中（收官步驟無 staged 自檢、無禁廣義 add）
$ grep -nE "git add" .claude-logs/templates/template_prompt_for_run.md
124:git add <檔案 A>   125:git add <檔案 B>   126:git add .claude-logs/archive/<備份檔案>
# → Run §8 逐檔範式、但無禁廣義 add 明文（同缺口）
$ grep -n "Check 執行報告" .claude-logs/templates/template_execution.md
126:> ℹ️ Check 執行報告的 §8 僅保留以下一行 commit 指令 …
# → 假設 Check 執行報告存在，但 template_prompt_for_check 未 mandate 產出（落差）
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 純 DOC-Refactor、無跨 Phase / 無模組間 code handoff；依 `WORKFLOW_SOP §7.2` 特例顯式申請整合測試豁免（純文檔、無 code handoff），由 baron 拍板（§9 Q5）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 收官流程摩擦↑（多一步自檢） | 🟢 低 | 自檢僅一行 `git diff --cached --name-only` 目視對照；換取杜絕跨任務混檔、划算 |
| 與既有鐵律（§3 L103-105）重疊/矛盾 | 🟢 低 | 新鐵律為「git add 範圍」維度，與 .bak/baton/一次性歸檔正交、不改既有三條文字；僅新增一條 |
| 與 WORKFLOW-5 既有 hook 守衛混淆 | 🟢 低 | §99.1 重複防護明列：本案為 git-add 範圍守衛（純文件鐵律），與 WORKFLOW-5 truncation/dirty-reset hook 正交、不同層 |
| 誤傷合法多檔 commit | 🟢 低 | 白名單＝執行報告宣告清單之聯集；規範明訂來源（U3），非禁止多檔、只禁「未宣告檔混入」 |
| 過度工程（單人 repo 立硬規） | 🟡 中 | §2.5 選最輕方案 A（純文件+自檢）、hook enforcement 列 backlog 不本案做 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 100% 不動。
- [ ] **`WORKFLOW_SOP.md` §1/§2/§4–§7** 五類工作流定義 / 文書類別 / 驗證分級 / SOP 核查 / 接縫契約 — 僅允許在 §3 強制規則**新增一條鐵律** + §99.2 加 Revision。
- [ ] **`template_prompt_for_check.md`** 既有 Conformance 五維度定義、Check 減負前移（WORKFLOW-4 U5）段 — 不改，只在收官自動化動作**新增自檢步驟** + git add 段加註 + mandate checkout 報告。
- [ ] **`template_prompt_for_run.md`** 既有三防線 / TODO 自癒 / 停止指令段 — 不改，只在 §8 git add 段**加「逐檔、禁廣義 add」一行**。
- [ ] **`template_execution.md`** 既有 §1–§7 結構 — 不改，只在 §8 git add 段加同一警語（Q3）。
- [ ] **WORKFLOW-5 既有 hook 腳本**（`tools/pre_tool_guard.sh` / `dirty_reset_guard.sh` / `test_hook_guards.sh`）— 不碰（本案不做 hook）。
- [ ] `.py` / `tests/` / golden baseline — 純 DOC、零觸發。
- [ ] baton/ 暫存報告 — Run 階段嚴禁 mv/git add，唯 checkout 一次性歸檔。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| 六階段 / 收官鐵律 / §7.2 豁免 / 命名 | `ref/WORKFLOW_SOP.md §3 / §6 / §7` |
| 雙軌制 / 提示詞歸檔 / 重複防護 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §6 / §99.1` |
| 收官執行載體 | `templates/template_prompt_for_check.md` / `templates/template_execution.md` |
| staged-set 自檢範式（實證） | 本次歷史重寫 `fe_rebuild.py` 之 `commit_exact`（斷言 staged == 預期集合） |
| 反例事件 | FE-PERF-1 混檔（WF5 掃入 `60cd126`）→ `pre-fe-rebuild` 重寫淨化 |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**（證純 DOC 零業務碼衝擊）：
  ```bash
  pytest tests/ -q   # 預期維持基線 passed（唯一既有 LOG_FORMAT env flake 除外）
  ```
- **預計新增測試**：**無**（純 `.md`、無可測程式邏輯）。驗收改以 grep/wc 靜態核查（見 §8.2）。

### §8.2 手動端到端（E2E）＝文件核查（純 DOC 無前端 E2E）

1. `grep` WORKFLOW_SOP §3 → 出現「收官 git-add 白名單鐵律」條 + 「逐檔 / 禁 `git add .` / staged 自檢」關鍵字 + 「checkout 必產執行報告」條；§99.2 有新 Revision。
2. `grep` template_prompt_for_check.md → 收官自動化含「commit 前 staged 自檢」步驟 + `git diff --cached --name-only` 範式；git add 段有「逐檔、禁廣義 add」註；**含 mandate 寫 `executions/…_checkout_執行.md`**。
3. `grep` template_prompt_for_run.md §8 + template_execution.md §8 → 皆有「逐檔、禁廣義 add」警語。
4. 核對既有 Conformance 五維度定義 / WORKFLOW-4 U5 段 / §1–§7 五類定義 / 三模板既有結構**未被改動**（grep 關鍵字數不變）。
5. `git diff --stat` → 僅命中 `WORKFLOW_SOP.md` + 三模板，零 `.py`/`static/`。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 規範主體放哪？ | **WORKFLOW_SOP §3 立鐵律（唯一權威源）+ template_prompt_for_check 落執行步驟** | 鐵律唯一源在 WORKFLOW_SOP §3（與 .bak/baton 三鐵律並列）；template 為執行載體。避免規範散置。 |
| **Q2** 是否本案就做 git pre-commit hook（harness enforcement）？ | **不做、列 backlog** | §2.5 方案 A：純文件鐵律 + 自檢已堵本次缺口；hook 需各環境部署 + 白名單餵入未解、對手動 commit 過重；再犯再升級（同 WORKFLOW-5 演進）。 |
| **Q3** 是否連動 `template_execution.md §8`？ | **加一行輕註（逐檔·禁廣義 add）** | §8 是各 Run/Check commit 命令的產生點，加一行與 §3 鐵律呼應、成本極低；若 baron 傾向最小改動則列選用。 |
| **Q4** staged 自檢是「人工目視對照」還是「附常駐腳本」？ | **人工 `git diff --cached --name-only` 目視對照範式、不寫常駐腳本** | 避免 tooling 膨脹；本次 `fe_rebuild.py` 已證範式有效，收官頻率低、目視足夠；未來如上 hook（Q2 backlog）再自動化。 |
| **Q5** §7.2 跨 Phase 整合測試豁免？ | **顯式豁免** | 純 DOC-Refactor、無 code handoff；同 WORKFLOW-3/4/5、FE-PERF-1 立規者先例。 |
| **Q6** checkout 必產執行報告的形式？ | **沿用「Check 執行報告」慣例、命名 `_checkout_執行.md`（或 `_Check_執行.md`）；聚焦 Conformance 五維度 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit（非完整 Run 版 §1–§8）** | template_execution.md L126 既已為「Check 執行報告」定義輕量形式（§8 僅一行 commit）；本案只是把「必產/必存」明文化並綁入 staged 自檢，非新造格式。 |

### §9.1 定案紀錄（baron 2026-07-02 review 核准）

| OQ | 定案 | 備註 |
|---|---|---|
| Q1 | 🟢 WORKFLOW_SOP §3 立鐵律 + template 落地 | SSOT + 執行載體、防 doc-drift |
| Q2 | 🟢 不做 hook、列 backlog | 再犯再升級 |
| Q3 | 🟢 連動 template_execution.md §8 加一行 | cost≈0 雙重保險 |
| Q4 | 🟢 人工 `git diff --cached` 目視 | 免 tooling 膨脹 |
| Q5 | 🟢 §7.2 顯式豁免 | 純 DOC |
| **範圍補強** | 🟢 **納入 `template_prompt_for_run.md §8`**（baron review 補：Run 中間 commit 同缺口） | 三模板 git add 段一致落註 |
| **Q6（新增）** | 🟢 **checkout 必產並保存執行報告**（U5·治「有時沒產報告」） | 形式沿用 Check 執行報告慣例 |

**六 OQ + 範圍補強全結清、plan 規格凍結，可進階段 2（tasks）。**

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 CHECKOUT-GUARD「收官 git-add 白名單鐵律 + staged 自檢」之目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查 §9 Open Questions 並在 tasks.md 拆分時引用；階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 CHECKOUT-GUARD tasks / 執行報告 / 產出之 WORKFLOW_SOP §3 條款 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段，baron 本案明示不給 commit 建議） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 收官鐵律唯一源在 WORKFLOW_SOP §3；本案為 git-add 範圍守衛（純文件鐵律），與 WORKFLOW-5 truncation/dirty-reset **hook 守衛正交、不同層**；template 僅為執行載體、不重寫鐵律本體 |

### §99.2 Revision 歷程

- v2 (2026-07-02)：baron review——① 範圍補強：git add 落註擴及 `template_prompt_for_run.md §8`（Run 中間 commit 同缺口）+ `template_execution.md §8`（共三模板）；② 新增 **U5 checkout 必產並保存執行報告**（治「checkout 輪有時未產報告」，消弭 template_execution L126↔template_prompt_for_check 落差），原 U5→U6；③ §9 Q1-Q5 定案 + 新增 Q6（報告形式）+ §9.1 定案表；規格凍結、可進階段 2。
- v1 (2026-07-02)：初版建立——動因 FE-PERF-1 收官跨任務混檔（WF5 未追蹤歸檔被廣義 git add 掃入 `60cd126`、以 `pre-fe-rebuild` 歷史重寫淨化）；規劃立「收官 git-add 白名單鐵律（逐檔·禁 `git add .`/`-A`/`<目錄>`）+ commit 前 staged-set 自檢」入 WORKFLOW_SOP §3 + template_prompt_for_check；§2.5 三候選（純文件鐵律選定、hook enforcement 列 backlog、放任否決）；§9 五 OQ 待 baron 拍板。
