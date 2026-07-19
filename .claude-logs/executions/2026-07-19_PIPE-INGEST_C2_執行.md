# PIPE-INGEST C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）執行報告

---

**任務代號**：PIPE-INGEST C2
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md`（v4）
**次級參考**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md`（§8 C2）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `e7b9e6c`（PIPE-INGEST C1、引擎已落地零接線）。litedoc P1 `_build_tiles` 仍走 A 軌組裝借用鏈——meta 判型被連續性假設作廢、figure 無 `content` 鍵、`_structured.json` 中間檔仍產出。
- **完成狀態**：`_build_tiles` 切換為 `ingestion_engine.assemble`（cleaned md + doc_structure sidecar → processed 相容 JSON）→ `TilingProcessor` 零改續用；A 軌 md2json／行級分塊借用鏈於 litedoc **退場**（`grep "MarkdownProcessor\|JsonProcessor"` → 0 命中、含註解層）。全套件 **774 passed**（前基線 771 + litedoc 新測試 3、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v4 §2.2（litedoc P1 切換）＋ §2.4（meta 重複歸零之 body 側）＋ §2.5（圖片全保留之攝入側）；無偏離——僅動 `_build_tiles` 與 imports，P3 譯題鏈／dead code 依界線留 C3。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | litedoc P1 `_build_tiles` 切換 ingestion_engine（meta 分離 + figure content 進 tiles）、A 軌組裝 import 退場、TilingProcessor 零改續用；litedoc 測試更新 +3 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_PIPE-INGEST_C2_litedoc_pipeline.py.bak` | imports 退場＋新增 `ingestion_engine`；`_build_tiles` 改引擎組裝；新增 `_META_TYPES` 注入常數 |
| 修改 | `tests/test_litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_PIPE-INGEST_C2_test_litedoc_pipeline.py.bak` | `_setup_p1_mocks` 移除 Md/Json fake（真引擎直跑）；新增 C2 測試 ×3 |

> ⚠️ 兩 `.bak` 依鐵律**必須**列入本 commit `git add` 清單（§8）。baton/ 暫存之 plan / tasks / 本報告**不在** git add 清單（Checkout 一次性歸檔）。

---

## §4 修法說明

### §4.1 `pipelines/litedoc_pipeline.py` — P1 攝入組裝切換

- **imports（L36-44）**：刪 `from processor.json_processor import JsonProcessor`、`from processor.md_processor import MarkdownProcessor`；增 `from pipelines import ingestion_engine`（C2 marker 區塊）。
- **`_META_TYPES = ("title", "authors", "publication_info")`**：litedoc 之 meta 判型集、route-specific 注入（引擎零字面量紀律的呼叫端側）。
- **`_build_tiles` 改寫**（唯一被改動之方法）：

```python
markdown_text = md_path.read_text(encoding="utf-8")
structure: Optional[Dict[str, Any]] = None
sidecar = md_path.parent / f"{md_path.stem}_doc_structure.json"
try:
    structure = json.loads(sidecar.read_text(encoding="utf-8"))
except Exception as exc:  # noqa: BLE001 — sidecar 缺失/壞損不阻斷 P1
    logger.warning("[PIPE-INGEST P1] %s doc_structure 讀取失敗（soft、無 meta 分離）: %s",
                   paper_name, exc, exc_info=True)
result = ingestion_engine.assemble(markdown_text, structure, meta_types=self._META_TYPES)
processed = output_dir / f"{paper_name}_processed.json"
processed.write_text(json.dumps({"title": result["title"], "sections": result["sections"]},
                                ensure_ascii=False, indent=2), encoding="utf-8")
tiled = output_dir / f"{paper_name}_tiled.json"
TilingProcessor().process(str(processed), str(tiled), doc_type=doc_type)
return self._load_tiles(tiled)
```

- 接縫契約落地：doc_structure 行號基準＝DocAnalyzer heading-fix 後同一 md 快照（`_build_tiles` 於 `analyze` 之後被呼叫、讀同一 `md_path`）；`_processed.json` 沿用現行檔名（審計連續性）、`_structured.json` 不再產出；`_load_tiles` 本體零改。
- 修正過程一處措辭調整：C2 marker 註解初版含退場處理器名稱、與 §6.2「grep 0 命中」驗收（含註解層）衝突 → 改為泛稱「A 軌 md2json／行級分塊借用鏈」（代碼行為零差）。

### §4.2 `tests/test_litedoc_pipeline.py` — 測試更新（+3、既有斷言零改寫）

- `_setup_p1_mocks`：移除 `_FakeMd`／`_FakeJson` 兩 stub 與對應 `monkeypatch.setattr`（對應 plan §2.2：borrowed 組裝退場後模組屬性不存在、patch 必失敗）；**攝入組裝改走真 `ingestion_engine`**（純函式直跑、無需 stub）；`_FakeTiling` 續用。既有 P1-P4 測試斷言本體零改寫、全數通過。
- 新增 `test_p1_build_tiles_via_ingestion_engine`：真 md（epigraph 夾於 byline 前之非連續判型）+ 真 doc_structure sidecar + **真 TilingProcessor**（bypass、零 API）→ 斷言 meta 行不入 tiles、title 不入內文、epigraph 保留、figure `content=![a](images/x.jpg)` 穿透、`_processed.json` 產出且 `_structured.json` 不再產（plan §2.2/§2.4/§2.5）。
- 新增 `test_p1_build_tiles_soft_fail_without_structure`：sidecar 缺失 → soft 退化（無 meta 分離、body 全保留、不阻斷）。
- 新增 `test_p1_borrowed_chain_retired`：模組源碼靜態掃描（借用鏈 token 0、引擎已接線）。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/litedoc_pipeline.py
 M tests/test_litedoc_pipeline.py
?? .claude-logs/archive/2026-07-19_PIPE-INGEST_C2_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_PIPE-INGEST_C2_test_litedoc_pipeline.py.bak
```

### §5.2 litedoc + engine 測試（實貼）

```
tests/test_litedoc_pipeline.py + tests/test_ingestion_engine.py
........................................................                 [100%]
56 passed in 0.64s
```

### §5.3 全套件（實貼）

```
774 passed, 3 skipped, 3 warnings in 54.61s
```

C1 後基線 771 passed → **774 passed（+3、0 failed、零回歸）**。

### §5.4 §6.2 驗收 grep（實貼）

```
--- 借用鏈退場（期望 0 命中）
grep -n "MarkdownProcessor\|JsonProcessor" pipelines/litedoc_pipeline.py
0 matches（exit=1）
--- 引擎已接線
pipelines/litedoc_pipeline.py:43:from pipelines import ingestion_engine
pipelines/litedoc_pipeline.py:211:# === [PIPE-INGEST C2 START] P1 攝入組裝切換 ingestion_engine ===
--- TilingProcessor 續用
pipelines/litedoc_pipeline.py:39:from processor.tiling_processor import TilingProcessor
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py
無命中（合規）——sidecar 異常路徑用 logger.warning(..., exc_info=True)
--- database：grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 寫入
```

---

## §6 不可動清單遵守狀態

- [x] `processor/md_processor.py`、`processor/json_processor.py` — 零改（僅 litedoc 移除自身 import）
- [x] `pipeline_core.py` 及 A 軌鏈全體 — 零改
- [x] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py` — 零改
- [x] `pipelines/section_engine.py`、`pipelines/ingestion_engine.py` — 零改
- [x] `litedoc_pipeline.py` 之 `_build_tiles` 以外 P1/P3 核心方法 — 零改（P3 譯題鏈／`_extract_translated_title`／`_detect_source_lang`／cover-prompt 全留 C3）
- [x] 母翻譯提示詞 / `pipelines/contracts.py` / `processor/rag_indexer.py` — 零改
- [x] 工具層四檔 — 零改
- [x] `settings.py` 旗標預設值 — 零改
- [x] 既有 tests 斷言本體 — 零改寫（僅移除因借用鏈退場而失效之 stub、新增測試）
- [x] 禁 constraints 鷹架 — 未向 `InjectionContext.constraints` 注入任何內容

---

## §7 銜接

- **baton 狀態**：本報告 + C1 報告 + plan v4 + tasks + design spec 均暫存 `baton/`、未 mv 未 git add（Checkout 一次性歸檔）。
- **hash 自癒**：C1 已 ship＝`e7b9e6c`；「待 baron 回填」佔位符雙源掃描＝0（上輪已清、本輪無新增）。
- **自評（正向）**：推進 plan §2.2（P1 切換）＋§2.4 body 側＋§2.5 攝入側；影子 E2E 可見效果＝meta 塊不再入內文、圖片進 tiles。**（負向防錯）**：扉頁後 meta 重複的「剝除側」與標題錯置仍在（P3 譯題鏈屬 C3）——C2 後影子輸出屬中間態、不宜單獨作最終 E2E 判定。
- **下一步**：C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）；等 baron 確認本 commit 後另行下達 C3 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C2_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST_C2_msg.txt）
cat > /tmp/PIPE-INGEST_C2_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）

1. 修改 pipelines/litedoc_pipeline.py 的 _build_tiles 攝入組裝方法，改呼叫 B 軌自有 ingestion_engine 進行 processed 相容組裝，完成 meta 欄位分離與圖片 figure content 欄位填寫，徹底使 A 軌 MarkdownProcessor 與 JsonProcessor 借用鏈在 litedoc 脫鉤退場。
2. 保持 TilingProcessor 既有分塊邏輯零改用，並利用其自癒特性補齊 blocks 的 index 與 part。
3. 更新 tests/test_litedoc_pipeline.py 斷言以匹配新攝入引擎產出，驗證文首 meta 區（epigraph/byline 等）已與內文完全分離。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST_C2_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C2 執行完成——P1 切換引擎、借用鏈退場（grep 0 命中）、774 passed 零回歸、SOP 雙核查合規
