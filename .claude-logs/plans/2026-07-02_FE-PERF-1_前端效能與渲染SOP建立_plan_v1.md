# FE-PERF-1 前端效能與渲染 SOP 建立 plan

> 目的：新建一份 `sop/` 前端效能與渲染 SOP，收斂「Osmani 瀏覽器渲染原理稽核（7 條）＋既有前端 hotfix 渲染正確性教訓」為可行動檢查表，並回填 WORKFLOW_SOP §1.1/§1.4 FE 兩列「必讀 SOP」缺口。純 DOC-Refactor、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：① WORKFLOW_SOP §1.1（FE-Refactor）/ §1.4（FE-Hotfix）「必讀 SOP」欄皆為「—」——**後端有 logging/database 兩份強制 SOP、前端一份都沒有**，是治理上唯一的不對稱缺口。② 前端渲染正確性教訓（KaTeX 注入 alt、CJK `**` emphasis、soft-break、`~` 誤判、`:has()` 消滅）散落於多份 hotfix 報告，**path #2 重蹈 path #1 的坑**、無收斂載體。③ Osmani《How modern browsers work》之瀏覽器渲染原理已產出 8 條前端稽核（`baton/frontend_browser_standards_audit.md`），但未凝練為 FE 落地前可逐項打勾的準則。
- **解法**：新建 **`sop/` 前端效能與渲染 SOP**——內容限「效能紅線 + 渲染正確性陷阱 + 驗收檢查表」，視覺/元件/token 一律**交叉引用 `design/docs/`、不重寫**；並回填 WORKFLOW_SOP §1.1/§1.4 兩列「必讀 SOP」指向本 SOP。範式對齊既有 logging/database/mineru SOP（workflow-gated、按需讀、§0/§99 結構）。
- **影響**：純 `.md`——新增 1 份 `sop/` SOP + 回填 `ref/WORKFLOW_SOP.md`（§1.1/§1.4 兩格 + §99.2 Revision）；**零業務代碼、零 runtime、零 schema、零 API 簽名變動、零 golden 重捕**。是否併動 `CLAUDE.md §2` 工作流表見 §9 Q2。

---

## §2 目標規格

本案「最終狀態」目標規格（可量化、可 grep 檢驗）：

- **U1 — SOP 檔存在且合規**：於 `sop/` 新建 SOP 檔（命名見 §9 Q5），含 `## §0 改版規則` 與 `## §99 治理規格`（`grep "^## §0\|^## §99"` 命中）；篇幅對齊既有 sop 手冊（**≤ ~260 行 / ~11KB**，`wc -l`/`wc -c` 可驗）。
- **U2 — 效能紅線章（收斂稽核 7 條）**：含一節逐條列出本次稽核之可行動紅線，**每條格式固定**＝「規則一行 + 反例錨點（對應 `static/index.html` 行號）+ 改法一句」，至少涵蓋：
  1. 串流回覆收尾才重排版（消除 `renderMarkdownWithMath` 每 token 全量重排 O(n²)）
  2. head `<script>` 一律 `defer` + 第三方套件自託管（消除 parser-blocking + CDN 白屏）
  3. 幾何動畫改 `transform`/`opacity`（禁 `transition: width/height/margin`）
  4. DOM 寫入對齊 `requestAnimationFrame`、scroll/touch listener 標 `passive`
  5. 自託管字型 `preload`（消除公式字型 FOUT/版跳）
  6. 後端靜態資源 Gzip + 強快取（`Cache-Control immutable`）
  7. 重量套件（KaTeX）按需 `import()` code-split
- **U3 — 渲染正確性陷阱章（收斂 hotfix 教訓）**：含一節條列既有前端 hotfix 已踩過的渲染坑，**每條附 hotfix 代號溯源**，至少涵蓋：marked/KaTeX 佔位順序（RAG-12 / RAG-12-HOTFIX-1）、CJK `**` emphasis 失效（PIPE-SLIDES-HOTFIX-3d）、soft-break 段落黏連（RAG-8 / PARA-HOTFIX-1 / RAG-10）、`~` 誤判刪除線（RAG-9）、`:has()` 消滅與 margin-top flow（FE-RHYTHM-UNIFY）、`<img alt>` 內特殊字轉義（RAG-12-HOTFIX-1）。
- **U4 — 驗收檢查表章**：含一份「FE 落地前逐項打勾」清單，明文對接 `template_execution.md §自評`（WORKFLOW-4 U3）與本 SOP §效能紅線/§渲染陷阱，供 FE-Refactor/FE-Hotfix 執行報告引用。
- **U5 — 重複防護明列**：SOP §99.1 明文邊界——視覺/元件/token/互動歸 `design/docs/`、跨 Phase 接縫歸 `WORKFLOW_SOP §7`、**效能 + 渲染正確性歸本 SOP**；防 doc-drift。
- **U6 — WORKFLOW_SOP 回填**：`ref/WORKFLOW_SOP.md` §1.1（FE-Refactor）與 §1.4（FE-Hotfix）「必讀 SOP」欄由「—」改為本 SOP 相對路徑；§99.2 加 Revision 一筆。**§1–§7 五類工作流定義本體不得改動**（僅填兩格 + Revision）。
- **U7 — 純 DOC 無迴歸**：全案零 `.py`/零 `static/` 業務代碼 diff（`git diff --stat` 僅命中 `sop/` 新檔 + `WORKFLOW_SOP.md`〔+ 視 Q2 決定的 `CLAUDE.md`〕）；既有 pytest 基線維持。

### §2.5 候選方案（Diverse Rollout）

> 本案核心決策＝「這份準則放哪、以何機制生效」屬架構級/易踩局部最優，故填本節。

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| **方案 A（選定）** | 放 `sop/`，回填 WORKFLOW_SOP §1.1/§1.4「必讀 SOP」欄使其 workflow-gated | 沿用 logging/database/mineru 既有機制、零新機制；只有 FE 工作流讀、不污染其他 session；擴充自然（未來 FE SOP 同放 sop/） |
| 方案 B（否決） | 放 `ref/` 並加進 `CLAUDE.md §0 @path` 自動載入 | `ref/` 目前僅 auto-load 2 檔（WORKFLOW_SOP + framework）；加前端內容 → **純後端/純文件 session 每次被灌前端 SOP**，違反 CLAUDE.md §99「≤200 行、最小化」精神；與 sop/ 先例分裂 |
| 方案 C（否決） | 併入 `design/docs/`（如新增 `design/docs/performance.md`） | design/docs 為視覺設計系統真理源；效能/渲染管線非其範疇 → 職責混淆；且 design/docs 不在治理工作流的「必讀 SOP」掛勾點上、無強制力 |

- **選定理由**：方案 A 用**既有 workflow-gated SOP 機制**填補既有缺口，零新概念、零污染、最小認知負荷，且是三份後端 SOP 的直接類比。
- **否決留痕**：B（ref/ auto-load）之污染代價、C（design/docs）之職責混淆，於此留底，防未來重議。

---

## §3 現況與證據

- **`design/docs/`（11 份前端文件、無效能/渲染管線）**：components.md(21KB) / dom-reference.md(17KB) / interaction.md / principles.md / typography.md / spacing.md / color-tokens.md / theme-guide.md / api-integration.md / icon-spec.md / copywriting.md——全為**設計系統/視覺/結構**導向，無一談效能與瀏覽器渲染。
- **`sop/`（workflow-gated SOP 先例）**：logging_SOP / database_SOP / mineru_SOP 三份「按領域強制、由 WORKFLOW_SOP 掛勾」手冊，皆 §0/§99 結構、~8–10KB。
- **`ref/WORKFLOW_SOP.md` §1.1 / §1.4**：FE-Refactor 與 FE-Hotfix「必讀 SOP」欄現值皆為「—」（缺口）。
- **`CLAUDE.md §0`**：@path 僅 auto-load `WORKFLOW_SOP.md` + `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` + `TODO.md` + `baton/*.md`（放 ref/ 不代表自動載入，須顯式加 @path）。
- **稽核來源**：`baton/frontend_browser_standards_audit.md`（8 findings + Priority Matrix，本 session 已補入串流 O(n²) 並重排）。
- **`static/index.html`（3835 行單檔，行號作 SOP 反例錨點）**：串流重排 `renderMarkdownWithMath` 每 token 呼叫（`L3519-L3523`、定義 `L1623-L1671`）；head 同步 script（`L8` marked CDN / `L10-L11` KaTeX）；`transition: width`（`L380/L522/L967`）；scroll listener（`L1781/L1922`）；全檔 `requestAnimationFrame`=0、`passive`=0。
- **hotfix 教訓來源（U3 溯源）**：RAG-12-HOTFIX-1（KaTeX 注入 alt 炸 img）/ RAG-9（`~` 刪除線）/ RAG-8·PARA-HOTFIX-1·RAG-10（soft-break）/ PIPE-SLIDES-HOTFIX-3c·3d（CJK emphasis、裸 URL）/ FE-RHYTHM-UNIFY（`:has()` 消滅、margin-top flow）。

### §3.1 grep 鋼鐵證據

```bash
$ ls .claude-logs/sop/
2026-05-23_database_SOP_手冊.md  2026-05-23_logging_SOP_手冊.md  2026-05-27_mineru_SOP_手冊.md  ...
$ ls design/docs/
components.md  dom-reference.md  interaction.md  principles.md  typography.md  spacing.md
color-tokens.md  theme-guide.md  api-integration.md  icon-spec.md  copywriting.md  README.md
# WORKFLOW_SOP FE 兩列「必讀 SOP」= 「—」（見 §1.1 FE-Refactor / §1.4 FE-Hotfix 表格）
$ grep -nE "requestAnimationFrame|passive" static/index.html | wc -l
0
$ grep -nE "renderMarkdownWithMath\(" static/index.html   # 每 token 呼叫證據
3116: ... 3136: ... 3205: ... 3522: aiMsg.innerHTML = renderMarkdownWithMath(formatted);
$ grep -nE "transition: *width" static/index.html
380:    transition: width 180ms ease;   522:    transition: width 200ms ease;   967:    transition: width 180ms ease;
$ grep -nE "cdnjs|katex.min.js" static/index.html | head
8:<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
11:<script src="/static/vendor/katex/katex.min.js"></script>
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 本案為純 DOC-Refactor、無跨 Phase / 無模組間 code handoff（僅 `.md` 文件產出與回填）。依 `WORKFLOW_SOP §7.2` 特例顯式申請整合測試豁免（純文檔、無 code handoff），由 baron 拍板（見 §9 Q6）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 認知負荷↑（多一份 FE 必讀 SOP） | 🟡 中 | 篇幅上限 U1（≤~260 行）+ 檢查表形態（非教科書）+ 僅 FE 工作流 workflow-gated 讀、不進 @path auto-load |
| doc-drift（與 design/docs 內容重疊） | 🟡 中 | U5 §99.1 重複防護明列邊界；視覺/元件/token 一律**引用不重寫**；SOP 只寫效能 + 渲染正確性 |
| SOP 定「應然」但稽核 7 條實修未落地 | 🟢 低 | SOP 定「標準」與「反例錨點」；實修屬另案（本案不含 code fix，對齊「不用給 commit 建議」精神）；SOP 上線即可先擋新 FE 改動重犯 |
| 回填動到權威源 WORKFLOW_SOP | 🟢 低 | 僅填 §1.1/§1.4 兩格「必讀 SOP」+ §99.2 Revision；**五類工作流定義本體 §1–§7 零改**（U6 硬約束） |
| Osmani 文中不可行動內容（V8 GC/site isolation/多進程/HTTP3）誤入 SOP | 🟢 低 | U2 明列「僅收斂稽核 7 條」；不可行動原理一律排除、SOP 不轉錄瀏覽器內核教科書 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `static/index.html` 及**任何前端/業務代碼**（本案純 SOP 文件、零 code diff；稽核 7 條之實修屬另案）。
- [ ] `design/docs/*` 全部 11 份（視覺設計真理源，不重寫、不搬移、不刪；SOP 僅引用）。
- [ ] `ref/WORKFLOW_SOP.md` §1–§7 **五類工作流定義本體、命名規則、接縫契約**（僅允許填 §1.1/§1.4「必讀 SOP」兩格 + §99.2 加 Revision）。
- [ ] 既有 `sop/` 三份手冊（logging/database/mineru）內容不動。
- [ ] `baton/frontend_browser_standards_audit.md`（作為 SOP 之來源引用、本案不再改）。
- [ ] 任何 `.py` / `tests/` / golden baseline（純 DOC、零觸發）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| 五類工作流定義 / 命名規則 / §7.2 豁免 | `ref/WORKFLOW_SOP.md §1 / §6 / §7` |
| 文件歸屬判定（sop/ 歸屬） | `ref/WORKFLOW_SOP.md §2` |
| 雙軌制 / 提示詞歸檔 / 重複防護 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §6 / §99.1` |
| SOP 撰寫結構參考 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §5`（SPEC 必備核心結構） |
| 稽核來源（7 條紅線） | `baton/frontend_browser_standards_audit.md` |
| 渲染正確性教訓來源 | 既有 hotfix 報告（RAG-12-HOTFIX-1 / RAG-9 / PIPE-SLIDES-HOTFIX-3c·3d / FE-RHYTHM-UNIFY 等） |
| 視覺設計真理源（交叉引用、不重寫） | `design/docs/*` |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**（證純 DOC 零業務碼衝擊）：
  ```bash
  pytest tests/ -q   # 預期維持基線 passed（唯一既有 LOG_FORMAT env flake 除外）
  ```
- **預計新增測試**：**無**（純 `.md`、無可測程式邏輯）。驗收改以 grep/wc 靜態核查（見 §8.2）。

### §8.2 手動端到端（E2E）＝文件核查（純 DOC 無前端 E2E）

1. `ls -la` + `wc -l/-c` SOP 檔 → 存在、非空、篇幅 ≤ U1 上限。
2. `grep "^## §0\|^## §99"` SOP → §0/§99 結構齊（對齊 WORKFLOW_SOP §4.2 A2）。
3. `grep` SOP 效能紅線 7 條 marker + 反例行號 → U2 全覆蓋；`grep` hotfix 代號 → U3 溯源齊。
4. `grep -nE "必讀 SOP" ref/WORKFLOW_SOP.md` → §1.1/§1.4 兩列已由「—」改指本 SOP；§99.2 有新 Revision。
5. 人工比對 SOP 與 `design/docs/` → 無視覺/元件內容重複（U5 邊界成立）。
6. `git diff --stat` → 僅命中 `sop/` 新檔 + `WORKFLOW_SOP.md`〔+ 視 Q2 之 `CLAUDE.md`〕，零 `.py`/`static/`（U7）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** SOP 放 `sop/` 還是 `ref/`？ | **`sop/`（§2.5 方案 A）** | workflow-gated、沿用 logging/database/mineru 先例、不污染 @path auto-load；ref/ 需顯式 @path 才生效且會灌爆非前端 session。 |
| **Q2** 是否同步改 `CLAUDE.md §2` 工作流表？ | **不改本體；WORKFLOW_SOP §1 為唯一源、僅回填 §1.1/§1.4** | §99.1 重複防護：工作流「必讀 SOP」唯一源在 WORKFLOW_SOP；CLAUDE.md §2 若也寫 → doc-drift。最多於 CLAUDE.md §2 表尾註一行指針（次選、baron 定）。 |
| **Q3** SOP 範圍：純效能 vs 含「渲染正確性陷阱」？ | **含渲染正確性（U3）** | hotfix 史證明反覆重蹈的是**渲染正確性 bug**（alt 炸圖/CJK emphasis/soft-break）而非純效能；收斂這些才是 SOP 最高 ROI。 |
| **Q4** SOP 與稽核 7 條「實修 plan」的順序？ | **本案只立 SOP（標準）；實修另開 FE-Refactor plan 引用本 SOP** | 對齊「不用給 commit 建議」精神；SOP 定「應然標準+反例錨點」先上線擋新犯，實修（動 index.html）風險與 golden/E2E 另案隔離評估。 |
| **Q5** SOP 檔名？ | **`sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`** | 對齊既有 `<date>_<主題>_SOP_手冊.md`（logging/database/mineru）命名慣例。 |
| **Q6** §7.2 跨 Phase 整合測試豁免？ | **顯式豁免** | 純 DOC-Refactor、無 code handoff；同 WORKFLOW-3/4/5 立規者先例（立規者自身不適用該規）。 |

### §9.1 定案紀錄（baron 2026-07-02 全數 🟢 核准）

| OQ | 定案 | 備註 |
|---|---|---|
| Q1 | 🟢 放 `sop/`（方案 A） | workflow-gated、不污染 @path auto-load |
| Q2 | 🟢 不改 `CLAUDE.md` 本體 | WORKFLOW_SOP §1.1/§1.4 回填為唯一源；表尾一行指針列 tasks 階段**選用微調、預設不加**（防 doc-drift） |
| Q3 | 🟢 含渲染正確性（U3） | hotfix 史證明渲染正確性 bug 為最高 ROI |
| Q4 | 🟢 本案僅立規、實修另案 | 文檔立規 ↔ 代碼實修解耦、本案零業務碼/零迴歸 |
| Q5 | 🟢 檔名 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` | 對齊既有 sop 命名慣例 |
| Q6 | 🟢 §7.2 顯式豁免 | 純 DOC、無 code handoff、立規者先例 |

**六 OQ 全結清、plan 規格凍結，可進階段 2（tasks 拆分 + 同步 TODO 🟡 WIP）。**

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-PERF-1「前端效能與渲染 SOP 建立」之目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查 §9 Open Questions 並在 tasks.md 拆分時引用；階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 FE-PERF-1 tasks / 執行報告 / 產出之 `sop/` 前端 SOP |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段，且 baron 本案明示不給 commit 建議） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格；工作目錄與流程規格引用 CLAUDE.md / WORKFLOW_SOP；SOP 產出物之視覺內容一律引用 design/docs、不重寫 |

### §99.2 Revision 歷程

- v2 (2026-07-02)：baron review 全數 🟢 核准——§9 六 OQ（Q1 sop/ / Q2 不改 CLAUDE.md 本體 / Q3 含渲染正確性 / Q4 僅立規實修另案 / Q5 檔名 / Q6 §7.2 豁免）定案入 §9.1；內容完整性經 review 判定無缺漏；規格凍結，可進階段 2（tasks）。
- v1 (2026-07-02)：初版建立——以 Osmani《How modern browsers work》稽核（`baton/frontend_browser_standards_audit.md` 8 findings）為基礎，規劃新建 `sop/` 前端效能與渲染 SOP（效能 7 條 + 渲染正確性陷阱 + 驗收檢查表）+ 回填 WORKFLOW_SOP §1.1/§1.4 FE 必讀 SOP；§2.5 三候選（sop/ 選定、ref/ 與 design/docs 否決）；§9 六 OQ 待 baron 拍板。
