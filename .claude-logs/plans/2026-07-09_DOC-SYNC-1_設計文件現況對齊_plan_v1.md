# DOC-SYNC-1 設計文件現況對齊 plan

> 目的：把 `design/docs/` 的「條目正確性」對齊 2026-07-09 前端現況——**清幽靈**（components.md 把未實作規劃寫成現況契約的 6 個 class、dom-reference 2 個已汰換 ID 的標註確認）+ **補漏記**（dom-reference 覆蓋率 36%→100%，48 個漏記 ID 以輕量條目補齊）。**刻意不深耕**：ownership map / `@layer` 原則 / theme-guide 契約改寫依既定順序留給 FE-CSS-GOV 各 commit 配套。純 DOC-Refactor、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：design/docs 停更於 2026-05-24~06-13、`static/index.html` 改到 2026-07-09（FE-AESTHETICS/RAG-12~14/PIPE-SLIDES/FE-PERF-2 ≈5 個任務世代未回灌）。實測：①**components.md 含 6 個幽靈 class**（`.msg-ai-actions`/`.msg-copy`/`.msg-regen`/`.title-meta`/`.title-meta-sep` 為規劃過未實作、`.dropdown-popup` 與實作不符）——「設計意圖寫成現況契約」，AI 讀到會去接不存在的線（**毒性最高**）；②**dom-reference.md 覆蓋率僅 36%**（記載 27 vs 實際 75 ID、漏 48 個：action/notice/prompt modal 全家、`chat-input`、`abstract-toolbar` 等）——文件失去路由價值、AI 只能裸 grep。token 契約層（color-tokens/spacing/typography/theme-guide 必供 19）實測**零差、不在本案範圍**。
- **解法**：兩檔定向修——**U1 清幽靈**（未實作者加「⚠️ 未實作（規劃保留）」in-place 標註、與實作不符者更正為實名）+ **U2 補漏記**（48 ID 依 dom-reference 既有分區表格式、輕量欄位補齊）+ **U3 同步戳**（兩檔頂部記對照基準 `index.html@<hash>`）。
- **影響**：僅 `design/docs/components.md` + `design/docs/dom-reference.md` 兩檔（+視 §9 Q3 之 token 層三檔一行驗證註）；**零業務代碼、零 runtime**；`static/index.html` 只讀對照、不動。

---

## §2 目標規格

- **U1 — components.md 幽靈清理（去毒）**〔v3 依 tasks 階段深掘修正對象與措辭〕：5 個 class 兩款處置——
  1. **真幽靈（未實作之規劃）**：`.title-meta`/`.title-meta-sep`（`renderTitleHeader` `:2748` 只建 title-zh/en/abstract、後端 0 命中）→ **in-place 加「⚠️ 未實作（規劃保留、勿接線）」**；
  2. **半實作（基建在、注入缺）**：`.msg-ai-actions`/`.msg-copy`/`.msg-regen`（CSS `:1063-1098` + 事件委派 `:2405-2406` + 匯出剝除 `:2411` 皆在、**DOM 注入缺席**→hover 現況不顯示）→ **in-place 加「⚠️ 半實作（樣式/委派已備、DOM 注入未接——現況不顯示、勿假設按鈕存在）」**；
  3. ~~`.dropdown-popup`~~ **v3 移除**：原判「與實作不符」為**稽核誤判**（`className = 'ctx-popup dropdown-popup'` 含空格模式漏抓；實存於 `:2241` 創建+`:264` CSS）——components.md L153/L209 現況正確、**零處置**。
  - 驗收：上列 5 個 class 名在 components.md 中**每一處出現**皆帶對應標註；`.dropdown-popup` 相關行零改動；`grep -n` 逐一可證。
- **U2 — dom-reference.md 漏記補齊（覆蓋率 100%）**：實際 75 個 ID 與文件記載之**差集歸零**（雙向：漏記 48 個補入；已汰換者沿用文件既有「原版 vs prototype 對照」標註慣例、不新增幽靈）。
  - **輕量條目約定（防深耕）**：新補條目走**輕量欄位**——`id`／所屬區塊／用途一句／JS 綁定點（`index.html` 行號級）；依既有分區表格式歸組（modal 家族一表等）；**不寫**狀態組合矩陣與長篇契約（既有 27 條的深度欄位不溯及要求）。
  - 驗收：`comm -13 doc_ids real_ids` = 0；dom-reference 增量 ≤ **~160 行**（輕量上限、防膨脹）。
- **U3 — 同步戳**：兩檔頂部各加一行「最後現況對照：2026-07-09、基準 `static/index.html@<C4 hash 8e5d1fa>`」——讓下次稽核可判斷新鮮度。
- **U4 — 純 DOC 零迴歸**：`git diff --stat` 僅命中 `design/docs/` 檔（兩檔＋視 Q3 三檔）；零 `.py`/`static/`；`static/index.html` 零 byte 變動。
- **U5 — 邊界（刻意不做、防 scope creep）**：**不做** ownership map、不加 `@layer`/命名作用域原則、不改寫 theme-guide 主題契約、不深耕 principles（含 FE-RHYTHM margin-flow 模型缺漏，見 §9 Q4）、不動 token 層三檔內容（實測零差）——**全數依既定順序屬 FE-CSS-GOV 各 commit 之 docs 配套**。

### §2.5 候選方案（Diverse Rollout）

> 幽靈內容處置屬易錯決策（刪了丟意圖、留了繼續毒），填本節。

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| **方案 A（選定）** | **in-place「⚠️ 未實作」標註 + 不符者更正實名** | 保留設計意圖（components.md 本質是設計契約書）、去除「現況」誤導、diff 最小、上下文不斷（z-index 表列等原位保留）；AI 讀到標註即知勿接線 |
| 方案 B（否決） | 刪除幽靈條目 | 最乾淨但**丟失設計意圖**（msg 操作鈕/title-meta 是有價值的未來規劃）；且 z-index 表刪列會斷層級敘事 |
| 方案 C（否決） | 集中搬遷至「未實作規劃」專節 | 意圖集中保留，但條目脫離原上下文（z-index 表、title 區敘述各需留殘根）、diff 大、易漏 |

- **選定理由**：A 以最小 diff 同時達成「去毒」與「保意圖」；components.md 自我定位是「所有新元件設計前先翻這份」——標註後它反而**更誠實地**扮演此角色。
- **否決留痕**：B（丟意圖）、C（斷上下文）留底。

---

## §3 現況與證據

> 全部為 2026-07-09 實測（一致性稽核 session），對照基準 `static/index.html@8e5d1fa`。

- **覆蓋率**：dom-reference 記載 ID **27** vs `index.html` 實際 **75**（`grep -oE 'id="..."' | sort -u` 對 `comm`）；漏記樣本：`action-modal/-box/-body/-ok/-cancel/-title`、`notice-*`、`prompt-*`（BUG-F4 A3 通用 modal 三件套）、`chat-input`（contenteditable 改制）、`chat-header-actions`、`abstract-toolbar`、`cleanup-btn`、`app` 等。
- **幽靈 ID（dom-reference、已自我標註）**：`#demo-bar`（L406 標「整段刪除」）、`#doc-type-select`（L344/L360 標「原版 native、prototype 用 `#doc-type-dropdown`」）——屬**對照語境非誤導**，U2 沿用該慣例、僅確認標註清晰。
- **幽靈 class（components.md）〔v3 tasks 階段深掘修正〕**：
  - **真幽靈**：`.title-meta`/`.title-meta-sep`（doc L325-327/L334-335）——`renderTitleHeader`（`index.html:2748`）實建僅 `h1.title-zh`/`p.title-en`/`details.title-abstract`；`processor/`/`pipelines/`/`web_server.py` 0 命中；前端唯一命中 `:3757` 為 stale 註解。
  - **半實作**：`.msg-ai-actions`/`.msg-copy`/`.msg-regen`（doc L357-359）——CSS `:1063-1098`、委派 handler `:2405-2406`、匯出剝除 `:2411` 皆在；**DOM 注入零處**（全檔無創建點）→ hover 現況不顯示任何按鈕。
  - **v3 勘誤**：`.dropdown-popup` 原判幽靈為**誤**——`:2241` `pop.className = 'ctx-popup dropdown-popup'`（含空格 className、原稽核 regex 漏抓）+ `:264` CSS 存活；components.md L153/L209 現況正確、移出本案範圍。
- **token 契約層零差（本案不動之依據）**：color-tokens ↔ `:root` 雙向差集 0；spacing/typography 值表逐項符（4/8/16px、14/13px）；theme-guide 必供 19 token 四主題缺 0。
- **文件新鮮度（git log -1）**：components/theme-guide/color-tokens 2026-05-24、principles 05-25、dom-reference 06-13（FE-RHYTHM-UNIFY C5 唯一一次 Docs Sync）；`index.html` 07-09。
- **仲裁條款既存**：dom-reference 頂部明文「若實際程式碼與本文件衝突 → 以 `index.html` 為準、本文件需更新」——本案即執行該條款。

### §3.1 grep 鋼鐵證據

```bash
$ grep -oE '`#[a-z][a-z0-9-]+`' design/docs/dom-reference.md | tr -d '`#' | sort -u | wc -l   # 27
$ grep -oE 'id="[a-z][a-z0-9-]+"' static/index.html | sed 's/id="//;s/"//' | sort -u | wc -l  # 75
$ comm -23 doc_ids real_ids → demo-bar / doc-type-select（僅 2、皆文件已標註）
$ comm -13 doc_ids real_ids | wc -l → 48（漏記）
$ for c in dropdown-popup msg-ai-actions msg-copy msg-regen title-meta title-meta-sep; do
    grep -c "$c" <(HTML class= ∪ JS className/classList 全集); done → 全部 0（幽靈確證）
$ comm（color-tokens ↔ :root）→ 雙向 0（token 層零差、不動）
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 純 `design/docs/` 文件對齊、無模組間 code handoff；`index.html` 唯讀對照。§7.2 豁免申請見 §9 Q5。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 補記 48 條淪為深耕、檔案膨脹 | 🟡 中 | U2 輕量欄位約定 + 增量 ≤~160 行硬上限；深度契約留給實際需要的任務隨用隨補 |
| 與 FE-CSS-GOV 重工（class 記載即將被命名收斂改名） | 🟢 低 | 本案**不碰** components 的 class 深度內容、只處置 6 幽靈；ID 層 95% 在 CSS-GOV 後存活（收斂的是 CSS 選擇器用法、非 DOM id） |
| 幽靈標註後仍被 AI 誤讀 | 🟢 低 | 標註措辭統一「⚠️ 未實作（規劃保留、勿接線）」——動詞明確禁止接線 |
| ~~`.dropdown-popup` 實名判斷~~（v3 已結）| — | tasks 階段深掘即實證其存活（`:2241`/`:264`）、提前於 Run 期解決並自 U1 移除；同時暴露原稽核 regex 盲點（含空格 className）→ U1 對象全數已用全文 grep 複驗 |
| 誤動 token 層/其餘 9 檔 | 🟢 低 | §6 不可動明列；U4 diff 範圍驗證 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] **業務代碼與前端**：`*.py` / `static/*`（含 `index.html`——唯讀對照基準、零 byte 變動）。
- [ ] **token 契約層三檔內容**：`color-tokens.md` / `spacing.md` / `typography.md`（實測零差；僅 Q3 若拍板「加一行驗證註」為唯一例外）。
- [ ] **`theme-guide.md` / `principles.md`**：整檔不動（`@layer`/主題契約/margin-flow 模型屬 FE-CSS-GOV 配套；Q4 例外由 baron 拍板）。
- [ ] **其餘 design/docs**（README/api-integration/interaction/icon-spec/copywriting）：不動。
- [ ] **既有 27 條 dom-reference 條目之深度內容**：不重寫（僅補漏、僅確認 2 個對照標註清晰）。
- [ ] **components.md 幽靈以外的內容**：不動（含所有現存 class 的規格敘述）。
- [ ] **兩份 audit / baton 長駐檔**：不碰。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| DOC-Refactor 工作流 + 驗收（§6.1 驗證清單） | `ref/WORKFLOW_SOP.md §1.3 / §4` |
| 雙軌制 / 重複防護 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §99.1` |
| 一致性實測證據 | 本 plan §3（2026-07-09 稽核 session、基準 `index.html@8e5d1fa`） |
| 順序定案（先清帳後改版、兩 plan 分開） | baron 2026-07-09 拍板（DOC-SYNC 輕量先行；ownership map/@layer 原則/theme-guide 改寫隨 FE-CSS-GOV 各 commit 配套） |
| dom-reference 仲裁條款 | `design/docs/dom-reference.md` 頂部（以 index.html 為準、文件需更新） |
| 收官 git-add 白名單鐵律 + checkout 報告鐵律 | `ref/WORKFLOW_SOP.md §3`（CHECKOUT-GUARD） |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- 無 pytest 需求（純 `.md`；且本環境 pytest 模組缺、FE-PERF-2 checkout 已標註）。以靜態核查替代：
  ```bash
  # U2 覆蓋率歸零差
  comm -13 <(doc_ids) <(real_ids) | wc -l    # 期望 0
  # U1 幽靈去毒
  for c in msg-ai-actions msg-copy msg-regen title-meta title-meta-sep; do
    grep -n "$c" design/docs/components.md | grep -vc "未實作"; done   # 每項期望 0（皆帶標註）
  grep -c "dropdown-popup" design/docs/components.md                    # 期望 0（已更正實名）
  # U3 同步戳
  grep -c "8e5d1fa" design/docs/dom-reference.md design/docs/components.md   # 各 ≥1
  # U2 膨脹上限 + U4 範圍
  git diff --stat design/ ; git diff --stat -- . ':!design'             # 後者期望空
  ```

### §8.2 手動端到端（E2E）＝文件核查（DOC-Refactor §6.1 清單）

1. `wc -l` 兩檔（dom-reference 增量 ≤~160 行）；命名合規（檔名不改、非 .md 產物無）。
2. 抽驗 5 個新補 ID 條目：對 `index.html` 行號/用途正確、欄位輕量（無深耕）。
3. 抽驗 6 個幽靈處置點：標註措辭統一、`.dropdown-popup` 更正處與實檔 grep 相符。
4. 確認 token 層三檔 diff（Q3 拍板前）為零。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 幽靈 class 處置形式？ | **§2.5 方案 A：in-place「⚠️ 未實作（規劃保留、勿接線）」標註 + `.dropdown-popup` 更正實名** | 去毒與保意圖兼得、diff 最小、上下文不斷。 |
| **Q2** dom-reference 補記深度？ | **輕量欄位**（id/區塊/用途一句/JS 綁定行號）、依既有分區表歸組、增量 ≤~160 行 | 本案定位「條目正確性」；深度契約留實際需要的任務隨用隨補，防 DOC-SYNC 變深耕。 |
| **Q3** token 層三檔要不要加一行「2026-07-09 實測零差」驗證註？ | **加**（各一行、含基準 hash） | 成本 3 行、把本次稽核成果留痕，防未來重複稽核勞動；不改任何 token 內容。 |
| **Q4** principles.md 缺 FE-RHYTHM margin-flow 模型，本案補嗎？ | **不補、隨 FE-CSS-GOV 的 principles 配套 commit 一併** | 該 commit 本來就要動 principles（@layer/作用域紀律）、一次寫齊；本案守「條目正確性」邊界。 |
| **Q5** §7.2 跨 Phase 整合測試豁免？ | **顯式豁免** | 純 DOC、無 code handoff（同 WORKFLOW-3/4/5、CONTEXT-1 先例）。 |
| **Q6** 任務代號與 commit 數？ | **DOC-SYNC-1**（依 §5 `<TYPE>-N`）；規模預期 **1–2 commits + checkout**（拆分屬 tasks 階段、本 plan 不給建議） | 對齊既有代號風格；「小」是本案的設計目標。 |

### §9.1 定案紀錄（baron 2026-07-09 review 全數 🟢 核准）

| OQ | 定案 | 備註 |
|---|---|---|
| Q1 | 🟢 §2.5 方案 A：in-place「⚠️ 未實作（規劃保留、勿接線）」+ `.dropdown-popup` 更正實名 | 保藍圖、斷毒性、diff 最小 |
| Q2 | 🟢 輕量欄位、增量 ≤~160 行 | 防過度工程 |
| Q3 | 🟢 token 三檔**頂部**各加一行「2026-07-09 實測零差 `index.html@8e5d1fa`」戳記 | 防未來重複稽核勞動 |
| Q4 | 🟢 principles 不補、隨 FE-CSS-GOV 一併 | 佈局原則隨 CSS 結構重構更省力 |
| Q5 | 🟢 §7.2 顯式豁免 | 純 DOC、無 code handoff |
| Q6 | 🟢 DOC-SYNC-1；**規模釘死＝1 實作 commit + 1 checkout**（收斂原「1–2」預估） | 簡單乾淨；tasks 依此拆 |

**六 OQ 全結清、規格凍結（含 Q6 規模釘死），可進階段 2（tasks 拆分 + 同步 TODO 🟡 WIP）。**
**review 對齊複核**：U1 幽靈/U2 48 差集/token 零差/基準 `8e5d1fa` 四點經 baron 獨立比對確認與實檔一致、零修正。
**v3 註**：其中「U1 幽靈六項」於 tasks 階段深掘後修正為「2 真幽靈 + 3 半實作 + 1 誤判移除（`.dropdown-popup` 存活）」——Q1 定案之處置形式（in-place 標註）不變、對象與措辭精緻化；U2/token/基準三點不受影響。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 DOC-SYNC-1「設計文件現況對齊（清幽靈+補漏記）」目標規格，作為 tasks 拆分與原子執行唯一基準 |
| **用途** | 供 baron 審查 §9 並於 tasks.md 拆分時引用；階段 3/5 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 DOC-SYNC-1 tasks / 執行報告；FE-CSS-GOV plan（銜接：本案不做項之歸屬） |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡/拍板過程；嚴禁 commit 拆分（tasks 階段、baron 明示不給）；嚴禁越 U5 邊界深耕 |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務完成、baron 同意歸檔 archive/ |
| **重複防護** | 視覺/元件規格 SSOT 仍在 `design/docs/`（本案是讓它回真、非另立源）；效能規範在 FE SOP；CSS 結構治理定案在 `baton/frontend_css_governance_audit.md`（本案不重寫其結論）；deep-doc（ownership map/@layer 原則）唯一歸屬 FE-CSS-GOV |

### §99.2 Revision 歷程

- v3 (2026-07-09)：tasks 階段深掘勘誤（§1.9 累積補強）——U1 對象修正：`.dropdown-popup` **誤判移除**（`:2241` 含空格 className 存活、原稽核 regex 盲點）；`.msg-*` 三項改判**半實作**（CSS+委派+匯出剝除在、DOM 注入缺）標註措辭升級；`.title-meta`×2 維持真幽靈（`renderTitleHeader:2748` 實建清單+後端 0 命中鐵證）；§3 證據/§5 風險/§9.1 同步；Q1 處置形式與 U2–U5 全部不變。
- v2 (2026-07-09)：baron review 全數 🟢 核准——四點對齊複核零修正（U1 幽靈/U2 差集 48/token 零差/基準 8e5d1fa）；§9 六 OQ 定案入 §9.1，含兩處銳化：**Q6 規模釘死＝1 實作 commit + 1 checkout**（收斂原 1–2 預估）、Q3 戳記位置明確「頂部」；規格凍結、可進階段 2。
- v1 (2026-07-09)：初版——依 2026-07-09 design/docs 一致性實測（dom-reference 27/75=36% 覆蓋、components 6 幽靈 class、token 層零差）與 baron 順序拍板（先清帳後 FE-CSS-GOV、兩 plan 分開），立 U1 清幽靈〔§2.5 A：in-place 未實作標註+實名更正〕/ U2 補漏記〔輕量欄位·≤~160 行〕/ U3 同步戳 / U4 零迴歸 / U5 邊界（不深耕清單）；§9 六 OQ 待 baron 拍板。
