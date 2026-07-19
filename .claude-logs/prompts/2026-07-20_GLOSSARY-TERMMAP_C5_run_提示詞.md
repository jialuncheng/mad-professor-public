# GLOSSARY-TERMMAP C5 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 01:31 |
| **任務代號** | GLOSSARY-TERMMAP C5 |
| **觸發 Commit** | C5 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_GLOSSARY-TERMMAP_C5_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`GLOSSARY-TERMMAP`／**當前 Commit 代號**：`C5`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8、含 §4.5 點火後觀察項）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C5 具體實作細節` 修改代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 models.py 表定義與合約；本 commit **僅限** settings.py 旗標預設翻轉、.env.example 說明更新、及因預設翻轉所致既有測試之 monkeypatch 隔離——不得更動任何其餘業務代碼。
2. **測試防線**（tasks §6.5）：`grep -rn "LLM_USE_GLOSSARY_ALIGN" tests/` 全盤點；依賴旗標關但未顯式 patch 之測試檔補 `monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)` 防禦性隔離（防打真 LLM／Regression、**既有斷言 100% 不動**）；pytest tests/ 全綠（基線 780+、零新 fail）；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp settings.py .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_settings.py.bak
cp .env.example .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_env.example.bak
# ⚠️ 同步列出並執行所有因 C5 掃描而受影響並進行 monkeypatch 修改之測試檔備份指令
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C5 → ✅、checkout → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-20_GLOSSARY-TERMMAP_C5_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C5)·hash 留空〕/ §1-§8（§3 含全部實體檔 + .bak；§4 條列受影響測試檔與 monkeypatch 隔離、.env.example 修改細節；§5 實貼；§7 指向 checkout）

### 📝 §8 baron 執行命令格式要求

git add（settings.py / .env.example / 掃描修改之測試檔 / 對應 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/GLOSSARY-TERMMAP_C5_msg.txt`（三點：旗標翻轉 true 全線啟用 / .env.example 同步含關回方式 / 測試掃描補 monkeypatch 隔離）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 checkout / 改動未列入 C5 之代碼 / 自發 git commit・push。
