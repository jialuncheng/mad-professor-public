# CHAT-EXPORT-HOTFIX-1 — 緊急熱修復：對話下載在 Dia 瀏覽器卡 8/8 不結束（導覽式下載 → fetch+blob）

> **警示**：本文件為**緊急熱修復 (Hotfix) 計畫（doc-only）**。程式碼以 diff 寫入本文件、**尚未落地實檔**；待 baron 過目後下「CHAT-EXPORT-HOTFIX-1 Run」才套用。
> **工作流類別**：FE-Hotfix（僅動 `static/index.html` 一個事件處理器、零後端、零 .py）。
> **修復原則**：只改下載觸發方式（導覽式 → fetch+blob），不碰後端 export 端點、不碰空對話防護、不夾帶其他功能。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **CHAT-EXPORT-HOTFIX-1** | `待 baron 回填` | fix(chat): CHAT-EXPORT-HOTFIX-1 — 對話下載改 fetch+blob，修 Dia 導覽式下載卡 8/8 不結束 |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象描述**：在 **Dia 瀏覽器**（The Browser Company 的 Chromium AI 瀏覽器）點「下載對話」，download chip 顯示 `DeHunt_CT..._chat (1).md  8/8 KB`——**內容已全數下載（8/8）、但下載進度條/spinner 永遠不結束**（連線狀態未乾淨收尾）。
- **受災範圍**：對話紀錄下載功能（`export-btn`）**在 Dia 瀏覽器**；**Safari / Chrome 正常**（瀏覽器特定）。
- **變因隔離（決定性）**：
  ```
  同一份對話、同一台測試機、同一後端：
    Safari → 下載正常收尾 ✅
    Dia    → 卡 8/8 不結束 ❌
  → 後端與網路相同、唯一變因＝瀏覽器 → 問題在「瀏覽器如何處理下載觸發方式」。
  ```

### 2. 真因診斷 (Root Cause)

**後端正確（已排除）**：`web_server.py:983 export_chat_history` 回 `Response(content=md_content.encode('utf-8'), media_type="text/markdown", headers={"Content-Disposition": ...})`。以**真 uvicorn + curl -v 實測**（含同款 2 個 `@app.middleware("http")`：`auth_guard` + `trace_id_middleware`）：
```
< HTTP/1.1 200 OK
< content-disposition: attachment; filename=a_chat.md
< content-length: 8004          ← 正確設定（starlette 1.0.0 BaseHTTPMiddleware 不丟 Content-Length）
（無 transfer-encoding: chunked）
下載 byte 數: 8004              ← 乾淨結束
```
→ Content-Length 正確、無 chunked → 合規瀏覽器收到 8004 bytes 即 finalize。**排除「BaseHTTPMiddleware 丟 Content-Length」與「nginx 重切塊」兩個常見元兇**；Safari 正常亦反證後端無誤。

**真因＝前端「導覽式下載」寫法在 Dia 收尾異常**：
- `static/index.html:2812` 以 **`window.location.href = '/api/.../chat/export'`** 觸發下載——這是**主框架導覽（top-level navigation）去 attachment URL**。
- 同時前端有**常駐 `EventSource`**（`static/index.html:2947` `/api/papers/{id}/chat/attach` SSE 聊天串流，切 paper 才關）。
- Safari 對「導覽去 attachment」用既有 navigation 語意、收尾正常；**Dia 對此情境的收尾處理不同**（疑與導覽/SSE 長連線狀態交互），導致 download chip 卡在 100% 不關。導覽式下載本就**依賴瀏覽器各自的 navigation-download 語意**、跨瀏覽器易 flaky。
- **定位程式碼**：`file:///static/index.html#L2812`（`window.location.href` 導覽式下載）。

---

## 熱修復修法 (Minimal Hotfix)

**改用 `fetch → blob → <a download>`**：完整緩衝回應後、以 blob object URL 經隱藏 `<a download>` 觸發下載——**不依賴主框架導覽語意**，由 JS 確定性建立/點擊/釋放，**瀏覽器無關**（Safari / Chrome / Dia 全收尾）。cookie 同源自動帶（`auth_guard` 照過）、檔名由 `a.download` 決定性指定、空對話既有防護不動。

### `static/index.html` — `export-btn` 事件處理器（L2802-2812 區）

```diff
- document.getElementById('export-btn').onclick = () => {
+ document.getElementById('export-btn').onclick = async () => {   // fetch 需 async
    if (!currentPaperId) return;
    // 對話為空時擋下載（避免後端回空檔 / 錯誤）
    const realMessages = document.querySelectorAll(
      '#chat-messages .msg-user, #chat-messages .msg-ai'
    );
    if (realMessages.length === 0) {
      customAlert({ title: '目前沒有對話內容可下載', body: '請先進行對話後再下載' });
      return;
    }
-   window.location.href = `/api/papers/${currentPaperId}/chat/export`;
+   // === [CHAT-EXPORT-HOTFIX-1 START] ===
+   // Dia 等瀏覽器對「主框架導覽去 attachment URL」收尾異常（download chip 卡 8/8 不關）；
+   // 改 fetch→blob→<a download> 不依賴導覽語意、瀏覽器無關（Safari/Chrome/Dia 全收尾）。
+   try {
+     const res = await fetch(`/api/papers/${currentPaperId}/chat/export`);
+     if (!res.ok) {
+       customAlert({
+         title: '下載失敗',
+         body: res.status === 404 ? '沒有對話紀錄' : `伺服器錯誤（${res.status}）`,
+       });
+       return;
+     }
+     const blob = await res.blob();
+     const url = URL.createObjectURL(blob);
+     const a = document.createElement('a');
+     a.href = url;
+     a.download = `${currentPaperId}_chat.md`;
+     document.body.appendChild(a);
+     a.click();
+     a.remove();
+     URL.revokeObjectURL(url);
+   } catch (e) {
+     customAlert({ title: '下載失敗', body: '網路或瀏覽器錯誤，請重試' });
+   }
+   // === [CHAT-EXPORT-HOTFIX-1 END] ===
  };
```

> **不可動**：後端 `web_server.py:983 export_chat_history`（已證正確、不碰）／空對話防護（`realMessages.length === 0` 既有檢查保留）／`async` 僅為 `await fetch` 必需的簽名變更（行為等價、無副作用）。
> **檔名一致**：`a.download = '${currentPaperId}_chat.md'` 與後端 `Content-Disposition: filename={paper_id}_chat.md` 一致（fetch+blob 下檔名由前端 `download` 屬性主導）。

---

## regression 預防與 E2E 驗證（Run 階段執行）

### 1. 靜態 grep 驗收（FE-Hotfix、無 pytest 業務邏輯；對齊既有 index.html grep 測試風格）
```bash
# 導覽式下載已移除（export handler 不再用 window.location.href 打 chat/export）
grep -n "location.href.*chat/export" static/index.html        # 期望：無命中（已移除）
# fetch+blob 機制就位
grep -n "createObjectURL\|a.download = .*_chat.md\|fetch(.*chat/export" static/index.html
# 包裹標記平衡
grep -c "CHAT-EXPORT-HOTFIX-1 START" static/index.html        # 1
grep -c "CHAT-EXPORT-HOTFIX-1 END" static/index.html          # 1
```

### 2. 手動 E2E（baron 測試機、跨瀏覽器）
```
前置：已有對話的 paper。
① Dia    瀏覽器 → 點「下載對話」 → download chip 應「正常收尾」（不再卡 8/8）、檔案內容完整。
② Safari 瀏覽器 → 點「下載對話」 → 仍正常（不退化）。
③ Chrome（若有）→ 點「下載對話」 → 正常。
④ 空對話 → 點「下載」 → 仍跳「目前沒有對話內容可下載」（防護不變）。
驗收標準：三瀏覽器皆「下載完成、chip 收尾」、檔名 {paper_id}_chat.md、內容與 Safari 既有下載一致。
```

### SOP 核查
```
FE-Hotfix 工作流：僅改 static/index.html（前端）、無 .py 改動 → logging / database SOP 不適用、跳過（合規）。
```

### 不可動遵守
- `web_server.py`（後端 export 端點、middleware）— 零改動（已證正確）。
- `export-btn` 空對話防護 — 保留。
- `EventSource` / chat 串流邏輯 — 不碰。
- 主 repo 目錄 — 未讀寫。

---

## baron 執行命令與 Commit Message 草稿（Run 落地後）

```bash
# 改前 .bak（Run 時備）
cp static/index.html .claude-logs/archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak

# 入庫：前端碼 + .bak（baton 下 hotfix.md 收官移 hotfixes/）
git add static/index.html
git add .claude-logs/archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak
git add .claude-logs/hotfixes/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md
git add .claude-logs/executions/2026-06-08_CHAT-EXPORT-HOTFIX-1_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-08_CHAT-EXPORT-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-08_CHAT-EXPORT-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git commit -F /tmp/CHAT-EXPORT-HOTFIX-1_msg.txt
```

### Commit message 草稿（Run 落地時寫入 `/tmp/CHAT-EXPORT-HOTFIX-1_msg.txt`）
```
fix(chat): CHAT-EXPORT-HOTFIX-1 — 對話下載改 fetch+blob，修 Dia 導覽式下載卡 8/8 不結束

真因：static/index.html export-btn 以 window.location.href 導覽去 attachment URL 觸發下載；
Dia 瀏覽器對「主框架導覽去 attachment」收尾與 Safari/Chrome 不同（配常駐 SSE）→ download chip
卡 8/8 KB 不結束。後端 export 端點已證正確（真 uvicorn+curl content-length 8004、無 chunked、
Safari 正常）。修法：改 fetch→blob→<a download>，不依賴導覽語意、瀏覽器無關（Safari/Chrome/Dia
全收尾）；保留空對話防護、後端零改。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
> ⚠️ 本檔 doc-only，msg 寫進文件（Run 落地時才寫 /tmp）。

---

## 回退與備案

```bash
git revert <CHAT-EXPORT-HOTFIX-1 hash>          # 或還原 archive/2026-06-08_CHAT-EXPORT-HOTFIX-1_index.html.bak
```
僅改前端下載觸發方式、無資料/schema/後端變動 → 回退即恢復 `window.location.href` 導覽式下載、無副作用。

---

## 後續（非本 hotfix）
- **可選強化**：若 paper 標題含特殊字元，未來可由後端回傳 `X-Filename` 或前端取 `Content-Disposition` 解析檔名（本 hotfix 沿用 `{paper_id}_chat.md`、與既有後端一致、不擴範圍）。
- **共用化**：若其他下載點（如未來匯出 PDF）也用 `window.location.href`，可抽 `downloadViaBlob(url, filename)` helper 統一（本 hotfix 只修對話下載受災點、不夾帶）。
