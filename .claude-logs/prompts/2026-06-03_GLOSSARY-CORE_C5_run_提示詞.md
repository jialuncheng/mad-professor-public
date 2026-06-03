`````markdown
# 2026-06-03 — GLOSSARY-CORE C5 Run 提示詞

> **收到時間**：2026-06-03 23:10（UTC+8）
> **任務代號**：GLOSSARY-CORE C5
> **觸發 commit**：C5
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C5_執行.md`
> **觸發情境**：baron 確認 C4 落地與 RAG-14 補丁（`595e3d8`）後，下達 C5 執行指令——新建 `tools/manage_glossary.py` 自癒 CLI（`--init` / `--test-pipeline --pdf` / `--backfill-existing-papers`）；logging SOP `setup_logging`（嚴禁 basicConfig）+ 批次提交安全邊界（防 SQLite locked）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 23:10 |
| **任務代號** | GLOSSARY-CORE C5 |
| **觸發 Commit** | C5 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 C4 落地與 RAG-14 補丁後，下達 C5 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C5_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C5。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C5｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C5 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：僅新增 `tools/manage_glossary.py`，既有業務代碼嚴禁改。
2. 測試防線：執行 §6.5 C5 驗收 grep + CLI 功能測試。
3. 文件防線：commit/push 由 baron 手動。
### ⚠️ 日誌規範與批次資料庫操作硬規則
- 對齊日誌：`from utils.logging_config import setup_logging`，CLI 入口呼叫；嚴禁 logging.basicConfig。
- 批次更新安全邊界：--backfill-existing-papers 分批極短交易 `with session.begin():`（防 database locked）。
### 💾 備份規則
新建檔案、無需 .bak；若改既有檔須先備份 .claude-logs/archive/。
### 🔄 同步更新 TODO.md（必做、即時）
1. C5 → ✅；C6 → 🟡 WIP。
2. git log 查 C3/C4 + RAG-14 補丁（595e3d8）真實 Hash，自癒回填 TODO.md 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C5_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add tools/manage_glossary.py + TODO + 提示詞 + INDEX（明確列檔、報告留 baton 不 add）；msg tmp/GLOSSARY-CORE_C5_commit_msg.txt。
### 🛑 停止指令
產出 C5_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：新增 `tools/manage_glossary.py`；修改 TODO.md；新增 C5_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C5。C6（Unit Tests）由 baron 後續獨立提示詞觸發。
`````
