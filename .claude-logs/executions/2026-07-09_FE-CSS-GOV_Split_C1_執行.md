# FE-CSS-GOV C1 — File Split 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV C1 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md §8 C1`（+ §4.1 錨段映射） |
| **次級參考** | plan v2（U1/U6）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`d4ce75a`（DOC-SYNC-1 checkout，git log HEAD）。
- **本次改動**：inline `<style>`（1,354 行 CSS）**零改寫等價**拆為 `static/css/` 7 檔、`index.html` 改 7 `<link>` 載入、新增 css-architecture.md + README 連結。
- **完成狀態**：三不變式對帳全過 + JS 主塊 byte-identical + §6.1 全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（B1 兩段式段一）：落地 **U1**（拆檔七件套）+ **U6**（C1 配套 css-architecture.md 初版+README）；cascade 語意變更（@layer）**刻意留 C2**（本 commit 保 source 序等價）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | File Split — inline CSS(1,354 行) 零改寫拆 7 檔（globals 89/overlays 178/layout 147/sidebar 286/content 304/chat 281/print 69 行）+ index.html 7 link + css-architecture.md 初版 + README 連結 | 待回填 |

---

## §3 變動檔案清單

- **新增（入 git）**：`static/css/{globals,overlays,layout,sidebar,content,chat,print}.css`（7）+ `design/docs/css-architecture.md`（1）
- **修改（入 git）**：`static/index.html`（`<style>` 塊 1,356 行 → 8 行〔1 註解+7 link〕+ theme-link 註解更正；diff −1358/+29）/ `design/docs/README.md`（+2 行連結）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-09_FE-CSS-GOV_C1_{index.html,README.md}.bak`（2）
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks。

---

## §4 修改說明（7 檔物理切分映射 + 對帳 + css-architecture）

### (a) partition（block 相對行、6 交界皆讀證為乾淨切點）
| 檔 | 行段 | 行/規則 |
|---|---|---|
| globals | 1–89 | 89/6（:root tokens+reset+fallback）|
| overlays | 90–267 | 178/27（tooltip+modal 家族+dropdown）|
| layout | 268–355 **+ 1227–1285** | 147/29（框架+按鈕+icon+收合 rail+scrollbar）|
| sidebar | 356–641 | 286/64（左欄+上傳占位+`.ctx-popup`+底部）|
| content | 642–945 | 304/52（中欄+META-NORM+slides+FE-RHYTHM+KaTeX）|
| chat | 946–1226 | 281/46（chat+msg 泡泡〔含 content-visibility 遺產〕+輸入+hashtag）|
| print | 1286–1354 | 69/10（@media print、19 !important 原樣）|

### (b) 對帳（三不變式，split.py 腳本執行）
1. **partition**：7 檔行合計＝1,354、`sorted(7 檔) == sorted(原塊)` **byte-identical multiset**（重跑：非空行 diff 空）。
2. **每檔 brace 平衡**：各檔 `{`==`}`（無規則被切斷）。
3. **`{` 守恆**：7 檔合計 234＝原塊 234。

### (c) index.html 換 link（載入序＝原 source 序、cascade 等價）
`<style>…</style>`（`:17-1372`）→ 7 `<link>`（globals→overlays→layout→sidebar→content→chat→print）；`#theme-link` 仍殿後（`:27`、主題後出者勝）。**載入序 cascade 安全性已驗**：唯一被提前段（layout 第二段 1227-1285 收合/scrollbar，原在 chat 後）之選擇器**全為 `.collapsed` 複合〔高特異度〕或 `*::-webkit-scrollbar` 唯一偽元素**、與 356-1226 零同選擇器衝突（grep 證）→ 提前零翻轉。

### (d) 誠實微調（2 處、非規則改寫）
- **theme-link 註解更正**：原「置於 `</style>` 之後」（`</style>` 已不存在）→「置於 7 個 static/css/ link 之後」+ C2 unlayered 前瞻註。屬**被 C1 作廢之 stale 註解修正**、非 CSS 規則。
- **檔頭 header 註解**：7 檔各加 5 行 `[FE-CSS-GOV C1]` 檔頭（新增註解、非搬遷內容改寫；對帳已排除 header 行）。

### (e) css-architecture.md（U6 配套·ownership map 初版）
七檔職責表+載入序+**歸屬判例**（`.ctx-popup`→sidebar 物理原生/收合段→layout 提前安全）+「新樣式寫哪」決策樹+@layer(C2 規劃勾)/作用域(C5-C7 規劃勾) 佔位章；README 導讀 9. + 文件清單列同步。

---

## §5 測試與驗收結果（§6.1 + SOP §4 自評）

```
grep -c '^<style>$' static/index.html                → 0 ✅
grep -c 'href="/static/css/' static/index.html       → 7 ✅
ls static/css/*.css | wc -l                          → 7 ✅
對帳：cat 7檔|去header|去空行|sort  ==  原塊|去空行|sort → diff 空（byte-identical multiset）✅
每檔 brace 平衡 + { 守恆 234                          ✅（split.py 三不變式）
inline JS 主塊 diff（.bak vs 現）                     → identical（2290 行零改）✅ 四鐵防線·JS
DOM id 數                                            → 75（DOC-SYNC 基準守恆）✅ 四鐵防線·id
node --check <script 區>                             → 通過 ✅
css-architecture.md 存在 + README 連結×2             ✅（U6 配套）
git diff --stat                                      → 僅 static/index.html+static/css/**+design/docs/{css-architecture,README}；零 .py ✅
```

**SOP §4 自評（本 commit 相關）**：
- [x] §2 效能紅線：拆檔為純物理搬遷、未改任何規則→FE-PERF-2 之 content-visibility/preload/節流 CSS 原樣落 chat.css/globals（grep 確認 content-visibility 在 chat.css）。
- [x] §3 渲染正確性：`renderMarkdownWithMath` 零觸碰（JS byte-identical）；KaTeX 防禦規則整段落 content.css。
- [x] 視覺一致性：等價搬遷、cascade 序保留→視覺零變（待 baron E2E 確認）。
- ⚠️ 三軌×4 主題視覺 E2E + console 0 + print 預覽：**留 baron 瀏覽器核查**（本環境無瀏覽器；對帳+JS byte-identical+cascade 提前安全性已證結構等價）。

---

## §6 不可動清單遵守

- [x] 後端 `.py` / JS 邏輯（主塊 byte-identical）/ `renderMarkdownWithMath`（零觸碰）— 四鐵防線 JS。
- [x] DOM id（75 守恆）/ 27+ JS 契約 class（未改名、CSS 內容零改寫）— 四鐵防線 id/class。
- [x] 主題視覺值 / themes 檔 — 本 commit 未動（C3 才動）。
- [x] `login.html` / vendor / FE-PERF-2 遺產（content-visibility 等原樣隨遷）— 未改。
- [x] audit 不做項（transition:width 等）— 隨 layout.css 原樣搬遷、未動。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / 本 C1 報告 暫存、未 mv 未 add（待 checkout 歸檔）。
- **git 追蹤**：本 commit ＝ 7 css + css-architecture + index.html + README + 2 .bak（12 檔）。
- **hash 自癒**：DOC-SYNC-1 checkout `d4ce75a`（TODO 索引+done_archive）、CONTEXT-1 C5 `5d3be98`（done_archive）已回填。
- **下一步**：**C2 — Layer Cascade（層化串接）**——七檔入 `@layer reset,tokens,base,components`、themes/print/自訂主題 unlayered、非 print `!important` 1 條個案、principles 補 @layer+margin-flow；由 baron 另下提示詞觸發。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？theme-link stale 註解更正屬 C1 作廢之連帶、已標；未動任何 CSS 規則/JS。(b) 推進 U1+U6；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-09_FE-CSS-GOV_C1_{index.html,README.md}.bak

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/index.html
git add static/css/globals.css static/css/overlays.css static/css/layout.css static/css/sidebar.css static/css/content.css static/css/chat.css static/css/print.css
git add design/docs/css-architecture.md
git add design/docs/README.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C1_index.html.bak
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C1_README.md.bak

# 2.5 commit 前 staged 自檢（期望恰 12 檔）
git diff --cached --name-only

# 3. commit message 草稿（寫入 /tmp/FE-CSS-GOV_C1_msg.txt）
cat > /tmp/FE-CSS-GOV_C1_msg.txt << 'EOF'
FE-Refactor: FE-CSS-GOV C1 — File Split

將 1354 行 inline CSS 等價拆分至 static/css/ 下的 7 支關注點樣式表，修改
static/index.html 透過 link 載入。同步新增 css-architecture.md 架構設計文獻。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-CSS-GOV_C1_msg.txt
```
