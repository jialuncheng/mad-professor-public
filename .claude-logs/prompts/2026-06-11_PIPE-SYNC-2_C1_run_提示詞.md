# PIPE-SYNC-2 C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 01:46 |
| 任務代號 | PIPE-SYNC-2 C1 |
| 觸發 Commit | C1 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SYNC-2_..._tasks.md` |
| 觸發情境 | baron 同意 tasks 規劃，下達 C1 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SYNC-2 / C1 — Master Plan Sync / DOC-Refactor；tasks §8 C1

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP / tasks（§8 C1 實作細節）

### 執行命令（tasks §8 C1）
① 改前備份母 plan v10 → archive/2026-06-11_PIPE-SYNC-2_C1_PIPE_plan_v10.md.bak
② 就地補註 `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（`<!-- === [PIPE-SYNC-2 C1 START/END] === -->` 包裹 + §99.2 補註⁶）：
   - U1：L71 + L257 兩處 resume「P3 100% Bypass」→「逐 heading section 翻譯 + 退化 fallback」（slides L70/L258 嚴禁動）
   - U2：§8.5 RAG-ASYNC「⬜ 待建立」→「✅ 已落地（C1-C7+HOTFIX-1/2/3）」+ 產出補 rag_indexer/六步/rag_sections/rag_tree；PIPE-RESUME 狀態註已落地+Golden 待重捕
   - U3 母句：§U4「key 對位巢狀樹」補「key＝原文標題 path、P2 產/P3 帶/P4 取同基準（詳 SPEC §1.4.1）」
   - U8：§U3「絕對均勻」補「均勻者為交付形狀；Tiles 產生方式各路自選（resume opt-out 先例、歸 INFRA-3）」
   - U5 指標：§8.5 PIPE-VISUAL 條目尾加「P1 Vision 解析引用 SPEC §1.3.1」
③ §6.1 六條驗收 grep
- 物理防線：嚴禁動代碼、slides 規格句不動

### TODO 同步
- C1 ✅、C2 🟡 WIP；git log 自癒回填殘留「待 baron 回填」

### 產出
- 執行報告 baton/2026-06-11_PIPE-SYNC-2_C1_執行.md（暫存 baton、不入版控）；template_execution

### §8 baron 命令
- git add：.bak + 2 prompts + TODO（嚴禁 baton/ 文件；母 plan 本體不入版控＝195e12b 先例）
- msg → /tmp/PIPE-SYNC-2_C1_msg.txt

### 停止
- 產出 C1_執行.md 後立即停止；不續 C2、不動未列文件、不自發 commit/push
