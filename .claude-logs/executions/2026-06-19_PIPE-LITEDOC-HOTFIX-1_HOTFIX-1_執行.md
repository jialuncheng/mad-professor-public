# PIPE-LITEDOC-HOTFIX-1 HOTFIX-1 執行報告 — litedoc 標題回聲剝除 + P1 二元繁中偵測

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC-HOTFIX-1 HOTFIX-1 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/hotfixes/2026-06-19_PIPE-LITEDOC-HOTFIX-1_hotfix.md`（收官後路徑）|
| 次級參考 | logging_SOP / database_SOP;PIPE-SLIDES-HOTFIX-1 `_strip_title_echo` 範式;A 軌 `_title_sim` 範式 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit HOTFIX-1)、pytest 704 passed、SOP 合規、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：PIPE-LITEDOC 全案結案（C8 `2a9b2e3`）後;litedoc QA 暴露雙缺陷（標題/Meta 重複 + 日文/簡體未翻譯）。
- **完成狀態**：F1（section_engine 四純函式）+ F2（P1 二元繁中偵測接線）+ F3（P3 雙剝標題回聲）落地;18 新測試、全套件 704 passed。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `hotfix.md 修法（F1/F2/F3 + 三鎖 + OQ-a/b 拍板）`。**問題一**＝原文層+譯後層雙剝使扉頁成唯一標題（RAG 不受污染）;**問題二**＝P1 源點二元「是不是繁中」偵測，一次解 P3 is_zh + P2 section_summaries 雙 gate，簡體不給 `zh*` 字串使四處 gate 零改不復活。無偏離。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| HOTFIX-1 | （待 baron 回填）| BE-Hotfix: PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁）|

## §3 變動檔案清單
| 檔案 | 動作 | git add |
|---|---|---|
| `pipelines/section_engine.py` | 修改（+133：四純函式 + import SequenceMatcher）| ✅ |
| `pipelines/litedoc_pipeline.py` | 修改（+18：F2 P1 + F3 ①② 雙剝）| ✅ |
| `tests/test_section_engine.py` | 修改（+88：13 純函式測試）| ✅ |
| `tests/test_litedoc_pipeline.py` | 修改（+58：5 接線/雙剝測試）| ✅ |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_litedoc_pipeline.py.bak` | 備份 | ✅ |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_section_engine.py.bak` | 備份 | ✅ |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | ✅ |
| `.claude-logs/TODO.md` | 結案 + hash 自癒 | ✅ |
| `hotfixes/2026-06-19_PIPE-LITEDOC-HOTFIX-1_hotfix.md`（baton→hotfixes mv）| 收官歸檔 | ✅ |
| `executions/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_執行.md`（本檔、baton→executions mv）| 收官歸檔 | ✅ |

## §4 修法說明（關鍵片段）
### F1 `section_engine.py`（共用純函式、零 doc_type/A 軌耦合）
- `detect_zh_tw(sample)`：有假名(`぀–ヿ`)/諺文(`가–힣`)→False;簡體專有字命中→False;漢字<8→False;ASCII>漢字×3→False;否則 True。
- `classify_source_lang(sample)`：繁→`"zh"`、簡→`"hans"`、ja/ko/en。**鎖一**：非繁皆 not startswith `"zh"`。
- `sample_body_text(tiles)`：tiles 文字節點串接、跳前 15%、取 800 字、短文兜底整篇。**鎖三**。
- `strip_title_echo(md, title, cap=3)`：前 cap 非空行找首個 `_title_echo_match`（==/包含/`SequenceMatcher≥0.7`）標題行→剝 + 連帶剝 byline/日期（`撰寫|報導|By\b|\d{4}[-/年]`）;找不到原樣返回。
### F2 `litedoc_pipeline.py` run_phase1
```python
_lang_sample = section_engine.sample_body_text(tiles) or markdown_text[:2000]
source_lang = section_engine.classify_source_lang(_lang_sample)
```
### F3 run_phase3 雙剝
```python
# ① pre-strip（讀 full_text 後、譯前）：en 全模式 + zh whole/is_zh、原標題 exact
_title_bare = title.replace(" (測試)", "").strip()
full_text = section_engine.strip_title_echo(full_text, _title_bare)
# ② post-strip（還原後、扉頁 prepend 前）：補 section 模式、譯後標題 exact（同 slot）
zh_text = section_engine.strip_title_echo(zh_text, (translated_title or "").replace(" (測試)", "").strip())
```

## §5 測試結果
### §5.1 受災測試（litedoc + section_engine）
```
$ venv/bin/python -m pytest tests/test_section_engine.py tests/test_litedoc_pipeline.py -q
64 passed in 0.73s
```
新增 18：detect_zh_tw 繁/日/簡/英/空封面;classify 鎖一 not-startswith-zh + token;sample 跳封面+短文兜底;strip 剝首標題+byline/不誤剝/譯後模糊;P3 dedup whole+section+RAG 不受影響;P1 日文+簡體接線。
### §5.2 全套件回歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 704 passed, 3 skipped in 564.18s
唯一 fail＝tests/test_logging_config.py::test_settings_log_format_default_auto（既有 .env LOG_FORMAT env flake、與本案無關）
基線 686 → 704（+18 新測試全綠）
```
### §5.3 SOP 一致性核查
```
§5.1 logging：本 hotfix 新增純函式 detect_zh_tw/classify_source_lang/sample_body_text/strip_title_echo
              **無任何 logger 呼叫**（純函式、存疑回 False/原樣、非致命）→ 無新增 logger.error。
              既有命中（litedoc :157/:228/:256/:360/:390/:419/:479/:603/:623、section_engine :103/:147/:374）
              皆既存且 exc_info=True、本 hotfix 未碰 → 合規。
§5.2 database：grep "\.commit\(\)" | grep -v "with .*session.*begin()" → 無命中（合規）；本 hotfix 零 DB 操作。
包裹 marker：litedoc 6 / section_engine 2（START/END 對稱）。
```

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| A 軌（pipeline_core/md_restore 等）| [x] ✅ 零碰（`_title_sim` 僅參照範式、section_engine 自帶實作、零 import）|
| rag_indexer / contracts.py 四凍結合約 | [x] ✅ 零碰（git diff 僅 4 檔）|
| resume_pipeline / slide_pipeline 本體 | [x] ✅ 零碰（共用 `startswith("zh")` gate 語意不變、鎖一保證）|
| render_meta_header_html / 扉頁結構 | [x] ✅ 未動（OQ-b 保留）|
| 只動 litedoc_pipeline + section_engine + 2 測試 | [x] ✅ git diff --stat 證實 4 檔 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。git diff 僅 `litedoc_pipeline.py`+`section_engine.py`+2 測試;A 軌/rag_indexer/contracts/resume/slide 本體零碰。
- **(b) 無關 / 違規?**：否。F1/F2/F3 全對應 hotfix.md;三鎖落實（鎖一 `test_classify_never_returns_zh_prefix_for_nonzh` 證、鎖二 section_engine 共用、鎖三 `test_sample_body_text_skips_cover` 證）;雙剝每模式 exact（`test_p3_dedup_whole/section`）;SOP 合規;不自發 commit。msg 補 Opus 4.8 簽名。
- **(c) 推進哪個 U-N?**：問題一（標題回聲雙剝）+ 問題二（P1 二元繁中、解 P2+P3 雙 gate）;無做白工。

## §7 銜接（收官歸檔已執行）
- **baton 歸檔**：`hotfix.md` → `hotfixes/`、本執行報告 → `executions/`（單 commit hotfix、Run 即收官）。
- **提示詞**：`HOTFIX-1_run_提示詞.md` + `doc_提示詞.md` 已 git add。
- **TODO**：PIPE-LITEDOC-HOTFIX-1 ✅ 完成表 + 索引 + PIPE-SYNC-4 C4 hash 自癒（`72bcb32`）。
- **下一步**：baron commit（msg `/tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt`）+ 回填 HOTFIX-1 hash + 影子 E2E（§修法依據 ⚠️ 五項）。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3 兩 .bak）

# 2. git add（業務碼 + 測試 + 兩 .bak + 提示詞 + TODO + 歸檔後 hotfix/執行報告）
git add pipelines/litedoc_pipeline.py pipelines/section_engine.py
git add tests/test_litedoc_pipeline.py tests/test_section_engine.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_section_engine.py.bak
git add .claude-logs/hotfixes/2026-06-19_PIPE-LITEDOC-HOTFIX-1_hotfix.md
git add .claude-logs/executions/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_執行.md
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt）

# 4. baron 手動 commit
git commit -F /tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt
```

## §9 回退方式
```bash
cp .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_litedoc_pipeline.py.bak pipelines/litedoc_pipeline.py
cp .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_section_engine.py.bak   pipelines/section_engine.py
# 或 commit 後：git revert <HOTFIX-1 hash>
```

---
### 結論
🟢 litedoc 雙缺陷最小侵入修復：**問題二**＝P1 二元繁中偵測（section_engine 共用、取內文樣本、簡體不給 zh* 契約、源點一改解 P2+P3 雙 gate）;**問題一**＝原文層+譯後層雙剝標題回聲（扉頁唯一標題、RAG 不受污染、每模式 exact）。只動 2 業務檔+2 測試、704 passed、SOP 合規。Run 即收官、待 baron commit。
