`````markdown
# 2026-06-02 — GOLDEN-BASELINE OP-1 run 提示詞

> **收到時間**：2026-06-02 02:22（UTC+8）
> **任務代號**：GOLDEN-BASELINE OP-1
> **觸發 commit**：OP-1
> **相關產出檔案**：.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md
> **觸發情境**：baron 確認 tasks 符合 plan，下達 OP-1 執行指令（五路黃金基準物理存盤：新建 tools/golden_baseline.py capture 子命令 + 五路 fixtures + golden 三維度凍結 + manifest）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-02 02:22`                                           |
| **任務代號**     | `GOLDEN-BASELINE OP-1`                                       |
| **觸發 Commit**  | `OP-1`                                                       |
| **相關產出檔案** | `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` |
| **觸發情境**     | `baron 確認 tasks 符合 plan，下達 OP-1 執行指令`             |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**
1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。
2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的 `## 依時間排序` 首行插入本條目：
   `- 2026-06-02 | GOLDEN-BASELINE OP-1 | run | 執行 OP-1 五路黃金基準物理存盤`
   若超過 15 筆則自動刪除最舊一筆。
3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md`」，然後繼續執行後續步驟。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`GOLDEN-BASELINE`
- **當前 Commit 代號**：`OP-1`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`
### 📖 強制讀檔清單
請在開始執行前，必須完整閱讀以下文件：
```
CLAUDE.md                                                                               # 核心規範與契約
.claude-logs/ref/WORKFLOW_SOP.md                                                        # 工作流規範
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md             # 本次執行的依據 tasks (§8 OP-1)
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                                          # BE 類必讀日誌 SOP
.claude-logs/sop/2026-05-23_database_SOP_手冊.md                                         # BE 類必讀 DB SOP
```
### 🛠️ 執行命令
請依 `tasks.md §8 OP-1 具體實作細節` 進行代碼編寫，並嚴格遵守以下三個防線：
1. **物理防線**（`tasks.md §7 不可動清單`）：
   - [ ] 嚴禁修改 `pipeline_core.py` 舊單體 11-stage 與 `_get_stage_output_path`（L191-209），本階段只可唯讀調用！
   - [ ] 嚴禁修改 `rag_retriever.py` `retrieve_with_context`（L92）簽名與檢索演算法。
   - [ ] 嚴禁修改既有 `delete_paper` / `list_papers` / `get_paper` API。
   - [ ] 嚴禁修改 `models.py` 既有 Schema（零 DB 變動）。
   - [ ] 嚴禁修改 `web_server.py` 業務代碼（本工具為旁路 CLI，不注入 runtime 主鏈 hook）。
   - [ ] 嚴禁讀寫主 repo 目錄（唯一合法工作區為 `.claude/worktrees/hopeful-yalow-902c50/`）。
2. **測試防線**（`tasks.md §6 測試計畫`）：
   - [ ] 執行 `capture --all` 存盤後，確認五路黃金快照的 D1/D2/D3 產物與 `manifest.json` 齊全。
   - [ ] 測試 capture 的防覆寫閘：不加 `--force` 再次重跑必須觸獲 `ABORT` 終止。
   - [ ] 確認執行報告嚴格暫留在 `baton/`，且尚未被 git 追蹤。
3. **文件防線**（`CLAUDE.md §1.3`）：
   - 所有 git commit / push 由 baron 手動執行，嚴禁自發。
### 💾 備份規則
- 本 Commit 為 **100% 新增工具與測試資產**，不修改任何既有 Python 業務代碼，故**跳過既有檔案備份（合規）**。
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新：**
1. **WIP 狀態更新**：
   - 尋找 `TODO.md` 中的 `GOLDEN-BASELINE` 區塊，將當前任務 `- [🟡 WIP] OP-1 — 五路黃金基準物理存盤` 的狀態更正為 `- [✅ done] OP-1 — 五路黃金基準物理存盤`。
   - 將下一個任務標記為 WIP：`- [🟡 WIP] OP-2 — 自動化 Regression Diff 比對腳本開發`。
   - **注意**：依據 `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §2.5`，由於本任務尚未「全案 Checkout 收官（即 OP-3）」，因此先不要將本任務整包移入頂部已完成表格，僅更新當前 OP 狀態。
2. **歷史已提交 Hash 自癒回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出先前所有已完成任務中，尚為 `待 baron 回填` 的真實 Commit Hash，並予以替換。
### 📁 產出規格
- **執行報告路徑**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md`
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `WORKFLOW_SOP.md §6` 命名規則。
#### ⚠️ `baton/` 暫存鐵律與 Git 歸鎖限制：
- **本執行報告嚴格暫存在 `baton/` 目錄下**。
- **嚴禁在本次執行結束時對本執行報告進行 `mv` 移動或 `git add`！**
- 本執行報告必須在工作區保持 Untracked/Gitignored 狀態，直到 OP-3（Checkout）才一次性歸檔。
---
### 📝 §8 baron 執行命令格式要求
在產出的執行報告 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md` 的 `## §8 baron 執行命令` 中，必須精確提供以下內容（**必須排除暫存報告檔**）：
```bash
# 1. 備份檔案已完成（無修改既有檔案，跳過）
# 2. git add 清單（所有本次新增的工具、測試與提示詞歸檔，嚴禁包含 baton/ 下的執行報告！）
git add tools/golden_baseline.py
git add tests/golden_baseline/
git add .claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/GOLDEN-BASELINE_OP-1_msg.txt）
cat > /tmp/GOLDEN-BASELINE_OP-1_msg.txt << 'EOF'
BE-Refactor: GOLDEN-BASELINE OP-1 — 五路黃金基準物理存盤
1. 新建旁路 CLI 工具 `tools/golden_baseline.py`，實作 `capture` 子命令。
2. 凍結學術、書籍節選、簡報、履歷與短文五路 PDF 至 `tests/golden_baseline/fixtures/`。
3. 唯讀呼叫舊體 PipelineCore 完整 11-stage 物理存盤 D1 md/D2 json/D3 RAG 召回結果。
4. 計算產物 SHA-256 Checksum 寫入 `manifest.json`，並配置 capture 防覆寫安全閘。
EOF
# 4. baron 手動執行
git commit -F /tmp/GOLDEN-BASELINE_OP-1_msg.txt
```
---
### 🛑 停止指令
**產出 `OP-1_執行.md` 並更新 `TODO.md` 後，必須立即停止所有工具呼叫與代碼修改。**
嚴禁：
- ❌ 繼續執行 `OP-2`（必須等 baron 確認後另行下達 OP-2 提示詞）。
- ❌ 修改任何未列入 `OP-1` 實作細節的代碼或文件。
- ❌ 自發執行 `git commit` 或 `git push`。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補
- 改動檔案數：新增 `tools/golden_baseline.py` + `tests/golden_baseline/` + 提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 `2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md`（tasks v2，OP-1 = 五路黃金基準物理存盤）。
`````
