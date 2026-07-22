# FITZ-HOTFIX-1 C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）執行報告

---

**任務代號**：FITZ-HOTFIX-1 C3
**執行日期**：2026-07-22
**依據規劃**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` §8 C3
**上游 plan**：同名 `_plan.md`（v4、六問拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C3)

---

## §1 基準與完成狀態

- 基準 commit：`a666a11`（FITZ-HOTFIX-1 C2、baron 已 ship）
- 完成狀態：R4 + R8 已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 範圍自檢：`git status -s`（排除 .claude-logs）＝恰為 `pipelines/litedoc_pipeline.py` + `tests/test_litedoc_pipeline.py` 兩檔；**`web_server.py` git diff 零**

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor Refinement（Fitz 處理器標題救回與結構修復） | `e8d57a6` |
| C2 | P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理） | `a666a11` |
| C3 | P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改 | R4 `_translate_title` + 兩處譯題改餵 `_title_bare`；R8 `_filter_source_figures` + P3 單點接線；`_SHADOW_SUFFIX` 常數 |
| `tests/test_litedoc_pipeline.py` | 修改 | +9 測試（R4 ×3／R8 ×5／雙語對稱 ×1） |
| `.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_litedoc_pipeline.py.bak` | 備份 | 改前快照（隨本 commit git add） |
| `.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_test_litedoc_pipeline.py.bak` | 備份 | 改前快照（隨本 commit git add） |

（baton 暫存之 plan/tasks/本報告依鐵律**不入** git add 清單；`web_server.py` 零改、不入清單。）

## §4 說明（真因與修法）

### R4 — 譯題輸入去後綴（治本、web_server 零改）
新增 `_SHADOW_SUFFIX = " (測試)"` 常數與 P3 私有 `_translate_title(title_bare, inj, tr, is_shadow)`：先以 `_title_bare`（L716 現成變數）呼 `translate_unit`，**LLM 全程不見後綴** → 輸出恆乾淨；若為影子軌（`_is_shadow_title` ＝ `title.strip() != _title_bare`）且譯文未帶後綴 → **由本處唯一重貼一次**。whole（L822）與 section（L838）兩分支同式改造；is_zh 分支 `translated_title = title` 原樣（無 LLM 介入、後綴自然保留）。

**根因釐清（tasks §3 問題 #4 之 grep 更正）**：plan v4 §2 稱「web_server 無防重」與現況不符——`web_server.py:775` 早由 **PIPE-RESUME SHADOW-HOTFIX-2** 落地 `endswith(" (測試)")` 守衛。真正病根是 P3 把**帶後綴** title 餵 LLM，LLM 可能回**變體**（全形 `（測試）`／空格差異／譯寫）→ 半形 `endswith` 失配 → web_server 再 append 成雙。改餵 bare 後變體不再產生、既有守衛恰好命中一次。**`web_server.py` 本案零改**（git diff 實證）。

### R8 — P3 單點行級圖片過濾（三通道收斂 + 雙語對稱不變式）
新增 `_filter_source_figures(ctx, text)`，接線於 `full_text = _read_source_text(ctx)` 與 `strip_title_echo` 之後、`is_zh` 分支之前（單點）。逐行以 `ingestion_engine._FIGURE_RE`（**複用引擎同一 regex、語意一致**）比對，命中且 `fig_filter(src, alt)` 回 False → **刪該行**。

**同基準保證**：`images_root = output_dir/"images"`——`_read_source_text` 之 md_path 亦位於同一 `output_dir`，故與 P1 `_build_tiles` 之 `md_path.parent/"images"` 為**同一路徑基準**，兩路 KEEP/DROP 判定必然一致。旗標關（`make_figure_filter` 回 None）→ 整段 no-op、byte 等價；任何解析/IO 異常 → `logger.warning(exc_info=True)` 後 **fail-open 回原文**。

**一次覆蓋三消費者**：`full_text` 為 P1 原始 md（未經 `_build_tiles` 的 figure_filter），而 P3 三處皆以之為素材——is_zh 分支 `zh_text=full_text`（L797）／whole 模式 `translate_whole(full_text)`（L818）／**`en_text=full_text`（L843、無條件）**。單點過濾即三路同收，並立 **「section mode 雙語圖片對稱」不變式**：zh 側走過濾後 tiles 重建、en 側走此處過濾後原文 → 兩側圖集相同（測試強斷言）。

## §5 測試與 Grep 結果

```
tests/test_litedoc_pipeline.py：122 passed（113 既有 + 9 新增）in 0.71s
全套件：967 passed, 3 skipped, 3 warnings in 67.25s   ← 基線 958 + 9、零回歸
```

新增 9 測試：
- **R4 ×3**：`test_translate_unit_receives_bare_title`（spy 捕捉 → 譯題輸入**全無後綴**、成品恰一個）／`test_non_shadow_title_gets_no_suffix`（非影子不加）／`test_translator_variant_output_still_single_suffix`（**LLM 回全形 `（測試）` 變體時，半形後綴仍恰一個**——直擊雙後綴根因）
- **R8 ×5**：`test_whole_mode_drops_junk_keeps_hero`（4 圖 → 三垃圾 DROP、hero 留、zh/en 雙側同步、正文零損）／`test_flag_off_is_noop_byte_equivalent`（旗標關 → 四圖原樣）／`test_fail_open_on_filter_exception`（工廠拋例外 → 全保留）／`test_is_zh_branch_also_filtered`（zh 路同收）／`test_missing_image_file_fail_open_keeps_line`（圖檔缺失 → filter fail-open KEEP）
- **雙語對稱 ×1**：`test_section_mode_en_zh_figure_sets_identical`（section mode 下 `final_en` 圖集 ≡ `final_zh` 圖集 ≡ tiles 過濾後圖集）

驗收 grep（§6.3 全項）：

```
R4：L822/L838 兩處 → self._translate_title(_title_bare, inj, tr, _is_shadow_title)  ✅
    （`translate_unit(title,…)` 舊呼叫零殘留；L758 為 docstring、L635 為 helper 內以 bare 呼叫）
R8：make_figure_filter 兩處 → L394（P1 _build_tiles）+ L652（P3 單點）  ✅
web_server：git diff --stat → 零 diff  ✅（防重已存在、本案零改）
範圍自檢：git status -s（排除 .claude-logs）＝ litedoc_pipeline.py + test_litedoc_pipeline.py  ✅
```

SOP 一致性核查（§6.5）：

```
logging：grep logger.error/exception/traceback.format_exc → 無命中（合規）；
         新增 R8 fail-open warning 含 exc_info=True（全檔 exc_info=True 計 12 處）
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/pdf_processor.py`／`processor/fitz_processor.py`／`pipelines/section_engine.py`／`pipelines/ingestion_engine.py`／`pipelines/image_filter.py`／`contracts.py` — 零改
- [x] **`web_server.py` — byte 不動**（防重 `web_server.py:775` 已由 SHADOW-HOTFIX-2 落地、git diff 實證零）
- [x] R8 `images_root` 與 P1 `_build_tiles` 同一路徑基準；旗標關 no-op、異常 fail-open
- [x] R4 譯題第一參數為去後綴 `_title_bare`；影子軌譯後重貼恰一次
- [x] resume／slides／book／academic 各路 — 零碰
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / C1 / C2 / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C_CHECKOUT — 收官歸檔**（Conformance〔plan v4 §2 八刀對照〕+ **§7.2 跨 Phase 整合測試**〔tasks §6.4：實體 born-digital PDF 串接 R1-R8 端到端〕+ TODO 雙層結案 + baton 一次性歸檔）；待 baron ship C3 後另下 checkout 提示詞。
- baron 影子 E2E（收官後、plan §8.2）：SpaceX 樣本驗標題／`#`+`##`×4+`###`×3 結構／零 meta 重播與 nav 與計數雜訊／垃圾小圖消失且 hero 在／恰一個 `(測試)`；另傳 <15k 短文驗 whole 路圖片過濾（R8 雙通道同享之 E2E 證）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、2 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-1_C3_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C3_msg.txt
```
