# FE-RHYTHM-UNIFY C2 — 統一垂直節奏模型落地（atomic）執行報告

> 階段 4 執行報告（C2）。依 `tasks.md §8 C2` + C1 凍結模型（§7.3）原子落地。
> **單一 commit 原子替換**：index.html 加統一模型 + 移除 FE-RHYTHM-1 + 4 主題清理垂直 margin。

---

## §1 基準與完成狀態

- **基準**：C1 Spike 後（凍結模型已定）；`gemini-refactor`、worktree `hopeful-yalow-902c50`。
- **完成狀態**：C2 代碼已落地、grep + pytest 驗收通過。**尚未 commit**（baron 手動，§8）。

## §2 落地 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C2 | （待 baron 回填）| FE-Refactor: FE-RHYTHM-UNIFY C2 — 統一垂直節奏模型落地（atomic 模型替換）|

## §3 diff stat

```
 static/index.html             | 41 +++++++++++++++++++++++++++--------------
 static/themes/kahn.css        |  8 ++++----
 static/themes/kandinsky.css   |  8 ++++----
 static/themes/mies.css        |  8 ++++----
 static/themes/nara.css        |  8 ++++----
（5 production 檔；另 TODO/INDEX 狀態檔、baton 報告不入本 commit；.gitignore 為 session 前既有 M、不納入）
```
**備份（5 份、納入 C2 git add）**：`.claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_{index.html,kahn.css,kandinsky.css,mies.css,nara.css}.bak`

## §4 真因（對應 plan）

閱讀視圖垂直節奏由逐交界 bespoke 規則治理（主題 p/h margin + L83 reset 歸零清單 margin + FE-RHYTHM-1 補 p↔list…），根因＝**margin-bottom-only + 清單 margin 歸零** → 節奏不對稱、打地鼠 + 同視覺兩機制。C2 以單一 margin-top flow 模型根治。

## §5 修法

### §5.1 `static/index.html`（base、`=== [FE-RHYTHM-UNIFY C2 START/END] ===` 包裹）
- **移除** FE-RHYTHM-1 兩條 `:has`（`p:has(+ul/ol){margin-bottom:space-1}` + `ul/ol:has(+p){margin-bottom:space-4}`，連註解整塊）。
- **新增** 統一模型 4 條 flow（C1 §7.3 凍結）：
  - `#paper-content > * + * { margin-top: var(--space-4); }`（基準流）
  - `#paper-content > :not(:is(h1,h2,h3,h4)) + :is(h1,h2,h3,h4) { margin-top: var(--space-6); }`（非標題→標題·區段斷點）
  - `#paper-content > :is(h1,h2,h3,h4) + * { margin-top: var(--space-2); }`（標題→其內文/子標題·含 h→h，取代擬議 FE-RHYTHM-2）
  - `#paper-content > p + :is(ul,ol) { margin-top: var(--space-1); }`（標籤段落→清單·收編 FE-RHYTHM-1）
- **特殊塊 margin-top 明列**（置於 flow 後、贏同特異度 tie、防 flow 覆寫原間距）：`.slide-head`(space-6)、`.paper-header-meta`(space-4)、`.katex-display`(space-2)、`.figure`(space-4)。`h1:first-child` 由既有 `#paper-content > h1:first-child` 規則處理（`:first-child` 永不被 `*+*` 命中、不重列）。

### §5.2 4 主題（`kahn`/`kandinsky`/`mies`/`nara`，各 `/* FE-RHYTHM-UNIFY：垂直 margin 移交 base */` 標記）
- 各移除 `#paper-content` 之 **p（margin-bottom）/ h1（margin-bottom）/ h2（margin、保 border-bottom+padding-bottom）/ h3（margin）** 四條垂直 margin 宣告（替換為標記註解）。
- **保留** 色票 / 字族 / 字級 / font-weight / line-height / letter-spacing / border-bottom / padding-bottom。

### §5.3 原子性（Q-A baron 定案）
模型替換 + 主題清理同一 commit：避免「base flow + 主題 margin-bottom 並存＝雙倍」或「主題清完 base 未加＝零間距」之破中間態；`git revert C2` 一步乾淨還原 5 檔。

## §6 不可動清單遵守狀態

- [x] **後端 / pipeline / RAG / final_zh / *.py**：零碰（`git diff --name-only | grep .py` 空、零 .py diff）。
- [x] **內容正規化層（3c/3d/promote）**：未動。
- [x] **HOTFIX-3b 清單 padding-left / HOTFIX-3 .slide-head border / RAG-12 katex overflow-padding**：非間距屬性保留。
- [x] **主題色票/字族/字級/border/padding-bottom**：保留（僅移垂直 margin）。
- [x] **chat `.msg-ai`**：未碰（diff 僅 index.html + 4 themes）。
- [x] **`#paper-content{margin:0 auto}` 水平置中**：未碰。
- [x] **主 repo 目錄**：未讀寫。

## §7 端到端驗證計畫結果

### §7.1 SOP 一致性核查（FE-Refactor·純 CSS 零 .py）
- logging：`grep -n "logger.error|traceback.format_exc|logger.exception"` 於本次改檔 → **無命中（合規、純 CSS 無 logging）**。
- database：`grep -nE "\.commit\(\)"` 於本次改檔 → **無命中（合規、純 CSS 無 DB）**。

### §7.2 grep 核查（tasks §6.2）
```
(1) 舊節奏 :has 規則  grep ":has(\+ (ul|ol|p))" → 0 命中（淨空）✓
(2) 統一模型 4 條     L917/920/923/926 命中 ✓；START/END 包裹 L910/936 ✓
(3) :has() 選擇器     實際 0（grep ":has(" 唯一命中為 C2 註解文字「完全消滅 :has()」、非選擇器）✓
(4) #paper-content >  10 條（4 flow + 4 特殊塊 + 既有 h1:first-child + 1 既有）✓
(5) 四主題真 margin 宣告殘留  kahn/kandinsky/mies/nara 各 0 ✓；h2 border-bottom 保留 ✓；FE-RHYTHM-UNIFY 標記各 4 ✓
(6) diff 範圍         僅 index.html + 4 themes（+ 狀態檔 TODO/INDEX、非 production）✓
```

### §7.3 全套件 pytest
```
1 failed, 631 passed, 3 skipped
```
- **631 passed = 基線維持**（FE-RHYTHM-1/HOTFIX-4 同基線）。
- 唯一 failed＝`test_logging_config.py::test_settings_log_format_default_auto`——**既有 `.env LOG_FORMAT=json` env flake**（`.env` 設 `LOG_FORMAT=json`、測試斷言預設 `auto`；TODO 多次記載）；**與本次純 CSS 變更零關係（零 .py diff 實證）**。

### §7.4 ⚠️ baron 視覺 E2E（C3 收官前、headless 無法替代）
**Dia + Safari × 四主題（kahn/mies/kandinsky/nara）× 三軌**：
- **履歷**：小標→條列貼緊、條列→下個小標留白；巢狀條列未過撐。
- **論文（2601/byz）**：段落↔清單交界、**連續標題 h2→h3 貼緊**（引擎頁類）、清單接章節留白、巢狀清單未誤撐、`.katex-display` 間距正常。
- **簡報（Ch37）**：施肥頁（p→list）+ 引擎頁（h→h）**節奏一致**；`.slide-head` 標題塊無雙重間距；圖↔內文間距。
- **chat**：AI 回答清單/段落節奏**不受影響**（`.msg-ai` 未波及）。
- 無 golden 重捕（純 CSS、final_zh byte 不變、RAG 不動）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3，5 份）

# 2. git add（5 production + 5 .bak；報告暫存 baton/ 不 add；.gitignore 為既有 M、不納入）
git add static/index.html static/themes/kahn.css static/themes/kandinsky.css static/themes/mies.css static/themes/nara.css
git add .claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_index.html.bak
git add .claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_kahn.css.bak
git add .claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_kandinsky.css.bak
git add .claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_mies.css.bak
git add .claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_nara.css.bak

# 3. commit message 草稿（已寫入 tmp/FE-RHYTHM-UNIFY_C2_msg.txt；簽名已更正為當前模型）
mkdir -p tmp
cat > tmp/FE-RHYTHM-UNIFY_C2_msg.txt << 'EOF'
FE-Refactor: FE-RHYTHM-UNIFY C2 — 統一垂直節奏模型落地（atomic 模型替換）

修法：
1. static/index.html (base)：移除 FE-RHYTHM-1 兩條 :has 舊規則；新增統一 margin-top flow 模型 4 條
   （基準流 > * + *、非標題→標題 > :not(h)+h 區段斷點、標題→* > h+* 貼緊〔含 h→h，取代擬議 FE-RHYTHM-2〕、
   p + ul/ol 標籤→清單最貼）；依 C1 凍結 token（4/6/2/1）+ 特殊塊 margin-top 明列
   （.slide-head/.paper-header-meta/.katex-display/.figure、置 flow 後贏 tie 防覆寫）。
2. 4 主題 (kahn/kandinsky/mies/nara)：移除 #paper-content p/h1/h2/h3 垂直 margin（移交 base），
   保留色票/字族/字級/border/padding-bottom。

優勢：margin-top 單向 flow 模型完全消滅 :has() 選擇器（清單改看上一個兄弟＝相鄰選擇器、相容 Safari 14+）；
單一節奏來源、根治「margin-bottom-only + 清單 margin 歸零」之前寬後窄黑洞 + 同視覺兩機制。
原子性：單 commit 同步替換模型 + 主題清理，避開雙重疊加 / 零間距黏字之破損中間態，git revert C2 一步可逆。

SOP 核查：純 CSS 重構、零後端/DB/.py 異動，logging + database 核查皆無命中（合規）。
驗證：grep 舊 :has 0 / 模型 4 條命中 / :has() 選擇器 0 / 四主題垂直 margin 0 殘留；全套件 631 passed（基線維持，唯一 fail 為既有 .env LOG_FORMAT env flake、與 CSS 無關）。
E2E 三軌（履歷/論文/簡報）× 四主題 + chat 不受影響，列 baron 收官前手動驗證。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F tmp/FE-RHYTHM-UNIFY_C2_msg.txt
```

> 簽名更正：提示詞原給 `Claude Sonnet 4.6 <noreply@anthreply.com>`（型號+網域皆誤）→ 已更正為當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。

## §9 回退方式（Rollback）

`git revert <C2-hash>` 一步乾淨還原 5 檔（atomic）；或從 `.claude-logs/archive/2026-06-13_FE-RHYTHM-UNIFY_C2_*.bak` 還原。回退後恢復 FE-RHYTHM-1 + 主題 margin 並存之原狀。

---

### 結論
🟢 統一模型落地、舊 FE-RHYTHM-1 淨空、`:has()` 選擇器 0、4 主題垂直 margin 移交 base、631 passed 基線維持、零 .py diff。**像素級視覺確認為 baron C3 前 E2E（三軌×四主題）**。
