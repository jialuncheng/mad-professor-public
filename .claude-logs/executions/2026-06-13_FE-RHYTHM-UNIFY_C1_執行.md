# FE-RHYTHM-UNIFY C1 — Spike & 模型凍結 執行報告

> 階段 4 執行報告（C1）。純 Spike 驗證 + 模型凍結，**零 production 代碼變動**。
> 依據：`.claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_tasks.md §8 C1`。

---

## §1 基準與完成狀態

- **基準**：`gemini-refactor` 分支、worktree `hopeful-yalow-902c50`，C2 尚未落地。
- **完成狀態**：C1 Spike 驗證完成、模型已凍結。**無 production 改動**（純驗證 + 文件）。
- **commit**：本階段無代碼 → baron 以 `git commit --allow-empty` 留審計節點（§8）。

## §2 落地 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C1 | （baron `--allow-empty`、待回填）| FE-Refactor: FE-RHYTHM-UNIFY C1 — Spike & 模型凍結 |

## §3 diff stat

```
（無 production 變更；git status -s static/ → 空。產出僅 baton 執行報告 + prompts 歸檔 + TODO/INDEX 狀態）
```

## §4 真因（對應 plan）

閱讀視圖垂直節奏由「逐交界 bespoke 規則」治理（主題各設 p/h margin、L83 reset 歸零清單 margin、FE-RHYTHM-1 補 p↔list…），根因＝**只用 margin-bottom + 清單 margin 被歸零** → 節奏不對稱、打地鼠。C1 任務＝在動 production 前，先驗證統一 margin-top flow 模型之三項前提假設並凍結確切規格，杜絕 C2 執行期二次設計漂移。

## §5 修法（本階段：驗證手段，無代碼）

1. **DOM 生成碼審查**（直接子代假設）：grep `static/index.html` 確認 `#paper-content` innerHTML 來源與結構。
2. **最小 HTML harness**（/tmp、repo 外）：複刻 L83 reset + 凍結模型 + 三軌片段，結構自檢（規則數 / `:has` 計數 / 巢狀解析），完成即刪。
3. **選擇器特異度 / 互斥 / margin 摺疊 嚴格推理**：逐 adjacency 證明命中規則唯一且確定。
4. **相容性**：依 caniuse 既知基線判定 `:is`/`:not`/`+`；像素級視覺終驗交 baron（headless 無瀏覽器、誠實標注）。

## §6 不可動清單遵守狀態

- [x] **後端 / pipeline / RAG / final_zh**：零碰。
- [x] **static/index.html / static/themes/\*.css**：零碰（`git status -s static/` 空）。
- [x] **內容正規化層（3c/3d/promote）**：未動。
- [x] **主 repo 目錄**：未讀寫。

## §7 端到端驗證計畫結果（Spike 核心）

### §7.1 `git status -s static/`
```
（空 — 無 production 檔案變更，物理防線達成）
```

### §7.2 三假設驗證結論

| # | 假設 | 方法 | 結論 |
|---|---|---|---|
| **A1** | 閱讀視圖塊級為 `#paper-content` **直接子代** | 碼審：`static/index.html:2878` `#paper-content.innerHTML = renderMarkdownWithMath(content)`（＝marked.parse 輸出）；`normalizeAcademicHeader()`（L2882+）**只改 `.paper-header-meta` 之 innerHTML、不重構頂層** | 🟢 **成立**。marked 輸出之頂層塊（h1/h2/h3/p/ul/ol/`<div class="slide-head">`/`<div class="paper-header-meta">`/`.figure`/`<p><img>`）賦給 innerHTML → 皆 `#paper-content` 直接子代。`> * + *` 命中頂層流。 |
| **A2** | 巢狀清單（`li` 內 `ul ul`、blockquote 內 p）**不被 `>*+*` 誤撐** | `>` 子結合器語義：僅直接子代；巢狀內容非直接子代 + A1 | 🟢 **成立**（邏輯必然）。harness 含巢狀 ul 解析正常；`>` 永不觸及 `li>ul`/`li>p`/`blockquote>p`。 |
| **A3** | Dia/Safari 渲染 `:is()`/`:not()`/`+` | caniuse 既知：`+` universal、`:is()` Safari 14+/Chromium 88+、`:not()` 含選擇器列表 Safari 14+；Dia＝近期 Chromium | 🟢 **支援**（compat 充分）。⚠️ 像素級視覺確認列 baron E2E（§7.6）。 |

### §7.3 凍結模型（C2 直接照此落地）

```css
/* ===== 基準流 + 三檔（margin-top 單一節奏來源）===== */
#paper-content > * + *                                     { margin-top: var(--space-4); } /* 基準流：內文↔內文、清單→下段 */
#paper-content > :not(:is(h1,h2,h3,h4)) + :is(h1,h2,h3,h4) { margin-top: var(--space-6); } /* 非標題→標題：區段斷點大留白（保「前面留白不用改」）*/
#paper-content > :is(h1,h2,h3,h4) + *                      { margin-top: var(--space-2); } /* 標題→其內文/子標題：貼緊（含 h→h，取消 FE-RHYTHM-2）*/
#paper-content > p + :is(ul,ol)                            { margin-top: var(--space-1); } /* 標籤段落→清單：最貼（收編 FE-RHYTHM-1）*/

/* ===== 特殊塊：明列 margin-top（須置於 flow 規則「之後」，以 source order 贏同特異度 tie）===== */
#paper-content > .slide-head        { margin-top: var(--space-6); margin-bottom: var(--space-3); } /* 投影片標題塊：保留原 6/3（border/padding 另由既有 .slide-head 規則保留）*/
#paper-content > .paper-header-meta  { margin-top: var(--space-4); } /* 學術扉頁（非首子時）*/
#paper-content > .katex-display      { margin-top: var(--space-2); } /* 顯示式（若為直接子代）*/
#paper-content > .figure             { margin-top: var(--space-4); }
#paper-content > h1:first-child      { margin-top: var(--space-4); } /* 封面標題（:first-child 不被 *+* 命中、顯式保留）*/
```

**Token 凍結**：基準流 `--space-4`(16px)、區段斷點 `--space-6`(24px)、標題後 `--space-2`(8px)、標籤→清單 `--space-1`(4px)。

### §7.4 互斥性 / 特異度 / margin 摺疊 證明（逐 adjacency）

特異度：`>*+*`=(1,0,0)、`:is(h)+*`=(1,0,1)、`:not(:is(h))+:is(h)`=(1,0,2)、`p+:is(ul,ol)`=(1,0,2)、特殊塊 `>.cls`=(1,0,1)。

| adjacency (A→B) | 命中規則 | 結果 | 說明 |
|---|---|---|---|
| p→p | 基準流 | space-4 | 唯一 |
| p→h（區段前） | `:not(h)+:is(h)` (1,0,2) | space-6 | A 非標題 → 命中；勝基準流 |
| h→p（標題後） | `:is(h)+*` (1,0,1) | space-2 | 勝基準流 (1,0,0) |
| **h→h（子標題）** | `:is(h)+*` (1,0,1) | space-2 | A=標題 → `:not(h)+:is(h)` **不命中**（互斥）→ 僅此規則、**無 source-order 依賴** |
| h→ul | `:is(h)+*` | space-2 | 標題擁抱其清單 |
| **p→ul（標籤）** | `p+:is(ul,ol)` (1,0,2) | space-1 | 勝基準流；B 非標題→不中標題規則 |
| ul→p（清單後） | 基準流 | space-4 | 群組間留白 |
| ul→h | `:not(h)+:is(h)` (1,0,2) | space-6 | 清單後新區段、大留白 |
| 首子 h1 | `h1:first-child` | space-4 | `*+*` 不命中（無前兄弟） |

> **核心互斥**：任一對 (A,B)——A 為標題 → 只走 `:is(h)+*`；A 非標題且 B 標題 → 只走 `:not(:is(h))+:is(h)`；二者**結構互斥、不依賴 source order**。特殊塊 (1,0,1) 與 `:is(h)+*` (1,0,1) 同特異度之 tie，靠**特殊塊規則置於 flow 之後**解（C2 落地須遵守此順序）。
> **margin 摺疊**：塊級 margin-bottom 經主題清理後＝0（L83 reset），margin-top 為單一來源;唯 `.slide-head` 保留 margin-bottom space-3，與下個塊之 flow margin-top space-4 **正常摺疊取大者 space-4**（不疊加、不破版）。

### §7.5 `:has()` 完全消滅 結論
🟢 **確認可完全消滅**。FE-RHYTHM-1 用 `p:has(+ul)` 係因 margin-**bottom** 制需看「下一個」兄弟；改 margin-**top** 制後，清單看「上一個」兄弟＝`p + :is(ul,ol)` 相鄰選擇器，**不需 `:has`**。凍結模型 `:has` 計數＝0（harness 自檢實證）。FE-RHYTHM-1 之 2 條 `:has` 為閱讀視圖節奏唯一 `:has` 用途、C2 移除後此用途歸零（其餘 index.html 若有非節奏 `:has` 不在本任務範圍）。

### §7.6 ⚠️ baron 視覺 E2E（C3 收官前、非本階段、headless 無法替代）
重建 §7.3 harness（或上線 C2 後）於 **Dia + Safari × 四主題** 肉眼確認：① 標題貼其內文/子標題、區段標題前留白足 ② 標籤段落貼清單、清單後留白 ③ 論文連續 h2→h3 貼緊、巢狀清單未被撐開 ④ 簡報施肥頁（p→list）與引擎頁（h→h）節奏一致 ⑤ `.slide-head`/`.katex-display` 無雙重間距 ⑥ chat（`.msg-ai`）不受影響。

## §8 baron 執行命令

```bash
# 1. 本階段無 production 檔案變動，無備份檔

# 2. git add 清單（本階段無 production 改動；報告暫存 baton/、不入 Git）
#    → add 清單為空（提示詞歸檔 / TODO / INDEX 之入庫時機由 baron 決定，C1 採空提交留審計節點）

# 3. commit message 草稿（已寫入 tmp/FE-RHYTHM-UNIFY_C1_msg.txt；簽名已更正為當前模型）
mkdir -p tmp
cat > tmp/FE-RHYTHM-UNIFY_C1_msg.txt << 'EOF'
FE-Refactor: FE-RHYTHM-UNIFY C1 — Spike & 模型凍結（垂直節奏 spike）

本 Commit 為純 Spike 與模型凍結，無 production 代碼修改。
碼審確認 #paper-content 直接子代假設成立（innerHTML=marked 輸出、normalizeAcademicHeader 不重構頂層）；
最小 HTML harness 驗 margin-top flow 模型 + 巢狀清單不被 >*+* 誤撐；
逐 adjacency 證明「:not(h)+:is(h)」與「:is(h)+*」結構互斥、不依賴 source order；
凍結節奏 token（基準流 4 / 區段斷點 6 / 標題後 2 / 標籤→清單 1）與特殊塊 margin-top 明列清單，
確認 margin-top 制完全消滅 :has()（清單改看上一個兄弟＝相鄰選擇器）。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行（空提交以留下驗證審計節點）
git commit --allow-empty -F tmp/FE-RHYTHM-UNIFY_C1_msg.txt
```

> 簽名更正：提示詞原給 `Claude Sonnet 4.6 <noreply@anthreply.com>`（型號與網域皆誤）→ 已更正為當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。

## §9 回退方式（Rollback）
本階段無 production 變更，無需回退；空提交如需撤除：`git reset --soft HEAD~1`。

---

### 結論
🟢 三假設全成立、模型凍結、`:has` 可消滅。**C2 可照 §7.3 凍結模型直接落地**（特殊塊規則須置於 flow 規則之後）。像素級視覺確認為 baron C3 前 E2E。
