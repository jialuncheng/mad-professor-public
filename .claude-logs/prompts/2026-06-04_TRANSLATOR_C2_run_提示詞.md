`````markdown
# 2026-06-04 — TRANSLATOR C2 Run 提示詞

> **收到時間**：2026-06-04 13:59（UTC+8）
> **任務代號**：TRANSLATOR C2
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_TRANSLATOR_C2_執行.md`
> **觸發情境**：baron 確認 C1 後，下達 C2 執行指令——`processor/translator.py` 補 `Translator` 類 + Prompt Engine（系統提示詞五步：text_type 路由含 caption / doc_type Style Hints / LCC 領域注入讀 ctx.domain_name 零 DB / Glossary 強約束含大小寫不敏感 / constraints 注入 + 用戶提示詞）；新建 `prompt/translate/caption_translate_prompt.txt`；C2 標記包裹、改前 .bak。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 13:59 |
| **任務代號** | TRANSLATOR C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_TRANSLATOR_C2_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C2。
### 📋 任務資訊
- 任務編碼 TRANSLATOR｜當前 Commit C2｜工作流 BE-Refactor
- Tasks `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TRANSLATOR tasks §8 C2 / database_SOP
### 🛠️ 執行命令與標記規則（四防線）
1. 物理防線：§7 不可動逐項確認、不越界。
2. 測試防線：執行 §6.2 C2 驗收 grep + Prompt Engine 測試。
3. 註記包裝：改既有檔處 `# === [TRANSLATOR C2 START/END] ===` 包裹。
4. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp processor/translator.py .claude-logs/archive/2026-06-04_TRANSLATOR_C2_translator.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C2 → ✅；C3 → 🟡 WIP。
2. git log 掃描 + 自癒回填「待 baron 回填」佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_TRANSLATOR_C2_執行.md`（套 template_execution，§1-§8、baton 不入 git）。
### 📝 §8 baron 執行命令格式
git add translator.py + caption_translate_prompt.txt + .bak + TODO + 提示詞 + INDEX（明確列檔、baton 報告不 add）；msg /tmp/TRANSLATOR_C2_msg.txt。
### 🛑 停止指令
產出 C2_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`processor/translator.py`（+Translator 類 + Prompt Engine）+ 新建 `caption_translate_prompt.txt` + .bak；修改 TODO.md；新增 C2_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 TRANSLATOR tasks §8 C2。C3（Dual-Mode Routing & Thinking）由 baron 後續獨立提示詞觸發。
`````
