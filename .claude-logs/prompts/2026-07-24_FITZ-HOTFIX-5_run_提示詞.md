# FITZ-HOTFIX-5 Run 階段提示詞

- **歸檔日期**：2026-07-24
- **任務**：FITZ-HOTFIX-5（譯後裸 HTML 標籤出口補中和）
- **階段**：階段 4（執行 HOTFIX-5）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-24 17:25 |
| **任務代號** | FITZ-HOTFIX-5 |
| **觸發 Commit** | HOTFIX-5 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md` |
| **觸發情境** | baron 同意 hotfix 設計後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞

1. 寫入 `.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-5_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（對應分類補登 + `## 依時間排序` 首行插入、超過 15 筆刪最舊）。
3. 確認完成後回覆「✅ 提示詞已歸檔」。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-5`
- **當前 Commit 代號**：`HOTFIX-5`
- **工作流類別**：`BE-Hotfix`
- **Hotfix 檔路徑**：`.claude-logs/baton/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md`

### 📖 強制讀檔清單

```
CLAUDE.md / WORKFLOW_SOP.md
baton/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md
sop/2026-05-23_logging_SOP_手冊.md / sop/2026-05-23_database_SOP_手冊.md
```

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3）

### 🛠️ 執行命令

依 `hotfix.md 熱修復修法` 修改程式，嚴守：

1. **物理防線**（hotfix 不可動清單）：
   - 嚴禁動 `image_filter`/`fitz_processor`/`md_cleaner` 等；本案極簡高度內聚於 `pipelines/litedoc_pipeline.py` 的 P3 出口接線。
   - 僅在 P3 `run_phase3` 尾段，`zh_text`/`en_text` 組裝完成、**扉頁 `_render_meta_headers` prepend 之前**，呼叫既有 `_neutralize_inline_html` 處理雙側 body。
   - 確保扉頁 `<div class="paper-header-meta">` 等合法 raw HTML 不被中和包裹（順序：先 body 中和、後 prepend 扉頁）。

2. **測試防線**（hotfix 測試計畫）：
   - `tests/test_litedoc_pipeline.py`：譯後復活〔模擬 `restore_sections_markdown` 回傳含裸 `<script>` 之 zh body → 出口中和後 body 段外裸標籤=0、`<script>` 已包〕/ 扉頁豁免〔`paper-header-meta` div 未被反引號包〕/ 冪等與行數不變〔重跑相等、前後行數全等〕/ whole 模式對稱〔zh/en 雙側補中和〕。
   - `pytest tests/` 全綠（基線 1021+、零新 fail），貼終端輸出 + SOP 核查。

3. **文件防線**（CLAUDE.md §1.3）：baton 暫存嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 與歷史 Hash 自癒回填

1. HOTFIX-5 → ✅；checkout → 🟡 WIP。
2. 雙源 hash 自癒回填（TODO.md + archive/TODO_done_archive.md）。

### 📁 產出規格

- 執行報告 `.claude-logs/baton/2026-07-24_FITZ-HOTFIX-5_執行.md`（暫存 baton/）
- 套用 `.claude-logs/templates/template_execution.md`；含元數據塊（Completed (Commit HOTFIX-5)、hash 留空）/ §1-§8（§3 含 1 實體檔 + 1 測試檔 + 2 `.bak`；baton 報告/hotfix 不列 git add）

### 📝 §8 baron 執行命令格式

```bash
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_test_litedoc_pipeline.py.bak
# commit message → /tmp/FITZ-HOTFIX-5_msg.txt；baron 手動 git commit -F
```

commit message 草稿（三點）：P3 run_phase3 尾端扉頁 prepend 前呼叫 `_neutralize_inline_html` 中和 zh_text/en_text 譯後復活裸標籤 / 時序在扉頁生成前使 paper-header-meta div 豁免 / 新增譯後復活+扉頁豁免+冪等+行數不變測試。

### 🛑 停止指令

產出 `2026-07-24_FITZ-HOTFIX-5_執行.md` 並更新 TODO.md 後必須立即停止。嚴禁繼續 checkout、改 HOTFIX-5 外代碼、自發 commit/push。
