`````markdown
# 2026-06-03 — API-PERF C3 run 提示詞

> **收到時間**：2026-06-03 08:14（UTC+8）
> **任務代號**：API-PERF C3
> **觸發 commit**：C3
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_C3_執行.md
> **觸發情境**：baron 確認 C2 執行報告並成功 commit 後下達 C3 執行指令——U3 廢 lifespan preload + ai_core/rag_retriever 快取容器改 OrderedDict + 上限 5 + Lazy Load + LRU popitem（+gc.collect）；`retrieve_*` 檢索演算法本體 100% 不動；修改區塊 `=== [API-PERF C3 START/END] ===` 包裹，追加 lru 測試。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 08:14`                                           |
| **任務代號**     | `API-PERF C3`                                                |
| **觸發 Commit**  | `C3`                                                         |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 確認 C2 執行報告並成功 commit，下達本次 C3 執行指令`  |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_API-PERF_C3_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **當前 Commit 代號**：`C3` ｜ **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks_v3（§8 C3）/ logging SOP / database SOP
### 🛠️ 執行命令與代碼註解防線
依 `tasks_v3.md §8 C3 — 向量庫與 RAG LRU 動態快取（U3 Lazy Load + LRU）` 修改：
1. **通用代碼註解防線**：修改既有原始碼處以 `# === [API-PERF C3 START] ===` / `# === [API-PERF C3 END] ===` 包裹。
2. **物理防線**（tasks §7）：`rag_retriever.py` 既有 `retrieve_with_context` / `retrieve_multi_with_context` 演算法與閾值**完全不動**，僅改快取容器型別與 LRU 機制。
3. **測試防線**（tasks §6.3 C3 驗收）：
   ```bash
   grep -nE "OrderedDict|popitem|move_to_end" ai_core.py rag_retriever.py
   grep -n "preload_vector_stores" web_server.py
   pytest tests/test_api_performance_and_robustness.py -k lru -q
   ```
   並跑全域 `pytest tests/ -q` 確保零迴歸。
4. **文件與 Git 防線**（CLAUDE.md §1.3）：C3 執行報告與 TODO 更新僅留本地；**baton/ 執行報告 C1–C5 期間嚴禁 git add**，留待 C6 收官；commit/push 由 baron 手動。
### 💾 備份規則
```bash
cp ai_core.py .claude-logs/archive/2026-06-03_API-PERF_C3_ai_core.py.bak
cp rag_retriever.py .claude-logs/archive/2026-06-03_API-PERF_C3_rag_retriever.py.bak
cp paper_manager.py .claude-logs/archive/2026-06-03_API-PERF_C3_paper_manager.py.bak
cp web_server.py .claude-logs/archive/2026-06-03_API-PERF_C3_web_server.py.bak
cp settings.py .claude-logs/archive/2026-06-03_API-PERF_C3_settings.py.bak
cp tests/test_api_performance_and_robustness.py .claude-logs/archive/2026-06-03_API-PERF_C3_test_api_performance_and_robustness.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
1. WIP：C3 → ✅、C4 → 🟡 WIP。
2. 歷史 Hash 自癒：`git log` 查 C1/C2 等仍 `待 baron 回填` 之真實 hash 並替換。
### 📁 產出規格
- 執行報告 `.claude-logs/baton/2026-06-03_API-PERF_C3_執行.md`（暫存 baton/、嚴禁 git add）；套用 template_execution.md。
- 含元數據 / §1 基準 / §2 Commit 表 / §3 變動檔案（含 .bak）/ §4 修法（附代碼）/ §5 測試（動態載入 + LRU 淘汰 pytest）/ §6 不可動清單 / §7 銜接 C4 / §8 baron 執行命令。
### 📝 §8 baron 執行命令格式要求
```bash
git add ai_core.py rag_retriever.py paper_manager.py web_server.py settings.py tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-06-03_API-PERF_C3_*.bak
git add .claude-logs/prompts/2026-06-03_API-PERF_C3_run_提示詞.md .claude-logs/prompts/INDEX.md .claude-logs/TODO.md
cat > /tmp/API-PERF_C3_msg.txt << 'EOF'
BE-Refactor: API-PERF C3 — 向量庫與 RAG LRU 動態快取
1. U3 廢除 lifespan 預載機制，移除 web_server 啟動時對 preload_vector_stores 的呼叫。
2. 重構 ai_core 與 rag_retriever 的快取容器為 OrderedDict，配置加載上限為 5 (可於 settings 配置)。
3. 實現 Lazy Load (按需加載) 與 LRU 快取自動淘汰機制 (超限時自動釋放最久未使用向量庫)，
   並於 popitem 後顯式呼叫 gc.collect()。既有 RAG 檢索演算法本體 100% 保持不動。
4. 新增對應單元測試驗證快取淘汰行為，維持既有測試全綠。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
git commit -F /tmp/API-PERF_C3_msg.txt
```
---
### 🛑 停止指令
產出 `C3_執行.md` 後立即停止。嚴禁續跑 C4 / 改非 C3 範圍代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（-k lru + 全域）
- 改動檔案數：修改 `ai_core.py` / `rag_retriever.py` / `paper_manager.py` / `web_server.py` / `settings.py`（各含 .bak）+ 測試追加（含 .bak）；提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 C2（`2026-06-03_API-PERF_C2_run_提示詞.md`）。下一步 C4 並發信號量與子進程降優。
`````
