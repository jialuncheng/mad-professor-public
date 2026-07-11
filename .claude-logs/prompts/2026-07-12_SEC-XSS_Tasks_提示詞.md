````markdown
# 2026-07-12 — SEC-XSS Tasks 提示詞

> **收到時間**：2026-07-12 04:22（UTC+8）
> **任務代號**：SEC-XSS Tasks
> **觸發 commit**：SEC-XSS-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md
> **觸發情境**：baron 同意 plan v1.1（execution-ready），下達階段 2 任務拆分指令，將 SEC-XSS plan 拆為可執行 Commit 清單並同步 TODO。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-12 04:22 |
| 任務代號 | SEC-XSS Tasks |
| 觸發 Commit | SEC-XSS-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先歸檔 → 更新 INDEX → 回覆後續行）

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：SEC-XSS
- 工作流類別：FE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / SEC-XSS plan / template_tasks / template_execution / frontend SOP

### 🏢 工作目錄與修改邊界規則
- 唯一修改與新建目標：static/index.html（載入標籤+消毒邏輯）、tools/fetch_frontend_vendor.sh（追加下載段落）、static/vendor/README.md（登記指紋）、建立 static/vendor/dompurify/**、建立 tests/ 前端守衛測試。
- 後端鐵防線：嚴禁改 web_server.py 等 .py 業務代碼（.py 僅限 tests/）。
- 管線原樣鐵律：renderMarkdownWithMath 的 code/math/img 佔位抽取與回填（RAG-12/RAG-12-HOTFIX-1）嚴禁修改重構。
- 執行中產出先放 baton/（checkout 才 mv+git add 歸檔）。

### 📊 成果盤點約束（§0.5 必置文件開頭）

### ⚙️ Commit 拆分與執行限制原則
- 不提供預設 Commit 建議：自行設計最小可逆原子 Commits。
- 最後一個 Commit 必為 checkout。
- 各階段（除 checkout）產執行報告至 baton/（template_execution）。
- 各階段測試與工具同步硬性綁定：每個 Commit 必含對應 test_sec_xss_guard 測試新增（嚴禁累積至收官）。
- checkout 才 mv 歸檔 plan/tasks/執行報告至 plans/ tasks/ executions/。

### 📋 §8 六維度 Commit 拆分表格（影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作細節）
### 📝 §1 TL;DR 中文括號命名要求
### 🔄 同步更新 TODO.md（🔴 高優先最前方新增 SEC-XSS 🟡 WIP·依賴無）
### 📁 產出規格：baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md·template_tasks·WORKFLOW_SOP §6

### 🛑 停止指令：產 tasks + 更新 TODO 後停止。嚴禁：續產 _執行.md / 動業務代碼 / 自發 git commit/push。
```

---

## 執行結果摘要

- ✅ 提示詞歸檔 + INDEX 更新
- ✅ 產出 tasks.md 至 baton/、同步 TODO 🟡 WIP
- 改動檔案（本階段）：2（prompts 歸檔 + INDEX）；tasks.md 暫存 baton/ 不入版控
- commit / push：無（tasks 階段不 commit）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
