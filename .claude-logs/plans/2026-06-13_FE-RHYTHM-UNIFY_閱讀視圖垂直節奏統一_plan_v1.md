# FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一 plan

> 將閱讀視圖（`#paper-content`）的垂直間距由「逐交界 bespoke 補丁 + margin-bottom-only 模型」重構為**單一 flow 節奏模型**（一條基準流間距 + 少數「緊貼對」覆寫）；收編 FE-RHYTHM-1、取消擬議 FE-RHYTHM-2、止血「打地鼠」。全文體閱讀視圖共用、純結構層 CSS。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：閱讀視圖垂直間距由**散落的逐交界規則**治理（主題各設 p/h margin、base reset 歸零清單 margin、FE-RHYTHM-1 補 p↔list、擬 FE-RHYTHM-2 補 h↔h…），根因＝**只用 margin-bottom 做節奏 + 清單 margin 被 reset 歸零** → 節奏天生不對稱、**每出現新交界就要補一條（打地鼠）**；且「區段標籤」因 Vision 措辭走 `###`(heading) 或 `<p>`(段落) 兩條節奏路徑（同視覺兩機制）。
- **解法**：以**單一 flow 節奏模型**取代——`#paper-content` 內**塊級元素間距由單一規則供給**（如相鄰兄弟 margin-top 基準流間距）+ **少數「緊貼對」覆寫**（標題→其內文、標籤段落→其清單）；既有逐交界補丁（FE-RHYTHM-1）與主題零散 margin 收編入此模型。**不動內容正規化層**（3c 箭頭/清單項收緊、3d、promote——markdown 層、與 CSS 節奏正交）。
- **影響**：`static/index.html` base CSS（節奏規則集中）+ 可能 `static/themes/*.css`（移除/讓位間距、保留色票/字族/分隔線——見 §9 Q2）；**全文體閱讀視圖共用**（履歷/論文/書籍/litedoc/簡報）；**chat（`.msg-ai`）不受影響**；零後端/pipeline/RAG/final_zh；無 golden 重捕。**supersede FE-RHYTHM-1（移除其 2 條 :has）、取消擬議 FE-RHYTHM-2**。

---

## §2 目標規格

達成下列可檢驗的最終狀態：

1. **單一節奏來源**：閱讀視圖塊級垂直間距由**一條基準流規則 + 一組明列的「緊貼對」覆寫**供給；**不得再有逐交界 bespoke margin 補丁**（FE-RHYTHM-1 之 `p:has`/`ul:has` 收編、不再獨立存在）。
2. **節奏對稱可預測**：任一相鄰塊對之間距由「是否為緊貼對」決定，非由「前者有無 margin-bottom / 後者有無 margin-top」之單向偶然決定。
3. **正確節奏（三檔 + 一條最貼、所有交界）**：
   - 內文→內文（段落↔段落、清單→下個區段 ul/ol→p）：**基準流間距**（`--space-4`）。
   - **非標題→標題**（p/list→h，區段斷點）：**較大留白**（`--space-6`）——保留現況刻意的區段分隔（baron「前面留白不用改」）；**不可降為基準流**（否則縮小現 h2 space-6/h3 space-5、區段分隔變弱＝回歸）。
   - **標題→其後任一塊**（h→p、h→ul、**h→h 子標題**）：**緊貼**（`--space-2`、標題擁抱其內容；h→h 由此涵蓋＝取消 FE-RHYTHM-2）。
   - **標籤段落→其清單**（p→ul/ol）：**最貼**（`--space-1`、收編 FE-RHYTHM-1）。
   - 兩條標題規則靠 `:not(:is(h…)) +` 與 `:is(h…) +` **天然互斥**（非標題→標題＝大留白、標題→標題＝緊貼），不依賴 source order。
4. **收編既案**：FE-RHYTHM-1 兩條 `:has()` 移除、其效果由統一模型涵蓋；擬議 FE-RHYTHM-2（h↔h 收緊）由「標題→其內文」緊貼對自然涵蓋、不另立。
5. **同視覺一致**：「區段標籤 + 清單」不論 Vision 吐 `###`(heading 路) 或 `X：`(段落路)，**最終節奏一致**（皆「標籤緊貼清單、群組間留白」）。
6. **內容正規化層不動**：3c（箭頭硬換行 + 相鄰清單項收緊）、3d（行內粗體/裸 URL）、`_promote_subheadings`、`_normalize_paragraph_breaks` 等 markdown 層轉換**不在本重構範圍**（正交、保留）。
7. **chat 不受影響**：`.msg-ai` 渲染之清單/段落節奏不變（選擇器不涵蓋）。
8. **零回歸 × 三軌 × 四主題**：履歷 / 論文 / 簡報閱讀視圖 × kahn/mies/kandinsky/nara 四主題，節奏皆正確、無破版、無退化。
9. **無 golden 重捕**：純 CSS、final_zh byte 不變、RAG 不動。
10. **相容性**：margin-top 模型**完全消滅 `:has()`**（清單看「上一個」兄弟＝`p + ul` 相鄰、非看「下一個」）→ 僅用 `+`/`:is()`/`:not()`，於 **Safari 14+/Chromium 88+** 可用（比 v1 預估更廣、Dia 穩）；舊版降級為可接受之退化（見 §9 Q6）。

---

## §3 現況與證據

### §3.1 垂直節奏「行為者」盤點（patchwork 現況）

| 交界/元素 | 由誰管 | 值 | 位置 |
|---|---|---|---|
| 段落 p（下邊距、無上邊距） | 四主題各設 `#paper-content p` | margin-bottom `var(--space-4)` | kahn:153 / kandinsky:148 / mies:141 / nara:145 |
| h1 / h2 / h3 | 四主題各設 | h2 `space-6 0 space-3`+border、h3 `space-5 0 space-2`（kahn 例） | kahn:130/139/147（餘主題對應行） |
| ul/ol margin | `index.html:79` 全域 reset 歸零 + 四主題 0 補 | margin `0` | index.html:79 |
| ul/ol padding | HOTFIX-3/3b | padding-left `1.5em` | index.html:904-908 |
| **p→清單** | **FE-RHYTHM-1** | `p:has(+ul/ol){margin-bottom:space-1}` | index.html:915-918 |
| **清單→p** | **FE-RHYTHM-1** | `ul/ol:has(+p){margin-bottom:space-4}` | index.html:919-922 |
| 清單項↔項、箭頭群 | 3c（管線 markdown 層） | 收緊/硬換行 | slide_pipeline.py `_tighten_point_groups` |
| `.slide-head` 標題塊 | base（HOTFIX-3 C） | margin `space-6 0 space-3`+border | index.html:885-893 |
| `.katex-display` | RAG-12 C2 | margin `space-2 0`+overflow+padding | index.html:930 |
| h→h（連續標題） | 未治（擬 FE-RHYTHM-2） | 間距=後者 h margin-top（space-5、過寬） | — |

### §3.2 根因（單一句）

> base 垂直節奏**只靠 margin-bottom**（主題 `#paper-content p` 無 margin-top）+ `index.html:79` reset 歸零清單 margin → 清單與標題後內容呈「**前有間距（吃前者 mb）、後無間距（自身/後者無 mt）**」單向偶然；**每個交界的間距各由不同元素的單向 margin 決定**，故每出現新交界（p↔list / h↔h / list↔h…）就要補一條 bespoke 規則。

### §3.3 grep 鋼鐵證據

```bash
grep -n "#paper-content p:has\|ul:has(+ p)" static/index.html        # FE-RHYTHM-1（915-922）
grep -n "margin" static/themes/kahn.css | grep paper-content          # 主題各設 p/h margin
sed -n '79p' static/index.html                                        # 全域 reset 歸零 ul/ol margin
# slide shadow 實證兩種「區段標籤」路徑：
#   施肥頁：'施肥 (Fertilization)：補充…' 純段落 + '* 收成…'（p→list、走 FE-RHYTHM-1）
#   引擎頁：'### 引擎 1 · 守護' + '### 傳統機上盒'（h→h、未治）
```

---

## §4 跨 Phase 接縫契約

無跨 Phase 資料 handoff（單一前端 CSS 重構）。
> 註：markdown 結構（pipeline 產 `#paper-content` 內 DOM）→ CSS 節奏為唯一「消費」關係；本重構之前提假設＝**塊級元素為 `#paper-content` 之直接子代**（marked 輸出 + `.slide-head` 單元），須於 §8 spike 驗證（見 §9 Q1）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **全文體閱讀視圖全域動間距** | 🔴 高 | 動 `#paper-content` 塊級節奏 → 履歷/論文/書籍/litedoc/簡報全受影響;§8 三軌 × 四主題矩陣 E2E 必驗;spike 先在真實樣本確認模型。 |
| **主題 margin 與統一模型衝突** | 🔴 高 | 四主題現各設 p/h margin（§3.1）;統一模型需「主題讓位間距 / base 覆寫」二選一（§9 Q2）→ 可能動 4 主題檔（非純 base）。 |
| **`> * + *` 直接子代假設** | 🟡 中 | 依賴塊級為 `#paper-content` 直接子代;`.slide-head`(div)、巢狀清單(li 內) 例外須處理;§8 spike 驗 DOM。 |
| **supersede 已 ship FE-RHYTHM-1** | 🟡 中 | 移除其 2 條 :has、效果須由新模型完全涵蓋（施肥頁回歸測試必驗）;移除與新增同 commit、避免中間態。 |
| **`:has()`/`:is()`/`+` 相容** | 🟡 中 | `+`/`:is()` 廣（Safari 14+）、`:has()` Safari 15.4+;若模型仍需 `:has()` 則同 FE-RHYTHM-1 基線;舊版降級（§9 Q6）。 |
| `.slide-head`/`.katex-display`/border 與 flow 疊加 | 🟡 中 | 這些自帶 margin/border 之特殊塊須納入模型或明列例外、避免雙重間距。 |
| chat 誤波及 | 🟢 低 | 選擇器限 `#paper-content`、chat 走 `.msg-ai`;驗證確認。 |
| 既有語料相容 | 🟢 低 | 純 CSS、final_zh 不變、免 backfill、無 golden 重捕。 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **後端 / pipeline / RAG / final_zh 產物** — 零碰（純前端 CSS）。
- [ ] **內容正規化層**：`_promote_subheadings` / `_normalize_paragraph_breaks` / `_tighten_point_groups`(3c) / `_render_inline_bold`+`_strip_bare_url_lines`(3d) — markdown 層、與 CSS 節奏正交、不動。
- [ ] **HOTFIX-3b 清單 padding-left** / **HOTFIX-3 `.slide-head` border** / **RAG-12 `.katex-display` overflow** 之**非間距**屬性 — 保留（本重構只統一**垂直間距**、不碰 border/overflow/padding-left）。
- [ ] **主題之色票 / 字族 / 字級 / 分隔線（border/divider）** — 保留（只動間距、見 §9 Q2）。
- [ ] **chat `.msg-ai`** — 不在選擇器範圍。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流定義（FE-Refactor） | `ref/WORKFLOW_SOP.md §1.1` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 專案進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 結構/外觀分層原則（間距=結構歸 base） | `design/docs/principles.md` |
| patchwork 審計 + 兩種標籤路徑實證 | §3 + slide shadow（施肥頁/引擎頁 repr） |
| 收編對象 | FE-RHYTHM-1（`hotfixes/2026-06-13_FE-RHYTHM-1_hotfix.md`、index.html:915-922） |

---

## §8 驗證計畫

### §8.0 spike（最先、定模型）
- worktree 內最小 HTML，餵真實三軌片段（履歷小標+條列 / 論文段落+清單+連續標題 / 簡報施肥頁 p→list + 引擎頁 h→h），套候選統一模型，肉眼比對節奏（標題貼內文、標籤貼清單、群組間留白、巢狀清單未誤撐）。
- 驗 `> * + *` 直接子代假設（marked 輸出 DOM + `.slide-head`）；驗 `:is()`/`:has()` 於 Dia/Safari。
- 產出：凍結模型（規則集 + token 值 + 主題讓位策略，§9 Q1-Q3 定案）。

### §8.1 自動化測試
- 純 CSS、零 `.py` diff → 不新增 pytest；全套件維持綠（與基線一致、僅既存 env flake）。
- 靜態 grep：確認 FE-RHYTHM-1 兩條 `:has()` 已移除、統一模型規則存在、themes 間距變更（若 Q2 採讓位）符合預期。

### §8.2 手動 E2E（三軌 × 四主題矩陣、baron、非 commit）

| 文體 | 檢查點 |
|---|---|
| **履歷** | 小標→條列貼緊、條列→下個小標留白；巢狀條列未過撐 |
| **論文（2601/byz）** | 段落↔清單交界、**連續標題（h2→h3）貼緊**、清單接章節留白、巢狀清單未誤撐、`$LaTeX$`/`.katex-display` 間距正常 |
| **簡報（Ch37）** | 施肥頁（p→list）+ 引擎頁（h→h）節奏一致正確；`.slide-head` 標題塊間距正常；圖↔內文間距 |
| **四主題** | kahn/mies/kandinsky/nara 各跑一遍上述三軌、節奏一致、無破版 |
| **chat** | AI 回答清單/段落節奏**不受影響**（`.msg-ai` 未波及） |

### §8.3 §7.2 整合
- 無跨 Phase code handoff → 不適用 §7.2 整合測試；以 §8.2 三軌×四主題 E2E 為驗收主軸（CSS 視覺、無法 headless）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 節奏模型：margin-top flow（`> * + *`）vs 保留 margin-bottom 補綴？ | **🟢 定案：margin-top flow**（單向、相鄰兄弟供間距 + 三檔覆寫） | 相鄰兄弟為現代垂直排版 SSOT 最佳實踐;容器首元素無多餘 margin-top（根治清單黑洞）;消滅「前者 mb / 後者 mt 偶然決定」之不對稱根因。須 spike 驗直接子代假設。 |
| **Q2** 主題 margin 如何處置（衝突源）？ | **🟢 定案：方案 A——間距移交 base、主題只留色票/字族/分隔線**（對齊 principles.md）;**tasks 階段將「清理主題 margin」拆為獨立 commit** | 真單一來源、根治;高特異度覆寫（方案 B）殘留冗餘 CSS、增維護成本;獨立 commit 隔離 4 主題檔變更、降 regression。 |
| **Q3** 節奏檔位/緊貼對集合？ | **🟢 定案：三檔 + 一條最貼**（見下「凍結候選模型」） | 較 v1 多一檔「非標題→標題」大留白（保 baron「前面留白不用改」+ 區段分隔、防回歸）;`:not(h)+h` 與 `h+*` 天然互斥;`h+*` 涵蓋 h→h（取消 FE-RHYTHM-2）;`p+ul` 收編 FE-RHYTHM-1。 |
| **Q4** token 值？ | **🟢 定案（spike 微調）**：基準流 `--space-4`(16px)、非標題→標題 `--space-6`、標題→\* `--space-2`(8px)、p→清單 `--space-1`(4px) | 基準流沿用現 p-to-p（零視覺回歸）;標題前 space-6 對齊現 h2 margin-top;緊貼值建立視覺親密性、保留標題層級感。 |
| **Q5** 3c/3d/promote（markdown 層）收編否？ | **🟢 定案：不收編、保持隔離**（SOC：pipeline 管結構語意、CSS 管展示） | 3c 收清單項/箭頭屬 markdown 結構、與 flow margin 不同層;URL 剝除等本就無法在 CSS 實現;混入膨脹樣式表。 |
| **Q6** 選擇器相容與降級？ | **🟢 定案：完全消滅 `:has()`**——僅 `+`/`:is()`/`:not()`（Safari 14+/Chromium 88+） | margin-top 制使清單看「上一個」兄弟＝`p+ul` 相鄰、不需 `:has`;相容性比 v1 預估更廣;舊版降級為「全走基準流、緊貼/區段檔失效」、不破版。 |
| **Q7** supersede FE-RHYTHM-1 / 取消 FE-RHYTHM-2？ | **🟢 定案：是**——同 commit 移除 FE-RHYTHM-1 兩條 :has + 不開 FE-RHYTHM-2 | 避免新舊並存產生雙重邊距災難 / 中間態。 |
| **Q8** `.slide-head` / `.katex-display` 等自帶 margin 特殊塊？ | **🟢 定案：納入模型覆寫**（於其專屬選擇器 reset/明列 margin-top、spike 定）；border/overflow 非間距屬性保留 | 防 flow margin 與其自帶 margin 雙重疊加過寬。 |
| **Q9** 範圍是否含 chat（`.msg-ai`）統一？ | **🟢 定案：不含**（本期只統一 `#paper-content`） | 對話框與閱讀視圖為兩獨立容器、緊湊度不同;隔離防 chat regression、另議。 |

### §9.1 凍結候選模型（Q3/Q4 定案、spike 確認後進 tasks）

```css
/* 單一節奏來源：取代主題 p/h margin + base reset + FE-RHYTHM-1 兩條 :has */
#paper-content > * + *                                     { margin-top: var(--space-4); } /* 基準流 */
#paper-content > :not(:is(h1,h2,h3,h4)) + :is(h1,h2,h3,h4) { margin-top: var(--space-6); } /* 非標題→標題：區段斷點大留白 */
#paper-content > :is(h1,h2,h3,h4) + *                      { margin-top: var(--space-2); } /* 標題→其內文/子標題：貼緊（含 h→h，取消 FE-RHYTHM-2）*/
#paper-content > p + :is(ul,ol)                            { margin-top: var(--space-1); } /* 標籤段落→清單：最貼（收編 FE-RHYTHM-1）*/
/* + 主題移除 p/h margin（Q2）；+ .slide-head/.katex-display 特殊塊 margin-top 明列（Q8）；+ 塊級 margin-bottom 歸零使 margin-top 為單一來源 */
```

> 互斥性證明：任一相鄰對 (A,B)——A 為標題 → 僅中第 3 條（第 2 條要求 A 非標題）；A 非標題、B 標題 → 僅中第 2 條；皆非標題 → 基準流（p→list 另由第 4 條以特異度覆寫）。**無 source-order 依賴**。spike 須驗：① 塊級為 `#paper-content` 直接子代（marked 輸出 + `.slide-head` 單元）② 巢狀清單（`li` 內、非直接子代）不被誤撐 ③ Dia/Safari 渲染。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義閱讀視圖垂直節奏統一之目標規格，作為後續 tasks 拆分與執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 FE-RHYTHM-UNIFY tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義垂直節奏統一規格；內容正規化層（3c/3d/promote）明列不收編；工作目錄/流程規格引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-13)：評估外部 review 回饋後補強——九 OQ 全 🟢 定案;**§2.3 / §9 Q3 新增「非標題→標題」大留白檔**（保 baron「前面留白不用改」+ 區段分隔、防回歸——v1 漏點）;§9.1 新增凍結候選模型（三檔 + 一條最貼、`:not(h)+h` ⊥ `h+*` 互斥證明）;Q4 token 釘值（4/16/8/6）;Q6 確認 margin-top 制**完全消滅 `:has()`**（相容 Safari 14+）;Q2 補「清理主題 margin 拆獨立 commit」
- v1 (2026-06-13)：初版建立（FE-Refactor；patchwork 審計 §3 + 單一 flow 節奏模型 §2 + 三軌×四主題驗證 §8 + 收編 FE-RHYTHM-1/取消 FE-RHYTHM-2 §9 Q7；九項 OQ，核心 Q1 模型/Q2 主題讓位/Q3 緊貼對集合）
