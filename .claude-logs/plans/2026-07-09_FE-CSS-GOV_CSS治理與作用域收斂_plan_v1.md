# FE-CSS-GOV CSS 治理與作用域收斂 plan

> 目的：落地 `baton/frontend_css_governance_audit.md` 定案之治理高度——`tokens（已達標）→ 檔案拆分 + @layer 串接層 + 主題去重 + :root 瘦身 + 命名作用域收斂`——把「別耦合」從 design/docs 文件紀律升級為**結構強制**。FE-Refactor、**每個 commit 含 design/docs 同步配套**（baron 凍結要求）；純前端（`static/`）零後端、零 golden；相容底線 **Safari 18+**（已定案）。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**（audit 實測、2026-07-09 重錨於 `index.html@d4ce75a`）：①全部樣式擠在單一 inline `<style>`（`:17-1372`、~1354 行）——定位難、blast radius 無界；②**ID 後代選擇器 85 行**＝全域耦合本體（FE-RHYTHM 級 bug 的溫床）；③cascade 全靠 source-order+特異度（`@layer`=0）；④4 支主題檔各含 **35–39 行結構屬性**（border/margin/padding/width…）——h2 border 類 DRY 債、改一漏三；⑤`:root` 混雜全域 token 與元件級魔術數字（`--btn-*`/`--toolbar-h`/`--rail-w`…）。
- **解法**：五槓桿一次到位、**絞殺者式漸進**（每步等價可驗、每 commit 可 ship 可逆）——
  1. **拆檔**：inline CSS 遷出至 `static/css/` 7 支關注點檔（globals/layout/sidebar/content/chat/overlays/print）、`<link>` 載入；
  2. **@layer**：主檔系 CSS 全數入層 `reset, tokens, base, components`；**themes 與自訂主題維持 unlayered**（cascade 規範 unlayered > all layers → 主題永遠贏、自訂主題上傳契約零變）；
  3. **主題去重**：結構規則上移 base（值差異者 token 化）、主題檔收斂至「允許屬性白名單」；
  4. **:root 瘦身**：元件級變數遷至對應關注點檔（不改名不改值）；
  5. **命名作用域收斂**：chrome UI 之 ID 後代選擇器改單 class；內容渲染容器白名單保留後代式。
- **影響**：`static/index.html`（CSS 遷出+HTML class 純加法）+ 新增 `static/css/*` + `static/themes/*.css`（僅去重）+ `design/docs/*`（每 commit 配套：**新增 css-architecture.md〔ownership map〕**、principles/theme-guide/components/dom-reference 同步）。**JS 邏輯零改、DOM id 零改、JS class 契約零改名**；零 `.py`、零 golden。本案為 DOC-SYNC-1 顯式移交之 deep-doc 唯一歸屬。

---

## §2 目標規格

- **U1 — 檔案架構（拆檔）**：inline `<style>`（`:17-1372`）全數遷出至 `static/css/` **7 檔**：`globals.css`（@layer 宣告+reset+tokens+base 元素基礎）/`layout.css`（三欄框架/rail/toolbar 骨架）/`sidebar.css`（資料夾樹/論文列表/左欄底部）/`content.css`（`#paper-content` 閱讀區/current-title/abstract/KaTeX 防禦）/`chat.css`（訊息泡泡/輸入區/hashtag）/`overlays.css`（modal 七家族/popup/tooltip/dropdown）/`print.css`（`@media print` 全部）。`index.html` head 以固定序 `<link>` 載入（katex → 7 檔 globals 首 → `#theme-link` 殿後）；**inline `<style>` 塊移除**。驗：`grep -c '<style>' index.html`=0、link 序 grep、**遷移期行數/規則對帳**（7 檔規則總量＝原 1354 行等價、無孤兒規則）。
- **U2 — @layer 串接層**：`globals.css` 首行**唯一**層序宣告 `@layer reset, tokens, base, components;`；7 檔內容各自 wrap 入所屬層（print.css **不入層**＝unlayered、保留其 19 個 `!important`——print 本質是最終覆蓋）；**themes 不入層**（unlayered > layers → 主題必贏 base、與自訂主題上傳向後相容）。**非 print `!important` 現僅 2 條 → 逐一審、目標 0**（保留須於 css-architecture 白名單註記）。驗：層宣告=1 處、各檔 wrap grep、非 print `!important` ≤白名單。
- **U3 — 命名作用域收斂**：85 行 ID 後代選擇器分類處置——①**內容渲染容器白名單**（`#paper-content`/`#chat-messages`/`#current-title`/`#abstract-toolbar` 之後代規則：內容為 marked/後端產物、無法加 class、**保留**並於 css-architecture 白名單化）；②單層 `#id { }` 自身樣式（唯一元素定位/佈局）**保留**；③其餘 chrome 後代式（`#sidebar h1 .title` 類）**收斂為單 class**（HTML 加 class 純加法、CSS 改 class 選擇器）。**鐵則：DOM id 零刪改（dom-reference §8 契約）、JS 依賴之 27+ class 名零改**（`.collapsed`/`.active`/`.ctx-popup`/`.msg-*`…實測清單見 §3）。驗：chrome 區 ID 後代式殘量=0（白名單外）、JS 契約 class grep 守恆、`getElementById` 全數仍可解析。
- **U4 — 主題去重（結構上移）**：定義**主題允許屬性白名單**（色系/背景/border-color/box-shadow/字族/字級/字重/letter-spacing/text-transform/line-height/`--token` 覆寫）；白名單外結構屬性（margin/padding/width/height/display/position/flex/gap/border-width…）**上移 base**——主題間值有差異者**先 token 化**（`--divider-w`/`--content-max-w` 既有範式）再上移。4 檔結構屬性行 35–39 → **白名單外=0**。驗：4 檔逐檔 grep 白名單外屬性=0、4 主題視覺 E2E 逐一比對。
- **U5 — :root 瘦身**：`:root` 變數分類——**A 全域 token**（`--color-*`/`--space-*`/`--font-*`/`--radius-*`/`--divider-w`/`--content-max-w`/`--transition`）留 `globals.css` tokens 層；**B 元件級**（`--btn-*`×6/`--gap-btn-*`×3/`--toolbar-h`/`--pad-panel`/`--rail-w`/`--chat-pad-x`）遷至對應關注點檔頂部（**不改名、不改值**——themes/JS 零影響）並註記「元件級、非主題調校面」。驗：globals `:root` 僅 A 類、B 類各檔就位、全站 `var(--…)` 解析零破（值守恆）。
- **U6 — docs 同步配套（每 commit、baron 凍結）**：配套矩陣——
  | 改版動作 | 同 commit 配套 docs |
  |---|---|
  | 拆檔+@layer | **新增 `design/docs/css-architecture.md`**（ownership map：檔×層×前綴×白名單+「新樣式寫哪」決策樹）+ `principles.md` 補 @layer 層序/作用域紀律/**margin-flow 模型補記**（DOC-SYNC Q4 移交）+ README 連結 |
  | 主題去重 | `theme-guide.md` **契約改寫**（允許屬性白名單+必供 token 清單更新+unlayered 語意+自訂主題撰寫指南） |
  | 命名收斂（各區） | `components.md`/`dom-reference.md` 對應 class 記載同步 + css-architecture 前綴表 |
  | 每檔 | 頂部同步戳更新（基準 hash） |
- **U7 — 行為零迴歸**：每 commit——tasks §6 靜態 grep + **三軌（論文含公式/履歷/簡報）×4 主題**該區 E2E + print 預覽 + console error=0 + **FE SOP §4 檢查表**貼執行報告 §自評；遷移期堅持「**先等價搬遷、後行為改造**」兩段式（§2.5-B）；`final_zh` 零觸碰無 golden。
- **U8 — 邊界（不做）**：❌ Tailwind/CSS Modules/SPA/build step；❌ 動 JS 邏輯（HTML class 屬性純加法除外）；❌ 動 `login.html`/vendor/`renderMarkdownWithMath`；❌ 改主題視覺值（去重只搬結構、token 化保值）；❌ 夾帶 css audit 緩議項以外之效能改動（FE-PERF-2 已收官之 content-visibility 等規則**原樣隨遷**）。

### §2.5 候選方案（Diverse Rollout）

**決策 A：themes 的 cascade 策略**
| 方案 | 核心做法 | trade-offs |
|---|---|---|
| **A1（選定）** | 主檔系入層、**themes+自訂主題維持 unlayered** | cascade 規範 unlayered>layered → 主題必贏 base；**4 主題檔零層改、RAG-13 自訂主題上傳契約零變、舊自訂主題零破**；紀律面：主檔系嚴禁 unlayered 規則（css-architecture 鐵則+驗收 grep） |
| A2（否決） | themes wrap `@layer themes`（層序最末） | 語意最顯式，但須改 4 檔+上傳流程注入 wrap+**既有自訂主題全破**（unlayered 使用者檔反而蓋過 themes 層之外的一切）——相容成本高 |
| A3（否決） | `<link layer=…>` 屬性 | **非標準**（提案未落地）、不可用 |

**決策 B：遷移策略**
| 方案 | 核心做法 | trade-offs |
|---|---|---|
| **B1（選定）** | **兩段式絞殺**：先「byte 等價搬遷」（拆檔+入層、規則零改寫、行數對帳）→ 後「行為改造」（收斂/去重/瘦身逐區小步） | 每步可驗等價、diff 可審、regression 可定位到單一 commit；工期略長 |
| B2（否決） | 搬遷+改寫一次到位 | diff 不可審（搬動與改寫混雜）、出錯無法定位——FE-RHYTHM 教訓的反面教材 |

**決策 C：命名收斂深度**
| 方案 | 核心做法 | trade-offs |
|---|---|---|
| **C1（選定）** | chrome UI 全收斂 + 內容渲染容器白名單保留 | 治到病灶（跨區牽連）、不碰不可行區（markdown 產物無 class 可掛） |
| C2（否決） | 全部收斂（含內容區） | 不可行——`#paper-content h2` 等內容由 marked/後端產、無法加 class |
| C3（否決） | 只立規不收斂 | 85 行既債放任、治理變紙上談兵 |

---

## §3 現況與證據

> 2026-07-09 重錨於 `index.html@d4ce75a`（3,902 行；FE-PERF-2/DOC-SYNC-1 皆收官後）。

- **CSS 塊**：`:17`（`<style>`）–`:1372`（`</style>`）≈1,354 行；載入序＝katex css（`:14`）→ inline style → `#theme-link`（`:1375`、kahn 預設）。
- **ID 選擇器**：含 `#` 之行 141；**含後代/組合之 `#` 選擇器行 85**（收斂基數）。
- **`!important`**：總 21、**print 區內 19** → 非 print 僅 **2**（層化前需逐一審的全部存量）。
- **`@layer`**：0；**`:has()`**：0（FE-RHYTHM 消滅、底線 18+ 後屬可用但非本案目標）。
- **`:root` 變數**（37+）：A 類全域 token（color×14/space×7/font×9/radius×2/`--divider-w`/`--content-max-w`/`--transition`）＋ B 類元件級（`--btn-h`/`--btn-pad-x`/`--btn-min-w`/`--btn-icon`/`--btn-icon-svg`/`--btn-icon-stroke`/`--gap-btn-tight`/`--gap-btn-normal`/`--gap-btn-loose`/`--toolbar-h`/`--pad-panel`/`--rail-w`/`--chat-pad-x`）。
- **themes**：4 檔結構屬性行 kahn 39/kandinsky 35/mies 36/nara 35；`--content-max-w` 各檔 override（token 化範式已存在）；主題檔位於層序後（source-order 贏）——A1 化後改由 unlayered 語意保證。
- **JS class 契約**（動態綁定實測 27 個）：`active/chevron/collapsed/copied/ctx-popup/cursor-blink/danger/dropdown-trigger/dropdown-value/fname/folder-item/hashtag-popup-item/hashtag-token-remove/menu-btn/modal-mask/msg-ai/msg-copy/msg-regen/open/paper-item/paper-menu-btn/paper-progress-fill/paper-progress-text/paper-title-zh/show/visible`＋靜態 `class=` 綁定家族（msg-user/msg-system/msg-sources/chat-empty/hashtag-popup/icon-only/modal-btn/toolbar-actions/sb-row/h-title/qa-group…）——**零改名鐵則對象**（dom-reference §8 契約）。
- **FE-PERF-2 遺產隨遷**：`.msg-user`/`.msg-ai` 之 `content-visibility:auto`+`contain-intrinsic-size:auto 120px`、KaTeX 防禦規則、`transition: width`（audit #6 裁決不做 translateX、**原樣保留**）。
- **design/docs 現況**：DOC-SYNC-1 後對齊 `@8e5d1fa`（幽靈已標註、75/75）；css-architecture.md 不存在（本案 U6 新增）；principles 無 @layer/margin-flow（DOC-SYNC Q4 顯式移交本案）。

### §3.1 grep 鋼鐵證據

```bash
$ git log --oneline -1 && wc -l static/index.html
d4ce75a DOC-Refactor: DOC-SYNC-1 checkout — 成果收官歸檔 / 3902
$ grep -n '^<style>$\|^</style>$' static/index.html → 17 / 1372（≈1354 行 CSS）
$ grep -cE '^\s*#[a-z][a-z0-9-]+[ >:.][^{]*\{|^\s*#[a-z][a-z0-9-]+ [^{]*\{' <css 塊> → 85（ID 後代/組合行）
$ grep -c '!important' <css 塊> → 21；awk '/@media print/,0' | grep -c → 19（print 內）→ 非 print=2
$ for f in static/themes/*.css; grep -cE 'border|margin|padding|width|height|display' → 39/35/36/35
$ grep -oE "closest\('\.[a-z-]+'|querySelector(All)?\('\.[a-z-]+'|classList\.\w+\('[a-z-]+'" static/index.html | … | sort -u → 27 個 JS 動態 class 契約
$ grep -c '@layer' static/index.html → 0
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 純前端 CSS/HTML-class/docs 改版：後端零觸碰、SSE/API 契約零變、`final_zh` 零觸碰；唯一「handoff」為 CSS 檔間層序與 token 引用——由 U1/U2 載入序與 css-architecture ownership map 凍結（前端內部、非跨 Phase 資料鏈）。§7.2 豁免申請見 §9 Q6。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 層化後 cascade 反轉（原靠 source-order/特異度贏的規則變輸） | 🔴 高 | B1 兩段式：搬遷段**層內保持原序**且規則零改寫；非 print `!important` 僅 2 條逐一審；每 commit 三軌×4 主題 E2E；出錯可 revert 單 commit |
| 搬遷漏規則/孤兒規則 | 🟡 中 | 行數/規則對帳（7 檔總量＝原 CSS 等價）+ 分區搬遷 diff 可審 + E2E |
| 主題去重致視覺回歸（結構上移後 4 主題外觀變） | 🟡 中 | 值差異者先 token 化（--divider-w 範式）；逐主題截圖級 E2E；theme-guide 白名單同 commit 凍結 |
| 命名收斂改壞 JS 依賴 | 🟡 中 | 鐵則：DOM id 零改、27+ 契約 class 零改名（§3 清單+守恆 grep）；HTML 僅**加** class；JS 檔零編輯 |
| 自訂主題（RAG-13 上傳）相容 | 🟢 低 | A1 unlayered 策略：使用者 CSS 天然贏所有層、契約零變；theme-guide 改寫僅「新指南」非破壞 |
| 多 `<link>` 之 FOUC/請求數 | 🟢 低 | 皆 head render-blocking（行為同現狀 inline）；HTTP/2 並行；強快取屬 BE 另案（audit #2） |
| print 迴歸 | 🟡 中 | print.css 獨立檔+unlayered+19 `!important` 原樣；print 預覽入每 commit E2E |
| 大案疲勞/範圍蔓延 | 🟡 中 | commit 粒度小（每區可 ship）；U8 邊界+緩議項禁夾帶；docs 配套矩陣防「事後補文件」堆積 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **一切 `.py` 後端** / SSE/API 契約 / `final_zh`（零 golden）。
- [ ] **JS 邏輯**：`index.html` script 區（`:1610` 起）零編輯（HTML 標籤上 class 屬性純加法不在此限）；`renderMarkdownWithMath`/節流器/事件綁定全數不碰。
- [ ] **DOM id 全集（75 個）**：零刪改（dom-reference §8「保留所有 🔒 id」契約）。
- [ ] **JS class 契約（§3 實測 27+ 靜態家族）**：零改名（收斂＝CSS 選擇器換用、非改名）。
- [ ] **主題視覺值**：去重僅搬結構/token 化，色票、字族、視覺結果不變。
- [ ] **`login.html` / `static/vendor/**`**：不動。
- [ ] **FE-PERF-2 落地規則**（content-visibility/preload/defer/節流 CSS 相關）：原樣隨遷、不重構。
- [ ] **audit 定案之「不做」項**：側欄 `transition:width` 保留（#6）、KaTeX code-split 不做（#8）、hover prefetch 不做——嚴禁夾帶。
- [ ] **design/docs 其餘檔**（icon-spec/copywriting/api-integration/interaction）：不動。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| FE-Refactor 工作流+驗收（E2E、console 0） | `ref/WORKFLOW_SOP.md §1.1` |
| **FE 必讀 SOP**（§2 紅線/§3 渲染陷阱/§4 檢查表——本案每 commit 適用） | `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| 規格源（治理高度/五槓桿/底線 18+/不做清單） | `baton/frontend_css_governance_audit.md`（v2、baron 兩輪定案） |
| docs 配套原則（每 commit 同步）+ deep-doc 移交 | baron 拍板（DOC-SYNC-1 plan §9.1/checkout 銜接註） |
| 雙軌制/不可動/驗證 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1/§8` |
| 收官 git-add 白名單鐵律+checkout 報告鐵律 | `ref/WORKFLOW_SOP.md §3` |
| cascade layers/unlayered 優先權語意 | CSS Cascading L5（unlayered author styles > layered）——A1 策略規範基礎 |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- 無 pytest 面（純前端；環境無 pytest 模組、FE-PERF-2 前例）。**靜態核查族**（每 commit 對應項＋收官全量）：
  ```bash
  grep -c '<style>' static/index.html                      # U1 終態 0
  ls static/css/ | wc -l                                   # U1 =7
  grep -rc '@layer' static/css/globals.css                 # U2 層序宣告=1（首行）
  <css 檔行數/規則對帳腳本輸出>                              # U1 搬遷等價
  <chrome ID 後代式殘量掃描> → 0（白名單外）                  # U3
  for f in static/themes/*.css; <白名單外結構屬性> → 0        # U4
  <JS 契約 class 守恆 grep（27+ 名單逐一 ≥原命中數）>          # U3/U7
  grep -c '!important' static/css/{globals,layout,sidebar,content,chat,overlays}.css → ≤白名單  # U2
  git diff --stat → 僅 static/index.html + static/css/** + static/themes/*.css + design/docs/**  # U8
  ```

### §8.2 手動端到端（E2E）驗證流程（每 commit 執行該區、收官全量）

1. **三軌×4 主題矩陣**：論文（含公式/表格/圖）/履歷/簡報 × kahn/kandinsky/mies/nara——版面與改前一致、console 0。
2. **互動 chrome**：側欄收合/資料夾樹/popup/七 modal/dropdown/hashtag autocomplete/主題切換+**自訂主題上傳**（A1 相容驗證）。
3. **串流**：長答案節流渲染正常（FE-PERF-2 遺產不受拆檔影響）。
4. **print 預覽**：三軌各一次（19 `!important` 遺產行為不變）。
5. **SOP §4 檢查表**逐 commit 貼執行報告 §自評；**docs 配套當 commit 驗**（css-architecture/theme-guide/principles 對應段落存在且與實作一致）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** themes cascade 策略？ | **A1：主檔系入層、themes+自訂主題 unlayered** | 規範保證主題必贏；4 主題+RAG-13 上傳零改零破；A2 破舊自訂主題、A3 非標準。 |
| **Q2** 拆檔清單與 print 歸屬？ | **7 檔如 U1；print.css 獨立且不入層**（unlayered、19 `!important` 原樣） | print 本質最終覆蓋、入層反增反轉風險；獨立檔利 ownership。 |
| **Q3** 命名前綴策略？ | **沿用既有家族名**（.paper-/.folder-/.msg-/.modal-/.hashtag-/.dropdown-/.sb-…），僅對「無家族之 chrome 區」新增前綴；細表 tasks 期凍結 | 27+ JS 契約零改名鐵則下，「沿用+補缺」diff 最小；避免為改而改。 |
| **Q4** :root B 類遷檔是否改名（如加 `--btn-` 統一）？ | **不改名不改值、純物理遷檔+註記** | themes/JS 可能引用；改名＝額外 regression 面、零收益。 |
| **Q5** 非 print `!important`（2 條）處置？ | **逐一審：能以層序/選擇器解者移除、否則 css-architecture 白名單註記保留** | 存量僅 2、逐條處理成本低；目標非 print=0。 |
| **Q6** §7.2 跨 Phase 整合測試豁免？ | **顯式豁免** | 純前端 CSS/docs、無跨 Phase 資料 handoff；驗證由 §8.2 矩陣 E2E 承擔（同 FE-PERF-2 先例）。 |
| **Q7** 內容渲染容器白名單？ | **四容器：`#paper-content`/`#chat-messages`/`#current-title`/`#abstract-toolbar`** 之後代規則保留 | 內容為 marked/後端/renderTitleHeader 產物、無 class 可掛；白名單入 css-architecture 防蔓延。 |
| **Q8** 主題允許屬性白名單？ | **允許：color 系/background/border-color/box-shadow/font-family/font-size/font-weight/letter-spacing/text-transform/line-height/`--token` 覆寫；其餘結構屬性禁** | 對齊 theme-guide 既有精神（「結構屬主檔」）；字級/行高屬主題美學（typography 實例 15px）故允許。 |

### §9.1 定案紀錄（baron 2026-07-09 review 全數 🟢 核准）

| OQ | 定案 | 備註 |
|---|---|---|
| Q1 | 🟢 A1：主檔系入層、themes+自訂主題 unlayered | unlayered>layered 規範保證主題必贏；RAG-13 舊自訂主題零破 |
| Q2 | 🟢 7 檔；print.css 獨立且不入層 | unlayered 完美覆蓋、職責邊界清晰 |
| Q3 | 🟢 沿用既有家族名、僅補缺前綴（細表 tasks 凍結） | 27+ JS 契約僅換 CSS 選擇器、不改名——防執行期崩潰 |
| Q4 | 🟢 :root B 類純物理遷檔、不改名不改值 | 免 themes/JS 解析 regression、零成本 |
| Q5 | 🟢 非 print `!important`（2 條）個案處理、目標歸零 | 層序/選擇器解；保留須白名單註記 |
| Q6 | 🟢 §7.2 顯式豁免 | 純前端、無後端/API handoff |
| Q7 | 🟢 四容器白名單（#paper-content/#chat-messages/#current-title/#abstract-toolbar） | marked/後端產物無法預掛 class、保留後代式為唯一可行解 |
| Q8 | 🟢 主題白名單＝外觀/字體允許、佈局結構禁 | 結構強移 base、落實 SSOT/DRY |

**八 OQ 全結清、plan 規格凍結（含符合性審查三項通過：audit 100% 符合／FE SOP 完全符合／缺失檢查無缺失），可進階段 2（tasks 拆分 + 同步 TODO 🟡 WIP、依 B1 兩段式排序）。**

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-CSS-GOV「CSS 治理與作用域收斂」目標規格（五槓桿+docs 配套矩陣），作為 tasks 拆分與原子執行唯一基準 |
| **用途** | 供 baron 審查 §9 並於 tasks.md 拆分時引用；階段 3/5 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 FE-CSS-GOV tasks/執行報告；產出之 `design/docs/css-architecture.md` |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡/拍板過程；嚴禁 commit 拆分（tasks 階段、baron 明示不給）；嚴禁越 U8 邊界（build/JS 邏輯/緩議項） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務完成、baron 同意歸檔 archive/ |
| **重複防護** | CSS 治理定案唯一源在 `baton/frontend_css_governance_audit.md`（本 plan 為其落地規格、不重寫結論）；效能紅線唯一源在 FE SOP；視覺 token/元件契約唯一源在 design/docs（本案 U6 為其新增架構篇+同步、非另立源）；margin-flow 模型補記歸 principles（DOC-SYNC Q4 移交之唯一落點） |

### §99.2 Revision 歷程

- v2 (2026-07-09)：baron review 全數 🟢 核准——符合性審查三項通過（audit 100% 符合／FE SOP 完全符合〔管線防線+§4 檢查表+FE-PERF-2 遺產繼承〕／缺失檢查無缺失〔B1 兩段式+U6 配套矩陣+零改名鐵則獲點名肯定〕）；§9 八 OQ 定案入 §9.1（A1 unlayered／7 檔+print 獨立／沿用家族名／B 類不改名／2 條 !important 個案歸零／§7.2 豁免／四容器白名單／主題外觀白名單）；規格凍結、可進階段 2。
- v1 (2026-07-09)：初版——依 css governance audit（v2、底線 Safari 18+）落地五槓桿：U1 拆檔 7 檔/U2 @layer〔themes unlayered·A1〕/U3 命名收斂〔chrome 收斂+四容器白名單·C1〕/U4 主題去重〔允許屬性白名單〕/U5 :root 瘦身〔B 類遷檔不改名〕+ U6 docs 配套矩陣〔每 commit·含 css-architecture.md 新增與 margin-flow 補記移交落點〕+ U7 零迴歸驗證矩陣 + U8 邊界；§2.5 三決策組（A1/B1/C1 選定）；§9 八 OQ 待 baron 拍板。
