`````markdown
# 2026-06-03 — DOMAIN-NORM C3 Run 提示詞

> **收到時間**：2026-06-03 18:38（UTC+8）
> **任務代號**：DOMAIN-NORM C3
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_DOMAIN-NORM_C3_執行.md`
> **觸發情境**：baron 確認 C2 後，下達 C3 執行指令——`domain_normalizer.py` 暴露模組級入口 `normalize_to_lcc(raw_domain, context_text=None)->LCCCode`（簽名逐字對齊 PIPE-SPEC §1.2.1 / PIPE master v10 L69）+ `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False、False 走舊 raw 直注不查 DB/不呼 LLM）；改既有檔前 `.bak` + C3 標記包裹。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 18:38 |
| **任務代號** | DOMAIN-NORM C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` |
| **觸發情境** | baron 確認 C2 Commit 後，下達 C3 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C3_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C3。
### 📋 任務資訊
- 任務編碼 `DOMAIN-NORM`｜當前 Commit `C3`｜工作流 `BE-Refactor`
- Tasks 路徑 `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / DOMAIN-NORM tasks / database_SOP / logging_SOP
### 🛠️ 執行命令（五防線）
1. 代碼包裝標籤：`# === [DOMAIN-NORM C3 START/END] ===`（settings.py + domain_normalizer.py）。
2. 單一入口：`normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode`，簽名逐字對齊 PIPE-SPEC / PIPE master v10。
3. 熱插拔旗標：`settings.LLM_USE_GLOSSARY_ALIGN` 預設 False；False → 直接回傳 raw_domain，不查 DB/不呼 LLM。
4. 物理防線：僅擴充入口 + 設定旗標，嚴禁改 models.py Paper / domain_detector / rag_retriever。
5. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp settings.py .claude-logs/archive/2026-06-03_DOMAIN-NORM_C3_settings.py.bak`（domain_normalizer.py 為 C2 新建未版控、無需 .bak，但改動仍用 C3 標記包裹）。
### 🔄 同步更新 TODO.md（必做、即時）
1. C3 → ✅；C4 → 🟡 WIP。
2. git log 查 C2 真實 Hash，自癒回填 TODO.md C2 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C3_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add settings.py + domain_normalizer.py + .bak + TODO.md（明確列檔、報告留 baton 不 add）；msg /tmp/DOMAIN-NORM_C3_msg.txt。
### 🛑 停止指令
產出 C3_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`settings.py`（+旗標、先 .bak）+ `processor/domain_normalizer.py`（+公開入口）；修改 TODO.md；新增 C3_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 DOMAIN-NORM tasks §8 C3。C4（Unit Tests）由 baron 後續獨立提示詞觸發。
`````
