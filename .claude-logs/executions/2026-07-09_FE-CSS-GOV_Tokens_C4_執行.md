# FE-CSS-GOV C4 — Token Slimming（作法2 純文件版·re-scoped）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV C4 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md §8 C4`（**baron 拍板作法2**） |
| **次級參考** | plan v2（U5）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`a49fb28`（C2）之上、C3 縮版（待 baron commit）之後。
- **⚠️ Scope Deviation（baron 授權·本 commit 核心）**：原 tasks C4「把 13 個 B 類元件變數遷出 globals 到 owning 元件檔」經執行期 grep 審查**前提不成立**——(1) 13 個中 **8 個跨 2–5 個元件檔共用**（`--btn-icon-stroke` 5 檔、`--gap-btn-normal` 5 檔…）、屬共用設計 token 系統、無單一 owner；(2) **CSS custom property 天生全域**（`:root{--x}` 不論寫哪支 CSS 都掛 document root 全域繼承）→ 遷檔給**零解耦**、只讓歸屬圖失真；(3) 部分真實 owner（`--gap-btn-tight`→`sidebar.css`）在 C4 編輯權外。經 §Open Questions 四 fork 上報、**baron 拍板作法2（純文件版）**：**零遷移**，改以 globals `:root` 語意分區 + css-architecture 消費地圖達成 U5 想要的 SSOT。
- **本次改動**：① `globals.css` `:root` 三層分區（T1 全域結構 scale／T2 共用元件系統／T3 主題覆寫面 fallback），**零變數值改動**（46 宣告多重集 byte-identical、僅 `--transition` 重排入 T1 + 三層標籤註解）；② `css-architecture.md` 新增 §6 Token 歸屬（三層表 + T2 13 個 grep 消費地圖 + 原則 + 維護規則）。
- **完成狀態**：§5 驗收全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**：交付 U5 之 SSOT map（語意分類 + 消費地圖）；「物理遷移」誠實廢除（zero-decoupling 已證）。FE-CSS-GOV **不中斷**，續 C5→C7→checkout。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | Token Slimming（作法2 純文件版）— globals `:root` 三層分區〔零值改動·46 宣告 byte-identical〕+ css-architecture §6 Token 歸屬〔三層表 + T2 13 個 grep 消費地圖 + custom-prop-全域原則 + 維護規則〕；**零遷移**（13 個全留 globals） | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·2）**：`static/css/globals.css`（`:root` 分區）+ `design/docs/css-architecture.md`（§6 + build 狀態）
- **備份（入 git·2）**：`.claude-logs/archive/2026-07-09_FE-CSS-GOV_C4_{globals.css,css-architecture.md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1/C2/C3 報告。
- **未動**（作法2 零遷移）：`static/css/{layout,content,chat,sidebar,overlays,print}.css`、`static/themes/*`、`static/index.html`、JS、後端——**全零 diff**（git 驗證）。
- **tasks 原列 5 檔 4 css+doc + 5 .bak → 作法2 縮為 2 檔 + 2 .bak**（layout/content/chat 無遷入故不動）。

---

## §4 修改說明

### (a) globals `:root` 三層分區（零值改動）
- **T1 全域結構 scale**（themes 不覆寫）：`--space-1..8` / `--font-xs..2xl`（字級階梯）/ `--transition`（由原「content-max-w 後」重排至此 T1）。
- **T2 共用元件系統 token**（跨元件·themes 不覆寫）：`--btn-*`×6 / `--toolbar-h` / `--pad-panel` / `--rail-w` / `--chat-pad-x` / `--gap-btn-*`×3（＝原 13 個「B 類」，**原地留存**、加 T2 標籤）。
- **T3 主題覆寫面 fallback**（themes 覆寫）：`--content-max-w` / `--color-*`×13 / `--divider-w` / `--radius-sm/md` / `--font-display` / `--font-body`。
- **頂部宣告**：新增三層分類說明 + 「custom property 全域繼承、歸屬是語意分類非檔案 scope、真正 scope 需元件選擇器（未採）」原則 + 指向 css-architecture §6。
- **零值改動證明**：`.bak` vs 現行抽 `--name: value;` 多重集 **byte-identical**（46=46、集合全等）；僅 `--transition` 位置重排 + 註解變動。

### (b) css-architecture §6 Token 歸屬
- **決策記載**：plan U5「遷 B 類解耦」grep 反證前提不成立（8/13 共用 + custom-prop 全域零解耦 + owner 在編輯權外）→ baron 拍板作法2 零遷移。
- **§6.1 三層分類表**：T1/T2/T3 × 角色 × themes 覆寫? × 成員。
- **§6.2 T2 消費地圖**（grep `@a49fb28` 實測）：13 個 token × 值 × 消費檔（如 `--btn-icon-stroke`→layout/sidebar/chat/overlays/content 5 檔）。
- **§6.3 維護規則**：新增 token 加 globals 對應層、勿散元件檔；改元件尺寸改 T2 一處；themes 只碰 T3。
- **build 狀態**：C4 ✅（§6·作法2 零遷移）+ C3 ✅（縮版）回填。

---

## §5 測試與驗收結果（§6.4 調整版 + SOP §4 自評）

```
globals token 宣告多重集：.bak(46) vs 現行(46) byte-identical → ✅ 零值改動（僅重排+註解）
13 個 T2 token 各唯一定義：grep -rl '^--X:' static/css → 各恰 1 處、皆 globals.css → ✅ 零重複/零遷出
T1/T2/T3 三層標籤：globals 齊備 → ✅
globals brace：{ 9 == } 9 → ✅ 平衡
css-architecture §6 Token 歸屬 + 消費地圖 + build C4 ✅ → 命中 4 → ✅
C4 範圍：globals.css + css-architecture.md 兩檔；layout/content/chat/themes/index.html → git diff --quiet ✅ 全零 diff
```

> **§6.4 原檢「globals :root 僅 A 類」刻意不達**：作法2 決定 13 個 T2 共用 token **留 globals**（premise 反證，見 §1）；改以「各唯一定義 + 三層分區 + 消費地圖」為驗收，達成 U5 的 SSOT 目標。

**SOP §4 自評（本 commit 相關）**：
- [x] §2 效能：純註解/重排 + docs，零規則值改動、零 `var()` 解析變動。
- [x] §3 渲染正確性：46 宣告 byte-identical（多重集證）→ 所有 `var(--x)` 解析結果不變、視覺零變；custom prop 全域繼承不受分區/重排影響。
- [x] Scope 誠實：C4 作法2 deviation 明載（§1）；「物理遷移」誠實廢除（zero-decoupling 論證 + owner 越界）；SSOT 改由語意分區+消費地圖達成。
- ⚠️ 按鈕/工具列/rail/聊天 padding 視覺 E2E：**留 baron 瀏覽器核查**（本環境無瀏覽器；46 宣告 byte-identical 已證所有 token 解析零變）。

---

## §6 不可動清單遵守

- [x] 後端 `.py` / JS 邏輯 / `renderMarkdownWithMath` / DOM id / 27+ 契約 class — 本 commit 僅動 globals.css + css-architecture.md。
- [x] **變數名稱與值零改動**（作法2 更強：零遷移）：46 宣告多重集 byte-identical、13 T2 全留 globals。
- [x] `static/css/{layout,content,chat,sidebar,overlays,print}.css` / `static/themes/*` / `static/index.html` — **全零 diff**（git 驗證）。
- [x] `@layer tokens` 包裹不變、brace 9/9 平衡。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1 / C2 / C3 / 本 C4 報告 暫存、未 mv 未 add。
- **git 追蹤**：本 commit ＝ globals.css + css-architecture.md + 2 `.bak`（4 檔）。
- **hash 自癒**：C2 已 ship `a49fb28`（TODO 已回填）；C1 `32e3a1a`；C3 待 baron commit。TODO 頂部完成表無 `待 baron 回填` 殘留。
- **下一步 → C5 — Sidebar Scope（左欄作用域收斂）**：`#sidebar`/`#sidebar-bottom`/`#paper-list`/`#folder-tree` 之 ID 後代式（18 行）收斂為 `.sb-*` 前綴單 class（HTML 加並存 class、JS 契約零改名）+ components/dom-reference/css-architecture 前綴表配套；由 baron 另下提示詞觸發。
- **收官後續集**：THEME-DEDUP（TODO ⬜ stub）已立；**token 架構本 commit 已定案**（無外溢）。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅 globals 分區 + docs、13 T2 零遷移、6 檔+themes+index 全零 diff。(b) 推進 U5（SSOT map）；「物理遷移」誠實廢除（有 grep 論證、非偷懶）。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-09_FE-CSS-GOV_C4_{globals.css,css-architecture.md}.bak ×2

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/css/globals.css design/docs/css-architecture.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C4_globals.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C4_css-architecture.md.bak

# 2.5 staged 自檢（期望恰 4 檔；TODO/INDEX/prompt 治理檔不在內、留 checkout 掃入）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-CSS-GOV_C4_msg.txt）
cat > /tmp/FE-CSS-GOV_C4_msg.txt << 'EOF'
FE-Refactor: FE-CSS-GOV C4 — Token Slimming（純文件版）

將 globals.css 的 :root 重整為三層語意分區（全域 scale / 共用元件系統 /
主題覆寫面），變數名稱與值維持不變、零遷移。在 css-architecture.md 補登
Token 歸屬與跨檔消費地圖，作為 token 定位的 SSOT。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-CSS-GOV_C4_msg.txt
```
