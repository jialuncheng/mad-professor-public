# PIPE-SECTION-BASE C3 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 16:37 |
| 任務代號 | PIPE-SECTION-BASE C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C3_執行.md` |
| 觸發情境 | baron 驗收 C2 報告後、下達 C3 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C3（rag 旁路 + meta header 純格式化器·U3.1 Zero Schema Coupling）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / **plan（全局策略 z·U1 re-inject）** / tasks（§8 C3）/ database SOP / logging SOP
- 三防線：物理（§7 不可動）/ 測試（§6.3 grep + pytest 行為等價）/ 文件（不自發 commit）
- 包裹：`# === [PIPE-SECTION-BASE C3 START/END] ===`
- 備份：`cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C3_resume_pipeline.py.bak`
- 實作（tasks §8 C3）：① `_collect_rag_sections`/`_single_container_sections` 原值搬入 section_engine（summary_key=原文標題 path 保留）② `_render_meta_header` **重構為純格式化器** U3.1：engine 新增 `render_meta_header(title, items: List[Tuple[str,str]], sep="：")`、**僅產 `# 標題`+無序列表、零讀 raw_metadata/ctx**;resume 呼叫端先從 ctx.raw_metadata 抽 domain/org/phone/email + lang label 對照 → 組 (Label,Value) → 呼 engine;輸出 byte 等價（label/順序/缺項規則照舊）③ resume delegate
- 驗收：§6.3 grep（`grep raw_metadata section_engine.py`=0）+ `pytest tests/test_resume_pipeline.py` 全綠 + §6.6 SOP
- TODO：C3 ✅ / C4 🟡 WIP + hash 自癒
- 產出：`baton/..._C3_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 動業務代碼僅 `section_engine.py` + `resume_pipeline.py`（plan/tasks 明指、CLAUDE.md §3 例外）。
