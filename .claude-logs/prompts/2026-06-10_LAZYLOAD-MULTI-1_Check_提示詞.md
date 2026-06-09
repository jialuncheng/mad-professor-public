# LAZYLOAD-MULTI-1 Check（C5 Checkout 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-10 |
| 任務代號 | LAZYLOAD-MULTI-1 Check（C5）|
| 觸發 Commit | LAZYLOAD-MULTI-1-Check（C5 Checkout）|
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | C1-C4 執行報告（baton/）|
| 觸發情境 | C1-C4 全部 commit 完畢，baron 下達 Conformance 驗收與收官指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- LAZYLOAD-MULTI-1 / Checkout（C5）
- Plan：baton/2026-06-09_LAZYLOAD-MULTI-1_..._plan_v5.md（+ v1/v2/v3/v4）；Tasks：baton/..._tasks.md
- 執行報告：baton/ C1/C2/C3/C4 執行.md

### Conformance 六維度
1. 目標規格（plan v5 §2 U1-U9）逐項對應 C1-C4 報告。
2. 驗收條件（tasks §6.1-§6.4）grep/pytest（test_lazyload_multi 10 passed、全套件 556 passed、1=既知 env flake）。
3. §7.2 跨 Phase 整合測試（Checkout 必驗）：test_retrieve_multi_loads_all_tagged〔6 篇只註冊 1、其餘自載全召〕；key=paper_uuid 全程穩定、無 key 轉換 → key-changing N/A（非翻譯型 handoff）。
4. 不可動清單（tasks §7）全報告 §6 標 ✅；C3/C4 web_server hunk 不重疊。
5. 提示詞稽核：ls prompts/ | grep LAZYLOAD-MULTI-1 各階段齊全。
6. msg 完整性：各報告 §8 含 msg 草稿。

### 收官動作（全綠後）
1. TODO：新增 `### BE-Refactor LAZYLOAD-MULTI-1` 完成表（C1 8893ad1/C2 9849600/C3 c5b0c31/C4-C5 待回填）+ active 移除 + 索引 ✅ + 全量 hash 自癒。
2. baton 一次性 mv + git add：plan v1-v5 → plans/ + tasks → tasks/ + C1-C4 報告 → executions/。
3. 確認 baton 無 LAZYLOAD 殘留；YuLun_Wu_CV_chat.md（baron 診斷匯出、非本任務）保持原狀不動。
4. C5 報告直寫 executions/（不過 baton）+ git add。
5. msg 草稿寫 /tmp/LAZYLOAD-MULTI-1_C5_msg.txt（refactor(rag)、署名 Claude Opus 4.8 (1M context)）。

### 停止
- 完成 TODO/baton 歸檔/C5 報告後立即停止；不自發 commit/push、不改已歸檔文件、不碰 .py、不動 baton 非本任務檔。
