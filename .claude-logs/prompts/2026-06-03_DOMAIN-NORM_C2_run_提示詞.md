`````markdown
# 2026-06-03 — DOMAIN-NORM C2 Run 提示詞

> **收到時間**：2026-06-03 18:28（UTC+8）
> **任務代號**：DOMAIN-NORM C2
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_DOMAIN-NORM_C2_執行.md`
> **觸發情境**：baron 確認 C1 後，下達 C2 執行指令——新建 `processor/domain_normalizer.py` 對齊器核心：快取查→LLM 收斂(Temp=0.0)→動態註冊(INSERT OR IGNORE)→寫回；**LLM 呼叫必須在 DB 交易外**；併發冪等 upsert + try/except 降級 general；logging SOP。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 18:28 |
| **任務代號** | DOMAIN-NORM C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` |
| **觸發情境** | baron 確認 C1 Commit 後，下達 C2 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C2_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C2。
### 📋 任務資訊
- 任務編碼 `DOMAIN-NORM`｜當前 Commit `C2`｜工作流 `BE-Refactor`
- Tasks 路徑 `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / DOMAIN-NORM tasks / database_SOP / logging_SOP
### 🛠️ 執行命令（六防線）
1. 代碼包裝標籤（若改既有檔）：`# === [DOMAIN-NORM C2 START/END] ===`。
2. **交易邊界鐵律**：LLM/外部 API（_llm_classify）必須完全在 `session.begin()` 之外；取得代碼後才開極短交易寫 Domains/DomainMapping。
3. 併發與錯誤自癒：INSERT OR IGNORE/upsert 冪等防 IntegrityError；try/except 包裹、失敗降級 "general" 不阻斷。
4. 物理防線：僅新增 `processor/domain_normalizer.py`，嚴禁改 models.py Paper / domain_detector / rag_retriever。
5. 測試與日誌：logger 記錄快取命中與 LLM 判定；異常 `logger.error(..., exc_info=True)`。
6. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
新建檔案，無需備份；若意外改既有檔須先備份 .claude-logs/archive/。
### 🔄 同步更新 TODO.md（必做、即時）
1. C2 → ✅；C3 → 🟡 WIP。
2. git log 查 C1 真實 Hash，自癒回填 TODO.md C1 佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C2_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add processor/domain_normalizer.py + TODO.md（明確列檔、報告留 baton 不 add）；msg /tmp/DOMAIN-NORM_C2_msg.txt。
### 🛑 停止指令
產出 C2_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：新增 `processor/domain_normalizer.py`；修改 TODO.md；新增 C2_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 DOMAIN-NORM tasks §8 C2。C3（Entry & Feature Flag）由 baron 後續獨立提示詞觸發。
`````
