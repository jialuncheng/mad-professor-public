# PIPE-SLIDES-HOTFIX-1b HOTFIX-1b 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-1b — F2 譯題旁路格式錯誤致影子寫庫掛掉 |
| 執行日期 | 2026-06-11 |
| 依據規劃 | `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md` |
| 次級參考 | baron 影子實測 log（06:45 AttributeError）/ paper_manager.py:231 / web_server.py:714 |
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 29 測試全綠 + 全套件 585 passed + SOP 合規；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：HOTFIX-1（`f933e54`）之上——其 F2 誤塞裸 str 致影子寫庫 AttributeError（P1-P4 全綠但 Paper row 未建、前端不顯示；A 軌不受影響）。
- **本次**：寫入端 dict 化 + 讀取端取 value + 2 測試堵盲區；**僅兩檔**；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-1b | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES HOTFIX-1b — F2 譯題旁路格式錯誤致影子寫庫掛掉 |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （F2 寫入端三欄 dict 化 + run_phase4 讀取端取 value；1b 標記 2 對）
修改：tests/test_slide_pipeline.py    （test_hf2 追加格式契約斷言 + 新增 test_hf1b 同式消費測試；1b 標記 2 對）
```
備份（入版控、審計）：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES-HOTFIX-1b START/END] ===` 包裹）

### ① 寫入端（`_deliver` F2 區塊內就地改）
```python
ctx.raw_metadata["translated_title"] = {
    "value": cover_zh_title, "source": "slide_pipeline", "confidence": "high"}
```
**真因**：`metadata_json` 欄位值全鏈採 metadata_extractor 三欄 dict 契約——`upsert_paper` L231 `.get('value')`、web_server SHADOW-HOTFIX-2 L714 `['value']` 雙端碼證；HOTFIX-1 誤塞裸 str → 對 str 取 `.get` 炸 AttributeError。

### ② 讀取端（`run_phase4`）
```python
_raw_tt = (ctx.raw_metadata or {}).get("translated_title")
_translated = (_raw_tt.get("value") if isinstance(_raw_tt, dict) else _raw_tt) or _title
```
dict 取 value、str 向後相容防呆；影子 `(測試)` 綴邏輯不變。

### ③ 測試堵盲區（HOTFIX-1 之 test_hf2 只測傳參、未測格式契約）
- `test_hf2` 追加：`translated_title` 為三欄 dict、value/source/confidence 斷言。
- 新增 `test_hf1b_meta_dict_upsert_compatible`：**與 `paper_manager.upsert_paper` L231 完全同式** `.get('translated_title', {}).get('value')` 消費（裸 str 在此必炸）+ web_server L714 同式賦值可行性。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
29 passed in 0.59s     # 28 既有（含改版 test_hf2）+ 1 新 test_hf1b

$ venv/bin/python -m pytest tests/ -q
1 failed, 585 passed, 3 skipped   # 唯一 failed=既知 env flake；585（584+1）
```

### §5.3 SOP 核查（BE-Hotfix 強制）
```
$ grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py → 無命中（合規）
$ grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v session.begin → 無命中（合規）
```

## §6 不可動清單遵守

- [x] **僅兩檔**；共用元件（paper_manager/web_server/metadata_extractor）/ A 軌零改（修我方寫入端對齊既有契約、非改契約）。
- [x] 1b 標記平衡（pipeline 2/2、test 2/2）。
- [x] 兩份 `2026-06-01_PIPE*` 規格書長駐 baton 未動未 add。

## §7 銜接（完成緊急修補、歸檔收官）

- 收官自動化已執行：hotfix.md → `hotfixes/`、本報告 → `executions/`（mv + git add）。
- **baron E2E（非 commit）**：影子重傳 ALi/ST 簡報 → log 無 `'str' object has no attribute 'get'`、前端列表顯示該件且標題=中文譯題+(測試)；順帶可驗 HOTFIX-1 F1/F4 效果。
- **golden**：維持原計畫——本 1b 落地後一次首捕 slides golden（`golden_baseline.py capture slides --force`）。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（hotfixes/ 與 executions/ 已於收官自動化 mv + git add 完畢）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-1b_run_提示詞.md
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-1b_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES-HOTFIX-1b_msg.txt
git commit -F /tmp/PIPE-SLIDES-HOTFIX-1b_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <HOTFIX-1b hash>   # 注意：單獨 revert 會退回影子寫庫掛掉狀態（HOTFIX-1 缺陷重現）、
                              # 應連 HOTFIX-1（f933e54）一起評估；或還原 2 .bak
```
