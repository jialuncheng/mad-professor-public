# PIPE-LITEDOC C2 執行報告 — LiteDoc 骨架與三 key 註冊（策略分派）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C2 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C2` |
| 次級參考 | plan v3 §2 U1;DocumentStrategy ABC（base_strategy）;resume/slides 註冊範式 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C2)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C1（`b1012bc`、section_engine HTML 扉頁 formatter）已 ship;factory `_registry` 僅 resume/slides、litedoc 未建 → unknown 降級回 NullStrategy 哨兵。
- **完成狀態**：新建 `pipelines/litedoc_pipeline.py`（三 key 註冊 + 四 Phase strict stub）+ `pipelines/__init__.py` 補註冊 import + `tests/test_litedoc_pipeline.py` 分派測試。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U1`（策略註冊與分派：`@register('litedoc'/'news'/'web')` + unknown 經 factory fallback 承接、主幹零 doc_type 分支）;無偏離。C2 為骨架——四 Phase strict stub、具體 P1-P4 屬 C3-C6。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C2 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C2 — LiteDoc 骨架與三 key 註冊（策略分派）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 新增（LiteDocPipeline 骨架）| **本 commit git add** |
| `pipelines/__init__.py` | 修改（註冊 import）| **本 commit git add** |
| `tests/test_litedoc_pipeline.py` | 新增（分派測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C2___init__.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C2_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C2 ✅ / C3 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C2_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C2 ...] ===` 包裹）
- **`litedoc_pipeline.py`（新）**：
  - `@PipelineFactory.register("litedoc")` + `@register("news")` + `@register("web")` **三裝飾器疊加**於 `class LiteDocPipeline(DocumentStrategy)`（每裝飾器 call register_strategy 並回傳 cls → 三 key 皆註冊）。
  - `rag_char_threshold = 10`（litedoc 長篇散文型、非 slides/resume ≥3、對齊 master plan v10 L183 + rag_indexer 預設）。
  - 四 `run_phase1..4` **strict stub**：拋 `NotImplementedError(_STUB_MSG)`（防靜默跑空通過、同 NullStrategy 範式;C3-C6 才實作）。
- **`__init__.py`**：PIPE-SLIDES import 後補 `from pipelines import litedoc_pipeline`（觸發三裝飾器註冊、同 resume/slides C7-hotfix 教訓範式）。
- **`tests/test_litedoc_pipeline.py`（新）**：分派測試〔litedoc/news/web 三 key → LiteDocPipeline / unknown → fallback LiteDocPipeline / threshold==10 / 四 Phase strict stub 拋 NotImplementedError〕。

關鍵片段：
```python
@PipelineFactory.register("litedoc")
@PipelineFactory.register("news")
@PipelineFactory.register("web")
class LiteDocPipeline(DocumentStrategy):
    rag_char_threshold: int = 10
    def run_phase1(self, ctx): raise NotImplementedError(self._STUB_MSG)
    ...
```

## §5 測試結果
### §5.1 §6.2 C2 驗收 grep
```
三 key 註冊：litedoc_pipeline.py:31-33（@register litedoc/news/web）
__init__ 註冊 import：1;四 stub：4/4;NotImplementedError：5;C2 包裹：litedoc 2 / init 2
```
### §5.2 分派測試 + 全套件 pytest
```
pytest tests/test_litedoc_pipeline.py -q → 9 passed
  〔litedoc/news/web 三 key 分派 ×3 + unknown fallback + threshold==10 + 四 Phase strict stub ×4〕
pytest tests/ -q → 1 failed, 670 passed, 3 skipped（670＝661 基線 + 9 新;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（logger.error / format_exc）：0 命中（合規）
database（裸 commit）：0 命中（合規;骨架無 DB 交易）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：pipelines/__init__.py(M) + pipelines/litedoc_pipeline.py(??) + tests/test_litedoc_pipeline.py(??)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| `section_engine.py`（C1 已加 formatter）| [x] ✅ 本 commit 未碰 |
| `rag_indexer.py` / `contracts.py` | [x] ✅ 零碰 |
| `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| 三大共用真理源 / A 軌全部 | [x] ✅ 零碰 |
| `DocumentStrategy` ABC / `factory` 機制 | [x] ✅ 僅新增註冊、未改機制 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅新建 litedoc_pipeline.py + test + 改 __init__（plan/tasks §8 C2 範圍）;section_engine/其他策略/合約零碰（git status 證）。
- **(b) 無關 / 違規?**：否。骨架 + 三 key 註冊 + 分派測試、無冗餘;四 Phase strict stub 防靜默通過（同 NullStrategy 範式）。msg 簽名校正 Opus 4.8（提示詞模板誤植 Sonnet）。符 CLAUDE.md（baton 不 add、不自發 commit）。
- **(c) 推進哪個 U-N?**：U1（策略註冊與分派）;無做白工——C3-C6 將於此骨架上實作 P1-P4。

## §7 銜接
- baton 狀態：C2 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C3 — P1 MinerU 攝入與 metadata 旁路**（MinerU+md_cleaner + DocAnalyzer 映射 U2.1 + 文字 metadata + URL publisher 解碼 + raw_metadata 旁路）→ IngestionMetadataSpec。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/litedoc_pipeline.py pipelines/__init__.py tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C2___init__.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C2_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C2_msg.txt）
cat > /tmp/PIPE-LITEDOC_C2_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C2 — LiteDoc 骨架與三 key 註冊（策略分派）

- 新建 pipelines/litedoc_pipeline.py：@PipelineFactory.register('litedoc'/'news'/'web') 三裝飾器
  疊加於 LiteDocPipeline(DocumentStrategy)；四 Phase strict stub（NotImplementedError、防靜默通過）；
  rag_char_threshold=10（長篇散文門檻、對齊 master plan v10 L183）。
- pipelines/__init__.py 補 from pipelines import litedoc_pipeline 觸發註冊（同 resume/slides 範式）。
- unknown doc_type 經 factory _FALLBACK_DOC_TYPE='litedoc' 自動承接。

驗證：分派測試 9 passed（litedoc/news/web 三 key + unknown fallback + threshold + 四 stub）；
全套件 670 passed（661 基線 + 9；唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logging/database 無命中；
section_engine/其他策略/合約零碰。baton（plan/tasks/C2 報告）未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C2_msg.txt
```

## §9 回退方式
`git revert <C2 hash>`（或刪 litedoc_pipeline.py + test + 自 .bak 還原 __init__.py）。

---
### 結論
🟢 LiteDocPipeline 骨架 + 三 key 註冊（litedoc/news/web + unknown fallback）、四 Phase strict stub、分派測試 9 passed、全套件 670 基線、SOP 合規。U1 策略分派達標。下一步 C3 P1 MinerU 攝入。
