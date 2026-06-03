`````markdown
# 2026-06-03 — GLOSSARY-CORE C2 Run 提示詞

> **收到時間**：2026-06-03 20:07（UTC+8）
> **任務代號**：GLOSSARY-CORE C2
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C2_執行.md`
> **觸發情境**：baron 確認 C1 落地後，下達 C2 執行指令——新建 `processor/glossary_extractor.py` GlossaryManager：`query_cascade`（專屬覆寫 general）+ LLM `extract_terms`（**交易外**）+ `upsert_terms`（INSERT OR IGNORE 冪等）；database SOP 交易邊界鐵律。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 20:07 |
| **任務代號** | GLOSSARY-CORE C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 C1 成功落地後，下達 C2 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C2_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C2。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C2｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C2 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：僅新增 `processor/glossary_extractor.py`，既有業務代碼嚴禁改。
2. 測試防線：執行 §6.2 C2 驗收 grep + 功能測試。
3. 文件防線：commit/push 由 baron 手動。
### ⚠️ 資料庫併發安全硬規則（database SOP）
- LLM `extract_terms` 必在 `session.begin()` 交易外（防 SQLite locked）。
- `upsert_terms` 極短交易僅 `session.execute(...on_conflict_do_nothing)`、即提交。
### 💾 備份規則
新建檔案、無需 .bak；若改既有檔須先備份 .claude-logs/archive/。
### 🔄 同步更新 TODO.md（必做、即時）
1. C2 → ✅；C3 → 🟡 WIP。
2. git log 查 C1 真實 Hash，自癒回填 TODO.md 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C2_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add glossary_extractor.py + TODO.md + 提示詞 + INDEX（明確列檔、報告留 baton 不 add）；msg tmp/GLOSSARY-CORE_C2_commit_msg.txt。
### 🛑 停止指令
產出 C2_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：新增 `processor/glossary_extractor.py`；修改 TODO.md；新增 C2_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C2。C3（Translate Integration & Backfill）由 baron 後續獨立提示詞觸發。
`````
