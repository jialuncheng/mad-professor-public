# FE-PERF-2 C3 — Stream Throttle 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-PERF-2 C3 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md §8 C3` |
| **次級參考** | plan v4（U1/U2、Q1/Q2、**收尾不變式**）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md §2-1` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`0de91af`（FE-PERF-2 C2 — Deferred Boot，已 ship）。
- **本次改動**：新增 `makeThrottledRenderer`（rAF+160ms）+ 主串流/replay 兩站點接線 + 四出口收斂；**消 O(n²) 串流熱路徑**（本包主菜）。
- **完成狀態**：§6.3 靜態全綠 + `node --check` 語法通過 + **節流器 node 單元 smoke 5/5**；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v4 策略 z）：落地 **U1**（節流+收尾不變式）+ **U2**（scrollTop 併同幀）；正向推進、未做白工。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | Stream Throttle — `makeThrottledRenderer`（rAF+160ms、update/flush/cancel）+ 主串流（sentence→update、done 首行 flush、catch flush）+ replay（sentence→update、done 首行 cancel+原碼收尾、onerror cancel）；scrollTop 移入 paintFn 同幀 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git）**：`static/index.html`（diff **+61/-7**：helper ~38 行 + 主串流 4 處 + replay 4 處、皆帶 `[FE-PERF-2 C3]` marker）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-09_FE-PERF-2_C3_index.html.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1/C2 執行報告。

---

## §4 修改說明（節流器核心邏輯 + Done/Catch/Replay 四出口）

### 節流器（插於 renderMarkdownWithMath 定義後、`:1677-1714`）
`makeThrottledRenderer(paintFn)` → `{update, flush, cancel}`：
- **update(t)**：暫存最新內容 + 排程——距上次 paint ≥160ms 直接 rAF；未滿則 setTimeout 補足間隔後 rAF（**尾批必排、不丟尾**）。
- **flush()**：取消 pending（timer+rAF）→ 若有暫存**立即 paint**；無暫存 no-op（**冪等、恰一次**）。
- **cancel()**：取消 pending + 丟棄暫存（讓位給呼叫端自己的渲染）。
- paintFn 按站點封裝、渲染與捲底**同幀**（Q2）：主串流＝`innerHTML`+`messages.scrollTop`；replay＝`removeCursor`→`innerHTML`→`appendCursor`→`msgsEl.scrollTop`（cursor 語意完整保留）。

### 四出口收斂（plan v4 U1 收尾不變式·恰一次）
| 出口 | 處置 | 理由 |
|---|---|---|
| 主串流 `chunk.done`（`:3556`） | **首行 `r.flush()`** 再 grounding | 原碼 done 不渲染（靠最後 sentence render）→ flush 補最終全量 |
| 主串流外層 `catch`（`:3569`） | `r.flush()` | 斷線保留最後一批已收內容 |
| replay `chunk.done`（`:3259`） | **首行 `r.cancel()`**、其後原收尾渲染碼**零改** | 原碼自帶收尾渲染、再 flush 即雙渲染 |
| replay `es.onerror`（`:3281`） | `r.cancel()` 於 `removeCursor()` 前 | **執行期補強**（見下） |

### 執行期補強（1 行、誠實標註）
tasks §8 C3 列了三出口；實作時發現 **replay `es.onerror` 是第四出口**：錯誤後若有 pending rAF，paint 會在 stream 已死時執行 `appendCursor()` → **殘留永久閃爍 cursor**。依 U1 不變式（不殘留）於 onerror 補 `r.cancel()` 一行——與 done 同契約、無新設計、已加 marker 註解。

### 主串流 r 定義位置（tasks 細節微調、誠實標註）
tasks 寫「迴圈前」；實作置於 **try 之外**（aiMsg 建立後、`:3527-3531`）——否則 fetch 即拋時 catch 內 `r.flush()` 是 ReferenceError。語意不變、更安全。

---

## §5 測試與驗收結果（§6.3 終端輸出 + SOP §4 自評）

```
$ node --check <script 本體 2290 行>
✅ 語法通過

$ node throttle_smoke.js       # 抽出 helper + rAF polyfill 實測
60 次 update → paint 3 次 ✅ 節流生效（~20x 削減）
最末 paint = t60 ✅ 尾字不丟
flush 後 = final ✅ flush 立即最終渲染
✅ flush 冪等（恰一次、無雙渲染）
✅ cancel 丟棄 pending（replay done/onerror 契約）

$ grep 計數：rAF=2 / makeThrottledRenderer=3（定義+2 站點）/ r.update=2 / r.flush=2 / r.cancel=2   ✅ 全符期望
$ 管線零觸碰：diff 中無任何佔位機制行（MO/MC/PLACEHOLDER/katex.renderToString）  ✅
$ git diff --stat：static/index.html +61/-7（單檔）  ✅
```

**保留的直呼點（規格內）**：`:2945` 論文內容 / `:3158` 歷史載入 / `:3178` partial 初渲（單次非熱路徑、Q4 不納）；`:3263` replay done 原碼收尾（U1 要求保留）；`:3231`/`:3548`＝paintFn 本體。

**SOP §4 檢查表自評（本 commit 相關項）**：
- [x] §2-1 串流：**紅線 1 本 commit 治本**——無「每 token 全量 re-parse/innerHTML」；重排版 rAF+160ms 節流 + 收尾恰一次。
- [x] §2-4 監聽/rAF：DOM 寫入對齊 rAF（paintFn）；scrollTop 讀寫同幀一次。
- [x] §3 渲染正確性：`renderMarkdownWithMath` 內部零改（diff 佐證）；同輸入同最終 HTML（paintFn 用同一 formatted 字串與原渲染式）。
- ⚠️ 瀏覽器 E2E（長答案打字流暢、尾字完整、replay cursor、grounding sources、DevTools Performance ≤6-7 次/秒）：**留 baron 視覺核查**（node smoke 已證節流/flush/cancel 邏輯正確）。

---

## §6 不可動清單遵守

- [x] 後端業務代碼（`.py`）/ SSE 契約 — 零改。
- [x] **`renderMarkdownWithMath` 內部七步管線 — 零觸碰**（§5 diff 佐證；只改呼叫頻率）。
- [x] `:3158` 歷史載入路徑 — 未納入節流（Q4 定案）。
- [x] marked/KaTeX vendor、`login.html`、`themes/`、`design/docs/` — 未動。
- [x] 未夾帶 C4/緩議項。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1–C3 執行報告 暫存 `baton/`，未 mv、未 git add。
- **git 追蹤**：本 commit ＝ `static/index.html` + `.claude-logs/archive/…C3_index.html.bak`。
- **hash 自癒**：C2 已 ship `0de91af` → TODO C2 列已回填（本輪同步）。
- **下一步**：**C4 — Paint Hints（字型預載/被動監聽/內容可視性）**，由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？兩處 tasks 細節微調（r 定義位置、onerror cancel）皆為 U1 不變式必要、已誠實標註、零新設計。(b) 推進哪個 U-N？U1+U2（本包最高槓桿）；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：.claude-logs/archive/2026-07-09_FE-PERF-2_C3_index.html.bak

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/index.html
git add .claude-logs/archive/2026-07-09_FE-PERF-2_C3_index.html.bak

# 2.5 commit 前 staged 自檢（期望恰為上列 2 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-PERF-2_C3_msg.txt）
cat > /tmp/FE-PERF-2_C3_msg.txt << 'EOF'
FE-Refactor: FE-PERF-2 C3 — Stream Throttle

新增 rAF 與 160ms 雙重節流器，重構主串流與 replay 的高頻渲染，並將
滾動 scrollTop 計算併入同幀，消除串流期間的 O(n²) 重排與強制 Reflow。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-PERF-2_C3_msg.txt
```
