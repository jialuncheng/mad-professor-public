# CONTEXT-1 session 載入鏈瘦身與 context 治理 plan

> 依 `baton/context_engineering_governance_audit.md`（五文獻稽核、2026-07-07 Review 版）落地其優先矩陣 #1/#2/#3：TODO.md 已完成區瘦身、`@baton/*.md` wildcard 收斂、載入排序原則明文化——降低每 session 啟動之 context 載入量與快取失效成本，SSOT 地位與六階段流程零改。純 DOC-Refactor、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：CLAUDE.md §0 之 @path 自動載入鏈每 session 灌入 ~2,140 行規範/狀態 + baton 全部 .md ~127KB；其中 TODO.md 1,419 行有 73.6%（L12–L1056）為已完成歷史考古、baton wildcard 把 44KB 長駐規格書（PIPE-SPEC）與待拍板稽核檔全數灌入——高噪訊比造成 context rot（鐵律條款被歷史淹沒）、且 TODO.md 每次狀態更新使其後全部快取失效、重建成本高。
- **解法**：① TODO.md「✅ 已完成」區整區逐字搬移至非 @path 之 tracked 歸檔檔、主檔改留一行式索引；② CLAUDE.md §0 `@.claude-logs/baton/*.md` 收斂為 `@.claude-logs/baton/README.md`；③ @path「靜態優先、動態靠後」排序原則明文化；④ 同步改版 FRAMEWORK §2.1/§2.4/§2.5 生命週期規則與兩份下游模板之 TODO 結案/hash 自癒措辭（消 doc-drift）。
- **影響**：`CLAUDE.md`（§0 載入行 + §3 工作目錄值 + §4 同步表列 + §99）、`.claude-logs/TODO.md`、新增 `archive/TODO_done_archive.md`、`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§2.1/§2.4/§2.5 + §99.2）、`templates/template_prompt_for_check.md` 與 `templates/template_prompt_for_run.md`（措辭同步）、`baton/README.md`（按需取用說明）。零 .py / 零 static/ / 零 runtime 影響。

---

## §2 目標規格

- **U1（TODO 主檔瘦身）**：`TODO.md` 主檔 ≤ 450 行；「✅ 已完成」區改為**一行式索引**，格式定案（Q3 🟢）：`- ✅ <代號> <主題>（<首hash>…<末hash>、N commits）→ archive/TODO_done_archive.md`；「🟡 進行中」「索引（依類別）」「🗑️ 遺失清單」三區內容**逐字不動**（唯一例外：RESCUE-1 C5 佔位符「待 baron 回填」依 Q1 🟢 授權回填為 `a150915`）；TODO.md 之 SSOT 地位（FRAMEWORK §2.1）經 U4 改版後維持成立。
- **U2（歸檔檔完整性）**：新建 tracked 歸檔檔 **`archive/TODO_done_archive.md`**（Q2 🟢 定案：無日期前綴之滾動累積檔、非 @path 目錄），承接「✅ 已完成」區**全部表格與註解區塊、byte 逐字搬移**；搬移前後之 7 碼 hash 去重集合**完全相等**（基準 256 個 + Q1 回填之 `a150915`＝257 個、全部位於已完成區，見 §3.1）；搬移＝移動非改寫、hash 零刪改。
- **U3（baton wildcard 收斂）**：`CLAUDE.md:12` 之 `@.claude-logs/baton/*.md` 改為 `@.claude-logs/baton/README.md`；baton 目錄與其內所有檔案**實體零觸碰**（零刪除、零搬移；PIPE-SPEC v8 / QUEUE-1 v2 依 RESCUE-1 Q3 定案續長駐）；`baton/README.md` 補一節「按需取用」說明（檔案由任務提示詞顯式指路或 ls/grep 檢索、不再自動全載）。
- **U4（生命週期規則同步）**：FRAMEWORK **§2.1「不另外分檔」原則改版**為「active 單檔 SSOT + 完成史歸檔」雙層表述、**§2.4/§2.5** 已完成寫入/歸檔搬移規則改指歸檔檔（一行索引入 TODO + 完整表格追加歸檔檔）+ §99.2 Revision；`template_prompt_for_check.md`（L137–153 TODO 結案段）與 `template_prompt_for_run.md`（L92–96 hash 自癒段）措辭同步（hash 自癒之掃描對象＝TODO 索引行 + 歸檔檔）。
- **U5（載入排序原則明文化）**：於 **CLAUDE.md §99.1「約束事項」欄**（Q5 🟢 定案）補「@path 引用順序：靜態規範優先、動態狀態靠後（最大化 prefix cache 命中）」+ §99.2 Revision。
- **U6（總量與零波及驗證）**：載入鏈實測下降——TODO.md −約 1,000 行、baton 自動載入由 130,356 bytes（7 檔）降至 7,408 bytes（僅 README）；CLAUDE.md §1/§2/§5 規範本體、WORKFLOW_SOP.md 整檔、業務代碼與測試零 diff；pytest 全套件基線不變。
- **U7（工作目錄 stale 修正）**：CLAUDE.md §3（L89）「唯一合法工作目錄」由已刪除之 `.claude/worktrees/hopeful-yalow-902c50/` 更新為**主 repo 根目錄**（Q9 🟢 授權），採**環境中立雙視圖寫法**：主值 `~/mad-professor-public/`、註記 Server 視圖 `/home/baroncheng/mad-professor-public` 與 Mac OrbStack 視圖 `/Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public`（baron 給定值）；**§4 跨環境同步表（L123）同一 stale worktree 列一併同步**（本項超出 Q9 字面授權、係 grep 附帶發現，標記待 baron 階段 3 驗證確認）；§3 其餘條款（嚴禁動業務代碼、baton 暫存、違規 revert 權）逐字不動 + §99.2 Revision。

### §2.5 候選方案（Diverse Rollout）（選用）

單一方案，無多方案需求（低風險純文件搬移 + 載入行改動；歸檔檔落點、索引行格式、排序原則落點等**參數級**選項已逐一列 §9 Open Questions 交 baron 拍板，非架構級分歧）。

---

## §3 現況與證據

- **CLAUDE.md §0（L9–L12）**：四行 @path 自動載入——`ref/WORKFLOW_SOP.md`（238 行、靜態）→ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（322 行、靜態）→ `TODO.md`（1,419 行、動態）→ `baton/*.md`（wildcard、動態）。排序恰為「靜態前、動態後」，但無明文約束（U5 補）。
- **TODO.md（1,419 行）**：`## ✅ 已完成` L12–L1056（1,045 行、73.6%）；`## 🟡 進行中` L1057；`## 索引（依類別）` L1253；`## 🗑️ 遺失清單` L1403。已完成區含 256 個去重 7 碼 hash（全檔 hash 亦僅存在於此區）。
- **baton/（wildcard 實際灌入量）**：7 支 .md 共 130,356 bytes——PIPE-SPEC v8 44,988（RESCUE-1 C2 重建、Q3 長駐）/ frontend_browser_standards_audit 24,040 / context_engineering_governance_audit 22,845 / frontend_css_governance_audit 14,597 / QUEUE-1 v2 9,890（Q3 長駐）/ README 7,408 / file_governance_improvement_plan 6,588。另 `2604.10352v1.pdf` 692.8K 非 .md 不受 wildcard 影響。
- **RESCUE-1 狀態**：已全案收官（C5 `a150915` 已 commit；MODEL-10 殘留已 C3 `1df608a` mv→archive/；RESCUE-1 plan/tasks 已歸檔 plans//tasks/）——本案與 RESCUE-1 C4 之 TODO 撞檔風險**已消滅**；僅 TODO 內 C5 hash「待 baron 回填」一處佔位符未結（§9 Q1）。
- **規格衝突點（本案必須同步處理）**：FRAMEWORK §2.1 明文「**不另外分檔**：待辦清單與已完成清單統一整合維護於 TODO.md 中」——與 U1/U2 分檔歸檔正面衝突，故 U4 將其納入改版範圍；`template_prompt_for_check.md` L137–153 與 `template_prompt_for_run.md` L92–96 引用「✅ 已完成表格」寫入/自癒流程，屬同一同步範圍。
- **守衛交互**：WORKFLOW-5 C4 之 `tools/pre_tool_guard.sh`（PreToolUse）保護 TODO.md 免於「>50% 且 >50 行」截斷——U1 瘦身幅度（−73.6%）**必然觸發 deny**，須依其設計之 sentinel 減速帶通行；經讀實作（`pre_tool_guard.sh:39-41`）確認 sentinel 判定對象＝**Write/Edit 呼叫之 tool_input 內容**（content/new_string/old_string），非檔案本體——故通行手法定案（Q6 🟢 銳化）：瘦身寫入時夾帶 `<!-- BYPASS_TRUNCATION_GUARD: CONTEXT-1 有意瘦身 -->` 註解行放行、隨後小 Edit 移除該行（其 old_string 含 sentinel、自然放行），TODO.md 最終**不殘留**標記；執行報告記載事由。
- **工作目錄 stale（U7 標的）**：CLAUDE.md L89（§3 唯一合法工作目錄）與 L123（§4 同步表）均指向已刪除之 worktree `hopeful-yalow-902c50`（RESCUE-1 動因遺留）；Q9 🟢 授權更新為主 repo。
- **規格來源**：`baton/context_engineering_governance_audit.md` §1/§2/§8 + 優先矩陣 #1/#2/#3（本 plan 為其唯一落地載體；矩陣 #4 FE 視覺自檢＝條件觸發 backlog、#5 產品 RAG＝不做，均不在本案）。

### §3.1 grep 鋼鐵證據

```bash
# @path 載入鏈（CLAUDE.md）
$ grep -n "@\.claude-logs" CLAUDE.md
9:@.claude-logs/ref/WORKFLOW_SOP.md
10:@.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
11:@.claude-logs/TODO.md
12:@.claude-logs/baton/*.md

# TODO.md 體量與分區
$ wc -l .claude-logs/TODO.md
1419
$ grep -n "^## " .claude-logs/TODO.md
12:## ✅ 已完成
1057:## 🟡 進行中 / ⬜ 未開始（依優先序）
1253:## 索引（依類別）
1403:## 🗑️ 2026-06 worktree 刪除遺失清單（RESCUE-1 C4 審計）

# baton wildcard 實灌量（7 支 .md）
$ du -b -c .claude-logs/baton/*.md | tail -1
130356	total

# hash 完整性基準（全檔 256 個、全數位於已完成區 L12–L1056）
$ grep -oE '[0-9a-f]{7}' .claude-logs/TODO.md | sort -u | wc -l          # → 256
$ sed -n '12,1056p' .claude-logs/TODO.md | grep -oE '[0-9a-f]{7}' | sort -u | wc -l   # → 256

# FRAMEWORK 衝突條款與下游模板引用
$ grep -n "不另外分檔" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
33:- **不另外分檔**：待辦清單與已完成清單統一整合維護於 `TODO.md` 中。…
$ grep -rn "✅ 已完成" .claude-logs/templates/template_prompt_for_check.md | head -2
139:1. 在 `## ✅ 已完成` 區塊，依任務類型新增完成表格：

# CLAUDE.md stale worktree（U7 標的、兩處）
$ grep -n "worktrees\|hopeful" CLAUDE.md
89:**唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
123:| Claude Code Server worktree | `~/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/` | …

# pre_tool_guard sentinel 判定對象＝tool_input 非檔案本體（Q6 銳化依據）
$ sed -n '39,41p' .claude-logs/tools/pre_tool_guard.sh
    blob = " ".join(str(ti.get(k, "")) for k in ("content", "new_string", "old_string"))
    if SENTINEL in blob:
        sys.exit(0)
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無**——純 DOC-Refactor、僅治理文件與模板、無任何程式模組間資料 handoff。§7.2 跨 Phase 整合測試依 WORKFLOW_SOP §7.2 於 §9 Q8 顯式申請豁免（同 WORKFLOW-3/4/5、RESCUE-1、CHECKOUT-GUARD 先例）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| TODO.md 搬移期半殘 / hash 損毀（SSOT 破壞） | 🔴 高 | 改前 `cp TODO.md → archive/*.bak`（RESCUE-1 C4 先例）；搬移與索引建立於**同一原子變更**完成、嚴禁中間態；U2 hash 集合全等驗證（§8.1）雙保險 |
| `pre_tool_guard.sh` 攔截 TODO.md 大幅縮減（deny） | 🟡 中 | 屬守衛正確行為非誤報；依 WORKFLOW-5 C4 設計之 `// BYPASS_TRUNCATION_GUARD` sentinel 減速帶通行 + 執行報告記錄使用事由（§9 Q6） |
| FRAMEWORK §2.1「不另外分檔」未同步 → 改完即憲法違規 | 🟡 中 | U4 將 §2.1/§2.4/§2.5 納入同案改版；不同步不得落地 |
| 下游模板結案/自癒流程斷鏈（check/run 模板仍指舊「✅ 表格」） | 🟡 中 | U4 兩模板措辭同步；hash 自癒掃描對象改「TODO 索引行 + 歸檔檔」雙源 |
| CLAUDE.md §0 載入行改壞 → 新 session 缺載 TODO / README | 🟡 中 | §8.1 A1 grep 驗證 + §8.2 新 session 實測載入 |
| Antigravity 掃描 / 外部引用斷鏈 | 🟢 低 | 歸檔檔為 tracked `.claude-logs/*.md`、仍在 FRAMEWORK §9.4 掃描範圍；TODO 索引行留 pointer 可溯 |
| 快取一次性全失效（改 CLAUDE.md/TODO 當下） | 🟢 低 | 一次性成本；此後 TODO 更新之失效面由 1,419 行縮至 ≤450 行、淨收益 |
| 歷史慣例衝擊（既有提示詞/報告寫「移入 ✅ 完成表」） | 🟢 低 | 已收官文件不溯及既往（WORKFLOW_SOP §2 慣例）；新流程自 U4 生效日起算 |

對齊 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] `CLAUDE.md` §1/§2/§5 規範本體（依定案僅動：§0 載入行〔U3〕、§3 工作目錄值與 §4 同步表列〔U7、Q9 🟢〕、§99.1 約束事項一句〔U5〕、§99.2 Revision；§3 其餘條款逐字不動）
- [ ] `ref/WORKFLOW_SOP.md` 整檔（本案零觸碰；五類工作流/六階段/命名規則唯一源不動）
- [ ] `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 除 §2.1/§2.4/§2.5 與 §99.2 外之全部章節（§1 心法/§3 編碼/§4 日誌契約/§5–§9 不動）
- [ ] `TODO.md`「🟡 進行中」「索引（依類別）」「🗑️ 遺失清單」三區內容逐字不動（僅「✅ 已完成」區搬移改索引）
- [ ] 已完成區表格與註解**內容 byte**（搬移非改寫；256 hash 集合零增刪）
- [ ] `baton/` 全部檔案實體（零刪除、零搬移；僅 `README.md` 允許補「按需取用」一節）；PIPE-SPEC v8 / QUEUE-1 v2 長駐地位（RESCUE-1 Q3 定案）不推翻
- [ ] `.gitignore` 之 baton 規則（`baton/*` 排除 + `!baton/README.md` 例外）不動
- [ ] 兩模板除 TODO 結案/hash 自癒措辭段外之全部結構（Conformance 五維度、三防線、staged 自檢步驟等 CHECKOUT-GUARD/WORKFLOW-4 既有條款零改）
- [ ] 全部業務代碼（`*.py` / `static/` / `tests/` / `prompts/` 既有歸檔）零 diff

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 五文獻稽核與優先矩陣（本案規格源） | `baton/context_engineering_governance_audit.md`（2026-07-07 Review 版） |
| 文書類別歸屬 / 命名規則 / §7.2 豁免機制 | `ref/WORKFLOW_SOP.md §2 / §6 / §7.2` |
| TODO 狀態標記 / 生命週期 / SSOT 原則（本案改版對象） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §2.1–§2.5` |
| CLAUDE.md 治理約束（≤200 行 / 嚴禁動態內容 / 改版規則） | `CLAUDE.md §99.1–§99.2` |
| baton 長駐定案（PIPE-SPEC v8 / QUEUE-1 v2） | `plans/2026-06-28_RESCUE-1_遺失治理文件挽救_plan_v1.md` §9 Q3 |
| 截斷守衛與 sentinel 減速帶 | `tools/pre_tool_guard.sh`（WORKFLOW-5 C4、`c107bfd`） |
| plan 結構 SSOT | `templates/template_plan.md`（v2） |

---

## §8 驗證計畫

### §8.1 自動化驗證（DOC-Refactor 依 WORKFLOW_SOP §1.3 / §4）

```bash
# C1/C2 目標檔存在且行數符合（U1/U2）
wc -l .claude-logs/TODO.md                    # ≤ 450
wc -l .claude-logs/archive/TODO_done_archive.md   # ≥ 1,000

# U2 hash 集合全等（零刪改鐵證；.bak 為搬移前基準；唯一容許差異＝Q1 回填之 a150915）
diff <(grep -oE '[0-9a-f]{7}' <TODO.md.bak> | sort -u) \
     <(cat .claude-logs/TODO.md .claude-logs/archive/TODO_done_archive.md | grep -oE '[0-9a-f]{7}' | sort -u)
# → 僅一行差異 "> a150915"（新增）、無任何 "<"（刪失）

# U1 sentinel 不殘留（Q6）
grep -c "BYPASS_TRUNCATION_GUARD" .claude-logs/TODO.md   # → 0

# U7 stale worktree 清零（CLAUDE.md §3/§4）
grep -n "hopeful-yalow" CLAUDE.md                        # → 無命中

# A1 @path 引用存在且收斂（U3）
grep -n "@\.claude-logs" CLAUDE.md            # 含 baton/README.md、不含 "baton/\*"
git check-ignore .claude-logs/baton/README.md # → 無輸出（tracked 例外維持）

# A5 動態內容缺席（CLAUDE.md）
grep -nE "待 baron 回填|[0-9a-f]{7}" CLAUDE.md   # → 無命中

# U4 同步完成（FRAMEWORK 與模板無殘留舊規）
grep -n "不另外分檔" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md   # → 舊表述已改版
grep -n "✅ 已完成" .claude-logs/templates/template_prompt_for_check.md        # → 指向新雙源流程

# U6 零業務波及
git diff --stat -- '*.py' static/ tests/      # → 空
pytest tests/ -v                              # → 與基線一致（唯一既知 flake＝LOG_FORMAT env）
```

### §8.2 手動端到端（E2E）驗證流程

1. 改動落地後**新開 Claude Code session**：確認自動載入＝三份 ref 規範 + 瘦身版 TODO + 僅 baton/README；PIPE-SPEC / 稽核檔不再出現於開場 context。
2. Spot-check 規範可及性：新 session 詢問任一鐵律（如 git-add 白名單）與任一已完成任務 hash——前者由規範層直答、後者應循 TODO 索引行 pointer 至歸檔檔 grep 取得。
3. 下一個任務之 checkout 輪實走 U4 新結案流程（一行索引 + 歸檔檔追加 + hash 自癒雙源），驗證模板可操作性。
4. §7.2 跨 Phase 整合測試：依 §9 Q8 申請純 DOC 顯式豁免。

---

## §9 Open Questions（2026-07-07 baron 全數 🟢 定案）

> **定案紀錄**：Q1–Q9 均採推薦方案（baron 拍板逐字存 `prompts/2026-07-07_CONTEXT-1_plan_v2_提示詞.md`）。兩項技術銳化：**Q6** sentinel 判定對象＝tool_input（見 §3 守衛交互）→ 夾帶註解放行＋後續移除、TODO 不殘留；**Q9** baron 給定值為 Mac OrbStack 視圖 → 正規化為雙視圖寫法、並附帶納入 §4 同步表同一 stale 列（超字面授權部分待 baron 階段 3 確認），落 U7。

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1 開工時機**：TODO 內 RESCUE-1 C5 hash 仍「待 baron 回填」（實際已 commit `a150915`） | baron 回填（或授權本案 hash 自癒順帶補）後即開工 | RESCUE-1 已全案收官、撞檔風險消滅；先結佔位符再搬移，避免歸檔檔帶著佔位符出生 |
| **Q2 歸檔檔落點與命名** | `archive/TODO_done_archive.md`（tracked、無日期前綴之滾動累積檔） | WORKFLOW_SOP §2 archive＝過期/歸檔語意；tracked 保 grep 與 Antigravity 掃描可及；滾動檔不宜日期前綴（非一次性產物）；否決拆多檔（定位破碎）與「僅靠 executions/」（密集註解表格在 executions 無單源對應） |
| **Q3 TODO 主檔索引行格式** | `- ✅ <代號> <主題>（<首hash>…<末hash>、N commits）→ archive/TODO_done_archive.md` 每任務一行 | 最小行數保 SSOT 可溯；hash 首末錨定供 git log 交叉；pointer 固定格式利機器檢索 |
| **Q4 wildcard 收斂範圍**：只留 README vs README+顯式列名長駐檔 | 只留 `baton/README.md` | CLAUDE.md §99.1 嚴禁動態內容——顯式列任務檔名即動態內容、違自身憲法；PIPE-SPEC/QUEUE-1 由任務提示詞指路（現行慣例本就逐份指路） |
| **Q5 載入排序原則落點** | CLAUDE.md §99.1「約束事項」欄補一句（不動 §0 行數） | §99.1 本為 CLAUDE.md 自身維護約束的權威欄位；§0 保持極簡 |
| **Q6 pre_tool_guard 攔截處理** | 以 `// BYPASS_TRUNCATION_GUARD` sentinel 減速帶通行 + 執行報告記載事由 | 守衛設計（WORKFLOW-5 C4）本就預留「有意大改寫」出口；暫卸 hook 會失去其他檔案保護窗口（否決） |
| **Q7 FRAMEWORK §2.1 改版幅度** | §2.1 改「雙層表述」：active 任務單檔 SSOT 於 TODO.md 不變、完成史移歸檔檔並由索引行錨定；§2.4/§2.5 寫入規則對應改指歸檔檔 | 保留 §2.1 的 SSOT 精神（單一入口交叉對照）、只把「物理單檔」放寬為「單一入口 + pointer」；完全刪除該原則（否決）會失去防散檔約束 |
| **Q8 §7.2 整合測試豁免** | 顯式豁免 | 純 DOC-Refactor、零業務代碼、無 Phase handoff；同 WORKFLOW-3/4/5、RESCUE-1、CHECKOUT-GUARD 先例 |
| **Q9 工作目錄與授權範圍** | 沿 RESCUE-1 先例主 repo 就地；授權限 `CLAUDE.md` + `.claude-logs/{TODO.md, ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md, archive/, baton/README.md, templates/{template_prompt_for_check.md, template_prompt_for_run.md}, prompts/}`；**附帶**：CLAUDE.md §3 仍指向已刪除之 worktree `hopeful-yalow-902c50`（stale、RESCUE-1 動因遺留），是否本案順修由 baron 拍板並給定新值 | §3 唯一權威源指向不存在目錄＝現行治理債；本案已動 CLAUDE.md、一行順修成本最低；但 §3 為工作目錄硬規則、新值必須 baron 拍板、不得自定 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 CONTEXT-1 session 載入鏈瘦身與 context 治理的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 CONTEXT-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md；五文獻論證與落實性裁決唯一源在 `baton/context_engineering_governance_audit.md`（本檔不重寫） |

### §99.2 Revision 歷程

- v2 (2026-07-07)：baron 九 OQ 全數定案回灌——U1 索引行格式＋C5 hash `a150915` 回填授權（Q1/Q3）、U2 歸檔檔名定案 `archive/TODO_done_archive.md`（Q2）、U5 落點定案 §99.1（Q5）、新增 U7 工作目錄 stale 修正〔§3 L89＋§4 L123 雙視圖寫法〕（Q9）；Q6 sentinel 機制銳化（tool_input 判定、夾帶後移除不殘留）＋ §3.1 補 worktree/sentinel 兩組 grep 證據＋ §8.1 驗證式對應更新（hash 容許差異＝+a150915、sentinel 清零、hopeful-yalow 清零）
- v1 (2026-07-07)：初版——依 context_engineering_governance_audit 優先矩陣 #1/#2/#3 立 U1–U6；納入 FRAMEWORK §2.1「不另外分檔」衝突改版（U4）與 pre_tool_guard 攔截處理（Q6）；證據基準＝RESCUE-1 全案收官後實測（TODO 1,419 行 / baton 7 檔 130,356 bytes / hash 256）
