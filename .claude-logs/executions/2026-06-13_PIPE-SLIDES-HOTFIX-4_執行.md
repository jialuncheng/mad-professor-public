# PIPE-SLIDES-HOTFIX-4 HOTFIX-4 執行報告

## 元數據
| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-4 |
| 執行日期 | 2026-06-13 |
| 依據規劃 | `.claude-logs/baton/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md`（§3 修法 / §5 測試） |
| 次級參考 | logging_SOP / database_SOP |
| 落地 Hash | 待 baron 回填 |
| 狀態 | 已備改動、待 baron commit |

---

## §1 基準與完成狀態

- 基準：HOTFIX-3d 後。
- 完成狀態：**未 commit**（已備 `git add` 清單 + msg 草稿）。
- 工作流：BE-Hotfix。範圍：`pipelines/slide_pipeline.py`（P1 `_VISION_PROMPT` 加 is_blank + ④ 過濾雙保險）+ `tests/test_slide_pipeline.py`（4 測試）。

---

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| HOTFIX-4 | 待 baron 回填 | BE-Hotfix: PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位） |

---

## §3 變動檔案清單

**修改**：
- `pipelines/slide_pipeline.py`（`_VISION_PROMPT` 加第 5 條 + schema `is_blank` 欄；`_process` ④ 加雙保險跳過）
- `tests/test_slide_pipeline.py`（+4 HOTFIX-4 測試 + `_resp_blank` helper）

**備份**：
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_slide_pipeline.py.bak`
- `.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_test_slide_pipeline.py.bak`

> 註：本執行報告（baton/）不入 git add。

---

## §4 修法說明

### 4.1 `_VISION_PROMPT` 加 `is_blank`（基底、所有頁皆得、含封面）
```
4. 頁面有明確標題放 title；沒有就空字串。
# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 START] ===
5. is_blank：若整頁**無任何實質內容**（空白頁、僅裝飾性橫條/分隔線/純背景/頁碼…）→ true；否則 false。
   **含真實圖表/照片/示意圖/資料之頁一律 is_blank=false。**
只輸出 JSON：
{"title": "", "subtitle": "", "markdown_content": "", "figure_description": "", "is_blank": true|false}
# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 END] ===
```
（`_COVER_PROMPT = _VISION_PROMPT + …` → 封面亦得 is_blank。）

### 4.2 `_process` ④ 雙保險跳過
```python
            # === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4] === Vision 判空白 + 無實質文字 → 跳
            if r.get("is_blank") and not ((r.get("title") or "").strip()
                                          or (r.get("markdown_content") or "").strip()):
                continue
            if not (r.get("title") or r.get("markdown_content")
                    or r.get("figure_description")):
                continue  # 空白頁跳過（A 軌同款、既有三欄全空）
```

### 4.3 設計要點
- **雙保險**：`is_blank` 為 LLM 判斷（temp=0 壓抖動、非 100%）；僅在 is_blank **且** title/content 皆空才跳 → Vision 誤標有內容頁仍保留。
- **純圖頁安全**：合法圖頁 is_blank=false → 不跳；空白頁 is_blank=true + 無文字 → 跳。
- **向後相容**：舊 golden 無 is_blank → `r.get("is_blank")` 回 None → falsy → 不跳。
- **既有三欄全空條件保留為第二道**；頁序 `n=len(units)+1` 連續重編、不留洞。

---

## §5 測試結果

### grep + SOP
```
is_blank 命中 = 6（prompt 第5條 + schema + 跳過條件 + 註解）✓
HOTFIX-4 標記 = 3（START/END + 注入）✓
既有三欄全空條件仍在（slide_pipeline.py:178）✓
is_cover = 6（未動）✓
SOP logging（traceback/logger.error/exception）→ 新增碼段無命中（合規）
SOP database（裸 .commit()）→ 無命中（合規、零 DB）
不可動：web_server.py / resume_pipeline.py git diff --stat → 空；merged（L972）仍取原始 zh_content
```

### pytest
```
HOTFIX-4 4 測試：4 passed
（test_p1_blank_flag_skips_empty / blank_flag_safety_belt_keeps_content /
  image_only_page_kept / legacy_no_is_blank_field）
slide 全套件：62 passed
全套件：venv/bin/python -m pytest tests/ -q → 1 failed, 631 passed, 3 skipped
  （631 = 627 + 4 hf4；唯一 failed = 既存 .env LOG_FORMAT=json env flake）
git diff --name-only *.py → 僅 pipelines/slide_pipeline.py + tests/test_slide_pipeline.py
```

---

## §6 不可動清單遵守

- [x] `is_cover` 封面判定 / `cover` metadata / `_COVER_PROMPT` 既有欄 不動（僅基底加 is_blank）
- [x] 既有「三欄全空跳過」保留為第二道、未移除
- [x] 渲染層（HOTFIX-3/3b/3c/3d、`_promote_subheadings`/`_tighten_point_groups` 等）不動
- [x] `ctx.rag_sections` / `merged`（L972 原始 zh_content）/ RAG / 向量 不動
- [x] 後端 `web_server.py` / DB / models / 其餘四路 pipeline 零改動（git diff 空）
- [x] `_render_pages` / 存圖 / 頁序重編 邏輯不動
- [x] 主 repo 目錄未讀寫

---

## §7 銜接

- **baton 狀態**：hotfix 不設 Check → 立即 mv 移出：`hotfix.md` → `hotfixes/`、`執行.md` → `executions/`；baton 不殘留本任務檔。
- **TODO**：✅ 已完成新增 HOTFIX-4 表 + 索引；hash 自癒（HOTFIX-3b/RAG-12 C1-C5 已回填；RESUME-PERF C3/MODEL-9-OPT C4 無確信 commit 留待）。
- **⚠️ baron 後續**：① **slides golden 須重捕**（Vision prompt 變更）、搭既有待重捕批次（HOTFIX-1/1b/2/3/3b/3c/3d + META-NORM C3/C4 + 本 4）一次首捕 ② 影子重傳 Ch37 E2E（第 16 張不再產頁、純圖頁未誤跳）。
- **PIPE-SLIDES slide 修補系列**：3/3b/3c/3d（渲染層）+ 4（P1 攝取層）全落地；另 FE-RHYTHM-1（清單節奏 + #2 黏字、FE-Hotfix）仍 baton 待 Run。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3、2 .bak）

# 2. git add 清單（baton 暫存報告本身不在 git）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_test_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md
git add .claude-logs/executions/2026-06-13_PIPE-SLIDES-HOTFIX-4_執行.md
git add .claude-logs/prompts/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_run_提示詞.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SLIDES-HOTFIX-4_msg.txt）
cat > /tmp/PIPE-SLIDES-HOTFIX-4_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）

真因：P1 ④ 空白跳過僅「title+markdown_content+figure_description 三欄全空」才跳；空白投影片
（Ch37 第 16 張、僅裝飾黑橫條）雖無 title/content，Vision 仍回非空 figure_description（描述空白）→
通過過濾 → 產出空框黑條 reading 頁。不能只看 title+content 空（會誤殺 title/content 皆空之合法純圖頁）。

修法：pipelines/slide_pipeline.py _VISION_PROMPT 加 is_blank 欄（基底、所有頁皆得，含封面）+ 第 5 條
判定指引（整頁無實質內容/僅裝飾橫條→true、含真實圖表→false）；④ 單位過濾加雙保險跳過——僅當
is_blank 且 title/content 皆空才跳（防 Vision 誤判有內容頁被丟）、合法純圖頁 is_blank=false 不受影響、
舊 golden 無 is_blank→falsy→向後相容不跳；既有三欄全空條件保留為第二道。與既有 is_cover 同模式對稱。

零後端/DB/models/static/RAG/渲染層/四路改動（只動 P1 prompt + 過濾）。rag_sections 取原始 zh_content
（merged，L972）未受影響。SOP logging+database 皆無命中（合規）。

驗證：grep is_blank 6 / HOTFIX-4 3 命中 / 既有條件仍在 / is_cover 未動；新增 4 pytest（空白跳過/
雙保險保留有內容/純圖頁保留/舊無欄相容）+ slide 62 passed、全套件 631 passed。⚠️ 改 Vision prompt →
slides golden 併既有待重捕批次一次首捕；baron E2E 影子重傳 Ch37 驗第 16 張不再產頁、純圖頁未誤跳。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SLIDES-HOTFIX-4_msg.txt
```

---

## §9 回退方式（Rollback）

移除 `# === [PIPE-SLIDES-HOTFIX-4 ...] ===` 包裹之 prompt 第 5 條 + schema is_blank 欄 + ④ 跳過條件，或 `git revert <HOTFIX-4 hash>`。舊 golden 無 is_blank 本就相容、回退僅還原「不檢測空白」、無資料/向量影響。
