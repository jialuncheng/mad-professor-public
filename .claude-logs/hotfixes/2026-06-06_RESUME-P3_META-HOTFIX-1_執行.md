# RESUME-P3 META-HOTFIX-1 — P1 Meta 渲染進文件 header 執行報告

---

**任務代號**：RESUME-P3 META-HOTFIX-1（BE-Hotfix）
**執行日期**：2026-06-06
**依據計畫**：`.claude-logs/baton/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md`
**次級參考**：`sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 驗收全綠 + 收官歸檔；待 baron commit）

---

## §1 基準與完成狀態
- **基準**：PARA-HOTFIX-1（`2772822`）head。
- **完成狀態**：`pipelines/resume_pipeline.py` 新增 `_render_meta_header`（讀 raw_metadata 旁路 + ingestion.title、組無序列表 header）+ `run_phase3` 寫出前 prepend final_zh/en；`tests/test_resume_pipeline.py` 追加 1 測試 + 對齊 2 既有 run_phase3 測試（header carryover）；`# === [RESUME-P3 META-HOTFIX-1 START/END] ===` 包裹；改前 2 `.bak`。**未 commit**（待 baron）。

---

## §2 落地 Commit 表格
| # | Hash | Subject |
|---|---|---|
| META-HOTFIX-1 | （待回填）| `fix(resume): RESUME-P3 META-HOTFIX-1 — run_phase3 組文件 header 讓 final 含 P1 meta` |

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 新增 `_render_meta_header` static helper + `run_phase3` prepend zh/en | `archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_meta_header_rendered` + 對齊 2 既有 run_phase3 測試（header prepend carryover）| `archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak` |

`git diff --stat`：
```
 pipelines/resume_pipeline.py  | 51 +++++++++++++++++++++++++++++++++
 tests/test_resume_pipeline.py | 59 +++++++++++++++++++++++++++++++++++++---
 2 files changed, 107 insertions(+), 3 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因（渲染缺口）
P1 抽的 meta 放兩處：`IngestionMetadataSpec.title`（姓名）+ `ctx.raw_metadata`（domain/organization/phone/email）。raw_metadata 旁路**設計終點是 DB**（P2 讀 domain→LCC、web_server 寫 `Paper.metadata_json`）。`run_phase3`（唯一產 final 處）只渲染 section body、**從不讀 raw_metadata、無 header 組裝** → P1 meta 對最終文件零貢獻。

### §4.2 修法（`pipelines/resume_pipeline.py`，走現有旁路、不動合約）
**新增 `_render_meta_header(ctx, gspec, *, lang)`**：
```python
raw = ctx.raw_metadata or {}
title = ((ctx.ingestion.title if ctx.ingestion else "") or "").strip()   # 含 (測試)
domain = ResumePipeline._meta_value(raw, "domain") or ""
if lang == "en":
    domain = (gspec.domain_name if gspec else "") or domain               # en 優先 LCC 英文名
org   = ResumePipeline._meta_value(raw, "organization") or ""
phone = ResumePipeline._meta_value(raw, "phone") or ""
email = ResumePipeline._meta_value(raw, "email") or ""
# # 姓名 + 無序列表（- **欄**：值）；缺項省略；整包空回 ''；結尾 \n\n
items = [f"- **{label[k]}**{sep}{v}" for k, v in (...) if str(v).strip()]
```
**`run_phase3` 寫出前 prepend**：
```python
zh_text = self._render_meta_header(ctx, gspec, lang="zh") + zh_text
en_text = self._render_meta_header(ctx, gspec, lang="en") + en_text
```
- **無序列表**（`- `）：CommonMark 規範保證每欄獨立一行，不依賴行尾空格、根治 RAG-10 軟換行（取代脆弱的 blockquote+尾隨空格）。
- **(測試) 保留**（baron 拍板、便於觀察）。
- **不動**：HEADING/PARA 實作、`_restore_sections_markdown`、凍結合約、A軌（不 import/不耦合）、其餘四路、母提示詞、DB。

### §4.3 測試
- 新增 `test_p3_meta_header_rendered`：`# 王小明 (測試)` 開頭 + 領域/機構/電話/Email 值 + 各欄獨立 list item（`\n- **領域**：` 等）。
- 對齊 2 既有 run_phase3 測試（header prepend carryover）：
  - `test_run_phase3_bypass_doctype_and_carryforward`：`final_zh/en == 純譯文` → 改 `startswith("# x")` + `rstrip().endswith(body)`。
  - `test_run_phase3_injects_resume_constraints`：`"(測試)" not in final_zh` → 改 `"# 王小明 (測試)" in final_zh`（(測試) 現於 header h1、intended）。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（hotfix.md §測試計畫）
```
$ grep -nc 'RESUME-P3 META-HOTFIX-1' pipelines/resume_pipeline.py        → 4   ✅ START/END 包裹
$ grep -nc 'def _render_meta_header' pipelines/resume_pipeline.py        → 1   ✅ helper
$ grep -nc '_render_meta_header(ctx' pipelines/resume_pipeline.py        → 2   ✅ run_phase3 prepend zh/en
$ grep -nc 'md_restore_processor|RestoreProcessor|_render_header_en' pipelines/resume_pipeline.py → 0  ✅ 不耦合 A軌
$ grep -nc 'def test_p3_meta_header_rendered' tests/test_resume_pipeline.py → 1  ✅ 新測試
```

### §5.2 SOP 一致性核查（BE-Hotfix 強制）
```
logging：grep logger.error|exception|traceback（resume_pipeline.py）→ 無命中（合規）
database：grep .commit()（resume_pipeline.py）→ 無裸 commit（合規）
```

### §5.3 pytest
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
29 passed in 0.63s     ✅（27 既有 + 1 新 + 2 對齊）

$ venv/bin/python -m pytest tests/ -q
1 failed, 502 passed, 3 skipped in 23.74s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- **502 passed**（PARA 後 501 + 本次 1 新）；唯一 failed 為既知環境 flake。✅ 不退化。
- 語法 `ast.parse` → OK。

---

## §6 不可動清單遵守狀態（hotfix.md）
| 不可動項 | 判定 |
|---|---|
| 標題還原（HEADING-HOTFIX-1）/ 段落正規化（PARA-HOTFIX-1）| [x] ✅ 未動 |
| `_restore_sections_markdown` 文體解析重組 | [x] ✅ 未動（header 只 prepend、不碰 body）|
| 凍結合約 `IngestionMetadataSpec` / `BilingualMarkdownSpec` | [x] ✅ 未動（走現有旁路）|
| `ctx.raw_metadata` 旁路本體 / P2 domain 消費 / web_server 寫庫 | [x] ✅ 未動（只新增讀取） |
| A軌 `md_restore_processor`（不 import、不耦合）/ 其餘四路 / 母提示詞 / DB Schema | [x] ✅ 未動（grep 0）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

> 對齊的 2 個既有測試屬 header prepend carryover（行為變更必然連動）、非越界改業務邏輯。`git diff --stat` 證：本次僅 `resume_pipeline.py` + `test_resume_pipeline.py`。

---

## §7 銜接與下一步
- **⚠️ Golden 重捕（baron 運維、非 commit）**：本 hotfix 在 B軌 `final_zh`/`final_en` 開頭新增 header → 衝擊 golden D1/D2。Flip/結案前須重捕 resume 單路：
  ```bash
  venv/bin/python tools/golden_baseline.py capture resume --force
  ```
- **E2E 肉眼**：影子上傳履歷 → B軌 `final_zh` 開頭出現 `# {姓名} (測試)` + 領域/機構/電話/Email 各欄獨立一行；body（工作經歷…）緊接其後、層級/段落正常；body 無第二個姓名 h1。
- **治本銜接**：INFRA-4（A軌死後）把 `_render_meta_header` 的讀取源由 `ctx.raw_metadata` 改為 `spec.meta`（本 helper 唯一改動點）。
- **domain 乾淨標籤**：屬另一任務（改 P1 domain prompt）、不在本 hotfix。

---

## §8 baron 執行命令
```bash
# 1. 備份檔案已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak
#    .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak

# 2. 收官搬移已由 Claude Code 完成（mv hotfix.md + 執行.md → hotfixes/）；git add 清單：
git add pipelines/resume_pipeline.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_META-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_META-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_META-HOTFIX-1_執行.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-P3_META-HOTFIX-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-P3_META-HOTFIX-1_msg.txt
```

### §8.2 commit message 草稿
```
fix(resume): RESUME-P3 META-HOTFIX-1 — run_phase3 組文件 header 讓 final 含 P1 meta

修改 pipelines/resume_pipeline.py：
1. 新增 pipelines/ 私有 helper _render_meta_header：讀現有 ctx.raw_metadata 旁路（domain/organization/phone/email）+ ctx.ingestion.title（姓名、沿用原值含 (測試)）+ gspec.domain_name（en 領域），組文件開頭 header（# 姓名 + 領域/機構/電話/Email 無序列表、缺項靜默省略、無序列表規範保證一欄一行防軟換行）。
2. run_phase3 寫出前 prepend header 至 final_zh（中文 label）/ final_en（英文 label），讓 P1 抽的 meta 進入最終文件。
不動凍結合約（走現有旁路、合約轉正屬 INFRA-4 遠期）；body 還原（HEADING/PARA hotfix）與 A軌均不動。
修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_meta_header_rendered 驗證 final 含 # 姓名（沿用 title 含 (測試)）+ 領域/機構/電話/Email 且各欄為獨立 list item（一欄一行）。
2. 對齊 2 既有 run_phase3 測試（header prepend carryover）。
變更與新增區塊已使用 # === [RESUME-P3 META-HOTFIX-1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <META-HOTFIX-1-hash>     # 單獨回退本 hotfix（保留 C1-C6 + HEADING/PARA）
git reset --hard 2772822            # 或退回 PARA-HOTFIX-1 落地點
```

---

## §99 Revision
- v1 (2026-06-06)：META-HOTFIX-1 落地——`run_phase3` 新增 `_render_meta_header`（讀 raw_metadata 旁路 domain/organization/phone/email + ingestion.title 姓名含 (測試) + en domain 優先 gspec.domain_name、組 `# 姓名`+領域/機構/電話/Email 無序列表、缺項省略、整包空回 ''、list 規範保證一欄一行）+ 寫出前 prepend final_zh/en；走現有旁路不動凍結合約（轉正屬 INFRA-4）；META-HOTFIX-1 包裹 + 2 .bak；追加 test_p3_meta_header_rendered + 對齊 2 既有 run_phase3 測試（header carryover）；grep 全綠（包裹 4 / helper 1 / prepend 2 / A軌不耦合 0 / 新測試 1）、SOP logging+database 合規、resume 29 passed、全套件 502 passed（唯一 failed 既知 LOG_FORMAT env flake）；代號由 HEADER 改 META 避免與 HEADING 混淆；改 B軌輸出 → resume golden 須重捕（baron 運維）。
