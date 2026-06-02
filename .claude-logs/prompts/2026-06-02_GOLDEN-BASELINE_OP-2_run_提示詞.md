`````markdown
# 2026-06-02 — GOLDEN-BASELINE OP-2 run 提示詞

> **收到時間**：2026-06-02 12:42（UTC+8）
> **任務代號**：GOLDEN-BASELINE OP-2
> **觸發 commit**：OP-2
> **相關產出檔案**：.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md
> **觸發情境**：baron 手動 commit 歸鎖 OP-1（capture 工具）後，下達 OP-2 執行指令——在 tools/golden_baseline.py 實作 diff 子命令 + 三維度比對引擎 + 紅綠燈裁決 + 雙格式報告，並新建 tests/test_golden_baseline.py。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-02 12:42`                                           |
| **任務代號**     | `GOLDEN-BASELINE OP-2`                                       |
| **觸發 Commit**  | `OP-2`                                                       |
| **相關產出檔案** | `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` |
| **觸發情境**     | `baron 手動 commit 歸鎖 OP-1，下達 OP-2 執行指令`            |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**
1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。
2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的 `## 依時間排序` 首行插入本條目：
   `- 2026-06-02 | GOLDEN-BASELINE OP-2 | run | 執行 OP-2 自動化 Regression Diff 比對腳本開發`
   若超過 15 筆則自動刪除最舊一筆。
3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md`」，然後繼續執行後續步驟。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`GOLDEN-BASELINE`
- **當前 Commit 代號**：`OP-2`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`
### 📖 強制讀檔清單
請在開始執行前，必須完整閱讀以下文件：
```
CLAUDE.md                                                                               # 核心規範與契約
.claude-logs/ref/WORKFLOW_SOP.md                                                        # 工作流規範
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md             # 本次執行的依據 tasks (§8 OP-2)
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                                          # BE 類必讀日誌 SOP
.claude-logs/sop/2026-05-23_database_SOP_手冊.md                                         # BE 類必讀 DB SOP
```
### 🛠️ 執行命令
請依 `tasks.md §8 OP-2 具體實作細節` 進行代碼編寫，並嚴格遵守以下三個防線：
1. **物理防線**（`tasks.md §7 不可動清單`）：
   - [ ] 嚴禁修改 `pipeline_core.py` 舊單體 11-stage 與 `_get_stage_output_path`（L191-209），只可唯讀調用！
   - [ ] 嚴禁修改 `rag_retriever.py` `retrieve_with_context`（L92）簽名與檢索演算法。
   - [ ] 嚴禁修改既有 `delete_paper` / `list_papers` / `get_paper` API。
   - [ ] 嚴禁修改 `models.py` 既有 Schema（零 DB 變動）。
   - [ ] 嚴禁修改 `web_server.py` 業務代碼（本工具為旁路 CLI，不注入 runtime 主鏈 hook）。
   - [ ] 嚴禁讀寫主 repo 目錄（唯一合法工作區為 `.claude/worktrees/hopeful-yalow-902c50/`）。
2. **測試防線**（`tasks.md §6 測試計畫`）：
   - [ ] 比對引擎單元測試全綠：`pytest tests/test_golden_baseline.py -v`。
   - [ ] 實測「自比對歸零」：對舊系統再跑一次同檔 diff，確認三維度 Diff 為 0% (PASS 綠燈)。
   - [ ] 驗收 `report/golden_baseline/*/` 雙格式報告 `diff_report.json` 與 `diff_report.md` 均正常產出。
   - [ ] 既有單元測試零迴歸：`pytest tests/` 保持全綠。
3. **文件防線**（`CLAUDE.md §1.3`）：
   - 所有 git commit / push 由 baron 手動執行，嚴禁自發。
### 💾 備份規則
修改 `tools/golden_baseline.py` 前，必須先備份：
```bash
cp tools/golden_baseline.py .claude-logs/archive/2026-06-02_GOLDEN-BASELINE_OP-2_golden_baseline.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新：**
1. **WIP 狀態更新**：
   - 尋找 `TODO.md` 中的 `GOLDEN-BASELINE` 區塊，將當前任務 `- [🟡 WIP] OP-2 — 自動化 Regression Diff 比對腳本開發` 的狀態更正為 `- [✅ done] OP-2 — 自動化 Regression Diff 比對腳本開發`。
   - 將下一個任務標記為 WIP：`- [🟡 WIP] OP-3 — Checkout / 收官歸檔`。
2. **歷史已提交 Hash 自癒回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出先前所有已完成任務中（特別是剛落地的 OP-1），尚為 `待 baron 回填` 的真實 Commit Hash，並予以替換。
### 📁 產出規格
- **執行報告路徑**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md`
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `WORKFLOW_SOP.md §6` 命名規則。
#### ⚠️ `baton/` 暫存鐵律與 Git 歸鎖限制：
- **本執行報告嚴格暫存在 `baton/` 目錄下**。
- **嚴禁在本次執行結束時對本執行報告進行 `mv` 移動或 `git add`！**
- 本執行報告必須在工作區保持 Untracked/Gitignored 狀態，直到 OP-3（Checkout）才一次性歸檔。
---
### 📝 §8 baron 執行命令格式要求
在產出的執行報告 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md` 的 `## §8 baron 執行命令` 中，必須精確提供以下內容（**必須排除暫存報告檔**）：
```bash
# 1. 備份檔案已完成
git add .claude-logs/archive/2026-06-02_GOLDEN-BASELINE_OP-2_golden_baseline.py.bak
# 2. git add 清單（請特別注意：嚴禁包含 baton/ 下的執行報告！）
git add tools/golden_baseline.py
git add tests/test_golden_baseline.py
git add .claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/GOLDEN-BASELINE_OP-2_msg.txt）
cat > /tmp/GOLDEN-BASELINE_OP-2_msg.txt << 'EOF'
BE-Refactor: GOLDEN-BASELINE OP-2 — 自動化 Regression Diff 比對腳本開發
1. 在 tools/golden_baseline.py 中實作 diff 子命令與三維度比對引擎。
2. 實作 checksum 驗證、影子/時間戳噪聲正規化、與紅綠燈裁決彙總邏輯。
3. 支援比對輸出機器可讀 diff_report.json 與人類可讀 diff_report.md 雙格式報告。
4. 新建 tests/test_golden_baseline.py，以 pytest 覆蓋比對引擎、噪聲正規化與已知改善豁免分支。
5. 實測本地「自比對歸零」通過，檢驗比對引擎零偽陽性，且既有單元測試零迴歸。
EOF
# 4. baron 手動執行
git commit -F /tmp/GOLDEN-BASELINE_OP-2_msg.txt
```
---
### 🛑 停止指令
**產出 `OP-2_執行.md` 並更新 `TODO.md` 後，必須立即停止所有工具呼叫與代碼修改。**
嚴禁：
- ❌ 繼續執行 `OP-3`（必須等 baron 確認後另行下達 OP-3 提示詞）。
- ❌ 修改任何未列入 `OP-2` 實作細節的代碼或文件。
- ❌ 自發執行 `git commit` 或 `git push`。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（tests/test_golden_baseline.py）
- 改動檔案數：修改 `tools/golden_baseline.py`（加 diff）+ 新建 `tests/test_golden_baseline.py` + .bak 備份 + 提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 OP-1（`2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md`，capture 工具）。OP-2 = diff 引擎 + 單元測試。
`````
