# template_prompt_for_sop.md — SOP 提示詞模板

> **用途**：baron 套用此模板，向 Claude Code 發出撰寫領域 SOP 手冊的指令，產出 `sop/<日期>_<領域>_SOP_手冊.md`。
> 使用前將所有 `<佔位符>` 替換為實際值，並移除本說明行。

---

## 使用說明

1. 複製以下「提示詞本體」的全部內容
2. 將 `<佔位符>` 替換為實際值
3. 提示詞歸檔：發出前先依 `prompts/README.md` 歸檔至 `.claude-logs/prompts/`
4. 發出提示詞後等待 Claude Code 產出 SOP 手冊，**不要追加任何後續指令**

---

## 提示詞本體（複製此段以下全部內容使用）

---

你現在扮演 **Claude Code**，請撰寫以下領域的 SOP 手冊。

### 📋 任務資訊

- **任務編碼**：`<任務編碼>`（例：LOGGING-4 / DB-SOP-2）
- **SOP 領域名稱**：`<領域名稱>`（例：logging / database / 快取友善度評分 / PDF 處理）
- **SOP 用途一句話**：`<描述此 SOP 的目的與適用範圍>`

### 📖 強制讀檔清單

請在開始撰寫前，必須完整閱讀以下文件（CLAUDE.md 已透過 @path 自動載入）：

```
CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md §5                    # SOP 一致性核查機制（已自動載入）
<既有相關 SOP（若有）：>
.claude-logs/sop/<既有相關 SOP 路徑>
<既有 codebase 慣例（grep 取樣）：>
<請列出需 grep 的代碼路徑，以了解現況慣例>
```

### 📐 撰寫原則（必遵守）

1. **規範性**：SOP 是最終判定依據，用語精確、無歧義
2. **可 grep 化**：每條規則必須能用一條 grep 命令核查合規性；核查指令直接附在規則後
3. **含核查指令**：每個「必須」/ 「嚴禁」條款後，附對應的 grep 驗證命令
4. **§0 / §99 拆分式結構**：依 `CLAUDE.md §1 核心規範` + `ref/WORKFLOW_SOP.md §3` 強制執行
5. **不含設計脈絡**：SOP 只記錄「規則是什麼」，不記錄「為什麼這樣設計」（那屬於 plan）

### 📄 套用拆分式 §0 / §99 結構

SOP 手冊必須包含以下章節：

```markdown
# <領域名稱> SOP 手冊

> 一行總覽（用途 / 觸發時機 / 適用工作流）

---

## §0 改版規則
- 改版觸發：§1–§N 任一規格條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 <主要規格章節 1>
...（含核查指令）

## §2 <主要規格章節 2>
...（含核查指令）

## §N <違規處理>
暫停落地 → 加入 _plan.md §9 Open Questions → 等 baron 拍板

---

## §99 治理規格

### §99.1 治理規格表
（套用 template_file_governance.md 格式）

### §99.2 Revision 歷程
- v1 (YYYY-MM-DD)：初版
```

### 📁 產出規格

- **產出路徑**：`.claude-logs/sop/<YYYY-MM-DD>_<領域>_SOP_手冊.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`
- **行數建議**：≤ 150 行（SOP 應精煉，不冗長）

---

### 🛑 停止指令

**產出 SOP 手冊後必須立即停止。**

嚴禁：
- ❌ 繼續修改業務代碼以符合 SOP（SOP 是規格文件，不是執行報告）
- ❌ 自發跳到下一個任務或 Commit
- ❌ 自發執行 `git commit` 或 `git push`

---

## 提示詞歸檔指令

發出提示詞前，請執行：
```bash
# 歸檔本提示詞
cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_sop_提示詞.md
echo "- $(date +%Y-%m-%d) | <任務編碼> | sop | 撰寫 <領域> SOP 手冊" >> .claude-logs/prompts/INDEX.md
```

依 `.claude-logs/prompts/README.md` 完整規則處理（敏感資訊需打碼）。
