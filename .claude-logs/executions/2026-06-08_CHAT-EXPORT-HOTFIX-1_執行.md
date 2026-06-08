# CHAT-EXPORT-HOTFIX-1 HOTFIX-1 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | CHAT-EXPORT-HOTFIX-1 HOTFIX-1 |
| 執行日期 | 2026-06-09 |
| 依據規劃 | `.claude-logs/hotfixes/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md` |
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 代碼落地 + 三條靜態 grep 全綠；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：對話下載 `export-btn` 以 `window.location.href` 導覽式下載（Dia 卡 8/8 不結束）。
- **本次**：改 `static/index.html` `export-btn` handler 為 fetch→blob→`<a download>`；**FE-Hotfix、僅前端、零 .py、零後端**；未 commit。
- **工作流類別**：FE-Hotfix（單一 Commit、執行時一次性歸檔：hotfix.md 已 mv → hotfixes/、執行報告直寫 executions/）。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-1 | `待 baron 回填` | fix(chat): CHAT-EXPORT-HOTFIX-1 — 對話下載改 fetch+blob，修 Dia 導覽式下載卡 8/8 不結束 |

## §3 變動檔案清單（含備份）

```
 static/index.html | 28 ++++++++++++++++++++++++++--
 1 file changed, 26 insertions(+), 2 deletions(-)
```
備份（改前 .bak，archive/，git add 強制含）：
```
.claude-logs/archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak
```

## §4 修法說明

### 真因摘要
`static/index.html:2812` `export-btn` 以 **`window.location.href = '/api/.../chat/export'`** 觸發下載（主框架導覽去 attachment URL）。**Dia 瀏覽器**對此情境收尾異常（配常駐 `EventSource` SSE）→ download chip 卡 8/8 KB 不結束；**Safari/Chrome 正常**（瀏覽器特定）。後端 export 端點已證正確（真 uvicorn+curl `content-length: 8004`、無 chunked、Safari 正常）→ 非後端、非 nginx。

### 修法邏輯
改 **fetch → blob → `<a download>`**：完整緩衝回應後以 blob object URL 經隱藏 `<a download>` 觸發下載，**不依賴主框架導覽語意**、由 JS 確定性建立/點擊/釋放 → 瀏覽器無關（Safari/Chrome/Dia 全收尾）。cookie 同源自動帶（`auth_guard` 照過）、檔名由 `a.download` 決定性指定、空對話既有防護不動。

### 關鍵 JS 片段（`// === [CHAT-EXPORT-HOTFIX-1 START/END] ===` 包裹）
```javascript
document.getElementById('export-btn').onclick = async () => {  // fetch 需 async
  if (!currentPaperId) return;
  // ...既有空對話防護（realMessages.length === 0）不動...
  // === [CHAT-EXPORT-HOTFIX-1 START] ===
  try {
    const res = await fetch(`/api/papers/${currentPaperId}/chat/export`);
    if (!res.ok) { customAlert({ title:'下載失敗', body: res.status===404?'沒有對話紀錄':`伺服器錯誤（${res.status}）` }); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${currentPaperId}_chat.md`;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  } catch (e) { customAlert({ title:'下載失敗', body:'網路或瀏覽器錯誤，請重試' }); }
  // === [CHAT-EXPORT-HOTFIX-1 END] ===
};
```

## §5 測試結果（三條靜態 grep 真實輸出）

```
① 導覽式下載已移除（期望無命中）
   grep "location.href.*chat/export" static/index.html → 無命中 ✅

② fetch+blob 機制就位
   :2816 const res = await fetch(`/api/papers/${currentPaperId}/chat/export`);
   :2824 const blob = await res.blob();
   :2825 const url = URL.createObjectURL(blob);
   :2828 a.download = `${currentPaperId}_chat.md`;
   :2832 URL.revokeObjectURL(url);                                          ✅

③ 包裹標記平衡：START 1 / END 1                                            ✅

附加：空對話防護保留（:2808 realMessages.length === 0）✅；diff 僅 static/index.html（+26/-2）。
```

### §5.3 SOP 核查
FE-Hotfix 工作流，僅改 `static/index.html`，無 .py 改動，logging/database SOP 不適用，跳過（合規）。

### 手動 E2E（baron 測試機、跨瀏覽器）
```
① Dia 點「下載對話」→ download chip 應正常收尾（不再卡 8/8）、檔案完整。
② Safari 點「下載對話」→ 仍正常（不退化）。
③ 空對話 → 仍跳「目前沒有對話內容可下載」（防護不變）。
驗收標準：跨瀏覽器皆「下載完成、chip 收尾」、檔名 {paper_id}_chat.md、內容與 Safari 既有下載一致。
```

## §6 不可動清單遵守

- [x] `web_server.py` export 端點 / middleware — 零改動（git status 無 .py）。
- [x] 其他 `.py` / 其他 `static/` 檔案 — 未動（git status -s 僅 static/index.html）。
- [x] `export-btn` 空對話防護（`realMessages.length === 0`）— 保留不動。
- [x] `EventSource` / chat 串流邏輯 — 未碰。
- [x] 主 repo 目錄 — 未讀寫。

## §7 銜接（baton 狀態 + 下一步）

- baton：hotfix.md 已一次性 `mv` → `hotfixes/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md`；baton 無 CHAT-EXPORT 殘留。
- 執行報告直寫 `executions/`（FE-Hotfix 不過 baton）。
- 下一步：baron 手動 commit（msg 已備 `/tmp/CHAT-EXPORT-HOTFIX-1_msg.txt`）+ Dia/Safari 跨瀏覽器 E2E 驗收。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak）

# 2. git add 清單
git add static/index.html
git add .claude-logs/archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak
git add .claude-logs/hotfixes/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md
git add .claude-logs/executions/2026-06-08_CHAT-EXPORT-HOTFIX-1_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-08_CHAT-EXPORT-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-08_CHAT-EXPORT-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/CHAT-EXPORT-HOTFIX-1_msg.txt
git commit -F /tmp/CHAT-EXPORT-HOTFIX-1_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <HOTFIX-1 hash>          # 或還原 archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak
```
僅改前端下載觸發方式、無資料/schema/後端變動 → 回退即恢復 `window.location.href` 導覽式下載、無副作用。
