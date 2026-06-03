`````markdown
# 2026-06-03 — GLOSSARY-CORE C6 Run 提示詞

> **收到時間**：2026-06-03 23:36（UTC+8）
> **任務代號**：GLOSSARY-CORE C6
> **觸發 commit**：C6
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C6_執行.md`
> **觸發情境**：baron 確認 C5 落地後，下達 C6 執行指令——新建 `tests/test_glossary_core.py` 5 測試（唯一約束 / 級聯優先 / 書籍融合優先 / Chat 注入 / CLI 回填）；mock LLM、不實打 API；file-based SQLite + FK ON fixture。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 23:36 |
| **任務代號** | GLOSSARY-CORE C6 |
| **觸發 Commit** | C6 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 C5 成功落地後，下達 C6 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C6_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C6。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C6｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C6 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：僅新增 `tests/test_glossary_core.py`，既有業務/DB 代碼嚴禁改。
2. 測試防線：`pytest tests/test_glossary_core.py -v` 5 綠 + `pytest tests/ -q` 無 regression。
3. 文件防線：commit/push 由 baron 手動。
### ⚠️ 測試中資料庫與 Mock 安全硬規則
- fixtures 設 `PRAGMA foreign_keys = ON`，合理模擬 Session 連接與事務。
- LLM/外部 API 一律 mock 隔離、嚴禁實打。
### 💾 備份規則
新建測試檔、無需 .bak。
### 🔄 同步更新 TODO.md（必做、即時）
1. C6 → ✅；C7 → 🟡 WIP。
2. git log 查 C5 真實 Hash，自癒回填 TODO.md 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C6_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add tests/test_glossary_core.py + TODO + 提示詞 + INDEX（明確列檔、報告留 baton 不 add）；msg tmp/GLOSSARY-CORE_C6_commit_msg.txt。
### 🛑 停止指令
產出 C6_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：新增 `tests/test_glossary_core.py`（5 測試）；修改 TODO.md；新增 C6_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C6 + plan §6.1。C7（Checkout 收官）由 baron 後續獨立提示詞觸發。
`````
