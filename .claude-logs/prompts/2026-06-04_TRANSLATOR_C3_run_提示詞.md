`````markdown
# 2026-06-04 — TRANSLATOR C3 Run 提示詞

> **收到時間**：2026-06-04 14:09（UTC+8）
> **任務代號**：TRANSLATOR C3
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_TRANSLATOR_C3_執行.md`
> **觸發情境**：baron 確認 C2 後，下達 C3 執行指令——`settings.py` 新增 `LLM_THINKING_BUDGET`（+預設 TRANSLATE_MODEL 改 gemini-3.5-flash）；`llm/client.py::chat()` 補 `thinking_config` 受控擴充分支（**§4 唯一例外**、gated budget>0 且思考世代模型、前向相容）；`processor/translator.py` 實作 `Translator.translate(text,ctx,mode,text_type)` 雙模式 chat 路由；C3 標記包裹、三檔改前 .bak。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 14:09 |
| **任務代號** | TRANSLATOR C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_TRANSLATOR_C3_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C3。
### 📋 任務資訊
- 任務編碼 TRANSLATOR｜當前 Commit C3｜工作流 BE-Refactor
- Tasks `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TRANSLATOR tasks §8 C3 / database_SOP
### 🛠️ 執行命令與標記規則（四防線）
1. 物理防線：§7 不可動——llm/client.py 僅准加 thinking_config 分支（唯一例外）、_api_semaphore/retry/既有路徑不動。
2. 測試防線：執行 §6.3 C3 驗收 grep + 雙模式測試。
3. 註記包裝：改既有檔處 `# === [TRANSLATOR C3 START/END] ===` 包裹。
4. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp settings.py / llm/client.py / processor/translator.py .claude-logs/archive/2026-06-04_TRANSLATOR_C3_*.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C3 → ✅；C4 → 🟡 WIP。
2. git log 掃描 + 自癒回填「待 baron 回填」佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_TRANSLATOR_C3_執行.md`（套 template_execution，§1-§8、baton 不入 git）。
### 📝 §8 baron 執行命令格式
git add settings.py + llm/client.py + translator.py + 3 .bak + TODO + 提示詞 + INDEX（明確列檔、baton 報告不 add）；msg /tmp/TRANSLATOR_C3_msg.txt。
### 🛑 停止指令
產出 C3_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`settings.py`（+LLM_THINKING_BUDGET、TRANSLATE_MODEL 預設）+ `llm/client.py`（thinking_config 受控擴充）+ `processor/translator.py`（translate 雙模式路由）+ 3 .bak；修改 TODO.md；新增 C3_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 TRANSLATOR tasks §8 C3。C4（Formatting Fallback & Tests）由 baron 後續獨立提示詞觸發。
`````
