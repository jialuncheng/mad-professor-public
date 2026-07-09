# FE-CSS-GOV C3 — Theme Dedup（縮版·re-scoped）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV C3 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md §8 C3`（**baron 拍板 re-scope**） |
| **次級參考** | plan v2（U4/Q8）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`a49fb28`（FE-CSS-GOV C2 — Layer Cascade，已 ship）。
- **⚠️ Scope Deviation（baron 授權·本 commit 最重要一項）**：原 tasks C3 目標「4 主題白名單外結構屬性=0」經執行期審查**與現況不符**——(1) 舊 85 行審計未涵蓋後補的**裝飾 CSS**（kahn `.ph::before` 天窗光線等）；(2) 裝飾佔位藝術屬**視覺識別**、既不能上移 base（會套全主題）也不能 token 化（整段規則獨有）；(3) `#demo-bar` 系死碼（HTML 早於 BUG-F5 B3 移除）→ 應刪非遷。經 §Open Questions 三 fork 上報、**baron 拍板路線 A**：C3 縮為「**死碼清除 + theme-guide 契約立規·不動結構**」，主題結構去重整包**外溢 THEME-DEDUP**（收官後獨立 plan）。
- **本次改動**：① 4 主題刪除 `#demo-bar` 死碼（純刪、零改寫其餘規則）；② 重寫 `theme-guide.md` 契約（Q8 白名單 + 裝飾 carve-out + unlayered 優先級 + §8 THEME-DEDUP 方向）。
- **完成狀態**：§5 驗收全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**：交付 U4 之「契約立規」半 + 死碼清理；U4 結構去重半外溢 THEME-DEDUP（TODO 已立 stub）。FE-CSS-GOV **不中斷**，續 C4→C7→checkout。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | Theme Dedup（縮版）— 4 主題 `#demo-bar` 死碼刪除（124 行純刪、brace 各 -4 平衡）+ `theme-guide.md` 契約重寫（允許屬性白名單/figure 裝飾 carve-out/必備 token/unlayered 優先級/THEME-DEDUP 方向）；結構去重 defer | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·5）**：`static/themes/{kahn,kandinsky,mies,nara}.css`（4，純刪死碼）+ `design/docs/theme-guide.md`（1，契約重寫）
- **備份（入 git·5）**：`.claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_{kahn,kandinsky,mies,nara}.css.bak + theme-guide.md.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1/C2 報告。
- **未動**：`static/css/*`（globals/content/layout **零觸**——不動結構）、`static/index.html`、`print.css`、JS、後端。

---

## §4 修改說明

### (a) 4 主題 `#demo-bar` 死碼刪除（純刪·零改寫）
- **死碼三證**（grep 實錄）：`index.html` 無 `id="demo-bar"`（僅 L383 記載移除的**註解**）；主檔系 `static/css/` 無 `#demo-bar` 規則（僅 globals L101 BUG-F5 B3 刪除記載註解）；**0 JS 引用**。
- **手段**：審計腳本匹配「展示控制條」註解 + 連續 `#demo-bar`/`.seg button`/`.credo`/`.credo::before` 規則塊 + 尾空行，整段刪除；斷言 `#demo-bar` 全無 + brace 平衡 + 無三連空行。
- **對帳**：`git diff --numstat` 四檔皆 `0 insertions / N deletions`（kahn 31／kandinsky 32／mies 29／nara 32＝計 124 行純刪）；brace 各 -4（4 塊×1 對）平衡；接縫 `#content-area` → 「三欄標題」註解單空行；`:root` token 各檔 17 行完好（未觸）。

### (b) `theme-guide.md` 契約重寫
- **§1 允許屬性白名單（Q8）**：明列允許（color 系/background/border-color/box-shadow/font-family/font-size/font-weight/font-style/letter-spacing/text-transform/line-height/`--token`）vs 禁（margin/padding/width/height/display/gap/非裝飾 position/border-width/border-style）。
- **§1 裝飾 carve-out（baron 2026-07-09 拍板）**：`#paper-content .figure .ph` 及 `::before` 之**純裝飾佔位幾何**（position/width/height/transform）視為主題自有外觀、保留主題（比照已允許的背景漸層；例 Kahn 天窗光線）。
- **§3 unlayered 優先級**：明文「themes（含自訂上傳）unlayered → 依 Cascade L5 恆勝主檔四層」；**作廢舊 source-order 說**（「`<link>` 排 `</style>` 後」已過時）；主題**嚴禁**寫 `@layer`。
- **§2 必備 token 覆寫清單**：13 色 + `--divider-w`/`--radius-*` + `--font-*` + `--content-max-w`；註明元件級 token 屬主檔非主題面。
- **§8 THEME-DEDUP 方向**：記載結構去重外溢（共用→base／異值→token／裝飾→保留）供後續 plan 依循。
- **清除**：所有 `#demo-bar` 撰寫指引（原 §1/§3/§4 Step6/checklist）除去，僅留 §7/§8 兩處「清 #demo-bar 死碼」狀態註記。

---

## §5 測試與驗收結果（§6.3 + SOP §4 自評）

```
死碼三證：index.html id="demo-bar"=0 / static/css #demo-bar 規則=0 / JS 引用=0    ✅
4 主題 #demo-bar 刪除：git diff --numstat 皆 0 insert / N delete（純刪 124 行）       ✅
brace 平衡：4 檔各 -4、{ == }                                                       ✅
接縫：4 檔 #content-area → 三欄標題註解、單空行、無 demo-bar 殘留                      ✅
主題 :root token：4 檔各 17 定義行完好（未觸）                                        ✅
theme-guide 契約命中：grep '允許屬性|白名單|unlayered' = 12                          ✅
theme-guide demo-bar 殘留：僅 2 處狀態註記（§7/§8「清 #demo-bar 死碼」）             ✅
C3 範圍：4 themes + theme-guide.md；static/css 零 diff、index.html/py 零 diff       ✅
```

**SOP §4 自評（本 commit 相關）**：
- [x] §2 效能：純刪死碼 + docs，未改任何生效規則值。
- [x] §3 渲染正確性：4 主題為**純刪除**（0 insert，git numstat 佐證）→ 其餘規則零改寫、視覺零變；unlayered 恆勝不變。
- [x] Scope 誠實：C3 縮版 deviation 明載（§1）；結構去重外溢 THEME-DEDUP、TODO 立 stub、theme-guide §8 記方向。
- ⚠️ 四主題切換視覺 E2E（線寬/字級/間距/figure 佔位藝術）：**留 baron 瀏覽器核查**（本環境無瀏覽器；純刪死碼 + numstat 純刪已證其餘零改）。

---

## §6 不可動清單遵守

- [x] 後端 `.py` / JS 邏輯 / `renderMarkdownWithMath` / DOM id / 27+ 契約 class — 本 commit 僅動 4 themes + theme-guide.md。
- [x] `static/css/*`（globals/content/layout/sidebar/chat/overlays）**零 diff** — 縮版不動結構、無上移 base、無新 token。
- [x] `static/index.html` / `print.css` 零 diff。
- [x] 主題 unlayered（4 檔未包 `@layer`，A1 鐵律）；`:root` token 未改名未改值。
- [x] 群組 B 共用 / C 異值 / D 裝飾結構 — **全數未動**（defer THEME-DEDUP）。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1 / C2 / 本 C3 報告 暫存、未 mv 未 add。
- **git 追蹤**：本 commit ＝ 4 themes + theme-guide.md + 5 `.bak`（10 檔）。
- **hash 自癒**：C2 已 ship `a49fb28`（本輪自癒回填 TODO）；C1 `32e3a1a`。TODO 頂部完成表無 `待 baron 回填` 殘留。
- **下一步 → C4 — Token Slimming（tokens 瘦身歸位）**：globals `:root` B 類 13 元件級變數遷至對應元件檔 `:root`（不改名不改值）+ css-architecture token 歸屬節；由 baron 另下提示詞觸發。**縮版 C3 不加任何 token → C4 無交叉 diff 顧慮**。
- **收官後續集 → THEME-DEDUP**（TODO 已立 ⬜ stub）：FE-CSS-GOV 全案 checkout 之後獨立開 plan、對全主題完整重審落地結構去重（吃 C4/C5-C7 終態）。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅刪死碼 + docs、static/css 零觸、結構未動。(b) 推進 U4（契約半）+ 死碼清理；結構去重誠實外溢（非跳過、有 stub + 方向文獻）。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-09_FE-CSS-GOV_C3_*.bak ×5

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/themes/kahn.css static/themes/kandinsky.css static/themes/mies.css static/themes/nara.css
git add design/docs/theme-guide.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_kahn.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_kandinsky.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_mies.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_nara.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C3_theme-guide.md.bak

# 2.5 staged 自檢（期望恰 10 檔；TODO/INDEX/prompt 治理檔不在內、留 checkout 掃入）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-CSS-GOV_C3_msg.txt）
cat > /tmp/FE-CSS-GOV_C3_msg.txt << 'EOF'
FE-Refactor: FE-CSS-GOV C3 — Theme Dedup（縮版）

清除 4 支主題檔的 #demo-bar 死碼（HTML 早已移除），並重寫 theme-guide.md
主題契約（允許屬性白名單、裝飾幾何例外、unlayered 優先級）。主題結構去重
整包外溢至後續 THEME-DEDUP plan，本 commit 不動任何結構。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-CSS-GOV_C3_msg.txt
```
