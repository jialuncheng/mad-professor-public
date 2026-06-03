`````markdown
# 2026-06-03 — GLOSSARY-CORE C1 Run 提示詞

> **收到時間**：2026-06-03 19:55（UTC+8）
> **任務代號**：GLOSSARY-CORE C1
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C1_執行.md`
> **觸發情境**：baron 確認 tasks 拆分後，下達 C1 執行指令——`models.py` 新增 `GlobalGlossary` 表（`(source_lang,target_lang,term_key,domain)` 聯合唯一約束 + 級聯查詢輔助索引）；`Paper` 等既有表不動；`=== [GLOSSARY-CORE C1 START/END] ===` 包裹；改前 `.bak`。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 19:55 |
| **任務代號** | GLOSSARY-CORE C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 tasks 拆分後，下達 C1 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C1_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C1。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C1｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C1 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：除新增 `GlobalGlossary` 表外，既有表欄位與關係不得改。
2. 測試防線：執行 §6.1 C1 驗收 grep + import 檢測。
3. 文件防線：commit/push 由 baron 手動。
代碼包裹：`# === [GLOSSARY-CORE C1 START/END] ===`。
### 💾 備份規則
`cp models.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C1_models.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C1 → ✅；C2 → 🟡 WIP。
2. git log 掃描 + 自癒回填所有「待 baron 回填」佔位符為真實 Hash。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C1_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add models.py + .bak（明確列檔、報告留 baton 不 add）；msg 草稿 tmp/GLOSSARY-CORE_C1_commit_msg.txt。
### 🛑 停止指令
產出 C1_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：新表 import + create_all 驗證（見 C1_執行.md §5）
- 改動檔案數：`models.py`（+`GlobalGlossary` 表）+ `.bak` 備份；新增 C1_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C1。C2（Glossary Core & Cascading Retrieval）由 baron 後續獨立提示詞觸發。
`````
