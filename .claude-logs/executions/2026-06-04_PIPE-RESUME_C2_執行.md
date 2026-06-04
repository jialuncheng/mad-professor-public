# PIPE-RESUME C2 — P1 Ingestion 執行報告

---

**任務代號**：PIPE-RESUME C2
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C2
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C1（`f3d4e41`）已落地——`pipelines/resume_pipeline.py` 骨架（四方法 stub）。`PipelineContext` 僅含 doc_type/paper_id/shadow 等，**無 pdf_path/owner_id**，策略無法定位輸入 PDF。
- **完成狀態**：實作 `run_phase1`（P1 Ingestion）——**全鏈編排**既有 processor（`ResumeProcessor` Vision + Metadata Stage A + `DocAnalyzer` 雙保險 + `MarkdownProcessor`/`JsonProcessor`/`TilingProcessor`）產出 `IngestionMetadataSpec`（title / source_lang / 物理分組 Tiles；零 Abstract/LCC/Glossary）。`phone`/`email`/`domain` 暫存 `self._raw_meta` interim 穿線。**經 baron 拍板**擴充共用基建 `PipelineContext`（加 `pdf_path`/`owner_id` 欄）+ PIPE-SCAFFOLD 影子派發點（`web_server.py:612`）同步傳入。複用既有 processor **零改動**；全套件 465 passed。

> **本 C2 兩項 baron 拍板擴充**（原 tasks §7 鎖定 context/web_server，經 baron 明確解鎖）：
> 1. **路徑輸入機制**：`PipelineContext` 加 `pdf_path`/`owner_id`（落地 PipelineContext 無此欄、影子接線未傳；首落地隨 PIPE-RESUME、五路共用）。
> 2. **P1 範圍**：全鏈編排（忠實 PIPE-SPEC §1.1①「Tiles 在 P1 產出」）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | `run_phase1` 全鏈 P1 Ingestion（ResumeProcessor + Stage A + analyze + md2json/json_process/tiling → IngestionMetadataSpec）+ `PipelineContext` 加 pdf_path/owner_id + web_server 影子派發傳值 | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C2_resume_pipeline.py.bak` | 實作 run_phase1 全鏈編排 + 7 個 P1 私有輔助；新增 C2 imports + 常數 |
| 修改 | `pipelines/context.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C2_context.py.bak` | `PipelineContext` 加 `pdf_path: Optional[str]=None` / `owner_id: Optional[int]=None`（C2 標記） |
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C2_web_server.py.bak` | 影子派發 `run_pipeline_shadow`（L612）`PipelineContext(...)` 補傳 `pdf_path`/`owner_id`（C2 標記） |

> ⚠️ 三個 `.bak` 必須在 C2 `git add` 清單中（§8）。`baton/` 暫存報告不入 Git。

---

## §4 修法說明

### §4.1 `pipelines/context.py` — 加策略輸入源欄位
`# === [PIPE-RESUME C2 START/END] ===` 包裹，於調度元欄位區追加：
```python
pdf_path: Optional[str] = None   # 輸入 PDF 路徑（派發點寫入）
owner_id: Optional[int] = None   # per-owner 輸出目錄隔離
```
預設 None → 既有 PIPE-CORE/SCAFFOLD 測試與骨架調用前向相容（25 pipelines 測試綠）。

### §4.2 `web_server.py` — 影子派發傳值
`run_pipeline_shadow`（L612 區）`# === [PIPE-RESUME C2 START/END] ===` 包裹：
```python
ctx = PipelineContext(
    doc_type=doc_type, paper_id=paper_id_shadow, shadow=True,
    pdf_path=str(pdf_path), owner_id=owner_id,
)
```
影子與 A 軌共用同一實體 PDF；輸出目錄靠 `paper_id_shadow`（`_shadow` 後綴）物理隔離。

### §4.3 `pipelines/resume_pipeline.py` — run_phase1 全鏈編排
`# === [PIPE-RESUME C2 START/END] ===` 包裹（imports / 常數 / run_phase1 / 7 輔助）：
```python
def run_phase1(self, ctx):
    pdf_path = Path(ctx.pdf_path)                       # 缺則 ValueError / 不存在 FileNotFoundError
    output_dir = paper_manager.paper_dir(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
    meta = self._extract_metadata(pdf_path)             # ① Stage A（soft-fail）
    md_path = Path(ResumeProcessor().parse(str(pdf_path), str(output_dir)))  # ② Vision
    DocAnalyzer().analyze(md_path, "resume")            # ③ 雙保險（soft-fail）
    tiles = self._build_tiles(md_path, output_dir, paper_name)  # ④⑤⑥ md2json→json_process→tiling
    title = self._resolve_title(meta, markdown_text, paper_name)       # candidate_name→#行→title→stem
    source_lang = self._detect_source_lang(markdown_text)              # CJK 啟發式 zh/en
    phone, email = self._extract_contact(markdown_text)                # markdown regex
    self._raw_meta = {"phone": phone, "email": email, "domain": ...}   # interim 穿線
    return IngestionMetadataSpec(title=title, source_lang=source_lang, tiles=tiles, ...)
```
**設計決策（grep 證據驅動）**：
- **Tiles**：`tiling` 輸出 `_tiled.json` 結構 `{"sections":[...]}`（`translate_processor.py:111` 消費 `data["sections"]`）→ tiles = sections list。
- **source_lang**：codebase 無落地偵測器（唯一用法 `translate_processor.py:247 getattr(self,'source_lang','en')`）→ C2 以 CJK 佔比啟發式（保留原語言哲學）。
- **phone/email**：`metadata_extractor._ALL_FIELDS` 無此二欄 → C2 以 markdown regex 自足抽取（**不動既有檔**）。
- **processor 複用**：全部無參建構、file-in/file-out 自足（對照 `pipeline_core.py:98-110` available_stages + `:604-693` 各 _stage 方法），零改動。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/context.py
 M pipelines/resume_pipeline.py
 M web_server.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_context.py.bak
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_resume_pipeline.py.bak
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_web_server.py.bak
# （.claude-logs/baton/、prompts/、TODO.md 文件改動另計）
```

### §5.2 驗收輸出
import + 註冊 + context 新欄位 + 缺 pdf 防護：
```
strategy= ResumePipeline rag_thr= 3
ctx.pdf_path= /x/y.pdf ctx.owner_id= 7
no-pdf -> ValueError OK
```
語法檢查：`web_server.py 語法 OK` / `context.py 語法 OK`。

pipelines 既有測試（防 context/web_server Regression）：
```
25 passed in 0.65s
```

全套件：
```
1 failed, 465 passed, 3 skipped in 149.12s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C2 Regression）
```

> 註：`tests/test_resume_pipeline.py`（P1-P4 契約測試）屬 **C6**、本 C2 尚未建檔；§6.2 的 pytest 斷言於 C6 落地。C2 以 import/註冊/grep/全套件防 Regression 驗收。

### §5.3 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**：`pipelines/resume_pipeline.py` 3 處 `logger.warning(..., exc_info=True)`（L130/173/197 analyze/Stage A/tiles soft-fail），**皆含 exc_info=True**；無裸 `logger.error`、無 `traceback.format_exc`（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/resume_pipeline.py pipelines/context.py`）：無命中（合規）——C2 無任何 DB 寫入/交易。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py`（A 軌 resume branch 保留） | [x] ✅ 未觸碰 |
| `processor/resume_processor.py` / `rag_processor.py` / `metadata_extractor.py` / `doc_analyzer.py` / `md_processor.py` / `json_processor.py` / `tiling_processor.py` | [x] ✅ 僅**呼叫**、零改動 |
| `pipelines/contracts.py`（不擴 custom_metadata） | [x] ✅ 未變更（phone/email/domain 走 _raw_meta interim） |
| `pipelines/base_strategy.py` / `factory.py` / `orchestrator.py` | [x] ✅ 僅繼承/註冊、未改本體 |
| `pipelines/context.py` | [⚠] **baron 拍板擴充**（加 pdf_path/owner_id；原 §7 鎖定經 baron 明確解鎖） |
| `web_server.py` | [⚠] **baron 拍板擴充**（影子派發 L612 傳值；A 軌 run_pipeline 本體未動） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端 | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

> §7 對 context/web_server 的鎖定經 baron 於本 C2 明確解鎖（AskUserQuestion 拍板「本 C2 一併擴 context.py」）；A 軌 `run_pipeline` 本體 byte 不動、旗標未動、線上 0 風險。

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `baton/`、不入版控，待 C7 收官 `mv`+`git add` 歸檔至 `executions/`。
- **下一步**：tasks.md C3 — P2 Glossary & Context Prep（四步循序自癒）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。
- **附帶（歷史 Hash 自癒）**：C1 已提交 `f3d4e41` → TODO active 列 C1 佔位符已回填。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 三個 .bak）

# 2. git add 清單（C2 程式碼 + 三 .bak；baton/ 報告嚴禁加入）
git add pipelines/resume_pipeline.py
git add pipelines/context.py
git add web_server.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_context.py.bak
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_web_server.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C2_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C2 — P1 Ingestion（Vision 整份解析與元數據）

實作 ResumePipeline.run_phase1：全鏈編排 ResumeProcessor（Vision 整份解析+去浮水印）
+ Metadata Stage A + doc_analyzer 雙保險 + md2json/json_process/tiling（產物理分組
Tiles），交付 IngestionMetadataSpec（title=candidate_name / source_lang 啟發式 / tiles；
零 Abstract/LCC/Glossary）；phone/email/domain 暫存 self._raw_meta interim 穿線。
擴 PipelineContext 加 pdf_path/owner_id 欄（首落地隨 PIPE-RESUME、五路共用），
web_server 影子派發點 (612) 同步傳入。複用既有 processor 零改動、全套件 465 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C2 的代碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C2 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C2 執行完畢——run_phase1 全鏈 P1 Ingestion + PipelineContext 擴 pdf_path/owner_id（baron 拍板）+ web_server 影子派發傳值；全套件 465 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。兩項 baron AskUserQuestion 拍板：路徑輸入機制（擴 context.py）+ P1 全鏈編排（忠實 PIPE-SPEC）。
