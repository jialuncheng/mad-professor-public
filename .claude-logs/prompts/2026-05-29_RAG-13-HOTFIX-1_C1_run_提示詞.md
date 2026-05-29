# 2026-05-29 — RAG-13-HOTFIX-1 C1 Run 提示詞

> **收到時間**：2026-05-29 13:34
> **任務代號**：RAG-13-HOTFIX-1 C1
> **觸發 Commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md`
> **觸發情境**：baron 審查通過 hotfix 規劃，下達 C1 執行指令，開始修復 scroll 攔截誤傷問題

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-29 13:34 |
| **任務代號** | RAG-13-HOTFIX-1 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md |
| **觸發情境** | baron 審查通過 hotfix 規劃，下達 C1 執行指令，開始修復 scroll 攔截誤傷問題 |

工作流類別：FE-Hotfix
Tasks 路徑：.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md

強制讀檔清單：
CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md（已自動載入）
.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_tasks.md（§8 C1 實作細節）

備份規則：cp static/index.html .claude-logs/archive/2026-05-29_RAG-13-HOTFIX-1_C1_static_index.html.bak

baton/ 暫存鐵律：執行報告 C1_執行.md 嚴禁 git add，僅在 Check 階段歸檔。

執行：依 tasks.md §8 C1 具體實作細節
1. 修改 static/index.html L1622 scroll handler 加 ctx-popup 過濾
2. 新增 tests/test_rag13_hotfix1_scroll_intercept.py（2 pytest）

產出：.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md

§8 baron 執行命令：嚴禁包含 baton/ 檔案
git add static/index.html
git add tests/test_rag13_hotfix1_scroll_intercept.py
git add .claude-logs/archive/2026-05-29_RAG-13-HOTFIX-1_C1_static_index.html.bak
git add .claude-logs/prompts/2026-05-29_RAG-13-HOTFIX-1_C1_run_提示詞.md

停止指令：產出 C1_執行.md 後必須立即停止。
嚴禁：❌ 執行下一 Commit ❌ 其他代碼改動 ❌ git commit / push
```

---

## 執行結果摘要

- ✅ 提示詞已歸檔
- ✅ `static/index.html` L1622 scroll handler 加 ctx-popup 過濾
- ✅ 新增 `tests/test_rag13_hotfix1_scroll_intercept.py`（2 pytest）
- ✅ pytest 全通過（+新增 2，1 pre-existing 失敗）
- ✅ C1 執行報告產出至 baton/

> 本文件依 `.claude-logs/prompts/README.md §3 檔案格式` 規範建立。
