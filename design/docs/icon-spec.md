# Icon 設計規格 · MadPro UI

> 本檔為標準。新增或修訂 icon 時必須符合本規格。
> 設計理念：**「漢堡 ☰」為視覺重量基準** — 三條等距橫線、無端點裝飾、無內部細節。
> 所有 icon 都應落在「與漢堡相當的視覺密度」範圍。

---

## 1. 容器規格

| 項目 | 數值 | 備註 |
|---|---|---|
| 容器尺寸 | `32 × 32 px` | `--btn-icon` |
| 內部 SVG 視覺尺寸 | `18 × 18 px` | `--btn-icon-svg` |
| 圓角 | `0`（直角） | `--radius-md`，主題決定，目前主檔為 0 |
| 邊框（idle） | `1px solid transparent` | **平常無框** |
| 背景（idle） | `transparent` | |
| 背景（`:hover`） | `var(--color-surface)` | 淺底反饋 |
| 背景（`:active`） | `var(--color-surface-2)` | 按下瞬間再深一階 |
| 背景（`.active`） | `var(--color-text)` + 白 icon | 持續啟用態（如：搜尋開啟） |
| `:focus-visible` | `outline: 2px solid var(--color-text); offset: 1px` | 鍵盤可達性 |

CSS 寫法上以單一 `.icon-only` 類別承擔，避免一處一規。

---

## 2. SVG 規範

| 屬性 | 值 | 理由 |
|---|---|---|
| `viewBox` | `0 0 24 24` | 24 grid，乾淨可整除 |
| `width / height` | 由 CSS 控制（18px） | HTML 上不寫死 |
| `fill` | `none` | 一律線條，不填充 |
| `stroke` | `currentColor` | 隨容器 `color` 走，主題切換無痛 |
| `stroke-width` | `1.5` | `--btn-icon-stroke`，與 18px viewport 視覺平衡 |
| `stroke-linecap` | `round` | MR01 連續管彎質感 |
| `stroke-linejoin` | `round` | 同上；自然處理 V 形與直角 |

例外：
- 純圓點（如 `?` 的底點、`⋯` 的三點）以 `<circle>` + `fill="currentColor" stroke="none"` 繪製，視為「實心點」，不適用 stroke。

---

## 3. 視覺密度基準（漢堡參考）

漢堡：
```
M4 6h16  ─────────────
M4 12h16 ─────────────
M4 18h16 ─────────────
```
3 path、每 path 1 segment、無內角、無端點裝飾。**這是視覺密度的天花板**，多數功能 icon 應落在這個範圍上下。

**設計守則**
1. **元素數量 ≤ 4** `path` / `circle`（不含實心圓點）
2. **避免內部小細節**：以輪廓表達。例如垃圾桶不畫內部刪線、印表機不畫面板按鈕。
3. **避免雙線重疊**：例如資料夾不要疊小加號 — 改用單一加號或單一資料夾即可。
4. **轉角策略（MR01 風格）**：
   - 主結構轉角（門框、托盤、容器邊）：`a2 2 0 0 1` 弧半徑 = 2
   - 小尺寸轉角（把手、紙匣口）：`a1.5 1.5 0 0 1`
   - 銳尖（chevron、箭頭尖）：靠 `stroke-linejoin: round` 自然圓化，不用 `arc` 強制

---

## 3.5 比例守則（出現視覺輕重問題時）

當某 icon 在 32×32 容器內**視覺上明顯比漢堡輕**（例如印表機、問號、雙向箭頭），優先順序：

1. **先檢查 path 占用範圍**
   - 漢堡橫線跨度 `x:4→20`（占 16/24 = 67%）
   - 若 icon 主要路徑只占 50% 以下，**整體放大**到 60–75%
   - 例：印表機原 `M7..M17`（10 寬）放大至 `M5..M19`（14 寬）

2. **檢查 viewBox 邊界利用**
   - 漢堡使用 `y:6/12/18`（垂直跨度 12/24=50%）
   - 若 icon 集中在中央 8×8 區域 → 拉開到 14×14

3. **若 path 已最大化但仍偏輕 → 微調 stroke-width**
   - 全域基準維持 `1.5`
   - 個別 icon 可在 **1.5–1.75** 區間微調（不超過 1.75）
   - 切忌全部 icon 都改 — 失去比例參照

4. **若超過 4 個元素仍偏弱 → 重畫**
   - 視為設計失敗，重新思考圖形語意

5. **抗鋸齒陷阱**：奇數 stroke-width（1.5）會落在像素半格，比偶數（2）**視覺看似更輕**；接受此特性，或必要時用 `shape-rendering: geometricPrecision`。

---

## 4. 標準 icon 集（截至本版）

| 用途 | id / class | 圖形語意 | path 重點 |
|---|---|---|---|
| 漢堡 | `#sidebar-toggle` `#chat-toggle` | 三橫線 | 基準 |
| 新資料夾 | `#new-folder-btn` | `+` | `M12 5v14M5 12h14` — 不再疊資料夾 |
| 上傳 | `#upload-btn` | 上箭頭 + 底線 | 簡化登入式 upload |
| 登出 | `#logout-btn` | 門框 + 左向箭頭 | r=2 門框、箭頭尖靠 linejoin |
| 清理 | `#cleanup-btn` | 垃圾桶 | Lucide 標準三段：頂線、把手、桶身 |
| 系統介紹 | `#help-btn` | 圓中問號 | Lucide HelpCircle，問號弧連續 |
| 列印 | `#print-btn` | 印表機 | 三段：紙匣、機身、出紙 |
| 語言切換 | `#lang-toggle` | 水平 ⇄ | arrow-left-right，兩條反向 |
| Web 搜尋 | `#web-search-toggle` | 放大鏡 | 圓 + 斜柄 |
| 下載 MD | `#export-btn` | 下載箭頭 | 向下箭頭 + 底線 |
| 更多 | `.paper-menu-btn` `.menu-btn` | `⋯` 三點 | 三 `<circle>` r=1（BUG-F6 C7：HTML 從 `⋯` 字元 + `title` 屬性遷移到 SVG + `data-tip`、跟其他 icon-only 按鈕對齊 §5 規範） |
| chevron | `.folder-item .chevron` | `›` | 單段，靠 linejoin 圓化 |
| 後退 | `#empty-state` 箭頭 | `←` | 主箭 + 尖端弧 |

---

## 5. Tooltip 規範

所有 icon-only 按鈕必須帶 `data-tip="<簡短中文>"`：
- 字數 **2–6 字**為佳，例：`新資料夾` / `收合本欄` / `退出系統`
- 不重複按鈕已顯露的文字（避免噪音）
- 出現條件：滑鼠停留 **200ms** 後
- 出現位置：icon **左側**（適應右撇子滑鼠軌跡）
- 樣式：純白底、1px 黑線、直角、無箭頭、無陰影
- 自動消失：顯示後 **800ms** 自動消失（即使仍 hover）；同一 icon 不再觸發，須先移開
- 滑鼠離開：**100ms** 後消失；期間移到其他 [data-tip] 元素會立即接力顯示

**取代瀏覽器原生 `title`**：不再使用 `title` 屬性，以避免重複工具提示與不一致樣式。

---

## 6. 群組間距三階

| Token | 數值 | 用途 |
|---|---|---|
| `--gap-btn-tight` | `4px` | icon-only 密集群（左欄底部四鈕） |
| `--gap-btn-normal` | `8px` | 同族群一般（標題列 icon 群） |
| `--gap-btn-loose` | `16px` | 不同族群（標題 ↔ 動作群） |

---

## 7. 規範審查 checklist

新增 icon 前，請逐項勾核：

- [ ] 容器尺寸 32×32，無 padding
- [ ] viewBox 24×24
- [ ] `fill: none`、`stroke: currentColor`、`stroke-width: 1.5`
- [ ] `stroke-linecap` / `stroke-linejoin` = `round`
- [ ] 元素數量 ≤ 4
- [ ] 無內部裝飾性細節
- [ ] 視覺密度與漢堡相近
- [ ] 帶 `data-tip` 屬性（2–6 字中文）
- [ ] 不使用 `title` 屬性
- [ ] 主題切換下顏色繼承 `currentColor`，無寫死色碼

---

## 8. 反例（避免）

- ❌ 在資料夾上加小 `+` → 雙物件擠在 16×16，密度遠超漢堡
- ❌ 印表機畫面板按鈕、紙張線 → 內部細節過多
- ❌ 問號使用三段 arc 拼接 → 不對稱、視覺不平衡
- ❌ 使用 `stroke-width: 1.25`（過輕）或 `2`（過重，破壞與漢堡平衡）
- ❌ 寫死 `stroke="#000"` → 主題切換時失效
- ❌ 帶 `title="..."` → 與自訂 tooltip 共存會出現雙提示
