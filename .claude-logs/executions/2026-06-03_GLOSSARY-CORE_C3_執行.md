# GLOSSARY-CORE C3 — Translate Integration & Backfill（翻譯管線術語融合與增量回填）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C3 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C3 + plan v2 §2 U3 |
| **次級參考** | database_SOP / logging_SOP / GLOSSARY-CORE C2（GlossaryManager） |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`9af971f`（BE-Refactor: C2 — Glossary Core & Cascading Retrieval）
- **完成狀態**：C3 於 `translate_processor.py`（注入）+ `pipeline_core.py`（回填）旗標閘門接入落地 worktree，旗標 ON/OFF 三路徑測試 + py_compile + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C3 | `待 baron 回填` | BE-Refactor: C3 — Translate Integration & Backfill（翻譯管線術語融合與增量回填） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/translate_processor.py` | +27/-1 行（`import settings` + L237-239 旗標閘門術語注入，C3 標記包裹） | 改前 `.bak` |
| `pipeline_core.py` | +31 行（`import settings` + `_stage_translate` 尾端背景回填 hook，C3 標記包裹） | 改前 `.bak` |
| `.claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_translate_processor.py.bak` | 新增備份 | **納入 git add** |
| `.claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_pipeline_core.py.bak` | 新增備份 | **納入 git add** |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C3_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C3→✅ / C4→🟡 WIP + C2 Hash 自癒（`待 baron 回填`→`9af971f`） | — |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C3_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git diff --stat`：
```
 pipeline_core.py                 | 31 +++++++++++++++++++++++++++++++
 processor/translate_processor.py | 27 ++++++++++++++++++++++++++-
 2 files changed, 57 insertions(+), 1 deletion(-)
```

## §4 修法說明

### §4.1 `translate_processor.py` 旗標閘門術語注入（C3 標記包裹）
`import settings`（既有 doc_analyzer/domain_detector pattern）+ L237-239 改為三分支：
```python
domain = getattr(self, 'domain', '')
# === [GLOSSARY-CORE C3 START] ===
if settings.LLM_USE_GLOSSARY_ALIGN and domain:
    try:
        from processor.glossary_extractor import GlossaryManager
        src_lang = getattr(self, 'source_lang', 'en'); tgt_lang = getattr(self, 'target_lang', 'zh-tw')
        glossary = GlossaryManager().query_cascade(src_lang, tgt_lang, domain)
        if glossary:
            term_lines = "\n".join(f"- {o} → {t}" for o, t in glossary.items())
            system_prompt += f"\n\n本文件主題領域：{domain}。以下為該領域權威術語對照表（不可違背...）：\n{term_lines}"
        else:
            system_prompt += f"\n\n本文件主題領域：{domain}，請以該領域標準術語翻譯。"
    except Exception:
        self.logger.error("[glossary] 術語注入失敗，降級回原行為", exc_info=True)
        system_prompt += f"\n\n本文件主題領域：{domain}，請以該領域標準術語翻譯。"
elif domain:
    system_prompt += f"\n\n本文件主題領域：{domain}，請以該領域標準術語翻譯。"
# === [GLOSSARY-CORE C3 END] ===
```
- **旗標 OFF（預設）→ `elif domain:` 分支**：與既有 L238-239 單行 **byte 等價**。
- **旗標 ON + 術語命中 → 注入「不可違背術語對照表」**；**ON + 空 / 例外 → 降級單行**。

### §4.2 `pipeline_core.py` translate 後背景回填 hook（C3 標記包裹）
`import settings` + `_stage_translate` 的 `process()` 後追加：
```python
# === [GLOSSARY-CORE C3 START] ===
if settings.LLM_USE_GLOSSARY_ALIGN and domain:
    try:
        from processor.glossary_extractor import GlossaryManager
        src_abstract = (self._metadata.get('abstract') or {}).get('value') if isinstance(self._metadata, dict) else ''
        tgt_abstract = getattr(self.translate_processor, 'translated_abstract', None) or ''
        if src_abstract and tgt_abstract:
            gm = GlossaryManager()
            pairs = gm.extract_terms(src_abstract, tgt_abstract, 'en', 'zh-tw', domain)  # LLM 交易外
            written = gm.upsert_terms(pairs, 'en', 'zh-tw', domain)                       # 極短交易冪等
            logger.info("[glossary] translate 回填 domain=%r 術語 %d 筆", domain, written)
    except Exception:
        logger.error("[glossary] translate 術語回填失敗（不阻塞主流程）", exc_info=True)
# === [GLOSSARY-CORE C3 END] ===
```
- **回填非阻塞**：獨立 `try/except`，任何提取/寫入異常僅 `logger.error`，**絕不中斷翻譯主流程**。
- **交易邊界**：`extract_terms`（LLM）在交易外、`upsert_terms` 極短交易（database SOP）。
- 以 abstract 原文/譯文對作為單文代表性術語種子（輕量、單次 LLM）；**書籍 `ParallelChapterTranslator` 雙層融合延後**（TRANSLATE-BOOK 未落地、tasks §9）。

## §5 測試結果

### §5.1 §6.3 grep 驗收（真實輸出節錄）
```
processor/translate_processor.py:244:        if settings.LLM_USE_GLOSSARY_ALIGN and domain:
processor/translate_processor.py:249:                glossary = GlossaryManager().query_cascade(src_lang, tgt_lang, domain)
pipeline_core.py:709:        if settings.LLM_USE_GLOSSARY_ALIGN and domain:
pipeline_core.py:721:                    pairs = gm.extract_terms(  # LLM 提取（交易外）
pipeline_core.py:724:                    written = gm.upsert_terms(pairs, 'en', 'zh-tw', domain)  # 極短交易冪等
```

### §5.2 py_compile 語法檢查
```
$ venv/bin/python -m py_compile processor/translate_processor.py pipeline_core.py
compile OK
```

### §5.3 旗標 ON/OFF 三路徑功能測試（攔截 system_prompt）
```
OFF 尾段: '本文件主題領域：SB，請以該領域標準術語翻譯。'    # 旗標 OFF: ✅ byte 等價舊行為
ON 含術語表: True | riesling→雷司令: True                  # 旗標 ON + 命中: 注入術語對照表
ON 空術語尾段: '本文件主題領域：SB，請以該領域標準術語翻譯。'  # 旗標 ON + 空: 降級單行
ALL OK
```

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 50.57s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C3 無關。

### §5.5 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：兩檔新增區無裸 commit（回填走 GlossaryManager.upsert_terms 內 `session.begin()`）→ 無命中（合規）。
- **logging §5.1**：注入降級 `self.logger.error(..., exc_info=True)` + 回填 `logger.error(..., exc_info=True)` → 合規。

## §6 不可動清單遵守

- [x] `translate_processor.py` / `pipeline_core.py` 旗標閘門**以外**既有邏輯 — **未動**（旗標 OFF byte 等價、§5.3 證實）。
- [x] `models.py` / `glossary_extractor.py`（C2）/ `normalize_to_lcc` — **未觸碰**。
- [x] `rag_retriever.py` / `tiling_processor.py` — **未觸碰**。
- [x] `AI_professor_chat.py` — **未觸碰**（Chat 注入屬 C4）。
- [x] 書籍 `ParallelChapterTranslator` — **未接**（延後）。
- [x] 改前兩檔 `.bak` 已備。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_GLOSSARY-CORE_C3_執行.md` 暫存 baton/，連同 C1/C2 報告 + plan_v2 + tasks 待 C7 收官一次性歸檔。
- **下一步**：C4 — Chat Injection：`AI_professor_chat.py:329-335` 旗標閘門按 `_domain`（LCC）`query_cascade` 取術語、組「不可違背 System constraint」附 character/explain prompt；改前 `.bak` + C4 標記包裹。待 baron 確認 C3 後另行下達。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_translate_processor.py.bak
#    .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_pipeline_core.py.bak
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add processor/translate_processor.py
git add pipeline_core.py
git add .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_translate_processor.py.bak
git add .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_pipeline_core.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C3_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C3_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C3_commit_msg.txt

# 4. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C3_commit_msg.txt
```
