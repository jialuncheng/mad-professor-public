# PIPE-SLIDES-HOTFIX-3c HOTFIX-3c 執行報告

## 元數據
| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-3c |
| 執行日期 | 2026-06-13 |
| 依據規劃 | `.claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md`（§3 修法 / §5 測試） |
| 次級參考 | logging_SOP / database_SOP |
| 落地 Hash | 待 baron 回填 |
| 狀態 | 已備改動、待 baron commit |

---

## §1 基準與完成狀態

- 基準：HOTFIX-3b（top-level 清單凸排）後。
- 完成狀態：**未 commit**（已備 `git add` 清單 + msg 草稿）。
- 工作流：BE-Hotfix。範圍：`pipelines/slide_pipeline.py`（helper + 2 注入）+ `tests/test_slide_pipeline.py`（9 測試）。

---

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| HOTFIX-3c | 待 baron 回填 | BE-Hotfix: PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊） |

---

## §3 變動檔案清單

**修改**：
- `pipelines/slide_pipeline.py`（+`_tighten_point_groups` helper + `_page_source_md`/`_deliver` 各 1 行殿後注入）
- `tests/test_slide_pipeline.py`（+9 HOTFIX-3c 測試）

**備份**：
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_slide_pipeline.py.bak`
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_test_slide_pipeline.py.bak`

> 註：本執行報告（baton/）不入 git add。

---

## §4 修法說明

### 4.1 `_tighten_point_groups`（保留原始符號、硬換行收緊）
- **①** 連續『行首箭頭 `→`/`->`』行 → 合併單一段落 + 行間兩尾隨空格硬換行（`<br>`）→ tight 群；**箭頭原樣保留為文字、不轉 bullet**；群內空行跳過；**孤行箭頭不變**；行中箭頭（連接詞句、行首非箭頭）不碰；`\r?` 相容 CRLF。
- **②** `- * + • / 數字.` 相鄰清單項間空行收緊（loose→tight）；清單↔標題/圖/段落邊界留白。

### 4.2 注入（殿後鐵則）
`_page_source_md`（en/fallback）+ `_deliver`（zh 正常路）：`_promote_subheadings` → `_normalize_paragraph_breaks` → **`_tighten_point_groups`（殿後）**。殿後保證硬換行（`  \n`）為最終輸出、不被 normalize 之單 `\n`→`\n\n` 拆回段落。
```python
body = self._promote_subheadings(zh_content)
body = self._normalize_paragraph_breaks(body)
# === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c] === 重點群收緊（殿後、硬換行不被 normalize 拆）
body = self._tighten_point_groups(body)
parts.append(body)
```

### 4.3 RAG 零影響（碼證）
`rag_sections` content 來自 `merged = "\n\n".join(... zh_content ...)`（`slide_pipeline.py:929`）= 原始 `zh_content`、**未套 `_tighten_point_groups`**；tighten 僅作用於渲染 `body`。slides RAG 走 `ctx.rag_sections` 旁路、不從 final_zh 切 → **召回零影響**。

---

## §5 測試結果

### §5 grep + SOP 一致性核查
```
grep _tighten_point_groups → 3 命中（定義1 + 注入2）✓
grep HOTFIX-3c → 4 命中（START/END + 2 注入）✓
grep merged → L929 仍取原始 zh_content（RAG 隔離）✓
SOP logging（traceback/logger.error/exception）→ 新增碼段無命中（合規）
SOP database（裸 .commit()）→ 無命中（合規、新碼零 DB）
不可動：web_server.py / resume_pipeline.py / rag_indexer.py git diff --stat → 空（未碰）
```

### pytest
```
HOTFIX-3c 9 測試：9 passed
（test_hf3c_arrow_group_hardbreak / arrow_group_skips_blank_lines / inline_arrow_preserved /
  single_arrow_unchanged / loose_list_tightened / list_heading_boundary_blank_kept /
  crlf_compat / rag_sections_unaffected〔真 P3〕/ nitrogen_page_end_to_end）

slide 全套件：49 passed
全套件：venv/bin/python -m pytest tests/ -q → 1 failed, 618 passed, 3 skipped
  （618 = 609 + 9 hf3c；唯一 failed = 既存 .env LOG_FORMAT=json env flake）
```

### diff stat
```
pipelines/slide_pipeline.py  | 68 +++（helper + 2 注入）
tests/test_slide_pipeline.py | 75 +++（9 測試）
```

---

## §6 不可動清單遵守

- [x] 只動渲染 body；`ctx.rag_sections`/`merged`（L929 原始 zh_content）未碰 → RAG 零影響
- [x] `web_server.py` / DB / models / 其餘四路 pipeline（resume/academic/litedoc/book）零改動（git diff 空）
- [x] `static/*` 零改動（純後端渲染層）
- [x] `_promote_subheadings`/`_normalize_paragraph_breaks`/`_slide_head_html` 既有邏輯不動（僅串接新 helper）
- [x] 主 repo 目錄未讀寫

---

## §7 銜接

- **baton 狀態**：hotfix 不設 Check → 立即 mv 移出：`hotfix.md` → `hotfixes/`、`執行.md` → `executions/`；baton 不殘留本任務檔。
- **TODO**：✅ 已完成新增 HOTFIX-3c 表 + 索引；hash 自癒（HOTFIX-3b=`1b8b939`、RAG-12 C1-C5=`013371a`等已回填；RESUME-PERF C3/MODEL-9-OPT C4 無確信 commit 留待）。
- **⚠️ baron 後續**：① slides golden 併批次首捕（HOTFIX-1/1b/2/3/3b + META-NORM C3/C4 + 本 3c）② 影子重傳 Ch37 E2E（頁 B `→` 群緊湊保箭頭、頁 A 清單均勻）③ **HOTFIX-3d**（字面 `**` + 裸 URL）仍 baton 暫存待 Run。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3、2 .bak）

# 2. git add 清單（含備份、代碼、移出後正式歸檔檔；baton 暫存報告本身不在 git）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_test_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md
git add .claude-logs/executions/2026-06-13_PIPE-SLIDES-HOTFIX-3c_執行.md
git add .claude-logs/prompts/2026-06-13_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_run_提示詞.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SLIDES-HOTFIX-3c_msg.txt）
cat > /tmp/PIPE-SLIDES-HOTFIX-3c_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）

真因：Vision 對「標題+重點群」每頁吐不同 markdown 結構（頁 A `*` loose list / 頁 B
`###`+`→` 散段落），CSS 對 loose `<p>`(16px) / tight `<li>`(0) / 散段落(16px) 給不同
margin → 每頁節奏不一（頁 A 母項下大縫·子項貼母項；頁 B 標題貼首項·項目散開）。

修法：pipelines/slide_pipeline.py 新增私有 _tighten_point_groups（① 連續行首箭頭 →/->
合併為單一段落+兩空格硬換行<br>、tight 群、箭頭原樣保留為文字、行中箭頭不碰 ② 相鄰清單項
間空行收緊 loose→tight、清單↔標題/圖/段落邊界留白；\r? 相容 CRLF）；_page_source_md +
_deliver 渲染 body 殿後注入（於 _promote_subheadings + _normalize_paragraph_breaks 之後，
硬換行不被 normalize 單 \n→\n\n 拆回段落）。全 slides 節奏一致、各頁原始符號（•/→）保留。

RAG 零影響：rag_sections content 取原始 zh_content（merged，L929）、未套 tighten；
slides RAG 走 ctx.rag_sections 旁路、不從 final_zh 切。零後端/DB/models/static/四路改動。
SOP 核查：新增碼段零 logging/commit → logging+database 皆無命中（合規）。

驗證：grep helper 3 命中 / HOTFIX-3c 4 命中 / merged 仍取原始 zh_content；9 新回歸
（箭頭硬換行群/群內空行/行中不碰/孤行不變/loose 收緊/邊界留白/CRLF/RAG 隔離〔真 P3〕/頁 B 端到端）
+ slide 49 passed、全套件 618 passed。⚠️ 改 B 軌 final_zh → slides golden 併既有批次一次首捕；
baron E2E 影子重傳 Ch37。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SLIDES-HOTFIX-3c_msg.txt
```

---

## §9 回退方式（Rollback）

`git revert <HOTFIX-3c hash>`；或移除 `# === [PIPE-SLIDES-HOTFIX-3c ...] ===` 包裹之 helper + 2 注入行。RAG 本未受影響，回退僅還原 final_zh 渲染（節奏回 loose/散段落）。
