# GOLDEN-BASELINE OP-1 — 五路黃金基準物理存盤 執行報告

---

**任務代號**：GOLDEN-BASELINE OP-1
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` §8 OP-1
**Git commit hash**：留空，由 baron 回填
**狀態**：⚠️ **Partially Completed** — 工具代碼完成且單元驗證；物理 `capture --all` 待 baron 端 MinerU 在線執行

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：工作區在 `a5b193f`（RAG-14-HOTFIX-1）之後；無 `tools/golden_baseline.py`、無 `tests/golden_baseline/` 結構。
- **完成狀態（誠實分割）**：
  - ✅ **已完成（worktree 可驗證）**：新建旁路 CLI `tools/golden_baseline.py`（`capture` 子命令，唯讀調用舊單體 + 三維度收集 + SHA-256 manifest + 防覆寫閘）；新建固定 query set `tests/golden_baseline/queries.json`（五路、凍結）；baron 已置入五路 fixtures PDF。靜態與單元層驗收全綠（見 §5）。
  - ❌ **未完成（環境阻擋）**：`capture --all` **物理存盤五路黃金快照未執行**。worktree **MinerU 服務離線**（`localhost:8000` not reachable、無 `MINERU_HOST`），舊單體 11-stage 第一站 `pdf2md` 即無法完成（實測 `capture resume` 跑 90s 仍卡死被 SIGTERM 終止）。故 `tests/golden_baseline/golden/<doc_type>/` 五組 D1/D2/D3 + manifest **尚未產生**，§6 測試門檻（五路齊全）**無法在此滿足**。
  - **業務代碼零改動**：`pipeline_core.py` / `rag_retriever.py` / `web_server.py` / `models.py` / `processor/*` 全程只讀，未改一行。

> ⚠️ **為何不標 ✅ done**：OP-1 的核心交付是「物理存盤五路黃金基準」，此步未實際執行（MinerU 離線）。若標 done 即為造假。本報告誠實標 Partially Completed，物理存盤交接 baron 端（§7）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | 新建 `tools/golden_baseline.py` capture 子命令 + `tests/golden_baseline/queries.json` 固定 query set（工具代碼完成、物理存盤待 MinerU） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `tools/golden_baseline.py` | — | 黃金基準工具，OP-1 實作 `capture` 子命令（diff 屬 OP-2） |
| 新建 | `tests/golden_baseline/queries.json` | — | D3 固定 query set（五路、凍結；plan v2 §2 U2 D3） |
| 既有（baron 置入） | `tests/golden_baseline/fixtures/{academic,book,slides,resume,litedoc}.pdf` | — | 五路代表性 PDF（plan v2 §2 U1）；體積 286K–1.2M，入版控與否見 §7 Git LFS 待議 |
| 新建 | `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md` | — | OP-1 提示詞歸檔 |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 登記 OP-1 提示詞 + 時間排序 |
| 修改 | `.claude-logs/TODO.md` | — | OP-1 狀態 🟡 WIP（代碼完成/物理存盤待 MinerU）+ Hash 自癒回填 a5b193f / ebf1b9c |
| 新建（暫存 baton/） | `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md` | — | 本報告（gitignored，OP-3 收官才歸檔） |

> 本 Commit 為 100% 新增工具與測試資產、零既有 Python 業務代碼改動，故**跳過 .bak 備份（合規）**。

---

## §4 修法說明

### §4.1 `tools/golden_baseline.py` — 黃金基準 capture 工具
依 plan v2 §2.5.1 capture 流程實作，核心設計：
- **唯讀調用舊單體**（`_run_old_monolith`）：對齊 `web_server.run_pipeline` L503-508 調用模式 `PipelineCore().process(pdf, work_dir, owner_id=哨兵, existing_paths={'_confirmed_doc_type': dt}, paper_id="golden_<dt>", original_filename=...)`，**不傳 on_progress、不改其本體**。以哨兵 `owner_id=900001` 隔離、產物落隔離工作區 `tests/golden_baseline/_capture_work/`，不污染業務 `output/`。
- **三維度收集**：D1 讀 `final_*_zh/en.md`、D2 讀 `final_*_rag_tree.json`、D3（`_collect_d3_recall`）對固定 query set 逐條呼叫既有 `RagRetriever.retrieve_with_context`（唯讀取結構化字串）+ 唯讀 `similarity_search_with_score` 取 chunk content SHA-256 + score（供 OP-2 Jaccard）。**未改 `retrieve_with_context` 簽名與演算法**（plan v2 §4）。
- **防覆寫閘**：`golden/<dt>/` 已存在且無 `--force` → 拋 `FileExistsError` ABORT（**在跑舊單體之前**檢查，零浪費）。
- **SHA-256 manifest**：凍結 4 檔（D1_zh/D1_en/D2_rag_tree/D3_recall）逐檔 SHA-256 寫 `manifest.json`（plan v2 §2 U2 防竄改）。
- **logging SOP 遵守**：模組級 `logger = logging.getLogger(__name__)`（鐵律二）；`__main__` 呼叫 `setup_logging()`（鐵律一）；失敗用 `logger.error(..., exc_info=True)`。

```python
# 防覆寫閘（在跑舊單體前）
dest = _GOLDEN_DIR / doc_type
if dest.exists() and not force:
    raise FileExistsError(f"黃金快照已存在、防覆寫 ABORT: {dest} ...")
```

### §4.2 `tests/golden_baseline/queries.json` — D3 固定 query set
五路各 3–4 條代表性 query（academic 4 / book 3 / slides 3 / resume 4 / litedoc 3），凍結為 D3 召回黃金基準輸入。檔頭 `_comment` 註明「一經凍結即不可變更（須走 plan §0 + baron 核准 + 重新存盤）」。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s tools/ tests/golden_baseline/
?? tests/golden_baseline/
?? tools/golden_baseline.py
# baton/ 報告 gitignored（.gitignore:186 .claude-logs/baton/*），未列入（合規）
```

### §5.2 單元 / 靜態核查結果（worktree 可驗證部分、全綠）
```bash
$ ./venv/bin/python -m py_compile tools/golden_baseline.py
compile OK

$ ./venv/bin/python tools/golden_baseline.py capture --help
usage: golden_baseline capture [-h] [--all] [--force] [doc_type]   # argparse OK

$ ./venv/bin/python tools/golden_baseline.py capture            # 無參數防呆
golden_baseline: error: capture 需指定 <doc_type> 或 --all

$ ./venv/bin/python -c "...; print(len(g._load_queries('academic')), g.DOC_TYPES)"
4 ['academic', 'book', 'slides', 'resume', 'litedoc']           # query set 載入 OK

# 防覆寫閘（造假快照、不加 --force）→ 正確 ABORT，且未觸 MinerU：
$ ./venv/bin/python tools/golden_baseline.py capture academic
{"level":"WARNING","logger":"__main__","message":"[golden capture] academic ABORT: 黃金快照已存在、防覆寫 ABORT: .../golden/academic ..."}
# ↑ JSON 單行格式 = setup_logging() 生效，logging SOP 合規
```

### §5.3 物理 capture 實測（誠實記錄失敗）
```bash
$ timeout 90 ./venv/bin/python tools/golden_baseline.py capture resume
Terminated   # 90s 仍卡死（MinerU 離線、pdf2md 無法完成）；exit 143 SIGTERM
# → 五路 golden/ 與 manifest 未產生，§6 五路齊全門檻無法在此滿足
```
環境實測證據：
| 前置條件 | 狀態 |
|---|---|
| 五路 fixtures PDF | ✅ 已備（baron 置入） |
| `.env` / Gemini SDK | ✅ 已備 |
| **MinerU 服務** | ❌ **離線**（`localhost:8000` not reachable、無 `MINERU_HOST`） |

### §5.4 SOP 一致性核查（BE-Refactor 強制）
本檔為**新增旁路 CLI 工具**，未改既有 `.py` 業務代碼；新工具自身核查：
- **logging 檢測**（`grep -nE "traceback.format_exc|logger.error|logger.exception" tools/golden_baseline.py`）：`logger.error(..., exc_info=True)` 1 處（含 exc_info=True，合規）；無 `traceback.format_exc` 手動拼接（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)" tools/golden_baseline.py`）：無命中（合規）——本工具零 DB 寫入，資料全落檔案系統。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 11-stage 與 `_get_stage_output_path` | [x] ✅ 未觸碰（只唯讀調用 `process`） |
| `rag_retriever.py` `retrieve_with_context` 簽名與演算法 | [x] ✅ 未變更（只呼叫取結果） |
| `delete_paper` / `list_papers` / `get_paper` API | [x] ✅ 未觸碰 |
| `models.py` 既有 Schema | [x] ✅ 未變更（零 DB Schema 改動） |
| `web_server.py` 業務代碼 | [x] ✅ 未觸碰（旁路 CLI、無 runtime hook） |
| 主 repo 目錄（worktree 父目錄） | [x] ✅ 未讀寫 |
| 已凍結 `golden/`（本次未產生、無覆寫風險） | [x] ✅ 防覆寫閘已就位 |

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`（gitignored），待 OP-3 收官以 `mv` + `git add` 歸檔至 `executions/`，**OP-1 階段嚴禁移動**。
- **OP-1 物理存盤交接 SOP（baron 端 MinerU 機器）**：
  1. 確認 MinerU 服務在線（`curl localhost:8000` 或設妥 `MINERU_HOST`）+ `.env` Gemini key + venv 依賴齊全。
  2. 執行 `python tools/golden_baseline.py capture --all`。
  3. 驗收 §6.1（tasks）：`ls tests/golden_baseline/golden/<doc_type>/` 五組 D1/D2/D3 + `manifest.json` 齊全；無 `--force` 重跑須 ABORT。
  4. 存盤完成後回填本報告 §5.3 真實輸出、TODO.md OP-1 → ✅。
- **下一步**：OP-1 物理存盤完成後 → tasks.md §8 OP-2（自動化 Regression Diff 比對腳本）。
- **消化歸檔之 baton 檔**：無（本任務首份 OP 報告）。

---

## §8 baron 執行命令

> ⚠️ **重要修正（誠實揭露）**：原 OP-1 提示詞 §8 的 commit message 草稿宣稱「凍結五路 PDF…唯讀呼叫舊體完整 11-stage 物理存盤 D1/D2/D3」——此描述**與實際不符**（capture 未執行、MinerU 離線）。下方 commit message 已改寫為**僅反映實際交付**（工具代碼 + 固定 query set），不宣稱未發生的物理存盤。

> ⚠️ **Git LFS 待議（plan v2 §7 Q1）**：`git add tests/golden_baseline/` 會納入五路 fixtures PDF（286K–1.2M，合計約 3.5M）。是否入 Git 版控或改 Git LFS **待 baron 拍板**；下方暫納入，baron 可改用 LFS 或先排除 PDF 僅追工具。

```bash
# 1. 備份檔案已完成（無修改既有檔案，跳過）
# 2. git add 清單（嚴禁包含 baton/ 下的執行報告！）
git add tools/golden_baseline.py
git add tests/golden_baseline/queries.json
git add tests/golden_baseline/fixtures/      # ← 體積大、Git LFS 待 baron 決定
git add .claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
# 3. commit message 草稿（已寫入 /tmp/GOLDEN-BASELINE_OP-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/GOLDEN-BASELINE_OP-1_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: GOLDEN-BASELINE OP-1 — 黃金基準 capture 工具與固定 query set

1. 新建旁路 CLI 工具 tools/golden_baseline.py，實作 capture 子命令：
   唯讀調用舊單體 PipelineCore 11-stage、收集 D1/D2/D3、SHA-256 manifest、防覆寫閘。
2. 新建 tests/golden_baseline/queries.json 五路固定 query set（D3 召回基準、凍結）。
3. 置入五路代表性 fixtures PDF（academic/book/slides/resume/litedoc）。
4. 工具代碼完成並通過靜態/單元/防覆寫閘驗證；物理 capture --all 五路存盤
   待 baron 端 MinerU 在線執行（worktree MinerU 離線、無法當場存盤）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 GOLDEN-BASELINE OP-1 的工具實作與驗收結果（含 MinerU 離線阻擋物理存盤之誠實揭露），作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；OP-3 收官 Conformance 核對後 `mv` 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | OP-3 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、OP-3 前不入版控；嚴禁宣稱未實際執行之物理存盤 |
| **改版觸發條件** | baron 端物理存盤完成後回填 §5.3 / 執行報告修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-1 執行唯一源，不重複 tasks 實作細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-1 執行——`tools/golden_baseline.py` capture 工具 + `queries.json` 固定 query set 代碼完成並通過 py_compile / CLI / argparse / query 載入 / 防覆寫閘（JSON logging）單元驗證；**誠實記錄** worktree MinerU 離線致 `capture --all` 物理存盤五路黃金快照未執行（實測 `capture resume` 90s SIGTERM）、§6 五路齊全門檻無法在此滿足、物理存盤交接 baron 端 MinerU 機器（§7 SOP）；TODO OP-1 標 🟡 WIP（代碼完成/物理存盤待 MinerU），同步 Hash 自癒回填 a5b193f（RAG-14-HOTFIX-1）/ ebf1b9c（RAG-14 Check）。
