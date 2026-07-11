# SEC-XSS 前端輸出消毒（DOMPurify）plan

> 目的：消除 PROJECT-REVIEW 安全審查 #2（MEDIUM，stored XSS）——前端 markdown / 來源 / 元數據渲染直接寫入 `innerHTML` 而無輸出消毒。自託管 vendored DOMPurify、於單一 markdown 渲染樞紐集中消毒（覆蓋 6 個 sink）、對 `renderSources` 改節點化 + URI scheme 白名單、對 meta / 論文清單標題等動態插值 sink 消毒；靜態/清空 sink 經分類確認安全、不動。純 `static/` 前端資產改動，零後端、零渲染管線行為變更（math/code/圖片佔位邏輯不動）。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：`static/index.html` 全程以 `marked.parse()` 原始輸出直接寫 `innerHTML`、**無任何 sanitizer**（`static/` 內無 vendored DOMPurify、grep 零命中）。`marked@9.1.6` 預設輸出 raw HTML。最尖銳為 `renderSources`（`s.uri`/`s.title` 來自 Gemini 聯網 grounding、寫入 DB grounding_sources、每次歷史重載重渲染 → **stored XSS**）；其次為 AI 對話氣泡 / 論文正文 markdown、學術扉頁 meta、論文清單標題。爆炸半徑受單 admin + HttpOnly cookie 限制，但同源 XSS 仍能外洩論文內容 / 驅動任一已認證端點。
- **解法**：
  1. **自託管 vendored DOMPurify**（比照 marked/katex：`static/vendor/dompurify/`、SHA-256 鎖定、head `defer` 載入、`tools/fetch_frontend_vendor.sh` 登記）。
  2. **markdown 集中消毒**：於 `renderMarkdownWithMath` 內 `marked.parse(t)` **之後、KaTeX 回填之前**注入 `DOMPurify.sanitize()`——一處改動覆蓋全部 6 個 markdown sink；KaTeX（可信產出）隨後插入、免去白名單 MathML。
  3. **`renderSources` 節點化**：改 `createElement('a')` + `textContent` 設標題 + `href` 走 `http(s):` scheme 白名單（拒 `javascript:` 等）。
  4. **其餘動態插值 sink——變數單體消毒（不消毒靜態模板）**：學術扉頁 meta（`normalizeAcademicHeader` 的 authors/venue/date/doi/keywords）、論文清單標題（`displayTitle`/`displaySubtitle`）——**僅對動態插值變數單體** `DOMPurify.sanitize(値)`（純文字欄位亦可用更嚴格 `textContent`）後填入靜態模板；**靜態模板本身（含 `data-tip="文件選單"` / `<svg>` menu 按鈕）不進 sanitizer**、原樣保留（精準、且免除 DOMPurify 版本/設定對可信模板的任何潛在改動）。
  5. **靜態/清空 sink 不動**：~27 個 `innerHTML=''` / 靜態字串 / 空骨架（後續以 `textContent` 填值）經分類確認無不可信插值、明列白名單、零改動。
- **影響範圍**：100% FE-Refactor（`static/index.html` + `static/vendor/dompurify/` + `tools/fetch_frontend_vendor.sh` + vendor README）；零後端、零 DB / API、零渲染管線行為（math/code/img 佔位鐵律不動）。

---

## §2 目標規格

達成後最終狀態須滿足以下可檢驗條件：

1. **DOMPurify 自託管在位**：`static/vendor/dompurify/purify.min.js` 存在、SHA-256 記錄於 vendor README、`index.html` head 以 `<script defer>` 載入、`tools/fetch_frontend_vendor.sh` 含其下載/校驗；`grep -i dompurify static/` 有命中。
2. **全部 6 個 markdown sink 消毒**：`renderMarkdownWithMath` 回傳前已經 `DOMPurify.sanitize()`；注入 XSS payload（如 `<img src=x onerror=alert(1)>`、`<script>`、`javascript:` 連結）經渲染後 **不含可執行向量**（無 `onerror`/`onload`/`<script>`/`javascript:` href）。sink 行：paper 正文 + AI 對話氣泡（現行 6 處 `innerHTML = renderMarkdownWithMath(...)`）。
3. **KaTeX / markdown 正常性不退化**：`$...$`/`$$...$$` 數學、code block、圖片、表格、粗體 / 清單等既有渲染**視覺與結構不變**（消毒點在 KaTeX 回填前、KaTeX 產出不被消毒；DOMPurify 預設允許 marked 產出之標準標籤與 `class`）。
4. **`renderSources` 節點化 + scheme 白名單**：不再字串拼 `innerHTML`；`title` 走 `textContent`、`href` 僅接受 `http:`/`https:`（其餘丟棄或不設 href）；grounding 標題含 `<img onerror>` / `javascript:` uri 時 **不執行、不破版**。
5. **meta / 論文清單標題——變數單體消毒、靜態模板零改**：`normalizeAcademicHeader` 與論文清單 `item.innerHTML` 之動態插值（authors/venue/date/doi/keywords/displayTitle/displaySubtitle）**逐一單體** `DOMPurify.sanitize(値)`（或 `textContent`）後填入模板；模板中的 `data-tip` / `<svg>` menu 按鈕**原樣保留、不進 sanitizer**（grep 實證 `item` 模板 L1505 含 `data-tip="文件選單"`+`<svg>`）；惡意標題不執行且 tooltip 功能不受影響。
6. **靜態 sink 白名單零改**：~27 個 `innerHTML=''` / 靜態字串 / 空骨架 sink 明列於 §3、確認無不可信插值、**不改動**（避免無謂改動與 diff 噪聲）。
7. **渲染管線鐵律不動**：`renderMarkdownWithMath` 的 code/math/img 佔位抽取與回填邏輯（RAG-12 / RAG-12-HOTFIX-1）**一字不改**，僅在指定點插入 sanitize 呼叫。

### §2.5 候選方案（Diverse Rollout）

XSS 消毒策略屬安全級決策、語意分散候選 ≥2：

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| **方案 A（選定）DOMPurify 集中 + renderSources 節點化（混合）** | markdown/meta/清單 → DOMPurify.sanitize()；renderSources → DOM 節點 + scheme 白名單 | 中；markdown 一處樞紐覆蓋 6 sink、改動面最小；renderSources 節點化最徹底防 uri 注入；業界標準庫、維護成本低 |
| 方案 B（否決）全面節點化（不引入 DOMPurify） | 所有 sink 改 DOM API 手工組裝 | 高；markdown 是任意 HTML 樹、手工節點化不可行（等於自寫 sanitizer）；重造輪子、易漏 |
| 方案 C（否決）僅 `marked` renderer 層轉義 | 覆寫 marked renderer 對 HTML block 轉義 | 中低但不足；擋不住 meta/renderSources 非 marked 路徑；且 marked 版本升級易破 |

- **選定理由**：markdown 產物是任意 HTML 樹，唯一穩健解是成熟 sanitizer（DOMPurify）；一處樞紐覆蓋 6 sink、改動最小。`renderSources` 是固定結構（連結列表）、節點化 + scheme 白名單比 sanitize 更徹底（連 `title` 都不進 HTML 解析）、且正是 baron 指定做法。
- **否決留痕**：B 對 markdown 不可行、C 覆蓋不全，均留底防未來重踩。

---

## §3 現況與證據

- **`static/index.html`**：
  - `renderMarkdownWithMath(raw)`（L288 起）：抽 code/img/math 佔位 → `marked.parse(t)`（L…「6. marked.parse」）→ KaTeX 回填 → 回傳 `html`。**回傳前無 sanitize**。此函式輸出被 6 處 `innerHTML` 消費。
  - `renderSources(aiMsg, sources)`（L1777-1785）：`div.innerHTML = '來源：' + sources.map(s => \`<a href="${s.uri}">${s.title}</a>\`)`——`s.uri`/`s.title` 為 Gemini grounding、**未經任何處理**。
  - `normalizeAcademicHeader`（L1634-1646）：`htmlBits` 插入 `authorsVal`/`venueVal`/`dateVal`/`doiVal`/`keywordsVal` → `metaEl.innerHTML`。
  - 論文清單 render（L1499-1503）：`item.innerHTML = \`…${displayTitle}…${displaySubtitle}…\``。
- **vendored 前端資產**：`static/vendor/` 僅 `marked/`（9.1.6）+ `katex/`（0.16.47），**無 dompurify**。
- **後端**：`web_server.py` **無 Content-Security-Policy** header（縱深防禦缺口、見 §9 OQ4）。

### §3.1 grep 鋼鐵證據

```bash
# DOMPurify 未 vendored（零命中）
$ grep -rin "dompurify" static/
(空)

# marked 9.1.6 自託管、無 sanitizer 接線
$ grep -n "marked.min.js\|marked.parse\|DOMPurify" static/index.html
9:<script src="/static/vendor/marked/marked.min.js" defer></script>
（renderMarkdownWithMath 內）let html = marked.parse(t);   # ← 之後直接回傳、無消毒

# innerHTML sink 共 36；動態插值子集（需消毒）：
$ grep -n '\${' static/index.html | grep -E "displayTitle|displaySubtitle|\.uri|\.title|Val}"
1502:  <div class="paper-title-zh">${displayTitle}</div>
1503:  <div class="paper-title-en">${displaySubtitle}</div>
1635:  ...header-authors">${authorsVal}
1640:  ...header-doi">DOI: ${doiVal}
1643:  ...header-keywords">…${keywordsVal}
1782:  <a href="${s.uri}" ...>${s.title}</a>

# markdown sink（renderMarkdownWithMath → innerHTML）6 處：
$ grep -n "innerHTML = renderMarkdownWithMath" static/index.html
1607 / 1820 / 1840 / 1893 / 1925 / 2210

# 靜態/清空 sink（安全、不動）：
$ grep -nE "innerHTML\s*=\s*''" static/index.html | wc -l   # ≥13（另含靜態字串共 ~27）

# 後端無 CSP
$ grep -n "Content-Security-Policy" web_server.py   # 零命中
```

---

## §4 跨 Phase 接縫契約

無。本任務單一模組（前端 `static/`）內改動，無 Phase/模組間資料 handoff。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| DOMPurify 消毒誤刪 KaTeX 數學輸出（MathML/span） | 🟡 中 | 消毒點置於 **KaTeX 回填之前**、僅消毒 marked 產物；KaTeX 可信產出隨後插入、不經消毒 → 根本規避。§8 E2E 驗數學渲染不退化 |
| DOMPurify 誤刪 marked 合法產出（class / code / table） | 🟢 低 | DOMPurify 預設允許標準 HTML 標籤 + `class`；§8 驗 code/表格/清單/圖片正常 |
| PUA math 佔位哨兵（/）被消毒破壞 | 🟢 低 | 佔位為純文字字元、DOMPurify 保留文字內容；消毒後 MO/MC 正則回填照常。§8 專項驗 |
| 遺漏某動態 sink（未納入消毒） | 🟡 中 | §3 已窮舉分類；tasks / 執行階段逐 sink 再 grep 覆核（`${` 插值全掃）；§8 XSS payload E2E |
| DOMPurify 增加載入體積 / GFW | 🟢 低 | 自託管（比照 marked/katex 既有先例）、SHA-256 鎖定、`defer` 不阻塞；~20KB min |
| 破壞既有前端測試 | 🟢 低 | 測試讀 `static/` 靜態源、非 runtime DOM；本改動不動 CSS/結構斷言。§8 跑全套件 |
| 消毒 meta / 清單「整段組裝 HTML」誤動可信模板（`data-tip` / `<svg>`）致 tooltip 失效 | 🟢 低（已規避） | 採**變數單體消毒**、靜態模板不進 sanitizer（§1 解法 4 / §2 #5）→ 結構性規避。技術補註：DOMPurify 預設 `ALLOW_DATA_ATTR:true` 本即保留 `data-*`、SVG 亦在預設 profile，故「整段 sanitize 弄壞 data-tip」非實際成因；採單體消毒之真正理由為**精準 + 可信模板零機率被任何 DOMPurify 版本/設定改動** |

對齊 framework §4.1 #5。

---

## §6 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] `renderMarkdownWithMath` 的 **code/math/img 佔位抽取與回填邏輯**（RAG-12 / RAG-12-HOTFIX-1 鐵律）——僅允許在 `marked.parse` 後、KaTeX 回填前插入一行 sanitize，其餘一字不改。
- [ ] `marked/` 與 `katex/` vendor 資產與其載入方式（版本、SHA-256、defer）。
- [ ] ~27 個**靜態/清空 sink**（`innerHTML=''` / 靜態字串 / 空骨架）——確認無不可信插值、不改動。
- [ ] **後端**：`web_server.py` / 任何 `.py`（CSP 屬 §9 OQ4 另案；本任務純前端）。
- [ ] DB grounding_sources schema 與既有 grounding 資料流（本任務只改「渲染時」消毒、不改儲存）。
- [ ] 前端測試斷言（`tests/` CSS/結構斷言）本體。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流分類（前端資產、非緊急 → FE-Refactor） | `CLAUDE.md §2` / `ref/WORKFLOW_SOP.md §1.1` |
| FE-Refactor 必讀 SOP | `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（vendor 自託管 / defer 載入慣例） |
| plan 結構 SSOT | `templates/template_plan.md` |
| 六階段 / 命名 / §7.2 | `ref/WORKFLOW_SOP.md §3 / §6 / §7.2` |
| 漏洞來源 | PROJECT-REVIEW 安全審查 #2（MEDIUM，stored XSS·renderSources） |
| vendored 先例 | RAG-12 KaTeX 自託管 + FE-PERF-2 C1 marked 自託管（`static/vendor/README.md`） |

> **關於提示詞所列 `baton/2026-06-01_PIPE_..._plan_v10.md`**：該檔於 baton 實際**不存在**（現存為 `2026-06-01_PIPE-SPEC_..._specification.md`，屬後端 PipelineCore 規格、與本前端 XSS 任務**正交**），故本 plan 未引用其內容；如 baron 另有所指請補正確路徑。

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試回歸**（確認未破壞前端結構 / CSS 斷言）：
  ```bash
  ./venv/bin/python -m pytest tests/ -q     # 期望：既有綠燈基線不退化（708 passed 級別）
  ```
- **預計新增測試**：於 `tests/` 新增 SEC-XSS 靜態守衛測試（讀 `static/index.html` + vendor）——斷言：① `dompurify` 已 vendored 且 head 載入；② `renderMarkdownWithMath` 於 `marked.parse` 後含 `DOMPurify.sanitize` 呼叫；③ `renderSources` 不再以 `innerHTML` 拼 `${s.uri}`/`${s.title}`（改節點化）。（純靜態源斷言，比照既有 `tests/test_bug_*` 前端守衛風格。）

### §8.2 手動端到端（E2E）驗證流程（baron）

1. **XSS payload 不執行**：於可控來源注入 `<img src=x onerror=alert(1)>`、`<script>alert(1)</script>`、`[x](javascript:alert(1))` 至（a）AI 對話回覆、（b）論文正文 markdown、（c）grounding 來源標題/URI、（d）論文標題/meta → 均**不彈窗、無 `onerror` 殘留**。
2. **正常渲染不退化**：開含數學（`$...$`/`$$`）、code block、表格、圖片、粗體清單的論文 → 視覺與結構與消毒前一致；KaTeX 數學正常。
3. **grounding 來源**：開啟聯網問答 → 「來源：」連結可點、`href` 僅 http(s)、標題為純文字。
4. **console 無 error**（FE-Refactor 驗收要求）。

> §7.2 跨 Phase 整合測試：本任務單一前端模組、無跨 Phase 資料 handoff（§4 標「無」），依 WORKFLOW_SOP §7.2 不適用；於 §9 OQ 顯式登記豁免。

---

## §9 Open Questions

> **拍板狀態（2026-07-12，baron review）**：OQ1–OQ6 全數採推薦方案定案 → 本 plan 進入 execution-ready，可拆 tasks。補強一項（見 OQ3）：meta / 論文清單改**變數單體消毒**、靜態模板（`data-tip`/`<svg>`）不進 sanitizer（已回灌 §1 解法 4 / §2 #5 / §5）。實作層（`fetch_frontend_vendor.sh` 之 npm pack 段落等）屬實作細節、依 §99.1 不入 plan、於 tasks / 執行報告定之。

| 開放問題 | 推薦方案（＝拍板結果） | 推薦理由 |
|---|---|---|
| OQ1：消毒策略？混合（DOMPurify + renderSources 節點化）vs 全節點化 vs marked renderer 層 | **混合（方案 A）** | markdown 是任意 HTML 樹、唯 sanitizer 穩健；一處樞紐覆蓋 6 sink；renderSources 固定結構、節點化最徹底（見 §2.5） |
| OQ2：DOMPurify 注入點？`marked.parse` 後 / KaTeX 回填前 vs 最終回傳前 | **marked 後、KaTeX 前** | 只消毒不可信 marked 產物、KaTeX 可信產出不經消毒 → 免白名單 MathML、根本規避數學被刪 |
| OQ3：「36 處」全數包 sanitize vs 僅動態子集 | **僅動態子集（~9 sink）+ 靜態白名單零改；meta/清單採「變數單體消毒、靜態模板不進 sanitizer」** | 對 `innerHTML=''`/靜態字串套 sanitize 無意義且增噪；變數單體消毒使可信模板（`data-tip`/`<svg>`）零機率被 DOMPurify 改動（見 §5 補註） |
| OQ4：是否本任務併加後端 CSP header（縱深防禦）？ | **不併、留 SEC-HARDEN / 獨立 BE 另案** | CSP 動 `web_server.py`（後端）、與本純前端 FE-Refactor 工作流不同類；本任務聚焦輸出消毒 |
| OQ5：DOMPurify 版本 pin | **pin 特定穩定 3.x（3.1.6 或更新 3.2.x）、確切 patch + SHA-256 於 vendor-fetch（執行階段）定案並登記 `static/vendor/README.md` + `tools/fetch_frontend_vendor.sh`** | 比照 marked/katex 自託管慣例、離線/GFW 穩定、供稽核 |
| OQ6：§7.2 跨 Phase 整合測試豁免 | **顯式豁免** | 單一前端模組、無資料 handoff，符合 §7.2 特例 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SEC-XSS 前端輸出消毒（DOMPurify）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 SEC-XSS tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-12)：初版建立（PROJECT-REVIEW 安全 #2 衍生；蒐證 DOMPurify 未 vendored / 36 sink 分類〔6 markdown + renderSources + meta + 清單標題 = 動態子集，~27 靜態安全〕/ marked 消毒注入點置 KaTeX 回填前；選定混合方案 A；§7.2 豁免；提示詞所列 PIPE plan_v10 baton 不存在且正交、未引用）
- v1.1 (2026-07-12)：baron review 拍板——§9 OQ1–OQ6 全數採推薦定案、標 execution-ready；補強 meta / 論文清單改**變數單體消毒**（靜態模板 `data-tip`/`<svg>` 不進 sanitizer，grep 實證 L1505）回灌 §1 解法 4 / §2 #5 / §5〔含技術補註：DOMPurify 預設 `ALLOW_DATA_ATTR:true` 本保留 `data-*`、採單體消毒之真因為精準而非防 data-tip 被刪〕；OQ5 版本補 3.1.6 選項；`fetch_frontend_vendor.sh` npm pack 段落屬實作細節不入 plan；規格本體方向未變
