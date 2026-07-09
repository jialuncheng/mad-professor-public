# 設計理念總綱 · MadPro UI

> 本檔為**理念**而非規範。所有其他規範文件都應遵循這份。
> 與主題無關 — 不論未來掛 Mies、Kahn、Wright、或其他主題，這些原則不變。

---

## 1. 五大核心理念

### 1.1 結構誠實（Structural Honesty）
- UI 元素的視覺重量應反映其功能重量：
  - 結構性分隔（三欄之間） = 主分隔線 `--color-divider`
  - 元件邊框（按鈕、modal） = 同色 1px
  - 裝飾性弱邊（paper-item、訊息泡） = `--color-border`
- **不靠陰影偽造層次**。深度由色階與結構線承擔。

### 1.2 Token 唯一事實
- **任何色、距、字、線**只可走 token，不寫死數值
- 改值改 token，不改使用點
- 例外：`rgba(0,0,0,0.4)` Modal mask、`#fff` 反白文字屬白名單

### 1.3 主檔／主題分層
- **主檔**（`Mad Professor Redesign.html`）= 結構：間距 / 按鈕尺寸 / layout / 行為 / fallback
- **主題**（`themes/*.css`）= 外觀：色票 / 字族 / 字距 / 圓角 / 分隔線粗細 / 印刷規則
- 切換主題只改一行 `<link href>`，不應改動任何 HTML 或 JS

### 1.4 桌面瀏覽器優先
- 三欄固定布局（260 / flex / 420）
- 鍵盤可達為基本要求；無 RWD 義務
- 行動裝置目前不支援；未來若需要，於主檔加 `@media` 不污染主題

### 1.5 中文為主、混排為輔
- 介面文字一律繁體中文
- 拉丁文僅在縮寫、品牌、技術術語、原文引用出現
- 文案語氣、標點規範 → 詳見 `copywriting.md`

---

## 2. 視覺語彙繼承

兩個現行主題共享的視覺承諾：

| 承諾 | 出處 |
|---|---|
| 直角（`--radius-* = 0`） | Mies 嚴格幾何 / Kahn 古典銘文皆採方 |
| 無陰影 | Mies「拒裝飾」、Kahn「材料誠實」 |
| 1px 起跳結構線 | Mies 1px、Kahn 2px；皆「線而非塊」 |
| **非襯線字族** | 介面密度區 12-14px 可讀性、中文 fallback 黑體系一致；**全主題硬規範**（詳 typography.md） |
| 大字微緊縮（Mies）/ 微鬆（其他） | 配合各主題字族特性 |
| 中文不斜體 | 瀏覽器斜體扭曲中文，違反誠實 |
| **論文 metadata 用 `-` 列表、不用 `>` blockquote** | marked.js GFM 對 `>` 單換行不分段、5 行 metadata 會塌成一段；改 `-` 列表 + 包 `<div class="paper-header-meta">` wrap、前端 `@media screen` class hook hide（BUG-B2 / ui-fixes-batch B8） |

**未來新主題如違反以上任一**（例如想做圓角現代風），須在該主題 README 註明，並承擔不一致風險。

---

## 3. 反規範優先級（衝突仲裁）

當多個規範衝突，**從上到下**生效：

1. 不可違反 — 保留 id 契約（DOM Reference §8）
2. 可讀性 — 中文閱讀體驗第一（typography）
3. 視覺一致 — icon、按鈕、色彩規範
4. 美學承諾 — 主題 credo
5. 規範條文 — 各 .md 文件

例：icon-spec 寫「平常無框」，但實作上有按鈕需要永遠視覺存在 — 仲裁時可破例，但須在 component 規格補註明。

---

## 4. 文件閱讀順序（給新進團隊／Claude Code）

1. **principles.md**（本檔）— 先讀；建立心智模型
2. **dom-reference.md** — DOM 契約；不可違反的 id / class
3. **api-integration.md** — 後端串接全圖
4. **components.md** — 元件規格速查
5. **icon-spec.md / typography.md / color-tokens.md / spacing.md** — 按需查
6. **interaction.md** — 互動細節
7. **theme-guide.md** — 要做新主題時讀
8. **copywriting.md** — 寫新文案時讀

---

## 5. 反向約束（什麼不該做）

- ❌ 為了快速完成而 inline `style=""` — 永遠走 class
- ❌ 為了主題而修改 HTML 結構 — 主題只能改外觀
- ❌ 為了 a11y 而加裝飾性 `aria-label` — 只用必要的 aria
- ❌ 為了「看起來像 X 框架」而引入 X 框架 — 維持單檔輕量
- ❌ 為了支援舊瀏覽器而放棄 CSS Grid / Flex gap — 桌面新版瀏覽器優先

---

## 6. 演化原則

- **加法為主、減法慎重**：移除既有 token / class 必須先全域搜尋確認無依賴
- **修舊不破新**：改 token 值前先確認所有使用點視覺仍合理
- **規範可改，但要解釋**：本檔可被推翻，但須在 commit 訊息或 PR 描述寫明「為何破例」

---

## 7. 認定範圍

本理念**僅限本專案**。Claude / Claude Code 不該將其推及其他 Anthropic 產品設計，亦不應假設使用者其他作品須遵循。

---

## 8. 範圍外（明確不做）

本專案**目前不處理**以下面向，未來上線前請另行評估：

| 項目 | 現況 | 理由 |
|---|---|---|
| Screen Reader 支援 | 未實作 | 用戶族群暫不含視障；介面語意僅優化 keyboard + 視覺對比 |
| 響應式（RWD） | 未實作 | 桌面瀏覽器 only；窄於 1100px 不保證可用 |
| 觸控目標達 44/48px | 未調 | 桌面 mouse-only；icon-only 採 32×32；若上行動端需另升 40-44px |
| 國際化（多語 UI） | 未實作 | 介面文字固定繁體中文；文章內容才支援 zh/en 切換 |
| 暗色模式 | 未實作 | 由主題系統承擔，未來可新增 mies-dark 等 |

⚠ 接這個專案的工程師若要補上述項目，需同步重審 `interaction.md` 鍵盤章節、`color-tokens.md` 對比度章節。
