# IMG-FILTER C1 — Image Filter Module（圖片過濾器模組）執行報告

---

**任務代號**：IMG-FILTER C1
**執行日期**：2026-07-20
**依據規劃**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`（§8 C1）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `0fab08a`（GLOSSARY-TERMMAP checkout）。litedoc 圖片全保留（PIPE-INGEST 交付）但站台 chrome 垃圾圖一併入文；過濾器不存在。
- **完成狀態**：新增 `pipelines/image_filter.py`（stdlib PNG/JPEG header 尺寸解析＋三規則閉包工廠＋fail-open＋DROP 審計 log）＋`settings.py` 三常數（**plan v2 校正值**）＋`.env.example` IMG-FILTER 段＋`tests/test_image_filter.py` 17 測試全綠。**純加法零接線**（`grep -rn "image_filter" pipelines/ingestion_engine.py pipelines/litedoc_pipeline.py` → 0 命中）、零第三方影像依賴、零 runtime 變化；全套件 **822 passed**（基線 805＋17、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.1（過濾器六硬規格）＋§2.4（三常數）；無偏離——門檻採校正值（100000／4.0／廢長邊軸、tasks §7 禁令遵守）、路徑解析 `Path(src).name`（review 硬要求）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pipelines/image_filter.py` 三規則過濾器＋settings 三常數＋.env.example＋`tests/test_image_filter.py`（17 測試、含 481×369 KEEP 守門） | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/image_filter.py` | —（全新檔、無需備份） | `_read_image_size`（stdlib 雙格式）＋`make_figure_filter`（三規則閉包工廠） |
| 新建 | `tests/test_image_filter.py` | —（全新檔、無需備份） | 17 測試：尺寸解碼 ×4／三規則 ×6／fail-open ×3／開關與審計 ×4 |
| 修改 | `settings.py` | `.claude-logs/archive/2026-07-20_IMG-FILTER_C1_settings.py.bak` | `IMG_FILTER_ENABLED`（true）／`IMG_FILTER_MIN_AREA`（100000）／`IMG_FILTER_MAX_ASPECT`（4.0）＋校正依據行註 |
| 修改 | `.env.example` | `.claude-logs/archive/2026-07-20_IMG-FILTER_C1_env.example.bak` | 檔尾 IMG-FILTER 段（三常數＋單點關回方式） |

> ⚠️ 兩 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `_read_image_size` — stdlib 二進位 header 解析（零 Pillow）

- **PNG**：驗 8-byte 簽名後直接 `struct.unpack(">II", head[16:24])` 取 IHDR 寬高——**僅讀前 24 bytes**、零全檔載入。
- **JPEG**：自 SOI（`\xff\xd8`）起以檔案指標掃 marker 段——padding `0xFF` 吸收、無長度段（SOI/TEM/RSTn）跳過、一般段以 `f.seek(seg_len - 2, 1)` **跳段不讀 payload**；命中 SOF0-SOF15（跳 C4/C8/CC）→ `struct.unpack(">HH")` 取 (h, w)；**遇 SOS（0xDA、壓縮資料起點）或 EOI（0xD9）立即終止回 None**——防止對大圖檔做無效全檔遍歷（防無效 I/O 之核心優化、tasks §8 C1 規格）。
- 不支援格式（如 GIF）回 None；檔案缺失／IO 異常上拋、由工廠閉包捕捉走 fail-open。

### §4.2 `make_figure_filter` — 三規則閉包工廠

```python
if enabled is None: enabled = settings.IMG_FILTER_ENABLED
if not enabled: return None          # 總開關關 → 呼叫端不注入、行為零變
...
def _filter(src, alt=""):
    if src in header_set:            # 規則③（不需讀檔）
        logger.info("[img-filter] DROP 規則③報頭區 src=%s", src); return False
    path = root / Path(src).name     # review 硬要求：basename 解析
    ...（fail-open ×3：異常／None／非正尺寸 → KEEP＋warning）
    if area < area_floor:  ...DROP＋log（src＋WxH＋area＋規則①）
    if aspect > aspect_cap: ...DROP＋log（規則②）
    return True
```

規則判定順序 ③→①→②（③ 零 IO 先行）；門檻**嚴格小於／嚴格大於**（邊界值 KEEP、測試釘死）；DROP 一律 `logger.info` 含 src＋實測尺寸＋命中規則（審計不靜默）。

### §4.3 settings／.env.example

三常數含校正依據行註（「⚠️ 廢除 spec F7 原始門檻——會誤殺 481×369 內容 chart」實錨入代碼註解）；`.env.example` 段落含關回方式。措辭修正一處：模組與 env 註解初版含路由字面量、與 §6.1「零文體字面量 grep=0」驗收衝突 → 改「文字攝入家族／文字攝入路」泛稱（行為零差）。

### §4.4 `tests/test_image_filter.py` — 17 測試

header-only 構造法（PNG＝簽名＋IHDR、JPEG＝SOI＋APP0＋SOF0——`_read_image_size` 僅讀 header、不需合法完整圖）。關鍵斷言：**`test_rule1_area_drop_and_keep_guard`（481×369＝177k 必 KEEP、門檻校正守門）**；邊界值 `area==min_area`／`aspect==max_aspect` 皆 KEEP；`test_jpeg_no_sof_terminates`（SOS 終止防無效遍歷）；規則③大圖在報頭仍 DROP／不在則走①②；任一命中即 DROP 三連；fail-open ×3；`enabled=False`→None＋settings 預設讀取；DROP log 含 src＋尺寸＋規則（caplog）＋KEEP 靜默。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M .claude-logs/TODO.md
 M .env.example
 M settings.py
?? .claude-logs/archive/2026-07-20_IMG-FILTER_C1_env.example.bak
?? .claude-logs/archive/2026-07-20_IMG-FILTER_C1_settings.py.bak
?? pipelines/image_filter.py
?? tests/test_image_filter.py
```

### §5.2 新測試（實貼）

```
tests/test_image_filter.py — 17 items 全數 PASSED
（TestReadImageSize ×4 / TestRules ×6 / TestFailOpen ×3 / TestSwitchAndAudit ×4）
============================== 17 passed in 0.52s ==============================
```

### §5.3 全套件（實貼）

```
822 passed, 3 skipped, 3 warnings in 55.93s
```

基線 805 passed → **822 passed（+17、0 failed、零回歸）**。

### §5.4 §6.1 驗收 grep（實貼）

```
--- 入口
pipelines/image_filter.py:37:def _read_image_size(...)
pipelines/image_filter.py:84:def make_figure_filter(
--- 三常數（settings + .env.example 兩檔命中）
settings.py:127/:130/:132、.env.example:84/:87/:89
--- 零接線（期望 0 命中）
grep -rn "image_filter" pipelines/ingestion_engine.py pipelines/litedoc_pipeline.py → 0 matches（exit=1）
--- 零文體字面量（期望 0）
grep -c "doc_type\|litedoc\|resume\|slides" pipelines/image_filter.py → 0
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <三檔>
無命中（合規）——DROP 走 logger.info 審計、fail-open 走 logger.warning（IO 異常含 exc_info=True）
--- database：grep -nE "\.commit\(\)" <三檔> | grep -v "with .*session.*begin()"
無命中（合規）——模組零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `pipelines/ingestion_engine.py`、`pipelines/litedoc_pipeline.py` — 零改（C1 零接線、grep 實證）
- [x] 純加法（新模組＋常數＋測試）；零 Pillow／零第三方影像套件（stdlib struct 解析）
- [x] 門檻＝plan v2 校正值（100000／4.0／廢長邊軸）——spec F7 原始門檻未使用（tasks §7 禁令）
- [x] `section_engine`／三路 pipeline／A 軌鏈／contracts／models — 零碰
- [x] Vision 不參與 DROP 決策（模組零 LLM）
- [x] 既有 tests 斷言本體 — 零改（僅新增測試檔）

---

## §7 銜接

- **baton 狀態**：本報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add（Checkout 一次性歸檔）。
- **hash 自癒**：GLOSSARY-TERMMAP checkout 已 ship＝`0fab08a`、雙源佔位符已回填歸零。
- **自評（正向）**：推進 plan v2 §2.1／§2.4——過濾器本體與門檻防線就緒、為 C2（engine 注入點）備妥唯一前置；門檻校正禁令物理落入代碼行註與測試守門。**（負向防錯）**：三規則對 SpaceX 分布完美、對其他版型泛化性待 C3 接線後 E2E 第二樣本驗證（plan §5 已列、env 可調兜底）。
- **下一步**：C2 — Engine Figure-Filter Hook（引擎純加法注入點）；等 baron 確認本 commit 後另行下達 C2 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質修改/新增之代碼、新測試與備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add .env.example
git add pipelines/image_filter.py
git add tests/test_image_filter.py
git add .claude-logs/archive/2026-07-20_IMG-FILTER_C1_settings.py.bak
git add .claude-logs/archive/2026-07-20_IMG-FILTER_C1_env.example.bak

# 3. commit message 草稿（已寫入 /tmp/IMG-FILTER_C1_msg.txt）
cat > /tmp/IMG-FILTER_C1_msg.txt << 'EOF'
BE-Refactor: IMG-FILTER C1 — Image Filter Module（圖片過濾器模組）

1. 於 settings.py 增設 IMG_FILTER_ENABLED/MIN_AREA/MAX_ASPECT 三項環境變數（預設分別為 true/100000/4.0），並於 .env.example 同步更新說明及單點關回方式。
2. 新建 pipelines/image_filter.py，實作二進位 stdlib 解析 PNG（IHDR 段）與 JPEG（SOF 區段掃描且遇 SOS/EOI 終止優化）尺寸功能，零第三方套件依賴。
3. 實作 make_figure_filter 工廠方法提供面積、長寬比、及報頭位置三幾何規則之閉包過濾判定，保障 fail-open（解析失敗則 KEEP）及 logger.info 丟棄審計。
4. 新建 tests/test_image_filter.py 單元測試覆蓋多格式尺寸解碼、門檻臨界點過濾判定、fail-open 容錯與審計日誌 caplog 斷言。
EOF

# 4. baron 手動執行
git commit -F /tmp/IMG-FILTER_C1_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-20)：C1 執行完成——過濾器本體＋三常數＋17 測試、822 passed 零回歸、SOP 雙核查合規、純加法零接線、門檻校正禁令落地
