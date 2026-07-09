# Spacing 設計規格 · MadPro UI

> 4px 模矩制（4px modular grid），所有距離數值必須走 token。

---

## 1. 基本 scale

| Token | 數值 | 典型用途 |
|---|---|---|
| `--space-1` | `4px` | 最小間隙、tight gap、小 icon 距離 |
| `--space-2` | `8px` | normal gap、清單列 padding、輸入框內距 |
| `--space-3` | `12px` | 卡片／列 padding、loose 基礎 |
| `--space-4` | `16px` | 面板內距 `--pad-panel`、按鈕水平內距 |
| `--space-5` | `24px` | Modal 內距上、訊息區 padding、文章下標題距 |
| `--space-6` | `32px` | Modal 大內距、文章上下內距 |
| `--space-8` | `48px` | 文章左右內距、空提示上距 |
| `--content-max-w` | `760px`（主檔預設）/ 主題覆寫（kahn 720 / nara 800 / kandinsky 820 / mies 860） | 中欄 toolbar + paper-content + abstract 共軌最大寬度（寬螢幕對稱）。BUG-F1 Bug 5 / ui-fixes-batch B7 新增 |

---

## 2. 按鈕群組三階間距

| Token | 數值 | 何時用 |
|---|---|---|
| `--gap-btn-tight` | `4px` | 同類密集 icon 群（早期左欄底部三鈕已棄用） |
| `--gap-btn-normal` | `8px` | 同族群一般（標題列 icon 群、訊息↔輸入區） |
| `--gap-btn-loose` | `16px` | 不同族群（標題 ↔ 動作群） |

**判斷法**
- 同功能性質、視覺連續 → normal
- 不同功能性質、語義切分 → loose
- 密集 toolbar 上的 icon 群 → normal（不宜 tight，hit-target 太擠）

---

## 3. 面板內距

| Token | 數值 | 套用對象 |
|---|---|---|
| `--pad-panel` | `16px` | 三欄標題列、左欄底部、右欄輸入區 |
| `--chat-pad-x` | `16px` | 右欄 chat-messages 與 chat-input-area 水平內距（邊界對齊）；chat-messages 另加 `scrollbar-gutter: stable` 保留捲軸位、左右視覺對稱 |

---

## 4. 按鈕／元件尺寸

| Token | 數值 | 用途 |
|---|---|---|
| `--btn-h` | `32px` | 所有可點按鈕高度（含 dropdown trigger） |
| `--btn-pad-x` | `16px` | 文字按鈕水平內距 |
| `--btn-min-w` | `64px` | 文字按鈕最小寬 |
| `--btn-icon` | `32px` | icon-only 容器邊長（含隱形 hit-target） |
| `--btn-icon-svg` | `18px` | SVG 內框 |
| `--toolbar-h` | `48px` | 三欄標題列基準高度（中欄可加高） |
| `--rail-w` | `48px` | collapsed 邊欄寬度 |

---

## 5. 圓角

| Token | 主檔 fallback | 主題（Mies / Kahn） |
|---|---|---|
| `--radius-sm` | `0` | `0` |
| `--radius-md` | `0` | `0` |

> 兩個主題都選擇直角（Mies 嚴格幾何、Kahn 古典銘文）。
> 若未來新增 organic 主題（例如 Aalto、Wright），可在該主題 .css 改值。

---

## 6. 線條粗細

| Token | 數值 | 用途 |
|---|---|---|
| `--divider-w` | `1px`（Mies）／ `2px`（Kahn） | 三欄主分隔、文章 h2 底線 |
| 元件邊框 | 固定 `1px` | 按鈕、modal、popup、輸入框 |
| icon stroke | `1.5`（`--btn-icon-stroke`）| 全部 SVG 線條 |

---

## 7. 內距策略對照

| 元件 | 上下 | 左右 |
|---|---|---|
| 標題列（左／右） | 0（高度由 `--toolbar-h` 撐）| `--pad-panel` |
| 中欄 toolbar | `10px`（min-height 48 + 大標題撐高）| `--pad-panel` |
| chat 訊息區 | `--space-5` | `--chat-pad-x` |
| chat 輸入區 | `--pad-panel` | `--chat-pad-x` |
| 文章 paper-content | `--space-6` | `--space-8` |
| paper-item | `--space-3` | `--space-3` |
| folder-item | `--space-2` | `--space-3` |
| Modal | `--space-6` | `--space-6` |
| Popup | `--space-1` | `--space-1` |
| Tooltip | `4px` | `10px` |
| 按鈕內距 | 0（高 32 撐）| `--btn-pad-x` |

---

## 8. 反例

- ❌ `padding: 10px` 寫死 → 用 `--space-2.5` 不存在；改用 `8px` (space-2) 或 `12px` (space-3)
- ❌ `gap: 6px` → 不在 scale 上
- ❌ `margin-top: 15px` → 用 `var(--space-4)` 16px
- ❌ 在密集 icon 群用 `--gap-btn-loose` → 視覺鬆散
- ❌ 在不同族群之間用 `--gap-btn-tight` → 語義不清
