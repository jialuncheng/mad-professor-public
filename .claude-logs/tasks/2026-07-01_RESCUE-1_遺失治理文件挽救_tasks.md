# RESCUE-1 遺失治理文件挽救 — Tasks

> 本文件為 RESCUE-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-28_RESCUE-1_遺失治理文件挽救_plan_v1.md`（v1.2）產出，含 5 個 Commit（C1–C4 + C5 Checkout）。
> **工作目錄（baron 拍板覆蓋 CLAUDE.md §3）**：主 repo `~/mad-professor-public/`（`gemini-refactor`）；授權範圍**僅限** `.claude-logs/{baton,archive}` + `TODO.md`。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 3 個 | `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（U2 重建 v8 本體·長駐 baton）/ `archive/2026-07-01_RESCUE-1_C1_QUEUE-1_v2_plan.md.bak`（U1 審計）/ `archive/2026-07-01_RESCUE-1_C2_PIPE-SPEC_v8.md.bak`（U2 審計） |
| **修改檔案** | 1 個 | `TODO.md`（U4 active 失效引用總修正 + U5 遺失清單尾註） |
| **移動檔案** | 1 個 | `baton/2026-05-27_MODEL-10_..._plan.md` → `archive/`（U3 殘留清理·tracked 審計） |
| **目錄初始化** | 0 個 | 皆用既有 `baton/` `archive/` |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1 → C2 → C3 → C4 → C5 Checkout |
| **baton 歸檔** | 1 次 | C5 Checkout 一次性 mv：plan → `plans/`、tasks → `tasks/`、C1–C5 執行報告 → `executions/` + `git add`（PIPE-SPEC v8 本體與 QUEUE-1 v2 依 Q3 **維持 baton 長駐、不歸檔入版控**） |

---

## §1 TL;DR（概要）

- **挑戰**：舊 worktree 刪除致 git-ignored `baton/` 未收官文件遺失；4 份治理文件真遺失、2 份實體存活主 repo baton（QUEUE-1 v2 / MODEL-10）、PIPE-SPEC 本體遺失但存 v7 `.bak` + C2 執行報告可機械重建；TODO active 存 3 條失效引用。
- **解法**：拆為 5 個小步 commit——C1 救回存活之 QUEUE-1 v2（+archive `.bak`）；C2 依 v7 `.bak` + C2 執行報告 D5-D8.1 + 對照現役 code 重建 PIPE-SPEC v8（+archive `.bak`）；C3 清理已收官 MODEL-10 殘留（mv→archive）；C4 總修正 TODO 失效引用 + 遺失清單尾註；C5 Checkout 收官歸檔。
- **影響範圍**：100% `.claude-logs/`（baton / archive / TODO.md）；**零 `.py` / 零 `static/` / 零業務代碼 / 零 schema / 零 API**；無 runtime 影響。
- **不可動清單**：見 §7

### Commit 序列（含中文括號命名）

- C1 — Restore Queue v2（還原 QUEUE-1 v2 雙實例排程計畫）
- C2 — Rebuild PIPE-SPEC v8（重建共用真理源規格書 v8）
- C3 — Purge MODEL-10 Residue（清理已收官殘留）
- C4 — TODO Reconciliation（TODO 狀態與遺失清單總修正）
- C5 — Checkout（收官與歸檔）

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `baton/…QUEUE-1_雙實例CFS…_plan.md` | 主 repo baton 存活（9890 bytes） | 尚無 archive `.bak` 審計副本（U6 防再遺失閘門缺） |
| PIPE-SPEC 本體 | 遺失；存 v7 `.bak`（archive·36172 bytes）+ C2 執行報告 D5-D8.1 | v8 本體須依 `.bak`(v7) + 變更清單重建 |
| `baton/…MODEL-10…_plan.md` | 已收官任務之 baton 殘留（15313 bytes） | 應清出 baton→archive（tracked 審計） |
| `TODO.md` active 區 | CHAT-STRUCT-1 / QUEUE-1(v1) / INFRA-2 指向已遺失/作廢 baton 路徑 | 失效引用未修正；無真遺失審計留痕 |

---

## §3 觀察問題

### 問題 #1：存活文件無防再遺失閘門
- **證據**：`ls .claude-logs/baton/` → QUEUE-1 v2 + MODEL-10 存活，但 `git check-ignore` 證其被 `baton/*` 排除、不入版控。
- **影響**：下次 worktree/目錄異動即再遺失、無 tracked 還原保險。

### 問題 #2：PIPE-SPEC 本體遺失、v8 僅存於 .bak(v7) + 執行報告
- **證據**：`git ls-files | grep PIPE-SPEC` → 僅 `archive/…C2_PIPE-SPEC.md.bak`（v7）；plans/ 無本體。
- **影響**：現役共用真理源家族規格（section_engine/MetaNormalizer 契約章）無完整可查本體。

### 問題 #3：TODO active 失效引用誤導
- **證據**：TODO L1013/L1019/L1028-1031 指向已遺失/作廢 baton plan 路徑。
- **影響**：未來啟動任務點擊失效路徑、狀態真理源失真。

---

## §4 設計方案

> 依賴鏈：C1–C4 各自獨立（無強前後序、但 commit 序線性以利驗收）；C5 依賴 C1–C4 全數完成。
> **共通約束**：所有操作限主 repo `.claude-logs/{baton,archive}` + `TODO.md`；各 Commit 執行報告暫存 baton、C5 才歸檔。

### §4.1 C1 — Restore Queue v2（U1 + U6 part）
- QUEUE-1 v2 本體**逐字保全**留置 baton（不動內容、不 mv）。
- 複製一份 tracked 審計副本 → `archive/2026-07-01_RESCUE-1_C1_QUEUE-1_v2_plan.md.bak` + `git add`。
- 驗證救援前後本體 byte 未變（9890）。
- 報告：`baton/2026-07-01_RESCUE-1_C1_執行.md`。

### §4.2 C2 — Rebuild PIPE-SPEC v8（U2 + U6 part）
- 以 `archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak`（v7）為基底，套 C2 執行報告 D5-D8.1 變更重建 v8 本體至 `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`：
  - **D5** 新增 §1.2.5 section_engine 契約章（三簇介面 + 四鐵律〔零 doc_type / 接縫 key=原文標題 path / Zero Schema Coupling / restore 不產 rag 副作用〕+ consumer）——對照現役 `pipelines/section_engine.py` 語意忠實。
  - **D5b** 新增 §1.2.4 MetaNormalizer 契約章（normalize_fields 三路分流 BS1/Q9/BS4 + MetaField/MetaFieldAlias schema + LLM 交易外/temp=0）——對照現役 `processor/meta_normalizer.py`。
  - **D6** §1.1.1 登記 LiteDoc 旁路欄位（date/url/publisher/translated_title）。
  - **D7** 「三大共用真理源」→「共用真理源家族」（§1.2 標題 + §0）。
  - **D8** §99.2 加 v8 Revision。
  - **D8.1 不改項（逐字守 .bak 原值）**：§1.3 L140 `news/web/未知 fallback`、§3.3 15k 安全閥門、§2/表 `≥ 10` 門檻、四凍結合約結構——**嚴禁趁重建竄改**。
- 複製 v8 本體 tracked 審計副本 → `archive/2026-07-01_RESCUE-1_C2_PIPE-SPEC_v8.md.bak` + `git add`。
- **誠實標註非 byte-identical**（Q2：D5/D5b 為對照 code 重寫、非逐字還原）。
- 報告：`baton/2026-07-01_RESCUE-1_C2_執行.md`。

### §4.3 C3 — Purge MODEL-10 Residue（U3）
- `mv baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md archive/` + `git add`（tracked 審計、不直接刪除）。
- 驗證 baton 不再含 MODEL-10、archive 含之。
- 報告：`baton/2026-07-01_RESCUE-1_C3_執行.md`。

### §4.4 C4 — TODO Reconciliation（U4 + U5）
- **active 區失效引用總修正**（僅動 active 區，頂部 ✅ 表格與既有 hash 零改）：
  - INFRA-2 → 標「原 plan 已隨 worktree 遺失；產出物已由 PIPE-SPEC / PIPE-CORE 取代」+ active 移除。
  - QUEUE-1(v1) → 標「原 plan 已遺失；經 PIPE-SPEC §3.1 審計判定『重構性廢除』」+ active 移除。
  - QUEUE-1 v2 → active 新增/校正條目，指向 baton 存活本體（MinerU 雙實例 CFS 物理分流）。
  - INFRA-4 → 正名「尚未撰寫之未來任務（合約轉正旁路收合）」、明載**非遺失**。
  - CHAT-STRUCT-1 / TRANSLATE-BOOK v7 / INFRA-3 → 失效 baton 路徑就地標「原 plan 已隨 worktree 遺失、待獨立重建」。
- **U5 遺失清單尾註**：TODO 末尾新增「2026-06 worktree 刪除遺失清單」（CHAT-STRUCT-1 / TRANSLATE-BOOK v5+v7 / INFRA-2 / INFRA-3 / QUEUE-1 v1 / YuLun_Wu_CV_chat.md / 工作筆記 + 處置：重建/取代/廢除/放棄）。
- 報告：`baton/2026-07-01_RESCUE-1_C4_執行.md`。

### §4.5 C5 — Checkout（收官與歸檔）
- Conformance 三維度（目標規格 U1-U6 / §6 驗收 grep / 不可動清單）。
- §7.2 純 DOC-Refactor、無 code handoff → **顯式豁免**（Q4）。
- baton 一次性 mv：plan→`plans/`、tasks→`tasks/`、C1–C5 報告→`executions/` + `git add`。**PIPE-SPEC v8 本體 + QUEUE-1 v2 依 Q3 維持 baton 長駐不歸檔入版控**（其 tracked 保險為 archive `.bak`）。
- TODO 結案（RESCUE-1 移入 ✅ 完成表 + 索引 + hash 自癒）。
- 報告：`baton/2026-07-01_RESCUE-1_C5_執行.md`。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 主 repo 操作越授權範圍 | 🟡 中 | 嚴格限 `.claude-logs/{baton,archive}` + `TODO.md`；業務碼/工作樹/✅ 表格零碰（§7） |
| PIPE-SPEC v8 非逐字還原 | 🟡 中 | D8.1 不改項逐字守 .bak；D5/D5b/D6 對照現役 code + C2 執行報告；誠實標註非 byte-identical |
| 存活文件再遺失 | 🟡 中 | archive `.bak` tracked 審計為唯一還原閘門（U6）；不破 baton 長駐先例 |
| TODO 誤動已收官表格/hash | 🟢 低 | 僅動 active 區 + 尾註；`git diff` 驗頂部 ✅ 表格與 hash 零改 |

---

## §6 測試計畫

> 純 .md 文件治理、零業務代碼；以 DOC-Refactor §6.1 驗證清單 + grep 為驗收主軸（pytest 基線不退化、非驗收主軸）。

### §6.1 C1 驗收
```bash
ls -la .claude-logs/baton/2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md   # 期望：存在、9890 bytes 不變
ls -la .claude-logs/archive/2026-07-01_RESCUE-1_C1_QUEUE-1_v2_plan.md.bak              # 期望：archive .bak 存在
git check-ignore -v .claude-logs/baton/2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md  # 期望：baton/* 命中（不入版控）
```

### §6.2 C2 驗收
```bash
grep -nE "§1.2.5|section_engine|§1.2.4|MetaNormalizer|§1.1.1|共用真理源家族|§99.2" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md  # 期望：D5-D8 命中
grep -nE "v8 \(2026" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md  # 期望：v8 Revision
grep -nE "news/web/未知|15k|15,000|≥ ?10" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md  # 期望：D8.1 不改項守住（對照 .bak 原值）
ls -la .claude-logs/archive/2026-07-01_RESCUE-1_C2_PIPE-SPEC_v8.md.bak                 # 期望：archive .bak 存在
```

### §6.3 C3 驗收
```bash
ls .claude-logs/baton/ | grep -c MODEL-10          # 期望：0（baton 已清）
ls .claude-logs/archive/ | grep MODEL-10           # 期望：archive 含之
```

### §6.4 C4 驗收
```bash
grep -nE "INFRA-2|QUEUE-1|INFRA-4|CHAT-STRUCT-1|TRANSLATE-BOOK|INFRA-3" .claude-logs/TODO.md | grep -E "遺失|廢除|取代|非遺失|待獨立重建"  # 期望：狀態標註到位
grep -n "2026-06 worktree 刪除遺失清單" .claude-logs/TODO.md   # 期望：尾註存在
git diff .claude-logs/TODO.md | grep -E "^\-.*`[0-9a-f]{7}`" | head  # 期望：無（頂部 ✅ 表格 hash 零刪改）
```

### §6.5 C5 收官驗收
```bash
ls .claude-logs/baton/ | grep -c RESCUE-1          # 期望：0（plan/tasks/報告已歸檔；PIPE-SPEC/QUEUE-1 依 Q3 長駐、非 RESCUE-1 前綴）
ls .claude-logs/plans/ | grep RESCUE-1             # 期望：plan 已歸檔
ls .claude-logs/executions/ | grep -c RESCUE-1     # 期望：5（C1-C5 報告）
```

---

## §7 不可動清單

**以下檔案與邏輯在本案中嚴禁任何改動：**

- [ ] **業務代碼**：任何 `.py`（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `pipelines/*.py`）/ `static/*` — 100% 不動
- [ ] **主 repo 授權範圍外一切檔案**：僅 `.claude-logs/{baton,archive}` + `TODO.md` 可寫（§9 Q1）；工作樹 / 業務碼嚴禁碰
- [ ] **`TODO.md` 頂部 `## ✅ 已完成` 既有表格與所有既有 Commit Hash** — 僅動 active 區與新增審計尾註
- [ ] **PIPE-SPEC v8 之 D8.1 不改項**（§1.3 L140 news/web/未知 + §3.3 15k + §2/表 ≥10 + 四凍結合約結構）— 逐字守 `C2.bak` 原值
- [ ] **既有 `archive/` 內所有 `.bak` 與長駐真理源** — 僅**新增**審計副本，不改既有
- [ ] **`.gitignore` `baton/*` 排除規則與 PIPE-SPEC「長駐 baton 不版控」先例** — 本案不破例

---

## §8 推薦 Commit 拆分

### C1 — Restore Queue v2（還原 QUEUE-1 v2 雙實例排程計畫）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `archive/2026-07-01_RESCUE-1_C1_QUEUE-1_v2_plan.md.bak`；`baton/…QUEUE-1…_plan.md` 本體**不動**（僅讀取複製） |
| **安全性** | 🟢 高 — 純複製、不改本體、零 runtime |
| **可逆性** | 🟢 高 — 刪 `.bak` 即復原 |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `cp` QUEUE-1 v2 本體 → `archive/2026-07-01_RESCUE-1_C1_QUEUE-1_v2_plan.md.bak` + `git add`；② 驗本體仍 9890 bytes、`git check-ignore` 證 baton 排除不變；③ 本體逐字保全、不 mv、不改。**執行報告暫存 `baton/2026-07-01_RESCUE-1_C1_執行.md`** |

### C2 — Rebuild PIPE-SPEC v8（重建共用真理源規格書 v8）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（v8 本體）+ `archive/2026-07-01_RESCUE-1_C2_PIPE-SPEC_v8.md.bak` |
| **安全性** | 🟡 中 — 重建含重寫（D5/D5b），須對照現役 code + .bak 保真 |
| **可逆性** | 🟢 高 — 刪重建本體與 `.bak` 即復原（未動任何既有檔） |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 無前置（可與 C1 並行；commit 序線性） |
| **具體實作細節** | ① 讀 `archive/…C2_PIPE-SPEC.md.bak`(v7) 為基底；② 依 §4.2 套 D5/D5b/D6/D7/D8 變更〔D5 對照 `pipelines/section_engine.py`、D5b 對照 `processor/meta_normalizer.py` 語意忠實重寫契約章〕；③ **D8.1 不改項逐字守 .bak 原值**（§1.3 L140 / §3.3 15k / ≥10 / 四凍結合約結構）；④ 寫入 baton 本體；⑤ `cp` 本體 → `archive/2026-07-01_RESCUE-1_C2_PIPE-SPEC_v8.md.bak` + `git add`；⑥ 報告誠實標註非 byte-identical。**執行報告暫存 `baton/2026-07-01_RESCUE-1_C2_執行.md`** |

### C3 — Purge MODEL-10 Residue（清理已收官殘留）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv baton/2026-05-27_MODEL-10_…_plan.md → archive/`（+ `git add`） |
| **安全性** | 🟢 高 — 已收官任務殘留、archive 保留審計 |
| **可逆性** | 🟢 高 — `mv` 回 baton 即復原 |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `mv .claude-logs/baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md .claude-logs/archive/`；② `git add` archive 落點（tracked 審計、不直接刪除）；③ 驗 baton 無 MODEL-10、archive 含之。**執行報告暫存 `baton/2026-07-01_RESCUE-1_C3_執行.md`** |

### C4 — TODO Reconciliation（TODO 狀態與遺失清單總修正）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（active 區失效引用 + 末尾遺失清單尾註；頂部 ✅ 表格零改） |
| **安全性** | 🟢 高 — 純文件、僅動 active 區與尾註 |
| **可逆性** | 🟢 高 — `.bak` 還原 |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | 無前置（描述引用 C1/C3 落點狀態，建議序後於 C1–C3） |
| **具體實作細節** | ① 改前 `cp TODO.md → archive/…C4_TODO.md.bak`；② 依 §4.4 修 active：INFRA-2 結案移除 / QUEUE-1(v1) 廢除移除 / QUEUE-1 v2 新增校正指 baton 存活本體 / INFRA-4 正名非遺失 / CHAT-STRUCT-1·TRANSLATE-BOOK v7·INFRA-3 就地標「隨 worktree 遺失待重建」；③ 末尾新增「2026-06 worktree 刪除遺失清單」尾註（含處置）；④ `git diff` 驗頂部 ✅ 表格 hash 零刪改。**執行報告暫存 `baton/2026-07-01_RESCUE-1_C4_執行.md`** |

### C5 — Checkout（收官與歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` 結案 + `prompts/INDEX.md` + baton 一次性 mv 歸檔（plan/tasks/C1–C5 報告） |
| **安全性** | 🟢 高 — 文件歸檔 |
| **可逆性** | 🟢 高 — git 可回溯 |
| **驗收 grep 條件** | §6.5 + 跨 §6.1–§6.4 全綠 |
| **依賴關係** | 依賴 C1–C4 全數完成 |
| **具體實作細節** | ① Conformance 三維度（目標規格 U1-U6 / §6 grep / 不可動清單）；② §7.2 純 DOC 顯式豁免（Q4）；③ baton 一次性 mv：`plan→plans/`、`tasks→tasks/`、`C1–C5 報告→executions/` + `git add`；**PIPE-SPEC v8 本體 + QUEUE-1 v2 依 Q3 維持 baton 長駐、不歸檔入版控**；④ TODO：RESCUE-1 移入 ✅ 完成表 + 索引 + hash 自癒；⑤ msg 草稿 /tmp、不自發 commit。**執行報告暫存 `baton/2026-07-01_RESCUE-1_C5_執行.md`（隨本階段一併 mv→executions/）** |

---

## §9 Open Questions

無。（plan v1.2 §9 六 Open Questions 已全數由 baron 拍板定案為「拍板定案之設計決策」：Q1 主 repo 授權 / Q2 對照 code 重寫 / Q3 baton 慣例 + archive .bak / Q4 §7.2 豁免 / Q5 MODEL-10 就地 mv / Q6 TODO 就地標註 + 尾註。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESCUE-1 遺失治理文件挽救的原子 Commit 拆分清單與實作細節 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RESCUE-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁碰主 repo 授權範圍外檔案；嚴禁動 TODO 頂部 ✅ 表格與既有 hash；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-01)：初版拆分完成——依 plan v1.2 拆 5 commit（C1 QUEUE-1 v2 救回 + archive .bak / C2 PIPE-SPEC v8 重建〔D5-D8.1、對照現役 code〕+ archive .bak / C3 MODEL-10 殘留 mv→archive / C4 TODO 失效引用總修正 + 遺失清單尾註 / C5 Checkout）；U1-U6 全覆蓋；Q1-Q6 已定案落 commit。
