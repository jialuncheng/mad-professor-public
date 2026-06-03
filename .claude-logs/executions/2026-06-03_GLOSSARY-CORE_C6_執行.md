# GLOSSARY-CORE C6 — Unit Tests（單元測試）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C6 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C6 + plan v2 §6.1 |
| **次級參考** | tests/test_domain_normalizer.py / test_paper_chunks_schema.py（fixture pattern）/ database_SOP |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`595e3d8`（BE-Fix: commit missing RAG-14 backend multi-tag routing）；C5 `tools/manage_glossary.py` 尚未經 baron commit（仍 untracked）。
- **完成狀態**：C6 新建 `tests/test_glossary_core.py`（5 pytest 全綠）落地 worktree，全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C6 | `待 baron 回填` | BE-Refactor: C6 — Unit Tests（單元測試） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `tests/test_glossary_core.py` | **新建**（約 200 行、5 測試 + fixture + MockLLM） | 純測試新增；無修改業務代碼（無 .bak、無包裹標記） |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C6_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C6→✅ / C7→🟡 WIP | C5 仍 `待 baron 回填`（C5 未 commit、無 Hash 可填） |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C6_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
?? tests/test_glossary_core.py
```

## §4 修法說明

依 tasks §8 C6 + plan v2 §6.1，新建 `tests/test_glossary_core.py`，對齊既有 file-based SQLite + FK ON fixture + mock LLM pattern。

### §4.1 fixture + mock（FK ON、LLM 不實打、DB 隔離）
```python
@pytest.fixture
def session_factory():
    # file-based 臨時 SQLite + PRAGMA foreign_keys=ON + create_all → sessionmaker
    ...
class _MockLLM:
    def chat(self, messages, temperature=0.5, stream=True, model=None): ...
```

### §4.2 五測試（plan §6.1）
| # | 測試 | 驗證點 |
|---|---|---|
| 1 | `test_global_glossary_unique_constraint` | 同 `(de,zh-tw,riesling,general)` 寫第二譯法 → `IntegrityError`（聯合唯一約束物理生效） |
| 2 | `test_cascading_priority_match` | `general`→「存在」、`BF` 專屬→「此在」；`query_cascade('BF')` 回「此在」（**專屬覆寫 general**） |
| 3 | `test_book_glossary_fusion_priority` | `{**book_glossary, **sqlite_glossary}` → 中央歷史「雷司令」覆寫本書「麗絲玲」；本書獨有「不甜」保留 |
| 4 | `test_chat_glossary_injection` | 旗標 ON + `query_cascade` → 組「術語強約束 System constraint」含 `riesling → 雷司令` 注入 system_message |
| 5 | `test_glossary_cli_backfill_existing` | `cmd_backfill_existing_papers`（mock normalize_to_lcc）→ p1「半導體」→`TK`、p2`general` 不變 |

## §5 測試結果

### §5.1 C6 五測試全綠（真實輸出）
```
$ venv/bin/python -m pytest tests/test_glossary_core.py -v
tests/test_glossary_core.py::test_global_glossary_unique_constraint PASSED [ 20%]
tests/test_glossary_core.py::test_cascading_priority_match        PASSED [ 40%]
tests/test_glossary_core.py::test_book_glossary_fusion_priority   PASSED [ 60%]
tests/test_glossary_core.py::test_chat_glossary_injection         PASSED [ 80%]
tests/test_glossary_core.py::test_glossary_cli_backfill_existing  PASSED [100%]
============================== 5 passed in 0.42s ===============================
```

### §5.2 全套件零迴歸（+5 新測試）
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 457 passed, 3 skipped in 63.08s
```
- 457 passed = C6 前 452 + 本次新增 5，**淨增 5、零既有迴歸**。
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C6 無關。

### §5.3 Mock / FK 安全硬規則落實
- fixtures 設 `PRAGMA foreign_keys=ON`（test 1 唯一約束驗證依賴 SQLite 約束生效）。
- LLM 全程 `_MockLLM` / monkeypatch `normalize_to_lcc`，**無實打外部 API**。

## §6 不可動清單遵守

- [x] 僅**新增** `tests/test_glossary_core.py`，**無改任何既有業務 / DB 代碼**。
- [x] `models.py` / `glossary_extractor.py` / `manage_glossary.py` / `translate_processor.py` / `pipeline_core.py` / `AI_professor_chat.py` — **未觸碰**（測試僅 import）。
- [x] DOMAIN-NORM `normalize_to_lcc` — 測試以 monkeypatch mock、**未改原始碼**。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_GLOSSARY-CORE_C6_執行.md` 暫存 baton/，連同 C1-C5 報告 + plan_v2 + tasks 待 C7 收官一次性歸檔。
- **下一步**：C7 — Checkout：三維度 Conformance 驗收（U1-U5 / 測試 §6.1-§6.6 / 不可動清單 git 全量證據）+ 一次性 mv plan_v2/tasks/C1-C7 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒。待 baron 下達 C7 收官提示詞。

## §8 baron 執行命令

```bash
# 1. 本 Commit 無修改既有檔，故無備份
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add tests/test_glossary_core.py
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C6_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C6_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C6_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C6_commit_msg.txt

# 4. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C6_commit_msg.txt
```
