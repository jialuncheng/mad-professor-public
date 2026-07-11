````markdown
# 2026-07-11 — SEC-SECRET SEC-SECRET-hotfix 提示詞

> **收到時間**：2026-07-11 16:39（UTC+8）
> **任務代號**：SEC-SECRET SEC-SECRET-hotfix
> **觸發 commit**：SEC-SECRET-hotfix
> **相關產出檔案**：.claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md
> **觸發情境**：PROJECT-REVIEW 安全審查 #1 HIGH——SESSION_SECRET 硬編碼 fallback 常數致認證繞過，執行緊急熱修復 Run 階段（落地 settings.py + web_server.py + 新增測試）。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-11 16:39 |
| 任務代號 | SEC-SECRET SEC-SECRET-hotfix |
| 觸發 Commit | SEC-SECRET-hotfix |
| 相關產出檔案 | .claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md |
| 觸發情境 | PROJECT-REVIEW 安全 #1 HIGH——SESSION_SECRET 硬編碼 fallback 致認證繞過，執行緊急熱修復 |

## 🗄️ 第一步：主動歸檔本提示詞（先歸檔 → 更新 INDEX → 回覆歸檔完成後續行）

你現在扮演 Claude Code，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊
- 任務編碼：SEC-SECRET
- 當前 Commit 代號：SEC-SECRET-hotfix
- 工作流類別：BE-Hotfix
- Tasks 路徑：.claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md /
baton/2026-07-11_SEC-SECRET_..._hotfix.md / logging_SOP / database_SOP / frontend SOP

### 🛠️ 執行命令（三防線）
1. 物理防線：只改 settings.py + web_server.py，並新增 tests/test_session_secret_failclosed.py。
2. 測試防線：pytest tests/ 全通過、無 regression。
3. 文件防線：commit/push 由 baron 手動、嚴禁自發。

### 💾 備份規則
cp settings.py .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_settings.py.bak
cp web_server.py .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_web_server.py.bak

### 🔄 同步更新 TODO.md 狀態 + 歷史 Hash 自癒回填（雙源 TODO.md + archive/TODO_done_archive.md）
- SEC-SECRET-hotfix 標 ✅ 已完成
- git log 掃描「待 baron 回填」佔位符 → 替換真實 hash（雙源物理對齊）

### 📁 產出規格
- 執行報告路徑：更新原 baton/2026-07-11_SEC-SECRET_..._hotfix.md
- 套用模板：template_hotfix.md（補齊實測輸出、SOP 核查、diff）
- 含：落地 Commit 表格 / 真因 / 修法 diff / regression E2E（真實 pytest）/ §5 SOP 核查 / §8 baron 執行命令

### 📝 §8 baron 執行命令格式（備份完成 + 逐檔 git add〔settings.py / web_server.py / tests 新檔 / 2 .bak〕+ commit message 草稿 /tmp/SEC-SECRET_..._msg.txt + git commit -F）

### 🛑 停止指令
更新 _hotfix.md 暫存檔後立即停止。嚴禁：改未列入之代碼 / 自發 git commit/push / Run 階段移出 baton。
```

---

## 執行結果摘要

- ✅/❌ 見文末（本檔）
- pytest baseline → final
- 改動檔案：settings.py + web_server.py + tests/test_session_secret_failclosed.py（+2 .bak）
- commit / push：無（§1.3 baron 手動；baton 待 Checkout 才歸檔）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
