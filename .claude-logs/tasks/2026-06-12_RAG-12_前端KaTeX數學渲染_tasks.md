# RAG-12 前端 KaTeX 數學渲染 — Tasks

> 本文件為 RAG-12 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-12_RAG-12_前端KaTeX數學渲染_plan_v7.md` 計畫產出，含 6 個 Commit。
> 工作流：**FE-Refactor**。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 6+ 個 | `static/vendor/katex/katex.min.css` / `static/vendor/katex/katex.min.js` / `static/vendor/katex/fonts/*.woff2`（~20 檔，KaTeX 0.16.47）/ `static/vendor/README.md` / `tools/fetch_frontend_vendor.sh` / `tests/test_latex_preservation.py` |
| **修改檔案** | 4 個 | `static/index.html`（head 載入 + `renderMarkdownWithMath` + CSS + 6 處 marked.parse 接線；含 `.bak`）/ `README.md`（前端 vendored 依賴段）/ `design/docs/api-integration.md` / `design/docs/dom-reference.md` |
| **目錄初始化** | 1 個 | `static/vendor/katex/`（自託管前端數學資產）|
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 6 個 | C1 → C2 → C3 → C4 → C5 → C6（Checkout） |
| **baton 歸檔** | 1 次 | C6 收官：`mv` baton `plan_v1~v7` → `plans/` + `tasks` → `tasks/` + `C1~C5_執行` → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：含真二維 LaTeX（`\frac`/`\mathrm`/`\tau`/`\tag`）的論文（`2601_16502v2`/`byz`/`2412`）在前端閱讀視圖與 chat 顯示**字面 `$$`/`$` 原始碼**；marked 不渲染數學、Unicode 無法表達二維結構。
- **解法**：前端自託管 KaTeX 0.16.47 + 三階段順序佔位整合（plan §2.1、spike 實證），原子化為 6 個 commit：
  - **C1 — Vendor KaTeX Assets（引入自託管 KaTeX 資產與載入）**
  - **C2 — Core Render Pipeline（核心數學渲染管線與 CSS）**
  - **C3 — Wire Consumers（接線六處 marked.parse 消費端）**
  - **C4 — Producer Contract Test（producer 契約 pytest）**
  - **C5 — Docs Sync（文件同步）**
  - **C6 — Checkout（收官歸檔）**
- **影響範圍**：前端 `static/index.html` + `static/vendor/` 新資產 + 文件 + 1 後端測試；**零後端業務邏輯、零 pipeline、零 RAG、零 schema、零 .env、既有語料免 backfill**。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `static/index.html:8` | marked.js 經 CDN 載入（9.1.6） | 無數學引擎；`$$`/`$` 不渲染 |
| `static/index.html:1567-1575` | 唯一全域 `marked.use({del})` | 無 KaTeX 整合 |
| `static/index.html:2806` | paper：`marked.parse(content)` → `#paper-content` | 直接 parse、數學原碼洩漏 |
| `static/index.html:3019/3039/3108/3117/3425` | chat：5 處 `marked.parse(formatted)` | 同上、chat 數學不渲染 |
| `static/`（目錄） | 僅 index.html/login.html/themes | 無 `vendor/` 自託管資產目錄 |
| `README.md` / `design/docs/` | 記載安裝與渲染 | 無前端 vendored 依賴 / 數學渲染說明 |

---

## §3 觀察問題

### 問題 #1：真二維 LaTeX 字面洩漏
- **證據**：`output/1/2601_16502v2/final_*_zh.md` 行 63-69（`$$ P_{IT}(t)=... \tag{1} $$`、行內 `$P_{base}$`）；前端 `static/index.html:2806` `marked.parse` 直渲。
- **影響**：論文/簡報數學式以原始碼呈現、不可讀；chat 回答含公式同樣破版。

### 問題 #2：loose delimiter + 怪空格 + 貨幣/code 邊界
- **證據**：plan §8.0 spike——`$$` 散文行尾開/行首閉/跨軟換行；token 怪空格；金融論文 `2412` 貨幣 `$`；code 內 `$`。
- **影響**：天真的 `$$` block 假設與貨幣誤渲會造成 regression；需三階段順序佔位 + texmath 正則根治。

---

## §4 設計方案

> 設計依據與 spike 實證見 plan_v7 §1/§2/§8.0；本節僅落地路線，正則/演算法以 plan §2-5/§2.1 為唯一規格源。

### §4.1 C1 — 引入自託管 KaTeX 資產與載入
新增 `static/vendor/katex/`（KaTeX 0.16.47 dist：`katex.min.css` + `katex.min.js` + `fonts/*.woff2`）；`tools/fetch_frontend_vendor.sh` 一鍵下載校驗；`static/vendor/README.md` 記版本/來源/SHA；`static/index.html` head 加 `<link>`/`<script>` 載入（KaTeX 全域可用、尚未接線 → 行為等價）。

### §4.2 C2 — 核心數學渲染管線與 CSS
`static/index.html` 新增 `renderMarkdownWithMath(raw)`（plan §2.1 七步、§2-5 無 lookbehind 正則、步驟 7 ESC 還原、`throwOnError:false` + `.katex-error` 降級）；加 `#paper-content .katex-display` 防禦 CSS（plan §2-9）。**僅定義、不接線** → 既有渲染不變。

### §4.3 C3 — 接線六處 marked.parse 消費端
將 paper（L2806）+ chat 5 處（L3019/3039/3108/3117/3425）的 `marked.parse(x)` 改呼 `renderMarkdownWithMath(x)`；非數學內容輸出須等價。

### §4.4 C4 — producer 契約 pytest
`tests/test_latex_preservation.py`：對實際產出數學論文之 academic 路（tasks 階段確認模組、可能 A-rail `md_restore_processor`/`pipeline_core`），斷言產出 markdown 保留完整 `$$...$$`/`$...$` 不截斷/轉義（plan §8.2 producer 半、§7.2 整合 producer 側）。

### §4.5 C5 — 文件同步
`README.md` 前端 vendored 依賴段；`design/docs/api-integration.md` + `dom-reference.md` 補數學渲染（順序佔位整合）+ `.katex-display` CSS + `renderMarkdownWithMath` 包裹點。

### §4.6 C6 — Checkout 收官歸檔
Conformance 驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C3 接線改 6 處 marked.parse、非數學行為退化 | 🟡 中 | `renderMarkdownWithMath` 對無 `$`/`$$` 輸入須與 `marked.parse` 等價（無數學→不抽取→直接 parse）；C2 spike 已證；C3 後逐一 E2E paper+chat 非數學內容。 |
| Safari lookbehind 載入崩潰 | 🟢 低（已解） | plan v6/v7 拿掉 lookbehind、正則零 ES2018；spike 無 lookbehind 版 10/10。 |
| 公式內 `\$` 渲染失敗 | 🟢 低（已解） | C2 步驟 7 ESC 還原（plan v7、spike 實證）。 |
| 自託管字型路徑錯（CSS 相對 `fonts/`） | 🟡 中 | C1 後即時 E2E 開含公式頁、確認字型載入無 404；`fetch_frontend_vendor.sh` 校驗。 |
| academic 路 producer 模組不明 | 🟡 中 | C4 tasks→execution 先 grep 確認產出 2601 的實際路徑、不假設 B-rail AcademicPipeline。 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
ls static/vendor/katex/katex.min.css static/vendor/katex/katex.min.js   # 存在
ls static/vendor/katex/fonts/ | grep -c woff2                            # >0
grep -n "vendor/katex/katex.min" static/index.html                       # head 載入 css+js 各 1
ls tools/fetch_frontend_vendor.sh static/vendor/README.md                # 存在
venv/bin/python -m pytest tests/ -q                                      # 後端綠（零 .py 業務 diff）
```

### §6.2 C2 驗收
```bash
grep -n "function renderMarkdownWithMath\|katex.renderToString\|__MATH_PLACEHOLDER\|__ESC_DOLLAR__" static/index.html  # 函式+回填+佔位
grep -n "katex-display" static/index.html                                # CSS 規格
grep -n "(?<!" static/index.html                                         # 期望：0 命中（無 lookbehind）
```

### §6.3 C3 驗收
```bash
grep -cn "renderMarkdownWithMath(" static/index.html   # 期望 ≥7（1 定義 + 6 呼叫點）
grep -n "marked.parse(" static/index.html              # 殘留直呼應為 0（或僅 renderMarkdownWithMath 內部 1 處）
```

### §6.4 C4 驗收
```bash
venv/bin/python -m pytest tests/test_latex_preservation.py -v   # producer 契約綠
grep -n "\\$\\$\|preserv\|latex" tests/test_latex_preservation.py
```

### §6.5 C5 驗收
```bash
grep -n "KaTeX\|vendor/katex\|katex" README.md design/docs/api-integration.md design/docs/dom-reference.md
```

### §6.6 手動 E2E（baron、非 commit）
plan §8.3 八項：2601 式(1)(2)、byz 單字母、2412 `\frac`+貨幣不誤渲、chat 串流、壞式降級、斷 CDN、slides 緊排、code/`\$` 字面。

### §6.7 §7.2 跨 Phase 整合驗收
- producer：C4 pytest（academic 路保留 `$$`）。
- consumer：真實 2601 final_zh 載入瀏覽器斷言 `.katex` DOM、字面 `$$` 消失（Checkout 前必過）。

---

## §7 不可動清單

- [ ] **後端業務代碼**：`web_server.py` / `pipelines/*` / `processor/*` / `rag_*` / `paper_manager.py` / `models.py` — 100% 不動行為（C4 僅新增 `tests/` 測試、不改業務碼）。
- [ ] **既有 final markdown 產物格式**：`final_*_zh.md`/`_en.md` LaTeX 文字不改/不清洗/不轉寫。
- [ ] **RAG / 向量**：`rag_sections`、向量庫、index_meta 不動、不重建。
- [ ] **`static/index.html:1567` 既有 `del` extension** 不移除/改寫。
- [ ] **`marked` 版本（CDN 9.1.6）** 不升、不改載入方式。
- [ ] **`.env` / `settings.py` / `requirements.txt`** 不新增數學相關項。
- [ ] **主 repo 目錄** — 嚴禁讀寫（唯一合法工作目錄 worktree）。

---

## §8 推薦 Commit 拆分

### C1 — Vendor KaTeX Assets（引入自託管 KaTeX 資產與載入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `static/vendor/katex/katex.min.css`、`static/vendor/katex/katex.min.js`、`static/vendor/katex/fonts/*.woff2`（KaTeX 0.16.47 dist）、`static/vendor/README.md`、`tools/fetch_frontend_vendor.sh`；修改 `static/index.html`（head 載入、含 `.bak`） |
| **安全性** | 🟢 高 — 純資產新增 + head 載入，KaTeX 全域可用但未接線、行為等價 |
| **可逆性** | 🟢 高 — `git revert C1` 移除 vendor/ 與 head 兩行 |
| **驗收 grep 條件** | §6.1（資產存在 + head 載入命中 + 後端綠） |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1. 備份：`cp static/index.html .claude-logs/archive/2026-06-12_RAG-12_C1_index.html.bak`。2. 寫 `tools/fetch_frontend_vendor.sh`：下載 `katex@0.16.47` dist（katex.min.css / katex.min.js / fonts/ 之 woff2）至 `static/vendor/katex/`，列印各檔 SHA-256 校驗。3. 執行該腳本取得實體資產（或 baron 端執行；資產入版控）。4. 寫 `static/vendor/README.md`：記 `katex 0.16.47`、官方來源 URL、各資產 SHA、刷新指令（跑 fetch 腳本）、字型清單。5. `static/index.html` head（緊接 L8 marked `<script>` 之後）前插兩行：`<link rel="stylesheet" href="/static/vendor/katex/katex.min.css">` 與 `<script src="/static/vendor/katex/katex.min.js"></script>`，以 `<!-- === [RAG-12 C1] === -->` 包裹。6. 驗 KaTeX CSS 以相對 `fonts/` 引用字型、路徑 `/static/vendor/katex/fonts/` 可達。**不接線、不寫 render 邏輯**。 |

### C2 — Core Render Pipeline（核心數學渲染管線與 CSS）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/index.html`（新增 `renderMarkdownWithMath` 函式 + `.katex-display` CSS，含 `.bak`） |
| **安全性** | 🟡 中 — 新增純函式 + CSS，未接線故既有渲染不變；函式邏輯已 spike 實證 |
| **可逆性** | 🟢 高 — `git revert C2` 移除函式與 CSS |
| **驗收 grep 條件** | §6.2（函式/回填/佔位命中 + CSS + 無 lookbehind 0 命中） |
| **依賴關係** | C1（需 KaTeX 全域） |
| **具體實作細節** | 1. 備份 index.html → `.bak`（C2 命名）。2. 於 `marked.use({del})`（L1567 區塊）**之後**新增 `renderMarkdownWithMath(raw)`，嚴格依 plan §2.1 七步：① `raw.replace(/(```[\s\S]*?```|`[^`\n]+?`)/g, …)` 抽 code→`__CODE_N__`；② `split('\\$').join('__ESC_DOLLAR__')` 護跳脫；③ `replace(/\$\$([\s\S]+?)\$\$/g, …)` 抽 block→`__MATH_N__`（displayMode=true）；④ `replace(/\$([^\s$](?:[^$]*?[^\s$])?)\$(?!\d)/g, …)` 抽 inline→`__MATH_N__`（displayMode=false）；⑤ 還原 code（`__CODE_N__`→原文）與 `__ESC_DOLLAR__`→`\$`（**僅 tempText**）；⑥ `marked.parse(tempText)`；⑦ `replace(/__MATH_(\d+)__/g, …)`：取公式、**先 `formula.replace(/__ESC_DOLLAR__/g,'\\$')` 還原**、再 `katex.renderToString(clean, {displayMode, throwOnError:false})`，try/catch → `<span class="katex-error" style="color:#cc0000">…</span>`。3. **正則一律字面量、零 lookbehind、block 用 `[\s\S]` 不用 `s` 旗標**（plan v7 §2-5）。4. 加 CSS（主 `<style>` `#paper-content` 區）：`#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; padding:4px 0; }`。5. 全段 `// === [RAG-12 C2 START/END] ===` 包裹。**不改任何 marked.parse 呼叫點**。 |

### C3 — Wire Consumers（接線六處 marked.parse 消費端）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/index.html`（L2806 paper + L3019/3039/3108/3117/3425 chat 共 6 處 marked.parse → renderMarkdownWithMath，含 `.bak`） |
| **安全性** | 🟡 中 — 改全部渲染入口；非數學內容須等價（C2 函式無 `$` 時退化為 `marked.parse`） |
| **可逆性** | 🟢 高 — `git revert C3` 還原 6 處呼叫 |
| **驗收 grep 條件** | §6.3（renderMarkdownWithMath 呼叫 ≥7、殘留直呼 marked.parse 收斂） |
| **依賴關係** | C2（需函式存在） |
| **具體實作細節** | 1. 備份 → `.bak`（C3）。2. 逐一替換 6 處：`marked.parse(content)`（L2806）→ `renderMarkdownWithMath(content)`；`marked.parse(formatted)`（L3019/3108/3117/3425）→ `renderMarkdownWithMath(formatted)`；`marked.parse(formatted || '')`（L3039）→ `renderMarkdownWithMath(formatted || '')`。3. 唯一允許殘留的 `marked.parse` 為 `renderMarkdownWithMath` **函式內部步驟 6** 那一處。4. 每處 `// === [RAG-12 C3] ===` 行內標記。5. 確認 6 處行號因 C1/C2 前插而位移、以**內容比對**定位非死行號。 |

### C4 — Producer Contract Test（producer 契約 pytest）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `tests/test_latex_preservation.py` |
| **安全性** | 🟢 高 — 純新增測試、不改業務碼 |
| **可逆性** | 🟢 高 — `git revert C4` 移除測試檔 |
| **驗收 grep 條件** | §6.4（pytest 綠 + 斷言 `$$` 保留） |
| **依賴關係** | 無（與 C1-C3 正交、可獨立） |
| **具體實作細節** | 1. **先 grep 確認產出 2601 的實際 producer 模組**（`grep -rn "final_.*_zh\|article_zh_path" pipelines/ processor/ pipeline_core.py`），鎖定 academic 路產 markdown 之函式（可能 A-rail `md_restore_processor` / `pipeline_core`、非 B-rail）。2. 寫 `test_latex_preservation.py`：構造含 `$$ ... $$` block + 行內 `$x$` 之 section/raw，跑該 producer 函式（mock 翻譯/embedding 隔離），斷言輸出 markdown substring **含完整 `$$`** 與 `$...$`、未被截斷或轉義（如 `\$`）。3. 若 academic 路產出函式無法獨立單測，退而對 `md_restore`/`tiling` 等不剝除 `$` 之最近層斷言、並於測試 docstring 註明 producer 契約範圍。4. 不改任何業務碼。 |

### C5 — Docs Sync（文件同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `README.md`、`design/docs/api-integration.md`、`design/docs/dom-reference.md` |
| **安全性** | 🟢 高 — 純文件 |
| **可逆性** | 🟢 高 — `git revert C5` |
| **驗收 grep 條件** | §6.5（三檔含 KaTeX/vendor 說明） |
| **依賴關係** | C1-C3（描述已落地之資產與接點） |
| **具體實作細節** | 1. `README.md` 新增「前端 vendored 依賴」段：KaTeX 0.16.47 自託管於 `static/vendor/katex/`、為何自託管（離線/GFW 字型）、如何更新（`tools/fetch_frontend_vendor.sh`）、marked 仍 CDN 註記。2. `design/docs/api-integration.md`（L59/L219 marked.parse 處）補註：`$$`/`$` 數學經 `renderMarkdownWithMath`（三階段順序佔位 + KaTeX）渲染、paper+chat 共用。3. `design/docs/dom-reference.md`（L233/L264 渲染容器）補 `.katex` / `.katex-display` 節點 + CSS 規格。 |

### C6 — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（結案）；baton → 正式目錄歸檔（`mv` + `git add`）；無代碼改動 |
| **安全性** | 🟢 高 — 純文件/歸檔 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | Conformance 全維度（plan §2 U1-U12 / tasks §6 grep+pytest / §7.2 整合〔producer pytest + consumer E2E〕/ 不可動 git 證據 / 提示詞稽核） |
| **依賴關係** | C1-C5 全部 ship |
| **具體實作細節** | 1. Conformance 五維度核對（目標規格 / §6 驗收 / 不可動清單 git diff / §7.2 整合〔C4 producer + consumer E2E〕/ 提示詞）。2. baton 一次性 `mv` 歸檔：`plan_v1~v7` → `plans/`、`tasks` → `tasks/`、`C1~C5_執行` → `executions/`；`git add` 含 `.bak`（archive/）、代碼、`static/vendor/`、測試、文件、TODO、prompts/INDEX、歸檔後文件。3. TODO 將 RAG-12 從 active 移除、寫入 ✅ 已完成表 + 索引同步。4. git log 自癒回填歷史 `待 baron 回填` 佔位符。**不自發 commit/push。** |

---

## §9 Open Questions

無。（plan_v7 §9 十項 OQ 已於七輪 review + 三次 spike 結清；Q6「帶數學段落未翻譯」已定案另立 backlog、不屬本任務範圍。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-12 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RAG-12 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動後端業務代碼；嚴禁跨 Commit 混合不同關注；嚴禁自動 `git commit`/`git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；正則/演算法唯一規格源為 plan_v7 §2-5/§2.1；不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- **執行期 deviation 補註（2026-06-13 C6 收官）**：① C2 §8 之 math 佔位 `__MATH_N__` 落地改 **Unicode PUA 哨兵**（spike 證 `__x__` 被 marked 雙底線咬 `<strong>`、步驟 7 撈不到）；② C4 §8 producer class `AcademicPipeline` 不存在、grep 得實際 **`RestoreProcessor`**（`md_restore_processor.py`）。詳見 plan_v7 §99.2 同註 + C2/C4 執行報告。
- v1 (2026-06-13)：初版拆分（依 plan_v7）——6 Commit：C1 自託管資產與載入 / C2 核心渲染管線+CSS / C3 接線六處 marked.parse / C4 producer 契約 pytest / C5 文件同步 / C6 Checkout；§0.5 成果盤點 + §8 六維度表（含 plan §2.1 七步、§2-5 無 lookbehind 正則、步驟 7 ESC 還原 具體實作細節）
