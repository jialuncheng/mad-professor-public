`````markdown
# 2026-06-03 — API-PERF C2 run 提示詞

> **收到時間**：2026-06-03 07:26（UTC+8）
> **任務代號**：API-PERF C2
> **觸發 commit**：C2
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_C2_執行.md
> **觸發情境**：baron 確認 C1 執行報告後下達 C2 執行指令——U4 upload_paper 1MB 分塊流式寫 + %PDF 魔術字節(415)/100MB(413)；U5 login X-Forwarded-For 真實 IP；修改區塊 `=== [API-PERF C2 START/END] ===` 包裹，追加 streaming/forwarded 測試。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 07:26`                                           |
| **任務代號**     | `API-PERF C2`                                                |
| **觸發 Commit**  | `C2`                                                         |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 確認 C1 執行報告，下達本次 C2 執行指令`               |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_API-PERF_C2_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **當前 Commit 代號**：`C2` ｜ **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks_v3（§8 C2）/ logging SOP / database SOP
### 🛠️ 執行命令與代碼註解防線
依 `tasks_v3.md §8 C2 — 流式上傳與真實 IP 解析（U4 Streaming + U5 Real IP）` 修改：
1. **通用代碼註解防線**：修改既有原始碼處以 `# === [API-PERF C2 START] ===` / `# === [API-PERF C2 END] ===` 包裹。
2. **物理防線**（tasks §7）：`/api/papers/{paper_id}/images/{filename}` 實體路徑防逃逸 `relative_to` 校驗不可觸碰。
3. **測試防線**（tasks §6.2 C2 驗收）：
   ```bash
   grep -nE "1024\s*\*\s*1024|%PDF|X-Forwarded-For" web_server.py
   pytest tests/test_api_performance_and_robustness.py -k "streaming or forwarded" -q
   ```
   並跑全域 `pytest tests/ -q` 確保零迴歸。
4. **文件與 Git 防線**（CLAUDE.md §1.3）：C2 執行報告與 TODO 更新僅留本地；**baton/ 執行報告 C1–C5 期間嚴禁 git add**，留待 C6 收官；commit/push 由 baron 手動。
### 💾 備份規則
```bash
cp web_server.py .claude-logs/archive/2026-06-03_API-PERF_C2_web_server.py.bak
cp tests/test_api_performance_and_robustness.py .claude-logs/archive/2026-06-03_API-PERF_C2_test_api_performance_and_robustness.py.bak
```
### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）
1. WIP：C2 → ✅、C3 → 🟡 WIP。
2. 歷史 Hash 自癒：`git log` 查 C1 等仍 `待 baron 回填` 之真實 hash 並替換。
### 📁 產出規格
- 執行報告 `.claude-logs/baton/2026-06-03_API-PERF_C2_執行.md`（暫存 baton/、嚴禁 git add）；套用 template_execution.md。
- 含元數據 / §1 基準 / §2 Commit 表 / §3 變動檔案（含 .bak）/ §4 修法（附代碼）/ §5 測試（streaming + XFF pytest）/ §6 不可動清單 / §7 銜接 C3 / §8 baron 執行命令。
### 📝 §8 baron 執行命令格式要求
```bash
# 2. git add 清單（執行報告嚴禁加入）
git add web_server.py
git add tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-06-03_API-PERF_C2_web_server.py.bak
git add .claude-logs/archive/2026-06-03_API-PERF_C2_test_api_performance_and_robustness.py.bak
git add .claude-logs/prompts/2026-06-03_API-PERF_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/API-PERF_C2_msg.txt）
cat > /tmp/API-PERF_C2_msg.txt << 'EOF'
BE-Refactor: API-PERF C2 — 流式上傳與真實 IP 解析
1. U4 upload_paper 端點：移除一次性 file.read()，重構為 1MB 分塊流式寫入臨時檔，
   首個 1MB chunk 校驗前 5 位元組之 %PDF 魔術字節（非 PDF 回 415），超 100MB 截斷回 413。
2. U5 login 端點：IP 解析優先獲取 X-Forwarded-For 最左 IP，防止代理環境下鎖死閘道。
3. 新增對應單元測試驗證，維持既有測試全綠。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
# 4. baron 手動執行
git commit -F /tmp/API-PERF_C2_msg.txt
```
---
### 🛑 停止指令
產出 `C2_執行.md` 後立即停止。嚴禁續跑 C3 / 改非 C2 範圍代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（-k "streaming or forwarded" + 全域）
- 改動檔案數：修改 `web_server.py`（U4+U5，含 .bak）+ `tests/test_api_performance_and_robustness.py`（追加，含 .bak）；提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 C1（`2026-06-03_API-PERF_C1_run_提示詞.md`）。下一步 C3 向量庫 LRU 動態快取。
`````
