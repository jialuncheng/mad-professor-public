# PIPE-LITEDOC C7 執行報告 — 單元與接縫整合測試（雙鎖）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C7 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C7` |
| 次級參考 | plan v3 §2 U8 / §9 Q6;WORKFLOW_SOP §7.2;RAG-ASYNC-HOTFIX-1 接縫不變式 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C7)、pytest 全綠驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C6（P4）已 ship、litedoc 四 Phase 全實作;分派 + P1-P4 契約測試已隨 C2-C6 加（24 測試），缺 §7.2 接縫整合。
- **完成狀態**：補 `tests/test_litedoc_pipeline.py` **§7.2 P2→P3→P4 key-changing 整合測試**;**零業務代碼改動**（純測試）。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U8 + §9 Q6`（§7.2 不豁免、寫 key-changing transform 整合測試、鎖接縫不變式）;無偏離。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C7 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C7 — 單元與接縫整合測試（雙鎖）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `tests/test_litedoc_pipeline.py` | 修改（追加 §7.2 整合測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C7_test_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C7_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C7 ✅ / C8 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C7_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C7 ...] ===` 包裹）
- **`test_seam_p2_p3_p4_key_changing_integration`**：真實 LiteDocPipeline 串接 P2→P3→P4（section_engine 真實、LLM/Translator mock）——
  - **P2**：`run_phase2` 真實 `section_engine.build_section_summaries`（tiles 標題 Intro/Body）→ section_summaries key＝原文標題 path `{Intro, Body}`。
  - **P3**：`_KeyChangeTr` **真把 `Intro`→`ZH::Intro`**（key-changing transform）;`_read_source_text` 回 16k 文字強制 section mode;`run_phase3` → `ctx.rag_sections` 之 `summary_key` 仍＝原文 `{Intro, Body}`、`title`＝譯後 `{ZH::Intro, ZH::Body}`。
  - **接縫不變式斷言**：`p2_keys == p3_summary_keys == {Intro, Body}`（跨譯零位移）+ `p3_titles == {ZH::Intro, ZH::Body}`（key-changing 真實發生、非自洽同 key 假象）。
  - **P4**：mock rag_indexer，斷言 `cap["section_summaries"] == gspec.section_summaries`（同一份、key 對齊）+ `doc_type=='litedoc'` + 每個 rag summary_key ∈ section_summaries（下游 match 成功）→ 堵 RAG-ASYNC-HOTFIX-1 靜默退化。

關鍵片段：
```python
class _KeyChangeTr:
    def translate(self, text, ctx, mode, text_type="content"):
        return f"ZH::{text}"          # 真改 key
...
assert p2_keys == p3_summary_keys == {"Intro", "Body"}     # 跨譯零位移
assert p3_titles == {"ZH::Intro", "ZH::Body"}               # key-changing 真實發生
for s in ctx.rag_sections:
    assert s["summary_key"] in cap["section_summaries"]      # P4 下游 match
```

## §5 測試結果
### §5.1 litedoc 全測試（含 §7.2 整合）
```
pytest tests/test_litedoc_pipeline.py -q → 25 passed
  〔C2 分派 4 / C3 P1 7 / C4 P2 2 / C5 P3 6 / C6 P4 3 + 本 C7 §7.2 整合 1〕
```
### §5.2 全套件 pytest
```
pytest tests/ -q → 1 failed, 686 passed, 3 skipped（686＝685 基線 + 1;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP / 零業務改動
```
業務 .py 變動：0（C7 純測試、git status 僅 tests/test_litedoc_pipeline.py）
C7 包裹 START/END：2（測試檔內）
```
### §5.4 變動範圍（git）
```
git status -s .py：僅 tests/test_litedoc_pipeline.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| 業務代碼（litedoc_pipeline.py / section_engine / rag_indexer / contracts / 其他策略 / A 軌）| [x] ✅ 全未動（C7 純測試）|
| 既有測試函式 | [x] ✅ 未動（僅追加 §7.2 整合測試）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅追加 `tests/test_litedoc_pipeline.py` 一個整合測試、零業務代碼/零既有測試改動（git status 證）。
- **(b) 無關 / 違規?**：否。§7.2 整合測試對應 U8/Q6;`_KeyChangeTr` 真改 key（非純 mock 同 key、符 WORKFLOW_SOP §7.2「含 key-changing transform、純 mock 不予承認」）。msg 簽名校正 Opus 4.8。
- **(c) 推進哪個 U-N?**：U8（§7.2 key-changing 整合·雙鎖之一）;無做白工——鎖死接縫不變式、為 litedoc 全鏈鋪保護網。

## §7 銜接
- baton 狀態：C1-C7 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C8 — Checkout 收官**：Conformance 五維度（目標規格 U1-U9+U2.1/U5b/U5c / tasks §6 grep+pytest / 不可動 / 提示詞稽核 / msg §8）+ §7.2 整合存在且通過（本 C7、**免豁免**）+ baton 一次性歸檔 + TODO 結案 + hash 自癒。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C7_test_litedoc_pipeline.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C7_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C7_msg.txt）
cat > /tmp/PIPE-LITEDOC_C7_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C7 — 單元與接縫整合測試（雙鎖）

- tests/test_litedoc_pipeline.py 補 §7.2 P2→P3→P4 key-changing 整合測試：_KeyChangeTr 真把
  「Intro」→「ZH::Intro」，斷言 P2 section_summaries key 與 P3 rag_sections summary_key 譯後仍
  同基準＝原文標題 path（跨譯零位移）、譯後 title 確實改變（key-changing 真實發生）、P4 消費同一份
  section_summaries 且下游可 match，堵 RAG-ASYNC-HOTFIX-1 靜默退化。
- 純 mock 同 key 兩端不予承認（WORKFLOW_SOP §7.2），故用真改 key 之 transform。

驗證：litedoc 25 passed（分派 4 / P1 7 / P2 2 / P3 6 / P4 3 + §7.2 整合 1）；全套件 686 passed
（唯一 fail＝既有 .env LOG_FORMAT flake）；零業務代碼/零既有測試改動。baton 未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C7_msg.txt
```

## §9 回退方式
`git revert <C7 hash>`（純測試、無業務影響）。

---
### 結論
🟢 §7.2 P2→P3→P4 key-changing 接縫整合測試落地（_KeyChangeTr 真改 title、接縫不變式鎖死、P4 下游 match、堵 RAG-ASYNC-HOTFIX-1）、零業務改動、litedoc 25 passed、全套件 686 基線。下一步 C8 Checkout 收官。
