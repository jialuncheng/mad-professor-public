# TODO-HOTFIX-1 — 緊急熱修復規劃書：TODO.md RAG 系列狀態損毀修復

> **類型**：DOC-Hotfix 規劃階段（v2，拆分為 2 個 Commit）  
> **問題**：TODO.md active 區塊 RAG 系列狀態混亂（已完成任務殘留 + 孤兒 heading + hash 缺失 + RAG-11/12 未獨立）+ MODEL-8 active 區殘留  
> **本文件用途**：baron 評估後授權執行，不含任何代碼改動

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 項目 | 狀態 |
|---|---|---|
| 修改 | `.claude-logs/TODO.md` | 兩次修改（TODO-HOTFIX-1 + TODO-HOTFIX-1b 各一次） |
| 新建 | `.claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak` | 第一次修改前備份 |
| 新建（暫存） | `.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md` | 本規劃書（baton/ 暫存） |
| 新建（暫存） | `.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_執行.md` | 執行報告（baton/ 暫存） |
| Commits | 2 個（TODO-HOTFIX-1 + TODO-HOTFIX-1b） | 待 baron 手動執行 |
| 收官歸檔 | hotfix.md + 執行.md → `hotfixes/` + `executions/` | 待 Check 階段執行 |

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **TODO-HOTFIX-1** | `待 baron 執行後回填` | `fix(TODO): sync RAG-1 Phase 2 and Bug Fix series to completed, split RAG-11/12` |
| **TODO-HOTFIX-1b** | `待 baron 執行後回填` | `fix(TODO): cleanup MODEL-8 active entry in TODO` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

**現象一：RAG-1 Phase 2 條目殘留 active 區**

- **現象**：`## 🟡 進行中 / ⬜ 未開始（依優先序）` → `### 🔴 高優先` 區塊仍包含一條已完成的 `✅ ~~**RAG-1 Phase 2 hashtag RAG 路由**~~...` 條目（第 198 行）
- **實際狀況**：該任務已在 `## ✅ 已完成` → `### Phase 4.X? RAG-1 Phase 2` 有完整表格（第 84–105 行，含 P2-1 `26a4439` / P2-2 `9ee44f3` / P2-3 `f85b830`）
- **影響**：active 區有已完成任務殘留，造成狀態二義

**現象二：RAG-1 Bug Fix 系列條目格式損毀（最嚴重）**

- **現象**：第 200–212 行為一整個混合區塊，包含：
  - 父行以 `✅ ~~**RAG-1 Bug Fix 系列**~~（**已落地、全鏈路收官**...）` 格式殘留於 active 區
  - 8 個子條目 BUG-F1~F6 + BUG-B1~B2 以 bullet 子列格式嵌入，非標準 `已完成表格`
  - BUG-B1 `hash 待 push 後回填`、BUG-B2 `hash 待 push 後回填`（hash 未填入）
  - RAG-11 / RAG-12 以子條目格式嵌入，應獨立為主條目
  - 結尾有多餘的「收官摘要」文字行
- **連帶問題**：第 213 行有孤兒標題 `### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）`，此標題無對應表格，純噪聲

**現象三：✅ 已完成區缺少 Bug Fix 系列專屬表格**

- Bug Fix 系列（8 commits）在 `## ✅ 已完成` 完全沒有對應的標準表格
- BUG-B1 / BUG-B2 hash 欄為「待 push 後回填」，但 git log 已顯示真實 hash

**現象四：RAG-11 / RAG-12 未獨立為主條目**

- 兩個任務目前以 `⬜` 子列格式嵌在 Bug Fix 系列 bullet block 內
- 應獨立為 `🔴 高優先` 的 `⬜ 未開始` 主條目（各自需要獨立 plan 評估）
- 索引區 `### RAG` 完全缺少這兩個任務的入口

### 2. 真因診斷 (Root Cause)

- **直接原因**：在歷史 session 中，Claude Code 在 TODO.md 中「標記」任務完成時，採用了 `✅ ~~...~~` 內聯格式殘留於 active 區（而非依照 §2.5 規定「從 active 列表移除 + 改寫入頂部 ✅ 已完成表格」）
- **加重因素**：WORKFLOW-1 的多輪 session 切換，使 TODO.md 的 active → completed 遷移動作跨 session 遺漏，cumulative 積壓
- **孤兒 heading**：第 213 行 `### Phase 4.X? RAG-1 Bug Fix 系列...` 是歷史整理時沖出的孤兒，其子表格從未被建立
- **hash 缺失**：BUG-B1 / BUG-B2 在落地時已知「待回填」，但後續 session 忘記補入

---

## Hash 盤點確認（via git log）

```bash
$ git log --oneline -n 20
9877e54  fix(RAG-1 BUG-F1): 前端 micro fix 包
ae20559  fix(RAG-1 BUG-F2): theme dropdown + ESC + P2-3 latent fix
57c71c8  fix(RAG-1 BUG-F3): .modal-input CSS
646afe4  fix(RAG-1 BUG-F4): P1 critical 4 項合併修
e799687  fix(RAG-1 BUG-F5): P2 inconsistencies
12428aa  fix(RAG-1 BUG-F6): P3 polish
a35a720  fix(RAG-1 BUG-B1): 後端 abstract fallback
94ed27d  fix(RAG-1 BUG-B2): 後端 blockquote → list + 前端 paper-header-meta CSS
```

**已確認 Hash 表：**

| Commit | Subject | Hash（git log 確認） |
|---|---|---|
| BUG-F1 | 前端 micro fix 包（Bug 1/3/4/5、5 pytest） | `9877e54` ✅ |
| BUG-F2 | theme dropdown + ESC + P2-3 latent fix（Bug 2+11、6 pytest） | `ae20559` ✅ |
| BUG-F3 | .modal-input CSS（Bug 7、2 pytest） | `57c71c8` ✅ 新確認 |
| BUG-F4 | P1 critical 4 項（A1~A4、9 pytest） | `646afe4` ✅ 新確認 |
| BUG-F5 | P2 inconsistencies（B1+B3+B4、8 pytest） | `e799687` ✅ 新確認 |
| BUG-F6 | P3 polish（C4+C5+C7、7 pytest） | `12428aa` ✅ 新確認 |
| BUG-B1 | 後端 abstract fallback（Bug 8、28 pytest） | `a35a720` ✅ 補填 |
| BUG-B2 | 後端 blockquote→list + paper-header-meta（Bug 10、7 pytest） | `94ed27d` ✅ 補填 |

---

## 熱修復修法（Minimal Hotfix — 最小 Markdown Diff 預覽）

**唯一目標檔**：`.claude-logs/TODO.md`  
**業務代碼變動**：0

---

### 修法 A：在 `## ✅ 已完成` 建立 Bug Fix 系列表格

**位置**：緊接在 `### Phase 4.X? RAG-1 Phase 2 Hashtag RAG...` 表格區塊之後，`### Phase 4.X? RAG-1 前端 UI Fixes...` 之前。

```diff
+ ### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）
+
+ | Commit | 內容 | Hash |
+ |---|---|---|
+ | BUG-F1 | 前端 micro fix 包 — tag fallback / placeholder 斷行 / export-btn / --content-max-w（Bug 1/3/4/5、5 pytest） | `9877e54` |
+ | BUG-F2 | theme dropdown + ESC + P2-3 latent fix — dropdownAPI IIFE + TDZ-aware 3 段拆分（Bug 2 + Bug 11、6 pytest） | `ae20559` |
+ | BUG-F3 | .modal-input CSS — ui-fixes-batch B5 廣義 selector + color-mix 跨主題 focus ring（Bug 7、2 pytest） | `57c71c8` |
+ | BUG-F4 | P1 critical 4 項 — A1 trackProgress / A2 empty-state / A3 customPrompt / A4 closeBizPopups（9 pytest） | `646afe4` |
+ | BUG-F5 | P2 inconsistencies — B1 廢 token 替換主 scale + B3 demo-bar dead code + B4 no-op（8 pytest） | `e799687` |
+ | BUG-F6 | P3 polish — C4 ~43 ticket 註解清理 / C5 marked 改寫 / C7 ⋯→SVG；C3+C6 no-op（7 pytest） | `12428aa` |
+ | BUG-B1 | 後端 abstract fallback — A 側路 translate_text + B regex 擴中日文「摘要/概要/內容提要/要旨」（Bug 8、28 pytest） | `a35a720` |
+ | BUG-B2 | 後端 blockquote→list + 前端 paper-header-meta CSS — `>` → `-` list + `<div>` wrap + @media screen（Bug 10、7 pytest、全鏈路收官） | `94ed27d` |
+
+ > **修法依據**：`.claude-logs/2026-05-24_RAG-1_前端_Bug_Fix_可行性評估.md` v2/v3 + `.claude-logs/2026-05-24_RAG-1_Bug_Fix_可行性評估.md` v4  
+ > **收官摘要**：6 前端 + 2 後端 = 8 commits、修 9 / 11 bugs、共 72 pytest 全綠、零迴歸；Bug 6 / Bug 9 延後為 RAG-11 / RAG-12
```

---

### 修法 B：從 `## 🟡 進行中` 徹底移除損毀區塊（第 198–213 行）

```diff
- - ✅ ~~**RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI**~~（已落地、P2-1 + P2-2 + P2-3 三 commit、共 26 pytest、見上方 ✅ 完成區、跟 Phase 1 R1/R2/R3 並列為 **RAG-1 完整收官**、跨文件查詢 baron 需求 3 / Commit 15 plan Q7 同步收官）
-
- - ✅ ~~**RAG-1 Bug Fix 系列**~~（**已落地、全鏈路收官**、前端 6 + 後端 2 = 8 commits、共 72 pytest、依 `.claude-logs/2026-05-24_RAG-1_前端_Bug_Fix_可行性評估.md` v2/v3 + `.claude-logs/2026-05-24_RAG-1_Bug_Fix_可行性評估.md` v4）
-   - ✅ **BUG-F1 前端 micro fix**（修 Bug 1/3/4/5、5 pytest、hash `9877e54`）
-   - ✅ **BUG-F2 theme dropdown + ESC + P2-3 latent fix**（修 Bug 2 + Bug 11、TDZ-aware 3 段拆分、6 pytest、hash `ae20559`）
-   - ✅ **BUG-F3 modal-input CSS**（修 Bug 7、ui-fixes-batch B5 + color-mix focus ring、2 pytest、hash `57c71c8`）
-   - ✅ **BUG-F4 P1 critical（A1+A2+A3+A4）**（修 4 項：trackProgress / empty-state / customPrompt / closeBizPopups、9 pytest、hash `646afe4`）
-   - ✅ **BUG-F5 P2 inconsistencies（B1+B3、B4 no-op）**（修 B1 廢 token + B3 demo-bar dead code、8 pytest、hash `e799687`）
-   - ✅ **BUG-F6 P3 polish（C4+C5+C7、C3+C6 no-op）**（修 ~43 ticket 註解清理 + marked 註解改寫 + ⋯→SVG、7 pytest、hash `12428aa`）
-   - ✅ **BUG-B1 後端 abstract fallback**（Bug 8 A 側路 + B regex 擴中日文、28 pytest、hash 待 push 後回填）
-   - ✅ **BUG-B2 後端 blockquote → list + 前端 paper-header-meta CSS**（Bug 10 混合 bug、後端 `>` → `-` + wrap + 前端 `@media screen` class hook hide、7 pytest、hash 待 push 後回填）
-   - ⬜ **RAG-11 reload SSE 還原**（延後、Bug 6、API 合約變更獨立 plan）
-   - ⬜ **RAG-12 LaTeX KaTeX**（延後、Bug 9、新 CDN 依賴獨立 plan）
-   - **收官摘要**：6 前端 + 2 後端 = 8 commits、修 9 / 11 bugs（含 P2-3 hashtag-autocomplete latent 自我發現）、共 72 pytest 全綠、零迴歸；2 延後 bug 另開獨立任務 RAG-11/12
-
- ### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）
```

---

### 修法 C：在 `### 🔴 高優先` 新增 RAG-11 / RAG-12 獨立主條目

**位置**：QUEUE-1 條目之後（`✅ ~~**RAG-1 Phase 2...**~~` 刪除後的空位）。

```diff
+ - ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
+   - 問題：切換 paper / 重新整理後，SSE chat history reload 功能缺失（API 合約需調整）
+   - 工時：待 plan 評估（預估 1-2 commits）
+   - 依賴：無
+
+ - ⬜ **RAG-12 LaTeX KaTeX 渲染支援**（Bug 9、需獨立 plan 評估）
+   - 問題：論文 / 履歷中的 LaTeX 數學公式無法在前端正確渲染（需引入 KaTeX CDN）
+   - 工時：待 plan 評估（預估 1 commit）
+   - 依賴：無
```

---

### 修法 D：更新 `## 索引（依類別）` → `### RAG` 段

```diff
- ### RAG（7 項 active）
+ ### RAG（9 項 active）
  - ✅ ~~RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI~~（已落地、P2-1 + P2-2 + P2-3 三 commit、見 ✅ 完成區）
  - ✅ ~~RAG-1 Phase 1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫~~（已落地、R1 + R2 + R3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
+ - ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
  - RAG-3 score 校準（中、等數據）
  - RAG-4 前端引用顯示（中）
  - RAG-5 合併 cap（低）
  - RAG-6 docs（低）
  - 🔵 RAG-10 中文 Header meta block 軟換行渲染 bug（候選、修法 ~5 行、user-facing 排版）
+ - ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
+ - ⬜ RAG-12 LaTeX KaTeX 渲染支援（高、需獨立 plan）
  - ⚙️ ~~RAG-2 backfill CLI~~（合併到 MODEL-8、見 MODEL 區）
  - ✅ ~~RAG-7 doc_analyzer 切 section~~（已落地、拆 RAG-7a `e2ed0e4` + RAG-7b `5c182cf`）
  - ✅ ~~RAG-8 md_restore / translate table 渲染 bug~~ `230ca13`
  - ✅ ~~RAG-9 markdown `~` 誤判刪除線~~ `3a0c523`
```

---

## E2E 驗證計畫（下階段執行後驗收）

| # | 驗收項目 | 驗收指令 / 方式 |
|---|---|---|
| V1 | ✅ 已完成區包含 Bug Fix 系列表格（含 BUG-F1~F6 + BUG-B1~B2 標題） | `grep -n "BUG-F1\|BUG-B1" .claude-logs/TODO.md` → 需在 ✅ 已完成區命中 |
| V2 | BUG-B1 hash = `a35a720`、BUG-B2 hash = `94ed27d` | `grep -n "a35a720\|94ed27d" .claude-logs/TODO.md` → 2 命中 |
| V3 | active 區不再有 RAG-1 Phase 2 / Bug Fix 殘留條目 | `grep -n "~~\*\*RAG-1" .claude-logs/TODO.md` → 僅應在 ✅ 已完成表格或索引區命中 |
| V4 | 孤兒 heading 消除 | `grep -n "Phase 4.X.*RAG-1 Bug Fix 系列" .claude-logs/TODO.md` → 0 命中（待刪除的孤兒）或 1 命中（✅ 已完成標題） |
| V5 | RAG-11 / RAG-12 出現為 `⬜` 獨立主條目 | `grep -n "RAG-11\|RAG-12" .claude-logs/TODO.md` → 命中應在高優先區與索引區 |
| V6 | 業務代碼零改動 | `git diff --cached --name-only \| grep -E "\.py$\|\.html$\|\.js$"` → 0 命中 |

---

## 回退與備案

本次修改為純 DOC-Hotfix，僅改動 `.claude-logs/TODO.md`。

若執行有誤，可用以下方式復原：

```bash
# 查找 TODO.md 的備份（執行前 Claude Code 應先備份至 archive/）
ls .claude-logs/archive/*TODO*

# 或直接 git checkout 還原
git checkout HEAD -- .claude-logs/TODO.md
```

---

## 執行前提條件

- **本文件為規劃預覽**，未對 TODO.md 做任何修改
- **等待 baron 評估確認後**，方可進入執行階段
- 執行時須先備份：`cp .claude-logs/TODO.md .claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak`

---

## Commit 拆分六維度表格

### Commit TODO-HOTFIX-1 — RAG 狀態整理與 RAG-11/12 抽離

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/TODO.md`（唯一目標檔）；業務代碼 0 改動 |
| **安全性** | 🟢 高 — 純文字 Markdown 整理，無邏輯代碼；備份已建立 |
| **可逆性** | 🟢 高 — `git checkout HEAD -- .claude-logs/TODO.md` 或 `cp archive/2026-05-26_TODO-HOTFIX-1.md.bak .claude-logs/TODO.md` |
| **驗收 grep 條件** | V1~V6（詳見 E2E 驗證計畫）：BUG-F1/BUG-B1 在 ✅ 完成區、hash 補填、active 無殘留、孤兒消除、RAG-11/12 獨立、業務代碼 0 |
| **依賴關係** | 無前置依賴；TODO-HOTFIX-1b 需在本 Commit 後執行 |
| **具體實作細節** | ①備份 TODO.md → ②✅ 已完成區插入 Bug Fix 表格（修法 A）→ ③刪除 active 區損毀 block（修法 B）→ ④新增 RAG-11/12 獨立條目（修法 C）→ ⑤更新 RAG 索引計數 7→9（修法 D）→ ⑥V1~V6 grep 驗收 |

### Commit TODO-HOTFIX-1b — MODEL-8 進行中殘留清理

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/TODO.md`（唯一目標檔）；業務代碼 0 改動 |
| **安全性** | 🟢 高 — 純刪除已完成任務的 active 殘留條目，不影響 ✅ 已完成區的完整表格 |
| **可逆性** | 🟢 高 — `git checkout HEAD~1 -- .claude-logs/TODO.md` |
| **驗收 grep 條件** | `grep -n "MODEL-8 SQLite paper_chunks 物理防線" .claude-logs/TODO.md` → 期望：active 區 0 命中，僅在 `## ✅ 已完成` 表格（第 71 行附近）與索引區命中 |
| **依賴關係** | 前置：TODO-HOTFIX-1 必須已完成 |
| **具體實作細節** | ①確認 ✅ 已完成區 MODEL-8 表格（第 71 行）hashes 完整（C1 `aeb42cb` / C2 `ab40fdc` / C3 `16f62d4`）→ ②定位 active 區殘留條目（第 235 行：`- ✅ ~~**MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI**~~...`，含後方兩個空行）→ ③實體刪除此單行殘留 → ④grep 驗收 |

---

### 修法 E（TODO-HOTFIX-1b 專屬）：從 `## 🟡 進行中` 移除 MODEL-8 殘留

**定位**：`### 🟡 中優先` 區段，第 235 行（近似）。

**現況**（需刪除的單行）：
```
- ✅ ~~**MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI**~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
```

**對應的 ✅ 已完成表格確認**（第 71–78 行，hashes 已正確）：
- C1 `aeb42cb` ✅
- C2 `ab40fdc` ✅
- C3 `16f62d4` ✅

```diff
- - ✅ ~~**MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI**~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
```

**結果**：`🟡 中優先` 區段的 MODEL-8 條目完全消除，僅保留 ✅ 已完成表格中的完整記錄。
