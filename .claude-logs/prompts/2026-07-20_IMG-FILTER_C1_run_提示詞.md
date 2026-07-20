# IMG-FILTER C1 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 22:25 |
| **任務代號** | IMG-FILTER C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_IMG-FILTER_C1_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`IMG-FILTER`／**當前 Commit 代號**：`C1`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C1 具體實作細節` 修改及建立代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 ingestion_engine 與 litedoc_pipeline 既有業務邏輯（C1 零接線）；必須純加法（過濾器模組＋常數＋測試）；嚴禁引入 Pillow 等第三方影像套件、尺寸讀取採 stdlib 二進位 header 解析；門檻必用 plan v2 校正值（100000/4.0、廢長邊軸）、嚴禁 spec 原始錯誤門檻。
2. **測試防線**（tasks §6.1）：`tests/test_image_filter.py` 覆蓋——PNG/JPEG header 尺寸解碼/面積與長寬比判定/報頭比對/fail-open/enabled=False 回 None/caplog 審計；pytest tests/ 全綠（基線 805+）；`grep -rn "image_filter" pipelines/` 確認無接線；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp settings.py .claude-logs/archive/2026-07-20_IMG-FILTER_C1_settings.py.bak
cp .env.example .claude-logs/archive/2026-07-20_IMG-FILTER_C1_env.example.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C1 → ✅、C2 → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-20_IMG-FILTER_C1_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C1)·hash 留空〕/ §1-§8（§3 含 4 實體檔 + 2 .bak；§4 說明 stdlib PNG/JPEG 解析含 JPEG SOF 掃描與防無效 I/O 遍歷；§5 實貼；§7 指向 C2）

### 📝 §8 baron 執行命令格式要求

git add 6 檔（settings/.env.example/image_filter/test_image_filter + 2 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/IMG-FILTER_C1_msg.txt`（四點：三常數+env 說明 / stdlib PNG IHDR+JPEG SOF 掃描零依賴 / make_figure_filter 三規則閉包+fail-open+審計 / 測試覆蓋）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 C2 / 改動未列入 C1 之代碼 / 自發 git commit・push。
