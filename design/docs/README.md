# MadPro UI · Design System 文件總覽

> 本資料夾為 MadPro UI 的**設計規範與工程交接全集**。
> 給新進工程師、設計改版者、Claude Code 等任何需要理解或改動 prototype 的人。
>
> 規則：實作與文件衝突時 → 以**原 `index.html` 程式碼**為準，並更新本資料夾文件。

---

## 閱讀順序

不熟悉本專案者，建議依以下順序讀；熟練後當查表用。

1. **principles.md** — 設計理念總綱（先建立心智模型）
2. **dom-reference.md** — DOM / id / class 契約（不可違反的硬規則）
3. **api-integration.md** — 後端串接全圖
4. **components.md** — 元件規格速查
5. **icon-spec.md** / **typography.md** / **color-tokens.md** / **spacing.md** — 按需查
6. **interaction.md** — 動態行為、過渡、鍵盤、捲動
7. **copywriting.md** — 寫新文案前讀
8. **theme-guide.md** — 要做新主題時讀

---

## 文件清單

| 檔名 | 角色 | 內容摘要 | 讀者 |
|---|---|---|---|
| **principles.md** | 總綱 | 五大核心理念、衝突仲裁優先級、認定範圍 | 全員 |
| **dom-reference.md** | 契約 | DOM 結構字典：每個 id / class 的用途、JS 依賴、狀態組合、不可違反契約；標示 prototype-only 元素 | 工程、Claude Code |
| **api-integration.md** | 串接 | endpoint × UI 對應、SSE 事件格式、payload / response shape、規劃中端點 | 後端、Claude Code |
| **components.md** | 規格 | 按鈕／Modal／Popup／Tooltip／Dropdown／輸入框／訊息泡／列表項／收合 Rail 結構契約 + z-index 層級 | 工程、設計 |
| **icon-spec.md** | 規格 | Icon 容器、SVG 參數、視覺密度基準、比例守則、標準 icon 集、checklist | 設計、Claude Code |
| **typography.md** | 規格 | 字級階梯、字級語意映射、字族、字重、字距、行高、中英混排守則 | 設計、Claude Code |
| **color-tokens.md** | 規格 | 14 個語意 token、主題色票對照（Mies / Kahn）、用色原則、對比度要求 | 設計、Claude Code |
| **spacing.md** | 規格 | 4px 模矩、按鈕群組三階間距、面板內距、各元件內距策略 | 設計、Claude Code |
| **interaction.md** | 行為 | 五態定義、transition 時序、popup/modal/tooltip 開關規則、上傳鏈、AI 問答鏈、鍵盤現況 | 工程、設計 |
| **copywriting.md** | 文案 | 命令式語氣、無句末標點、中英／中數字空格、tooltip 對照、術語表、錯誤訊息三段式 | 全員 |
| **theme-guide.md** | 操作 | 主題能／不能控制清單、必填 token、step-by-step 範例（Wright）、5 大陷阱 | 設計、工程 |

> 未寫：accessibility.md（暫不對外開放，鍵盤／a11y 規範待完成）

---

## 文件關係圖

```
                    principles.md
                    ─────────────
                    （理念總綱）
                          │
        ┌──────────┬──────┴──────┬──────────┐
        ▼          ▼             ▼          ▼
  dom-reference  api-           components  theme-guide
  （契約）       integration     （規格）    （操作）
                 （串接）             │
                                      │
              ┌───────────┬───────────┼───────────┬──────────┐
              ▼           ▼           ▼           ▼          ▼
        icon-spec   typography  color-tokens  spacing   interaction
        (規格)       (規格)       (規格)        (規格)    (行為)
                                                            │
                                                            ▼
                                                       copywriting
                                                        (文案)
```

- 上層（principles）只談理念
- 中層（dom-reference / api / components / theme-guide）談**結構契約**與**操作**
- 下層（icon / typography / color / spacing / interaction / copywriting）談**細節規範**

---

## 改版／新增文件守則

1. **新增規範**：先確認既有文件無法承擔該內容，再開新檔
2. **修舊規範**：先全域搜尋（grep）有無依賴；改值前驗證視覺
3. **規範可破例，但須解釋**：在 commit 或 PR 描述寫明「為何破例」
4. **更新本檔**：新增 / 廢止文件時，同步更新此清單

---

## 相關專案檔案（非 docs/）

| 檔案 | 角色 |
|---|---|
| `Mad Professor Redesign.html` | 主檔；結構層 CSS、HTML、JS |
| `themes/mies.css` | 主題 · Mies van der Rohe |
| `themes/kahn.css` | 主題 · Louis Isadore Kahn（Kimbell 美術館語彙） |
| `themes/kandinsky.css` | 主題 · Wassily Kandinsky / Bauhaus |
| `themes/nara.css` | 主題 · 奈良美智（Yoshitomo Nara） |
| `uploads/index.html` | 原始程式碼權威來源（任何文件對不上時以此為準） |
| `uploads/mad-professor_design_spec.md` | 原系統現況描述（接手資料） |
