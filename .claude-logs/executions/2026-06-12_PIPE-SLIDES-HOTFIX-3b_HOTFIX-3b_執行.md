# PIPE-SLIDES-HOTFIX-3b HOTFIX-3b 執行報告

> 工作流：FE-Hotfix · 依據 `templates/template_execution.md`

---

## §1 基準與完成狀態

- 基準 Commit：`3f26d5c`（PIPE-SLIDES-HOTFIX-3）
- 本次 Commit：`HOTFIX-3b`（**未 commit**，已備好 `git add` 清單 + msg 草稿待 baron 手動執行）
- 改檔範圍：`static/index.html` 單檔單 hunk（base CSS）
- 不動：`.py` / 後端 / `static/themes/*.css` / RAG / pipeline

---

## §2 落地 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| HOTFIX-3b | 待 baron 回填 | FE-Hotfix: PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（HOTFIX-3 二補完） |

---

## §3 diff stat

```
 static/index.html | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)
```

備份：`.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_index.html.bak`（149237 bytes、修改前快照、入 git add 供審計）

---

## §4 真因

`static/index.html:79` 全域 reset：
```css
body, h1, h2, h3, p, ol, ul { margin: 0; padding: 0; }
```
把 top-level `ul/ol` 的 `padding` 歸零 → 預設 `list-style-position: outside` 下 bullet marker 繪於 padding 區（現為 0）外側 → 溢出到 `#paper-content` 左 padding（`var(--space-8)`，kahn.css:126）之內、視覺上比同頁標題更左（凸排）。

HOTFIX-3「二」的 selector 只涵蓋 `ul ul / ol ol / ul ol / ol ul`（巢狀第二層以下），**漏第一層 `#paper-content ul` / `#paper-content ol`** → top-level bullet 仍吃 L79 的 `padding: 0` → 凸排未解。

---

## §5 修法

`static/index.html` HOTFIX-3 既有 CSS 區塊「二」selector 前置一行 top-level `ul/ol`，`padding-left: 1.5em` 沿用、區塊位置與 START/END 包裹不動：

```css
  /* 二：清單縮排（結構性 fallback、主題無關、含自訂主題受益）
     L79 全域 reset 把 ul/ol padding 歸零 → list-style:outside 下 bullet 凸排；
     此處補回 top-level + 巢狀縮排（HOTFIX-3b：補 top-level、原僅巢狀） */
  #paper-content ul, #paper-content ol,
  #paper-content ul ul, #paper-content ol ol,
  #paper-content ul ol, #paper-content ol ul {
    padding-left: 1.5em;
  }
```

實際 git diff（單 hunk）：
```diff
@@ -894,7 +894,10 @@
     margin: 4px 0 0;
     line-height: 1.5;
   }
-  /* 二：巢狀清單縮排（結構性 fallback、主題無關、含自訂主題受益） */
+  /* 二：清單縮排（結構性 fallback、主題無關、含自訂主題受益）
+     L79 全域 reset 把 ul/ol padding 歸零 → list-style:outside 下 bullet 凸排；
+     此處補回 top-level + 巢狀縮排（HOTFIX-3b：補 top-level、原僅巢狀） */
+  #paper-content ul, #paper-content ol,
   #paper-content ul ul, #paper-content ol ol,
   #paper-content ul ol, #paper-content ol ul {
     padding-left: 1.5em;
```

**歸屬（base 不 themes）**：四主題 `#paper-content ul/ol/li` grep 0 命中（縮排現由 base L79 reset 單方決定、themes 無 selector 可改）；縮排=結構歸主檔（`design/docs/principles.md`）；base 一處含自訂上傳主題受益、放 themes 須改 4 檔且自訂主題永遠漏。

---

## §6 不可動清單遵守狀態

- [x] 不動任何 `.py`（`git diff --stat -- '*.py'` 空）
- [x] 不動 `static/themes/*.css`（grep 清單 0 命中、未越界）
- [x] 不動 HOTFIX-3 其餘規則（slide-head / slide-head h2 / slide-sub 三塊 byte 不變）
- [x] 不動 `padding-left: 1.5em` 值與 HOTFIX-3 START/END 包裹
- [x] 不碰 RAG / pipeline / 後端

---

## §7 端到端驗證計畫結果

### 7.1 git status -s（相關）
```
 M static/index.html
?? .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_index.html.bak
```
唯一代碼變動 = `static/index.html`。

### 7.2 靜態 grep（全綠）
```
① grep "#paper-content ul, #paper-content ol,"        → static/index.html:900（1 命中 ✅）
② grep "#paper-content ul ul, #paper-content ol ol,"  → static/index.html:901（1 命中 ✅，巢狀未誤刪）
③ themes 清單命中：kahn 0 / kandinsky 0 / mies 0 / nara 0（皆 0 ✅，未越界）
```

### 7.3 pytest 回歸
```
venv/bin/python -m pytest tests/ -q
→ 1 failed, 605 passed, 3 skipped
```
- **605 passed 與 HOTFIX-3 基線一致**（TODO HOTFIX-3 行載「全套件 605 passed」）。
- 唯一 failed：`tests/test_logging_config.py::test_settings_log_format_default_auto` — **env flake、與本 hotfix 零關聯**：
  - 本 hotfix `git diff --stat -- settings.py utils/logging_config.py tests/test_logging_config.py` 為**空**（零 Python diff，CSS 變動不可能影響 logging）。
  - 真因：測試機 `.env:54 LOG_FORMAT=json` 覆寫預設；測試 `monkeypatch.delenv('LOG_FORMAT')` 後 `importlib.reload(settings)`，settings 經 dotenv 仍讀 `.env` 的 `json` → 斷言 `== "auto"` 失敗。屬既存環境條件、非本次引入。

### 7.4 baron E2E（前端、非 commit）
- 重整 ALi 簡報 reading-view → 第一層 `•` 與標題左緣對齊/內縮、不再凸排。
- 巢狀子項仍正確縮排（HOTFIX-3 二未退化）。
- 四主題（kahn/mies/kandinsky/nara）逐一確認清單縮排一致、無破版。
- 非 slides 文體（論文/履歷）清單顯示正常。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列）：
#    .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_index.html.bak

# 2. git add 清單（含備份、代碼、提示詞、歸檔移動後文件）
git add static/index.html
git add .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_index.html.bak
git add .claude-logs/prompts/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_run_提示詞.md
git add .claude-logs/prompts/2026-06-12_PIPE-SLIDES-HOTFIX-3b_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3b_hotfix.md
git add .claude-logs/executions/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_執行.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SLIDES-HOTFIX-3b_msg.txt）
cat > /tmp/PIPE-SLIDES-HOTFIX-3b_msg.txt << 'EOF'
FE-Hotfix: PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（HOTFIX-3 二補完）

真因：static/index.html:79 全域 reset `ul/ol { padding:0 }` 歸零 top-level 清單縮排，list-style:outside 下第一層 bullet marker 溢出到 #paper-content 左 padding（var(--space-8)）外側→凸排（比同頁標題更左）。HOTFIX-3「二」只補了巢狀（ul ul/ol ol/ul ol/ol ul），漏 top-level `#paper-content ul/ol`。

修法：HOTFIX-3 既有 CSS 區塊「二」selector 前置 `#paper-content ul, #paper-content ol,` 一行、padding-left 沿用 1.5em；含 top-level + 巢狀。不動 themes（四主題 grep 0 命中清單、縮排=結構歸主檔 principles.md、base 一處含自訂上傳主題受益）。

範圍：static/index.html 單檔單 hunk、零 .py、零後端、零 RAG/pipeline。
驗證：grep top-level/巢狀 selector 各 1 命中、themes 仍 0；全套件零 Python diff 維持 605 passed（僅 .env LOG_FORMAT env flake）；baron E2E ALi 簡報第一層 bullet 不凸排 + 四主題一致 + 巢狀未退化。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SLIDES-HOTFIX-3b_msg.txt
```

---

## §9 回退方式（Rollback）

單檔單 hunk：移除新增的 `#paper-content ul, #paper-content ol,` selector 行 + 還原註解；或 `git revert <HOTFIX-3b hash>`。不涉資料/向量/schema，零副作用。
