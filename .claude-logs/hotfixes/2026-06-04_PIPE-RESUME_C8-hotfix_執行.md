# PIPE-RESUME C8-hotfix — 影子論文 DB 寫入缺失修復 執行報告

---

**任務代號**：PIPE-RESUME C8-hotfix
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C8-hotfix_hotfix.md`（hotfix 規劃、校正版）
**次級參考**：`pipeline_core.py:547` A 軌 upsert_paper 同款呼叫；PIPE master U10 影子 row 設計
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C8-hotfix)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C7-hotfix（`d2e0af2`）後，開發機影子上傳履歷 → 影子 P1-P4 全綠、生成實體檔（`final_*_zh/en.md` + vectors）、`rag_status=ready`，但前端論文列表**不顯示 (測試) 列**（影子 Paper row 未建、`list_papers` 讀 DB 撈不到）。
- **完成狀態**：BE-Hotfix——`web_server.py` `run_pipeline_shadow` 於 `Orchestrator().run(ctx)` 後、`status='done'` 前補 `paper_manager.upsert_paper(...)` 寫 Paper row。採**校正版**（依規劃文件 + baron 前輪確認）：str 絕對路徑（去 `relative_to` ValueError 風險）+ `ctx.bilingual` 守衛 + `confidence='high'`，以 `# === [PIPE-RESUME C8-hotfix START/END] ===` 包裹。**doc_type-agnostic（以 ctx 凍結合約欄位組裝、五路通用）**；A 軌 `run_pipeline` 本體 byte 不動。test_pipe_scaffold 5 passed、全套件 480 passed。

> **執行差異透明標註**：本 Run 提示詞 §2 貼出的是**校正前舊版** diff（`relative_to(OUTPUT_DIR)` / `confidence:1.0` / 無 `ctx.bilingual` 守衛）；但提示詞要求「依 C8-hotfix_hotfix.md」、baron 於前兩輪已確認**校正版**（str 絕對路徑 / 守衛 / `'high'` / `from db`）。據此以**規劃文件校正版**落地。兩版功能皆可運作，校正版更安全（避 relative_to 風險 + 守衛）且 final_paths 不入庫（grep 證實 Paper 無 paths 欄）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C8-hotfix | `web_server.py` `run_pipeline_shadow` 補 `paper_manager.upsert_paper` 寫影子 Paper row（修復前端不顯示） | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak` | `run_pipeline_shadow` 尾端補 upsert_paper（C8-hotfix 標記包裹）；A 軌與既有派發 byte 不動 |

> ⚠️ `.bak` 須在 C8-hotfix `git add` 清單中（§8）。`baton/` 暫存報告於 hotfix 移出鐵律下移至 `hotfixes/`。

---

## §4 修法說明

### §4.1 `web_server.py` — `run_pipeline_shadow` 補影子 Paper row 寫入
`# === [PIPE-RESUME C8-hotfix START/END] ===` 包裹，於 `Orchestrator().run(ctx)` 後：
```python
if ctx.bilingual is not None:                 # 守衛：P3 已交付才寫庫
    final_paths = {'zh': str(ctx.bilingual.final_zh_path),
                   'en': str(ctx.bilingual.final_en_path)}
    if ctx.rag is not None:
        final_paths['vector_store'] = str(ctx.rag.vectors_path)
    meta_dict = {
        'title': {'value': ctx.ingestion.title if ctx.ingestion else paper_id_shadow,
                  'source': 'pipeline', 'confidence': 'high'},
        'translated_abstract': {'value': ctx.glossary_ready.translated_abstract
                  if ctx.glossary_ready else '', 'source': 'pipeline', 'confidence': 'high'},
    }
    paper_manager.upsert_paper(
        str(OUTPUT_DIR), owner_id, paper_id_shadow,
        {k: v for k, v in final_paths.items() if v},
        metadata=meta_dict,
        domain=(ctx.glossary_ready.domain_name if ctx.glossary_ready else None),
        doc_type=doc_type,
        original_filename=f"{original_filename or paper_id} (測試)")
```

**真因（grep 證據）**：`run_pipeline_shadow` 於 `Orchestrator().run(ctx)` 後僅設 `status='done'`、**無 upsert_paper**；`upsert_paper`（`paper_manager.py:205`）為建 Paper row 唯一函式（A 軌 `pipeline_core.py:547` 呼叫）；`list_papers`（`paper_manager.py:175`）`query(Paper).filter_by(owner_id)` 讀 DB → 影子無 row → 前端不顯示。此完成期寫庫缺口在 NullStrategy 時代被遮蔽、由 PIPE-RESUME 首個跑完四 Phase 暴露。

**設計要點**：
- **ctx 原地改寫**：`Orchestrator.run`（`orchestrator.py:98/146/134`）原地填 ctx specs → 直接讀 `ctx.bilingual/ingestion/glossary_ready/rag`，不改既有 run_in_executor 行。
- **final_paths 不入庫**：grep 確認 `upsert_paper` 不存 final_paths（Paper 無 paths 欄）、僅 `_read_title_from_rag_tree` 用；故傳 str 絕對路徑即可、**不做 `relative_to`**（避 ValueError）。
- **doc_type-agnostic**：以凍結合約欄位組裝、不依賴 resume 特性 → 五路通用。
- **A 軌零影響**：僅動 `run_pipeline_shadow`（B 軌影子單元）。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M web_server.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak
# （.claude-logs/baton→hotfixes/ 移出 + prompts/ + TODO.md 改動另計）
```

### §5.2 語法 + 單元測試
```bash
$ venv/bin/python -c "import ast; ast.parse(open('web_server.py').read()); print('OK')"
web_server.py 語法 OK

$ venv/bin/python -m pytest tests/test_pipe_scaffold.py -q
5 passed in 0.69s

$ venv/bin/python -m pytest tests/ -q
1 failed, 480 passed, 3 skipped in 40.14s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C8-hotfix Regression）
```

### §5.3 E2E DB 行驗證（baron 端開發機影子上傳後執行）
```python
from db import SessionLocal          # 模組名為 db（非 database）
from models import Paper
with SessionLocal() as s:
    p = s.query(Paper).filter_by(paper_uuid="DeHunt_CTO_Tzung-Yuan_Lee_shadow").one_or_none()
    assert p is not None
    assert p.original_filename.endswith("(測試)")
    assert p.status == 'done'
```
> 前端肉眼：列表同時出現「原著」與「原著 (測試)」兩列（影子 row 同庫獨立、list_papers 自動帶出、對齊 PIPE master U10）。實打影子上傳屬 baron 端開發機驗證。

### §5.4 SOP 一致性核查（BE-Hotfix 強制）
- **logging 檢測**（C8-hotfix 新增區塊）：無 `logger.error`/`traceback.format_exc`（合規；本區塊無新 logger 呼叫）。
- **database 檢測**（C8-hotfix 新增區塊）：無裸 `.commit()`/`session.begin()`（合規）。本 hotfix 僅**呼叫**既有 `upsert_paper`（其內部自管 session+commit、A 軌已用、屬既有）；寫庫不含 LLM/Embedding（前置 P1-P4 已完成、極短交易不鎖庫）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| A 軌 `run_pipeline`（web_server.py）本體 | [x] ✅ byte 不動 |
| `pipeline_core.py` / `paper_manager.py` / 既有 processors | [x] ✅ 未觸碰（僅呼叫 upsert_paper）|
| `pipelines/*`（resume_pipeline / orchestrator / contracts / 等） | [x] ✅ 未變更（僅讀 ctx specs）|
| `models.py` / `db.py` | [x] ✅ 未觸碰（DB 寫入委派 upsert_paper）|
| `web_server.py` | [⚠] **本 hotfix 受災點**：僅 `run_pipeline_shadow` 尾端加 upsert_paper 區塊（C8-hotfix 標記）；既有派發/A 軌 byte 不動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態（Hotfix 移出鐵律）**：本執行報告與 hotfix 規劃檔（`C8-hotfix_hotfix.md`）於通過驗證後一次性 `mv` 移出 `baton/` → `hotfixes/` + `git add`（見 §8）。
- **下一步**：待 baron 手動 commit 本 hotfix 並 push 同步至測試機，驗證影子 resume pipeline 完成後前端列出「原著 (測試)」列；**嚴禁自發續跑後續 Check**。
- **消化歸檔之 baton 檔**：`C8-hotfix_hotfix.md` + `C8-hotfix_執行.md` → `hotfixes/`。
- **doc_type-agnostic 紅利**：後續四路（VISUAL/ACADEMIC/LITEDOC/BOOK）跑完影子皆自動受惠、無須重複修（屬 PIPE-SCAFFOLD 影子完成期通用寫庫補強）。
- **回退方式（Rollback）**：`git revert <C8-hotfix hash>`；或 `cp .claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak web_server.py`。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單
git add web_server.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-06-04_PIPE-RESUME_C8-hotfix_hotfix.md
git add .claude-logs/hotfixes/2026-06-04_PIPE-RESUME_C8-hotfix_執行.md
git add .claude-logs/prompts/

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C8-hotfix_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C8-hotfix_msg.txt
```

### §8.2 commit message 草稿

（草稿已寫入 `/tmp/PIPE-RESUME_C8-hotfix_msg.txt`）

```
BE-Hotfix: PIPE-RESUME C8-hotfix — 影子論文資料庫（DB）寫入缺失修復

修復影子派發單元 run_pipeline_shadow 於完成 Orchestrator 呼叫後，
漏掉調用 paper_manager.upsert_paper(...) 導致影子論文未註冊至 SQLite、前端無法列出的 Bug。
在 web_server.py 影子派發尾端補上 upsert_paper 呼叫（校正版：str 絕對路徑 + ctx.bilingual 守衛
+ confidence='high'，doc_type-agnostic 五路通用），並以 [C8-hotfix] 註解包裹。
upsert_paper 為既有安全函式、A 軌零影響；test_pipe_scaffold 5 passed、全套件 480 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C8-hotfix 影子 DB 寫入缺失修復與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/ → 通過驗證後移出 hotfixes/ 入版控 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | hotfixes/ 歸檔 / Antigravity 驗證 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；BE-Hotfix 最小侵入、A 軌零影響 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 hotfixes/，不刪除 |
| **重複防護** | 本檔為 C8-hotfix 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C8-hotfix 執行完畢——`web_server.py` `run_pipeline_shadow` 補 `paper_manager.upsert_paper` 寫影子 Paper row，修復影子完成期 DB 寫入缺失致前端不顯示 (測試) 列。採規劃文件校正版（str 絕對路徑/ctx.bilingual 守衛/'high'、doc_type-agnostic）；Run 提示詞 §2 為校正前舊版、已透明標註以校正版落地。test_pipe_scaffold 5 passed、全套件 480 passed（唯一 failed 為既存環境性、非 Regression）。A 軌零影響、最小侵入。
