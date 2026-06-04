`````markdown
# 2026-06-04 — PIPE-RESUME C7-hotfix Run 提示詞

> **收到時間**：2026-06-04 22:24（UTC+8）
> **任務代號**：PIPE-RESUME C7-hotfix
> **觸發 commit**：C7-hotfix（策略註冊缺失與加載鏈修復）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C7-hotfix_執行.md`
> **觸發情境**：baron 確認 C6 後，影子測試服上傳履歷 PDF 觸發 `NullStrategy` → P1 `NotImplementedError` 阻斷 Bug（runtime 路徑無人 import resume_pipeline → @register('resume') 不觸發）。下達 BE-Hotfix：`pipelines/__init__.py` 補 `from pipelines import resume_pipeline` 觸發註冊；備份 .bak + 測試 + factory._registry 驗證 + 移出 baton→hotfixes/ + TODO 同步後即停（不自發 commit）。

---

## 完整提示詞

````
# 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 22:24 |
| **任務代號** | PIPE-RESUME C7-hotfix |
| **觸發 Commit** | C7-hotfix |
| **相關產出檔案** | .claude-logs/baton/2026-06-04_PIPE-RESUME_C7-hotfix_hotfix.md |
| **觸發情境** | baron 確認 C6 後，影子測試服發現 NullStrategy 策略加載缺失阻斷 Bug，下達此熱修復指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_PIPE-RESUME_C7-hotfix_run_提示詞.md`（依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行）。
3. 回覆「✅ 提示詞已歸檔：...」後續執行。

你現在扮演 Claude Code，執行緊急熱修復（BE-Hotfix）。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C7-hotfix / 工作流 BE-Hotfix
- Hotfix 規劃路徑 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C7-hotfix_hotfix.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / C7-hotfix_hotfix.md / logging_SOP / database_SOP

### 🛠️ 執行命令
1. 💾 備份：`cp pipelines/__init__.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix___init__.py.bak`
2. 📝 最小改動：`pipelines/__init__.py` 末尾加
   ```python
   # === [PIPE-RESUME C7-hotfix START] ===
   from pipelines import resume_pipeline
   # === [PIPE-RESUME C7-hotfix END] ===
   ```
3. 🧪 驗收：`pytest tests/test_resume_pipeline.py -v` + `python -c "from pipelines.factory import PipelineFactory; import pipelines; print(PipelineFactory._registry)"`（須印出 'resume'）

### 🔄 同步更新 TODO.md
PIPE-RESUME 任務 C6 與 C7 之間插入 `- [x] ✅ C7-hotfix — 緊急熱修復：ResumePipeline 策略註冊缺失與加載鏈修復（待 baron 回填）`；歷史 Hash 自癒。

### 📁 產出與移出規格
- 套用 template_execution；執行報告先暫存 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C7-hotfix_執行.md`。
- Hotfix 移出鐵律：產報告並通過驗證後，mv hotfix_hotfix.md + 執行.md → `.claude-logs/hotfixes/` + git add。

### 📝 §8 baron 執行命令
git add pipelines/__init__.py + .bak + TODO.md；msg 寫 /tmp/PIPE-RESUME_C7-hotfix_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出與移動 C7-hotfix_執行.md 後立即停止。嚴禁續跑 C7 Checkout（待 baron commit+push 測試機測試後另行下達）；嚴禁自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`pipelines/__init__.py` 補 `from pipelines import resume_pipeline`（觸發 @register('resume')）+ .bak
- 測試：test_resume_pipeline 15 passed + factory._registry 含 'resume' + 全套件防 Regression
- 移出：hotfix_hotfix.md + 執行.md → hotfixes/
- 是否 commit / push：否（msg 寫 /tmp、baron 手動；嚴禁自發）

## 後續引用

承 C1-C6（四 Phase 落地）+ C7 收官。本 C7-hotfix 修復線上策略註冊缺失；待 baron commit+push 測試機驗證後，C7 Checkout（已於 21:50 前收官、本 hotfix 為其後緊急補丁）由 baron 另行協調。
`````
