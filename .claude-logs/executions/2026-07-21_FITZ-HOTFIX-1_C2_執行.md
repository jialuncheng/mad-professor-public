# FITZ-HOTFIX-1 C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）執行報告

---

**任務代號**：FITZ-HOTFIX-1 C2
**執行日期**：2026-07-22
**依據規劃**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` §8 C2
**上游 plan**：同名 `_plan.md`（v4、六問拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §1 基準與完成狀態

- 基準 commit：`e8d57a6`（FITZ-HOTFIX-1 C1、baron 已 ship）
- 完成狀態：R6（含時序前移）+ R7 已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 範圍自檢：`git status -s`（排除 .claude-logs）＝恰為宣告之 4 檔

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor Refinement（Fitz 處理器標題救回與結構修復） | `e8d57a6` |
| C2 | P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `pipelines/ingestion_engine.py` | 修改 | R6：`meta_values` 純加法貫穿 `mark_meta_lines`/`assemble` + 正規化純函式 |
| `pipelines/litedoc_pipeline.py` | 修改 | R6 時序前移 + `_collect_meta_values`/`_date_variants` + R7 `_clean_short_number_lines` 接線 |
| `tests/test_ingestion_engine.py` | 修改 | +7 測試（R6 正規化/等價/剝除/soft-fail 兜底/assemble 端到端） |
| `tests/test_litedoc_pipeline.py` | 修改 | +18 測試（R7 剝除與守衛、R6 值集合與變體、時序斷言） |
| `.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_*.bak` ×4 | 備份 | 改前快照（隨本 commit git add） |

（baton 暫存之 plan/tasks/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

### R6 — `mark_meta_lines` 值比對演算法
新增純函式 `_normalize_meta_text(s)`＝`casefold()` + 僅保留 `isalnum()` 字元——吸收大小寫／空白／標點差異（`MARC ANDREESSEN AND MICHAEL MCGUINESS` ≡ `Marc Andreessen and Michael McGuiness`）；`normalize_meta_values(values)` 將呼叫端值集合轉正規化集合（空值自動略去）。`mark_meta_lines` 新增 `meta_values: Optional[Set[str]] = None`（**預設 None → 行為 byte 等價**），內部以閉包 `_apply_value_pass` 對**未標記行**掃描：整行正規化後**等於**任一值即標 meta（鍵 `meta_value`、供審計）。

**關鍵設計**：比對為「**整行相等**」而**非子字串包含**——正文句「In 2019 Marc Andreessen wrote…」不會被誤殺（測試守門）。且值比對於**判型成功與 soft-fail 兩路皆套用**（原三處 `return fallback` 統一改走 `_fallback()` 閉包）——正是 plan「不依賴判型心情」之確定性兜底本意：fitz md 前段形狀走樣致 DocAnalyzer 判型失準時，仍能剝除 meta 重播。`assemble` 同步貫穿該參數（末位、預設 None）。

### R6 — `_extract_litedoc_metadata` 時序前移接點
原序 `_build_tiles`(L191) → `_extract_litedoc_metadata`(L194) 顛倒（plan §3.8 grep 證），使 meta 值無法注入 assemble。今將 metadata 抽取**前移至 `_build_tiles` 之前**（現 L269 < L272）。該函式簽名單參數、僅唯讀 `markdown_text`、零 tiles 依賴 → 調序安全無副作用；**下游 `_resolve_title`／`source_lang` 合成／`raw_metadata` 旁路等消費位置一律保持原位不動**（僅移動抽取本身、diff 最小）。

### R6 — 呼叫端 `_collect_meta_values` 與 date 變體
`_collect_meta_values(meta)` 組值集合：① `authors` list 逐項 + **合併型**（`" and ".join` / `", ".join`——扉頁常整行印 `A AND B`）；② `publisher`／`date` 原值；③ `_date_variants(iso)` 展開列印變體。**分工明確**：大小寫/分隔符差異由 engine 正規化吸收，本函式只處理**語意變體**。`_date_variants("2026-06-15")` → `{Jun 15, June 15, Jun 15 2026, June 15 2026, 06/15/2026, 2026/06/15}`；非 ISO／月份越界 → 空集合（不阻斷）。

### R7 — `_clean_short_number_lines` 過濾與守衛
接線於清洗步（`MarkdownCleaner().clean` 後、與 `repair_ligatures` 同段）。`_is_number_dominated(line)` 三閘：① **markdown 語法行首守衛**——`#`/`!`/`>`/`-`/`*`/`|` 一律跳過（防誤殺 `- 1` 列表／`# 1` 標題／`![alt](src)` 圖行／`| 1 |` 表格／`> 1` 引用）；② token 數 ≤3；③ 數字 token（`^\d+([.,]\d+)*$` 精確匹配整數/千分位/小數）**過半**——含字母者（`v1.2`/`M1`/`A4`/`3rd`）自動不計為數字。

**行數不變式**：命中行改為**空行**（不刪行）→ 下游 doc_structure 判型行索引與 `assemble`／`_collect_header_srcs` 行界維持同基準（與連字修復同一哲學）。誠實邊界：`561 Likes` 型（1/2 不過半）會逃——保守版先行、寧漏勿誤殺（plan Q3 拍板）。

## §5 測試與 Grep 結果

```
tests/test_ingestion_engine.py：39 passed（32 既有 + 7 新增）
tests/test_litedoc_pipeline.py：113 passed（95 既有 + 18 新增）
全套件：958 passed, 3 skipped, 3 warnings in 58.11s   ← 基線 933 + 25、零回歸
```

新增測試重點：
- **R6 engine**：正規化等價（大小寫/分隔）／`meta_values=None` 與未傳參**完全同結果**（純加法保證）／整行值剝除 + **正文句提及作者名不誤殺**／**soft-fail 路徑兜底仍生效**（行號越界 structure）／`assemble` 端到端 meta 重播消失且正文保留／`assemble` 預設等價回歸
- **R6 litedoc**：值集合含 authors 逐項+合併型+publisher+date+6 種列印變體／缺欄與非 ISO 日期安全略過／`_date_variants` 三態（空/非 ISO/月份越界）
- **R6 時序**：mock spy 捕捉呼叫序 → **`meta` 先於 `assemble`** 且 `meta_values` 確實注入（值內容斷言）／`_build_tiles` 未傳參 → assemble 收到 `None`（等價回歸）
- **R7**：`53 82 Share`/`561`/`1,234 5.6` 剝除；`Chapter 5`/4-token/完整句保留；**markdown 語法行 6 種參數化全不剝**；`v1.2`/`M1`/`A4`/`3rd` 不計數字；**行數不變式**斷言

驗收 grep（§6.2 全項）：

```
meta_values 貫穿：engine L98(mark_meta_lines)/L349(assemble)、litedoc L274(注入)/L367(_build_tiles)/L397(→assemble)  ✅
R6 時序：litedoc L269 meta = _extract_litedoc_metadata  <  L272 tiles = _build_tiles  ✅（原 L194 > L191 已倒轉）
R7 接線：L248 _clean_short_number_lines（緊接 L241 repair_ligatures 同段）  ✅
範圍自檢：git status -s（排除 .claude-logs）＝ ingestion_engine / litedoc_pipeline / 兩測試檔  ✅
```

SOP 一致性核查（§6.5）：

```
logging：grep logger.error/exception/traceback.format_exc @ 兩改動檔 → 無命中（合規；
         本 commit 新增日誌點皆為 logger.debug 審計、既有 warning 未動）
database：grep "\.commit()" @ 兩改動檔 → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/pdf_processor.py`／`processor/fitz_processor.py`／`pipelines/section_engine.py`／`web_server.py`／`pipelines/image_filter.py`／`contracts.py` — 零改
- [x] `meta_values` 為**純加法可選參數**、預設 None → resume／slides／book 等其他 consumer byte 等價（測試斷言 `mark_meta_lines`/`assemble` 預設路徑與未傳參完全同結果）
- [x] 時序調整**僅移動** `_extract_litedoc_metadata`；`_resolve_title`／`source_lang` 合成／旁路等下游消費位置原位不動
- [x] R7 markdown 語法行首守衛與精確數字 regex 皆依規格落地（參數化測試守門）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / C1 / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）**（R4 譯題餵 `_title_bare`〔web_server 零改、防重已存在〕+ R8 P3 單點行級圖片過濾）；待 baron ship C2 後另下 C3 提示詞。
- §7.2 跨 Phase 整合測試（tasks §6.4）於 C3 或 Checkout 前補齊（屆時八刀齊備、可端到端串接驗證）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、4 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add pipelines/ingestion_engine.py
git add pipelines/litedoc_pipeline.py
git add tests/test_ingestion_engine.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_ingestion_engine.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_ingestion_engine.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-1_C2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C2_msg.txt
```
