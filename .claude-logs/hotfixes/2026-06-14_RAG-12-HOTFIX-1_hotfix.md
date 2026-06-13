# RAG-12-HOTFIX-1 — 緊急熱修復：圖片 alt 內 LaTeX 致 `<img>` 炸穿與後續排版全毀

> **警示**：本文件為 **FE-Hotfix** 緊急熱修復紀錄，修正 RAG-12（前端 KaTeX 數學渲染）落地後、於含 LaTeX 圖說之文件上觸發的嚴重級聯破版。
> **修復原則**：只改 `static/index.html` 之 `renderMarkdownWithMath` 受災點;零後端、零管線、零 .py、零 golden 重捕。
> **工作流**：FE-Hotfix（依 `ref/WORKFLOW_SOP.md §1.4`、套 `template_hotfix.md`）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **RAG-12-HOTFIX-1** | `待 baron 回填` | FE-Hotfix: RAG-12-HOTFIX-1 — 圖片 alt 內 LaTeX 破版（renderMarkdownWithMath 抽 math 前保護圖片整段） |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：B 軌簡報 `Ch37_Plant-Nutrition_shadow`（植物營養）閱讀視圖，自**氮循環圖（page-30）起、後續所有投影片排版全毀**——該圖之圖說（圖片 alt）內的化學式被渲染成**直排亂碼**，`![alt](url)` 圖片語法被咬爛（殘骸形如 `…transport）。">`），其後內容（輪作 / 過場頁 / 菌根 / 內外生菌根 / 根際…）全被吞入畸形 HTML。
- **受災範圍**：**所有圖說（figure_description→圖片 alt）含 LaTeX `$...$` 之文件**之閱讀視圖。實測 28 篇中僅此簡報之氮循環圖中招（Vision 忠實轉錄圖中化學式 `$N_2$`/`$\text{NH}_4^+$`/`$\text{NO}_3^-$` 進 alt）。**A 軌（academic/md_restore，圖走 `.figure`/`.ph` 區塊、不塞 markdown alt）與履歷（圖說無 LaTeX）皆正常**——此為「非 CSS、非空白頁」之鐵證（A/B 兩軌共用同一 `renderMarkdownWithMath` 與 `#paper-content` CSS，A 軌正常即證 FE-RHYTHM-UNIFY CSS 無辜）。
- **首發證據（baron 端 rendered DOM 殘骸）**：
  ```
  …大氣氮 （$N_2$
  ）與有機質（
  o
  r
  g
  a
  n
  i
  c
  …）…轉化為銨根（$\text{NH}_4^+$）與硝酸鹽（$\text{NO}_3^-$），…（plant root absorption and transport）。">
  ```
  （`$...$` 變直排 KaTeX glyph + 圖片 `](url)` 被咬成 `">`）

### 2. 真因診斷 (Root Cause)

- **技術細節**：`renderMarkdownWithMath`（RAG-12 C2）之 math 抽取**不分場合**——步驟 4 的 inline-math 正則對整份原文抽 `$...$`，**含 markdown 圖片 `![ …$N_2$… ](url)` 之 alt 文字內的 `$...$`**。其後致命級聯：
  1. **步驟 4**：alt 內 `$N_2$` 等被抽成 PUA math 佔位符（`{idx}`）。
  2. **步驟 6**：`marked.parse` 產出 `<img … alt="…{佔位符}…">`（佔位符落在 **alt 屬性值內**）。
  3. **步驟 7**：以 `katex.renderToString()` 之回傳 **`<span class="katex">…`（內含 `"` 與 `<>`）** 取代佔位符 → **注入 `alt="…"` 屬性內** → KaTeX HTML 之 `class="…"` 的 `"` 使 alt 屬性**提前閉合** → `<img>` 標籤結構崩壞、KaTeX 殘餘 `>…</span>` 外洩為裸 HTML → **吞噬該圖之後所有內容** → 「後續排版全部錯誤」。
- **為何 RAG-12 漏此邊界**：RAG-12 plan/spike 聚焦「正文」之 `$`/`$$` 渲染與 `__MATH__`→PUA 佔位、code 保護、texmath 啟發式;**未涵蓋「`$...$` 出現在圖片 alt 屬性」之情境**（alt 內數學無渲染意義、且注入屬性必炸標籤）。
- **定位程式碼**：`static/index.html` `renderMarkdownWithMath`（約 L1623–1659）——步驟 4 inline math `t.replace(/\$([^\s$](?:[^$]*?[^\s$])?)\$(?!\d)/g, …)`（L1639）抽到 alt 內 `$`;步驟 7 回填（L1648–1657）注入 alt。

---

## 熱修復修法 (Minimal Hotfix)

**核心**：抽 math **之前**，先把 **markdown 圖片整段 `![...](...)` 抽成佔位符**（與既有 code 保護同手法）；於 **`marked.parse` 之前還原**。如此 alt 內 `$...$` **永不進 math 管線**（步驟 4 抽不到 → 步驟 7 無佔位可注入 alt），圖片標籤不再被炸;alt 內留**字面 `$N_2$`**（alt 為無障礙 fallback、不可見、無害）。

- **通用性**：解**所有文體**（不只簡報）凡圖說含 `$` 之破版;非簡報 OK 繃。
- **零行為變更（正常圖片/正文 math）**：無 LaTeX 之圖片 alt → 佔位/還原前後等價;正文 `$$…$$`/`$x$` 仍照常抽取渲染（圖片保護只圈 `![...](...)` span、不碰正文）。

### `static/index.html` — `renderMarkdownWithMath` 最小改動

```diff
   function renderMarkdownWithMath(raw) {
     if (raw == null) raw = '';
     const MO = '', MC = '';     // math 佔位哨兵（Unicode PUA、marked 原樣穿透）
-    const codeBlocks = [], mathBlocks = [];
+    const codeBlocks = [], mathBlocks = [], imgBlocks = [];
     let t = String(raw);
     // 1. 抽 code（fenced + inline）→ 佔位（步驟 5 還原、不穿透 marked）
     t = t.replace(/(```[\s\S]*?```|`[^`\n]+?`)/g, function (m) {
       codeBlocks.push(m); return '__CODE_PLACEHOLDER_' + (codeBlocks.length - 1) + '__';
     });
+    // === [RAG-12-HOTFIX-1 START] === 1.5 抽 markdown 圖片整段 → 佔位（步驟 5 還原、marked.parse 前）
+    //   真因：圖說（figure_description）整段塞進 ![alt](url) 之 alt；alt 內若含 $...$（如氮循環圖
+    //   $N_2$/$\text{NH}_4^+$），步驟 4 會抽成 math 佔位 → 步驟 7 把 katex.renderToString 的
+    //   <span class="katex">…（含 " 與 <>）回填進 alt="…" → 引號提前閉合、<img> 標籤炸穿、
+    //   後續 HTML 全被吞 → 「後續排版全部錯誤」。保護圖片整段使 alt 內 $ 永不進 math 管線
+    //   （步驟 5 marked.parse 前還原；alt 留字面 $、不可見、無害）。
+    t = t.replace(/!\[[^\]]*\]\([^)]*\)/g, function (m) {
+      imgBlocks.push(m); return '__IMG_PLACEHOLDER_' + (imgBlocks.length - 1) + '__';
+    });
+    // === [RAG-12-HOTFIX-1 END] ===
     // 2. 護跳脫 \$（split 法、無 lookbehind）→ 使步驟 3/4 之 $ 必為真 math
     t = t.split('\\$').join('__ESC_DOLLAR__');
     // 3. 抽 block math（$$ 先於 $；[\s\S] 跨行、不用 dotAll s 旗標）→ PUA 佔位
     t = t.replace(/\$\$([\s\S]+?)\$\$/g, function (m, f) {
       mathBlocks.push({ formula: f, displayMode: true }); return MO + (mathBlocks.length - 1) + MC;
     });
     // 4. 抽 inline math（texmath：開 $ 後非空白、閉 $ 前非空白且後非數字；僅 lookahead、無 lookbehind）
     t = t.replace(/\$([^\s$](?:[^$]*?[^\s$])?)\$(?!\d)/g, function (m, f) {
       mathBlocks.push({ formula: f, displayMode: false }); return MO + (mathBlocks.length - 1) + MC;
     });
     // 5. 還原 code 與 \$（僅 tempText；math 仍佔位）
     t = t.replace(/__CODE_PLACEHOLDER_(\d+)__/g, function (m, i) { return codeBlocks[i]; });
     t = t.split('__ESC_DOLLAR__').join('\\$');
+    // === [RAG-12-HOTFIX-1] === 還原圖片（marked.parse 前；alt 內 $ 已不在 math 佔位、留字面）
+    t = t.replace(/__IMG_PLACEHOLDER_(\d+)__/g, function (m, i) { return imgBlocks[i]; });
     // 6. marked.parse（math PUA 佔位穿透）
     let html = marked.parse(t);
     // 7. 回填 math：先還原公式內 __ESC_DOLLAR__→\$（步驟 7 鐵律），再 katex 渲染、壞式優雅降級
     html = html.replace(new RegExp(MO + '(\\d+)' + MC, 'g'), function (m, i) {
       …（不變）…
     });
     return html;
   }
```

### 設計說明與邊界（誠實）

- **佔位符存活**：`__IMG_PLACEHOLDER_N__` 無 `$`、無 PUA → 不被步驟 2（esc）/3（block）/4（inline）誤動;步驟 5 於 esc 還原後、`marked.parse` 前還原 → marked 照常渲染原圖、alt 留字面 `$`。
- **正則邊界**：`!\[[^\]]*\]\([^)]*\)`——alt 不含 `]`（HOTFIX-2 `_safe_alt` 已將 alt 內 `][()` 轉全形 → 不咬斷）、url 不含 `)`（slide 圖 `/api/papers/…/page-N.jpg` 無 `)`）。
- **不涵蓋（範圍外、非本 bug）**：① reference-style `![alt][id]`（slide 用 inline `![](url)`、不發生）② 裸 HTML `<img alt="$…$">`（A 軌走 `.figure`/`.ph` 區塊、B 軌走 markdown image、皆不產裸 `<img>` 含 LaTeX alt）。如未來出現再議。
- **與 RAG-12 既有保護不衝突**：圖片保護置於 code 保護之後、math 之前;三者佔位符命名空間獨立（`__CODE_/__IMG_/__ESC_` 與 PUA）。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組（純前端、零 .py）

```bash
# 零 .py diff（FE-Hotfix）
git diff --name-only | grep '\.py$'        # 期望：空
# 全套件維持基線（純 CSS/JS、不影響 pytest）
venv/bin/python -m pytest -q               # 期望：631 passed（唯一 fail＝既有 .env LOG_FORMAT flake）
```

### 2. 靜態 grep 核查

```bash
grep -n "RAG-12-HOTFIX-1\|imgBlocks\|__IMG_PLACEHOLDER_" static/index.html
#   期望：START/END 包裹 + imgBlocks 宣告 + 抽取/還原各 1
```

### 3. 前端 node spike（正則層、不需 katex/marked 本體）

於 worktree 拋棄式 node 腳本驗證（完成即刪、零 production diff）：
- **(a) 圖片含 LaTeX alt 受保護**：輸入 `![圖說 $N_2$ 與 $\text{NO}_3^-$](images/p.jpg)` → 經「抽圖片→抽 math→還原圖片」後，**圖片整段原樣還原、alt 內 `$N_2$` 為字面**（mathBlocks 不含 alt 內公式 → 步驟 7 不會注入 alt）。
- **(b) 正文 math 不受影響**：輸入 `正文 $$E=mc^2$$ 與行內 $x$` → block/inline math 仍各自抽成 PUA 佔位（正常渲染路徑不變）。
- **(c) 混合**：圖片 alt 之 `$` 與正文 `$` 並存 → 僅正文 `$` 進 mathBlocks、alt 之 `$` 不進 → 斷言 mathBlocks 數 == 正文 math 數。

### 4. baron 瀏覽器 E2E（收尾、headless 不可替代）

影子重整 `Ch37_Plant-Nutrition_shadow`（**無需重跑管線**——純前端渲染修、final_zh 不變、重整即生效）：
- 氮循環圖（page-30）正常顯示為一張圖（alt 內化學式不再直排、不再炸圖）。
- 其後輪作 / 過場頁 / 菌根 / 內外生菌根 / 根際 等**全部恢復正常排版**（級聯破版消失）。
- 正文若有真 `$$…$$`/`$…$`（如本簡報 page-30 正文之 `$N_2$` 等）仍正確 KaTeX 渲染。
- A 軌 / 履歷不受影響（本即正常）。

---

## ⚠️ 後續未竟（baron 擱置、非本 hotfix）

- **B2 過場投影片沒踢除**：page-32「過場投影片 (Transition Slide)」被 Vision 給了標題 → HOTFIX-4 跳過條件「is_blank 且 title+content 皆空」不成立 → 沒踢。屬 HOTFIX-4 gap（次要、不致命），baron 擱置;未來如修，方向＝放寬跳過為「is_blank 且 markdown_content 空」（容許 title/figure_description）+ 釐清 Vision prompt 過場/分隔頁 is_blank=true，須搭 golden 重捕。

---

## 回退與備案

```bash
# 若本 Hotfix 未解或引發更大 regression：
git revert <RAG-12-HOTFIX-1 hash>          # 單檔單 hunk、一步乾淨還原
# 或自備份還原：
cp .claude-logs/archive/2026-06-14_RAG-12-HOTFIX-1_index.html.bak static/index.html
```

---

## baron 執行命令（Run 階段、commit 草稿）

```bash
# 1. 備份
cp static/index.html .claude-logs/archive/2026-06-14_RAG-12-HOTFIX-1_index.html.bak

# 2. （依 §3 diff 改 static/index.html）

# 3. git add（含備份）
git add static/index.html .claude-logs/archive/2026-06-14_RAG-12-HOTFIX-1_index.html.bak

# 4. commit message 草稿（寫入 tmp/RAG-12-HOTFIX-1_msg.txt；簽名當前模型）
mkdir -p tmp
cat > tmp/RAG-12-HOTFIX-1_msg.txt << 'EOF'
FE-Hotfix: RAG-12-HOTFIX-1 — 圖片 alt 內 LaTeX 破版（renderMarkdownWithMath 抽 math 前保護圖片整段）

真因：renderMarkdownWithMath（RAG-12 C2）步驟 4 不分場合抽 $...$，含 markdown 圖片
![alt](url) 之 alt 內的 $...$（如氮循環圖 figure_description 的 $N_2$/$\text{NH}_4^+$/$\text{NO}_3^-$）；
步驟 7 以 katex.renderToString 的 <span class="katex">…（含 " 與 <>）回填進 alt="…" →
引號提前閉合、<img> 標籤炸穿、後續 HTML 全被吞 → 後續排版全部錯誤 + 圖說直排亂碼。
A 軌（.figure/.ph 區塊、不塞 markdown alt）與履歷（圖說無 LaTeX）皆正常 → 證 FE-RHYTHM-UNIFY CSS 無辜。

修法：抽 math 之前先把 markdown 圖片整段 ![...](...) 抽成 __IMG_PLACEHOLDER_N__（同 code 保護手法），
marked.parse 前還原 → alt 內 $ 永不進 math 管線（留字面、不可見、無害）、<img> 不再被炸。
通用解所有文體圖說含 $ 之破版；純前端 index.html、零後端/管線/.py、零 golden 重捕。

驗證：grep HOTFIX-1 包裹+imgBlocks 命中；node spike 驗（a）圖片 LaTeX alt 受保護原樣還原（b）正文 math 不受影響；
全套件 631 passed（基線維持、唯一 fail＝既有 .env LOG_FORMAT flake、零 .py diff）。
baron 瀏覽器 E2E：重整 Ch37 簡報 → 氮循環圖正常、其後排版全恢復（無需重跑管線、final_zh 不變）。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 5. baron 手動 commit
git commit -F tmp/RAG-12-HOTFIX-1_msg.txt
```

> 收官歸檔（hotfix 無 Check 階段）：Run 落地後本文件 `mv` baton → `hotfixes/`、執行報告 `mv` baton → `executions/`、一次性 `git add`（依 WORKFLOW_SOP §3 baton 暫存鐵律）。
