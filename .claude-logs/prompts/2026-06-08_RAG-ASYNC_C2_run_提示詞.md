`````markdown
# 2026-06-08 — RAG-ASYNC C2 Run（Contract·合約欄位 section_summaries）提示詞

> **收到時間**：2026-06-08 04:31（UTC+8）
> **任務代號**：RAG-ASYNC C2（BE-Refactor·階段 4 執行）
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 C1 規格同步報告後，下達 C2 合約欄位修改指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 04:31 | 任務 RAG-ASYNC C2 | 觸發 Commit C2 | 依據 tasks §8 C2 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C2_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C2（BE-Refactor·合約欄位）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / logging SOP / database SOP / contracts.py / resume_pipeline.py / test_pipe_core.py

### 執行命令（依 tasks §8 C2 具體實作細節）
1. 物理防線（§7 不可動）；2. 測試防線（§6.2 grep + pytest 全綠）；3. 文件防線（不自發 commit）；
4. 註解包裹：# === [RAG-ASYNC C2 START/END] ===。

### 備份
cp contracts.py / resume_pipeline.py / test_pipe_core.py → archive/…_C2_….bak

### 改動
- GlossaryReadySpec 移除 chapter_summaries: Optional[List[str]]、新增 section_summaries: Optional[Dict[str,str]]=None（五路通用節點摘要、key 對位巢狀樹、繁中、向後相容、frozen/extra=forbid 不破）。
- 全庫 grep chapter_summaries、對齊所有引用（resume_pipeline / test_pipe_core 等）。
- pytest tests/ -q 綠。

### Git 可入庫
archive/ 三 .bak + contracts.py + resume_pipeline.py + test_pipe_core.py；baton（含 _執行.md）C7 前不 git add。

### TODO 同步 + Hash 自癒
C2 → ✅；C3 → 🟡 WIP；git log 回填佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C2_執行.md（暫存、不 git add）；§5 貼 pytest + SOP 核查；§8 git add 清單 + msg（/tmp/RAG-ASYNC_C2_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C3、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：contracts.py（section_summaries 取代 chapter_summaries）+ 對齊 resume_pipeline/test_pipe_core；各 .bak
- 驗收：grep（section_summaries 命中 / chapter_summaries 0 命中）+ pytest 全綠 + SOP 核查
- 報告：baton/…_C2_執行.md（暫存、不 git add）
- 是否動業務代碼：是（contracts 欄位）；是否 commit：否（待 baron）

## 後續引用

C2 合約欄位 section_summaries 落地（五路通用節點摘要、取代 chapter_summaries）；下一步 C3（rag_indexer Strategy B 分塊 + size-cap、零 import rag_processor）。
`````
