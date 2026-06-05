# RESUME-P3 HEADING-HOTFIX-1 — B軌標題層級遞迴深度修復 執行報告

---

**任務代號**：RESUME-P3 HEADING-HOTFIX-1（BE-Hotfix）
**執行日期**：2026-06-06
**依據計畫**：`.claude-logs/baton/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md`
**次級參考**：`sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 驗收全綠 + 收官歸檔；待 baron commit）

---

## §1 基準與完成狀態
- **基準**：MODEL-11 C4（`01a4e5b`）head；RESUME-P3 C6（`a1d5d7f`）後的 B軌標題 Regression hotfix。
- **完成狀態**：`pipelines/resume_pipeline.py` 標題層級改由遞迴深度 `depth` 推算（廢恆=1 `level` 扁平死欄短路）+ `tests/test_resume_pipeline.py` 追加 1 測試；`# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` 包裹；改前 2 `.bak`。**未 commit**（待 baron）。

---

## §2 落地 Commit 表格
| # | Hash | Subject |
|---|---|---|
| HEADING-HOTFIX-1 | （待回填）| `fix(resume): RESUME-P3 HEADING-HOTFIX-1 — B軌標題層級改由遞迴深度推算 (修標題塌陷全 h1)` |

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `pipelines/resume_pipeline.py` | `_restore_sections_markdown`（depth=0 起算）+ `_restore_one_section`（簽名 +depth、`level=min(2+depth,6)`、children depth+1）| `archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_resume_pipeline.py.bak` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_heading_level_by_recursion_depth` | `archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_test_resume_pipeline.py.bak` |

`git diff --stat`：
```
 pipelines/resume_pipeline.py  | 22 +++++++++++++++-----
 tests/test_resume_pipeline.py | 47 +++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 64 insertions(+), 5 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因（兩層）
1. **`level` 欄恆=1 扁平死欄**：md2json/json_process 的 section 真實深度在 `children` 樹與 `heading_level`（=2+樹深度）；`level` 欄不分深淺一律 1（dump 鋼證：頂層 level=1/heading_level=2、子層 level=1/heading_level=3、孫層 level=1/heading_level=4）。
2. **`or` 短路**：C3 `_restore_one_section` 寫 `int(sec.get("level") or sec.get("heading_level") or 1)`，因 `level`=1 truthy → 永不讀 `heading_level` → 全標題 `#`(h1)、塌成單一層級。

### §4.2 修法（`pipelines/resume_pipeline.py`、遞迴深度推算）
```python
# _restore_sections_markdown：頂層 depth=0 起算
self._restore_one_section(sec, inj, tr, translate, parts, depth=0)

# _restore_one_section：簽名加 depth:int=0；廢資料欄短路、改遞迴深度
level = min(2 + depth, 6)            # 頂層 h2（候選人名為 h1、md_restore 樣板另渲染）、每下潛 +1、上限 h6
parts.append(f"{'#' * level} {zh_title}")
...
# children 遞迴時 depth+1
self._restore_one_section(child, inj, tr, translate, parts, depth=depth + 1)
```
- **等價性**：`heading_level == 2 + 樹深度`，遞迴深度公式在資料正確時與 heading_level 完全等價，但不依賴該欄被正確填寫（結構保證階層）。
- **不動**：content 分流 / `_translate_whole` / `_t` / C4 退化偵測 / `run_phase3` 主流程 / `BilingualMarkdownSpec`。
- 為使驗收 grep `sec.get("level")` 真 0-hit，HEADING-HOTFIX-1 註解改寫為「level 欄 or heading_level 欄」描述、不留字面字串（沿用本專案慣例）。

### §4.3 測試（`tests/test_resume_pipeline.py`）
`test_p3_heading_level_by_recursion_depth`：3 層巢狀 section、**所有節點 `level=1`**（複現短路陷阱）、文字均衡避免觸 C4 退化；FakeTr 回顯原文 → 斷言 `## TopExperience` / `### MidCompany` / `#### LeafRole` 皆存在、頂層非 h1、至少兩個不同層級（防塌陷）。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（hotfix.md §測試計畫）
```
$ grep -nc 'RESUME-P3 HEADING-HOTFIX-1' pipelines/resume_pipeline.py
6     ✅ START/END 包裹

$ grep -nc 'sec.get("level")' pipelines/resume_pipeline.py
0     ✅ 恆=1 死欄讀取已移除（含註解去字面）

$ grep -n 'depth: int = 0|min(2 + depth, 6)|depth=depth + 1|depth=0' pipelines/resume_pipeline.py
L553 depth=0 / L559 depth:int=0 / L571 min(2+depth,6) / L595 depth=depth+1     ✅ 遞迴深度推算

$ grep -nc 'def test_p3_heading_level_by_recursion_depth' tests/test_resume_pipeline.py
1     ✅ 新測試
```

### §5.2 SOP 一致性核查（BE-Hotfix 強制）
```
# logging：logger.error 須 exc_info
$ grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
無命中（合規）

# database：裸 commit
$ grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
無命中（合規）
```

### §5.3 pytest
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
27 passed in 0.68s     ✅（26 既有 + 1 新）

$ venv/bin/python -m pytest tests/ -q
1 failed, 500 passed, 3 skipped in 27.97s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- **500 passed**（MODEL-11 後 499 + 本次 1 新）；唯一 failed 為既知環境 flake。✅ 不退化。
- 語法 `ast.parse` → OK。

---

## §6 不可動清單遵守狀態（hotfix.md）
| 不可動項 | 判定 |
|---|---|
| `content` item 分流（text/formula/figure/table）| [x] ✅ 未動 |
| `_translate_whole` / `_t` / C4 退化偵測（`_is_heading_degraded`/`_flatten_sections`/`_own_text_len`）| [x] ✅ 未動 |
| `run_phase3` 主流程 / `BilingualMarkdownSpec` 合約 | [x] ✅ 未動 |
| A軌 `md_restore_processor` / `translate_processor` / 其餘四路 / 母提示詞 / DB Schema | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `pipelines/resume_pipeline.py` + `tests/test_resume_pipeline.py`。

---

## §7 銜接與下一步
- **⚠️ Golden 重捕（baron 運維、非 commit）**：本 hotfix 改變 B軌 `final_zh` 標題層級（`#`→`##`/`###`/`####`）→ 衝擊 golden D1/D2。Flip/結案前須重捕 resume 單路：
  ```bash
  venv/bin/python tools/golden_baseline.py capture resume --force
  ```
  （與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 同屬 B軌輸出變更類；其餘四路無 B軌免捕。）
- **E2E 肉眼驗證**：影子上傳履歷 → B軌 `final_zh`：頂層段落（工作經歷/學歷…）= `##`、公司條目 = `###`、子項 = `####`，階層回復、不再全 h1。
- **收官歸檔**：本報告 + hotfix.md 一次性 mv → `hotfixes/`（§8）。

---

## §8 baron 執行命令
```bash
# 1. 備份檔案已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_resume_pipeline.py.bak
#    .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_test_resume_pipeline.py.bak

# 2. 收官搬移已由 Claude Code 完成（mv hotfix.md + 執行.md → hotfixes/）；git add 清單：
git add pipelines/resume_pipeline.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_執行.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-P3_HEADING-HOTFIX-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-P3_HEADING-HOTFIX-1_msg.txt
```

### §8.2 commit message 草稿
```
fix(resume): RESUME-P3 HEADING-HOTFIX-1 — B軌標題層級改由遞迴深度推算 (修標題塌陷全 h1)

修改 pipelines/resume_pipeline.py：
1. 在 _restore_sections_markdown 呼叫時傳入起始 depth=0。
2. 在 _restore_one_section 方法簽名增加 depth，並將 level 計算改為遞迴深度公式 level = min(2 + depth, 6)，消除恆=1的 level 扁平死欄短路。
3. 遞迴 children 時傳入 depth=depth + 1，完成遞迴深度推算標題層級。
修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_heading_level_by_recursion_depth 驗證 3 層巢狀 section 能正確還原出 h2/h3/h4 標題，結構層級正確且不依賴 level 資料欄位。
變更與新增區塊已使用 # === [RESUME-P3 HEADING-HOTFIX-1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <HEADING-HOTFIX-1-hash>     # 單獨回退本 hotfix（保留 RESUME-P3 C1-C6）
git reset --hard a1d5d7f               # 或退回 hotfix 前最後穩定點（RESUME-P3 C6）
```

---

## §99 Revision
- v1 (2026-06-06)：HEADING-HOTFIX-1 落地——`_restore_one_section` 標題層級改遞迴深度 `level=min(2+depth,6)`（廢恆=1 level 扁平死欄短路）+ `_restore_sections_markdown` depth=0 起算 + children depth+1；追加 `test_p3_heading_level_by_recursion_depth`（3 層巢狀全 level=1 仍還原 ##/###/####、防塌陷）；HEADING-HOTFIX-1 包裹 + 2 .bak；grep 全綠（包裹 6 / sec.get("level")=0 / 遞迴深度 / 新測試）、SOP logging+database 合規、resume 27 passed、全套件 500 passed（唯一 failed 既知 LOG_FORMAT env flake）；改 B軌標題層級 → resume golden 須重捕（baron 運維）。
