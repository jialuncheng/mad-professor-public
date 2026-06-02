# PIPE-CORE OP-2 — 工廠與策略基類 執行報告

---

**任務代號**：PIPE-CORE OP-2
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md` §8 OP-2
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：OP-1（`aa786a1`）已 ship，`pipelines/` 有 contracts + context；無策略層。
- **完成狀態**：✅ OP-2 完整落地且全綠。新建 `pipelines/base_strategy.py`（`DocumentStrategy` ABC + `NullStrategy` 哨兵）+ `pipelines/factory.py`（`PipelineFactory` 註冊/查找/降級）；更新 `__init__.py` 匯出；`tests/test_pipe_core.py` 追加 6 項（共 14 全綠）。**零既有業務代碼改動**。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-2 | `base_strategy.py`（ABC + NullStrategy）+ `factory.py`（註冊/LiteDoc 降級）+ 測試追加（14 pytest） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/base_strategy.py` | — | DocumentStrategy ABC（四 Phase + rag_char_threshold）+ NullStrategy 哨兵 |
| 新建 | `pipelines/factory.py` | — | PipelineFactory（register/get_strategy + LiteDoc 降級 + NullStrategy fallback） |
| 修改 | `pipelines/__init__.py` | — | 匯出 DocumentStrategy / NullStrategy / PipelineFactory |
| 修改 | `tests/test_pipe_core.py` | `.claude-logs/archive/2026-06-02_PIPE-CORE_OP-2_test_pipe_core.py.bak` | 追加 6 工廠/策略測試（registry 隔離 fixture） |
| 新建 | `.claude-logs/prompts/2026-06-02_PIPE-CORE_OP-2_run_提示詞.md` | — | OP-2 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-2 提示詞 |
| 修改 | `.claude-logs/TODO.md` | — | PIPE-CORE OP-2 → ✅ / OP-3 → 🟡 WIP |

> ⚠️ **.bak 強制納入**：`.claude-logs/archive/2026-06-02_PIPE-CORE_OP-2_test_pipe_core.py.bak` 已於 §8 git add 清單包含（審計存檔）。
> ⚠️ 本報告自身（baton/）**不入** §8 git add 清單（baton 暫存鐵律）。

---

## §4 修法說明

### §4.1 `pipelines/base_strategy.py` — DocumentStrategy ABC + NullStrategy
`DocumentStrategy(abc.ABC)` 宣告四抽象方法 `run_phase1..4(ctx)`（回傳對應合約）+ 類屬性 `rag_char_threshold:int=10`（≥10 或 ≥3 由五路覆寫，SPEC §3.1）。`NullStrategy(DocumentStrategy)` 四 Phase 一律 `raise NotImplementedError`（未註冊策略時顯式失敗哨兵、防靜默通過）。

```python
class NullStrategy(DocumentStrategy):
    def run_phase1(self, ctx): raise NotImplementedError(self._MSG)
    # run_phase2/3/4 同
```

### §4.2 `pipelines/factory.py` — PipelineFactory
類級 `_registry: dict[str, type[DocumentStrategy]]` + `register(doc_type)` 裝飾器 / `register_strategy()` 顯式註冊 + `get_strategy(doc_type)`：命中回實例 → 未命中且 litedoc 已註冊則降級 LiteDoc（SPEC §3.3 最後防線）→ 否則回 NullStrategy 哨兵。logging SOP 合規（模組級 logger，註冊 info / 降級 warning）。

```python
@classmethod
def get_strategy(cls, doc_type):
    if doc_type in cls._registry: return cls._registry[doc_type]()
    if _FALLBACK_DOC_TYPE in cls._registry: return cls._registry[_FALLBACK_DOC_TYPE]()
    return NullStrategy()
```

### §4.3 `tests/test_pipe_core.py` — 追加 6 工廠/策略測試
`clean_registry` fixture（快照還原 `_registry`，測試隔離）；`_StubStrategy`（四 Phase 回最小合法合約）。覆蓋：命中註冊策略 / 裝飾器註冊 / 未命中降級 LiteDoc / 無策略回 NullStrategy / NullStrategy 四 Phase 拋 NotImplementedError / stub 四 Phase 回合法合約。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s pipelines/ tests/test_pipe_core.py
 M pipelines/__init__.py
 M tests/test_pipe_core.py
?? pipelines/base_strategy.py
?? pipelines/factory.py
# baton/ 報告 gitignored，未列入（合規）
```

### §5.2 OP-2 + OP-1 全測試（全綠）
```bash
$ ./venv/bin/python -c "from pipelines import PipelineFactory, DocumentStrategy, NullStrategy; print('import OK')"
import OK

$ ./venv/bin/python -m pytest tests/test_pipe_core.py -v
... (14 items)
tests/test_pipe_core.py::test_factory_hit_returns_registered_strategy PASSED
tests/test_pipe_core.py::test_factory_decorator_register PASSED
tests/test_pipe_core.py::test_factory_unknown_falls_back_to_litedoc PASSED
tests/test_pipe_core.py::test_factory_no_strategy_returns_nullstrategy PASSED
tests/test_pipe_core.py::test_nullstrategy_four_phases_raise PASSED
tests/test_pipe_core.py::test_stub_strategy_phases_return_valid_contracts PASSED
========================= 14 passed in 0.02s =========================
```

### §5.3 既有測試零迴歸
```bash
$ ./venv/bin/python -m pytest tests/ -q
1 failed, 426 passed, 3 skipped in 41.52s
```
- **唯一失敗 `test_settings_log_format_default_auto` 為環境誘發、非 OP-2 迴歸**：`.env:54 LOG_FORMAT=json` 覆寫測試 `"auto"` 預設斷言。OP-2 僅新增 `pipelines/{base_strategy,factory}.py` + 改 `__init__`/測試，**未動 `settings.py`/`utils/`**。426 passed 含 OP-2 新增 6 項。

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger.error|traceback.format_exc" pipelines/*.py`）：無命中（合規）——factory 僅 info/warning，無 error 拼接。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/*.py`）：無命中（合規）——零 DB 操作。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 舊單體 | [x] ✅ 未觸碰 |
| `web_server.py` 上傳/派發入口 | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更（零 DB） |
| `processor/*` 既有模組 | [x] ✅ 未接線（ABC 只定義介面、不附具體策略） |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |
| Orchestrator 禁 doc_type 分支 | [x] ✅ 不適用（OP-2 無 orchestrator，屬 OP-3） |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-4 收官一併 `mv` + `git add` 歸檔至 `executions/`，**OP-2 階段嚴禁移動**。
- **下一步**：tasks_v2 §8 OP-3（Orchestrator 四 Phase DAG）——`orchestrator.py` 宣告式 P1→P4 + 交接點 Pydantic 驗證 + reading_ready/rag_status + Early Emit/Checkpoint/P4 派發掛點 + shadow 貫穿；驗收 `grep "doc_type ==" orchestrator.py` 須 0 命中；修改 `tests/test_pipe_core.py` 前須 `.bak` 備份。
- **消化歸檔之 baton 檔**：無（OP-4 收官統一處理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 已列）
# cp tests/test_pipe_core.py .claude-logs/archive/2026-06-02_PIPE-CORE_OP-2_test_pipe_core.py.bak
# 2. git add 清單（含 .bak 備份；排除 baton/ 暫存報告與 tasks 檔）
git add pipelines/base_strategy.py
git add pipelines/factory.py
git add pipelines/__init__.py
git add tests/test_pipe_core.py
git add .claude-logs/archive/2026-06-02_PIPE-CORE_OP-2_test_pipe_core.py.bak
git add .claude-logs/prompts/2026-06-02_PIPE-CORE_OP-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/PIPE-CORE_OP-2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-CORE_OP-2_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-CORE OP-2 — 工廠與策略基類

1. 新建 pipelines/base_strategy.py：DocumentStrategy ABC（四 Phase + rag_char_threshold）
   + NullStrategy 哨兵（四 Phase 拋 NotImplementedError、防靜默通過）。
2. 新建 pipelines/factory.py：PipelineFactory 註冊表 + get_strategy（命中 / 未命中降級
   LiteDoc SPEC §3.3 / 無策略回 NullStrategy）。
3. 更新 pipelines/__init__.py 匯出策略與工廠介面。
4. tests/test_pipe_core.py 追加 6 工廠/策略測試（registry 隔離 fixture），共 14 pytest 全綠；
   既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發、非本次）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-CORE OP-2 工廠與策略基類落地與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-4 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-4 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-4 前不入版控；嚴禁本報告自身入 git add |
| **改版觸發條件** | 執行報告修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-2 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-2 執行——`pipelines/base_strategy.py`（DocumentStrategy ABC 四 Phase + rag_char_threshold + NullStrategy 哨兵）+ `pipelines/factory.py`（PipelineFactory register/get_strategy + LiteDoc 降級 + NullStrategy fallback）+ `__init__.py` 匯出；`tests/test_pipe_core.py` 追加 6 測試（registry 隔離 fixture）共 14 pytest 全綠；既有測試零迴歸（唯一失敗為 .env LOG_FORMAT=json 環境誘發）；零業務代碼改動；修改測試檔前 `.bak` 備份；TODO OP-2→✅ / OP-3→🟡 WIP。
