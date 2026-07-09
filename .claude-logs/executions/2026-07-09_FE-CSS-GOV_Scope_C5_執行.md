# FE-CSS-GOV C5 — Scope Map & Sidebar Cleanup（C5–C7 併一·re-scoped）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV C5（併 C6/C7） |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md §8 C5–C7`（**baron 拍板併為一**） |
| **次級參考** | plan v2（U3/§3-#1/#2/#3）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`a49fb28`（C2）之上、C3/C4 縮版（待 baron commit）之後。
- **⚠️ Scope Deviation（baron 授權·本 commit 核心）**：原 tasks 分 C5（左）/C6（右）/C7（中）三 commit 收斂「36 行 ID 後代式」。執行期 grep 全掃 sidebar/chat/content **反證前提**——36 行絕大多數是正當模式（chrome CSS 其實結構良好）。每個 `#`-選擇器落五類：A 容器自身 ID／B 內容渲染容器白名單／C 自身狀態式／D 跨欄共用語意 class（ID-scope 正當）／E 真正私有可收斂。**唯一該物理收斂的是 E 類（`.sb-row` 6 行）**；C6/C7 grep 後**可乾淨收斂＝0 行**（全為 A/B/C/D）。經 §Open Questions 兩輪四 fork 上報、**baron 拍板：C5–C7 併為一個「Scope Map」commit**（唯一乾淨收斂 + 作用域白名單全量表）。
- **本次改動**：① `sidebar.css` `.sb-row` 卸 `#sidebar-bottom` ID 前綴為單級 class（E 類·6 行）；② `css-architecture.md` §5 補完作用域白名單全量表（A/B/C/D/E 五類逐條 + 鐵則）+ build 狀態 C5 ✅；③ `dom-reference.md` §3.3 `.sb-row` scope 收斂註；④ `components.md` header 補 CSS 架構/作用域指針。
- **完成狀態**：§5 驗收全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**：交付 U3 之真價值（作用域白名單地圖 + 唯一乾淨解耦）；FE-CSS-GOV 從 C5+C6+C7+checkout（4）誠實縮為 C5 + checkout（2）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C5（併 C6/C7） | Scope Map & Sidebar Cleanup — `.sb-row` 卸 ID 前綴（唯一 E 類·6 行）+ css-architecture §5 作用域白名單全量表〔A/B/C/D/E 五類·grep 實證〕+ dom-reference/components 同步 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·4）**：`static/css/sidebar.css`（`.sb-row` 卸前綴）+ `design/docs/{css-architecture,dom-reference,components}.md`（作用域地圖 + 同步）
- **備份（入 git·4）**：`.claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_{sidebar.css,css-architecture.md,dom-reference.md,components.md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1–C4 報告。
- **未動**（併一後 C6/C7 零物理收斂）：`static/index.html`（`.sb-row` 已在·卸前綴純 CSS 動作免加法）、`static/css/{layout,content,chat,globals,overlays,print}.css`、`static/themes/*`、JS、後端——**全零 diff**（git 驗證）。
- **tasks 原列 index.html + sidebar.css + 3 docs + 5 .bak → 併一後縮為 sidebar.css + 3 docs + 4 .bak**（index.html 免改故不動不備份）。

---

## §4 修改說明

### (a) E 類唯一收斂：`.sb-row` 卸前綴（sidebar.css）
- `#sidebar-bottom .sb-row`（6 處：base×2/`> button`/`:hover`/`:active`/`svg`）→ 單級 `.sb-row`。
- **安全性 grep 實證**：`.sb-row` 僅用於 sidebar-bottom（HTML L172 唯一、在 `#sidebar-bottom` L171 內；CSS 僅 sidebar.css；L769 為 JS 註解非引用；0 JS classList/querySelector 引用）→ 卸前綴後單級 `.sb-row` 無他處匹配、行為等價。
- **HTML 免改**：`.sb-row` class 已在 HTML、卸前綴純屬 CSS 選擇器簡化。
- 對帳：`git diff --numstat` sidebar.css 7 add/6 del（6 選擇器改 + 1 註解）；`#sidebar-bottom .sb-row` 殘留=0、單級 `.sb-row`=6、容器 `#sidebar-bottom{}` 保留、brace 65/65。

### (b) css-architecture §5 作用域白名單全量表（A/B/C/D/E）
- 五類分類表（判準 × 處置 × grep 實例）：A 容器自身 ID（12 個·保留）/ B 內容渲染容器白名單（`#paper-content` 33 行等·保留）/ C 自身狀態式（`:focus`/`:empty`/`[contenteditable]` 等·保留）/ D 跨欄共用語意 class（`.title`/`.toolbar-actions`/`.h-title`·ID-scope 正當保留）/ E 私有可收斂（`.sb-row`·已收斂）。
- §5.1 鐵則：DOM id/JS 契約 class 零改名；D 類為何不硬收斂（owner 跨 layout/content/themes、硬拆製造不一致）；新增 chrome 樣式優先單 class、複用語意 class 沿 ID-scope。

### (c) docs 同步
- `dom-reference.md §3.3`：`.sb-row` 單級化 + scope map 指針。
- `components.md` header：CSS 架構/作用域/主題契約交叉指針。

---

## §5 測試與驗收結果（§6.5 調整版 + SOP §4 自評）

```
E 類收斂：#sidebar-bottom .sb-row 殘留=0 / 單級 .sb-row=6 / 容器 #sidebar-bottom{} 保留=1  ✅
sidebar.css brace：{ 65 == } 65                                                          ✅
JS 契約守恆：HTML class="sb-row"=1、id="sidebar-bottom"=1（零改名）                        ✅
css-architecture §5 五類 + C5 build ✅ + §5.1 鐵則                                        ✅
C5' 範圍：sidebar.css + 3 docs 四檔；index.html/layout/content/chat/globals/themes → git diff --quiet ✅ 全零 diff
```

> **§6.5 原檢「該區 ID 後代式=0 / HTML 加並存 class」調整**：併一後（baron 拍板）——A/B/C/D 四類為正當保留（非「後代式=0」目標）、E 類已收斂；HTML 免加法（`.sb-row` 已在）。改以「五類白名單全量表 + E 類收斂 + JS 契約守恆」為驗收。

**SOP §4 自評（本 commit 相關）**：
- [x] §2 效能：卸 CSS 前綴 + docs，零規則值改動。
- [x] §3 渲染正確性：`.sb-row` 卸前綴行為等價（grep 證唯一）；D 類共用 class 保留 ID-scope、視覺零變。
- [x] Scope 誠實：C5–C7 併一 deviation 明載（§1）；「36 行需收斂」grep 反證為高估（A/B/C/D 正當保留）；U3 改由白名單全量表交付。
- ⚠️ 左欄 E2E（資料夾展開/選中/bottom popup 四 icon）：**留 baron 瀏覽器核查**（本環境無瀏覽器；`.sb-row` 卸前綴 grep 證等價）。

---

## §6 不可動清單遵守

- [x] 後端 `.py` / JS 邏輯（index.html L1610+）/ `renderMarkdownWithMath` / DOM id / 27+ 契約 class — 本 commit 僅動 sidebar.css + 3 docs。
- [x] DOM id 與 JS 契約 class 零改名：`.sb-row`/`#sidebar-bottom` 保留（僅卸 CSS 選擇器前綴）。
- [x] D 類跨欄共用語意 class（`.title`/`.toolbar-actions`/`.h-title`）— 未動（正當 ID-scope 保留）。
- [x] `static/index.html` / `static/css/{layout,content,chat,globals,overlays,print}.css` / `static/themes/*` — **全零 diff**。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1–C4 / 本 C5 報告 暫存、未 mv 未 add（→ checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ sidebar.css + 3 docs + 4 `.bak`（8 檔）。
- **hash 自癒**：C2 已 ship `a49fb28`；C1 `32e3a1a`；C3/C4/C5 待 baron commit。
- **下一步 → checkout（收官）**：C5–C7 併一後，checkout 為 FE-CSS-GOV 最後一個 commit；baton 一次性歸檔（plan→plans/、tasks→tasks/、C1–C5 報告→executions/）+ TODO 雙層結案 + hash 自癒 + staged 自檢 + checkout 執行報告。**本 session 續接執行、不中斷**（baron 拍板）。
- **收官後續集**：THEME-DEDUP（TODO ⬜ stub·結構去重）；token 架構 C4 已定案、作用域 C5 已定案，**無新外溢**。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅 sidebar.css 卸前綴 + docs、6 檔+themes+index 零 diff。(b) 推進 U3（作用域白名單地圖 + 唯一乾淨解耦）；「逐欄物理收斂」誠實廢除（grep 反證·非偷懶）。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-09_FE-CSS-GOV_C5_*.bak ×4

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/css/sidebar.css design/docs/css-architecture.md design/docs/dom-reference.md design/docs/components.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_sidebar.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_css-architecture.md.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_dom-reference.md.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_components.md.bak

# 2.5 staged 自檢（期望恰 8 檔；TODO/INDEX/prompt 治理檔留 checkout 掃入）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-CSS-GOV_C5_msg.txt）
cat > /tmp/FE-CSS-GOV_C5_msg.txt << 'EOF'
FE-Refactor: FE-CSS-GOV C5 — Scope Map & Sidebar Cleanup

將 sidebar 的 .sb-row 由 ID 後代選擇器卸為單級 class（grep 證唯一），並在
css-architecture.md 補完 chrome 作用域五類白名單全量表。C6/C7 併入本 commit
（grep 反證其餘 ID 選擇器均為正當保留、零物理收斂）。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-CSS-GOV_C5_msg.txt
```
