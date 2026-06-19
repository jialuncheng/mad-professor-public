# PIPE-SYNC-4 C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 14:23 |
| 任務代號 | PIPE-SYNC-4 C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_C2_執行.md` |
| 觸發情境 | baron 確認 C1 完成、下達 C2 執行指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C2（PIPE-SPEC 回灌·D5-D8.1）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / plan（全局策略 z）/ tasks（§8 C2）
- 三防線：物理（§7 不可動·特別 D8.1 嚴禁改 §1.3 L140 + 四凍結合約結構）/ 測試（§6.2 grep）/ 文件（不自發 commit）
- 備份：`cp baton/2026-06-01_PIPE-SPEC_..._specification.md archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak`
- 實作（tasks §8 C2）：
  - D5 新增 §1.2.5 section_engine 契約章（9 介面 + 鐵律 + consumer 列表）
  - D5b 新增 §1.2.4 MetaNormalizer 契約章（normalize_fields + 三路分流 + schema 表 + 交易邊界）
  - D6 §1.1.1 登記 LiteDoc 旁路欄位（date/url/publisher/translated_title）
  - D7 「三大共用真理源」→「共用真理源家族」措辭
  - D8 §99.2 v8 Revision
  - D8.1 確認 §1.3 L140 及四凍結合約結構未改
- 驗收：§6.2 grep + 零業務代碼旁證
- TODO：C2 ✅ / C3 🟡 + hash 自癒
- 產出：`baton/..._C2_執行.md`（template_execution、§1 對齊欄 + §自評）;msg → `/tmp/PIPE-SYNC-4_C2_msg.txt`
- 版控：**SPEC 本體 baton 就地不版控、僅 .bak→archive git add**;執行報告嚴禁 git add
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 文件 / 自發 commit

## 偏差註記
- SPEC 為 gitignored baton-resident（PIPE-SYNC-2 195e12b 先例）→ 本體就地改、不 git add、僅 .bak→archive 入版控作審計。
- msg 草稿補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
