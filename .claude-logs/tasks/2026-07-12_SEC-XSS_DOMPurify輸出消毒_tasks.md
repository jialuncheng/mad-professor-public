# SEC-XSS 前端輸出消毒（DOMPurify）— Tasks

> 本文件為 SEC-XSS 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_plan_v1.md`（v1.1 execution-ready）產出，含 4 個 Commit（C1 → C2 → C3 → checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2~3 個 | `static/vendor/dompurify/purify.min.js`（+ 選配 `LICENSE`）/ `tests/test_sec_xss_guard.py` |
| **修改檔案** | 3 個 | `static/index.html` / `tools/fetch_frontend_vendor.sh` / `static/vendor/README.md` |
| **目錄定義** | 1 個 | `static/vendor/dompurify/` |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` baton plan + tasks + C1/C2/C3 執行報告 → `plans/` + `tasks/` + `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：`static/index.html` 以 `marked@9.1.6` 原始輸出直接寫 `innerHTML`、無 sanitizer（`static/` 無 vendored DOMPurify），最尖銳為 `renderSources`（Gemini grounding → 寫 DB → 重載重渲染＝stored XSS）；另 6 個 markdown sink、meta、論文清單標題皆未消毒。
- **解法（4 commit）**：
  - **C1 — Vendor & Load（DOMPurify 自託管與載入）**：npm pack 自託管 `static/vendor/dompurify/`、`fetch_frontend_vendor.sh` 追加下載段落、vendor README 登記 SHA-256、`index.html` head `defer` 載入；純載入、零行為變更。
  - **C2 — Markdown Sanitize（Markdown 渲染樞紐消毒）**：`renderMarkdownWithMath` 於 `marked.parse(t)`（L323）後、KaTeX 回填前注入 `DOMPurify.sanitize()`——一處覆蓋全部 6 個 markdown sink；佔位管線鐵律不動。
  - **C3 — Sources & Meta Hardening（來源節點化與元數據消毒）**：`renderSources` 節點化 + `href` scheme 白名單；`normalizeAcademicHeader` 與論文清單標題**變數單體消毒**（靜態模板 `data-tip`/`<svg>` 不進 sanitizer）。
  - **checkout — 成果收官歸檔**。
- **影響範圍**：100% FE-Refactor（`static/**` + `tools/fetch_frontend_vendor.sh` + `tests/`）；零後端、零 DB/API、零渲染管線行為。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `static/index.html` | `renderMarkdownWithMath` L323 `marked.parse(t)` 後直接回傳、無消毒；6 處 `innerHTML=renderMarkdownWithMath(...)` | markdown XSS 面（正文 + 對話氣泡） |
| `static/index.html` | `renderSources` L1777-1785 字串拼 `<a href="${s.uri}">${s.title}</a>` | grounding stored XSS（uri/title 未處理） |
| `static/index.html` | `normalizeAcademicHeader` L1634-1645 / 論文清單 item L1499-1505 動態插值入 `innerHTML` | meta / 標題 XSS（值為文件衍生） |
| `static/vendor/` | 僅 `marked/`+`katex/`，無 `dompurify/` | 無 sanitizer 可用 |
| `tools/fetch_frontend_vendor.sh` | 有 katex npm pack 段落（L6-24） | 缺 DOMPurify 下載段落 |
| `static/vendor/README.md` | 有 katex 分節 + SHA-256 表 | 缺 DOMPurify 分節 |

---

## §3 觀察問題

### 問題 #1：markdown 渲染無輸出消毒（6 sink）
- **證據**：`static/index.html:323`（`let html = marked.parse(t);` 後直接回傳）；6 消費點 L1607/1820/1840/1893/1925/2210。
- **影響**：AI 對話 / 論文正文任意 HTML 執行；同源 XSS。

### 問題 #2：renderSources stored XSS
- **證據**：`static/index.html:1781-1782`（`s.uri`/`s.title` 來自 Gemini grounding、`llm/client.py` 產、寫 DB grounding_sources、L1823/1928/2247 重載重渲染）。
- **影響**：惡意頁面標題（`<img onerror>`）/ `javascript:` uri → 持久化 XSS。

### 問題 #3：meta / 論文清單標題動態插值未消毒
- **證據**：`static/index.html:1635/1640/1643/1645`（meta）、`1502/1503/1505`（清單，模板含 `data-tip="文件選單"`+`<svg>`）。
- **影響**：文件衍生標題含腳本則執行。

---

## §4 設計方案

### §4.1 C1 — Vendor & Load（DOMPurify 自託管與載入）
- npm pack `dompurify@<pin 特定穩定 3.x，如 3.1.6>` → 取 `dist/purify.min.js` 存 `static/vendor/dompurify/`。
- `tools/fetch_frontend_vendor.sh`：比照 katex 段落（L6-24 範式）追加 `DOMPURIFY_VERSION` + npm pack + cp + sha256sum 段落。
- `static/vendor/README.md`：新增「dompurify/ — HTML 消毒引擎」分節（版本 / 官方來源 / 載入 / SHA-256）。
- `static/index.html` head：`marked` script（L9）後插 `<script src="/static/vendor/dompurify/purify.min.js" defer></script>`（defer、與 marked/katex 一致；app 邏輯於 DOMContentLoaded 後執行、DOMPurify 屆時已就緒）。
- **零行為變更**（載入未使用之庫）。

### §4.2 C2 — Markdown Sanitize（Markdown 渲染樞紐消毒）
- `renderMarkdownWithMath`：於 L323 `let html = marked.parse(t);` **後**、步驟 7 KaTeX 回填**前**注入：
  `html = DOMPurify.sanitize(html);`（DOMPurify 預設 config：允許標準 HTML 標籤 + `class` + `data-*`，涵蓋 marked 產出；KaTeX 可信產出於其後插入、不經消毒）。
- **佔位管線鐵律不動**：code/math/img 佔位抽取（步驟 1-5）與回填（步驟 7）一字不改；PUA 哨兵（``/``）為文字節點、經 sanitize 保留、回填正則照常。
- 一處改動覆蓋 6 個 markdown sink。

### §4.3 C3 — Sources & Meta Hardening（來源節點化與元數據消毒）
- `renderSources`（L1777）：改 `createElement('a')`；`a.textContent = s.title`；`href` 僅接受 `http:`/`https:`（`new URL` 或 scheme 正則判定，其餘不設 href / 丟棄）；`target=_blank rel=noopener` 保留；以 `appendChild` 組裝、不再字串拼 innerHTML。
- `normalizeAcademicHeader`（L1634-1645）：對 `authorsVal`/`venueVal`/`dateVal`/`doiVal`/`keywordsVal` **各自** `DOMPurify.sanitize(値)`（或純文字欄位用 `textContent` 更嚴）後填入既有靜態 `<div class="header-*">` 模板。
- 論文清單 item（L1499-1505）：對 `displayTitle`/`displaySubtitle` 單體消毒後填入模板；`data-tip="文件選單"`+`<svg>` menu 按鈕**原樣保留、不進 sanitizer**。

### §4.4 checkout — 成果收官歸檔
- `mv` baton plan → `plans/`、tasks → `tasks/`、C1/C2/C3 執行報告 → `executions/`；逐檔 `git add`。
- 產 `executions/2026-07-12_SEC-XSS_checkout_執行.md`（Conformance 五維度 + staged 自檢實貼 + baton 歸檔確認 + §8 一行 commit）。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| DOMPurify 消毒誤刪 KaTeX 數學（MathML/span） | 🟡 中 | 消毒點置 KaTeX 回填**前**、僅消毒 marked 產物；C2 測試 + E2E 驗數學不退化 |
| PUA math 佔位哨兵被消毒破壞致回填失敗 | 🟢 低 | 哨兵為純文字、DOMPurify 保留文字；C2 專項驗（含公式論文渲染正常） |
| 消毒誤刪 marked 合法產出（code/表格/class） | 🟢 低 | DOMPurify 預設允許標準標籤 + class + data-*；E2E 驗 |
| 消毒整段 meta/清單模板誤動 `data-tip`/`<svg>` | 🟢 低（已規避） | C3 採**變數單體消毒**、靜態模板不進 sanitizer（plan §5 補註） |
| DOMPurify 下載/版本不可重現（無網/GFW） | 🟢 低 | 自託管 npm pack + SHA-256 鎖定（比照 katex）；README 登記 |
| 破壞既有前端測試 | 🟢 低 | 測試讀靜態源、非 runtime DOM；不動 CSS/結構斷言；每 commit 跑全套件 |

---

## §6 測試計畫

> 依提示詞「各階段測試同步硬性綁定」：`tests/test_sec_xss_guard.py` 於 C1 建立、C2/C3 逐階段追加對應斷言（純靜態源守衛，比照 `tests/test_bug_*` 風格）。

### §6.1 C1 驗收
```bash
ls static/vendor/dompurify/purify.min.js                      # 期望：存在
grep -n "dompurify/purify.min.js" static/index.html           # 期望：head defer 載入命中
grep -n "DOMPURIFY_VERSION\|dompurify" tools/fetch_frontend_vendor.sh   # 期望：下載段落命中
grep -n "dompurify" static/vendor/README.md                   # 期望：分節 + SHA-256 命中
./venv/bin/python -m pytest tests/test_sec_xss_guard.py -q    # 期望：C1 守衛測試通過
```

### §6.2 C2 驗收
```bash
# renderMarkdownWithMath 於 marked.parse 後含 sanitize
grep -n "marked.parse(t)" static/index.html                   # L323
grep -n "DOMPurify.sanitize" static/index.html                # 期望：renderMarkdownWithMath 內命中（marked 後）
./venv/bin/python -m pytest tests/test_sec_xss_guard.py -q    # 期望：+markdown 消毒守衛通過
```

### §6.3 C3 驗收
```bash
# renderSources 不再字串拼 innerHTML；meta/清單變數單體消毒
grep -n 'href="${s.uri}"' static/index.html || echo "已移除字串拼接（節點化）"   # 期望：無命中
grep -n "createElement('a')\|textContent" static/index.html   # 期望：renderSources 節點化命中
./venv/bin/python -m pytest tests/test_sec_xss_guard.py -q    # 期望：+來源/meta 守衛通過
```

### §6.4 全套件迴歸（每 commit）
```bash
./venv/bin/python -m pytest tests/ -q     # 期望：綠燈基線不退化（≥708 passed 級別 + 新增守衛）
```

---

## §7 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] `renderMarkdownWithMath` 的 **code/math/img 佔位抽取與回填邏輯**（RAG-12 / RAG-12-HOTFIX-1）——僅允許 L323 後、KaTeX 回填前插入一行 sanitize。
- [ ] `static/vendor/marked/`、`static/vendor/katex/` 資產與載入方式。
- [ ] ~27 個**靜態/清空 sink**（`innerHTML=''`/靜態字串/空骨架）——不改動。
- [ ] **後端**：`web_server.py` 及任何 `.py` 業務代碼（`.py` 僅限 `tests/`）；DB grounding_sources schema 與儲存流程。
- [ ] 論文清單 / meta 模板中的 `data-tip` / `<svg>` menu 按鈕（靜態、不進 sanitizer）。
- [ ] 前端測試既有斷言本體。

---

## §8 推薦 Commit 拆分

### C1 — Vendor & Load（DOMPurify 自託管與載入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/vendor/dompurify/purify.min.js`（新增，+選配 `LICENSE`）、`tools/fetch_frontend_vendor.sh`（+`.bak`）、`static/vendor/README.md`（+`.bak`）、`static/index.html`（+`.bak`）、`tests/test_sec_xss_guard.py`（新增）；baton C1 執行報告**嚴禁**列入 git 追蹤 |
| **安全性** | 🟢 高 — 純資產自託管 + head 載入、零行為變更 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；改檔留 `.bak` |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① npm pack `dompurify@<pin 3.x>` 取 `dist/purify.min.js`（+選配 LICENSE）存 `static/vendor/dompurify/`；② `tools/fetch_frontend_vendor.sh` 比照 katex L6-24 追加 `DOMPURIFY_VERSION="…"` + npm pack + cp `dist/purify.min.js` + sha256sum 段落；③ `static/vendor/README.md` 新增 dompurify 分節（版本/來源/載入/SHA-256 實貼）；④ `static/index.html` head L9（marked script）後插 `<script src="/static/vendor/dompurify/purify.min.js" defer></script>`；⑤ 建 `tests/test_sec_xss_guard.py`：斷言 purify.min.js 存在 + index.html head 載入 dompurify + fetch 腳本含 DOMPurify 段落；⑥ 改檔先產 `.bak`；⑦ 跑 §6.1 + §6.4 |

### C2 — Markdown Sanitize（Markdown 渲染樞紐消毒）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（+`.bak`）、`tests/test_sec_xss_guard.py`（追加）；baton C2 執行報告嚴禁列入 |
| **安全性** | 🟢 高 — 單一函式一行注入、佔位管線不動 |
| **可逆性** | 🟢 高 — `git revert C2` 回滾；`.bak` |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 前置 C1（DOMPurify 已載入） |
| **具體實作細節** | ① `static/index.html` L323 `let html = marked.parse(t);` **後**、步驟 7 KaTeX 回填**前**插入 `html = DOMPurify.sanitize(html);`（預設 config）；② code/math/img 佔位抽取回填與 PUA 哨兵邏輯**一字不改**；③ `tests/test_sec_xss_guard.py` 追加：斷言 `renderMarkdownWithMath` 內 `marked.parse` 後含 `DOMPurify.sanitize`；④ 改檔先產 `.bak`；⑤ 跑 §6.2 + §6.4（含含公式論文渲染 sanity，若 fixture 允許） |

### C3 — Sources & Meta Hardening（來源節點化與元數據消毒）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（+`.bak`）、`tests/test_sec_xss_guard.py`（追加）；baton C3 執行報告嚴禁列入 |
| **安全性** | 🟢 高 — 侷限 3 個渲染函式、靜態模板保留 |
| **可逆性** | 🟢 高 — `git revert C3` 回滾；`.bak` |
| **驗收 grep 條件** | 見 §6.3 |
| **依賴關係** | 前置 C1（meta/清單單體消毒需 DOMPurify；renderSources 節點化不需 DOMPurify 但併於本 commit） |
| **具體實作細節** | ① `renderSources`（L1777）改節點化：`createElement('a')` + `a.textContent = s.title` + `href` 僅接受 `http(s):`（否則不設）+ `target/rel` 保留 + `appendChild`；② `normalizeAcademicHeader`（L1634-1645）對 authors/venue/date/doi/keywords **各自** `DOMPurify.sanitize(値)`（純文字欄位可 `textContent`）後填入靜態模板；③ 論文清單 item（L1499-1505）對 `displayTitle`/`displaySubtitle` 單體消毒後填入、`data-tip`/`<svg>` 原樣保留；④ `tests/test_sec_xss_guard.py` 追加：斷言 `renderSources` 無 `href="${s.uri}"` 字串拼接 + 含 `createElement('a')`/`textContent` + meta/清單單體消毒；⑤ 改檔先產 `.bak`；⑥ 跑 §6.3 + §6.4 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：plan → `plans/`、tasks → `tasks/`、C1/C2/C3 + checkout 執行報告 → `executions/`；狀態：`TODO.md`（🟡→✅ 雙層結案）、`prompts/INDEX.md`（已於 tasks 階段登記） |
| **安全性** | 🟢 高 — 純文件搬移 + 狀態更新 |
| **可逆性** | 🟢 高 — 文件層 `git revert` / `mv` 復位 |
| **驗收 grep 條件** | baton 歸檔後僅剩既有長駐真理源（SEC-XSS 暫存檔已移出）；`git diff --cached --name-only` = 宣告白名單 |
| **依賴關係** | 前置 C1/C2/C3 全綠 |
| **具體實作細節** | ① 產 `executions/2026-07-12_SEC-XSS_checkout_執行.md`（Conformance 五維度 + staged 自檢實貼 + baton 歸檔確認 + §7.2 純前端豁免）；② `mv`（**禁 `git mv`**）baton plan/tasks/C1-C3 報告至正式目錄；③ 逐檔顯式 `git add`（plan + tasks + 4 執行報告 + 各 `.bak` + 新增資產/測試 + `TODO.md` + `prompts/INDEX.md` + SEC-XSS 提示詞），**禁 `git add .`/`-A`/`<目錄>`**；④ commit 前 `git diff --cached --name-only` 自檢＝宣告清單；⑤ TODO 雙層結案（active 移除 + `archive/TODO_done_archive.md` 追加表格 + 索引一行 + 類別索引）；⑥ 附一行 commit 指令（baron 手動） |

---

## §9 Open Questions

無。（plan v1.1 §9 OQ1–OQ6 已於 baron review 全數拍板結案：混合方案 A / marked 後 KaTeX 前注入 / 動態子集 + 變數單體消毒 / CSP 留 BE 另案 / pin 3.x + SHA-256 / §7.2 顯式豁免。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SEC-XSS 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 SEC-XSS executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動後端業務代碼；嚴禁改渲染管線佔位邏輯；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-12)：初版拆分完成（依 plan v1.1；4 commit＝C1 Vendor & Load / C2 Markdown Sanitize〔L323 marked 後 KaTeX 前注入〕/ C3 Sources & Meta Hardening〔renderSources 節點化 + meta/清單變數單體消毒〕/ checkout；測試逐 commit 綁定 test_sec_xss_guard；§7.2 純前端豁免）
