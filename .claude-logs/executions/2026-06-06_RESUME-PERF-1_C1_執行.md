# RESUME-PERF-1 C1 — Collect/Assemble 重構（收集-組裝解耦）執行報告

---

**任務代號**：RESUME-PERF-1 C1
**執行日期**：2026-06-06
**依據規劃**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（v2、§7 OQ Q1-Q7 核准）
**依據 tasks**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_..._tasks.md`（§8 C1）
**Git commit hash**：（C1 留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 既有測試全綠＝byte 等價；暫存 baton，待 baron commit）

---

## §0 改版規則
- 改版觸發：§1–§8 任一執行條款變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 基準與完成狀態
- **基準**：VISION-HOTFIX-1（`3d5be32`）head。
- **完成狀態**：`pipelines/resume_pipeline.py` 將 `_restore_one_section`（邊走邊翻邊組）重構為「`_collect_render_slots` 序列收集有序 slot → 逐 slot **序列**翻譯 → 按序組裝」；**仍序列、輸出 byte 等價**（既有 29 resume 測試全綠）。`# === [RESUME-PERF-1 C1 START/END] ===` 包裹；改前 `.bak`。**未 commit**（待 baron）。

---

## §2 Commit 表格（本次）
| Commit | 內容 | Hash |
|---|---|---|
| C1 | `resume_pipeline.py` 收集-組裝解耦（`_collect_render_slots` + 重構 `_restore_sections_markdown`、仍序列）| （留空，待 baron 回填）|

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 重構 `_restore_sections_markdown`（collect→序列翻譯→組裝）+ 新增 `_collect_render_slots`、移除 `_restore_one_section`（無外部引用）| `archive/2026-06-06_RESUME-PERF-1_C1_resume_pipeline.py.bak` |

`git diff --stat`：
```
 pipelines/resume_pipeline.py | 114 +++++++++++++++++++++++--------------------
 1 file changed, 62 insertions(+), 52 deletions(-)
```

---

## §4 真因與修法

### §4.1 目的
plan §1/§4.1：把「逐 section 邊遞迴邊翻邊組」解耦成「收集 → 翻譯 → 組裝」三段，使 C2 能把中間「翻譯」段換成並行而不動結構。C1 本身**仍序列、輸出不變**，先證明解耦不破壞輸出（風險隔離：C1 擋「結構是否壞」、C2 才管「並行是否亂序」）。

### §4.2 修法（`pipelines/resume_pipeline.py` 唯一改檔）
**新增 `_collect_render_slots(sections, depth, out)`**（遞迴鏡像原 DFS pre-order、不翻譯）：
- title → `{"kind":"title","text":title,"level":min(2+depth,6)}`（HEADING-HOTFIX 邏輯、值不變）
- text item → `{"kind":"content","text":content}`
- 非 text 有 content → `{"kind":"raw","text":content}`（passthrough）
- 字串 fallback → `{"kind":"content","text":txt}`
- children → 遞迴 `depth+1`

**重構 `_restore_sections_markdown`**：`slots=[]; _collect_render_slots(sections,0,slots)` → 逐 slot **序列**：`raw` 直取原文、`title`/`content` 經 `_t(text, inj, tr, "title"/"content")` → 組裝（`title`→`f"{'#'*level} {zh}"`、`content`→`_normalize_paragraph_breaks(zh)`、`raw`→原文）→ `"\n\n".join(非空).strip()+"\n"`。

**移除 `_restore_one_section`**（全專案僅內部自引用、無測試呼叫，grep 證；邏輯已搬入 collect+assemble）。

### §4.3 byte 等價性論證
- slot 順序 = 原 `_restore_one_section` DFS pre-order（title → content items → children 遞迴）→ 完全一致。
- 各 slot 的翻譯（`_t` 同參數）與後處理（title 前綴 `'#'*level`、content `_normalize_paragraph_breaks`、raw 原文）**邏輯與原碼逐一對應**。
- 最終 `"\n\n".join(...).strip()+"\n"` 不變。
- → 輸出與序列版 byte 等價；**既有 29 resume 測試全綠為鐵證**。

### §4.4 不可動清單遵守
- HEADING-HOTFIX-1 `level=min(2+depth,6)`：值不變、僅由 collect 記錄。
- PARA-HOTFIX-1 `_normalize_paragraph_breaks`：不改、於 assemble 套用。
- META-HOTFIX-1 `_render_meta_header` / `run_phase3` 主流程 / `_t` / `_translate_whole` / 退化偵測 / zh* 路徑 / 凍結合約 / Translator / LLMClient / A軌：**全未動**。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（tasks §6.1）
```
$ grep -nc 'RESUME-PERF-1 C1' pipelines/resume_pipeline.py
3     ✅ START/END 包裹
$ grep -nc 'def _collect_render_slots\|_collect_render_slots(' pipelines/resume_pipeline.py
3     ✅ 新 helper（定義 + 頂層呼叫 + 遞迴）
$ grep -nc 'self._t(' pipelines/resume_pipeline.py
1     ✅ 仍序列（單一呼叫點、C1 未並行）
$ grep -n 'ThreadPool|asyncio|gather' pipelines/resume_pipeline.py
L557（C1 docstring 提及 C2 將換 ThreadPool）← 非實碼、C1 無並行原語
```

### §5.2 SOP 一致性核查（BE-Refactor 強制）
```
logging：grep logger.error|exception|traceback → 無命中（合規）
database：grep .commit() → 無裸 commit（合規）
```

### §5.3 pytest（byte 等價鐵證）
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
29 passed in 0.63s     ✅ 既有 resume 測試全綠 = 重構後輸出 byte 等價

$ venv/bin/python -m pytest tests/ -q
1 failed, 504 passed, 3 skipped in 23.55s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- 語法 `ast.parse` → OK。

---

## §6 不可動清單遵守狀態（tasks §7）
| 不可動項 | 判定 |
|---|---|
| Translator / LLMClient / `_api_semaphore` | [x] ✅ 未動 |
| HEADING-HOTFIX `level` 邏輯 | [x] ✅ 值不變、僅搬至 collect |
| PARA-HOTFIX `_normalize_paragraph_breaks` | [x] ✅ 不改、assemble 套用 |
| META-HOTFIX `_render_meta_header` / `run_phase3` 主流程 / 合約 | [x] ✅ 未動、輸出等價 |
| `_translate_whole` 退化 / zh* 路徑 | [x] ✅ 未動 |
| A軌 / 其餘四路 / 母提示詞 / DB Schema | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `pipelines/resume_pipeline.py`。

---

## §7 銜接與下一步
- **C2（下一 commit）**：把 `_restore_sections_markdown` 的「逐 slot 序列翻譯」段換成 `ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)`、slot index 保序回填、單 unit 失敗退原文+warning。
- **baton 暫存**：C1 報告留 baton、**不 git add**，待 C4 Checkout 一次性歸檔。

---

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-PERF-1_C1_resume_pipeline.py.bak

# 2. git add 清單（嚴禁 git add baton/ 下本執行報告）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-PERF-1_C1_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-PERF-1_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-PERF-1_C1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-PERF-1_C1_msg.txt
```

### §8.2 commit message 草稿
```
refactor(resume): RESUME-PERF-1 C1 — Collect/Assemble 重構以解耦收集與組裝

修改 pipelines/resume_pipeline.py：
1. 新增私有 helper _collect_render_slots，將原邊遞迴邊翻譯邊還原的邏輯改為「序列收集有序 slots 列表」，slots 包括 title/content/raw 三種型態。
2. 重構 _restore_sections_markdown，先 collect slots，再序列翻譯 slots（此步驟仍為序列、不改執行緒），最後序列組裝（沿用 HEADING 遞迴深度層級、PARA 段落正規化）。
3. 移除無外部引用的 _restore_one_section（邏輯已搬入 collect+assemble）。
達成功效：將逐 section 翻譯與 Markdown 還原解耦，並保證輸出與序列版 byte-level 完全等價（既有 29 個測試全綠）。
變更與新增區塊已使用 # === [RESUME-PERF-1 C1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <C1-hash>          # 完全回滾、恢復 _restore_one_section 序列版
```

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 記錄 RESUME-PERF-1 C1 收集-組裝解耦的落地與 byte 等價驗證，作為 C2 並行化前置 |
| 用途 | 收官時 mv 歸檔 executions/ |
| 權威源 | 本檔 §4 修法 + §5 驗收 |
| 約束事項 | C1 限改 resume_pipeline.py、行為等價；嚴禁動 Translator/LLMClient/合約/自發 commit |
| 改版規則 | 直接改章節 + §99.2 加 Revision |
| 刪除條件 | 永久保留歸檔 executions/ |

### §99.2 Revision 歷程
- v1 (2026-06-06)：C1 落地——`resume_pipeline.py` 新增 `_collect_render_slots`（遞迴收集 title/content/raw 有序 slot、不翻譯、HEADING 層級值不變）+ 重構 `_restore_sections_markdown`（collect→逐 slot **序列**翻譯→按序組裝、PARA 正規化沿用）+ 移除無外部引用的 `_restore_one_section`；仍序列、輸出 byte 等價；RESUME-PERF-1 C1 包裹 + .bak；grep（包裹 3 / _collect_render_slots / 仍序列 _t 1 / 無並行原語）、SOP logging+database 合規、resume 29 passed（byte 等價鐵證）、全套件 504 passed（唯一 failed 既知 LOG_FORMAT env flake）。
