# RAG-12 前端 KaTeX 數學渲染 plan（v7·spike 實證·無 lookbehind·ESC 還原修補）

> 在前端閱讀視圖與 chat 回答中，將 final markdown 內的 LaTeX 數學（`$$...$$` 區塊式、`$...$` 行內式）渲染為正確數學排版。引擎採自託管 KaTeX 0.16.47；整合採三階段順序佔位保護（code/`\$`/math 隔離）+ pandoc/texmath 行內 `$` 啟發式。**整條鏈已 spike 實證（§8.0）；正則零 ES2018 特性（無 lookbehind/無 dotAll 旗標）、universal 瀏覽器相容、無載入期崩潰風險**。純前端，不動後端業務邏輯 / pipeline / RAG / 既有語料。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：含真二維 LaTeX（`\frac`、`\mathrm`、`\tau`、`\left(\right)`、`\tag`）的論文（`2601_16502v2`／`byz`／`2412_20138v7`）在閱讀視圖呈現**字面 `$$...$$` / `$...$` 原始碼**；Unicode 無法表達二維結構，**必須引入數學渲染引擎**。
- **解法**：前端引入**自託管 KaTeX 0.16.47**（`static/vendor/katex/`，含字型）；整合採**三階段順序佔位保護**——① 抽 code →佔位 ② 護 `\$`→佔位 ③ 抽 math（`$$` 先於 `$`、行內套 texmath 正則）→佔位 → 還原 code/`\$` → `marked.parse` → math 佔位呼 `katex.renderToString` 回填。`throwOnError:false` 單式降級。單一整合點覆蓋 paper（L2806）與 chat 5 處。**整合方式採佔位保護、不用 marked-katex-extension（spike 證佔位即能吃 loose `$$`）**。
- **影響**：僅 `static/index.html` + 新增 `static/vendor/katex/` 資產 + 安裝/文件檔。**零後端業務邏輯、零 pipeline、零 RAG、零 schema、零 .env、既有語料免 backfill**；新增測試僅驗 producer 契約（不改 pipeline 行為）。

---

## §2 目標規格

1. **區塊式渲染**：`2601` 式(1)(2) 二維置中（分數/上下標/希臘字母/式號），**無字面 `$$`**。
2. **行內式渲染**：`byz` `$i$`/`$v_{j}$`/`$j \neq i$`、`2601` `$P_{base}$`/`$k_{1}$` 內嵌、`_`/`{}` 不被 emphasis 咬、**單字母 `$i$` 與數字開頭 `$3x$`/`$1+x=y$` 皆不退化**。
3. **loose delimiter 相容**：「`$$` 散文行尾冒號後開／行首閉後接散文／content 跨軟換行」與「`$$` 自成一行」兩型皆渲染。
4. **怪空格容忍**：`P _ { \mathrm { b a s e } }` → `P_base`（KaTeX math-mode 忽略空格，**spike 證渲染正確、不需前置清洗**）。
5. **行內 `$` 判定（pandoc/texmath；凍結正則契約、§8.0 spike 兩版各 10/10 驗證；零 ES2018 特性）**：
   - 區塊（跨行用 `[\s\S]`、**不用 dotAll `s` 旗標**）：`/\$\$([\s\S]+?)\$\$/g`。
   - 行內（**僅 lookahead `(?!\d)`、無 lookbehind**）：`/\$([^\s$](?:[^$]*?[^\s$])?)\$(?!\d)/g`。
   - 語意：開 `$` 後接非空白（可數字）；閉 `$` 前非空白、後非數字。
   - **跳脫 `\$` 不靠 lookbehind**：由 §2.1 步驟 2 先把 `\$` 換 `__ESC_DOLLAR__`（`split('\\$')` 法）→ 抽 math 時文字已無 `\$`、lookbehind 冗餘故移除 → **無載入期 SyntaxError 風險（Safari 16.4 限制溶解）**。
   - 行為基準（spike 全過）：`$3x$`✓ `$1 + x = y$`✓ `$i$`✓ `$P_{base}$`✓ `$0.5 \tau$`✓ / `$100-$200`✗ `costs $100 to $200`✗ `costs $100`✗ `\$50`✗ 「` `$x$` `」(code)✗。
6. **code 與轉義隔離**：fenced/inline code 內 `$` 不渲染；`\$` 字面（三階段順序佔位、spike 證）。
7. **失敗降級**：單式語法錯誤僅該式 `.katex-error` 紅字、不影響整頁（`throwOnError:false` + try/catch，**spike 證壞式 `\frac{1}{` 優雅降級不拋**）。
8. **雙消費端覆蓋**：paper 閱讀視圖與 chat AI 回答同時生效。
9. **slides 緊排 / 撐欄 / 切邊（KaTeX 顯示式 CSS）**：`#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; padding:4px 0; }`。
10. **離線可用**：KaTeX JS/CSS/字型自託管、runtime 零外部 CDN。
11. **零回歸**：既有 `del` override（L1567）、6 處 `marked.parse` 非數學行為不變；既有語料免重跑、final markdown byte 不變。
12. **安裝可重現**：vendored 資產之版本/來源/SHA/刷新方式有文件。

### §2.1 三階段順序佔位演算法（spec、§8.0 spike 已驗、完整 JS 留 execution）

1. 抽 code（` ```fenced``` ` 與 `` `inline` ``）→ `__CODE_N__`
2. 護 `\$` → `__ESC_DOLLAR__`（`split('\\$').join('__ESC_DOLLAR__')`、**不用 lookbehind**；此步使 3/4 的 `$` 必為真 math、lookbehind 冗餘）
3. 抽 block math（`$$` regex）→ `__MATH_N__`（displayMode=true）
4. 抽 inline math（`$` regex）→ `__MATH_N__`（displayMode=false）
5. 還原 code 與 `\$`（**僅還原 `tempText`；math 陣列內公式仍含 `__ESC_DOLLAR__`、見步驟 7**）
6. `marked.parse(tempText)`（math 仍佔位）
7. `__MATH_N__` → 取出公式、**先把公式內 `__ESC_DOLLAR__` 還原為 `\$`**（`formula.replace(/__ESC_DOLLAR__/g,'\\$')`）→ `katex.renderToString(cleanFormula,{displayMode,throwOnError:false})` 回填，catch → `.katex-error`

> **⚠️ 步驟 7 ESC 還原鐵律**：公式**內部**含跳脫 `\$`（如 `$price = \$50$`、KaTeX 中 `\$`＝字面 `$`）時，步驟 2 已將其轉 `__ESC_DOLLAR__` 並隨抽取存入 math 陣列；步驟 5 只還原 `tempText`（公式已佔位、不在 tempText 內）。**若步驟 7 直接渲染未還原之公式，KaTeX 解析 `__ESC_DOLLAR__` 失敗→該式降級**（§8.0 spike 實證）。故步驟 7 渲染前必先還原公式內 `__ESC_DOLLAR__`→`\$`。
>
> KaTeX 顯示式輸出為 `<span class="katex-display">`（inline-level span），佔位即使落 `<p>` 內亦合法 HTML。

---

## §3 現況與證據

- **`static/index.html`**：`L8` marked CDN 9.1.6；`L1567-1575` 唯一 `marked.use({del})`；`marked.parse` 6 處（paper L2806 + chat L3019/3039/3108/3117/3425）；`L1325` 主題 CSS 本地 link。
- **前端**：無 package.json / build；`static/` 僅 index.html/login.html/themes（無 vendor/）。
- **後端安裝**：install.sh + requirements.txt + .env.example；README.md 記載。
- **文件**：api-integration.md（L59/L219）、dom-reference.md（L233/L264）、principles.md（L51）。

### §3.1 grep 鋼鐵證據

```bash
grep -n "marked\|<script" static/index.html | head
# 8:marked/9.1.6 / 1567:marked.use({del}) / 2806+3019/3039/3108/3117/3425:marked.parse
ls static/  # index.html login.html themes/（無 vendor/）；ls package.json → 無
# 真實 delimiter（PaperRead-Lab、repr 實測）2601 行 63-69：見 v4 §3.1（$$ 跨行、行尾開/行首閉後接散文 + 行內 $P_base$/$k_1$）
```

---

## §4 跨 Phase 接縫契約

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| LaTeX 數學格式 | MinerU/pipeline 產 `final_*_zh.md`/`_en.md`：`$$...$$` loose（散文行尾冒號後開／行首閉後接散文／跨軟換行；亦可自成行）+ 行內 `$...$`（含 `_`/`{}`、token 空格、單字母 `$i$`、數字開頭 `$3x$`、可能貨幣 `$`） | 前端三階段順序佔位（§2-5 正則）交 `katex.renderToString` | **delimiter＝「loose `$$`/`$`、非 fenced、跨軟換行/行中、含單字母與數字開頭公式」**；producer 既存輸出凍結為驗證基準（`2601` 式(1)(2)、`byz` 行內、`2412` `\frac`+貨幣）；**§8.0 spike 以真實樣本實證 consumer 能正確抽取+渲染**；§8.3 後端 pytest 鎖 producer 不截斷/轉義 `$$`、前端 E2E 鎖 consumer 產 `.katex` DOM。 |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解（spike 後更新） |
|---|---|---|
| ~~整合方式選型（佔位 vs extension）~~ | ✅ 已解 | **spike 證佔位保護即能吃 loose `$$`** → 凍結佔位、不用 extension（vendoring 少一檔）。 |
| ~~行內 `$` 判定（貨幣 ↔ 數字開頭/單字母）~~ | ✅ 已解 | **spike §2-5 正則 10/10 行為基準全過**（`$3x$`/`$i$` 渲染、貨幣含跨段不誤渲）。 |
| ~~怪空格 / `\tag` / `\frac` 渲染~~ | ✅ 已解 | **spike 證 KaTeX 0.16.47 渲染真實怪空格式 + `\tag` 出式號 + `\frac` 出分數線、壞式優雅降級**。 |
| ~~JS lookbehind `(?<!\\)` 於 Safari~~ | ✅ 已解 | **拿掉 lookbehind**（步驟 2 已用 `split('\\$')` 護跳脫、lookbehind 冗餘）；正則零 ES2018（無 lookbehind/無 dotAll 旗標、`[\s\S]` 取代 `s`）→ **無載入期 SyntaxError 風險、universal 相容**；spike 無 lookbehind 版 10/10 複驗。〔背景：字面量 lookbehind 在舊 Safari 為**載入期** SyntaxError、會癱瘓整段 `<script>`——本設計從根源避開。〕 |
| code 內 `$` / `\$` 轉義 | 🟢 低（spike 驗） | 三階段順序佔位徹底隔離、spike 案全過。 |
| `del` 衝突 / chat 串流半截 `$$` | 🟢 低 | 佔位在 marked 外、零衝突；未閉合 `$$` 不匹配→留原碼→閉合即渲染、無紅字抖動。 |
| KaTeX 顯示式 margin/撐欄/切邊 | 🟡 中 | §2-9 防禦 CSS。 |
| 字型/體積（自託管 ~1.5M、字型 60 檔/1.2M） | 🟢 低 | 僅 vendor woff2（~20 檔）可再瘦身；瀏覽器快取。 |
| 既有語料相容 | 🟢 低 | 純前端 byte 不變、免 backfill。 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **後端業務全部**：`web_server.py`/`pipelines/*`/`processor/*`/`rag_*`/`paper_manager.py`/`models.py` 零行為改動（§8.3 僅新增 producer 契約 pytest）。
- [ ] **既有 final markdown 產物格式**：LaTeX 文字不改/不清洗/不轉寫。
- [ ] **RAG / 向量**：`rag_sections`、向量庫、index_meta 不動。
- [ ] **`static/index.html:1567` 既有 `del` extension** 不移除/改寫。
- [ ] **既有 6 處 `marked.parse`** 非數學渲染行為不變（改呼 `renderMarkdownWithMath` 包裹、非數學輸出須等價）。
- [ ] **`marked` 版本（CDN 9.1.6）** 不升、不改載入方式（Q4 另議）。
- [ ] **`.env`/`settings.py`/`requirements.txt`** 不新增數學相關項。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流定義（FE-Refactor） | `ref/WORKFLOW_SOP.md §1.1` |
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 專案進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 真實 LaTeX delimiter 樣本 | `output/1/2601_16502v2/final_*_zh.md` |
| 行內 `$` pandoc/texmath 啟發式 + 渲染可行性 | §8.0 spike（本機 node 20 + katex 0.16.47 實證） |
| KaTeX（外部、自託管） | KaTeX 0.16.47（§8.4 vendoring 清單） |

---

## §8 驗證計畫

### §8.0 spike 結論（已執行、2026-06-12）

- **環境**：本機 node v20.20.2 + `katex@0.16.47`。
- **正則/管線（零依賴）**：§2-5 正則 + §2.1 三階段管線，對**真實 2601 loose `$$`（跨行、行尾開/行首閉後接散文）**正確抽 block + 保留散文 + 抽行內 `$P_base$`；`byz` 單字母 `$i$`/`$j \neq i$`/`$v_{j}$` 全抽；**10/10 行為基準通過**（`$3x$`/`$0.5\tau$` 渲染、`$100-$200`/跨段貨幣/`\$50`/code 內 `$` 全不誤渲）。
- **渲染（katex）**：真實怪空格式(1)(2) + `\tag`（出式號）+ `\frac`（出分數線）+ 行內全部產 `.katex` 節點 7/7；壞式 `\frac{1}{` 優雅降級 `.katex-error` 不拋。
- **無 lookbehind 複驗（v6）**：拿掉 `(?<!\\)`、改用步驟 2 `split('\\$')` 護跳脫、block 用 `[\s\S]` 取代 dotAll 旗標 → **再次 10/10**（含真實 2601 跨行 `$$`）→ 正則零 ES2018 特性、無載入期崩潰、Safari 16.4 限制溶解。
- **ESC 還原邊界（v7）**：輸入 `文字 \$ 與數學 $price = \$50$` → 步驟 4 抽出公式＝`price = __ESC_DOLLAR__50`；**未還原直接渲染 → `katex-error`（含字面 `__ESC_DOLLAR__`）；步驟 7 先 `__ESC_DOLLAR__`→`\$` 還原 → 無錯、產 `.katex` 節點**（katex 0.16.47 實證）。已納 §2.1 步驟 7 鐵律。
- **結論**：佔位保護路徑 + §2-5（無 lookbehind）正則 + 步驟 7 ESC 還原 + KaTeX 0.16.47 **整鏈可行、凍結為實作基準；無剩餘待驗項**。

### §8.1 自動化測試

- 前端行為 pytest 無法覆蓋 → 不新增前端 Python 測試；後端套件維持綠：
  ```bash
  venv/bin/python -m pytest tests/ -q   # 與基線一致（零 .py 業務 diff）
  ```
- 靜態 grep：`grep -n "katex\|renderToString\|MATH_PLACEHOLDER\|renderMarkdownWithMath\|vendor/katex" static/index.html`；`ls static/vendor/katex/`。

### §8.2 §7.2 跨 Phase 整合驗收（producer pytest + consumer E2E）

- **producer（後端 pytest、僅驗不改）**：對實際產出數學論文之路徑（`2601` 為 arXiv academic；**tasks 查實際 producer——可能 A-rail `pipeline_core`/`md_restore_processor`、未必有 B-rail `AcademicPipeline`**），取含 `$$` raw、跑該路產 `final_zh`/`_en` 後**斷言輸出含完整 `$$...$$`/`$...$`**（鎖上游不截斷/轉義）；slides 帶數學可加同型測。
- **consumer（前端 E2E）**：未清洗真實 `2601` final_zh 載入瀏覽器，斷言式(1)(2) 產 `.katex` DOM、字面 `$$` 消失。Checkout 前必過。

### §8.3 手動 E2E + 套件安裝檔/文件更新（交付物）

**E2E**：① `2601` 式(1)(2) 二維無字面 `$$`、zh/en 皆渲染 ② `byz` 行內單字母不退化 ③ `2412` `\frac`+`$3x$` 渲染、`$` 金額不誤渲 ④ chat 串流完成正確、半截不抖 ⑤ 壞式 `.katex-error` 降級 ⑥ 斷 CDN 重載仍渲染 ⑦ slides 公式頁縫隙自然/不撐欄/不切下標 ⑧ code/`\$` 顯示字面。

**套件安裝檔 / 文件（vendoring 清單 spike 確認）**：
- vendored 資產（自託管、總 ~1.5M）：`static/vendor/katex/katex.min.css`、`static/vendor/katex/katex.min.js`、`static/vendor/katex/fonts/*.woff2`（KaTeX 0.16.47；字型完整 60 檔含 ttf/woff/woff2、可僅取 **woff2 ~20 檔** 瘦身；CSS 以相對 `fonts/` 引用）。**不含 marked-katex-extension（佔位路徑）**。
- 新增 `static/vendor/README.md`：版本（katex 0.16.47）/官方來源 URL/SHA/刷新指令/字型清單。
- 新增 `tools/fetch_frontend_vendor.sh`：一鍵下載/校驗 katex 0.16.47 dist 到 `static/vendor/katex/`。
- 更新 `README.md`：前端 vendored 依賴段（KaTeX 自託管/放哪/如何更新；marked 仍 CDN）。
- 更新 `design/docs/api-integration.md`/`dom-reference.md`：`$$`/`$` KaTeX 渲染（順序佔位整合）+ `.katex-display` CSS + `renderMarkdownWithMath` 包裹點。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 狀態 / 理由 |
|---|---|---|
| **Q1** CDN 還是自託管？ | **自託管** + `tools/fetch_frontend_vendor.sh` | 字型阻斷風險高、跨環境一致、可重現。 |
| **Q2** loose `$$` 整合 + 行內 `$` 判定？ | **三階段順序佔位 + §2-5 texmath 正則** | ✅ **spike 凍結**：佔位吃 loose `$$`、正則 10/10、不用 extension。 |
| **Q3** 加 `MATH_RENDER` 旗標？ | **不加**、always-on | `throwOnError:false` graceful；純前端可隨時 hotfix revert。 |
| **Q4** 一併 vendor marked？ | **本期不動 marked、僅 vendor KaTeX** | marked 6 處消費、一併改擴大回歸面。 |
| **Q5** 版本 pin？ | **KaTeX 0.16.47**（僅此一個；不用 extension） | ✅ **spike 實證可渲染真實樣本**；佔位路徑無 extension。 |
| **Q6** 「帶數學段落未翻譯」納入？ | **不納、另立 backlog**（academic 路 translator 對 `$$` 段） | 與渲染正交、屬後端 pipeline。 |
| **Q7** §7.2 整合測試形式 + 檔案目標？ | **producer 後端 pytest（academic 路、tasks 查實際模組〔可能 A-rail md_restore〕）+ consumer 前端 E2E（`.katex` DOM）** | 不假設 B-rail AcademicPipeline 存在。 |
| **Q8** chat 串流半截公式？ | **不特殊處理**（佔位不匹配未閉合） | 避免紅字抖動。 |
| **Q9** KaTeX 顯示式 CSS？ | **`margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; padding:4px 0;`** | 避撞 3c tight list、防撐欄、防切下標。 |
| **Q10** Safari lookbehind？ | **拿掉 lookbehind**（步驟 2 `split('\\$')` 護跳脫使其冗餘）；正則零 ES2018、universal | ✅ **已解凍結**：spike 無 lookbehind 版 10/10；根源避開載入期 SyntaxError、無需 `new RegExp`/fallback。**plan 無剩餘待驗項**。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-12 前端 KaTeX 數學渲染之目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 RAG-12 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- **執行期 deviation 補註（2026-06-13 C6 收官）**：① **math 佔位符**——§2.1/§2-5 原寫 `__MATH_PLACEHOLDER_N__`，C2 執行期 spike 實證該格式被 marked GFM 雙底線解析為 `<strong>`、步驟 7 撈不到致數學靜默不渲染 → 落地改用 **Unicode PUA 哨兵 `{idx}`**（不可見/零 markdown 語意/marked 原樣穿透；code/ESC 佔位於 marked.parse 前還原故維持 `__x__`）。② **producer 模組**——§8.2/§8.3 預判 academic 路 producer，C4 grep 確認實際為 A-rail `processor/md_restore_processor.py::RestoreProcessor`（非 `AcademicPipeline`，與 Q7「不假設 B-rail AcademicPipeline」一致）。兩者皆執行期實證校正、不改本 plan 設計意圖。
- v7 (2026-06-12)：第七輪 review（步驟 7 ESC 還原漏洞）——採納：公式**內部**含 `\$`（如 `$price = \$50$`）時，步驟 2 轉 `__ESC_DOLLAR__` 隨抽取存入 math 陣列、步驟 5 只還原 tempText → 步驟 7 若直接渲染未還原公式則 KaTeX 解析失敗降級；§2.1 步驟 7 補「先還原公式內 `__ESC_DOLLAR__`→`\$` 再渲染」鐵律；§8.0 katex 0.16.47 實證 bug（未修 `katex-error`）+ 修法（產 `.katex` 節點）
- v6 (2026-06-12)：第六輪 review（Q10 lookbehind 防禦）——採納其「字面量 lookbehind 為**載入期** SyntaxError、會癱瘓整段 `<script>`」之風險認知，但**改採更乾淨解**：拿掉 lookbehind（步驟 2 已 `split('\\$')` 護跳脫、lookbehind 冗餘）+ block 用 `[\s\S]` 取代 dotAll `s` 旗標 → 正則**零 ES2018 特性、universal 相容、無載入崩潰**，免去 review 的 `new RegExp`+try/catch+fallback 複雜防禦；§8.0 無 lookbehind 版 spike 複驗 10/10；**Q10 由「待驗」轉「已解」、plan 無剩餘待驗項**
- v5 (2026-06-12)：**spike 實證**（本機 node 20 + katex 0.16.47）——§2-5 正則 10/10 行為基準 + 真實 2601 loose `$$` 跨行抽取 + byz 單字母 + KaTeX 渲染怪空格/`\tag`/`\frac`/壞式降級全過；§8.0 記錄結論；Q2/Q5 由「推薦」轉「凍結」、**確定佔位保護不用 extension**、Q5 pin KaTeX 0.16.47；§5 三風險轉 ✅ 已解；§8.4 vendoring 清單確認（60 字型檔/可瘦身 woff2）；新增 Q10（Safari lookbehind 唯一剩餘待驗）
- v4 (2026-06-12)：Q2 行內 `$` 修正為 pandoc/texmath 標準（修 v3「開 `$` 後非數字」退化 `$3x$`）+ §2-5 凍結正則 + §2.1 七步 + lookbehind 風險 + Q7 不假設 AcademicPipeline
- v3 (2026-06-12)：Q2 texmath 啟發式（修 v2 白名單退化單字母）+ 三階段順序佔位 + Q9 padding + Q7 academic 校正
- v2 (2026-06-12)：Q2 佔位保護為主+互斥+三守則；Q5 校正；Q7 拆 producer/consumer；新增 Q9 CSS
- v1 (2026-06-12)：初版（marked-katex-extension + 自託管 KaTeX；§4 接縫契約；§8.4 vendoring；八項 OQ）
```
