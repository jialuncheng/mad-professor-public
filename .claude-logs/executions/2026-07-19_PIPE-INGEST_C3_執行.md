# PIPE-INGEST C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）執行報告

---

**任務代號**：PIPE-INGEST C3
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md`（v4）
**次級參考**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md`（§8 C3）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `ca4e0e7`（PIPE-INGEST C2、P1 已切換引擎）。P3 section 模式譯題仍撈第一個 title slot（標題錯置三受害者病根）、post-strip 拿錯 key、cover-prompt 無 OCR 正規化、`_detect_source_lang` dead code 殘留、§7.2 整合測試未建。
- **完成狀態**：P3 譯題**唯一源＝P1 title**（section/whole 同式 `translate_unit`、slot 撈題方法廢除）；post-strip 隨之取得正確譯題 key（測試實證回聲被剝）；cover-prompt 增補 publisher 正規化／OCR 自癒／作者 Title Case 三規則；litedoc 之 source_lang 啟發式 dead code（含孤兒常數 `_CJK_MIN`/`_CJK_RATIO`）移除；§7.2 跨 Phase 整合測試（key-changing）落地。全套件 **780 passed**（C2 後基線 774 + 6、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v4 §2.3（譯題單一源）＋§2.8（publisher 正規化）＋§2.9（dead code）＋§8.1 §7.2 整合測試；無偏離。resume/slides 各自的 `_detect_source_lang`（活代碼、各自在用）零碰。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | P3 譯題單一源（廢 slot 撈題）+ cover-prompt 正規化三規則 + dead code 清理 + §7.2 key-changing 整合測試 ×3 + litedoc 測試更新 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_PIPE-INGEST_C3_litedoc_pipeline.py.bak` | P3 section 分支改 `translate_unit(title)`；廢除 slot 撈題方法；移除 source_lang 啟發式 dead code＋孤兒常數；cover-prompt 增三規則；docstring 同步 |
| 修改 | `tests/test_litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_PIPE-INGEST_C3_test_litedoc_pipeline.py.bak` | 1 條斷言依規格更新＋新增 3 測試（post-strip 正確 key／dead-paths／cover-prompt 規則） |
| 修改 | `tests/test_ingestion_engine.py` | —（C1 新建檔延續編修、依 tasks 無需 bak） | 新增 `TestCrossPhaseIntegration` §7.2 整合測試 ×3 |

> ⚠️ 兩 `.bak` 依鐵律**必須**列入本 commit `git add` 清單（§8）。baton/ 暫存之 plan / tasks / 本報告**不在** git add 清單。

---

## §4 修法說明

### §4.1 `pipelines/litedoc_pipeline.py`

- **P3 section 分支譯題改源**（原 L524 slot 撈取 → 與 whole 分支同式）：

```python
# === [PIPE-INGEST C3] U5c ② slot 撈題廢除：譯題唯一源＝P1 title（與 whole 分支同式；
# 根治標題錯置三受害者——zh 扉頁 # 標題 / HTML <title> / PDF /Title）===
translated_title = section_engine.translate_unit(title, inj, tr, "title") if title else title
```

- **slot 撈題方法整段刪除**（原 `_extract_translated_title`、先經全庫 grep 確認僅本檔兩處引用）；**source_lang 啟發式 dead code 整段刪除**（原 L303-311、HOTFIX-1 起由 `section_engine.classify_source_lang` 接替、全庫零 caller）＋其唯一消費之孤兒常數 `_CJK_MIN`/`_CJK_RATIO` 一併移除。⚠️ resume（`resume_pipeline.py:312`）/ slides（`slide_pipeline.py:388`）各自的同名方法為**活代碼**、零碰。
- **cover-prompt 增補**（`_LITEDOC_META_SYSTEM_PROMPT` Rules 2/3、原 2/3 遞移 4/5）：

```python
"2. publisher: output the organization's official name; fix obvious OCR distortions of "
"well-known outlet names (e.g. AI6Z -> a16z, G00gle -> Google). Do NOT invent a publisher "
"that is not indicated by the text or URL.\n"
"3. authors: normalize letter casing to Title Case (e.g. MARC ANDREESSEN -> Marc Andreessen); "
"keep name order and spelling unchanged.\n"
```

- **docstring 同步**：`run_phase3` 流程註解③由「三路（分段→頂層 title slot）」改為「唯一源＝P1 title」。
- 移除識別字不得殘留於註解（§6.3 grep 含註解層）：替位註解一律用泛稱（「slot 撈題方法」「source_lang 啟發式」）。

### §4.2 `tests/test_litedoc_pipeline.py`（斷言更新 1 + 新增 3）

- **依規格更新**（唯一被改寫之既有斷言、對應 plan v4 §2.3）：`test_p3_translated_title_section` 原斷言 `translated_title == "ZH::Sec1"`（頂層 title slot＝**本次缺陷①之病根行為**）→ `== "ZH::Big Headline"`（P1 title）。
- 新增 `test_p3_post_strip_uses_correct_translated_title`：tiles 首節為標題回聲（三節內容均衡、避開 heading 退化 fallback）→ 譯後層回聲 heading 被剝、內文不受累（post-strip 拿到正確 key 之實證）。
- 新增 `test_p3_dead_paths_removed`（模組源碼靜態掃描雙識別字歸零）、`test_cover_prompt_normalization_rules`（official name / AI6Z -> a16z / Title Case / Do NOT invent 四斷言）。

### §4.3 `tests/test_ingestion_engine.py` — §7.2 跨 Phase 整合測試

`TestCrossPhaseIntegration`：SAMPLE_MD＋判型 → `assemble` → `collect_render_slots` → **key-changing mock 翻譯**（`[譯]` 前綴、譯文≠原文）→ 按 slot 組裝。三斷言組：
1. figure `content` 經 raw slot 全穿透至譯後輸出（缺陷②不變式）；
2. 文件標題與 meta 行零重播、非 meta 內文（epigraph）正常穿透（缺陷①③不變式、防過度剔除）；
3. **node key 對位**：title slot `key`＝原文標題 path（`Section Alpha`／`Section Alpha/Alpha Child`）、譯文已變 key 零位移、`collect_rag_sections` 之 `summary_key`＝原文 path 而 `title`＝譯文（P2/P4 同基準、RAG-ASYNC #1 防回歸）。

過程修正一處：post-strip 測試初版 tiles（回聲節空內文＋單小節）誤觸 `is_heading_degraded` → whole fallback；改三節均衡素材後按預期走 section 模式（引擎與業務碼零改、屬測試素材校準）。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/litedoc_pipeline.py
 M tests/test_ingestion_engine.py
 M tests/test_litedoc_pipeline.py
?? .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_test_litedoc_pipeline.py.bak
```

### §5.2 目標測試（實貼）

```
tests/test_ingestion_engine.py + tests/test_litedoc_pipeline.py
..............................................................           [100%]
62 passed in 0.58s
```

### §5.3 全套件（實貼）

```
780 passed, 3 skipped, 3 warnings in 57.42s
```

C2 後基線 774 passed → **780 passed（+6、0 failed、零回歸）**。

### §5.4 §6.3 驗收 grep（實貼）

```
--- 雙廢除（期望 0 命中）
grep -n "_extract_translated_title\|_detect_source_lang" pipelines/litedoc_pipeline.py
0 matches（exit=1）
--- translate_unit 兩分支（whole L515 / section L524）
pipelines/litedoc_pipeline.py:515:...translated_title = section_engine.translate_unit(title, inj, tr, "title") if title else ...
pipelines/litedoc_pipeline.py:524:...translated_title = section_engine.translate_unit(title, inj, tr, "title") if title else ...
--- cover-prompt 正規化規則
pipelines/litedoc_pipeline.py:69: official name / :70: AI6Z -> a16z / :72: Title Case（俱命中）
--- §7.2 整合測試存在
tests/test_ingestion_engine.py: class TestCrossPhaseIntegration + key-changing 斷言（命中）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py tests/test_ingestion_engine.py
無命中（合規）
--- database：grep -nE "\.commit\(\)" <三檔> | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 寫入
```

---

## §6 不可動清單遵守狀態

- [x] `processor/md_processor.py`、`processor/json_processor.py` — 零改
- [x] `pipeline_core.py` 及 A 軌鏈全體 — 零改
- [x] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py` — 零改（各自 `_detect_source_lang` 活代碼原樣保留）
- [x] `pipelines/section_engine.py`、`pipelines/ingestion_engine.py` — 零改
- [x] 改動僅限譯題單一源／cover-prompt 規則／dead code 清除／整合測試（提示詞界線）
- [x] 母翻譯提示詞 / `pipelines/contracts.py` / `processor/rag_indexer.py` — 零改
- [x] 工具層四檔 — 零改
- [x] `settings.py` 旗標預設值 — 零改
- [x] 既有 tests 斷言本體 — 僅 1 條依 plan §2.3 規格更新（§4.2 記錄）、其餘零改
- [x] 禁 constraints 鷹架 — 未向 `InjectionContext.constraints` 注入任何內容

---

## §7 銜接

- **baton 狀態**：C1/C2/C3 三執行報告 + plan v4 + tasks + design spec 均暫存 `baton/`、未 mv 未 git add（Checkout 一次性歸檔）。
- **hash 自癒**：C2 已 ship＝`ca4e0e7`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：推進 plan v4 §2.3／§2.8／§2.9＋§8.1 整合測試——C1-C3 至此覆蓋 plan §2 全部實作條款（§2.1-§2.5、§2.8、§2.9），影子輸出六缺陷之結構項全數治畢。**（負向防錯）**：§7.2 整合測試以 `SAMPLE_MD` 擬真樣本行之、非 SpaceX 全文——真實樣本端到端驗證屬 baron 影子 E2E（plan §8.2、Checkout 後）。
- **下一步**：C_CHECKOUT — Checkout（收官歸檔）；等 baron 確認本 commit 後另行下達 checkout 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add tests/test_ingestion_engine.py
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST_C3_msg.txt）
cat > /tmp/PIPE-INGEST_C3_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）

1. 修改 pipelines/litedoc_pipeline.py，使 section 與 whole 翻譯模式下的譯題 translated_title 一律統一經由 translate_unit 翻譯 P1 true title，並廢除與清理舊的 _extract_translated_title 插槽提取方法，根治瀏覽器與 PDF Title 錯置。
2. 增補 _LITEDOC_META_SYSTEM_PROMPT 出版方（publisher）正規化 OCR 自癒規則與作者 Title Case 格式化指令。
3. 清理 pipelines/litedoc_pipeline.py 中的 _detect_source_lang 棄用死碼（已全數由 classify_source_lang 接替）。
4. 於 tests/test_ingestion_engine.py 新增 §7.2 跨 Phase 整合測試，全面斷言非 text elements 穿透、meta 不重複、及 node key 基準對齊。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST_C3_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C3 執行完成——譯題單一源＋cover-prompt 正規化＋dead code 清理＋§7.2 整合測試、780 passed 零回歸、SOP 雙核查合規
