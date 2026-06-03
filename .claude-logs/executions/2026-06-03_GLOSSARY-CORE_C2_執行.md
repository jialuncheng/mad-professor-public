# GLOSSARY-CORE C2 — Glossary Core & Cascading Retrieval（術語庫核心與級聯優先權查詢）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C2 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C2 + plan v2 §2 U2 |
| **次級參考** | database_SOP 原則 1+2 / logging_SOP / DOMAIN-NORM C2（pattern 對齊） |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`03d85c8`（BE-Refactor: C1 — Database Schema）
- **完成狀態**：C2 新建 `processor/glossary_extractor.py`（GlossaryManager）落地 worktree，import + 功能 smoke test + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C2 | `待 baron 回填` | BE-Refactor: C2 — Glossary Core & Cascading Retrieval（術語庫核心與級聯優先權查詢） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/glossary_extractor.py` | **新建**（約 230 行） | C2 核心類 GlossaryManager；**未對外接線**（translate/chat/CLI 屬 C3/C4/C5） |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C2_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C2→✅ / C3→🟡 WIP + C1 Hash 自癒（`待 baron 回填`→`03d85c8`） | — |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C2_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

- **備份**：純新建檔案、**無修改任何既有檔**，故無 `.bak`、無 C2 包裹標記（包裹標記僅在改既有檔時觸發）。

`git status -s`：
```
?? processor/glossary_extractor.py
```

## §4 修法說明

依 tasks §8 C2 + plan v2 §2 U2，新建 `processor/glossary_extractor.py`，對齊 DOMAIN-NORM C2 的依賴注入 + 交易邊界 + 冪等 upsert pattern。

### §4.1 級聯優先權查詢（U2、read-only 極短 session）
```python
def query_cascade(self, source_lang, target_lang, domain) -> Dict[str, str]:
    domains = ['general'] + ([domain] if domain and domain != 'general' else [])
    # SELECT WHERE source_lang=? AND target_lang=? AND domain IN (...)
    # 記憶體：general 先填、專屬 domain 後覆寫（dict 後寫覆蓋）→ 專屬優先
    merged = {**general_map, **specific_map}
```

### §4.2 LLM 術語提取（**交易外**、不持有 session）
- System Instruction 定義「抽取原文術語 + 繁中譯詞、只收專有名詞、輸出 JSON 陣列」。
- `temperature=0.0` + `stream=False` + `model=settings.LLM_DOMAIN_MODEL`（複用 cheap model）。
- `_parse_extract_result`：容錯 ```json fence + `json.loads`，格式不符回 `[]`。

### §4.3 冪等回填（取得術語後才開極短交易、database SOP 原則 1+2）
```python
def upsert_terms(self, pairs, source_lang, target_lang, domain, source='auto_extract'):
    # term_key = lowercase+strip；同批 dedup
    with self._session_factory() as session:
        with session.begin():                       # 成功自動 commit / 失敗自動 rollback
            session.execute(
                sqlite_insert(GlobalGlossary).values(values)
                .on_conflict_do_nothing(            # 併發/重複冪等（聯合唯一約束）
                    index_elements=["source_lang","target_lang","term_key","domain"]))
```

### §4.4 交易邊界鐵律落實
`extract_terms`（外部 API）與 `upsert_terms`（DB 寫）為**獨立方法、由 caller 分開呼叫**；caller（C3 pipeline）先 extract（交易外）再 upsert（極短交易），物理上杜絕「LLM 在交易內」。全程 try/except → `logger.error(..., exc_info=True)`，失敗回空字典/空清單/0，不阻斷上游。

## §5 測試結果

### §5.1 §6.2 grep 驗收（真實輸出節錄）
```
$ grep -nE "class .*Glossary|query_cascade|on_conflict_do_nothing|session.begin|def extract_terms" processor/glossary_extractor.py
53:class GlossaryManager:
78:    def query_cascade(
122:    def extract_terms(
207:                with session.begin():
212:                        .on_conflict_do_nothing(
```

### §5.2 import 檢測
```
$ venv/bin/python -c "from processor.glossary_extractor import GlossaryManager, GENERAL_DOMAIN; print('C2 import OK', GENERAL_DOMAIN)"
C2 import OK general
```

### §5.3 功能 smoke test（mock LLM + in-memory SQLite + FK ON）
```
general 查詢: {'riesling': '雷司令'}
SB 級聯（專屬覆寫）: {'riesling': '麗絲玲'}        # 專屬 domain SB 覆寫 general
冪等後 general: {'riesling': '雷司令'} | 仍為雷司令: True   # 重複 upsert 不覆寫
提取: [('Spätburgunder', '黑皮諾')] | temp= 0.0          # extract + temperature=0.0
fence 容錯: [('Trocken', '不甜')]                         # ```json fence 解析
壞 JSON: []                                               # 格式錯 → 空清單
ALL OK
```
- 驗證級聯**專屬覆寫 general**、寫入**冪等不覆寫**、提取 **temperature=0.0**、JSON 容錯。

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 40.48s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C2（純新增未接線模組）**無關**。

### §5.5 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：無裸 commit（僅 `with session.begin():`）→ 無命中（合規）。
- **logging §5.1**：3 處 `logger.error(..., exc_info=True)`（query_cascade / extract_terms / upsert_terms 降級）→ 合規。

## §6 不可動清單遵守

- [x] `models.py` `Paper`/`GlobalGlossary` 等表 — **未觸碰**（C2 僅 import `GlobalGlossary`）。
- [x] DOMAIN-NORM `normalize_to_lcc` / `Domains` / `DomainMapping` — **未觸碰**。
- [x] `rag_retriever.py` / `tiling_processor.py` — **未觸碰**。
- [x] `translate_processor.py` / `pipeline_core.py` / `AI_professor_chat.py` — **未觸碰**（接線屬 C3/C4）。
- [x] 僅**新增** `processor/glossary_extractor.py`，無改任何既有檔。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_GLOSSARY-CORE_C2_執行.md` 暫存 baton/，連同 C1 報告 + plan_v2 + tasks 待 C7 收官一次性歸檔。
- **下一步**：C3 — Translate Integration & Backfill：`translate_processor.py:237-239` 旗標閘門 `query_cascade` 注入術語契約 + `pipeline_core.py` translate 後 `extract_terms`→`upsert_terms` 背景回填（單文路徑；書籍 `ParallelChapterTranslator` 融合延後）。改前各 `.bak` + C3 標記包裹。待 baron 確認 C2 後另行下達。

## §8 baron 執行命令

```bash
# 1. 本 Commit 無修改既有檔，故無備份
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add processor/glossary_extractor.py
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C2_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C2_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C2_commit_msg.txt

# 4. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C2_commit_msg.txt
```
