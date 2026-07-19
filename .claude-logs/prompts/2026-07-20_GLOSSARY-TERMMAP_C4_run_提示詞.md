# GLOSSARY-TERMMAP C4 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 00:53 |
| **任務代號** | GLOSSARY-TERMMAP C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_GLOSSARY-TERMMAP_C4_run_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`GLOSSARY-TERMMAP`／**當前 Commit 代號**：`C4`／**工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md（自動載入）+ plan（v2）+ tasks（§8）+ design_spec + logging SOP + database SOP

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### 🛠️ 執行命令

依 `tasks.md §8 C4 具體實作細節` 修改代碼，嚴守防線：

1. **物理防線**（tasks §7）：嚴禁動 models.py 表定義與合約；section_engine 僅限 `slot_context_fn` 參數擴充與 `collect_render_slots` 加 `key` 欄位等**純加法**修改（預設參數路徑 byte 等價、resume 呼叫端零改動；**結構性受阻立即停止回報 baron**）；嚴禁引入譯文型 preceding（強制序列化、破壞並行收益）。
2. **測試防線**（tasks §6.4）：`tests/test_section_engine.py` 與 `tests/test_litedoc_pipeline.py` 分別新增測試——slot_context_fn 缺省回歸／傳入時 context 逐段注入正確／鄰近段落摘要滑窗 preceding 機制；pytest tests/ 全綠（基線 780+）；`grep -n "slot_context_fn" pipelines/section_engine.py pipelines/litedoc_pipeline.py` 期望有命中；貼驗收與 SOP 核查輸出。
3. **文件防線**（CLAUDE.md §1.3）：執行報告與 plan/tasks 均 baton 暫存、嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/section_engine.py .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_section_engine.py.bak
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_litedoc_pipeline.py.bak
cp tests/test_section_engine.py .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_section_engine.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

1. C4 → ✅、C5 → 🟡 WIP。
2. `git log` 掃描「待 baron 回填」、雙源替換真實 hash。

### 📁 產出規格

- 執行報告：`.claude-logs/baton/2026-07-20_GLOSSARY-TERMMAP_C4_執行.md`（baton 暫存）；套 template_execution.md
- 必含：元數據塊〔Completed (Commit C4)·hash 留空〕/ §1-§8（§3 含 4 實體檔 + 4 .bak；§4 說明 slot_context_fn 參數設計與 Pydantic `model_copy(update=...)` 複製上下文安全做法；§5 實貼；§7 指向 C5）

### 📝 §8 baron 執行命令格式要求

git add 8 檔（section_engine / litedoc_pipeline / 兩測試 + 4 .bak、逐檔顯式）+ msg 草稿寫 `/tmp/GLOSSARY-TERMMAP_C4_msg.txt`（四點：section_engine slot_context_fn+content slots key / litedoc 上下文工廠前一鄰近摘要 preceding 注入 / section_engine 缺省等價測試 / litedoc 滑窗+容缺+fallback 測試）+ baron 手動 `git commit -F`。

### 🛑 停止指令

產出執行報告並更新 TODO 後立即停止。嚴禁：續跑 C5 / 改動未列入 C4 之代碼 / 自發 git commit・push。
