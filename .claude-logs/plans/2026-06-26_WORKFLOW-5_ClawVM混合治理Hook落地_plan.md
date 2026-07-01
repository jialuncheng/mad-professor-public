# WORKFLOW-5 ClawVM 混合治理 Hook 落地 plan

> 基於 ClawVM 論文精神，承認「純文件約束」的結構性不足，跨出純文件邊界。透過真實的 Claude Code Hook 機制（Harness Enforcement）與 Baton 3-Phase 形式化，實作最小保真不變式與確定性故障偵測，防範失憶與破壞性寫入。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：純文件約束仰賴 AI 自由心證，無法可靠防止失憶或破壞性寫入（如論文指出的結構性缺陷）；且原先依賴的提示詞防護形同 Theater。
- **解法**：運用真實的專案級 `settings.json` Hook 系統：
  1. 實作 `SessionEnd` (或 `Stop` + 守衛) 與 `PreToolUse` Hook 腳本（防 DIRTY-RESET 與 DESTRUCTIVE-WRITE）。
  2. Baton 3-Phase 形式化（非破壞性寫入）。
  3. 於 Template §99 引入 Scope / Provenance，並推動 Minimum-Fidelity Floor 的機器可讀化。
- **誠實聲明 (Threat Model)**：本治理計畫的三道防線具備不同的防禦強度極限：
  - **Baton 3-Phase 歸檔自檢 = 最強 (不可繞過)**：依賴 Harness 確定性 Validation。
  - **DESTRUCTIVE-WRITE 截斷守衛 = 防誤觸 (Agent 可繞過)**：透過 Sentinel 機制，防範的是「意外/手滑的破壞性截斷」，不防「Agent 意識到後決定自我授權繞過」。
  - **DIRTY-RESET = Observable Fault (可觀測故障)**：為免鎖死使用者，首版實作僅做可觀測的日誌/警告，不強制阻擋退出。
- **影響**：改動 `baton/README.md`、`template_file_governance.md`，新增版控化 Hook 腳本至 `.claude-logs/tools/`，並透過專案級 `.claude/settings.json` 指針掛載。不影響業務模組。

---

## §2 目標規格

1. **Baton 3-Phase Writeback 形式化**：
   - 於 `baton/README.md` 明定歸檔時的**非破壞性寫入語意**。
   - *對帳 WORKFLOW_SOP §3 `mv` 鐵律*：歸檔依然維持一次性 `mv`（Staging → Commit），但在此動作前，必須加入 Provenance / Schema 的「自檢步驟（Validation）」。

2. **Hook 確定性故障偵測 (DIRTY-RESET / DESTRUCTIVE-WRITE)**：
   - **防 DIRTY-RESET (Observable Fault 首版)**：
     - **觸發條件修正**：任務正常跨 session 時 baton 本來就會非空，因此**不攔截單純的「baton 非空」**。DIRTY-RESET 僅在**「達到 Checkout 階段（如 TODO 標記為 ✅）但 baton 內卻仍有該任務的 dirty state 未歸檔」**時才發報。（執行期需撰寫 baton 檔名→任務代號→TODO 狀態的解析邏輯）。
     - **技術路徑**：為避免強制 block session 退出導致極差體驗（想關關不掉），首版 DIRTY-RESET 統一實作為 **Observable Fault Only**（僅發布警告與日誌寫入）。但仍須在動工第一步（C1）測試 `SessionEnd` 的阻擋能力，做為未來擴充的技術探勘。
   - **防 DESTRUCTIVE-WRITE (PreToolUse Hook)**：
     - **攔截目標**：正確匹配寫入工具名稱 `Write|Edit`，保護範圍擴大至高價值真理源：`plans/`、`sop/`、`ref/` 以及根目錄的 `CLAUDE.md` 與 `TODO.md`。
     - **硬擋 (Hard Deny)**：觸發違規時直接回傳 `deny`（例如 exit 2），強制要求 AI 確認或改走版控寫入。
     - **攔截條件重塑（分階實施）**：
       - *第一階段（截斷守衛）*：比對磁碟現有檔案。保守起始門檻：**若行數或大小驟降超過 50% 且超過 50 行**，則判定為異常截斷並攔截。
       - *Bypass 機制 (防誤觸設計)*：當 AI 確實需要大幅刪減內容時，Hook deny 訊息將提示 AI 在工具呼叫中加入特定 Sentinel (例如 `// BYPASS_TRUNCATION_GUARD`) 來自我授權放行。這讓守衛退回「減速帶」角色，專防失憶時的盲目修改。
       - *第二階段（Floor 守衛）*：需等待 Template §99.1 的 Fidelity Floor 轉化為機器可讀格式後，方可實作。

3. **最小保真不變式 (Minimum-fidelity floor) 寫入 Template**：
   - 擴充 `template_file_governance.md §99.1` 新增維度：**Scope** (session-private vs project-shared)、**Provenance** (資料溯源)。
   - 新增 **Fidelity Floor** 欄位（降級底線），並為未來機器可讀化預留空間。
   - **Cost-Aware 保留**：高重算成本之 evidence（grep 證據、實測輸出、commit hash）標註為優先不降級。

---

## §3 現況與證據

真正的 Hook 攔截基建存在於 Claude Code 的 `settings.json` 機制中：

### §3.1 grep 鋼鐵證據

```bash
# 證明 .claude/ 被 gitignore 排除
grep -n "^\.claude/$" .gitignore
# 預期輸出： 174:.claude/

# 本地真實的 Hook 機制（示意）
cat .claude/settings.json | grep "hooks"
# 預期輸出： "hooks": { "PreToolUse": [{ "matcher": "Write|Edit", "command": "./.claude-logs/tools/pre_tool_guard.sh" }] }
```

由於 `.claude/` 被排除版控，專案級 `.claude/settings.json` 雖不進版控，但可用作輕量級的「指針」，指向受版控的 `.claude-logs/tools/` 腳本，從而達成跨環境同步與專案隔離。

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

無（本任務為文件與 Hook 治理基建更新，不涉及業務模組資料 Handoff）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| Hook 寫錯導致死鎖或無法退出 | 🔴 高 | Hook 腳本是會把人鎖在外的代碼。必須在 `.claude-logs/tools/` 加入單獨的乾跑 (dry-run) / 單元測試腳本。且首版 DIRTY-RESET 僅做 Observable Fault，不鎖死退出。 |
| Hook 誤擋正常的 DOC-Refactor | 🟡 中 | 截斷守衛設定保守門檻 (>50%)，並明文設計 AI 可自行觸發的 bypass 機制，防止卡死。 |
| 全域 Hook 誤傷其他專案 | 🟡 中 | 廢棄全域設定，改用專案級 `.claude/settings.json` 指針。 |

---

## §6 不可動清單

- [ ] `ref/WORKFLOW_SOP.md` 既有的「六階段強制觸發鏈」（屬核心流程，不可動）。
- [ ] 既有業務代碼 (`web_server.py`, `pipeline_core.py` 等) 絕對不可動。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| ClawVM 論文 | `.claude-logs/baton/2604.10352v1.pdf` |
| 工作目錄硬規則與 .gitignore | `CLAUDE.md §3` |
| 跨環境同步規則 | `CLAUDE.md §4` |

---

## §8 驗證計畫

### §8.1 自動化單元測試 / 乾跑 (Dry-Run)

- **腳本獨立測試**：針對 `.claude-logs/tools/` 內新撰寫的 Hook 腳本，必須撰寫獨立的單元測試（如餵入不同大小差異的 mock 檔案，驗證「截斷守衛」是否能正確 deny 並返回 exit 2，而帶有 bypass sentinel 或正常 append 則放行）。

### §8.2 手動端到端（E2E）驗證流程

1. **實測 SessionEnd 行為（動工前 C1 Spike 必做）**：編寫極簡的 SessionEnd hook，實測 Claude Code 是否允許中斷 session 終止。
2. 建立包含未歸檔暫存檔的 `baton/` 目錄，模擬 TODO 標記為 ✅ 的 Checkout 狀態，觸發結束信號，驗證是否能精確產出 DIRTY-RESET 的 Observable Fault 紀錄與警告。
3. 以 CLI 嘗試用 `Write` 或 `Edit` 大幅刪減現有 `WORKFLOW_SOP.md`，驗證 PreToolUse Hook 是否正確觸發 DESTRUCTIVE-WRITE 並執行 Hard Deny；加入 bypass 標記後再次測試是否放行。
4. 檢查新的 `template_file_governance.md` 是否成功包含 Scope、Provenance、Fidelity Floor 欄位。

---

## §9 Open Questions

| 開放問題 | 決策方案 (已拍板) | 決策理由 |
|---|---|---|
| **[Q1] `.claude/` 被 gitignore，如何跨環境同步且不誤殺全域？** | **採專案級 `.claude/settings.json` 作為指針**。腳本實體放 `.claude-logs/tools/` (受版控)，而在各部署環境僅需手動貼上 5 行的專案級 settings。 | 同時滿足「腳本可版控」+「作用域隔離（不污染機器上其他專案）」+「維持 `CLAUDE.md §3` 的隱私隔離」。 |
| **[Q2] 若 SessionEnd Hook 無法阻擋退出，DIRTY-RESET 該如何實作？** | **C1 Spike 測試，但實作首版統一採 Observable Fault Only**。 | 忠於論文精神，讓 fault 具備可追蹤性。避免一開始就強制 block session 退出帶來「想關關不掉」的惡劣體驗。先觀測，確認無誤殺後再考慮阻擋。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-5 ClawVM 混合治理 Hook 落地 的目標規格 |
| **用途** | 供 baron 審查，做為後續執行的唯一基準 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 WORKFLOW-5 執行報告 / Tasks |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含 commit 拆分細節（不用給 commit 建議） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 本檔僅定義技術規格，工作流規範依據 WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v6 (2026-06-26)：Open Questions 拍板定案：Q1 改採專案級 `.claude/settings.json` 作為版控腳本之指針以確保作用域隔離；Q2 確立首版 DIRTY-RESET 採 Observable Fault 降低鎖死風險，並定調 C1 須執行 SessionEnd spike。
- v5 (2026-06-26)：加入 Threat Model 誠實聲明，明確界定 Bypass Sentinel 僅作為「防手滑減速帶」，不可繞過的保證僅在 Baton 3-Phase 驗證階段。
- v4 (2026-06-26)：精化執行期條件：修正 DIRTY-RESET 條件為「達到 Checkout 階段且未歸檔」以避免跨 Session 正常行為被誤殺；截斷守衛加入 50% 縮減門檻與 Bypass 放行機制；擴展守衛範圍至 `ref/`、`CLAUDE.md` 及 `TODO.md`。
- v3 (2026-06-26)：修正 Hook 技術細節：改為匹配真實工具名 `Write\|Edit`，將覆寫攔截優化為「截斷守衛 (Hard Deny)」，並將「SessionEnd 能否 block」與跨環境版控升級為核心 Open Questions。
- v2 (2026-06-26)：捨棄純文件提示詞約束，改用實體 Hook 攔截 (SessionEnd / PreToolUse)；定義精準的 DESTRUCTIVE-WRITE 攔截條件。
- v1 (2026-06-26)：初版建立
