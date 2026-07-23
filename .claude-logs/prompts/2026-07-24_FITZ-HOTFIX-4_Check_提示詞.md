# FITZ-HOTFIX-4 Check 階段提示詞

- **歸檔日期**：2026-07-24
- **任務**：FITZ-HOTFIX-4（裸 HTML 中和與報頭集基準修正）
- **階段**：階段 6（Conformance 驗收與 Checkout 收官）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-24 03:20 |
| **任務代號** | FITZ-HOTFIX-4 Check |
| **觸發 Commit** | FITZ-HOTFIX-4-Check |
| **相關產出檔案** | 所有執行報告路徑 |
| **觸發情境** | HOTFIX-4 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞

1. 寫入 `.claude-logs/prompts/2026-07-24_FITZ-HOTFIX-4_Check_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（對應分類補登 + `## 依時間排序` 首行插入、超過 15 筆刪最舊）。
3. 確認完成後回覆「✅ 提示詞已歸檔」。

---

## 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-4`
- **Hotfix**：`.claude-logs/baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md`
- **執行報告**：`.claude-logs/baton/2026-07-24_FITZ-HOTFIX-4_執行.md`

## 📖 強制讀檔清單

```
CLAUDE.md / WORKFLOW_SOP.md / TODO.md
baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md（v1）
baton/2026-07-24_FITZ-HOTFIX-4_執行.md
```

## 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3）

## ✅ Conformance 驗收流程

**第一步**：依目標規格（K1 裸 HTML 中和 / K2 報頭集原封基準修正 / 雙語圖片對稱不變式）、測試計畫驗收條件、不可動清單與提示詞歸檔狀態交叉核對，產出 Conformance 驗收報告表格。

**提示詞歸檔稽核**：`ls .claude-logs/prompts/ | grep "FITZ-HOTFIX-4"` 確認 2 份（run、Check）。

## 🗃️ 收官自動化動作（全部合規後）

1. **TODO + 雙源 Hash 自癒**：archive 追加完成表格；`git log -n 5` 讀 HOTFIX-4 真實 hash；替換佔位符；移除 active 條目 + 更新類別索引。
2. **搬移 baton**：hotfix→hotfixes/、執行報告→executions/。
3. **確認 baton 清除**（除影子 PDF）。
4. **prompts 納 git add**（INDEX + 2 提示詞）。
5. **staged 自檢 + checkout 報告**：產 `executions/2026-07-24_FITZ-HOTFIX-4_checkout_執行.md`（輕量格式、Conformance 通過、雙語圖片對稱 E2E 與中和測試通過、無跨 Phase handoff 豁免）；`git diff --cached --name-only` 自檢暫存集。
6. **`/tmp/FITZ-HOTFIX-4_checkout_msg.txt`**。

## §8 baron 執行命令格式（逐檔 git add；嚴禁 `git add .`/`-A`）

歸檔清單：hotfix/2 執行報告/2 提示詞/INDEX/2 .bak/TODO/archive；commit message 草稿 → /tmp/FITZ-HOTFIX-4_checkout_msg.txt；baron 手動 `git commit -F`。

## 🛑 停止指令

產出 `checkout_執行.md` 後必須立即停止。嚴禁自發 commit/push、嚴禁改已歸檔歷史文件。
