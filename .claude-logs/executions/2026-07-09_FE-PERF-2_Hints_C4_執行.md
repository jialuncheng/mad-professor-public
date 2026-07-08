# FE-PERF-2 C4 — Paint Hints 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-PERF-2 C4 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md §8 C4` |
| **次級參考** | plan v4（U4/U5/U8、Q8）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md §2-4/§2-5` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit）——C1–C4 實作全數完結、餘 checkout |

---

## §1 基準與完成狀態

- **基準 Commit**：`b2f21d8`（FE-PERF-2 C3 — Stream Throttle，已 ship）。
- **本次改動**：三項宣告式 hint——KaTeX 兩核心字型 preload（U4）+ 兩處 scroll passive（U5）+ `.msg-user`/`.msg-ai` content-visibility 記憶尺寸型（U8）。
- **完成狀態**：§6.4 全綠 + `node --check` 通過；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v4 策略 z）：落地 **U4+U5+U8**；至此 U1–U5、U8 實作完結（U6/U7 屬 checkout 總驗）；未做白工。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | Paint Hints — head preload×2（`Main-Regular`/`Math-Italic`、`as="font" type="font/woff2" crossorigin`）+ scroll passive×2（`:1825`/`:1966`）+ `.msg-user`（`:1015`）/`.msg-ai`（`:1045`）`content-visibility: auto; contain-intrinsic-size: auto 120px` | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git）**：`static/index.html`（diff **+11/-2**：head 3 行〔marker+2 preload〕+ CSS 兩塊各 3 行 + scroll 兩處改參）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-09_FE-PERF-2_C4_index.html.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1–C3 執行報告。

---

## §4 修改說明

1. **字型 preload（U4）**：`katex.min.css` link 之前插入兩條（preload scanner 於 CSSOM 建成**前**即發起、消公式字型 FOUT/版跳）：
   ```html
   <link rel="preload" href="/static/vendor/katex/fonts/KaTeX_Main-Regular.woff2" as="font" type="font/woff2" crossorigin>
   <link rel="preload" href="/static/vendor/katex/fonts/KaTeX_Math-Italic.woff2" as="font" type="font/woff2" crossorigin>
   ```
   僅此二支（25.7K+16.1K）、防無公式頁過度預載；`crossorigin` 為字型 preload 規範必需（同源亦然、否則雙重下載）。
2. **scroll passive（U5）**：兩處第三參 `true` → `{ capture: true, passive: true }`（capture 語意保留、告知瀏覽器不 preventDefault → 合成滾動不等 JS）：
   - `:1825` `closePopups` 監聽（handler 僅 closest 判斷+closePopups、無 preventDefault ✅）
   - `:1966` tooltip `hideNow`（無 preventDefault ✅）
3. **content-visibility（U8·Q8 定案）**：兩 CSS 塊首各加：
   ```css
   content-visibility: auto;
   contain-intrinsic-size: auto 120px;
   ```
   **記憶尺寸型**（`auto` 關鍵字：首渲染後記真實尺寸、120px 估值僅首渲前生效）——聊天泡泡高度差異巨大、固定值必致上捲 scrollHeight 跳動，故禁；視窗外歷史訊息跳過 layout/paint、長對話滾動成本下降；Safari 18+ 基線內特性（相容底線已定案）。

---

## §5 測試與驗收結果（§6.4 終端輸出 + SOP §4 自評總勾）

```
$ grep 計數：preload=2 / as="font"+crossorigin=2 / passive: true=2 /
  content-visibility=2 / contain-intrinsic-size: auto=2 / 固定值殘留=0   ✅ 全符期望
$ node --check <script 本體>（passive 改動觸及 script、複驗）
✅ 語法通過
$ git diff --stat：static/index.html +11/-2（單檔）  ✅
```

**SOP §4 檢查表總勾（U7·C1–C4 落地完結自評）**：
- [x] §2-1 串流：C3 rAF+160ms 節流+收尾恰一次（node smoke 5/5）。
- [x] §2-2 script：C1 自託管（零裸 CDN）+ C2 全 defer+DOMContentLoaded。
- [x] §2-3 動畫：全案未新增任何過渡；未 animate width/height/margin（側欄 rail 未碰）。
- [x] §2-4 監聽：本 commit scroll×2 passive+capture 保留；DOM 寫入已對齊 rAF（C3 paintFn）。
- [x] §2-5/7 資源：本 commit 字型 preload×2；KaTeX code-split 依 audit 裁決不做（緩議）。
- [x] §3 渲染正確性六類：佔位管線零觸碰（C3 diff 佐證）/ 未動 alt/CJK/soft-break/`~` 相關 / 未引入 `:has()`（U8 為 property 非選擇器）。
- [x] 視覺一致性：未動 design/docs 轄下 token/排版；U8 僅渲染調度不改視覺。
- ⚠️ 瀏覽器 E2E（三軌 + console 0 + FOUT 消除 + ≥30 則上捲無跳動 + 串流錨底 + Performance 節流證跡）：**留 baron 視覺核查**（checkout Conformance 前置）。

---

## §6 不可動清單遵守

- [x] 後端業務代碼（`.py`）/ SSE 契約 — 零改。
- [x] `renderMarkdownWithMath` 內部 — 未觸。
- [x] KaTeX vendor 本體 — 僅 head 加 preload 標籤、檔案未動。
- [x] 側欄 `transition: width` / rail — 未碰（audit #6 不做）。
- [x] `login.html` / `themes/` / `design/docs/` — 未動。
- [x] 未夾帶緩議項（popup rAF / hover prefetch / code-split / `:3158` 歷史路徑）。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1–C4 執行報告（6 檔）暫存 `baton/`，未 mv、未 git add（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ `static/index.html` + `.claude-logs/archive/…C4_index.html.bak`。
- **hash 自癒**：C3 已 ship `b2f21d8` → TODO C3 列已回填（本輪同步）。
- **下一步**：**checkout — 成果收官歸檔**（U1–U8 Conformance 總驗 + SOP §4 總勾複核 + 鐵律 checkout 報告直產 executions/ + staged 白名單自檢 + TODO 雙層結案），由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？否——三項皆宣告式、逐錨點精準落點。(b) 推進哪個 U-N？U4+U5+U8（實作面收官）；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：.claude-logs/archive/2026-07-09_FE-PERF-2_C4_index.html.bak

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/index.html
git add .claude-logs/archive/2026-07-09_FE-PERF-2_C4_index.html.bak

# 2.5 commit 前 staged 自檢（期望恰為上列 2 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-PERF-2_C4_msg.txt）
cat > /tmp/FE-PERF-2_C4_msg.txt << 'EOF'
FE-Refactor: FE-PERF-2 C4 — Paint Hints

預載入 KaTeX 兩支核心字型防止 FOUT，為兩處 scroll 監聽加入 passive
以提高滑動流暢度，並為訊息泡泡加上 content-visibility 記憶尺寸優化。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-PERF-2_C4_msg.txt
```
