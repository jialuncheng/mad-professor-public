# PIPE-RESUME C1 — 策略骨架與工廠註冊 執行報告

---

**任務代號**：PIPE-RESUME C1
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C1
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：工作區處於 TRANSLATOR C5 收官（`b55219b`）之後；`pipelines/` 已有 PIPE-CORE 落地的 `base_strategy.py`（`DocumentStrategy` ABC 四抽象方法）/ `factory.py`（`PipelineFactory.register`/`get_strategy`）/ `context.py` / `contracts.py` / `orchestrator.py`；尚無任何具體五路策略，`get_strategy('resume')` 會降級回 `NullStrategy` 哨兵。
- **完成狀態**：新建 `pipelines/resume_pipeline.py`，以 `@PipelineFactory.register('resume')` 註冊 `ResumePipeline(DocumentStrategy)`，覆寫 `rag_char_threshold=3`（SPEC §3.1 Vision 短文檔），`__init__` 定義 interim 穿線容器 `self._raw_meta`，四方法 `run_phase1..4` 以 `NotImplementedError`（指向 C2-C5）佔位。`get_strategy('resume')` 現回 `ResumePipeline` 實例。**純新建檔案、零既有業務代碼改動、旗標未動、A 軌不受影響、線上 0 風險。**

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `pipelines/resume_pipeline.py` 骨架 + `@PipelineFactory.register('resume')` + `DocumentStrategy` 四方法 stub + `rag_char_threshold=3` + `_raw_meta` interim 容器 | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/resume_pipeline.py` | — | ResumePipeline 策略骨架；註冊插件 + 四 Phase stub（Phase 實作待 C2-C5） |

> C1 為純新建檔案，**無既有檔案修改 → 無 `.bak` 備份**。`baton/` 暫存執行報告不入 Git。

---

## §4 修法說明

### §4.1 `pipelines/resume_pipeline.py` — 新建策略骨架

全檔以 `# === [PIPE-RESUME C1 START] ===` / `# === [PIPE-RESUME C1 END] ===` 包裹（Flip/審計錨點）。關鍵結構：

```python
@PipelineFactory.register("resume")
class ResumePipeline(DocumentStrategy):
    # SPEC §3.1：Vision 短文檔 RAG 入庫字數門檻放寬至 3（保 Python/Docker 等技能詞）。
    rag_char_threshold: int = 3

    def __init__(self) -> None:
        # interim 穿線容器（tasks §9 硬前置）：P1 抽出的 phone/email/domain 暫存於此，
        # 供 P2 消費 domain 餵 normalize_to_lcc；待 custom_metadata 正式入合約後改走合約欄。
        self._raw_meta: Dict[str, Any] = {}

    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        raise NotImplementedError(_NOT_IMPLEMENTED_MSG.format(phase="run_phase1", commit="C2"))
    # run_phase2/3/4 同理，分別指向 C3/C4/C5
```

設計要點：
- **工廠註冊**：`@PipelineFactory.register("resume")` 觸發 `factory.py` 將 `resume → ResumePipeline` 入 `_registry`；`get_strategy('resume')` 不再降級 `NullStrategy`。
- **ABC 對映**：四方法簽名逐字對齊落地 `DocumentStrategy`（`base_strategy.py:35-47`）`run_phaseN(ctx)→對應凍結合約`。
- **門檻覆寫**：`rag_char_threshold=3` 覆寫 ABC 預設 10（SPEC §3.1、resume Vision 短文檔），供 C5 P4 使用。
- **interim 穿線**：`self._raw_meta` 為 tasks §9 拍板的硬前置暫存機制（`custom_metadata` 未入凍結合約前，P1→P2 穿線 `phone`/`email`/`domain`）。
- **logging SOP**：模組頂 `logger = logging.getLogger(__name__)`，無 `basicConfig`/`dictConfig`。
- **stub 安全**：四方法拋 `NotImplementedError`（非靜默通過），明示尚未落地之 Phase 與對應 Commit。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
?? pipelines/resume_pipeline.py
# （.claude-logs/baton/、prompts/、TODO.md 等文件改動另計；resume_pipeline.py 為唯一新增業務碼）
```

### §5.2 驗收腳本實際輸出

§6.1-a 類定義 + 註冊 + 四方法：
```
46:@PipelineFactory.register("resume")
47:class ResumePipeline(DocumentStrategy):
58:    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
64:    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
70:    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
76:    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
```

§6.1-b `get_strategy('resume')` 回 ResumePipeline + 屬性：
```
class= ResumePipeline | rag_char_threshold= 3 | _raw_meta= {}
```

四方法 stub 行為（拋 NotImplementedError）：
```
run_phase1 -> NotImplementedError OK
run_phase2 -> NotImplementedError OK
run_phase3 -> NotImplementedError OK
run_phase4 -> NotImplementedError OK
```

§6.1-c 策略內 0 doc_type 分支：
```
✅ 0 命中（策略內無 doc_type 分支）
```

pipelines 既有測試（防 Regression 重點）：
```
25 passed in 0.58s   # tests/test_pipe_core.py + tests/test_pipe_scaffold.py
```

全套件：
```
1 failed, 465 passed, 3 skipped in 121.11s
# 唯一 failed = tests/test_logging_config.py::test_settings_log_format_default_auto
# 既存環境性問題（.env LOG_FORMAT=json 覆寫預設 auto），跨所有歷史 commit 一致、非 C1 Regression
```

### §5.3 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**（`grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/resume_pipeline.py`）：無命中（合規）——C1 純骨架無錯誤日誌呼叫。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/resume_pipeline.py`）：無命中（合規）——C1 無任何 DB 操作。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` 業務代碼 | [x] ✅ 未觸碰 |
| `processor/resume_processor.py` / `rag_processor.py` / 三大真理源 | [x] ✅ 未觸碰（C1 不接線） |
| `pipelines/contracts.py` `IngestionMetadataSpec`（不擴 custom_metadata） | [x] ✅ 未變更 |
| `pipelines/base_strategy.py` / `factory.py` / `context.py` / `orchestrator.py` | [x] ✅ 僅繼承/註冊、未改本體 |
| `pipelines/__init__.py`（不自動 import 策略） | [x] ✅ 未改（C1 驗收以顯式 import 觸發註冊） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端 | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存於 `baton/`、不入版控，待 C7 收官時以 `mv` + `git add` 一次性歸檔至 `executions/`，恢復 `baton/` 只剩 README。
- **下一步**：tasks.md C2 — P1 Ingestion（Vision 整份解析與元數據）；由 baron 另行下達執行提示詞觸發。
- **消化歸檔之 baton 檔**：無（C1 為首個實作 Commit）。
- **附帶（非本 Commit 業務碼）**：歷史 Hash 自癒——TODO.md L22 TRANSLATOR C5 佔位符 `待 baron 回填` 已回填真實 hash `b55219b`（git show 確認該 commit 歸檔 TRANSLATOR plan_v10/tasks_v1/C1-C5 報告）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案：無（C1 純新建檔、無既有檔案修改）

# 2. git add 清單（僅本次 C1 新增程式碼；baton/ 暫存報告嚴禁加入）
git add pipelines/resume_pipeline.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C1_msg.txt
```

### §8.2 commit message 草稿

（草稿已寫入 `/tmp/PIPE-RESUME_C1_msg.txt`）

```
BE-Refactor: PIPE-RESUME C1 — 策略骨架與工廠註冊（插件註冊與四方法骨架）

新建 pipelines/resume_pipeline.py 骨架並以 @PipelineFactory.register('resume') 註冊；
ResumePipeline 繼承 DocumentStrategy、覆寫 rag_char_threshold=3（SPEC §3.1 Vision 短文檔）、
定義 _raw_meta interim 穿線容器（custom_metadata 硬前置）、四方法 run_phase1..4 以
NotImplementedError 佔位指向 C2-C5。純新建檔零既有改動、旗標未動、線上 0 風險。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C1 的代碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C1 執行唯一源，不重複 tasks 六維度實作細節、不重複 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C1 執行完畢產出報告——新建 `pipelines/resume_pipeline.py` 骨架 + 工廠註冊 + 四方法 stub；25 pipelines 測試綠 / 全套件 465 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。
