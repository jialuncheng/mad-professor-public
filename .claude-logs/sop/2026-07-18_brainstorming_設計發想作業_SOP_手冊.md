# Brainstorming 設計發想作業 SOP 手冊

> 本文件為 Mad Professor 專案「設計發想（brainstorming）作業」的權威規範。
> 蒸餾自 superpowers（`obra/superpowers@HEAD` `skills/brainstorming/SKILL.md`）之蘇格拉底式問答骨架，**改寫貼合本專案落點 / 溯源 / 護欄**——**不裝 plugin、以 vendored 檔案運作**（BRAINSTORM-1）。
> 用途：在正式 plan（階段 1）**之前**的「還沒想清楚要做什麼功能 / 哪種設計」發散階段使用；產出的 design spec 定位為既有 `_audit.md` 式**原料**，餵入 `.claude-logs/templates/template_plan.md`。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規範變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 概念模型與適用時機

### §1.1 定位：plan 的再上游

```
[本 SOP] brainstorming 問答發散 ──→ 產 design spec（原料，落 baton/）
                                          │（當作輸入）
                                          ▼
階段 1：_plan.md（套 template_plan + 補證據/接縫/護欄/驗證）
                                          ▼
階段 2～6（tasks → 驗證 → 執行 → 驗證 → 收官，原封不動）
```

- spec 是 plan 的**輸入**，**不是**與 plan 打對台的另一份 plan。
- 加入 brainstorming **不改任何既有治理契約**（消費端 `template_plan` 零變動）。

### §1.2 何時用 / 何時不用

- **用**：功能構想未定、設計方向多於一種、需要與 baron 來回釐清意圖與邊界時。
- **不用**：需求已明確、可直接進 `template_plan`；或純 bug 修補（走 hotfix 流程）。
- **鐵律（承 superpowers）**：**在提出設計並經 baron 核准前，嚴禁動任何業務代碼、嚴禁 scaffold、嚴禁進 tasks/execution**（對齊 `CLAUDE.md §1.1` plan-execution 雙軌制）。

---

## §2 問答流程骨架

依序執行，每步產完即與 baron 對齊，不搶跑：

1. **探索 context**：先 view / grep 相關檔案、既有設計文件、近期 commit，理解現況（對齊 `CLAUDE.md §1.7` grep 證據）。
2. **逐一澄清**：**一次只問一個問題**、**優先選擇題**（降低 baron 認知負荷、加速收斂）。釐清目的、使用者、約束、成功條件。
3. **提 2-3 個方案**：對關鍵決策攤 **2-3 個語意分散**候選 + 各自 trade-offs + 推薦（呼應 `template_plan §2.5` Diverse Rollout 與 `CLAUDE.md §1.9` 決策軌跡）。
4. **分段呈現設計**：依複雜度分段、**每段取得核准後**才續下一段（避免一次灌大設計）。
5. **產 design spec**：寫入 `.claude-logs/baton/`（見 §3 落點與溯源）。**格式不設限**——可含條列 / 表格 / ASCII 圖 / mermaid，依主題自由。
6. **自檢**：檢查 placeholder（TBD / 待補）、前後矛盾、模糊語、scope 溢出。
7. **baron 核准閘**：spec 經 baron 過目 / 修改後才視為原料就緒。
8. **交棒 plan**：唯一下游動作＝進階段 1，用 `template_plan` 消費 spec（見 §4）。**不自動接任何執行動作**。

---

## §3 落點規範與溯源 header

### §3.1 落點（硬規範）

- design spec 一律落 **`.claude-logs/baton/<YYYY-MM-DD>_<任務編碼>_design_spec.md`**（任務代號未定時用 `TBD`）。
- **嚴禁** 落 `docs/superpowers/`（superpowers 預設落點，本專案不用）。
- baton/ 平時為空原則不變：spec 屬暫存原料，於其消費任務 Checkout 時隨該任務歸檔或按 baron 指示處置。

### §3.2 溯源 header 樣板（強制·滿足 `baton/README.md §2` Provenance 自檢）

每份 spec **頂部必附**：

```markdown
---
產出工具：brainstorming SOP（vendored superpowers brainstorming·不裝 plugin）
產出時間：<YYYY-MM-DD HH:MM UTC+8>
產出情境：<本次發散的 session 描述 / baron 指定代號>
參考來源：<若引用論文 / audit / 外部工具則列來源；純問答發散則寫「brainstorming 問答」>
任務代號：<TYPE-N（若已定）或 TBD>
---
```

---

## §4 spec → template_plan 欄位對照與兩護欄

### §4.1 欄位對照表

| `template_plan` 章節 | spec 是否供給 | 階段 1 補強動作 |
|---|---|---|
| §2 目標規格 | ✅ 直接來 | 轉錄選定方案與量化目標 |
| §2.5 候選方案（Diverse Rollout） | ✅ 直接來 | 轉錄 §2 步驟 3 的方案權衡與否決留痕 |
| §9 Open Questions | 🟡 半給 | 澄清問答未決者轉「問題+推薦+理由」三欄 |
| §3 現況與證據（grep 行號） | ❌ 不供給 | **階段 1 自行 grep 補**（`CLAUDE.md §1.7`） |
| §4 跨 Phase 接縫契約 | ❌ 不供給 | **階段 1 凍結**（`WORKFLOW_SOP §7`） |
| §6 不可動清單 | ❌ 不供給 | **階段 1 劃定** |
| §8 驗證計畫（pytest / E2E / SOP 核查） | ❌ 不供給 | **階段 1 補** |

### §4.2 兩條護欄（不可鬆手）

1. **原料 ≠ plan**：spec 是輸入、不是 plan 半成品。上表四樣 ❌（grep 證據 / 接縫契約 / 不可動清單 / 驗證計畫）**只能在階段 1 手工長出、嚴禁從鬆散 spec 繼承**。spec 再完整都不得跳過階段 1 的嚴謹層。
2. **原料必帶溯源 header**：無 §3.2 header 之 spec 過不了 `baton/README.md §2 Phase 2` Provenance 自檢，不得作為 plan 依據。

---

## §5 視覺伴讀（畫圖·可選增強）

當某問題「用看的比用讀的更好懂」（UI 線框 / 架構圖 / 並排比較 / 空間關係）時啟用；純需求釐清 / 概念選型 / 取捨分析留在終端問答即可。**just-in-time 提供、不預設開**。

- **操作指引**：見 `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md`（vendored·路徑已改指本專案）。
- **腳本位置**：`.claude-logs/tools/`（`start-server.sh` / `stop-server.sh` / `server.cjs` / `helper.js` / `frame-template.html`，BRAINSTORM-1 C2 導入）。
- **環境前置**：需 **Node ≥ 12**（`server.cjs` 零 npm 相依）；缺 Node 僅失去畫圖、**問答主體零依賴不受影響**。
- **mockup 落點**：`.claude-logs/baton/.brainstorm/<session>/`（`baton/*` 已 gitignored、天然不入版控）；session 結束 / Checkout 前清空、守 baton 平時為空。

---

## §6 禁令（與 superpowers 預設之差異）

- ❌ **不 auto-commit**：superpowers 原流程產 spec 後會 `git commit`；本專案**移除此步**，所有 commit 由 baron 手動（`CLAUDE.md §1.3`）。
- ❌ **不裝 plugin**：本 SOP 以 vendored 檔案運作，不透過 marketplace 安裝 superpowers（避免 14-skill 自動觸發污染、遙測外送）。
- ❌ **不接執行鏈**：brainstorming 之後唯一動作是進階段 1 plan；嚴禁自動接 tasks / execution / worktree / subagent。

---

## §7 驗收檢查表

發散完成、交棒 plan 前自檢：

- [ ] spec 落 `.claude-logs/baton/`、命名合規、**含 §3.2 溯源 header**
- [ ] 關鍵決策已攤 2-3 方案 + 推薦 + 否決留痕
- [ ] 自檢無 placeholder / 矛盾 / 模糊 / scope 溢出
- [ ] baron 已核准 spec
- [ ] 四樣護欄欄位（grep 證據 / 接縫契約 / 不可動清單 / 驗證計畫）**確認留待階段 1**、未在 spec 內偽裝完成
- [ ] 未 auto-commit、未接執行鏈

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 規範 brainstorming 設計發想作業（問答骨架 / 落點 / 溯源 / 護欄 / 視覺伴讀），產 design spec 作為階段 1 plan 之原料 |
| **用途** | workflow-gated：發散階段按需取用；**不進 CLAUDE.md @path 自動載入**（不污染 session context、對齊 CONTEXT-1 瘦身方向） |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 視覺伴讀指引 `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md` |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | spec 落點唯一源在本檔 §3；兩護欄唯一源在本檔 §4.2；不重寫 template_plan / WORKFLOW_SOP / baton README 既有規格（僅引用） |
| **改版觸發條件** | §1–§7 任一規範變動 / 上游 superpowers 同步 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 不刪（brainstorming 作業長期規範） |
| **重複防護** | 落點/溯源/護欄唯一源在本檔；plugin 不裝之決策依據見 BRAINSTORM-1 plan §2.5 |

### §99.2 Revision 歷程

- v1 (2026-07-18)：BRAINSTORM-1 C1 初版建立（蒸餾 superpowers brainstorming 問答骨架 + 落點改導 `.claude-logs/baton/` + 溯源 header 樣板 + spec→template_plan 對照 + 兩護欄 + 移除 auto-commit + 視覺伴讀章指向 vendored 指引；全文完整根路徑防呆）
