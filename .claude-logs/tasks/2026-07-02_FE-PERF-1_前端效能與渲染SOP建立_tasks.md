# FE-PERF-1 前端效能與渲染 SOP 建立 — Tasks

> 本文件為 FE-PERF-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_plan_v1.md`（內部 v2、§9 六 OQ 全定案）產出，含 3 個 Commit（C1 → C2 → checkout）。
> 工作流：DOC-Refactor。**純文件、零業務代碼、零 runtime、零 golden 重捕。**

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `.claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（前端效能與渲染 SOP·長駐 sop/、C1 產出即版控） |
| **修改檔案** | 1 個 | `.claude-logs/ref/WORKFLOW_SOP.md`（§1.1/§1.4「必讀 SOP」欄回填 + §99.2 Revision） |
| **目錄初始化** | 0 個 | 無（sop/ 既存） |
| **狀態更新** | 2 個 | `TODO.md`（本階段即時 🟡 WIP、checkout 轉 ✅）/ `prompts/INDEX.md`（已於歸檔同步） |
| **Commits** | 3 個 | C1 → C2 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` plan_v1 → `plans/` + tasks → `tasks/` + C1/C2 執行報告 → `executions/` + `git add`（SOP 手冊與 WORKFLOW_SOP 於 C1/C2 已就地版控、不在此列） |

---

## §1 TL;DR（概要）

- **挑戰**：WORKFLOW_SOP §1.1（FE-Refactor）/ §1.4（FE-Hotfix）「必讀 SOP」欄皆「—」（後端有兩份 SOP、前端零），且前端渲染/效能教訓散落各 hotfix、Osmani 稽核 8 findings 未凝練為 FE 落地前可打勾準則。
- **解法**：拆 3 原子 commit 落地——
  - **C1 — SOP Authoring（新建前端效能與渲染 SOP 手冊）**：於 `sop/` 產出手冊（效能 7 條紅線 + 渲染正確性陷阱 + 驗收檢查表 + §99.1 重複防護）。
  - **C2 — Workflow Backfill（回填 WORKFLOW_SOP FE 必讀 SOP）**：§1.1/§1.4 兩格「—」→ 手冊路徑 + §99.2 加 Revision。
  - **checkout — 成果收官歸檔（成果歸檔與移出暫存）**：Conformance 驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。
- **影響範圍**：100% DOC-Refactor / 零業務代碼 / 零 runtime / 零 schema / 零 golden 重捕。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `ref/WORKFLOW_SOP.md` §1.1 / §1.4 | FE-Refactor / FE-Hotfix「必讀 SOP」欄＝「—」 | 前端工作流無強制 SOP（後端有 logging/database 兩份），治理不對稱缺口 |
| `sop/`（logging/database/mineru 三份） | 皆 workflow-gated、§0/§99 結構、~8–10KB | **無**前端效能/渲染 SOP |
| `design/docs/`（11 份） | 視覺/元件/token/互動設計系統真理源 | 無一談效能與瀏覽器渲染管線（範疇不含） |
| `baton/frontend_browser_standards_audit.md` | Osmani 稽核 8 findings + Priority Matrix（已補串流 O(n²)） | 為稽核產物、非工作流可強制引用之 SOP |
| `static/index.html`（3835 行） | 存串流每 token 重排、head 同步 CDN script、`transition:width`、rAF=0 | 作 SOP 反例錨點來源（本案不修 code、僅立規引用行號） |

---

## §3 觀察問題

### 問題 #1：FE 工作流無強制 SOP（治理不對稱）
- **證據**：`ref/WORKFLOW_SOP.md` §1.1 FE-Refactor 與 §1.4 FE-Hotfix「必讀 SOP」欄皆「—」；`sop/` 僅 logging/database/mineru 三份後端向。
- **影響**：前端改動無落地前準則可依，渲染正確性 bug 反覆由 baron QA 才抓到。

### 問題 #2：渲染教訓散落、path #2 重蹈 path #1
- **證據**：RAG-12-HOTFIX-1（KaTeX 注入 alt 炸 img）/ RAG-9（`~` 刪除線）/ PIPE-SLIDES-HOTFIX-3c·3d（CJK emphasis、裸 URL）/ FE-RHYTHM-UNIFY（`:has()` 消滅）散於各 hotfix 報告，無收斂載體。
- **影響**：同類渲染坑跨路次重犯，維護成本高。

### 問題 #3：Osmani 稽核未凝練為可打勾準則
- **證據**：`baton/frontend_browser_standards_audit.md` 為分析報告、非工作流引用點。
- **影響**：稽核價值無法在 FE 落地時被強制檢查。

---

## §4 設計方案

### §4.1 C1 — SOP Authoring（新建前端效能與渲染 SOP 手冊）
於 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` 新建手冊，落地 plan U1–U5：
- **§0 改版規則 / §1 觸發**：FE-Refactor / FE-Hotfix 落地前必讀；對接 WORKFLOW_SOP §1.1/§1.4。
- **§2 效能紅線（7 條）**：每條格式＝「規則一行 + 反例錨點（`static/index.html` 行號）+ 改法一句」，涵蓋 plan U2 七條（串流收尾重排 / head script defer+自託管 / transform 動畫 / rAF+passive / 字型 preload / Gzip+強快取 / 重量套件 code-split）。
- **§3 渲染正確性陷阱清單**：每條附 hotfix 代號溯源（plan U3 六類）。
- **§4 驗收檢查表**：FE 落地前逐項打勾、對接 `template_execution.md §自評`。
- **§5 交叉引用**：視覺→`design/docs/`、跨 Phase→`WORKFLOW_SOP §7`。
- **§99 治理規格**：§99.1 重複防護明列邊界（視覺歸 design/docs、跨 Phase 歸 WORKFLOW_SOP §7、效能+渲染正確性歸本檔）+ §99.2 v1。
- 篇幅 ≤ ~260 行 / ~11KB。

### §4.2 C2 — Workflow Backfill（回填 WORKFLOW_SOP FE 必讀 SOP）
`ref/WORKFLOW_SOP.md`：
- §1.1 FE-Refactor 表「必讀 SOP」列：`—` → `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`。
- §1.4 FE-Hotfix 表「必讀 SOP」列：`—` → 同上。
- §99.2 加 Revision v5（記 FE-PERF-1 C2 回填 FE 兩列必讀 SOP）。
- **§1–§7 五類工作流定義本體、命名規則、§7 接縫契約一律不動**（僅動兩格 + Revision）。

### §4.3 checkout — 成果收官歸檔
Conformance 驗收（目標規格 U1–U7 / §6 grep / 不可動清單）+ §7.2 純 DOC 顯式豁免 + baton 一次性歸檔（plan_v1 → plans/、tasks → tasks/、C1/C2 執行報告 → executions/、+ git add）+ TODO 結案（🟡→✅、寫入 ✅ 完成表 + 索引同步）+ hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 認知負荷↑（多一份 FE 必讀 SOP） | 🟡 中 | 篇幅上限 ≤~260 行 + 檢查表形態 + workflow-gated（不進 @path auto-load） |
| doc-drift（與 design/docs 重疊） | 🟡 中 | C1 §99.1 重複防護明列邊界；視覺內容一律引用不重寫 |
| C2 誤動 WORKFLOW_SOP 五類定義本體 | 🟢 低 | §7 不可動；C2 §6.2 grep 驗只兩格 + §99.2 變動、§1 五類定義文字零改 |
| Osmani 不可行動內容誤入 SOP | 🟢 低 | C1 只收斂稽核 7 條；V8 GC/site isolation/多進程/HTTP3 排除 |
| baton 過程文件提前 mv / git add | 🟢 低 | §8 各 commit 影響範圍明列 baton 報告不入 git；唯 checkout 一次性歸檔 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
# 檔存在、非空、篇幅上限
ls -la .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md
wc -l .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md      # 期望：≤ ~260
# §0/§99 結構齊（WORKFLOW_SOP §4.2 A2）
grep -nE "^## §0|^## §99" .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md   # 期望：各 ≥1 命中
# 效能 7 條紅線 + 反例行號錨點
grep -nE "index\.html|renderMarkdownWithMath|transition|requestAnimationFrame|preload|Gzip|import\(" \
  .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md   # 期望：多命中（7 條覆蓋）
# 渲染正確性陷阱 hotfix 溯源
grep -nE "RAG-12-HOTFIX-1|RAG-9|PIPE-SLIDES-HOTFIX-3|FE-RHYTHM-UNIFY" \
  .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md   # 期望：多命中
# 重複防護邊界
grep -n "design/docs" .claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md   # 期望：有命中（交叉引用）
```

### §6.2 C2 驗收
```bash
# 兩格已回填、無「—」殘留於 FE 兩列
grep -nA6 "FE-Refactor（前端重構）" .claude-logs/ref/WORKFLOW_SOP.md | grep "必讀 SOP"   # 期望：指向 sop 手冊、非「—」
grep -nA6 "FE-Hotfix（前端緊急修補）" .claude-logs/ref/WORKFLOW_SOP.md | grep "必讀 SOP"  # 期望：指向 sop 手冊、非「—」
grep -c "frontend_效能與渲染_SOP_手冊" .claude-logs/ref/WORKFLOW_SOP.md                  # 期望：≥2（§1.1 + §1.4）
# §99.2 新 Revision
grep -n "v5 (2026-07-02)" .claude-logs/ref/WORKFLOW_SOP.md                               # 期望：有命中
# 五類工作流定義本體未動（抽驗關鍵字未變）
grep -c "五類工作流定義" .claude-logs/ref/WORKFLOW_SOP.md                                 # 期望：維持既有數
```

### §6.3 checkout 驗收
```bash
# 純 DOC 零業務碼
git -C . diff --stat   # 期望：僅 sop/ 新檔 + WORKFLOW_SOP.md + 歸檔 plans//tasks//executions/；零 .py / 零 static/
# baton 已清空本任務過程檔（歸檔至正式目錄）
ls .claude-logs/plans/2026-07-02_FE-PERF-1*  .claude-logs/tasks/2026-07-02_FE-PERF-1*  .claude-logs/executions/2026-07-02_FE-PERF-1*
# TODO 結案
grep -n "FE-PERF-1" .claude-logs/TODO.md   # 期望：✅ 完成表 + 索引、active 列表已移除
# 既有測試基線（證零業務碼衝擊）
pytest tests/ -q   # 期望：維持基線 passed（唯一既有 LOG_FORMAT env flake 除外）
```

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 100% 不動（本案純文件、稽核 7 條之實修屬另案）。
- [ ] **`design/docs/*`** 全 11 份 — 視覺設計真理源、不重寫/不搬移/不刪（SOP 僅交叉引用）。
- [ ] **`ref/WORKFLOW_SOP.md` §1–§7** 五類工作流定義本體 / 命名規則 / §7 接縫契約 — 僅允許填 §1.1/§1.4「必讀 SOP」兩格 + §99.2 加 Revision。
- [ ] **既有 `sop/` 三份手冊**（logging/database/mineru）— 內容不動。
- [ ] **`baton/frontend_browser_standards_audit.md`** — 作為 SOP 來源引用、本案不再改。
- [ ] **`.py` / `tests/` / golden baseline** — 純 DOC、零觸發。
- [ ] **baton/ 暫存報告** — Run 階段嚴禁 mv / git add，唯 checkout 一次性歸檔。

---

## §8 推薦 Commit 拆分

### C1 — SOP Authoring（新建前端效能與渲染 SOP 手冊）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `.claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（就地版控、C1 git add）。〔另產 `.claude-logs/baton/2026-07-02_FE-PERF-1_SOP手冊_C1_執行.md` 執行報告、**暫存 baton、不入本 commit git 追蹤**、待 checkout 歸檔〕 |
| **安全性** | 🟢 高 — 純新增 `.md`、零 runtime / 零業務碼 / 零 schema。 |
| **可逆性** | 🟢 高 — `git revert C1` 或直接刪除新檔即完全回滾。 |
| **驗收 grep 條件** | 見 §6.1（檔存在 + §0/§99 結構 + 效能 7 條 marker + hotfix 溯源 + design/docs 交叉引用）。 |
| **依賴關係** | 無前置。 |
| **具體實作細節** | 依 §4.1 產出手冊，章節與內容固定：① `## §0 改版規則`（改版觸發 §1–§99 變動）。② `## §1 觸發與適用`（FE-Refactor/FE-Hotfix 落地前必讀、對接 WORKFLOW_SOP §1.1/§1.4）。③ `## §2 效能紅線`：逐條列 plan U2 七條，每條「**規則** + 反例錨點〔如 `static/index.html:3519-3523` 串流每 token 重排 / `L8` head CDN marked / `L380/522/967` transition:width / rAF=0·passive=0 / `L10-11` KaTeX 未 preload〕 + **改法一句**」。④ `## §3 渲染正確性陷阱`：逐條列 plan U3 六類，每條附 hotfix 代號〔RAG-12-HOTFIX-1 / RAG-9 / PIPE-SLIDES-HOTFIX-3c·3d / RAG-8·PARA-HOTFIX-1·RAG-10 / FE-RHYTHM-UNIFY〕+ 一句規避原則。⑤ `## §4 落地前驗收檢查表`：checkbox 清單、明文對接 `template_execution.md §自評`。⑥ `## §5 交叉引用`：視覺/元件/token→`design/docs/`、跨 Phase→`WORKFLOW_SOP §7`。⑦ `## §99 治理規格`：§99.1 表（含**重複防護**明列邊界）+ §99.2 v1 Revision。全檔 ≤ ~260 行、檢查表形態、不轉錄瀏覽器內核教科書、不重寫 design/docs 內容。 |

### C2 — Workflow Backfill（回填 WORKFLOW_SOP FE 必讀 SOP）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/ref/WORKFLOW_SOP.md`（§1.1/§1.4 兩格 + §99.2）。〔另產 `.claude-logs/baton/2026-07-02_FE-PERF-1_WORKFLOW回填_C2_執行.md` 執行報告、**暫存 baton、不入本 commit git 追蹤**〕〔.bak 備份鐵律：修改前產 `WORKFLOW_SOP.md.bak`、於本 commit git add〕 |
| **安全性** | 🟢 高 — 僅填兩格 + 加一筆 Revision、五類定義本體零改。 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾；.bak 可 `git show` 追溯原狀。 |
| **驗收 grep 條件** | 見 §6.2（兩列指向手冊、無「—」殘留、≥2 命中手冊名、§99.2 v5、五類定義未動）。 |
| **依賴關係** | 前置 C1（回填指向的手冊路徑須先存在、避免懸空引用）。 |
| **具體實作細節** | ① 修改前先產 `.claude-logs/ref/WORKFLOW_SOP.md.bak`。② §1.1 FE-Refactor 表「必讀 SOP」列 `—` → `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`。③ §1.4 FE-Hotfix 表「必讀 SOP」列 `—` → 同上。④ §99.2 頂部加：`- v5 (2026-07-02)：FE-PERF-1 C2——§1.1/§1.4 FE 兩列「必讀 SOP」由「—」回填指向 sop/ 前端效能與渲染 SOP 手冊（補齊前端工作流強制 SOP 缺口）`。⑤ 嚴禁改動 §1 五類定義文字、§2 文書類別、§3 六階段、§6 命名規則、§7 接縫契約任何內容。 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` + `git add`：`baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_plan_v1.md` → `plans/`；`baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_tasks.md` → `tasks/`；`baton/2026-07-02_FE-PERF-1_SOP手冊_C1_執行.md` + `..._WORKFLOW回填_C2_執行.md` → `executions/`；修改 `TODO.md`（結案）。〔C1 sop 手冊、C2 WORKFLOW_SOP 已於各自 commit 版控、不在此重列〕 |
| **安全性** | 🟢 高 — 純文件搬移 + TODO 更新、零 runtime。 |
| **可逆性** | 🟢 高 — 歸檔為 `mv`、可反向搬回 baton；TODO 更新 `git revert` 可回滾。 |
| **驗收 grep 條件** | 見 §6.3（git diff --stat 零 .py/static、baton 過程檔已歸檔、TODO 結案、pytest 基線）。 |
| **依賴關係** | 前置 C1 + C2 全部 ship。 |
| **具體實作細節** | ① Conformance 驗收：目標規格 U1–U7 逐項核（引 C1/C2 §6 grep 結果）；不可動清單逐項打勾（git diff 證零業務碼）；提示詞稽核（plan/Tasks/C1/C2 提示詞入 git）。② **§7.2 顯式豁免**：純 DOC-Refactor、無 code handoff，依 WORKFLOW_SOP §7.2 特例豁免跨 Phase 整合測試（同 WORKFLOW-3/4/5 立規者先例）、checkout 報告明載。③ baton 一次性歸檔（上列 mv + git add）。④ TODO 結案：active 列表移除 FE-PERF-1、頂部新增 `### DOC-Refactor FE-PERF-1 …` ✅ 完成表（C1/C2/checkout 三列 + hash）、同步索引（依類別）。⑤ hash 自癒：回填各 commit 前 7 碼。⑥ checkout 自身不另產 executions 報告（收官動作於 TODO 完成表 + checkout commit message 記錄）。 |

---

## §9 Open Questions

無。（plan v2 §9 六 OQ 已於審核中全數 🟢 定案，見 plan §9.1。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-PERF-1 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FE-PERF-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混不同優先級文件；嚴禁自動 git commit / push；baton 報告唯 checkout 歸檔 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計脈絡引 plan、全局硬規則引 CLAUDE.md、SOP 產出物視覺內容引 design/docs |

### §99.2 Revision 歷程

- v1 (2026-07-02)：初版拆分——依 plan v2（六 OQ 定案）拆 3 commit〔C1 新建 sop/ 前端效能與渲染 SOP 手冊 / C2 回填 WORKFLOW_SOP §1.1/§1.4 FE 必讀 SOP + §99.2 v5 / checkout 收官歸檔〕；純 DOC-Refactor、§7.2 顯式豁免、同步 TODO 🟡 WIP。
