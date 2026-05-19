# Color Tokens 設計規格 · MadPro UI

> 色彩採「語意化 token」設計：HTML/CSS 不寫死色碼，
> 主檔提供 fallback、`themes/*.css` 提供實際值。

---

## 1. Token 總覽

| Token | 語意 | 不可作的用途 |
|---|---|---|
| `--color-bg` | 全域底色（servant 邊欄） | 不可用在前景文字 |
| `--color-bg-served` | 中欄「served」底色（可同 bg 或略亮） | 不可用在邊欄 |
| `--color-surface` | hover、次級表面、輸入框內底 | 不可作主結構分隔 |
| `--color-surface-2` | 強調表面（rail、訊息泡內、進度底） | 不可作主文字色 |
| `--color-border` | 一般邊框、訊息泡輪廓 | 不可作結構性主分隔（請用 `--color-divider`） |
| `--color-border-strong` | 強邊框、銘文線 | 不可作主文字色 |
| `--color-divider` | **三欄結構性主分隔線**、文章 h2 底線 | 不可作弱邊框 |
| `--color-text` | 主文字、accent 同值 | 不可作 disabled 文字 |
| `--color-text-muted` | 次要文字（原文標題、來源、byline） | 不可作主標題 |
| `--color-text-subtle` | 弱提示（空狀態、系統訊息、disabled） | 不可作正文 |
| `--color-accent` | 主按鈕、user 訊息泡、實心填色 | 不可作大面積背景 |
| `--color-accent-hover` | 主按鈕 hover | 不可作 idle |
| `--color-danger` | 刪除、警告（少用） | 不可作確認、成功 |

---

## 2. 主題色票對照

| Token | Mies | Kahn (Kimbell) | Kandinsky | Nara | 來源 |
|---|---|---|---|---|---|
| `--color-bg` | `#ffffff` | `#dcdcdc` | `#fbf9f1` | `#f4ecdf` | 純白／清水模中灰／畫布／奶米 |
| `--color-bg-served` | `#ffffff` | `#ececec` | `#ffffff` | `#fbf6ed` | 中欄背景 |
| `--color-surface` | `#f7f7f5` | `#cacaca` | `#f1ede0` | `#e7dcc8` | 二級表面 |
| `--color-surface-2` | `#efefec` | `#b4b4b4` | `#e6dfc8` | `#d4c4a8` | 強表面 |
| `--color-border` | `#e5e5e2` | `#a8a8a8` | `#d8d0b5` | `#c5b599` | 一般邊框 |
| `--color-border-strong` | `#c8c8c4` | `#6a6a6a` | `#2a2a2a` | `#8a7558` | 強邊框 |
| `--color-divider` | `#1a1a1a` | `#2e2e2e` | `#0a0a0a` | `#3a2f23` | 主結構分隔 |
| `--color-text` | `#111111` | `#161616` | `#0a0a0a` | `#2a2218` | 主文字 |
| `--color-text-muted` | `#555555` | `#555555` | `#5a5a5a` | `#6a5f4c` | 次要 |
| `--color-text-subtle` | `#757575` | `#6e6e6e` | `#757575` | `#7a6e55` | 弱提示（修正 AA 對比） |
| `--color-accent` | `#111111` | `#232323` | `#0052a5` | `#b04c4c` | 主強調 |
| `--color-accent-hover` | `#2a2a2a` | `#2e2e2e` | `#003d7a` | `#8a3a3a` | |
| `--color-danger` | `#a8242c` | `#8c2f2f` | `#d62828` | `#c43b3b` | Roman red／vermilion／不安紅 |

---

## 3. 用色原則

### 3.1 對比層級
- 文字色三階：text → text-muted → text-subtle
- **同段落不混用三階**：選一階為主，最多再加一階輔助

### 3.2 主從關係
- selected / active：實心 `--color-accent` 底 + 白字
- hover：`--color-surface` 淺底，**不改文字色**
- :active：`--color-surface-2` 再深一階

### 3.3 結構 vs 邊框
- **結構性分隔（三欄之間、文章 h2 底線）→ `--color-divider`**（粗、深、明確）
- **元件邊框（按鈕、modal、popup、輸入框、tooltip）→ `--color-divider`**（與結構同色，視覺一致）
- **裝飾性弱邊（paper-item、訊息泡）→ `--color-border`**（淺、近 surface）

### 3.4 危險色
- 僅用於：刪除文件、刪除資料夾、Modal 警告文字
- 不可用於 hover、不可用於主按鈕
- 文字色 only；不可作背景（避免警示過度）

---

## 4. 透明度規則

- Modal mask：`rgba(0, 0, 0, 0.4)` 固定，不隨主題
- 任何 token 都不可用 `opacity` 改色 → 改用對應的淺一階 token

---

## 5. 反例

- ❌ `color: #888` 寫死灰色 → 用 `--color-text-muted`
- ❌ 用 `--color-border` 作三欄主分隔（太淡）
- ❌ 用 `--color-danger` 作刪除鍵背景（紅塊噪音）
- ❌ 用 `opacity: 0.5` 作 disabled 文字 → 用 `--color-text-subtle`
- ❌ 跨主題寫死色碼 `#171717` → 永遠走 token
