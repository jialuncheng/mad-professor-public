# IMG-FILTER C2 — Engine Figure-Filter Hook（引擎純加法注入點）執行報告

---

**任務代號**：IMG-FILTER C2
**執行日期**：2026-07-20
**依據規劃**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`（§8 C2）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `de3a475`（IMG-FILTER C1、過濾器本體零接線）。`ingestion_engine` figure block 無過濾閘門、無 `figure_filter` 注入介面。
- **完成狀態**：`figure_filter` 可選參數**貫穿三函式**（`split_blocks` L132／`build_sections` L227／`assemble` L290、flush 內兩處呼叫同步傳遞）；DROP 閘門落於 figure block 產生前——**已匹配 caption 於 DROP 路徑標 `used[cap_idx]=True`**（孤兒圖說防護硬要求）。**litedoc 仍未接線**（grep 0 命中、C3 界線）、預設 None 與現行為完全等價（等價測試實證）。全套件 **827 passed**（C1 後基線 822＋5、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.2（engine 純加法注入＋caption used 硬要求）；無偏離——既有業務邏輯（清洗／分類／段落拼接）100% 相同、引擎維持零 IO。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | `ingestion_engine` figure_filter 純加法貫穿（三函式）＋DROP 閘門含 caption used 標記＋測試 ×5 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/ingestion_engine.py` | `.claude-logs/archive/2026-07-20_IMG-FILTER_C2_ingestion_engine.py.bak` | `figure_filter=None` 貫穿三函式＋figure 分支過濾閘門＋`Callable` import |
| 修改 | `tests/test_ingestion_engine.py` | `.claude-logs/archive/2026-07-20_IMG-FILTER_C2_test_ingestion_engine.py.bak` | 新增 `TestFigureFilterHook` ×5（既有 26 測試斷言零改） |

> ⚠️ 兩 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 hook 位置與 caption 防護（核心片段）

閘門置於 figure 分支內、**caption 查找之後、block 組裝之前**（cap_idx 已知才能標記）：

```python
m_img = _FIGURE_RE.match(stripped)
if m_img:
    used[i] = True
    alt, src = m_img.group("alt"), m_img.group("src")
    caption, cap_idx = _find_caption(lines, i, used)
    # === [IMG-FILTER C2] 過濾閘門：DROP 時 block 與 caption 皆不入；
    # caption 行必標 used（防退化為孤兒 text block、plan v2 §2.2 硬要求）===
    if figure_filter is not None and not figure_filter(src, alt):
        if caption and cap_idx is not None:
            used[cap_idx] = True
        i += 1
        continue
    fig_block = {...}  # KEEP 路徑零變（content=![alt](src) 契約原樣）
```

**孤兒圖說防護機制**：`_find_caption` 僅回傳、不標記——若 DROP 路徑漏標 `used[cap_idx]`，後續掃描會把圖說行當一般行處理（一般圖說不匹配 `_FIGURE_CAPTION_RE` 之 Figure-N 型式者將成 text block 重播）——正是 PIPE-LITEDOC-QA 孤兒圖說缺陷的回歸路徑，故 DROP 與 KEEP 兩路皆標。

### §4.2 三函式貫穿（純加法）

`split_blocks(lines, *, figure_filter=None)` → `build_sections(..., *, figure_filter=None)`（`flush()` 內兩處 `split_blocks(buffer, figure_filter=figure_filter)`）→ `assemble(..., figure_filter=None)`；`typing` 補 `Callable`。預設 None 全路徑與修改前行為等價；filter 收 markdown 原文 `(src, alt)`（§4 接縫契約：src 零轉換、測試釘死）；引擎自身仍零 IO（讀檔在呼叫端 closure）。

### §4.3 測試 ×5（`TestFigureFilterHook`）

缺省／顯式 None 等價（含 caption 關聯零變）；**全過濾**（figure 不入、caption 不入且 body 無 "sample caption"＝孤兒守門、text/table/formula 零變）；恆 True ＝ None 完全等價；**選擇性過濾保序**（三圖濾一、序列逐項斷言＋KEEP 者 content 契約）；filter 收到原文 (src, alt)。既有 26 測試（含 PIPE-INGEST C1/C3 全部）原樣通過＝byte 等價回歸。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/ingestion_engine.py
 M tests/test_ingestion_engine.py
?? .claude-logs/archive/2026-07-20_IMG-FILTER_C2_ingestion_engine.py.bak
?? .claude-logs/archive/2026-07-20_IMG-FILTER_C2_test_ingestion_engine.py.bak
```

### §5.2 目標測試（實貼）

```
tests/test_ingestion_engine.py
...............................                                          [100%]
31 passed in 0.59s
```

（26 既有＋5 新增；既有全數原樣通過＝預設路徑等價實證）

### §5.3 全套件（實貼）

```
827 passed, 3 skipped, 3 warnings in 56.37s
```

C1 後基線 822 passed → **827 passed（+5、0 failed、零回歸）**。

### §5.4 §6.2 驗收 grep（實貼）

```
--- figure_filter 三函式貫穿
pipelines/ingestion_engine.py:132（split_blocks 簽名）/:173（閘門）/:227（build_sections 簽名）
/:245/:249（flush 兩處傳遞）/:290（assemble 簽名）/:302（傳遞）
--- litedoc 未接線（期望 0 命中）
grep -rn "figure_filter" pipelines/litedoc_pipeline.py → 0 matches（exit=1）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <兩修改檔>
無命中（合規）——本 commit 未新增日誌呼叫（審計 log 在 image_filter、C1 已核）
--- database：grep -nE "\.commit\(\)" <兩修改檔> | grep -v "with .*session.*begin()"
無命中（合規）——零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `pipelines/litedoc_pipeline.py` — 零改（C2 未接線、grep 實證、防 staging 混雜）
- [x] `ingestion_engine` 改動僅限三函式對 `figure_filter=None` 之傳遞與呼叫——清洗／分類／段落拼接等既有邏輯 100% 相同（26 既有測試原樣通過實證）
- [x] DROP 路徑 caption `used[cap_idx]=True` 硬要求 — 落地＋守門測試
- [x] `pipelines/image_filter.py`（C1 產物）／`section_engine`／三路 pipeline／A 軌鏈／contracts — 零碰
- [x] 既有 tests 斷言本體 — 零改（僅新增 5 測試）

---

## §7 銜接

- **baton 狀態**：C1／C2 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add。
- **hash 自癒**：C1 已 ship＝`de3a475`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：plan v2 §2.2 落地——注入介面與孤兒防護就緒、C3（litedoc pre-pass 接線）唯一前置齊備。**（負向防錯）**：閘門生效與否完全取決於呼叫端注入——C2 後生產行為零變、真實過濾效果自 C3 接線起；§7.2 全鏈整合測試依拆分屬 C3。
- **下一步**：C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）；等 baron 確認本 commit 後另行下達 C3 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/ingestion_engine.py
git add tests/test_ingestion_engine.py
git add .claude-logs/archive/2026-07-20_IMG-FILTER_C2_ingestion_engine.py.bak
git add .claude-logs/archive/2026-07-20_IMG-FILTER_C2_test_ingestion_engine.py.bak

# 3. commit message 草稿（已寫入 /tmp/IMG-FILTER_C2_msg.txt）
cat > /tmp/IMG-FILTER_C2_msg.txt << 'EOF'
BE-Refactor: IMG-FILTER C2 — Engine Figure-Filter Hook（引擎純加法注入點）

1. 修改 pipelines/ingestion_engine.py 的 split_blocks、build_sections、以及 assemble 介面，貫穿注入 figure_filter 參數，以純加法方式支援外部過濾。
2. 於 split_blocks 實作圖片過濾閘門：當圖檔被 figure_filter 攔截為 False 時，確保其已關聯的 Caption 行在 used 陣列中標記為 True 以防退化重播，隨後跳過該 block。
3. 擴充 tests/test_ingestion_engine.py 驗收無注入時的等價回歸、全過濾時圖片與圖說之拋棄斷言、以及選擇性過濾的保序。
EOF

# 4. baron 手動執行
git commit -F /tmp/IMG-FILTER_C2_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-20)：C2 執行完成——figure_filter 三函式貫穿＋caption used 硬要求＋5 測試、827 passed 零回歸、litedoc 未接線界線遵守、SOP 雙核查合規
