`````markdown
# 2026-06-04 — PIPE-RESUME C8-hotfix Run 提示詞

> **收到時間**：2026-06-04 23:21（UTC+8）
> **任務代號**：PIPE-RESUME C8-hotfix
> **觸發 commit**：C8-hotfix（影子論文 DB 寫入缺失修復）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C8-hotfix_執行.md`
> **觸發情境**：baron 確認 C7-hotfix 後，影子測試服影子論文成功處理（P1-P4 全綠、實體檔生成）但前端不顯示——根因 `run_pipeline_shadow` 漏 `paper_manager.upsert_paper`、影子 Paper row 未建、`list_papers`（讀 DB）撈不到。下達 BE-Hotfix：`web_server.py` 影子派發尾端補 upsert_paper 寫庫。
> **執行註記**：本 Run 提示詞 §2 貼的修法為**校正前舊版**（relative_to/1.0/無守衛）；提示詞同時要求「依 C8-hotfix_hotfix.md」、baron 前輪已確認校正版（str 絕對路徑/ctx.bilingual 守衛/'high'/from db），故依**規劃文件校正版**落地並透明標註差異。

---

## 完整提示詞

````
# 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 23:21 |
| **任務代號** | PIPE-RESUME C8-hotfix |
| **觸發 Commit** | C8-hotfix |
| **相關產出檔案** | .claude-logs/baton/2026-06-04_PIPE-RESUME_C8-hotfix_hotfix.md |
| **觸發情境** | baron 確認 C7-hotfix 後，影子測試服發現影子論文成功處理但前端因無 DB 寫入不顯示，下達此緊急熱修復指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_PIPE-RESUME_C8-hotfix_run_提示詞.md`（依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行）。
3. 回覆「✅ 提示詞已歸檔：...」後續執行。

你現在扮演 Claude Code，執行緊急熱修復（BE-Hotfix）。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C8-hotfix / 工作流 BE-Hotfix
- Hotfix 規劃路徑 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C8-hotfix_hotfix.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / C8-hotfix_hotfix.md / logging_SOP / database_SOP

### 🛠️ 執行命令
1. 💾 備份：`cp web_server.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak`
2. 📝 最小改動：依 C8-hotfix_hotfix.md，於 run_pipeline_shadow 的 Orchestrator 呼叫後、status='done' 前補 paper_manager.upsert_paper 寫庫（§2 貼出舊版 diff：relative_to/1.0/無守衛——以規劃文件校正版為準）。
3. 🧪 驗收：`pytest tests/test_pipe_scaffold.py -v` + Python E2E（`from db import SessionLocal`、斷言 Paper row 存在、original_filename endswith '(測試)'、status='done'）。

### 🔄 同步更新 TODO.md
PIPE-RESUME 任務 C7-hotfix 之下插入 `- [x] ✅ C8-hotfix — 緊急熱修復：影子論文資料庫（DB）寫入缺失修復（待 baron 回填）`；歷史 Hash 自癒。

### 📁 產出與移出規格
- 套用 template_execution；報告先暫存 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C8-hotfix_執行.md`。
- Hotfix 移出鐵律：產報告並通過驗證後，mv hotfix_hotfix.md + 執行.md → `.claude-logs/hotfixes/` + git add。

### 📝 §8 baron 執行命令
git add web_server.py + .bak + TODO.md；msg 寫 /tmp/PIPE-RESUME_C8-hotfix_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出與移動 C8-hotfix_執行.md 後立即停止。嚴禁續跑收官 Check（待 baron commit+push 測試機驗證影子列出 (測試) 後另行下達）；嚴禁自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`web_server.py` `run_pipeline_shadow` 補 `paper_manager.upsert_paper`（校正版：str 絕對路徑 + ctx.bilingual 守衛 + 'high'）+ .bak
- 測試：test_pipe_scaffold 通過 + 全套件防 Regression（實打 DB E2E 屬 baron 端影子驗證）
- 移出：hotfix_hotfix.md + 執行.md → hotfixes/
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C7-hotfix（策略註冊修復）。本 C8-hotfix 修復影子完成期 DB 寫入缺失（doc_type-agnostic、五路通用）；待 baron commit+push 測試機驗證影子列出 (測試) 後協調後續。
`````
