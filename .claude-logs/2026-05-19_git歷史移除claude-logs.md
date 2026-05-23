# 2026-05-19 從 git 歷史完全移除 .claude-logs/（歷史重寫）

非業務邏輯變更；只處理 .claude-logs/ 與 .gitignore。

## 環境關鍵點
- 共用 object db 的 linked worktree：
  - 主 checkout /home/baroncheng/mad-professor-public → gemini-refactor @ 4e9892f
  - 本 worktree → claude/hopeful-yalow-902c50
- filter-repo 未安裝；且 filter-repo 在共用 worktree/非 fresh clone 會拒跑或半途中止 → 風險高。
- 決策：用內建 `git filter-branch`，且**只重寫本分支**（`-- claude/hopeful-yalow-902c50`，不用 --all），
  保護主 worktree 的 gemini-refactor 不被波及。

## 步驟
1. 備份本地 .claude-logs → /tmp/claude-logs-backup（13 檔）
2. .gitignore 加入 `.claude-logs/`（原有 .claude/ 條目不動）
3. 先 commit .gitignore（filter-branch 需乾淨工作樹）→ e8166b6
4. `FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter \
   'git rm -rf --cached --ignore-unmatch .claude-logs' --prune-empty -- claude/hopeful-yalow-902c50`
5. 清理：refs/original 刪除、reflog expire --expire=now --all、git gc --prune=now
6. 從備份還原本地 .claude-logs（現為 gitignore 忽略的未追蹤檔）
7. 強制推送 `git push origin claude/hopeful-yalow-902c50:gemini-refactor --force`

## 用了哪個工具
git filter-branch（內建；filter-repo 不可用且在共用 worktree 不安全）。
範圍限定當前分支，未用 --all。

## 移除前後對比
- 重寫前：184 commits；8 個 commit 動過 .claude-logs；.claude-logs 版控檔 13。
- 加 .gitignore commit 後 185；filter-branch --prune-empty 未刪任何 commit
  （8 個 phase commit 皆同時含程式碼變更，非 log-only）→ 重寫後仍 185。
- 重寫後：git ls-files .claude-logs = 0；git log -- .claude-logs/ = 空。
- 強制推送：3850036...a3de37b（forced update）；分支所有 hash 已變。

## 本地檔案
完整保留：ls .claude-logs/ = 13 檔（含本檔將成 14）。git status 乾淨（已被 .gitignore 忽略）。

## 遠端
- origin/gemini-refactor tree 無 .claude-logs ✅
- 遠端歷史動過 .claude-logs 的 commit 數 = 0 ✅
- 遠端 HEAD = a3de37b（重寫後）

## 主 worktree 未受影響
git worktree list 確認 /home/baroncheng/mad-professor-public 仍 gemini-refactor @ 4e9892f（未動）。

## 遺留風險
1. GitHub 端：force push 後舊 commit（含 .claude-logs）可能仍存在於 GitHub 內部快取/
   pull request refs/事件一段時間；要徹底永久清除需聯絡 GitHub Support 或等其 GC。
   一般情況下 force push 後網頁與 clone 已看不到。
2. 任何「舊 clone / 既有 PR / fork」仍可能保有舊歷史（本案單一 collaborator，風險可控）。
3. 全分支 commit hash 已改寫；若他處有以舊 hash 為基礎的引用會錯亂（單人使用，無此情形）。
4. 主 worktree 的本地 gemini-refactor(4e9892f) 與遠端(a3de37b) 已分叉；
   下次在主 worktree 操作該分支前需自行 reset/對齊（非本任務範圍，僅提醒）。
5. /tmp/claude-logs-backup 為臨時備份，重啟環境會消失；本地 .claude-logs/ 已還原為主來源。

## 結論
.claude-logs/ 已從本分支 git 歷史完全移除並 force push；本地內容完整保留且日後不再入版控；
主 worktree 其他分支未受影響。狀態一致、任務完成。
