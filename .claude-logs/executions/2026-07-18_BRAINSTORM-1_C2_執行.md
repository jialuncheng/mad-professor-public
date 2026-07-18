# BRAINSTORM-1 C2 — Vendored Scripts & Env Redirect 執行報告

---

**任務代號**：BRAINSTORM-1 C2
**執行日期**：2026-07-18
**依據規劃**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md`（v2；Checkout 歸檔更名去 "vendoring"）
**次級參考**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C1 落地後（sop/ 兩檔已建）。`.claude-logs/tools/` 無視覺伴讀腳本。
- **完成狀態**：vendored 5 腳本 + 1 smoke 至 `.claude-logs/tools/`；`start-server.sh` 落點改導 `.superpowers/brainstorm` → `.claude-logs/baton/.brainstorm`（4 行）；其餘 4 檔逐字＝上游。**smoke 實測 HTTP 200 端到端通過**。零業務代碼、零 .py。
- **與全局策略對齊**：本 commit conditioned on `plan §2` 目標 2/3（vendored 腳本入 tools + 路徑接線改寫、server.cjs 零編輯）——完全落地、無偏離。**vendored 來源＝`obra/superpowers@d884ae0`**（curl 直取原始 bytes、非摘要）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Vendored Scripts & Env Redirect：5 腳本 + smoke 入 `.claude-logs/tools/`，start-server.sh 落點改導、server.cjs 零編輯 | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `.claude-logs/tools/server.cjs` | — | vendored 逐字＝上游（零 npm 相依 http server） |
| 新建 | `.claude-logs/tools/start-server.sh` | — | vendored + **僅改 4 落點行**（`.superpowers/brainstorm`→`.claude-logs/baton/.brainstorm`） |
| 新建 | `.claude-logs/tools/stop-server.sh` | — | vendored 逐字＝上游 |
| 新建 | `.claude-logs/tools/helper.js` | — | vendored 逐字＝上游（瀏覽器端 WS 互動） |
| 新建 | `.claude-logs/tools/frame-template.html` | — | vendored 逐字＝上游（frame 模板） |
| 新建 | `.claude-logs/tools/test_brainstorm_server_smoke.sh` | — | 新增 smoke（隔離 temp project-dir·起→curl 200→停） |

> 本 Commit 僅新增檔案、無修改既有內容檔 → **全程零 `.bak`**。

---

## §4 修法說明

### §4.1 五腳本 vendored（`obra/superpowers@d884ae0` `skills/brainstorming/scripts/`）

以 `curl` 自 raw.githubusercontent 直取原始 bytes（確保逐字、非 WebFetch 摘要）。`server.cjs` / `helper.js` / `stop-server.sh` / `frame-template.html` **零編輯**（§5.3 diff 證實逐字相同）。

### §4.2 `start-server.sh` — 落點改導（唯一允許改動·plan §6）

落點基底 `.superpowers/brainstorm` 於 4 行出現（1 usage 註解 + SESSION_DIR + PORT_FILE + TOKEN_FILE），一致改導為 `.claude-logs/baton/.brainstorm`（保留 `${PROJECT_DIR}/` 前綴、經既有 `BRAINSTORM_DIR` env 傳入 node、**`server.cjs` 零編輯**）：

```diff
- SESSION_DIR="${PROJECT_DIR}/.superpowers/brainstorm/${SESSION_ID}"
+ SESSION_DIR="${PROJECT_DIR}/.claude-logs/baton/.brainstorm/${SESSION_ID}"
- export BRAINSTORM_PORT_FILE="${PROJECT_DIR}/.superpowers/brainstorm/.last-port"
+ export BRAINSTORM_PORT_FILE="${PROJECT_DIR}/.claude-logs/baton/.brainstorm/.last-port"
- export BRAINSTORM_TOKEN_FILE="${PROJECT_DIR}/.superpowers/brainstorm/.last-token"
+ export BRAINSTORM_TOKEN_FILE="${PROJECT_DIR}/.claude-logs/baton/.brainstorm/.last-token"
```

> 三路徑檔（session/port/token）同屬一落點基底，一致改導避免 port/token 檔另造未被 gitignore 的 `.superpowers/` 夾。`cd "$SCRIPT_DIR"`（line 151）+ `SCRIPT_DIR` 由 `$0` 計算（line 20）→ vendored 至 tools/ 後 `node server.cjs` 仍可攜。

### §4.3 `test_brainstorm_server_smoke.sh` — 新增 smoke

隔離 `mktemp -d` 作 project-dir（不觸真實 baton）→ `start-server.sh --background` → sed 解析 JSON 取 url/state_dir → `curl` 期望 200 → `stop-server.sh` → cleanup。

---

## §5 測試結果

### §5.1 本地改動狀態確認

```bash
$ git status -s | grep -E "\.py$"
（無輸出 → 零 .py 改動）

$ git status -s .claude-logs/tools/
?? .claude-logs/tools/frame-template.html
?? .claude-logs/tools/helper.js
?? .claude-logs/tools/server.cjs
?? .claude-logs/tools/start-server.sh
?? .claude-logs/tools/stop-server.sh
?? .claude-logs/tools/test_brainstorm_server_smoke.sh
```

### §5.2 §6.2 C2 驗收（真實輸出）

```bash
$ grep -n "\.claude-logs/baton/\.brainstorm" .claude-logs/tools/start-server.sh
9: / 117: / 120: / 121:                    # 落點改導 4 行 ✅
$ grep -c "\.superpowers/brainstorm" .claude-logs/tools/start-server.sh
0                                          # 原落點清零 ✅

$ node --check .claude-logs/tools/server.cjs   → server.cjs syntax OK ✅
$ node --check .claude-logs/tools/helper.js    → helper.js syntax OK ✅

$ bash .claude-logs/tools/test_brainstorm_server_smoke.sh
SMOKE OK: server served http://localhost:51414/?key=e8dedfd9...c2f0 (HTTP 200)
smoke exit=0                               # 端到端健康 ✅
```

### §5.3 逐字＝上游驗證（重抓 `@d884ae0` diff）

```bash
$ for f in server.cjs stop-server.sh helper.js frame-template.html; do diff <upstream> <本地>; done
server.cjs: 逐字相同 ✅   stop-server.sh: 逐字相同 ✅
helper.js: 逐字相同 ✅     frame-template.html: 逐字相同 ✅

$ diff <upstream start-server.sh> <本地>
# 全部差異＝9/117/120/121 四行（皆 .superpowers/brainstorm → .claude-logs/baton/.brainstorm）✅

$ git check-ignore -v .claude-logs/baton/.brainstorm/test/foo.html
.gitignore:186:.claude-logs/baton/*   →   mockup 落點 gitignored ✅
```

### §5.4 SOP 一致性核查（BE-Refactor / BE-Hotfix 強制）

DOC-Refactor 工作流，無 .py 改動，跳過（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 業務代碼（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`） | [x] ✅ 未觸碰（零 .py） |
| `server.cjs` / `helper.js` / `stop-server.sh` / `frame-template.html` 逐字＝上游 | [x] ✅ diff 證實零編輯 |
| 既有 `.claude-logs/tools/` 5 腳本（hook 等） | [x] ✅ 未觸碰 |
| `.gitignore` 現有規則 | [x] ✅ 未變更（tools 天然入版控、baton 天然排除） |
| `CLAUDE.md` / `WORKFLOW_SOP` / framework 核心規範 | [x] ✅ 未變更 |
| `start-server.sh` 僅改落點（其餘邏輯不動） | [x] ✅ diff 僅 4 落點行 |

---

## §自評（策略對齊自我審查）

- **(a) 越界?**：否。僅新增 tools/ 6 檔 + 依 prompt 同步 TODO + 歸檔提示詞；start-server.sh 僅改落點 4 行、其餘 vendored 逐字。
- **(b) 無關 / 違規?**：否。全對應 tasks §8 C2；未 auto-commit（守 §1.3）；smoke 用隔離 temp 不污染真實 baton。
- **(c) 推進哪個 U-N?（正向軸）**：推進 `plan §2` 目標 2/3（vendored 腳本 + server.cjs 零編輯改導），為 Checkout（E2E + 歸檔）鋪定。

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `.claude-logs/baton/`，待 Checkout 一次性 `mv + git add` 歸檔至 `executions/`。
- **hash 自癒（本輪）**：複掃 `待 baron 回填` 佔位＝0（C1 已清 SOP-COMPLY checkout `fb3e76a`），本輪無新增回填。
- **下一步**：Checkout — Archive & Verify（收官歸檔與驗證），待 baron 下達獨立提示詞。
- **消化歸檔之 baton 檔**：無（本階段不歸檔）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（本 Commit 僅新增檔案，無備份）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
#    commit 前以 git diff --cached --name-only 自檢 staged 集合＝本清單，多/少一檔即停。
#    ⚠️ baton/ 執行報告與 plan/tasks 嚴禁在此階段 git add（Checkout 才歸檔）。
git add .claude-logs/tools/server.cjs
git add .claude-logs/tools/start-server.sh
git add .claude-logs/tools/stop-server.sh
git add .claude-logs/tools/helper.js
git add .claude-logs/tools/frame-template.html
git add .claude-logs/tools/test_brainstorm_server_smoke.sh

# 3. commit message 草稿（已寫入 /tmp/BRAINSTORM-1_C2_msg.txt）
git commit -F /tmp/BRAINSTORM-1_C2_msg.txt
```

### §8.2 commit message 草稿

（草稿已寫入 `/tmp/BRAINSTORM-1_C2_msg.txt`）

```
DOC-Refactor: BRAINSTORM-1 C2 — Vendored Scripts & Env Redirect

- 導入 server.cjs / helper.js / stop-server.sh / frame-template.html 至 .claude-logs/tools/（逐字＝上游 obra/superpowers@d884ae0）
- 導入 start-server.sh 並僅改 4 落點行：.superpowers/brainstorm → .claude-logs/baton/.brainstorm（server.cjs 零編輯）
- 新增 test_brainstorm_server_smoke.sh 輕量 smoke（實測 HTTP 200）
- 執行報告暫存於 baton/ 不入版控

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 BRAINSTORM-1 C2 的腳本 vendoring 與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；階段 6 收官時 Conformance 核對原始 plan；核對後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 階段 6 收官 check 提示詞 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、Checkout 前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C2 執行唯一源，不重複 tasks 六維度、不重複 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-07-18)：C2 執行完畢產出報告（vendored 5 腳本 + smoke·來源 `@d884ae0`、start-server.sh 僅 4 落點行、4 檔逐字＝上游、smoke HTTP 200、零 .bak、零 .py）
