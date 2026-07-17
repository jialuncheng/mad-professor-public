# GOV-PATH-FIX Checkout 執行報告 — 收官與歸檔

| 欄位 | 值 |
|---|---|
| **任務代號** | GOV-PATH-FIX Checkout |
| **執行日期** | 2026-07-12 |
| **依據規劃** | `hotfixes/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md`（本 checkout 一併歸檔） |
| **次級參考** | fix commit `31f7500`；`ref/WORKFLOW_SOP.md §2/§3`（hotfixes/ 歸屬 + 收官 git-add 白名單鐵律 + checkout 執行報告鐵律） |
| **fix Hash** | `31f7500`（已落地） |
| **checkout Hash** | （留空，待 baron commit 後回填） |
| **狀態** | ✅ 全案結案；收官歸檔完成、未自發 commit |

> **hotfix 兩 commit 結構**：本案＝① fix commit `31f7500`（3 治理檔 + 3 .bak）已落地 + ② 本 checkout commit（收官歸檔）。同 SEC-SECRET 先例（`a7fa87f` fix + `14158b6` 收官）。

---

## Conformance 驗收結果

### 目標規格合規性（hotfix 規劃書修法）
| # | 規格項 | 活驗結果 | 狀態 |
|---|---|---|---|
| 1 | template_prompt_for_tasks.md 工作目錄硬規則對齊 CLAUDE.md §3 | `grep 唯一合法工作目錄` → 主 repo `~/mad-professor-public/`（引用 §3） | ✅ 合規 |
| 2 | framework §9.1 重點句去硬編 worktree | 改「主 repo 根目錄（詳見 CLAUDE.md §3、雙視圖）」 | ✅ 合規 |
| 3 | GOVERNANCE_OVERVIEW.md 6 導航連結改相對路徑 | `file:///` 命中 = 0；4 相對目標實檔可解析 | ✅ 合規 |

### 驗收條件合規性（hotfix §regression + §5）
| # | 驗收 | 活驗結果 | 狀態 |
|---|---|---|---|
| 1 | 3 活躍源零殘留 stale worktree | `grep -rln hopeful-yalow-902c50 templates/ ref/` → 空輸出 | ✅ 合規 |
| 2 | GOVERNANCE_OVERVIEW 無死絕對路徑 | `file:///` = 0 | ✅ 合規 |
| 3 | fix commit 含 3 治理檔 + 3 .bak | `git show --stat 31f7500` → 6 files | ✅ 合規 |
| 4 | §5 SOP 一致性核查 | **不適用**（DOC-Refactor 純治理、非後端 logging/database） | ✅ 豁免 |

### 不可動清單合規性
| 項目 | 結果 | 狀態 |
|---|---|---|
| 業務代碼（`.py` / `static/` / `tests/`） | fix commit `git show --stat` 零命中 | ✅ 未觸碰 |
| 歷史檔不溯及既往（hotfixes/executions/plans/tasks/archive 既有 stale） | 64 處刻意保留、本案零改 | ✅ 未觸碰 |
| CLAUDE.md §3（唯一權威源） | 未動（3 下游檔改為對齊/引用之） | ✅ 未觸碰 |

### 特化維度
| 維度 | 結果 |
|---|---|
| 提示詞歸檔稽核 | hotfix + Check 提示詞實體存在；收官階段 `git add` 納入 git（原 untracked） |
| msg.txt 草稿完整性 | hotfix 規劃書 §8 含完整 `cat > /tmp/GOV-PATH-FIX_msg.txt`；本報告 §8 含 checkout msg |
| 跨 Commit 累加分析 | 100% 覆蓋 3 下游引用檔 stale 路徑；零業務碼（DOC-Refactor） |
| §7.2 跨 Phase 整合測試 | 純文件、無 handoff → **顯式豁免** |

### 總結
- 🟢 **全部合規**：已執行收官歸檔動作。

---

## §1 基準與完成狀態

- **基準**：fix commit `31f7500` 之上。
- **完成狀態**：Conformance 三維度活驗全綠 → baton hotfix 規劃書 `mv → hotfixes/` + `git add`；TODO 結案（fix hash `31f7500` 回填、路徑更新 baton→hotfixes/）；hotfix + Check 提示詞 + INDEX `git add`；產本 checkout 執行報告。**未自發 commit**。

---

## §3 變動檔案清單（本 checkout commit）

| 檔案 | 動作 |
|---|---|
| `.claude-logs/hotfixes/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md` | baton `mv` → hotfixes/（歸檔）+ git add |
| `.claude-logs/executions/2026-07-12_GOV-PATH-FIX_checkout_執行.md` | 新增（本報告）+ git add |
| `.claude-logs/TODO.md` | 修改（GOV-PATH-FIX → ✅ 結案·fix hash `31f7500` 回填·路徑 baton→hotfixes/） |
| `.claude-logs/prompts/2026-07-12_GOV-PATH-FIX_hotfix_提示詞.md` | git add（原 untracked） |
| `.claude-logs/prompts/2026-07-12_GOV-PATH-FIX_Check_提示詞.md` | 新增 + git add |
| `.claude-logs/prompts/INDEX.md` | 修改（補 Check 條目 + 最後更新） |

> **雙源 hash 審計**：`archive/TODO_done_archive.md` 無 GOV-PATH-FIX 條目（本 hotfix 記於 TODO.md active 區 ✅、未入 done 歸檔表）→ 無需回填、**不納入本 commit**（其 ` M` 狀態屬他任務遺留）。
> **索引（依類別）**：GOV-PATH-FIX 為一次性治理 hotfix、無既有 `## 索引（依類別）` 分類行 → 以 active 區 ✅ 條目為結案記錄，不新增分類（避免為單一 hotfix 造類）。

---

## §5 staged 白名單自檢（commit 前）

```
$ git diff --cached --name-only
.claude-logs/TODO.md
.claude-logs/executions/2026-07-12_GOV-PATH-FIX_checkout_執行.md
.claude-logs/hotfixes/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md
.claude-logs/prompts/2026-07-12_GOV-PATH-FIX_Check_提示詞.md
.claude-logs/prompts/2026-07-12_GOV-PATH-FIX_hotfix_提示詞.md
.claude-logs/prompts/INDEX.md
```
→ **staged 完全等於宣告 6 檔（無多無少）**；跨任務未追蹤檔（SEC-HARDEN plan/tasks、PROJECT-REVIEW、`archive/TODO_done_archive.md`）未混入。✅

> **判定**：staged 集合須**完全等於**本案宣告 6 檔（§3 + §8 git add 清單之聯集）；跨任務未追蹤檔（SEC-HARDEN plan/tasks 提示詞、PROJECT-REVIEW 提示詞、`archive/TODO_done_archive.md`）**嚴禁混入**（WORKFLOW_SOP §3 白名單鐵律·反例錨 FE-PERF-1 混檔）。多一檔／少一檔即停。

---

## §6 不可動清單遵守

- [x] 業務代碼（`.py` / `static/` / `tests/`）— 100% 未碰
- [x] 歷史檔（hotfixes/executions/plans/tasks/archive 既有 stale 64 處）— 不溯及既往、未動
- [x] CLAUDE.md §3 權威源 — 未動
- [x] baton 長駐檔（QUEUE-1 v2 / PIPE-SPEC / SEC-HARDEN 暫存 / PDF / README）— 未碰

---

## §7 銜接

- **baton 狀態**：GOV-PATH-FIX 暫存檔已全數移出（`ls baton | grep GOV-PATH-FIX` = 0）；長駐檔維持。
- **Audit Trail**：`baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md` → `hotfixes/`（本 checkout commit）。
- **GOV-PATH-FIX 全案結案**：fix `31f7500` + checkout（待 baron 回填）。

---

## §8 baron 執行命令

```bash
# 1. 歸檔與狀態自檢已完成（本報告 §3/§5）

# 2. git add 清單（逐檔顯式，禁 git add .）
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md
git add .claude-logs/executions/2026-07-12_GOV-PATH-FIX_checkout_執行.md
git add .claude-logs/prompts/2026-07-12_GOV-PATH-FIX_hotfix_提示詞.md
git add .claude-logs/prompts/2026-07-12_GOV-PATH-FIX_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/GOV-PATH-FIX_Checkout_msg.txt）
cat > /tmp/GOV-PATH-FIX_Checkout_msg.txt << 'EOF'
docs(governance): GOV-PATH-FIX Checkout — 收官歸檔

1. 執行 Conformance 比對，驗收 template_prompt_for_tasks、framework 及 GOVERNANCE_OVERVIEW 之工作目錄校正。
2. 將暫存於 baton/ 的 hotfix 規劃書移入 hotfixes/ 正式歸檔目錄。
3. 歸檔與稽核本案相關的所有 Prompts 提示詞檔案。
4. 完成 TODO.md 自「進行中」標記為 ✅ 之結案更新，並對 TODO.md 進行 Hash 自癒補填（fix 31f7500）。
5. 產出並保存 checkout 收官執行報告。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/GOV-PATH-FIX_Checkout_msg.txt
```
