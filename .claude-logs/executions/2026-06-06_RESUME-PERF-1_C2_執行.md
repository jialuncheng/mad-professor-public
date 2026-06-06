# RESUME-PERF-1 C2 — ThreadPool 並行翻譯（序列→受限並行）執行報告

---

**任務代號**：RESUME-PERF-1 C2
**執行日期**：2026-06-07
**依據規劃**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（v2、§7 OQ Q1-Q7 核准）
**依據 tasks**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_..._tasks.md`（§8 C2）
**Git commit hash**：（C2 留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 既有測試全綠＝行為等價；暫存 baton，待 baron commit）

---

## §0 改版規則
- 改版觸發：§1–§8 任一執行條款變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 基準與完成狀態
- **基準**：RESUME-PERF-1 C1（`b110742`）head。
- **完成狀態**：`pipelines/resume_pipeline.py` 把 `_restore_sections_markdown` 的「逐 slot 序列翻譯」換成 `ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)` 受限並行、**slot index 保序回填**、**單 unit 失敗退原文 + warning**；組裝/退化/zh* 不動。`# === [RESUME-PERF-1 C2 START/END] ===` 包裹；改前 `.bak`。**未 commit**（待 baron）。

---

## §2 Commit 表格（本次）
| Commit | 內容 | Hash |
|---|---|---|
| C2 | `resume_pipeline.py` 翻譯段序列→ThreadPool 並行（受既有 semaphore 限流）+ 單 unit 異常隔離 | （留空，待 baron 回填）|

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 檔頭 import `ThreadPoolExecutor` + `LLM_MAX_CONCURRENT`；`_restore_sections_markdown` 翻譯段並行化 + 異常隔離 | `archive/2026-06-06_RESUME-PERF-1_C2_resume_pipeline.py.bak` |

`git diff --stat`：
```
 pipelines/resume_pipeline.py | 42 +++++++++++++++++++++++++++++++++++++-----
 1 file changed, 37 insertions(+), 5 deletions(-)
```

---

## §4 真因與修法

### §4.1 目的
plan §1/§4.2：把 C1 解耦後的「逐 slot 序列翻譯」段換成受限並行，整份履歷 ~40 個翻譯單元由串行改並行（理論 ~5x）；不動組裝/順序（slot index 為唯一順序源）。

### §4.2 修法（`pipelines/resume_pipeline.py` 唯一改檔）
1. **檔頭 import**（`# === [RESUME-PERF-1 C2 START/END] ===`、L76-77）：`from concurrent.futures import ThreadPoolExecutor` + `from settings import LLM_MAX_CONCURRENT`（模組級名、便於 C3 測試 patch）。
2. **`_restore_sections_markdown` 翻譯段並行化**：
   ```python
   todo = [(i, slot, "title"/"content") for i,slot in enumerate(slots) if slot["kind"] in ("title","content")]
   with ThreadPoolExecutor(max_workers=max(1, LLM_MAX_CONCURRENT)) as ex:
       fut_to_idx = {ex.submit(self._t, slot["text"], inj, tr, ttype): i for i,slot,ttype in todo}
       for fut, i in fut_to_idx.items():
           try: zh_by_index[i] = fut.result()
           except Exception as exc:   # 單 unit 隔離
               zh_by_index[i] = slots[i]["text"]
               logger.warning("[RESUME-PERF-1] 單元翻譯失敗、退回原文",
                              extra={'extra_fields':{'event':'resume_translate_unit_fallback','reason':str(exc)[:200]}})
   ```
3. **組裝段不動**：仍按 `enumerate(slots)` 原序——`title`→`f"{'#'*level} {zh}"`、`content`→`_normalize_paragraph_breaks(zh)`、`raw`→原文；`zh = zh_by_index.get(i, slot["text"])`。
4. **限流**：實際 API 併發受**既有** `LLMClient._api_semaphore`（6）限（C2 不新增鎖）；`max_workers` 與其對齊。
5. **不並行**：`translate=False`（zh* 原文）與退化 `_translate_whole` 路徑不進並行段、不動。

### §4.3 行為等價性
- 結果以 **slot index** 保序回填、組裝按 `enumerate(slots)` 原序 → 與序列版**輸出順序完全一致**；翻譯/後處理邏輯不變。
- 並行只改 `_t` 的**執行先後**、不改各 slot 的輸入/輸出 → **既有 29 resume 測試全綠為等價鐵證**（mock 譯文確定、並行與序列輸出相同）。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（tasks §6.2）
```
$ grep -nc 'RESUME-PERF-1 C2' pipelines/resume_pipeline.py
4     ✅ START/END 包裹（import 區 + 翻譯段）
$ grep -n 'ThreadPoolExecutor\|LLM_MAX_CONCURRENT' pipelines/resume_pipeline.py
L76 import ThreadPoolExecutor / L77 import LLM_MAX_CONCURRENT / L580 max_workers=max(1, LLM_MAX_CONCURRENT)     ✅
$ grep -n "resume_translate_unit_fallback" pipelines/resume_pipeline.py
L593     ✅ 異常隔離 event 埋點（logger.warning、非 error）
```

### §5.2 SOP 一致性核查（BE-Refactor 強制）
```
logging：grep logger.error|exception|traceback → 無命中（合規；異常隔離用 logger.warning）
database：grep .commit() → 無裸 commit（合規）
```

### §5.3 pytest（行為等價鐵證）
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
29 passed in 0.60s     ✅ 既有 resume 測試全綠 = 並行後輸出與序列版等價

$ venv/bin/python -m pytest tests/ -q
1 failed, 504 passed, 3 skipped in 28.24s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- 語法 `ast.parse` → OK。

> **C3 銜接**：本次未動測試。**並行專屬覆蓋**（多 section byte 等拍保序 / 併發峰值 ≤ LLM_MAX_CONCURRENT / 單 unit 異常隔離 / 退化單呼叫不並行）於 C3 補齊；C1/C2 的等價基本盤由既有 29 測試守。

---

## §6 不可動清單遵守狀態（tasks §7）
| 不可動項 | 判定 |
|---|---|
| `Translator.translate` / `LLMClient.chat` / `_api_semaphore` 限流機制 | [x] ✅ 未動（沿用 semaphore 限流）|
| HEADING-HOTFIX 層級 / PARA-HOTFIX 正規化 / META-HOTFIX header | [x] ✅ 未動（組裝段不變）|
| `run_phase3` 主流程 / `BilingualMarkdownSpec` 合約 / 輸出順序 | [x] ✅ 等價不變（slot index 保序）|
| `_translate_whole` 退化 / zh* 路徑 | [x] ✅ 不並行、未動 |
| A軌 / 其餘四路 / 母提示詞 / DB Schema / 凍結合約 | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `pipelines/resume_pipeline.py`。

---

## §7 銜接與下一步
- **C3（下一 commit）**：`tests/test_resume_pipeline.py` 追加並行專屬測試（保序 byte 等拍 / 併發峰值 ≤ `LLM_MAX_CONCURRENT`〔patch `resume_pipeline.LLM_MAX_CONCURRENT` 小值〕/ 單 unit 異常隔離退原文 / 退化單呼叫不並行）。
- **效能驗證**：wall-clock 下降屬 baron E2E（影子上傳履歷觀察 run_phase3 翻譯時間 ~300s → ~60-90s）。
- **baton 暫存**：C2 報告留 baton、**不 git add**，待 C4 Checkout 一次性歸檔。

---

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-PERF-1_C2_resume_pipeline.py.bak

# 2. git add 清單（嚴禁 git add baton/ 下本執行報告）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-PERF-1_C2_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-PERF-1_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-PERF-1_C2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-PERF-1_C2_msg.txt
```

### §8.2 commit message 草稿
```
feat(resume): RESUME-PERF-1 C2 — ThreadPool 並行翻譯與異常隔離

修改 pipelines/resume_pipeline.py：
1. 檔頭引入 concurrent.futures.ThreadPoolExecutor 與 settings.LLM_MAX_CONCURRENT。
2. 將 _restore_sections_markdown 中的「逐 slot 序列翻譯」更換為 ThreadPoolExecutor 並行翻譯，最大執行緒限制為 LLM_MAX_CONCURRENT，以 slot index 保序回填，實際 API 併發受既有 LLMClient._api_semaphore 的 6 併發限制。
3. 實作單一單元異常隔離：取結果時如拋出 Exception，該 slot 退回原文（slot["text"]），並發出 logger.warning 與 event: resume_translate_unit_fallback 埋點，保證其餘單元仍能翻譯並完整重組交付。
變更與新增區塊已使用 # === [RESUME-PERF-1 C2 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <C2-hash>          # 回 C1 序列版（行為等價、不影響輸出）
```

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 記錄 RESUME-PERF-1 C2 翻譯並行化的落地與行為等價驗證 |
| 用途 | 收官時 mv 歸檔 executions/ |
| 權威源 | 本檔 §4 修法 + §5 驗收 |
| 約束事項 | C2 限改 resume_pipeline.py 翻譯段；嚴禁動 Translator/LLMClient/合約/組裝邏輯/自發 commit |
| 改版規則 | 直接改章節 + §99.2 加 Revision |
| 刪除條件 | 永久保留歸檔 executions/ |

### §99.2 Revision 歷程
- v1 (2026-06-07)：C2 落地——`resume_pipeline.py` import `ThreadPoolExecutor`+`LLM_MAX_CONCURRENT`；`_restore_sections_markdown` 翻譯段序列→`ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)` 並行、`{future:index}` 保序回填〔實際 API 併發受既有 `_api_semaphore` 限〕、單 unit 拋例外退原文+`logger.warning(event=resume_translate_unit_fallback)`；組裝/退化/zh* 不動；RESUME-PERF-1 C2 包裹 + .bak；grep（包裹 4 / ThreadPool+LLM_MAX_CONCURRENT / 異常隔離 event）、SOP logging+database 合規、resume 29 passed（行為等價鐵證）、全套件 504 passed（唯一 failed 既知 LOG_FORMAT env flake）；並行專屬測試歸 C3。
