# 2026-07-11 — TEST-GREEN Check 提示詞

> **收到時間**：2026-07-11 22:21（UTC+8）
> **任務代號**：TEST-GREEN Check
> **觸發 commit**：checkout
> **相關產出檔案**：.claude-logs/executions/2026-07-11_TEST-GREEN_checkout_執行.md
> **觸發情境**：C1 Commit 已由 baron ship 完畢，下達 Conformance 五維度驗收與 checkout 收官指令（TODO 結案 + hash 自癒 + baton 歸檔 + 直產 checkout 執行報告）。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-11 22:21 |
| **任務代號** | TEST-GREEN Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | .claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md |
| **觸發情境** | C1 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-11_TEST-GREEN_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-11_TEST-GREEN_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 `checkout` 動作。

### 📋 任務資訊

- **任務編碼**：TEST-GREEN
- **Plan 路徑**：.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md
- **Tasks 路徑**：.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：

```

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/TODO.md                                   # 任務狀態（已自動載入）
.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md  # 原始規格
.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md  # 任務拆分與驗收條件
.claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md  # C1 執行報告

```

---

### ✅ Conformance 驗收流程

**第一步：逐項交叉比對**

依以下五個維度，逐項核對：

| 驗收維度 | 來源 | 核對方式與特定要求 |
|---|---|---|
| **目標規格** | `plan.md §2 目標規格` | 逐項確認執行報告中是否有對應的「完成狀態」（引 C1） |
| **驗收條件** | `tasks.md §6 測試計畫` | 逐項確認 Pytest 定向重跑與全套件綠燈結果是否在執行報告中全綠通過 |
| **不可動清單** | `tasks.md §7 不可動清單` | 確認所有執行報告 §6 中均標記「✅ 未觸碰」（尤其是業務代碼、前端 CSS 資產及斷言 Pattern 本體零改動） |
| **提示詞歸檔與版控稽核** | `.claude-logs/prompts/` | 1. 執行 `ls .claude-logs/prompts/ \| grep "TEST-GREEN"`，確認 plan / tasks / runs / Check 各階段 `.md` 提示詞實體皆存在；<br>2. **檢查提示詞歸檔是否已加入 Git**：執行 `git status` 確認這些 prompts 檔案非 `untracked`。若是 `untracked`，必須在此階段一併執行 `git add` 將其納入版控。 |
| **msg.txt 草稿完整性** | 本任務各執行報告 §8 | 確認 C1 執行報告 §8 含完整 msg.txt 草稿展示 |

**第二步：產出 Conformance 驗收報告**

```markdown
## Conformance 驗收結果

### 目標規格合規性
| # | plan §2 規格項 | 對應執行報告 | 狀態 |
|---|---|---|---|
| 1 | U1 — 綠燈基線（705 passed） | C1_執行.md §1/§5 | ✅ 合規 / ❌ 不符 |
| 2 | U2 — 15 個 stale 測試全數轉綠 | C1_執行.md §1/§4/§5 | ✅ 合規 / ❌ 不符 |
| 3 | U3 — 20 個現行通過測試維持通過 | C1_執行.md §1/§4/§5 | ✅ 合規 / ❌ 不符 |
| 4 | U4 — 聯集源決定性與正確性 | C1_執行.md §4 | ✅ 合規 / ❌ 不符 |
| 5 | U5 — 邊界（不做） | C1_執行.md §6 | ✅ 合規 / ❌ 不符 |

### 測試計畫合規性
| # | tasks §6 驗收條件 | 執行報告驗證 | 狀態 |
|---|---|---|---|
| 1 | C1 驗收 - 六檔定向重跑 35 passed | C1_執行.md §5 | ✅ 合規 / ❌ 不符 |
| 2 | C1 驗收 - 全套件 705 passed | C1_執行.md §5 | ✅ 合規 / ❌ 不符 |
| 3 | C1 驗收 - 斷言 Pattern 零改動 diff 核對 | C1_執行.md §5 | ✅ 合規 / ❌ 不符 |
| 4 | C1 驗收 - 6 檔皆含聯集源變數 | C1_執行.md §5 | ✅ 合規 / ❌ 不符 |

### 不可動清單合規性
| 項目 | 所有執行報告 §6 | 狀態 |
|---|---|---|
| 業務代碼 / 前端 CSS 資產 | 全部標記「✅ 未觸碰」 | ✅ / ❌ |
| 斷言 Pattern 本體與期望值 | 全部標記「✅ 未觸碰」 | ✅ / ❌ |
| 20 個通過測試之專用源 | 全部標記「✅ 未觸碰」 | ✅ / ❌ |

### 總結
- 🟢 全部合規：執行收官與歸檔動作
- 🔴 有不符項：停止收官，列出例外並等待 baron 拍板
```

---

### 🗃️ 收官自動化動作（全部合規後才執行）

**第一步：更新 TODO.md 與已提交 Hash 補填**

1. **更新 TODO.md**：將本任務從「進行中」移至「已完成」區塊。在 `## ✅ 已完成` 的 `### 流程治理` 類別最前方新增完成表格：
   ```markdown
   ### 前端CSS測試改讀分包 (TEST-GREEN)

   | Commit | 內容 | Hash |
   |---|---|---|
   | C1 | 測試源字串分包聯集改讀 | `待 baron 回填` |
   | checkout | 成果收官歸檔 | `待 baron 回填` |
   ```

2. **歷史已提交 Hash 自癒補填（⚠️ 關鍵要求）**：
   在更新 TODO.md 的同時，你必須強制執行 `git log` 讀取 Git 歷史紀錄，將剛剛手動 commit 的 C1 真實 hash（以及本任務表格中所有殘留的 `待 baron 回填` 佔位符）自動替換為真實 Git Commit Hash，保持歷史自癒。
   同時，從 `## 🟡 進行中 / ⬜ 未開始` 區塊移除 `TEST-GREEN`，並將 `## 索引（依類別）` 底部對應的 `TEST-GREEN` 標記為 ✅。

**第二步：歸檔 baton/ 暫存文件（⚠️ 搬移出 baton）**

執行以下 `mv` 與 `git add`，將 `baton/` 下本任務所有過程文件搬移到正式目錄並納入 Git 管理：

```bash
# 1. 搬移 plan
mv .claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md \
   .claude-logs/plans/
git add .claude-logs/plans/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md

# 2. 搬移 tasks
mv .claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md \
   .claude-logs/tasks/
git add .claude-logs/tasks/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md

# 3. 搬移 C1 執行報告
mv .claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md \
   .claude-logs/executions/
git add .claude-logs/executions/2026-07-11_TEST-GREEN_C1_執行.md
```

**第三步：確認 baton/ 目錄乾淨**

執行 `ls .claude-logs/baton/` 檢驗本任務所有暫存檔皆已移出，只留下 `README.md`。

**第四步：直產 checkout 執行報告**

依照 `WORKFLOW_SOP §3` 鐵律，直接在 `executions/` 目錄下建立 checkout 執行報告：
`.claude-logs/executions/2026-07-11_TEST-GREEN_checkout_執行.md`
內容必須完整記錄 Conformance 總驗結論與 `git diff --cached` staged 白名單自檢輸出。

---

### 📝 §8 baron 執行命令格式要求 (checkout)

在你的最終回覆結尾，寫入本次收官 commit 的執行指令（寫入 `/tmp/TEST-GREEN_checkout_msg.txt`）：

```bash
# 1. 搬移與歸檔已完成（所有過程檔案已從 baton/ 移出、且已直產 checkout 執行報告並執行 git add）
git add .claude-logs/executions/2026-07-11_TEST-GREEN_checkout_執行.md

# 2. 將先前遺漏或新產出的 prompts 提示詞歸檔檔案與 .bak 備份檔案加入 Git（⚠️ 逐檔 add，禁廣義 add）
git add .claude-logs/prompts/2026-07-11_TEST-GREEN_Tasks_提示詞.md
git add .claude-logs/prompts/2026-07-11_TEST-GREEN_C1_run_提示詞.md
git add .claude-logs/prompts/2026-07-11_TEST-GREEN_Check_提示詞.md
git add .claude-logs/TODO.md

# 3. commit message draft（已寫入 /tmp/TEST-GREEN_checkout_msg.txt）
cat > /tmp/TEST-GREEN_checkout_msg.txt << 'EOF'
FE-Refactor: TEST-GREEN checkout — 成果收官歸檔

完成了 TEST-GREEN 前端CSS測試改讀分包任務的 Conformance 驗收。已將暫存
於 baton/ 下的 plan、tasks 與 1 份執行報告物理搬移歸檔至 plans/、tasks/、
executions/ 正式目錄。直產 checkout 執行報告，更新 TODO.md 並全量回填歷史 Commit Hash。
EOF

# 4. baron 手動執行
git commit -F /tmp/TEST-GREEN_checkout_msg.txt
```

---

### 🛑 停止指令

**完成 TODO.md 更新、baton/ 搬移、直產 checkout 報告與輸出 checkout commit 指令後必須立即停止所有工具呼叫。**

嚴禁：
- ❌ 自發執行 `git commit` 或 `git push`
- ❌ 修改已歸檔目錄下（plans/、tasks/、executions/）的任何文件
- ❌ 在未獲 baron 授權下修改其他代碼
````

---

## 執行結果摘要

- ✅ Conformance 五維度 🟢 全綠（plan §2 五項 / tasks §6.1 四項〔ship 後實測複驗 35 + 705 passed〕/ 不可動〔C1 commit `a4e6e5b` 內容物==宣告 12 檔機器證〕/ 提示詞 3 份稽核入版控 / msg 草稿）+ §7.2 顯式豁免
- 收官完成：baton 三檔 mv 歸檔（plans/tasks/executions）、TODO 雙層結案 + hash 自癒（C1=`a4e6e5b`）、checkout 執行報告直產 executions/、staged 10 檔白名單自檢相符
- ⚠️ 揭露：TODO/TODO_done_archive/INDEX 三共用狀態檔攜帶 THEME-DEDUP checkout（未 ship）hunks，方案 (a)/(b) 待 baron 拍板（見 checkout 報告 §3）
- 未 commit / push（baron 手動；msg 草稿 `/tmp/TEST-GREEN_checkout_msg.txt`）；TEST-GREEN 全案結案

## 後續引用

- （暫無）
