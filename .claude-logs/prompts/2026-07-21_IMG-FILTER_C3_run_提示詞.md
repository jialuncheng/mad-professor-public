# IMG-FILTER C3 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 00:21 |
| **任務代號** | IMG-FILTER C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-21_IMG-FILTER_C3_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`IMG-FILTER`／**當前 Commit 代號**：`C3`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C3 具體實作細節` 修改代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 resume/slide 兩路（無圖片路零碰）；嚴禁動 A 軌鏈本體與 contracts 凍結合約；嚴禁引入任何 Vision LLM 參與 Drop 決策。
2. **測試防線**（tasks §6.3）：§7.2 跨 Phase 整合測試（暫存 mock md＋實體圖檔＋判型 dict → 真 `_build_tiles` 端到端；**特別斷言 481×369 級內文 Chart KEEP 守門**、報頭小圖 DROP、Caption 未殘留）；擴充 test_litedoc_pipeline（`_collect_header_srcs` 行界界定〔行界外 Hero 不入〕/sidecar 缺失降級/`IMG_FILTER_ENABLED=False` None 回歸）；pytest tests/ 全綠（基線 805+）；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-21_IMG-FILTER_C3_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_litedoc_pipeline.py.bak
cp tests/test_ingestion_engine.py .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_ingestion_engine.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C3 → ✅、checkout → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-21_IMG-FILTER_C3_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C3)·hash 留空〕/ §1-§8（§3 含 3 實體檔 + 3 .bak；§4 說明 _collect_header_srcs 行號邊界與 fig_filter 組裝注入；§5 實貼；§7 指向 checkout）

### 📝 §8 baron 執行命令格式要求

git add 6 檔（litedoc_pipeline / 兩測試 + 3 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/IMG-FILTER_C3_msg.txt`（四點：_collect_header_srcs 判型行界預掃 / make_figure_filter 組裝注入 assemble / litedoc 測試〔行界+降級〕/ §7.2 整合〔報頭 DROP+481 級 KEEP 守門〕）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 checkout / 改動未列入 C3 之代碼 / 自發 git commit・push。
