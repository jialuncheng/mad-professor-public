# WORKFLOW-2 Tasks — 任務拆分 執行報告

---

**任務代號**：WORKFLOW-2 Tasks（Commit 拆分階段）
**執行日期**：2026-05-26
**依據規劃**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`
**次級參考**：`.claude-logs/templates/template_tasks.md`
**Git commit hash**：`待 baron 回填`
**狀態**：Completed (Tasks)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：WORKFLOW-2 plan.md 已完成，baron 審查 plan §7 Open Questions 後拍板（Q1 採摘要重建、Q3 採獨立維度五），下達 Tasks 拆分指令。
- **完成狀態**：產出 `baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`，含 5 個 Commit（C1~C5）六維度完整拆分表格（§0.5 成果盤點 + §8 推薦 Commit 拆分）；同步更新 `TODO.md` 新增 WORKFLOW-2 🟡 WIP 條目於 🔴 高優先最前方；更新 `prompts/INDEX.md` 補登 WORKFLOW-2 Tasks 提示詞條目。業務代碼零改動。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| WORKFLOW-2-Tasks | 產出 tasks.md + TODO.md WIP 條目 + INDEX.md 更新 | `待 baron 回填` |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md` | — | 5 Commit 六維度拆分清單（C1~C5）|
| 修改 | `.claude-logs/TODO.md` | — | 🔴 高優先頂部新增 WORKFLOW-2 🟡 WIP 條目（含 C1~C5 子細節）|
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 最後更新行更新；WORKFLOW-2 系列補登 Plan + Tasks 條目；依時間排序新增 2 筆至 15 筆 |
| 新建 | `.claude-logs/prompts/2026-05-27_WORKFLOW-2_Tasks_提示詞.md` | — | WORKFLOW-2 Tasks 提示詞歸檔（R1 新防線首次實戰） |

---

## §4 修法說明

### §4.1 `tasks.md` — WORKFLOW-2 5 Commit 拆分

依 plan §2.1~§2.5 規格，拆分為 5 個原子 Commit：
- C1：R1 五大提示詞模板自愈歸檔防線（修改 5 個 template_prompt_for_*.md）
- C2：R2 Check Conformance 維度四+五（修改 template_prompt_for_check.md）
- C3：R3+R4 SOP 備份暫存鐵律 + §8 重構（修改 WORKFLOW_SOP.md + template_execution.md + template_tasks.md）
- C4：R5a 歷史 9 份提示詞物理補建（新建 9 個 prompts/*.md）
- C5：R5b INDEX.md 雙向對齊 + baton 收官歸檔（修改 INDEX.md + mv baton → plans/tasks）

每個 Commit 含六維度表格：影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節。

### §4.2 `TODO.md` — WORKFLOW-2 WIP 條目新增

在 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方插入：
```
- 🟡 **WORKFLOW-2 流程模板重構與提示詞自動歸檔**（`baton/tasks.md`）
  - C1：R1 五大提示詞模板自愈歸檔防線
  - C2：R2 Check Conformance 維度四+五
  - C3：R3+R4 SOP 備份暫存鐵律 + §8 重構
  - C4：R5a 歷史 9 份提示詞物理補建
  - C5：R5b INDEX.md 雙向對齊收官
  - 工時：5 個 commits；依賴：無
```

---

## §5 測試結果

### §5.1 本地改動狀態確認

```bash
$ git status -s
?? .claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md
 M .claude-logs/TODO.md
 M .claude-logs/prompts/INDEX.md
?? .claude-logs/prompts/2026-05-27_WORKFLOW-2_Tasks_提示詞.md
```

（本 Commit 為純文件改動，baton/ 暫存不入版控）

### §5.2 驗收結果

```bash
$ wc -l .claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md
248  （任務規模合理）

$ grep -c "###.*C[1-5]" .claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md
5  （5 個 Commit 六維度表格均存在）

$ grep "🟡.*WORKFLOW-2" .claude-logs/TODO.md
- 🟡 **WORKFLOW-2 流程模板重構與提示詞自動歸檔**...  ✅ 命中
```

### §5.3 SOP 一致性核查

DOC-Refactor 工作流，無 .py 改動，跳過（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 業務代碼（`pipeline_core.py` 等）| [x] ✅ 未觸碰 |
| 主 repo 目錄（worktree 父目錄）| [x] ✅ 未讀寫 |
| `prompts/` 既有 28 個 .md 文件 | [x] ✅ 未改動 |
| `CLAUDE.md` §1–§5 | [x] ✅ 未改動 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存於 baton/；tasks.md 暫存於 baton/；待 C5 收官時一次性 mv + git add 歸檔至 tasks/ 和 executions/。
- **下一步**：baron 審查 tasks.md 合規後，下達 C1 Run 指令執行。
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 本 Commit 為 Tasks 拆分，改動僅有 TODO.md + INDEX.md + baton/tasks.md（baton 不入版控）
# baron 可在 C1~C5 全部完成後統一 commit，或單獨 commit 此階段產出：

# 若單獨 commit Tasks 階段：
git add .claude-logs/TODO.md .claude-logs/prompts/INDEX.md
git add ".claude-logs/prompts/2026-05-27_WORKFLOW-2_Tasks_提示詞.md"

cat > /tmp/WORKFLOW-2_Tasks_msg.txt << 'EOF'
DOC-Refactor: WORKFLOW-2 Tasks — 五大漏洞修補 Commit 拆分清單

- 產出 baton/tasks.md：5 Commit 六維度完整拆分（C1 五模板自愈 / C2 Check 維度四五 / C3 SOP 鐵律 / C4 歷史補建 / C5 INDEX 收官）
- TODO.md：🔴 高優先頂部新增 WORKFLOW-2 🟡 WIP 條目（C1~C5 子細節）
- INDEX.md：補登 WORKFLOW-2 Plan + Tasks 提示詞條目，依時間排序維持 15 筆

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

git commit -F /tmp/WORKFLOW-2_Tasks_msg.txt
```

> ℹ️ 本報告為補發（Tasks 階段原未產出執行報告，於 C1 Run 階段補建）。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 WORKFLOW-2 Tasks 階段（任務拆分）的產出與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C5 收官時 Conformance 核對；核對後 mv → executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | WORKFLOW-2 Check 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 本報告為補發；暫存於 baton/，C5 收官前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 Tasks 拆分階段唯一執行記錄，不重複 tasks.md 中的六維度實作細節 |

### §99.2 Revision 歷程

- v1 (2026-05-27)：補發建立（WORKFLOW-2 C1 Run 階段追溯產出，記錄 Tasks 拆分階段成果）
