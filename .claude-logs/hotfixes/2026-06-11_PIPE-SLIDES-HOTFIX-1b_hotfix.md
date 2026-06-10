# PIPE-SLIDES HOTFIX-1b — 緊急熱修復：F2 譯題旁路格式錯誤致影子寫庫 AttributeError（前端不顯示）

> 工作流類別：**BE-Hotfix**（修補前次 HOTFIX-1 之 F2 缺陷；17-1b / TODO-HOTFIX-1b 命名先例）
> 依據：baron 影子上傳實測 log（2026-06-11 06:45、`ALi_Strategic_Framework_v3_Victor_20260519_shadow`）
> 受災檔：`pipelines/slide_pipeline.py`（F2 兩處）+ `tests/test_slide_pipeline.py`（堵測試盲區）

---

## 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1b | F2 譯題旁路改**三欄 dict 格式**（`{value, source, confidence}`、對齊 metadata_extractor 契約）+ `run_phase4` 讀取端 dict 取 value（str 向後相容）+ 補格式契約測試 | `待 baron 回填` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

影子上傳簡報：**P1-P4 全綠**（log 證 `chunks=3`、`rag_status=ready`、實體檔案與向量皆產出），但最後一步影子寫庫拋錯：

```
ERROR 影子論文處理失敗（不影響 A 軌正本）: ... - 'str' object has no attribute 'get'
  File "web_server.py", line 723, in run_pipeline_shadow → paper_manager.upsert_paper(
  File "paper_manager.py", line 231, in upsert_paper
    m_tt = (metadata.get('translated_title', {}).get('value')
AttributeError: 'str' object has no attribute 'get'
```

→ Paper row 未建 → `list_papers`（讀 DB）撈不到 → **前端列表看不到該 (測試) 件**（C8-hotfix 修過的同位症狀、由 HOTFIX-1 F2 重新引入）。A 軌正本不受影響。

### 2. 真因診斷 (Root Cause)

**契約格式不匹配**——`metadata`（`metadata_json`）的欄位值全鏈採 metadata_extractor 三欄格式 `{value, source, confidence}`：

- `paper_manager.upsert_paper` L231：`metadata.get('translated_title', {}).get('value')`——期望 **dict**。
- `web_server` SHADOW-HOTFIX-2 L714：`meta_dict['translated_title']['value'] = f"{_tt_val} (測試)"`——同樣期望 **dict**。

而 **HOTFIX-1 F2 塞的是裸字串**：

```python
ctx.raw_metadata["translated_title"] = cover_zh_title   # ← str、非 {value: ...}
```

影子寫庫把 `raw_metadata` 整包當 `meta_dict` 餵 `upsert_paper` → 對 str 呼 `.get('value')` → AttributeError。

**為何 HOTFIX-1 測試沒照出**（流程誠實）：`test_hf2` 只斷言 `rag_indexer.index` 傳參與旁路存在、**未斷言旁路值的格式契約**、更無 web_server 寫庫端整合——測試盲區，本次補堵。

---

## 熱修復修法 (Minimal Hotfix)

### `pipelines/slide_pipeline.py` — 兩處最小改動（`# === [PIPE-SLIDES-HOTFIX-1b ...] ===` 包裹）

#### ① 寫入端（`_deliver` F2 區塊、原 HOTFIX-1 落點就地改）

```python
            # === [PIPE-SLIDES-HOTFIX-1b START] === F2 旁路值改三欄 dict（HOTFIX-1 誤塞裸 str →
            # upsert_paper L231 / web_server L714 對 dict 取 .get('value')/['value'] → AttributeError、
            # 影子寫庫掛掉前端不顯示；對齊 metadata_extractor {value,source,confidence} 全鏈契約）
            cover_zh_title = zh_fields[0][0] if zh_fields else ""
            if cover_zh_title:
                ctx.raw_metadata["translated_title"] = {
                    "value": cover_zh_title,
                    "source": "slide_pipeline",
                    "confidence": "high",
                }
            # === [PIPE-SLIDES-HOTFIX-1b END] ===
```

#### ② 讀取端（`run_phase4` F2 區塊、dict 取 value + str 向後相容）

```python
        # === [PIPE-SLIDES-HOTFIX-1b START] === 旁路值已為三欄 dict → 取 value（str 向後相容防呆）
        _raw_tt = (ctx.raw_metadata or {}).get("translated_title")
        _translated = (
            _raw_tt.get("value") if isinstance(_raw_tt, dict) else _raw_tt
        ) or _title
        # === [PIPE-SLIDES-HOTFIX-1b END] ===
        if ctx.paper_id.endswith("_shadow") and not _translated.endswith(" (測試)"):
            _translated = f"{_translated} (測試)"
```

### `tests/test_slide_pipeline.py` — 改 1 補 1（堵盲區）

```python
# 既有 test_hf2_translated_title_wired 追加格式契約斷言：
    tt = ctx.raw_metadata['translated_title']
    assert isinstance(tt, dict) and tt['value'] == '譯Power Deck'      # 三欄 dict（非裸 str）
    assert tt.get('source') and tt.get('confidence')

# 新增寫庫端契約測試（模擬 upsert_paper L231 取法、HOTFIX-1b 主回歸）：
def test_hf1b_meta_dict_upsert_compatible(monkeypatch, tmp_path):
    """F2 旁路值必須能被 upsert_paper 式 .get('value') 消費（裸 str 必紅）。"""
    ...跑 run_phase3 後：
    m_tt = ctx.raw_metadata.get('translated_title', {}).get('value')   # 與 paper_manager L231 同式
    assert m_tt == '譯Power Deck'
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -v   # 28 既有 + 1 新全綠
venv/bin/python -m pytest tests/ -q                          # 全套件不退化（基準 584）
```

### §5 SOP 核查（BE-Hotfix 強制）
```bash
grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py   # 預期：無命中
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v session.begin # 預期：無命中
```

### 2. 本地 E2E 快速復現與驗證（baron、非 commit）
1. 影子重傳同一份 ALi/ST 簡報 → log **無** `'str' object has no attribute 'get'`、出現 upsert 成功；前端列表顯示該件、**標題為中文譯題 + (測試)**（web_server L714 對 dict 補綴生效）。
2. 點開閱讀視圖正常（HOTFIX-1 F1/F4 效果同步可驗）。

### ⚠️ golden
不另衝擊（F2 只影響 DB/rag_tree 譯題、HOTFIX-1 已宣告 slides golden 落地後首捕——**維持原計畫：本 1b 落地後一次首捕**）。

---

## 回退與備案

```bash
git revert <HOTFIX-1b hash>          # 單 commit 可逆
# 或還原 .bak：
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_slide_pipeline.py.bak
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1b_test_slide_pipeline.py.bak
# 備案：若 revert 則回到 HOTFIX-1 狀態（影子寫庫仍會掛）→ 不建議單獨 revert 1b、應連 1 一起評估
```

---

## commit message 草稿（落地時寫入 /tmp/PIPE-SLIDES-HOTFIX-1b_msg.txt）

```
BE-Hotfix: PIPE-SLIDES HOTFIX-1b — F2 譯題旁路格式錯誤致影子寫庫掛掉

修補 HOTFIX-1 F2 引入的回歸：raw_metadata['translated_title'] 誤塞裸 str、
而 upsert_paper L231 / web_server SHADOW-HOTFIX-2 L714 全鏈期望 metadata_extractor
三欄 dict 格式 → 影子寫庫 AttributeError（P1-P4 全綠但 Paper row 未建、前端不顯示）。
- 寫入端改 {value, source, confidence} 三欄 dict（對齊全鏈契約）
- run_phase4 讀取端 dict 取 value（str 向後相容防呆）
- test_hf2 追加格式契約斷言 + 新增 upsert 同式消費測試（堵 HOTFIX-1 測試盲區）

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
