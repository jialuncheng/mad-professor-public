````markdown
# 2026-07-11 — SEC-SECRET Check 提示詞

> **收到時間**：2026-07-11 18:00（UTC+8）
> **任務代號**：SEC-SECRET Check
> **觸發 commit**：SEC-SECRET-Check
> **相關產出檔案**：.claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md
> **觸發情境**：SEC-SECRET-hotfix 程式碼 commit 已由 baron 手動提交，下達 Conformance 驗收與收官歸檔指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-11 18:00 |
| 任務代號 | SEC-SECRET Check |
| 觸發 Commit | SEC-SECRET-Check |
| 相關產出檔案 | .claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md |
| 觸發情境 | SEC-SECRET-hotfix 程式碼 Commit 已由 baron 手動提交，下達 Conformance 驗收與收官歸檔指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先歸檔 → 更新 INDEX → 回覆後續行）

你現在扮演 Claude Code，請對本任務執行 Conformance 驗收，全部合規後執行收官歸檔。

### 📋 任務資訊
- 任務編碼：SEC-SECRET
- Plan/Tasks/執行報告：baton/2026-07-11_SEC-SECRET_..._hotfix.md（單一文件追蹤·template_hotfix）

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / TODO.md / baton hotfix 檔

### ✅ Conformance 驗收流程（五維度）
| 目標規格 | hotfix §真因 | settings 隨機 Ephemeral + web_server prod「未設」「弱金鑰」雙 fail-closed |
| 驗收條件 | hotfix §regression | tests/test_session_secret_failclosed.py 通過且含 teardown 污染清理 |
| 不可動清單 | hotfix §修復原則 | 變動僅 settings.py + web_server.py + 一新增測試檔 |
| 提示詞歸檔稽核 | prompts/ 物理目錄 | ls prompts/ | grep SEC-SECRET 存在且入 Git |
| msg.txt 草稿完整性 | hotfix §Commit 草稿 | 含完整 cat > /tmp/... 與 commit 草稿 |
→ 產 Conformance 驗收表格；不符暫停、全綠才收官。

### 🗃️ 收官自動化動作（全綠才執行）
1. 更新 TODO.md（雙層 §2.1/§2.4/§2.5）：archive/TODO_done_archive.md 追加「Phase 4.X SEC-SECRET 密鑰安全修補」表格；TODO.md ✅ 索引加一行；移除 active SEC-SECRET；類別索引標 ✅；歷史 hash 自愈補填（git log 讀真 hash 雙源替換「待 baron 回填」）
2. 歸檔 baton：mv hotfix → hotfixes/ + git add；git rm --cached（|| true）
3. 確認 baton 僅剩 README
4. git add prompts 三份（hotfix/run/check）+ INDEX
5. staged 自檢：git diff --cached --name-only 須完全等於宣告集合
6. 產 executions/2026-07-11_SEC-SECRET_checkout_執行.md（Conformance 五維度 + staged 自檢 + §8 commit 指令）+ git add

### 🛑 停止指令
完成 TODO 更新與歸檔後停止。嚴禁自發 git commit / push（最後 checkout commit 由 baron 手動）。

### 📝 §8 baron 執行命令格式（checkout 執行報告中）
cat > /tmp/SEC-SECRET_check_msg.txt << 'EOF'
chore(security): SEC-SECRET hotfix 收官歸檔與 Conformance 驗收
- 歸檔暫存文件至 hotfixes/...
- 更新 TODO.md 及 archive/TODO_done_archive.md 完成史歸檔
- 歸檔提示詞並更新 prompts/INDEX.md
- 產出 checkout 執行報告
EOF
git commit -F /tmp/SEC-SECRET_check_msg.txt
```

---

## 執行結果摘要

- ✅/❌ 見 executions/2026-07-11_SEC-SECRET_checkout_執行.md
- Conformance 五維度全綠 → 收官
- baton 歸檔至 hotfixes/、TODO 雙層結案 + hash 自癒、提示詞入版控
- commit / push：無（§1.3 由 baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
