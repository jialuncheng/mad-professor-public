# 前端效能與渲染 SOP 手冊

> [!NOTE]
> 本文件為 Mad Professor **前端效能與渲染** 的權威 SOP。
> 依 Osmani《How modern browsers work》瀏覽器渲染管線原理 + 本專案歷次前端 hotfix 教訓凝練。
> **職責邊界**：效能紅線 + 渲染正確性歸本檔；**視覺 / 元件 / token / 互動歸 `design/docs/`**（引用不重寫）；**跨 Phase 接縫歸 `WORKFLOW_SOP §7`**（見 §99.1 重複防護）。
> 反例錨點行號對應改版當下之 `static/index.html`；重構後行號可能位移，以「規則」為準、行號僅供定位。

---

## §0 改版規則

- 改版觸發：§1–§5 任一規則變動、或新增前端渲染/效能紅線、或新增 hotfix 教訓
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 觸發與適用

- **強制讀取時機**：`FE-Refactor`（前端重構）/ `FE-Hotfix`（前端緊急修補）**落地前必讀**——由 `WORKFLOW_SOP §1.1 / §1.4`「必讀 SOP」欄掛勾。
- **適用範圍**：`static/index.html` 及任何前端渲染/互動/資源載入邏輯。
- **使用方式**：改動前對照 §2 效能紅線 + §3 渲染陷阱；落地後跑 §4 驗收檢查表、結果併入執行報告 `§自評`（`template_execution.md`）。
- **非目標**：瀏覽器內核原理教科書（V8 GC / site isolation / 多進程 / HTTP3 等不可行動內容不在本檔）。

---

## §2 效能紅線（Hard Rules）

> 格式：**規則** ｜ 反例錨點 ｜ 改法。違反須於 plan/執行報告顯式說明理由。

1. **串流回覆收尾才重排版、禁每 token 全量 re-parse**
   - 反例：SSE 迴圈每個 `sentence` 呼叫 `renderMarkdownWithMath(整段 accumulated)` + `innerHTML=` + 讀 `scrollHeight`（`static/index.html:3519-3523`；函式 `L1623-1671`；歷史載入 `L3116/L3136/L3205`）→ 對整段重解析 O(n²) + 每 token 整棵子樹 style/layout/paint + 強制同步 reflow。
   - 改法：串流只 append 純文字（`textContent`/增量節點）；`marked.parse` + KaTeX 只在 `chunk.done` 或每 ~150–200ms `requestAnimationFrame` 節流跑一次；滾動用 `scrollIntoView({block:'end'})` 或把 `scrollTop` 寫入包進 rAF、勿緊接讀 `scrollHeight`。

2. **head `<script>` 一律 `defer`、第三方套件自託管、禁裸 CDN 阻塞**
   - 反例：`static/index.html:8` `marked.min.js` 自 cdnjs 同步載入於 `<head>`、無 `defer`；`L10-11` KaTeX 同步。head 同步 script 阻塞 HTML parsing；CDN 在離線/GFW 可致白屏。
   - 改法：`marked` 比照 KaTeX 自託管 `/static/vendor/`；兩 script 加 `defer`，行內初始化包進 `DOMContentLoaded`（防 `defer` 後 `ReferenceError`）。短期保留 CDN 至少補 `<link rel="preconnect">`。

3. **幾何動畫改 `transform`/`opacity`、禁 `transition: width/height/margin/top/left`**
   - 反例：`static/index.html:380 / 522 / 967` `transition: width …`（側欄收合 `classList.toggle('collapsed')`）→ 每幀 relayout+repaint。
   - 改法：改 `transform: translateX()` + `opacity`（合成執行緒、GPU、主執行緒忙仍 60fps）；必要時 `will-change: transform` 提升圖層（勿濫用致圖層爆炸）。

4. **DOM 寫入對齊 `requestAnimationFrame`、scroll/touch listener 標 `passive`**
   - 反例：全檔 `requestAnimationFrame`=0、`passive`=0；scroll listener `static/index.html:1781/1922`（capture、未節流、每次 scroll 跑 `closePopups()`）。
   - 改法：scroll/touch 加 `{passive:true}` 並先廉價早退再動 DOM；批次 DOM 寫入放 rAF 對齊幀邊界。

5. **自託管字型 `preload`、消除 FOUT/版跳**
   - 反例：KaTeX `woff2` 需先下載/解析 `katex.min.css` 建 CSSOM 才被發現（`static/index.html:10-11`）→ 公式字型延遲、版面跳動。
   - 改法：`<head>` 對核心字型加 `<link rel="preload" as="font" type="font/woff2" crossorigin>`，讓 preload scanner 提前抓。

6. **後端靜態資源 Gzip + 強快取**
   - 反例：FastAPI `web_server.py` 未掛 `GZipMiddleware`；`/static` `vendor/*`（含永不變 `woff2`）無 `Cache-Control`（見 `baton/frontend_browser_standards_audit.md §5`）。
   - 改法：`app.add_middleware(GZipMiddleware, minimum_size=1000)`；`vendor/` 靜態回 `Cache-Control: public, max-age=31536000, immutable`。（屬後端 BE 改動、非本 SOP 前端範疇之強制項，列此供 FE/BE 協同。）

7. **重量套件按需 `import()` code-split**
   - 反例：KaTeX（含 20 個 woff2）不論文獻有無公式一律 eager 載入（`static/index.html:11`）；履歷/簡報多數無公式。
   - 改法：偵測內容含 `$` 才動態 `import()` KaTeX（優先度低、自託管本地載入本快）。

---

## §3 渲染正確性陷阱清單（附 hotfix 溯源）

> 專案已踩過的坑，改前端 Markdown/渲染前逐條核對，勿讓 path #2 重蹈 path #1。

1. **marked / KaTeX 佔位順序**（RAG-12 / RAG-12-HOTFIX-1）：抽取順序須 code → 圖片 → `\$` 跳脫 → block/inline math → 還原 → `marked.parse` → KaTeX 回填；math 佔位用 Unicode PUA 哨兵（`/`）避免 marked 雙底線咬粗體。**改任一步先讀 `renderMarkdownWithMath` 註解。**
2. **`<img alt>` 內特殊字 / KaTeX HTML 注入**（RAG-12-HOTFIX-1）：`![alt](url)` 之 `alt` 內含 `$…$` 或 `][()` 會使 KaTeX 產出的 `<span>`（含 `"`/`<>`）回填進 `alt="…"` → 引號提前閉合、`<img>` 炸穿、後續全毀。**圖片整段須在 math 管線前佔位保護；`alt` 內 `$` 留字面。**
3. **CJK `**` 粗體失效**（PIPE-SLIDES-HOTFIX-3d）：CommonMark emphasis 對「閉合 `**` 前接全形標點、後接中文」判為字面星號。**中文粗體需 raw HTML `<strong>` 繞過，勿依賴 `**`。**
4. **soft-break 段落黏連**（RAG-8 / PARA-HOTFIX-1 / RAG-10）：CommonMark 單 `\n`＝soft break（渲染成空格），須 `\n\n` 或行尾雙空格才斷行/分段；pipe table row 的 `\n` 須保留不升級。**產 Markdown 時段落間補空行、meta 欄位行尾補雙空格。**
5. **`~` 誤判刪除線**（RAG-9）：marked GFM 把單 `~` 配對成 `<del>`（如 `100~500 人`/`2003/8~`）。**關閉 GFM strikethrough 或轉義 `~`。**
6. **`:has()` 消滅 + margin-top flow 模型**（FE-RHYTHM-UNIFY）：閱讀視圖垂直節奏採單一 `margin-top` flow（基準流/區段斷點/標題貼內文/標籤貼清單），**完全不用 `:has()`**（相容 Safari 14+）；主題只管色票/字族、垂直 margin 歸 base。**加節奏規則勿引入 `:has()`、勿在主題檔重加垂直 margin。**

---

## §4 落地前驗收檢查表（對接 `template_execution.md §自評`）

FE 改動 ship 前逐項打勾，結果貼入執行報告 `§自評`：

- [ ] **§2-1 串流**：未新增「每 token 全量 re-parse / innerHTML 整段替換」；重排版於收尾或 rAF 節流。
- [ ] **§2-2 script**：新增 `<script>` 皆 `defer`/自託管；未引入裸 CDN 阻塞。
- [ ] **§2-3 動畫**：新增過渡用 `transform`/`opacity`；未 animate `width/height/margin/top/left`。
- [ ] **§2-4 監聽**：新增 scroll/touch listener 標 `passive` 且早退；批次 DOM 寫入對齊 rAF。
- [ ] **§2-5/7 資源**：新增自託管字型有 `preload`；重量套件評估 code-split。
- [ ] **§3 渲染正確性**：涉 Markdown/公式/圖片渲染者，已核對 §3 六類陷阱（佔位順序 / alt 注入 / CJK 粗體 / soft-break / `~` / `:has`）。
- [ ] **視覺一致性**：對照 `design/docs/`（components / typography / spacing / color-tokens），未破壞設計系統。
- [ ] **驗收**：純前端無 golden 重捕者，附三軌×主題 E2E 或 node spike 佐證；`final_zh` byte 不變則註明免重捕。

---

## §5 交叉引用

| 主題 | 唯一權威源 | 本檔關係 |
|---|---|---|
| 視覺 / 元件 / token / 互動 / 排版 | `design/docs/*`（components / typography / spacing / color-tokens / interaction / dom-reference / theme-guide …） | 本檔引用、不重寫 |
| 跨 Phase 接縫契約 / 收官前整合測試 | `ref/WORKFLOW_SOP.md §7` | 本檔引用、不重寫 |
| 五類工作流 / 命名 / 六階段 | `ref/WORKFLOW_SOP.md` | 本檔被 §1.1/§1.4 掛勾 |
| Osmani 稽核原始 findings | `baton/frontend_browser_standards_audit.md`（收官後歸 executions/archive） | 本檔為其可行動凝練 |

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義前端效能紅線與渲染正確性避坑準則，作為 FE-Refactor/FE-Hotfix 落地前強制對照基準 |
| **用途** | 由 `WORKFLOW_SOP §1.1/§1.4`「必讀 SOP」掛勾、workflow-gated 讀取；不入 CLAUDE.md @path auto-load |
| **權威源** | 本檔 §1–§5 |
| **引用方** | FE-Refactor / FE-Hotfix plan 與執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 僅寫效能 + 渲染正確性；嚴禁轉錄瀏覽器內核教科書；嚴禁重寫 design/docs 視覺內容 |
| **改版觸發條件** | §1–§5 規則變動 / 新增紅線 / 新增 hotfix 教訓 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 不刪（前端工作流長期必讀） |
| **重複防護** | 視覺/元件/token/互動唯一源在 `design/docs/`；跨 Phase 接縫唯一源在 `WORKFLOW_SOP §7`；工作流定義唯一源在 `WORKFLOW_SOP`；本檔僅定義效能 + 渲染正確性 |

### §99.2 Revision 歷程

- v1 (2026-07-02)：FE-PERF-1 C1 初版——以 Osmani《How modern browsers work》稽核（`baton/frontend_browser_standards_audit.md`）為基礎，凝練 §2 效能 7 條紅線（附 `static/index.html` 反例行號）+ §3 渲染正確性陷阱 6 類（附 hotfix 溯源 RAG-12/RAG-12-HOTFIX-1/PIPE-SLIDES-HOTFIX-3d/RAG-8/PARA-HOTFIX-1/RAG-9/RAG-10/FE-RHYTHM-UNIFY）+ §4 驗收檢查表（對接 template_execution §自評）+ §5 交叉引用 + §99.1 重複防護邊界。
