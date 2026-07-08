# FE-PERF-2 前端效能紅線四項實修 — Tasks

> 本文件為 FE-PERF-2 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_plan_v1.md`（內部 v3、八 OQ 全定案、相容底線 Safari 18+）產出，含 5 個 Commit（C1 → C2 → C3 → C4 → checkout）。
> 工作流：**FE-Refactor**（必讀 SOP：`sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`、本案首次實碼 dogfood）。
> 修改邊界：**僅 `static/index.html` + 新增 `static/vendor/marked/**`**；零後端、零 golden。
> 工作目錄註：提示詞模板之 worktree 路徑為殘留；依 `CLAUDE.md §3`（v5、CONTEXT-1 C2）**主 repo 雙視圖為唯一合法工作目錄**、以此為準。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `static/vendor/marked/marked.min.js`（9.1.6 鎖版自託管、C1 入 git） |
| **修改檔案** | 1 個 | `static/index.html`（C1 換源 / C2 defer+包裹 / C3 串流節流 / C4 preload+passive+content-visibility，累計四次） |
| **目錄初始化** | 1 個 | `static/vendor/marked/`（vendored 第三方庫、比照 katex） |
| **備份（.bak 鐵律）** | 4 份 | `archive/2026-07-09_FE-PERF-2_C{1..4}_index.html.bak`（各自 commit `git add`） |
| **狀態更新** | 2 個 | `TODO.md`（本階段 🟡 WIP、checkout 雙層結案）/ `prompts/INDEX.md`（隨歸檔同步） |
| **Commits** | 5 個 | C1 → C2 → C3 → C4 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` plan_v1 → `plans/` + tasks → `tasks/` + C1–C4 執行報告 → `executions/` + 逐檔 `git add`；checkout 執行報告依鐵律**直產** `executions/` |

---

## §1 TL;DR（概要）

- **挑戰**：串流每 token 全量重排 O(n²)（`static/index.html:3518-3524` 主串流、`:3202-3214` replay）+ head 同步跨源 marked（`:8`、parser-blocking+GFW 白屏風險）+ KaTeX 字型 CSSOM 後發現（FOUT）+ scroll listener 未 passive（`:1781`/`:1922`）+ 長對話視窗外泡泡全量 layout/paint。
- **解法**（5 原子 commits）：
  - **C1 — Marked Vendoring（marked 自託管換源）**：9.1.6 原檔入 `static/vendor/marked/`、head 換本地 src（**不加 defer**、行為零變）——先殺 CDN 依賴。
  - **C2 — Deferred Boot（defer 與初始化包裹）**：兩外部 script 加 `defer` + inline 主 script（`:1599-3833`）整包 `DOMContentLoaded`（前置閘：`on[a-z]+=` 期望 0）——消 parser-blocking。
  - **C3 — Stream Throttle（串流節流與滾動同批）**：rAF+160ms dirty-flag 節流 helper、主串流+replay 兩路接線、done/error 出口強制 flush、`scrollTop` 併入同幀——消 O(n²) 熱路徑。
  - **C4 — Paint Hints（字型預載/被動監聽/內容可視性）**：兩支 woff2 `preload` + 兩處 scroll `{passive:true}` + `.msg-user`/`.msg-ai` 加 `content-visibility: auto; contain-intrinsic-size: auto <fallback>`。
  - **checkout — 成果收官歸檔（成果歸檔與移出暫存）**：Conformance U1–U8 + SOP §4 檢查表總驗 + staged 白名單自檢 + checkout 執行報告 + baton 歸檔 + TODO 雙層結案。
- **影響範圍**：100% 前端（`static/index.html` + vendor 新檔）；SSE 契約零改、`renderMarkdownWithMath` 內部零改、零 `.py`、零 golden。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案/位置 | 現狀 | 缺失 / 待處理 |
|---|---|---|
| `static/index.html:8` | marked 9.1.6 自 cdnjs **同步**載入 | 唯一跨源依賴、parser-blocking、離線/GFW 白屏（C1/C2） |
| `:11` | KaTeX 自託管但**同步** | parser-blocking（C2 defer） |
| `:1599-3833`（單一 inline `<script>`） | 頂層 `marked.use()`（`:1607`）等即時執行 | 直接 defer 必 ReferenceError → 需 DOMContentLoaded 整包（C2）；body markup `:1367-1598` 已驗**零 inline handler** |
| `:3518-3524` 主串流 | 每 `sentence` 全量 `renderMarkdownWithMath`+`innerHTML`+讀 `scrollHeight` | O(n²) 重排 + 每 token 強制 reflow（C3）；**done 分支（`:3525`）不重渲染**→節流後需 flush |
| `:3202-3214` replay | 同模式；含 `removeCursor()`/`appendCursor()` 包渲染；**done 分支自帶收尾渲染** | 節流接線需保 cursor 語意（C3） |
| `:1781` / `:1922` scroll | capture、未 passive（handler 無 preventDefault） | 主執行緒阻塞風險（C4） |
| `:1014 .msg-user` / `:1040 .msg-ai` | 無 content-visibility | 長對話視窗外泡泡全量 layout/paint（C4·U8） |
| `static/vendor/katex/fonts/` | `KaTeX_Main-Regular.woff2`(25.7K)/`KaTeX_Math-Italic.woff2`(16.1K) 存在但未 preload | 公式頁 FOUT（C4·U4） |

---

## §3 觀察問題

### 問題 #1：串流 O(n²) 全量重排（體感最卡）
- **證據**：`file:///static/index.html#L3518-L3524`（主）、`#L3202-L3214`（replay）；`renderMarkdownWithMath` 每 token 對整段累積字串重跑。
- **影響**：長答案數百次全量 parse+layout+paint+強制 reflow，UI 凍結。

### 問題 #2：head 同步跨源 script
- **證據**：`#L8` cdnjs marked 無 defer；`#L1607` 頂層 `marked.use()` 鎖死 defer 路徑。
- **影響**：阻塞 HTML parsing；cdnjs 不通即白屏（與 KaTeX 自託管理由矛盾）。

### 問題 #3：資源提示與監聽細節
- **證據**：woff2 未 preload；scroll 未 passive；全檔 rAF=0；`.msg-*` 無 content-visibility。
- **影響**：公式 FOUT、滾動阻塞、長對話滾動成本線性攀升。

---

## §4 設計方案

### §4.1 C1 — Marked Vendoring（marked 自託管換源）
- `mkdir -p static/vendor/marked` + 自 cdnjs 原 URL 下載 **9.1.6** 原檔（鎖版、Q3）；驗 byte 規模（~39KB）與版本標記。
- `index.html:8` src 換 `/static/vendor/marked/marked.min.js`（**本 commit 不加 defer**——換源與時序變更分離、各自可逆）。
- 行為零變（同版同步載入、僅來源改變）。

### §4.2 C2 — Deferred Boot（defer 與初始化包裹）
- 前置閘（U3-4）：`grep -nE 'on[a-z]+='` 全檔（含 JS 建構字串）期望 0；若命中→該函式 `window.fn=fn` 顯式暴露後才包裹、記入執行報告。
- `:8`/`:11` 兩 script 加 `defer`。
- inline 主 script 整包（Q7）：`<script>` 後插 `document.addEventListener('DOMContentLoaded', () => {`、`</script>` 前插 `});`，**頭尾插入、不重排既有 2200 行縮排**（diff 最小化）、加 `[FE-PERF-2 C2]` 註解 marker。deferred 保證先於 DOMContentLoaded 執行 → `marked.use()`（`:1607`）安全。

### §4.3 C3 — Stream Throttle（串流節流與滾動同批）
- 新增節流 helper（包內、`renderMarkdownWithMath` 附近）：`makeThrottledRenderer(paintFn)` → `{update(txt), flush(), cancel()}`——dirty-flag + rAF + 最小間隔 160ms（Q1）；`flush()` 取消 pending 並以最新內容立即 paint；paint 內**最後**執行捲底（Q2、同幀一次）。
- **主串流接線**（`:3518-3524`）：`sentence` 分支改 `r.update(formatted)`；paintFn＝現行「`innerHTML`+`scrollTop=scrollHeight`」封裝；**`chunk.done`（`:3525`）先 `r.flush()` 再 grounding sources**；外層 `catch`（`:3537`）補 `r.flush()`（斷線保留尾巴）。
- **replay 接線**（`:3202-3214`）：paintFn 含既有 `removeCursor()`→`innerHTML`→`appendCursor()`→`scrollTop` 語意；**done 分支自帶收尾渲染 → 改 `r.cancel()` 後沿用既有 final render 原碼**（byte 等價、最小侵入）。
- 不變式：同輸入 → 最終 HTML 與改前一致；`renderMarkdownWithMath` 內部零改。

### §4.4 C4 — Paint Hints（字型預載/被動監聽/內容可視性）
- head（`:10` 前）插兩條：`<link rel="preload" href="/static/vendor/katex/fonts/KaTeX_{Main-Regular,Math-Italic}.woff2" as="font" type="font/woff2" crossorigin>`（僅此二支、U4）。
- `:1781` 尾參改 `{capture:true, passive:true}`；`:1922` 同（U5）。
- `:1014 .msg-user` 與 `:1040 .msg-ai` 各加：`content-visibility: auto; contain-intrinsic-size: auto 120px;`（**記憶尺寸型、禁固定值**；120px 估值僅首渲染前生效、數值非關鍵）（U8）。

### §4.5 checkout — 成果收官歸檔
Conformance（plan §2 U1–U8 跨 commit 覆蓋 / tasks §6 重跑 / §7 不可動 / 提示詞 7 份稽核 / msg 草稿）+ §7.2 豁免（Q6）+ **checkout 執行報告直產 `executions/`**（WORKFLOW_SOP §3 鐵律：五維度+staged 自檢輸出+baton 歸檔確認+§8 一行 commit）+ staged 白名單自檢（多/少一檔即停）+ baton 一次性歸檔 + **TODO 雙層結案**（framework §2.5 v5：完整表格追加 `archive/TODO_done_archive.md` + TODO 一行索引 + 類別索引）+ hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C2 包裹後全域暴露改變（JS 建構字串含 inline handler） | 🟡 中 | 前置閘 grep 期望 0（body 已驗 0）；命中→window 顯式暴露；C2 §6.2 全站互動 E2E |
| C3 節流器漏 flush（最後一批 dirty 未渲染） | 🟡 中 | 三出口收斂（主 done/外層 catch/replay cancel+原碼收尾）；E2E 驗尾字完整 |
| C3 replay cursor 語意破壞 | 🟡 中 | paintFn 封裝既有 remove/appendCursor 原順序；replay done 沿用原收尾碼 byte 等價 |
| C4 content-visibility 上捲跳動 | 🟡 中 | 強制 `contain-intrinsic-size: auto <fallback>`（記憶尺寸）；E2E ≥30 則上捲；不合格單獨 revert（獨立兩行） |
| C1 下載檔完整性/版本漂移 | 🟢 低 | 鎖 9.1.6 原 URL、byte+版本標記驗證、三軌 smoke |
| .bak ×4（各 ~153KB）入 git 體積 | 🟢 低 | 鐵律要求之審計成本、可接受；checkout 後可由 baron 評估 archive 清理另案 |
| defer 時序（包外殘留同步依賴） | 🟢 低 | 單一 script 塊整包、無第二塊；E2E 硬重整+封鎖 cdnjs 驗證 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
ls -la static/vendor/marked/marked.min.js            # 存在、~39KB 級
grep -c "cdnjs" static/index.html                    # 期望 0
grep -c "/static/vendor/marked/marked.min.js" static/index.html   # 期望 1
grep -cE "9\.1\.6|marked" static/vendor/marked/marked.min.js      # 期望 ≥1（版本/庫標記）
# E2E：三軌開頁渲染正常（markdown 生效）、console 0 error
```

### §6.2 C2 驗收
```bash
grep -cE '<script src="/static/vendor/(marked/marked|katex/katex)\.min\.js" defer>' static/index.html  # 期望 2
grep -c "DOMContentLoaded" static/index.html          # 期望 ≥1（C2 包裹 marker 段）
grep -cE "on[a-z]+=" static/index.html                # 前置閘：期望 0（含 JS 字串）
# E2E：硬重整無 "marked is not defined"；DevTools block cdnjs → 零影響；上傳/主題/傳訊互動 smoke；console 0
```

### §6.3 C3 驗收
```bash
grep -c "requestAnimationFrame" static/index.html     # 期望 ≥1
grep -cE "makeThrottledRenderer|r\.flush\(\)|\.update\(" static/index.html   # helper+兩路接線命中
# E2E：長答案串流輸入框可打字；尾字完整；replay（重整）正常含 cursor；grounding sources 正常；
#      DevTools Performance：渲染批次 ≤ ~6-7 次/秒（改前每 token 一次 long task）
```

### §6.4 C4 驗收
```bash
grep -c 'rel="preload"' static/index.html             # 期望 2（兩支 woff2）
grep -cE "passive: *true" static/index.html           # 期望 ≥2
grep -c "content-visibility" static/index.html        # 期望 ≥2（.msg-user/.msg-ai）
grep -cE "contain-intrinsic-size: *auto" static/index.html   # 期望 ≥2（記憶尺寸型、禁固定值）
# E2E：公式頁 Network 驗 woff2 早期發起、無 FOUT；滾動關 popup 正常；≥30 則上捲無跳動、串流錨底不變
```

### §6.5 checkout 驗收
```bash
git -c core.quotepath=false diff --stat <base>..HEAD  # 僅 static/index.html + static/vendor/marked/** + archive/*.bak + 歸檔文件
pytest tests/ -q                                      # 基線 passed（零 .py 旁證）
ls .claude-logs/baton/ | grep FE-PERF-2               # 期望：無（過程檔全歸檔）
grep -n "FE-PERF-2" .claude-logs/TODO.md              # 期望：一行索引 + 類別索引 ✅；archive/TODO_done_archive.md 有完整表
# SOP §4 檢查表（U7）：C1–C4 執行報告 §自評均含勾選、checkout Conformance 總驗
```

---

## §7 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] **後端業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` — 100% 不動（SSE 契約 `chunk.sentence`/`done`/`grounding_sources` 零改）。
- [ ] **`renderMarkdownWithMath`（`:1623-1671`）內部七步佔位管線** — 只改呼叫頻率；解析邏輯/正則/佔位順序零改（SOP §3-1）。
- [ ] **marked 版本** — 鎖 9.1.6；嚴禁升版。
- [ ] **KaTeX vendor 本體**（`static/vendor/katex/**`）— 僅 head 加 preload 標籤。
- [ ] **`login.html` / `themes/*.css` / `design/docs/*`** — 不動。
- [ ] **側欄 `transition: width` / `.collapsed` rail** — audit #6 裁決不做。
- [ ] **audit 緩議/不做項嚴禁夾帶**：#5 popup/tooltip rAF 定位、§1-3 hover prefetch、#8 KaTeX code-split、`:3116` 歷史載入路徑。
- [ ] **`.py` / `tests/` / DB / 向量 / golden** — 零觸碰（`final_zh` byte 不變、無 golden 重捕）。
- [ ] **baton 暫存鐵律**：Run 產出之執行報告嚴禁 mv/git add；唯 checkout 一次性歸檔。
- [ ] **收官 git-add 白名單鐵律**：一律逐檔顯式、禁 `git add .`/`-A`/`<目錄>`；commit 前 `git diff --cached --name-only` 自檢＝宣告清單。

---

## §8 推薦 Commit 拆分

### C1 — Marked Vendoring（marked 自託管換源）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `static/vendor/marked/marked.min.js`；修改 `static/index.html`（僅 `:8` src 一行）；備份 `archive/2026-07-09_FE-PERF-2_C1_index.html.bak`（入 git）。〔執行報告暫存 baton、不入 git〕 |
| **安全性** | 🟢 高 — 同版換源、零行為變更；殺跨源依賴。 |
| **可逆性** | 🟢 高 — `git revert C1` 即回 CDN；vendor 檔獨立可刪。 |
| **驗收 grep 條件** | §6.1（cdnjs=0、vendor 路徑=1、檔案存在+版本標記、三軌 smoke）。 |
| **依賴關係** | 無前置。 |
| **具體實作細節** | ① `cp static/index.html archive/2026-07-09_FE-PERF-2_C1_index.html.bak`。② `mkdir -p static/vendor/marked && curl -o static/vendor/marked/marked.min.js https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js`；驗 `ls -la`（~39KB）+ `grep -c marked` ≥1。③ `index.html:8` 改 `<script src="/static/vendor/marked/marked.min.js"></script>`（**不加 defer**、留 C2）。④ 跑 §6.1 + 三軌 E2E smoke + console 0。⑤ 報告 §自評附 SOP §4 檢查表相關項。git add（逐檔）：vendor 檔 + index.html + C1 .bak。 |

### C2 — Deferred Boot（defer 與初始化包裹）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/index.html`（`:8`/`:11` 加 defer + `:1599`/`:3833` 頭尾插包裹）；備份 `archive/2026-07-09_FE-PERF-2_C2_index.html.bak`（入 git）。〔執行報告暫存 baton〕 |
| **安全性** | 🟡 中 — 改載入時序；有前置閘 + 整包策略（Q7）+ E2E 防護。 |
| **可逆性** | 🟢 高 — `git revert C2` 回同步載入；與 C1 解耦（revert C2 仍保自託管）。 |
| **驗收 grep 條件** | §6.2（defer=2、DOMContentLoaded marker、前置閘 on[a-z]+= 0、硬重整/封鎖 cdnjs E2E）。 |
| **依賴關係** | 前置 C1（defer 的 src 須已是本地檔）。 |
| **具體實作細節** | ① `.bak`。② **前置閘**：`grep -nE 'on[a-z]+=' static/index.html` 期望 0；命中→逐一 `window.fn=fn` 暴露並記入報告後才續。③ `:8`/`:11` 加 ` defer`。④ `:1599` `<script>` 次行插 `// === [FE-PERF-2 C2] DOMContentLoaded 包裹 START ===` + `document.addEventListener('DOMContentLoaded', () => {`；`:3833` `</script>` 前插 `}); // === [FE-PERF-2 C2] END ===`；**不重排既有縮排**。⑤ E2E：硬重整（無 ReferenceError）、DevTools block `cdnjs.cloudflare.com` 零影響、公式頁渲染、上傳/主題/傳訊 smoke、console 0。git add：index.html + C2 .bak。 |

### C3 — Stream Throttle（串流節流與滾動同批）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/index.html`（helper 新增 + `:3518-3524` 主串流與 `:3202-3214` replay 接線 + `:3525` done flush + `:3537` catch flush）；備份 `archive/2026-07-09_FE-PERF-2_C3_index.html.bak`（入 git）。〔執行報告暫存 baton〕 |
| **安全性** | 🟡 中 — 觸串流熱路徑；不變式明確（同輸入同最終 HTML）、管線內部零改。 |
| **可逆性** | 🟢 高 — `git revert C3` 回每 token 渲染；helper 獨立函式無外溢。 |
| **驗收 grep 條件** | §6.3（rAF≥1、helper+接線命中、長答案/replay/grounding E2E、Performance 批次對比）。 |
| **依賴關係** | 前置 C2（helper 定義於 DOMContentLoaded 包內、且 E2E 需 defer 環境定型）。 |
| **具體實作細節** | ① `.bak`。② 於 `renderMarkdownWithMath` 定義後新增（Q1/Q2 定案）：`function makeThrottledRenderer(paintFn){ let latest=null, timer=0, raf=0, last=0; const MIN=160; function paintNow(){ raf=0; last=performance.now(); const t=latest; latest=null; if(t!==null) paintFn(t); } function schedule(){ if(raf) return; const wait=Math.max(0, MIN-(performance.now()-last)); if(wait===0){ raf=requestAnimationFrame(paintNow); } else if(!timer){ timer=setTimeout(()=>{ timer=0; raf=requestAnimationFrame(paintNow); }, wait); } } return { update(t){ latest=t; schedule(); }, flush(){ if(timer){clearTimeout(timer);timer=0;} if(raf){cancelAnimationFrame(raf);raf=0;} if(latest!==null){ const t=latest; latest=null; paintFn(t);} }, cancel(){ if(timer){clearTimeout(timer);timer=0;} if(raf){cancelAnimationFrame(raf);raf=0;} latest=null; } }; }`。③ **主串流**：迴圈前 `const r = makeThrottledRenderer(t => { aiMsg.innerHTML = renderMarkdownWithMath(t); messages.scrollTop = messages.scrollHeight; });`；`:3519-3523` sentence 分支改 `accumulated += …; r.update(formatted)`；`:3525` `chunk.done` 分支**首行 `r.flush()`** 再 grounding；`:3537` 外層 `catch` 補 `r.flush()`（`isStreaming=false` 前）。④ **replay**：paintFn 封裝 `removeCursor(); aiMsg.innerHTML=renderMarkdownWithMath(t); appendCursor(); msgsEl.scrollTop=msgsEl.scrollHeight;`；sentence 分支改 `r.update(formatted)`；**done 分支首行 `r.cancel()`、其後既有收尾渲染原碼零改**（byte 等價）。⑤ E2E §6.3 全項 + SOP §4 檢查表。git add：index.html + C3 .bak。 |

### C4 — Paint Hints（字型預載/被動監聽/內容可視性）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `static/index.html`（head 2 preload + 2 scroll passive + `.msg-user`/`.msg-ai` CSS）；備份 `archive/2026-07-09_FE-PERF-2_C4_index.html.bak`（入 git）。〔執行報告暫存 baton〕 |
| **安全性** | 🟢 高 — 三項皆宣告式、彼此獨立；U8 有單獨 revert 逃生口。 |
| **可逆性** | 🟢 高 — `git revert C4`；或僅摘除 `.msg-*` 兩行（U8 獨立）。 |
| **驗收 grep 條件** | §6.4（preload=2、passive≥2、content-visibility≥2、intrinsic auto≥2、FOUT/上捲/錨底 E2E）。 |
| **依賴關係** | 無前置（排 C3 後純序列）。 |
| **具體實作細節** | ① `.bak`。② `:10` 前插兩條 `<link rel="preload" href="/static/vendor/katex/fonts/KaTeX_Main-Regular.woff2" as="font" type="font/woff2" crossorigin>`（另一條 Math-Italic）。③ `:1781` 監聽尾參 `true` → `{ capture: true, passive: true }`；`:1922` 同。④ `:1014 .msg-user{}` 與 `:1040 .msg-ai{}` 各加 `content-visibility: auto; contain-intrinsic-size: auto 120px;`（**auto 關鍵字必留**）。⑤ E2E §6.4 全項 + SOP §4 檢查表**全表總勾**。git add：index.html + C4 .bak。 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`+逐檔 `git add`：plan_v1→`plans/`、tasks→`tasks/`、C1–C4 執行報告→`executions/`；**新產** `executions/2026-07-09_FE-PERF-2_checkout_執行.md`（鐵律直產、入 git）；修改 `TODO.md` + `archive/TODO_done_archive.md`（雙層結案）+ prompts 7 份入 git。 |
| **安全性** | 🟢 高 — 純歸檔+狀態更新。 |
| **可逆性** | 🟢 高 — mv 可反向、TODO revert 可回。 |
| **驗收 grep 條件** | §6.5（diff 範圍、pytest 基線、baton 清空、TODO 雙層、SOP §4 總驗）。 |
| **依賴關係** | 前置 C1–C4 全部 ship。 |
| **具體實作細節** | ① Conformance：plan §2 **U1–U8 跨 commit 覆蓋總驗**（U1/U2→C3、U3→C1+C2、U4/U5/U8→C4、U6→§6.5 diff+pytest、U7→四報告 §自評）+ tasks §6 重跑 + §7 不可動逐項 + 提示詞 7 份（plan/Tasks/C1–C4/checkout）稽核入 git + msg 草稿五維度。② **§7.2 顯式豁免**（Q6：consumer 內部優化、SSE 契約零改）。③ **checkout 執行報告**依 WORKFLOW_SOP §3 鐵律直產 `executions/`（Conformance 五維度 + staged 自檢輸出實貼 + baton 歸檔確認 + §8 一行 commit）。④ baton 一次性歸檔（上列 mv + 逐檔 git add；audit 兩份長駐 baton 不碰）。⑤ **TODO 雙層結案**（framework §2.5 v5）：完整表格追加 `archive/TODO_done_archive.md`、TODO `## ✅ 已完成（索引）` 加一行、active 移除、類別索引標 ✅。⑥ hash 自癒（C1–C4 真實 hash + 殘留佔位掃描）。⑦ staged 白名單自檢：`git diff --cached --name-only` ＝宣告清單、多/少一檔即停。 |

---

## §9 Open Questions

無。（plan v3 §9 八 OQ 已全數 🟢 定案，見 plan §9.1；相容底線 Safari 18+ 已定案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-PERF-2 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FE-PERF-2 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改後端業務代碼與 `renderMarkdownWithMath` 內部；嚴禁跨 Commit 夾帶緩議項；嚴禁自動 git commit/push；baton 報告唯 checkout 歸檔；git add 逐檔白名單 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 設計依據唯一源在 plan v3；效能規範唯一源在 FE SOP；本檔僅拆分細節與驗收指令 |

### §99.2 Revision 歷程

- v1 (2026-07-09)：初版拆分——依 plan v3（八 OQ + 底線 Safari 18+ 定案）拆 5 commit〔C1 marked 9.1.6 自託管換源（不 defer）/ C2 defer+DOMContentLoaded 整包（前置閘 on[a-z]+=0）/ C3 rAF+160ms 節流 helper+主串流/replay 接線+done/catch flush+滾動同批 / C4 preload×2+passive×2+content-visibility 記憶尺寸型 / checkout（U1–U8 總驗+雙層結案+鐵律報告）〕；.bak ×4 各 commit 入 git；SSE 契約與渲染管線內部零改；同步 TODO 🟡 WIP。
