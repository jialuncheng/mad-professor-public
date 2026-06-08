# WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試 — Tasks

> 本文件為 WORKFLOW-3 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_plan_v3.md` 計畫產出，含 4 個 Commit（C1–C3 + C4 Checkout 收官）。
> **100% DOC-Refactor、零業務代碼（.py）改動。**

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （純改既有治理文件）|
| **修改檔案** | 3 個 | `ref/WORKFLOW_SOP.md`（新增 §7 接縫契約+整合測試條款 + §3 強制規則一行 + §4.2 A6 + §99 v4）/ `templates/template_plan.md`（升 plan 結構 SSOT：新增接縫契約+變動風險章 + 重編號 + Revision）/ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 改引用 template_plan + §99 v4）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1（WORKFLOW_SOP 條款）→ C2（template_plan SSOT）→ C3（framework 改引用）→ C4（Checkout 收官）|
| **baton 歸檔** | 1 次 | C4 Checkout：`mv` plan_v1/v2/v3 → `plans/` + tasks → `tasks/` + C1–C4 執行報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：RAG-ASYNC #1 接縫缺陷——plan 未凍結跨 Phase key 契約 + plan→tasks→6 run→Conformance 全是單元/grep 尺度、無整合測試 → 6 commit 全綠仍漏（C5 白做）；另查 `template_plan.md` 自身與 `framework §4.1` 八章節 doc-drift（連計畫模板都規格不一致）。
- **解法**：以 DOC-Refactor 補兩條強制條款 + 一次根治 plan 結構 drift，拆 4 commit：
  - **C1 — WORKFLOW_SOP 接縫契約與整合測試條款（接縫契約強制條款）**：新增 §7（跨 Phase 接縫契約 + worked example + 收官前整合測試 + key-changing transform）+ §3 強制規則一行 + §4.2 A6 + §99 v4。
  - **C2 — template_plan SSOT 化（plan 結構真理源升格）**：新增「跨 Phase 接縫契約」+「變動風險與相容性評估」兩章 + 重編號 + Revision。
  - **C3 — framework §4.1 改引用 template（消滅 doc-drift）**：§4.1 八章節列表改為引用 template_plan SSOT + §99 v4。
  - **C4 — Checkout 收官（一次性歸檔結案）**：Conformance grep 驗收 + baton 一次性 mv 歸檔 + TODO ✅ + hash 回填。
- **影響範圍**：100% DOC-Refactor / 零業務代碼（.py）影響 / 不溯及既往。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `ref/WORKFLOW_SOP.md` | §0–§6 + §99；§3 六階段（階段6 收官 L95）強制規則 L98-105；§4.2 進階驗證 A1-A5（L119-127）；§99.2 v3（L195）| 無「跨 Phase 接縫契約」條款；無「收官前整合測試」前置；§4.2 無 A6 整合測試項 |
| `templates/template_plan.md` | §0/§1 TL;DR/§2 目標規格/§3 現況與證據/§4 不可動/§5 規格依據/§6 驗證/§7 OQ/§99 | 無「跨 Phase 接縫契約」佔位章；無「變動風險與相容性評估」章 → 與 framework §4.1 doc-drift；未確立為 plan 結構 SSOT |
| `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` | §4.1 計畫檔結構契約自列 8 章節（L122-131，含 #5 變動風險）；§99.2 v3（L323）| §4.1 自列八章節與 template_plan drift（template 採新精煉哲學、framework 舊版）；未改為引用 template SSOT |

---

## §3 觀察問題

### 問題 #1：跨 Phase 接縫 key 契約未凍結 + 無整合測試 → 缺陷全綠出貨
- **證據**：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md §真因`——plan v2 §U3/D1 只寫「key 對位巢狀樹」、未凍結 key 身份與同基準；C5（原文 key）/C6（譯文 title）同在 `resume_pipeline.py` 內各自孤立、單元皆自洽；全程無 P2→P3→P4 串接 + 真翻譯器整合測試。
- **影響**：6 commit + C7 Conformance 五維度全綠，Chapter Summary 仍 100% 進不了 chunk、C5 白做（靜默退化）。

### 問題 #2：template_plan 與 framework §4.1 doc-drift（計畫模板自身規格不一致）
- **證據**：`framework §4.1`（L122-131）自列 8 章節含「變動風險」；`template_plan.md` 無此章、§5 為「規格依據」（採 WORKFLOW-1/2 後精煉「plan=純規格、不寫實作」哲學）。
- **影響**：兩份規格各自漂移、無單一真理源；WORKFLOW-3 自證「連計畫模板都 drift」。

---

## §4 設計方案

### §4.1 C1 — WORKFLOW_SOP 接縫契約與整合測試條款
新增頂層 `## §7 跨 Phase 接縫契約`（置於 §6 命名規則 與 §99 之間）：
- `§7.1 接縫契約`：跨 ≥2 Phase/模組 + handoff 任務，plan 必逐 handoff 列 **producer / consumer / key 精確身份 / 同基準保證**；附**填好的 worked example**（修正版 RAG-ASYNC #1）+ 反例錨點（原始「key 對位巢狀樹」不合格）。
- `§7.2 收官前跨 Phase 整合測試`：同類任務階段 6 收官前必跑「串接整條 Phase + ≥1 個會改變 key 的真實/擬真 transform」整合測試；Checkout Conformance 必驗（缺則不得 🟢、保留 plan §OQ 顯式申請豁免）。
- `§3 強制規則`末追加一行（整合測試前置）；`§4.2` 表新增 A6；`§99.1` 重複防護 + `§99.2` v3→v4。

### §4.2 C2 — template_plan SSOT 化
新增兩章並重編號（確立為 plan 結構唯一真理源）：
- `## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則「無」）`：producer/consumer/key 同基準三欄式範本 + 交叉引用 WORKFLOW_SOP §7 worked example。
- `## §5 變動風險與相容性評估`：風險/等級/緩解三欄式範本（補齊與 framework §4.1 對齊之缺章）。
- 重編號：§4 不可動→§6 / §5 規格依據→§7 / §6 驗證→§8 / §7 OQ→§9；同步 §0 改版規則（§1-§7→§1-§9）+ §99 + 加 Revision。

### §4.3 C3 — framework §4.1 改引用 template
`§4.1 計畫檔結構契約` 八章節列表改為「**plan 結構唯一真理源＝`template_plan.md`**（不再自列、消滅 drift）」+ 保留「plan=純規格不寫實作」哲學一句；§99.2 v3→v4。

### §4.4 C4 — Checkout 收官
Conformance grep 驗收（§6 全項）+ baton 一次性歸檔 + TODO ✅ + hash 回填。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| template_plan 重編號漏改 §0/§99 內部 §X 引用 | 🟡 中 | C2 §8 明列所有需同步的引用點；C2 驗收 grep `^## §` 數列校驗；C4 Conformance 複驗 |
| §7 新增致 §99 被誤判位移 | 🟢 低 | §7 為新增頂層節、§99 仍在末尾；C1 驗收 grep `^## §7\|^## §99` 並存 |
| framework §4.1 改引用後其他文件斷鏈 | 🟢 低 | §4.1 僅改「自列→引用」、章節編號 §4.1 不變；引用方（CLAUDE.md §1.1）不受影響 |
| 動態內容（hash/任務名）誤入治理文件 | 🟢 低 | 各 Commit 驗收含 A5 `grep TODO-hash\|commit-hash` 期望無命中 |
| baton 文件在非 Checkout commit 被誤搬 | 🟢 低 | §7 不可動 + 每 Commit §8 明列「不 mv baton」；僅 C4 歸檔 |

---

## §6 測試計畫

> DOC-Refactor，採 `WORKFLOW_SOP §6.1` 文件 grep 驗收，無 pytest。

### §6.1 C1 驗收（WORKFLOW_SOP 條款）
```bash
grep -n '^## §7 跨 Phase 接縫契約' .claude-logs/ref/WORKFLOW_SOP.md          # 新節存在
grep -n 'producer\|consumer\|同一基準\|worked example\|修正版' .claude-logs/ref/WORKFLOW_SOP.md
grep -n 'A6\|跨 Phase 整合測試\|key-changing\|改變.*key' .claude-logs/ref/WORKFLOW_SOP.md
grep -n '^## §0\|^## §99' .claude-logs/ref/WORKFLOW_SOP.md                   # §0/§99 結構仍在（A2）
grep -n '- v4 ' .claude-logs/ref/WORKFLOW_SOP.md                             # Revision v4
grep -n 'TODO-hash\|commit-hash' .claude-logs/ref/WORKFLOW_SOP.md            # 期望：無（A5）
```

### §6.2 C2 驗收（template_plan SSOT）
```bash
grep -n '跨 Phase 接縫契約\|變動風險與相容性評估' .claude-logs/templates/template_plan.md
grep -cn '^## §' .claude-logs/templates/template_plan.md                     # 章節數 +2（重編號後 §1-§9）
grep -n '^### §99.2 Revision\|WORKFLOW-3' .claude-logs/templates/template_plan.md
grep -n '^## §0\|^## §99' .claude-logs/templates/template_plan.md
```

### §6.3 C3 驗收（framework 改引用）
```bash
grep -n 'template_plan\|plan 結構.*真理源\|SSOT\|唯一真理源' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n '- v4 ' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
```

### §6.4 C4 Checkout 驗收
```bash
ls -la .claude-logs/plans/2026-06-08_WORKFLOW-3_*plan_v3.md                  # 歸檔到位
ls -la .claude-logs/tasks/2026-06-08_WORKFLOW-3_*tasks.md
ls -la .claude-logs/executions/2026-06-08_WORKFLOW-3_*執行.md                # C1-C4 報告
ls .claude-logs/baton/ | grep WORKFLOW-3 || echo "✅ baton 已清"
grep -c '待 baron 回填\|✅.*WORKFLOW-3' .claude-logs/TODO.md
```

---

## §7 不可動清單

明確劃定修改邊界。**以下在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：所有 `.py`（`pipeline_core.py` / `web_server.py` / `pipelines/*` / `processor/*` 等）— 100% 不動。
- [ ] **CLAUDE.md** — 本任務不改（接縫契約唯一源置 WORKFLOW_SOP §7、plan 結構唯一源置 template_plan；CLAUDE.md 引用屬另議）。
- [ ] `WORKFLOW_SOP §1/§2/§5/§6` 既有條款 / `§3` 既有六階段定義 — 不重寫（C1 僅新增 §7 + §4.2 A6 + §3 強制規則一行）。
- [ ] `framework §1–§8 既有章節`（除 §4.1 改引用）/ `§4.2 執行報告契約` — 不重寫。
- [ ] `template_plan.md` 既有章節語意（§2 目標規格「不寫實作」精煉哲學）— 保留為 SSOT 基準、不推翻（C2 僅新增 2 章 + 重編號）。
- [ ] **既有已收官任務** — 不溯及既往。
- [ ] **baton/ 文件**：C1-C3 嚴禁 `mv` / `git add` baton 文件；僅 C4 Checkout 一次性歸檔。
- [ ] **主 repo 目錄**（worktree 父目錄）— 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — WORKFLOW_SOP 接縫契約與整合測試條款（接縫契約強制條款）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/ref/WORKFLOW_SOP.md`（新增 §7 + §3 強制規則一行 + §4.2 A6 + §99.1/§99.2）+ 改前 `.bak`（archive/）。baton/ 暫存報告嚴禁列入。 |
| **安全性** | 🟢 高 — 純文件新增、零 runtime 影響、不改既有條款語意 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾 |
| **驗收 grep 條件** | 見 §6.1（§7 新節 + worked example + A6 + §0/§99 + v4 + A5 無動態內容）|
| **依賴關係** | 無前置（獨立目標）|
| **具體實作細節** | ① 改前備份 `cp ref/WORKFLOW_SOP.md archive/2026-06-08_WORKFLOW-3_C1_WORKFLOW_SOP.md.bak`。② 於 `## §6 命名規則` 章節結束、`## §99 治理規格` 之前，插入新頂層章節 `## §7 跨 Phase 接縫契約`，內含：**§7.1 接縫契約**——文字定義「凡跨 ≥2 Phase 或 ≥2 模組、且 Phase/模組間有資料 handoff（一方產一方消費）者，其 plan 必含『接縫契約』，逐 handoff 明列 producer（誰產/欄位 key 名）/ consumer（誰取/如何 match）/ key 精確身份（原文 or 譯文 or 穩定 id）/ **同基準保證**（producer 寫入與 consumer 查找為同一基準、不得各自孤立決定）」+ **填好的 worked example**（三欄表：producer＝P2 `_collect_summary_targets`〔key=原文標題 path〕／consumer＝P4 `rag_indexer._walk`〔以 summary_key=原文標題 path 查〕／同基準＝原文標題 path）+ **反例錨點**（原始 RAG-ASYNC #1「key 對位巢狀樹」屬不合格——未凍結 key 身份與同基準）；**§7.2 收官前跨 Phase 整合測試**——文字定義「同類任務於階段 6 收官（Checkout）前必跑一條整合測試：串接整條相關 Phase + **至少一個會改變傳遞物 key 的真實/擬真 transform**（如真翻譯器使譯文≠原文 key、純 mock 同 key 兩端不予承認），斷言上游產物經整條鏈後下游正確消費；Checkout Conformance 必驗其存在且通過、缺則多 Phase 任務不得判 🟢，特例（純文檔/付費 API 強依賴）得於 plan §Open Questions 顯式申請豁免、baron 拍板」。③ 於 `§3 六階段` 之「強制規則」清單（L98-105）末尾追加一行：`- 跨 Phase 整合測試前置：跨 ≥2 Phase/模組且有 handoff 之任務，收官（階段 6）前必跑 §7.2 整合測試、Checkout Conformance 必驗（詳見 §7）`。④ 於 `### §4.2 進階驗證` 表格 A5 列後追加 A6 列：`| A6 | 跨 Phase 整合測試 | 任務跨 ≥2 Phase/模組且有資料 handoff 時 | <整合測試指令，含 key-changing transform、pass；缺則申請豁免> |`，並把標題「（特定條件觸發，5 項）」改為「（特定條件觸發，6 項）」。⑤ `§99.1` 治理規格表「重複防護」欄補「跨 Phase 接縫契約唯一源在本檔 §7」；`§99.2` 新增 `- v4 (2026-06-08)：WORKFLOW-3 C1——新增 §7 跨 Phase 接縫契約 + 收官前整合測試強制條款 + §4.2 A6 + §3 強制規則整合測試前置（治本 RAG-ASYNC #1 接縫缺陷）`。⑥ 全程使用 Markdown，不含任何動態 hash/任務進度數字（A5）。⑦ **嚴禁** mv/git add baton 文件。 |

### C2 — template_plan SSOT 化（plan 結構真理源升格）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/templates/template_plan.md`（新增 2 章 + 重編號 + §0/§99 同步 + Revision）+ 改前 `.bak`。 |
| **安全性** | 🟢 高 — 純模板文件、影響未來新 plan 結構、零 runtime |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾 |
| **驗收 grep 條件** | 見 §6.2（兩新章 + 章節數 + Revision + §0/§99）|
| **依賴關係** | 無前置（與 C1 正交；C3 依賴 C2）|
| **具體實作細節** | ① 改前備份 `cp templates/template_plan.md archive/2026-06-08_WORKFLOW-3_C2_template_plan.md.bak`。② 於 `## §3 現況與證據`（含 §3.1 grep 鋼鐵證據）章節之後、原 `## §4 不可動清單` 之前，插入兩新頂層章節：`## §4 跨 Phase 接縫契約` —— 說明「跨 ≥2 Phase/模組 + handoff 任務必填、否則標『無』」+ 三欄式空範本表（| handoff | producer（誰產/key） | consumer（誰取/match） | key 精確身份 + 同基準保證 |）+ 一句「填寫規範與 worked example 見 `WORKFLOW_SOP §7`（唯一權威源）」；`## §5 變動風險與相容性評估` —— 三欄式空範本表（| 風險 | 等級（🔴/🟡/🟢） | 評估 / 緩解 |）+ 一句「對齊 framework §4.1 #5」。③ **重編號**原有後續章節：原 `## §4 不可動清單`→`## §6 不可動清單`、原 `## §5 規格依據`→`## §7 規格依據`、原 `## §6 驗證計畫`（含 §6.1/§6.2 子節）→`## §8 驗證計畫`（子節 §8.1/§8.2）、原 `## §7 Open Questions`→`## §9 Open Questions`。④ 同步 `## §0 改版規則`：「改版觸發：§1–§7 任一…」改為「§1–§9」。⑤ 同步 `## §99 治理規格`：「權威源 本檔 §1–§7」改為「§1–§9」、「改版觸發條件」同步；`§99.2 Revision` 新增 `- v? (2026-06-08)：WORKFLOW-3 C2——升格 plan 結構 SSOT，新增 §4 跨 Phase 接縫契約 + §5 變動風險與相容性評估 + 重編號 §6-§9（對齊 framework §4.1）`（若 template_plan §99.2 無版本欄則新增 Revision 段）。⑥ 驗收 `grep -c '^## §'` 確認章節數 = 原數 +2。⑦ 不含動態內容（A5）。⑧ **嚴禁** mv/git add baton。 |

### C3 — framework §4.1 改引用 template（消滅 doc-drift）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 改引用 + §99.2 v4）+ 改前 `.bak`。 |
| **安全性** | 🟢 高 — 純文件、§4.1 編號不變僅內容改「自列→引用」 |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | 見 §6.3（template_plan 引用 + SSOT + v4）|
| **依賴關係** | **依賴 C2**（framework 引用的 SSOT 須先在 template_plan 確立）|
| **具體實作細節** | ① 改前備份 `cp ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md archive/2026-06-08_WORKFLOW-3_C3_framework.md.bak`。② 將 `### 4.1 計畫檔 (_plan.md) 結構契約`（L122-131）之自列八章節（1. TL;DR … 8. 開放問題）改寫為：保留前言「計畫檔是用來向人類/自己證明你已經想透了解法。不寫程式碼，純分析。」+ 新增一句「**plan 結構之唯一真理源（SSOT）為 `.claude-logs/templates/template_plan.md`**——本節不再自列章節清單、改以該模板為準（避免 doc-drift）；模板含 TL;DR / 現況 / 目標規格 / 跨 Phase 接縫契約 / 變動風險與相容性評估 / 驗證 / 不可動 / Open Questions 等章。跨 Phase 接縫契約條款權威源見 `WORKFLOW_SOP §7`。」③ 不刪除 §4.2 執行報告契約等其他章節。④ `§99.2 Revision` 新增 `- v4 (2026-06-08)：WORKFLOW-3 C3——§4.1 計畫檔結構契約改引用 template_plan 為 plan 結構 SSOT（消滅 template↔framework doc-drift）`。⑤ 不含動態內容（A5）。⑥ **嚴禁** mv/git add baton。 |

### C4 — Checkout 收官（一次性歸檔結案）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton → `plans/`（plan_v1/v2/v3）+ `tasks/`（tasks）+ `executions/`（C1-C4 執行報告）+ `git add`；更新 `TODO.md`（WORKFLOW-3 ✅ + hash 回填）+ `prompts/INDEX.md`（狀態 ✅）。**無 .py / 無治理文件本體改動。** |
| **安全性** | 🟢 高 — 純檔案搬移 + 狀態更新 |
| **可逆性** | 🟡 中 — 歸檔搬移可由 git 還原（baton→正式目錄為 git rename）|
| **驗收 grep 條件** | 見 §6.4（歸檔到位 + baton 清空 + TODO ✅）|
| **依賴關係** | **依賴 C1+C2+C3 全部落地**（收官殿後）|
| **具體實作細節** | ① **Conformance 三維度驗收**：目標規格（plan v3 §2 U1-U5 對照 C1-C3 grep 全綠）/ tasks §6 全項 grep / 不可動清單 git 證據（`git diff --stat` 確認僅 3 治理文件 + .bak、零 .py）。**註**：本任務為 DOC-Refactor + 不跨 Phase handoff（純治理文件），依新 §7.2 / plan §8 Q2-Q3，**自身豁免整合測試**（無 code handoff、grep 驗收即足）——於執行報告明載此豁免理由。② SOP 核查欄填「DOC-Refactor 工作流、無 .py 改動、跳過（合規）」。③ **baton 一次性歸檔**：`mv baton/2026-06-08_WORKFLOW-3_*plan_v1.md baton/*plan_v2.md baton/*plan_v3.md → .claude-logs/plans/`（三版全歸檔、作 §1.9 多輪 review 軌跡）、`mv baton/2026-06-08_WORKFLOW-3_*tasks.md → .claude-logs/tasks/`、`mv baton/2026-06-08_WORKFLOW-3_*_C1_執行.md ..._C2_執行.md ..._C3_執行.md ..._C4_執行.md → .claude-logs/executions/`。④ **TODO.md**：將 WORKFLOW-3 條目自 active 移除、於 `## ✅ 已完成` 新增 `### DOC-Refactor WORKFLOW-3` 完成表（C1-C4 + Hash `待 baron 回填`）、同步索引；執行 `git log` 自癒回填全 TODO 殘留 `待 baron 回填`（有明確 commit 者）。⑤ `prompts/INDEX.md` WORKFLOW-3 狀態 🟡→✅。⑥ 產出 C4 執行報告（直寫 executions/）。⑦ msg 草稿寫 `/tmp/WORKFLOW-3_C4_msg.txt`（含 Co-Authored-By: Claude Opus 4.8 (1M context)）。⑧ 嚴禁自發 git commit/push。 |

---

## §9 Open Questions

無。（規劃層面 Open Questions 已於 plan v3 §8 結案：Q1-Q5/Q7 採推薦、Q6/Q8 定案；本 Tasks 階段不再開放。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-3 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 WORKFLOW-3 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（.py）；嚴禁跨 Commit 混合；嚴禁自動 git commit/push；C1-C3 嚴禁 mv baton |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；接縫契約條款內容在 plan/WORKFLOW_SOP §7、不在本檔重寫 |

### §99.2 Revision 歷程

- v1 (2026-06-08)：初版拆分——依 plan v3 拆 4 commit（C1 WORKFLOW_SOP 條款 / C2 template_plan SSOT / C3 framework 改引用 / C4 Checkout 收官）；100% DOC-Refactor、不預設於標準模板外加碼、各 Commit 各產執行報告暫存 baton、Checkout 一次性歸檔。
