````markdown
# 2026-07-12 — GOV-PATH-FIX hotfix 提示詞

> **收到時間**：2026-07-12（UTC+8）
> **任務代號**：GOV-PATH-FIX（DOC-Refactor·hotfix 文件形式）
> **觸發 commit**：GOV-PATH-FIX-hotfix
> **相關產出檔案**：.claude-logs/baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md
> **觸發情境**：查核 SEC-HARDEN Tasks 提示詞帶已刪除 worktree 路徑之來源 → 發現 CONTEXT-1 C2 更新 CLAUDE.md §3 為主 repo 雙視圖時，漏改 3 個下游治理檔（template_prompt_for_tasks.md / framework §9.2 / GOVERNANCE_OVERVIEW.md）仍硬編 `hopeful-yalow-902c50`。baron 下令開 GOV-PATH-FIX DOC-Refactor、以 hotfix 文件形式修正。

---

## 完整提示詞

```
開一個 DOC-Refactor
GOV-PATH-FIX
針對以上面內容做一個hotfix文件
存檔路徑baton/

依據
template_hotfix.md

詳細說明原因
程式碼也加入文件
包含commit
```

> 上文「以上面內容」＝本 session 稽核結論：`.claude-logs/templates/template_prompt_for_tasks.md:67`（元凶·每產一次 Tasks 提示詞複製一次死 worktree 路徑）+ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md:282`（§9.2 硬編）+ `ref/GOVERNANCE_OVERVIEW.md`（6 條 file:/// 死路徑連結）；權威源 CLAUDE.md §3 已於 CONTEXT-1 C2（v5）改主 repo 雙視圖、僅此 3 下游檔漏改。歷史檔（prompts/executions/tasks/plans/hotfixes/archive）依 §2 不溯及既往、不動。

---

## 執行結果摘要

- ✅ 產出 hotfix 文件至 baton/（真因 + 3 檔 diff + commit 草稿）
- 改動檔案（文件產出階段）：1（prompts 歸檔）+ hotfix 文件暫存 baton/；治理檔實檔未動（diff 僅記錄）
- commit / push：無（§1.3 baron 手動）

---

## 完整提示詞（Run 執行階段·2026-07-12 08:24）

> 前段為「文件產出階段」提示詞；本段為 baron 核准 hotfix 規劃後之「執行階段」提示詞（非破壞性追加、保留兩階段）。

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-12 08:24 | 任務代號 | GOV-PATH-FIX hotfix | 觸發 Commit | GOV-PATH-FIX-hotfix |
| 相關產出檔案 | .claude-logs/baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md |
| 觸發情境 | baron 核准 hotfix 規劃後下達執行；校正 3 個下游治理檔殘留的已刪除 worktree 路徑 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成）
寫入本檔 + 更新 INDEX（分類 + 時間排序首行·超 15 刪最舊）→ 回覆「✅ 提示詞已歸檔」後繼續。

你現在扮演 Claude Code，執行單一 Commit GOV-PATH-FIX-hotfix（DOC-Refactor）。
依據：baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md（套用 template_hotfix）。

### 工作目錄與授權
主 repo 就地（CLAUDE.md §3）；授權限 CLAUDE.md + .claude-logs/ 特定治理配置檔；嚴禁業務碼（*.py/static/tests）；
hotfix 規劃書留 baton、本 commit **嚴禁 git add**（待收官 checkout 才歸檔 hotfixes/）。

### 執行命令（守三防線）
1. 物理防線：歷史歸檔與 prompts 不溯及既往、不動。
2. 測試防線：regression grep（3 活躍源無殘留死 worktree 路徑 + E2E 相對路徑可連結）。
3. 文件防線：commit/push 由 baron 手動。

### 備份規則（修改前 cp）
cp template_prompt_for_tasks.md → archive/2026-07-12_GOV-PATH-FIX_template_prompt_for_tasks.md.bak
cp PROJECT_PROGRESS_CONTROL_FRAMEWORK.md → archive/2026-07-12_GOV-PATH-FIX_framework.md.bak
cp GOVERNANCE_OVERVIEW.md → archive/2026-07-12_GOV-PATH-FIX_GOVERNANCE_OVERVIEW.md.bak

### 同步更新 TODO.md
1. ## 🟡 進行中 最上方新增 hotfix 條目標 ✅（GOV-PATH-FIX 校正下游治理檔 stale worktree 路徑）
2. git log 掃描替換「待 baron 回填」

### 產出規格
修復紀錄 baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md（既存·嚴禁 git add·維持 baton 暫存）；模板 template_hotfix.md。
§8 baron 執行命令：msg 寫 /tmp/GOV-PATH-FIX_msg.txt；git add 3 治理檔 + 3 .bak；嚴禁 git add baton hotfix 檔。

### 停止指令
執行完修改並產出最終紀錄後立即停止。嚴禁：續跑收官/其他任務 / 改未列入細節的檔 / 自發 git commit|push。
```

### Run 階段執行結果摘要
- ✅ 校正 3 下游治理檔（template_prompt_for_tasks.md 工作目錄硬規則 / framework §9.2 去硬編 worktree / GOVERNANCE_OVERVIEW.md 導航連結改相對路徑）
- 改動：3 治理檔 + TODO.md（+ 3 .bak）；hotfix 規劃書留 baton 不 git add
- commit/push：無（§1.3 baron 手動）

---

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
