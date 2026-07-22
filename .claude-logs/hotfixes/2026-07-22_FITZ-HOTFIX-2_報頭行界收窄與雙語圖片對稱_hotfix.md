# FITZ-HOTFIX-2 — 緊急熱修復：報頭行界收窄與雙語圖片對稱

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 FITZ-HOTFIX-1（`e8d57a6`…`e6f3e44`）落地後首次影子 E2E 立即發現的圖片誤殺與雙語不對稱缺陷。
> **修復原則**：只改動受災點程式碼（`pipelines/litedoc_pipeline.py` 單檔＋測試），嚴禁夾帶任何無關的新功能或大型重構。
> 證據包：`baton/litedoc_shadow_artifacts/SpaceX_v3_hotfix1/`（gitignored 長駐、審計附件）。
> 拍板：**banner 甲案＝保留**（baron 2026-07-22 指認封面 cover art）；BE-Hotfix 單 commit；型別集合複用 `_META_TYPES`（外部 review 覆核、三問全拍板）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-2** | `[留空，由 baron 回填]` | BE-Hotfix: FITZ-HOTFIX-2 — Header Boundary Narrowing & Bilingual Figure Symmetry（報頭行界收窄與雙語圖片對稱） |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：SpaceX v3 影子 E2E（2026-07-22）——zh 閱讀視圖缺兩張圖：①**封面大圖**（1456×1442、A16Z NEWS／PROFILES OF THE FUTURE cover art、含文章標題、baron 指認必留）②**Falcon 9 降落駁船內容照片**（500×333、誤殺最冤）。且 `final_en.md`＝**21 圖** vs `final_zh.md`＝**19 圖**——HOTFIX-1 plan v4 §4 立的「雙語圖片對稱不變式」破功。
- **受災範圍**：litedoc 路（fitz／MinerU 兩來源）之 zh 閱讀視圖圖片完整性 + 雙語一致性；文字面八刀成果不受影響。
- **首發日誌（img_filter_log.txt 實貼）**：

  ```
  tiles 路（13:37:11）：
  [img-filter] DROP 規則③報頭區 src=images/page_0_29.png   ← 頭像(垃圾)
  [img-filter] DROP 規則③報頭區 src=images/page_0_15.png   ← 頭像(垃圾)
  [img-filter] DROP 規則③報頭區 src=images/page_0_16.png   ← 封面大圖(誤殺!)
  [img-filter] DROP 規則③報頭區 src=images/page_0_17.png   ← 分隔線(垃圾)
  [img-filter] DROP 規則③報頭區 src=images/page_1_34.png   ← Falcon 9 照片(誤殺!)
  R8 路（13:38:53）：僅規則① ×3（頭像×2＋分隔線）→ 兩通道 DROP 集不同＝不對稱實錘
  ```

### 2. 真因診斷 (Root Cause)

- **真因 A（行界過寬）**：`_collect_header_srcs` 之 `hdr_end = max(int(b["end"]) for b in blocks)` 對**全部**判型 blocks 取 max——而 DocAnalyzer 判型深入正文（v3 sidecar 實測：`intro_text` 標到 25-91、103-119）→ hdr_end=**119**＝「報頭行界」涵蓋前三分之一篇 → 區內圖片（md line 15 封面大圖、≤91 區 Falcon 9）全被規則③誤殺。IMG-FILTER plan v2「收窄界定」的前提（判型只覆蓋前導 meta 簇）不成立。
- **真因 B（單通道）**：R8 `_filter_source_figures` 呼 `make_figure_filter(output_dir / "images")` **未傳 `header_srcs`** → 規則③只作用 tiles 路（zh）、R8 路（en／whole／is_zh）只跑①② → 兩通道 DROP 集分歧 → 雙語不對稱。HOTFIX-1 §7.2 測試 fixture 判型太淺、未照出。
- **定位程式碼**：`pipelines/litedoc_pipeline.py` `_collect_header_srcs`（hdr_end 一行）＋ `_filter_source_figures`（`make_figure_filter` 呼叫）。
- **佐證（v3 實物四對帳）**：sidecar hdr_end=119／md 行號地圖（line 15 封面、23 分隔線）／en 21 vs zh 19（`page_0_16`/`page_1_34` 僅 en 有）／`_processed.json` tiles 存活恰 19＝zh 集。

---

## 熱修復修法 (Minimal Hotfix)

### K1 — `_collect_header_srcs` 行界收窄（甲案）

```diff
- hdr_end = max(int(b["end"]) for b in blocks)
+ # [FITZ-HOTFIX-2 K1] 行界＝meta 型塊（title/authors/publication_info）之最末 end——
+ # 回歸「報頭＝判型 meta 區」設計本意；DocAnalyzer 深判正文（intro_text/other）不再撐大行界。
+ meta_ends = [int(b["end"]) for b in blocks
+              if str(b.get("type") or "") in _HEADER_META_TYPES]
+ if not meta_ends:
+     return set()          # 無 meta 型塊 → 規則③自然停用（①②照跑、沿用 soft 語意）
+ hdr_end = max(meta_ends)
```

- `_HEADER_META_TYPES = set(_META_TYPES) | {"title"}`（複用 `litedoc:366` 類別常數、與 `mark_meta_lines`「title 恆視 meta」語意同源；**勘誤註**：`_META_TYPES` 現值已含 `"title"`、`| {"title"}` 屬防禦性 no-op、防未來 tuple 改動漏 title）。
- **真 sidecar 模擬（v3 實物、寫碼前已驗）**：hdr_end **119→10**——頭像(4/6)仍中③（且①兜底）；**封面大圖(15)獲救**；分隔線(23)逃③改由①殺（area 7280）；**Falcon 9(≤91)獲救**。

### K2 — `_filter_source_figures` 補傳同一份 header_srcs（對稱恢復）

```diff
- fig_filter = image_filter.make_figure_filter(output_dir / "images")
+ # [FITZ-HOTFIX-2 K2] 與 tiles 路同一 _collect_header_srcs（含 K1 新行界）算出之
+ # 同一集合注入——任何規則之 DROP 兩通道必同步（雙語對稱之結構性保證、非兩邊各算）。
+ header_srcs = self._load_header_srcs(ctx, text)
+ fig_filter = image_filter.make_figure_filter(
+     output_dir / "images", header_srcs
+ )
```

**sidecar 定位（`_load_header_srcs`、外部 review 核心發現）**：影子軌 `ctx.paper_id` 帶 `_shadow` 後綴、sidecar 檔名基於**原始 PDF stem**（v3 實物：`SpaceX_the_Sentient_Sun_doc_structure.json` 無後綴）——**嚴禁以 `ctx.paper_id` 組檔名**。三級定位：
1. 主路 `output_dir / f"{Path(ctx.pdf_path).stem}_doc_structure.json"`（與 `_read_source_text` 之 md 定位**同一 stem 基準**、production 已證）；
2. 備路 `sorted(output_dir.glob("*_doc_structure.json"))` 取首個（per-paper 目錄唯一）；
3. 皆失／解析異常 → ∅ fail-open（warning + exc_info）——兩通道規則③**同步**停用、對稱維持。

### 不可動清單

- `pipelines/image_filter.py` 三規則本體／門檻／工廠簽名（K2 僅呼叫端多傳既有參數）
- `processor/fitz_processor.py`（HOTFIX-1 八刀）／`ingestion_engine`／`section_engine`／`rag_indexer`／contracts
- A 軌全鏈／resume／slides／book；`IMG_FILTER_*`／`LITEDOC_*` 旗標語意

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（落地時實貼輸出）

- K1：以 v3 真 sidecar 為 fixture——hdr_end 斷言 **10**（非 119）；meta 型塊缺席 → ∅；型別集合與 `_META_TYPES` 同源斷言（防 drift）
- K2：R8 過濾含 header_srcs——meta 簇內圖 DROP、簇外大圖 KEEP；**影子後綴情境**（`ctx.paper_id` 帶 `_shadow`、sidecar 無後綴 → 主路仍命中）；sidecar 缺檔 → ∅ fail-open；**對稱斷言強化**——造「③會殺」fixture（深判型＋簇內圖）驗 `final_en` 圖集 == `final_zh` 圖集（補 HOTFIX-1 fixture 判型太淺盲區）
- 全套件 **968 passed** 基線不退；SOP 雙 grep（logging／database）照跑實貼

```bash
$ pytest tests/ -v
# [落地時貼上真實輸出]
```

### 2. 本地 E2E 快速復現與驗證（baron 影子軌）

1. 重傳 `SpaceX & the Sentient Sun.pdf`：**zh=en=21 圖**、封面大圖與 Falcon 9 照片**雙語皆在**、垃圾三圖雙語皆滅
2. log 驗：tiles 路與 R8 路 DROP 集**完全相同**（頭像×2＋分隔線、無 `page_0_16`／`page_1_34`）
3. 文字面回歸抽查：標題／恰一個 `(測試)`／零 meta 重播（HOTFIX-1 成果不退化）

```
[落地後貼上成功日誌]
```

---

## 回退與備案

```bash
# 單 commit 可逆：
git revert [HOTFIX-2 hash]

# 或免 commit 單點降級（圖片全保留、兩通道同步 no-op）：
# .env 設 IMG_FILTER_ENABLED=false 後重啟
```

---

## 附：拍板與溯源紀錄

- 三問拍板（2026-07-22、外部 review 覆核）：Q1 BE-Hotfix 單 commit／Q2 複用 `_META_TYPES`（含勘誤註）／Q3 banner 甲案保留
- 候選方案留痕：乙（meta 末塊後間隙圖片併入報頭、可殺 banner）否決——baron 要留 banner 且間隙判定引入新誤殺面；丙（連續前導 meta 塊）否決——epigraph 插在 title 與 authors 間致 hdr_end=0、規則③失能
- 溯源：FITZ-HOTFIX-1 plan v4 §4 對稱不變式（本案恢復）；IMG-FILTER plan v2 §2.3 規則③「收窄界定」原始意圖（本案使其名實相符）；診斷 session 提示詞 `prompts/2026-07-22_FITZ-HOTFIX-2_診斷與plan_提示詞.md`
