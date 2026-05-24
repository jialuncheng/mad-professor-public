# Phase 4.7d Commit 4 — 執行報告（兩個 prompt 修正）

> 基準：`457f1c6`（Phase 4.7d Commit 3：abstract 雙語注入）
> 完成：2 commits 本地建立完成，**未 push**

---

## 2 個 Commit Hash

| # | Hash | Subject |
|---|---|---|
| 4-1 | `9bba1f7` | fix(slides): SLIDE_PROMPT 改 markdown 輸出、保留階層與表格 |
| 4-2 | `2b9aed6` | feat(metadata): resume prompt 加招募平台 / Hunter 判斷 |

---

## 累計 diff stat（457f1c6..HEAD）

```
 processor/metadata_extractor.py      |  5 ++++
 processor/slides_processor.py        | 50 +++++++++++++++++++++++++-----------
 prompt/processor/metadata_resume.txt | 27 ++++++++++++++++++-
 tests/test_metadata_extractor.py     | 29 +++++++++++++++++++++
 4 files changed, 95 insertions(+), 16 deletions(-)
```

純 prompt + schema 加 2 欄位（scalar / bool）+ key rename。**不動** registry、pipeline、md_restore、前端、DB schema。

---

## Commit 4-1 `9bba1f7` — SLIDE_PROMPT markdown 輸出

### 真因
原 SLIDE_PROMPT 要求 LLM 回傳純文字 `content`，導致：
- 投影片內副標題被平鋪、階層概念遺失
- 表格被破壞為「a | b | c」字串行
- 階層、表格、條列混雜

### 改動

`processor/slides_processor.py`：
- **SLIDE_PROMPT 改寫**：要求 LLM 輸出純 markdown（`### 副標題`、markdown 表格、`-` 條列、`1.` 編號、4 空白縮排）
- **階層分工**：`#` 整份簡報、`##` 投影片主標題（由 caller 加）、`###` 投影片內副標題（由 LLM 輸出）
- **圖表分離**：圖表描述繼續走 `figure_description`，**不混進** `markdown_content`
- **JSON key 改名**：`content` → `markdown_content`

caller `_process` 對應改 key 名：
- `result.get("content")` → `result.get("markdown_content")`
- 空判斷 / log 字數 / `lines.append` 同步換變數名

### 不動
- 投影片主標 `## {slide_title}` 由 caller 加（line 142-145 不動）
- `## 第 N 頁` fallback 不動
- 圖片插入 `![slide_NN](images/...)` 不動

---

## Commit 4-2 `2b9aed6` — resume 招募平台 / Hunter 判斷

### 真因
履歷不一定是候選人自己投的版本：
- **招募平台代發**（104 / LinkedIn / CakeResume 等）：版型框、平台 logo
- **獵頭改造**（Robert Walters / Michael Page 等）：顧問署名、聯絡走顧問

此時 `candidate_name` 可能被遮蔽為「XXX」「J. Doe」「候選人 A」、聯絡資訊被代理。LLM 應辨識並標記。

### 改動

#### `prompt/processor/metadata_resume.txt`
- 第 7 項 **source_platform**：`self` / `104` / `linkedin` / `cakeresume` / `yourator` / `1111` / `indeed` / `glassdoor` / `robert_walters` / `michael_page` / `adecco` / `hays` / `manpower` / `randstad` / `unknown`
- 第 8 項 **is_third_party**：boolean
- 判斷線索：logo、版型框、顧問署名、URL 浮水印、footer 文字
- `candidate_name` 規則調整：若 `is_third_party=true` 且姓名被遮蔽 → `null`、不編造
- `source_platform` / `is_third_party` 不能為 null（fallback `"unknown"` / `false`）
- JSON 範例追加 2 欄

#### `processor/metadata_extractor.py`
- `_ALL_FIELDS` 加 `'source_platform'`, `'is_third_party'`
- `_LLM_FLAT_KEYS` 同步
- `fill_from_llm_page1` mapping 同步
- `_LIST_FIELDS` 不動（兩者皆 scalar / bool）
- 既有 `_coerce_llm_meta` 邏輯：bool 走 else 分支 pass-through；`None` 走 elif 設 None
- `_set_field` 既有「`value is not None`」判斷 → `False` 也算有值

#### 不動其他 prompt
academic / technical metadata prompt **不動**：這 2 欄非該 doc_type 概念、為 None / 缺失、reader 端 optional chain 處理。

#### tests/test_metadata_extractor.py（新 2 個）
- `test_resume_metadata_includes_source_platform`：schema 結構驗證
- `test_llm_meta_source_platform_field`：fill 後值 / source 正確（含 `is_third_party=True` 寫入）

---

## 不可動清單（已遵守）

- [x] DB schema：未動（`metadata_json` 是 JSON、加欄位不需 migration）
- [x] doc_type registry：未動
- [x] pipeline_core：未動
- [x] 前端：未動
- [x] `md_restore_processor`：未動（resume header template 暫不顯示 source_platform，留 4.7e）
- [x] `domain_detector` / `translate_processor`：未動
- [x] `_deprecated/`：未動
- [x] 未引入新 CDN / 套件

---

## 端到端驗證計畫（給 baron）

### 1. 確認 commits

```bash
git log --oneline -5
# 應看到：
# 2b9aed6（Commit 4-2）/ 9bba1f7（Commit 4-1）
# 457f1c6 / d54a32c / 2da527e（Commit 1-3）
```

### 2. push

```bash
git push origin HEAD:gemini-refactor
```

### 3. OrcStack

```bash
git pull
pkill -f web_server
# 重啟
venv/bin/pytest tests/ -q       # 應 70 passed 3 skipped
venv/bin/python tools/check_doc_type_registry.py   # exit 0
```

### 4. Test 4-1：上傳新 slides PDF

預期：raw markdown（`output/1/<paper>/<name>.md`）內：
- 投影片副標 / 區塊標題 → `### ...`
- 表格 → markdown table 語法（| 表頭 |、`| --- |`）
- 條列 → `- ` 開頭
- 圖表描述 → 仍在 `figure_description`（會被 caller 用 `*圖表：...*` 包）

`logs/pipeline.log`：
```
slide N: 標題=..., 內容字數=...
```

### 5. Test 4-2：上傳 LinkedIn 履歷 PDF

- 預期 `metadata.source_platform.value == "linkedin"`
- 預期 `metadata.is_third_party.value == true`
- 若 LinkedIn 顯示完整姓名 → `candidate_name` 仍有值；若被遮蔽（「J. D.」等）→ `null`

#### Test 4-2 B：上傳獵頭改造履歷

- 預期 `source_platform == "robert_walters"`（或其他顧問公司）
- `is_third_party == true`

#### Test 4-2 C：上傳自寫 PDF 履歷

- 預期 `source_platform == "self"`
- `is_third_party == false`

### 6. 看 logs（不應出現）

- `KeyError: 'source_platform'`
- `KeyError: 'markdown_content'`
- `TypeError: bool not subscriptable`
- slides 內文出現「a | b | c」純文字行（應為 markdown 表格）

---

## 回退方式

```bash
git revert 2b9aed6 9bba1f7 --no-edit
# 或硬退：
git reset --hard 457f1c6
```

---

## 全 worktree 待 push 總覽

| 群 | commits |
|---|---|
| Stage A chat stateless | 4 |
| MinerU 模組化方案 X | 5 |
| Phase 4.7c metadata 顯示 | 5 |
| Phase 4.7c 修正 1-4 | 4 |
| Phase 4.7d Commit 0 + 1 | 2 |
| Phase 4.7d Commit 2 + 3 | 2 |
| **Phase 4.7d Commit 4-1 + 4-2** | **2** |
| **合計** | **24** |

---

## 狀態

**2 commits 已建立、未 push、等 baron 跑完 Test 4-1 / 4-2 後一起 push。**

後續可選 / 待安排：
- 4.7e：md_restore resume header 顯示 source_platform 標記、前端 toolbar 顯示「招募平台」徽章、是否封鎖 LinkedIn 履歷反追蹤
- registry marker 補完（PART II 列出的 8 個無 marker doc_type 分支點，技術債清理）
