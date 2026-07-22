# FITZ-HOTFIX-2 — Header Boundary Narrowing & Bilingual Figure Symmetry（報頭行界收窄與雙語圖片對稱）執行報告

---

**任務代號**：FITZ-HOTFIX-2
**執行日期**：2026-07-22
**依據規劃**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md`（熱修復修法 K1/K2）
**上游 plan**：同名 `_plan.md`
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit HOTFIX-2)

---

## §1 基準與完成狀態

- 基準 commit：`f5a3ec6`（FITZ-HOTFIX-1 checkout、baron 已 ship）
- 完成狀態：K1 + K2 已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 範圍自檢：`git status -s`（排除 .claude-logs）＝恰為 `pipelines/litedoc_pipeline.py` + `tests/test_litedoc_pipeline.py` **單檔 + 對應測試**

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-2 | Header Boundary Narrowing & Bilingual Figure Symmetry（報頭行界收窄與雙語圖片對稱） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改 | K1 `_HEADER_META_TYPES` 同源常數 + `_collect_header_srcs` 行界收窄；K2 `_load_header_srcs` 三級定位 + `_filter_source_figures` 注入 |
| `tests/test_litedoc_pipeline.py` | 修改 | +10 測試（K1 ×4／K2 ×6）＋既有 `test_collect_header_srcs_line_boundary` 契約更新 |
| `.claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_litedoc_pipeline.py.bak` | 備份 | 改前快照（隨本 commit git add） |
| `.claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_test_litedoc_pipeline.py.bak` | 備份 | 改前快照（隨本 commit git add） |

（baton 暫存之 plan/hotfix/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

### K1 — 報頭行界收窄（`_HEADER_META_TYPES` 同源實作）
**真因**：`_collect_header_srcs` 之行界原取 `max(int(b["end"]) for b in blocks)`——**全部**判型塊之最末 end。而 DocAnalyzer 會把正文段落也判成塊（`intro_text`／`other`），致行界被撐到文件深處（v3 實物 hdr_end=**119**），把封面大圖與正文 Falcon 9 照片一併掃進「報頭集」→ 規則③ 誤殺。

**修法**：行界改為**僅計 meta 型塊**之 `max(end)`；無 meta 型塊 → 回 `set()`（規則③自然停用、①②照跑、沿用既有 soft 語意）。

**同源保證（防常數漂移）**：新增類別常數 `_HEADER_META_TYPES = set(_META_TYPES) | {"title"}`，**緊鄰 `_META_TYPES` 定義**（同一區塊、視覺上不可能各改一邊），與 `mark_meta_lines`「title 恆視 meta」語意一致；`| {"title"}` 於現值屬防禦性 no-op（`_META_TYPES` 已含 title），防未來 tuple 調整時漏掉 title。

**效果（v3 實物模擬、測試鎖定）**：hdr_end **119→10**——頭像（line 4/6）仍中③（且①面積兜底）；**封面大圖（line 15）獲救**；**Falcon 9（line 91）獲救**。

### K2 — `_load_header_srcs` 三級定位與 R8 補傳（對稱恢復）
**真因**：`_filter_source_figures`（P3 原文通道）原僅傳 `images_root`、**未傳 `header_srcs`** → 該通道規則③**恆停用**；而 tiles 通道有③ → 同一張圖兩通道判定不同 → 雙語圖片不對稱（v3 實測 en21 vs zh19）。

**修法**：新增 `_load_header_srcs(ctx, output_dir, text)`，讀 sidecar 判型後**複用同一個 `_collect_header_srcs`**（含 K1 新行界）算出集合，注入 `make_figure_filter` → **任何規則之 DROP 兩通道必同步**（結構性保證、非兩邊各算）。

**sidecar 定位（三級、外部 review 核心發現）**：sidecar 檔名基於**原始 PDF stem**，而影子軌 `ctx.paper_id` 帶 `_shadow` 後綴（v3 實物：`SpaceX_the_Sentient_Sun_doc_structure.json` 無後綴）——**嚴禁以 `ctx.paper_id` 組檔名**（必 miss、規則③靜默停用、對稱再破）：
1. **主路** `{Path(ctx.pdf_path).stem}_doc_structure.json`（與 `_read_source_text` 之 md 定位**同一 stem 基準**、production 已證）；
2. **備路** `sorted(output_dir.glob("*_doc_structure.json"))` 取首個（per-paper 目錄唯一）；
3. **兜底** 皆失／解析異常 → `set()` fail-open（`logger.warning` + `exc_info=True`）——兩通道規則③**同步**停用、對稱維持。

### ⚠️ 既有測試契約更新（預期行為變更、誠實留痕）
`test_collect_header_srcs_line_boundary`（IMG-FILTER C3）於 K1 落地後失敗——其 fixture `_HDR_STRUCT` 含 `{"start":2,"end":5,"type":"other"}`（**非 meta 型**），舊行界 max=5、新行界 max(meta)=4，故 `hdr2.jpg`（line 5）自此不再列入報頭集。**此為 K1 之預期收窄**（該 `other` 塊正是實測中把行界撐到 119 的同類元凶）。已更新該測試至新契約並於 docstring 記明變更理由與溯源。

## §5 測試與 Grep 結果

```
tests/test_litedoc_pipeline.py：133 passed（123 既有〔含 1 契約更新〕+ 10 新增）in 0.77s
全套件：978 passed, 3 skipped, 3 warnings in 54.92s   ← 基線 968 + 10、零回歸
```

新增 10 測試：
- **K1 ×4**：`test_boundary_narrowed_to_meta_blocks`（v3 真 sidecar 形狀 → 頭像仍中③、**封面大圖與 Falcon 9 獲救**）／`test_old_behaviour_would_have_swallowed_everything`（對照組實證 **119 vs 10**）／`test_no_meta_block_returns_empty`（無 meta 型塊 → `set()`）／`test_header_meta_types_sourced_from_meta_types`（**同源守衛**：`_META_TYPES ⊆ _HEADER_META_TYPES` 且含 title）
- **K2 ×6**：`test_primary_path_by_pdf_stem_not_paper_id`（**影子軌 `_shadow` 後綴陷阱**：主路以 PDF stem 命中）／`test_glob_fallback_when_stem_mismatch`（備路 glob）／`test_missing_sidecar_fail_open_empty`／`test_corrupt_sidecar_fail_open_empty`／`test_rule3_drop_applies_to_source_text_channel`（**規則③於原文通道生效**：報頭大圖 DROP、界外大圖 KEEP；兩圖尺寸皆逃過①②故只有③能殺）／`test_bilingual_symmetry_under_rule3`（**對稱不變式**：規則③會殺之情境下 `final_en` 圖集 ≡ `final_zh` 圖集）

驗收 grep：

```
K1：L371 _HEADER_META_TYPES = set(_META_TYPES) | {"title"}（緊鄰 L366 _META_TYPES）✅
    L444 行界只計 meta 型塊；舊 `max(int(b["end"]) for b in blocks)` **零殘留** ✅
K2：L657 _load_header_srcs／L674 主路 PDF stem／L676 備路 glob／L709 注入 make_figure_filter ✅
    `paper_id` 拼 sidecar 檔名 → **零命中** ✅（影子軌陷阱已避）
範圍：git status -s（排除 .claude-logs）＝ litedoc_pipeline.py + test_litedoc_pipeline.py ✅
```

SOP 一致性核查：

```
logging：grep logger.error/exception/traceback.format_exc → 無命中（合規）；
         K2 兩處 fail-open 皆 logger.warning(..., exc_info=True)
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `pipelines/image_filter.py` 三規則本體／門檻／工廠簽名 — 零改（K2 僅呼叫端多傳既有參數）
- [x] `processor/fitz_processor.py`（HOTFIX-1 八刀）／`pipelines/ingestion_engine.py`／`pipelines/section_engine.py`／`processor/rag_indexer.py`／`contracts` — 零改
- [x] A 軌全鏈／resume／slides／book／academic — 零碰
- [x] `IMG_FILTER_*`／`LITEDOC_*` 旗標語意 — 零改
- [x] K1 型別集與 `mark_meta_lines` 同源（`_META_TYPES` 導出、測試守衛）
- [x] K2 未以 `ctx.paper_id` 拼接 sidecar 檔名（三級定位、grep 實證）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / hotfix / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**checkout 收官**（Conformance + TODO 雙層結案 + baton 一次性歸檔）；待 baron ship HOTFIX-2 後另下 checkout 提示詞。
- baron 影子 E2E（收官後）：重傳 SpaceX v3 樣本——**封面大圖與 Falcon 9 降落照片回歸可見**、頭像/logo/分隔線仍被濾；後端 log 規則③ DROP 筆數應顯著下降且不再命中內容圖；**`final_en` 與 `final_zh` 圖片數一致**（v3 為 en21 vs zh19、修後應相等）。
- 契約回灌：K1/K2 併入 **PIPE-SYNC-6** 批次（與 PIPE-INGEST-FITZ／LANG-DETECT／FITZ-HOTFIX-1 八刀同批、待 E2E 綠燈後開）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、2 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-2_msg.txt
```
