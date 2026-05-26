# template_prompt_for_plan.md — 規劃提示詞模板

> **用途**：baron / Antigravity / Claude Design 套用此模板，向 AI 發出階段 1 規劃指令，產出純規格 `_plan.md`。
> 使用前將所有 `<佔位符>` 替換為實際值，並移除本說明行。

---

## 使用說明

1. 複製以下「提示詞本體」的全部內容
2. 將 `<佔位符>` 替換為實際值
3. 提示詞歸檔：發出前先依 `prompts/README.md` 歸檔至 `.claude-logs/prompts/`
4. 發出提示詞後等待 AI 產出 plan.md，**不要追加任何後續指令**

---

## 提示詞本體（複製此段以下全部內容使用）

---

你現在扮演 **規劃顧問**，請依以下指令產出任務規格計畫書。

### 📋 任務資訊

- **任務編碼**：`<任務編碼>`（例：RAG-10 / CHAT-4 / MODEL-11）
- **任務簡述**：`<一句話描述任務目標與動機>`
- **工作流類別**：`<FE-Refactor | BE-Refactor | DOC-Refactor | FE-Hotfix | BE-Hotfix>`

### 📖 強制讀檔清單

請在開始規劃前，必須完整閱讀以下文件（CLAUDE.md 已透過 @path 自動載入）：

```
CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md # 框架規範（已自動載入）
<若工作流類別為 BE-Refactor / BE-Hotfix，必讀：>
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md
.claude-logs/sop/2026-05-23_database_SOP_手冊.md
<若有相關既有 plan，請補充：>
.claude-logs/plans/<相關既有 plan 路徑>
```

### 📐 撰寫原則（必遵守）

1. **純規格原則**：plan.md 只記錄「現況 + 問題 + 解法 + 驗證」，嚴禁混入設計脈絡、演進過程、拍板記錄
2. **What it should be**：描述目標狀態，不含 Why（Why 屬於設計決策，由 baron 主導）
3. **證據驅動**：所有「現況盤點」必須附 grep 指令 + 真實行號，不依賴記憶
4. **Open Questions 三欄**：plan §7 Open Questions 必含「問題 + 推薦答案 + 理由」三欄，baron 拍板後才進 execution

### 📄 套用模板結構

請嚴格套用 `.claude-logs/templates/template_plan.md` 的結構，產出 plan 必須包含以下章節：

| 章節 | 要求 |
|---|---|
| **頂部元數據** | 任務編碼 / 日期 / 工作流類別 / 狀態 |
| **§1 TL;DR** | 挑戰（三行內）/ 解法摘要 / 影響範圍 / 不可動清單指引 |
| **§2 目標規格** | 最終狀態的可驗證描述（無 why） |
| **§3 現況與證據** | grep 指令 + 真實行號；代碼 snippet（若有）|
| **§4 不可動清單** | 明確列出禁止改動的檔案 / 函式 / API |
| **§5 規格依據** | 引用 SOP / 框架章節 / 既有 plan |
| **§6 驗證計畫** | pytest 指令 + E2E 手動核查步驟 + grep 驗收條件 |
| **§7 Open Questions** | 問題 + 推薦答案 + 理由（三欄表格）|
| **§99 治理規格** | 套用 template_file_governance.md 格式 |

### 📁 產出規格

- **產出路徑**：`.claude-logs/plans/<YYYY-MM-DD>_<任務編碼>_<描述>_plan.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 plan.md 後必須立即停止。**

嚴禁：
- ❌ 繼續拆分 commit（階段 2 由 Claude Code 負責）
- ❌ 動任何業務代碼（plan 階段只能 view / grep / 文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`

---

## 提示詞歸檔指令

發出提示詞前，請執行：
```bash
# 1. 新建歸檔檔案
cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_plan_提示詞.md

# 2. 更新索引
echo "- $(date +%Y-%m-%d) | <任務編碼> | plan | <一句話描述>" >> .claude-logs/prompts/INDEX.md
```

依 `.claude-logs/prompts/README.md` 完整規則處理（敏感資訊需打碼）。
