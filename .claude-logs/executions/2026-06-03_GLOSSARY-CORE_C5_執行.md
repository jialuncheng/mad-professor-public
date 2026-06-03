# GLOSSARY-CORE C5 — Hot-Pluggable CLI（自癒補丁 CLI）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C5 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C5 + plan v2 §2 U5 |
| **次級參考** | logging_SOP（setup_logging）/ database_SOP（批次極短交易）/ tools/regen_rag.py（CLI pattern）|
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`595e3d8`（BE-Fix: commit missing RAG-14 backend multi-tag routing）
- **完成狀態**：C5 新建 `tools/manage_glossary.py`（三子命令）落地 worktree，py_compile + CLI 子命令實跑（--init / --help / 缺參報錯 / --backfill dry-run+實寫）+ 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C5 | `待 baron 回填` | BE-Refactor: C5 — Hot-Pluggable CLI（自癒補丁 CLI） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `tools/manage_glossary.py` | **新建**（約 195 行、3 子命令 + setup_logging 入口） | 純新增；無修改既有檔（無 .bak、無包裹標記） |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C5_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C5→✅ / C6→🟡 WIP + 歷史 Hash 自癒（C4→`06bf3df` / RAG-14 補丁 `待 baron 回填`→`595e3d8`）+ 清理 RAG-14 表/索引殘渣 | 見 §4.2 |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C5_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
?? tools/manage_glossary.py
```

## §4 修法說明

### §4.1 `tools/manage_glossary.py` 三子命令（對齊 regen_rag.py）
- **`--init`** → `cmd_init`：`Base.metadata.create_all(bind=engine)` 冪等建表（含 `GlobalGlossary`）。
- **`--test-pipeline --pdf PATH`** → `cmd_test_pipeline`：離線閉環
  `DomainDetector.detect` → `normalize_to_lcc`（消費 DOMAIN-NORM）→ `query_cascade` 比對 →
  `extract_terms`（LLM 交易外）→ `upsert_terms`（冪等）→ 輸出 `{stem}_glossary.json`。
- **`--backfill-existing-papers [--dry-run]`** → `cmd_backfill_existing_papers`：
  1. 唯讀載出 `papers.domain IS NOT NULL` 清單（極短交易）。
  2. **交易外**對每筆跑 `normalize_to_lcc`（內部可能呼 LLM）。
  3. **分批極短交易寫回**：每 `_BACKFILL_BATCH_SIZE=10` 筆一個 `with session.begin():`（防 SQLite locked、database SOP）；每批 try/except 隔離、失敗跳過續行。

### §4.2 日誌與批次安全硬規則落實
- **logging SOP**：入口 `from utils.logging_config import setup_logging; setup_logging()`，**無任何 `logging.basicConfig()` 呼叫**（grep 確認 2 命中皆為 docstring/註解文字）。
- **批次安全邊界**：backfill 分批 `session.begin()`、每批 ≤10 筆，杜絕長交易鎖庫。

### §4.3 附帶 TODO 治理自癒（依本提示詞 self-heal 指令 + §1.4）
- C4 Hash 回填 `06bf3df`；RAG-14「Fix (補)」+ 索引條目回填 `595e3d8`。
- 清理 RAG-14 完成表與索引區的**殘渣行**（先前手動編輯遺留的 `+|` / `- -` / `+ -` diff 衝突標記與重複列），回復單一乾淨列。

## §5 測試結果

### §5.1 §6.5 grep 驗收（真實輸出節錄）
```
$ grep -nE "init|test-pipeline|backfill-existing-papers|argparse|setup_logging" tools/manage_glossary.py
19:import argparse
35:def cmd_init() -> int:
... --init / --test-pipeline / --backfill-existing-papers 子命令齊全
$ grep -nE "logging\.basicConfig\(" tools/manage_glossary.py   → 無命中（合規，僅註解提及）
```

### §5.2 py_compile
```
$ venv/bin/python -m py_compile tools/manage_glossary.py
compile OK
```

### §5.3 CLI 子命令實跑
```
$ python tools/manage_glossary.py --help          → usage 正常顯示三子命令
$ cmd_init()（in-memory 隔離）                      → rc:0 | global_glossaries 建成: True
$ python tools/manage_glossary.py --test-pipeline  → [ERROR] --test-pipeline 需搭配 --pdf <path>（缺參正確報錯）
$ cmd_backfill_existing_papers（in-memory + 2 paper + mock normalize_to_lcc）：
    dry-run → 列印待升級
    實寫    → p1.domain: TK | p2.domain: general（半導體→TK 升級、general 不變）→ backfill OK
```

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 52.81s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C5 無關。

### §5.5 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：backfill 寫入走 `with session.begin():`（無裸 commit）→ 合規。
- **logging §5.1**：CLI 用 `setup_logging()`、降級用 `logger.error(..., exc_info=True)`、無 basicConfig → 合規。

## §6 不可動清單遵守

- [x] 僅**新增** `tools/manage_glossary.py`，**無改任何既有業務代碼**。
- [x] DOMAIN-NORM `normalize_to_lcc` / `Domains` / `DomainMapping` — **僅呼叫消費、未改**。
- [x] `models.py` / `glossary_extractor.py` / `translate_processor.py` / `pipeline_core.py` / `AI_professor_chat.py` — **未觸碰**。
- [x] `rag_retriever.py` / `tiling_processor.py` — **未觸碰**。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_GLOSSARY-CORE_C5_執行.md` 暫存 baton/，連同 C1-C4 報告 + plan_v2 + tasks 待 C7 收官一次性歸檔。
- **下一步**：C6 — Unit Tests：`tests/test_glossary_core.py` 5 測試（唯一約束 / 級聯優先 / 書籍融合優先 / Chat 注入 / CLI 回填），mock LLM + file-based SQLite。待 baron 確認 C5 後另行下達。

## §8 baron 執行命令

```bash
# 1. 本 Commit 無修改既有檔，故無備份
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add tools/manage_glossary.py
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C5_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C5_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C5_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C5_commit_msg.txt

# 4. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C5_commit_msg.txt
```
