# FE-PERF-2 前端效能紅線四項實修 plan

> 目的：落地 `baton/frontend_browser_standards_audit.md` 落實性複核定案之「FE-Refactor 一包」——#1 串流每 token 全量重排（O(n²)）改 rAF 節流+收尾全量、#3 marked 自託管+defer（消 parser-blocking 與 CDN 白屏）、#4 KaTeX 核心字型 preload（消 FOUT）、#7 scroll listener passive。純前端 `static/index.html` + 新增 `static/vendor/marked/`；SSE 契約與渲染管線邏輯不變；零後端、零 golden 重捕。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：①**串流 O(n²) 全量重排（體感最卡處）**——SSE 每收一個 `sentence` 就對「整段累積字串」重跑 `renderMarkdownWithMath` + `innerHTML=` 整棵重建 + 讀 `scrollHeight` 強制同步 reflow（主串流 `static/index.html:3518-3524`、replay `:3202-3214`）；一則長答案數百次全量 parse+layout+paint。②**head 同步跨源 script**——`marked.min.js` 自 cdnjs 同步載入（`:8`）、KaTeX 同步（`:11`），阻塞 HTML parsing、GFW/離線下白屏（與 KaTeX 自託管理由自相矛盾）。③ KaTeX 字型需 CSSOM 建成才被發現 → 公式頁 FOUT/版跳。④ scroll listener 未 passive（`:1781`/`:1922`）、全檔 rAF=0。
- **解法**：#1 串流渲染改 **dirty-flag + rAF 節流（含最小間隔）+ `chunk.done` 收尾全量一次**，滾動寫入併入同幀；#3 marked **鎖 9.1.6 自託管** `/static/vendor/marked/` + 兩外部 script 加 `defer` + **inline 主 script 整包 `DOMContentLoaded`**（deferred 保證先於 DOMContentLoaded 執行、`marked.use()` 不再頂層裸跑）；#4 head 加 `KaTeX_Main-Regular` + `KaTeX_Math-Italic` 兩支 woff2 `preload`；#7 兩處 scroll listener 加 `{passive:true}`。
- **影響**：僅 `static/index.html` + 新增 `static/vendor/marked/marked.min.js`；**渲染管線內部邏輯（七步佔位）零改、SSE 契約零改、零 `.py`、零 schema、零 golden**（`final_zh` byte 不變）。本案為 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` **首次實碼 dogfood**（治其 §2 紅線 1/2/4/5，紅線 3/6/7 依 audit 裁決不做或另案）。
- **增補（baron review 採納）**：U8 聊天泡泡 `content-visibility: auto`——跳過視窗外歷史訊息的 layout/paint（對話越長效益越大）。**相容底線已更新定案 Safari 18+**（baron 2026-07-09：系統不對外、過度支援無意義），`content-visibility` 為**基線內正式特性、可直接依賴**；落實形式限**記憶尺寸型** `contain-intrinsic-size: auto <fallback>`（防上捲跳動）。

---

## §2 目標規格

- **U1 — 串流渲染節流（消 O(n²) 熱路徑）**：兩條串流路徑（主串流 `:3518-3524`、replay `:3202-3214`）之 `renderMarkdownWithMath` + `innerHTML` 由「每 `sentence` 1 次」改為「**rAF + 最小間隔節流**（穩態 ≤ ~6–7 次/秒）」；串流結束後之最終 DOM 與改前逐 token 版**視覺等價**（同輸入同最終 HTML）。
  **收尾不變式（恰一次、分路提供）**：done 後最終全量渲染**恰發生一次**——不漏尾字、不雙渲染：
  - **主串流**：原碼 `chunk.done` 分支（`:3525`）**不渲染**（靠最後一次 sentence render）→ 節流後由節流器 **`flush()`** 提供最終渲染（外層 `catch` 同）；
  - **replay**：原碼 `chunk.done` 分支**自帶收尾渲染** → 節流器改 **`cancel()`** 讓位、沿用既有收尾原碼，**嚴禁再 flush**（防雙渲染）。
  - 兩路 paintFn **按站點封裝**（replay 含既有 `removeCursor()`/`appendCursor()` 語意）、不得共用主串流版本。
- **U2 — 強制同步 reflow 移出每 token 熱路徑**：串流中不再「每 `sentence` 讀一次 `scrollHeight`」；滾動寫入與渲染**同批**（同一 rAF 內、渲染後執行一次），行為維持既有「總是捲至底部」不變（不新增 near-bottom 判斷、防 scope creep）。
- **U3 — marked 自託管 + 全 head script defer**：
  1. `marked.min.js`（**鎖 9.1.6 同版**）自託管於 `static/vendor/marked/`，head 改引本地路徑；`grep cdnjs static/index.html` → **0 命中**。
  2. `marked` 與 `katex` 兩支 `<script>` 皆加 `defer`。
  3. inline 主 script（`:1599-3833`）主體包進 `document.addEventListener('DOMContentLoaded', …)`——頂層 `marked.use()`（`:1607`）隨之入包；包裹後**零頂層裸依賴** marked/katex。
  4. 前置閘（Run 必查）：`grep -cE "on[a-z]+=" static/index.html` 於 JS 建構之 HTML 字串**期望 0**（body markup L1367-1598 已驗零 inline handler）；若有命中 → 對應函式以 `window.fn = fn` 顯式暴露後才可包裹。
- **U4 — KaTeX 核心字型 preload**：head 加 `KaTeX_Main-Regular.woff2` + `KaTeX_Math-Italic.woff2` 兩條 `<link rel="preload" as="font" type="font/woff2" crossorigin>`（實檔存在：25.7K/16.1K）；**僅此二支**（防無公式頁過度預載）。
- **U5 — scroll passive**：`:1781` 與 `:1922` 兩處 scroll listener 改 `{capture:true, passive:true}`（兩 handler 皆無 `preventDefault`，語意不變）。
- **U6 — 純前端零迴歸**：`git diff --stat` 僅命中 `static/index.html` + `static/vendor/marked/**`；pytest 全套件維持基線（零 `.py` 改動之旁證）；`final_zh`/DB/向量零觸碰 → **無 golden 重捕**。
- **U7 — FE SOP 首次 dogfood**：落地前逐項打勾 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md §4 驗收檢查表`並貼入執行報告 §自評；三軌（論文含公式/履歷/簡報）手動 E2E、**console error = 0**（WORKFLOW_SOP §1.1 FE-Refactor 驗收要求）。
- **U8 — 聊天泡泡 content-visibility（baron review 增補）**：`.msg-ai` 與 `.msg-user` 加 `content-visibility: auto` + **`contain-intrinsic-size: auto <fallback>`（記憶尺寸型、必用 `auto` 關鍵字）**——視窗外歷史訊息跳過 layout/paint、滾動長對話成本下降。**約束**：① 相容：**底線已定 Safari 18+**（見 §7、系統不對外）→ `content-visibility` 為基線內特性、直接依賴、無需 fallback 邏輯；② **嚴禁**固定值 `contain-intrinsic-size`（聊天泡泡高度差異巨大、固定估值→上捲 scrollHeight 重估跳動）；③ E2E 必驗「長歷史上捲無跳動 + 串流錨底不受影響」（§8.2-8）。chat 於 `@media print` 隱藏、export 讀 DOM 非 paint → 列印/匯出零影響。

### §2.5 候選方案（Diverse Rollout）

> 串流渲染策略屬架構級、易踩局部最優，填本節。

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| **方案 A（選定）** | **dirty-flag + rAF 節流（含最小間隔 ~160ms）+ done 收尾全量**：每 `sentence` 只 `accumulated +=` 並標 dirty；渲染由節流器對整段跑既有 `renderMarkdownWithMath` | 改動最小（渲染管線零改、只改呼叫頻率）；保留串流期間即時 markdown 格式化 UX；每秒重排從「每 token」降至 ≤ ~6–7 次、長答案卡頓消失；最終輸出與現行完全等價 |
| 方案 B（否決） | 串流期間只 `textContent` append 純文字，`chunk.done` 才一次 marked+KaTeX | 最省 CPU，但**串流期間 UX 退化**——使用者看到裸 `**`/`$` markdown 符號直到收尾才格式化；體驗倒退不可接受 |
| 方案 C（否決·留未來） | 增量渲染：已定稿段落不重 parse、只重 parse 最後未完成段 | 理論最優（O(n)），但**切段點若落在未閉合 `$…$` / `![](…)` 內即觸發 SOP §3 陷阱**（破式/炸圖）；需段落邊界偵測 + 佔位管線改造，複雜度高、迴歸面大；待方案 A 實測仍不足時再評估 |

- **選定理由**：A 以最小 diff 消滅熱路徑（O(n²)→每秒常數次），不動 `renderMarkdownWithMath` 內部（RAG-12 全系 hotfix 的結晶、SOP §3-1 明令「改任一步先讀註解」），UX 零退化。
- **否決留痕**：B（UX 退化）、C（渲染正確性風險+複雜度）留底防重議。

---

## §3 現況與證據

> 時效性：`static/index.html`（3835 行）自稽核（2026-07-02）以來**零改動**（其間 FE-PERF-1/CHECKOUT-GUARD/CONTEXT-1 皆純 DOC），全部行號於 2026-07-09 重驗有效。

- **head 腳本（`static/index.html:8-11`）**：`:8` marked 9.1.6 自 cdnjs **同步**載入（唯一跨源依賴）；`:10-11` KaTeX 自託管但**同步**。皆無 `defer`。
- **頂層 `marked.use()`（`:1607`）**：inline 主 script（`:1599-3833`、單一 `<script>` 塊）開頭即頂層呼叫 `marked.use({...})`（關閉 GFM strikethrough、RAG-9）→ **直接加 defer 必 ReferenceError**，須連帶 DOMContentLoaded 化。
- **主串流迴圈（`:3518-3524`）**：每 `chunk.sentence` → `accumulated +=` → `renderMarkdownWithMath(整段)` → `aiMsg.innerHTML=` → `messages.scrollTop = messages.scrollHeight`（讀 scrollHeight = 強制同步 reflow）。
- **replay 路徑（`:3202-3214`）**：sentence 分支同全量重排模式，但兩點與主串流**不同**（階段 2 拆分探勘確認）：①渲染由 `removeCursor()`→`innerHTML`→`appendCursor()` 包裹（cursor 管理）；②**`chunk.done` 分支自帶收尾渲染**（主串流 done 則不渲染）——U1 收尾不變式據此分路。**歷史載入（`:3116`）為單次渲染非熱路徑**（每則訊息一次、非每 token），依 audit 裁決不納（見 §9 Q4）。
- **`renderMarkdownWithMath`（`:1623-1671`）**：七步佔位管線（code→img→`\$`→math→還原→marked.parse→KaTeX 回填）——**本案零改其內部**。
- **scroll listener（`:1781` / `:1922`）**：capture、未 passive；handler 皆無 `preventDefault`。全檔 `requestAnimationFrame` = 0、`passive` = 0。
- **KaTeX 字型實檔**：`static/vendor/katex/fonts/KaTeX_Main-Regular.woff2`（25.7K）/ `KaTeX_Math-Italic.woff2`（16.1K）存在。
- **body markup（`:1367-1598`）**：全數 `id` + `addEventListener` 綁定、**零 `onclick=` 等 inline handler**（2026-07-09 全段人工掃描）→ DOMContentLoaded 包裹不破壞全域依賴（JS 建構字串部分留 U3-4 前置閘複驗）。
- **login.html**：不用 marked/katex、不在本案範圍。

### §3.1 grep 鋼鐵證據

```bash
$ grep -nE "cdnjs|katex.min.js\"" static/index.html
8:<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
11:<script src="/static/vendor/katex/katex.min.js"></script>
$ grep -n "marked.use({" static/index.html
1607:  marked.use({                     # 頂層、defer 前必 DOMContentLoaded 化
$ sed -n '3518,3524p' static/index.html   # 主串流每 token 全量重排 + scrollHeight
3519: accumulated += chunk.sentence; … 3522: aiMsg.innerHTML = renderMarkdownWithMath(formatted);
3523: messages.scrollTop = messages.scrollHeight;
$ grep -nE "addEventListener\('scroll'" static/index.html
1781: window.addEventListener('scroll', (e) => {   1922: window.addEventListener('scroll', hideNow, true);
$ grep -cE "requestAnimationFrame|passive" static/index.html
0
$ ls static/vendor/katex/fonts/ | grep -E "Main-Regular|Math-Italic"
KaTeX_Main-Regular.woff2  25.7K / KaTeX_Math-Italic.woff2  16.1K
# body markup（1367-1598）人工全段掃描：零 on[a-z]+= inline handler（2026-07-09）
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 本案為前端**消費端內部優化**：SSE 契約（`chunk.sentence` / `chunk.done` / `grounding_sources`、後端 chat endpoint）**零改動**——producer（web_server SSE）與 consumer（前端迴圈）之 key/格式不變，僅 consumer 內部的渲染頻率與資源載入方式改變。無跨 Phase / 模組 handoff 變更。§7.2 整合測試豁免申請見 §9 Q6。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| DOMContentLoaded 包裹改變全域暴露（JS 建構 HTML 字串若含 `on*=` 引用頂層函式） | 🟡 中 | U3-4 前置閘：Run 期 `grep -cE "on[a-z]+="` 期望 0（body 已驗 0）；若命中 → `window.fn = fn` 顯式暴露該函式後才包裹；包裹後全站互動 E2E |
| defer 時序：任何「包外」同步依賴 marked/katex 的殘留 | 🟡 中 | 全 inline script 單塊整包（無第二個 script 塊）；包內程式於 DOMContentLoaded 觸發時 deferred script 已執行完（HTML 規範保證順序）；E2E 首屏含公式頁驗證 |
| rAF 節流改變串流視覺節奏（每 token → ~6-7 次/秒批次） | 🟢 低 | 人眼難辨 <160ms 批次；`chunk.done` 收尾全量保證最終完整；體感反而更順（不再卡頓） |
| 節流器漏渲染（最後一批 dirty 未 flush） | 🟡 中 | `chunk.done` / stream 結束 / catch 路徑**皆強制 final render**（三出口收斂）；E2E 驗最終文字完整 |
| marked 自託管檔案完整性/版本漂移 | 🟢 低 | 鎖 9.1.6（與現行 CDN 同版、行為零變）；下載自 cdnjs 原 URL、Run 期 byte 大小 + 三軌渲染 smoke |
| preload 對無公式文獻多下載 ~42KB | 🟢 低 | 僅預載 2 支核心字型；一次性成本、後續配 BE 強快取（另案 #2）攤平 |
| scroll passive 後 handler 內含 preventDefault 失效 | 🟢 低 | 已驗兩 handler（closePopups/hideNow）皆無 preventDefault、語意不變 |
| 渲染管線誤動（RAG-12 系結晶） | 🟢 低 | §6 不可動明列 `renderMarkdownWithMath` 內部零改；本案只改呼叫頻率與載入時序 |
| U8 上捲跳動（視窗外泡泡以估值參與 scrollHeight、進視窗換真實尺寸） | 🟡 中 | 強制記憶尺寸型 `contain-intrinsic-size: auto <fallback>`（首渲染後記真實尺寸、跳動僅首次上捲極輕微）+ E2E 長歷史上捲驗證；不可接受則單獨 revert U8（獨立 CSS 兩行、零耦合） |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **`renderMarkdownWithMath`（`:1623-1671`）內部七步佔位管線**——RAG-12 全系 hotfix 結晶、SOP §3-1 保護對象；只允許改「呼叫它的頻率」、嚴禁動其解析邏輯/正則/佔位順序。
- [ ] **SSE 契約與後端**：`web_server.py` chat endpoint、`chunk.sentence`/`chunk.done`/`grounding_sources` 格式——零改（本案純 consumer 內部）。
- [ ] **全部 `.py` / `tests/` / DB / 向量 / golden baseline**——零觸碰（`final_zh` byte 不變、無 golden 重捕）。
- [ ] **`themes/*.css` / `design/docs/*`**——不動。
- [ ] **KaTeX vendor 本體**（`static/vendor/katex/**`）——只在 head 加 preload 標籤、不動其檔案。
- [ ] **marked 版本**——鎖 9.1.6（自託管同版、不升版；升版屬另案）。
- [ ] **側欄 `transition: width` / `.collapsed` rail 行為**——audit #6 裁決不做（translateX 會破壞 icon-rail UI）。
- [ ] **audit 緩議/不做項不得夾帶**：#5 popup/tooltip rAF 定位、§1-3 hover prefetch、#8 KaTeX code-split、`:3116` 歷史載入路徑改造。
- [ ] **`login.html`**——不在範圍。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| FE-Refactor 工作流 + 驗收要求（E2E、console error 0） | `ref/WORKFLOW_SOP.md §1.1` |
| **FE 必讀 SOP（本案首次實碼 dogfood）** | `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（§2 紅線 1/2/4/5 = 本案 U1/U3/U5/U4；§3 渲染陷阱 = §2.5 方案 C 否決依據；§4 檢查表 = U7） |
| 稽核來源 + 落實性裁決（打包定案） | `baton/frontend_browser_standards_audit.md`（Priority Matrix + 建議打包） |
| 雙軌制 / 不可動 / 驗證 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §8` |
| 收官 git-add 白名單鐵律 + checkout 報告鐵律 | `ref/WORKFLOW_SOP.md §3`（CHECKOUT-GUARD） |
| 前端相容底線 | **Safari 18+**（baron 2026-07-09 更新定案：系統不對外、過度支援無意義；**取代**原 15.4 定案——`@layer`/`:has()`/`content-visibility`/`contain-intrinsic-size: auto` 皆在基線內；本案 rAF/passive/preload/defer/U8 全數無相容疑慮） |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**（證零 `.py` 迴歸）：
  ```bash
  pytest tests/ -q   # 期望：維持基線 passed（唯一既有 LOG_FORMAT env flake 除外）
  ```
- **預計新增測試**：無 pytest（前端 JS 不在 pytest 覆蓋面）。**靜態核查**替代：
  ```bash
  grep -c "cdnjs" static/index.html                      # 期望 0（U3）
  grep -cE '<script src="/static/vendor/(marked|katex)[^>]*defer' static/index.html   # 期望 2（U3）
  grep -c 'rel="preload" .*woff2' static/index.html      # 期望 2（U4）
  grep -cE "passive: *true" static/index.html            # 期望 ≥2（U5）
  grep -c "requestAnimationFrame" static/index.html      # 期望 ≥1（U1）
  grep -c "content-visibility" static/index.html         # 期望 ≥1（U8）
  grep -cE "contain-intrinsic-size: *auto" static/index.html   # 期望 ≥1（U8·記憶尺寸型、禁固定值）
  git diff --stat                                        # 期望：僅 index.html + vendor/marked/**（U6）
  ```

### §8.2 手動端到端（E2E）驗證流程

1. **三軌渲染**：開論文（含公式）/ 履歷 / 簡報各一——版面與改前一致、KaTeX 公式正常、**console error = 0**。
2. **長答案串流**（U1/U2 核心）：發問產生長回覆——串流期間輸入框可打字不凍結、內容仍即時格式化、結束後全文完整；DevTools Performance 錄製對比：改前每 token 一個 long task → 改後渲染批次 ≤ ~6-7 次/秒。
3. **defer 正確性**（U3）：硬重整（Cmd+Shift+R）首屏正常、無 `marked is not defined`；DevTools Network block `cdnjs.cloudflare.com` → 頁面**完全不受影響**（自託管生效）。
4. **字型 preload**（U4）：Network 面板驗 2 支 woff2 於 HTML parse 早期即發起（priority 高）；公式頁無字型閃爍。
5. **scroll 行為**（U5）：捲動論文/清單時 popup/tooltip 正常關閉、無 console 警告。
6. **SOP dogfood**（U7）：逐項打勾 `sop §4 檢查表`、結果貼入執行報告 §自評。
7. **replay 路徑**：重整頁面觸發 chat 歷史 replay——渲染正常、無重複/缺漏。
8. **U8 content-visibility**：載入含長歷史（≥30 則）的對話——①上捲逐則閱讀**無捲動跳動**；②串流進行中錨底行為不受影響；③DevTools Performance 對比長對話滾動之 layout/paint 成本下降。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 節流實作參數？ | **rAF + 最小間隔 ~160ms（dirty-flag；到點才於下一 rAF 渲染）** | 純 rAF（60fps）仍可能每秒 60 次全量 parse（長文昂貴）；160ms ≈ 每秒 6 次、人眼無感且 CPU 削 10x。**收尾分路**（U1 不變式）：主串流 done/catch → `flush()`（原碼 done 不渲染）；replay done → `cancel()` + 沿用既有收尾原碼（原碼自帶渲染、再 flush 即雙渲染）。 |
| **Q2** 滾動寫入方式？ | **與渲染同批：同 rAF 內 render 後執行既有 `scrollTop = scrollHeight` 一次** | 行為與現行完全等價（總是捲底）、每幀至多一次 forced reflow（可接受）；`scrollIntoView` 雖免 JS 讀幾何但行為差異面大（smooth/巢狀捲動容器），保守選等價方案。 |
| **Q3** marked 自託管取得方式？ | **自 cdnjs 原 URL 下載 9.1.6 原檔入 `static/vendor/marked/`（比照 KaTeX vendored 慣例）** | 鎖同版=行為零變；不走 npm/不升版（升版屬另案、須重驗 RAG-9/RAG-12 佔位相容）。 |
| **Q4** 歷史載入（`:3116`）與 attach 一次性渲染是否納入節流？ | **不納入**（維持單次渲染） | 非熱路徑（每則訊息一次、非每 token）；納入反增改動面；audit 裁決已列非熱路徑。 |
| **Q5** scroll handler 是否加「無 popup 早退」旗標？ | **不加、僅 passive** | 旗標引入狀態同步風險（popup 開合多入口）；passive 已解主執行緒阻塞問題；`closePopups` 本身廉價。 |
| **Q6** §7.2 跨 Phase 整合測試豁免？ | **顯式豁免** | 前端 consumer 內部優化、SSE 契約零改、無跨 Phase handoff 變更；驗證以 §8.2 三軌 E2E + replay 承擔。 |
| **Q7** inline script 包裹粒度？ | **整塊單包**（`:1599-3833` 全部進一個 `DOMContentLoaded` listener） | 單一 script 塊、內部相互引用密集，拆多包反增時序面；前置閘（U3-4）保證無外部全域依賴後整包最安全。 |
| **Q8** content-visibility 增補（baron review）？ | **採納為 U8、記憶尺寸型** | 原理正確且與 U1/U2 無衝突；相容疑慮經 baron 上調底線至 Safari 18+ 而消除（基線內特性、直接依賴）；唯一保留約束＝必用 `contain-intrinsic-size: auto <fallback>` 防上捲跳動；獨立兩行 CSS、不合格可單獨 revert。 |

### §9.1 定案紀錄（baron 2026-07-09 review 全數 🟢 核准）

| OQ | 定案 | 備註 |
|---|---|---|
| Q1 | 🟢 rAF + 最小間隔 ~160ms + done 收尾 final render | CPU 削 10x、視覺無感 |
| Q2 | 🟢 滾動與渲染同批（同 rAF 內 render 後 scrollTop 一次） | 行為等價、每幀至多一次 reflow |
| Q3 | 🟢 下載 cdnjs 同版 9.1.6 原檔自託管 | 鎖版＝RAG-9/RAG-12 佔位規則零風險 |
| Q4 | 🟢 歷史載入不納入節流 | 單次非熱路徑、避免過度重構 |
| Q5 | 🟢 不加旗標、僅 passive | 防狀態同步冗餘 bug |
| Q6 | 🟢 §7.2 顯式豁免 | 純 consumer 效能重構、無 code handoff |
| Q7 | 🟢 整塊單包 DOMContentLoaded | 避免全域引用斷裂、最安全 |
| **Q8（增補）** | 🟢 **採納 content-visibility（U8）**——記憶尺寸型 `contain-intrinsic-size: auto`；**相容底線由 baron 上調至 Safari 18+ 後為基線內特性**（系統不對外、過度支援無意義） | 「漸進增強」定位隨底線上調撤銷；固定 intrinsic-size 禁令保留 |

**八 OQ 全結清、相容底線定案 Safari 18+、plan 規格凍結，可進階段 2（tasks 拆分 + 同步 TODO 🟡 WIP）。**

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-PERF-2「前端效能紅線四項實修」目標規格，作為 tasks 拆分與原子執行唯一基準 |
| **用途** | 供 baron 審查 §9 並於 tasks.md 拆分時引用；階段 3/5 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 FE-PERF-2 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡/演進歷史/拍板過程；嚴禁含 commit 拆分（屬 tasks 階段、baron 明示不給）；嚴禁夾帶 audit 緩議/不做項 |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務完成、baron 同意歸檔 archive/ |
| **重複防護** | 效能紅線規範唯一源在 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（本 plan 為其實修、不重寫規範）；稽核發現唯一源在 `baton/frontend_browser_standards_audit.md`；渲染管線保護條款以 SOP §3 為準 |

### §99.2 Revision 歷程

- v4 (2026-07-09)：階段 2 拆分探勘回饋銳化（§1.9 累積補強、方向零變）——U1 補**收尾不變式（恰一次、分路提供）**：主串流 done 原碼不渲染→`flush()`；replay done 原碼自帶收尾渲染→`cancel()` 沿用原碼、嚴禁再 flush（防雙渲染）；paintFn 按站點封裝（replay 含 cursor 語意）。§3 replay 現況補 cursor/done 差異證據；§9 Q1 備註同步分路（原「done/錯誤路徑強制 flush」字面對 replay 會誘導雙渲染或致階段 5 誤判 deviation）。tasks §8 C3 已為正確語意、零改。
- v3 (2026-07-09)：baron 拍板**相容底線上調 Safari 15.4 → 18+**（系統不對外、過度支援無意義）——U8 由「漸進增強」升格為**基線內正式特性**（撤銷 15.4–17 相關 hedging：§1/§2 U8-①/§5 刪 15.4–17 風險列/§7 底線列改 18+ 並註取代 15.4/§8.2-8 刪優雅忽略驗證/§9 Q8 與 §9.1 同步）；記憶尺寸型 `contain-intrinsic-size: auto` 禁令與上捲 E2E 保留（與底線無關、防跳動）。
- v2 (2026-07-09)：baron review——①Q1–Q7 全數 🟢 核准入 §9.1；②增補 **U8 聊天泡泡 content-visibility**（Q8 採納）：經複核修正原建議兩點——相容定位改「漸進增強（`content-visibility` 需 Safari 18+、15.4–17 優雅忽略非『直接安全』）」、落實形式強制記憶尺寸型 `contain-intrinsic-size: auto <fallback>`（禁固定值、防上捲 scrollHeight 跳動）；連動 §1/§2 U8/§5 兩風險/§8.1 grep/§8.2-8 E2E；規格凍結、可進階段 2。
- v1 (2026-07-09)：初版——依 `frontend_browser_standards_audit.md` 落實性複核定案之 FE 包（#1 串流 rAF 節流+收尾全量〔§2.5 三候選、A 選定〕/ #3 marked 鎖 9.1.6 自託管+defer+inline script DOMContentLoaded 整包〔body 零 inline handler 已驗+Run 前置閘〕/ #4 KaTeX 兩核心字型 preload / #7 scroll passive）；U1–U7；SSE 契約零改、渲染管線內部零改、零 golden；FE 必讀 SOP 首次實碼 dogfood；§9 七 OQ 待 baron 拍板。
