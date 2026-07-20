# PIPE-INGEST-FITZ C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）執行報告

---

**任務代號**：PIPE-INGEST-FITZ C3
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md` §8 C3
**上游 plan**：同名 `_plan.md`（v2、六 OQ 拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C3)

---

## §1 基準與完成狀態

- 基準 commit：`ff7bf3f`（PIPE-INGEST-FITZ C2、baron 已 ship）
- 完成狀態：代碼與測試已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 工作區自檢：`git status -s`（排除 .claude-logs）＝恰為本 commit 4 檔（`.env.example` / `pipelines/litedoc_pipeline.py` / `settings.py` / `tests/test_litedoc_pipeline.py`）

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor（Fitz 直抽處理器） | `3cc3850` |
| C2 | Ligature Repair（連字修復純函式） | `ff7bf3f` |
| C3 | Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `settings.py` | 修改 | 三常數（IMG-FILTER 區塊後、L135-146） |
| `.env.example` | 修改 | 快速道/門檻/修復三項 kill-switch 註記 |
| `pipelines/litedoc_pipeline.py` | 修改 | import 2 模組 + `run_phase1` ① 改 `_ingest_markdown` 閘門 + ②' 修復步 + 新私有 `_ingest_markdown` |
| `tests/test_litedoc_pipeline.py` | 修改 | +6 測試（閘門三態/flag off byte 等價/修復接線/§7.2 整合） |
| `.claude-logs/archive/2026-07-21_PIPE-INGEST-FITZ_C3_settings.py.bak` 等 4 檔 | 備份 | 改前 `.bak` ×4（隨本 commit git add） |

（baton 暫存之 plan/tasks/報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

1. **文字層閘門（`_ingest_markdown`、P1 ① 唯一呼叫點改造）**：`LITEDOC_FITZ_ENABLED` 開啟時先呼 `fitz_processor.median_page_chars(pdf)`——中位數 ≥ `LITEDOC_FITZ_MIN_CHARS_PER_PAGE`（150）判 born-digital → `FitzProcessor().parse`（`logger.info` 路由審計）；未達標 → info 後走既有 `PDFProcessor()`（MinerU）。
2. **fail-open 降級**：閘門判定與 fitz 直抽整段包 `try/except Exception`——任何異常（壞檔、字型怪癖、fitz 內部錯誤）→ `logger.warning(..., exc_info=True)` 後**退 MinerU 續行**、絕不讓新 impl 阻斷攝入；flag off 時完全不諮詢 `median_page_chars`（測試以 raising spy 鎖住）、行為與現行 byte 等價。
3. **連字修復接線（②' 步、清洗後判型前）**：`LITEDOC_LIGATURE_REPAIR_ENABLED` 開啟時，`MarkdownCleaner().clean` 之後、`DocAnalyzer().analyze` 之前對 md 檔整檔 `repair_ligatures` 行內改寫——兩攝入來源（fitz／MinerU）同享修復；因行數不變式，判型 sidecar 行索引與後續 `assemble`／`_collect_header_srcs` 行界同基準（§7.2 整合測試以「修復前行號建 sidecar → 修復後判型分離仍正確」實證）。
4. **P1 ③-⑦ 零動**：analyze／`_build_tiles`／cover-prompt（meta 純正文）／source_lang／旁路全部原樣。

## §5 測試結果

```
tests/test_litedoc_pipeline.py：50 passed（44 既有 + 6 新增）in 0.75s
全套件：875 passed, 3 skipped, 3 warnings in 54.72s   ← C2 後基線 869 + 6、零回歸
```

新增 6 測試：
- `test_p1_gate_born_digital_routes_fitz`（三態①：median 500 → fitz、MinerU 零呼）
- `test_p1_gate_sparse_routes_mineru`（三態②：median 10 → MinerU）
- `test_p1_gate_fitz_failure_fails_open_to_mineru`（三態③：直抽拋例外 → warning **帶 exc_info** 斷言 + 退 MinerU + spec 正常交付）
- `test_p1_flags_off_byte_equivalent_regression`（雙 flag off：median 以 raising spy 鎖「不得被諮詢」+ md byte 原樣）
- `test_p1_ligature_repair_wired_after_clean`（MinerU 路 md 之 `;rst Pro1les de1ning` 全修）
- `test_seam_fitz_ingest_key_changing_integration`（**§7.2**：實體 PDF〔H1+連字損毀+跨頁頁首 URL+400×300 圖〕→ 真 FitzProcessor → 真 MarkdownCleaner → 真 repair〔行數不變式斷言〕→ 修復前行號建判型 sidecar → 真 `_build_tiles`〔真 ingestion_engine + image_filter + tiling bypass〕——斷言連字已修、頁首已剪、title 行界分離未移位、圖穿透 image_filter KEEP、正文零損）

驗收 grep（§6.3 全項）：

```
settings.py L138/141/144 三常數 ✅
litedoc_pipeline.py L166 repair_ligatures / L241 median_page_chars / L244 FitzProcessor ✅
git diff --stat pdf_processor.py md_cleaner.py resume_pipeline.py slide_pipeline.py → 零 diff ✅
test_seam_fitz_ingest_key_changing_integration @ tests/test_litedoc_pipeline.py:923 ✅
```

SOP 一致性核查（§6.4）：

```
logging：grep logger.error/exception/traceback.format_exc @ litedoc_pipeline.py → 無命中（合規）；
         新增之 logger.warning（fail-open）含 exc_info=True（測試斷言 record.exc_info 鎖住）
database：grep "\.commit()" @ 三改動檔 → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/pdf_processor.py` / `processor/md_cleaner.py` — byte 不動（git diff 零）
- [x] `pipelines/resume_pipeline.py` / `pipelines/slide_pipeline.py` — byte 不動（git diff 零）
- [x] P1 ③-⑦ 步序、cover-prompt 純正文原則、`classify_source_lang` — 零動（接線僅 ①/②' 段）
- [x] `pipelines/ingestion_engine.py` / `image_filter.py` / `section_engine.py` — 零動
- [x] 零 `fitz.metadata`、零新依賴
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / C1 / C2 / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C_CHECKOUT — 收官歸檔**（Conformance + TODO 雙層結案 + baton 一次性歸檔）；待 baron ship C3 後另下 checkout 提示詞。
- baron 影子 E2E（收官後、plan §8.2）：重傳 SpaceX 樣本驗 fitz 路 log／publisher=a16z／連字消失；掃描樣本驗退 MinerU；`LITEDOC_FITZ_ENABLED=false` 應急實測。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、4 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add settings.py
git add .env.example
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_PIPE-INGEST-FITZ_C3_settings.py.bak
git add .claude-logs/archive/2026-07-21_PIPE-INGEST-FITZ_C3_env.example.bak
git add .claude-logs/archive/2026-07-21_PIPE-INGEST-FITZ_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_PIPE-INGEST-FITZ_C3_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST-FITZ_C3_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST-FITZ_C3_msg.txt
```
