# Phase 4.7d Commit 8 — 執行報告（_resolve_venue 型別容錯）

> 基準：`62ebe07`（Phase 4.7d Commit 6）
> 完成：1 commit 本地建立完成，**未 push**

---

## Commit Hash

| # | Hash | Subject |
|---|---|---|
| 8 | `1a605fa` | fix(md_restore): _resolve_venue 型別容錯 |

## diff stat

```
 processor/md_restore_processor.py  | 53 ++++++++++++++++++++++++++++----------
 tests/test_md_restore_processor.py | 37 ++++++++++++++++++++++++++
 2 files changed, 77 insertions(+), 13 deletions(-)
```

---

## 真因

baron 實測 ALi 簡報跑 md_restore 階段炸：
```
AttributeError: 'list' object has no attribute 'strip'
```

`_resolve_venue` (L327) 假設 `metadata.organization.value` 是 str、直接 `.strip()`。LLM 對該 PDF 把 organization 自由發揮回 list（多機構名）；schema `_LIST_FIELDS = {'authors', 'keywords'}` 沒列入 organization，但 LLM prompt 也沒明文擋 string-only → 型別 drift。

## 修法

md_restore 層做型別容錯（不動 LLM prompt，避免改 prompt 後又出現別的型別逃出）。

### 新增 `_coerce_to_str(v)`
```python
def _coerce_to_str(v) -> str:
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, list):
        for item in v:
            if isinstance(item, str) and item.strip():
                return item.strip()
        return ''
    return ''
```

對 str → strip 行為等效；對 list → 取第一個非空 str；對其他 type（None/int/dict）→ `''`。

### 改用 `_coerce_to_str` 的 5 處

| 函式 | 欄位 |
|---|---|
| `_resolve_venue` | `journal_or_conference` / `publisher` / `organization`（**主修點**） |
| `_resolve_date` | `publication_date` |
| `_resolve_doi` | `doi` |
| `_resolve_title` | `title.value` / `translated_title.value` / `candidate_name.value` 三處 |
| `_resolve_candidate_extras` | `organization` |

### 不動

- `_resolve_authors`：本就預期 list 結構
- `_resolve_abstract`：從 `sections[].content[]` 取、不從 `metadata.value`
- `_resolve_keywords`：原本就用 `str(k).strip()` 套上（隱式 coerce）
- metadata_extractor schema / `_LIST_FIELDS`：未動
- LLM prompt：未動

---

## 5 個新測試

| 名稱 | 驗證 |
|---|---|
| `test_resolve_venue_organization_as_list` | 主修點：`['NVIDIA', 'Mellanox']` → 取 'NVIDIA' |
| `test_resolve_venue_organization_empty_list` | `['', '  ', None]` → 跳過該欄、繼續 fallback |
| `test_resolve_doi_value_as_list` | `[doi_str, fallback]` → 取第一個再走格式驗證 |
| `test_resolve_date_value_as_list` | `[date_str, 'unknown']` → 取 date_str |
| `test_resolve_title_metadata_as_list` | `title.value = [真標題, 副名]` → 取 '真標題' 走決策樹 |

---

## 不可動清單（已遵守）

- [x] metadata_extractor schema / `_LIST_FIELDS`：未動
- [x] LLM prompt：未動
- [x] `_resolve_authors` / `_resolve_abstract`：未動
- [x] pipeline_core / 前端 / DB：未動
- [x] `_deprecated/`：未動
- [x] 未引入新 CDN / 套件

---

## 端到端驗證計畫（給 baron）

### 1. 確認 commit

```bash
git log --oneline -2
# 1a605fa（Commit 8）/ 62ebe07（Commit 6）
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
venv/bin/pytest tests/ -q       # 應 75 passed 3 skipped
```

### 4. Test A — ALi 簡報回歸

- 重新上傳 ALi 簡報（或任一過去因 organization=list 炸過的 paper）
- 預期：
  - logs/pipeline.log 看到 `[md_restore] venue: 'ALi Corp' (organization, llm_page1)` 或類似
  - 不再炸 `AttributeError: 'list' object has no attribute 'strip'`
  - final_*_zh.md / _en.md 正常產生
  - paper 在前端列表正常顯示

### 5. Test B — 既有 str 行為等效

- 上傳一份正常 paper（organization 是 str）
- 預期：行為完全等效於 Commit 8 之前

### 6. Test C — 其他欄位型別容錯（觸發機率低，但測試覆蓋）

- 此 case 一般不會發生，但若觀察到 logs 有「`organization=list`」等型別記錄，可確認 `_coerce_to_str` 攔截路徑生效

### 7. logs（不應出現）

- `AttributeError: 'list' object has no attribute 'strip'`
- `AttributeError: 'list' object has no attribute 'casefold'`
- `AttributeError: 'NoneType' object has no attribute 'strip'`

---

## 回退方式

```bash
git revert 1a605fa --no-edit
# 或硬退：
git reset --hard 62ebe07
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
| Phase 4.7d Commit 4-1 + 4-2 | 2 |
| Phase 4.7d Commit 5 | 1 |
| Phase 4.7d Commit 6 | 1 |
| **Phase 4.7d Commit 8** | **1** |
| **合計** | **27** |

---

## 狀態

**1 commit 已建立、未 push、等 baron 跑完 Test A-B 後一起 push。**
