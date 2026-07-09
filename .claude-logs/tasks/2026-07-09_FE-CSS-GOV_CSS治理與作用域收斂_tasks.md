# FE-CSS-GOV CSS 治理與作用域收斂 — Tasks

> 本文件為 FE-CSS-GOV 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md`（內部 **v2**、八 OQ 定案、B1 兩段式）產出，含 **8 個 Commit（C1–C7 → checkout）**。
> 工作流：**FE-Refactor**（必讀 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`、每 commit §4 檢查表）。
> **文獻同步硬性綁定**（baron 凍結）：每 commit 依 §4.0 配套矩陣同步 design/docs、嚴禁累積至收官。
> 四鐵防線：JS 邏輯零改／DOM id 零改／27+ JS 契約 class 零改名／`renderMarkdownWithMath` 七步管線零改。
> 工作目錄註：提示詞模板 worktree 路徑為殘留、依 `CLAUDE.md §3`（v5）主 repo 為準。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 8 個 | `static/css/{globals,layout,sidebar,content,chat,overlays,print}.css`（7）+ `design/docs/css-architecture.md`（1） |
| **修改檔案** | ~11 個 | `static/index.html`（C1–C7 累計）/ `static/themes/{kahn,kandinsky,mies,nara}.css`（C3）/ `design/docs/{principles,theme-guide,components,dom-reference,README}.md`（各配套 commit）+ checkout 戳統一 |
| **目錄定義** | 1 個 | `static/css/`（主檔系樣式表、比照 vendor 慣例） |
| **備份（.bak 鐵律）** | ~15 份 | `archive/2026-07-09_FE-CSS-GOV_C{n}_<檔名>.bak`——index.html×7（C1–C7 各一）+ themes×4（C3）+ 各 docs 被修檔（對應 commit）；各自 commit `git add` |
| **狀態更新** | 2 個 | `TODO.md`（🟡 WIP→checkout 雙層結案）/ `prompts/INDEX.md` |
| **Commits** | 8 個 | C1→C2→C3→C4→C5→C6→C7→checkout |
| **baton 歸檔** | 1 次 | checkout：plan/tasks/C1–C7 報告（9 檔）mv→plans//tasks//executions/ + 逐檔 git add；checkout 報告依鐵律直產 executions/ |

---

## §1 TL;DR（概要）

- **挑戰**：單檔 1,354 行 inline CSS、85 行 ID 後代式全域耦合、cascade 零層化、4 主題檔 35–39 行結構重複、`:root` 混元件級變數（詳 plan §1/§3、基準 `index.html@d4ce75a`）。
- **解法（B1 兩段式、8 commits）**：
  - **段一·等價搬遷**：`C1 — File Split(檔案拆分七件套)`：CSS 依 §4.1 錨段映射**零改寫**遷入 7 檔+`<link>` 序、行數/規則對帳；docs：**css-architecture.md 初版**+README。`C2 — Layer Cascade(層化串接)`：四層 wrap+層序宣告、themes/print/自訂主題 unlayered（A1）、非 print `!important` 1 條個案；docs：**principles 補 @layer/作用域/margin-flow**。
  - **段二·行為改造**：`C3 — Theme Dedup(主題結構去重)`：4 主題白名單外結構上移 base、值差 token 化；docs：**theme-guide 契約改寫**。`C4 — Token Slimming(tokens 瘦身歸位)`：`:root` B 類 13 變數遷檔不改名；docs：css-architecture token 歸屬節。`C5 — Sidebar Scope(左欄作用域收斂)`（18 行）、`C6 — Chat Scope(右欄作用域收斂)`（~13 行）、`C7 — Content Chrome Scope(中欄框架收斂與白名單審計)`（~5 行+殘量歸零審計）；docs：components/dom-reference 對應區同步+css-architecture 前綴/白名單表。
  - `checkout — 成果收官歸檔（成果歸檔與移出暫存）`：Conformance U1–U8 總驗+戳統一+雙層結案。
- **影響範圍**：`static/index.html`+`static/css/**`（新）+`static/themes/**`+`design/docs/**`；零 `.py`、零 JS 邏輯、零 golden。
- **不可動清單**：見 §7。

---

## §2 現況

| 對象 | 現狀（`@d4ce75a` 實測） | 待處理 |
|---|---|---|
| inline `<style>` | `:17-1372`、≈1,354 行、含 25+ 區塊註解錨（§4.1 映射基礎） | C1 遷出七件套 |
| cascade | `@layer`=0；載入序 katex→inline→theme-link | C2 四層化、themes unlayered |
| `!important` | 21 行＝19 print 宣告+1 非 print 宣告（`css:1260`、collapsed rail 隱藏）+1 註解行（`css:1256`）——**plan「2 條」係含註解行、本表誠實微正** | C2 個案：1 條 |
| ID 後代式 85 行 | 分佈：`#paper-content`28/`#sidebar`9/`#sidebar-bottom`7/`#chat-panel`7/`#abstract-toolbar`7/`#current-title`4/`#chat-input`4/其餘≤2（§3 分類表） | C5–C7 收斂+白名單 |
| themes 4 檔 | 結構屬性行 39/35/36/35；`--content-max-w` token 化範式已存在 | C3 去重 |
| `:root` | A 類全域 token+B 類元件級 13 變數混雜 | C4 遷檔 |
| design/docs | DOC-SYNC-1 後對齊 `@8e5d1fa`；無 css-architecture；principles 無 @layer/margin-flow | 各 commit 配套 |

---

## §3 觀察問題（85 行分類處置表·凍結）

### 問題 #1：跨元素 ID 後代式＝收斂對象（~36 行）
| 根 id | 行數 | 處置 commit |
|---|---|---|
| `#sidebar`/`#sidebar-bottom`/`#paper-list`/`#folder-tree` | 9+7+1+1=18 | **C5**（前綴 `.sb-*` 沿 `.sb-row` 家族） |
| `#chat-panel`/`#chat-header`/`#chat-header-actions`/`#chat-input-area`/`#hashtag-autocomplete` | 7+2+1+1+2=13 | **C6**（前綴 `.chat-*` 沿既有家族） |
| `#content-toolbar`/`#content-area`/`#app` | 2+1+1=4 | **C7**（前綴 `.ct-*` 新增最小） |

### 問題 #2：內容渲染容器白名單＝保留（50 行、Q7）
`#paper-content`38（含 META-NORM/KaTeX 防禦/FE-PERF 遺產）/`#abstract-toolbar`7/`#current-title`4/`#chat-messages`1——後代對象為 marked/後端/renderTitleHeader 產物；**C7 一併登記 css-architecture 白名單表**。

### 問題 #3：自身狀態式＝保留（非牽連）
`#chat-input`4（`[contenteditable]`/`:empty` 偽類）/`#web-search-toggle`2（`.active` 自身態）/`#tooltip`2（`.show`）/`#empty-state`2——單元素自身狀態、非跨元素耦合；連同 21 個單層 `#id{}` 併入白名單表（**保留、嚴禁誤收斂**）。

---

## §4 設計方案

### §4.0 文獻同步配套矩陣（每 commit 硬綁定、baron 凍結）
| Commit | 同 commit docs 配套 |
|---|---|
| C1 | **新增 `design/docs/css-architecture.md`**（檔×職責×載入序+「新樣式寫哪」決策樹初版）+ `README.md` 目錄連結 |
| C2 | `principles.md` 補「@layer 層序/主檔系嚴禁 unlayered 紀律/**margin-flow 模型**（DOC-SYNC Q4 移交）」+ css-architecture 層序節 |
| C3 | `theme-guide.md` **契約改寫**（Q8 允許屬性白名單+必供 token 清單更新+unlayered 語意+自訂主題撰寫指南） |
| C4 | css-architecture「token 歸屬」節（A 類/B 類清單與所在檔） |
| C5/C6/C7 | `components.md`/`dom-reference.md` 對應區 class 記載同步 + css-architecture 前綴表（C5 起建）/白名單表（C7 完成） |
| checkout | 全部被修 docs 頂部同步戳統一更新（新基準 hash） |

### §4.1 C1 — File Split（檔案拆分七件套）
**零改寫等價搬遷**。依 inline CSS 既有區塊錨（行號＝css 塊內部、run 期以**錨文字**定位）切檔：
| 目標檔 | 錨段（css 塊內） | 內容 |
|---|---|---|
| `globals.css` | `1-85`（`:root`+fallback）+ reset 兩行（`*,::before,::after`/`body,h1…`）+ base 元素通則 | tokens+reset+base |
| `overlays.css` | `90-267`（tooltip/modal 家族/`.modal-input`/dropdown）+ `569-603`（`.ctx-popup`） | 彈出層 |
| `layout.css` | `268-355` 共用按鈕/icon-only + 三欄框架/rail collapse 段（`~1230-1262`）+ divider | 框架/按鈕系統 |
| `sidebar.css` | `356-641`（左欄/上傳占位/左欄底部；popup 段除外） | 左欄 |
| `content.css` | `642-`中欄起 至 chat 區前（含 `#paper-content`/META-NORM/KaTeX/rhythm/FE-PERF 遺產於 `.msg` 前之段） | 中欄 |
| `chat.css` | msg 泡泡系（含 `.msg-*` content-visibility 遺產）→ 輸入區/hashtag 段 | 右欄 |
| `print.css` | `@media print` 全段（19 `!important` 原樣） | 列印 |
- `index.html`：刪 `<style>` 塊、於原位插 7 `<link>`（globals 首、print 末、`#theme-link` 仍殿後）；**規則/行數對帳**：7 檔 CSS 行數和＝原 1,354±空行、選擇器數守恆 grep。
- docs 配套：css-architecture.md 初版 + README 連結。

### §4.2 C2 — Layer Cascade（層化串接）
- `globals.css` 首行 `@layer reset, tokens, base, components;`；globals 內容依段 wrap 入 `reset/tokens/base`；layout/sidebar/content/chat/overlays 整檔 wrap `@layer components { … }`；**print.css/themes 不動（unlayered）**。
- 非 print `!important` 個案（`display:none !important`、collapsed rail）：試以「同層後宣告/選擇器調整」替代→移除；不可行則保留+css-architecture 白名單註記（Q5）。
- 驗：層宣告=1、五檔 wrap grep、**全站 E2E 特別驗 rail 收合/主題四款/自訂主題上傳**（unlayered 相容）。
- docs 配套：principles（@layer 層序+主檔系禁 unlayered 鐵則+margin-flow 模型節）+ css-architecture 層序節。

### §4.3 C3 — Theme Dedup（主題結構去重）
- 4 主題逐檔：白名單（Q8）外結構屬性→比對四檔值——**同值**：直接上移 base（content/layout 對應檔）刪主題行；**異值**：立 token（`--x` 入 tokens 層、主題僅覆 token 值）再上移結構。
- 驗：4 檔白名單外屬性=0、四主題視覺 E2E 逐款、`--content-max-w` 等既有 token 行為不變。
- docs 配套：theme-guide 契約改寫（白名單/必供 token 更新/unlayered 語意/自訂主題指南）。

### §4.4 C4 — Token Slimming（tokens 瘦身歸位）
- B 類 13 變數（`--btn-h/--btn-pad-x/--btn-min-w/--btn-icon/--btn-icon-svg/--btn-icon-stroke/--gap-btn-tight/--gap-btn-normal/--gap-btn-loose/--toolbar-h/--pad-panel/--rail-w/--chat-pad-x`）自 globals `:root` 遷至對應檔頂 `:root`（layout：btn×6+gap×3+toolbar-h+rail-w；content：pad-panel？依實際消費檔定；chat：chat-pad-x）——**不改名不改值**、加「元件級、非主題調校面」註。
- 驗：globals `:root` 僅 A 類、`var()` 解析零破（全站 E2E+grep 每變數仍有唯一定義）。
- docs 配套：css-architecture token 歸屬節。

### §4.5 C5/C6/C7 — Scope Convergence（作用域收斂三區）
- 通式（每區）：對 §3-#1 該區行——HTML 對應元素**加**新 class（原 class/id 全保留）→ CSS 選擇器改單 class →刪 ID 後代式；前綴凍結：C5 `.sb-*`、C6 `.chat-*`、C7 `.ct-*`；**JS 契約 27+ 名單零觸碰**（僅新增並存）。
- C7 加**收官審計**：白名單表（§3-#2/#3 全量）落 css-architecture；chrome ID 後代式殘量掃描=0。
- 驗（每區）：該區 ID 後代式=0、JS 契約 class grep 守恆、`getElementById` 全解析、該區互動 E2E×4 主題。
- docs 配套：components/dom-reference 該區 class 記載同步+前綴表。

### §4.6 checkout — 成果收官歸檔
Conformance（plan §2 **U1–U8** 跨 commit 覆蓋總驗+tasks §6 重跑+§7 四鐵防線+提示詞 10 份稽核+msg）+ §7.2 顯式豁免（Q6）+ **checkout 報告直產 executions/**（staged 白名單自檢實貼）+ docs 戳統一 + baton 歸檔（9 檔）+ TODO 雙層結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| C2 層化 cascade 反轉 | 🔴 高 | C1/C2 分離（搬遷零改寫先驗等價）；層內保原序；非 print `!important` 僅 1 條個案；全站 E2E×4 主題 |
| C1 搬遷漏規則 | 🟡 中 | 錨段映射表+行數/選擇器數對帳+分檔 diff 可審 |
| C3 主題視覺回歸 | 🟡 中 | 同值/異值二分流程（異值必 token 化保值）；逐主題 E2E |
| C5–C7 誤刪保留類（自身狀態式/單層 #id） | 🟡 中 | §3 分類表凍結+「原 class/id 全保留、新 class 純加法」通式+守恆 grep |
| 自訂主題相容 | 🟢 低 | A1 unlayered 天然贏；C2/C3 E2E 各驗一次上傳主題 |
| print 迴歸 | 🟡 中 | print.css 獨立 unlayered 原樣；每 commit print 預覽 |
| 大案疲勞/文獻債 | 🟡 中 | 8 顆小步可 ship；§4.0 矩陣硬綁定（嚴禁收官補文件） |

---

## §6 測試計畫

### §6.1 C1
```bash
grep -c '<style>' static/index.html                 # 0
ls static/css/ | wc -l                              # 7
grep -c 'rel="stylesheet" href="/static/css/' static/index.html   # 7（序：globals 首/print 末）
# 對帳：cat static/css/*.css | grep -cE '^\s*[.#\[:@a-z*]' ≒ 原選擇器/規則行基線（run 期記錄基線→比對）
grep -c "css-architecture" design/docs/README.md    # ≥1
ls design/docs/css-architecture.md                  # 存在
# E2E：三軌×4 主題 smoke、console 0（等價搬遷、視覺零變）
```
### §6.2 C2
```bash
grep -c '@layer reset, tokens, base, components;' static/css/globals.css   # 1
for f in layout sidebar content chat overlays; do grep -c '@layer components' static/css/$f.css; done  # 各 1
grep -c '@layer' static/css/print.css static/themes/*.css                  # 各 0（unlayered）
grep -rc '!important' static/css/{globals,layout,sidebar,content,chat,overlays}.css  # ≤白名單（目標 0）
grep -nE '@layer|margin-flow|unlayered' design/docs/principles.md          # 三主題命中
# E2E：rail 收合/四主題/自訂主題上傳/print 預覽
```
### §6.3 C3
```bash
for f in static/themes/*.css; do <白名單外結構屬性掃描> ; done   # 各 0
grep -nE '允許屬性|白名單|unlayered' design/docs/theme-guide.md   # 契約改寫命中
# E2E：四主題逐款視覺比對（重點：h2 border/間距/divider）
```
### §6.4 C4
```bash
<globals :root 掃描> → 僅 A 類；for v in btn-h …chat-pad-x; grep -rc "\-\-$v:" static/css/ → 各恰 1（唯一定義）
# E2E：按鈕/工具列/rail/聊天 padding 視覺零變
```
### §6.5 C5–C7（每區）
```bash
<該區根 id 後代式掃描 static/css/> → 0
for c in <27+ 契約名單>; do grep -c "$c" static/index.html; done   # ≥基線（零改名、只增）
# C7 加：<全 chrome ID 後代式殘量> → 0；css-architecture 白名單表存在（§3-#2/#3 全量）
# E2E：該區互動×4 主題
```
### §6.6 checkout
```bash
git diff --stat <基線>..HEAD → 僅 index.html+static/css/**+themes/**+design/docs/**（零 .py/JS 段零 diff）
node --check <script 區>（防 HTML 編輯誤傷 script）
ls .claude-logs/baton/ | grep FE-CSS-GOV → 空；TODO 雙層+hash；提示詞 10 份稽核
```

---

## §7 不可動清單

- [ ] **四鐵防線**：JS 邏輯（`:1610` 起 script 區零編輯）／DOM id 75 個零刪改／27+ JS 契約 class 零改名（§3 名單）／`renderMarkdownWithMath` 零改。
- [ ] **§3-#2/#3 保留類**：四容器白名單後代式＋自身狀態式＋21 單層 `#id{}`——嚴禁誤收斂。
- [ ] **主題視覺值**：C3 僅搬結構/token 化、色字視覺零變；**themes 檔嚴禁入層**（A1）。
- [ ] **FE-PERF-2 遺產**：content-visibility/preload/defer/節流相關規則原樣隨遷、不重構。
- [ ] **audit 不做項**：`transition:width` 保留／KaTeX code-split 不做／hover prefetch 不做。
- [ ] `login.html`／`static/vendor/**`／後端 `*.py`／`final_zh`。
- [ ] design/docs 之 icon-spec/copywriting/api-integration/interaction——不動。
- [ ] baton 暫存鐵律／收官 git-add 白名單鐵律（WORKFLOW_SOP §3）。

---

## §8 推薦 Commit 拆分

### C1 — File Split（檔案拆分七件套）
| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `static/css/{globals,layout,sidebar,content,chat,overlays,print}.css`；修改 `static/index.html`（`<style>` 刪除+7 link）；新增 `design/docs/css-architecture.md`；修改 `design/docs/README.md`；備份 `archive/…C1_index.html.bak`+`…C1_README.md.bak`（入 git）。〔C1 執行報告暫存 baton〕 |
| **安全性** | 🟡 中 — 大搬遷但零改寫；對帳+E2E 防護。 |
| **可逆性** | 🟢 高 — revert 即回 inline；新檔獨立。 |
| **驗收 grep 條件** | §6.1。 |
| **依賴關係** | 無前置。 |
| **具體實作細節** | ① `.bak`×2。② 依 §4.1 錨段映射逐段剪貼（**錨文字定位**、零改寫、含註解原樣）；歸屬歧義規則以「選擇器主體所屬區」判、判例記入 css-architecture。③ index.html `<style>`→7 `<link rel="stylesheet" href="/static/css/<f>.css">`（globals→layout→sidebar→content→chat→overlays→print 序）。④ 對帳：搬前記錄 css 塊「非空行數+`{` 計數」基線→7 檔合計相等。⑤ css-architecture.md 初版（七檔職責表+載入序+決策樹「新樣式寫哪」+歧義判例）；README 目錄加連結。⑥ §6.1+三軌×4 主題 smoke+SOP §4 表。git add（逐檔）：7 css+index.html+css-architecture+README+2 bak。 |

### C2 — Layer Cascade（層化串接）
| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/css/` 六檔（globals 層序+wrap；五檔 components wrap；print 不動）；修改 `design/docs/principles.md`+`css-architecture.md`；備份 `archive/…C2_{globals,layout,sidebar,content,chat,overlays,principles,css-architecture}*.bak`（入 git）。 |
| **安全性** | 🔴 低→控 — cascade 語意變更點；C1 已隔離搬遷風險、層內原序+1 條 important 個案+全站 E2E。 |
| **可逆性** | 🟢 高 — revert 回無層檔（C1 態）。 |
| **驗收 grep 條件** | §6.2。 |
| **依賴關係** | 前置 C1。 |
| **具體實作細節** | ① `.bak`。② globals 首行層序宣告；globals 內容三段 wrap（reset/tokens/base——依 C1 段界）；五檔整檔 `@layer components { }` wrap（**內容縮排不動、僅首尾行**、比照 FE-PERF-2 C2 包裹範式）。③ `!important` 個案（css 原 `:1260` collapsed rail）：改寫為同層可勝選擇器（如提升為後宣告/加一層 class 特異度）並移除 `!important`→E2E rail 驗證；失敗則保留+白名單註記。④ principles 三節：@layer 層序與語意（含 themes/print/自訂主題 unlayered 鐵則「主檔系嚴禁 unlayered 規則」）／作用域紀律（前綴+白名單引 css-architecture）／**margin-flow 單一節奏源模型**（FE-RHYTHM 定案補記、DOC-SYNC Q4 落點）。⑤ css-architecture 層序節。⑥ §6.2 全項 E2E。git add 逐檔。 |

### C3 — Theme Dedup（主題結構去重）
| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/themes/*.css`×4+承接之 `static/css/{content,layout,globals}.css`；修改 `design/docs/theme-guide.md`；備份 ×~7（入 git）。 |
| **安全性** | 🟡 中 — 視覺敏感；同值直移/異值 token 化雙流程+逐主題 E2E。 |
| **可逆性** | 🟢 高 — revert 回 C2 態。 |
| **驗收 grep 條件** | §6.3。 |
| **依賴關係** | 前置 C2（token 需落 tokens 層）。 |
| **具體實作細節** | ① `.bak`。② 產四檔白名單外屬性清單（Q8 白名單逐字入 css-architecture/theme-guide）→逐條：四檔同值→上移對應主檔系檔+刪四處；異值→立 `--token`（tokens 層、預設=主檔現值）+主檔結構改吃 token+四主題僅留 token 覆寫。③ theme-guide 契約改寫四節：允許屬性白名單／必供 token 清單（含新立 token）更新／cascade 語意（unlayered 必贏、禁 `!important`）／自訂主題撰寫指南（RAG-13 上傳相容聲明）。④ §6.3+四主題逐款 E2E（h2 border/divider/間距重點）。git add 逐檔。 |

### C4 — Token Slimming（tokens 瘦身歸位）
| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/css/{globals,layout,content,chat}.css`；`design/docs/css-architecture.md`；備份（入 git）。 |
| **安全性** | 🟢 高 — 純物理遷移不改名值。 |
| **可逆性** | 🟢 高。 |
| **驗收 grep 條件** | §6.4。 |
| **依賴關係** | 前置 C1（檔已在）；C2/C3 後執行避免交叉 diff。 |
| **具體實作細節** | ① `.bak`。② B 類 13 變數按消費檔遷移（layout：`--btn-*`×6+`--gap-btn-*`×3+`--toolbar-h`+`--rail-w`；chat：`--chat-pad-x`；content/layout 依 `--pad-panel` 實際消費 grep 定）——各檔頂 `@layer components { :root { … } }` 或 tokens 層內分節（run 依 C2 結構定、判例記檔）；globals 留 A 類+分節註。③ css-architecture token 歸屬節（A/B 清單×所在檔）。④ §6.4+E2E。 |

### C5 — Sidebar Scope（左欄作用域收斂）
| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（左欄 HTML class 純加法）+`static/css/sidebar.css`；`design/docs/{components,dom-reference}.md` 左欄區+`css-architecture.md` 前綴表；備份（入 git）。 |
| **安全性** | 🟡 中 — 18 行收斂；守恆 grep+E2E。 |
| **可逆性** | 🟢 高。 |
| **驗收 grep 條件** | §6.5（區=sidebar 系）。 |
| **依賴關係** | 前置 C2。 |
| **具體實作細節** | ① `.bak`。② §3-#1 sidebar 系 18 行逐行：HTML 目標元素加 `.sb-<語意>` class（原 class 保留）→ sidebar.css 選擇器改 `.sb-*` 單 class →刪 ID 後代式；`.sb-row` 既有家族沿用。③ 27+ 契約守恆 grep+左欄全互動 E2E（樹展開/選中/popup/上傳列）×4 主題。④ docs：dom-reference §2.1/§3 與 components 對應段補新 class 記載；css-architecture 前綴表起建（`.sb-*`）。 |

### C6 — Chat Scope（右欄作用域收斂）
| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（右欄 chrome class 加法）+`static/css/chat.css`（+overlays 之 hashtag 段）；docs 同步；備份。 |
| **安全性** | 🟡 中 — 13 行；含 hashtag/輸入區敏感互動。 |
| **可逆性** | 🟢 高。 |
| **驗收 grep 條件** | §6.5（區=chat 系）。 |
| **依賴關係** | 前置 C5（前綴表已建、範式複用）。 |
| **具體實作細節** | 同 C5 通式：`#chat-panel`7/`#chat-header`2/`#chat-header-actions`1/`#chat-input-area`1/`#hashtag-autocomplete`2 → `.chat-*` 家族；**`#chat-input` 4 行自身狀態式保留**（§3-#3）；E2E：串流/hashtag autocomplete/收合×4 主題；docs 同步 §2.3/§5 區。 |

### C7 — Content Chrome Scope（中欄框架收斂與白名單審計）
| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`+`static/css/{content,layout}.css`；`css-architecture.md` **白名單表完成**+components/dom-reference；備份。 |
| **安全性** | 🟢 高 — 僅 4 行+審計。 |
| **可逆性** | 🟢 高。 |
| **驗收 grep 條件** | §6.5（C7 加全 chrome 殘量=0+白名單表）。 |
| **依賴關係** | 前置 C6。 |
| **具體實作細節** | ① `#content-toolbar`2/`#content-area`1/`#app`1 → `.ct-*`；② **白名單審計收官**：§3-#2（四容器 50 行）+#3（自身狀態+21 單層）全量落 css-architecture 白名單表（附「為何保留」一句）；chrome ID 後代式殘量掃描=0 貼報告；③ E2E＋docs 同步。 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）
| 維度 | 內容 |
|---|---|
| **影響範圍** | mv+逐檔 git add：plan/tasks/C1–C7 報告（9 檔）→正式目錄；**直產** `executions/2026-07-09_FE-CSS-GOV_checkout_執行.md`；`TODO.md`+`archive/TODO_done_archive.md` 雙層；prompts 10 份+INDEX；design/docs 被修檔頂部戳統一。 |
| **安全性** | 🟢 高。 |
| **可逆性** | 🟢 高。 |
| **驗收 grep 條件** | §6.6。 |
| **依賴關係** | 前置 C1–C7 全 ship。 |
| **具體實作細節** | ① Conformance：plan §2 U1–U8 跨 commit 覆蓋總驗（U1→C1/U2→C2/U3→C5-C7/U4→C3/U5→C4/U6→矩陣逐 commit 驗/U7→各報告 E2E+SOP 表/U8→diff 邊界）+tasks §6 重跑+§7 四鐵防線；② §7.2 顯式豁免；③ 鐵律報告（staged 白名單自檢實貼）；④ docs 戳統一（新基準 hash）；⑤ TODO 雙層+hash 自癒；⑥ staged 自檢多/少一檔即停。 |

---

## §9 Open Questions

無。（plan v2 §9 八 OQ 已全數 🟢 定案〔§9.1〕；本 tasks 之「非 print `!important`＝1 宣告」為對 plan「2 條」之計數誠實微正〔原計入 1 註解行〕、處置方式不變。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-CSS-GOV 8 commits 拆分與實作細節（B1 兩段式+文獻硬綁定），執行期唯一指針 |
| **用途** | baron 審查後按序執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FE-CSS-GOV executions/ 報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 四鐵防線；§3 保留類嚴禁誤收斂；文獻配套嚴禁累積收官；git add 逐檔白名單 |
| **改版觸發條件** | plan 規格變動 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 收官歸檔後經 baron 同意移 archive/ |
| **重複防護** | 規格唯一源 plan v2；治理定案唯一源 css governance audit；本檔僅拆分/驗收/凍結表（85 行分類表+前綴表+錨段映射） |

### §99.2 Revision 歷程

- v1 (2026-07-09)：初版拆分——B1 兩段式 8 commits〔C1 拆檔七件套（錨段映射+對帳）/C2 層化（themes·print unlayered+1 條 important 個案+principles margin-flow 落點）/C3 主題去重（同值直移·異值 token 化+theme-guide 改寫）/C4 B 類 13 變數歸位/C5-C7 三區收斂（85 行分類表凍結：收斂 36·白名單 50·自身狀態保留）/checkout〕；§4.0 文獻配套矩陣硬綁定；非 print `!important` 計數微正（2→1 宣告+1 註解行）。
