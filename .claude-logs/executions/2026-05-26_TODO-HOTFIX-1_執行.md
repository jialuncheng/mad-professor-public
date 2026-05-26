# TODO-HOTFIX-1 — 執行報告：TODO.md RAG 系列狀態修復

---

**任務代號**：TODO-HOTFIX-1  
**執行日期**：2026-05-26  
**依據規劃**：`.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md`  
**Git commit hash**：`待 baron 執行後回填`  
**狀態**：Completed (Commit TODO-HOTFIX-1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：
  - `## 🟡 進行中` active 區有 2 個已完成任務殘留（RAG-1 Phase 2 + Bug Fix 系列 bullet block）
  - RAG-1 Bug Fix 系列 8 個子條目（BUG-F1~F6 + BUG-B1~B2）以 bullet 子列格式殘留於 active 區，非標準已完成表格
  - BUG-B1 / BUG-B2 的 hash 欄為「待 push 後回填」（hash 缺失）
  - 第 213 行有孤兒標題 `### Phase 4.X? RAG-1 Bug Fix 系列...` 無對應表格
  - RAG-11 / RAG-12 以子條目形式嵌於 Bug Fix block，未獨立為主條目
  - `## ✅ 已完成` 缺少 Bug Fix 系列標準表格
  
- **完成狀態**：
  - `## ✅ 已完成` 新增 `Phase 4.X? RAG-1 Bug Fix 系列` 標準表格（8 commits、所有 hash 填入）
  - BUG-B1 補填 `a35a720`、BUG-B2 補填 `94ed27d`（via git log 確認）
  - Active 區損毀 block（第 198–213 行）徹底清除
  - RAG-11 / RAG-12 獨立為 `### 🔴 高優先` 的 `⬜` 主條目
  - `## 索引（依類別）` → `### RAG` 段更新（計數 7→9，新增 3 條目）
  - 業務代碼零改動

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| TODO-HOTFIX-1 | TODO.md 修復：Bug Fix 已完成表格 + active 清除 + RAG-11/12 獨立 | `待 baron 執行後回填` |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `.claude-logs/TODO.md` | `.claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak` | 4 項修法（A+B+C+D） |
| 新建 | `.claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak` | — | 修改前備份（納入版控） |
| 新建（暫存） | `.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md` | — | 階段 1 規劃書（baton/ 暫存，待 Check 歸檔） |
| 新建（暫存） | `.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_執行.md` | — | 本執行報告（baton/ 暫存，待 Check 歸檔） |

---

## §4 修法說明

### §4.1 修法 A — ✅ 已完成區建立 Bug Fix 標準表格

**位置**：`### Phase 4.X? RAG-1 Phase 2 Hashtag RAG 路由...` 表格（第 84–107 行）之後，`### Phase 4.X? RAG-1 前端 UI Fixes...` 之前。

新增段落（第 109–124 行）：
- `### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）`
- 8 列標準表格，含所有確認 hash
- 關鍵補填：BUG-B1 `a35a720`、BUG-B2 `94ed27d`（原為「待 push 後回填」）

### §4.2 修法 B — Active 區損毀 block 清除

刪除原 `## 🟡 進行中` 第 198–213 行（共 15 行）：
- 第 198–199 行：`✅ ~~**RAG-1 Phase 2...**~~` 殘留條目（已在 ✅ 區）
- 第 200–211 行：`✅ ~~**RAG-1 Bug Fix 系列**~~` 父行 + 8 子條目 + RAG-11/12 子條目 + 收官摘要
- 第 213 行：`### Phase 4.X? RAG-1 Bug Fix 系列...` 孤兒標題

### §4.3 修法 C — RAG-11 / RAG-12 獨立主條目

在 `### 🔴 高優先` → QUEUE-1 條目之後，新增兩個獨立 `⬜` 主條目：
- `⬜ **RAG-11 reload SSE 還原**`（問題描述 + 工時 + 依賴）
- `⬜ **RAG-12 LaTeX KaTeX 渲染支援**`（問題描述 + 工時 + 依賴）

### §4.4 修法 D — 索引 `### RAG` 段更新

- 計數：`RAG（7 項 active）` → `RAG（9 項 active）`
- 新增：`✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~` 已完成條目
- 新增：`⬜ RAG-11 reload SSE 還原（高、需獨立 plan）`
- 新增：`⬜ RAG-12 LaTeX KaTeX 渲染支援（高、需獨立 plan）`

---

## §5 測試結果

### §5.1 V1：BUG-F1 / BUG-B1 在 ✅ 已完成區命中

```bash
$ grep -n "BUG-F1\|BUG-B1" .claude-logs/TODO.md
109:### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）
113:| BUG-F1 | 前端 micro fix 包 — tag fallback / placeholder 斷行 / export-btn / --content-max-w（Bug 1/3/4/5、5 pytest） | `9877e54` |
119:| BUG-B1 | 後端 abstract fallback — A 側路 translate_text + B regex 擴中日文（Bug 8、28 pytest） | `a35a720` |
423:- ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
```
✅ 命中在 ✅ 已完成區（第 109/113/119 行）+ 索引區（第 423 行）

### §5.2 V2：BUG-B1 `a35a720` / BUG-B2 `94ed27d` hash 存在

```bash
$ grep -n "a35a720\|94ed27d" .claude-logs/TODO.md
119:| BUG-B1 | 後端 abstract fallback... | `a35a720` |
120:| BUG-B2 | 後端 blockquote→list... | `94ed27d` |
```
✅ 兩個原「待回填」hash 已補填，各 1 命中

### §5.3 V3：Active 區無 `~~**RAG-1` 殘留

```bash
$ grep -n "~~\*\*RAG-1" .claude-logs/TODO.md
（0 命中 — active 區無殘留 ✅）
```
✅ Active 區完全清除

### §5.4 V4：孤兒 heading 已移除，僅剩 ✅ 已完成標題

```bash
$ grep -n "Phase 4\.X.*RAG-1 Bug Fix" .claude-logs/TODO.md
109:### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）
```
✅ 1 命中，且位於 `## ✅ 已完成` 區（第 109 行）；孤兒 heading 已刪除

### §5.5 V5：RAG-11 / RAG-12 出現為獨立條目

```bash
$ grep -n "RAG-11\|RAG-12" .claude-logs/TODO.md
123:> ...Bug 6 / Bug 9 延後為 RAG-11 / RAG-12
214:- ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
219:- ⬜ **RAG-12 LaTeX KaTeX 渲染支援**（Bug 9、需獨立 plan 評估）
429:- ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
430:- ⬜ RAG-12 LaTeX KaTeX 渲染支援（高、需獨立 plan）
```
✅ 第 214/219 行為 🔴 高優先區獨立主條目；第 429/430 行為索引區條目

### §5.6 V6：業務代碼零改動

```bash
$ git diff --cached --name-only | grep -E "\.py$|\.html$|\.js$"
（0 命中 — 業務代碼零改動 ✅）
```
✅ DOC-Hotfix，業務代碼零改動

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` | ✅ 未觸碰 |
| `static/*` | ✅ 未觸碰 |
| 主 repo 目錄（worktree 父目錄） | ✅ 未讀寫 |
| 既有 100+ 歷史 `.claude-logs/` 文件（TODO.md 除外） | ✅ 未改動 |
| `templates/template_hotfix.md` | ✅ 未觸碰 |

---

## §7 銜接

- **baton/ 暫存狀態**：
  - `2026-05-26_TODO-HOTFIX-1_hotfix.md`（規劃書）— 待 Check 歸檔至 `hotfixes/`
  - `2026-05-26_TODO-HOTFIX-1_執行.md`（本報告）— 待 Check 歸檔至 `executions/`
- **備份檔**：`archive/2026-05-26_TODO-HOTFIX-1.md.bak` — 已入版控（`git add` 清單中）
- **下一步（baron 決定）**：
  1. baron 執行 §8 commit 命令
  2. 如需進行 Check 驗收歸檔，向 Claude Code 發出 Check 指令
  3. RAG-11 / RAG-12 已就位為 `⬜` 高優先任務，baron 可隨時開 plan

---

## §8 baron 執行命令

```bash
# 1. git add 追蹤清單
git add .claude-logs/TODO.md
git add .claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak

# 2. commit message 草稿（已寫入 /tmp/TODO-HOTFIX-1_msg.txt）
git commit -F /tmp/TODO-HOTFIX-1_msg.txt
```

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | TODO.md RAG 系列狀態修復執行紀錄（Hash 補填 + 格式修復 + RAG-11/12 獨立） |
| 用途 | baron 手動 commit 依據；Check 階段 Conformance 比對 |
| 權威源 | 本檔 §1–§8 |
| 引用方 | Check 階段驗收 |
| 被引用方 | `<由 Antigravity 自動掃描注入>` |
| 約束事項 | 暫存於 baton/；Check 後 mv → executions/ + git add |
| 刪除條件 | 不刪（歸檔至 executions/ 永久保留） |
| 重複防護 | 修復邏輯唯一源在 hotfix.md；本檔僅記錄執行結果 |

### §99.2 Revision 歷程

- v1 (2026-05-26)：初版（TODO-HOTFIX-1 執行完成）
