# FITZ-HOTFIX-4 Run 階段提示詞

- **歸檔日期**：2026-07-24
- **任務**：FITZ-HOTFIX-4（裸 HTML 中和與報頭集基準修正）
- **階段**：階段 4（執行 HOTFIX-4）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-24 02:54 |
| **任務代號** | FITZ-HOTFIX-4 |
| **觸發 Commit** | HOTFIX-4 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md` |
| **觸發情境** | baron 同意 hotfix 設計與現象 C 分析後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞

1. 寫入 `.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（對應分類補登 + `## 依時間排序` 首行插入、超過 15 筆刪最舊）。
3. 確認完成後回覆「✅ 提示詞已歸檔」。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-4`
- **當前 Commit 代號**：`HOTFIX-4`
- **工作流類別**：`BE-Hotfix`
- **Hotfix 檔路徑**：`.claude-logs/baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md`

### 📖 強制讀檔清單

```
CLAUDE.md / WORKFLOW_SOP.md
baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md
sop/2026-05-23_logging_SOP_手冊.md / sop/2026-05-23_database_SOP_手冊.md
```

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3）

### 🛠️ 執行命令

依 `hotfix.md 熱修復修法` 修改程式，嚴守：

1. **物理防線**（hotfix 不可動清單）：
   - 嚴禁動 `pipelines/image_filter.py` 規則、`processor/fitz_processor.py`、`processor/md_cleaner.py` 等；本案極簡高度內聚於 `pipelines/litedoc_pipeline.py` 的 K1 與 K2 接線。
   - K1 裸 HTML 中和（`_neutralize_inline_html`）接線於 P1 ②' 清洗步（連字修復寫檔塊附近）、`DocAnalyzer` 判型之前執行、帶**反引號守衛**防重複包裹。
   - K2 報頭集預算必須在 P3 一進場（K3 刪行之前）依**原封行序**預算 `_pristine_header_srcs`，一路向下傳遞給 `_filter_source_figures`，消除刪行後行號位移漏網面。

2. **測試防線**：
   - `tests/test_litedoc_pipeline.py`：K1 中和〔`<script>`/`<link>`/`<img>` 反引號包裹·已在 code span 不重包·`a < b` 不誤判·行數不變式·Browsers 實物段落 fixture 經 marked+sanitize 後文不被 DOMPurify 吞〕/ K2〔圖在第 8 行、K3 刪 0-4 行·舊方式誤 DROP vs 新方式 KEEP·`header_srcs=None` 兜底〕/ 雙語圖片對稱 E2E〔whole + section 模式圖片數與 src 全等〕。
   - `pytest tests/` 全綠（基線 1010+、零新 fail），貼終端輸出 + SOP 核查。

3. **文件防線**（CLAUDE.md §1.3）：baton 暫存嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 與歷史 Hash 自癒回填

1. HOTFIX-4 → ✅；checkout → 🟡 WIP。
2. 雙源 hash 自癒回填（TODO.md + archive/TODO_done_archive.md）。

### 📁 產出規格

- 執行報告 `.claude-logs/baton/2026-07-24_FITZ-HOTFIX-4_執行.md`（暫存 baton/）
- 套用 `.claude-logs/templates/template_execution.md`；含元數據塊（Completed (Commit HOTFIX-4)、hash 留空）/ §1-§8（§3 含 1 實體檔 + 1 測試檔 + 2 `.bak`；baton 報告/hotfix 不列 git add）

### 📝 §8 baron 執行命令格式

```bash
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_test_litedoc_pipeline.py.bak
# commit message → /tmp/FITZ-HOTFIX-4_msg.txt；baron 手動 git commit -F
```

### 🛑 停止指令

產出 `2026-07-24_FITZ-HOTFIX-4_執行.md` 並更新 TODO.md 後必須立即停止。嚴禁繼續 checkout、改 HOTFIX-4 外代碼、自發 commit/push。
