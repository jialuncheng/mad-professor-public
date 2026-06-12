# API 串接規格 · MadPro UI

> 給後端工程師、Claude Code 等任何要把 prototype 接上實機資料的人。
> **權威來源 = 原 `index.html` 既有 fetch 呼叫**。本檔列出 endpoint → UI 對應關係，
> 不杜撰、不擴張。規劃中但尚未實作的條目集中在第 12 章。

---

## 0. 通用慣例

- 全部走 **同源 cookie session**：`fetch(... , { credentials: 'include' })`
- 未登入 → `401` → 由前端導 `/login`（目前由全域處理，個別 fetch 無 retry 邏輯）
- JSON 請求帶 `Content-Type: application/json`
- 路徑前綴：`const API = ''`（同源）
- 上傳檔案走 `multipart/form-data`，不帶 Content-Type（瀏覽器自填 boundary）

---

## 1. 論文清單

### `GET /api/papers`

**觸發點**
- 頁面初始載入（IIFE 最後一行）
- 任何「新增 / 刪除 / 移動」操作完成後
- 上傳處理 `done` 後

**Response（陣列）**
```ts
{
  id: string,                  // UUID
  title: string,               // 原文標題
  translated_title?: string,   // 翻譯標題（中文，可能缺）
  folder_id: number | null,    // 所屬資料夾；null = 未分類
}[]
```

**前端用法**
- 快取到 `allPapers`
- 經 `papersInCurrentFolder()` 篩選後渲染進 `#paper-list`

---

## 2. 論文內容

### `GET /api/papers/{paperId}/content?lang={zh|en}`

**觸發點**
- 點 `.paper-item` 切換論文（`loadPaper`）
- 點 `#lang-toggle` 切語言

**Response**
```ts
{ content: string }    // Markdown 純文字
```

**前端後處理**
- 圖片路徑改寫：`![](images/x.png)` → `![](/api/papers/{id}/images/x.png)`
- `marked.parse()` 渲染到 `#paper-content`

### `GET /api/papers/{paperId}/images/{filename}`

**用途**：圖片靜態檔代理；不直接 fetch，由瀏覽器隨 `<img>` 載入。

---

## 3. 論文上傳

### `POST /api/papers/upload`（multipart）

**觸發點**：`#upload-btn` 選 PDF 後

**Request**
```
FormData:
  file: <PDF>
```

**Response**
```ts
{
  paper_id: string,                    // UUID，後續所有狀態追蹤的鍵
  suggested_doc_type?: string,         // 'academic' | 'book' | 'technical' | 'slides' | 'web' | 'news'
}
```

**前端後處理**
- 顯示 `#confirm-modal` 讓使用者確認 `doc_type`
- 若 `suggested_doc_type === 'slides'`，`#confirm-desc` 用特殊提示

### `POST /api/papers/{paperId}/confirm_type`

**Request**
```ts
{ doc_type: 'academic' | 'book' | 'technical' | 'slides' | 'web' | 'news' }
```

**Response**：忽略；只需 2xx

**觸發點**：`#confirm-ok-btn` 點擊

---

## 4. 處理進度（SSE）

### `GET /api/papers/{paperId}/status`（EventSource）

**觸發點**：`confirm_type` 後立即建立 `new EventSource(...)`

**事件流**
每筆 `event.data` 為 JSON。三種 `status` 值：

```ts
// 進行中
{
  status: 'processing',
  progress: {
    index: number,         // 階段索引（0..11，10 = extra_info、11 = rag）
    stage_name: string,    // 階段中文名（顯示在進度文字裡）
    progress: number       // 該階段 0..100
  }
}
// 完成
{ status: 'done' }
// 失敗
{ status: 'error', error?: string }
```

**前端行為**
- `processing`：
  - 更新 `#upload-btn` 文字為「{stage_name}... {progress}%」**（原版）**
  - **本 prototype 規劃**：改為更新左欄占位列 `.paper-item.uploading` 的 `.paper-progress-text`、`.paper-progress-fill width`
  - 當 `progress.index >= 10`：把該論文標記為 `reading_ready`（內容可閱讀、AI 問答仍未就緒），若使用者沒在看別篇則自動 `loadPaper`
- `done`：
  - 關閉 SSE、復原上傳按鈕、把該論文標記為 `done`
  - 重抓 `GET /api/papers` 把占位列換成真正的 `.paper-item`
  - 若當前看的就是此論文：展開 `#chat-panel`、解鎖問答、`loadChatHistory`
- `error`：
  - 關閉 SSE、`alert(error)`、復原上傳按鈕

---

## 5. 論文刪除

### `DELETE /api/papers/{paperId}`

**觸發點**：論文 ⋯ popup「刪除文件」項目（前端先 `confirm()`）

**前端後處理**
- 若刪的是當前看的：清空 `#current-title`、`#paper-content`、`#chat-messages`、收起 toolbar、disable chat
- 重抓論文清單

---

## 6. 論文移動

### `PATCH /api/papers/{paperUuid}`

**Request**
```ts
{ folder_id: number | null }    // null = 未分類
```

**觸發點**：論文 ⋯ popup「移動到資料夾 ▸」內某項目

---

## 7. 資料夾 CRUD

### `GET /api/folders`
- **觸發**：頁面初始載入、任何資料夾變更後
- **Response**：flat 陣列
  ```ts
  { id: number, name: string, parent_id: number | null, sort_order: number }[]
  ```
- 前端用 `buildTree()` 自行組成樹

### `POST /api/folders`
- **Request**：`{ name: string, parent_id: number | null }`
- **觸發**：`#new-folder-btn` 或 folder ⋯ popup「新增子資料夾」
- **驗證**：name 1–50 字元，前端 prompt 驗證

### `PATCH /api/folders/{id}`
- **Request**：`{ name?: string, parent_id?: number | null, sort_order?: number }`
- **觸發**：folder ⋯ popup「改名」

### `DELETE /api/folders/{id}`
- **觸發**：folder ⋯ popup「刪除」（前端先 `confirm()` 警告子資料夾與內部論文）
- **語意**：子資料夾遞迴刪除；內部論文 `folder_id` 設為 `null`（回未分類）

---

## 8. AI 問答（SSE 串流）

### `POST /api/papers/{paperId}/chat`（SSE）

**Request**
```ts
{
  query: string,
  paper_id: string,             // 同 URL，重複一份
  use_web_search: boolean       // 由 #web-search-toggle 控制
}
```

**Response**：SSE 流，每行 `data: <json>`
```ts
// 中段
{ sentence: string }
// 結尾
{
  done: true,
  grounding_sources?: { uri: string, title: string }[]
}
```

**前端行為**
- 立即插入 user 訊息泡、AI 訊息泡（佔位字元 `▋`）
- 累積 `accumulated += sentence`、`marked.parse()` 後覆寫 `aiMsg.innerHTML`
- `done` 後若有 `grounding_sources`：
  - 寫入 `aiMsg.dataset.groundingSources`（JSON 字串）
  - 渲染 `.msg-sources` 來源列
- 結束後呼叫 `saveChatHistory()` 持久化整個對話

---

## 9. 對話歷史

### `GET /api/papers/{paperId}/chat/history`
- **觸發**：`loadPaper` 完成時、或上傳處理 `done` 時
- **Response**
  ```ts
  {
    role: 'user' | 'assistant',
    content: string,                          // 純文字
    grounding_sources?: { uri, title }[]      // 僅 assistant 有
  }[]
  ```

### `POST /api/papers/{paperId}/chat/history`
- **觸發**：每次 chat SSE 完成 `done` 之後
- **Request**：`{ messages: <同 GET response 結構> }`
- 前端透過 DOM 抓 `.msg-user` / `.msg-ai` 文字 + `dataset.groundingSources` 組出來

### `GET /api/papers/{paperId}/chat/export`
- **觸發**：`#export-btn` 點擊
- **行為**：`location.href = ...` 觸發瀏覽器下載 .md 檔
- **Response**：`Content-Disposition: attachment` 的 Markdown

---

## 10. 系統維護

### `POST /api/cleanup`
- **觸發**：`#cleanup-btn` 點擊（前端先 `confirm()`）
- **Response**
  ```ts
  { count: number, removed: string[] }
  ```
- 前端 `alert` 顯示結果

### `POST /logout`
- **觸發**：`#logout-btn` 點擊
- **後續**：`location.href = '/login'`

---

## 11. 認證

實際登入頁是另一個 SSR template（不在 SPA 範圍）。本 SPA 假設已登入；任何 fetch 401 應由全域 interceptor 處理（目前未實作）。

---

## 12. 規劃中（尚未實作）

⚠️ 以下功能在 UI 上有暗示，但**後端 endpoint 尚未存在**。

### 12.1 刪除對話
- **UI**：`.paper-item` ⋯ popup 中「刪除對話」項目，目前 `disabled`、title「即將上線（Phase 3.4）」
- **預期 endpoint**：`DELETE /api/papers/{paperId}/chat/history`
- **預期行為**：清空該論文的對話紀錄，前端清 `#chat-messages` 為 chat-empty 狀態

### 12.2 重新命名論文
- **UI**：目前無入口；建議加在 `.paper-item` ⋯ popup
- **預期 endpoint**：`PATCH /api/papers/{paperUuid}` 加 `{ title?, translated_title? }` 支援

### 12.3 切換介面風格
- **UI**：左欄底部 `#theme-btn` 已實作，點開 `#theme-modal` 可選 Mies / Kahn / Kandinsky / Nara
- **目前**：前端 `<link>.href` 切換 + `localStorage['madpro-theme']` 持久化，重整後自動還原
- **預期 endpoint**（接後端後改寫）：
  - `GET /api/user/preferences` → `{ theme: 'mies' | 'kahn' | 'kandinsky' | 'nara', ... }`
  - `PATCH /api/user/preferences` → `{ theme }`
- **預期行為**：登入後讀偏好優先於 localStorage、套用對應主題；切換時持久化到後端

---

## 13. 端點總表（速查）

| Method | Path | 觸發 UI |
|---|---|---|
| GET | `/api/papers` | 初始化、刪除、移動、上傳完成後 |
| GET | `/api/papers/{id}/content?lang=` | 點 paper-item、切 lang |
| GET | `/api/papers/{id}/images/{file}` | `<img>` 自動載入 |
| POST | `/api/papers/upload` | `#upload-btn` |
| POST | `/api/papers/{id}/confirm_type` | `#confirm-ok-btn` |
| GET | `/api/papers/{id}/status` (SSE) | `confirm_type` 完成後 |
| DELETE | `/api/papers/{id}` | 論文 ⋯「刪除文件」|
| PATCH | `/api/papers/{uuid}` | 論文 ⋯「移動到資料夾」|
| GET | `/api/folders` | 初始化、資料夾任何變更後 |
| POST | `/api/folders` | `#new-folder-btn`、「新增子資料夾」|
| PATCH | `/api/folders/{id}` | 「改名」 |
| DELETE | `/api/folders/{id}` | 「刪除」 |
| POST | `/api/papers/{id}/chat` (SSE) | `#chat-input` Ctrl+Enter |
| GET | `/api/papers/{id}/chat/history` | `loadPaper`、上傳完成 |
| POST | `/api/papers/{id}/chat/history` | chat 結束後 |
| GET | `/api/papers/{id}/chat/export` | `#export-btn` |
| POST | `/api/cleanup` | `#cleanup-btn` |
| POST | `/logout` | `#logout-btn` |
