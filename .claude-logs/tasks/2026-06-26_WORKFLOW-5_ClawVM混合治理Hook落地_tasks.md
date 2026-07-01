# WORKFLOW-5 ClawVM 混合治理 Hook 落地 — Tasks

> 本文件為 WORKFLOW-5 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_plan.md`（v5）產出，含 7 個 Commit（C1–C6 + C7 Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 4 個 | `.claude-logs/tools/pre_tool_guard.sh`（截斷守衛）/ `.claude-logs/tools/dirty_reset_guard.sh`（DIRTY-RESET 守衛）/ `.claude-logs/tools/test_hook_guards.sh`（hook 乾跑/單元測試）/ `.claude-logs/tools/settings.hooks.sample.json`（settings 掛載樣本） |
| **修改檔案** | 2 個 | `.claude-logs/baton/README.md`（Baton 3-Phase 非破壞性寫入契約 + 部署 SOP 一段）/ `.claude-logs/templates/template_file_governance.md`（§99.1 新增 Scope/Provenance/Fidelity Floor 三維度） |
| **目錄初始化** | 0 個 | `.claude-logs/tools/` 已存在（既有 golden_baseline.py / regen_rag.py / manage_glossary.py），無需建立 |
| **狀態更新** | 2 個 | `TODO.md` / `.claude-logs/prompts/INDEX.md` |
| **Commits** | 7 個 | C1 → C2 → C3 → C4 → C5 → C6 → C7 Checkout |
| **baton 歸檔** | 1 次 | C7 Checkout 一次性 mv：plan → `plans/`、tasks → `tasks/`、C1–C7 執行報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：純文件治理仰賴 AI 自由心證，無法可靠防失憶（DIRTY-RESET）與破壞性截斷（DESTRUCTIVE-WRITE）；plan v5 已確立改用真實 Claude Code Hook（harness enforcement）+ Baton 3-Phase 形式化 + Template Fidelity Floor。
- **解法**：將 plan 三大目標原子化為 7 個獨立可驗證 commit，**以 C1 SessionEnd dry-run 為硬 gate**（其結果決定 C5 走攔截或 observable），純文件章節與 hook 腳本分離成獨立 commit，最後 C7 收官歸檔。
- **影響範圍**：100% 治理基建（`.claude-logs/tools/` hook 腳本 + baton/template 文件）；**零業務代碼影響**（hook 腳本屬治理工具，比照 tools/ 既有 CLI）。
- **不可動清單**：見 §7

### Commit 序列（含中文括號命名）

- C1 — SessionEnd Dry-Run（阻擋能力實測·gate）
- C2 — Baton 3-Phase 形式化（baton/README 非破壞性寫入契約）
- C3 — Template Fidelity Floor（§99.1 Scope/Provenance/降級底線三維度）
- C4 — 截斷守衛腳本（PreToolUse pre_tool_guard 截斷偵測 Hard Deny）
- C5 — DIRTY-RESET 守衛腳本（依 C1 結果走攔截或 Observable Fault）
- C6 — Settings 掛載與部署 SOP（Q1 跨環境同步）
- C7 — Checkout（收官與歸檔）

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `~/.claude/settings.json` | 已有 `PreToolUse`(matcher Bash → `rtk hook claude`)，證 hook 機制可用 | 無治理用 hook；DESTRUCTIVE-WRITE / DIRTY-RESET 無實體攔截 |
| `.claude/`（專案級） | 被 `.gitignore:174` 排除版控 | 專案級 settings 無法跨環境同步 → 防護網靜默失效（Q1 已定 (a)：腳本進 tools/ 版控） |
| `.claude-logs/baton/README.md` | §2 僅述 `mv` + `git add` | 未明定非破壞性寫入語意與 3-Phase 自檢 |
| `.claude-logs/templates/template_file_governance.md` | §99.1 僅基本治理維度 | 缺 Scope / Provenance / Fidelity Floor，floor 無機器可讀依據 |
| `SessionEnd` hook 阻擋能力 | 未知 | plan §9 Q2：能否 block 決定 DIRTY-RESET 走攔截或 observable → C1 必先實測 |

---

## §3 觀察問題

### 問題 #1：DESTRUCTIVE-WRITE 無實體防線
- **證據**：`CLAUDE.md §1.3` 僅文字述 `auto-classifier`，repo 內無實作（grep 僅命中 CLAUDE.md 文字）。
- **影響**：失憶 / 判斷錯誤時可盲目截斷既有真理源（CLAUDE.md / WORKFLOW_SOP.md / plans / sop），無 hard deny 攔截。

### 問題 #2：DIRTY-RESET 仰賴自報
- **證據**：plan §1 — 提示詞自報形同 Theater；失憶 agent 無法可靠自我診斷。
- **影響**：Checkout 階段該歸檔卻未歸檔的 dirty baton 無確定性偵測。

### 問題 #3：跨環境同步斷點
- **證據**：`grep -n "^\.claude/$" .gitignore` → `174:.claude/`。
- **影響**：專案級 hook 設定不入版控、三環境（Mac / Server / GCP）漏裝即靜默失效。

---

## §4 設計方案

> 依賴鏈：C1（gate）→ C5 走向；C3（floor 機器可讀）→ C4 第二階段預留；C4/C5 腳本 → C6 掛載；全部 → C7 收官。
> C2/C3 為純文件，可與 C1 並行；但 commit 序維持線性以利驗收。

### §4.1 C1 — SessionEnd Dry-Run（阻擋能力實測·gate）
- 撰寫極簡 SessionEnd（及對照 Stop）測試 hook，回傳 block/deny，實測 Claude Code 是否允許中斷 session 終止。
- 結果寫進 C1 執行報告，**據此定案 plan §9 Q2**：
  - 可 block → C5 路徑 A（攔截）。
  - 僅清理/事後 → C5 路徑 B（Observable Fault Only）。
- **本 commit 不留永久腳本**（測試 hook 為 throwaway，測畢移除），唯一交付＝執行報告內的實測結論。
- baron 建議傾向：即使可 block，DIRTY-RESET 首版先做 Observable（降低把自己鎖在外的風險），是否升級攔截留後續。

### §4.2 C2 — Baton 3-Phase 形式化（baton/README 非破壞性寫入契約）
- 改寫 `baton/README.md §2`：明定歸檔 = Staging（寫 baton）→ Deterministic Validation（Provenance / Schema / 非破壞性自檢）→ Scoped Commit（一次性 `mv` + `git add`）。
- **對帳 WORKFLOW_SOP §3 `mv` 鐵律**：維持一次性 `mv`，僅在 `mv` 前插入自檢步驟；不改既有「Run 階段嚴禁 mv、Checkout 才歸檔」鐵律。
- 純文件、零腳本。

### §4.3 C3 — Template Fidelity Floor（§99.1 三維度）
- `template_file_governance.md §99.1` 新增三維度：
  - **Scope**：session-private vs project-shared。
  - **Provenance**：資料溯源（來源 tool call / transcript span / 上游真理源）。
  - **Fidelity Floor**：降級底線（如「Constraint / 不可動清單永不低於 structured」），並以可解析格式預留機器可讀空間（供 C4 第二階段 floor 守衛）。
- **Cost-Aware 保留**：高重算成本 evidence（grep 證據 / 實測輸出 / commit hash）標註優先不降級。
- 純文件、零腳本。

### §4.4 C4 — 截斷守衛腳本（PreToolUse Hard Deny）
- 新建 `.claude-logs/tools/pre_tool_guard.sh`：
  - 讀 stdin 的 PreToolUse JSON，取 `tool_name`（`Write`/`Edit`）與 `tool_input.file_path`。
  - 僅對保護範圍生效：`plans/`、`sop/`、`ref/`、根 `CLAUDE.md`、`TODO.md`。
  - **第一階段截斷守衛**：比對磁碟現檔行數/大小，新內容驟降 **>50% 且 >50 行** → 判截斷 → `deny`（exit 2）+ 提示訊息。
  - **Bypass（防誤觸減速帶）**：寫入內容含 sentinel `// BYPASS_TRUNCATION_GUARD` → 放行。
  - **第二階段 floor 守衛**：預留 stub，標註「待 C3 floor 機器可讀化後實作」，本 commit 不啟用。
- 同 commit 補 `test_hook_guards.sh` 的截斷守衛測試案例（見 §6）。

### §4.5 C5 — DIRTY-RESET 守衛腳本（依 C1 結果）
- 新建 `.claude-logs/tools/dirty_reset_guard.sh`：
  - **觸發條件**：非「baton 非空」，而是「TODO 標 ✅ Checkout 但 baton 仍有該任務 dirty state 未歸檔」→ 需解析 baton 檔名→任務代號→TODO 狀態。
  - 依 C1 定案：路徑 A 則於 SessionEnd block + 警告；路徑 B 則僅寫日誌 / 印警告（Observable Fault Only）。
- 同 commit 補 `test_hook_guards.sh` 的 DIRTY-RESET 測試案例。

### §4.6 C6 — Settings 掛載與部署 SOP（Q1）
- 新建 `.claude-logs/tools/settings.hooks.sample.json`：示範 `PreToolUse`(Write|Edit → pre_tool_guard.sh) 與 SessionEnd（→ dirty_reset_guard.sh）掛載。
- **掛載點決策（plan §9 Q1 + 審查建議）**：採專案級 `.claude/settings.json` 指向版控腳本（作用域隔離、不污染其他專案），而非全域 `~/.claude/settings.json`。
- 於 `baton/README.md`（C2 已改）追加「跨環境部署 SOP」一段：各環境一次性貼上 sample、指向 `.claude-logs/tools/` 版控腳本。

### §4.7 C7 — Checkout（收官與歸檔）
- Conformance 驗收（目標規格 / §6 grep / 不可動清單 / 提示詞稽核 / msg）。
- §7.2 跨 Phase 整合測試：**純治理 + hook 腳本、無業務 Phase handoff → 顯式豁免**（同 WORKFLOW-3/4 立規者先例）。
- baton 一次性 mv：plan → `plans/`、tasks → `tasks/`、C1–C7 報告 → `executions/` + `git add`。
- TODO 結案 + hash 自癒 + INDEX 連結正式路徑。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| Hook 寫錯導致 session 死鎖 / 無法退出 | 🔴 高 | C1 先 dry-run 確認能力；C4/C5 配 `test_hook_guards.sh` 乾跑；腳本失敗一律 fail-open（exit 0 放行）防鎖死 |
| 截斷守衛誤擋合法 DOC-Refactor | 🟡 中 | 保守門檻（>50% 且 >50 行）+ sentinel bypass；保護範圍限真理源 |
| DIRTY-RESET 誤報（跨 session 正常中途結束） | 🟡 中 | 觸發條件鎖死「TODO ✅ 但未歸檔」，非「baton 非空」 |
| 跨環境漏裝 hook 靜默失效 | 🟡 中 | 腳本版控（tools/）+ 部署 SOP（C6）+ sample settings |
| SessionEnd 無法 block | 🟡 中 | C1 gate；不能 block 則 C5 降級 Observable Fault（plan §9 Q2 已定 fallback） |

---

## §6 測試計畫

> 純治理任務，無業務 pytest；以 hook 腳本獨立乾跑 + 文件 grep 驗收。

### §6.1 C1 驗收
```bash
# C1 執行報告須記錄 SessionEnd 實測結論（能否 block）；無永久檔
grep -nE "SessionEnd|可 block|Observable" .claude-logs/baton/2026-06-26_WORKFLOW-5_C1_執行.md  # 期望：有結論
```

### §6.2 C2 驗收
```bash
grep -nE "Staging|Validation|Scoped Commit|非破壞" .claude-logs/baton/README.md   # 期望：3-Phase 命中
grep -n "mv" .claude-logs/baton/README.md                                          # 期望：保留一次性 mv 鐵律
```

### §6.3 C3 驗收
```bash
grep -nE "Scope|Provenance|Fidelity Floor|降級底線" .claude-logs/templates/template_file_governance.md  # 期望：三維度命中
grep -nE "grep 證據|commit hash|優先不降級" .claude-logs/templates/template_file_governance.md          # 期望：cost-aware 命中
```

### §6.4 C4 驗收
```bash
ls -la .claude-logs/tools/pre_tool_guard.sh                       # 期望：存在且可執行
bash .claude-logs/tools/test_hook_guards.sh truncation            # 期望：截斷 deny / append 放行 / sentinel 放行 全綠
grep -n "BYPASS_TRUNCATION_GUARD" .claude-logs/tools/pre_tool_guard.sh  # 期望：bypass 機制命中
```

### §6.5 C5 驗收
```bash
ls -la .claude-logs/tools/dirty_reset_guard.sh                    # 期望：存在且可執行
bash .claude-logs/tools/test_hook_guards.sh dirty_reset           # 期望：Checkout✅未歸檔→報、中途非空→放行
```

### §6.6 C6 驗收
```bash
cat .claude-logs/tools/settings.hooks.sample.json | grep -E "Write\|Edit|SessionEnd"  # 期望：兩 hook 掛載
grep -nE "跨環境|部署 SOP|專案級" .claude-logs/baton/README.md                          # 期望：部署段命中
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `processor/*.py` / `pipelines/*.py` / `static/*` — 100% 不動
- [ ] **`ref/WORKFLOW_SOP.md` 六階段強制觸發鏈** — 核心流程不動（本案不重寫 §3/§4 維度定義）
- [ ] **`CLAUDE.md §3 工作目錄硬規則`** — 不重寫（C6 掛載決策引用而非修改）
- [ ] **主 repo 業務目錄** — 嚴禁讀寫
- [ ] **`.gitignore` `.claude/` 排除規則** — 本案不放行 `.claude/`（Q1 採腳本進 tools/ 方案，不動 gitignore）

---

## §8 推薦 Commit 拆分

### C1 — SessionEnd Dry-Run（阻擋能力實測·gate）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 臨時測試 hook（throwaway，測畢移除）+ 各環境 `.claude/settings.json` 暫時掛載（測完還原）；無永久檔交付 |
| **安全性** | 🟡 中 — 測試 hook 可能影響 session 退出；務必 fail-open + 測畢立即移除 |
| **可逆性** | 🟢 高 — 移除臨時 hook + 還原 settings 即復原 |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置（gate，須最先做） |
| **具體實作細節** | ① 寫極簡 SessionEnd hook（echo + 嘗試回傳 block/deny JSON）暫掛 `.claude/settings.json`；② 觸發 session 結束，觀察是否被中斷；③ 對照測 Stop hook 行為；④ 將「能否 block」結論 + 對 C5 路徑 A/B 的裁決寫入 C1 執行報告；⑤ 移除臨時 hook、還原 settings。**不留永久腳本** |

### C2 — Baton 3-Phase 形式化（baton/README 非破壞性寫入契約）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/baton/README.md`（+ `.bak`） |
| **安全性** | 🟢 高 — 純文件 / 零 runtime |
| **可逆性** | 🟢 高 — `git revert` 或 `.bak` 還原 |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 無前置（可與 C1/C3 並行） |
| **具體實作細節** | 改寫 §2 為三階段：Staging（發起方寫 baton）→ Deterministic Validation（接收方查 Provenance / Schema / 非破壞性）→ Scoped Commit（驗證通過一次性 `mv` + `git add` + Audit Trail）；明文對帳 WORKFLOW_SOP §3「Run 嚴禁 mv、Checkout 才歸檔」鐵律不變；改前產 `.bak` |

### C3 — Template Fidelity Floor（§99.1 三維度）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/templates/template_file_governance.md`（+ `.bak`） |
| **安全性** | 🟢 高 — 純文件 |
| **可逆性** | 🟢 高 — `.bak` 還原 |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | 無前置；C4 第二階段 floor 守衛依賴本 commit 的機器可讀格式 |
| **具體實作細節** | §99.1 治理規格表新增列：**Scope**（session-private / project-shared）、**Provenance**（來源溯源）、**Fidelity Floor**（降級底線，舉例 Constraint/不可動清單永不低於 structured，並用 key:value 等可解析格式預留機器可讀）；加 Cost-Aware 註（grep 證據 / 實測輸出 / commit hash 優先不降級）；改前產 `.bak` |

### C4 — 截斷守衛腳本（PreToolUse Hard Deny）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `.claude-logs/tools/pre_tool_guard.sh` + `.claude-logs/tools/test_hook_guards.sh`（截斷案例） |
| **安全性** | 🟡 中 — hook 腳本可影響寫入；fail-open 設計防鎖 |
| **可逆性** | 🟢 高 — 刪檔 / settings 不掛載即停用 |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | 無前置（floor 守衛 stub 依賴 C3，但本 commit 僅做第一階段截斷） |
| **具體實作細節** | ① 讀 stdin PreToolUse JSON，解析 `tool_name`/`tool_input.file_path`（用 jq 或純 shell）；② 範圍過濾：plans/ ∪ sop/ ∪ ref/ ∪ CLAUDE.md ∪ TODO.md，範圍外 exit 0；③ 讀磁碟現檔行數/大小、估算新內容、驟降 >50% 且 >50 行 → 輸出 deny JSON / exit 2 + 提示改走版控；④ 內容含 `// BYPASS_TRUNCATION_GUARD` → exit 0 放行；⑤ floor 守衛 stub 註「待 C3 機器可讀後實作」；⑥ 任何解析異常 fail-open exit 0；⑦ test_hook_guards.sh 加 truncation 子命令（截斷 deny / append 放行 / sentinel 放行 / 範圍外放行） |

### C5 — DIRTY-RESET 守衛腳本（依 C1 結果）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `.claude-logs/tools/dirty_reset_guard.sh` + `test_hook_guards.sh`（dirty_reset 案例） |
| **安全性** | 🟡 中 — 若走路徑 A（block）可影響退出；fail-open 防鎖 |
| **可逆性** | 🟢 高 — 刪檔 / 不掛載即停用 |
| **驗收 grep 條件** | §6.5 |
| **依賴關係** | **依賴 C1**（Q2 路徑 A/B 定案） |
| **具體實作細節** | ① 解析 baton/ 內檔名→任務代號；② 讀 TODO.md 該任務狀態；③ 條件＝「TODO 標 ✅/Checkout 但 baton 仍有該任務 dirty state」才觸發（非「baton 非空」）；④ 路徑 A：SessionEnd 回 block + 警告；路徑 B：寫日誌 + 印警告（Observable Fault Only，baron 建議首版採此）；⑤ 異常 fail-open；⑥ test_hook_guards.sh 加 dirty_reset 子命令（Checkout✅未歸檔→報 / 中途非空→放行 / 已歸檔→放行） |

### C6 — Settings 掛載與部署 SOP（Q1）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `.claude-logs/tools/settings.hooks.sample.json` + `.claude-logs/baton/README.md` 追加部署段（+ `.bak`） |
| **安全性** | 🟢 高 — 樣本 + 文件，不自動掛載 |
| **可逆性** | 🟢 高 — `.bak` 還原 / 刪樣本 |
| **驗收 grep 條件** | §6.6 |
| **依賴關係** | 依賴 C4/C5 腳本路徑就緒 |
| **具體實作細節** | ① 寫 sample json：`PreToolUse`(matcher `Write|Edit` → `./.claude-logs/tools/pre_tool_guard.sh`) + `SessionEnd`(→ `./.claude-logs/tools/dirty_reset_guard.sh`)；② baton/README 追加「跨環境部署 SOP」：採**專案級 `.claude/settings.json`** 指向版控腳本（作用域隔離、不污染他案），三環境一次性貼上；③ 明示 `.claude/settings.json` 本身不入版控、邏輯在 tools/ 版控 |

### C7 — Checkout（收官與歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` 結案 + `prompts/INDEX.md` 連結正式路徑 + baton 一次性 mv 歸檔 |
| **安全性** | 🟢 高 — 文件歸檔 |
| **可逆性** | 🟢 高 — git 可回溯 |
| **驗收 grep 條件** | 跨 §6.1–§6.6 全綠 + 不可動清單 git diff 證據 |
| **依賴關係** | 依賴 C1–C6 全部完成 |
| **具體實作細節** | ① Conformance：目標規格 / §6 grep / 不可動 / 提示詞稽核（plan/tasks/C1–C7 各份）/ msg §8；② §7.2 純治理 + hook、無業務 handoff → 顯式豁免（WORKFLOW-3/4 先例）；③ baton 一次性 mv：plan→plans/、tasks→tasks/、C1–C7 報告→executions/ + `git add`；④ TODO 結案改寫入 ✅ 表 + hash 自癒；⑤ INDEX 連結正式路徑；⑥ msg 草稿寫 /tmp，不自發 commit |

---

## §9 Open Questions

無。（plan v5 §9 兩 Open Questions——Q1 跨環境同步採 (a) 腳本版控、Q2 SessionEnd 阻擋能力——已於拆分階段定案：Q1 落 C6 專案級掛載、Q2 落 C1 dry-run gate + C5 路徑分支；待 baron 拍板後進 Run。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-5 ClawVM 混合治理 Hook 落地的原子 Commit 拆分清單與實作細節 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 WORKFLOW-5 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-26)：初版拆分完成——依 plan v5 拆 7 commit（C1 SessionEnd dry-run gate / C2 baton 3-Phase / C3 template floor / C4 截斷守衛 / C5 DIRTY-RESET 守衛 / C6 掛載與部署 SOP / C7 Checkout）；Q1/Q2 於拆分階段定案落 commit。
