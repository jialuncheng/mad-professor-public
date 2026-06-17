# WORKFLOW-4 StraTA 原理移植進文件治理模板 — Tasks

> 本文件為 WORKFLOW-4 的 Commit 拆分清單（階段 2 產出）。
> 依據 plan：`.claude-logs/baton/2026-06-14_WORKFLOW-4_StraTA原理移植文件治理模板_plan_v1.md`（v2、U1-U6、六 OQ 全定案）。
> 含 4 個 Commit（C1 Plan 側 → C2 Execution 側 → C3 Check 側 → C4 checkout 收官）。

---

## §0 改版規則
- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （純模板加法、無新檔；各 C 執行報告暫存 baton/）|
| **修改檔案** | 5 個 | `templates/template_plan.md`（U4 §2.5 候選方案）/ `templates/template_prompt_for_plan.md`（U4 撰寫原則+結構表 + Q5 stale 校正）/ `templates/template_prompt_for_run.md`（U1 讀檔加 plan）/ `templates/template_execution.md`（U2 §1 對齊欄 + U3 §自評）/ `templates/template_prompt_for_check.md`（U5 減負前移註）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1（Plan 側 Diverse Rollout）→ C2（Execution 側 Conditioning + 自評）→ C3（Check 側減負前移）→ C4（checkout 收官）|
| **baton 歸檔** | 1 次 | C4 checkout：`mv` baton（plan_v1 + tasks + C1-C4 報告）→ `plans/`+`tasks/`+`executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：把 StraTA 提高長程任務成功率的三原理（顯式策略 conditioning / 條件化多候選探索 / 逐步雙軸自評）固化進文件治理模板;我們六階段已內建一半，補三缺口（Run 不 re-inject 策略 / 無逐 commit 自評 / 設計單線）。
- **解法**：5 模板**輕量加法**、自主拆 4 commit，依 StraTA 資料流 + 依賴序（U5 依 U3）排：
  - **C1 — Plan 側 Diverse Rollout（多候選探索）**：`template_plan` 新增選用 §2.5 候選方案 + `template_prompt_for_plan`（U4 撰寫原則/結構表同步 + Q5 stale 校正）。
  - **C2 — Execution 側 Conditioning + 雙軸自評（策略約束）**：`template_prompt_for_run`（U1 讀檔加 plan=策略 z）+ `template_execution`（U2 §1 對齊欄 + U3 §自評三問）。
  - **C3 — Check 側減負前移（信用分配）**：`template_prompt_for_check`（U5 維度三/五前移分攤註、減負非省略）。
  - **C4 — checkout 收官（驗收歸檔）**。
- **影響範圍**：100% DOC-Refactor、零業務代碼（.py/.html/.css/.js）;改模板影響後續任務（純加章節/欄位、向後相容）。
- **不可動清單**：見 §7。

---

## §2 現況

| 模板 | 現狀 | 待加 |
|---|---|---|
| `template_plan.md` | §1-§9、無「候選方案」章 | U4 §2.5 候選方案（選用）|
| `template_prompt_for_plan.md` | 撰寫原則 L68-73、結構表 L82-89（與 template_plan §4 跨Phase 不一致·stale）| U4 多候選要求 + Q5 結構表對齊 |
| `template_prompt_for_run.md` | 強制讀檔 L58-65 僅列 tasks.md | U1 加 plan.md（策略 z）|
| `template_execution.md` | §1 基準/§5 測試/§6 不可動；無對齊欄、無自評節 | U2 §1 對齊欄 + U3 §自評 |
| `template_prompt_for_check.md` | 五維度全壓 Check | U5 維度三/五前移分攤註 |

---

## §3 觀察問題

### 問題 #1：Run 不 re-inject 全局策略（U1）
- **證據**：`grep -nE "tasks.md|plan" template_prompt_for_run.md` → 讀清單僅 tasks、無 plan。
- **影響**：執行只受局部 tasks 約束、缺全局策略 z conditioning（StraTA §4.1 反例：純反應式→近視/反覆回溯）。

### 問題 #2：無逐 commit 雙軸自評（U3）
- **證據**：`template_execution.md` 無 §自評。
- **影響**：scope creep / 做白工（無關冗餘碼）靠終局 Check 才攔、倒回成本高（StraTA §4 critical self-judgment 缺位）。

---

## §4 設計方案
依 plan §2 U1-U6 落 5 模板、4 commit。C1 Plan 側（策略生成上游）→ C2 Execution 側（U5 依此）→ C3 Check 側 → C4 收官。各 commit 改前 .bak、`<!-- === [WORKFLOW-4 C? ...] === -->`（md HTML 註解）包裹新增段。

---

## §5 風險
| 風險 | 等級 | 緩解 |
|---|---|---|
| 流程膨脹 | 🟡 中 | 全輕量加法;U4 多候選條件化（高風險才觸發） |
| 改模板影響後續任務 | 🟡 中 | 純加章節/欄位、向後相容、不溯及已歸檔文件 |
| 誤動六階段骨架/Conformance 維度 | 🟢 低 | §7 鎖死：不增刪階段、不重寫維度定義 |
| 純文件零代碼 | 🟢 低 | grep 驗收 + pytest 旁證未動代碼 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
grep -n "§2.5\|候選方案\|Diverse Rollout" .claude-logs/templates/template_plan.md          # U4 章節存在
grep -n "候選\|多方案\|高風險\|farthest\|語意分散" .claude-logs/templates/template_prompt_for_plan.md  # U4 撰寫原則
grep -nE "§4 跨 Phase|§5 變動風險" .claude-logs/templates/template_prompt_for_plan.md       # Q5 結構表已對齊 template_plan 實際章
```
### §6.2 C2 驗收
```bash
grep -n "plan.md\|全局策略\|策略 z" .claude-logs/templates/template_prompt_for_run.md      # U1 讀清單含 plan
grep -n "與全局策略對齊\|conditioned\|U-N" .claude-logs/templates/template_execution.md     # U2 §1 對齊欄
grep -n "§自評\|自我審查\|推進.*U-N\|越界\|做白工" .claude-logs/templates/template_execution.md  # U3 三問（含正向軸）
```
### §6.3 C3 驗收
```bash
grep -n "前移分攤\|減負非省略\|U-coverage\|§7.2" .claude-logs/templates/template_prompt_for_check.md  # U5 註記
```
### §6.4 全套件
```bash
git diff --name-only | grep -cE '\.py$|\.html$|\.css$|\.js$'   # 期望 0（零業務代碼）
venv/bin/python -m pytest -q                                   # 期望維持基線（旁證未動代碼）
```
### §6.5 C4 驗收
```bash
grep -rn "WORKFLOW-4" .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/  # baton 歸檔
git status -s   # 歸檔後乾淨
```

---

## §7 不可動清單
- [ ] **業務代碼 / .py / .html / .css / .js / static** — 零碰（純模板文件）。
- [ ] **六階段強制觸發鏈（WORKFLOW_SOP §3）** — 不增刪階段、不改 plan→tasks→run→check 骨架。
- [ ] **Conformance 五維度定義本身（WORKFLOW_SOP §4）** — 不重寫；U5 僅在 Check 提示詞註「前移分攤·減負非省略」。
- [ ] **未列入 §0.5 的其他模板**（template_tasks / template_hotfix / template_specification / template_file_governance / template_prompt_for_tasks / _sop）— 不動。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — Plan 側 Diverse Rollout（多候選探索）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_plan.md`（新增選用 §2.5 候選方案）+ `templates/template_prompt_for_plan.md`（U4 撰寫原則/結構表 + Q5 stale 校正）;`.bak`：`.claude-logs/archive/2026-06-18_WORKFLOW-4_C1_template_plan.md.bak`、`..._template_prompt_for_plan.md.bak`（入 C1 git add）|
| **安全性** | 🟢 高 — 純文件模板改動、零 runtime |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾 / 自 .bak 還原 |
| **驗收 grep 條件** | §6.1（§2.5 候選方案存在 / prompt_for_plan 多候選原則 / 結構表已對齊）|
| **依賴關係** | 無前置（Bootstrap First：策略生成上游）|
| **具體實作細節** | 1. `cp` 兩檔 .bak。2. `template_plan.md`：於 `## §2 目標規格` 之後、`## §3` 之前插入選用 `### §2.5 候選方案（Diverse Rollout）`——說明「**僅高風險/模糊/架構級決策**列 ≥2 個語意分散（非同案變體）方案 + trade-offs〔開發難易/對既有碼衝擊/擴充性〕+ 選定理由 + 被否決案留痕〔呼應 CLAUDE.md §1.9〕;低風險明寫『單一方案、無多方案需求』」;`<!-- === [WORKFLOW-4 C1 U4] === -->` 包裹。3. `template_prompt_for_plan.md`：① 撰寫原則（L68-73 區）加一條「高風險決策須於 §2.5 列 ≥2 語意分散候選 + trade-offs、baron 擇優」;② **Q5 校正**「套用模板結構」表（L82-89）對齊 template_plan 實際章（§4 跨 Phase 接縫契約 / §5 變動風險 / §6 不可動 / §7 規格依據 / §8 驗證 / §9 OQ + 新 §2.5）;`<!-- === [WORKFLOW-4 C1 U4/Q5] === -->` 包裹。|

### C2 — Execution 側 Conditioning + 雙軸自評（策略約束）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_prompt_for_run.md`（U1 讀檔加 plan）+ `templates/template_execution.md`（U2 §1 對齊欄 + U3 §自評）;`.bak`：`..._C2_template_prompt_for_run.md.bak`、`..._C2_template_execution.md.bak`（入 C2 git add）|
| **安全性** | 🟢 高 — 純文件模板改動 |
| **可逆性** | 🟢 高 — `git revert C2` / 自 .bak |
| **驗收 grep 條件** | §6.2（run 讀清單含 plan / execution §1 對齊欄 / §自評三問含正向軸）|
| **依賴關係** | 無硬前置（與 C1 獨立、可後於 C1）|
| **具體實作細節** | 1. `cp` 兩檔 .bak。2. `template_prompt_for_run.md`：「📖 強制讀檔清單」（L58-65）在 tasks.md 上方加一列 **`<plan.md 路徑>  # 全局策略 z（StraTA conditioning re-inject）`**;`<!-- === [WORKFLOW-4 C2 U1] === -->` 包裹。3. `template_execution.md`：① `## §1 基準與完成狀態` 加欄位「**與全局策略對齊**：本 commit conditioned on `plan §2` 哪個 U-N、有無偏離」;② 新增 `## §自評（策略對齊自我審查）`（置 §6 不可動遵守 附近/之後），AI 跑完測試後對照 `git diff` 自答三問——**(a) 越界?**〔超 tasks §7 不可動/邊界〕 **(b) 無關/違規?**〔與任務無關或違 CLAUDE.md〕 **(c) 推進哪個 U-N?（正向軸）**〔答不出＝做白工/scope creep 紅旗〕;有命中→報告自 flag + 交付前自清;`<!-- === [WORKFLOW-4 C2 U2/U3] === -->` 包裹。|

### C3 — Check 側減負前移（信用分配）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_prompt_for_check.md`（U5 減負前移註）;`.bak`：`..._C3_template_prompt_for_check.md.bak`（入 C3 git add）|
| **安全性** | 🟢 高 — 純文件、僅加註記 |
| **可逆性** | 🟢 高 — `git revert C3` / 自 .bak |
| **驗收 grep 條件** | §6.3（前移分攤 / 減負非省略 / U-coverage / §7.2 命中）|
| **依賴關係** | **前置 C2**（U5 註記引用 C2 落地之 §自評〔U3〕、需其先存在）|
| **具體實作細節** | 1. `cp` .bak。2. `template_prompt_for_check.md` 加輕量註記：「**不可動清單（維度三）+ msg 完整（維度五）已由各 Run 階段 §自評（U3）前移分攤**;Check 聚焦『跨 commit 目標規格 U-coverage（總驗收）』+『§7.2 跨 Phase 整合』——**減負非省略**（前移非取消、Check 仍為最後總閘門、審計所有 commit 疊加是否 100% 實現全部 U-N）」;**不重寫 WORKFLOW_SOP §4 五維度定義**;`<!-- === [WORKFLOW-4 C3 U5] === -->` 包裹。|

### C4 — checkout 收官（驗收歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（WORKFLOW-4 → ✅ 完成表 + 索引）;baton 一次性 `mv` 歸檔（plan_v1→`plans/`、tasks→`tasks/`、C1-C4 報告→`executions/`）+ `git add` |
| **安全性** | 🟢 高 — 純文件歸檔/狀態 |
| **可逆性** | 🟢 高 — 文件操作可逆 |
| **驗收 grep 條件** | §6.5（baton 歸檔 + git status 乾淨）|
| **依賴關係** | 前置 C1/C2/C3 全 ship |
| **具體實作細節** | 1. Conformance 五維度：① 目標規格 plan §2 U1-U6 ② §6 grep 全綠 + 全套件 pytest 維持基線（零業務代碼 diff）③ 不可動（六階段骨架/Conformance 維度/contracts/業務碼零變動）④ 提示詞稽核（plan/tasks/C1-C3 run + Check）⑤ **§7.2 顯式豁免**（DOC-Refactor、無 code handoff、同 WORKFLOW-3 先例）。2. baton 一次性 mv + git add（plan/tasks/C1-C4 報告 + 各 .bak）。3. TODO 結案（active 移除 → ✅ 完成表，hash 待 baron 回填）+ §99.2/INDEX 補 Check 提示詞。4. git log hash 自癒回填。 |

---

## §9 Open Questions
無。（plan v2 §9 六 OQ 已全 🟢 baron 拍板定案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-4 原子 Commit 拆分與實作細節，作為執行期唯一指針 |
| **用途** | 供 baron 審查並交 Claude Code 按序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8（設計規格權威源為 plan v2 §2）|
| **引用方** | 後續 WORKFLOW-4 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁動業務代碼 / 推翻六階段骨架 / 重寫 Conformance 維度；僅在既有模板加章節/欄位；baton 一律 C4 才歸檔 |
| **改版觸發條件** | plan 規格變動 / baron 拍板 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務收官歸檔、經 baron 同意移 archive/ |
| **重複防護** | StraTA 原理唯一源為論文 + plan v2；本 tasks 僅定義「改哪模板哪段」、不重寫 plan 細節 |

### §99.2 Revision 歷程
- v1 (2026-06-18)：初版拆分（4 commit：C1 Plan 側 §2.5 候選方案 + prompt_for_plan〔U4+Q5〕/ C2 Execution 側 run 讀 plan〔U1〕 + execution 對齊欄+§自評〔U2/U3〕/ C3 Check 側減負前移〔U5、依 C2〕/ C4 checkout；純文件 grep 驗收、§7.2 DOC 豁免、六階段骨架不動）
