# 2026-05-29 — FE-AESTHETICS C2-hotfix Run 提示詞

> **收到時間**：2026-05-29 16:30
> **任務代號**：FE-AESTHETICS C2-hotfix
> **觸發 commit**：C2-hotfix
> **相關產出檔案**：.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md
> **觸發情境**：baron 確認 Hotfix Tasks 拆分完備，下達 C2-hotfix Commit 執行指令（當前 Checkout Commit: 75ab18acb2ddb570bef0d4142719be11119ce756）

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-29 16:30 |
| **任務代號** | FE-AESTHETICS C2-hotfix |
| **觸發 Commit** | C2-hotfix |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md |
| **觸發情境** | baron 確認 Hotfix Tasks 拆分完備，下達 C2-hotfix Commit 執行指令 (當前 Checkout Commit: 75ab18acb2ddb570bef0d4142719be11119ce756) |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入提示詞歸檔檔：`.claude-logs/prompts/2026-05-29_FE-AESTHETICS_C2-hotfix_run_提示詞.md`
2. 更新 INDEX.md，在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。
3. 確認完成後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：FE-AESTHETICS
- **當前 Commit 代號**：C2-hotfix (Frontend Academic Header Self-Healing)
- **工作流類別**：FE-Hotfix
- **Tasks 路徑**：.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md

### 📖 強制讀檔清單

CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md / .claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md / static/index.html / tests/test_bug_f1_frontend_micro_fix.py

### 🛠️ 執行命令

依 hotfix_tasks.md §8 C2-hotfix 具體實作細節進行修改，遵守三個防線：
1. 物理防線：後端業務邏輯 100% 不動；fetchContent 以外 JS / .paper-header-meta 以外 CSS 不動
2. 測試防線：全量 pytest 387 passed, 0 failed, 3 skipped
3. 文件防線：不自發 git commit / push

### 💾 備份規則

```bash
cp static/index.html .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_static_index.html.bak
cp tests/test_bug_f1_frontend_micro_fix.py .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_test_bug_f1_frontend_micro_fix.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做）

1. C2-hotfix 標記 ✅，Check 標記 🟡 WIP
2. git log 掃描並自動回填所有 `待 baron 回填` 佔位符

### 📁 產出規格

執行報告路徑：`.claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md`（baton 暫存，嚴禁 git add）

執行報告必須包含：§1 基準與完成狀態 / §2 Commit 表格 / §3 變動檔案清單 / §4 修法說明 / §5 測試結果 / §6 不可動清單遵守 / §7 銜接 / §8 baron 執行命令

### 📝 §8 baron 執行命令格式

```bash
git add static/index.html
git add tests/test_bug_f1_frontend_micro_fix.py
git add tests/test_fe_aesthetics_c2_hotfix.py
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_static_index.html.bak
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_test_bug_f1_frontend_micro_fix.py.bak
git add .claude-logs/prompts/2026-05-29_FE-AESTHETICS_C2-hotfix_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git commit -F /tmp/FE-AESTHETICS_HOTFIX-1_msg.txt
```

### 🛑 停止指令

產出 C2-hotfix_執行.md 並更新 TODO.md 後必須立即停止。
嚴禁：繼續執行 Check / 修改未列入本 Commit 的代碼 / 自發 git commit / git push
```

---

## 執行結果摘要

- ✅ 提示詞歸檔完成
- ✅ INDEX.md 更新完成
- ✅ static/index.html 修改完成（CSS 靠左 + normalizeAcademicHeader 函式 + fetchContent 呼叫）
- ✅ tests/test_bug_f1_frontend_micro_fix.py L129/L135 斷言自癒
- ✅ tests/test_fe_aesthetics_c2_hotfix.py 新建
- ✅ pytest 387 passed, 0 failed, 3 skipped
- ✅ 執行報告產出至 baton/
- ✅ TODO.md 更新（C2-hotfix ✅，Check 🟡 WIP，歷史 hash 自癒）
- 等待 baron 手動 commit C2-hotfix
