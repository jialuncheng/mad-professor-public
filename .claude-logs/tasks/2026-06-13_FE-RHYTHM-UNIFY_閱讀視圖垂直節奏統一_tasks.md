# FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一 — Tasks

> 本文件為 FE-RHYTHM-UNIFY 的 Commit 拆分清單（階段 2 產出）。
> 依據 plan：`.claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_plan_v1.md`（v2、九 OQ 全定案、§9.1 凍結候選模型）。
> 含 3 個 Commit（C1 Spike → C2 模型落地 → C3 Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （spike harness 為 worktree 拋棄式、不入版控；spike 報告與各 commit 執行報告暫存 baton/） |
| **修改檔案** | 5 個 | `static/index.html`（base：加統一節奏模型 + 移除 FE-RHYTHM-1 兩條 :has）/ `static/themes/kahn.css`·`kandinsky.css`·`mies.css`·`nara.css`（各移除 p/h 垂直 margin、保留色票/字族/border/padding） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（高優先區新增 FE-RHYTHM-UNIFY）/ `prompts/INDEX.md`（Tasks 提示詞已歸檔） |
| **Commits** | 3 個 | C1（Spike & 模型凍結）→ C2（統一垂直節奏模型落地·atomic）→ C3（Checkout 收官） |
| **baton 歸檔** | 1 次 | C3 收官：`mv` baton（plan v1/tasks/C1-C3 報告 + spike 報告）→ `plans/`+`tasks/`+`executions/`，及 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：閱讀視圖（`#paper-content`）垂直間距由「逐交界 bespoke 規則」治理（主題各設 p/h margin、L83 reset 歸零清單 margin、FE-RHYTHM-1 補 p↔list…），根因＝**只用 margin-bottom + 清單 margin 被歸零** → 節奏天生不對稱、每出現新交界要補一條（打地鼠）；且「區段標籤」因 Vision 措辭走 `###` 或 `<p>` 兩條節奏路徑。
- **解法**：以 **margin-top flow 單一節奏模型**（基準流 + 三檔 + 一條最貼、見 plan §9.1）取代逐交界補丁；收編 FE-RHYTHM-1、取消擬議 FE-RHYTHM-2。原子化為 3 commit：
  - **C1 — Spike & 模型凍結（垂直節奏 spike）**：worktree 拋棄式 harness 驗 3 假設（直接子代 / 巢狀清單不誤撐 / Dia 渲染）+ 凍結 token 與特殊塊處理；零 production diff。
  - **C2 — 統一垂直節奏模型落地（atomic 模型替換）**：index.html 加 4 條 flow + 移除 FE-RHYTHM-1；4 主題移除 p/h 垂直 margin；特殊塊明列 margin-top。**5 檔一次 atomic 換模型**（避免 double/zero 破中間態）。
  - **C3 — Checkout 收官（驗收歸檔）**：Conformance + baton 一次性歸檔 + TODO 結案。
- **影響範圍**：純前端 CSS（index.html + 4 主題）；全文體閱讀視圖共用；chat（`.msg-ai`）不受影響；零後端/pipeline/RAG/final_zh；無 golden 重捕。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `static/index.html` L83 | 全域 reset `body,h1,h2,h3,p,ol,ul{margin:0;padding:0}` | 歸零後由主題再加回 margin → 節奏散落兩處 |
| `static/index.html` L915-922 | FE-RHYTHM-1 兩條 `p:has(+ul/ol)` / `ul:has(+p)`（margin-bottom 制） | 逐交界補丁、margin-bottom 制需 `:has`；C2 收編移除 |
| `static/index.html` L885-893 | `.slide-head{margin:space-6 0 space-3 + border}`、`.slide-sub{margin:4px 0 0}` | 特殊塊自帶 margin；flow `*+*` 會疊加 → C2 須明列 margin-top |
| `static/index.html` L869-874 | `#paper-content > h1:first-child{margin-top:space-4;margin-bottom:space-2}` | 封面標題特殊塊（`:first-child` 不被 `*+*` 命中、但須與模型相容） |
| `static/index.html` L930-935 | `.katex-display{margin:space-2 0}` | 特殊塊自帶 margin → C2 須明列 margin-top |
| `static/index.html` `.paper-header-meta`/`.paper-dynamic-meta` | 學術扉頁/動態 meta，自帶 margin+flex | 特殊塊、非 markdown flow；C2 須排除或明列 |
| `static/themes/{kahn,kandinsky,mies,nara}.css` | 各設 `#paper-content p{margin-bottom:space-4}`、`h1{margin-bottom:space-4/5}`、`h2{margin:space-6 0 space-3 + border + padding}`、`h3{margin:space-5 0 space-2}` | 間距與外觀混在主題 → C2 移除垂直 margin（保 border/padding/色票/字族），間距移交 base |

> 主題間距一致性（grep 實證）：四主題 p `margin-bottom:space-4`、h2 `margin:space-6 0 space-3`、h3 `margin:space-5 0 space-2` 完全一致；h1 僅 kahn `space-4`、餘三 `space-5`。

---

## §3 觀察問題

### 問題 #1：清單「前寬後窄」單向黑洞
- **證據**：`static/index.html:83`（reset 歸零 ul/ol margin）+ 主題 `#paper-content p{margin-bottom}`（無 margin-top）
- **影響**：清單前有間距（吃前段 mb）、後無間距（自身 0、後段無 mt）→ 節奏不對稱（FE-RHYTHM-1 點補 p↔list）

### 問題 #2：連續標題間距過寬（標題離自己內文太遠）
- **證據**：B 軌 shadow `### 引擎 1 · 守護`(h3) + `### 傳統機上盒`(h3) 連續；h3 `margin-top:space-5` → 兩標題間距 space-5（過寬）
- **影響**：section 標題與其子標題隔太開（baron 引擎頁觀察）

### 問題 #3：同視覺兩節奏機制
- **證據**：「區段標籤+清單」——施肥頁 `施肥：…`(純段落 p→list、走 FE-RHYTHM-1) vs 引擎頁 `### 引擎`(h→h、未治)
- **影響**：Vision 措辭決定走哪條節奏路徑、節奏不一致；打地鼠不止

---

## §4 設計方案

### §4.1 C1 — Spike & 模型凍結
worktree 拋棄式 HTML harness，餵真實三軌片段（履歷小標+條列 / 論文段落+清單+連續標題 h2→h3 / 簡報施肥頁 p→list + 引擎頁 h→h），套 plan §9.1 凍結候選模型，肉眼比對。**驗 3 假設**：① 閱讀視圖塊級為 `#paper-content` 直接子代（檢視真實 reading-view DOM：marked 輸出 + `.slide-head`/`.paper-header-meta` 等 wrapper）② 巢狀清單（`li` 內、非直接子代）不被 `>*+*` 誤撐 ③ Dia/Safari 渲染 `:is`/`:not`/`+`。**凍結產出**：確切 token（基準流 space-4 / 非標題→標題 space-6 / 標題→* space-2 / p→清單 space-1）+ 特殊塊（`.slide-head`/`.katex-display`/`h1:first-child`/`.paper-header-meta`/`.paper-dynamic-meta`/`.figure`）的 margin-top 明列清單。零 production diff、產 spike 報告（baton）。

### §4.2 C2 — 統一垂直節奏模型落地（atomic）
**單一 commit 原子替換**（避免破中間態，見 §5 風險 #1）：
- **index.html base**：移除 FE-RHYTHM-1 兩條 :has（L915-922）；新增統一模型（4 條 flow + 特殊塊 margin-top 明列，依 C1 凍結）。
- **4 主題**：移除 `#paper-content p`/`h1`/`h2`/`h3` 之垂直 margin（保留 border-bottom/padding-bottom/色票/字族/字級）。
- 包裹 `/* === [FE-RHYTHM-UNIFY C2 START/END] === */`（index.html）+ 主題各以註解標記移除處。

### §4.3 C3 — Checkout 收官
Conformance（目標規格 plan §2 / §6 grep / 不可動 / 提示詞稽核 / §8.2 三軌×四主題 E2E 列 baron 運維）+ baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| **#1 模型替換非原子 → 破中間態** | 🔴 高 | base 先加 flow 而主題仍有 margin-bottom → **雙倍間距**；先清主題而 base 未加 flow → **零間距**。**故 C2 必須 atomic**（model + 主題清理同 commit）。⚠️ **與 plan Q2「主題清理拆獨立 commit」張力**——拆分產生破中間態（非 git 安全的可獨立測試狀態），故本 tasks 採 atomic；若 baron 仍欲拆，須接受中間態視覺破版（仍 git 可逆）。見 §9 Q-A。 |
| **#2 `>*+*` 直接子代假設不成立** | 🟡 中 | C1 spike 先驗真實 reading-view DOM；若有非預期 wrapper（如 marked 包 `<p><img>`）則調整選擇器或納特殊塊。 |
| **#3 特殊塊 margin 雙重疊加** | 🟡 中 | C1 凍結特殊塊清單（.slide-head/.katex-display/h1:first-child/.paper-header-meta/.figure）；C2 為其明列 margin-top（reset flow 疊加）。 |
| **#4 supersede 已 ship FE-RHYTHM-1 殘留** | 🟡 中 | C2 同 commit 移除其兩條 :has + START/END 包裹；§6 grep 驗 0 殘留。 |
| **#5 全文體×四主題回歸** | 🟡 中 | §8.2 三軌（履歷/論文/簡報）× 四主題矩陣 E2E（baron 運維）；C2 .bak 五份可逆。 |
| **#6 chat 誤波及** | 🟢 低 | 選擇器限 `#paper-content`、chat 走 `.msg-ai`；§6 grep 確認。 |

---

## §6 測試計畫

### §6.1 C1 驗收（spike）
```bash
# spike 報告存在且記載三假設結論 + 凍結 token/特殊塊
ls -la .claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_C1_執行.md
grep -nE "直接子代|巢狀清單|Dia|space-4|space-6|space-2|space-1|slide-head|katex-display" .claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_C1_執行.md
# 零 production diff
git status -s static/   # 期望：無 static/ 變更
```

### §6.2 C2 驗收
```bash
cd .claude/worktrees/hopeful-yalow-902c50
# (1) FE-RHYTHM-1 兩條 :has 已移除（0 命中）
grep -nE "p:has\(\+ ul\)|ul:has\(\+ p\)" static/index.html   # 期望：0 命中
# (2) 統一模型 4 條存在
grep -nE "FE-RHYTHM-UNIFY C2|> \* \+ \*|:not\(:is\(h1,h2,h3,h4\)\) \+ :is|:is\(h1,h2,h3,h4\) \+ \*|p \+ :is\(ul,ol\)" static/index.html   # 期望：模型規則命中
# (3) 完全無 :has（消滅）
grep -nc ":has(" static/index.html   # 期望：0（或僅非節奏既有用途、C1 確認）
# (4) 四主題垂直 margin 已移除（p margin-bottom / h margin 0 命中）
for f in static/themes/*.css; do echo "--- $f ---"; grep -nE "#paper-content p \{" -A4 "$f" | grep "margin"; done   # 期望：p 無 margin-bottom
# (5) 主題 border/padding 保留（h2 border-bottom 仍在）
grep -nE "border-bottom" static/themes/kahn.css   # 期望：h2 border-bottom 仍命中
# (6) chat 未波及（.msg-ai 不在本次 diff）
git diff --stat   # 期望：僅 index.html + 4 themes
# (7) 全套件綠（純 CSS、零 .py）
venv/bin/python -m pytest -q   # 期望：與基線一致（僅既存 env flake）
```

### §6.3 C3 驗收
```bash
grep -rn "FE-RHYTHM-UNIFY" .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/   # baton 已歸檔
git status -s   # 期望：歸檔後乾淨
```

---

## §7 不可動清單

- [ ] **後端 / pipeline / RAG / final_zh 產物** — 100% 不動（純前端 CSS）。
- [ ] **內容正規化層**：`_promote_subheadings`/`_normalize_paragraph_breaks`/`_tighten_point_groups`(3c)/`_render_inline_bold`+`_strip_bare_url_lines`(3d) — markdown 層、正交、不動。
- [ ] **HOTFIX-3b 清單 `padding-left:1.5em`** / **HOTFIX-3 `.slide-head` border** / **RAG-12 `.katex-display` overflow/padding** 之**非垂直間距**屬性 — 保留。
- [ ] **主題色票 / 字族 / 字級 / border / padding-bottom（h2 底線）** — 保留（只移垂直 margin）。
- [ ] **chat `.msg-ai`** — 不在選擇器範圍、不動。
- [ ] **`#paper-content{margin:0 auto}`（水平置中）** — 非垂直節奏、不動。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — Spike & 模型凍結（垂直節奏 spike）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 無 production 檔案（worktree 拋棄式 HTML harness、不入版控）；產出 spike 報告 → `baton/2026-06-13_FE-RHYTHM-UNIFY_C1_執行.md`（暫存、Check 才歸檔） |
| **安全性** | 🟢 高 — 零 production diff、純驗證 |
| **可逆性** | 🟢 高 — 無 production 變更、harness 刪除即可 |
| **驗收 grep 條件** | §6.1（spike 報告存在 + 記載三假設結論與凍結值；`git status -s static/` 無變更） |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1. worktree 內建最小 HTML（內嵌 base reset L83 + plan §9.1 候選 4 條 flow + 一主題色票），餵三軌片段：① 履歷小標+條列 ② 論文 `<p>…</p><ul>…</ul>` + 連續 `<h2>`+`<h3>` ③ 簡報施肥頁（`<p>施肥：</p><ul>`）+ 引擎頁（連續 `<h3>`）。2. 開瀏覽器（Dia/Safari）肉眼驗：標題貼內文、標籤貼清單、非標題→標題大留白、清單→下段留白、巢狀清單未誤撐。3. 檢視**真實 reading-view DOM**（既有上傳文件、開發者工具）確認 `#paper-content` 直接子代結構（marked 輸出 + `.slide-head`/`.paper-header-meta`/`<p><img>` 等 wrapper 是否直接子代）。4. **凍結並寫入報告**：確切 token（4/6/2/1）、特殊塊 margin-top 明列清單（`.slide-head`/`.katex-display`/`h1:first-child`/`.paper-header-meta`/`.paper-dynamic-meta`/`.figure` 各自處理）、選擇器最終形（含 `:not(:is(h…))+:is(h…)` 與 `:is(h…)+*` 互斥確認）、`:has` 是否完全消滅。5. 刪除 harness。**零 production 改動**。 |

### C2 — 統一垂直節奏模型落地（atomic 模型替換）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（base：移除 FE-RHYTHM-1 兩條 :has〔L915-922〕+ 新增統一模型）/ `static/themes/kahn.css`·`kandinsky.css`·`mies.css`·`nara.css`（各移除 `#paper-content p/h1/h2/h3` 垂直 margin）；**5 檔 + 5 `.bak`**（`.claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_<檔名>.bak`，git add 清單含 .bak）|
| **安全性** | 🟡 中 — 動全文體×四主題閱讀視圖間距；純 CSS、零 runtime/後端；.bak 可逆 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾（5 檔同 commit、原子）|
| **驗收 grep 條件** | §6.2（FE-RHYTHM-1 0 命中 / 模型 4 條命中 / :has 消滅 / 主題 p margin-bottom 移除 / border 保留 / diff 僅 5 檔 / pytest 綠）|
| **依賴關係** | 前置 C1（凍結 token + 特殊塊清單 + 三假設確認）|
| **具體實作細節** | **index.html**：(a) 在 `=== [FE-RHYTHM-1 START] === … END ===` 區塊內移除兩條 `p:has(+ul/ol){margin-bottom:space-1}` + `ul/ol:has(+p){margin-bottom:space-4}`（連註解整塊刪）。(b) 新增 `=== [FE-RHYTHM-UNIFY C2 START] ===` 區塊含 plan §9.1 四條：`#paper-content > * + * {margin-top:var(--space-4)}` / `#paper-content > :not(:is(h1,h2,h3,h4)) + :is(h1,h2,h3,h4) {margin-top:var(--space-6)}` / `#paper-content > :is(h1,h2,h3,h4) + * {margin-top:var(--space-2)}` / `#paper-content > p + :is(ul,ol) {margin-top:var(--space-1)}`；緊接特殊塊 margin-top 明列（依 C1 凍結，如 `.slide-head`/`.katex-display`/`.paper-header-meta` 重置或保留其既有 margin、防 flow 疊加）。(c) 確認塊級 margin-bottom 為 0（L83 reset 提供、主題清理後不再加回）。**4 主題各檔**：移除 `#paper-content p{margin-bottom:…}` 整條 margin、`#paper-content h1{margin-bottom:…}`、`#paper-content h2{margin:…}`（**僅移 margin、保留 border-bottom + padding-bottom**）、`#paper-content h3{margin:…}`；以註解標記移除處（如 `/* FE-RHYTHM-UNIFY：垂直 margin 移交 base */`）。**不動**主題色票/字族/字級/border/padding。 |

### C3 — Checkout 收官（驗收歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（FE-RHYTHM-UNIFY → ✅ 完成）；baton 一次性 `mv` 歸檔（plan v1 → `plans/`、tasks → `tasks/`、C1-C3 報告 + spike 報告 → `executions/`）|
| **安全性** | 🟢 高 — 純文件歸檔 / 狀態更新 |
| **可逆性** | 🟢 高 — 文件操作可逆 |
| **驗收 grep 條件** | §6.3（baton 歸檔至正式目錄 + git status 乾淨）|
| **依賴關係** | 前置 C1、C2 全部 ship |
| **具體實作細節** | 1. Conformance 五維度：① 目標規格（plan §2 U1-U10）② §6 grep 全綠 + 全套件 pytest 綠 ③ 不可動清單 git diff（僅 index.html+4 themes、零 .py）④ 提示詞稽核（plan/tasks/C1-C2 run + Check）⑤ **§8.2 三軌×四主題 E2E 列 baron 運維**（CSS 視覺、無法 headless；§7.2 整合：無跨 Phase code handoff → 不適用、以 E2E 為主軸）。2. baton 一次性 `mv` + `git add`（plan/tasks/執行報告/spike 報告 + 5 .bak）。3. TODO 結案（active 移除 → ✅ 完成表，hash 待 baron 回填）+ §99.2 / INDEX 補 Check 提示詞。4. git log hash 自癒回填既有條目。 |

---

## §9 Open Questions

> plan 階段九 OQ 已全 🟢 定案（見 plan §9）。本 tasks 階段一項執行期抉擇已 🟢 baron 拍板：

| 開放問題 | 定案 | 理由 |
|---|---|---|
| **Q-A** C2 是否 atomic（model + 主題清理同 commit），還是依 plan Q2 拆「主題清理」獨立 commit？ | **🟢 定案（baron 拍板）：atomic（C2 單一 commit 同步替換模型與清理主題）；否定「拆獨立 commit」** | ① **防止提交已知破損狀態**——拆分必在 git 歷史留「雙倍超寬」或「零間距黏字」破版中間節點、違 WORKFLOW_SOP「commit 須語意完整可獨立測試」。② **保證可逆**——單 commit `git revert C2` 一步乾淨還原 5 檔；拆兩 commit 回滾易部分回滾致破版。③ **符合備份鐵律**——C2 同 commit 為 5 檔各產 `.bak` 納入 git add、審計鏈完整。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-RHYTHM-UNIFY 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8（設計脈絡權威源為 plan §9.1 凍結模型）|
| **引用方** | 後續 FE-RHYTHM-UNIFY executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼 / 後端 / pipeline；嚴禁動內容正規化層（3c/3d/promote）；嚴禁自動 git commit/push；baton 一律 Check 才歸檔 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正（尤 §9 Q-A）|
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計模型唯一源在 plan §9.1；節奏統一原則不在此重寫 |

### §99.2 Revision 歷程

- v2 (2026-06-13)：§9 Q-A baron 拍板 🟢 定案——C2 採 **atomic**（單一 commit 同步替換模型 + 清理主題、否定拆獨立 commit；理由：防已知破損中間態 / 保證 `git revert C2` 一步可逆 / 5 .bak 審計鏈完整）；C1-C3 結構不變
- v1 (2026-06-13)：初版拆分完成（3 commit：C1 Spike & 模型凍結 / C2 統一垂直節奏模型落地·atomic / C3 Checkout；§9 Q-A 提出 atomic vs 拆主題清理之執行期抉擇〔證據：拆分破中間態〕待 baron 拍板）
