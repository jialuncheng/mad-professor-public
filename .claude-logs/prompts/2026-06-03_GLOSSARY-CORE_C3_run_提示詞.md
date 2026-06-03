`````markdown
# 2026-06-03 — GLOSSARY-CORE C3 Run 提示詞

> **收到時間**：2026-06-03 22:05（UTC+8）
> **任務代號**：GLOSSARY-CORE C3
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C3_執行.md`
> **觸發情境**：baron 確認 C2 落地後，下達 C3 執行指令——`translate_processor.py:237-239` 旗標閘門注入級聯術語表 + `pipeline_core.py` translate 後背景回填 hook；全 `if settings.LLM_USE_GLOSSARY_ALIGN:` 閘門 + 回填 try/except 非阻塞 + `=== [GLOSSARY-CORE C3 START/END] ===` 包裹 + 改前 .bak；旗標 OFF byte 等價舊行為。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 22:05 |
| **任務代號** | GLOSSARY-CORE C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 C2 成功落地後，下達 C3 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C3_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C3。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C3｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C3 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：僅改 translate_processor.py + pipeline_core.py 接入；旗標 OFF byte 等價舊行為。
2. 測試防線：執行 §6.3 C3 驗收 grep + 旗標 ON/OFF 測試。
3. 文件防線：commit/push 由 baron 手動。
### ⚠️ 業務接入與非阻塞自癒硬規則
- 防線閘門：所有接入以 `if settings.LLM_USE_GLOSSARY_ALIGN:` 包裹、預設 False。
- 回填非阻塞：pipeline_core 提取+回填獨立 try/except，異常僅 error log、絕不中斷翻譯核心流程。
### ⚠️ 代碼註解包裹規範
`# === [GLOSSARY-CORE C3 START/END] ===` 包裹兩檔修改區。
### 💾 備份規則
`cp processor/translate_processor.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_translate_processor.py.bak`
`cp pipeline_core.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_pipeline_core.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C3 → ✅；C4 → 🟡 WIP。
2. git log 查 C2 真實 Hash，自癒回填 TODO.md 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C3_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add translate_processor.py + pipeline_core.py + 2 .bak + TODO + 提示詞 + INDEX（明確列檔、報告留 baton 不 add）；msg tmp/GLOSSARY-CORE_C3_commit_msg.txt。
### 🛑 停止指令
產出 C3_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`translate_processor.py`（旗標閘門術語注入）+ `pipeline_core.py`（背景回填 hook）+ 2 .bak；修改 TODO.md；新增 C3_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C3。書籍 ParallelChapterTranslator 雙層融合延後（TRANSLATE-BOOK 未落地）。C4（Chat Injection）由 baron 後續獨立提示詞觸發。
`````
