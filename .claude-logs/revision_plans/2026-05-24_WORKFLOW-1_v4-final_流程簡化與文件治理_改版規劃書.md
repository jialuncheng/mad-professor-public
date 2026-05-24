# WORKFLOW-1 流程簡化與文件治理改版規劃書 v4-final（2026-05-24）

> 本文件為 **WORKFLOW-1 改版規劃書 v4-final**、為 v4 規劃書整合「baron 對第二輪雙評估的 6 個 D1-D6 拍板 + 7 個互補增益」後的最終版本。
> 套 v4 §2 拆分式結構（§0 簡頂 + §99 末尾）撰寫、作為「進入 WORKFLOW-1-1 落地」的官方輸入規格。

---

## §0 改版規則（極簡靜態頂部）

- 改版觸發：WORKFLOW-1 全部 commit ship 後過期、由實際落地的執行報告取代
- 重複防護：本文件僅整合 v4 + 雙評估 + baron 拍板結果、不重複 v3 既有內容
- 完整治理規格 → 詳見文末 §99

---

## §1 v4-final 跟 v3 / v4 的關係

```
v3 規劃書（708 行、16 章節）
   ↓
   第一輪雙評估（Claude Code + Antigravity）→ 5 個重大歧見 + 8 個獨有觀點
   ↓
v4 規劃書（628 行、整合 baron 16 個決策、提出混合方案）
   ↓
   第二輪雙評估 → 0 個重大歧見、S1-S5 100% 一致、6 個細節決策 + 7 個互補增益
   ↓
   baron 對 D1-D6 拍板 + 採納全部互補增益 + 修正多 worktree 假設
   ↓
v4-final（本檔）= **進入 WORKFLOW-1-1 落地的最終規格**
   ↓
   執行階段：WORKFLOW-1-1 → 1-2 → 1-2b → 1-3 → 1-4 → 1-5 → 1-6 → 1-7 → 1-8 → 1-9
```

**v4-final 跟 v4 的差異**（簡）：
- v4 §8「兩方案（A/B）」 → v4-final §8 確定為**方案 B（9+2b = 10 commit）**、不再二選一
- v4 §10「五個待 AI 評估」 → v4-final §10 變成「五個已採納的最小可行版本」（D1-D5 拍板結果）
- v4 §6「baton 機制」 → v4-final 修正「不適用 multi-worktree」、簡化交接流程
- v4 §12「10 個開放問題」 → v4-final §12 變成「3 個落地時的 Open Items」（其他全部拍板）

---

## §1.5 標準工作流（baron 2026-05-24 確認、為本專案後續所有任務的執行範本）

### §1.5.1 流程圖

```
┌────────────────────────────────────────────────────────┐
│ 階段 1：規劃（任一角色都可發起）                       │
│   ├─ baron 自己寫                                      │
│   ├─ Antigravity（掃 codebase 後產規劃書）             │
│   └─ Claude Design（前端視覺改版）                     │
│                                                        │
│   產出：改版規劃書（套 template_revision_plan.md）     │
└────────────────────────┬───────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│ 階段 2：Claude Code 依規劃書產執行計劃                 │
│   產出：_plan.md（套 template_plan.md）                │
│   必含：commit 拆分 / 不可動清單 / E2E 驗證計畫        │
└────────────────────────┬───────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│ 階段 3：Antigravity 驗證執行計劃（v4-final 新增）      │
│   ├─ 🟢 通過 → 進入階段 4                              │
│   └─ 🔴 不通過 → 階段 3a 循環                          │
└────────────────────────┬───────────────────────────────┘
                         │ 🔴 不通過時
                         ↓
┌────────────────────────────────────────────────────────┐
│ 階段 3a：執行計劃調整循環（不通過時）                  │
│   baron / Antigravity 提建議                           │
│        ↓                                               │
│   Claude Code 調整執行計劃（產 _plan.md v2）           │
│        ↓                                               │
│   Antigravity 再次驗證                                 │
│        ↓                                               │
│   循環直到 🟢 通過                                     │
└────────────────────────┬───────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│ 階段 4：Claude Code 逐 commit 落地                     │
│   每個 commit：                                        │
│   ├─ Claude Code 修改代碼                              │
│   ├─ Claude Code 產 _執行.md                           │
│   ├─ baron 手動 git commit + push                      │
│   └─ Antigravity 驗證 commit（模板 D、核心 3 項）      │
│        ↓                                               │
│        🟢 通過 → 下一個 commit                         │
│        🔴 不通過 → 退回 Claude Code 修正、再驗證       │
└────────────────────────┬───────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│ 階段 5：任務收官                                       │
│   ├─ 全部 commit ship 完                               │
│   ├─ TODO.md 從 🟡 WIP → ✅ 完成                       │
│   └─ Antigravity 若發現 SOP 跟代碼脫節 → 自動提示      │
└────────────────────────────────────────────────────────┘
```

### §1.5.2 各角色職責表

| 角色 | 階段 1 規劃 | 階段 2 產執行計劃 | 階段 3 驗證計劃 | 階段 4 落地 | 階段 4 驗證 commit | 階段 5 收官 |
|---|---|---|---|---|---|---|
| **baron** | ✅ 可發起 / 審核 | ❌ | ✅ 審核 + 拍板 | ✅ 手動 commit + push | ❌ | ✅ 拍板任務完成 |
| **Claude Code** | ❌ | ✅ 主責 | ❌（接收驗證結果） | ✅ 主責 | ❌ | ❌ |
| **Antigravity** | ✅ 可發起 | ❌ | ✅ **主責**（v4-final 新增） | ❌ | ✅ 主責（模板 D） | ✅ SOP 脫節偵測 |
| **Claude Design** | 🟡 前端時可發起 | ❌ | 🟡 前端時可覆核 | ❌ | 🟡 前端時可覆核視覺 | ❌ |

### §1.5.3 階段 3「Antigravity 驗證執行計劃」的具體做法

這是 v4-final 新明文化的環節。Antigravity 收到 _plan.md 後、做以下驗證（**先於 Claude Code 落地代碼**）：

| 驗證項目 | 內容 |
|---|---|
| **項目 1** | _plan.md 是否覆蓋改版規劃書所有要求？有沒有漏項？ |
| **項目 2** | commit 拆分是否合理？每個 commit 是否獨立可逆？ |
| **項目 3** | 不可動清單是否完整？有沒有遺漏關鍵保護項？ |
| **項目 4** | E2E 驗證計畫是否真能驗證設計目標？ |
| **項目 5** | 跟既有 SOP（logging / database / 工作目錄硬規則）是否一致？ |
| **項目 6** | 工作流類別判定（FE/BE/DOC × Refactor/Hotfix）是否正確？ |
| **項目 7** | §0 / §99 拆分式結構是否落地？ |

**輸出**：🟢 通過 / 🔴 不通過（含具體修正建議）

### §1.5.4 階段 3a「執行計劃調整循環」的退出條件

循環次數無上限、但每次循環必須產 **新版本** 的 _plan.md（v1 → v2 → v3...）、不重寫舊版本（用 Revision 區塊追加）。

退出條件：
- 🟢 Antigravity 給出明確「通過」結論
- baron 在循環中拍板「就這樣、進入階段 4」（強制退出）

### §1.5.5 跟 v3 雙軌制的關係

v3 PROJECT_PROGRESS_CONTROL_FRAMEWORK §1.1 雙軌制（plan → execution）跟本工作流的關係：

| v3 雙軌制 | v4-final 工作流階段 |
|---|---|
| 第 1 軌：plan | 階段 1 + 2 + 3 + 3a（規劃 → 產計劃 → 驗證計劃 → 調整） |
| 第 2 軌：execution | 階段 4（落地代碼） |

v3 雙軌制是「概念框架」、v4-final §1.5 是「具體執行範本」、兩者一致、本檔僅補上 v3 沒明文化的「階段 3 驗證計劃」環節。

### §1.5.6 WORKFLOW-1 自身的工作流軌跡（baron 已實際走過一遍、用作試點）

| 階段 | 實際發生 | 文件 |
|---|---|---|
| 1 規劃（v3） | baron 三輪指正、產出 v3 規劃書 | v3 規劃書 708 行 |
| 2 產執行計劃 | Claude Code + Antigravity 第一輪評估 | 兩份雙評估報告 |
| 3 驗證計劃 | baron 整合決策、產 v4 | v4 規劃書 628 行 |
| 3a 調整循環 | Claude Code + Antigravity 第二輪評估 | 兩份第二輪報告 |
| 3a 退出 | baron 對 D1-D6 拍板、產 v4-final | 本檔 |
| 4 落地 | **即將啟動 WORKFLOW-1-1** | 待產出 |
| 5 收官 | **WORKFLOW-1-9 試跑通過後** | 待產出 |

WORKFLOW-1 自身就是本工作流的「試點任務」、未來所有改版任務（RAG / MODEL / BUG / LOGGING / DOC...）都套用 §1.5 流程。

---

## §2 baron 拍板總表（覆蓋 v3-v4 全部決策）

### §2.1 第一輪雙評估後拍板（v4 §1 既有 16 項）

維持 v4 §1.1-§1.4 全部結果、不再列出（請參見 v4 §1）。

### §2.2 第二輪雙評估後拍板（v4-final 新增 6 項）

| 編號 | 議題 | baron 決策 | 落地位置 |
|---|---|---|---|
| **D1** | SOP 偵測 MVP 位置 | **寫進 WORKFLOW_SOP §5**（雙工具共用） | §3 |
| **D2** | 快取評分機制設計 | **混合方案**：Antigravity 算法（靜態前綴檢測、輕量）+ 獨立報告檔（不污染 §99）；**由 Antigravity 建立 SOP 給 baron 用** | §4 |
| **D3** | TL;DR 命名 | `## §1 TL;DR（概要）`（含括號子標題、符合中文閱讀） | §5 |
| **D4** | 非 .md 檔案命名 | **全部加日期前綴**（Antigravity 統一方案）`YYYY-MM-DD_<任務編碼>_<描述>.<ext>` | §6 |
| **D5** | DOC-Refactor 是否強制讀目標文件 | **強制讀**（寫進 WORKFLOW_SOP §4.5 規則） | §7 |
| **D6** | baton 跨 worktree 同步方案 | **不適用**——本專案不會有多 worktree；主 repo 是裝正式機用、開發一律在 `.claude/worktrees/hopeful-yalow-902c50/` 進行 | §8 |

### §2.3 7 個互補增益（全部納入、無爭議）

| 編號 | 增益 | 落地位置 |
|---|---|---|
| **C-B1** | baton 多 active 並存衝突規則 | `.claude-logs/baton/README.md`（§8.4） |
| **C-B2** | 工作目錄強制規範（v4 多 worktree → v4-final 單一 worktree） | 框架 §9 / WORKFLOW_SOP §6 |
| **C-B3** | 模板 D 分級制預設行為文件化 | WORKFLOW_SOP §4 驗證分級章節 |
| **C-B4** | §99 跳號說明 | WORKFLOW_SOP §2 文書類別釐清章節 |
| **A-B2** | 「被引用方」掃描具體規則 | WORKFLOW_SOP §5 + §9 |
| **A-B3** | 進階 5 項硬編碼觸發 | WORKFLOW_SOP §4 驗證分級章節 |
| **A-B1** | baton 入版控規範 → **本專案改為「本地檔不入版控、單 worktree 隔離」** | §8.5 |

### §2.4 工作目錄硬規則（v4-final 新增、來自 baron 明確指示）

> **本專案絕對規則**：
> 1. **開發一律在 `.claude/worktrees/hopeful-yalow-902c50/` 進行**
> 2. **主 repo 目錄是裝正式機用、開發階段嚴禁讀寫**
> 3. **Claude Code / Antigravity 兩工具都不准去主 repo 目錄讀寫檔案**
> 4. 這條規則寫進 PROJECT_PROGRESS_CONTROL_FRAMEWORK §9 / CLAUDE_CODE_ENTRY.md / WORKFLOW_SOP §6

---

## §3 D1 落地：SOP 脫節自動偵測（寫進 WORKFLOW_SOP §5）

### §3.1 落地內容（WORKFLOW-1-3 commit 時新增 WORKFLOW_SOP §5）

```markdown
## §5 SOP 一致性自動核查（BE-Refactor / BE-Hotfix 必跑）

在落地前、執行以下 grep 核查（每項 < 5 秒）：

### §5.1 logging SOP 核查
\`\`\`bash
# 對正在修改的 .py 檔案確認：
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔.py>
# 若用 logger.error：必須含 exc_info=True
# 若用 traceback.format_exc：不合規、改為 logger.error("...", exc_info=True)
\`\`\`

### §5.2 database SOP 核查
\`\`\`bash
# 對涉及 SQLAlchemy 的 .py 檔案確認：
grep -n "s\.commit()\|session\.commit()" <修改檔.py>
# 若有裸 commit：不合規、改為 session.begin() 上下文管理器
\`\`\`

### §5.3 違規處理
若發現不一致、暫停落地、在 plan 的「§9 Open Questions」加入衝突點、等 baron 拍板。

### §5.4 雙工具共用
本節 §5 為 Claude Code 落地前的 self-check + Antigravity 模板 D 驗證時的稽核項目。
- Claude Code 在 _執行.md 內必貼 grep 結果
- Antigravity 在驗證報告內必引用 grep 結果做合規判定
```

### §3.2 為什麼選 D1 寫進 WORKFLOW_SOP（baron 決策理由）

- 寫 SOP 共用 = 兩工具都依同一規則檢查、不會分歧
- 寫 Antigravity 內部規則 = 只有 Antigravity 跑驗證時才檢查、Claude Code 落地階段沒卡點
- baron 決策 = 雙工具共用版（更早攔截違規、防 Claude Code 寫出不合規代碼）

---

## §4 D2 落地：快取友善度評分機制（混合方案）

### §4.1 baron 決策：要 Antigravity 建立 SOP 給 baron 用

baron 不直接寫腳本、不直接管實作——委派 Antigravity 在 WORKFLOW-1 落地後、產出一份 `CACHE_OPTIMIZATION_SOP.md`、給 baron 使用。

### §4.2 SOP 必含內容（Antigravity 撰寫時對齊）

```markdown
# Cache Optimization SOP（由 Antigravity 撰寫、待 WORKFLOW-1 ship 後產出）

## §1 評分算法（用 Antigravity 提議的靜態前綴檢測、輕量）

- 100 分（完美）：文件頂部 `# 標題` 後直接是靜態 `## §0`、所有日期/Revision/動態欄位都在文件最後 10% 行數中
- 50 分（黃牌警告）：文件中段或前段含任何變動日期 / 時間戳 / Revision 表格
- 0 分（紅牌）：文件頂部前 20% 行含高頻變動的任務名稱 / 時間戳 / git hash

## §2 評分結果存放（用 Claude Code 提議的獨立報告檔、不污染 §99）

- 寫入：`.claude-logs/ref/2026-XX-XX_CACHE_FRIENDLINESS_REPORT.md`
- 不寫入：個別文件的 §99（避免「評分過程本身破壞被評分文件的快取」）
- 報告格式：表格 + 紅黃綠標 + 文件路徑 + 建議修正

## §3 觸發時機

- Antigravity 跑 codebase 掃描時觸發（建議一週一次）
- baron 可手動命令觸發：「請對 .claude-logs/ref/ 跑快取友善度評分」

## §4 最小可行範圍（first iteration）

- 第一輪僅評分 5 份核心文件：
  · PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
  · WORKFLOW_SOP.md
  · CLAUDE_CODE_ENTRY.md
  · 2026-05-23_logging_SOP_手冊.md
  · 2026-05-23_database_SOP_手冊.md
- 後續迭代再擴大範圍
```

### §4.3 為什麼採混合方案（baron 決策理由）

- Antigravity 原方案：算法輕（靜態 grep）但結果存 §99 = **破壞被評分文件的快取**（自相矛盾）
- Claude Code 原方案：算法重（git log diff）但結果存獨立檔 = **乾淨**
- baron 決策 = **取兩邊長處**：Antigravity 輕量算法 + Claude Code 獨立檔存放 + Antigravity 撰寫 SOP

---

## §5 D3 落地：TL;DR 命名規則

### §5.1 落地內容（WORKFLOW-1-2 commit 時改 template_plan.md）

`template_plan.md` 章節編號改為：

```markdown
# Phase [Phase名稱] Commit [N] — Plan：[主題名稱]

> 本文件為純分析與設計計畫、在計畫獲得確認前嚴禁修改任何業務代碼與配置

## §0 來源與審核軌跡（極簡）

## §1 TL;DR（概要）          ← v4-final 新增格式

## §2 現況盤點
## §3 觀察到的問題與證據
## §4 設計方案
## §5 變動風險與相容性評估
## §6 測試計畫與 E2E 驗證計畫
## §7 不可做 / 不可動清單
## §8 推薦 Commit 拆分與順序
## §9 開放問題

---

## §99 治理規格與 Revision
```

### §5.2 為什麼選 `## §1 TL;DR（概要）`（baron 決策理由）

- 純 `## §1 TL;DR` 對 AI 跳讀友善、但人類首讀「TL;DR」三字母不一定立即理解
- `## §1 TL;DR（概要）` 含中文子標題、人類首讀立即理解 + AI 仍能精準跳讀
- baron 決策 = 兩全方案（含括號子標題）

### §5.3 對既有 plan 檔案的影響

- **零衝擊**——「不溯及既往」、歷史 plan 不改名
- 新 plan（從 WORKFLOW-1 落地後產出的）一律用新格式

---

## §6 D4 落地：非 .md 檔案統一加日期前綴

### §6.1 落地內容（WORKFLOW-1-7 commit 時更新 §12 命名規則）

```markdown
## §12 文件命名強約束

### §12.1 .md 文件命名規則（v3 既有、不變）
（既有規則保留）

### §12.2 非 .md 文件命名規則（v4-final 新增）

**統一規則**：所有非 .md 檔案一律加日期前綴

  YYYY-MM-DD_<任務編碼>_<描述>.<ext>

| 檔案類型 | 範例 |
|---|---|
| `.json` 任務快照 | `2026-05-24_MODEL-8_schema_snapshot.json` |
| `.yaml` 配置快照 | `2026-05-24_INFRA-1_pipeline_config.yaml` |
| `.log` 運行日誌備份 | `2026-05-24_BUG-F8_error_trace.log` |
| `.svg` / `.png` 架構圖 | `2026-05-24_RAG-2_data_flow.svg` |
| `.txt` 臨時導出 | `2026-05-24_RAG-1_ocr_sample.txt` |

### §12.3 非 .md 文件不適用 §0/§99 結構

非 .md 屬「資料/圖像快照」、不是「治理文件」、不需要 §0/§99。

### §12.4 反例（嚴禁）

❌ `schema_snapshot.json`（無日期前綴）
❌ `RAG-2_data_flow.svg`（無日期前綴）
❌ `2026-05-24_data.json`（無任務編碼）
```

### §6.2 為什麼選統一加日期（baron 決策理由）

- Claude Code 原方案：區分「任務快照」加日期 vs「長期生效」不加 = 太複雜、判定線模糊
- Antigravity 原方案：全部加日期 = 規則簡單、AI / 人類都容易遵守
- baron 決策 = 統一加日期（簡單性勝過細緻區分）

---

## §7 D5 落地：DOC-Refactor 強制讀目標文件

### §7.1 落地內容（WORKFLOW-1-3 commit 時新增 WORKFLOW_SOP §4.5）

```markdown
## §4.5 DOC-Refactor（v4 新增、v4-final §7 細化）

### §4.5.1 觸發條件
- 主要影響 `.claude-logs/*.md` / `design/docs/*.md` 改動 ≥ 10 行
- 跨多份文件的流程治理改動

### §4.5.2 強制讀檔順序（v4-final 新增）
1. CLAUDE_CODE_ENTRY.md
2. .claude-logs/baton/*.md（必讀、若無 active 檔則跳過）
3. **WORKFLOW_SOP.md §4.5（本節）**
4. **目標文件本身**（v4-final D5 強制）—— 必讀正在改的文件、不可跳過
5. 對應領域 SOP（若改 logging_SOP 則讀 logging_SOP 自己）

### §4.5.3 為什麼強制讀目標文件
- 防止 AI 在不知道目標文件既有規範的情況下做「重複寫入」或「衝突修改」
- 例：若改 logging_SOP §6 加 SQL 降噪規範、AI 必須先讀 logging_SOP 的 §1-§5、確認現有規範語意、避免重複

### §4.5.4 強制 template
- 套 template_plan.md 9 章節 + §0 + §99
- 產 _執行.md 套 template_execution.md
```

### §7.2 為什麼選強制讀（baron 決策理由）

- 第二輪壓力測試 F 中：Antigravity 主動讀了 logging_SOP / Claude Code 跳過
- baron 認為「改 logging SOP 卻不讀 logging SOP」是反常識
- baron 決策 = 寫進規則、強制讀（不留模糊空間）

---

## §8 D6 + 工作目錄硬規則：本專案單 worktree 設計

### §8.1 baron 明確指示

> 本專案不會有多 worktree
> 主 repo 是拿來裝正式機用的
> 工作目錄強制 hopeful-yalow-902c50
> 因為 repo 目錄是拿來裝機用的
> 開發一律用 hopeful-yalow-902c50
> 兩邊都不准去 repo 目錄讀寫檔案

### §8.2 v4 §6.5 baton 多 worktree 議題簡化

v4 §6.5 / v4 第二輪盲點 A-B1 / C-B2 都涉及「多 worktree 處理」、v4-final 一律**簡化為「不適用」**：

| 原議題 | v4-final 處置 |
|---|---|
| C-B2 多 worktree「被引用方」掃描失效 | 不適用、Antigravity 一律掃 `.claude/worktrees/hopeful-yalow-902c50/` |
| A-B1 baton 多 worktree 同步衝突 | 不適用、baton 本地檔即可、不需 git 同步 |

### §8.3 落地內容（WORKFLOW-1-3 WORKFLOW_SOP §6 + 框架 §9 新增）

```markdown
## §6 工作目錄硬規則（v4-final 新增、來自 baron 明確指示）

### §6.1 唯一開發目錄
- 開發一律在 `.claude/worktrees/hopeful-yalow-902c50/` 進行
- 此為 git worktree 的子目錄、跟主 repo 同步

### §6.2 嚴禁觸碰主 repo 目錄
- 主 repo（worktree 父目錄）為「正式機裝機用」、嚴禁開發階段讀寫
- Claude Code 嚴禁透過絕對路徑去主 repo 目錄讀寫任何檔案
- Antigravity 嚴禁透過絕對路徑去主 repo 目錄讀寫任何檔案

### §6.3 違規偵測
- 若 Claude Code 在執行報告中發現任何主 repo 的絕對路徑、視為違規
- Antigravity 在模板 D 驗證時偵測：grep `git diff` 結果、若含主 repo 路徑、立即報告 baron

### §6.4 為什麼這條規則重要
- 主 repo 是裝機用、若被誤改可能導致裝機腳本失效
- 單一工作目錄能保證跨 session 一致性、不會有「A worktree 改了、B worktree 沒看到」的問題
```

### §8.4 baton 衝突規則（C-B1 落地）

baton 在單 worktree 內仍可能有「多個 active 並存」（例如：Antigravity → Claude Code 的 RAG-2 plan 和 Claude Code → Antigravity 的 RAG-1 verify 同時存在）。

```markdown
# .claude-logs/baton/README.md（WORKFLOW-1-4 commit 時新增）

## 本目錄用途
存放跨 AI 工具的活躍交接棒、平時為空、有交接才有檔。

## 衝突規則（多 active 並存時）
1. 依 baron 在提示詞中的明確指示決定優先順序
2. 若 baron 未指定：依任務優先級排序 🔴 高 > 🟡 中 > 🟢 低
3. 若優先級相同：取建立時間最新的 active 文件
4. 若兩個交接互相阻塞（例：A → B + B → A）：baron 介入仲裁、AI 不自行判斷

## baton 不入版控（v4-final 修正）
- baton/ 目錄存在於 .gitignore（除 README.md 外）
- 理由：單 worktree 環境、不需跨 worktree 同步、本地檔即可
- README.md 入版控、確保目錄結構穩定
```

### §8.5 為什麼選不入版控（baron 決策理由）

- v4 第二輪 Antigravity 提議 baton 入版控（透過 git 跨 worktree 同步）
- baron 明確說「本專案不會有多 worktree」 = 無跨 worktree 需求
- baton 入版控 = 每次交接 git commit + push、過度工程
- baron 決策 = baton 為本地檔、簡單就好

---

## §9 v4-final 最終 commit 拆分（方案 B、9+2b = 10 commit）

### §9.1 拆分清單（基於 v4 §8.1 方案 B + D1-D6 拍板 + 7 個互補增益）

| 序號 | 變動內容 | 影響程度 | 安全性 | 資料結構 | 可逆性 |
|---|---|---|---|---|---|
| **WORKFLOW-1-1** | 新增 3 個 template：`template_revision_plan.md` + `template_file_governance.md` + `template_specification.md` | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-2** | 既有 3 template（`template_plan.md` / `template_execution.md` / `template_hotfix.md`）加 §0/§99；template_plan 加 `## §1 TL;DR（概要）` 編號（D3 落地） | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-2b** | 修改 v3 §15、§0 改版規則從「文件頂部」變更為「拆分式」（§0 簡頂 + §99 末尾） | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-3** | 新增 `WORKFLOW_SOP.md`：含五類工作流（FE/BE/DOC × Refactor/Hotfix 5 類）+ §5 SOP 一致性核查（D1）+ §6 工作目錄硬規則（D6 + C-B2）+ §4 驗證分級（C-B3 + A-B3）+ §2 §99 跳號說明（C-B4） | 🔴 高 | 🟡 中（新流程） | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-4** | 新增 `CLAUDE_CODE_ENTRY.md`（repo 根層）+ 建立 `.claude-logs/baton/` 資料夾 + `baton/README.md`（含衝突規則 C-B1） | 🔴 高 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-5** | 修改 `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`：追加 §9 補充條款 + 補 §0/§99（拆分式）+ §9 含工作目錄硬規則（D6）+ 被引用方掃描規則（A-B2） | 🟡 中 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-6** | 既有 SOP / TODO 加 §0/§99：logging_SOP / database_SOP / database-schema_SOP / README__Prompt / TODO.md | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-7** | 命名規則實證：§12.4 補入歷史違規 pattern + §12.2 非 .md 命名規則新增（D4） | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-8** | TODO.md 加 WORKFLOW-1 任務紀錄 + prompts/INDEX 更新 + Antigravity 產出 `CACHE_OPTIMIZATION_SOP.md`（D2） | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-9** | 試跑 §6.1 六個壓力測試 A-F（含 v4 新增 F：DOC-Refactor）+ 留結果報告 | 🟡 中 | 🟢 高 | 🟢 無 | 🟢 高 |

### §9.2 依賴關係圖

```
WORKFLOW-1-1（純新增 template）
    ↓
WORKFLOW-1-2（既有 template 加 §0/§99 + TL;DR 編號）
    ↓
WORKFLOW-1-2b（規則性改動：§0 改為拆分式）
    ↓
WORKFLOW-1-3（WORKFLOW_SOP、依賴 1-1/1-2/1-2b）
    ↓
WORKFLOW-1-4（CLAUDE_CODE_ENTRY + baton/、依賴 1-3）
    ↓
WORKFLOW-1-5（框架 §9、依賴 1-3/1-4 新流程就位）
    ↓
WORKFLOW-1-6 ← 可與 1-7 平行
WORKFLOW-1-7 ← 可與 1-6 平行
    ↓
WORKFLOW-1-8（TODO 等所有 commit hash + Antigravity 產 cache SOP）
    ↓
WORKFLOW-1-9（試跑、依賴 1-1~1-8 全部）
```

平行可執行：`WORKFLOW-1-6` + `WORKFLOW-1-7`

### §9.3 每個 commit 的驗收標準

| 序號 | 驗收標準 |
|---|---|
| **1-1** | `find .claude-logs/templates/ -name "template_*.md" -newer .claude-logs/templates/template_plan.md` 返回 3（新增 3 份） |
| **1-2** | `grep "## §0\|## §1 TL;DR（概要）\|## §99" .claude-logs/templates/template_plan.md` 全部命中 |
| **1-2b** | v3 §15 拆分式設計落地（template_plan.md 自己就是試點） |
| **1-3** | `grep -c "## §4.1\|## §4.2\|## §4.3\|## §4.4\|## §4.5\|## §5\|## §6" .claude-logs/ref/WORKFLOW_SOP.md` 返回 ≥ 7（五類工作流 + 核查 + 工作目錄） |
| **1-4** | `find . -maxdepth 2 -name "CLAUDE_CODE_ENTRY.md"` 返回 1；`find .claude-logs/baton/ -name "README.md"` 返回 1；`grep "動態\|當前任務\|TODO" CLAUDE_CODE_ENTRY.md` 返回 0（無動態內容、不破壞快取） |
| **1-5** | `grep "## §9\|工作目錄硬規則" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 全部命中 |
| **1-6** | `grep -l "## §0\|## §99" .claude-logs/ref/2026-05-23_logging_SOP_手冊.md ... TODO.md` 返回 5 個檔名 |
| **1-7** | 命名合規報告產出；§12.4 補入 2 個歷史違規 pattern；§12.2 非 .md 規則就位 |
| **1-8** | `grep "WORKFLOW-1" .claude-logs/TODO.md` 返回 ≥ 1；`find .claude-logs/ref/ -name "*CACHE_OPTIMIZATION*"` 返回 1（Antigravity 產出） |
| **1-9** | 六個壓力測試結果報告存於 `.claude-logs/2026-05-XX_WORKFLOW-1_壓力測試結果.md`；F (DOC-Refactor) 必須正確分類 |

---

## §10 v4-final 落地階段 Open Items（3 個、不阻擋進入 WORKFLOW-1-1）

### §10.1 Antigravity 撰寫 `CACHE_OPTIMIZATION_SOP.md` 的時機

- baron 決策：D2 委派 Antigravity 在「WORKFLOW-1-8」commit 時產出
- Open Item：Antigravity 撰寫時可能發現更好的算法 / 更簡的格式、屆時可微調
- 處置：WORKFLOW-1-8 落地時、若 Antigravity 提議偏離本檔 §4.2、baron 在當下拍板

### §10.2 進階 5 項硬編碼觸發的具體 git diff 關鍵字（A-B3）

baron 已採納 A-B3「硬編碼觸發」、但具體關鍵字清單需 Antigravity 在 WORKFLOW-1-3 撰寫 WORKFLOW_SOP §4.x 時定案：

候選關鍵字（初版、Antigravity 可調整）：
- `.sql` / `migration` / `alembic`
- `models.py` / `schema.py`
- `setup_logging` / `JSONFormatter`
- `auth_guard` / `SessionMiddleware`
- `session.begin` / `bulk_insert_mappings`
- BE-Refactor 改動行數 ≥ 50 行

### §10.3 「被引用方」掃描 Antigravity 實作細節（A-B2）

baron 已採納「Antigravity 自動掃描注入」、但實作細節由 Antigravity 在 WORKFLOW-1-5 落地時敲定：

候選實作（Antigravity 給最小可行版本）：
- 掃描範圍：只掃 `.claude-logs/*.md`（不掃業務代碼節省 token）
- 匹配機制：用 regex 抓 `[[]]` 連結 + `references` / `引用方` 關鍵字
- 更新頻率：每週一次 + Phase 結束時
- commit 規範：`chore(doc): auto-update references metadata`

### §10.4 SOP 偵測 grep 語法泛化（v4-final-r2 新增、Antigravity 二輪覆核補強）

baron 已採納 §3.1「session.commit() 規則」、但 Antigravity 二輪覆核時指出**grep 語法可能漏網**：

候選變體寫法（Python 實務中存在但 §3.1 grep 未涵蓋）：
- `db.commit()`（包裝層）
- `self.session.commit()`（類別屬性）
- `await session.commit()`（非同步）
- 任何其他變體

**處置**：在 WORKFLOW-1-3 落地 WORKFLOW_SOP §5.2 database 核查時、Antigravity / Claude Code 一起把 grep 語法升級為：

```bash
# 寬鬆匹配（涵蓋所有變體）
grep -nE "\.commit\(\)" <修改檔.py> \
  | grep -v "with .*session.*begin\(\)"
# 若有命中且不在 with session.begin() 區塊內：不合規
```

具體實作細節（regex 容忍度 / 多行 with 區塊匹配 / false positive 排除）由 WORKFLOW-1-3 落地時 Claude Code 提議、Antigravity 驗證計劃時審核。

### §10.5 非 .md 治理例外規則寫入 WORKFLOW_SOP（v4-final-r2 新增、Antigravity 二輪覆核補強）

baron 已採納 §6 「非 .md 統一加日期前綴」、Antigravity 二輪覆核指出 §6 還缺一條**例外規則的明文化**：

- §6.2 表格列出非 .md 檔案類型（`.json` / `.yaml` / `.log` / `.svg` / `.png` / `.txt`）
- §6.3 寫了「非 .md 不適用 §0/§99 結構」
- **缺**：這條「免治理」例外規則須在 WORKFLOW-1-7 落地時、明確寫進 WORKFLOW_SOP 的「命名章節」內、防止未來 AI 對資料檔案產生過度約束

**處置**：在 WORKFLOW-1-7 落地時、Claude Code 在 WORKFLOW_SOP §X 命名章節新增以下段落：

```markdown
## §X.Y 非 .md 檔案治理例外

非 .md 檔案（如 .json / .yaml / .log / .svg / .png）屬「資料/圖像快照」、不屬「治理型文書」、適用以下例外規則：

- ✅ 套用 YYYY-MM-DD 命名前綴規則（同 .md）
- ❌ 不需 §0 改版規則
- ❌ 不需 §99 治理規格表
- ❌ 不需 Revision 區塊
- ❌ 不納入「被引用方」自動掃描範圍
- ❌ 不納入快取友善度評分

理由：資料 / 圖像 / 配置快照是結構化純資料、生命週期極短、靠 schema / 副檔名約束即可、不需治理 metadata。
```

具體章節編號與位置由 WORKFLOW-1-7 落地時 Claude Code 提議。

---

## §11 v4-final 不可動清單

跟 v3 §7 相同、新增：

- [ ] **v3 / v4 規劃書本身**：不重寫、本 v4-final 為「拍板整合」、未來執行階段不再回頭改 v3/v4
- [ ] **第一輪 / 第二輪雙評估報告**：歷史不竄改
- [ ] **業務代碼**（pipeline / web_server / paper_manager / static / design/* 任何 .py / .html / .css）：100% 不動
- [ ] **主 repo 目錄**：v4-final §8.2 嚴禁讀寫、Claude Code / Antigravity 兩工具都不准
- [ ] **既有 100+ 檔案的歷史命名**：不溯及既往、命名規則只對新檔生效

---

## §12 進入落地階段的提示詞

> baron 可直接複製以下提示詞給 Claude Code、啟動 WORKFLOW-1-1。

````
你好 Claude Code。

本次任務為 **WORKFLOW-1-1 落地：新增 3 份 template 檔案**、工作流類別 DOC-Refactor。

═══════════════════════════════════════════
第 1 步｜強制讀檔
═══════════════════════════════════════════

依快取友善度（穩定 → 動態）讀以下檔案：

1. .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
2. .claude-logs/templates/template_plan.md（既有、作為新 template 結構參考）
3. .claude-logs/ref/2026-05-24_WORKFLOW-1_v4-final_流程簡化與文件治理_改版規劃書.md（本次落地的權威規格）

═══════════════════════════════════════════
第 2 步｜產執行計劃
═══════════════════════════════════════════

依 v4-final §9.1 WORKFLOW-1-1 描述產執行計劃、命名：

  .claude-logs/2026-05-XX_WORKFLOW-1-1_新增三份template_plan.md

關鍵章節必含：
- §0 來源與審核軌跡（v4-final §3.1 拆分式格式）
- §1 TL;DR（概要）（v4-final §5.1 新格式）
- §7 不可動清單（嚴守工作目錄硬規則 §8.2）
- §99 治理規格與 Revision

═══════════════════════════════════════════
第 3 步｜落地 commit
═══════════════════════════════════════════

新增 3 份 template：
- .claude-logs/templates/template_revision_plan.md（依 v3 §11 + v4 §11 修正）
- .claude-logs/templates/template_file_governance.md（依 v3 §14 + v4 §5 修正）
- .claude-logs/templates/template_specification.md（依 v4 §3.1 極簡格式）

每份 template 自身用拆分式 §0/§99 結構撰寫、作為自己的試點。

═══════════════════════════════════════════
第 4 步｜產執行報告 + 建議 commit message
═══════════════════════════════════════════

產 .claude-logs/2026-05-XX_WORKFLOW-1-1_執行.md
附建議 commit message：
  feat(workflow): WORKFLOW-1-1 - 新增 3 份 template 啟動文件治理改造

═══════════════════════════════════════════
本次任務變數
═══════════════════════════════════════════

- 任務編碼：WORKFLOW-1-1
- 改版規劃書：.claude-logs/ref/2026-05-24_WORKFLOW-1_v4-final_流程簡化與文件治理_改版規劃書.md
- 工作流類別：DOC-Refactor
- 範圍：純新增 3 份 template、零代碼、零既有檔案修改

═══════════════════════════════════════════
工作目錄硬規則
═══════════════════════════════════════════

- 一律在 .claude/worktrees/hopeful-yalow-902c50/ 工作
- 嚴禁讀寫主 repo 目錄

——以上、請開始。
````

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 整合 v3-v4 全部雙評估決策、為 WORKFLOW-1 進入落地階段的最終規格 |
| **用途** | baron 給 Claude Code 提示詞時引用、Antigravity 驗證 commit 時引用 |
| **權威源** | baron 對 22 個決策的最終拍板結果（v4 §1.1-1.4 + v4-final §2.2-2.4） |
| **引用方** | v3 規劃書、v4 規劃書、第一輪雙評估報告、第二輪雙評估報告、第二輪差異比對 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動 v3/v4 既有設計、嚴禁進入落地前再次評估、嚴禁讀寫主 repo 目錄 |
| **改版觸發條件** | WORKFLOW-1-1 至 1-9 落地過程中發現原規格不可行（極少數情況） |
| **改版規則** | 新增 Revision 區塊、不重寫整檔 |
| **刪除條件** | WORKFLOW-1-9 試跑壓力測試通過、且 baron 確認後 |
| **重複防護** | 本檔不重複 v3/v4 既有設計細節、僅整合 baron 拍板結果、實作細節仍指向 v3/v4 |

### §99.2 Revision 歷程

- **v4-final-r2 (2026-05-24)**：依雙評估發現修正
  · 修問題 #1：§1 / §9 標題「9 commit」→「9+2b = 10 commit」
  · 修問題 #2：§9.1 / §9.3 WORKFLOW-1-9「五個壓力測試」→「六個壓力測試」（A-F、v3 殘留錯誤）
  · 補問題 #3：§10.4 新增「SOP 偵測 grep 語法泛化」（Antigravity 二輪覆核補強、WORKFLOW-1-3 落地處理）
  · 補問題 #4：§10.5 新增「非 .md 治理例外規則寫入 WORKFLOW_SOP」（Antigravity 二輪覆核補強、WORKFLOW-1-7 落地處理）
- **v4-final-r1 (2026-05-24)**：baron 確認標準工作流、新增 §1.5「五階段工作流」章節（含 Antigravity 驗證執行計劃環節、補 v3 雙軌制未明文化的部分）
- **v4-final (2026-05-24)**：整合 baron 對第二輪雙評估的 6 個 D1-D6 拍板 + 7 個互補增益 + 工作目錄硬規則。為進入 WORKFLOW-1-1 落地的最終規格、後續不再回頭改 v3/v4
- v4 (2026-05-24)：整合 baron 對第一輪雙評估的 16 個決策、提出混合方案
- v3 (2026-05-24)：依 baron 第三輪指正全面重寫（16 章節、708 行）
- v2 / v1 (2026-05-24)：早期版本

### §99.3 v4-final 的「最終性」聲明

> 本檔為 WORKFLOW-1 改版的**最終規格**、後續落地階段（WORKFLOW-1-1 到 1-9）一律依本檔執行、不再回頭修改 v3 / v4 / 雙評估報告等歷史檔案。
>
> 若落地過程中發現 v4-final 內任何規格不可行、處理流程：
> 1. Claude Code 在執行報告 §9 Open Questions 列出問題
> 2. baron 拍板修正方向
> 3. v4-final 加 Revision 區塊（v4-final-r1 / r2...）、不重寫本檔
> 4. 後續 commit 依 Revision 修正執行

