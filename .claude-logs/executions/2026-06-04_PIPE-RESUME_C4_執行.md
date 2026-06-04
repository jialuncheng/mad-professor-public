# PIPE-RESUME C4 — P3 Translation & Restore 執行報告

---

**任務代號**：PIPE-RESUME C4
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C4
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C4)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C3（`48aa5df`）已落地——`run_phase2`（P2）交付 `GlossaryReadySpec`，`run_phase3` 仍為 stub。
- **完成狀態**：實作 `run_phase3`（P3 Translation & Restore）——① 建 `InjectionContext`（lcc / glossary / `zh_summary`←P2 `translated_abstract` / `domain_name` / **`doc_type='resume'`**）；② 正文 **100% Bypass** 整份 `Translator.translate(text, ctx, NORMAL, "content")`（不切 Section、不開 Sliding Window）；③ **md_restore 純樣板渲染**（廢除 extra_info）：`final_en`=原著、`final_zh`=中文版各寫一份乾淨 Markdown；④ 交付 `BilingualMarkdownSpec`（`translated_abstract` 沿用 P2、必填）。消費 Translator 真理源**零改動**；全套件 465 passed。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | `run_phase3` 100% Bypass 整份翻譯 + 純樣板渲染（InjectionContext doc_type='resume' / Translator NORMAL / final_zh+en 寫檔）→ BilingualMarkdownSpec | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C4_resume_pipeline.py.bak` | 實作 run_phase3（C4 標記）；複用 C3 `_read_source_text` |

> ⚠️ `.bak` 須在 C4 `git add` 清單中（§8）。`baton/` 暫存報告不入 Git。

---

## §4 修法說明

### §4.1 `pipelines/resume_pipeline.py` — run_phase3 100% Bypass 翻譯還原
`# === [PIPE-RESUME C4 START/END] ===` 包裹。核心：
```python
def run_phase3(self, ctx):
    gspec = ctx.glossary_ready                      # P2 交付（缺則 ValueError）
    source_lang = (ctx.ingestion.source_lang ...) or "en"
    full_text = self._read_source_text(ctx)         # 原著 markdown（複用 C3 helper）
    inj = InjectionContext(lcc=gspec.lcc, glossary=gspec.glossary,
        zh_summary=gspec.translated_abstract, domain_name=gspec.domain_name,
        doc_type="resume")                          # ① 正式商務中文風格
    if source_lang.startswith("zh"):                # 原文已中文 → 不重譯
        zh_text = en_text = full_text
    else:                                           # ② 100% Bypass 整份翻譯
        zh_text = Translator().translate(full_text, inj, TranslateMode.NORMAL, "content")
        en_text = full_text                         # 原著
    zh_path = paper_manager.article_zh_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
    en_path = paper_manager.article_en_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
    zh_path.write_text(zh_text); en_path.write_text(en_text)   # ③ 純樣板渲染
    return BilingualMarkdownSpec(final_zh_path=str(zh_path), final_en_path=str(en_path),
        translated_abstract=gspec.translated_abstract, rag_tree_json=None)   # ④
```

**設計裁決（grep 證據驅動、據實記錄）**：
1. **新原子翻譯路徑（非舊 TranslateProcessor/RestoreProcessor）**：既有 P3 用舊 `TranslateProcessor.process`（JSON 逐段、`pipeline_core.py:695`）+ `RestoreProcessor.process`（複雜學術渲染 + extra_info、`pipeline_core.py:786`）。tasks §8 C4 明定**整份 `Translator.translate`（新原子翻譯器、text-in/out）+ md_restore 純樣板渲染**，故 P3 為**新簡化路徑**、不複用舊兩 processor（對齊 plan U4「md_restore 退化純樣板、廢除 extra_info」）。
2. **doc_type='resume' 風格**：`InjectionContext.doc_type='resume'` → Translator `_STYLE_HINTS` 套「正式商務中文」（非旗標閘門、`translator.py:110` 恆套用）。
3. **final_en/final_zh 語義**：`final_en`=原著（source 語言原文）、`final_zh`=中文版（source≠zh 則為譯文；source=zh 原文已中文則 zh=原文、不重複翻譯，因 Translator 目標固定 zh-tw）。檔名走 `paper_manager.article_zh_path`/`article_en_path`（`final_{paper_id}_zh.md`/`_en.md`、`paper_manager.py:93/97`）。
4. **R3.1 純淨性**：僅整份翻譯原文，無 AI Questions / 章節 Summary / extra_info 注入（grep `question`/`extra_info` 僅 docstring 禁令文字、無實際生成碼）。
5. **translated_abstract 沿用**：`BilingualMarkdownSpec.translated_abstract`（必填、`contracts.py:71`）直接沿用 `gspec.translated_abstract`，防 P3→P4 ValidationError。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C4_resume_pipeline.py.bak
# （.claude-logs/baton/、prompts/、TODO.md 文件改動另計）
```

### §5.2 驗收輸出
import + 註冊：`strategy= ResumePipeline`。

§6.4 grep 精準命中：
```
434:            doc_type="resume",                              # InjectionContext doc_type
443:                full_text, inj, TranslateMode.NORMAL, "content"   # 100% Bypass NORMAL
459:            final_zh_path=str(zh_path),
460:            final_en_path=str(en_path),
461:            translated_abstract=gspec.translated_abstract,   # 沿用 P2、必填
```

pipelines 既有測試（防 Regression）：`25 passed in 0.63s`。
全套件：
```
1 failed, 465 passed, 3 skipped in 134.19s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C4 Regression）
```

> 註：`tests/test_resume_pipeline.py` P3 契約測試屬 **C6**、本 C4 尚未建檔；C4 以 import/grep/SOP/全套件防 Regression 驗收。

### §5.3 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**：C4 run_phase3 僅 1 處 `logger.info`（完成摘要）、無 `logger.error`/`warning`/`traceback.format_exc`（合規；既有 6 處 warning 皆 exc_info=True 不變）。
- **database 檢測**：C4 **無任何 DB 操作**（純翻譯 + 寫檔）；`grep .commit()/session.begin()` 於 resume_pipeline.py 僅 C3 docstring 註解文字（合規）。
- **R3.1 原著純淨性**：grep `question`/`extra_info` 僅 docstring 禁令文字、無實際生成碼（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` 業務代碼 | [x] ✅ 未觸碰（paper_manager 僅呼叫 article_zh/en_path） |
| `processor/translator.py`（Translator 真理源） | [x] ✅ 僅**消費** translate/InjectionContext/TranslateMode、零改動 |
| `processor/translate_processor.py` / `md_restore_processor.py`（舊 P3 鏈） | [x] ✅ 未觸碰（C4 走新原子翻譯路徑、不複用） |
| `pipelines/contracts.py` / `context.py` / `base_strategy.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更 |
| 其他 Phase（run_phase1/2/4） | [x] ✅ 未觸碰（1/2 已落地、4 仍 stub） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端 | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `baton/`、不入版控，待 C7 收官 `mv`+`git add` 歸檔至 `executions/`。
- **下一步**：tasks.md C5 — P4 Async RAG（門檻 ≥3 技能詞保護）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。
- **附帶（歷史 Hash 自癒）**：C3 已提交 `48aa5df` → TODO active 列 C3 佔位符已回填。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（C4 程式碼 + .bak；baton/ 報告嚴禁加入）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C4_resume_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C4_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C4_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C4 — P3 Translation & Restore（100% Bypass 翻譯還原）

實作 ResumePipeline.run_phase3：① 建 InjectionContext（lcc/glossary/zh_summary←P2
translated_abstract/domain_name/doc_type='resume'，套正式商務中文風格）；② 正文 100%
Bypass 整份 Translator.translate(text, ctx, NORMAL, "content")，不切 Section/不開 Sliding
Window；③ md_restore 純樣板渲染（廢除 extra_info）：final_en=原著、final_zh=中文版各寫一份
乾淨 Markdown（嚴禁 AI Questions/Summary）；④ 交付 BilingualMarkdownSpec（translated_abstract
沿用 P2、必填防 ValidationError）。source_lang='zh*' 原文已中文則不重譯。複用既有 Translator
零改動、全套件 465 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C4 的代碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控；嚴禁含 AI Questions/Summary（R3.1） |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C4 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C4 執行完畢——run_phase3 100% Bypass 整份翻譯（Translator NORMAL + InjectionContext doc_type='resume'）+ 純樣板渲染 final_zh/final_en → BilingualMarkdownSpec（translated_abstract 沿用 P2）。設計裁決：走新原子翻譯路徑（非舊 TranslateProcessor/RestoreProcessor、對齊 plan U4 純樣板）；source=zh 不重譯。全套件 465 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。
