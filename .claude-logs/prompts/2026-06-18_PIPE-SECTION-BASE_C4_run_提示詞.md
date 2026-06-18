# PIPE-SECTION-BASE C4 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 17:27 |
| 任務代號 | PIPE-SECTION-BASE C4 |
| 觸發 Commit | C4 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C4_執行.md` |
| 觸發情境 | baron 驗收 C3 報告後、下達 C4 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C4（引擎單元測試 + 接縫整合測試·雙鎖 U5/Q6）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / **plan（全局策略 z·U1 re-inject）** / tasks（§8 C4）/ database SOP / logging SOP
- 三防線：物理（§7 不可動·本階段純新增測試）/ 測試（§6.4 grep + pytest）/ 文件（不自發 commit）
- 包裹：本階段新增 `tests/test_section_engine.py`、無改既有原始碼故無須包裹（若微調既有檔才用 C4 START/END）
- 備份：本階段僅新增測試檔、無須備份
- 實作（tasks §8 C4）：新建 `tests/test_section_engine.py` 覆蓋——① DFS collect_summary_targets 走任意子樹 / ② parse_indexed 批次保序 / ③ restore_sections_markdown 並行 byte 等拍保序 + max_workers 限流計數 + 單 unit 拋例外退原文 / ④ is_heading_degraded 退化 fallback / ⑤ render_meta_header 純格式化（給 tuples → 預期 markdown、不碰 dict）/ ⑥ **base 層 P2→P3→P4 key-changing 整合測試**（Mock Translator 真改 key、斷言 collect_summary_targets 之 key 與 collect_rag_sections 之 summary_key 同基準＝原文標題 path、堵 RAG-ASYNC-HOTFIX-1）
- 驗收：§6.4 grep + `pytest tests/test_section_engine.py -v` 全綠 + `pytest tests/ -q` 基線（≥640 + 新增）
- TODO：C4 ✅ / C5 🟡 WIP + hash 自癒
- 產出：`baton/..._C4_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- C4 純新增測試、零業務代碼改動（不可動清單天然守住）。
