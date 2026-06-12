# RAG-12 前端 KaTeX 數學渲染 plan

> 在前端閱讀視圖與 chat 回答中，將 final markdown 內的 LaTeX 數學（`$$...$$` 區塊式、`$...$` 行內式）渲染為正確數學排版。採 marked-katex-extension + 自託管 KaTeX；純前端，不動後端 / pipeline / RAG / 既有語料。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：含真二維 LaTeX（`\frac`、`\mathrm`、`\tau`、`\left( \right)`、`\tag`）的論文（如 `2601_16502v2`／`byz`／`2412_20138v7`）在閱讀視圖呈現**字面 `$$ ... $$` / `$...$` 原始碼**，未渲染為數學排版；Unicode 上下標無法表達二維結構，**必須引入數學渲染引擎**。
- **解法**：前端引入 **KaTeX 引擎 + `marked-katex-extension`**，於既有全域 `marked.use({...})`（`static/index.html:1567`）註冊 `$`/`$$` tokenizer + renderer；KaTeX 資產**自託管**於 `static/vendor/katex/`（離線/GFW 穩定、字型不依賴外部 CDN）；`throwOnError:false` 單式失敗降級不炸頁。一處註冊同時覆蓋 paper 閱讀視圖（`marked.parse` @L2806）與 chat 5 處（L3019/3039/3108/3117/3425）。
- **影響**：僅 `static/index.html` + 新增 `static/vendor/` 資產 + 安裝/文件檔。**零後端、零 pipeline、零 RAG、零 schema、零 .env、既有語料免 backfill**（final_zh.md 保留原始 LaTeX 純文字、僅前端渲染）。

---

## §2 目標規格

達成下列可檢驗的最終狀態：

1. **區塊式渲染**：閱讀視圖中，`2601_16502v2` 之式(1)`P_{IT}(t)=P_{base}+α·U(t)` 與式(2)`τ·dQ_cool/dt + Q_cool = k₁·P_IT` 呈現為**置中、二維排版**的數學（含分數線、上下標、希臘字母、式號 `(1)/(2)`），**不再出現字面 `$$`**。
2. **行內式渲染**：`byz` 之 `$i$`、`$v_{j}$`、`$j \neq i$`、`2601` 之 `$P_{base}$`、`$k_{1}$` 等行內數學正確內嵌於段落、**不出現字面 `$`**、且其中的 `_`/`{}` **不被 markdown 當 emphasis 咬壞**。
3. **loose delimiter 相容**：正確處理真實型態——`$$` 開在散文行尾（`...modeled by: $$`）、閉在行首後接散文（`$$ where ...`）、且 content 跨軟換行（段內無空行）；以及 `$$` 自成一行（`$$ ` 後接公式行）兩種皆須渲染。
4. **怪空格容忍**：token 間多餘空格（`P _ { \mathrm { b a s e } }`）正確渲染為 `P_base`（KaTeX math-mode 忽略空格、不需前置清洗）。
5. **失敗降級**：任一式語法錯誤時，僅該式以原碼/紅字呈現、**不影響整頁其餘內容**（`throwOnError:false`）。
6. **雙消費端覆蓋**：paper 閱讀視圖與 chat AI 回答**同時**生效（單一 `marked.use` 註冊）。
7. **離線可用**：KaTeX JS/CSS/字型**自託管**、不在 runtime 依賴外部 CDN（含字型 woff2）。
8. **零回歸**：既有 `del`/strikethrough override（L1567）、既有 6 處 `marked.parse` 既有行為（非數學內容）不變；既有語料無需重跑、final markdown byte 不變。
9. **安裝可重現**：vendored 前端資產之**版本、來源、刷新方式**有文件記載（新增 `static/vendor/README.md` + README.md 前端依賴段 + design/docs 同步）。

---

## §3 現況與證據

- **`static/index.html`**：
  - `L8`：`marked` 經 **CDN** 載入：`<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>`。
  - `L1567-1575`：**唯一全域 `marked.use({...})` 註冊點**（現註冊 `del` extension 關閉 GFM strikethrough）；KaTeX extension 註冊於此處。
  - `marked.parse` 共 **6 處消費**：paper 閱讀視圖 `L2806`（`#paper-content`）、chat AI 回答 `L3019 / L3039 / L3108 / L3117 / L3425`。單一 `marked.use` 註冊即全覆蓋。
  - `L1325`：主題 CSS 以 `<link id="theme-link" href="/static/themes/kahn.css">` 本地載入（本地資產先例）。
- **前端建置**：**無 `package.json` / node_modules / build step**（純 vanilla HTML/JS）。前端「套件」＝CDN script 或本地 vendored 檔。
- **`static/` 目錄**：僅 `index.html`、`login.html`、`themes/`（無 `vendor/`）。
- **後端安裝**：`install.sh` + `requirements.txt`（Python）+ `.env.example`；README.md 記載安裝流程（前端僅 CDN、未列為依賴）。
- **文件**：`design/docs/api-integration.md`（L59「`marked.parse()` 渲染到 `#paper-content`」、L219 chat 串流 `marked.parse`）、`design/docs/dom-reference.md`（L233/L264 marked 渲染容器）、`design/docs/principles.md`（L51 marked GFM 行為註記）。
- **真實 LaTeX 型態（`output/1/2601_16502v2/final_..._zh.md` 實測 repr）**：
  - 區塊式跨軟換行（行 63-65）：`'$$ '` → `'P _ { \\mathrm { I T } } ( t ) = ... \\tag{1}'` → `' $$ where $P _ { \\mathrm { b a s e } }$ is ...'`。
  - 區塊式開在行尾（行 67）：`'...The cooling load can be modeled by: $$ '`。
  - 行內式（行 65/69）：`$P _ { \\mathrm { b a s e } }$`、`$k _ { 1 }$`。
  - 其他樣本：`byz` 行 146 `每個 $i$ … $v _ { j }$ … $\\mathrm { O } \\dot { \\mathbf { M } } ( m - 1 ) $`；`2412` 行 370 `…如下：$$ ` + `\\frac{...}{...} \\left( \\right)`。

### §3.1 grep 鋼鐵證據

```bash
grep -n "marked\|katex\|<script" static/index.html | head
# 8:<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
# 1567:  marked.use({ ... del extension ... });
# 2806:  ...#paper-content...innerHTML = marked.parse(content);
# 3019/3039/3108/3117/3425: aiMsg.innerHTML = marked.parse(formatted);

ls static/                      # index.html  login.html  themes/   （無 vendor/）
ls package.json 2>/dev/null     # （無 → 純 vanilla/CDN）

# 真實 delimiter（PaperRead-Lab）
venv/bin/python - <<'PY'
import glob
p=glob.glob('output/1/2601_16502v2/final_*_zh.md')[0]
L=open(p,encoding='utf-8').read().splitlines()
for i in range(62,70): print(i+1, repr(L[i]))
PY
# 63 '$$ '
# 64 'P _ { \mathrm { I T } } ( t ) = P _ { \mathrm { b a s e } } + \alpha \cdot U ( t )\tag{1}'
# 65 ' $$ where $P _ { \mathrm { b a s e } }$ is the standby power ...'
# 67 '...The cooling load can be modeled by: $$ '
# 68 '\tau \frac { d Q _ { c o o l } ( t ) } { d t } + Q _ { c o o l } ( t ) = k _ { 1 } \cdot P _ { I T } ( t )\tag{2}'
# 69 ' $$ where $k _ { 1 }$ and τ are ...'
```

---

## §4 跨 Phase 接縫契約

> 本任務為單一前端模組變更，但與上游 pipeline 產物有「LaTeX 格式」之 producer/consumer handoff，故列接縫契約以凍結驗證基準。

| handoff | producer（誰產 / 形式） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| LaTeX 數學格式 | MinerU/pipeline 產出 `final_{paper}_zh.md`／`_en.md` 內之 LaTeX：`$$...$$` **loose**（可開於散文行尾冒號後、閉於行首後接散文、content 跨軟換行；亦可 `$$` 自成行）+ 行內 `$...$`（含 `_`/`{}`、token 間多餘空格） | 前端 `marked-katex-extension` 之 `$`/`$$` tokenizer 解析後交 `katex.renderToString` | **delimiter 精確身份＝「loose `$$`/`$`、非 fenced-on-own-line、可跨軟換行/行中」**；producer 既存輸出形式**凍結為驗證基準**（`2601_16502v2` 式(1)/(2)、`byz` 行內、`2412` `\frac`）；consumer 設定**必須吃下此確切形式**、不得假設「`$$` 獨立成行」。任一方變更格式須同步更新本契約與 §8 驗證樣本。 |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| `marked-katex-extension` 是否原生解析 **loose `$$`（跨軟換行/行中開閉）** | 🔴 高 | **最大不確定**。需先 spike：用真實 `2601` 樣本驗證 extension（含 `nonStandard` 選項）能否吃下「行尾開/行首閉/跨軟換行」。若不行 → fallback：渲染前以 placeholder 保護 `$$...$$`/`$...$` 抽出、`marked.parse` 後再 `katex.renderToString` 回填（自管 tokenize、徹底避開 marked 行為）。§9 Q2 凍結決策。 |
| `$...$` 內 `_`/`*` 被 markdown 當 emphasis 咬壞 | 🟡 中 | extension 將 `$`/`$$` 註冊為 tokenizer、**先於 emphasis** 解析 → 根治；以 `byz` `$v_{j}$`、`2601` `$P_{base}$` 驗證 `_` 未被吃。 |
| 與既有 `del` extension（L1567）衝突 | 🟢 低 | 不同 delimiter（`~` vs `$`）、`marked.use` 可疊加註冊；驗證 strikethrough 行為與數學渲染並存。 |
| chat 串流半截 `$$`（未閉合）中途 parse | 🟢 低 | `throwOnError:false` 自然降級為原碼；串流以 `marked.parse(accumulated)` 每塊重渲染、閉合到齊即正確（L3108/3425 既有模式）。 |
| 頁面載入體積/字型（KaTeX ~JS+CSS+woff2 數十檔） | 🟢 低 | 自託管、瀏覽器快取；KaTeX 同步渲染、對含數十式長文 CPU 可接受。 |
| 離線/GFW 取不到外部資產 | 🟢 低 | **自託管全部資產**（含字型）於 `static/vendor/`，runtime 零外部依賴。 |
| 既有語料相容 | 🟢 低 | 純前端渲染、final markdown byte 不變、RAG 索引原文不變、**免 backfill**。 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **後端全部**：`web_server.py` / `pipelines/*` / `processor/*` / `rag_*` / `paper_manager.py` / `models.py` 零改動（本任務純前端）。
- [ ] **既有 final markdown 產物格式**：`final_*_zh.md` / `_en.md` 的 LaTeX 文字不改、不清洗、不轉寫（消費端容忍）。
- [ ] **RAG / 向量**：`rag_sections`、向量庫、index_meta 不動、不重建。
- [ ] **`static/index.html:1567` 既有 `del` extension** 邏輯不得移除/改寫（僅在同一 `marked.use` 體系**疊加**註冊 katex）。
- [ ] **既有 6 處 `marked.parse` 呼叫點**之非數學渲染行為不得改變。
- [ ] **`marked` 版本（CDN 9.1.6）** 本期不升、不改載入方式（僅新增 katex 資產；marked 是否 vendoring 屬 §9 Q4 另議）。
- [ ] **`.env` / `settings.py` / `requirements.txt`（Python 後端依賴）** 不新增數學相關項（KaTeX 為前端資產）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流定義（FE-Refactor） | `ref/WORKFLOW_SOP.md §1.1` |
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 專案進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 真實 LaTeX delimiter 樣本 | `output/1/2601_16502v2/final_*_zh.md`（§3.1 repr 實測） |
| KaTeX / marked-katex-extension（外部） | KaTeX 官方 + `marked-katex-extension`（版本 pin 見 §9 Q5、自託管清單見 §8.3） |

---

## §8 驗證計畫

### §8.1 自動化測試

- 本任務為前端 JS（marked/KaTeX 於瀏覽器渲染），**pytest 無法覆蓋 marked.parse 行為** → 不新增 Python 單元測試；既有後端套件須維持綠以證未誤改：
  ```bash
  venv/bin/python -m pytest tests/ -q   # 預期與基線一致（純前端改動、零 .py diff）
  ```
- **靜態 grep 驗收**（落地後）：
  ```bash
  grep -n "katex\|markedKatex" static/index.html        # head 載入 3 行 + marked.use 註冊
  grep -n "vendor/katex" static/index.html              # 自託管路徑（非 cdn）
  ls static/vendor/katex/                                # css/js/fonts 資產存在
  ```

### §8.2 手動端到端（E2E）驗證流程

1. 開啟 `2601_16502v2` 閱讀視圖 → 式(1)/(2) 呈現二維數學（分數/上下標/希臘字母/式號）、無字面 `$$`；切換 zh/en 皆渲染。
2. 開啟 `byz` → 段落內 `$i$`/`$v_{j}$`/`$j \neq i$` 行內渲染、`_` 未被吃。
3. `2412_20138v7` → `\frac{...}{...}` 分數正確堆疊。
4. chat 對含公式論文提問、AI 回答含 `$...$`/`$$...$$` → 串流完成後正確渲染、半截不炸頁。
5. 故意餵一個語法錯誤式 → 僅該式降級（原碼/紅字）、整頁其餘正常。
6. 斷網/封鎖外部 CDN 後重載 → 數學仍渲染（自託管字型生效）。

### §8.3 §7.2 跨 Phase 整合驗收（以真實樣本充當 key-changing 驗證）

- 「LaTeX → 渲染 HTML」即 producer→consumer 之**真實 transform**；以**未經清洗的真實 `2601` final_zh**（含 loose `$$`、怪空格）載入瀏覽器、斷言式(1)/(2) 產出 KaTeX DOM（`.katex` 節點）而非原碼 `$$`，作為接縫不變式驗收（純 mock 同形式不承認）。Checkout 前必過此 E2E。

### §8.4 套件安裝檔與文件更新（本任務交付物之一）

- **新增 vendored 資產**：`static/vendor/katex/katex.min.css`、`static/vendor/katex/katex.min.js`、`static/vendor/katex/fonts/*.woff2`、`static/vendor/marked-katex-extension.umd.min.js`（版本 pin 見 §9 Q5）。
- **新增 `static/vendor/README.md`**：記載每項資產的**版本、官方來源 URL、SHA、刷新指令**（含字型完整清單）。
- **更新 `README.md`**：新增「前端 vendored 依賴」段（KaTeX/marked-katex 為何自託管、放哪、如何更新）；註明 `marked` 仍 CDN（或 §9 Q4 決議）。
- **（可選）新增 `tools/fetch_frontend_vendor.sh`**：一鍵下載/校驗 vendored 資產到 `static/vendor/`（離線部署可重現）。
- **更新 `design/docs/api-integration.md` / `dom-reference.md`**：於 `marked.parse` 渲染說明補註「`$$`/`$` 數學經 marked-katex-extension + KaTeX 渲染」。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** KaTeX 資產 CDN 還是自託管？ | **自託管**（`static/vendor/katex/`、含字型） | 離線/GFW 穩定、字型 woff2 不受外部封鎖；對齊 §4 跨環境（GCP 正式機）；marked 現雖 CDN 但字型阻塞風險高於 JS。 |
| **Q2** marked-katex-extension 能否原生吃 **loose `$$`（行尾開/行首閉/跨軟換行）**？ | **先 spike 真實 `2601` 樣本**；吃得下 → 用 extension（`nonStandard:true`）；吃不下 → **placeholder 保護 fallback**（抽 `$..$`/`$$..$$`→佔位→`marked.parse`→`katex.renderToString` 回填） | 這是最大技術不確定；以真實樣本（非理想 fenced）驗證後才凍結實作路徑，避免做完才發現不渲染（重蹈 HOTFIX-1 接縫坑）。 |
| **Q3** 是否加 `MATH_RENDER` 開關旗標？ | **不加** | 渲染 always-on + `throwOnError:false` 已 graceful；旗標增複雜度無收益；純前端可隨時 revert。 |
| **Q4** 是否一併把 `marked`（現 CDN）也 vendoring？ | **本期不動 marked、僅 vendor KaTeX** | 減少 churn 與回歸面；marked 一致性 vendoring 可另開小任務；本任務聚焦數學渲染。 |
| **Q5** KaTeX / marked-katex-extension 版本 pin？ | **KaTeX 最新穩定（0.16.x）+ marked-katex-extension 對應 marked 9.x 之相容版本** | 鎖版本可重現；落地前以實機確認相容（marked 9.1.6 ↔ extension 版本矩陣）。 |
| **Q6** 「帶數學段落未翻譯」（`2601` 行 65/67/69 整段英文）要否納入本 plan？ | **不納、另立獨立 backlog（academic 路 translator 對 `$$` 段處理）** | 與渲染正交；本 plan 只管「顯示」、翻譯覆蓋缺口屬 pipeline 後端、混入會擴大 FE-Refactor 範圍。 |
| **Q7** §7.2 整合測試形式（FE 無 pytest-for-marked）？ | **browser E2E against 真實 `2601` 樣本**（§8.3）充當 key-changing 整合驗收；不申請豁免 | 有真實 loose-`$$` 樣本可驗接縫不變式、比 pytest mock 更強；符合 §7.2「含真實 transform」要求。 |
| **Q8** chat 串流半截公式處理？ | **不特殊處理**、靠 `throwOnError:false` + 每塊重渲染 | 串流完成即正確；既有 chat 模式（accumulated→marked.parse）天然相容。 |

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

- v1 (2026-06-12)：初版建立（FE-Refactor；marked-katex-extension + 自託管 KaTeX；§4 接縫契約凍結 loose `$$`/`$` 真實型態 + 2601/byz/2412 驗證基準；§8.4 vendoring 與文件更新交付物；§9 八項 OQ，Q2 loose-`$$` spike 為最大不確定）
```
