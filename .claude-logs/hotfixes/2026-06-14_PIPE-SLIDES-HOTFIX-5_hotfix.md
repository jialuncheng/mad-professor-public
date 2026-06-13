# PIPE-SLIDES-HOTFIX-5 — 緊急熱修復：有標題的過場/分隔頁未被踢除（HOTFIX-4 跳過條件過嚴）

> **警示**：本文件為 **BE-Hotfix** 緊急熱修復紀錄，修正 PIPE-SLIDES-HOTFIX-4（P1 空白頁 is_blank 檢測）落地後、對「Vision 給了標題之過場/分隔頁」漏踢之缺口。
> **修復原則**：只改 `pipelines/slide_pipeline.py` P1 受災點（is_blank 跳過邏輯 + Vision prompt is_blank 定義）;RAG/渲染層/四路零碰。
> **工作流**：BE-Hotfix（依 `ref/WORKFLOW_SOP.md §1.5`、套 `template_hotfix.md`、附 §5 logging/database SOP 核查）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **PIPE-SLIDES-HOTFIX-5** | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（is_blank 跳過放寬 + Vision prompt 釐清） |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：B 軌簡報 `Ch37_Plant-Nutrition_shadow` 之 **page-32「過場投影片 (Transition Slide)」**（深藍底生態球裝飾圖、無教學內容）**未被踢除**，於閱讀視圖產出一張只有裝飾圖 + 「過場投影片」標題的單位。
- **受災範圍**：所有**被 Vision 賦予標題之過場/章節分隔/純裝飾頁**（HOTFIX-4 的 is_blank 機制對其失效）。非阻斷崩潰、屬內容雜訊（多一張無資訊頁、頁序順移）。
- **首發證據（final_zh 實際渲染）**：
  ```
  ![深藍色背景中央有一個暗紅色的圓形…呈現生態球 （Ecosphere） 的意象。](images/page-32.jpg)

  <div class="slide-head">
  <h2>過場投影片 (Transition Slide)</h2>
  </div>
  ```
  （title 非空 → HOTFIX-4 跳過條件不成立 → 整單位保留）

### 2. 真因診斷 (Root Cause)

- **技術細節**：HOTFIX-4 之跳過判定採「**雙保險**」——要求 `is_blank=true` **且 title 與 markdown_content 皆空**（當初為「防 Vision 誤判有內容頁被丟」之保守設計）。但 Vision 對過場頁**忠實轉錄出標題**「過場投影片 (Transition Slide)」（頁面確有此字樣/Vision 判讀為標題）→ **title 非空** → 雙保險不成立 → 不跳;其後既有「三欄全空」規則亦因 **figure_description 非空**（描述生態球裝飾圖）而不跳 → 漏網。
- **結構同型困境**：過場頁（title + 裝飾 figure_description + 無 markdown_content）與「純圖表內容頁」（title + 真圖 figure_description + 無 markdown_content）**結構完全同型**;唯一可區分者＝Vision 的 `is_blank` 語意判斷。故修復**必須信任 is_blank** 來分辨，並同時強化 prompt 使 is_blank 對過場頁可靠。
- **定位程式碼**：`pipelines/slide_pipeline.py`
  - Vision prompt is_blank 定義：L57–62（`_VISION_PROMPT` 第 5 條）
  - 跳過邏輯：L170–178（HOTFIX-4 雙保險 + 既有三欄全空）

---

## 熱修復修法 (Minimal Hotfix)

**雙管齊下**（互補、缺一不夠穩）：

1. **放寬跳過邏輯**：由「is_blank 且 title+content 皆空」→「**is_blank 且 markdown_content 空**」（**容許 title / figure_description 非空**）。過場頁特徵＝有裝飾圖（figure_description）+ 可能標題（title）但**無條列正文**（markdown_content 空）→ 命中跳過;**保留安全網**：若 is_blank=true 但 markdown_content 有實質正文（自相矛盾）→ 不跳（防誤殺）。
2. **Vision prompt 釐清**：明訂「純過場/章節分隔/裝飾頁**即使你判讀出『過場/Transition/Section』之類標題，仍 is_blank=true**」;同時保留「**含真實圖表/照片/示意圖/資料/條列正文之頁一律 is_blank=false**」→ 真圖表內容頁 is_blank=false 不受影響、不被誤踢。

> **為何安全（不誤殺真圖頁）**：真圖表/照片內容頁依 prompt → `is_blank=false` → 跳過條件第一項即不成立 → 不跳。放寬只在 `is_blank=true` 時生效，而 Vision 僅對「裝飾/過場」判 true。markdown_content 空之要求再加一層：任何有條列正文之頁永不被踢。

### `pipelines/slide_pipeline.py` — 改動 ①：Vision prompt is_blank 定義（L57–62）

```diff
 # === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 START] ===
-5. is_blank：若整頁**無任何實質內容**（空白頁、僅裝飾性橫條/分隔線/純背景/頁碼，無標題無正文
-   無有意義圖表）→ is_blank=true；否則 false。**含真實圖表/照片/示意圖/資料之頁一律 is_blank=false。**
+5. is_blank：若整頁**無任何實質教學內容** → is_blank=true；否則 false。涵蓋：
+   (a) 空白頁、僅裝飾性橫條/分隔線/純背景/頁碼；
+   (b) 純過場/章節分隔/裝飾頁（僅一張裝飾圖、或僅「過場/Transition/Section」之類字樣，無條列正文與實質資料）
+       —— **即使你判讀出『過場投影片』之類標題，這類頁仍 is_blank=true**。
+   **含真實圖表/照片/示意圖/資料/條列正文之頁一律 is_blank=false**（勿把有資訊的圖表頁誤判為過場）。
 只輸出 JSON：
 {"title": "", "subtitle": "", "markdown_content": "", "figure_description": "", "is_blank": true|false}
 # === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 END] ===
```

### `pipelines/slide_pipeline.py` — 改動 ②：跳過邏輯放寬（L170–175）

```diff
-            # === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4] === Vision 判空白 + 無實質文字 → 跳
-            #   雙保險：僅當 is_blank 且 title/content 皆空才跳（防 Vision 誤判有內容頁被丟）；
-            #   合法純圖頁 is_blank=false 不受影響；舊 golden 無 is_blank → None falsy → 向後相容不跳。
-            if r.get("is_blank") and not ((r.get("title") or "").strip()
-                                          or (r.get("markdown_content") or "").strip()):
-                continue
+            # === [PIPE-SLIDES-HOTFIX-5 HOTFIX-5 START] === 放寬：is_blank 且「無條列正文」即跳
+            #   真因：過場/分隔頁被 Vision 賦予標題（如「過場投影片」）→ HOTFIX-4「title 須空」不成立 → 漏網。
+            #   改為僅看 markdown_content 空（容許 title/figure_description 非空，過場頁特徵＝裝飾圖+可能標題、無正文）。
+            #   安全網：is_blank 但有 markdown_content 實質正文（自相矛盾）→ 不跳，防誤殺；
+            #   真圖表/資料頁依 prompt is_blank=false → 第一項即不成立、不跳；舊 golden 無 is_blank → None falsy → 不跳。
+            if r.get("is_blank") and not (r.get("markdown_content") or "").strip():
+                continue
+            # === [PIPE-SLIDES-HOTFIX-5 HOTFIX-5 END] ===
             if not (r.get("title") or r.get("markdown_content")
                     or r.get("figure_description")):
                 continue  # 空白頁跳過（A 軌同款、既有三欄全空）
```

### 設計說明與邊界（誠實）

- **頁序**：跳過於 `units.append` 之前（continue 早於 L181 write_bytes + L182 append）→ 過場頁不存圖、不入單位、`n=len(units)+1` 自然順移（同 HOTFIX-4 既有行為）。
- **不確定 Vision is_blank 原值**：此件 page-32 之 is_blank 未持久化、無法事後確認。本修雙管齊下覆蓋兩情境——若原為 is_blank=true（標題擋跳）→ 改動 ② 即解;若原為 is_blank=false（Vision 未判過場）→ 改動 ① prompt 使其判 true。重跑後生效。
- **誤殺風險（殘留、可接受）**：唯有 Vision 違反自身 prompt（對「真圖表頁」誤判 is_blank=true 且該頁無 markdown_content）才會誤踢;temp=0 + 強化 prompt 下機率低，且僅影響該單張、頁序順移、可由 baron E2E 抽查。
- **與既有規則並存**：第二道「三欄全空」保留為後盾;與 `is_cover` 機制對稱、互不干擾。

---

## §5 SOP 一致性核查（BE-Hotfix 強制）

### §5.1 logging 核查
```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/slide_pipeline.py
```
本次改動僅 prompt 字串 + 跳過條件，**未新增任何 logging** → 對本 hotfix 改動行：**無命中（合規）**。

### §5.2 database 核查
```bash
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v "with .*session.*begin\(\)"
```
本次改動不涉資料庫/交易 → **無命中（合規）**。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組單元測試
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -q   # 期望：既有 + 新增全綠
venv/bin/python -m pytest -q                                # 期望：全套件維持基線（唯一 fail＝既有 .env LOG_FORMAT flake）
```

### 2. 新增回歸測試（tests/test_slide_pipeline.py）
- `test_hf5_transition_skipped_with_title`：unit `is_blank=true, title="過場投影片", markdown_content="", figure_description="生態球"` → **被跳過**（不入 units）。
- `test_hf5_blank_with_decorative_figure_skipped`：`is_blank=true, title="", markdown_content="", figure_description="裝飾橫條"` → 跳過（HOTFIX-4 案沿用）。
- `test_hf5_real_figure_page_kept`：`is_blank=false, title="架構圖", markdown_content="", figure_description="系統架構…"` → **保留**（真圖頁不誤殺）。
- `test_hf5_is_blank_but_has_content_kept`：`is_blank=true, markdown_content="* 真實條列"` → **保留**（安全網、防自相矛盾誤殺）。
- `test_hf5_legacy_no_is_blank_kept`：無 `is_blank` 欄（舊 golden）→ None falsy → 不跳（向後相容）。

### 3. baron 影子 E2E（重跑管線、headless 不可替代）
影子重傳 `Ch37_Plant-Nutrition.pdf` →
- page-32 生態球過場頁**不再產出 reading 頁**、頁序順移。
- 真圖表頁（如氮循環圖、土壤剖面、PCoA 圖等）**未被誤踢**、全數保留。

---

> ⚠️ **更正（PIPE-SLIDES-HOTFIX-6 回溯）**：本文件下方「slides golden 須重捕/首捕」之敘述**作廢**。
> `golden_baseline.py capture slides` 捕的是 **A 軌**（`PipelineCore`/`slides_processor`、shadow=False 正本基準）；
> 本 hotfix 改的是 **B 軌**（`slide_pipeline.py`）→ **A 軌 golden 不受影響、不需重捕**。
> B 軌驗證走**影子重傳 E2E**（+ 未來 PIPE Flip 時 B 軌 diff A 軌 golden、改善豁免 Q8）。

## ⚠️ golden 重捕（行為變更）

改動 ① 變更 Vision prompt（is_blank 定義）→ **Vision schema/輸出變更 → slides golden 須重捕**。**搭既有待重捕批次一次首捕、零額外成本**：HOTFIX-1/1b/2/3/3b/3c/3d/**4** + META-NORM C3/C4 + 本 HOTFIX-5（`venv/bin/python tools/golden_baseline.py capture slides --force`）。

---

## 回退與備案

```bash
git revert <PIPE-SLIDES-HOTFIX-5 hash>     # 單檔、prompt + 跳過兩 hunk、一步還原
# 或自備份：
cp .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak pipelines/slide_pipeline.py
```

---

## baron 執行命令（Run 階段、commit 草稿）

```bash
# 1. 備份
cp pipelines/slide_pipeline.py .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak

# 2. （依 §修法 diff 改 pipelines/slide_pipeline.py：prompt 第 5 條 + 跳過邏輯）+ 補 5 回歸測試

# 3. git add（含備份 + 測試）
git add pipelines/slide_pipeline.py tests/test_slide_pipeline.py .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak

# 4. commit message 草稿（寫入 tmp/PIPE-SLIDES-HOTFIX-5_msg.txt；簽名當前模型）
mkdir -p tmp
cat > tmp/PIPE-SLIDES-HOTFIX-5_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（is_blank 跳過放寬 + Vision prompt 釐清）

真因：HOTFIX-4 跳過要求 is_blank 且 title+content 皆空（防誤殺保守設計）；過場/分隔頁被 Vision
忠實轉錄出標題（如「過場投影片 (Transition Slide)」）→ title 非空 → 不跳；既有三欄全空規則亦因
figure_description 非空（描述裝飾圖）而不跳 → 漏網（Ch37 page-32 生態球過場頁）。

修法（雙管齊下）：
1. 跳過邏輯放寬：is_blank 且 markdown_content 空即跳（容許 title/figure_description 非空，
   過場頁＝裝飾圖+可能標題但無條列正文）；安全網＝is_blank 但有實質正文則不跳，防誤殺。
2. Vision prompt 釐清：純過場/分隔/裝飾頁即使有「過場/Transition」標題仍 is_blank=true；
   保留「含真實圖表/資料/條列正文一律 is_blank=false」→ 真圖表頁不誤踢。

結構同型困境：過場頁與純圖表頁同型（title+裝飾/真圖 figure_description+無正文），唯 is_blank 可分；
故信任 is_blank 並強化 prompt 使其對過場頁可靠。RAG/渲染層/四路零碰。

SOP 核查：logging + database 皆無命中（合規）。
驗證：5 新回歸測試（過場頁跳/裝飾頁跳/真圖頁保留/有正文保留/舊無欄相容）+ 全套件維持基線。
⚠️ 改 Vision prompt → slides golden 須重捕，搭既有批次（HOTFIX-1..4 + META-NORM C3/C4）一次首捕。
baron 影子 E2E：重傳 Ch37 → page-32 不產頁、真圖表頁未誤踢。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 5. baron 手動 commit
git commit -F tmp/PIPE-SLIDES-HOTFIX-5_msg.txt
```

> 收官歸檔（hotfix 無 Check）：Run 落地後本文件 `mv` baton → `hotfixes/`、執行報告 `mv` baton → `executions/`、`.bak` 入 git add（依 WORKFLOW_SOP §3）。
