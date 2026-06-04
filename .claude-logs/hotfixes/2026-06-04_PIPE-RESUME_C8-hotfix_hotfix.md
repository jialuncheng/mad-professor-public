# PIPE-RESUME Commit C8-hotfix — 緊急熱修復：影子論文資料庫（DB）寫入缺失修復

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正前一次 Commit 落地後立即發現的嚴重阻斷性 Bug 或 Regression。
> **修復原則**：只改動受災點程式碼，嚴禁夾帶任何無關的新功能或大型重構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **C8-hotfix** | `待 baron 回填` | fix(pipeline): upsert shadow paper to DB upon orchestrator completion |

---

## 阻斷性問題與真因

詳細記錄發生的 Regression 或 Block 問題，以及造成此問題的直接真因：

### 1. 阻斷現象 (Block Issue)
- **現象描述**：啟用影子測試上傳履歷 PDF 時，影子論文 `DeHunt_CTO_Tzung-Yuan_Lee_shadow` 完成了處理（日誌顯示 P1-P4 全綠，且最終 `rag_status=ready`），但**前端頁面完全沒有顯示任何 `(測試)` 的影子論文產出**，無法進行端到端視覺與比對測試。
- **受災範圍**：所有影子文體的影子端到端比對測試在前端全面失效。
- **首發日誌/錯誤堆疊**：
  ```
  [PIPE-RESUME P4] DeHunt_CTO_Tzung-Yuan_Lee_shadow paper_db_id 未取得（DB 寫入降級、僅 FAISS + index_meta）
  [paper_chunks] paper_db_id 未提供、跳過寫入 SQLite (可由 tools/regen_rag.py --init 事後補完)
  [rag_finished] DeHunt_CTO_Tzung-Yuan_Lee_shadow rag_status=ready
  影子論文處理完成: owner=1 DeHunt_CTO_Tzung-Yuan_Lee_shadow
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：新核心已 100% 成功跑完 P1-P4 且生成硬碟實體檔。但影子派發單元 `run_pipeline_shadow` 在 `Orchestrator().run(ctx)` 後**漏掉 `paper_manager.upsert_paper(...)` 寫庫呼叫**。影子論文紀錄從未在 SQLite 建立，前端論文列表 API 自然讀不到。
- **定位程式碼**：`web_server.py` `run_pipeline_shadow`（`Orchestrator().run(ctx)` 後僅設 `processing_tasks[...]['status']='done'`、無寫庫）。
- **grep 證據（已驗證）**：
  - `paper_manager.upsert_paper`（`paper_manager.py:205`、docstring「pipeline 完成時呼叫：upsert Paper row」）為建立 Paper row 的**唯一函式**；A 軌於 `pipeline_core.py:547` 呼叫，B 軌影子**從未呼叫**。
  - `paper_manager.list_papers`（`paper_manager.py:175`）以 `s.query(Paper).filter_by(owner_id=...)` **讀 DB** → 無 Paper row 即不顯示於前端。
  - `upsert_paper` body：建立/更新 `Paper(owner_id, paper_uuid, title, domain, doc_type, metadata_json, original_filename)` 並設 `p.status='done'`（`Paper.status` 欄位存在、`models.py`）；**`final_paths` 不入庫**（Paper 無 paths 欄），僅 `_read_title_from_rag_tree(final_paths['rag_tree'])` 用於 title 解析（缺則 `resolve_title` fallback metadata→paper_uuid）。
  - `Orchestrator.run(ctx)`（`orchestrator.py:69`）**原地改寫並回傳** ctx（`setattr(ctx, field, result)` L98 / `ctx.rag=result` L146 / `return ctx` L134）→ 影子派發於 run_in_executor 後可直接讀 `ctx.ingestion/glossary_ready/bilingual/rag`。
  - **對齊 PIPE master U10**：「影子 row 為同庫獨立 row、必須靠既有 list_papers 零改動自動帶出」——故影子完成後**本就應**呼叫 upsert_paper 建獨立 row；漏掉即本 bug。
- **架構歸屬**：受災點 `run_pipeline_shadow` 屬 **PIPE-SCAFFOLD** scaffolding 代碼；此完成期寫庫缺口在 NullStrategy 時代（P1 即崩潰、到不了結尾）被遮蔽，**由 PIPE-RESUME 成為首個真正跑完四 Phase 的策略而暴露**（「首落地隨 PIPE-RESUME」）。修法以 ctx 凍結合約欄位組裝、**doc_type-agnostic（五路通用）**。

---

## 熱修復修法 (Minimal Hotfix)

本修復採取的**最小侵入式**解決方案：

### [web_server.py](file:////Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/web_server.py) — 最小改動
在 `web_server.py` 的影子派發最後，補上對 `paper_manager.upsert_paper` 的最小調用，以將產出成果正式鏡像登記至 SQLite 資料庫：

**校正要點**（依 grep 證據）：① ctx 由 Orchestrator 原地改寫、直接讀即可（不改既有 run_in_executor 行）；② `final_paths` **不入庫**（僅 rag_tree 用於 title）→ 改用 **str 絕對路徑**（對齊 A 軌 `pipeline_core.py:547` `{k: str(v)…}`、去除 `relative_to(OUTPUT_DIR)` 的 ValueError 風險）；③ 加 `ctx.bilingual` 守衛（P3 未交付則不寫庫）；④ metadata `confidence` 用字串 `'high'`（對齊既有 metadata 結構慣例）。

```diff
@@ async def run_pipeline_shadow(...):
         await loop.run_in_executor(None, lambda: Orchestrator().run(ctx))
+
+        # === [PIPE-RESUME C8-hotfix START] ===
+        # 影子完成後鏡像登記 Paper row（list_papers 讀 DB → 前端 (測試) 列自動帶出）。
+        # ctx 由 Orchestrator 原地填入四 Phase specs；本寫庫 doc_type-agnostic（五路通用）。
+        # 與 A 軌 pipeline_core.py:547 同款 upsert_paper；final_paths 僅供 rag_tree 標題解析
+        # （Paper 無 paths 欄、不入庫），故傳 str 絕對路徑即可、不做 relative_to。
+        if ctx.bilingual is not None:
+            final_paths = {
+                'zh': str(ctx.bilingual.final_zh_path),
+                'en': str(ctx.bilingual.final_en_path),
+            }
+            if ctx.rag is not None:
+                final_paths['vector_store'] = str(ctx.rag.vectors_path)
+            meta_dict = {
+                'title': {
+                    'value': ctx.ingestion.title if ctx.ingestion else paper_id_shadow,
+                    'source': 'pipeline', 'confidence': 'high',
+                },
+                'translated_abstract': {
+                    'value': ctx.glossary_ready.translated_abstract if ctx.glossary_ready else '',
+                    'source': 'pipeline', 'confidence': 'high',
+                },
+            }
+            paper_manager.upsert_paper(
+                str(OUTPUT_DIR), owner_id, paper_id_shadow,
+                {k: v for k, v in final_paths.items() if v},
+                metadata=meta_dict,
+                domain=(ctx.glossary_ready.domain_name if ctx.glossary_ready else None),
+                doc_type=doc_type,
+                original_filename=f"{original_filename or paper_id} (測試)",
+            )
+        # === [PIPE-RESUME C8-hotfix END] ===
+
         with tasks_lock:
```

> **交易邊界（database SOP）**：`upsert_paper` 為既有落地函式、內部自管 session 與 commit（A 軌已用）；本 hotfix 僅**呼叫**它、不引入新的裸 commit / session.begin；其前置 P1-P4 已完成、寫庫不含 LLM/Embedding（極短交易、不鎖庫）。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
在開發機上執行 pytest 確保全套件不受影響：
```bash
$ venv/bin/python -m pytest tests/test_pipe_scaffold.py -v
```

### 2. 本地 E2E 快速復現與驗證
在開發機上啟動 Web Server，打開 Python 互動式環境，模擬 `run_pipeline_shadow` 完成後的 DB row：
```python
# 驗證 SQLite 中存在該影子論文紀錄，狀態 'done'、original_filename 帶 (測試)
from db import SessionLocal              # 校正：模組名為 db（非 database）
from models import Paper
with SessionLocal() as s:
    p = s.query(Paper).filter_by(paper_uuid="DeHunt_CTO_Tzung-Yuan_Lee_shadow").one_or_none()
    assert p is not None
    assert p.original_filename.endswith("(測試)")
    assert p.status == 'done'            # upsert_paper 設 p.status='done'（已驗證）
```

### 3. 前端肉眼驗收
開發機 `SHADOW_LAUNCH_ENABLED=true` 上傳履歷 PDF → 前端論文列表應同時出現「原著」與「原著 (測試)」兩列（影子 row 為同庫獨立 row、靠既有 list_papers 自動帶出，對齊 PIPE master U10）。

---

## 回退與備案

```bash
# 退回到最初安全穩定版本的 Commit (C7-hotfix)
git reset --hard a644e48
```

---

## 銜接與注意事項（驗證紀錄 + 執行期強制約束）

### 1. 驗證紀錄（grep 證據、因果確認）
- **根因確認**：`run_pipeline_shadow` 於 `Orchestrator().run(ctx)` 後僅設 `status='done'`、**無 upsert_paper**；`list_papers` 讀 DB（`query(Paper)`）→ 影子無 Paper row → 前端不顯示。亦解釋 C5 日誌 `paper_db_id 未取得（降級）`——`get_paper_db_id` 對未建 row 的影子回 None。
- **修法正確性**：`upsert_paper`（`paper_manager.py:205`）為唯一建 row 函式、A 軌 `pipeline_core.py:547` 同款呼叫；ctx 由 Orchestrator 原地改寫（`orchestrator.py:98/146/134`）→ specs 可讀；對齊 PIPE master U10「影子 row 同庫獨立、list_papers 自動帶出」。
- **與提案差異（已校正）**：① `final_paths` 不入庫（Paper 無 paths 欄、僅 rag_tree 解析 title）→ 去 `relative_to(OUTPUT_DIR)` 改 str 絕對路徑（對齊 A 軌、避 ValueError）；② 加 `ctx.bilingual` 守衛；③ E2E `from database`→`from db`；④ confidence `1.0`→`'high'`。

### 2. doc_type-agnostic（五路通用、非 resume 專屬）
本寫庫以 ctx 凍結合約欄位（`bilingual`/`ingestion`/`glossary_ready`/`rag`）組裝，**不依賴 resume 特性** → 後續 PIPE-VISUAL/ACADEMIC/LITEDOC/BOOK 任一路跑完影子皆自動受惠、無須重複修。屬 PIPE-SCAFFOLD 影子完成期的通用寫庫補強（由 PIPE-RESUME 首落地暴露）。

### 3. BE-Hotfix 執行期強制約束（.bak + SOP 核查）
本 hotfix 改 `web_server.py`（`.py` 業務代碼）→ **BE-Hotfix** 工作流，落地執行期須：
- **`.bak` 備份鐵律**：`cp web_server.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C8-hotfix_web_server.py.bak`，並於 `git add` 清單強制包含此 `.bak`（WORKFLOW_SOP §3）。
- **SOP 一致性核查**（落地前貼 grep 結果）：
  ```bash
  grep -nE "logger\.error|logger\.exception|traceback.format_exc" web_server.py   # 既有 IP 行；本 hotfix 區塊不新增 → 標「本次新增區塊無命中（合規）」
  grep -nE "\.commit\(\)" web_server.py | grep -v "with .*session.*begin\(\)"     # 本 hotfix 不新增裸 commit（upsert_paper 內部自管交易、屬既有）
  ```
  本 hotfix 僅**呼叫** `upsert_paper`（既有安全函式）、無新 logger/裸 commit/session.begin → 兩項核查對「本次新增區塊」必為空命中（合規）。
- **註解包裹**：修改區塊以 `# === [PIPE-RESUME C8-hotfix START/END] ===` 包裹（見「熱修復修法」）。
- **A 軌零影響**：本 hotfix 僅動 `run_pipeline_shadow`（B 軌影子單元）；A 軌 `run_pipeline` 本體 byte 不動、線上 0 風險。

### 4. 結論
hotfix **對症、修法正確（校正後）、grep 證據完備**。baron 套用後，開發機影子 resume pipeline 完成將鏡像登記 Paper row（`status='done'`、`original_filename` 帶 (測試)），前端論文列表即同步顯示「原著 (測試)」列，端到端比對測試可進行。
