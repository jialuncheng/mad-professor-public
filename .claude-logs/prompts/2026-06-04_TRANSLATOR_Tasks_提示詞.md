`````markdown
# 2026-06-04 — TRANSLATOR Tasks 提示詞

> **收到時間**：2026-06-04 13:13（UTC+8）
> **任務代號**：TRANSLATOR Tasks
> **觸發 commit**：TRANSLATOR-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md`
> **觸發情境**：baron 同意 TRANSLATOR plan v10 規格（歷經 v1→v10 八輪 review 收斂）後，下達 tasks 拆分指令——拆 Commit 清單（彈性數量 + 最後 Checkout 收官 Commit），中間 Commit 全留 baton/、唯 Checkout 一次性歸檔；對齊已落地 DOMAIN-NORM/GLOSSARY-CORE/PIPE-CORE + PIPE-SPEC §1.2.3 v3 凍結合約。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 13:13 |
| **任務代號** | TRANSLATOR Tasks |
| **觸發 Commit** | TRANSLATOR-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_TRANSLATOR_Tasks_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，依指令將 plan 拆分為可執行 Commit 清單。
### 📋 任務資訊
- 任務編碼 TRANSLATOR｜工作流 BE-Refactor
- Plan `.claude-logs/baton/2026-06-01_TRANSLATOR_雙模式原子翻譯器_plan_v10.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TODO / TRANSLATOR plan_v10 / PIPE master v10 / PIPE-SPEC / PIPE-CORE plan_v2 / DOMAIN-NORM plan_v2 / GLOSSARY-CORE plan_v2 / database_SOP / model_recommendations / template_tasks / template_execution
### 🏢 工作目錄硬規則與暫存歸檔約束
唯一合法 worktree；嚴禁讀寫主 repo；Run 階段嚴禁改業務代碼（只讀/檢索/產 tasks）；各執行階段須產執行報告（template_execution、暫存 baton/）；baton 暫存鐵律（plan/tasks/執行報告嚴禁提前 mv/git add）；必含 Checkout Commit（唯收官一次性 mv plan→plans//tasks→tasks//執行報告→executions/ + git add）。
### 📊 成果盤點約束（§0.5 必置文件開頭）
（新增檔案 processor/translator.py + caption_translate_prompt.txt / 修改檔案 pipelines/contracts.py + llm/client.py / Commits / baton 歸檔）
### ⚙️ Commit 拆分原則（不用給 commit 建議）
彈性最小功能單元排序（C1 合約與 Context → C2 Prompt Engine → C3 Client thinking_config 受控擴充+雙模式路由 → C4 分行容錯+單元測試 → C5 Checkout）；實作細節表格內嚴禁 git commit 命令/message 草稿。
### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填）
（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）
### 📝 §1 TL;DR 中文括號命名要求（每 Commit 引用含中文括號子標題）
### 🔄 同步更新 TODO.md（必做、即時）
於 ### 🔴 高優先 最前方新增 TRANSLATOR 條目（🟡 WIP、依實際 Commit 數量）；依賴：無。
### 📁 產出規格
產出 baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md；套用 template_tasks.md；命名依 WORKFLOW_SOP §6。
### 🛑 停止指令
產出 tasks.md 並更新 TODO.md 後立即停止。嚴禁續產 _執行.md / 動業務代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（tasks 拆分階段、無代碼變動）
- 改動檔案數：新增 tasks_v1.md + 提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 TRANSLATOR plan v10（八輪 review 收斂定稿）。上游真理源 DOMAIN-NORM/GLOSSARY-CORE/PIPE-CORE 已落地、PIPE-SPEC §1.2.3 v3 凍結合約已含 text_type/domain_name/doc_type。Commit 執行階段由 baron 後續獨立提示詞觸發。
`````
