# THEME-DEDUP 主題規格凍結與結構去重 — Tasks

> 本文件為 THEME-DEDUP 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md`（v7·全 13 OQ 定案）產出，含 **6 個 Commit**（C0 Baseline → C1–C4 → checkout）。
>
> ⚠️ **工作目錄 deviation**：Tasks 提示詞稱唯一合法目錄為 worktree `hopeful-yalow-902c50`——該 worktree 已刪除；依 `CLAUDE.md §3`（CONTEXT-1 C2 v5）於**主 repo 就地**執行（RESCUE-1 C1 先例）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `design/docs/theme-template.css`（統一骨架模板）/ `.claude-logs/tools/check_css_governance.py`（常駐契約檢查·純標準庫） |
| **新增追蹤** | 5 個 | `static/themes/{apple,corbusier,fuller,google,gropius}.css`（C0 原樣入版控） |
| **修改檔案** | 13 個 | `static/themes/*.css` ×9（正規化）/ `static/css/globals.css`（+7 token）/ `static/css/content.css`（base 承接）/ `design/docs/theme-guide.md`（凍結規格重寫）/ `design/docs/css-architecture.md`（對照表+登記） |
| **目錄定義** | 0 個 | `.claude-logs/tools/` 既存 |
| **狀態更新** | 2 個 | `TODO.md`（本 tasks 同步 🟡 WIP + 各 Run 更新）/ `prompts/INDEX.md` |
| **Commits** | 6 個 | C0 → C1 → C2 → C3 → C4 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` plan + tasks + C0–C4 執行報告（7 檔）→ `plans/`+`tasks/`+`executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：主題規格未凍結——9 支主題（4 內建 + 5 上傳）殘留非白名單結構屬性、上傳 5 支帶 `#demo-bar` 死碼與缺 `--content-max-w`、無權威規格致新主題必再現不一致（plan §1/§3）。
- **解法**：6 個原子 commit——`C0 — Theme Baseline（導入原始自訂主題）` 鎖基線 → `C1 — Token & Base Foundation（token 立基與 base 承接）` 零視覺變鋪底 → `C2 — Builtin Normalize（內建四支骨架重排與去結構）` + theme-guide 凍結規格重寫 → `C3 — Uploads Normalize（上傳五支正規化）` → `C4 — Template & Guard（統一模板與常駐契約腳本）` → `checkout — 成果收官歸檔（成果歸檔與移出暫存）`。
- **影響範圍**：100% FE-Refactor（CSS + design docs + tools 治理腳本）；零後端業務代碼、零 `static/index.html`、零 JS。
- **不可動清單**：見 §7。

---

## §2 現況

| 對象 | 現狀（plan §3 實測） | 待處理 |
|---|---|---|
| 上傳 5 支 | untracked；各帶 `#demo-bar` 死碼 4-6 條；token 18/19（缺 `--content-max-w`）；apple/google 另有 chrome 覆寫段 | C0 鎖基線 → C3 正規化 |
| 內建 4 支 | tracked（C3 `0fbafeb` 後）；token 19；結構屬性 9-11 行（h2 border/pc padding/figure/byline/figcaption/ph border） | C2 正規化 |
| `globals.css` | T1/T2/T3 三層分區（FE-CSS-GOV C4）；無 7 個異值結構 token | C1 +7（T3） |
| `content.css` | `#paper-content h2 {}` 空槽（有註）；`.figure`/`figcaption` 部分槽；無 `.byline` 規則 | C1 承接 |
| `theme-guide.md` | C3 版契約（白名單/carve-out/§8 方向）；無凍結骨架/26 token/兩槽 | C2/C3/C4 重寫 |
| `css-architecture.md` | §6 Token 歸屬 19+13；無「主題結構→base/token 對照表」 | C1/C3 補 |
| 模板 / 契約腳本 | 皆無 | C4 新建 |

---

## §3 觀察問題

- **#1 死碼再生產**：上傳 5 支全帶 `#demo-bar`（拷貝 C3 前舊樣板）——證「無凍結規格＋無乾淨模板 → 不一致自動再生產」（plan §3.0）。
- **#2 base 已預留槽**：`content.css` 之 h2/figure/figcaption 空槽（含「由主題控制」註）＝設計早預期 base 承接（plan §3.4）。
- **#3 重排安全**：9 支皆無重複選擇器（plan v5.1 實測）→ 骨架重排不翻轉 cascade。

---

## §4 設計方案

### §4.0 文獻/工具同步配套矩陣（每 commit 硬綁定）

| Commit | 同 commit 文獻/工具配套 |
|---|---|
| C0 | —（Baseline 鐵則：嚴禁任何修改、純 git add 原樣） |
| C1 | `css-architecture.md`：§6 Token 歸屬 +7（T3 主題覆寫面）+ 新增「主題結構→base/token 對照表」節 |
| C2 | `theme-guide.md`：**凍結規格重寫**（26 必備 token / 16 必備選擇器 + 統一骨架 9 段 / 屬性白名單含 text-align / 裝飾槽 + chrome 槽 / 禁止清單；§8 方向章收斂為正文） |
| C3 | `theme-guide.md`：補「自訂/上傳主題」章（unlayered 相容、chrome 槽用法、Q_chrome 建議 var 不強制）+ `css-architecture.md` build 狀態 |
| C4 | 模板+腳本本身即工具交付；`theme-guide.md` Step-by-step 改指模板（取代「拷貝 mies」）+ 腳本用法登記；**首次全綠輸出貼入 C4 執行報告**（工具 commit 伴首次測試報告） |
| checkout | 被修 docs 頂部同步戳統一更新 |

### §4.1 C0 — Theme Baseline（導入原始自訂主題）
5 支上傳原樣 `git add` 入版控（**嚴禁任何內容修改**·序位鐵則：任何正規化嚴禁先於本 commit）。

### §4.2 C1 — Token & Base Foundation（token 立基與 base 承接）
- `globals.css` T3 段 +7 token（default＝多數派值）：`--pc-pad: var(--space-6) var(--space-8)` / `--figure-margin-y: var(--space-6)` / `--byline-margin-b: var(--space-6)` / `--byline-pad-b: var(--space-2)` / `--byline-border-w: 1px` / `--figcaption-margin-t: var(--space-3)` / `--ph-border-w: 1px`。
- `content.css` base 承接（@layer components 內·填/新增規則讀 token）：h2 填槽（`border-bottom: var(--divider-w) solid var(--color-divider); padding-bottom: var(--space-2);`·Group B 同值直移）；`#paper-content { padding: var(--pc-pad); }`；`.figure { margin: var(--figure-margin-y) 0; }`；**新增** `.byline { margin-bottom: var(--byline-margin-b); padding-bottom: var(--byline-pad-b); border-bottom: var(--byline-border-w) solid var(--color-border-strong); }`；`figcaption { margin-top: var(--figcaption-margin-t); }`；`.ph { border: var(--ph-border-w) solid var(--color-divider); }`。
- **零視覺變保證**：9 支主題此時仍帶自身結構規則（unlayered 恆勝 base）→ base 新規則全被蓋、視覺零變。

### §4.3 C2 — Builtin Normalize（內建四支骨架重排與去結構）
- 4 支各：全檔重排 9 段骨架 → `:root` 補 7 token 覆寫值（各自原值，如 kahn `--pc-pad: var(--space-8)`、mies `--byline-border-w: 0`、kandinsky/nara `--ph-border-w: 2px`）→ 刪 15 內容選擇器上的結構屬性行 → 補裝飾槽（kahn 原 `::before` 入槽、其餘 3 支空規則）+ chrome 槽 marker（4 支皆空）→ 白名單色偏差以白名單屬性補（kandinsky `.byline { border-color: var(--color-divider) }`、kahn `.ph { border-color: var(--color-border-strong) }`）。
- Q3 例外保留：kahn figcaption `max-width/margin-inline`、mies `max-width: none`、kahn `.ph position: relative`。

### §4.4 C3 — Uploads Normalize（上傳五支正規化）
- 5 支各：清 `#demo-bar` 死碼（C3-內建同法·審計腳本+斷言）→ `:root` 補 `--content-max-w: 760px` + 7 token 覆寫（值＝各自 baseline 原結構值、run 期逐支 grep 對照）→ 骨架重排 + 兩槽 → 刪 15 內容選擇器結構屬性 → **apple/google chrome 覆寫內容整塊原序入槽 9（不改一字）**、其餘 3 支僅 marker。

### §4.5 C4 — Template & Guard（統一模板與常駐契約腳本）
- `design/docs/theme-template.css`：統一骨架 9 段 + 26 token 佔位 + 16 選擇器 + 兩空槽 + 逐段註解（模板自身須過腳本檢查）。
- `.claude-logs/tools/check_css_governance.py`：四類檢查（① 主檔系 unlayered=0/themes @layer=0 ② token 唯一定義於 globals ③ 9 主題骨架合規〔26 token+16 選擇器+2 槽 marker+內容選擇器白名單·Q3 例外表〕④ 死碼=0）；**純標準庫**（re/sys/pathlib/json）、退出碼 0/1+違規清單；可 `--file` 單檔模式。
- 首次全綠輸出貼 C4 執行報告。

### §4.6 checkout — 成果收官歸檔（成果歸檔與移出暫存）
Conformance（plan §2 目標全驗 + §6 重跑 + §7 不可動 + 提示詞稽核 + msg）→ baton 一次性歸檔（plan/tasks/C0–C4 報告）→ TODO 雙層結案 + hash 自癒 + staged 白名單自檢 + checkout 執行報告（executions/ 直產）。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C2/C3 視覺回歸（去結構後 base/token 值差） | 🟡 中 | token 值＝原值 byte 對照（.bak+baseline diff）；每 commit E2E×該批主題；C1 先鋪底零視覺變 |
| apple/google chrome 層誤傷 | 🟡 中 | 整塊原序入槽、不改一字；驗收＝槽內容 diff vs C0 baseline == 空 |
| 重排翻轉 cascade | 🟢 低 | 9 支無重複選擇器（已驗）；multiset 對帳每支 |
| 腳本誤報（Q3 例外/白名單邊界） | 🟢 低 | 例外表顯式編碼（figcaption max-width/margin-inline、ph position、裝飾槽幾何）；Q_hook 定不掛 hook、僅手跑 |
| baseline 序位破壞 | 🟢 低 | C0 首發鐵則；C3 依賴 C0（§8 依賴鏈） |

---

## §6 測試計畫

### §6.1 C0 驗收
```bash
git diff --cached --name-only            # 恰 5 檔（5 支上傳）
git diff --cached --stat | grep -c 'themes'  # 純新增、零修改行於既有 tracked 檔
```

### §6.2 C1 驗收
```bash
grep -c '\-\-pc-pad\|--figure-margin-y\|--byline-margin-b\|--byline-pad-b\|--byline-border-w\|--figcaption-margin-t\|--ph-border-w' static/css/globals.css   # 7 定義
grep -A3 '#paper-content h2 {' static/css/content.css | grep -c 'border-bottom\|padding-bottom'  # 2
grep -c '\.byline' static/css/content.css   # ≥1（新增規則）
# 主題零 diff：git diff --quiet static/themes/ → 通過（C1 不碰主題）
# E2E：任一主題視覺零變（unlayered 蓋 base）
```

### §6.3 C2 驗收（內建 4 支）
```bash
for f in kahn kandinsky mies nara; do
  # 26 token / 16 選擇器+2 槽 / 內容選擇器結構=0（Q3 例外除外）/ multiset 對帳 vs .bak
done
grep -c '26\|統一骨架\|chrome 覆寫層' design/docs/theme-guide.md   # 凍結規格重寫命中
```

### §6.4 C3 驗收（上傳 5 支）
```bash
grep -rc 'demo-bar' static/themes/ | grep -v ':0' | wc -l        # 0
for f in apple corbusier fuller google gropius; do <26 token/16+2/結構=0/token 值==baseline 原值>; done
# apple/google chrome 槽內容 diff vs C0 baseline == 空
```

### §6.5 C4 驗收
```bash
python3 .claude-logs/tools/check_css_governance.py               # 退出碼 0（9 支+模板全綠）
python3 -c "import ast;ast.parse(open('.claude-logs/tools/check_css_governance.py').read())"  # 語法
grep -c 'import' .claude-logs/tools/check_css_governance.py      # 僅標準庫（人工核 re/sys/pathlib/json）
grep -c 'theme-template' design/docs/theme-guide.md              # Step-by-step 指模板
```

### §6.6 checkout 驗收
staged 白名單自檢（`git diff --cached --name-only` == 宣告集合）+ baton 歸檔非破壞性 + TODO 雙層結案。

---

## §7 不可動清單

- [ ] **後端業務代碼**（`web_server.py`/`pipeline_core.py`/`processor/*` 等全部 `.py`·唯一例外＝新增 `tools/check_css_governance.py`）— 100% 不動
- [ ] **`static/index.html`** — 零觸（含 JS/DOM id/契約 class）
- [ ] **視覺值零改動** — 9 支 token/base 承接值 == 原值（byte 對照）
- [ ] **apple/google chrome 覆寫內容** — 不改一字、僅整塊入槽
- [ ] **裝飾例外**（kahn `.ph position`+`::before`、figcaption max-width/margin-inline）— 保留
- [ ] **themes unlayered**（嚴禁 `@layer`）/ **globals T1/T2 既有 token** / **content.css `.slide-head` override** — 不破壞
- [ ] **C0 baseline 原樣**（嚴禁夾任何修改）；baton 過程檔嚴禁 run 期 git add

---

## §8 推薦 Commit 拆分

### C0 — Theme Baseline（導入原始自訂主題）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/themes/{apple,corbusier,fuller,google,gropius}.css`（5·原樣新增追蹤；**無 .bak**——原樣即基線） |
| **安全性** | 🟢 高 — 純 git add、零內容改動、零 runtime 影響 |
| **可逆性** | 🟢 高 — `git revert` 即移除追蹤 |
| **驗收 grep 條件** | §6.1（staged 恰 5 檔、零既有檔修改） |
| **依賴關係** | 無前置（全案首發·序位鐵則） |
| **具體實作細節** | ① 確認 5 檔現況 md5 存檔於執行報告（基線指紋）② `git add` 逐檔 ③ msg 草稿 `/tmp/THEME-DEDUP_C0_msg.txt`（沿既備 baseline msg）④ 執行報告 `baton/2026-07-10_THEME-DEDUP_Baseline_C0_執行.md` |

### C1 — Token & Base Foundation（token 立基與 base 承接）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/css/globals.css` + `static/css/content.css` + `design/docs/css-architecture.md` + 3 `.bak`（archive/2026-07-10_THEME-DEDUP_C1_*.bak） |
| **安全性** | 🟢 高 — base 新規則全被主題 unlayered 蓋過、視覺零變（§4.2 保證）；純加法 |
| **可逆性** | 🟢 高 — `git revert` 完整回滾（主題未動） |
| **驗收 grep 條件** | §6.2（7 token 定義/h2 填槽/byline 新規則/主題零 diff/E2E 零變） |
| **依賴關係** | C0（序位；技術上獨立） |
| **具體實作細節** | ① 備份 3 檔 ② globals T3 段（`--content-max-w` 後）插 7 token+註「異值結構 token（THEME-DEDUP·主題覆寫）」③ content.css：h2 空槽填 2 行；`#paper-content`/`.figure`/`figcaption`/`.ph` 既有槽位（以錨文字定位·行號經 C5 已漂移）補讀-token 結構行；新增 `.byline` 規則（置 figure 前、@layer components 內）④ css-architecture §6 +7 列（T3）+ 新增「主題結構→base/token 對照表」節（7 token × base 規則 × 主題覆寫值矩陣）⑤ 驗收 §6.2 ⑥ 報告 `baton/…_Foundation_C1_執行.md` |

### C2 — Builtin Normalize（內建四支骨架重排與去結構）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/themes/{kahn,kandinsky,mies,nara}.css` + `design/docs/theme-guide.md` + 5 `.bak` |
| **安全性** | 🟡 中 — 主題行為改造；token 值==原值 + multiset 對帳 + E2E 四支把關 |
| **可逆性** | 🟢 高 — `git revert`；`.bak` 双保險 |
| **驗收 grep 條件** | §6.3（26/16+2/結構=0/multiset/theme-guide 凍結命中） |
| **依賴關係** | C1（base/token 必須先在、主題才能卸結構） |
| **具體實作細節** | ① 備份 5 檔 ② 腳本化重排：解析各主題規則 → 按 9 段骨架序重組（規則內容零改寫·multiset 斷言）③ `:root` 補 7 覆寫值（kahn `--pc-pad: var(--space-8)`/`--byline-pad-b: var(--space-3)`；mies `--figure-margin-y: var(--space-5)`/`--byline-margin-b: var(--space-5)`/`--byline-pad-b: 0`/`--byline-border-w: 0`/`--figcaption-margin-t: var(--space-2)`；kandinsky+nara `--ph-border-w: 2px`；其餘＝default 亦顯式寫滿 26）④ 刪結構行（h2 border/padding、pc padding、figure margin、byline 3 行、figcaption margin-top、ph border）⑤ 白名單色補償（kandinsky byline `border-color: var(--color-divider)`、kahn ph `border-color: var(--color-border-strong)`）⑥ 兩槽（kahn ::before 入槽、3 支空規則；chrome marker×4）⑦ theme-guide 凍結規格重寫（§4.0-C2）⑧ §6.3 + E2E×4 ⑨ 報告 `…_Builtin_C2_執行.md` |

### C3 — Uploads Normalize（上傳五支正規化）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/themes/{apple,corbusier,fuller,google,gropius}.css` + `design/docs/theme-guide.md` + `design/docs/css-architecture.md` + 7 `.bak` |
| **安全性** | 🟡 中 — 同 C2 手法（C2 先行驗證流程）；chrome 槽 diff==baseline 把關 |
| **可逆性** | 🟢 高 — `git revert` 回 C0 baseline；`.bak` 双保險 |
| **驗收 grep 條件** | §6.4（demo-bar=0/26/16+2/結構=0/chrome diff==空） |
| **依賴關係** | C0（baseline 對照源）+ C1（base/token）+ C2（流程與 theme-guide 規格先立） |
| **具體實作細節** | ① 備份 7 檔 ② 清 demo-bar（審計腳本+斷言·C3-內建同法）③ `:root` 補 `--content-max-w: 760px` + 7 覆寫（值＝run 期逐支 grep baseline 原結構值核定）④ 骨架重排+兩槽（apple/google chrome 段整塊原序入槽 9）⑤ 刪 15 內容選擇器結構行 ⑥ theme-guide 補自訂/上傳章（§4.0-C3）+ css-architecture build 狀態 ⑦ §6.4 + E2E×5 ⑧ 報告 `…_Uploads_C3_執行.md` |

### C4 — Template & Guard（統一模板與常駐契約腳本）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `design/docs/theme-template.css`（新）+ `.claude-logs/tools/check_css_governance.py`（新）+ `design/docs/theme-guide.md` + `design/docs/css-architecture.md` + 2 `.bak`（theme-guide/css-architecture） |
| **安全性** | 🟢 高 — 新檔 + docs；模板不入 static/themes/（不進下拉）；腳本唯讀檢查 |
| **可逆性** | 🟢 高 — `git revert` |
| **驗收 grep 條件** | §6.5（腳本退出碼 0 全綠/純標準庫/語法/Step-by-step 指模板） |
| **依賴關係** | C2+C3（9 支全 conformant 後腳本才可全綠） |
| **具體實作細節** | ① 備份 2 檔 ② 模板：統一骨架 9 段 + 26 token 佔位註解 + 16 選擇器 + 兩空槽 + 逐段用途註解 ③ 腳本：四類檢查 + Q3 例外表 + `--file` 模式 + 退出碼/違規清單（純 re/sys/pathlib/json）④ 首跑全綠輸出貼報告 ⑤ theme-guide Step-by-step 改指模板 + 腳本用法登記 ⑥ §6.5 ⑦ 報告 `…_Guard_C4_執行.md` |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | TODO.md / archive/TODO_done_archive.md / prompts/INDEX.md / prompts 歸檔 ×N / plans+tasks+executions 歸檔檔（baton mv 而來·**唯此階段可入 git**） |
| **安全性** | 🟢 高 — 純治理歸檔 |
| **可逆性** | 🟢 高 — `git revert` |
| **驗收 grep 條件** | §6.6（staged 白名單自檢 == 宣告集合） |
| **依賴關係** | C0–C4 全部 ship |
| **具體實作細節** | Conformance 驗收（plan §2 全目標 + §6 重跑 + §7 不可動 + 提示詞稽核 + msg）→ baton 一次性 mv（plan/tasks/C0–C4 報告 7 檔·非破壞性檢查）→ TODO 雙層結案 + hash 自癒 → checkout 執行報告直產 executions/（含 staged 自檢輸出）→ §8 一行 commit 指令 |

---

## §9 Open Questions

無。（plan v7 全 13 OQ 已定案結清。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 THEME-DEDUP 的原子 Commit 拆分清單與實作細節，作為執行期唯一指針 |
| **用途** | 供 baron 審查並按 Commit 序號逐一觸發執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 THEME-DEDUP executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動後端業務代碼（例外＝tools/ 檢查腳本）；嚴禁 `static/index.html`；C0 嚴禁夾修改；嚴禁自動 `git commit`/`git push`；baton 過程檔 run 期嚴禁 git add |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔、baron 同意移至 archive/ |
| **重複防護** | 凍結規格內容唯一源 plan §2.2（落地後 theme-guide.md）；本檔僅拆分與驗收 |

### §99.2 Revision 歷程

- v1 (2026-07-10)：初版拆分——6 commits（C0 Baseline〔序位鐵則〕→ C1 零視覺變鋪底 → C2 內建+凍結規格 → C3 上傳+chrome 槽 → C4 模板+腳本〔首綠報告〕→ checkout）；文獻/工具逐 commit 硬綁定（§4.0）；工作目錄 deviation 記載（stale worktree → 主 repo 就地）
