# CONTEXT-1 session 載入鏈瘦身與 context 治理 — Tasks

> 本文件為 CONTEXT-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md`（§99.2 v2、九 OQ 全 🟢 定案）計畫產出，含 5 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 7 個 | `archive/TODO_done_archive.md`（C4）/ `baton/2026-07-08_CONTEXT-1_C1~C4_執行.md` ×4 / `executions/2026-07-08_CONTEXT-1_checkout_執行.md`（C5、依 checkout 執行報告鐵律直落 executions/）/ 本 tasks.md；另 `.bak` 審計備份 ×7（C1 ×2 / C2 ×1 / C3 ×3 / C4 ×1、逐列於 §8 各 commit） |
| **修改檔案** | 6 個 | `CLAUDE.md`（C1 §0/§99 + C2 §3/§4）/ `baton/README.md`（C1 按需取用節）/ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（C3 §2.1/§2.4/§2.5+§99.2）/ `templates/template_prompt_for_check.md`（C3 結案雙源）/ `templates/template_prompt_for_run.md`（C3 自癒雙源）/ `TODO.md`（C4 瘦身+a150915 回填；各階段狀態勾稽） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（本階段 🟡 WIP 條目、各 Run 勾稽、C5 結案〔dogfood 新雙層流程〕）/ `prompts/INDEX.md` |
| **Commits** | 5 個 | C1 → C2 → C3 → C4 → C5（checkout） |
| **baton 歸檔** | 1 次 | C5 收官：`mv` plan → `plans/`、tasks → `tasks/`、C1–C4 執行報告 → `executions/` + 逐檔 `git add`；**`context_engineering_governance_audit.md`（規格源）長駐 baton 不歸檔**（同 PIPE-SPEC v8 / QUEUE-1 v2 之 RESCUE-1 Q3 先例） |

---

## §1 TL;DR（概要）

- **挑戰**：session 啟動 @path 鏈灌入 ~2,140 行 + baton 7 檔 130,356 bytes，TODO.md 73.6% 為已完成考古、wildcard 無差別全載 → context rot + 快取失效代價高；FRAMEWORK §2.1「不另外分檔」與瘦身正面衝突、CLAUDE.md §3/§4 指向已刪除 worktree（stale）、pre_tool_guard 必攔大幅縮減。
- **解法**：五個最小可逆原子 commit，「憲法先行、動作在後」——C1 — Loading Chain Convergence（載入鏈收斂）→ C2 — Workdir Stale Fix（工作目錄修正）→ C3 — Lifecycle Rules Sync（生命週期規則同步）→ C4 — TODO Slimming（TODO 瘦身歸檔）→ C5 — Checkout（收官歸檔）。
- **影響範圍**：100% DOC-Refactor、零業務代碼（`*.py` / `static/` / `tests/` 零 diff）、零 runtime。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `CLAUDE.md` | L12 `@.claude-logs/baton/*.md` wildcard；L89（§3）/ L123（§4）指向已刪除 worktree `hopeful-yalow-902c50`；§99.1 無載入排序約束 | C1 收斂 wildcard + 排序原則；C2 修 stale 工作目錄（雙視圖） |
| `TODO.md` | 1,419 行；`## ✅ 已完成` L12–L1056（1,045 行、73.6%）；256 個去重 7 碼 hash 全在此區；RESCUE-1 C5 hash「待 baron 回填」佔位符 | C4 瘦身至 ≤450 行 + 一行式索引 + 回填 `a150915` |
| `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` | §2.1（L33）明文「不另外分檔」；§2.4/§2.5 寫入/歸檔規則指 TODO 頂部表格 | C3 改雙層表述 + 寫入規則改指歸檔檔 |
| `templates/template_prompt_for_check.md` | L137–153 TODO 結案寫「✅ 已完成區塊新增完成表格」+ 全量 hash 自癒掃 TODO 頂部 | C3 改雙源（索引行 + 歸檔檔） |
| `templates/template_prompt_for_run.md` | L92–96 hash 自癒佔位符掃描指 TODO | C3 同步雙源 |
| `baton/README.md` | 無「按需取用」說明（wildcard 時代不需要） | C1 補一節 |
| `archive/TODO_done_archive.md` | 不存在 | C4 新建（承接已完成區 byte 逐字） |

---

## §3 觀察問題

### 問題 #1：TODO 已完成區＝pre-retrieval 反模式（plan §3）
- **證據**：`TODO.md` L12–L1056（1,045 行/73.6%）每 session 全載；內容可由 git log + executions/ 還原
- **影響**：context rot（鐵律被歷史淹沒）+ 每次 TODO 更新使其後全部快取失效、重建成本高

### 問題 #2：baton wildcard 抵銷 filesystem offload 設計（plan §3）
- **證據**：`CLAUDE.md:12` wildcard；baton 7 檔 130,356 bytes（含 44,988 bytes PIPE-SPEC 長駐規格書）全數灌入與任務無關之 session
- **影響**：按需取用機制被強制推送取代、stale/無關內容污染注意力

### 問題 #3：FRAMEWORK §2.1 憲法衝突 + CLAUDE.md §3/§4 stale（plan §3）
- **證據**：`PROJECT_PROGRESS_CONTROL_FRAMEWORK.md:33`「不另外分檔」；`CLAUDE.md:89/:123` 指向已刪除 worktree
- **影響**：不先改憲法則瘦身即違規；工作目錄權威源指向不存在目錄＝治理債

---

## §4 設計方案

拆分主軸＝「**憲法先行、動作在後**」：先收斂載入端與修 stale（C1/C2、彼此獨立、各自可 revert），再改生命週期規則（C3），規則生效後才執行 TODO 物理瘦身（C4 依賴 C3），最後 checkout（C5）。

### §4.1 C1 — Loading Chain Convergence（載入鏈收斂）
CLAUDE.md §0 wildcard→僅 README（plan U3/Q4）+ §99.1 約束事項補「靜態優先、動態靠後」排序原則（U5/Q5）+ §99.2 v4；baton/README.md 補「按需取用」一節。

### §4.2 C2 — Workdir Stale Fix（工作目錄修正）
CLAUDE.md §3 L89 唯一合法工作目錄改主 repo 雙視圖寫法 + §4 L123 同步表列同步（U7/Q9）+ §99.2 v5。**tasks 級銳化**：§3 首 bullet「嚴禁讀寫主 repo 目錄（worktree 父目錄）」與新主值直接矛盾（plan U7 未列、grep 附帶發現），一併改為「嚴禁讀寫授權範圍外檔案（授權範圍由各任務 plan/tasks 工作目錄條款定義）」——與 U7 既有「待 baron 階段 3 確認」標記同批送驗。

### §4.3 C3 — Lifecycle Rules Sync（生命週期規則同步）
FRAMEWORK §2.1 改「單一入口（雙層結構）」表述、§2.4/§2.5 寫入與歸檔規則改指 `archive/TODO_done_archive.md` + §99.2 v5（U4/Q7）；`template_prompt_for_check.md` TODO 結案段與 `template_prompt_for_run.md` hash 自癒段改雙源。規則與模板同 commit 原子落地、消不一致窗口。

### §4.4 C4 — TODO Slimming（TODO 瘦身歸檔）
cp .bak → 新建 `archive/TODO_done_archive.md`（byte 逐字承接 L12–L1056）→ TODO 主檔已完成區改一行式索引（Q3 格式）+ RESCUE-1 C5 hash 回填 `a150915`（Q1）+ 頂部說明對齊雙層結構；pre_tool_guard 以 sentinel 夾帶放行、事後移除不殘留（Q6 銳化）。依賴 C3。

### §4.5 C5 — Checkout（收官歸檔）
Conformance 五維度 + §7.2 純 DOC 顯式豁免（Q8）+ baton 一次性歸檔 + TODO 結案（**dogfood C3 新雙層流程**：一行索引入 TODO + 完整表格追加歸檔檔）+ checkout 執行報告鐵律（staged 自檢輸出）+ hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C4 搬移期 TODO 半殘 / hash 損毀 | 🔴 高 | 改前 `cp → archive/*.bak`；搬移+索引+回填單一 commit 原子完成；§6.4 hash 集合 diff（唯一容許差異 `+a150915`） |
| pre_tool_guard deny C4 大幅縮減 | 🟡 中 | sentinel 夾帶於 Write 內容放行 → 後續小 Edit 移除（old_string 含 sentinel 自然放行）；執行報告記載事由（plan Q6 銳化） |
| C1 載入行改壞 → 新 session 缺載 | 🟡 中 | §6.1 grep 驗證 @path 五行完整；E2E 新 session 實測列 baron 驗收 |
| C3 規則/模板不同步窗口 | 🟡 中 | FRAMEWORK + 兩模板同 commit 原子落地；§6.3 grep 三檔皆無舊表述殘留 |
| C2 §3 首 bullet 矛盾（tasks 級銳化超 plan 字面） | 🟡 中 | 於 C2 執行報告顯著標記 deviation、與 U7 同批交 baron 階段 3 確認；被否決則單獨 revert C2 |
| Antigravity 掃描 / 外部引用斷鏈 | 🟢 低 | 歸檔檔為 tracked `.claude-logs/*.md` 仍在掃描範圍；索引行留 pointer |
| 快取一次性全失效 | 🟢 低 | 一次性成本；此後失效面由 1,419 行縮至 ≤450 行 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "@\.claude-logs" CLAUDE.md
# 期望：仍 4 行；含 "baton/README.md"、不含 "baton/\*"
grep -n "靜態規範優先" CLAUDE.md            # 期望：§99.1 約束事項命中 1
grep -n "按需取用" .claude-logs/baton/README.md   # 期望：命中 ≥1
grep -c "v4 (2026-07-08)" CLAUDE.md          # 期望：1（§99.2 Revision）
wc -l CLAUDE.md                              # 期望：≤200（§99.1 約束）
```

### §6.2 C2 驗收

```bash
grep -n "hopeful-yalow" CLAUDE.md            # 期望：無命中（§3+§4 雙處清零）
grep -n "OrbStack/claude-lab" CLAUDE.md      # 期望：§3 命中（Mac 視圖）
grep -n "嚴禁讀寫主 repo 目錄" CLAUDE.md     # 期望：無命中（矛盾 bullet 已改）
grep -c "v5 (2026-07-08)" CLAUDE.md          # 期望：1
```

### §6.3 C3 驗收

```bash
grep -n "不另外分檔" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
# 期望：無命中（改為「單一入口（雙層結構）」）
grep -n "TODO_done_archive" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md \
  .claude-logs/templates/template_prompt_for_check.md \
  .claude-logs/templates/template_prompt_for_run.md
# 期望：三檔皆命中（雙源規則落地）
grep -n "Conformance" .claude-logs/templates/template_prompt_for_check.md | head -3
# 期望：既有五維度結構未動（CHECKOUT-GUARD/WORKFLOW-4 條款零改）
```

### §6.4 C4 驗收

```bash
wc -l .claude-logs/TODO.md                          # 期望：≤450
wc -l .claude-logs/archive/TODO_done_archive.md     # 期望：≥1,000
diff <(grep -oE '[0-9a-f]{7}' .claude-logs/archive/2026-07-08_CONTEXT-1_C4_TODO.md.bak | sort -u) \
     <(cat .claude-logs/TODO.md .claude-logs/archive/TODO_done_archive.md | grep -oE '[0-9a-f]{7}' | sort -u)
# 期望：僅一行 "> a150915"（Q1 回填新增）、零 "<"（零刪失）
grep -c "BYPASS_TRUNCATION_GUARD" .claude-logs/TODO.md   # 期望：0（sentinel 不殘留）
grep -c "待 baron 回填" .claude-logs/TODO.md .claude-logs/archive/TODO_done_archive.md
# 期望：兩檔皆 0（a150915 已回填）
grep -n "→ archive/TODO_done_archive.md" .claude-logs/TODO.md | head -3   # 期望：索引行 pointer 命中
```

### §6.5 C5 驗收（checkout）

```bash
ls .claude-logs/baton/
# 期望：僅 README.md + context_engineering_governance_audit.md（長駐）+ PIPE-SPEC + QUEUE-1 v2（長駐）+ 2604.10352v1.pdf 等既有長駐；plan/tasks/C1-C4 執行報告已 mv
ls .claude-logs/plans/ | grep CONTEXT-1 && ls .claude-logs/tasks/ | grep CONTEXT-1
ls .claude-logs/executions/ | grep CONTEXT-1        # 期望：C1-C4 + checkout 共 5 份
git diff --cached --name-only                        # 期望：＝checkout 報告 §8 白名單（多/少一檔即停）
git diff --stat -- '*.py' static/ tests/             # 期望：空（零業務波及）
pytest tests/ -v 2>&1 | tail -3                      # 期望：與基線一致（唯一既知 flake＝LOG_FORMAT env）
```

---

## §7 不可動清單

- [ ] **業務代碼**：`*.py` / `static/` / `tests/` — 100% 不動（pytest 基線為證）
- [ ] `CLAUDE.md` §1 / §2 / §5 規範本體 — 僅動 §0 載入行（C1）、§3/§4 工作目錄（C2）、§99（C1/C2 Revision）
- [ ] `ref/WORKFLOW_SOP.md` 整檔 — 零觸碰
- [ ] FRAMEWORK 除 §2.1/§2.4/§2.5/§99.2 外全部章節（§1 心法/§3 編碼/§4 日誌契約/§5–§9）— 零觸碰
- [ ] `TODO.md`「🟡 進行中」「索引（依類別）」「🗑️ 遺失清單」三區 — 內容逐字不動（唯 CONTEXT-1 自身狀態勾稽 + Q1 授權之 a150915 回填例外）
- [ ] 已完成區表格與註解**內容 byte** — 搬移非改寫、hash 零增刪（僅 +a150915）
- [ ] `baton/` 檔案實體 — 零刪除、零搬移（README 補節例外；PIPE-SPEC/QUEUE-1/audit 長駐地位不動；C5 收官歸檔屬鐵律例外）
- [ ] `.gitignore` baton 規則（`baton/*` + `!baton/README.md`）— 零觸碰
- [ ] 兩模板既有結構（Conformance 五維度 / 三防線 / staged 自檢 / WORKFLOW-4 U1-U5 markers）— 僅動 TODO 結案與 hash 自癒措辭段
- [ ] `prompts/` 既有歸檔 — 零觸碰（僅 INDEX 追加）

---

## §8 推薦 Commit 拆分

### C1 — Loading Chain Convergence（載入鏈收斂）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `CLAUDE.md`、`baton/README.md`；備份：`archive/2026-07-08_CONTEXT-1_C1_CLAUDE.md.bak`、`archive/2026-07-08_CONTEXT-1_C1_baton_README.md.bak` |
| **安全性** | 🟢 高 — 純載入配置與說明文件、零 runtime；wildcard 收斂即刻生效於下個 session |
| **可逆性** | 🟢 高 — `git revert` 單 commit 完整恢復 wildcard 與舊 README |
| **驗收 grep 條件** | 本檔 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `cp CLAUDE.md .claude-logs/archive/2026-07-08_CONTEXT-1_C1_CLAUDE.md.bak`、`cp .claude-logs/baton/README.md .claude-logs/archive/2026-07-08_CONTEXT-1_C1_baton_README.md.bak`；② `CLAUDE.md:12` `@.claude-logs/baton/*.md` → `@.claude-logs/baton/README.md`（U3/Q4）；③ §99.1「約束事項」cell 現值「嚴禁含動態內容（當前任務名 / hash / 變動數字）；≤ 200 行」尾端追加「；§0 @path 引用順序：靜態規範優先、動態狀態靠後（最大化 prefix cache 命中）」（U5/Q5）；④ §99.2 追加 `- v4 (2026-07-08)：CONTEXT-1 C1——§0 baton wildcard 收斂為僅 README（按需取用、audit 優先矩陣 #2）+ §99.1 補 @path 靜態優先動態靠後排序原則（#3）`；⑤ `baton/README.md` 於既有末節之後新增一節「按需取用（CONTEXT-1）」：說明 baton 檔案自此不被 @path 自動全載、任務檔由該任務提示詞顯式指路、臨時查閱以 ls/grep/Read 按需取；長駐檔（PIPE-SPEC / QUEUE-1 v2 / 稽核源文件）依 RESCUE-1 Q3 續駐；既有 §1–§3（3-Phase / 部署 SOP）內容零改、節次編號依實際檔案順延；⑥ Run 產 `baton/2026-07-08_CONTEXT-1_C1_執行.md`（template_execution、§8 git add 白名單含 2 `.bak`） |

### C2 — Workdir Stale Fix（工作目錄修正）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `CLAUDE.md`（§3 L89 主值行 + §3 首 bullet + §4 L123 表列 + §99.2）；備份：`archive/2026-07-08_CONTEXT-1_C2_CLAUDE.md.bak`（C1 後基準） |
| **安全性** | 🟢 高 — 純治理文字；不改任何授權邏輯之外的規範 |
| **可逆性** | 🟢 高 — `git revert` 單 commit；與 C1 hunk 不重疊（§0/§99.1 vs §3/§4） |
| **驗收 grep 條件** | 本檔 §6.2 |
| **依賴關係** | C1（僅 .bak 基準順序、無邏輯依賴；可獨立 revert） |
| **具體實作細節** | ① `cp CLAUDE.md .claude-logs/archive/2026-07-08_CONTEXT-1_C2_CLAUDE.md.bak`；② L89 `**唯一合法工作目錄**：\`.claude/worktrees/hopeful-yalow-902c50/\`` → `**唯一合法工作目錄**：主 repo 根目錄 \`~/mad-professor-public/\`（Server 視圖 \`/home/baroncheng/mad-professor-public\`；Mac OrbStack 視圖 \`/Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public\`）`（U7/Q9 雙視圖）；③ §3 首 bullet「嚴禁讀寫主 repo 目錄（worktree 父目錄）」→「嚴禁讀寫授權範圍外檔案（授權範圍由各任務 plan / tasks 工作目錄條款定義）」（**tasks 級銳化**，見 §4.2、C2 執行報告標 deviation 交 baron 確認）；④ §3 其餘 bullet（嚴禁改動業務代碼 / 違規 revert / baton 暫存）逐字不動；⑤ §4 表 L123 `| Claude Code Server worktree | \`~/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/\` | gemini-refactor |` → `| Claude Code Server（主 repo 就地） | \`~/mad-professor-public/\` | gemini-refactor |`；⑥ §99.2 追加 `- v5 (2026-07-08)：CONTEXT-1 C2——§3 工作目錄由已刪除 worktree 更新為主 repo 雙視圖 + §3 首 bullet 授權範圍化 + §4 同步表列同步（U7/Q9）`；⑦ Run 產 `baton/2026-07-08_CONTEXT-1_C2_執行.md` |

### C3 — Lifecycle Rules Sync（生命週期規則同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`、`templates/template_prompt_for_check.md`、`templates/template_prompt_for_run.md`；備份：`archive/2026-07-08_CONTEXT-1_C3_framework.md.bak`、`archive/2026-07-08_CONTEXT-1_C3_check模板.md.bak`、`archive/2026-07-08_CONTEXT-1_C3_run模板.md.bak` |
| **安全性** | 🟡 中 — 動生命週期憲法與 checkout 流程模板；規則+模板同 commit 原子落地消不一致窗口 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 恢復舊規則；C4 未跑前 revert 零副作用 |
| **驗收 grep 條件** | 本檔 §6.3 |
| **依賴關係** | 無前置（邏輯上須先於 C4） |
| **具體實作細節** | ① 三檔各 `cp → archive/*.bak`；② FRAMEWORK §2.1（L33）「**不另外分檔**：待辦清單與已完成清單統一整合維護於 `TODO.md` 中。…」→「**單一入口（雙層結構）**：active 任務（⬜/🔵/🟡）單檔維護於 `TODO.md`（SSOT 入口不變）；已完成任務（✅）以一行式索引留存 TODO.md、完整成果表格與註解歸檔於 `archive/TODO_done_archive.md`（tracked）——單一入口 + pointer 保留交叉對照、防歷史膨脹吞噬注意力預算」（Q7 雙層表述）；③ §2.4 已完成清單寫入規則：表格範例保留、寫入目的地改「追加至 `archive/TODO_done_archive.md` 對應主題表格」+ 補 Q3 索引行格式定義 `- ✅ <代號> <主題>（<首hash>…<末hash>、N commits）→ archive/TODO_done_archive.md`；④ §2.5 生命週期第 2–4 點：「從下方列表移除」不變、「追加寫入至頂部 ✅ 表格」→「完整表格追加 `archive/TODO_done_archive.md` + TODO.md ✅ 區新增一行索引」、「類別索引更新」不變；⑤ FRAMEWORK §99.2 追加 v5 Revision；⑥ `template_prompt_for_check.md` L137–153：結案步驟 1「在 ✅ 已完成區塊新增完成表格」→「完整表格追加 `archive/TODO_done_archive.md` + TODO.md ✅ 區新增一行索引（Q3 格式）」、L153 全量 hash 自癒掃描對象「TODO.md 頂部已完成任務」→「TODO.md 索引行 + `archive/TODO_done_archive.md`」；⑦ `template_prompt_for_run.md` L92–96 hash 自癒佔位符掃描對象同步雙源；⑧ 兩模板其餘結構（Conformance 五維度 / 三防線 / staged 自檢 / StraTA markers）零改；⑨ Run 產 `baton/2026-07-08_CONTEXT-1_C3_執行.md`（§8 git add 含 3 `.bak`） |

### C4 — TODO Slimming（TODO 瘦身歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`、新建 `archive/TODO_done_archive.md`；備份：`archive/2026-07-08_CONTEXT-1_C4_TODO.md.bak` |
| **安全性** | 🟡 中 — 動 SSOT 本體；byte 逐字搬移 + hash 集合 diff 雙保險；pre_tool_guard sentinel 程序化通行 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 恢復完整 TODO；`.bak` 為第三重保險 |
| **驗收 grep 條件** | 本檔 §6.4 |
| **依賴關係** | C3（生命週期規則須先生效，瘦身才合憲） |
| **具體實作細節** | ① `cp .claude-logs/TODO.md .claude-logs/archive/2026-07-08_CONTEXT-1_C4_TODO.md.bak`；② 新建 `archive/TODO_done_archive.md`：檔頭（標題「Mad Professor — TODO 已完成歸檔（Done Archive）」+ 說明〔依 FRAMEWORK §2.1 雙層結構、來源＝TODO.md L12–L1056、CONTEXT-1 C4 建檔、日期〕）+ **byte 逐字貼入原 `## ✅ 已完成` 區全部內容（L13–L1056）**；③ 於歸檔檔內 RESCUE-1 C5 列將「待 baron 回填」→ `a150915`（Q1 授權、唯一內容級改動）；④ `TODO.md` 以 Write 重寫：頂部說明對齊雙層結構（「已完成索引見下、完整表格 → archive/TODO_done_archive.md」）+ `## ✅ 已完成（索引）` 區＝每任務一行 Q3 格式（依原區 `###` 標題逐任務萃取：代號、主題、該任務首末 commit hash、`→ archive/TODO_done_archive.md`）+ 「🟡 進行中」「索引（依類別）」「🗑️ 遺失清單」三區逐字保留；**Write 內容夾帶 `<!-- BYPASS_TRUNCATION_GUARD: CONTEXT-1 C4 有意瘦身（plan Q6） -->` 註解行**（pre_tool_guard 放行）；⑤ 隨即 Edit 移除該 sentinel 行（old_string 含 sentinel、自然放行；TODO 最終零殘留）；⑥ 跑 §6.4 全部驗收（wc / hash diff 唯一 `+a150915` / sentinel 0 / 佔位符 0 / pointer 命中）；⑦ Run 產 `baton/2026-07-08_CONTEXT-1_C4_執行.md`（記載 sentinel 使用事由、§8 git add 含 `.bak` + 歸檔檔 + TODO.md） |

### C5 — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton→正式目錄（plan → `plans/`、本 tasks → `tasks/`、C1–C4 執行報告 → `executions/`）、新建 `executions/2026-07-08_CONTEXT-1_checkout_執行.md`、`TODO.md`（CONTEXT-1 結案）、`prompts/INDEX.md`、msg 草稿 `/tmp/CONTEXT-1_C5_msg.txt` |
| **安全性** | 🟢 高 — 純歸檔與狀態結案；git-add 白名單鐵律 + staged 自檢 |
| **可逆性** | 🟢 高 — `git revert` 恢復 baton 暫存態 |
| **驗收 grep 條件** | 本檔 §6.5 |
| **依賴關係** | C1–C4 全部 ship 完畢（WORKFLOW_SOP §3：所有 commit ship 完才跑階段 5/6） |
| **具體實作細節** | ① Conformance 五維度驗收：目標規格 plan U1–U7 逐項實檔複驗（含 C2 tasks 級銳化與 U7 §4 附帶項之 baron 確認結果）/ tasks §6.1–§6.5 全部重跑貼輸出 / 不可動清單 §7 逐項 git diff 證據 / 提示詞稽核（plan、plan_v2、Tasks、C1–C4 run、Check 全數入 git）/ msg 草稿完整性；② §7.2 純 DOC-Refactor 顯式豁免聲明（Q8、同 WORKFLOW-3/4/5、RESCUE-1 先例）；③ baton 一次性歸檔：`mv` plan_v1 → `plans/`、本 tasks → `tasks/`、C1–C4 執行報告 → `executions/`；**`context_engineering_governance_audit.md` 長駐 baton 不歸檔**（規格源、RESCUE-1 Q3 同型先例）；④ TODO 結案 **dogfood C3 新流程**：CONTEXT-1 自「🟡 進行中」移除 → 完整成果表格追加 `archive/TODO_done_archive.md` → TODO.md ✅ 索引區加一行（Q3 格式、hash 待 baron 回填後自癒）→ 類別索引同步；⑤ 依 checkout 執行報告鐵律產 `executions/2026-07-08_CONTEXT-1_checkout_執行.md`（含 Conformance 結果 + `git diff --cached --name-only` staged 自檢實貼 + baton 歸檔確認 + §8 一行 commit）；⑥ commit msg 草稿寫 `/tmp/CONTEXT-1_C5_msg.txt`；git add 逐檔顯式白名單（嚴禁 `git add .`/`-A`/`<目錄>`）、staged 集合＝宣告清單、多/少一檔即停 |

---

## §9 Open Questions

無。（plan §9 九 OQ 已於 2026-07-07 全數 🟢 定案；唯二執行期銳化——C2 §3 首 bullet 矛盾修正、U7 §4 表附帶同步——依 plan 既定機制標記於執行報告、由 baron 階段 3/5 驗證時確認，不阻塞執行。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 CONTEXT-1 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 CONTEXT-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push`；各 Run 產出暫存 baton/、C5 才歸檔 |
| **改版觸發條件** | 任務計畫（plan）規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 中的全局規格與五文獻論證，不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-08)：初版拆分完成——5 commits（C1 載入鏈收斂 / C2 工作目錄修正〔含 §3 首 bullet 矛盾之 tasks 級銳化〕/ C3 生命週期規則同步〔FRAMEWORK+兩模板原子落地〕/ C4 TODO 瘦身歸檔〔sentinel 程序 + hash 集合全等〕/ C5 Checkout）；依 plan §99.2 v2 九 OQ 定案
