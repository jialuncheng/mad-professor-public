`````markdown
# 2026-06-08 — RAG-ASYNC C1 Run（Spec Sync·規格文件同步）提示詞

> **收到時間**：2026-06-08 04:10（UTC+8）
> **任務代號**：RAG-ASYNC C1（DOC-Refactor·階段 4 執行）
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 tasks.md，下達 C1 規格文件同步指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 04:10 | 任務 RAG-ASYNC C1 | 觸發 Commit C1 | 依據 tasks §8 C1 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C1_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C1（DOC-Refactor·規格文件同步）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / 母 plan v10 / PIPE-SPEC

### 執行命令（依 tasks §8 C1 具體實作細節）
1. 物理防線（§7 不可動清單）；2. 測試防線（§6.1 grep）；3. 文件防線（不自發 commit）；
4. 註解包裹：修改區塊用 HTML 註解 <!-- === [RAG-ASYNC C1 START/END] === --> 包裹。

### 備份與 Git
- 改檔前 cp 兩檔至 archive/…_C1_….bak。
- baton/ 下檔案（含被改的 plan_v10/SPEC + _執行.md）C7 前絕不 git add。
- 本 commit 僅 .bak（archive/）可入庫。

### 改動（依 tasks §4.1/§8 C1）
- 母 plan v10 §U2（section summary 歸 P2 統一六步）/§U6（措辭：零 Embedding 呼叫；P2 summary 屬 LLM 文字、批次有界、非致命、不阻 reading_ready）。
- PIPE-SPEC §1.1②（section_summaries 取代 chapter_summaries）/§1.4（Chapter Summary 來源 P2 + 物理分塊 P4 自生 + size-cap）/§1.3（resume P3「100% Bypass」→「逐 heading section 翻譯 + 退化 fallback」）。
- 兩檔 §99.2 各加 RAG-ASYNC C1 Revision。

### TODO 同步 + Hash 自癒
C1 → ✅；C2 → 🟡 WIP；git log 回填殘留佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C1_執行.md（template_execution、暫存、嚴禁 git add）；§8 含 git add 清單（僅 .bak）+ msg 寫 /tmp/RAG-ASYNC_C1_msg.txt。

### 🛑 停止
產報告後立即停止；不續 C2、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：母 plan v10（§U2/§U6）+ PIPE-SPEC（§1.1②/§1.4/§1.3 含修 P3 doc-drift）+ 兩檔 §99.2 Revision；各 .bak
- 驗收：§6.1 grep（section_summaries 命中、resume P3「100% Bypass」0 命中）
- 報告：baton/…_C1_執行.md（暫存、不 git add）
- 是否動業務代碼：否（純規格文件）；是否 commit：否（待 baron）

## 後續引用

C1 規格同步落地（母 plan v10 + PIPE-SPEC 對齊 plan v2 + 修 §1.3 P3 doc-drift）；下一步 C2（合約欄位 section_summaries 取代 chapter_summaries）。
`````
