# CHAT-EXPORT-HOTFIX-1 HOTFIX-1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 03:09 |
| 任務代號 | CHAT-EXPORT-HOTFIX-1 HOTFIX-1 |
| 觸發 Commit | HOTFIX-1 |
| 工作流類別 | FE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md` |
| 觸發情境 | baron 過目 hotfix.md 並拍板，下達 HOTFIX-1 Run 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：CHAT-EXPORT-HOTFIX-1 / Commit：HOTFIX-1 / 工作流類別：FE-Hotfix
- Hotfix 路徑：`.claude-logs/baton/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / hotfix.md（唯一依據）
- ⚠️ FE-Hotfix：logging/database SOP 不適用、跳過（合規）

### 執行命令（依 hotfix.md diff）
① 改前備份 static/index.html → archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak。
② 改 `export-btn` handler（L2802-2812）：`onclick = () =>`→`async () =>`；移除 `window.location.href` 導覽式下載；替換 fetch→blob→`<a download>`〔含 !res.ok/catch〕、`# === [CHAT-EXPORT-HOTFIX-1 START/END] ===` 包裹；保留空對話防護。
③ 收官搬移：`mv baton/...CHAT-EXPORT-HOTFIX-1_hotfix.md → hotfixes/`（FE-Hotfix Run 階段一次性歸檔）。
④ 更新 TODO：CHAT-EXPORT-HOTFIX-1 狀態；git log 自癒回填殘留「待 baron 回填」。

### 三防線
- 物理：hotfix.md 不可動清單（web_server.py / 其他 .py / 其他 static 檔案 / 空對話防護 不動）。
- 測試：三條靜態 grep（`location.href.*chat/export` 無命中 / `createObjectURL` 命中 / START/END 各 1）。
- 文件：不自發 commit/push。

### 產出規格
- 執行報告 `executions/2026-06-08_CHAT-EXPORT-HOTFIX-1_執行.md`（FE-Hotfix 直寫 executions、不過 baton）；套 template_execution。
- §5.3 SOP 核查填「FE-Hotfix 僅改 static/index.html、無 .py、logging/database 不適用、跳過（合規）」。

### §8 baron 執行命令
- git add：static/index.html + .bak + hotfix.md(hotfixes/) + 執行報告 + TODO + 2 prompts。
- msg 草稿寫 `/tmp/CHAT-EXPORT-HOTFIX-1_msg.txt`。
  ⚠️ 署名校正：依 CLAUDE.md 全局規範用 `Claude Opus 4.8 (1M context)`（提示詞模板誤寫 Sonnet 4.6、以全局規範為準）。

### 停止指令
產出執行報告後立即停止；不改 web_server/其他 .py/其他 static、不動空對話防護、不自發 commit/push。
