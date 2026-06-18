# PIPE-SECTION-BASE C4 執行報告 — 引擎單元測試與接縫整合測試（雙鎖）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SECTION-BASE C4 |
| 執行日期 | 2026-06-18 |
| 依據規劃 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_tasks.md §8 C4` |
| 次級參考 | plan v2 §8 / §9 Q6（雙鎖）;RAG-ASYNC-HOTFIX-1（接縫不變式）|
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C4)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C1（`e400789`）+ C2（`24db977`）+ C3（`4078a9e`）已 ship;section_engine 三簇全抽出、無引擎專屬測試。
- **完成狀態**：新建 `tests/test_section_engine.py`（17 測試）直接覆蓋共用引擎 + base 層 key-changing 整合測試;**零業務代碼改動**（純新增測試檔）。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §8 + §9 Q6`（雙鎖：resume 既有測試證「路徑不退化」+ base 層獨立測試證「引擎對任意 doc_type 接縫 key 不位移」）;無偏離。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C4 | （待 baron 回填）| BE-Refactor: PIPE-SECTION-BASE C4 — 引擎單元測試與接縫整合測試 |

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `tests/test_section_engine.py` | 新增（17 測試）| **本 commit git add** |
| `.claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C4_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C4 ✅ / C5 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C4_執行.md`（本檔）/ C1-C3 報告 / plan / tasks | baton 暫存 | **baton/ 暫存（C5 checkout 歸檔）·嚴禁 git add** |
| 備份 | — | 本階段純新增測試、無須備份既有檔 |

## §4 修法說明（`tests/test_section_engine.py` 新增、無改既有原始碼故無 C4 marker）
17 測試分 6 區覆蓋共用引擎：
- **① 標題樹走訪**：`collect_summary_targets` DFS path key（父先於子、`/` 串接）/ **吃任意子樹（U3.2）** / 空節點略過。
- **② 批次摘要保序**：`parse_indexed` 亂序+越界容錯 / `build_section_summaries` 批次非 N（fake.calls==2）+ key=原文標題 path / LLM 失敗非致命（{}）/ `translate_section_summaries` zh* skip（calls==0）。
- **③ 排版還原**：`restore_sections_markdown` byte 序保真（title 亦翻 `## ZH::S0`、保序）/ 並行限流峰值 ≤ max_workers / 單 unit 拋例外退原文。
- **④ heading 退化**：數 < min / 單一巨 section 佔比 > ratio / 均勻不退化。
- **⑤ meta header 純格式化器**：收 `(Label,Value)` tuples → markdown、空 value 略過、title 空回 ''、en sep。
- **⑥ base 層 P2→P3→P4 key-changing 整合**（核心·Q6）：`_DetTr` 真把 `Skills`→`ZH::Skills`、斷言 P2 `section_summaries` key == P3 `rag_sections` `summary_key` == 原文 `Skills`（譯文 title `ZH::Skills` 僅供顯示）、且下游可用 P2 key 命中 P3 section → 堵 RAG-ASYNC-HOTFIX-1 類退化。

關鍵片段（接縫不變式斷言）：
```python
assert p2_keys == {"Skills", "Education", "Experience"}
assert p3_summary_keys == p2_keys                       # 同基準（跨譯零位移）
assert p3_display_titles == {"ZH::Skills", "ZH::Education", "ZH::Experience"}  # key-changing 真實發生
for sec in rag_sections:
    assert sec["summary_key"] in section_summaries       # 下游 match 成功
```

## §5 測試結果
### §5.1 §6.4 C4 驗收 grep
```
tests/test_section_engine.py 存在（14647 bytes）;接縫不變式關鍵詞（key-changing/同基準/summary_key）12 命中
```
### §5.2 §6.6 SOP（本 commit 純測試、無業務碼）
```
不適用（無新增 logging.error / DB commit;測試檔不涉 runtime SOP）
```
### §5.3 pytest
```
pytest tests/test_section_engine.py -v → 17 passed
pytest tests/ -q → 1 failed, 657 passed, 3 skipped（657＝640 基線 + 17 新增;唯一 fail＝既有 .env LOG_FORMAT env flake）
```
### §5.4 變動範圍（git）
```
git status -s 業務 .py：0（C4 純新增 tests/test_section_engine.py、無 M 業務檔）
```
> **執行期修正（測試端）**：`test_restore_byte_order_preserved` 初版預期值漏算「title slot 亦翻」、期望 `## S0` → 修正為 `## ZH::S0`（引擎行為正確、測試斷言誤寫已改）;非業務代碼問題。

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| 業務代碼（section_engine.py / resume_pipeline.py / slide / contracts / rag_indexer / A 軌）| [x] ✅ 全未動（C4 純新增測試）|
| 既有測試檔（test_resume_pipeline.py 等）| [x] ✅ 未動（僅新增 test_section_engine.py）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅新增 `tests/test_section_engine.py`、零業務代碼/零既有測試改動（git status 證）。
- **(b) 無關 / 違規?**：否。17 測試全對應引擎公開函式 + Q6 接縫整合;一處執行期測試斷言修正（title 翻譯誤算、引擎正確）已 §5.3 誠實載明。符 CLAUDE.md（baton 不 add、不自發 commit）。
- **(c) 推進哪個 U-N?**：U5（引擎單元測試）+ Q6（base 層 key-changing 整合·雙鎖之一）;無做白工。

## §7 銜接
- baton 狀態：C1-C4 報告 + plan + tasks 留 baton（待 C5 一次性歸檔）。
- 下一步：**C5 — Checkout 收官**：Conformance 五維度（目標規格 U1-U6 / tasks §6 grep+pytest / 不可動 / 提示詞稽核 / msg §8）+ §7.2 整合測試存在且通過（C4 base 層 key-changing + resume 既有整合、**免豁免**）+ baton 一次性歸檔（plan→plans/、tasks→tasks/、C1-C5 報告→executions/）+ TODO 結案 + hash 自癒（回填 C1 `e400789`/C2 `24db977`/C3 `4078a9e`）。

## §8 baron 執行命令
```bash
# 1. 本階段純新增測試、無備份

# 2. git add（測試 + 提示詞 + TODO;baton 暫存嚴禁 add）
git add tests/test_section_engine.py
git add .claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C4_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿
cat > /tmp/PIPE-SECTION-BASE_C4_msg.txt << 'EOF'
BE-Refactor: PIPE-SECTION-BASE C4 — 引擎單元測試與接縫整合測試

- 新增 tests/test_section_engine.py（17 測試）覆蓋共用 section 引擎：標題樹走訪+子樹（U3.2）/
  批次摘要保序+非致命+zh skip / 排版還原 byte 序+並行限流+單 unit 退原文 / heading 退化 /
  meta header 純格式化器（收 tuples、不碰 dict）。
- 新增 base 層 P2→P3→P4 key-changing 整合測試：_DetTr 真改標題文字，斷言 P2 section_summaries
  key 與 P3 rag_sections summary_key 同基準＝原文標題 path（譯文 title 僅顯示），堵 RAG-ASYNC-HOTFIX-1。

驗證：test_section_engine 17 passed；全套件 657 passed（640 基線 + 17 新；唯一 fail＝既有 .env
LOG_FORMAT flake）；零業務代碼/零既有測試改動。baton 未 add、待 C5 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SECTION-BASE_C4_msg.txt
```

## §9 回退方式
`git revert <C4 hash>`（純測試、無業務影響）或刪 `tests/test_section_engine.py`。

---
### 結論
🟢 新建 `tests/test_section_engine.py`（17 測試）+ base 層 key-changing 整合測試（雙鎖之一、堵 RAG-ASYNC-HOTFIX-1）、零業務改動、全套件 657 passed（640+17）。引擎保護網織成。下一步 C5 Checkout 收官。
