# IMG-FILTER C2 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 22:34 |
| **任務代號** | IMG-FILTER C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_IMG-FILTER_C2_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`IMG-FILTER`／**當前 Commit 代號**：`C2`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C2 具體實作細節` 修改代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 `litedoc_pipeline.py`（C2 未接線、防 staging 混雜）；`ingestion_engine.py` 僅限 split_blocks/build_sections/assemble 對可選 `figure_filter=None` 之傳遞與呼叫、既有業務邏輯 100% 相同；**實作硬要求**：DROP 時已匹配 caption 須 `used[cap_idx]=True` 防孤兒重播。
2. **測試防線**（tasks §6.2）：擴充 `tests/test_ingestion_engine.py`——缺省 byte 等價/全過濾（圖+caption 不入且不退化、孤兒守門）/lambda True 同 None/選擇性過濾保序；pytest tests/ 全綠（基線 805+）；`grep -rn "figure_filter" pipelines/litedoc_pipeline.py` 確保未接線；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/ingestion_engine.py .claude-logs/archive/2026-07-20_IMG-FILTER_C2_ingestion_engine.py.bak
cp tests/test_ingestion_engine.py .claude-logs/archive/2026-07-20_IMG-FILTER_C2_test_ingestion_engine.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C2 → ✅、C3 → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-20_IMG-FILTER_C2_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C2)·hash 留空〕/ §1-§8（§3 含 2 實體檔 + 2 .bak；§4 說明 hook 位置與 used[cap_idx]=True 防孤兒圖說；§5 實貼；§7 指向 C3）

### 📝 §8 baron 執行命令格式要求

git add 4 檔（ingestion_engine / test_ingestion_engine + 2 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/IMG-FILTER_C2_msg.txt`（三點：figure_filter 貫穿注入 / DROP 閘門含 caption used 標記 / 測試等價+拋棄+保序）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 C3 / 改動未列入 C2 之代碼 / 自發 git commit・push。
