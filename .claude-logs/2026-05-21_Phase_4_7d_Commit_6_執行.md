# Phase 4.7d Commit 6 — 執行報告（前端互動小修）

> 基準：`b277d87`（Phase 4.7d Commit 5：多檔上傳）
> 完成：1 commit 本地建立完成，**未 push**

---

## Commit Hash

| # | Hash | Subject |
|---|---|---|
| 6 | `62ebe07` | fix(frontend): chat-input 初始鎖住 + export-btn 空對話擋下載 |

## diff stat

```
 static/index.html | 21 +++++++++++++++++++--
 1 file changed, 19 insertions(+), 2 deletions(-)
```

純前端、單檔 4 處小修。

---

## 修正 1：chat-input 初始未鎖住

**真因**：`<textarea id="chat-input">` 與 `<button id="web-search-toggle">` HTML 預設都沒 `disabled` 屬性。`enableChat()` / `disableChat()` 邏輯對的，但**初始載入頁面沒任何 paper 被選 → 不會走 disableChat → 使用者可在沒選文件時輸入問題**（按 Ctrl+Enter 後才 error）。

**修法**：
- L1212 `<button id="web-search-toggle">` 加 `disabled`
- L1225 `<textarea id="chat-input">` 加 `disabled`
- chat-input 加 `focus` 監聽：`currentPaperId` 空時 `alert + blur`（雙保險：正常 disabled 後 focus 不會觸發、若未來某 bug 沒套 disabled 這層補友善訊息）

## 修正 2：對話為空時按下載按鈕沒擋

**真因**：`export-btn` onclick 只擋 `!currentPaperId`、沒擋「chat-messages 無真實訊息」→ 剛載 paper 沒發問就按 → 後端回空檔或錯誤。

**修法**：
```js
const realMessages = document.querySelectorAll(
  '#chat-messages .msg-user, #chat-messages .msg-ai'
);
if (realMessages.length === 0) { alert('目前沒有對話內容可下載'); return; }
```

**注意**：實際訊息 class 是 `.msg-user` / `.msg-ai`（grep L2276 既有 `saveChatHistory` 用同樣 selector，已驗）；`.chat-empty` / `#reading-ready-msg` 是系統提示、不算對話內容。

---

## 不可動清單（已遵守）

- [x] 後端 / DB / pipeline / processor：未動
- [x] `enableChat` / `disableChat` 函式內部：未動
- [x] web-search-toggle 切換邏輯：未動
- [x] modal 設計：未動
- [x] `_deprecated/`：未動
- [x] 未引入新 CDN / 套件

---

## 端到端驗證計畫（給 baron）

### 1. 確認 commit

```bash
git log --oneline -2
# 62ebe07（Commit 6）/ b277d87（Commit 5）
```

### 2. push

```bash
git push origin HEAD:gemini-refactor
```

### 3. OrcStack

```bash
git pull
pkill -f web_server
# 重啟
```

### 4. Test A — 初始載入

- 開頁面、不選任何 paper
- 預期：
  - chat-input 灰色、不能 focus（瀏覽器 disabled 樣式）
  - web-search-toggle 灰色、不能點
  - 點 chat-input：無反應（disabled 不觸發 focus）

### 5. Test B — 選 paper

- 點任一 paper
- 預期：`enableChat()` 觸發 → chat-input / web-search-toggle 解鎖

### 6. Test C — 沒對話按下載

- 剛選 paper、還沒發問
- 點 export-btn（下載 MD）
- 預期：alert「目前沒有對話內容可下載」

### 7. Test D — 有對話按下載

- 發問 1 次、AI 回 1 次
- 點 export-btn
- 預期：正常下載 .md 檔（既有行為）

### 8. Test E — focus 監聽雙保險（DevTools 模擬）

- 開 DevTools console
- `document.getElementById('chat-input').disabled = false`（手動解除）
- 點 textarea
- 預期：alert「請先選擇文件」+ 自動 blur

### 9. console / logs（不應出現）

- `Cannot read property 'querySelectorAll' of null`
- 雙重 alert（一次點擊跳兩個）

---

## 回退方式

```bash
git revert 62ebe07 --no-edit
# 或硬退：
git reset --hard b277d87
```

---

## 全 worktree 待 push 總覽

| 群 | commits |
|---|---|
| Stage A chat stateless | 4 |
| MinerU 模組化方案 X | 5 |
| Phase 4.7c metadata 顯示 | 5 |
| Phase 4.7c 修正 1-4 | 4 |
| Phase 4.7d Commit 0 + 1 | 2 |
| Phase 4.7d Commit 2 + 3 | 2 |
| Phase 4.7d Commit 4-1 + 4-2 | 2 |
| Phase 4.7d Commit 5 | 1 |
| **Phase 4.7d Commit 6** | **1** |
| **合計** | **26** |

---

## 狀態

**1 commit 已建立、未 push、等 baron 跑完 Test A-E 後一起 push。**
