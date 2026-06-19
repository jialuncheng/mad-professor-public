# PIPE-SYNC-4 C3 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 14:34 |
| 任務代號 | PIPE-SYNC-4 C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_C3_執行.md` |
| 觸發情境 | baron 確認 C2 完成、下達 C3 執行指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C3（HOW_TO_ADD B 軌範式·D9）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / plan（全局策略 z）/ tasks（§8 C3）
- 三防線：物理（§7 不可動·A 軌既有章不動）/ 測試（§6.3 grep）/ 文件（不自發 commit）
- 備份：`cp docs/HOW_TO_ADD_DOC_TYPE.md archive/2026-06-19_PIPE-SYNC-4_C3_HOW_TO_ADD_DOC_TYPE.md.bak`
- 實作（tasks §8 C3）：補一節「B 軌（PIPE 五路）加 doc_type」——
  - 裝飾器機制（@PipelineFactory.register + pipelines/__init__ import 觸發 + 四 Phase 消費共用真理源〔section_engine + DomainNormalizer/Glossary/Translator + rag_indexer〕+ raw_metadata 旁路 + §7.2 key-changing 整合測試）
  - A/B 機制對比（B 軌裝飾器插件 vs A 軌 pipeline_core.py 硬分支〔即將絞殺〕、下游嚴禁寫 A 軌分支）
  - U2.1 DocAnalyzer 映射規範（扁平短文 litedoc/unknown 安全映射避免 fallback academic、深結構文體對齊既有 structure/heading_fix prompts）
  - A 軌既有章不動、`<!-- === [PIPE-SYNC-4 C3] === -->` 包裹新增節
- 驗收：§6.3 grep（PipelineFactory.register/section_engine/B 軌/A 軌 由 0→≥1；DocAnalyzer/安全映射/U2.1）
- TODO：C3 ✅ / C4 🟡 + hash 自癒
- 產出：`baton/..._C3_執行.md`（template_execution、§1 對齊欄 + §自評）;msg → `/tmp/PIPE-SYNC-4_C3_msg.txt`
- 版控：HOW_TO_ADD 版控直接 git add + .bak;執行報告嚴禁 git add
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 文件 / 自發 commit

## 偏差註記
- msg 草稿補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
