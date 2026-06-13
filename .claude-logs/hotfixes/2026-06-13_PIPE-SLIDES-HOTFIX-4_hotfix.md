# PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）

> 工作流：**BE-Hotfix**（動 `pipelines/slide_pipeline.py` P1 Vision prompt + 單位過濾、零後端 API/DB）
> 依據：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md §1.5 + §5` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.3/§4.4`
> 必讀 SOP：`sop/2026-05-23_logging_SOP_手冊.md` + `sop/2026-05-23_database_SOP_手冊.md`（本修零 logging/db 變更，§5 核查見 §7.5）
> 代號：`PIPE-SLIDES-HOTFIX-4`（slide 系列；3/3b/3c/3d 為渲染層、**4 為 P1 攝取層**）

---

## 1. 基準與完成狀態

- 基準 Commit：`HOTFIX-3d`（slide 渲染層清洗）後。
- 完成狀態：**未 commit**（baton 暫存、待 baron 過目 → Run）。
- 改檔範圍：`pipelines/slide_pipeline.py`（`_VISION_PROMPT` 加 `is_blank` 欄 + 單位過濾雙保險）+ `tests/test_slide_pipeline.py`（測試）。
- 不動：後端 API / DB / RAG / `ctx.rag_sections` / `is_cover` 封面邏輯 / 渲染層（3/3b/3c/3d）/ 其餘四路。

---

## 2. 真因（Root Cause）

### 2.1 症狀
baron 比對原稿 `Ch37_Plant-Nutrition.pdf`，**第 16 張為空白投影片（僅底部一條裝飾黑橫條、無任何標題/正文/有意義圖表）**；B 軌 reading view 仍為它**產出一頁**（空框 + 黑條 + 一句描述），體驗破碎。

### 2.2 現有空白跳過為何漏網（grep 實證）
`pipelines/slide_pipeline.py:161-168`：
```python
# ④ 空白單位跳過 + 存圖（僅保留單位、檔名=頁序）
units = []
for img, r in zip(page_images, results):
    if not r:
        continue
    if not (r.get("title") or r.get("markdown_content")
            or r.get("figure_description")):
        continue  # 空白頁跳過（A 軌同款）
```
→ **僅在 `title` + `markdown_content` + `figure_description` 三欄全空時才跳。**

空白頁雖無 title/content，但 **Vision 對它回了非空的 `figure_description`**——它「描述了那張空白/黑條」（如「一張幾乎空白的投影片、底部有黑色橫條」）→ `figure_description` 非空 → **通過過濾 → 產出空頁**。

### 2.3 為何不能只看「title+content 空」就跳
會**誤殺合法純圖頁**：架構圖/照片/示意圖頁常 `title`+`content` 皆空、僅 `figure_description` 載真實圖說——與空白頁**欄位形狀相同**（title+content 空、figure_description 非空），差別只在 figure_description 的**語意**（真圖 vs 描述虛無）。純欄位空判定分不出。

### 2.4 解法（baron 拍板：A）
**Vision `is_blank` 旗標**——Vision 看得到該頁渲染圖、最有資格判「整頁無實質內容」；與既有 `is_cover`（封面判定旗標）**同模式對稱**。跳過 `is_blank` 之單位。
- **否決 B**（figure_description 關鍵詞啟發式）：脆、看 Vision 措辭、「黑色長條圖」類誤殺、語言相依。
- **否決 C**（像素門檻）：難調、純白少字頁誤殺。

---

## 3. 修法（程式碼）

### 3.1 `_VISION_PROMPT` 加 `is_blank` 欄（基底、所有頁皆得；含封面，因 `_COVER_PROMPT = _VISION_PROMPT + …`）

```python
_VISION_PROMPT = """你是簡報忠實轉錄器。請將這一頁簡報的內容忠實轉錄為 JSON，嚴格遵守：
1. 嚴禁重組、摘要、補完或改寫——只忠實轉錄頁面上實際出現的文字與結構。
2. markdown_content 用 markdown 保留階層/條列/表格；表格儲存格（cell）內嚴禁使用 ### 等標題語法。
3. 圖表/示意圖/照片：用一兩句話描述放 figure_description 欄，嚴禁混入 markdown_content。
4. 頁面有明確標題放 title；沒有就空字串。
# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 START] ===
5. is_blank：若整頁**無任何實質內容**（空白頁、僅裝飾性橫條/分隔線/純背景/頁碼、無標題無正文
   無有意義圖表）→ is_blank=true；否則 false。**含真實圖表/照片/示意圖/資料之頁一律 is_blank=false。**
只輸出 JSON：
{"title": "", "subtitle": "", "markdown_content": "", "figure_description": "", "is_blank": true|false}
# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 END] ===
其中 title 放頁面**大標題**、subtitle 放緊接其下的**次級小標題**（如有；無則空字串）；
正文（條列/段落/表格）一律放 markdown_content、不要把小標題塞進正文。"""
```
> 原 `只輸出 JSON:` 與其後 schema 行被 HOTFIX-4 區塊取代（加入第 5 條 + schema 補 `is_blank`）。

### 3.2 單位過濾加 `is_blank` 雙保險跳過（`_process` 內 ④ 區塊）

```python
        # ④ 空白單位跳過 + 存圖（僅保留單位、檔名=頁序）
        units = []
        for img, r in zip(page_images, results):
            if not r:
                continue
            # === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4] === Vision 判空白 + 無實質文字 → 跳
            #   雙保險：僅當 is_blank 且 title/content 皆空才跳（防 Vision 誤判有內容頁被丟）；
            #   合法純圖頁 is_blank=false 不受影響；舊 golden 無 is_blank → None falsy → 向後相容不跳。
            if r.get("is_blank") and not ((r.get("title") or "").strip()
                                          or (r.get("markdown_content") or "").strip()):
                continue
            if not (r.get("title") or r.get("markdown_content")
                    or r.get("figure_description")):
                continue  # 空白頁跳過（A 軌同款、既有三欄全空）
            n = len(units) + 1
            ...
```

### 3.3 設計要點
- **雙保險**：`is_blank` 為 LLM 判斷（temp=0 壓抖動、非 100% 確定）；故僅在「is_blank **且** title/content 皆空」才跳——若 Vision 誤把有內容頁標 is_blank，因其有 title/content 仍保留（防誤殺）。
- **純圖頁安全**：合法圖頁 `is_blank=false`（Vision 看到真圖）→ 不跳；空白頁 `is_blank=true` + title/content 空 → 跳。
- **向後相容**：舊 Vision 回應（golden）無 `is_blank` → `r.get("is_blank")` 回 None → falsy → 不跳（行為等同舊狀）。
- **頁序連續**：沿用既有 `n = len(units) + 1`（跳過後頁序自動連續重編、不留洞）。

---

## 4. 不可動清單

- [ ] `is_cover` 封面判定 / `cover` metadata 抽取 / `_COVER_PROMPT` 既有欄位（僅基底加 is_blank、封面欄不動）
- [ ] 既有「三欄全空跳過」條件（保留為第二道、不移除）
- [ ] 渲染層（HOTFIX-3/3b/3c/3d、`_promote_subheadings`/`_tighten_point_groups` 等）
- [ ] `ctx.rag_sections` / `merged` / RAG / 向量
- [ ] 後端 `web_server.py` / DB / models / 其餘四路 pipeline
- [ ] `_render_pages` / 存圖 / 頁序重編邏輯

---

## 5. 端到端驗證計畫

### 5.1 靜態 grep
```bash
grep -n "is_blank" pipelines/slide_pipeline.py            # prompt schema + 第5條 + 跳過條件、≥3 命中
grep -n "HOTFIX-4" pipelines/slide_pipeline.py            # START/END + 注入 = 3 命中
grep -n "三欄全空\|空白頁跳過（A 軌同款" pipelines/slide_pipeline.py  # 既有條件仍在（未移除）
```

### 5.2 pytest（≥3 新增、`tests/test_slide_pipeline.py`）
- `test_p1_blank_flag_skips_empty`：Vision 回 `is_blank=true` + title/content 空（figure_description 描述空白）→ **單位被跳、不入 tiles、不存圖**。
- `test_p1_blank_flag_safety_belt_keeps_content`：Vision 回 `is_blank=true` **但** 有 title/content → **保留**（雙保險防誤殺）。
- `test_p1_image_only_page_kept`：`is_blank=false` + title/content 空 + figure_description 非空（純圖頁）→ **保留**。
- `test_p1_legacy_no_is_blank_field`：Vision 回應無 `is_blank` 欄（舊 golden）→ 不跳、行為等同舊狀（向後相容）。
- 既有 `test_p1_blank_unit_skipped`（三欄全空）續綠（第二道未動）。

全套件：`venv/bin/python -m pytest tests/ -q`（slide 套件 + 全套件維持綠）。

### 5.3 baron E2E（前端、非 commit）
- 影子重傳 Ch37 → **原第 16 張空白頁不再產出 reading 頁**（頁序連續、無空框黑條頁）；其餘頁正常、頁碼順移。
- 驗純圖頁（架構圖/照片）**未被誤跳**。

### 5.4 ⚠️ Golden（Vision prompt 變更）
本修**改 Vision prompt（加 is_blank 欄 + 第 5 條）** → Vision 輸出 schema 變更 → **slides golden 須重捕**；**搭既有待重捕批次**（HOTFIX-1/1b/2/3/3b/3c/3d + META-NORM C3/C4）一次首捕、零額外成本。

### 5.5 §5 SOP 一致性核查（BE 強制）
```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/slide_pipeline.py  # 新增碼段無 logging（合規）
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py   # 零 DB（合規）
```

---

## 6. 回退方式（Rollback）

移除 `# === [PIPE-SLIDES-HOTFIX-4 ...] ===` 包裹之 prompt 第 5 條 + schema is_blank 欄 + 跳過條件，或 `git revert <HOTFIX-4 hash>`。不涉 DB/向量/schema；舊 golden 無 is_blank 本就相容、回退僅還原「不檢測空白」。

---

## 7. Commit

**git add 清單**：
```
pipelines/slide_pipeline.py
tests/test_slide_pipeline.py
.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_slide_pipeline.py.bak
.claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_HOTFIX-4_test_slide_pipeline.py.bak
.claude-logs/baton/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md     # 收官階段才 add（hotfix 移出後）
```

**commit message 草稿**（`/tmp/PIPE-SLIDES-HOTFIX-4_msg.txt`）：
```
BE-Hotfix: PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）

真因：P1 ④ 空白跳過僅「title+markdown_content+figure_description 三欄全空」才跳；空白投影片
（Ch37 第 16 張、僅裝飾黑橫條）雖無 title/content，Vision 仍回非空 figure_description（描述空白）→
通過過濾 → 產出空框黑條 reading 頁。不能只看 title+content 空（會誤殺 title/content 皆空之合法純圖頁）。

修法：pipelines/slide_pipeline.py _VISION_PROMPT 加 is_blank 欄（基底、所有頁皆得，含封面）+ 第 5 條
判定指引（整頁無實質內容/僅裝飾橫條→true、含真實圖表→false）；④ 單位過濾加雙保險跳過——僅當
is_blank 且 title/content 皆空才跳（防 Vision 誤判有內容頁被丟）、合法純圖頁 is_blank=false 不受影響、
舊 golden 無 is_blank→falsy→向後相容不跳；既有三欄全空條件保留為第二道。與既有 is_cover 同模式對稱。

零後端/DB/models/static/RAG/渲染層/四路改動。SOP logging+database 皆無命中（合規）。

驗證：grep is_blank ≥3 / HOTFIX-4 3 命中 / 既有條件仍在；新增 pytest（空白跳過/雙保險保留有內容/
純圖頁保留/舊無欄相容）+ slide 套件全綠。⚠️ 改 Vision prompt → slides golden 併既有待重捕批次一次首捕；
baron E2E 影子重傳 Ch37 驗第 16 張不再產頁、純圖頁未誤跳。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
