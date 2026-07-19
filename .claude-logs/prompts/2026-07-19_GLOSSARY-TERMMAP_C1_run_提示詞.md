# GLOSSARY-TERMMAP C1 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-19 22:54 |
| **任務代號** | GLOSSARY-TERMMAP C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-19_GLOSSARY-TERMMAP_C1_run_提示詞.md`（格式依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`GLOSSARY-TERMMAP`／**當前 Commit 代號**：`C1`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8 實作細節）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C1 具體實作細節` 修改及建立代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 `models.py` 表定義（GlobalGlossary 聯合唯一約束）；嚴禁動 `pipelines/contracts.py`；嚴禁 C1 與三路 Pipeline 接線（三路仍呼舊 `_heal_glossary`、旗標維持關閉）、必須純加法 builder + 單元測試；所有 LLM 呼叫必須在 DB 交易之外。
2. **測試防線**（tasks §6.1）：新增 `tests/test_glossary_termmap.py` 覆蓋切塊/census/去重/**廢早退分流自癒斷言（Q1）**/批次翻譯次數控制/定案寫入屬性/軟降級；pytest tests/ 全綠（基線 780+、零新 fail）；`grep -rn "build_termmap" pipelines/` 期望 0 命中；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；git commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp settings.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_settings.py.bak
cp processor/glossary_extractor.py .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C1_glossary_extractor.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C1 → ✅、C2 → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」佔位符、雙源（TODO.md + archive/TODO_done_archive.md）替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_C1_執行.md`（baton 暫存）；套用 template_execution.md
- 必含：元數據塊〔Completed (Commit C1)·hash 留空〕/ §1 基準與完成 / §2 Commit 表 / §3 變動檔案（3 實體 + 2 .bak；baton 檔嚴禁列入）/ §4 修法說明（含 census/translate prompts 設計）/ §5 測試結果實貼 / §6 不可動遵守 / §7 銜接（指向 C2）/ §8 baron 執行命令

### 📝 §8 baron 執行命令格式要求

git add 5 檔（settings.py / glossary_extractor.py / test_glossary_termmap.py / 2 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/GLOSSARY-TERMMAP_C1_msg.txt`（三點：settings census 常數 / build_termmap 五步廢早退 / 測試含廢早退回歸）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 C2 / 改動未列入 C1 之代碼 / 自發 git commit・push。
