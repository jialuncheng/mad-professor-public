# PIPE-SLIDES-HOTFIX-6 — 緊急熱修復：殘留母片日期（單頁）清除 + golden 重捕說明回溯更正

> **警示**：本文件含兩部分——**Part A（BE-Hotfix·程式）** 修 `_strip_master_date` 對「單頁殘留母片日期」漏網;**Part B（DOC·回溯更正）** 修正先前 8 份 PIPE-SLIDES hotfix 文件「slides golden 須重捕」之 A/B 軌混淆誤述。
> **工作流**：BE-Hotfix（依 `ref/WORKFLOW_SOP.md §1.5`、套 `template_hotfix.md`、附 §5 logging/database SOP 核查）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **PIPE-SLIDES-HOTFIX-6** | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正 |

---

# Part A — 殘留母片日期（單頁）清除

## A.1 阻斷現象

- **現象描述**：B 軌簡報 `Ch37_Plant-Nutrition_shadow`「都市農業 (Urban Farming)」頁底殘留一個日期 **`2026/4/28`**（母片頁尾日期、非投影片內容）。
- **受災範圍**：母片頁尾日期**僅被 Vision 在單一頁吐成獨立 content 行**之簡報（多頁型已由 HOTFIX-2 E 處理）。非阻斷、屬內容雜訊。
- **首發證據（final_zh）**：
  ```
  <div class="slide-head">
  <h2>都市農業 (Urban Farming)：城市的永續未來 (Sustainable Future)！</h2>
  <p class="slide-sub">垂直社區 (Vertical Community)：城市的未來生活 (Future Life)</p>
  </div>

  2026/4/28          ← 該頁唯一 content、全檔唯一日期行（L393）
  ```

## A.2 真因診斷

- **技術細節**：`_strip_master_date`（HOTFIX-2 E）以「整行即日期 + 出現於 **≥2 頁**」判定母片日期並剔除（≥2 門檻為防誤殺真內容單頁日期如時間軸）。本輪 Vision 僅在「都市農業」**一頁**把母片頁尾日期吐成獨立 content 行（其他頁省略/併入）→ `hit_pages = 1 < 2` → **函式早退、不洗** → 該日期留存 → P3 翻譯把 US 格式 `4/28/2026` 重排成中式 `2026/4/28`（即 baron 觀察之「日期被翻譯出來」）。
- **`_DATE_LINE_RE` 非問題**：`r"^\s*\d{1,4}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{1,4}\s*$"` 確實匹配 `2026/4/28`;漏網純因 hit_pages 門檻。
- **定位**：`pipelines/slide_pipeline.py` `_strip_master_date`（約 L356–373，`if hit_pages < 2: return` 早退）。

## A.3 熱修復修法（Part A）

**加一條精準的單頁 pass（運行於既有 ≥2 頁邏輯之前、無條件執行）**：整頁 `content` **僅由純日期行構成** → 清空。母片/頁尾日期的典型樣態＝該頁實質資訊在 title/figure，content 只剩一個日期。真內容頁（日期與其他文字並存）**不受影響**——其他行不匹配日期正則 → `all(...)` 為 False → 不清。

### `pipelines/slide_pipeline.py` — `_strip_master_date` 改動

```diff
     def _strip_master_date(units: list) -> None:
         """母片日期頁眉洗除（HOTFIX-2 E）：整行僅為日期、且出現於 ≥2 頁 → ...（docstring 不變）"""
+        # === [PIPE-SLIDES-HOTFIX-6 HOTFIX-6 START] === 單頁殘留：整頁 content 僅純日期行 → 清空
+        #   （母片/頁尾日期典型樣態、無論幾頁；補 HOTFIX-2「≥2 頁」門檻對「僅單頁殘留」之漏網。
+        #   真內容頁不受影響：日期與其他文字並存時其他行不匹配 → all(...) False → 不清。
+        #   運行 P1 譯前 → 清掉原文 4/28/2026、永不進 P3 重排成 2026/4/28。）
+        for u in units:
+            body = u["content"].strip()
+            if body and all(_DATE_LINE_RE.match(ln)
+                            for ln in body.splitlines() if ln.strip()):
+                u["content"] = ""
+        # === [PIPE-SLIDES-HOTFIX-6 HOTFIX-6 END] ===
         hit_pages = sum(
             1 for u in units
             if any(_DATE_LINE_RE.match(ln) for ln in u["content"].splitlines()))
         if hit_pages < 2:
             return
         removed = 0
         for u in units:
             lines = u["content"].splitlines()
             kept = [ln for ln in lines if not _DATE_LINE_RE.match(ln)]
             removed += len(lines) - len(kept)
             u["content"] = "\n".join(kept).strip()
         logger.info("[PIPE-SLIDES P1] 母片日期頁眉洗除 pages=%d lines=%d", hit_pages, removed)
```

### 設計說明與邊界
- **互補非取代**：HOTFIX-6 處理「整頁 content 就只有日期」（單頁亦洗）;HOTFIX-2 ≥2 頁邏輯仍保留、處理「日期夾在其他 content、跨多頁」。兩者正交。
- **真內容日期不誤殺**：時間軸/founded 年份等與其他文字並存 → `all(date)` False → 保留;單頁純年份標語（罕見）會被清（reading view 視為噪聲、可接受）。
- **RAG**：運行 P1（譯前、進 P2/P3 之前）→ 清掉的是母片日期噪聲、對 RAG 召回有益無害;不碰 `ctx.rag_sections` 旁路機制本身。

---

# Part B — golden 重捕說明回溯更正（DOC）

## B.1 真因（流程誤述）

先前 8 份 PIPE-SLIDES hotfix 文件皆載「改 B 軌 final_zh / Vision prompt → **slides golden 須重捕**（`golden_baseline.py capture slides --force`）」。**此敘述為 A/B 軌混淆、錯誤**：

- `golden_baseline.py` `_run_old_monolith`（L88-94）白紙黑字：**「唯讀調用舊單體 A 軌 `PipelineCore.process`、shadow=False（正本基準）」** → `capture slides` 捕的是 **A 軌**（`slides_processor`/`PipelineCore`）。
- HOTFIX-1/1b/2/3/3c/3d/4/5 + HOTFIX-6 **全改 B 軌 `slide_pipeline.py`**（+ 3b/RAG-12-HOTFIX-1 前端）→ **A 軌 `slides_processor` 零變更** → **A 軌 golden 不受影響、重捕亦無意義**。
- B 軌正確驗證方式＝**baron 影子重傳 E2E**（+ 未來 PIPE Flip 時 B 軌 shadow 輸出 diff A 軌 golden、改善豁免 Q8）;A 軌 golden 維持穩定參考、僅 A 軌自身改動才重捕。

## B.2 回溯更正修法（Part B）

於下列 **8 份已歸檔 hotfix 文件**之 golden 段落（見各檔行號）**插入更正註記**（不刪原句、加 banner 標作廢，保留審計軌跡）：

| 檔案 | golden 誤述行 |
|---|---|
| `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md` | L258, L290 |
| `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md` | L122 |
| `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md` | L194, L234 |
| `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md` | L257, L302 |
| `hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md` | L230, L281 |
| `hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md` | L173, L226 |
| `hotfixes/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md` | L134, L177 |
| `hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md` | L137, L139, L184 |

**統一更正 banner**（插於各檔 golden 段首、一次即可）：

```markdown
> ⚠️ **更正（PIPE-SLIDES-HOTFIX-6 回溯）**：本文件下方「slides golden 須重捕/首捕」之敘述**作廢**。
> `golden_baseline.py capture slides` 捕的是 **A 軌**（`PipelineCore`/`slides_processor`、shadow=False 正本基準）；
> 本 hotfix 改的是 **B 軌**（`slide_pipeline.py`）→ **A 軌 golden 不受影響、不需重捕**。
> B 軌驗證走**影子重傳 E2E**（+ 未來 PIPE Flip 時 B 軌 diff A 軌 golden、改善豁免 Q8）。
```

> **不改**：`hotfixes/2026-06-14_RAG-12-HOTFIX-1_hotfix.md`（其載「零 golden 重捕」、本即正確）。
> **TODO 同步**：`.claude-logs/TODO.md` 內 HOTFIX-1..5 完成表之「golden 須重捕/搭批次」附註亦屬同一誤述 → 各加一句尾註「（更正 HOTFIX-6：A 軌 golden、B 軌不需重捕、影子 E2E 驗）」。

---

## §5 SOP 一致性核查（BE-Hotfix 強制·針對 Part A 程式）

```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/slide_pipeline.py | grep HOTFIX-6
#   期望：無命中（合規、Part A 僅迴圈清空 content、無 logging）
grep -n "\.commit(" pipelines/slide_pipeline.py
#   期望：無命中（合規、本檔不涉 DB）
```

---

## regression 預防與 E2E 驗證

### 1. 新增回歸測試（tests/test_slide_pipeline.py）
- `test_hf6_sole_date_content_cleared`：unit content 僅 `'2026/4/28'`（單頁）→ 清空為 `''`、單位保留（title/figure 在）。
- `test_hf6_date_amid_content_kept`：unit content `'2026/4/28\n* 真實條列'`（單頁）→ **不清**（其他行非日期、HOTFIX-6 all() False;hit_pages=1 HOTFIX-2 亦不洗）→ 真內容單頁日期保留。
- `test_hf6_multipage_inline_date_stripped`：≥2 頁 content 含日期行 + 其他內容 → HOTFIX-2 ≥2 邏輯仍剔日期行、保留其他（既有行為不退化）。
- `test_hf6_real_content_untouched`：一般無日期 content → 不變。

### 2. 全套件
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -q   # 期望：既有 + hf6 新測試全綠
venv/bin/python -m pytest -q                                # 期望：基線 + hf6（唯一 fail＝既有 .env LOG_FORMAT flake）
```

### 3. ⚠️ golden / baron E2E（依 Part B 更正後之正確認知）
- **A 軌 golden 不需重捕**（Part A 改 B 軌、A 軌 `slides_processor` 未動）。
- baron **影子重傳 Ch37** → 「都市農業」頁底 **不再殘留 `2026/4/28`**;其餘真內容頁日期（若有時間軸）未誤殺。

---

## 回退與備案

```bash
git revert <PIPE-SLIDES-HOTFIX-6 hash>     # 一步還原 Part A 程式 + Part B 文件註記
# 或 Part A 自備份：
cp .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak pipelines/slide_pipeline.py
```

---

## baron 執行命令（Run 階段、commit 草稿）

```bash
# 1. 備份（Part A）
cp pipelines/slide_pipeline.py .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak

# 2. （Part A：改 _strip_master_date + 補測試；Part B：8 份 hotfix 文件 + TODO 插入更正 banner）

# 3. git add（Part A code/test/bak + Part B 8 文件 + TODO）
git add pipelines/slide_pipeline.py tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md \
        .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md \
        .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md \
        .claude-logs/hotfixes/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md \
        .claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md
git add .claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-6_hotfix.md \
        .claude-logs/executions/2026-06-14_PIPE-SLIDES-HOTFIX-6_執行.md \
        .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-6_run_提示詞.md .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-6_doc_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 4. commit message 草稿（寫入 tmp/PIPE-SLIDES-HOTFIX-6_msg.txt）
mkdir -p tmp
cat > tmp/PIPE-SLIDES-HOTFIX-6_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正

Part A（程式）：_strip_master_date 加「整頁 content 僅純日期行 → 清空」單頁 pass（無論幾頁、運行 P1 譯前）。
  真因：HOTFIX-2 ≥2 頁門檻對「Vision 僅單頁吐母片頁尾日期」漏網（Ch37 都市農業頁 4/28/2026 留存、P3 譯成 2026/4/28）。
  真內容頁不受影響（日期與其他行並存 → all() False → 不清）；補 HOTFIX-2 之單頁缺口、兩者正交。

Part B（文件回溯更正）：釐清 golden_baseline.py capture slides 捕 A 軌（PipelineCore/slides_processor、正本基準）、
  非 B 軌（slide_pipeline）→ B 軌 hotfix 不需 A 軌 golden 重捕、驗證走影子 E2E。
  8 份 PIPE-SLIDES hotfix 文件（HOTFIX-1/1b/2/3/3c/3d/4/5）「slides golden 須重捕」誤述加更正 banner 作廢
  （RAG-12-HOTFIX-1「零 golden 重捕」本即正確不改）+ TODO 同步尾註。

SOP 核查：logging + database 皆無命中（合規）。
驗證：4 新回歸測試（單頁純日期清空/單頁日期夾內容保留/多頁 HOTFIX-2 不退化/一般不動）+ 全套件維持基線。
A 軌 golden 不需重捕（本改 B 軌）；baron 影子重傳 Ch37 → 都市農業頁不再殘留日期。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 5. baron 手動 commit
git commit -F tmp/PIPE-SLIDES-HOTFIX-6_msg.txt
```

> 收官歸檔（hotfix 無 Check）：Run 落地後本文件 `mv` baton → `hotfixes/`、執行報告 `mv` baton → `executions/`、`.bak` 入 git add（依 WORKFLOW_SOP §3）。Part B 的 8 份文件本就在 hotfixes/、就地編輯。
