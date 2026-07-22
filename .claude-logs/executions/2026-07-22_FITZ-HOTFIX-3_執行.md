# FITZ-HOTFIX-3 — Overlap Dedup, Chrome Hint & Meta Zeroing（同位重繪去重、chrome 線索回收與 full_text meta 歸零）執行報告

---

**任務代號**：FITZ-HOTFIX-3
**執行日期**：2026-07-23
**依據規劃**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md`（修法 K1/K2/K3、v3 定稿）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit HOTFIX-3)

---

## §1 基準與完成狀態

- 基準 commit：`18eb19f`（FITZ-HOTFIX-2 checkout、baron 已 ship）
- 完成狀態：K1 + K2 + K3 已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 範圍自檢：`git status -s`（排除 .claude-logs）＝恰為 `processor/fitz_processor.py`／`pipelines/litedoc_pipeline.py` + 兩測試檔

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3 | Overlap Dedup, Chrome Hint & Meta Zeroing（同位重繪去重、chrome 線索回收與 full_text meta 歸零） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `processor/fitz_processor.py` | 修改 | K1 `_collect_page` 同位去重；K2 `_URL_RE`／`_assemble` 回收 chrome_urls／`parse` 落 sidecar |
| `pipelines/litedoc_pipeline.py` | 修改 | K2 `_load_source_hints`＋`_extract_litedoc_metadata(hints=)` 截斷後拼接；K3 `_strip_meta_source_lines`＋`_locate_doc_structure`＋`_collect_p3_meta_values`＋P3 接線 |
| `tests/test_fitz_processor.py` | 修改 | +5 測試（K1 ×3／K2 ×2） |
| `tests/test_litedoc_pipeline.py` | 修改 | +10 測試（K2 ×4／K3 ×6）＋1 spy 簽名純加法對齊 |
| `.claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_*.bak` ×4 | 備份 | 改前快照（隨本 commit git add） |

（baton 暫存之 hotfix/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

### K1 — `_collect_page` 同位重繪去重（治標題全滅）
**真因（四環）**：NHK 標題帶 text-stroke → 瀏覽器列印同座標重繪 ×4 → fitz 忠實抽 4 份 → 全判 h1 → md 出現 `# 標題` ×4 → **`md_cleaner` 浮水印規則**（同 heading ≥3 次全殺）誤殺真標題八行 → cover-prompt 讀無標題 md、退回 NHK 話題標籤「大谷翔平」。A 軌沒中＝MinerU 自帶去重；R2 沒防＝R2 管跨頁、本案是同頁同座標（不同物種）。

**修法**：`_collect_page` 收行時加 `dedup_key = (text, round(y0,1), round(x0,1), round(size,1))`、`seen_lines` **每頁獨立初始化**——精確同座標同字級同文字之重疊副本只留一份；合法重複（異座標）key 不同、零影響；**每頁獨立故不干涉跨頁 chrome（R2 管轄）**。`md_cleaner` 本體零改（其治 MinerU 路浮水印有戰功、病根在 fitz 供給端）。

### K2 — chrome URL 線索回收（治 publisher 空白）
**真因**：NHK 身份僅存於 logo 圖 + 列印頁尾 URL chrome；R2 正確剝除跨頁重複 URL → cover-prompt「URL→publisher 解碼」無米之炊。

**修法（fitz 端）**：`_assemble` 於 chrome 剝除點以 `_URL_RE` 捕 URL 入 `chrome_urls`、`_assemble` 回傳 `(chunks, chrome_urls)`、`parse` 落 `{pdf_file.stem}_source_hints.json` sidecar（best-effort、缺之無害）。**（litedoc 端）**：`_load_source_hints(output_dir, pdf_path)` 三級 stem 定位（**嚴禁 paper_id**、影子後綴陷阱）；`_extract_litedoc_metadata` 增 `hints` 純加法參數（預設 `""` byte 等價）、**於 `[:_META_INPUT_CHARS]` 截斷之後拼接**——防長文（NHK md 15K）尾接 hint 被截掉靜默失效（v2 自查陷阱）。hint 只進 LLM 輸入、**不寫 md**（判型/行號基準零擾動）。

### K3 — P3 full_text 行級 meta 歸零（治 en 側洩漏＋雙語文字對稱）
**真因（族群）**：R6 meta 歸零只掛 `assemble`（tiles 路）；P3 `en_text=full_text`（所有模式）＋whole/is_zh 之 zh 側素材＝原始 md、只經 echo-strip（僅剝標題+緊隨）與 R8 圖片過濾——**meta 原文行沒人管**。SpaceX v3 鐵證：`shadow_en.md` `MARC ANDREESSEN`/`JUN 15` 重播、`shadow_zh.md` 零命中（雙語文字不對稱）。

**修法**：`_strip_meta_source_lines(ctx, text)` **雙判據**——① sidecar 判型 spans（type ∈ `_HEADER_META_TYPES` 之行號區間）；② 值比對（`ingestion_engine.normalize_meta_values`／`_normalize_meta_text` **整行相等**、非子字串、複用 R6 同一正規化源）。任一命中刪行；sidecar 缺→僅值比對／值集空→僅 spans／兩缺→no-op（fail-open）；**圖片行不碰**（歸 R8）。

**接線順序（關鍵）**：掛於 `_read_source_text` 之後、**echo-strip 與 R8 之前**——K3 以 sidecar **行號**比對，必須作用在與 sidecar 同基準之**原封 md 行序**上（echo-strip/R8 刪行位移前、與 hint 截斷同款陷阱、設計期先堵）。三消費者（en_text／whole zh／is_zh zh）一次乾淨；section-mode zh（tiles 路、R6）本已乾淨 → **雙語文字對稱恢復**（與 HOTFIX-2 圖片對稱成對）。

## §5 測試與 Grep 結果

```
tests/test_fitz_processor.py：34 passed（29 既有 + 5 新增）
tests/test_litedoc_pipeline.py：149 passed（133 既有〔含 1 spy 簽名對齊〕+ 16 新增）
全套件：993 passed, 3 skipped, 3 warnings in 54.99s   ← 基線 978 + 15、零回歸
```

新增 15 測試：
- **K1 ×3**：同座標重繪 ×4 → 恰一份＋真 `MarkdownCleaner` 放行標題存活（**對照組：未去重 ×4 會被殺**）／合法重複（異座標）全保留／每頁獨立不越權跨頁（R2 協作）
- **K2 fitz ×2**：chrome URL 回收 sidecar／無 URL 頁零產出
- **K2 litedoc ×4**：stem 定位加載／缺檔回 `""`／**截斷窗斷言**（>8000 字 md → hint URL **仍在** LLM 輸入內）／`hints=""` byte 等價
- **K3 ×6**：meta 行剝除＋正文提及作者不誤殺／sidecar 缺退值比對／兩判據皆缺 no-op／**圖片行不碰**／**順序斷言**（K3 < echo-strip < R8）／**雙語文字對稱**（whole 模式 en 與 zh meta 行皆歸零）

驗收 grep：

```
K1：L213 seen_lines 每頁初始化／L248 dedup_key（text+座標+字級）  ✅
K2：L35 _URL_RE／L181 {pdf_file.stem}_source_hints.json／L515 [:_META_INPUT_CHARS] + (hints)  ✅
    `paper_id}_source_hints` → 零命中（影子後綴陷阱已避）  ✅
K3：L969 _strip_meta_source_lines  <  L973 strip_title_echo  <  L983 _filter_source_figures  ✅
不可動：md_cleaner/image_filter/ingestion_engine/rag_indexer → git diff 全零  ✅
範圍：git status -s（排除 .claude-logs）＝ fitz_processor + litedoc_pipeline + 兩測試檔  ✅
```

SOP 一致性核查：

```
logging：grep logger.error → 僅既有 fitz_processor:171（C1 解析失敗、含 exc_info=True）；
         K2/K3 新增 fail-open 皆 logger.warning(..., exc_info=True)；零 traceback.format_exc
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/md_cleaner.py` 浮水印規則本體／`WATERMARK_HEADING_THRESHOLD` — 零改（病根在 fitz 供給端）
- [x] cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` 六欄與規則 — 零改（K2 只增輸入、不改提示詞）
- [x] `pipelines/image_filter.py`／`pipelines/ingestion_engine.py`／`pipelines/section_engine.py`／`processor/rag_indexer.py` — git diff 全零
- [x] HOTFIX-1 八刀／HOTFIX-2 兩刀語意 — 零改；`PDFParser` ABC 簽名不變（sidecar 屬 side-effect、與 images/ 同類）
- [x] A 軌全鏈／resume／slides — 零碰
- [x] K1 每頁獨立、不干涉 R2 跨頁；K2 stem 基準非 paper_id；K3 接線在 echo-strip/R8 前（測試守衛）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：hotfix / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**checkout 收官**（Conformance + TODO 雙層結案 + baton 一次性歸檔）；待 baron ship HOTFIX-3 後另下 checkout 提示詞。
- baron 影子 E2E（收官後、hotfix §驗證）：① 重傳 NHK 樣本——標題＝完整日文系譯題＋恰一個 `(測試)`、**publisher=NHK**、date=2026-05-21、authors=0（誠實空）；log 驗 `[md_cleaner] 移除浮水印` **不再命中標題**；② SpaceX 回歸——標題/21 圖/meta 不退化＋**`shadow_en.md` grep `MARC ANDREESSEN`/`JUN 15` 歸零**、zh/en meta 行雙零對稱。
- 契約回灌：K1（同位去重）／K2（chrome 線索回收＋截斷後拼接）／K3（full_text meta 歸零＋族群鐵律「凡對 tiles 淨化必問 full_text」）併入 **PIPE-SYNC-6** 批次——待 E2E 綠燈、契約穩定後開。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、4 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add processor/fitz_processor.py
git add pipelines/litedoc_pipeline.py
git add tests/test_fitz_processor.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-3_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-3_msg.txt
```
