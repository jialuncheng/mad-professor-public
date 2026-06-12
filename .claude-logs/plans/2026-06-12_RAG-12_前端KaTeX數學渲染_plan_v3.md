# RAG-12 前端 KaTeX 數學渲染 plan（v3）

> 在前端閱讀視圖與 chat 回答中，將 final markdown 內的 LaTeX 數學（`$$...$$` 區塊式、`$...$` 行內式）渲染為正確數學排版。引擎採自託管 KaTeX；整合採「三階段順序佔位保護」（code/`\$`/math 隔離）+ texmath 啟發式行內 `$` 判定。純前端，不動後端業務邏輯 / pipeline / RAG / 既有語料。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：含真二維 LaTeX（`\frac`、`\mathrm`、`\tau`、`\left( \right)`、`\tag`）的論文（`2601_16502v2`／`byz`／`2412_20138v7`）在閱讀視圖呈現**字面 `$$...$$` / `$...$` 原始碼**；Unicode 無法表達二維結構，**必須引入數學渲染引擎**。
- **解法**：前端引入**自託管 KaTeX**（`static/vendor/katex/`，含字型）；整合採**三階段順序佔位保護**——① 抽 code（fenced+inline）→佔位 ② 護 `\$`→佔位 ③ 抽 math（`$$` 先於 `$`、行內套 texmath 啟發式門檻）→佔位 → 還原 code/`\$` → `marked.parse`（math 仍在佔位、100% 不被 markdown 咬）→ 遍歷 math 佔位呼 `katex.renderToString` 回填。`throwOnError:false` 單式失敗降級。單一整合點覆蓋 paper 閱讀視圖（L2806）與 chat 5 處（L3019/3039/3108/3117/3425）。
- **影響**：僅 `static/index.html` + 新增 `static/vendor/` 資產 + 安裝/文件檔。**零後端業務邏輯、零 pipeline、零 RAG、零 schema、零 .env、既有語料免 backfill**；新增測試僅驗 producer 契約（不改 pipeline 行為）。

---

## §2 目標規格

1. **區塊式渲染**：`2601` 式(1)`P_{IT}(t)=P_{base}+α·U(t)`、式(2)`τ·dQ_cool/dt+Q_cool=k₁·P_IT` 二維置中（分數/上下標/希臘字母/式號），**無字面 `$$`**。
2. **行內式渲染**：`byz` `$i$`/`$v_{j}$`/`$j \neq i$`、`2601` `$P_{base}$`/`$k_{1}$` 內嵌、`_`/`{}` **不被 emphasis 咬**、**單字母變數 `$i$`/`$n$`/`$x$` 不退化**。
3. **loose delimiter 相容**：「`$$` 散文行尾冒號後開／行首閉後接散文／content 跨軟換行」與「`$$` 自成一行」兩型皆渲染。
4. **怪空格容忍**：`P _ { \mathrm { b a s e } }` → `P_base`（math-mode 忽略空格、不前置清洗）。
5. **行內 `$` 判定（texmath 啟發式、防貨幣誤渲且不退化單字母）**：
   - 開 `$` **後接「非空白且非數字」**才算數學開（`$100`/`$1.2M` 之 `$1`＝貨幣、不開；`costs $100 to $200` 首 `$` 後接數字即不開 → 跨段貨幣不誤匹配）；
   - 閉 `$` **前為非空白**、且閉 `$` **後非數字**；
   - 空內容/純空白不轉。
   - → `$i$`（後接字母）渲染、`$100`（後接數字）保留。
6. **code 與轉義隔離**：fenced/inline code 內 `$` 不渲染；`\$` 保留為字面（三階段順序佔位保證）。
7. **失敗降級**：單式語法錯誤僅該式原碼/紅字、不影響整頁（`throwOnError:false`）。
8. **雙消費端覆蓋**：paper 閱讀視圖與 chat AI 回答同時生效。
9. **slides 緊排 / 撐欄 / 切邊（KaTeX 顯示式 CSS）**：`#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; padding:4px 0; }`（收斂預設 `1em` margin 避免撞 3c tight list；`overflow-x` 防超長式撐破中欄；`padding` 防橫向 scrollbar 切到下標尾巴）。
10. **離線可用**：KaTeX JS/CSS/字型自託管、runtime 零外部 CDN。
11. **零回歸**：既有 `del` override（L1567）、6 處 `marked.parse` 非數學行為不變；既有語料免重跑、final markdown byte 不變。
12. **安裝可重現**：vendored 資產之版本/來源/SHA/刷新方式有文件（`static/vendor/README.md` + README.md + design/docs）。

---

## §3 現況與證據

- **`static/index.html`**：`L8` marked CDN（9.1.6）；`L1567-1575` 唯一 `marked.use({del})`；`marked.parse` 6 處（paper L2806 + chat L3019/3039/3108/3117/3425）；`L1325` 主題 CSS 本地 link。
- **前端**：無 package.json / build；`static/` 僅 index.html/login.html/themes（無 vendor/）。
- **後端安裝**：install.sh + requirements.txt + .env.example；README.md 記載。
- **文件**：api-integration.md（L59/L219）、dom-reference.md（L233/L264）、principles.md（L51）。

### §3.1 grep 鋼鐵證據

```bash
grep -n "marked\|<script" static/index.html | head
# 8:<script ... marked/9.1.6/marked.min.js></script>
# 1567: marked.use({ del }); / 2806+3019/3039/3108/3117/3425: marked.parse(...)
ls static/  # index.html login.html themes/（無 vendor/）；ls package.json → 無

venv/bin/python - <<'PY'   # PaperRead-Lab 真實 delimiter
import glob; p=glob.glob('output/1/2601_16502v2/final_*_zh.md')[0]
L=open(p,encoding='utf-8').read().splitlines()
for i in range(62,70): print(i+1, repr(L[i]))
PY
# 63 '$$ ' / 64 'P _ { \mathrm { I T } } ... \tag{1}' / 65 ' $$ where $P _ { \mathrm { b a s e } }$ is ...'
# 67 '...modeled by: $$ ' / 68 '\tau \frac { d Q _ { c o o l } } { d t } + ... \tag{2}' / 69 ' $$ where $k _ { 1 }$ ...'
```

---

## §4 跨 Phase 接縫契約

| handoff | producer（誰產 / 形式） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| LaTeX 數學格式 | MinerU/pipeline 產 `final_*_zh.md`/`_en.md`：`$$...$$` loose（散文行尾冒號後開／行首閉後接散文／跨軟換行；亦可自成行）+ 行內 `$...$`（含 `_`/`{}`、token 間空格、含單字母變數 `$i$`） | 前端三階段順序佔位保護抽 `$`/`$$`（texmath 行內門檻）交 `katex.renderToString` | **delimiter＝「loose `$$`/`$`、非 fenced、可跨軟換行/行中、含單字母變數」**；producer 既存輸出凍結為驗證基準（`2601` 式(1)(2)、`byz` 行內+單字母、`2412` `\frac`+可能貨幣 `$`）；consumer 須吃此確切形式、不假設 fenced；**§8.3 後端 pytest 鎖 producer 不截斷/轉義 `$$`、前端 E2E 鎖 consumer 產 `.katex` DOM**。任一方變更須同步本契約與樣本。 |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **整合方式選型**（順序佔位保護 vs marked-katex-extension，互斥） | 🔴 高 | 預設順序佔位保護；spike 用真實 `2601` loose `$$` 驗 extension 能否原生吃，吃得下才考慮。影響 vendoring（§8.4）與 Q5。 |
| **行內 `$` 判定**（貨幣誤渲 ↔ 單字母退化，雙向陷阱） | 🔴 高 | **白名單會退化 `$i$`、純數字黑名單漏跨段貨幣** → 採 texmath 啟發式（開 `$` 後非空白非數字 / 閉 `$` 前非空白且後非數字）；以 `byz` 單字母 + `2412` 貨幣並存案雙向驗證。 |
| **code 內 `$` / `\$` 轉義** | 🟡 中 | 三階段順序佔位（code 先抽、`\$` 先護）徹底隔離；以含 code/含 `\$` 構造案驗。 |
| `$...$` 內 `_`/`*` 被 emphasis 咬 | 🟢 低 | 佔位保護天然根治（marked 只見佔位）。 |
| 與既有 `del` extension 衝突 | 🟢 低 | 佔位保護在 marked 之外、零衝突。 |
| chat 串流半截 `$$` | 🟢 低 | 佔位 regex 不匹配未閉合 → 留原碼、閉合即渲染、無紅字抖動。 |
| KaTeX 顯示式 margin 撞 slides 緊排 / 撐欄 / 切邊 | 🟡 中 | §2-9 防禦 CSS（margin 收斂 + overflow-x + padding）。 |
| 字型/體積、離線/GFW、既有語料相容 | 🟢 低 | 自託管含字型 runtime 零外部依賴；純前端 byte 不變、免 backfill。 |
| 版本相容（KaTeX ↔ marked 9.1.6） | 🟡 中 | 提議版本（§9 Q5）spike 必驗、不憑記憶斷言；佔位路徑 extension 無關、僅 pin KaTeX。 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **後端業務全部**：`web_server.py`/`pipelines/*`/`processor/*`/`rag_*`/`paper_manager.py`/`models.py` 零行為改動（§8.3 僅新增 producer 契約 pytest、不改業務碼）。
- [ ] **既有 final markdown 產物格式**：LaTeX 文字不改/不清洗/不轉寫。
- [ ] **RAG / 向量**：`rag_sections`、向量庫、index_meta 不動。
- [ ] **`static/index.html:1567` 既有 `del` extension** 不移除/改寫。
- [ ] **既有 6 處 `marked.parse`** 非數學渲染行為不變。
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
| 真實 LaTeX delimiter 樣本 | `output/1/2601_16502v2/final_*_zh.md`（§3.1） |
| 行內 `$` texmath 啟發式 | pandoc / markdown-it-texmath 既有慣例（開 `$` 後非數字＝貨幣） |
| KaTeX（外部、自託管） | KaTeX 官方（版本見 §9 Q5、清單見 §8.4） |

---

## §8 驗證計畫

### §8.1 spike（最先、定奪整合路徑與版本）

- worktree 最小 HTML，用真實 `2601`/`byz`/`2412` 片段測：
  - (A) marked-katex-extension（`nonStandard`）能否渲染 loose `$$`/行內 `$`；
  - (B) 三階段順序佔位 + texmath 門檻：渲染 loose `$$`、`$i$` 不退化、`$100`/code/`\$` 不誤渲。
- 產出：選定路徑（預設 B）+ 凍結 KaTeX（與 extension，若 A）確切版本/相容性。

### §8.2 自動化測試

- 前端行為 pytest 無法覆蓋 → 不新增前端 Python 測試；後端套件維持綠：
  ```bash
  venv/bin/python -m pytest tests/ -q   # 與基線一致（零 .py 業務 diff）
  ```
- 靜態 grep：`grep -n "katex\|renderToString\|MATH_PLACEHOLDER" static/index.html`；`grep -n "vendor/katex" static/index.html`；`ls static/vendor/katex/`。

### §8.3 §7.2 跨 Phase 整合驗收（producer pytest + consumer E2E）

- **producer（後端 pytest、僅驗不改）**：對**產出數學論文之路徑（academic 路；確切模組 tasks 階段確認，非 slides——`2601` 為 arXiv 論文）**，取含 `$$` 之 raw、跑該路 P3 產 `final_zh` 後，**斷言輸出 substring 仍含完整 `$$...$$`/`$...$`**（鎖上游不截斷/不轉義）；slides 若帶數學可加同型測。
- **consumer（前端 E2E）**：未清洗真實 `2601` final_zh 載入瀏覽器，斷言式(1)(2) 產 `.katex` DOM、字面 `$$` 消失（真實 loose-`$$` transform 充當 key-changing 整合驗收、非 mock）。Checkout 前必過。

### §8.4 手動 E2E + 套件安裝檔/文件更新（交付物）

**E2E**：
1. `2601` → 式(1)(2) 二維、無字面 `$$`、zh/en 皆渲染。
2. `byz` → `$i$`/`$v_{j}$` 渲染、單字母不退化、`_` 未被吃。
3. `2412`（金融）→ `\frac` 渲染，內文 `$` 金額（如有）不誤渲。
4. chat 含公式 → 串流完成正確、半截不炸/不抖紅字。
5. 語法錯誤式 → 僅該式降級。
6. 斷外部 CDN 重載 → 數學仍渲染（自託管字型）。
7. slides 含公式頁 → `.katex-display` 縫隙自然、超長式不撐欄、scrollbar 不切下標。
8. 含 code/`\$` 文件 → code 內 `$` 與 `\$` 顯示字面、不誤渲。

**套件安裝檔 / 文件**：
- vendored 資產：`static/vendor/katex/katex.min.css`、`katex.min.js`、`fonts/*.woff2`（佔位路徑不含 extension；spike 選 extension 才加 `marked-katex-extension.umd.min.js`）。
- 新增 `static/vendor/README.md`（版本/來源 URL/SHA/刷新；字型完整清單）。
- 新增 `tools/fetch_frontend_vendor.sh`（一鍵下載/校驗、離線可重現）。
- 更新 `README.md`（前端 vendored 依賴段；marked 仍 CDN 註記）。
- 更新 `design/docs/api-integration.md`/`dom-reference.md`（`$$`/`$` KaTeX 渲染〔順序佔位整合〕+ `.katex-display` CSS 規格）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** CDN 還是自託管？ | **自託管** + `tools/fetch_frontend_vendor.sh` | 字型 woff2 離線/GFW 阻斷風險高；跨環境一致；一鍵刷新可重現。 |
| **Q2** loose `$$` 整合 + 行內 `$` 判定？ | **三階段順序佔位保護**（code→`\$`→math〔`$$`先〕→還原→parse→回填）；行內 `$` 採 **texmath 啟發式**（開 `$` 後非空白非數字 / 閉 `$` 前非空白且後非數字 / 空內容不轉）；marked-katex-extension 備選、互斥、spike 定奪 | 佔位徹底掌控 loose `$$` + code/`\$` 隔離 + 順帶解串流抖動；texmath 門檻**一條同解「貨幣（含跨段）不誤渲 + 單字母 `$i$` 不退化」**（白名單退化單字母、純數字黑名單漏跨段貨幣，皆不取）。 |
| **Q3** 加 `MATH_RENDER` 旗標？ | **不加**、always-on | `throwOnError:false` graceful；純前端可隨時 hotfix revert。 |
| **Q4** 一併 vendor marked？ | **本期不動 marked、僅 vendor KaTeX** | marked 6 處消費、一併改擴大回歸面；marked 無字型阻塞、CDN 風險低。 |
| **Q5** 版本 pin？ | **僅 pin KaTeX（提議 0.16.x 最新穩定）**；extension 版本僅 spike 選 A 時相關（提議 5.0.x 對 marked 9.x，**須 spike 實證相容、不斷言**） | 佔位路徑只一個 KaTeX 版本；相容屬可驗事實、spike 鎖定。 |
| **Q6** 「帶數學段落未翻譯」（`2601` 行 65/67/69 英文）納入？ | **不納、另立 backlog**（academic 路 translator 對 `$$` 段處理） | 與渲染正交、屬後端 pipeline；混入擴大 FE 範圍。 |
| **Q7** §7.2 整合測試形式 + 檔案目標？ | **producer 後端 pytest（academic 路、模組 tasks 確認，非 slides）斷言 `final_zh` 含完整 `$$`/`$` + consumer 前端 E2E 斷言 `.katex` DOM** | 接縫拆兩半各自可測；**校正：`2601` 為 arXiv academic 論文、producer 測試對 academic 路非 slide_pipeline**；以真實樣本驗、不豁免。 |
| **Q8** chat 串流半截公式？ | **不特殊處理**（佔位 regex 不匹配未閉合、閉合即渲染） | 避免半截解析反覆跳紅字抖動。 |
| **Q9** KaTeX 顯示式 CSS（slides 緊排/撐欄/切邊）？ | **`#paper-content .katex-display { margin: var(--space-2) 0; overflow-x:auto; overflow-y:hidden; padding:4px 0; }`** | 收斂預設 `1em` margin 避撞 3c tight list；`overflow-x` 防超長式撐欄；`padding` 防橫向 scrollbar 切下標尾巴。 |

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

- v3 (2026-06-12)：第三輪 review 補強——**Q2 行內 `$` 改 texmath 啟發式**（修正 v2 白名單退化單字母 `$i$` 之 regression；亦否決「純數字黑名單」因漏跨段貨幣）+ **三階段順序佔位管線**（code→`\$`→math）正式入規（§1/§8.1）；§2-5 重寫判定規格、§2-9 CSS 補 `padding:4px 0`（防 scrollbar 切下標）；**Q7 校正 producer 測試目標為 academic 路（非 slide_pipeline、`2601` 為 arXiv 論文）**；§5 雙向陷阱風險升 🔴
- v2 (2026-06-12)：第二輪——Q2 佔位保護為主+與 extension 互斥+三守則；Q5 校正；Q7 拆 producer/consumer；新增 Q9 CSS
- v1 (2026-06-12)：初版（marked-katex-extension + 自託管 KaTeX；§4 接縫契約；§8.4 vendoring；八項 OQ）
```
