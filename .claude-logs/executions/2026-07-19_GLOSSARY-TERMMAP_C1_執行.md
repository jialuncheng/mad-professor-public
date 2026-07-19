# GLOSSARY-TERMMAP C1 — Termmap Builder（術語定案表產生器）執行報告

---

**任務代號**：GLOSSARY-TERMMAP C1
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`（§8 C1）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `3133333`（PIPE-INGEST checkout）。glossary 機制僅有摘要對抽詞之 `extract_terms`（漏 body 長尾）、三路 `_heal_glossary` 各帶飛輪早退、無事前定案 builder。
- **完成狀態**：`GlossaryManager.build_termmap` 五步落地（N1 段落切塊／N2 並行 census 只認詞／N3a `_normalize_key` 去重／N3b 分流已知∪未知**廢早退**／N4 未知一次批次翻譯／N5 `source="termmap_decided"` 定案 upsert）＋ `settings.GLOSSARY_CENSUS_CHUNK_CHARS=6000`＋新測試檔 13 測試全綠。**純加法零接線**（`grep -rn "build_termmap" pipelines/` → 0 命中）、旗標維持關閉、零 runtime 變化；全套件 **793 passed**（基線 780＋13、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.1（builder 五步硬規格）；無偏離——LLM 全在 DB 交易外、term_key 三方同一正規化函式（§4 契約）、整體失敗降級回 `query_cascade`。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `GlossaryManager.build_termmap` 五步 builder＋census 常數＋`tests/test_glossary_termmap.py`（13 測試、含 Q1 廢早退回歸） | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `settings.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_settings.py.bak` | 增 `GLOSSARY_CENSUS_CHUNK_CHARS`（預設 6000、Q3；旗標 L112 **零動**） |
| 修改 | `processor/glossary_extractor.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_glossary_extractor.py.bak` | 增雙 prompt＋`_split_census_chunks`／`_census_chunk`／`_translate_unknown_terms`／`build_termmap`；既有三函式零動 |
| 新建 | `tests/test_glossary_termmap.py` | —（全新檔、無需備份） | 13 測試：切塊 ×3／census ×2／去重分流 ×3（含 Q1）／翻譯定案 ×3／軟降級 ×2 |

> ⚠️ 兩 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存之 plan／tasks／本報告不在清單。

---

## §4 修法說明

### §4.1 `settings.py` — census 切塊常數

```python
# === [GLOSSARY-TERMMAP C1 START] ===
GLOSSARY_CENSUS_CHUNK_CHARS = int(os.getenv("GLOSSARY_CENSUS_CHUNK_CHARS", "6000"))
```

置於 `LLM_USE_GLOSSARY_ALIGN`（L112、零動）之後；註記 Q3 拍板與「census 召回 vs size-gate 兩獨立」。

### §4.2 `processor/glossary_extractor.py` — build_termmap 五步

- **雙 prompt 設計**：
  - `_CENSUS_SYSTEM_PROMPT`（N2）：專有名詞普查——人名／組織／產品／地名／作品名＋文件內高頻領域術語（Q5 界定）；「只認詞、**絕對不要翻譯**」；輸出 JSON 字串陣列、無可抽回 `[]`。
  - `_TERM_TRANSLATE_SYSTEM_PROMPT`（N4）：批次逐行 `[i] 譯法`、摘要對引導風格、「人名品牌慣例不譯者原樣輸出（譯法＝原文）」——為 C2 免括號約束備妥同字定案。
- **`build_termmap` 主流程**（關鍵片段）：

```python
# N3a 去重（與 query/upsert 同一 _normalize_key、接縫契約）
unique = {}
for t in census:
    key = self._normalize_key(t)
    if key and key not in unique:
        unique[key] = t.strip()
# N3b 分流：已知 ∪ 未知（廢早退——已知照收、未知照抽）
known = self.query_cascade(source_lang, target_lang, domain=domain)
unknown_originals = [orig for key, orig in unique.items() if key not in known]
# N4 僅未知一次批次翻譯；N5 定案 upsert
new_pairs = self._translate_unknown_terms(unknown_originals, abstract, translated_abstract)
if new_pairs:
    self.upsert_terms(list(new_pairs.items()), ..., source="termmap_decided")
return {**known, **{self._normalize_key(k): v for k, v in new_pairs.items()}}
```

- **N1**：`_split_census_chunks` 以 `\n\n` 段落累積、超長單段自成一塊、不切句中。**N2**：`ThreadPoolExecutor`（workers=`max_workers or settings.LLM_MAX_CONCURRENT`、底層受 `_api_semaphore` 限流）逐塊並行、單塊失敗 `logger.warning(exc_info=True)` soft。**整體失敗**：`logger.error(exc_info=True)` 後**降級回 `query_cascade`**（不阻斷上游）。
- **SOP**：LLM 呼叫全在 DB 交易外（N5 走既有 `upsert_terms` 之 `session.begin()` 極短交易）；新增 error/warning 均含 `exc_info=True`；既有 `query_cascade`／`extract_terms`／`upsert_terms` 三函式**零動**。

### §4.3 `tests/test_glossary_termmap.py` — 13 測試

沿 `test_glossary_core` file-based SQLite fixture 範式＋路由式 `_TermmapMockLLM`（census／翻譯雙路、call count 追蹤）。關鍵斷言：
- **`test_no_early_return_when_db_has_terms`（Q1 廢早退回歸）**：DB 先種 `starship→星艦` → build_termmap 仍 census、僅 `Raptor` 入翻譯、已知沿用 DB 定譯、新詞寫庫（飛輪滾動實證）。
- `test_known_terms_zero_translate_calls`（已知免翻、translate_calls==0）／`test_single_batch_translate_call`（3 未知詞仍 1 次呼叫）／`test_upsert_source_termmap_decided`／`test_identical_translation_preserved`（`SpaceX→SpaceX` 同字定案、供 C2 免括號消費）／軟降級 ×2（builder 失敗回級聯、N4 失敗僅交付已知且**未寫入任何收割物**）。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M .claude-logs/TODO.md
 M processor/glossary_extractor.py
 M settings.py
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_glossary_extractor.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_settings.py.bak
?? tests/test_glossary_termmap.py
```

### §5.2 新測試（實貼）

```
tests/test_glossary_termmap.py::TestSplitCensusChunks::test_paragraph_boundary_accumulation PASSED
tests/test_glossary_termmap.py::TestSplitCensusChunks::test_oversized_single_paragraph_own_chunk PASSED
tests/test_glossary_termmap.py::TestSplitCensusChunks::test_short_text_single_chunk_and_empty PASSED
tests/test_glossary_termmap.py::TestCensus::test_census_prompt_forbids_translation PASSED
tests/test_glossary_termmap.py::TestCensus::test_single_chunk_failure_is_soft PASSED
tests/test_glossary_termmap.py::TestDedupAndSplit::test_normalize_dedup_multiform PASSED
tests/test_glossary_termmap.py::TestDedupAndSplit::test_no_early_return_when_db_has_terms PASSED
tests/test_glossary_termmap.py::TestDedupAndSplit::test_known_terms_zero_translate_calls PASSED
tests/test_glossary_termmap.py::TestTranslateAndDecide::test_single_batch_translate_call PASSED
tests/test_glossary_termmap.py::TestTranslateAndDecide::test_upsert_source_termmap_decided PASSED
tests/test_glossary_termmap.py::TestTranslateAndDecide::test_identical_translation_preserved PASSED
tests/test_glossary_termmap.py::TestSoftDegrade::test_builder_failure_falls_back_to_cascade PASSED
tests/test_glossary_termmap.py::TestSoftDegrade::test_translate_failure_returns_known_only PASSED

============================== 13 passed in 0.44s ==============================
```

### §5.3 全套件（實貼）

```
793 passed, 3 skipped, 3 warnings in 51.90s
```

基線 780 passed → **793 passed（+13、0 failed、零回歸）**。

### §5.4 §6.1 驗收 grep（實貼）

```
--- build_termmap 入口
processor/glossary_extractor.py:331:    def build_termmap(
--- census 常數（settings 定義 + builder 消費）
settings.py:119:GLOSSARY_CENSUS_CHUNK_CHARS = int(os.getenv("GLOSSARY_CENSUS_CHUNK_CHARS", "6000"))
processor/glossary_extractor.py:357:            cc = chunk_chars or settings.GLOSSARY_CENSUS_CHUNK_CHARS
--- pipelines 零接線（期望 0 命中）
grep -rn "build_termmap" pipelines/ → 0 matches（exit=1）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" processor/glossary_extractor.py settings.py tests/test_glossary_termmap.py
glossary_extractor.py:138/:171/:245（既有三處、原即含 exc_info=True）/:407（本次新增、含 exc_info=True）
→ 全數合規（error 必含 exc_info；無 traceback.format_exc）
--- database：grep -nE "\.commit\(\)" <三檔> | grep -v "with .*session.*begin()"
無命中（合規）——寫入僅經既有 upsert_terms 之 session.begin() 極短交易；LLM 全交易外
```

---

## §6 不可動清單遵守狀態

- [x] `models.py` GlobalGlossary 表定義（聯合唯一約束）— 零改
- [x] `pipelines/contracts.py` 凍結合約 — 零改
- [x] 三路 Pipeline 零接線（仍呼舊 `_heal_glossary`、grep 實證 §5.4）；旗標 `LLM_USE_GLOSSARY_ALIGN` 預設維持 false — 零改
- [x] LLM 呼叫全在 DB 交易外（census／批次翻譯皆無 session 持有）
- [x] `glossary_extractor` 既有三函式簽名與行為 — 零改（純加法追加）
- [x] `prompt/translate/*.txt` 母提示詞／A 軌鏈／section_engine／ingestion_engine — 零改
- [x] 既有 tests 斷言本體 — 零改（僅新增測試檔）

---

## §7 銜接

- **baton 狀態**：本報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add（Checkout 一次性歸檔）。
- **hash 自癒**：PIPE-INGEST checkout 已 ship＝`3133333`、雙源佔位符已回填歸零。
- **自評（正向）**：推進 plan v2 §2.1 全部五步＋Q1/Q3/Q5 三拍板落地；為 C2（litedoc 收斂）備妥唯一前置——含同字定案（`SpaceX→SpaceX`）供免括號約束消費。**（負向防錯）**：census／翻譯品質僅以 mock 驗規格、真 LLM 召回率待 C5 旗標點火後 baron 影子 E2E 實測（plan §8.2）。
- **下一步**：C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）；等 baron 確認本 commit 後另行下達 C2 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質修改之代碼、新測試與備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add processor/glossary_extractor.py
git add tests/test_glossary_termmap.py
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_settings.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_glossary_extractor.py.bak

# 3. commit message 草稿（已寫入 /tmp/GLOSSARY-TERMMAP_C1_msg.txt）
cat > /tmp/GLOSSARY-TERMMAP_C1_msg.txt << 'EOF'
BE-Refactor: GLOSSARY-TERMMAP C1 — Termmap Builder（術語定案表產生器）

1. 於 settings.py 中新增 GLOSSARY_CENSUS_CHUNK_CHARS 環境變數設定（預設為 6000），作為術語 census 切塊字元上限。
2. 於 processor/glossary_extractor.py 中建立 GlossaryManager.build_termmap 共用 builder，實作切塊、逐塊純 LLM census（只抽不翻）、去重、DB 分流（已知與新詞）、未知詞批次翻譯、以及 upsert 定案表的完整五步流，廢除早退快取邏輯，確保飛輪自癒學習。
3. 建立 tests/test_glossary_termmap.py 覆蓋 builder 全流程切分、分流、翻譯次數、upsert 及軟降級規格，特別包含廢早退回歸自癒測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/GLOSSARY-TERMMAP_C1_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C1 執行完成——build_termmap 五步＋13 測試、793 passed 零回歸、SOP 雙核查合規、純加法零接線
