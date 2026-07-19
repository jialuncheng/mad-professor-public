# GLOSSARY-TERMMAP Check（Conformance 驗收與 Checkout 收官）提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 02:01 |
| **任務代號** | GLOSSARY-TERMMAP Check |
| **觸發 Commit** | GLOSSARY-TERMMAP-Check |
| **相關產出檔案** | baton/ 之 C1-C5 執行報告五份 |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_GLOSSARY-TERMMAP_Check_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 Checkout 動作。

### 📋 任務資訊

- 任務編碼：`GLOSSARY-TERMMAP`；Plan / Tasks / C1-C5 執行報告均於 baton/

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md / TODO.md（自動載入）+ plan + tasks + C1-C5 執行報告（按順序）

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### ✅ Conformance 驗收流程

第一步：產出 Conformance 驗收報告（目標規格〔build_termmap 落地/三路 P2 收斂/預設開旗標/連貫附論滑窗注入等〕/ 測試計畫驗收 / 不可動清單 / 提示詞歸檔狀態；表格依 template_prompt_for_check 第二步格式）。
提示詞歸檔稽核：`ls .claude-logs/prompts/ | grep "GLOSSARY-TERMMAP"` 確認 tasks、C1-C5 run、Check 共 7 份俱在。

### 🗃️ 收官自動化動作（全部合規後才執行）

第一步：TODO 雙層結案 + 雙源 hash 自癒（archive 追加表格 / git log -n 12 取 C1-C5 hash / 索引 pointer + 佔位符替換 / active 移除 + 類別索引）。
第二步：baton 一次性 mv（plan→plans/、tasks→tasks/、C1-C5 報告→executions/）。
第三步：`ls .claude-logs/baton/` 確認本案零殘留。
第四步：7 份提示詞 + INDEX.md git add。
第五步：staged 自檢 + `executions/2026-07-20_GLOSSARY-TERMMAP_checkout_執行.md`（輕量格式、Conformance 通過 + §7.2 整合測試存在且通過；`git diff --cached --name-only` 僅含宣告檔案）。
第六步：`/tmp/GLOSSARY-TERMMAP_checkout_msg.txt` 產生並展示於報告。

### 📝 §8 baron 執行命令格式要求

git add 歸檔清單（plan/tasks/6 執行報告/7 prompts/INDEX/各 commit .bak〔C1×2/C2×3/C3×4/C4×4/C5×3〕/TODO.md/archive 歸檔檔、逐檔顯式）+ msg 草稿（五點：build_termmap 落地與三路收斂廢早退 / 滑窗+免括號 / 旗標點火+測試隔離 / baton 歸檔 / TODO 結案 hash 自癒）+ baron 手動 `git commit -F /tmp/GLOSSARY-TERMMAP_checkout_msg.txt`。

### 🛑 停止指令

產出 checkout_執行.md 後立即停止。嚴禁自發 git commit / push、嚴禁修改已歸檔正式歷史文件。
