# PIPE-SYNC-2 C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 01:54 |
| 任務代號 | PIPE-SYNC-2 C2 |
| 觸發 Commit | C2 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SYNC-2_..._tasks.md` |
| 觸發情境 | baron 確認 C1 後，下達 C2 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SYNC-2 / C2 — SPEC Sync / DOC-Refactor；tasks §8 C2

### 執行命令（tasks §8 C2）
① 改前備份 SPEC → archive/2026-06-11_PIPE-SYNC-2_C2_PIPE-SPEC_specification.md.bak
② 就地補註 `baton/2026-06-01_PIPE-SPEC_..._specification.md`（`<!-- === [PIPE-SYNC-2 C2 START/END] === -->` + §99.2 v6）：
   - U3：§1.1② + §1.4.1 凍結三句（key=原文標題 path；P2 產 _collect_summary_targets/P3 帶 slot key→summary_key/P4 取 _walk 首選 summary_key 同基準；譯後 title 僅顯示）逐字對齊 WORKFLOW_SOP §7.1
   - U4：P3 章補 zh 來源規格（跳過翻譯、仍建 per-section rag_sections、無 section 退兜底；五路通用 edge path）
   - U5：§1.3 附近新增 §1.3.1 Vision 解析共用規格三原則（忠實轉錄鐵律/temp=0/非確定性註記；Schema 級約束留 PIPE-VISUAL）
   - U6：L146 樣例 gemini-embedding-2 → gemini-embedding-001（MODEL-11、不可混庫）
   - U7：§1.4.1 補 rag_tree 由 rag_indexer.build_rag_tree 自建（key_map=chunk Header=node_key→path）
   - U8：§1.3 resume 行 P1 欄補 opt-out TextTiling；U9：§1.2.3.1 末補受限並行句；U10：resume 行尾還原三件套註
- 物理防線：四凍結合約欄位結構不得動、僅補註與樣例字面；嚴禁動代碼

### TODO 同步
- C2 ✅、C3 🟡 WIP；git log 自癒回填

### 產出
- 執行報告 baton/2026-06-11_PIPE-SYNC-2_C2_執行.md（暫存、不入版控）；§5 貼 §6.2 七條 grep

### §8 baron 命令
- git add：.bak + 2 prompts + TODO（嚴禁 baton 文件、SPEC 本體不入版控）；msg → /tmp/PIPE-SYNC-2_C2_msg.txt

### 停止
- 產出 C2_執行.md 後立即停止；不續 C3、不自發 commit/push
