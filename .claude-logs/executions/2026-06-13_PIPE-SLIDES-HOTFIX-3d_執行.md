# PIPE-SLIDES-HOTFIX-3d HOTFIX-3d 執行報告

## 元數據
| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-3d |
| 執行日期 | 2026-06-13 |
| 依據規劃 | `.claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md`（§3 修法 / §5 測試） |
| 次級參考 | logging_SOP / database_SOP |
| 落地 Hash | 待 baron 回填 |
| 狀態 | 已備改動、待 baron commit |

---

## §1 基準與完成狀態

- 基準：HOTFIX-3c（標題+重點節奏正規化）後。
- 完成狀態：**未 commit**（已備 `git add` 清單 + msg 草稿）。
- 工作流：BE-Hotfix。範圍：`pipelines/slide_pipeline.py`（2 helper + 2 注入）+ `tests/test_slide_pipeline.py`（9 測試）。

---

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| HOTFIX-3d | 待 baron 回填 | BE-Hotfix: PIPE-SLIDES-HOTFIX-3d — 字面 ** 未粗體 + 裸 URL 破版（slide 渲染層清洗） |

---

## §3 變動檔案清單

**修改**：
- `pipelines/slide_pipeline.py`（+`_render_inline_bold` + `_strip_bare_url_lines` + `_page_source_md`/`_deliver` 各 2 行注入）
- `tests/test_slide_pipeline.py`（+9 HOTFIX-3d 測試）

**備份**：
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_slide_pipeline.py.bak`
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_test_slide_pipeline.py.bak`

> 註：本執行報告（baton/）不入 git add。

---

## §4 修法說明

### 4.1 `_render_inline_bold`（繞 CommonMark CJK emphasis）
`re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)`——行內 `**X**`→raw `<strong>`。marked 9.x 不 sanitize 原樣輸出 → 不論 CJK 緊貼皆正確粗體。於 `_promote_subheadings` 後跑（整行 `**X**` 已升 `###`、此處只剩行內 span）；落單 `**` 保留。

### 4.2 `_strip_bare_url_lines`（剝整行裸 URL）
`url_line = ^\s*<?https?://\S+>?\s*\r?$`——僅剝「整行純 URL」；**行內 URL（同行有字）+ `![](images/…)` 圖片行（非 http 開頭）保留**。

### 4.3 注入（promote 後、normalize 前）
`_page_source_md` + `_deliver`：`_promote_subheadings` → **`_render_inline_bold` → `_strip_bare_url_lines`** → `_normalize_paragraph_breaks` → `_tighten_point_groups`(3c)。
```python
body = self._promote_subheadings(zh_content)
# === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d] === 行內粗體轉 <strong> + 剝除整行裸 URL
body = self._render_inline_bold(body)
body = self._strip_bare_url_lines(body)
body = self._normalize_paragraph_breaks(body)
body = self._tighten_point_groups(body)
```

### 4.4 RAG 零影響（碼證）
`rag_sections` content＝`merged`（`slide_pipeline.py:962`）= 原始 `zh_content`、未套 3d（仍含 `**` 與 URL）；3d 僅作用渲染 `body`。slides RAG 走 `ctx.rag_sections` 旁路、不從 final_zh 切 → **召回零影響**。

---

## §5 測試結果

### §5 grep + SOP
```
grep _render_inline_bold + _strip_bare_url_lines → 6 命中（2 定義 + 4 注入）✓
grep HOTFIX-3d → 4 命中（START/END + 2 注入）✓
grep merged → L962 仍取原始 zh_content（RAG 隔離）✓
SOP logging → 新增碼段無命中（合規）；SOP database 裸 commit → 無命中（合規、零 DB）
不可動：web_server.py / resume_pipeline.py git diff --stat → 空（未碰）
```

### 端到端（真實 marked@9.1.6、worktree 外 spike、已清）
```
① CJK 緊貼 **「根際細菌 **互利共生 (X)**中」→ <strong>互利共生 (X)</strong>中、無字面 **：true
② 整行裸 URL（biorender）剝除：true
③ ![](images/page-1.jpg) 圖片行保留：true
④ 行內 URL「見 https://a.com 說明」保留：true
```

### pytest
```
HOTFIX-3d 9 測試：9 passed
（inline_bold_to_strong / inline_bold_cjk_adjacent / lone_asterisks_preserved /
  whole_line_bold_still_heading / strip_bare_url_line / inline_url_preserved /
  image_line_preserved / rag_sections_unaffected〔真 P3〕/ rhizosphere_end_to_end）

slide 全套件：58 passed
全套件：venv/bin/python -m pytest tests/ -q → 1 failed, 627 passed, 3 skipped
  （627 = 618 + 9 hf3d；唯一 failed = 既存 .env LOG_FORMAT=json env flake）
```

---

## §6 不可動清單遵守

- [x] 只動渲染 body；`ctx.rag_sections`/`merged`（L962 原始 zh_content）未碰 → RAG 零影響
- [x] `web_server.py` / DB / models / 四路 pipeline 零改動（git diff 空）
- [x] `static/*` 零改動（純後端渲染層）
- [x] 保留 `![](images/…)` 圖片行 + 行內 URL（測試證）
- [x] `_promote_subheadings`/`_normalize_paragraph_breaks`/`_tighten_point_groups` 既有邏輯不動（僅串接新 helper）
- [x] 主 repo 目錄未讀寫

---

## §7 銜接

- **baton 狀態**：hotfix 不設 Check → 立即 mv 移出：`hotfix.md` → `hotfixes/`、`執行.md` → `executions/`；baton 不殘留本任務檔。
- **TODO**：✅ 已完成新增 HOTFIX-3d 表 + 索引；hash 自癒（HOTFIX-3b=`1b8b939`、RAG-12 C1-C5 已回填；RESUME-PERF C3/MODEL-9-OPT C4 無確信 commit 留待）。
- **⚠️ baron 後續**：① slides golden 併批次首捕（HOTFIX-1/1b/2/3/3b/3c + META-NORM C3/C4 + 本 3d）② 影子重傳 Ch37 E2E（p27 粗體無字面 `**`、無 biorender 裸連結）。
- **PIPE-SLIDES slide 排版修補系列完結**：3/3b（CSS）+ 3c（節奏）+ 3d（清洗）全落地。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3、2 .bak）

# 2. git add 清單（含備份、代碼、移出後正式歸檔檔；baton 暫存報告本身不在 git）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_test_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md
git add .claude-logs/executions/2026-06-13_PIPE-SLIDES-HOTFIX-3d_執行.md
git add .claude-logs/prompts/2026-06-13_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_run_提示詞.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SLIDES-HOTFIX-3d_msg.txt）
cat > /tmp/PIPE-SLIDES-HOTFIX-3d_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-3d — 字面 ** 未粗體 + 裸 URL 破版（slide 渲染層清洗）

真因（B 軌 vs 原稿 Ch37 比對、原稿無 B 軌引入）：
A 字面 **：CommonMark 右側界定符規則下，閉合 ** 前接全形標點、後接中文字（非空白非
標點）→ 不認 closer → 字面星號（p27 根圈）。原稿英文 **bold** 後接空白故無症、翻中後
CJK 緊貼 ** 才觸發。
B 裸 URL：投影片來源/縮圖網址被 Vision 轉錄成整行裸連結，gfm 自動連結 + 超長無斷點
→ 撐破 #paper-content（p6/p18/p27/p35）。

修法：pipelines/slide_pipeline.py 新增 _render_inline_bold（行內 **X**→<strong>X</strong>、
raw HTML 繞過 CommonMark CJK emphasis、marked 不 sanitize 原樣輸出）+ _strip_bare_url_lines
（剝除整行純 URL、行內 URL 與 ![](images/…) 圖片行保留）；_page_source_md + _deliver
於 _promote_subheadings 後注入（promote→inline_bold→strip_url→normalize→tighten[3c]）。

RAG 零影響：rag_sections content 取原始 zh_content（merged，L962）、未套 3d；slides RAG
走 ctx.rag_sections 旁路、不從 final_zh 切。零後端/DB/models/static/四路改動。
SOP 核查：新增碼段零 logging/commit → logging+database 皆無命中（合規）。

驗證：grep helper 6 命中 / HOTFIX-3d 4 命中 / merged 仍取原始 zh_content；9 新回歸
（行內粗體/CJK 緊貼/落單 ** 保留/整行 ** 升標題/剝整行 URL/行內 URL 保留/圖片行保留/
rag_sections 隔離〔真 P3〕/p27 端到端）+ 端到端真 marked 4/4、slide 58 passed、全套件 627 passed。
⚠️ 改 B 軌 final_zh → slides golden 併既有批次一次首捕；baron E2E 影子重傳 Ch37 驗 p27 粗體正常無裸連結。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SLIDES-HOTFIX-3d_msg.txt
```

---

## §9 回退方式（Rollback）

`git revert <HOTFIX-3d hash>`；或移除 `# === [PIPE-SLIDES-HOTFIX-3d ...] ===` 包裹之 2 helper + 各注入 2 行。RAG 未受影響，回退僅還原 final_zh 顯示層（`**` 回字面、URL 回裸連結）。
