# BRAINSTORM-1 brainstorming 問答與視覺伴讀 vendoring plan

> 將 superpowers 的 brainstorming skill（蘇格拉底式問答 + 視覺伴讀畫圖）以「不裝 plugin、只 vendor 檔案」方式落地 `.claude-logs/`，改寫落點/溯源/護欄貼合本專案治理，產出設計 spec 作為既有 audit-doc 式原料餵入階段 1 plan。純新增治理文件 + 工具腳本，零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：想在「設計/功能發想」階段用 superpowers `brainstorming` 的蘇格拉底式問答（含視覺伴讀畫 mockup/diagram），但**整包裝 plugin** 有五個治理衝突：① marketplace 只給整包 → 拉進 14 個會自動觸發的 skill；② 預設落點 `docs/superpowers/specs/` 撞 CLAUDE.md §3；③ 產完 spec 自動 `git commit` 撞 §1.3（Claude Code 不 commit）；④ 遙測預設開，設計構想有外送疑慮（§1.8）；⑤ `.claude/` 不入版控 → 各環境各裝。而真正想要的只有「問答紀律 + 畫圖 + 一份設計文件」。
- **解法**：**不裝 plugin，改 vendor**。把 `brainstorming` 的問答骨架 + 視覺伴讀整套（`scripts/` + `visual-companion.md`）抽進 `.claude-logs/`，落點/命名/溯源/護欄**寫死**成本專案規範（不再靠每次 prompt 軟 override）；auto-commit 步驟移除（交 baron 手動）。產出 spec 定位為既有 `_audit.md` 式**原料**，餵入階段 1 `template_plan`。
- **影響**：純新增 `sop/` 一份作業 SOP + `tools/` 五個 vendored 腳本；**零業務代碼**（不觸 §3 不可動清單）；無 runtime / DB Schema / API 簽名 影響；不動 `.gitignore`（`tools/` 已入版控、`baton/*` 已排除，二選擇天然吻合）。

---

## §2 目標規格

本任務完成後須達到以下可檢驗最終狀態：

> **路徑防呆鐵律（baron review #1）**：本 plan 與後續 SOP 內所有路徑一律寫**完整根路徑** `.claude-logs/sop/`、`.claude-logs/tools/`、`.claude-logs/baton/`，**嚴禁**簡寫 `sop/` / `tools/`（防 AI 誤在專案根目錄新建同名夾）。

1. **新建作業 SOP**：`.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md`，內容含：
   - (a) 問答流程骨架（探索 context → 逐一澄清問題〔一次一題、優先選擇題〕→ 提 2-3 方案權衡 → 分段核准 → 產 spec → 自檢）
   - (b) **落點規範**：spec 落 `.claude-logs/baton/<YYYY-MM-DD>_<任務編碼>_design_spec.md`（禁 `docs/superpowers/`）
   - (c) **溯源 header 樣板**（滿足 baton README §2 Phase 2 Provenance 自檢：產出工具/時間/session 或參考來源）
   - (d) **spec → `template_plan` 欄位對照表**（明列 spec 只覆蓋 §2 目標規格 + 半個 §9 OQ；§3 grep 證據 / §4 接縫契約 / §6 不可動清單 / §8 驗證計畫**仍須在階段 1 手工長出**）
   - (e) **兩條護欄**：① 原料 ≠ plan（四樣嚴謹層留階段 1 凍結）；② 原料必帶溯源 header
   - (f) 視覺伴讀啟用/停用指引 + Node≥12 前置聲明 + mockup 落點
2. **vendored 視覺伴讀腳本**入 `.claude-logs/tools/`（入版控）：`server.cjs`（零 npm 相依）、`start-server.sh`、`stop-server.sh`、`helper.js`、`frame-template.html`；`visual-companion.md` 指引**獨立存** `.claude-logs/sop/` 作附件（Q7 拍板）、SOP 正文引用。
3. **路徑接線改寫（baron review #2·強化為 server.cjs 零編輯）**：
   - `visual-companion.md` / SOP 內所有 `scripts/xxx` 相對引用改指 `.claude-logs/tools/xxx`。
   - mockup HTML 輸出改導**僅改 `.claude-logs/tools/start-server.sh` 內 bash 的 `SESSION_DIR` 組裝**——由 `${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}` 改為 `.claude-logs/baton/.brainstorm/${SESSION_ID}`，再經既有 `BRAINSTORM_DIR` env 傳入 node。
   - **`server.cjs` 完全零編輯**：它只消費 `BRAINSTORM_DIR` env（`content`/`state` 子路徑在 session 夾內部，無關落點）→ 改導不觸 server 業務邏輯、自足性零損（§3 已附源碼證據）。
   - `baton/*` 已 gitignored、mockup 自動不入版控。
4. **移除 auto-commit**：SOP 明載「產出 spec 後不 commit，交 baron 手動」（對齊 §1.3）。
5. **畫圖行為等價**：`server.cjs` / `helper.js` 業務邏輯**零改**（僅路徑接線），視覺伴讀點選 → events 檔 → agent 讀回之迴路與原版一致。
6. **來源可追溯**：SOP header 記錄 vendored 自 `obra/superpowers@<commit>` 之來源版本，供日後 pull-diff 同步。

### §2.5 候選方案（Diverse Rollout）

本任務涉及「引入外部方法論組件」之架構級決策，列二語意分散候選：

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| 方案 A（選定）**Vendor 檔案** | 不裝 plugin，抽 `brainstorming` SKILL + 視覺伴讀腳本進 `.claude-logs/`，落點/護欄寫死本專案規範 | ✅ 落點硬改零軟 override / 零 14-skill 污染 / 零遙測 / 各環境隨 git 同步 / 畫圖照樣保留（腳本自足可搬運）。❌ 需手動追上游更新（緩解：header 記來源 commit） |
| 方案 B（否決）**裝 plugin** | `/plugin install superpowers@…` 整包裝，靠 prompt/preference 軟 override 落點、靠 hook 擋 commit | ❌ 拉 14 個自動觸發 skill 且會鏈式外推 execution 鏈 / 落點·commit 每次靠紀律攔 / 遙測外送 / `.claude/` 不入版控致各環境各裝。✅ 隨上游自動更新 |

- **選定理由**：baron 只要「單獨、手動」用問答 + 畫圖；vendor 把治理衝突從「每次執行期政策化攔截」降為「一次性寫死」，且畫圖經查為自足可搬運（§3 證據），無損失。
- **否決留痕**：方案 B 之「隨上游自動更新」在本專案 2 人 / 嚴治理情境下，價值遠低於其帶來的自動觸發污染與落點失控成本。

---

## §3 現況與證據

- **`.gitignore`**：L179 明宣「`.claude-logs/` 不排除任何檔案」，僅 L183-196 具名排除 `logseq/ pages/ journals/ baton/* _phase_4_7e_outputs/`（`baton/` 僅 README 例外）→ `tools/` 新檔天然入版控、`baton/` 新檔天然排除，吻合 baron 二選擇、**零 gitignore 改動**。
- **`.claude-logs/tools/`**：已入版控且含 5 檔（hook 腳本等）→ vendored 腳本並列即入版控，比照 WORKFLOW-5 治理 hook 前例。
- **superpowers 來源檔**（`obra/superpowers@HEAD` git tree 實查）：`skills/brainstorming/SKILL.md`、`visual-companion.md`、`scripts/{server.cjs,start-server.sh,stop-server.sh,helper.js,frame-template.html}`。
- **視覺伴讀自足性**（可搬運關鍵證據）：`server.cjs` 所有 `require` 皆 Node 內建（crypto/http/fs/path/os/child_process）→ 零 npm install；`helper.js` 靠 `window.location.host` 動態解析、零硬編路徑 → 複製到任何 repo 可跑；回饋走檔案系統（點選寫 `state_dir/events`、agent 下輪讀回）→ 不綁 plugin 機制；唯一耦合＝ `visual-companion.md` 內 `scripts/xxx` **相對路徑**，vendor 時一併改指即可。
- **輸出目錄由外部注入（server.cjs 零編輯之源碼證據）**：`server.cjs` 以 `const SESSION_DIR = process.env.BRAINSTORM_DIR || '/tmp/brainstorm'` 讀環境變數決定根目錄，`content`/`state` 僅為其下固定子夾；`start-server.sh` 於 bash 端組 `SESSION_DIR="${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}"` 後以 `env BRAINSTORM_DIR="$SESSION_DIR" … node server.cjs` 傳入 → **落點完全由 `start-server.sh` 掌控、改導不需碰 `server.cjs`**。
- **本機環境**：Node `v20.20.2` / npm `10.8.2` 已在（遠超 server 所需 Node≥12）。

### §3.1 grep 鋼鐵證據

```bash
$ grep -n "claude-logs" .gitignore
179:# .claude-logs/ 不排除任何檔案
183:.claude-logs/logseq/
184:.claude-logs/pages/
185:.claude-logs/journals/
186:.claude-logs/baton/*
187:!.claude-logs/baton/README.md
196:.claude-logs/_phase_4_7e_outputs/

$ git ls-files .claude-logs/tools/
.claude-logs/tools/check_css_governance.py
.claude-logs/tools/dirty_reset_guard.sh
.claude-logs/tools/pre_tool_guard.sh
.claude-logs/tools/settings.hooks.sample.json
.claude-logs/tools/test_hook_guards.sh

$ git check-ignore -v .claude-logs/tools/server.cjs
→ 不被 ignore（可入版控）

$ node --version
v20.20.2
```

---

## §4 跨 Phase 接縫契約

**無跨 Phase 資料 handoff**。視覺伴讀存在一條「agent 寫 HTML fragment → server → 使用者點選寫 `events` 檔 → agent 讀回」之迴路，但屬**單一工具內部 filesystem 迴路**，非跨 ≥2 Phase/模組之資料管線 producer/consumer。整合測試依 §7.2 於 §9 顯式申請豁免（純 DOC + tooling、無業務資料 handoff，對齊 WORKFLOW-5 前例）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 路徑接線錯 → 畫圖 server 起不來 | 🟡 中 | 落地後跑 smoke（`start-server.sh` → `curl` 首頁 → `stop-server.sh`）+ 手動開瀏覽器驗一次（§8.2） |
| vendored 腳本日後與上游 superpowers 分岔 | 🟢 低 | SOP header 記來源 commit；同步採手動 pull-diff、按需為之（不自動耦合） |
| 跨環境（Mac/GCP）Node 缺失 → 畫圖不可用 | 🟢 低 | SOP 標 Node≥12 前置；**問答主體零依賴**、畫圖為可選增強，缺 Node 只失去畫圖不阻斷發想 |
| mockup 檔干擾 baton「平時為空」原則 | 🟢 低 | mockup 落 `baton/.brainstorm/<session>/`、已 gitignored；SOP 規定 session 結束/Checkout 前清空 |
| SOP 進 `sop/` 但不入 `@path` 自動載入 | 🟢 低 | 依 §2.5 sop/ 為 workflow-gated、不污染 session context（對齊 CONTEXT-1 瘦身方向） |

---

## §6 不可動清單

- [ ] `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`（CLAUDE.md §3 業務代碼）**零改**
- [ ] 既有 `tools/` 5 腳本（`pre_tool_guard.sh` / `dirty_reset_guard.sh` / `test_hook_guards.sh` / `check_css_governance.py` / `settings.hooks.sample.json`）不動
- [ ] `.gitignore` 現有規則不動（二落點天然吻合、無需新增）
- [ ] CLAUDE.md §1–§5 / WORKFLOW_SOP §1–§7 核心規範本輪不改（是否登記 brainstorming 為正式前置 → §9 Q1 詢問，若採屬**另一 commit**）
- [ ] `server.cjs` / `helper.js` **完全零編輯**（含業務邏輯與路徑）；mockup 輸出改導僅發生於 `.claude-logs/tools/start-server.sh` 之 `SESSION_DIR`/`BRAINSTORM_DIR` 組裝（baron review #2）

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 文書類別（sop/ 歸屬） | `ref/WORKFLOW_SOP.md §2` |
| 跨 Phase 整合測試豁免 | `ref/WORKFLOW_SOP.md §7.2` |
| baton 溯源自檢（Provenance） | `.claude-logs/baton/README.md §2 Phase 2` + `§4 按需取用` |
| 不 commit / 工作目錄硬規則 | `CLAUDE.md §1.3 / §3` |
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| vendored 腳本入 tools/ 前例 | WORKFLOW-5（治理 hook 腳本版控於 tools/、baton README §3） |

---

## §8 驗證計畫

### §8.1 自動化測試

- **既有測試零回歸**：本任務零 `.py` 業務邏輯，`pytest tests/ -v` 全跑確認 748 綠燈基線不動（vendored 為 node/bash/md、不進 pytest 收集範圍）。
- **新增測試**：**不 vendor** superpowers 原 `tests/brainstorm-server/*.test.js`（node test、非 pytest，維護成本高）；改於 SOP 附一條**視覺伴讀 smoke 腳本**驗 server 健康（起→探→停）。是否採 → §9 Q2。

### §8.2 手動端到端（E2E）驗證流程

1. **純問答路**：跑一次 brainstorming 問答、全程拒絕視覺伴讀 → 驗 spec 落 `baton/<命名>`、含溯源 header、**未** git commit。
2. **視覺伴讀路**：跑一次接受畫圖 → `start-server.sh` 起本地 server → 瀏覽器開頁見 mockup → 點一個選項 → 驗 `events` 檔寫入 + agent 下輪讀回選擇 → `stop-server.sh` 收尾 → 驗 mockup 落 `baton/.brainstorm/` 且 `git status` 不顯示（gitignored）。
3. **接 plan 驗證**：拿路 1 的 spec，實走一次「原料 → `template_plan` 欄位對照」，確認四樣護欄欄位（grep 證據/接縫契約/不可動清單/驗證計畫）在階段 1 被要求補齊、非從 spec 繼承。

---

## §9 Open Questions

> **baron 拍板（2026-07-18）：Q1–Q7 全數採「推薦方案」定案**。以下表格保留供 tasks 階段引用。
>
> **歸檔命名更正（baron review #3）**：本 plan 於 Checkout 歸檔至 `plans/` 時，檔名更正為 `2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_plan.md`（去 "vendoring"、對齊 WORKFLOW_SOP §6 `<描述>_plan.md`）；baton 暫存期沿用現名不 mv（Run 階段嚴禁 mv，baton README §2 Phase 1）。

| 開放問題 | 推薦方案（＝baron 定案） | 推薦理由 |
|---|---|---|
| Q1 是否同步在 WORKFLOW_SOP / CLAUDE.md 登記 brainstorming 為正式「階段 0 前置」？ | **本輪只立 SOP，登記留下一輪（分開 commit）** | 最小可逆；先讓 SOP 落地 dogfood 幾次、確認流程順再入核心規範，避免一次改動核心 @path 鏈 |
| Q2 是否 vendor superpowers 原 node 測試？ | **否，改一條輕量 smoke** | 原測為 node test 非 pytest、維護成本高；smoke（起/探/停）已足顧畫圖回歸 |
| Q3 §7.2 跨 Phase 整合測試是否豁免？ | **豁免** | 純 DOC + tooling、無業務資料 handoff（§4 已析），對齊 WORKFLOW-5 / CONTEXT-1 純 DOC 豁免前例 |
| Q4 vendored 腳本與上游同步策略？ | **header 記來源 commit + 手動 pull-diff 按需** | 避免自動耦合；本專案重穩定 > 追新 |
| Q5 任務代號採 `BRAINSTORM-1`？ | **是** | 自描述、與既有 WORKFLOW-N/DOC-SYNC 風格一致（§5 新類型自然增長） |
| Q6 mockup 落點與清理時機？ | **`baton/.brainstorm/<session>/`、gitignored、Checkout 前清空** | 守 baton「平時為空」；gitignored 不污染版控 |
| Q7 `visual-companion.md` 併入 SOP 還是獨立存 sop/？ | **獨立存 `sop/` 作附件、SOP 正文引用** | 保持與上游對照方便日後 diff，SOP 正文不被冗長操作細節灌爆 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 BRAINSTORM-1 之目標規格：vendor brainstorming 問答 + 視覺伴讀進 `.claude-logs/`、改寫落點/溯源/護欄，作為 tasks 拆分與原子執行唯一基準 |
| **用途** | 供 baron 審查、tasks.md 拆分引用；Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 BRAINSTORM-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成、baron 同意後歸檔 archive/ |
| **重複防護** | 僅定義技術規格；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-07-18)：baron review 併入——#1 全路徑防呆鐵律（§2 頂 + 各處 `sop/`→`.claude-logs/sop/`、`tools/`→`.claude-logs/tools/`）/ #2 mockup 改導強化為 `server.cjs` 零編輯〔僅改 `start-server.sh` 之 `BRAINSTORM_DIR` 組裝、附源碼證據於 §3、收緊 §6〕/ #3 Checkout 歸檔檔名去 "vendoring"（§9 註）；§9 Q1–Q7 baron 拍板全採推薦、標定案；Q7 定案獨立存 `visual-companion.md`（§2.2）
- v1 (2026-07-18)：初版建立（DOC-Refactor；vendor 方案定案、baron 三落點拍板〔scripts→tools/入版控 / mockup→baton/ / SOP→sop/〕已納 §2）
