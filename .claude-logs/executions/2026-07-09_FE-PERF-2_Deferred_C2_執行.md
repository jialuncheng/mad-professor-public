# FE-PERF-2 C2 — Deferred Boot 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-PERF-2 C2 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md §8 C2` |
| **次級參考** | plan v4（U3-2/3/4、Q7 整塊單包）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`337764e`（FE-PERF-2 C1 — Marked Vendoring，已 ship）。
- **本次改動**：marked/katex 兩外部 script 加 `defer` + inline 主 script（2,234 行）整包 `DOMContentLoaded`；**消除 head parser-blocking**。
- **完成狀態**：§6.2 驗收全綠 + `node --check` 語法驗證通過；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v4 策略 z）：落地 **U3-2/3/4**（defer + 整包 + 前置閘）；U3 全數完成（U3-1 已於 C1）；正向推進、未做白工。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Deferred Boot — `:9`/`:12` 兩 script 加 `defer` + inline 主 script（`:1600-:3837`）整包 `DOMContentLoaded`（頭尾插入 3 行、零重排） | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git）**：`static/index.html`（diff **+5/-2**：defer×2 + 包裹 START 2 行 + 包裹 END 1 行；既有 2,200+ 行縮排零重排）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-09_FE-PERF-2_C2_index.html.bak`（修改前原狀；路徑依專案慣例落 `.claude-logs/archive/`）
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1 執行報告（皆留 baton）。

---

## §4 修改說明（前置閘結果 / defer / 包裹實作）

1. **前置閘（U3-4）**：`grep -nE 'on[a-z]+=' static/index.html` → **8 命中、逐筆裁定全為誤命中**：7 筆 `contenteditable=`（子字串 `ontenteditable=` 撞正則）+ 1 筆註解文字（`:3553`「使用 addEventListener 而非 onkeydown=…」為說明文字非屬性）。**零真實 inline event handler → 閘通過、無需 `window.fn` 暴露**（與 tasks 拆分時 body markup 人工掃描結論一致）。
2. **defer**（`:9`/`:12`）：
   ```diff
   - <script src="/static/vendor/marked/marked.min.js"></script>
   + <script src="/static/vendor/marked/marked.min.js" defer></script>
   - <script src="/static/vendor/katex/katex.min.js"></script>
   + <script src="/static/vendor/katex/katex.min.js" defer></script>
   ```
3. **DOMContentLoaded 整包**（Q7）：`<script>`（`:1600`）次行插 START marker + `document.addEventListener('DOMContentLoaded', () => {`；原最末 `});` 後、`</script>` 前插 `}); // === [FE-PERF-2 C2] === END`。**僅頭尾 3 行、不重排既有縮排**。時序保證：deferred scripts 依 HTML 規範**先於** `DOMContentLoaded` 執行 → 包內頂層 `marked.use()`（原 `:1607`）與全部 `marked`/`katex` 引用安全。
4. 首屏效果：HTML parsing 不再被兩支 script 阻塞（marked 36KB + katex 277KB 改與 parse 並行下載、parse 完才執行）。

---

## §5 測試與驗收結果（§6.2 終端輸出 + SOP §4 自評）

```
$ grep -cE '<script src="/static/vendor/(marked/marked|katex/katex)\.min\.js" defer>' static/index.html
2                                        # defer=2 ✅
$ grep -n "FE-PERF-2 C2" static/index.html
1601:// === [FE-PERF-2 C2] === DOMContentLoaded 包裹 START（…）
3836:}); // === [FE-PERF-2 C2] === DOMContentLoaded 包裹 END     # 頭尾 marker ✅
$ grep -cE "on[a-z]+=" static/index.html
8                                        # 前置閘：8 筆全裁定為 contenteditable=/註解、零 handler ✅

$ sed -n '1601,3836p' static/index.html > c2_script_body.js && node --check c2_script_body.js
✅ 語法通過（DOMContentLoaded 包裹完整、無斷裂）   # 2,236 行包裹後 script 本體語法驗證

$ git diff --stat static/
 static/index.html | 7 +++++--   # +5/-2、零重排 ✅
```

**SOP §4 檢查表自評（本 commit 相關項）**：
- [x] §2-2 script：兩外部 script 皆 `defer`、無裸 CDN（紅線 2 本 commit 完成）。
- [x] §3 渲染正確性：未觸 `renderMarkdownWithMath` 內部；`marked.use()` 在包內、deferred 時序保證可用。
- [x] 視覺一致性：零 CSS/DOM 結構改動。
- ⚠️ 瀏覽器 E2E（硬重整無 `marked is not defined`、三軌渲染、上傳/主題/傳訊互動、console 0）：**留 baron 視覺核查**（本環境無瀏覽器；`node --check` 已證語法完整、時序由 HTML 規範保證）。

---

## §6 不可動清單遵守

- [x] 後端業務代碼（`.py`）— 零改動。
- [x] `renderMarkdownWithMath` 內部 — 未觸（包裹不改內文任何一行）。
- [x] marked 版本 / KaTeX vendor 本體 — 未動。
- [x] `login.html` / `themes/` / `design/docs/` — 未動。
- [x] 既有 2,200+ 行縮排 — 零重排（diff +5/-2 佐證）。
- [x] 未夾帶 C3/C4/緩議項。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1 執行報告 / 本 C2 執行報告 暫存 `baton/`，未 mv、未 git add（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ `static/index.html` + `.claude-logs/archive/…C2_index.html.bak`。
- **hash 自癒**：C1 已 ship `337764e` → TODO C1 列已回填真 hash（本輪同步）。
- **下一步**：**C3 — Stream Throttle（串流節流與滾動同批）**，由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？否——僅 defer×2 + 包裹 3 行。(b) 推進哪個 U-N？U3-2/3/4（U3 完結）；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：.claude-logs/archive/2026-07-09_FE-PERF-2_C2_index.html.bak

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/index.html
git add .claude-logs/archive/2026-07-09_FE-PERF-2_C2_index.html.bak

# 2.5 commit 前 staged 自檢（期望恰為上列 2 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-PERF-2_C2_msg.txt）
cat > /tmp/FE-PERF-2_C2_msg.txt << 'EOF'
FE-Refactor: FE-PERF-2 C2 — Deferred Boot

為 marked 與 katex 腳本加上 defer，並將 inline 主 script 封裝在
DOMContentLoaded 事件中，消除了首屏的 parser-blocking 阻塞。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-PERF-2_C2_msg.txt
```
