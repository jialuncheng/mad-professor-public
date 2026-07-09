# FE-CSS-GOV C2 — Layer Cascade 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV C2 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md §8 C2` |
| **次級參考** | plan v2（U2/§2.5-A1）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`32e3a1a`（FE-CSS-GOV C1 — File Split，已 ship）。
- **本次改動**：主檔系 6 檔套 `@layer`（globals 三分 reset/tokens/base + 5 檔整檔 components）、themes/print/自訂主題維持 unlayered；非 print `!important`(1) 白名單保留；principles+css-architecture 文獻配套。
- **完成狀態**：§6.2 全綠 + 規則零改寫（md5 對帳）+ unlayered 鐵律驗；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（B1 段一）：落地 **U2**（層化串接、A1 themes unlayered）+ U6 配套；cascade 語意變更完成、行為經對帳/特異度分析等價。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Layer Cascade — globals `@layer reset,tokens,base,components;`+三分包裹；layout/sidebar/content/chat/overlays 整檔 `@layer components`；print+themes+自訂主題 unlayered；非 print `!important`(1) 白名單保留；principles §6.5（@layer/unlayered/`!important`/margin-flow）+ css-architecture §4/§4.1 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·8）**：`static/css/{globals,layout,sidebar,content,chat,overlays}.css`（6，層化）+ `design/docs/{principles,css-architecture}.md`（2，配套）
- **備份（入 git·8）**：`.claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_{6 css + 2 md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1 報告。
- **未動**：`static/index.html`（`git status` 確認）、`print.css`、`themes/*.css`、JS、後端。

---

## §4 修改說明（層級包覆 / !important 消除手段 / margin-flow）

### (a) globals 三分（surgical、僅插 wrapper 行、規則零改寫）
- 首行插 `@layer reset, tokens, base, components;`（全站唯一層序宣告）。
- `@layer tokens { :root{…} }`（原 6-72）／`@layer reset { *{box-sizing} body,h1…{margin:0} }`（原 74-75）／`@layer base { body{…} button a }`（原 76-89）。三子區**無重疊屬性**（reset 設 margin/padding，base 設 background/color/layout）→ 層序間零衝突。
- 對帳：剝 `@layer` 行後 md5 == C1 `.bak`（規則零改寫）；brace 6→9（+3 層 wrapper）。

### (b) 5 component 檔整檔 wrap（腳本、僅首尾插入）
- 各檔 C1 檔頭後插 `@layer components {`、檔尾插 `}`；**內容零重排**。
- 對帳：5 檔剝 wrapper 行後 md5 逐檔 == C1 `.bak`（**零改寫**）；brace 各 +1/+1 平衡。

### (c) `!important` 處置——**保留 + 白名單（非移除）**
- 唯一非 print `!important`＝`layout.css` `#chat-panel.collapsed … :not(#chat-toggle){ display:none !important }`。
- **判定：不可移除、屬 CSS 規範必要**——其作用是蓋過 `enableChat()` 設的 **inline `style="display:block"`**；inline 特異度 `1,0,0,0` 高於任何選擇器，`@layer`／提升特異度**皆無法勝**，只有 stylesheet 的 `!important` 能贏。此為「`!important` 唯一合法用例（蓋 inline JS）」。
- 依 tasks/提示詞「若不可行則保留並記錄」→ 保留 + 登 `css-architecture.md §4.1 白名單`（附規範理由）。

### (d) 文獻配套
- `principles.md §6.5`（新增）：(a) @layer 層序 + 主檔系嚴禁 unlayered 鐵則；(b) `!important` 唯一合法用例；(c) 作用域紀律（C5-C7 前瞻）；(d) **margin-flow 單一節奏源模型**（FE-RHYTHM-UNIFY 定案、DOC-SYNC-1 Q4 移交落點：相鄰選擇器單一 margin-top flow、鐵則勿回退逐交界補丁、已消滅 `:has()`）。
- `css-architecture.md`：§4 層序表（各層×檔×unlayered 三者）+ §4.1 `!important` 白名單 + build 狀態 C2 ✅。

---

## §5 測試與驗收結果（§6.2 + SOP §4 自評）

```
globals 層宣告 '@layer reset, tokens, base, components;'   → 1 ✅
globals 三子層 @layer (tokens|reset|base) {               → 3 ✅
5 檔 @layer components {                                   → 各 1 ✅
unlayered 鐵律：grep '^@layer' print.css themes/*.css     → 0 ✅（print 的 @layer 字樣為 C1 檔頭註解、非規則）
每檔 brace 平衡：globals9 layout30 sidebar65 content53 chat47 overlays28 print10 → 各 {==} ✅
規則零改寫對帳（剝 @layer/wrapper 行後 md5 == C1 .bak）：globals+5 檔 逐檔 identical ✅
!important：layout 1 條宣告（+1 註解行）保留、白名單登錄 ✅
git diff --stat → 6 css + 2 docs；index.html/JS/themes/.py 零 diff ✅
```

**SOP §4 自評（本 commit 相關）**：
- [x] §2 效能：層化為結構治理、未改任何規則值；FE-PERF-2 遺產（content-visibility 於 chat.css）隨 chat 入 components 層、行為不變。
- [x] §3 渲染正確性：規則零改寫（md5 對帳）；margin-flow 模型入 principles（DOC-SYNC Q4 移交完成）。
- [x] cascade 等價論證：層序 reset<tokens<base<components + themes unlayered 恆勝——主題換膚/print/自訂主題上傳三者優先權**與 C1 source-order 結果一致**（unlayered>layered 規範保證）。
- ⚠️ rail 收合 / 四主題切換 / **自訂主題上傳覆寫** / print 預覽 E2E：**留 baron 瀏覽器核查**（本環境無瀏覽器；規則零改寫+unlayered 鐵律+特異度分析已證等價）。

---

## §6 不可動清單遵守

- [x] 後端 `.py` / JS 邏輯 / `renderMarkdownWithMath` / DOM id / 27+ 契約 class — 本 commit 僅動 css+docs、`index.html` 零 diff。
- [x] `print.css` unlayered（`^@layer`=0）／`themes/*.css` 未動且 unlayered（=0）— A1 鐵律。
- [x] CSS 規則內容零改寫（md5 逐檔對帳）— 僅加 @layer wrapper。
- [x] FE-PERF-2 遺產 / audit 不做項 — 隨檔入層、未改。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1 報告 / 本 C2 報告 暫存、未 mv 未 add。
- **git 追蹤**：本 commit ＝ 6 css + 2 docs + 8 `.bak`（16 檔）。
- **hash 自癒**：C1 已 ship `32e3a1a`；TODO 頂部完成表無 `待 baron 回填` 殘留（掃描=0），本輪無需補填。
- **下一步**：**C3 — Theme Dedup（主題結構去重）**——4 主題白名單外結構上移 base（同值直移/異值 token 化）+ theme-guide 契約改寫；由 baron 另下提示詞觸發。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅 css 層化+docs 配套、規則零改寫、index.html 零觸。(b) 推進 U2+U6；`!important` 保留為規範必要（非偷懶）、已附證據。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-09_FE-CSS-GOV_C2_*.bak ×8

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/css/globals.css static/css/layout.css static/css/sidebar.css static/css/content.css static/css/chat.css static/css/overlays.css
git add design/docs/principles.md design/docs/css-architecture.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_globals.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_layout.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_sidebar.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_content.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_chat.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_overlays.css.bak
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_principles.md.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C2_css-architecture.md.bak

# 2.5 staged 自檢（期望恰 16 檔）
git diff --cached --name-only

# 3. commit message 草稿（寫入 /tmp/FE-CSS-GOV_C2_msg.txt）
cat > /tmp/FE-CSS-GOV_C2_msg.txt << 'EOF'
FE-Refactor: FE-CSS-GOV C2 — Layer Cascade

為 6 支樣式表套用原生 @layer 串接層，並保持 themes 與 print 處於 unlayered
狀態以確保覆蓋優先權。同步在 principles.md 中登載 layout margin-flow 模型。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-CSS-GOV_C2_msg.txt
```
