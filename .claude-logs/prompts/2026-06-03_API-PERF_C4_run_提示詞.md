`````markdown
# 2026-06-03 — API-PERF C4 run 提示詞

> **收到時間**：2026-06-03 15:13（UTC+8）
> **任務代號**：API-PERF C4
> **觸發 commit**：C4
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_C4_執行.md
> **觸發情境**：baron 確認 C3 執行報告並成功 commit 後下達 C4 執行指令——U1 PIPELINE_SEMAPHORE 守 A 軌 run_pipeline + B 軌 run_pipeline_shadow 派發點 + queued SSE；U2 pdf_processor 子進程 nice 19 soft-fail；修改區塊 `=== [API-PERF C4 START/END] ===` 包裹，實體寫 /tmp/API-PERF_C4_msg.txt，追加 semaphore/queue 測試。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 15:13`                                           |
| **任務代號**     | `API-PERF C4`                                                |
| **觸發 Commit**  | `C4`                                                         |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 確認 C3 執行報告並成功 commit，下達本次 C4 執行指令`  |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_API-PERF_C4_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **當前 Commit 代號**：`C4` ｜ **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks_v3（§8 C4）/ logging SOP / database SOP
### 🛠️ 執行命令與代碼註解防線
依 `tasks_v3.md §8 C4 — 並發信號量與子進程降優（U1 Semaphore + U2 Nice）` 修改：
1. **通用代碼註解防線**：修改既有原始碼處以 `# === [API-PERF C4 START] ===` / `# === [API-PERF C4 END] ===` 包裹。
2. **硬性要求：實體寫入 commit msg 草稿** 至 `/tmp/API-PERF_C4_msg.txt`。
3. **物理防線**（tasks §7）：A 軌 `run_pipeline` process 調用本體完全不動，僅外層包 Semaphore。
4. **測試防線**（tasks §6.4 C4 驗收）：
   ```bash
   grep -nE "PIPELINE_SEMAPHORE|Semaphore|os.nice|nice\(" web_server.py settings.py pipeline_core.py processor/pdf_processor.py
   grep -n "queued" web_server.py
   pytest tests/test_api_performance_and_robustness.py -k "semaphore or queue" -q
   ```
   並跑全域 `pytest tests/ -q` 確保零迴歸。
5. **文件與 Git 防線**（CLAUDE.md §1.3）：C4 執行報告與 TODO 更新僅留本地；**baton/ 執行報告 C1–C5 期間嚴禁 git add**，留待 C6 收官；commit/push 由 baron 手動。
### 💾 備份規則
```bash
cp settings.py .claude-logs/archive/2026-06-03_API-PERF_C4_settings.py.bak
cp web_server.py .claude-logs/archive/2026-06-03_API-PERF_C4_web_server.py.bak
cp pipeline_core.py .claude-logs/archive/2026-06-03_API-PERF_C4_pipeline_core.py.bak
cp processor/pdf_processor.py .claude-logs/archive/2026-06-03_API-PERF_C4_pdf_processor.py.bak
cp tests/test_api_performance_and_robustness.py .claude-logs/archive/2026-06-03_API-PERF_C4_test_api_performance_and_robustness.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
1. WIP：C4 → ✅、C5 → 🟡 WIP。
2. 歷史 Hash 自癒：`git log` 查 C1/C2/C3 等仍 `待 baron 回填` 之真實 hash 並替換。
### 📁 產出規格
- 執行報告 `.claude-logs/baton/2026-06-03_API-PERF_C4_執行.md`（暫存 baton/、嚴禁 git add）；套用 template_execution.md。
- 含元數據 / §1 基準 / §2 Commit 表 / §3 變動檔案（含 .bak）/ §4 修法（附代碼）/ §5 測試（排隊 + nice pytest）/ §6 不可動清單 / §7 銜接 C5 / §8 baron 執行命令。
### 📝 §8 baron 執行命令格式要求
```bash
git add settings.py web_server.py pipeline_core.py processor/pdf_processor.py tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-06-03_API-PERF_C4_*.bak
git add .claude-logs/prompts/2026-06-03_API-PERF_C4_run_提示詞.md .claude-logs/prompts/INDEX.md .claude-logs/TODO.md
cat > /tmp/API-PERF_C4_msg.txt << 'EOF'
BE-Refactor: API-PERF C4 — 並發信號量與子進程降優
1. U1 併發信號量：在 web_server 引入 PIPELINE_SEMAPHORE (上限 1，settings 配置)，
   以 async with 語意同步守護 A 軌 run_pipeline 與 B 軌 run_pipeline_shadow 派發點。
   等待期正確更新狀態為 queued 並以 SSE 推送 queue 進度資訊。
2. U2 子進程 nice 調整：在 pdf_processor 啟動背景轉檔子進程時，加入 preexec_fn
   設定 nice 值為 19 (Windows 環境下以 try/except soft-fail 機制降級相容)。
3. 新增對應單元測試驗證排隊與 nice 行為，維持既有測試全綠。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
git commit -F /tmp/API-PERF_C4_msg.txt
```
---
### 🛑 停止指令
產出 `C4_執行.md` 後立即停止。嚴禁續跑 C5 / 改非 C4 範圍代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（-k "semaphore or queue" + 全域）
- 改動檔案數：修改 `settings.py` / `web_server.py` / `pipeline_core.py` / `processor/pdf_processor.py`（各含 .bak）+ 測試追加（含 .bak）；提示詞歸檔；修改 TODO.md / INDEX.md；寫 /tmp/API-PERF_C4_msg.txt
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 C3（`2026-06-03_API-PERF_C3_run_提示詞.md`）。下一步 C5 結構化計時埋點與 CLI 分析工具。
`````
