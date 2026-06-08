# WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試 plan v2

> 定義流程治理改版：於 `WORKFLOW_SOP.md` 新增兩條強制條款——①「跨 Phase 接縫契約」（plan 必凍結每個跨 Phase/模組 handoff 的 producer／consumer／key 同基準）②「收官前跨 Phase 整合測試」（多 Phase 任務 Checkout 前必跑串接整合測試、Conformance 必驗）——並同步 `§4.2 進階驗證 A6`、`framework §4.1 計畫檔結構契約` 與 **`template_plan.md`**（佔位章節）。源於 RAG-ASYNC #1 接縫缺陷（plan 未凍結 key 契約 + 全程無整合測試 → 6 commit + Conformance 五維度全綠仍漏）之治本。本 plan 為純規格定義、不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§8 任一規格條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：RAG-ASYNC #1——P2 產 `section_summaries` 以原文標題 path 為 key、P3 `rag_sections` 帶譯後 title、P4 以譯後 title 查 → MISS → C5 整個 commit 白做。**根因＝流程兩個結構性盲點**：① plan v2 只寫「key 對位巢狀樹」、**未凍結跨 Phase 接縫之 key 契約**（沒規定 key＝何物、且 producer／consumer 須同基準）；② plan→tasks→6 個 run→Checkout Conformance **每一道關卡都是「單元/grep 尺度」、無一條跨 Phase 串接測試**——各 commit 孤立正確 + 單元全綠，接縫斷裂卻沒任何 gate 照得出，帶缺陷全綠結案。
- **解法**：以 DOC-Refactor 補 `WORKFLOW_SOP.md` 兩條**強制條款**——① **跨 Phase 接縫契約**（凡跨 ≥2 Phase/模組且有資料 handoff 之任務，plan 必含「接縫契約」章節：逐 handoff 列 producer／consumer／傳遞物之 key/欄位**精確身份**且明示「producer 產與 consumer 取為同一 key 基準」）；② **收官前跨 Phase 整合測試**（此類任務 Checkout（階段 6）前必跑一條「串接整條 Phase + 含至少一個會改變 key 的真實/擬真 transform」之整合測試，Checkout Conformance 必驗其存在且通過）。同步 `§4.2 A6`、`framework §4.1`，並將 **`template_plan.md` 同步升格為必要範圍**（新增佔位章節，使新計畫從建立首站即被工具導引；順手對齊 template 與 framework §4.1 之既存 doc-drift）。
- **影響**：`WORKFLOW_SOP.md`（新增 §7 條款 + §4.2 A6 + §99.2 v3→v4）、`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 計畫檔結構契約同步 + §99.2 v3→v4）、**`template_plan.md`**（新增「跨 Phase 接縫契約」佔位 + 補「變動風險」缺章對齊 framework）；**100% DOC-Refactor、零業務代碼**；不溯及既往（既有已收官任務不回溯）。
- **不可動清單**：見 §5。

---

## §2 目標規格

> 「最終狀態」目標,可量化檢驗;不含 commit 拆分（屬 tasks 階段）。

### U1. WORKFLOW_SOP 新增「跨 Phase 接縫契約」強制條款
- `WORKFLOW_SOP.md` 新增章節（建議 `§7 跨 Phase 接縫契約`），定義：**凡任務跨 ≥2 Phase 或 ≥2 模組、且 Phase/模組間有資料 handoff（一方產、另一方消費）者，其 plan 必含「接縫契約」**，逐 handoff 明列：
  - **producer**（誰產、產什麼、欄位/key 名）；
  - **consumer**（誰取、如何 match）；
  - **key/欄位精確身份**（原文 or 譯文 or 穩定 id；何種 path/索引基準）；
  - **同基準保證**：明文「producer 寫入之 key 與 consumer 查找之 key 為**同一基準**，不得各自孤立決定」。
- 規格附**反例錨點**（RAG-ASYNC #1：「key 對位巢狀樹」屬不合格——未凍結 key 身份與同基準）。

### U2. WORKFLOW_SOP 新增「收官前跨 Phase 整合測試」強制條款
- 同類任務（跨 ≥2 Phase/模組 + handoff）於**階段 6 收官（Checkout）前必跑一條跨 Phase 整合測試**，要求：
  - **串接整條相關 Phase/模組**（非單一 Phase 單元）；
  - **至少含一個會改變傳遞物 key 的真實/擬真 transform**（如真翻譯器使譯文≠原文 key），否則無法照出接縫斷裂；
  - 斷言「上游產物經整條鏈後，下游確實正確消費」（接縫不變式）。
- **Checkout Conformance 必驗**：驗收維度新增「跨 Phase 整合測試存在且通過」一項；缺此測試之多 Phase 任務不得判 🟢 通過（豁免見 §8 Q3）。

### U3. §4.2 進階驗證新增 A6
- `WORKFLOW_SOP.md §4.2 進階驗證` 表新增一列：
  - `A6 | 跨 Phase 整合測試 | 任務跨 ≥2 Phase/模組且有資料 handoff | <整合測試指令，含 key-changing transform、pass>`。

### U4. framework §4.1 + template_plan 同步（template 升格必要）
- `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 計畫檔結構契約` 之必備章節清單**新增「跨 Phase 接縫契約」項**（當任務跨 Phase 時必填；不跨 Phase 時標「無」），交叉引用 `WORKFLOW_SOP §7`（唯一權威源、framework 不重寫條款細節）。
- **`template_plan.md` 同步升格為本任務必要範圍**（非後續可選）：
  - 新增「**跨 Phase 接縫契約**」佔位章節（含 producer/consumer/key 同基準三欄式範本 + 「不跨 Phase 標『無』」說明），使新計畫從建立首站即被導引、條款不致淪空談；
  - **順手對齊 template 與 framework §4.1 之既存 doc-drift**：template 目前缺 framework §4.1 之「變動風險與相容性評估」等章（template §5 為「規格依據」、與 framework 不一致）→ 至少補回「變動風險」佔位（對齊深度見 §8 Q8）。

### U5. 不溯及既往 + Revision 版本精確化
- 對齊 `WORKFLOW_SOP §2`「歷史命名不溯及既往」：本條款**只對生效後新任務強制**，既有已收官任務不回溯補測試；**生效時點＝本任務落地 commit**（進行中分支相容處置見 §4）。
- 落地時 Revision 版本：`WORKFLOW_SOP.md §99.2` **v3 → v4**、`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §99.2` **v3 → v4**、`template_plan.md` 加 Revision（如其有版本欄）；`WORKFLOW_SOP §99.1` 之「約束事項/重複防護」同步（接縫契約唯一源在 WORKFLOW_SOP、framework/template 引用）。

---

## §3 現況與證據

- **`WORKFLOW_SOP.md`**：
  - `§3 六階段強制觸發鏈 L87-`：`階段 5 驗證執行 L94`／`階段 6 收官 L95`——**現無「收官前整合測試」前置要求**。
  - `§4.1 核心驗證 L111`（C1-C3）/`§4.2 進階驗證 L119-127`（A1-A5：@path/§0§99/baton gitignore/pytest 全通過/動態內容）——**A4 僅「pytest 全通過」、無跨 Phase 整合測試項**；單元尺度。
  - `§99.2 Revision` 現為 v3（L… `- v3 (2026-05-27)`）——落地後累加 v4。
- **`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`**：
  - `§4.1 計畫檔結構契約 L121-131`：8 必備章節（…**#5 變動風險與相容性評估** / #6 測試與 E2E L129 / #7 不可動 L130 / #8 Open Questions L131）——**無「跨 Phase 接縫契約」章節**；E2E 屬手動、未強制跨 Phase 整合**自動化**測試。`§99.2` 現為 v3。
- **`template_plan.md`**：
  - 現有章節 §0/§1 TL;DR/§2 目標規格/§3 現況/§4 不可動/**§5 規格依據**/§6 驗證/§7 Open Questions/§99——**與 framework §4.1 八章節不一致**（template 無「變動風險」「設計方案」獨立章、§5 為規格依據）；**WORKFLOW-3 自證：連計畫模板都與框架 doc-drift**，故 template 同步既補接縫佔位、亦順手收此 drift。
- **反例證據（RAG-ASYNC #1）**：plan v2 §U3/D1「`section_summaries: Dict[node_key]`、key 對位巢狀樹」未凍結 key 身份；C5 `_collect_summary_targets`（原文 tiles key）vs C6 `_collect_rag_sections`（譯文 title）各自孤立（**且二者同在 `resume_pipeline.py` 內——故觸發判準必須是 handoff、非跨目錄**）；6 commit 單元 + C7 Conformance 五維度全綠仍漏（`RAG-ASYNC-HOTFIX-1_hotfix.md §真因`）。

### §3.1 grep 鋼鐵證據
```bash
grep -n '## §3 六階段\|階段 5：驗證執行\|階段 6：收官' .claude-logs/ref/WORKFLOW_SOP.md      # 87/94/95
grep -n '### §4.2 進階驗證\|^| A[1-5] ' .claude-logs/ref/WORKFLOW_SOP.md                    # A1-A5、無 A6
grep -n '變動風險與相容性\|不可做 / 不可動清單\|開放問題' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md  # §4.1 八章節
grep -n '## §5 規格依據\|變動風險' .claude-logs/templates/template_plan.md                 # template 無變動風險章（drift）
grep -n '- v3 ' .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md  # 現 v3、落地累加 v4
```

---

## §4 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **認知負荷↑**：每個跨 Phase 任務 plan 多寫「接縫契約」章 + 多撰一條含 key-changing transform 的整合測試 | 🟡 中 | 由 §8 Q2「handoff 觸發判準」收斂範圍（單檔純邏輯/小任務不觸發）+ §8 Q3 顯式豁免通道 + template 佔位降低撰寫摩擦；整體成本 << 一次接縫缺陷返工（#1 即 C5 整 commit 白做） |
| **進行中分支相容**：本條款生效時，已開工但未收官之多 Phase 任務是否須補 | 🟡 中 | 生效時點＝落地 commit（§U5）；**進行中分支以「下一個 Checkout」為界**——生效後才進 Checkout 者須補整合測試、生效前已 Checkout 者不溯及（§U5 / §8 Q5）；避免半途強制造成返工 |
| **擬真 transform 撰寫成本**：Q4 要求測試含「會改 key 的真實/擬真 transform」，部分任務需自建輕量變更機制（如 `f"ZH::{x}"` 假翻譯器） | 🟢 低 | 多數情境可用極輕量 stub（如 #1 hotfix 之 `FakeTr` 加前綴即足）；SOP 僅要求「key 會變」、不要求真 API；範式寫入 A6 指令欄 |
| **template ↔ framework 對齊牽動範圍**：補 template 缺章（變動風險等）可能誘發 template 全面重構 | 🟡 中 | 本任務**只補必要佔位**（接縫契約 + 變動風險）、**不全面重構 template**；完整對齊深度列 §8 Q8 由 baron 拍板，避免任務膨脹 |
| **硬 gate 卡死特例**：純文檔重構 / 外部強依賴（付費 API）等無法跑整合測試 | 🟢 低 | §8 Q3 保留 plan §Open Questions 顯式申請豁免（baron 拍板）；DOC-Refactor 等不跨 Phase 者本不觸發 |
| **既有條款相容**：新增 §7 / A6 是否衝突 §1-§6 既有規範 | 🟢 低 | 純**新增**（§7 / §4.2 A6 / framework 新項 / template 新章），不改既有條款語意（§5 不可動）；§99.1 重複防護宣告唯一源 |

---

## §5 不可動清單

- [ ] `WORKFLOW_SOP.md §1 五類工作流 / §2 文書類別 / §5 SOP 一致性核查 / §6 命名規則` 既有條款 — 不重寫（僅新增 §7 + §4.2 A6）。
- [ ] `WORKFLOW_SOP.md §3 六階段` 之既有六階段定義 — 不改階段本身（僅於收官階段前掛整合測試前置要求、不新增/移除階段）。
- [ ] `framework §1–§8 既有章節 / §4.2 執行報告契約` — 不重寫（僅 §4.1 計畫檔結構契約新增「接縫契約」項）。
- [ ] `template_plan.md` 既有章節語意 — 不重寫（僅**新增**接縫契約 + 變動風險佔位；不全面重構，重構深度待 §8 Q8 拍板）。
- [ ] **既有已收官任務** — 不溯及既往、不回溯補測試（§U5）。
- [ ] 任何**業務代碼**（`.py`）— 100% 不動（純治理文件）。
- [ ] `CLAUDE.md` — 本任務不改（接縫契約唯一源置 WORKFLOW_SOP；CLAUDE.md 引用屬另議）。
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫（CLAUDE.md §3）。

---

## §6 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| RAG-ASYNC #1 接縫缺陷（治本動因 + 反例） | `.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md`（§真因）|
| 待改：工作流規範（六階段 / 驗證分級 / 治理） | `ref/WORKFLOW_SOP.md`（§3 / §4 / §99） |
| 待改：計畫檔結構契約（§4.1 八章節含變動風險） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 / §99） |
| 待改：計畫模板（佔位章節 + 對齊 framework） | `templates/template_plan.md` |
| 治理 .md 改版規格（§0/§99 結構、不溯及既往、Revision） | `ref/WORKFLOW_SOP.md §0/§2/§99` + `framework §0/§99` |
| 進階驗證 A2/A5（治理 .md 改版時 §0/§99 + 動態內容缺席核查） | `ref/WORKFLOW_SOP.md §4.2` |
| 專案進度管控框架（plan-execution 雙軌、不可動清單、Open Questions） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §7 驗證計畫

> 本任務為 DOC-Refactor，驗收採 `WORKFLOW_SOP §6.1` 文件驗證清單（無 pytest）。

### §7.1 文件自動化驗證
```bash
# U1：WORKFLOW_SOP 新增「跨 Phase 接縫契約」（含 producer/consumer/同基準/反例）
grep -n '跨 Phase 接縫契約\|同一基準\|producer\|consumer' .claude-logs/ref/WORKFLOW_SOP.md
# U2/U3：收官前整合測試 + §4.2 A6
grep -n 'A6\|跨 Phase 整合測試\|收官前.*整合\|改變.*key\|key-changing' .claude-logs/ref/WORKFLOW_SOP.md
# U4：framework §4.1 新增項 + template_plan 佔位 + 變動風險對齊
grep -n '跨 Phase 接縫契約\|WORKFLOW_SOP §7' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n '跨 Phase 接縫契約\|變動風險與相容性評估' .claude-logs/templates/template_plan.md
# U5：版本 v4 + 治理結構（A2 §0/§99、A5 無動態內容）
grep -n '- v4 ' .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n '^## §0\|^## §99' .claude-logs/ref/WORKFLOW_SOP.md
grep -n 'TODO-hash\|commit-hash' .claude-logs/ref/WORKFLOW_SOP.md   # 期望：無（動態內容缺席）
```

### §7.2 手動驗證流程
1. 取一個「跨 Phase 假任務」對照新 `§7` + template 佔位：能否逐 handoff 填出 producer/consumer/key 同基準（可填即條款可操作）。
2. 以 RAG-ASYNC #1 為反例回測：依新條款，C5/C6 之 key 不同基準會在「接縫契約」章節被擋下、整合測試會在 Checkout 前照出——驗證新條款確能堵此類缺陷。
3. 確認既有已收官任務不被回溯要求（不溯及）；進行中分支以下一個 Checkout 為界。

---

## §8 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1**：接縫契約條款放哪？ | **主體置 `WORKFLOW_SOP §7`（唯一權威源）**；`framework §4.1` / `template_plan` 僅新增項並交叉引用 §7 | 對齊「唯一源 + 引用」防重複；WORKFLOW_SOP 為流程權威、framework/template 引用 |
| **Q2**：「跨 Phase」觸發判準？ | **跨 ≥2 Phase 或 ≥2 模組、且存在資料 handoff**；單檔內純邏輯改不觸發 | 抓「接縫」本質（handoff）；**#1 之 producer/consumer 同在 resume_pipeline.py → 按目錄/檔案判定會漏，故必以 handoff 為準** |
| **Q3**：整合測試是硬 gate 還是建議？ | **硬 gate**（Checkout Conformance 必驗、缺則不得 🟢）+ 允許 plan §Open Questions 顯式申請豁免（baron 拍板） | #1 證明軟性建議會被略過；硬 gate 才有效；保留特例退出通道（純文檔/付費 API 強依賴） |
| **Q4**：整合測試的「最小定義」？ | 必須**串接整條相關 Phase + 至少一個會改變傳遞物 key 的真實/擬真 transform**；純 mock 同一 key 兩端不予承認 | #1 所有單元測試都用「自洽同 key」故全綠；唯有 key-changing transform 能照出接縫；轉接成本低（前綴 stub 即足） |
| **Q5**：是否溯及既往？ | **不溯及**（只對生效後新任務）；生效時點＝落地 commit；進行中分支以「下一個 Checkout」為界 | 對齊 WORKFLOW_SOP §2「歷史不溯及」；避免回溯成本爆炸與 regression |
| **Q6**：是否同步動 CLAUDE.md / template_plan？ | **不動 `CLAUDE.md`；`template_plan.md` 升格為必要範圍**（新增接縫契約 + 變動風險佔位） | CLAUDE.md 全局語境宜穩定；**template 是建計畫第一站，不同步則新規範缺工具導引、淪空談**（原 v1「可選後續」修正為必要）|
| **Q7**：條款命名與 A6 指令範式？ | §7 標題「跨 Phase 接縫契約」；A6 給整合測試指令範式（pytest 串接 + key-changing transform 斷言）+ 豁免註記 | 與既有 §4.2 A1-A5 體例一致、Conformance 可操作 |
| **Q8**（新）：template_plan 對齊 framework §4.1 的**深度**？ | **最小對齊**：只補「跨 Phase 接縫契約 + 變動風險」兩佔位章；**不全面重構** template 至 framework 八章節 | 控 WORKFLOW-3 範圍、避免任務膨脹；template 全面對齊（補設計方案/重排序等）列為**獨立後續**（WORKFLOW-4 候選）|

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-3（跨 Phase 接縫契約 + 收官前整合測試 + template 同步）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 WORKFLOW-3 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含 commit 拆分（屬 tasks 階段）；100% DOC-Refactor 零業務代碼；接縫契約條款唯一源置 WORKFLOW_SOP、framework/template 僅引用；不溯及既往 |
| **改版觸發條件** | §1–§8 任一規格條款變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 條款唯一源在 WORKFLOW_SOP §7；framework §4.1 / template_plan 僅引用佔位，不重寫條款細節 |

### §99.2 Revision 歷程

- **v2 (2026-06-08)**：baron + Antigravity 審查後納入 4 deltas——① 新增 **§4 變動風險與相容性評估**（認知負荷/進行中分支相容/擬真 transform 成本/template 對齊牽動/硬 gate 特例/既有條款相容，章節重編號 §4 不可動→§5、§5 規格依據→§6、§6 驗證→§7、§7 OQ→§8、§0/§99 觸發範圍 §1-§7→§1-§8）；② **Q6 修正為 A**（template_plan 升格必要、U4 納入佔位章節，原 v1「可選後續」推翻）；③ **U5 版本精確化**（WORKFLOW_SOP/framework v3→v4）；④ **新增 template↔framework §4.1 doc-drift 對齊**（U4 補變動風險缺章 + §8 Q8 對齊深度）。
- v1 (2026-06-08)：初版建立。依 RAG-ASYNC #1 接縫缺陷治本 + baron 指定 DOC-Refactor 補 WORKFLOW_SOP 強制條款；§2 五項目標規格 + §7 七項 Open Questions；不含 commit 拆分。
