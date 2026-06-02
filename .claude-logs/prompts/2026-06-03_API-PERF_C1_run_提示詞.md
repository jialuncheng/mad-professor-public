`````markdown
# 2026-06-03 — API-PERF C1 run 提示詞

> **收到時間**：2026-06-03 07:09（UTC+8）
> **任務代號**：API-PERF C1
> **觸發 commit**：C1
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_C1_執行.md
> **觸發情境**：baron 確認 tasks_v3 規格後下達 C1 執行指令——U6 SQLite 連接池與防鎖死（db.py busy_timeout 30s + QueuePool + pool_pre_ping），修改區塊以 `=== [API-PERF C1 START/END] ===` 包裹，建 tests/test_api_performance_and_robustness.py。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 07:09`                                           |
| **任務代號**     | `API-PERF C1`                                                |
| **觸發 Commit**  | `C1`                                                         |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 確認 tasks 規格，下達本次 C1 執行指令`                |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_API-PERF_C1_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **當前 Commit 代號**：`C1` ｜ **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks_v3（§8 C1） / logging SOP / database SOP
### 🛠️ 執行命令與代碼註解防線
依 `tasks_v3.md §8 C1 — 資料庫連接池與防鎖死配置（U6 SQLite QueuePool）` 修改：
1. **通用代碼註解防線**：修改既有原始碼處以 `# === [API-PERF C1 START] ===` / `# === [API-PERF C1 END] ===` 包裹（利後續審計/Flip 移除）。
2. **物理防線**（tasks §7）：不改既有 RAG 核心檢索演算法/閾值、不破壞 API 路由/簽名。
3. **測試防線**（tasks §6.1 C1 驗收）：
   ```bash
   grep -nE "busy_timeout=30000|QueuePool|pool_pre_ping" db.py
   pytest tests/test_api_performance_and_robustness.py -k db -q
   ```
   並跑全域 `pytest tests/ -q` 確保零迴歸。
4. **文件與 Git 防線**（CLAUDE.md §1.3）：C1 執行報告與 TODO.md 更新僅留本地；**baton/ 執行報告 C1–C5 期間嚴禁 git add**，留待 C6 收官；commit/push 由 baron 手動。
### 💾 備份規則
```bash
cp db.py .claude-logs/archive/2026-06-03_API-PERF_C1_db.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
1. WIP：C1 → ✅、C2 → 🟡 WIP。
2. 歷史 Hash 自癒：`git log` 查 PIPE-SCAFFOLD 等仍 `待 baron 回填` 之真實 hash 並替換。
### 📁 產出規格
- 執行報告 `.claude-logs/baton/2026-06-03_API-PERF_C1_執行.md`（暫存 baton/、嚴禁 git add）；套用 template_execution.md。
- 含元數據塊 / §1 基準與完成 / §2 Commit 表 / §3 變動檔案（含 .bak）/ §4 修法（附代碼）/ §5 測試結果（db pool 參數 + pytest）/ §6 不可動清單 / §7 銜接 C2 / §8 baron 執行命令。
### 📝 §8 baron 執行命令格式要求
```bash
# 2. git add 清單（執行報告嚴禁加入）
git add db.py
git add tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-06-03_API-PERF_C1_db.py.bak
# 3. commit message 草稿（已寫入 /tmp/API-PERF_C1_msg.txt）
cat > /tmp/API-PERF_C1_msg.txt << 'EOF'
BE-Refactor: API-PERF C1 — 資料庫連接池與防鎖死配置
調整 SQLite busy_timeout 為 30 秒，並在 create_engine 中配置 QueuePool
（pool_size=5, max_overflow=10, pool_pre_ping=True）以提升併發寫鎖耐受性。
新增對應單元測試驗證連線參數，維持既有測試全綠。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
# 4. baron 手動執行
git commit -F /tmp/API-PERF_C1_msg.txt
```
---
### 🛑 停止指令
產出 `C1_執行.md` 後立即停止。嚴禁續跑 C2 / 改非 C1 範圍代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（tests/test_api_performance_and_robustness.py -k db + 全域）
- 改動檔案數：修改 `db.py`（U6，含 .bak）；新建 `tests/test_api_performance_and_robustness.py`；提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 API-PERF tasks_v3 §8 C1。下一步 C2 流式上傳與真實 IP。
`````
