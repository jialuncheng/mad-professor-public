# RESUME-PERF-1 C3 — Unit Tests（並行專屬測試）執行報告

---

**任務代號**：RESUME-PERF-1 C3
**執行日期**：2026-06-07
**依據規劃**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（v2、§7 OQ Q1-Q7 核准）
**依據 tasks**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_..._tasks.md`（§8 C3）
**Git commit hash**：（C3 留空，由 baron 回填）
**狀態**：Completed（測試落地 + 全綠；暫存 baton，待 baron commit）

---

## §0 改版規則
- 改版觸發：§1–§8 任一執行條款變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 基準與完成狀態
- **基準**：RESUME-PERF-1 C2（`d5abdf0`）head。
- **完成狀態**：`tests/test_resume_pipeline.py` 追加 4 並行專屬測試（保序 byte 等拍 / 併發峰值 ≤ `LLM_MAX_CONCURRENT` / 單 unit 異常隔離 / 退化單呼叫不並行）；`# === [RESUME-PERF-1 C3 START/END] ===` 包裹；改前 `.bak`。**純測試、不動業務碼**。**未 commit**（待 baron）。

---

## §2 Commit 表格（本次）
| Commit | 內容 | Hash |
|---|---|---|
| C3 | `tests/test_resume_pipeline.py` 追加 4 並行專屬測試 | （留空，待 baron 回填）|

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `tests/test_resume_pipeline.py` | 追加 `_DetTr` helper + 4 測試 | `archive/2026-06-06_RESUME-PERF-1_C3_test_resume_pipeline.py.bak` |

`git diff --stat`：
```
 tests/test_resume_pipeline.py | 126 ++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 126 insertions(+)
```

---

## §4 真因與修法

### §4.1 目的
C1/C2 的「等價基本盤」由既有 29 resume 測試守；C3 補**並行專屬覆蓋**——強驗「並行不亂序、受限流、異常隔離、退化不並行」四個 C2 引入的新行為。

### §4.2 修法（`tests/test_resume_pipeline.py` 唯一改檔、純測試）
新增 `_DetTr`（確定化 Translator：`translate(text)→f"ZH::{text}"`）+ 4 測試（`# === [RESUME-PERF-1 C3 START/END] ===` 包裹）：
1. **`test_p3_parallel_order_byte_equal`**：多層 section〔Top→text+figure→Child(text)〕直呼 `_restore_sections_markdown`〔inj=None、`_DetTr` 忽略〕→ 輸出 **byte 等於**手算序列預期 `"## ZH::Top\n\nZH::alpha\n\n![](x.png)\n\n### ZH::Child\n\nZH::beta\n"`（保序 + 層級 ##/### + raw passthrough）。
2. **`test_p3_parallel_concurrency_capped`**：`monkeypatch.setattr(rp, "LLM_MAX_CONCURRENT", 2)` + lock 計數 + `time.sleep(0.02)` 製造重疊；6 section → 斷言併發峰值 `>=1` 且 `<=2`。
3. **`test_p3_parallel_unit_error_isolated`**：某 text 含 "BOOM" → `_ErrTr` 拋例外 → `run_phase3` → 斷言 `BilingualMarkdownSpec` 仍交付、`ZH::alpha` 在（正常）、`BOOM-text` 在（退原文）、`ZH::BOOM-text` 不在（未翻）。
4. **`test_p3_parallel_degraded_single_call`**：單一巨 section（heading < 2）→ 退化 → `_translate_whole` → 斷言 translate `calls==1`（未並行逐 unit）、spec 交付。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（tasks §6.3）
```
$ grep -nc 'def test_p3_parallel_order_byte_equal\|def test_p3_parallel_concurrency_capped\|def test_p3_parallel_unit_error_isolated\|def test_p3_parallel_degraded_single_call' tests/test_resume_pipeline.py
4     ✅ 4 新測試命中
$ grep -nc 'RESUME-PERF-1 C3' tests/test_resume_pipeline.py
2     ✅ START/END 包裹
```

### §5.2 SOP 一致性核查（純測試檔）
```
logging：grep logger.error|traceback → 無命中（合規）
database：grep .commit() → 無命中（合規）
```

### §5.3 pytest
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
33 passed in 0.80s     ✅（29 既有 + 4 新）

$ venv/bin/python -m pytest tests/ -q
1 failed, 508 passed, 3 skipped in 33.70s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- **508 passed**（C2 後 504 + 本次 4 新）；唯一 failed 為既知環境 flake。✅ 不退化。

---

## §6 不可動清單遵守狀態（tasks §7）
| 不可動項 | 判定 |
|---|---|
| `resume_pipeline.py` 業務碼（C1/C2 實作）| [x] ✅ 未動（C3 純測試）|
| `Translator` / `LLMClient` / `_api_semaphore` | [x] ✅ 未動 |
| A軌 / 其餘四路 / 母提示詞 / DB Schema / 合約 | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `tests/test_resume_pipeline.py`。

---

## §7 銜接與下一步
- **C4（下一 commit、Checkout）**：Conformance 三維度驗收（plan §2 U1-U7 / tasks §6 / 不可動清單）+ SOP 核查 + 提示詞稽核 + baton 一次性歸檔（plan_v1/tasks/C1-C4 報告 → plans//tasks//executions/）。
- **效能 E2E（baron）**：影子上傳履歷觀察 run_phase3 翻譯 wall-clock 下降（~300s → ~60-90s）。
- **baton 暫存**：C3 報告留 baton、**不 git add**，待 C4 一次性歸檔。

---

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-PERF-1_C3_test_resume_pipeline.py.bak

# 2. git add 清單（嚴禁 git add baton/ 下本執行報告）
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-PERF-1_C3_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-PERF-1_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-PERF-1_C3_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-PERF-1_C3_msg.txt
```

### §8.2 commit message 草稿
```
test(resume): RESUME-PERF-1 C3 — 追加並行翻譯與異常隔離測試

修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_parallel_order_byte_equal，Mock 譯文為確定化字串，驗證多層 section 巢狀結構下，並行版之還原結果與序列預期逐字元完全相同（保序與結構等價）。
2. 追加 test_p3_parallel_concurrency_capped，藉由 patch 限制 LLM_MAX_CONCURRENT=2，以計數器與 lock 模擬併發重疊，驗證同時呼叫的並行執行緒峰值不超過設定值。
3. 追加 test_p3_parallel_unit_error_isolated，模擬某一單元翻譯拋出例外時，該區塊能安全退回原文，其餘單元翻譯正常，且最終 BilingualMarkdownSpec 能順利完成交付。
4. 追加 test_p3_parallel_degraded_single_call，模擬 heading 退化時 run_phase3 降級為整檔翻譯單次呼叫，不啟動並行翻譯執行緒。
變更與新增區塊已使用 # === [RESUME-PERF-1 C3 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <C3-hash>          # 回滾測試追加（純測試、不影響 runtime）
```

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 記錄 RESUME-PERF-1 C3 並行專屬測試的落地與驗收 |
| 用途 | 收官時 mv 歸檔 executions/ |
| 權威源 | 本檔 §4 修法 + §5 驗收 |
| 約束事項 | C3 限改 tests/test_resume_pipeline.py；嚴禁動業務代碼/自發 commit |
| 改版規則 | 直接改章節 + §99.2 加 Revision |
| 刪除條件 | 永久保留歸檔 executions/ |

### §99.2 Revision 歷程
- v1 (2026-06-07)：C3 落地——`tests/test_resume_pipeline.py` 新增 `_DetTr` + 4 並行專屬測試（order_byte_equal 多層 byte 等拍保序 / concurrency_capped patch LLM_MAX_CONCURRENT=2 lock 計數驗峰值 ≤ 2 / unit_error_isolated 單 unit 拋例外退原文 spec 仍交付 / degraded_single_call 退化 _translate_whole calls==1 不並行）；RESUME-PERF-1 C3 包裹 + .bak；grep 4 新測試命中、SOP 合規、resume 33 passed、全套件 508 passed（唯一 failed 既知 LOG_FORMAT env flake）。
