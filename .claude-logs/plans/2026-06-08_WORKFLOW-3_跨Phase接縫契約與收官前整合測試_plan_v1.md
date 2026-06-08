# WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試 plan

> 定義流程治理改版：於 `WORKFLOW_SOP.md` 新增兩條強制條款——①「跨 Phase 接縫契約」（plan 必凍結每個跨 Phase/模組 handoff 的 producer／consumer／key 同基準）②「收官前跨 Phase 整合測試」（多 Phase 任務 Checkout 前必跑串接整合測試、Conformance 必驗）——並同步 `§4.2 進階驗證 A6` 與 `framework §4.1 計畫檔結構契約`。源於 RAG-ASYNC #1 接縫缺陷（plan 未凍結 key 契約 + 全程無整合測試 → 6 commit + Conformance 五維度全綠仍漏）之治本。本 plan 為純規格定義、不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：RAG-ASYNC #1——P2 產 `section_summaries` 以原文標題 path 為 key、P3 `rag_sections` 帶譯後 title、P4 以譯後 title 查 → MISS → C5 整個 commit 白做。**根因＝流程兩個結構性盲點**：① plan v2 只寫「key 對位巢狀樹」、**未凍結跨 Phase 接縫之 key 契約**（沒規定 key＝何物、且 producer／consumer 須同基準）；② plan→tasks→6 個 run→Checkout Conformance **每一道關卡都是「單元/grep 尺度」、無一條跨 Phase 串接測試**——各 commit 孤立正確 + 單元全綠，接縫斷裂卻沒任何 gate 照得出，帶缺陷全綠結案。
- **解法**：以 DOC-Refactor 補 `WORKFLOW_SOP.md` 兩條**強制條款**——① **跨 Phase 接縫契約**（凡跨 ≥2 Phase/模組且有資料 handoff 之任務，plan 必含「接縫契約」章節：逐 handoff 列 producer／consumer／傳遞物之 key/欄位**精確身份**且明示「producer 產與 consumer 取為同一 key 基準」）；② **收官前跨 Phase 整合測試**（此類任務 Checkout（階段 6）前必跑一條「串接整條 Phase + 含至少一個會改變 key 的真實/擬真 transform」之整合測試，Checkout Conformance 必驗其存在且通過）。並同步 `§4.2` 新增 `A6` 觸發項、`framework §4.1` 計畫檔結構契約新增對應必填章節。
- **影響**：`WORKFLOW_SOP.md`（新增條款 + §4.2 A6 + §99.2 Revision）、`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 計畫檔結構契約同步 + §99.2 Revision）；**100% DOC-Refactor、零業務代碼**；不溯及既往（既有已收官任務不回溯）。

---

## §2 目標規格

> 「最終狀態」目標，可量化檢驗；不含 commit 拆分（屬 tasks 階段）。

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
- **Checkout Conformance 必驗**：驗收維度新增「跨 Phase 整合測試存在且通過」一項；缺此測試之多 Phase 任務不得判 🟢 通過。

### U3. §4.2 進階驗證新增 A6
- `WORKFLOW_SOP.md §4.2 進階驗證` 表新增一列：
  - `A6 | 跨 Phase 整合測試 | 任務跨 ≥2 Phase/模組且有資料 handoff | <整合測試指令，含 key-changing transform、pass>`。

### U4. framework §4.1 計畫檔結構契約同步
- `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 計畫檔結構契約` 之必備章節清單**新增第 9 項「跨 Phase 接縫契約」**（當任務跨 Phase 時必填；不跨 Phase 時標「無」），並交叉引用 `WORKFLOW_SOP §7`（唯一權威源、framework 不重寫條款細節）。

### U5. 不溯及既往 + Revision 留痕
- 對齊 `WORKFLOW_SOP §2`「歷史命名不溯及既往」：本條款**只對生效後新任務強制**，既有已收官任務不回溯補測試。
- `WORKFLOW_SOP.md` 與 `framework` 各於 `§99.2` 加 Revision；`WORKFLOW_SOP §99.1` 之「約束事項/重複防護」同步（接縫契約唯一源在 WORKFLOW_SOP、framework 引用）。

---

## §3 現況與證據

- **`WORKFLOW_SOP.md`**：
  - `§3 六階段強制觸發鏈 L87-`：`階段 5 驗證執行 L94`（所有 commit ship 完才跑）/`階段 6 收官 L95`——**現無「收官前整合測試」前置要求**。
  - `§4.1 核心驗證 L111`（C1-C3：檔存在/行數/命名）/`§4.2 進階驗證 L119-127`（A1-A5：@path/§0§99/baton gitignore/pytest 全通過/動態內容）——**A4 僅「pytest 全通過」、無跨 Phase 整合測試項**；單元尺度。
  - `§99.1` 約束/重複防護——待同步接縫契約唯一源宣告。
- **`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`**：
  - `§4.1 計畫檔結構契約 L121-131`：8 必備章節（…#6 測試與 E2E 驗證計畫 L129 / #7 不可動清單 L130 / #8 Open Questions L131）——**無「跨 Phase 接縫契約」章節**；#6 之 E2E 屬手動驗證、未強制跨 Phase 整合**自動化**測試。
- **反例證據（RAG-ASYNC #1）**：plan v2 §U3/D1「`section_summaries: Dict[node_key]`、key 對位巢狀樹」未凍結 key 身份；C5 `_collect_summary_targets`（原文 tiles key）vs C6 `_collect_rag_sections`（譯文 title）各自孤立；6 commit 單元 + C7 Conformance 五維度全綠仍漏（hotfix RAG-ASYNC-HOTFIX-1 doc §真因）。

### §3.1 grep 鋼鐵證據
```bash
# WORKFLOW_SOP §3 六階段（收官前無整合測試前置）
grep -n '## §3 六階段\|階段 5：驗證執行\|階段 6：收官' .claude-logs/ref/WORKFLOW_SOP.md
# 87 / 94 / 95

# §4.2 進階驗證僅 A1-A5（無跨 Phase 整合測試）
grep -n '### §4.2 進階驗證\|^| A[1-5] ' .claude-logs/ref/WORKFLOW_SOP.md

# framework §4.1 計畫檔結構契約 8 章節（無接縫契約）
grep -n '不可做 / 不可動清單\|開放問題\|測試與端到端' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

# 反例：RAG-ASYNC #1 接縫缺陷
grep -n '真因\|接縫\|key 契約\|整合測試' .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md 2>/dev/null || true
```

---

## §4 不可動清單

- [ ] `WORKFLOW_SOP.md §1 五類工作流 / §2 文書類別 / §5 SOP 一致性核查 / §6 命名規則` 既有條款 — 不重寫（僅新增 §7 + §4.2 A6）。
- [ ] `WORKFLOW_SOP.md §3 六階段` 之既有六階段定義 — 不改階段本身（僅於收官階段前掛整合測試前置要求、不新增/移除階段）。
- [ ] `framework §1–§8 既有章節 / §4.2 執行報告契約` — 不重寫（僅 §4.1 計畫檔結構契約新增第 9 項）。
- [ ] **既有已收官任務** — 不溯及既往、不回溯補測試（對齊 §2 不溯及）。
- [ ] 任何**業務代碼**（`.py`）— 100% 不動（純治理文件）。
- [ ] `CLAUDE.md` — 本任務不改（接縫契約唯一源置 WORKFLOW_SOP；CLAUDE.md 如需引用屬另議）。
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫（CLAUDE.md §3）。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| RAG-ASYNC #1 接縫缺陷（治本動因 + 反例） | `.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md`（§真因）|
| 待改：工作流規範（六階段 / 驗證分級 / 治理） | `ref/WORKFLOW_SOP.md`（§3 / §4 / §99） |
| 待改：計畫檔結構契約 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.1 / §99） |
| 治理 .md 改版規格（§0/§99 結構、不溯及既往、Revision） | `ref/WORKFLOW_SOP.md §0 / §2 / §99` + `framework §0 / §99` |
| 進階驗證 A2/A5（治理 .md 改版時 §0/§99 + 動態內容缺席核查） | `ref/WORKFLOW_SOP.md §4.2` |
| 專案進度管控框架（plan-execution 雙軌、不可動清單、Open Questions） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §6 驗證計畫

> 本任務為 DOC-Refactor，驗收採 `WORKFLOW_SOP §6.1` 文件驗證清單（無 pytest）。

### §6.1 文件自動化驗證
```bash
# U1：WORKFLOW_SOP 新增「跨 Phase 接縫契約」條款（含 producer/consumer/同基準/反例）
grep -n '跨 Phase 接縫契約\|同一基準\|producer\|consumer' .claude-logs/ref/WORKFLOW_SOP.md
# U2/U3：收官前整合測試 + §4.2 A6
grep -n 'A6\|跨 Phase 整合測試\|收官前.*整合\|key-changing\|改變.*key' .claude-logs/ref/WORKFLOW_SOP.md
# U4：framework §4.1 新增第 9 項 + 交叉引用 WORKFLOW_SOP §7
grep -n '跨 Phase 接縫契約\|WORKFLOW_SOP §7' .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
# 治理結構：§0/§99 完整（A2）、無動態內容（A5）、各 §99.2 加 Revision
grep -n '^## §0\|^## §99\|WORKFLOW-3' .claude-logs/ref/WORKFLOW_SOP.md .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
grep -n 'TODO-hash\|commit-hash' .claude-logs/ref/WORKFLOW_SOP.md   # 期望：無（動態內容缺席）
```

### §6.2 手動驗證流程
1. 取一個「跨 Phase 假任務」對照新 `§7`：能否逐 handoff 填出 producer/consumer/key 同基準（可填即條款可操作）。
2. 以 RAG-ASYNC #1 為反例回測：依新條款，C5/C6 之 key 不同基準會在「接縫契約」章節被擋下、整合測試會在 Checkout 前照出——驗證新條款確能堵此類缺陷。
3. 確認既有已收官任務不被回溯要求（不溯及既往）。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1**：接縫契約條款放哪？ | **主體置 `WORKFLOW_SOP §7`（唯一權威源）**；`framework §4.1` 僅新增「第 9 項·跨 Phase 接縫契約」並交叉引用 §7（不重寫細節） | 對齊既有「唯一源 + 引用」防重複（WORKFLOW_SOP 為流程規範權威、framework 引用）；baron 指定 WORKFLOW_SOP |
| **Q2**：「跨 Phase」觸發判準？ | **跨 ≥2 Phase 或 ≥2 模組、且存在資料 handoff（一方產、另一方消費）**；單檔內純邏輯改不觸發 | 抓「接縫」本質（handoff）；避免對小任務過度負擔 |
| **Q3**：整合測試是硬 gate 還是建議？ | **硬 gate**（Checkout Conformance 必驗、缺則不得 🟢）；但允許 plan §Open Questions 顯式豁免並說明理由（baron 拍板） | #1 證明軟性建議會被略過；硬 gate 才有效；保留 baron 顯式豁免彈性 |
| **Q4**：整合測試的「最小定義」？ | 必須**串接整條相關 Phase + 至少一個會改變傳遞物 key 的真實/擬真 transform**（如真翻譯器）；純 mock 同一 key 兩端不算 | #1 的所有單元測試都用「自洽同 key」故全綠；唯有 key-changing transform 能照出接縫 |
| **Q5**：是否溯及既往？ | **不溯及**（只對生效後新任務）；既有已收官任務不回溯補測試 | 對齊 WORKFLOW_SOP §2「歷史不溯及既往」；避免回溯成本爆炸 |
| **Q6**：是否同步動 CLAUDE.md / template_plan？ | 本任務**不動 CLAUDE.md**；`template_plan.md` 是否加「接縫契約」佔位章節 → 列為**可選後續**（避免本任務膨脹） | 控範圍；template 同步可隨後小改、非治本必要 |
| **Q7**：條款命名與 A6 指令範式？ | §7 標題「跨 Phase 接縫契約」；A6 觸發欄「任務跨 ≥2 Phase/模組且有 handoff」、指令欄給整合測試範式（pytest 串接 + key-changing transform 斷言） | 與既有 §4.2 A1-A5 表格體例一致、可操作 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-3（跨 Phase 接縫契約 + 收官前整合測試強制條款）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 WORKFLOW-3 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含 commit 拆分（屬 tasks 階段）；100% DOC-Refactor 零業務代碼；接縫契約條款唯一源置 WORKFLOW_SOP、framework 僅引用；不溯及既往 |
| **改版觸發條件** | §1–§7 任一規格條款變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 條款唯一源在 WORKFLOW_SOP §7；framework §4.1 / template 僅引用，不重寫條款細節 |

### §99.2 Revision 歷程

- v1 (2026-06-08)：初版建立。依 RAG-ASYNC #1 接縫缺陷治本 + baron 指定 DOC-Refactor 補 WORKFLOW_SOP 強制條款；§2 五項目標規格（U1 跨 Phase 接縫契約條款 / U2 收官前整合測試強制 / U3 §4.2 A6 / U4 framework §4.1 同步 / U5 不溯及既往+Revision）；§7 七項 Open Questions（條款歸屬 / 觸發判準 / 硬 gate / 整合測試最小定義 / 溯及 / CLAUDE.md·template / 命名與 A6 範式）；不含 commit 拆分。
