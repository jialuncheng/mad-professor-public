# DOC-SYNC-1 設計文件現況對齊 — Tasks

> 本文件為 DOC-SYNC-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_plan_v1.md`（內部 **v3**：六 OQ 定案 + Q6 規模釘死 + U1 tasks 階段勘誤〔dropdown-popup 誤判移除、msg 家族改判半實作〕）產出，含 **2 個 Commit（C1 → checkout）**。
> 工作流：DOC-Refactor。僅動 `design/docs/` 5 檔；`static/index.html` 唯讀對照（基準 `@8e5d1fa`）；零代碼。
> 工作目錄註：提示詞模板 worktree 路徑為殘留、依 `CLAUDE.md §3`（v5）主 repo 為準。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | 無 |
| **修改檔案** | 5 個 | `design/docs/components.md`（幽靈/半實作標註）/ `design/docs/dom-reference.md`（補 48 ID + 同步戳）/ `design/docs/{color-tokens,spacing,typography}.md`（頂部零差驗證戳各一行·Q3） |
| **目錄初始化** | 0 個 | 無 |
| **備份（.bak 鐵律）** | 5 份 | `archive/2026-07-09_DOC-SYNC-1_C1_<檔名>.md.bak`（C1 入 git） |
| **狀態更新** | 2 個 | `TODO.md`（🟡 WIP → checkout 雙層結案）/ `prompts/INDEX.md` |
| **Commits** | 2 個 | C1 → checkout |
| **baton 歸檔** | 1 次 | checkout：plan_v1 → `plans/`、tasks → `tasks/`、C1 報告 → `executions/` + 逐檔 git add；checkout 報告依鐵律直產 `executions/` |

---

## §1 TL;DR（概要）

- **挑戰**：design/docs 元件/DOM 記載層過時——components.md 把「未實作/半實作」寫成現況契約（AI 讀到會接不存在的線）、dom-reference 覆蓋率 36%（27/75 ID）。token 契約層實測零差、只缺「已驗證」留痕。
- **解法**（Q6 釘死 2 commits）：
  - **C1 — Docs Truth Sync（文件真值同步）**：components.md 5 個 class 兩款 in-place 標註（2 真幽靈「未實作」+ 3 半實作「注入未接」）+ dom-reference 依既有分區補 48 ID（輕量欄位、≤160 行）+ 兩檔同步戳 + token 三檔頂部零差驗證戳（5 檔一 commit）。
  - **checkout — 成果收官歸檔（成果歸檔與移出暫存）**：Conformance + 鐵律 checkout 報告 + baton 歸檔 + TODO 雙層結案。
- **影響範圍**：100% DOC；`.dropdown-popup` 經 v3 勘誤**零處置**（存活於 `:2241`/`:264`）。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 待處理 |
|---|---|---|
| `components.md`（最後更新 05-24） | L325-327/L334-335 `.title-meta(-sep)` 寫成現況（實為未實作：`renderTitleHeader:2748` 只建 zh/en/abstract、後端 0 命中）；L357-359 `.msg-ai-actions/.msg-copy/.msg-regen` 寫「hover 顯示」（實為半實作：CSS `:1063-1098`+委派 `:2405-2406`+匯出剝除 `:2411` 在、DOM 注入缺→現況不顯示） | U1 兩款標註 |
| `dom-reference.md`（06-13） | 記載 27 ID vs 實際 75；分區結構 §0–§6 完整、`#demo-bar`/`#doc-type-select` 已自帶對照標註 | U2 補 48、U3 戳 |
| token 三檔（05-24） | 實測零差（color 雙向 0、spacing/typography 值表符、theme 必供 19 全過） | Q3 頂部戳各一行 |

---

## §3 觀察問題

### 問題 #1：components.md 規劃寫成現況（毒性最高）
- **證據**：`design/docs/components.md#L357-L359`（msg 動作鈕「hover 顯示」）vs `index.html` 全檔無 DOM 注入點；`#L325-L327` title-meta vs `renderTitleHeader`（`:2748`）實建清單。
- **影響**：AI 依文件對 `.msg-copy` 接線／對 `.title-meta` 排版必落空。

### 問題 #2：dom-reference 覆蓋率 36%
- **證據**：`comm -13` 差集 48（modal 三件套家族/chat-input/theme 家族/tag 家族等）。
- **影響**：文件失去路由價值、AI 只能裸 grep。

### 問題 #3：token 層驗證成果無留痕
- **證據**：三檔無任何「最後對照」資訊；本次稽核成果若不落戳、未來必重複勞動。

---

## §4 設計方案

### §4.1 C1 — Docs Truth Sync（文件真值同步）

**(a) components.md 標註（U1·v3 對象）**——兩款固定措辭、in-place：
- 真幽靈（`.title-meta`/`.title-meta-sep`，L325-327 與 L334-335 兩處）：行內加 **「⚠️ 未實作（規劃保留、勿接線）」**。
- 半實作（`.msg-ai-actions`/`.msg-copy`/`.msg-regen`，L357-359 區塊）：區塊首加 **「⚠️ 半實作（樣式/事件委派已備〔`index.html:1063-1098`/`:2405-2406`〕、DOM 注入未接——現況 hover 不顯示；勿假設按鈕存在）」**。
- `.dropdown-popup`（L153/L209）：**零改動**（v3 勘誤：存活）。

**(b) dom-reference.md 補 48 ID（U2）**——輕量欄位（id｜區塊｜用途一句｜JS 綁定行號級），依既有分區歸組：

| 歸入既有分區 | 補入 ID |
|---|---|
| §1 根容器 | `app` |
| §2.1 左欄 h1 | `new-folder-btn`、`sidebar-toggle` |
| §2.2 中欄 toolbar | `lang-toggle`、`print-btn`、`edit-tags-btn` |
| §2.3 右欄 chat-header | `chat-header-actions`、`web-search-toggle`、`export-btn`、`chat-toggle` |
| §3.3 左欄底部 | `logout-btn`、`cleanup-btn` |
| §4 中欄內容 | `abstract-toolbar` |
| §5.2 輸入區 | `chat-input`、`hashtag-autocomplete` |
| §6 彈出層（**新增小節 §6.x「Modal 家族」**，六表） | help：`help-close-btn`、`help-title`；theme：`theme-box`、`theme-dropdown`、`theme-title`、`theme-ok-btn`、`theme-upload-btn`、`theme-upload-input`；tag：`tag-modal`、`tag-box`、`tag-input`、`tag-title`、`tag-save-btn`、`tag-cancel-btn`；confirm：`confirm-title`、`confirm-desc`、`confirm-ok-btn`、`confirm-cancel-btn`；action：`action-modal`、`action-box`、`action-title`、`action-body`、`action-ok`、`action-cancel`；notice：`notice-modal`、`notice-box`、`notice-title`、`notice-body`、`notice-ok`；prompt：`prompt-modal`、`prompt-box`、`prompt-title`、`prompt-body`、`prompt-input`、`prompt-ok`、`prompt-cancel` |
| §0/圖例後（雜項一行） | `theme-link`（head 主題 css `<link>`、JS 換膚切 href） |

（合計 48；各條目一行、不寫狀態矩陣；既有 27 條深度不溯及。）

**(c) 同步戳（U3）+ token 驗證戳（Q3）**：
- `components.md`/`dom-reference.md` 頂部 blockquote 加：「最後現況對照：2026-07-09、基準 `static/index.html@8e5d1fa`（DOC-SYNC-1）」。
- `color-tokens.md`/`spacing.md`/`typography.md` H1 下各加一行：「> ✅ 2026-07-09 實測零差：本檔約定與 `static/index.html@8e5d1fa` 逐項相符（DOC-SYNC-1 稽核戳、未改任何 token 內容）」。

### §4.2 checkout — 成果收官歸檔
Conformance（plan §2 U1–U5〔v3 版〕/ tasks §6 / §7 不可動 / 提示詞 4 份稽核 / msg 草稿）+ §7.2 顯式豁免（Q5）+ **checkout 報告直產 `executions/`**（含 staged 白名單自檢實貼）+ baton 歸檔（plan/tasks/C1 報告 3 檔）+ **TODO 雙層結案**（framework §2.5 v5）+ hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| 補記淪為深耕、超 160 行 | 🟡 中 | 輕量欄位固定四欄；Modal 家族以「每 modal 一表、每 id 一行」壓縮；§6.1 wc 驗 |
| 標註措辭不統一致 AI 誤讀 | 🟢 低 | 兩款措辭於 §4.1(a) 凍結逐字；§6.1 grep 驗每處帶「⚠️」 |
| 誤動 `.dropdown-popup` 相關行 | 🟢 低 | v3 明令零處置；§6.1 diff 驗該兩行零變 |
| 誤動 token 內容（非僅戳） | 🟢 低 | 三檔 diff 限「+1 行戳」；§6.1 驗 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
# U2 覆蓋率
comm -13 <(grep -oE '`#[a-z][a-z0-9-]+`' design/docs/dom-reference.md | tr -d '`#' | sort -u) \
         <(grep -oE 'id="[a-z][a-z0-9-]+"' static/index.html | sed 's/id="//;s/"//' | sort -u) | wc -l   # 期望 0
# U1 標註（每 class 每處出現皆帶 ⚠️；dropdown-popup 零變）
for c in title-meta title-meta-sep msg-ai-actions msg-copy msg-regen; do
  grep -n "$c" design/docs/components.md | grep -vc "⚠️"; done            # 每項期望 0
git diff design/docs/components.md | grep -c "dropdown-popup"            # 期望 0
# U3/Q3 戳記
grep -lc "8e5d1fa" design/docs/{components,dom-reference,color-tokens,spacing,typography}.md | wc -l  # 期望 5
# 膨脹上限 + 範圍
wc -l design/docs/dom-reference.md      # 增量 ≤ ~160（對照 .bak）
git -c core.quotepath=false diff --stat -- . ':!design' ':!.claude-logs'  # 期望空（零代碼）
```

### §6.2 checkout 驗收
```bash
git diff --cached --name-only    # ＝宣告白名單（5 檔+5 .bak 已於 C1；本 commit 歸檔+prompts+TODO+INDEX+archive+checkout 報告）
ls .claude-logs/baton/ | grep DOC-SYNC-1   # 期望：無
grep -n "DOC-SYNC-1" .claude-logs/TODO.md  # 一行索引+類別索引；archive/TODO_done_archive.md 完整表
```

---

## §7 不可動清單

- [ ] **一切代碼**：`*.py` / `static/*`（`index.html` 唯讀對照、零 byte 變動）。
- [ ] **`.dropdown-popup` 相關行**（components.md L153/L209）——v3 勘誤存活、零處置。
- [ ] **token 三檔內容**——僅頂部各 +1 行戳、token 定義零改。
- [ ] **`theme-guide.md`/`principles.md`/其餘 design/docs 5 檔**——整檔不動（deep-doc 歸 FE-CSS-GOV）。
- [ ] **既有 27 條 dom-reference 深度內容**——不重寫；`#demo-bar`/`#doc-type-select` 既有對照標註不動。
- [ ] **components.md 標註以外內容**——不動。
- [ ] **baton 長駐檔（兩 audit/PIPE-SPEC/QUEUE-1/PDF）**——不碰。
- [ ] **baton 暫存鐵律 / 收官 git-add 白名單鐵律**——依 WORKFLOW_SOP §3。

---

## §8 推薦 Commit 拆分

### C1 — Docs Truth Sync（文件真值同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 5 檔：`design/docs/components.md`、`design/docs/dom-reference.md`、`design/docs/color-tokens.md`、`design/docs/spacing.md`、`design/docs/typography.md`；備份 5 份 `archive/2026-07-09_DOC-SYNC-1_C1_<檔名>.md.bak`（入 git）。〔C1 執行報告暫存 baton、不入 git〕 |
| **安全性** | 🟢 高 — 純 `.md` 標註/補條目/戳記；零代碼。 |
| **可逆性** | 🟢 高 — `git revert C1`；5 .bak 可 `git show` 追溯。 |
| **驗收 grep 條件** | §6.1 全項。 |
| **依賴關係** | 無前置。 |
| **具體實作細節** | ① 5 檔各 `cp` → `archive/2026-07-09_DOC-SYNC-1_C1_<檔名>.md.bak`。② components.md：L325-327 與 L334-335 之 `.title-meta`/`.title-meta-sep` 每處行內加「⚠️ 未實作（規劃保留、勿接線）」；L357-359 區塊首加「⚠️ 半實作（樣式/事件委派已備〔`index.html:1063-1098`/`:2405-2406`〕、DOM 注入未接——現況 hover 不顯示；勿假設按鈕存在）」；**L153/L209 dropdown-popup 零碰**。③ dom-reference.md：依 §4.1(b) 歸組表補 48 條（每條一行：`#id`｜用途一句｜JS 綁定 `index.html` 行號級；Modal 家族新增 §6.x 六小表；`theme-link` 一行入雜項）；頂部加同步戳。④ components.md 頂部加同步戳。⑤ token 三檔 H1 下各 +1 行零差驗證戳（§4.1(c) 逐字）。⑥ 跑 §6.1 全項 + `wc -l` 對照 .bak 驗 ≤160 增量。git add（逐檔）：5 檔 + 5 .bak。 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`+逐檔 `git add`：plan_v1→`plans/`、tasks→`tasks/`、C1 報告→`executions/`；**直產** `executions/2026-07-09_DOC-SYNC-1_checkout_執行.md`（鐵律、入 git）；`TODO.md`+`archive/TODO_done_archive.md` 雙層結案；prompts 4 份（plan/Tasks/C1/Check）+ `INDEX.md` 入 git。 |
| **安全性** | 🟢 高 — 純歸檔+狀態。 |
| **可逆性** | 🟢 高 — mv 可逆、revert 可回。 |
| **驗收 grep 條件** | §6.2。 |
| **依賴關係** | 前置 C1 ship。 |
| **具體實作細節** | ① Conformance：plan §2 U1–U5（v3 版）逐項實檔複驗 + tasks §6.1 重跑 + §7 不可動 + 提示詞 4 份稽核 + msg 草稿。② §7.2 顯式豁免（Q5）。③ checkout 報告直產（Conformance + staged 白名單自檢實貼 + baton 歸檔確認 + §8 一行 commit）。④ baton 歸檔 3 檔。⑤ TODO 雙層結案（完整表→done_archive、TODO 一行索引、active 移除、類別索引；hash 自癒 C1）。⑥ staged 自檢：多/少一檔即停（他任務未追蹤檔嚴禁混入）。 |

---

## §9 Open Questions

無。（plan v3 §9 六 OQ 已定案〔§9.1〕；v3 勘誤僅修 U1 對象與措辭、Q1 處置形式不變。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 DOC-SYNC-1 原子 Commit 拆分與實作細節，作為執行期唯一指針 |
| **用途** | baron 審查後交 Claude Code 按序執行；階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 DOC-SYNC-1 executions/ 報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁動代碼；嚴禁越 plan U5 邊界深耕；嚴禁自動 git commit/push；git add 逐檔白名單 |
| **改版觸發條件** | plan 規格變動 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 收官歸檔後經 baron 同意移 archive/ |
| **重複防護** | 規格唯一源在 plan v3；本檔僅拆分與驗收指令 |

### §99.2 Revision 歷程

- v1 (2026-07-09)：初版拆分——依 plan v3（Q6 釘死 1 實作+1 checkout；U1 勘誤後對象＝2 真幽靈+3 半實作、dropdown-popup 零處置）拆 C1 Docs Truth Sync〔components 兩款標註 + dom-reference 48 ID 分區歸組表 + 同步戳×2 + token 零差戳×3、5 檔一 commit、5 .bak〕+ checkout〔鐵律報告+雙層結案〕。
