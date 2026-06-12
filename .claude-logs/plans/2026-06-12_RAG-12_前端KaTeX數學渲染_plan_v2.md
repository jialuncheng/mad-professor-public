# RAG-12 前端 KaTeX 數學渲染 plan（v2）

> 在前端閱讀視圖與 chat 回答中，將 final markdown 內的 LaTeX 數學（`$$...$$` 區塊式、`$...$` 行內式）渲染為正確數學排版。引擎採自託管 KaTeX；整合方式以「佔位保護」為主、`marked-katex-extension` 為備選（spike 定奪、二者互斥）。純前端，不動後端業務邏輯 / pipeline / RAG / 既有語料。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：含真二維 LaTeX（`\frac`、`\mathrm`、`\tau`、`\left( \right)`、`\tag`）的論文（`2601_16502v2`／`byz`／`2412_20138v7`）在閱讀視圖呈現**字面 `$$...$$` / `$...$` 原始碼**，未渲染為數學排版；Unicode 上下標無法表達二維結構，**必須引入數學渲染引擎**。
- **解法**：前端引入**自託管 KaTeX 引擎**（`static/vendor/katex/`，含字型），於既有全域 `marked.use({...})`（`static/index.html:1567`）所在前端流程整合數學渲染；**整合方式以「佔位保護（Placeholder Protection）」為主**——渲染前以 regex 抽出 `$$..$$`/`$..$`→替換為佔位標籤→`marked.parse`（math 內容 100% 不被 markdown 咬）→ 遍歷佔位呼 `katex.renderToString` 回填；`marked-katex-extension` 為**備選**（spike 若證實能吃 loose `$$` 則改用、二者互斥）。`throwOnError:false` 單式失敗降級。單一整合點同時覆蓋 paper 閱讀視圖（L2806）與 chat 5 處（L3019/3039/3108/3117/3425）。
- **影響**：僅 `static/index.html` + 新增 `static/vendor/` 資產 + 安裝/文件檔。**零後端業務邏輯、零 pipeline、零 RAG、零 schema、零 .env、既有語料免 backfill**（final markdown 保留原始 LaTeX 純文字、僅前端渲染）；**新增之測試僅驗 producer 契約（不改 pipeline 行為）**。

---

## §2 目標規格

1. **區塊式渲染**：`2601_16502v2` 式(1)`P_{IT}(t)=P_{base}+α·U(t)`、式(2)`τ·dQ_cool/dt + Q_cool = k₁·P_IT` 呈現為置中二維排版（分數線/上下標/希臘字母/式號 `(1)(2)`），**不再出現字面 `$$`**。
2. **行內式渲染**：`byz` `$i$`/`$v_{j}$`/`$j \neq i$`、`2601` `$P_{base}$`/`$k_{1}$` 正確內嵌、**不出現字面 `$`**、其中 `_`/`{}` **不被 markdown 當 emphasis 咬壞**。
3. **loose delimiter 相容**：正確處理「`$$` 開於散文行尾冒號後／閉於行首後接散文／content 跨軟換行」與「`$$` 自成一行」兩型。
4. **怪空格容忍**：`P _ { \mathrm { b a s e } }` 正確渲染為 `P_base`（KaTeX math-mode 忽略空格、不需前置清洗）。
5. **誤判防護（佔位保護必含）**：
   - **貨幣 `$` 不誤渲**：行內 `$...$` 僅在「**像數學**」（內容含 `\` / `_` / `^` / `{`）時轉換；純數字/純文字（如金融論文 `2412` 之 `$100`）保留原樣。
   - **code 內 `$` 不渲染**：markdown 反引號 inline code 與 fenced code block 內的 `$` 不被抽取。
   - **`$$` 先於 `$` 抽取**、`\$` 跳脫保留為字面。
6. **失敗降級**：任一式語法錯誤僅該式以原碼/紅字呈現、不影響整頁（`throwOnError:false`）。
7. **雙消費端覆蓋**：paper 閱讀視圖與 chat AI 回答同時生效（單一整合點）。
8. **slides 緊排相容（KaTeX 顯示式 CSS）**：`#paper-content .katex-display` 之上下 margin 收斂為 `var(--space-2)`（避免與 3c tight list 產生過大縫隙）+ `overflow-x:auto`（防超長公式撐破中欄）。
9. **離線可用**：KaTeX JS/CSS/**字型**自託管、runtime 零外部 CDN 依賴。
10. **零回歸**：既有 `del`/strikethrough override（L1567）、既有 6 處 `marked.parse` 非數學渲染行為不變；既有語料免重跑、final markdown byte 不變。
11. **安裝可重現**：vendored 前端資產之版本/來源/SHA/刷新方式有文件記載（`static/vendor/README.md` + README.md + design/docs）。

---

## §3 現況與證據

- **`static/index.html`**：
  - `L8`：`marked` 經 **CDN** 載入（`cdnjs.cloudflare.com/.../marked/9.1.6/marked.min.js`）。
  - `L1567-1575`：唯一全域 `marked.use({...})`（現註冊 `del` 關閉 GFM strikethrough）——數學整合於此前端流程。
  - `marked.parse` **6 處消費**：paper `L2806`（`#paper-content`）、chat `L3019/3039/3108/3117/3425`。
  - `L1325`：主題 CSS 本地 `<link href="/static/themes/kahn.css">`（本地資產先例）。
- **前端建置**：**無 package.json / build step**（純 vanilla）。前端「套件」＝CDN 或本地 vendored。
- **`static/`**：僅 `index.html` / `login.html` / `themes/`（無 `vendor/`）。
- **後端安裝**：`install.sh` + `requirements.txt`（Python）+ `.env.example`；README.md 記載安裝。
- **文件**：`design/docs/api-integration.md`（L59/L219 marked.parse）、`dom-reference.md`（L233/L264 渲染容器）、`principles.md`（L51 marked GFM 註記）。
- **真實 LaTeX 型態（`output/1/2601_16502v2/final_*_zh.md` repr 實測）**：見 §3.1。

### §3.1 grep 鋼鐵證據

```bash
grep -n "marked\|<script" static/index.html | head
# 8:<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
# 1567:  marked.use({ ... del ... });
# 2806/3019/3039/3108/3117/3425: marked.parse(...)
ls static/                 # index.html login.html themes/  （無 vendor/）
ls package.json 2>/dev/null  # （無）

venv/bin/python - <<'PY'   # PaperRead-Lab
import glob; p=glob.glob('output/1/2601_16502v2/final_*_zh.md')[0]
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

| handoff | producer（誰產 / 形式） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| LaTeX 數學格式 | MinerU/pipeline 產 `final_*_zh.md`/`_en.md` 內：`$$...$$` **loose**（散文行尾冒號後開／行首閉後接散文／content 跨軟換行；亦可自成行）+ 行內 `$...$`（含 `_`/`{}`、token 間多餘空格） | 前端佔位保護（或 marked-katex-extension）抽 `$`/`$$` 交 `katex.renderToString` | **delimiter 精確身份＝「loose `$$`/`$`、非 fenced-on-own-line、可跨軟換行/行中」**；producer 既存輸出**凍結為驗證基準**（`2601` 式(1)(2)、`byz` 行內、`2412` `\frac`）；consumer 必須吃下此確切形式、不得假設「`$$` 獨立成行」；**§8.3 後端 pytest 鎖死 producer 不得截斷/轉義 `$$`、前端 E2E 鎖死 consumer 產 `.katex` DOM**。任一方變更格式須同步更新本契約與驗證樣本。 |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **整合方式選型**（佔位保護 vs marked-katex-extension，**互斥**） | 🔴 高 | 預設佔位保護；spike 用真實 `2601` loose `$$` 驗 extension 能否原生吃，吃得下才考慮改用 extension。二者擇一、影響 vendoring 清單（§8.4）與 Q5。 |
| **貨幣 `$` 撞車**（行內 `$..$` 誤吃 `$100..$200`） | 🔴 高 | 語料含金融論文 `2412`（TradingAgents）；行內僅在內容含 `\`/`_`/`^`/`{` 時轉換（§2-5）；以 `2412` 之 `$` 金額（若有）+ 公式並存案驗證。 |
| **code 內 `$` 誤渲** | 🟡 中 | 佔位抽取須排除 inline code（反引號）與 fenced code block；以含 code 之 CS 論文驗（或構造案）。 |
| `$...$` 內 `_`/`*` 被 emphasis 咬 | 🟡 中 | 佔位保護天然根治（marked 只見佔位 HTML）；extension 路徑靠 tokenizer 先於 emphasis。 |
| 與既有 `del` extension（L1567）衝突 | 🟢 低 | 不同 delimiter；佔位保護在 marked 之外、零衝突。 |
| chat 串流半截 `$$` | 🟢 低 | 佔位 regex 不匹配未閉合 `$$` → 留原碼、閉合到齊下塊重渲即正確（無紅字抖動）。 |
| KaTeX **顯示式 margin 撞 slides 緊排** + 超長公式撐欄 | 🟡 中 | `#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; }`（§2-8）。 |
| 字型/體積（自託管數十 woff2） | 🟢 低 | 瀏覽器快取、KaTeX 同步渲染；長文數十式 CPU 可接受。 |
| 離線/GFW | 🟢 低 | 自託管全資產（含字型）、runtime 零外部依賴。 |
| 既有語料相容 | 🟢 低 | 純前端、final markdown byte 不變、RAG 原文不變、免 backfill。 |
| **版本相容**（KaTeX / extension ↔ marked 9.1.6） | 🟡 中 | 提議版本（§9 Q5）**spike 必驗、不憑記憶斷言**；佔位保護路徑下 extension 版本無關、僅 pin KaTeX。 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **後端業務全部**：`web_server.py` / `pipelines/*` / `processor/*` / `rag_*` / `paper_manager.py` / `models.py` 零行為改動（測試除外，§8.3 僅新增驗 producer 契約之 pytest、不改業務碼）。
- [ ] **既有 final markdown 產物格式**：`final_*_zh.md`/`_en.md` 的 LaTeX 文字不改、不清洗、不轉寫。
- [ ] **RAG / 向量**：`rag_sections`、向量庫、index_meta 不動、不重建。
- [ ] **`static/index.html:1567` 既有 `del` extension** 邏輯不得移除/改寫。
- [ ] **既有 6 處 `marked.parse`** 非數學渲染行為不得改變。
- [ ] **`marked` 版本（CDN 9.1.6）** 本期不升、不改載入方式（Q4 另議）。
- [ ] **`.env` / `settings.py` / `requirements.txt`** 不新增數學相關項（KaTeX 為前端資產）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流定義（FE-Refactor） | `ref/WORKFLOW_SOP.md §1.1` |
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 專案進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 真實 LaTeX delimiter 樣本 | `output/1/2601_16502v2/final_*_zh.md`（§3.1） |
| KaTeX（外部、自託管） | KaTeX 官方（版本 pin/驗證見 §9 Q5、自託管清單見 §8.4） |

---

## §8 驗證計畫

### §8.1 spike（最先、定奪整合路徑）

- worktree 內最小 HTML，用**真實 `2601` 片段**（含 loose `$$`、怪空格）測：
  - (A) marked-katex-extension（`nonStandard`）能否渲染 loose `$$`/行內 `$`；
  - (B) 佔位保護能否渲染且不誤吃貨幣/code。
- 產出：選定路徑（預設 B）+ 凍結 KaTeX（與 extension，若 A）之確切版本/相容性。

### §8.2 自動化測試

- 前端 marked/KaTeX 行為 pytest 無法覆蓋 → 不新增前端 Python 測試；既有後端套件維持綠：
  ```bash
  venv/bin/python -m pytest tests/ -q   # 與基線一致（前端改動零 .py 業務 diff）
  ```
- **靜態 grep 驗收**：
  ```bash
  grep -n "katex\|renderToString\|katex-placeholder" static/index.html
  grep -n "vendor/katex" static/index.html        # 自託管路徑（非 cdn）
  ls static/vendor/katex/                          # css/js/fonts 存在
  ```

### §8.3 §7.2 跨 Phase 整合驗收（producer pytest + consumer E2E）

- **producer（後端 pytest，僅驗不改）**：於 `tests/`（academic 路相關）新增斷言——pipeline 產出 markdown 含**完整未截斷/未轉義**的 `$$...$$` 與 `$...$`（鎖死上游不得破壞數學原文）。
- **consumer（前端 E2E）**：用**未清洗的真實 `2601` final_zh** 載入瀏覽器，斷言式(1)(2) 產出 `.katex` DOM、字面 `$$` 消失（真實 loose-`$$` transform 充當 key-changing 整合驗收，非 mock）。Checkout 前必過。

### §8.4 手動 E2E + 套件安裝檔/文件更新（交付物）

**E2E**：
1. `2601` 閱讀視圖 → 式(1)(2) 二維渲染、無字面 `$$`、zh/en 皆渲染。
2. `byz` → 行內 `$i$`/`$v_{j}$` 渲染、`_` 未被吃。
3. `2412`（金融）→ `\frac` 渲染，且若內文有 `$` 金額**不被誤渲為公式**。
4. chat 問含公式論文 → 串流完成正確渲染、半截不炸頁/不抖紅字。
5. 餵語法錯誤式 → 僅該式降級、整頁正常。
6. 斷外部 CDN 重載 → 數學仍渲染（自託管字型）。
7. slides 含公式頁 → `.katex-display` 與前後 tight list 縫隙自然、超長式不撐欄。

**套件安裝檔 / 文件（本任務交付物）**：
- 新增 vendored 資產：`static/vendor/katex/katex.min.css`、`katex.min.js`、`fonts/*.woff2`（**佔位保護路徑：不含 marked-katex-extension**；若 spike 選 extension 才加 `static/vendor/marked-katex-extension.umd.min.js`）。
- 新增 `static/vendor/README.md`：每項資產的**版本/官方來源 URL/SHA/刷新指令**（含字型完整清單）。
- 新增 `tools/fetch_frontend_vendor.sh`：一鍵下載/校驗 vendored 資產（離線部署可重現）。
- 更新 `README.md`：新增「前端 vendored 依賴」段（KaTeX 為何自託管/放哪/如何更新；marked 仍 CDN）。
- 更新 `design/docs/api-integration.md` / `dom-reference.md`：補註「`$$`/`$` 數學經 KaTeX 渲染（佔位保護整合）」+ `.katex-display` CSS 規格。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** CDN 還是自託管？ | **自託管**（`static/vendor/katex/` 含字型）+ `tools/fetch_frontend_vendor.sh` | 字型 woff2 離線/GFW 阻斷風險高；跨環境（GCP 正式機）一致；一鍵刷新可重現。 |
| **Q2** loose `$$` 整合方式？ | **佔位保護為主**（抽 `$$`/`$`→佔位→`marked.parse`→`katex.renderToString` 回填）；**marked-katex-extension 為備選、二者互斥**；spike 定奪 | 真實 `$$` 為散文行尾開/行首閉/跨軟換行，marked block tokenizer 易失誤；佔位保護徹底掌控 delimiter + 順帶解串流抖動（Q8）。**⚠️ 必含三守則**：貨幣閘門（內容含 `\`/`_`/`^`/`{` 才轉）、排除 code 內 `$`、`$$` 先於 `$` 抽 + `\$` 跳脫。 |
| **Q3** 加 `MATH_RENDER` 旗標？ | **不加**、always-on | `throwOnError:false` 已 graceful；純前端可隨時 hotfix revert；旗標增複雜度無收益。 |
| **Q4** 一併 vendor marked？ | **本期不動 marked、僅 vendor KaTeX** | marked 6 處消費、一併改擴大回歸面；marked JS 無字型阻塞，CDN 風險低；一致性 vendoring 另立任務。 |
| **Q5** 版本 pin？ | **僅 pin KaTeX（提議 0.16.x 最新穩定）**；marked-katex-extension 版本**僅在 spike 選 extension 時才相關**（提議 5.0.x 對 marked 9.x，**須 spike 實證相容、不憑記憶斷言**） | 佔位保護路徑不用 extension → 只 KaTeX 一個版本；版本相容屬可驗事實、spike 鎖定。 |
| **Q6** 「帶數學段落未翻譯」（`2601` 行 65/67/69 英文）納入？ | **不納、另立獨立 backlog**（academic 路 translator 對 `$$` 段處理） | 與渲染正交、屬後端 pipeline；混入擴大 FE 範圍、模糊測試基準。 |
| **Q7** §7.2 整合測試形式？ | **後端 pytest 驗 producer（markdown 含完整 `$$`/`$` 不截斷）+ 前端 E2E 驗 consumer（`.katex` DOM）** | 把接縫拆兩半各自可測；後端鎖上游不破壞數學原文、前端鎖渲染落地；以真實 `2601` 樣本驗、不申請豁免。 |
| **Q8** chat 串流半截公式？ | **不特殊處理**（佔位 regex 不匹配未閉合 `$$`、閉合即渲染） | 避免半截解析失敗反覆跳紅字抖動；與佔位保護天然契合。 |
| **Q9（新）** KaTeX 顯示式 CSS 與 slides 緊排/撐欄？ | **加防禦 CSS** `#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; }` | KaTeX `displayMode` 預設 `margin:1em 0` 會與 3c tight list 產生大縫；超長式須 `overflow-x:auto` 防撐破中欄。 |

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

- v2 (2026-06-12)：第二輪 review 補強——Q2 改「佔位保護為主、與 extension 互斥」+ 補三守則（貨幣閘門/排除 code/`$$`先抽+`\$`跳脫）；Q5 校正（佔位路徑只 pin KaTeX、版本須 spike 實證不斷言）；Q7 拆 producer pytest + consumer E2E；**新增 Q9 KaTeX 顯示式 CSS（slides 緊排 margin + overflow-x 防撐欄）**；§2-5/§2-8 規格化、§5 加貨幣/code/版本/margin 四風險、§8.1 spike 前置、§8.4 vendoring 隨整合路徑調整
- v1 (2026-06-12)：初版建立（FE-Refactor；marked-katex-extension + 自託管 KaTeX；§4 接縫契約凍結 loose `$$`/`$`；§8.4 vendoring 與文件更新；§9 八項 OQ）
```
