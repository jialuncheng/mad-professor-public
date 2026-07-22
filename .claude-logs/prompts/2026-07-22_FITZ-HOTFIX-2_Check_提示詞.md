# FITZ-HOTFIX-2 Check（Checkout 收官）階段提示詞

- **歸檔日期**：2026-07-22
- **任務**：FITZ-HOTFIX-2（報頭行界收窄與雙語圖片對稱）
- **階段**：階段 5/6（Conformance 驗收 + Checkout 收官歸檔）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-22 17:14 |
| **任務代號** | FITZ-HOTFIX-2 Check |
| **觸發 Commit** | FITZ-HOTFIX-2-Check |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | HOTFIX-2 提交落地完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行 any 讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下熱修復任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 Checkout 動作。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-2`
- **Plan 路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_plan.md`
- **Hotfix 任務路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_執行.md
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/TODO.md                                           # 任務狀態（已自動載入）
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_plan.md  # 原始規格
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md  # 熱修復任務與驗收條件
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_執行.md            # HOTFIX-2 執行報告
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

---

### ✅ Conformance 驗收流程

**第一步：產出 Conformance 驗收報告**
依據目標規格（包含 K1 報頭行界收窄防誤殺、K2 P3 補算與補傳 `header_srcs` 對齊過濾基準）、單元測試與對稱性斷言結果、不可動清單與提示詞歸檔狀態，交叉核對並在回覆中產出 Conformance 驗收報告表格（依 `template_prompt_for_check.md` 第二步格式）。

**提示詞歸檔稽核要求**：
- 執行 `ls .claude-logs/prompts/ | grep "FITZ-HOTFIX-2"` 確認本任務相關的所有提示詞檔案（診斷、run、Check 提示詞共 3 份）是否都已確實建立於物理目錄中。

---

### 🗃️ 收官自動化動作（全部合規後才執行）

**第一步：更新 TODO.md 與雙源 Hash 自癒補填**
1. 在 `archive/TODO_done_archive.md` 的策略管線/文字與連字合規分類下**追加**本熱修復任務的完成表格。
2. 執行 `git log -n 5` 讀取先前 `HOTFIX-2` 已經由 baron 手動提交落地的真實 Commit Hash。
3. 自動將 `TODO.md` 的 `## ✅ 已完成（索引）` 索引行（pointer 格式）與 `archive/TODO_done_archive.md` 中表格的 `待 baron 回填` 佔位符，**全部替換為真實的 Git Commit Hash**。
4. 從 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始` 中**移除**本任務條目，並更新底部類別索引。

**第二步：搬移並歸檔 baton/ 暫存文件**
執行以下搬移指令，將暫存於 `baton/` 的文件歸檔至正式目錄，並寫入 git add 清單中：

```bash
# 搬移 Plan
mv .claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_plan.md .claude-logs/plans/

# 搬移 Hotfix 任務檔
mv .claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md .claude-logs/tasks/

# 搬移 HOTFIX-2 執行報告
mv .claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_執行.md .claude-logs/executions/
```

**第三步：確認 baton/ 內本案任務檔案已被清除**
執行 `ls .claude-logs/baton/` 確保除影子 PDF 外，無本案殘留文件。

**第四步：檢查並將 prompts/ 下本任務提示詞全部納入 git add**
檢查並確保 `.claude-logs/prompts/INDEX.md` 與本任務相關的 3 個提示詞歸檔檔案已被確實 `git add` 納入版控中。

**第五步：staged 自檢與 checkout 報告產出**
1. 產出並將 `executions/2026-07-22_FITZ-HOTFIX-2_checkout_執行.md` 寫入（套用 `template_execution.md` 輕量格式，註明 Conformance 驗收通過、單元與對稱測試通過、純後端無跨 Phase 資料手遞手豁免）。
2. 在 commit 前執行 `git diff --cached --name-only` 自檢暫存集合，確保**僅包含**本任務宣告歸檔的檔案（實體代碼修改、新測試代碼、備份的 2 個 `.bak`、plan + hotfix 任務檔 + 2 份執行報告 + prompts/INDEX.md + 3 個 prompts 歸檔檔 + TODO.md + archive/TODO_done_archive.md），並剔除無關檔案。

**第六步：產生 `/tmp/FITZ-HOTFIX-2_checkout_msg.txt`**
將 checkout 階段 the commit message 寫入 `/tmp/FITZ-HOTFIX-2_checkout_msg.txt`，並展示於報告 §8.2 中。

---

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 搬移暫存檔已完成（報告 §3 已列出）

# 2. git add 歸檔清單（⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A`）
git add .claude-logs/plans/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_plan.md
git add .claude-logs/tasks/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md
git add .claude-logs/executions/2026-07-22_FITZ-HOTFIX-2_執行.md
git add .claude-logs/executions/2026-07-22_FITZ-HOTFIX-2_checkout_執行.md
git add .claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_診斷與plan_提示詞.md
git add .claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_run_提示詞.md
git add .claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_test_litedoc_pipeline.py.bak
git add TODO.md
git add archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-2_checkout_msg.txt）
cat > /tmp/FITZ-HOTFIX-2_checkout_msg.txt << 'EOF'
BE-Hotfix: FITZ-HOTFIX-2 checkout — 成果收官歸檔（成果歸檔與移出暫存）

1. Conformance 總驗收通過，完成報頭行界收窄與雙語圖片對稱緊急熱修復（K1-K2）。
2. 通過將報頭行界 hdr_end 收窄至 meta 塊最大值以避免 intro_text 撐大，成功在 B 軌直抽中保留封面大圖（cover art）與 Falcon 9 駁船降落內容照片。
3. 通過在 P3 原文過濾時，利用 glob 定位 sidecar 取得 header_srcs 並注入 figure 篩選器，對齊雙語過濾基準，徹底恢復 final_en 與 final_zh 的雙語圖片對稱不變式。
4. 將暫存於 baton/ 的 plan、hotfix 任務檔、HOTFIX-2 執行報告搬移歸檔至正式目錄。
5. 歸檔與納入版控 3 個階段的 prompts 提示詞、INDEX.md 及 2 份代碼 .bak 備份。
6. TODO.md 進行雙層結案更新（移至已完成索引，archive 追加完成明細表，完成歷史 hash 自動補填）。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-2_checkout_msg.txt
```

---

### 🛑 停止指令

**產出 `checkout_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`（必須等待 baron 核對暫存集無誤後手動 commit）
- ❌ 修改任何已歸檔的正式歷史文件
