# THEME-DEDUP checkout — 成果收官歸檔 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | THEME-DEDUP checkout |
| **執行日期** | 2026-07-10 |
| **依據規劃** | `tasks.md §8 checkout` + `WORKFLOW_SOP §3 checkout 執行報告鐵律` + CHECKOUT-GUARD 白名單鐵律 |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 收官完成（待 baron commit checkout） |

---

## §1 基準與完成狀態

- **已 ship**：C0 `2380420`／C1 `f64d15b`／C2 `0fd4ca6`／C3 `bf4577c`／C4 `3cad5f0`（baron 手動·全數 git log 實證）。
- **提示詞 stale 修正（×3·誠實記錄）**：① 讀檔清單列 `Baseline_C0_執行.md`＝**不存在**（C0 由 baron 直接 commit、無獨立報告；C1 報告 §1 已記載）→ C0 驗收以 git 實證替代；② §8 列 `C0_run_提示詞.md`＝不存在（同因）→ add 清單修正為實存 7 份（含 `2026-07-09_THEME-DEDUP_plan_提示詞.md`·提示詞漏列）；③ TODO 結案格式依 **framework §2.5 v5 雙層結構**（完整表→done_archive + 一行索引）、非提示詞所述「TODO 內新增表格」（framework 為 SSOT·同 FE-CSS-GOV/FE-PERF-2 先例）。

---

## §2 Conformance 驗收結果

### 目標規格合規性（plan §2）
| # | 規格項 | 對應報告 | 狀態 |
|---|---|---|---|
| 1 | 凍結規格目錄級契約（26 token/16 選擇器/骨架/白名單/兩槽） | C2 §4（theme-guide 重寫）| ✅ 合規 |
| 2 | 9 支全檔改寫（骨架/去結構/token 補齊/死碼/chrome 保留） | C2/C3 §4/§5 | ✅ 合規 |
| 3 | 前置 baseline 序位 | C0 `2380420` 先於 C2/C3（C1 技術獨立·報告記載） | ✅ 合規 |
| 4 | 視覺 100% 等價 | C1 結構證明 + C2/C3 delta 對帳+token 值==原值（機器證） | ✅ 合規 |
| 5 | base/token 承接 | C1 §4/§5 | ✅ 合規 |
| 6 | docs 權威化（目錄級語言+§11 遺留登記） | C2/C3 §4 | ✅ 合規 |
| 7 | 模板產出（落點鐵防線） | C4 §4（design/docs/·非 static/themes/） | ✅ 合規 |
| 8 | 契約腳本常駐化（純標準庫） | C4 §4/§5（首綠+突變負測） | ✅ 合規 |

### 測試計畫合規性（tasks §6）
| # | 驗收 | 驗證 | 狀態 |
|---|---|---|---|
| 1 | C0 — 5 支原樣 baseline | git `2380420`（原樣·後續 delta 以其為基） | ✅ |
| 2 | C1 — 鋪底（7 token/h2 填槽/byline/主題零 diff/零視覺變） | C1 §5 | ✅ |
| 3 | C2 — 內建 4 支（delta 對帳/26/兩槽/multiset） | C2 §5 | ✅ |
| 4 | C3 — 上傳 5 支（死碼=0/26/值==baseline/chrome 零改寫） | C3 §5 | ✅ |
| 5 | C4 — 腳本首次全綠 EXIT 0 + 突變負測 | C4 §5 | ✅ |
| 6 | **收官重跑常駐腳本（本 checkout 實測）** | `✅ CSS 契約檢查全綠（全量（主檔系 7 + 主題 9 + 模板 1））… EXIT: 0` | ✅ |

### 不可動清單合規性
| 項目 | 驗證 | 狀態 |
|---|---|---|
| 後端業務代碼（tools 除外） | `git diff 6fea7dc..HEAD -- '*.py'`（排 tools）= 0 | ✅ |
| `static/index.html` | `git diff 6fea7dc..HEAD --stat` = 0 | ✅ |
| 視覺值與裝飾例外 | C2/C3 機器證 + §11.3 登記 | ✅ |
| apple/google chrome 覆寫層內容 | C3 delta multiset 零改寫 + 收官抽查（border-radius 原樣） | ✅ |
| themes/自訂主題 unlayered | 腳本 ①（收官重跑含） | ✅ |

### 提示詞歸檔與版控稽核
7 份實存（plan/Tasks/C1–C4/Check·**無 C0 run＝baron 直 commit、如實**）、現皆 untracked → 本 checkout commit 逐檔 add（§4 清單）。

### msg 草稿完整性
C1–C4 報告 §8 皆含完整 msg（C0 msg＝`/tmp/THEME-DEDUP_baseline_msg.txt` 由 Claude 預備、baron 已用）。

**總結：🟢 全部合規 → 執行收官歸檔。**

---

## §3 baton 歸檔確認（3-Phase·非破壞性）

| 檔 | baton → 正式目錄 | 非破壞性 |
|---|---|---|
| plan_v1 | → `plans/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md` | ✅ 無同名 |
| tasks | → `tasks/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md` | ✅ 無同名 |
| C1–C4 執行報告（4） | → `executions/2026-07-10_THEME-DEDUP_{Foundation_C1,Builtin_C2,Uploads_C3,Guard_C4}_執行.md` | ✅ 無同名 |

`ls baton/` 收官後＝README + 4 長駐（QUEUE-1 v2／PIPE-SPEC／css governance audit／Osmani PDF）——**THEME-DEDUP 零殘留** ✅。

---

## §4 TODO 雙層結案 + hash 自癒

- **完整成果表**：`archive/TODO_done_archive.md` 頂部新增 THEME-DEDUP 六列表（C0–checkout·**C0–C4 hash 全實填**）+ 修法依據/動因/視覺等價機器證/deviation/§7.2/後續註。
- **一行索引**：TODO ✅ 區新增 `✅ FE-Refactor THEME-DEDUP …（2380420…checkout 待回填、6 commits）`。
- **active 移除**：🔴 高優先 THEME-DEDUP 區塊移除（殘留提及=1＝索引行 ✓）。
- **hash 自癒**：C0 `2380420`/C1 `f64d15b`/C2 `0fd4ca6`/C3 `bf4577c`/C4 `3cad5f0` 全填；唯 checkout 待 baron commit 後回填（本表 1 處 + TODO 索引行）。

---

## §5 staged 白名單自檢（CHECKOUT-GUARD 鐵律）

**checkout commit 宣告集合（17 檔·全為治理歸檔·零業務碼零 .bak）**：
```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/prompts/INDEX.md
.claude-logs/prompts/2026-07-09_THEME-DEDUP_plan_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_Tasks_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_C1_run_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_C2_run_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_C3_run_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_C4_run_提示詞.md
.claude-logs/prompts/2026-07-10_THEME-DEDUP_Check_提示詞.md
.claude-logs/plans/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md
.claude-logs/tasks/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md
.claude-logs/executions/2026-07-10_THEME-DEDUP_Foundation_C1_執行.md
.claude-logs/executions/2026-07-10_THEME-DEDUP_Builtin_C2_執行.md
.claude-logs/executions/2026-07-10_THEME-DEDUP_Uploads_C3_執行.md
.claude-logs/executions/2026-07-10_THEME-DEDUP_Guard_C4_執行.md
.claude-logs/executions/2026-07-10_THEME-DEDUP_checkout_執行.md
```
baron commit 前 `git diff --cached --name-only` 須**完全等於**上列（多一少一即停）。⚠️ 工作區另有 `executions/2026-07-09_FE-CSS-GOV_checkout_執行.md` 之 M＝**baron 自有變更、勿混入**（自行另行處理）。

---

## §6 不可動清單遵守

- [x] 收官純治理歸檔 + hash 自癒；零業務碼、零 static/ 觸碰。
- [x] baton 非破壞性歸檔（無同名覆寫）；4 長駐源保留。
- [x] CHECKOUT-GUARD：17 檔逐檔顯式、staged 自檢、baron 自有變更隔離警示。

---

## §7 銜接

- **THEME-DEDUP 全案結案**——主題規格凍結（theme-guide 權威）+ 9 支 conformant + 模板 + 常駐腳本（機器可驗防線）全交付。
- **消化 baton 映射**：plan_v1→plans/、tasks→tasks/、C1–C4 報告→executions/（本 checkout commit 一次性 add）。
- **後續（均另議·不阻結案）**：腳本掛 hook（plan Q_hook 定不掛·先手跑累積經驗）／上傳主題 label 正名+升內建（BE 微任務·`/api/themes` hardcode）／上傳遺留節奏 margin 收斂（theme-guide §11.3 登記在案）。
- ⚠️ **留 baron 瀏覽器總 E2E**：9 主題逐款切換（重點：apple/google chrome re-skin 完好、fuller 虛線、mies 無 byline 底線、kahn 天窗光線、內文間距逐款零變）。

---

## §8 baron 執行命令

```bash
# 1. 搬移歸檔已完成（§3）；checkout 報告已直產 executions/

# 2. git add（17 檔·逐檔顯式；嚴禁 git add . / 廣義 add）
git add .claude-logs/TODO.md .claude-logs/archive/TODO_done_archive.md .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-07-09_THEME-DEDUP_plan_提示詞.md .claude-logs/prompts/2026-07-10_THEME-DEDUP_Tasks_提示詞.md
git add .claude-logs/prompts/2026-07-10_THEME-DEDUP_C1_run_提示詞.md .claude-logs/prompts/2026-07-10_THEME-DEDUP_C2_run_提示詞.md .claude-logs/prompts/2026-07-10_THEME-DEDUP_C3_run_提示詞.md .claude-logs/prompts/2026-07-10_THEME-DEDUP_C4_run_提示詞.md .claude-logs/prompts/2026-07-10_THEME-DEDUP_Check_提示詞.md
git add .claude-logs/plans/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md .claude-logs/tasks/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md
git add .claude-logs/executions/2026-07-10_THEME-DEDUP_Foundation_C1_執行.md .claude-logs/executions/2026-07-10_THEME-DEDUP_Builtin_C2_執行.md .claude-logs/executions/2026-07-10_THEME-DEDUP_Uploads_C3_執行.md .claude-logs/executions/2026-07-10_THEME-DEDUP_Guard_C4_執行.md
git add .claude-logs/executions/2026-07-10_THEME-DEDUP_checkout_執行.md

# 2.5 staged 自檢（== §5 清單 17 檔·多一少一即停）
git diff --cached --name-only

# 3. commit（msg 已備 /tmp/THEME-DEDUP_checkout_msg.txt）
git commit -F /tmp/THEME-DEDUP_checkout_msg.txt
```
