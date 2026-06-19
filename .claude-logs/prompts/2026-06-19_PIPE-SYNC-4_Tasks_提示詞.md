# PIPE-SYNC-4 Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 13:48 |
| 任務代號 | PIPE-SYNC-4 Tasks |
| 觸發 Commit | PIPE-SYNC-4-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_litedoc與section_engine落地回灌母plan與SPEC_tasks.md` |
| 觸發情境 | baron 同意 plan v3 規格、下達任務拆分指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、將 PIPE-SYNC-4 plan v3 拆為可執行 Commit 清單。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / TODO / plan / template_tasks
- 工作目錄硬規則：唯一 worktree、嚴禁主 repo、嚴禁動業務代碼（純文件回灌）、產出先 baton/
- §0.5 成果盤點置開頭;§8 每 Commit 六維度表;§1 TL;DR 中文括號命名
- 不給 commit 建議（依 D1-D9+D5b drift 範疇自主拆分）;最後 Commit 必為 checkout（才 mv baton→正式目錄 + git add）;各 Commit 產 baton 執行報告（template_execution）
- 同步 TODO（高優先最前、🟡 WIP + Commit 清單）
- 停止：產 tasks + 更新 TODO 後立即停;嚴禁產 _執行.md / 動業務代碼 / 自發 commit

## 偏差註記
- plan v3：D1-D4 master plan v10〔版控〕/ D5 section_engine §1.2.5 + D5b MetaNormalizer §1.2.4 + D6 litedoc 旁路登記 + D7 家族措辭 + D8 bump v8〔SPEC·baton 就地〕/ D9 HOW_TO_ADD〔版控·B 軌範式+A/B 對比+U2.1 映射〕;§9 五 OQ 全 🟢;§7.2 純 DOC 豁免。
- SPEC 版控機制依 PIPE-SYNC-2/3 先例（SPEC 長駐 baton、.bak→archive、本體就地處理）;tasks 須明示。
