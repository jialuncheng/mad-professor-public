# GLOSSARY-TERMMAP C3 Run 階段 提示詞

### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-19 23:34 |
| **任務代號** | GLOSSARY-TERMMAP C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-19_GLOSSARY-TERMMAP_C3_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`GLOSSARY-TERMMAP`／**當前 Commit 代號**：`C3`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C3 具體實作細節` 修改代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 models.py 表定義與合約；嚴禁動三路 P2 中除 `_heal_glossary` 以外任何步序（摘要/LCC/節點摘要等）；本 commit 僅限 `resume_pipeline.py` 與 `slide_pipeline.py` 兩路 P2 術語自癒收斂、其餘業務邏輯不得觸碰（等價替換最小回歸面）。
2. **測試防線**（tasks §6.3）：pytest tests/ 全綠（基線 780+、零新 fail）；`grep -n "if existing" pipelines/resume_pipeline.py pipelines/slide_pipeline.py` 期望 0 命中；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_resume_pipeline.py.bak
cp pipelines/slide_pipeline.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_slide_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_resume_pipeline.py.bak
cp tests/test_slide_pipeline.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_slide_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C3 → ✅、C4 → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_C3_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C3)·hash 留空〕/ §1-§8（§3 含 4 實體檔 + 4 .bak；§4 說明兩路現場讀全文 md/頁面文本傳 builder 方式；§5 實貼；§7 指向 C4）

### 📝 §8 baron 執行命令格式要求

git add 8 檔（resume/slide 兩業務 + 兩測試 + 4 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/GLOSSARY-TERMMAP_C3_msg.txt`（四點：resume 收斂傳 md 全文 / slides 收斂傳合併頁文本 / 雙廢早退 / 測試 stub 對位）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 C4 / 改動未列入 C3 之代碼 / 自發 git commit・push。
