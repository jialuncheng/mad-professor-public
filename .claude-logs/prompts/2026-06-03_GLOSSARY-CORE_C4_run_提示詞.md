`````markdown
# 2026-06-03 — GLOSSARY-CORE C4 Run 提示詞

> **收到時間**：2026-06-03 22:35（UTC+8）
> **任務代號**：GLOSSARY-CORE C4
> **觸發 commit**：C4
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C4_執行.md`
> **觸發情境**：baron 確認 C3 落地後，下達 C4 執行指令——`AI_professor_chat.py:329-335` 旗標閘門按 `_domain`（LCC）`query_cascade` 取術語、組「不可違背 System constraint」附 character/explain prompt；前台崩潰防護 try/except graceful degradation + `=== [GLOSSARY-CORE C4 START/END] ===` 包裹 + 改前 .bak；旗標 OFF byte 等價。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 22:35 |
| **任務代號** | GLOSSARY-CORE C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 確認 C3 成功落地後，下達 C4 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C4_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C4。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜當前 Commit C4｜工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / GLOSSARY-CORE tasks §8 C4 / logging_SOP / database_SOP
### 🛠️ 執行命令（三防線）
1. 物理防線：僅改 AI_professor_chat.py domain 注入段，不動 messages 組裝/下游核心。
2. 測試防線：執行 §6.4 C4 驗收 grep + 旗標 ON/OFF 測試。
3. 文件防線：commit/push 由 baron 手動。
### ⚠️ 前台降級容錯與防線硬規則
- 防線閘門：`if settings.LLM_USE_GLOSSARY_ALIGN:` 包裹、預設 False。
- 前台崩潰防護：query_cascade 單獨 try/except graceful degradation；異常僅 error log、退回原樣注入主題領域字串（舊行為），絕不讓 DB 異常崩潰前台問答。
### ⚠️ 代碼註解包裹規範
`# === [GLOSSARY-CORE C4 START/END] ===` 包裹修改區。
### 💾 備份規則
`cp AI_professor_chat.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C4_AI_professor_chat.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C4 → ✅；C5 → 🟡 WIP。
2. git log 查 C3 真實 Hash，自癒回填 TODO.md 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C4_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add AI_professor_chat.py + .bak + TODO + 提示詞 + INDEX（明確列檔、報告留 baton 不 add）；msg tmp/GLOSSARY-CORE_C4_commit_msg.txt。
### 🛑 停止指令
產出 C4_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`AI_professor_chat.py`（旗標閘門 Chat 術語注入）+ .bak；修改 TODO.md；新增 C4_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 GLOSSARY-CORE tasks §8 C4。C5（Hot-Pluggable CLI）由 baron 後續獨立提示詞觸發。
`````
