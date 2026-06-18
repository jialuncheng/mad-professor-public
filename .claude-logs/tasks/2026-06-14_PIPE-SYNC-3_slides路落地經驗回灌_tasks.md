# PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC — Tasks

> 本文件為 PIPE-SYNC-3 的 Commit 拆分清單（階段 2 產出）。
> 依據 plan：`.claude-logs/baton/2026-06-14_PIPE-SYNC-3_slides路落地經驗回灌母plan與SPEC_plan_v1.md`（v3、D1-D7、六 OQ 全定案）。
> 含 3 個 Commit（C1 SPEC 同步 → C2 master plan 同步 → C3 Checkout）。

---

## §0 改版規則
- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （純真理源回灌、無新檔；報告暫存 baton/）|
| **修改檔案** | 2 個 | `baton/2026-06-01_PIPE-SPEC_..._specification.md`（C1：D1/D3/D4/D6/D7/D5 + bump v7）/ `plans/2026-06-01_PIPE_..._plan_v10.md`（C2：D2 §8.5 措辭 + 補註⁸）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（PIPE-SYNC-3 進度 + 結案）/ `prompts/INDEX.md`（Tasks 提示詞已歸檔）|
| **Commits** | 3 個 | C1（SPEC v7 同步）→ C2（master plan 補註⁸）→ C3（Checkout 收官）|
| **baton 歸檔** | 1 次 | C3 收官：`mv` baton（plan/tasks/C1-C3 報告）→ `plans/`+`tasks/`+`executions/` + `git add`；**SPEC 本體（長駐 baton）僅就地 git add 不 mv** |

---

## §1 TL;DR（概要）

- **挑戰**：slides 路 7 次 hotfix 落地後，兩真理源（PIPE-SPEC / master plan v10）有 2 真理源錯誤（D1 SPEC slides P3「100% Bypass」drift、D2「B 軌另捕」A/B 軌 golden 混淆）+ 4 缺口（D3 alt LaTeX 跨軌契約 / D4 is_blank / D6 rag_sections 旁路未登記 / D7 rag_tree_json 含糊）+ 1 可選（D5 清洗層），不回灌則下一路 PIPE-ACADEMIC 被誤導。
- **解法**：DOC-Refactor 兩真理源就地回灌，原子化為 3 commit：
  - **C1 — SPEC v7 同步（SPEC 真理源回灌）**：D1 drift 矯正 + D2 golden 釐清(SPEC 側) + D3 alt LaTeX + D4 is_blank + D6 rag_sections §1.1.2 + D7 rag_tree_json + D5 一行帶過 + bump v6→v7。
  - **C2 — master plan 補註⁸（母 plan 真理源回灌）**：D2 §8.5「B 軌另捕」措辭修正 + 補註⁸（不 bump 主版本）。
  - **C3 — Checkout 收官（驗收歸檔）**：Conformance + §7.2 DOC 豁免 + baton 一次性歸檔 + TODO 結案。
- **影響範圍**：100% DOC-Refactor、零 .py/.html/.css、零 golden（本案正是釐清 golden）；僅 SPEC + master plan 兩檔 + 狀態檔。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理 |
|---|---|---|
| SPEC L134 | SlidePipeline P3＝`100% Bypass 一鍵` | D1 drift（應 `逐頁翻譯與排版還原`）|
| SPEC §1.3.1 #3 / §2.4 | 無 A/B 軌 capture 釐清 | D2（加 golden A/B 軌權威句）|
| SPEC R3.2 (L210) | alt 對齊、無特殊字元後果 | D3（補 alt LaTeX/`][()` 前端保護契約）|
| SPEC §1.3.1 / L242 | 只記 is_cover | D4（補 is_blank 頁面類型判定）|
| SPEC §1.1（旁路登記） | 僅 §1.1.1 raw_metadata | D6（新增 §1.1.2 rag_sections）|
| SPEC §1.1③ (L66) | 「對應 JSON 節點」含糊 | D7（點名 rag_tree_json）|
| master plan v10 L258 | 「Golden Diff 通過（B 軌另捕…）」 | D2（措辭修正 + 補註⁸）|

> contracts.py 四凍結合約「型別欄位」皆最新（venue/doi/section_summaries/domain_name）、無 drift → **本任務不動 contracts.py 程式**。

---

## §3 觀察問題

### 問題 #1：真理源錯誤致下游誤導（D1/D2）
- **證據**：SPEC L134「100% Bypass」（PIPE-SLIDES C4 已改 per-page）；master plan L258「B 軌另捕」（capture 僅捕 A 軌）。
- **影響**：PIPE-ACADEMIC 等下一路依 SPEC 開發 → 重蹈 slides P3 + golden A/B 軌覆轍。

### 問題 #2：旁路登記不對稱（D6）
- **證據**：§1.1.1 已登記 raw_metadata 旁路；rag_sections（RAG-ASYNC C6、P3→P4、五路共用）僅在 §1.4.1 功能性提及、無 §1.1.x 登記。
- **影響**：「四合約 + 旁路」交接登記表不完整、P3→P4 真實側通道隱形。

---

## §4 設計方案

### §4.1 C1 — SPEC v7 同步
SPEC（`baton/2026-06-01_PIPE-SPEC_..._specification.md`）就地回灌 D1/D2(SPEC)/D3/D4/D6/D7/D5，HTML 註解包裹 `<!-- === [PIPE-SYNC-3 C1 ...] === -->`，bump §99.2 v6→v7。四凍結合約型別欄位零變動。

### §4.2 C2 — master plan 補註⁸
master plan v10（`plans/2026-06-01_PIPE_..._plan_v10.md`）§8.5 PIPE-SLIDES 條目 D2 措辭修正 + §99.2 加補註⁸（不 bump 主版本）。HTML 註解包裹。

### §4.3 C3 — Checkout 收官
Conformance（plan §2 U1-U8 / §6 grep / 不可動 / 提示詞稽核 / §7.2 DOC 豁免）+ baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| 誤動四凍結合約型別欄位 | 🟡 中 | C1 只動敘述/加註/旁路登記文字、不碰 §1.1 合約表型別欄;diff 自審合約 JSON 段未動;不改 contracts.py |
| 誤動 slides 以外路次條款 | 🟡 中 | C1 grep 自審只動 slides + golden + 旁路相關段;academic/book/resume 條款 diff 空 |
| 兩真理源版本/指標懸掛 | 🟢 低 | C1 SPEC bump v7、C2 master 補註⁸ 不 bump 主版本（同 PIPE-SYNC-2 慣例）;不動其他下游指標 |
| 純文件、零代碼 | 🟢 低 | DOC-Refactor;§7 鎖死 |

---

## §6 測試計畫

### §6.1 C1 驗收（SPEC）
```bash
SPEC=".claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md"
sed -n '/SlidePipeline/p' "$SPEC" | grep -q "逐頁翻譯與排版還原"   # D1：已矯正
sed -n '/SlidePipeline/p' "$SPEC" | grep -c "100% Bypass"        # D1：期望 0
grep -c "§1.1.2" "$SPEC"                                          # D6：rag_sections 旁路登記存在
grep -nE "rag_sections.*旁路|P3→P4 旁路" "$SPEC"                   # D6
grep -nE "renderMarkdownWithMath|_safe_alt" "$SPEC"               # D3：alt LaTeX 契約
grep -n "is_blank" "$SPEC"                                        # D4
grep -n "rag_tree_json" "$SPEC"                                   # D7（§1.1③ 點名）
grep -nE "capture.*A 軌|A 軌.*capture" "$SPEC"                     # D2：golden A/B 軌釐清
grep -n "PIPE-SYNC-3" "$SPEC"                                     # 包裹存在
grep -c "v7" "$SPEC"                                              # bump
```

### §6.2 C2 驗收（master plan）
```bash
PLAN=".claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md"
grep -c "B 軌另捕" "$PLAN"          # D2：期望 0（措辭已改）
grep -n "補註⁸\|PIPE-SYNC-3" "$PLAN"  # 補註⁸ + 包裹存在
```

### §6.3 全套件
```bash
git diff --name-only | grep -cE '\.py$|\.html$|\.css$'   # 期望 0（零代碼）
venv/bin/python -m pytest -q                              # 期望維持基線（旁證未誤動代碼）
```

### §6.4 C3 驗收
```bash
grep -rn "PIPE-SYNC-3" .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/  # baton 歸檔
git status -s   # 歸檔後乾淨
```

---

## §7 不可動清單

- [ ] **四凍結 JSON Schema 合約型別欄位**（contracts.py 程式 + SPEC §1.1 合約表型別欄）— 零變動。
- [ ] **業務代碼 / .py / .html / .css / static** — 零碰（純文件）。
- [ ] **slides 以外路次條款**（academic/book/resume/litedoc）+ **resume PIPE-SYNC-2 已回灌之 §1.3/key 契約** — 不動。
- [ ] **GOLDEN-BASELINE plan / 其他下游 plan / SOP 檔** — 不動（只動 SPEC + master plan 兩檔）。
- [ ] **SPEC 本體長駐 baton**（不 mv、收官僅就地 git add）— 維持。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — SPEC v7 同步（SPEC 真理源回灌）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（就地回灌 D1/D2-SPEC/D3/D4/D6/D7/D5 + §99.2 v7）+ `.bak`（`.claude-logs/archive/2026-06-14_PIPE-SYNC-3_C1_PIPE-SPEC.md.bak`、入 C1 git add）|
| **安全性** | 🟢 高 — 純文件、零 runtime;只動 slides/golden/旁路相關敘述、不碰合約型別欄 |
| **可逆性** | 🟢 高 — `git revert C1` 或自 `.bak` 還原 |
| **驗收 grep 條件** | §6.1（D1 0 命中 Bypass / §1.1.2 rag_sections / alt 契約 / is_blank / rag_tree_json / golden A/B / v7）|
| **依賴關係** | 無前置 |
| **具體實作細節** | 依 plan §2：**D1** §1.3 表 SlidePipeline 列 P3「100% Bypass 一鍵」→「逐頁翻譯與排版還原」;**D2** §1.3.1 #3 golden 句擴充加 A/B 軌權威釐清（`capture <route>` 一律捕 A 軌舊單體、B 軌變更不需/無法經 capture 重捕、走影子 E2E + diff A 軌 golden + 改善豁免）;**D3** R3.2 後補跨軌契約註（alt 可能含 LaTeX `$...$`/`][()` → 前端 renderMarkdownWithMath 抽 math 前保護圖片整段〔RAG-12-HOTFIX-1〕+ B 軌 `_safe_alt` 全形化〔HOTFIX-2〕）;**D4** §1.3.1 提煉第 4 原則「頁面類型判定（is_blank/is_cover）供管線過濾」+ L242 一句指回（is_blank=true 空白/裝飾/過場頁〔含有標題過場頁〕→ 跳過；HOTFIX-4/5）;**D6** §1.1 新增 §1.1.2 `PipelineContext.rag_sections`（P3→P4 旁路、五路共用、對稱 §1.1.1：P3 產譯後 section〔summary_key=原文標題 path/slides page_key〕、P4 rag_indexer 消費；非凍結合約欄）;**D7** §1.1③「對應 JSON 節點」點名 `rag_tree_json`（可選欄）;**D5** SlidePipeline 列/§1.3.1 一行帶過「P3 含 slides 專屬排版噪聲清洗層」（Q4 至多一行）;全部 `<!-- === [PIPE-SYNC-3 C1 ...] === -->` 包裹;§99.2 加 v7 條目。 |

### C2 — master plan 補註⁸（母 plan 真理源回灌）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（§8.5 D2 措辭 + §99.2 補註⁸）+ `.bak`（`.claude-logs/archive/2026-06-14_PIPE-SYNC-3_C2_plan_v10.md.bak`、入 C2 git add）|
| **安全性** | 🟢 高 — 純文件、不 bump 主版本（防下游指標級聯漂移）|
| **可逆性** | 🟢 高 — `git revert C2` 或自 `.bak` 還原 |
| **驗收 grep 條件** | §6.2（「B 軌另捕」0 命中 / 補註⁸ + PIPE-SYNC-3 包裹）|
| **依賴關係** | 前置 C1（SPEC 已立 golden A/B 軌權威句、master plan 措辭指向之）|
| **具體實作細節** | §8.5 PIPE-SLIDES 條目「Golden Diff 通過（**B 軌另捕**、改善豁免＝plan Q8）」→ 措辭修正為「（capture 僅捕 A 軌正本基準；B 軌不另捕、走 B 軌 shadow 輸出 diff A 軌 golden + 改善豁免＝plan Q8）」;`<!-- === [PIPE-SYNC-3 C2 ...] === -->` 包裹;§99.2 加**補註⁸**（不 bump 主版本、對齊補註⁶/⁷ 慣例、記 D2 措辭修正承 HOTFIX-6 A/B 軌更正）。 |

### C3 — Checkout 收官（驗收歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（PIPE-SYNC-3 → ✅）;baton 一次性 `mv` 歸檔（plan→`plans/`、tasks→`tasks/`、C1-C3 報告→`executions/`）;SPEC 本體就地 git add 不 mv |
| **安全性** | 🟢 高 — 純文件歸檔/狀態 |
| **可逆性** | 🟢 高 — 文件操作可逆 |
| **驗收 grep 條件** | §6.4（baton 歸檔 + git status 乾淨）|
| **依賴關係** | 前置 C1、C2 ship |
| **具體實作細節** | 1. Conformance 五維度：① 目標規格 plan §2 U1-U8 ② §6 grep 全綠 + 全套件 pytest 維持基線（零 .py/.html/.css diff）③ 不可動（合約型別欄/其他路次/contracts.py 零變動）④ 提示詞稽核（plan/tasks/C1-C2 run + Check）⑤ **§7.2 顯式豁免**（DOC-Refactor、無 code handoff、同 PIPE-SYNC-2 先例）。2. baton 一次性 mv + git add（plan/tasks/執行報告 + 2 .bak）;SPEC 本體就地 git add（長駐 baton 不 mv、同 PIPE-SYNC-2 先例 195e12b）。3. TODO 結案（active 移除 → ✅ 完成表，hash 待 baron 回填）+ §99.2/INDEX 補 Check 提示詞。4. git log hash 自癒回填。 |

---

## §9 Open Questions

無。（plan v3 §9 六 OQ 已全 🟢 baron 拍板定案；D6/D7 方案明確、無新 OQ。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SYNC-3 原子 Commit 拆分與實作細節，作為執行期唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8（設計規格權威源為 plan v3 §2）|
| **引用方** | 後續 PIPE-SYNC-3 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁動四凍結合約型別欄位/contracts.py 程式/業務代碼/slides 以外路次;只動 SPEC + master plan 兩檔;baton 一律 Check 才歸檔 |
| **改版觸發條件** | plan 規格變動 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔、經 baron 同意移 archive/ |
| **重複防護** | 回灌內容唯一源為各 hotfix 文件 + plan v3；本 tasks 僅定義「改哪檔哪段」、不重寫 hotfix/plan 細節 |

### §99.2 Revision 歷程
- v1 (2026-06-14)：初版拆分（3 commit：C1 SPEC v7 同步〔D1/D2-SPEC/D3/D4/D6/D7/D5〕/ C2 master plan 補註⁸〔D2 §8.5〕/ C3 Checkout；§7.2 DOC 豁免；只動 SPEC + master plan 兩檔、四凍結合約型別欄位零變動）
