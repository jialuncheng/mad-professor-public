# BRAINSTORM-1 brainstorming 問答與視覺伴讀 — Tasks

> 本文件為 BRAINSTORM-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md`（v2）產出，含 3 個 Commit（C1 / C2 / Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 8 個 | `.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md`（作業 SOP）/ `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md`（視覺伴讀指引附件）/ `.claude-logs/tools/server.cjs` / `.claude-logs/tools/start-server.sh` / `.claude-logs/tools/stop-server.sh` / `.claude-logs/tools/helper.js` / `.claude-logs/tools/frame-template.html` / `.claude-logs/tools/test_brainstorm_server_smoke.sh`（smoke 驗證） |
| **修改檔案** | 0 個 | 全數為新增（vendored 自 superpowers）；無既有內容檔被改（故全程零 `.bak`） |
| **目錄初始化** | 1 個 | `.claude-logs/baton/.brainstorm/`（mockup 暫存·server 執行期建·`baton/*` 已 gitignored） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 3 個 | C1 → C2 → Checkout |
| **baton 歸檔** | 1 次 | Checkout 一次性：`mv` plan → `plans/` + tasks.md → `tasks/` + C1/C2 執行報告 → `executions/` + `git add`（逐檔） |

---

## §1 TL;DR（概要）

- **挑戰**：想在設計/功能發想階段用 superpowers `brainstorming` 的蘇格拉底式問答（含視覺伴讀畫圖），但整包裝 plugin 有五個治理衝突（14 skill 污染 / 落點撞 §3 / auto-commit 撞 §1.3 / 遙測 / 各環境各裝）。
- **解法**：不裝 plugin、改 **vendor**，把問答骨架 + 視覺伴讀整套抽進 `.claude-logs/`，落點/溯源/護欄寫死本專案規範。原子化拆為三 commit：
  - `C1 — Brainstorming SOP & Visual Companion（作業 SOP 與視覺伴讀指引導入）`
  - `C2 — Vendored Scripts & Env Redirect（tools 腳本導入與環境變數改導）`
  - `Checkout — Archive & Verify（收官歸檔與驗證）`
- **影響範圍**：100% DOC-Refactor + 工具導入；**零業務代碼影響**；無 runtime / DB / API 影響。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `.claude-logs/sop/` | 已入版控、含 `2026-07-02_frontend_效能與渲染_SOP_手冊.md` 等前例 | 無 brainstorming 設計發想作業規範 → 待新建 SOP + 視覺伴讀指引 |
| `.claude-logs/tools/` | 已入版控、含 5 腳本（hook 等）；`git check-ignore` 實測新檔不被排除 | 無視覺伴讀腳本 → 待 vendor 5 腳本 + smoke |
| `obra/superpowers@HEAD`（外部來源） | `skills/brainstorming/{SKILL.md, visual-companion.md, scripts/*}` | 落點預設 `docs/superpowers/specs/` + auto-commit + `scripts/` 相對路徑 → 待改寫貼合本專案 |
| `.claude-logs/baton/` | `baton/*` 已 gitignored（僅 README 例外） | mockup 落點需導向此、天然不入版控 |

---

## §3 觀察問題

### 問題 #1：brainstorming 預設落點與 auto-commit 撞治理
- **證據**：superpowers `skills/brainstorming/SKILL.md` — spec 存 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` 且 `Commit the design document to git`
- **影響**：撞 `CLAUDE.md §3`（落點）與 `§1.3`（Claude Code 不 commit）→ vendor 時須將落點改導 `.claude-logs/baton/` 並移除 auto-commit 指示。

### 問題 #2：視覺伴讀輸出目錄需改導，但須守 server.cjs 零編輯
- **證據**：`scripts/server.cjs` — `const SESSION_DIR = process.env.BRAINSTORM_DIR || '/tmp/brainstorm'`（根目錄由 env 注入、`content`/`state` 為固定子夾）；`scripts/start-server.sh` — bash 端組 `SESSION_DIR="${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}"` 後 `env BRAINSTORM_DIR="$SESSION_DIR" … node server.cjs`
- **影響**：落點完全由 `start-server.sh` 掌控 → mockup 改導**只改 `start-server.sh` 一行 bash**、`server.cjs` 零編輯即可（守 plan §6）。

### 問題 #3：`scripts/xxx` 相對路徑耦合
- **證據**：`visual-companion.md` 內引 `scripts/start-server.sh`、`scripts/frame-template.html`、`scripts/helper.js`（相對路徑）
- **影響**：vendor 後路徑改指 `.claude-logs/tools/xxx`（發生於 C1 的指引文件），否則搬移後引用斷裂。

---

## §4 設計方案

### §4.1 C1 — Brainstorming SOP & Visual Companion（作業 SOP 與視覺伴讀指引導入）

新建兩份文件於 `.claude-logs/sop/`（工作產物、直接落最終位置；執行報告暫存 baton）：

1. **作業 SOP**（`2026-07-18_brainstorming_設計發想作業_SOP_手冊.md`）：問答流程骨架（探索 context → 逐一澄清〔一次一題·優先選擇題〕→ 提 2-3 方案權衡 → 分段核准 → 產 spec → 自檢）+ **落點規範**（spec → `.claude-logs/baton/<YYYY-MM-DD>_<任務編碼>_design_spec.md`、禁 `docs/superpowers/`）+ **溯源 header 樣板**（滿足 baton README §2 Provenance）+ **spec→`template_plan` 欄位對照表**（明列四樣護欄仍須階段 1 手工長出）+ **兩護欄**（原料≠plan / 原料必帶溯源 header）+ 移除 auto-commit 明載 + 視覺伴讀啟用/停用指引 + Node≥12 前置聲明。
2. **視覺伴讀指引附件**（`2026-07-18_brainstorming_visual-companion_指引.md`）：vendored 自 superpowers `visual-companion.md`，**所有 `scripts/xxx` 改指 `.claude-logs/tools/xxx`**、mockup 落點描述改 `.claude-logs/baton/.brainstorm/<session>/`（Q7 定案獨立存、SOP 正文引用）。

> **路徑防呆鐵律（plan v2 review #1）**：兩份文件內所有路徑一律寫完整根路徑 `.claude-logs/sop/`、`.claude-logs/tools/`、`.claude-logs/baton/`，嚴禁簡寫。

### §4.2 C2 — Vendored Scripts & Env Redirect（tools 腳本導入與環境變數改導）

vendor 5 腳本 + 1 smoke 至 `.claude-logs/tools/`（工作產物；執行報告暫存 baton）：

- `server.cjs` / `helper.js` / `stop-server.sh` / `frame-template.html`：**逐字 vendored**（零編輯）自 superpowers。
- `start-server.sh`：vendored **且僅改一處** bash 落點組裝——`SESSION_DIR` 由 `${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}` 改為 `.claude-logs/baton/.brainstorm/${SESSION_ID}`（經既有 `BRAINSTORM_DIR` env 傳入 node）；其餘一字不改。
- `test_brainstorm_server_smoke.sh`：新增輕量 smoke（`start-server.sh` 起 → `curl` 首頁 → `stop-server.sh` 收）驗 server 健康。

### §4.3 Checkout — Archive & Verify（收官歸檔與驗證）

- 跑 smoke（自動）+ Conformance 五維度；baron 手動 E2E（純問答路 + 視覺伴讀路，plan §8.2）。
- 一次性歸檔：`mv` plan → `plans/`（檔名去 "vendoring" 更正為 `2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_plan.md`）+ tasks.md → `tasks/` + C1/C2 執行報告 → `executions/`；逐檔 `git add`；產 `executions/2026-07-18_BRAINSTORM-1_checkout_執行.md`（含 staged 白名單自檢實貼）。
- 還原 baton/ 僅剩 README。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `start-server.sh` 落點改導打錯 → 畫圖 server 起不來 | 🟡 中 | C2 smoke（起/探/停）+ Checkout baron E2E 視覺伴讀路 |
| `server.cjs` 等被誤改、失去逐字自足性 | 🟢 低 | C2 §6.2 驗收：對照 superpowers raw 逐字（僅 start-server.sh 允許差一行 `SESSION_DIR`） |
| vendored 逐字漏抄 / 換行汙染 | 🟡 中 | 對照上游 raw + smoke 實跑；node `--check` 語法驗 |
| 跨環境（Mac/GCP）Node 缺失 → 畫圖不可用 | 🟢 低 | SOP 標 Node≥12 前置；問答主體零依賴、畫圖為可選增強 |
| SOP 前向引用 C2 尚未落地的 `tools/` 腳本 | 🟢 低 | 純文件指針、C1/C2 皆於 Checkout 前落地；獨立 revert 亦不破壞（僅指標暫懸） |
| mockup 干擾 baton「平時為空」 | 🟢 低 | 落 `baton/.brainstorm/`、已 gitignored；SOP 規定 session 結束/Checkout 前清空 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# SOP + 指引存在且非空
ls -la .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
ls -la .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md
# SOP 含關鍵章節（溯源 header 樣板 / spec→template_plan 對照 / 兩護欄 / 落點禁令）
grep -nE "溯源|template_plan|護欄|baton" .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
# 指引路徑已改指、無殘留裸 scripts/ 引用
grep -c "\.claude-logs/tools/" .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md   # 期望：>0
grep -nE "(^|[^.])scripts/" .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md       # 期望：無裸 scripts/ 命中
```

### §6.2 C2 驗收

```bash
# 5 腳本 + smoke 就位
ls -la .claude-logs/tools/{server.cjs,start-server.sh,stop-server.sh,helper.js,frame-template.html,test_brainstorm_server_smoke.sh}
# 落點已改導、原 .superpowers 路徑清零
grep -n "\.claude-logs/baton/\.brainstorm" .claude-logs/tools/start-server.sh   # 期望：有命中
grep -c "\.superpowers/brainstorm" .claude-logs/tools/start-server.sh           # 期望：0
# server.cjs 零編輯（對照上游 raw、僅允許 EOL/無差異）
node --check .claude-logs/tools/server.cjs && echo "syntax OK"
# smoke：起 → 探 → 停
bash .claude-logs/tools/test_brainstorm_server_smoke.sh   # 期望：exit 0
```

### §6.3 Checkout 驗收

```bash
pytest tests/ -q                       # 期望：748 passed 零回歸（本任務零 .py）
git diff --cached --name-only          # staged 白名單自檢＝宣告清單
ls .claude-logs/baton/                 # 期望：僅 README.md
```

---

## §7 不可動清單

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 100% 不動
- [ ] `server.cjs` / `helper.js` / `stop-server.sh` / `frame-template.html` **內容逐字＝上游**（零編輯）；唯 `start-server.sh` 允許改一處 `SESSION_DIR` 落點組裝
- [ ] 既有 `.claude-logs/tools/` 5 腳本（`pre_tool_guard.sh` / `dirty_reset_guard.sh` / `test_hook_guards.sh` / `check_css_governance.py` / `settings.hooks.sample.json`）不動
- [ ] `.gitignore` 現有規則不動（`tools/` 天然入版控、`baton/*` 天然排除）
- [ ] `CLAUDE.md §1–§5` / `WORKFLOW_SOP §1–§7` / framework 核心規範不動（登記為正式前置留下一輪·plan Q1）
- [ ] `prompts/` 既有歷史檔不動（僅新增本任務提示詞 + INDEX 同步）

---

## §8 推薦 Commit 拆分

### C1 — Brainstorming SOP & Visual Companion（作業 SOP 與視覺伴讀指引導入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md` + `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md`（皆新建、無 `.bak`）；`baton/` 執行報告不列入（Checkout 一次性歸檔） |
| **安全性** | 🟢 高 — 純文件新增、零 runtime / 零業務代碼 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾（僅刪兩新檔） |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置（指引內引用之 `.claude-logs/tools/` 腳本於 C2 落地＝前向文件指針、不阻斷本 commit） |
| **具體實作細節** | ① 新建 SOP 手冊，章節含：問答流程骨架（探索 context→逐一澄清〔一次一題·優先選擇題〕→提 2-3 方案權衡→分段核准→產 spec→自檢）／落點規範（spec→`.claude-logs/baton/<YYYY-MM-DD>_<任務編碼>_design_spec.md`、明文禁 `docs/superpowers/`）／溯源 header 樣板（產出工具·時間·session 或參考來源，對齊 baton README §2 Provenance）／spec→`template_plan` 欄位對照表（標明 §3 grep 證據·§4 接縫契約·§6 不可動清單·§8 驗證計畫**四樣仍須階段 1 手工長出**）／兩護欄（原料≠plan、原料必帶溯源 header）／移除 auto-commit 明載（交 baron 手動）／視覺伴讀啟用—停用指引 + Node≥12 前置 + mockup 落點 `.claude-logs/baton/.brainstorm/<session>/`。② 新建視覺伴讀指引：vendored 自 superpowers `visual-companion.md`，**逐一將 `scripts/xxx` 改指 `.claude-logs/tools/xxx`**、mockup/session 目錄描述改 `.claude-logs/baton/.brainstorm/<session>/`。③ 全文路徑一律完整根路徑（防呆鐵律）。④ 產 C1 執行報告暫存 `.claude-logs/baton/`（套 template_execution）。 |

### C2 — Vendored Scripts & Env Redirect（tools 腳本導入與環境變數改導）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `.claude-logs/tools/{server.cjs, start-server.sh, stop-server.sh, helper.js, frame-template.html, test_brainstorm_server_smoke.sh}`（皆新建、無 `.bak`）；`baton/` 執行報告不列入 |
| **安全性** | 🟢 高 — 新增獨立工具腳本、不接入任何業務流程 / 不改 runtime |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾（僅刪 6 新檔） |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 無前置（與 C1 各自獨立可 revert；C1 指引引用本 commit 腳本為前向指針） |
| **具體實作細節** | ① `server.cjs` / `helper.js` / `stop-server.sh` / `frame-template.html`：自 `obra/superpowers@HEAD` `skills/brainstorming/scripts/` **逐字 vendored、零編輯**。② `start-server.sh`：vendored 後**僅改一處**——bash 落點組裝 `SESSION_DIR="${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}"` → `SESSION_DIR=".claude-logs/baton/.brainstorm/${SESSION_ID}"`（維持經 `BRAINSTORM_DIR` env 傳入 node 之機制不變），其餘一字不動。③ 新增 `test_brainstorm_server_smoke.sh`：純 bash（起 `start-server.sh` → `curl` 首頁 200 → `stop-server.sh`），exit 0/1。④ `chmod +x` 三 `.sh`。⑤ 產 C2 執行報告暫存 `.claude-logs/baton/`（套 template_execution，§5 貼 node --check + smoke 實測）。 |

### Checkout — Archive & Verify（收官歸檔與驗證）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：`baton/…_plan.md` → `plans/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_plan.md`（去 "vendoring"）／`baton/…_tasks.md` → `tasks/`／C1·C2 執行報告 → `executions/`；`git add` 逐檔含本任務提示詞 + `TODO.md` + `prompts/INDEX.md`；新建 `executions/2026-07-18_BRAINSTORM-1_checkout_執行.md` |
| **安全性** | 🟢 高 — 純文件搬移 + 狀態更新、零業務代碼 |
| **可逆性** | 🟡 中 — 歸檔為 `mv`；回滾需反向 `mv` + 還原 TODO（Conformance 全綠後才執行） |
| **驗收 grep 條件** | 見 §6.3（pytest 748 零回歸 + `git diff --cached --name-only` 白名單自檢 + `ls baton/` 僅 README） |
| **依賴關係** | 前置 C1 + C2 全數落地 |
| **具體實作細節** | ① 跑 §6.2 smoke（自動）；baron 手動 E2E 兩路（純問答路：spec 落 baton·含溯源 header·未 commit／視覺伴讀路：server 起·瀏覽器開頁·點選寫 events·agent 讀回·mockup 落 `baton/.brainstorm` 且 `git status` 不顯示）。② Conformance 五維度核對 plan §2 + tasks §6。③ `mv` baton 三類文件 → 正式目錄（plan 更名去 vendoring）。④ 逐檔 `git add`（嚴禁 `git add .`/`-A`/`<目錄>`），`git diff --cached --name-only` 自檢＝宣告清單。⑤ 產 checkout 執行報告（§8 僅一行 commit·輕量慣例、含 staged 自檢實貼 + §7.2 豁免聲明）。⑥ TODO 雙層結案（active 移除 + `archive/TODO_done_archive.md` 追加表格 + 索引 pointer + 類別索引）。⑦ 驗 baton/ 僅剩 README。 |

---

## §9 Open Questions

無。（plan v2 §9 Q1–Q7 已由 baron 拍板定案；本階段無新增開放問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 BRAINSTORM-1 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 BRAINSTORM-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡，不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-18)：初版拆分完成（依 plan v2；C1 作業 SOP 與視覺伴讀指引 / C2 tools 腳本導入與環境變數改導 / Checkout 收官；全程零 `.bak`〔全數新增〕、零業務代碼、§7.2 純 DOC+tooling 豁免〔Checkout 顯式聲明〕）
