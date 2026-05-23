# Interaction 設計規格 · MadPro UI

> 元件「靜態長相」由 components.md 規範；本檔規範**動態行為**：
> 五態切換、過渡時序、開關互動、鍵盤、捲動行為。

---

## 1. 五態定義

所有可互動元素必須涵蓋以下狀態（不適用者忽略，不可遺漏）：

| 狀態 | 觸發 | 視覺契約 |
|---|---|---|
| **idle** | 預設 | 元件 baseline 樣式 |
| **hover** | 滑鼠進入 | `--color-surface` 底（icon-only）或邊框深一階；**文字色不動** |
| **active** | 滑鼠按下瞬間 | `--color-surface-2` 底（icon-only）；**僅按住期間** |
| **selected**（持續啟用態）| `.active` class | 實心 `--color-accent` 底 + 白前景；非 click-feedback |
| **disabled** | `:disabled` 或 `disabled` 屬性 | `opacity: 0.5`、`cursor: not-allowed`；不觸發 hover |
| **focus-visible** | 鍵盤 tab | `outline: 2px solid var(--color-text); offset: 1px`；滑鼠 focus 不出現 |

⚠️ `active` 與 `selected` 命名衝突注意：
- CSS `:active` 偽類 = 按下瞬間（click feedback）
- HTML `.active` class = 持續啟用態（如搜尋開啟）
- 兩者**互不衝突**，皆同時可生效

---

## 2. 過渡（transition）時序

| 場景 | 時長 | 緩動 | 變數 |
|---|---|---|---|
| 顏色 / 背景 / 邊框切換 | 150ms | ease | `--transition` |
| 欄位收合 / 展開 | 180ms | ease | hardcoded `width 180ms ease` |
| Chevron 旋轉 | 150ms | ease | `--transition` |
| Tooltip 顯示 | 100ms（淡入） | ease | hardcoded |
| Modal 顯示 | 0（瞬間） | — | 故意不加 transition；保結構誠實 |
| Popup 顯示 | 0（瞬間） | — | 同上 |
| 進度條填充 | 200ms | ease | hardcoded |
| 占位列脈動 | 1.6s | ease-in-out | `paperUploadingPulse` keyframes |
| 點閃動畫 | 1s | ease-in-out | `paperUploadingBlink` keyframes |

**原則**：UI 反饋 ≤ 200ms；動畫只用於「等待」與「持續狀態」。

---

## 3. Tooltip 觸發 / 隱藏

### 觸發
- 滑鼠進入 `[data-tip]` 元素 → 啟動 200ms 計時
- 200ms 內離開 → 取消，不顯示
- 滿 200ms → 顯示
- **接力**：若已有 tooltip 顯示中（或在 100ms 離開緩衝期），移入新 `[data-tip]` 立即切換內容，不重新等 200ms

### 自動消失
- **顯示後 800ms 自動消失**，即使滑鼠仍停在同一個 icon 上
- 自動消失後，停留同一 icon **不重新觸發**；須先離開該 icon、再回來才會重新計時
- **設計緣由（有意偏離標準）**：標準 tooltip（Apple HIG / Material）只要 hover 就常駐。本系統採 800ms 自動消失，原因是現階段 icon 圖形仍在打磨，tooltip 為輔助而非主要訊息來源；常駐 tooltip 會干擾使用者讀文章。日後 icon 系統穩定後可重新評估改回常駐

### 隱藏
- 滑鼠離開 `[data-tip]` → 排程 100ms 後隱藏（緩衝相鄰 icon 間移動）
- 100ms 內移到另一 `[data-tip]` → 取消隱藏、接力顯示新內容
- 視窗捲動（任一容器）→ 立即隱藏（不達 100ms）
- 視窗失焦 → 立即隱藏
- 點擊任意處 → tooltip 不變，依然按 hover 規則

### 位置算法
1. 預設：icon 左側（右撇子鼠標習慣）
2. 左側放不下（`left < 4px`）→ 改右側
3. 上下邊界保護：top 限 `[4, viewport - height - 4]`

---

## 4. Popup 觸發 / 關閉

### 觸發
- 點對應 `.menu-btn` / `.paper-menu-btn` / `.dropdown-trigger`
- 若已開同類 popup → 視為 toggle，**關閉**而非重新定位

### 關閉
- 點 popup 外任意處
- 視窗捲動（capture phase 監聽）
- 視窗 resize
- 點 popup 內某項目 → 觸發該項目動作後關閉

### 定位演算法（per-item popup）
- 水平：靠 `item.right - popup.width - 4px` 對齊 item 右緣
- 垂直：`btn.bottom + 4px`；若超出視窗下緣 → 翻到 `btn.top - popup.height - 4px`

### 定位演算法（dropdown popup）
- 水平：`trigger.left`，寬度 = `trigger.width`
- 垂直：`trigger.bottom - 1px`（重疊 1px 邊框、視覺貼齊 native）

---

## 5. Modal 開關

### 開啟
- 對應觸發事件 → 容器加 `.show` class
- 自動聚焦：**目前未實作**；建議未來補 `autofocus` 在主按鈕

### 關閉
| Modal | 點 mask | 主按鈕 | ESC | 取消鈕 |
|---|---|---|---|---|
| `#help-modal` | ✅ | ✅ | ⚠️ 未實作 | — |
| `#confirm-modal` | ❌ 故意不可 | ✅ | ⚠️ 未實作 | — |

**原則**：流程關鍵 modal（confirm-modal）不可點外面取消，避免誤關。

---

## 6. 收合 Rail 動畫

- 觸發：點各欄漢堡按鈕
- 動作：`width 260px → 48px` 或 `420px → 48px`
- 時長 180ms ease
- 內容（`#paper-list`、`#folder-tree`、`#chat-messages` 等）`display: none`，**不參與動畫**
- 漢堡 icon 永遠保留並貼齊分隔線

---

## 7. 鍵盤行為（現況）

| 鍵 | 範圍 | 行為 |
|---|---|---|
| Tab | 全域 | 標準 focus 巡覽 |
| Shift+Tab | 全域 | 反向巡覽 |
| Ctrl+Enter | `#chat-input` | 送出訊息（IME 組字中不觸發） |
| Enter | `#chat-input` | 換行（避免誤送）；autocomplete 開啟時 = 確認當前 hashtag |
| Tab | `#chat-input` | autocomplete 開啟時 = 確認當前 hashtag（RAG-1 P2-3） |
| ↑↓ | `#chat-input` | autocomplete 開啟時 = 切換選項（RAG-1 P2-3） |
| Esc | `#chat-input` | autocomplete 開啟時 = 關閉 popup（RAG-1 P2-3）；未實作其他 popup/modal |

## 12. 不在規範內的範圍

| 項目 | 處理 |
|---|---|
| Screen Reader | 不做 — 未來補時須加 aria-*, live region, lang 動態切換 |
| RWD | 不做 — 桌面瀏覽器 only |
| ↑↓ / Enter 操作 popup | 規劃中（鍵盤增強，但目前手動 click 為主） |
| 手機觸控 | 不做 — `@media (hover: none)` 只處理 hover 切換（如 paper-menu-btn 永遠顯示） |

詳見 `principles.md` §8。

---

## 8. 捲動行為

- 三欄各自有獨立捲軸（`#paper-list`、`#folder-tree`、`#paper-content`、`#chat-messages`）
- 任何捲動事件 → 自動關閉 popup 與 tooltip（避免錨點失準）
- 文章區捲到底 → 不觸發 lazy load（目前無此功能）
- chat 訊息新增 → 自動 `scrollTop = scrollHeight`

---

## 9. 上傳流程互動鏈

```
點 #upload-btn
  ↓
原生 file picker
  ↓
POST /api/papers/upload
  ↓
顯示 #confirm-modal（無法點外關閉）
  ↓
點 #confirm-ok-btn
  ↓
POST /api/papers/{id}/confirm_type
  ↓
建立 SSE EventSource
  ↓
左欄頂端插入 .paper-item.uploading
  ↓
processing 事件 → 更新 .paper-progress-fill width + text
  ↓
progress.index >= 10 → 標記 reading_ready；若未在看別篇 → 自動 loadPaper
  ↓
done 事件 → 關 SSE、移除占位、重抓 GET /api/papers、解鎖 chat
```

---

## 10. AI 問答互動鏈

```
輸入 #chat-input 內容
  ↓
Ctrl+Enter
  ↓
立即插入 .msg-user
  ↓
立即插入 .msg-ai（▋ 佔位）
  ↓
POST /api/papers/{id}/chat（SSE）
  ↓
每個 sentence chunk → 累積 → marked.parse → 覆寫 .msg-ai.innerHTML
  ↓
done chunk → 渲染 .msg-sources（若有）+ POST chat/history 持久化
```

---

## 11. 反例

- ❌ Modal 加開啟動畫 → 違反「結構誠實，瞬間出現」
- ❌ 在 hover 上改文字色 → 違反「hover 只動背景」
- ❌ Tooltip 觸發 < 200ms → 滑鼠經過時亂閃
- ❌ Popup 不關自動消失 → 用 setTimeout 隱藏會打架使用者意圖
- ❌ 用 `:hover` 模擬持續選中 → 用 `.active` class
