`````markdown
# 2026-06-03 — API-PERF C5 run 提示詞

> **收到時間**：2026-06-03 15:41（UTC+8）
> **任務代號**：API-PERF C5
> **觸發 commit**：C5
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_C5_執行.md
> **觸發情境**：baron 確認 C4 執行報告並成功 commit 後下達 C5 執行指令——U7 (phase,stage) 二維鍵 performance_metric 埋點落 pipeline_core（A 軌 phase 映射）+ orchestrator（PhaseEnum P1-P4 附加式、DAG/合約/Strategy 本體不動）+ pipeline_finished(phases_breakdown) + 獨立 rag_finished + 新建零依賴 scripts/analyze_performance.py；修改區塊 `=== [API-PERF C5 START/END] ===` 包裹，實體寫 /tmp/API-PERF_C5_msg.txt，pipelines 既有 20 pytest 維持全綠。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 15:41`                                           |
| **任務代號**     | `API-PERF C5`                                                |
| **觸發 Commit**  | `C5`                                                         |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 確認 C4 執行報告並成功 commit，下達本次 C5 執行指令`  |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_API-PERF_C5_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **當前 Commit 代號**：`C5` ｜ **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks_v3（§8 C5）/ logging SOP / database SOP
### 🛠️ 執行命令與代碼註解防線
依 `tasks_v3.md §8 C5 — 結構化計時埋點與 CLI 分析工具（U7 (phase,stage) 二維鍵）` 修改：
1. **通用代碼註解防線**：修改既有原始碼處以 `# === [API-PERF C5 START] ===` / `# === [API-PERF C5 END] ===` 包裹。
2. **硬性要求：實體寫入 commit msg 草稿** 至 `/tmp/API-PERF_C5_msg.txt`。
3. **物理防線**（tasks §7）：**B 軌 `pipelines/orchestrator.py` DAG 推進/合約驗證/Strategy 介面本體完全不動**（僅附加式計時 log）；`pipeline_core.py` A 軌既有處理邏輯本體不動。
4. **測試防線**（tasks §6.5 C5 驗收）：
   ```bash
   grep -nE "performance_metric|pipeline_finished|rag_finished|phases_breakdown" pipeline_core.py pipelines/orchestrator.py
   ls scripts/analyze_performance.py && python scripts/analyze_performance.py --help 2>&1 | head
   pytest tests/test_api_performance_and_robustness.py -k "performance or phase" -q
   ```
   並跑全域 `pytest tests/ -q`，尤其 `pipelines` 既有 20 pytest 必須全綠。
5. **文件與 Git 防線**（CLAUDE.md §1.3）：C5 執行報告與 TODO 更新僅留本地；**baton/ 執行報告 C1–C5 期間嚴禁 git add**，留待 C6 收官；commit/push 由 baron 手動。
### 💾 備份規則
```bash
cp pipeline_core.py .claude-logs/archive/2026-06-03_API-PERF_C5_pipeline_core.py.bak
cp pipelines/orchestrator.py .claude-logs/archive/2026-06-03_API-PERF_C5_orchestrator.py.bak
cp tests/test_api_performance_and_robustness.py .claude-logs/archive/2026-06-03_API-PERF_C5_test_api_performance_and_robustness.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
1. WIP：C5 → ✅、C6 → 🟡 WIP。
2. 歷史 Hash 自癒：`git log` 查 C1/C2/C3/C4 等仍 `待 baron 回填` 之真實 hash 並替換。
### 📁 產出規格
- 執行報告 `.claude-logs/baton/2026-06-03_API-PERF_C5_執行.md`（暫存 baton/、嚴禁 git add）；套用 template_execution.md。
- 含元數據 / §1 基準 / §2 Commit 表 / §3 變動檔案（含 .bak）/ §4 修法（附代碼）/ §5 測試（計時日誌 + CLI 輸出）/ §6 不可動清單 / §7 銜接 C6 / §8 baron 執行命令。
### 📝 §8 baron 執行命令格式要求
```bash
git add pipeline_core.py pipelines/orchestrator.py scripts/analyze_performance.py tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-06-03_API-PERF_C5_*.bak
git add .claude-logs/prompts/2026-06-03_API-PERF_C5_run_提示詞.md .claude-logs/prompts/INDEX.md .claude-logs/TODO.md
cat > /tmp/API-PERF_C5_msg.txt << 'EOF'
BE-Refactor: API-PERF C5 — 結構化計時埋點與 CLI 分析工具
1. U7 結構化計時：在 pipeline_core 舊單體 A 軌（以 stage 映射 phase）與 orchestrator
   新調度 B 軌（對齊 PhaseEnum P1-P4 迴圈）中附加結構化計時埋點，每原子步驟結束列印
   含有 (phase, stage) 二維鍵的 performance_metric 事件 JSON。
2. 主鏈完成時印出 pipeline_finished 總計時與 phases_breakdown 細分耗時；
   P4 異步 RAG 獨立記錄為 rag_finished，不併入主鏈彙總。
3. 新建獨立 Python 效能日誌分析 CLI 腳本 scripts/analyze_performance.py
   (零外部依賴、流式解析 pipeline.log、輸出 ASCII 統計報表)。
4. 新增對應單元測試驗證二維鍵埋點，且 pipelines 既有 20 pytest 維持全綠。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
git commit -F /tmp/API-PERF_C5_msg.txt
```
---
### 🛑 停止指令
產出 `C5_執行.md` 後立即停止。嚴禁續跑 C6 / 改非 C5 範圍代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（-k "performance or phase" + 全域、pipelines 20 pytest 維持）
- 改動檔案數：修改 `pipeline_core.py` / `pipelines/orchestrator.py`（各含 .bak）+ 新建 `scripts/analyze_performance.py` + 測試追加（含 .bak）；提示詞歸檔；修改 TODO.md / INDEX.md；寫 /tmp/API-PERF_C5_msg.txt
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 C4（`2026-06-03_API-PERF_C4_run_提示詞.md`）。下一步 C6 Checkout 收官歸檔（API-PERF 全案結案）。
`````
