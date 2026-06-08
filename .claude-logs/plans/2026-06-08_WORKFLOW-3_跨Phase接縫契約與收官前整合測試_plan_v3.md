# WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試 plan v3

> 定義流程治理改版：於 `WORKFLOW_SOP.md` 新增兩條強制條款——①「跨 Phase 接縫契約」（plan 必凍結每個跨 Phase/模組 handoff 的 producer／consumer／key 同基準、**附填好的範例**）②「收官前跨 Phase 整合測試」（多 Phase 任務 Checkout 前必跑串接整合測試、Conformance 必驗）——並**確立 `template_plan.md` 為「plan 結構」唯一真理源（SSOT）、`framework §4.1` 改為引用 template（根治既存 doc-drift）**，同步 `§4.2 A6`。源於 RAG-ASYNC #1 接縫缺陷（plan 未凍結 key 契約 + 全程無整合測試 → 6 commit + Conformance 五維度全綠仍漏）之治本。本 plan 為純規格定義、不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§8 任一規格條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：RAG-ASYNC #1——P2 產 `section_summaries` 以原文標題 path 為 key、P3 `rag_sections` 帶譯後 title、P4 以譯後 title 查 → MISS → C5 整個 commit 白做。**根因＝流程兩個結構性盲點**：① plan 只寫「key 對位巢狀樹」、**未凍結跨 Phase 接縫之 key 契約**；② plan→tasks→6 run→Checkout Conformance **每關都是單元/grep 尺度、無一條跨 Phase 串接測試**——各 commit 孤立正確 + 單元全綠，接縫斷裂沒任何 gate 照得出，帶缺陷全綠結案。另查得 **`template_plan.md` 自身與 `framework §4.1` 八章節 doc-drift**（template 為 WORKFLOW-1/2 後精煉版、framework 為舊版）——WORKFLOW-3 自證「連計畫模板都規格不一致」。
- **解法**：以 DOC-Refactor 補 `WORKFLOW_SOP.md` 兩條**強制條款**（① 跨 Phase 接縫契約·附 worked example；② 收官前跨 Phase 整合測試·含 key-changing transform），同步 `§4.2 A6`；並**一次根治 plan 結構 drift**——**確立 `template_plan.md` 為 plan 結構 SSOT**（加「跨 Phase 接縫契約 + 變動風險」章），`framework §4.1` 改為**引用 template_plan**（不再自列會 drift 的八章），以同一「唯一源 + 引用」原則永久消滅模板/框架不同步。
- **影響**：`WORKFLOW_SOP.md`（新增 §7 條款 + worked example + §4.2 A6 + §99.2 v3→v4）、`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 改為引用 template_plan + §99.2 v3→v4）、`template_plan.md`（確立為 plan 結構 SSOT：新增接縫契約 + 變動風險章、補齊與 framework 對齊 + 加 Revision）；**100% DOC-Refactor、零業務代碼**；不溯及既往。
- **不可動清單**：見 §5。

---

## §2 目標規格

> 「最終狀態」目標,可量化檢驗;不含 commit 拆分（屬 tasks 階段）。

### U1. WORKFLOW_SOP 新增「跨 Phase 接縫契約」強制條款（附 worked example）
- `WORKFLOW_SOP.md` 新增章節（建議 `§7 跨 Phase 接縫契約`），定義：**凡任務跨 ≥2 Phase 或 ≥2 模組、且有資料 handoff 者，plan 必含「接縫契約」**，逐 handoff 列 **producer／consumer／key 精確身份／同基準保證**（producer 寫入與 consumer 查找之 key 為同一基準、不得各自孤立決定）。
- **必附一份「填好的接縫契約範例」**（worked example，以**修正版 RAG-ASYNC #1** 為例：producer=P2 `_collect_summary_targets`〔key=原文標題 path〕／consumer=P4 `rag_indexer._walk`〔以 `summary_key`=原文標題 path 查〕／同基準=原文標題 path），**降低撰寫摩擦、提高合規**（重評「認知負荷」之 do-now 處置）。
- 附**反例錨點**（原始 #1：「key 對位巢狀樹」屬不合格——未凍結 key 身份與同基準）。

### U2. WORKFLOW_SOP 新增「收官前跨 Phase 整合測試」強制條款
- 同類任務（跨 ≥2 Phase/模組 + handoff）於**階段 6 收官（Checkout）前必跑一條跨 Phase 整合測試**：**串接整條相關 Phase/模組 + 至少一個會改變傳遞物 key 的真實/擬真 transform**（如真翻譯器使譯文≠原文 key），斷言「上游產物經整條鏈後下游正確消費」。
- **Checkout Conformance 必驗**：驗收維度新增「跨 Phase 整合測試存在且通過」；缺則多 Phase 任務不得判 🟢（顯式豁免見 §8 Q3）。

### U3. §4.2 進階驗證新增 A6
- `WORKFLOW_SOP.md §4.2 進階驗證` 表新增：`A6 | 跨 Phase 整合測試 | 任務跨 ≥2 Phase/模組且有資料 handoff 時 | <整合測試指令，含 key-changing transform、pass；缺則申請豁免>`（觸發條件採事件語法「…時」、與 A1-A5「CLAUDE.md 修改時」等體例 100% 對位）。

### U4. 確立 template_plan 為 plan 結構 SSOT、framework §4.1 改引用（根治 drift）
- **`template_plan.md` 確立為「plan 結構」唯一真理源（SSOT）**：
  - 新增「**跨 Phase 接縫契約**」章節（producer/consumer/key 同基準三欄式範本 + worked example 連結 + 「不跨 Phase 標『無』」）；
  - 新增「**變動風險與相容性評估**」章節（補齊與 framework §4.1 對齊之缺章）；
  - template 加 Revision 欄/紀錄。
- **`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 計畫檔結構契約` 改為「引用 `template_plan.md` 為 plan 結構 SSOT」**（不再自列八章節、消滅 template↔framework drift），保留「plan 為純規格、不寫實作」之精煉哲學（template 版為準）。
- **採同「唯一源 + 引用」原則**（與 §7 接縫契約一致）：plan 結構唯一源在 `template_plan.md`、framework 引用。

### U5. 不溯及既往 + Revision 版本精確化
- 對齊 `WORKFLOW_SOP §2`「歷史不溯及既往」：條款**只對生效後新任務強制**；**生效時點＝落地 commit、進行中分支以「下一個 Checkout」為界**。
- 落地版本：`WORKFLOW_SOP.md §99.2` **v3→v4**、`framework §99.2` **v3→v4**、`template_plan.md` 加 Revision；`WORKFLOW_SOP §99.1` 約束/重複防護同步（接縫契約唯一源在 WORKFLOW_SOP；plan 結構唯一源在 template_plan）。

---

## §3 現況與證據

- **`WORKFLOW_SOP.md`**：`§3 六階段 L87-`（階段 5 L94／階段 6 L95，**無收官前整合測試前置**）；`§4.2 進階驗證 L119-127`（A1-A5、**無 A6 整合測試項**、單元尺度）；`§99.2` 現 v3。
- **`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 L121-131`**：自列 8 必備章節（含 #4 設計方案 / #5 變動風險）；`§99.2` 現 v3。
- **`template_plan.md`**：章節 §1 TL;DR/§2 **目標規格**(明寫「不可寫實作細節」)/§3 現況/§4 不可動/§5 **規格依據**/§6 驗證/§7 OQ——**與 framework §4.1 八章節 doc-drift**（template 無「變動風險/設計方案」獨立章、§5 為規格依據；template 採「plan=純目標規格、不寫實作」精煉哲學，framework 採舊版「plan 含設計方案」）→ **二者為「誰是 plan 結構真理源」之衝突**；WORKFLOW-3 以 template（較新精煉版）為 SSOT 根治。
- **反例證據（RAG-ASYNC #1）**：plan v2 §U3/D1「key 對位巢狀樹」未凍結 key 身份；C5（原文 tiles key）vs C6（譯文 title）**同在 `resume_pipeline.py` 內各自孤立**（→ 觸發判準必以 handoff、非跨目錄）；6 commit 單元 + C7 Conformance 五維度全綠仍漏（`RAG-ASYNC-HOTFIX-1_hotfix.md §真因`；其修正版接縫契約即 U1 worked example 取材）。

### §3.1 grep 鋼鐵證據
```bash
grep -n '階段 6：收官\|### §4.2 進階驗證\|^| A[1-5] ' .claude-logs/ref/WORKFLOW_SOP.md
grep -n '設計方案\|變動風險與相容性\|計畫檔結構契約' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n '## §2 目標規格\|## §5 規格依據\|不可寫實作細節\|變動風險' .claude-logs/templates/template_plan.md  # 證 template↔framework drift
grep -n '- v3 ' .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md       # 現 v3 → 落地 v4
```

---

## §4 變動風險與相容性評估

> 依「對專案有幫助就做、不拖延」原則重評：**2 項升級為現在做、2 項維持限縮（做更多會害或無益、非拖延）**。

| 風險 | 等級 | 重評處置（do-now-if-helps） |
|---|---|---|
| **template ↔ framework drift** | 🟡 中 | 🟢 **現在做**：v2 原「只補佔位 + WORKFLOW-4 候選」屬拖延；改 **template=SSOT、framework 引用**一次根治、on-theme、規模小（U4）。**刪 WORKFLOW-4 候選**。 |
| **認知負荷↑**（每跨 Phase 任務多寫接縫契約 + 整合測試） | 🟡 中 | 🟢 **現在做**：v2 僅「空佔位」仍要從零寫；改**附「填好的接縫契約範例」(修正版 #1)** 入 SOP §7 + template（U1），降摩擦提合規、成本低。觸發限 handoff（Q2）+ 豁免（Q3）續用。 |
| **進行中分支相容** | 🟡 中 | ⏸ **維持邊界**：唯一在途多 Phase 工作＝RAG-ASYNC hotfixes，且 **HOTFIX-1 doc 已含接縫整合測試**（已前瞻合規）；稽核無新事、「做更多」=0 工不幫助。生效＝落地 commit、以「下一個 Checkout」為界。 |
| **硬 gate 卡死特例**（純文檔/付費 API 強依賴） | 🟢 低 | ⏸ **維持豁免**：移除豁免會卡死合法特例＝**有害**；現已是「plan 顯式申請 + baron 核准」強式（Q3）、非拖延。 |
| **擬真 transform 撰寫成本** | 🟢 低 | 多數用極輕量 stub（如 #1 hotfix `FakeTr` 加 `ZH::` 前綴即足）；SOP 僅要求「key 會變」、不要求真 API；範式入 A6。 |
| **既有條款相容** | 🟢 低 | 純**新增**（§7 / A6 / template 章 / framework 改引用），不改既有條款語意（§5 不可動）；§99.1 重複防護宣告唯一源。 |

---

## §5 不可動清單

- [ ] `WORKFLOW_SOP.md §1/§2/§5/§6` 既有條款 / `§3 六階段` 既有六階段定義 — 不重寫（僅新增 §7 + §4.2 A6 + 收官前整合測試前置）。
- [ ] `framework §1–§8 既有章節`（除 §4.1 改為引用 template）/ `§4.2 執行報告契約` — 不重寫。
- [ ] `template_plan.md` 既有章節語意（§2 目標規格「不寫實作」精煉哲學） — **保留為 SSOT 基準、不推翻**（僅新增接縫契約 + 變動風險章）。
- [ ] **既有已收官任務** — 不溯及既往、不回溯補測試（§U5）。
- [ ] 任何**業務代碼**（`.py`）— 100% 不動（純治理文件）。
- [ ] `CLAUDE.md` — 本任務不改（接縫契約唯一源置 WORKFLOW_SOP；plan 結構唯一源置 template_plan）。
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫（CLAUDE.md §3）。

---

## §6 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| RAG-ASYNC #1 接縫缺陷（治本動因 + 反例 + U1 worked example 取材） | **現位於 `.claude-logs/baton/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md`**（HOTFIX-1 尚未 Run/Checkout、暫存 baton/；收官後物理移入 `.claude-logs/hotfixes/`）；引 §真因/§修法 |
| 待改：工作流規範（六階段 / 驗證分級 / 治理） | `ref/WORKFLOW_SOP.md`（§3 / §4 / §99）|
| 待改：計畫檔結構契約（§4.1 改為引用 template） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 / §99）|
| 待改：plan 結構 SSOT（接縫契約 + 變動風險章 + 對齊） | `templates/template_plan.md` |
| 治理 .md 改版規格（§0/§99、不溯及、Revision）/ 進階驗證 A2/A5 | `ref/WORKFLOW_SOP.md §0/§2/§4.2/§99` + `framework §0/§99` |
| 專案進度管控框架（雙軌、不可動、Open Questions） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §7 驗證計畫

> DOC-Refactor，採 `WORKFLOW_SOP §6.1` 文件驗證清單（無 pytest）。

### §7.1 文件自動化驗證
```bash
# U1：接縫契約條款 + worked example
grep -n '跨 Phase 接縫契約\|同一基準\|producer\|consumer\|範例\|worked' .claude-logs/ref/WORKFLOW_SOP.md
# U2/U3：收官前整合測試 + A6
grep -n 'A6\|跨 Phase 整合測試\|改變.*key\|key-changing' .claude-logs/ref/WORKFLOW_SOP.md
# U4：template SSOT（接縫契約 + 變動風險章）+ framework 改引用 template
grep -n '跨 Phase 接縫契約\|變動風險與相容性評估' .claude-logs/templates/template_plan.md
grep -n 'template_plan\|plan 結構.*真理源\|SSOT' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
# U5：v4 + 治理結構（A2/A5）
grep -n '- v4 ' .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n 'TODO-hash\|commit-hash' .claude-logs/ref/WORKFLOW_SOP.md   # 期望：無
```

### §7.2 手動驗證流程
1. 取一個「跨 Phase 假任務」對照 §7 + template 接縫契約章 + worked example：能否逐 handoff 填出 producer/consumer/key 同基準。
2. RAG-ASYNC #1 反例回測：依新條款，C5/C6 key 不同基準會在接縫契約章被擋、整合測試在 Checkout 前照出。
3. 確認 template=SSOT、framework §4.1 引用 template（無重複八章）；既有已收官任務不溯及。

---

## §8 Open Questions

> v3 已依「對專案有幫助就做」收斂：Q6/Q8 定案、WORKFLOW-4 候選刪除。

| 開放問題 | 推薦/定案 | 理由 |
|---|---|---|
| **Q1**：接縫契約條款放哪？ | **主體置 `WORKFLOW_SOP §7`（唯一源）**；framework/template 引用 §7 | 唯一源 + 引用防重複 |
| **Q2**：「跨 Phase」觸發判準？ | **跨 ≥2 Phase/模組 + 有資料 handoff**；單檔純邏輯不觸發 | #1 producer/consumer 同檔 → 必以 handoff、非跨目錄 |
| **Q3**：硬 gate 還是建議？ | **硬 gate + plan 顯式申請豁免（baron 核准）** | 軟性會被略過；豁免防卡死特例 |
| **Q4**：整合測試最小定義？ | **串接整條 Phase + ≥1 個會改 key 的真實/擬真 transform**；純 mock 同 key 不認 | 唯有 key-changing transform 照得出接縫 |
| **Q5**：溯及既往？ | **不溯及**；生效＝落地 commit、進行中以下一 Checkout 為界 | 對齊 §2 歷史不溯及、避免回溯爆炸 |
| **Q6**：CLAUDE.md / template_plan？ | **【定案】不動 CLAUDE.md；template_plan 升格 SSOT**（接縫契約 + 變動風險章） | template 是建計畫第一站、不同步則規範淪空談 |
| **Q7**：條款命名 / A6 範式？ | §7「跨 Phase 接縫契約」；A6 給整合測試指令範式 + 豁免註記 | 與 §4.2 A1-A5 體例一致 |
| **Q8**：template↔framework 對齊深度？ | **【定案】template=SSOT、framework §4.1 改引用**（一次根治 drift）；**WORKFLOW-4 候選刪除** | v2「只補佔位 + 候選」屬拖延；SSOT 一次做掉、on-theme |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-3（跨 Phase 接縫契約 + 收官前整合測試 + template SSOT 化）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 WORKFLOW-3 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含 commit 拆分；100% DOC-Refactor 零業務代碼；接縫契約唯一源 WORKFLOW_SOP §7、plan 結構唯一源 template_plan；不溯及既往 |
| **改版觸發條件** | §1–§8 任一規格條款變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 接縫契約唯一源 WORKFLOW_SOP §7；plan 結構唯一源 template_plan；framework / 引用方不重寫 |

### §99.2 Revision 歷程

- **v3 校訂 (2026-06-08)**：baron 三點審查——② §6 規格依據修正 HOTFIX-1 路徑漂移（現位 `baton/`、收官後移 `hotfixes/`）；③ §2 U3 之 A6 觸發條件加「時」與 A1-A5 事件語法對位；① §7.1 已含 template_plan 接縫契約 grep（無需新增、確認涵蓋）。
- **v3 (2026-06-08)**：依「對專案有幫助就做、不拖延」原則重評 §4 四項處置——**2 項升級為現在做**：① **template↔framework drift → SSOT 根治**（U4：template=plan 結構 SSOT、framework §4.1 改引用、**刪 WORKFLOW-4 候選**、§8 Q8 定案）；② **認知負荷 → 附 worked example**（U1：SOP §7 + template 附「填好的接縫契約範例·修正版 #1」）。**2 項維持限縮**（做更多有害/無益、非拖延）：進行中分支以下一 Checkout 為界（HOTFIX-1 已前瞻合規）、硬 gate 顯式豁免（移除會卡死特例）。
- v2 (2026-06-08)：納入 baron+Antigravity 4 deltas（新增 §4 變動風險、Q6→A template 升格、版本 v3→v4、template↔framework 對齊起列 WORKFLOW-4 候選）；章節重編號 §1-§8。
- v1 (2026-06-08)：初版（§2 五目標規格 + §7 七 Open Questions）。
