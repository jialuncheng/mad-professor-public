# GLOSSARY-CORE 中央領域術語庫與跨語系一致性 — Tasks

> 本文件為 GLOSSARY-CORE 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md`（U1-U5）產出，含 7 個 Commit（C1-C6 實作/測試 + C7 Checkout 收官）。
> **收官歸檔鐵律**：C1-C6 執行期所有 plan/tasks/執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 C7（Checkout）一次性 `mv` + `git add`** 搬移 plan_v2 + tasks + 全部 `C*_執行.md`（WORKFLOW_SOP §3）。
> **上游硬前置**：DOMAIN-NORM 已收官（C1-C5、見 TODO ✅）；本任務 `domain` LCC 一律經 `normalize_to_lcc(raw_domain, context_text=None)->LCCCode` 取得，純消費、不自定義收斂。
> **旗標複用**：沿用 DOMAIN-NORM 既建 `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False、零風險），本任務不重複定義。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 3 個 | `processor/glossary_extractor.py`（術語提取+級聯查詢+回填核心）/ `tools/manage_glossary.py`（自癒 CLI）/ `tests/test_glossary_core.py`（5 測試） |
| **修改檔案** | 4 個 | `models.py`（**新增** `GlobalGlossary` 表；既有表不動）/ `processor/translate_processor.py`（L237-239 旗標閘門術語注入）/ `pipeline_core.py`（translate 後增量回填 hook）/ `AI_professor_chat.py`（L329-335 旗標閘門 Chat 術語注入） |
| **目錄初始化** | 0 個 | —（複用既有 `processor/` `tools/` `tests/`） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 7 個 | C1（資料庫結構）→ C2（術語核心與級聯查詢）→ C3（翻譯管線融合與回填）→ C4（前台問答注入）→ C5（自癒 CLI）→ C6（單元測試）→ C7（Checkout 收官） |
| **執行報告** | 7 個 | `baton/2026-06-03_GLOSSARY-CORE_C1~C7_執行.md`（套用 template_execution.md、暫存 baton/） |
| **.bak 備份** | 每改既有檔前必備 | C1 改 `models.py` / C3 改 `translate_processor.py`+`pipeline_core.py` / C4 改 `AI_professor_chat.py` 前各產 `.bak`，納入該 Commit git add |
| **baton 歸檔** | 1 次 | **僅 C7 收官**一次性 `mv` plan_v2＋tasks＋C1-C7 報告至正式目錄 + `git add` |

> **邊界**：本任務建「中央術語存儲 + 級聯查詢 + 翻譯/問答一致性注入 + 自癒 CLI」；**LCC 收斂純消費 DOMAIN-NORM**（不自定義白名單）。`normalize_to_lcc`/`DomainMapping`/`rag_retriever`/`tiling_processor` 皆不動（§7）。旗標 OFF 時全鏈路 100% 維持舊行為。

---

## §1 TL;DR（概要）

- **挑戰**：跨文獻/跨時間/跨語系術語譯名漂移（同一專名在不同書、前台問答與譯本譯法不一）；LLM 無狀態思考易漂移。
- **解法**（逐 Commit、中文括號命名）：
  - **C1 — Database Schema（資料庫結構與聯合唯一索引）**：`models.py` 新增 `GlobalGlossary`（`(source_lang,target_lang,term_key,domain)` 聯合唯一約束、物理鎖死同語系同領域唯一譯法）。
  - **C2 — Glossary Core & Cascading Retrieval（術語庫核心與級聯優先權查詢）**：新建 `processor/glossary_extractor.py`——級聯查詢（`domain IN (LCC, 'general')` + 記憶體專屬覆寫通用）+ LLM 術語提取 + `INSERT OR IGNORE` 回填（交易外呼 LLM）。
  - **C3 — Translate Integration & Backfill（翻譯管線術語融合與增量回填）**：`translate_processor.py:237-239` 旗標閘門術語注入 + `pipeline_core.py` translate 後背景回填 hook（單文路徑；書籍並行融合延後）。
  - **C4 — Chat Injection（前台問答術語強約束注入）**：`AI_professor_chat.py:329-335` 旗標閘門按 `paper.domain` 拉術語注入 System Prompt 契約。
  - **C5 — Hot-Pluggable CLI（自癒補丁 CLI）**：新建 `tools/manage_glossary.py`（`--init`/`--test-pipeline --pdf`/`--backfill-existing-papers`）。
  - **C6 — Unit Tests（單元測試）**：`tests/test_glossary_core.py` 5 測試（唯一約束/級聯優先/書籍融合優先/Chat 注入/CLI 回填）。
  - **C7 — Checkout（收官與成果審計）**：Conformance 驗收 + 一次性歸檔 plan_v2/tasks/C1-C7 報告。
- **影響範圍**：1 新表 + 1 核心模組 + 1 CLI + 3 業務代碼旗標閘門接入（plan §1 明確授權）+ 測試；旗標預設 False、線上 0 風險。
- **不可動清單**：見 §7。

---

## §2 現況（plan §3 grep，已實地查證）

| 檔案:行 | 現狀 | 待處理 |
|---|---|---|
| `models.py:104` | `domain: Mapped[Optional[str]]`；無 `GlobalGlossary` 表 | C1 新增 `GlobalGlossary` 表；`Paper` 不動 |
| `processor/translate_processor.py:237-239` | `domain = getattr(self,'domain','')` → `system_prompt += f"\n\n本文件主題領域：{domain}..."` | C3 旗標閘門：True 時改注入術語表契約 |
| `processor/translate_processor.py:31/41` | `translate_text(..., domain='')` 簽名 + `self.domain` | C3 讀其 domain 查術語、不改簽名 |
| `AI_professor_chat.py:329-335` | `domain=paper_data.get('_domain','')` → `character_prompt/explain_prompt += f"\n\n當前文件主題：{domain}"` | C4 旗標閘門：True 時附加術語強約束 |
| `AI_professor_chat.py:338` | `messages=[{"role":"system","content":system_message}]` | C4 注入點下游、不動結構 |
| `pipeline_core.py:692-700 _stage_translate` | `TranslateProcessor()` + `domain=output_paths.get('_domain')` 傳入 | C3 translate 完成後加旗標閘門背景回填 hook |
| `pipeline_core.py:540-550` | 寫 DB `domain=output_paths.get('_domain')` | 不動（回填讀此 domain） |
| `processor/glossary_extractor.py` / `tools/manage_glossary.py` / `tests/test_glossary_core.py` | 不存在 | C2/C5/C6 新建 |
| `settings.py` `LLM_USE_GLOSSARY_ALIGN` | DOMAIN-NORM 已建（預設 False） | 純複用、不改 |

---

## §3 觀察問題

### 問題 #1：跨文獻術語無一致性防線
- **證據**：plan §1——同一專名跨書/跨時間/前台問答譯法不一；translate 僅注入 raw domain 字串（`translate_processor.py:239`），無術語表約束。
- **影響**：需中央 `GlobalGlossary` + 級聯查詢，將歷史真理術語強約束注入 translate 與 chat。

### 問題 #2：LLM 無狀態思考譯名漂移、無知識飛輪
- **證據**：plan §1/U3——每本書重複思考同術語、結果不回寫累積。
- **影響**：需 LLM 提取 + `INSERT OR IGNORE` 增量回填，命中即 0 API（對齊 DOMAIN-NORM 快取哲學）。

---

## §4 設計方案

> 逐 Commit 落地概要；完整規格見 plan v2 §2（U1–U5）。

- **C1（U1）**：`GlobalGlossary` 表 + `(source_lang,target_lang,term_key,domain)` 聯合唯一索引 + 級聯查詢輔助索引。
- **C2（U2 核心）**：`glossary_extractor.py`——① `query_cascade(src,tgt,domain)`：`SELECT WHERE domain IN (LCC,'general')`，Python 記憶體合併、**專屬 LCC 覆寫 general**；② `extract_terms(text, src, tgt, domain)`：LLM 提取術語對（**交易外**）；③ `upsert_terms(...)`：極短交易 `INSERT OR IGNORE`（`source='auto_extract'`）；全程 try/except 不阻斷。
- **C3（U3 單文路徑）**：`translate_processor.py:237-239` 旗標閘門——True 時 `query_cascade` 取術語建約束塊附 system_prompt；`pipeline_core.py` translate 完成後旗標閘門背景回填本文新術語。**書籍 `ParallelChapterTranslator` 雙層融合延後**（TRANSLATE-BOOK 未落地、見 §9）。
- **C4（U4）**：`AI_professor_chat.py:329-335` 旗標閘門——True 時按 `_domain`（LCC）`query_cascade` 取術語、組「不可違背 System constraint」附 character/explain prompt。
- **C5（U5）**：`tools/manage_glossary.py`——`--init`/`--test-pipeline --pdf`（detect→normalize_to_lcc→cascade→extract→backfill→`{stem}_glossary.json`）/`--backfill-existing-papers`（掃 papers、`normalize_to_lcc` 升級 domain）；`setup_logging`。
- **C6**：5 pytest（mock LLM + in-memory/file SQLite）。
- **C7**：Checkout 收官歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 修改 `models.py`（CLAUDE.md §3 清單） | 🟡 中 | plan v2 已 baron 核准；**僅新增** `GlobalGlossary`，既有表 byte 不動；C1 改前 `.bak` |
| 修改業務代碼 `translate_processor.py`/`pipeline_core.py`/`AI_professor_chat.py`（CLAUDE.md §3 清單） | 🔴 高 | **plan §1/U4 明確授權**熱插拔接入；全部 `if settings.LLM_USE_GLOSSARY_ALIGN:` 閘門包裹、`=== [GLOSSARY-CORE C3/C4 START/END] ===` 標記、改前 `.bak`；旗標 OFF=舊行為 byte 等價 |
| DB 交易內含 LLM 提取 → SQLite 鎖死 | 🔴 高 | **LLM `extract_terms` 必在 `session.begin()` 交易外**，取得術語後才開極短交易 `upsert`（database SOP 原則 2、對齊 DOMAIN-NORM C2） |
| 級聯查詢併發 upsert IntegrityError | 🟡 中 | 聯合唯一約束 + `INSERT OR IGNORE`/`on_conflict_do_nothing` 冪等 |
| 回填阻塞 Pipeline 主流程 | 🟡 中 | 背景/極短交易 + try/except；失敗僅略過回填、不影響 translate 產物 |
| 書籍並行融合接到未落地 TRANSLATE-BOOK | 🔴 高 | **C3 只做單文路徑**；書籍 `ParallelChapterTranslator` 融合介面預留、實接延後（§9 Open Question） |
| baton 報告提早 mv/git add | 🔴 高 | C1-C6 全留 baton；唯 C7 收官一次性歸檔 |

---

## §6 測試計畫

> 對齊 plan §6.1；C6 集中建 `tests/test_glossary_core.py`（mock LLM、不實打 API）。

### §6.1 C1 驗收（GlobalGlossary 表 + 唯一約束）
```bash
grep -nE "class GlobalGlossary|term_key|uq_glossary|UniqueConstraint" models.py
python -c "import models; print('GlobalGlossary' in dir(models))"
```
### §6.2 C2 驗收（核心、交易外、級聯）
```bash
grep -nE "class .*Glossary|query_cascade|on_conflict_do_nothing|session.begin|def extract_terms" processor/glossary_extractor.py
```
### §6.3 C3 驗收（translate 旗標閘門 + 回填）
```bash
grep -nE "LLM_USE_GLOSSARY_ALIGN|GLOSSARY-CORE C3|query_cascade|backfill" processor/translate_processor.py pipeline_core.py
```
### §6.4 C4 驗收（Chat 注入）
```bash
grep -nE "LLM_USE_GLOSSARY_ALIGN|GLOSSARY-CORE C4|query_cascade" AI_professor_chat.py
```
### §6.5 C5 驗收（CLI 子命令）
```bash
grep -nE "init|test-pipeline|backfill-existing-papers|argparse" tools/manage_glossary.py
```
### §6.6 C6 驗收（5 pytest 全綠 + 零迴歸）
```bash
pytest tests/test_glossary_core.py -v
pytest tests/ -q
```

---

## §7 不可動清單

明確劃定修改邊界。**以下嚴禁任何改動：**

- [ ] `models.py` `Paper` 等既有表主欄位與關係——僅可**新增** `GlobalGlossary` 表。
- [ ] DOMAIN-NORM 的 `normalize_to_lcc` 入口與 `Domains`/`DomainMapping` 表結構——僅可呼叫消費。
- [ ] `rag_retriever.py` RAG 核心檢索邏輯。
- [ ] `processor/tiling_processor.py` `tiling_method` 與 Bypass 判斷邏輯。
- [ ] `translate_processor.py`/`pipeline_core.py`/`AI_professor_chat.py` 中**旗標閘門以外**的既有邏輯（旗標 OFF 須 byte 等價舊行為）。
- [ ] `settings.LLM_USE_GLOSSARY_ALIGN` 旗標定義（DOMAIN-NORM 權威源、純複用）。
- [ ] 主 repo 目錄（worktree 父目錄）。
- [ ] baton/ 暫存文件（C1-C6 期間嚴禁提前 mv/git add；唯 C7 收官一次性歸檔）。

---

## §8 推薦 Commit 拆分

### C1 — Database Schema（資料庫結構與聯合唯一索引）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `models.py`（**新增** `GlobalGlossary`，先 `.bak`） |
| **安全性** | 🟢 高 — 純新增表、不動既有表/關係；無資料遷移 |
| **可逆性** | 🟢 高 — 還原 `.bak`（新表無既有依賴） |
| **驗收 grep 條件** | `grep -nE "class GlobalGlossary\|term_key\|uq_glossary\|UniqueConstraint" models.py` # 期望：表+唯一約束命中 |
| **依賴關係** | 無前置（DOMAIN-NORM 已落地） |
| **具體實作細節** | 1. `cp models.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C1_models.py.bak`（納入 git add）。2. 對齊既有 SQLAlchemy 2.0 風格新增 `class GlobalGlossary`：`id` PK int；`source_lang`/`target_lang` `String`；`term_key` `String`（存 lowercase+strip）；`original_term`/`translation` `Text`/`String`；`domain` `String(3)`（LCC、由 DOMAIN-NORM 提供）；`source` `String`（`auto_extract`/`manual_edit`）；`created_at`。3. `__table_args__`：`UniqueConstraint("source_lang","target_lang","term_key","domain", name="uq_glossary_lang_term_domain")` + `Index("ix_glossary_cascade","source_lang","target_lang","domain")`（級聯查詢加速）。4. **不改 `Paper` 等既有表**。5. `create_all` 自動建表。6. 產 C1 執行報告（baton/）。 |

### C2 — Glossary Core & Cascading Retrieval（術語庫核心與級聯優先權查詢）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `processor/glossary_extractor.py`（核心類，尚不對外接線） |
| **安全性** | 🟢 高 — 純新增模組、不接線既有 pipeline |
| **可逆性** | 🟢 高 — 刪除新檔即還原 |
| **驗收 grep 條件** | `grep -nE "query_cascade\|on_conflict_do_nothing\|session.begin\|def extract_terms" processor/glossary_extractor.py` |
| **依賴關係** | C1（GlobalGlossary 表） |
| **具體實作細節** | 1. `glossary_extractor.py` 定義 `class GlossaryManager`（依賴注入 `llm`/`session_factory`，對齊 DOMAIN-NORM C2 pattern）。2. `query_cascade(source_lang, target_lang, domain)->dict[str,str]`：`SELECT ... WHERE source_lang=? AND target_lang=? AND domain IN (domain,'general')`；Python 先填 `general` 再以**專屬 LCC 覆寫**（dict update 順序保證專屬優先），回 `{term_key: translation}`。3. `extract_terms(text, source_lang, target_lang, domain)->list[tuple]`：LLM（cheap model、Temp=0.0、System Instruction 定義「回原文術語+繁中譯詞」）；**交易外**呼叫。4. `upsert_terms(rows, source='auto_extract')`：`with session.begin(): session.execute(sqlite_insert(GlobalGlossary)....on_conflict_do_nothing(index_elements=[四欄]))`（極短交易、冪等）。5. 全程 try/except + `logger.error(..., exc_info=True)`，失敗不阻斷。6. 產 C2 執行報告（baton/）。 |

### C3 — Translate Integration & Backfill（翻譯管線術語融合與增量回填）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/translate_processor.py`（L237-239 旗標閘門、先 `.bak`）+ `pipeline_core.py`（translate 後回填 hook、先 `.bak`） |
| **安全性** | 🟡 中 — 動業務代碼；但全旗標閘門、預設 False byte 等價舊行為 |
| **可逆性** | 🟢 高 — 還原兩 `.bak` |
| **驗收 grep 條件** | `grep -nE "LLM_USE_GLOSSARY_ALIGN\|GLOSSARY-CORE C3\|query_cascade\|backfill" processor/translate_processor.py pipeline_core.py` |
| **依賴關係** | C2（GlossaryManager）+ DOMAIN-NORM `normalize_to_lcc` |
| **具體實作細節** | 1. 兩檔改前各 `cp ... .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C3_<name>.bak`（納入 git add）。2. `translate_processor.py:237-239` 以 `# === [GLOSSARY-CORE C3 START/END] ===` 包裹：`if settings.LLM_USE_GLOSSARY_ALIGN:` → `GlossaryManager().query_cascade(src,tgt,self.domain)` 取術語、組「術語對照表（不可違背）」塊附 `system_prompt`；`else:` 維持既有 `本文件主題領域：{domain}` 原句（byte 等價）。3. `pipeline_core.py` `_stage_translate`（L692-700）尾端以 C3 標記包裹旗標閘門：True 時把本文提取術語經 `upsert_terms` 背景回填（極短交易、try/except 不阻塞 core）。4. **書籍並行 `ParallelChapterTranslator` 雙層融合不在本 Commit**（§9 延後）。5. 產 C3 執行報告（baton/）。 |

### C4 — Chat Injection（前台問答術語強約束注入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `AI_professor_chat.py`（L329-335 旗標閘門、先 `.bak`） |
| **安全性** | 🟡 中 — 動業務代碼；旗標閘門、預設 False byte 等價 |
| **可逆性** | 🟢 高 — 還原 `.bak` |
| **驗收 grep 條件** | `grep -nE "LLM_USE_GLOSSARY_ALIGN\|GLOSSARY-CORE C4\|query_cascade" AI_professor_chat.py` |
| **依賴關係** | C2（GlossaryManager） |
| **具體實作細節** | 1. `cp AI_professor_chat.py .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C4_AI_professor_chat.py.bak`。2. L329-335 既有 `if domain:` 區塊內以 `# === [GLOSSARY-CORE C4 START/END] ===` 包裹追加：`if settings.LLM_USE_GLOSSARY_ALIGN and domain:` → `GlossaryManager().query_cascade(src,tgt,domain)` 取術語、組「不可違背 System constraint：以下專有名詞譯法必須一致」塊附 `character_prompt`/`explain_prompt`；旗標 OFF 時既有 `當前文件主題：{domain}` 行為 byte 不變。3. 不動 `messages` 組裝（L338）與下游。4. 產 C4 執行報告（baton/）。 |

### C5 — Hot-Pluggable CLI（自癒補丁 CLI 工具）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `tools/manage_glossary.py` |
| **安全性** | 🟢 高 — 獨立 CLI、不接線 runtime 流量 |
| **可逆性** | 🟢 高 — 刪除新檔 |
| **驗收 grep 條件** | `grep -nE "init\|test-pipeline\|backfill-existing-papers\|argparse" tools/manage_glossary.py` |
| **依賴關係** | C2（GlossaryManager）+ DOMAIN-NORM `normalize_to_lcc` |
| **具體實作細節** | 1. `argparse` 三子命令：`--init`（`Base.metadata.create_all`）；`--test-pipeline --pdf [path]`（`DomainDetector.detect`→`normalize_to_lcc`→`query_cascade` 比對→`extract_terms`→`upsert_terms`→輸出 `{stem}_glossary.json`、離線閉環）；`--backfill-existing-papers`（掃 `papers` 表、對每筆 `domain` 跑 `normalize_to_lcc` 升級為 LCC、極短交易批次寫回）。2. 入口 `from utils.logging_config import setup_logging`（CLI 對齊 logging SOP、取代 basicConfig）。3. 全程 try/except + 結構化 log。4. 產 C5 執行報告（baton/）。 |

### C6 — Unit Tests（單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `tests/test_glossary_core.py` |
| **安全性** | 🟢 高 — 純測試新增 |
| **可逆性** | 🟢 高 — 刪除測試檔 |
| **驗收 grep 條件** | `pytest tests/test_glossary_core.py -v`（5 passed）+ `pytest tests/ -q`（零既有迴歸） |
| **依賴關係** | C1-C5 |
| **具體實作細節** | 1. mock LLM + file-based SQLite + FK ON fixture（對齊 `tests/test_domain_normalizer.py` / `test_paper_chunks_schema.py`）。2. 五測試（plan §6.1）：① `test_global_glossary_unique_constraint`（同 lang+domain+term 不可寫不同譯法→IntegrityError 或 on_conflict 不覆寫）；② `test_cascading_priority_match`（`BF` 專屬譯法覆寫 `general` 通用譯法）；③ `test_book_glossary_fusion_priority`（雙層融合時中央歷史術語優先權 > 本書實時提取）；④ `test_chat_glossary_injection`（旗標 on 時 query_cascade 結果被組進注入塊）；⑤ `test_glossary_cli_backfill_existing`（`--backfill-existing-papers` 批量升級 domain 正確）。3. 產 C6 執行報告（baton/）。 |

### C7 — Checkout（收官與成果審計）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`+`git add` baton/ plan_v2→`plans/` + tasks→`tasks/` + C1-C7 報告→`executions/`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ |
| **驗收 grep 條件** | `ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ \| grep GLOSSARY-CORE`（齊全）；`ls .claude-logs/baton/ \| grep -c GLOSSARY-CORE` # 期望：0 |
| **依賴關係** | C1-C6（全部報告已產於 baton/） |
| **具體實作細節** | 1. Conformance 三維度驗收（目標規格 U1-U5 / 測試 §6.1-§6.6 / 不可動清單 git 全量證據 + 上游：domain 一律經 `normalize_to_lcc` 取得）→ 產 `baton/2026-06-03_GLOSSARY-CORE_C7_執行.md`。2. **一次性歸檔**（WORKFLOW_SOP §3）：`mv` plan_v2 baton→`plans/`；tasks baton→`tasks/`；C1-C7 `_執行.md` baton→`executions/`。3. `git add` 上述正式檔 + `models.py`/`glossary_extractor.py`/`translate_processor.py`/`pipeline_core.py`/`AI_professor_chat.py`/`manage_glossary.py`/`test_glossary_core.py` + 全部 `.bak` + prompts/INDEX + TODO（**明確列檔、嚴禁 `git add -A`**）。4. **更新 TODO.md**：GLOSSARY-CORE 移入 ✅ 已完成表（Hash 待 baron 回填）+ 刪 active 條目 + 索引標 ✅ + 歷史 Hash 自癒。5. 驗 baton/ 無 GLOSSARY-CORE 殘留。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3）。 |

---

## §9 Open Questions

| 開放問題 | 推薦答案 | 理由 |
|---|---|---|
| **書籍並行 `ParallelChapterTranslator` 雙層融合（plan U3 後半）落地時機** | **C3 只做單文 translate 路徑 + 回填；書籍融合介面預留、實接延後至 TRANSLATE-BOOK 落地後的整合路次** | `TRANSLATE-BOOK` 仍為 baton plan_v4（未實作），其 `GlobalTranslator`/`ParallelChapterTranslator` 不存在，無法接線；強接會造 import 失敗。`GlossaryManager.query_cascade`/`upsert_terms` 為共用介面、屆時 TRANSLATE-BOOK 直接消費即可。 |
| **`source_lang`/`target_lang` 由誰提供** | **translate/chat 端以既有語系設定推導（預設 `source`=偵測語、`target`='zh-tw'）；C2 介面接受參數、不寫死** | 對齊既有翻譯管線語系；避免 GLOSSARY-CORE 自建語系偵測（超範圍）。 |
| **回填是否同步阻塞 translate** | **背景/極短交易 + try/except、不阻塞 core**（對齊 API-PERF 並發底座精神） | translate 產物為主、術語回填為輔；回填失敗不得影響使用者譯文產出。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GLOSSARY-CORE 的 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` C1-C7 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | LCC 純消費 DOMAIN-NORM；LLM 提取在 DB 交易外；業務代碼接入須旗標閘門+標記+`.bak`+旗標 OFF byte 等價；嚴禁自動 git commit/push；C1-C6 報告嚴禁移動、唯 C7 一次性歸檔 |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 領域 LCC 收斂唯一源在 DOMAIN-NORM plan；旗標定義唯一源在 settings（DOMAIN-NORM 建）；本檔僅定義拆分細節與驗收指令 |

### §99.2 Revision 歷程

- v1 (2026-06-03)：初版拆分，依 plan v2 §2（U1–U5）拆為 7 Commit——C1 Database Schema（GlobalGlossary 表+聯合唯一索引）/ C2 Glossary Core & Cascading Retrieval（級聯查詢+LLM 提取+冪等回填、LLM 在交易外）/ C3 Translate Integration & Backfill（translate_processor 旗標閘門注入+pipeline_core 回填 hook、單文路徑、書籍融合延後）/ C4 Chat Injection（AI_professor_chat 旗標閘門術語強約束）/ C5 Hot-Pluggable CLI（manage_glossary.py 三子命令）/ C6 Unit Tests（5 pytest）/ C7 Checkout 收官；LCC 純消費 DOMAIN-NORM `normalize_to_lcc`；旗標複用 `LLM_USE_GLOSSARY_ALIGN` 預設 False；業務代碼接入全旗標閘門+標記+`.bak`；不給 commit 建議；§9 標註書籍融合延後 / 語系來源 / 回填非阻塞三項 Open Questions。
