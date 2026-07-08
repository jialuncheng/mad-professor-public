# FE-PERF-2 C1 — Marked Vendoring 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-PERF-2 C1 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md §8 C1` |
| **次級參考** | `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_plan_v1.md`（v4、U3-1）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`5d3be98`（CONTEXT-1 C5，git log HEAD）。
- **本次改動**：marked 9.1.6 鎖版自託管 + `index.html` head 換本地 src；**未加 defer**（時序變更屬 C2、換源與時序解耦）。
- **完成狀態**：§6.1 驗收全綠 + node 功能 smoke 通過；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v4 策略 z）：落地 **U3-1**（自託管、head 零跨源）；U3-2/3/4（defer+包裹+前置閘）屬 C2；正向推進、未做白工。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Marked Vendoring — marked 9.1.6 自 cdnjs 原 URL 下載自託管 `static/vendor/marked/marked.min.js`（36,054 bytes、banner 驗證 `marked v9.1.6`）+ `index.html:8` src 換 `/static/vendor/marked/marked.min.js`（不加 defer） | 待回填 |

---

## §3 變動檔案清單

- **新增（入 git）**：`static/vendor/marked/marked.min.js`（36,054 bytes、UMD、banner `marked v9.1.6`）
- **修改（入 git）**：`static/index.html`（`:8` 一行換 src + C1 註解一行；diff +2/-1）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-09_FE-PERF-2_C1_index.html.bak`（修改前原狀）
  - **路徑正規化註**：run 提示詞寫 `archive/`，依專案慣例（既有全部 `.bak` 所在）落 `.claude-logs/archive/`。
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks（皆留 baton）。

---

## §4 修改說明（自託管原檔獲取與換源）

1. **備份**：`cp static/index.html .claude-logs/archive/2026-07-09_FE-PERF-2_C1_index.html.bak`。
2. **下載**：`mkdir -p static/vendor/marked && curl -sS -o static/vendor/marked/marked.min.js https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js` → 36,054 bytes、檔頭 banner `marked v9.1.6 - a markdown parser`（鎖版驗證、Q3）。
3. **換源**（`index.html:8`）：
   ```diff
   - <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
   + <!-- === [FE-PERF-2 C1] === marked 9.1.6 自託管（原 CDN 同版換源、離線/GFW 零跨源依賴、比照 KaTeX vendored；defer 屬 C2） -->
   + <script src="/static/vendor/marked/marked.min.js"></script>
   ```
4. **微修正（過程自癒）**：C1 註解初稿含 `cdnjs` 字樣使 §6.1 `grep -c cdnjs` 誤命中 1 → 措辭改「原 CDN」，硬條件歸 0（無功能影響）。
5. 同版同步載入、行為零變；跨源依賴數 1 → **0**。

---

## §5 測試與驗收結果（§6.1 終端輸出 + SOP §4 自評）

```
$ grep -c "cdnjs" static/index.html
0                                        # 期望 0 ✅（零跨源）
$ grep -c "/static/vendor/marked/marked.min.js" static/index.html
1                                        # 期望 1 ✅
$ wc -c < static/vendor/marked/marked.min.js
36054                                    # ~36KB ✅
$ grep -c "marked v9.1.6" static/vendor/marked/marked.min.js
1                                        # 鎖版標記 ✅

$ node -e "const m=require('./static/vendor/marked/marked.min.js'); …parse('**bold** and \$math\$')"
parse => <p><strong>bold</strong> and $math$</p>
✅ marked 功能正常                        # UMD 載入 + parse 功能 smoke（$ 原樣穿透、符佔位管線預期）
```

**SOP §4 檢查表自評（本 commit 相關項）**：
- [x] §2-2 script：未新增裸 CDN；第三方套件自託管（本 commit 主體）。defer 屬 C2、暫維持同步（與改前等價）。
- [x] §3 渲染正確性：未觸 `renderMarkdownWithMath`；同版 marked、佔位管線行為零變（node smoke `$` 原樣穿透佐證）。
- [x] 視覺一致性：無 CSS/DOM 結構改動。
- ⚠️ 瀏覽器 E2E（三軌開頁渲染 + console 0）：**留 baron 視覺核查**（本環境無瀏覽器；node smoke 已證檔案功能完整）。

---

## §6 不可動清單遵守

- [x] 後端業務代碼（`.py`）— 零改動。
- [x] `renderMarkdownWithMath` 內部 — 未觸。
- [x] marked 版本 — 鎖 9.1.6（banner 驗證）。
- [x] KaTeX vendor / `login.html` / `themes/` / `design/docs/` — 未動。
- [x] 未加 defer（屬 C2）、未夾帶緩議項。
- [x] baton 過程檔 — 未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / 本 C1 執行報告 暫存 `baton/`，未 mv、未 git add（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ `static/index.html` + `static/vendor/marked/marked.min.js` + `.claude-logs/archive/…C1_index.html.bak`。
- **hash 自癒**：TODO L16 CONTEXT-1 索引行末 hash `待 baron 回填` → `5d3be98`（git log 實證）已回填。
- **下一步**：**C2 — Deferred Boot（defer 與初始化包裹）**，由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？否——僅 head 一行換源 + vendor 新檔。(b) 推進哪個 U-N？U3-1；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：.claude-logs/archive/2026-07-09_FE-PERF-2_C1_index.html.bak

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔；WORKFLOW_SOP §3 白名單鐵律）
git add static/index.html
git add static/vendor/marked/marked.min.js
git add .claude-logs/archive/2026-07-09_FE-PERF-2_C1_index.html.bak

# 2.5 commit 前 staged 自檢（期望恰為上列 3 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/FE-PERF-2_C1_msg.txt）
cat > /tmp/FE-PERF-2_C1_msg.txt << 'EOF'
FE-Refactor: FE-PERF-2 C1 — Marked Vendoring

將 marked 9.1.6 自 cdnjs 下載並自託管於 static/vendor/marked/，修改
static/index.html 頭部引用為本地路徑，消除跨源外部依賴。
EOF

# 4. baron 手動執行
git commit -F /tmp/FE-PERF-2_C1_msg.txt
```
