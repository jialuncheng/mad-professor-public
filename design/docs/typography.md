# Typography 設計規格 · MadPro UI

> 字體規範依「主檔（結構）」+「主題（外觀）」分層。
> 主檔只定義字級階梯與字級用途；字族（family）、字重、字距由各 `themes/*.css` 提供。
>
> **🔒 全域硬規範：所有主題字體一律使用「非襯線（sans-serif）」字族。**
> 跨主題的差異只能來自不同的 sans-serif（Helvetica / IBM Plex Sans / Jost / Quicksand …）；
> 不得引入 serif、handwriting、monospace、display 等其他類別。理由：
>   1. 介面（標題列、按鈕、tooltip、popup）需在 12–14px 高密度區可讀，sans-serif 表現最穩
>   2. 中文 fallback 走 PingFang TC / Microsoft JhengHei，皆為黑體系，與 sans-serif 搭配視覺一致
>   3. 強制統一可避免新主題切換時版面跳動（serif 與 sans 字寬／行高差異大）

---

## 1. 字級階梯（主檔 token）

| Token | 數值 | 用途 |
|---|---|---|
| `--font-xs` | `12px` | 原文標題、step-note、來源連結、tooltip |
| `--font-sm` | `13px` | 資料夾名、ghost 鈕、副資訊 |
| `--font-base` | `14px` | 內文、主按鈕、標題列文字 |
| `--font-lg` | `16px` | Modal h3、文章 h3 |
| `--font-xl` | `20px` | 文章 h2 |
| `--font-2xl` | `28px` | 文章 h1、中欄標題 `#current-title` |

> Kahn 主題會把正文與 h1 各自再放大一階（15px / 36px），維持古典經文比例。

---

## 2. 字級用途對照

| 元件 | Mies | Kahn | 備註 |
|---|---|---|---|
| body 正文 | 14px Inter | 15px IBM Plex Sans | 中欄 paper p 跟此值同步 |
| 文章 h1 | 28px / 700 / -0.01em | 36px / 500 / 0.002em | 大字微緊縮（Mies）/ 微鬆（Kahn） |
| 文章 h2 | 20px / 600 / -0.005em | 24px / 600 | 底線 1px 黑（Mies）/ 2px 冷灰（Kahn） |
| 文章 h3 | 16px / 600 | 19px / 600 | |
| 中欄 toolbar 標題 | 28px / 700 | 36px / 500 | **與 h1 同字級**（避免上下層級錯位） |
| 左/右欄 toolbar 標題 | 14px / 600 | 15px / 600 + uppercase + letter-spacing 0.16em | 次要區塊用較小、museum-label 風 |
| AI 訊息泡泡 | 14px / 1.8 | 同主檔 | line-height 加大利於閱讀 |
| 使用者訊息泡泡 | 14px / 1.6 | 同主檔 | |
| 系統訊息 .msg-system | 13px subtle | 同 | |
| popup 項目 | 13px | 同 | |
| modal h3 | 16px / 600 | 同 | |
| modal step-note | 12px subtle | 同 | |
| tooltip | 12px | 同 | |
| paper-item 中文標題 | 13px / 500 | 同 | |
| paper-item 英文原題 | 12px muted / 2-line clamp | 同 | |
| 進度文字 | 12px muted | 同 | |
| chat-empty | 13px subtle | 同 | |
| 上傳中占位列標題 | 13px / italic muted | 同 | |

---

## 3. 字族（family）

主檔提供兩個 token，主題決定值：

| Token | Mies | Kahn | Kandinsky | Nara |
|---|---|---|---|---|
| `--font-display` | Inter, Helvetica Neue, ... | IBM Plex Sans, PingFang TC, ... | Jost, Futura, ... | Quicksand, PingFang TC, ... |
| `--font-body` | 同 display | 同 display | 同 display | 同 display |
| 雲端載入 | ✅ Google Fonts | ✅ Google Fonts | ✅ Google Fonts | ✅ Google Fonts |

**規則**
- 任何 UI 文字宣告 family 時，必須用 token，**不可寫死字串**
- 一個元件只有一個字族（display 或 body），不混用
- 中欄 toolbar h2 與 paper h1 必須同字族
- Modal、popup、tooltip 一律 body 字族

---

## 4. 字重

| 用途 | weight |
|---|---|
| 一般文字 | 400 |
| 標籤、按鈕、強調 | 500 |
| h2 / h3 / panel 標題 | 600 |
| h1（Mies） | 700 |
| h1（Kahn） | 500（IBM Plex Sans 在 36px 大字 500 已具紀念碑感） |

---

## 5. 字距（letter-spacing）

- 一般中文／拉丁文 ≥ 14px：`0`（不動）
- 大字（28px+）拉丁文：`-0.01em` 微緊縮，提升結構感（Mies）
- 大字（36px+）拉丁文（Kahn）：`0.002em` 微鬆，配 Plex Sans 大字呼吸
- **uppercase 拉丁文**：必須加 `letter-spacing`
  - Mies：`0.12em`（無噪音）
  - Kahn：`0.16em–0.22em`（museum-label 質感）

---

## 6. 行高（line-height）

| 文字類型 | line-height |
|---|---|
| 正文段落 | 1.75 – 1.8 |
| 標題 h1 / h2 / h3 | 1.2 – 1.3 |
| 按鈕、tooltip、單行 UI 文字 | 1.4 |
| 訊息泡泡 AI（內容含 list） | 1.8 |
| 訊息泡泡 user | 1.6 |
| toolbar 多行標題 | 1.25 |
| popup 項目 | 預設（由 padding 撐高） |

---

## 7. 中英混排

- 中文與拉丁文之間 **不主動加空格**（瀏覽器 / 字型自動處理）
- 中文不使用斜體（瀏覽器斜體會強制傾斜，視覺破碎）
- 引用、書名、強調 → 用 `<em>` 加色或粗體，不靠 italic

---

## 8. 反例

- ❌ 在 `<style>` 寫死 `font-family: "Helvetica"` 而不走 token
- ❌ 中文字加 `font-style: italic`
- ❌ 14px 中文加 `letter-spacing > 0.05em`（中文字距過寬不可讀）
- ❌ Toolbar 標題用比 h1 小的字級（造成上下層級顛倒）
- ❌ Tooltip 用 14px+（噪音過多、與內文同重）
