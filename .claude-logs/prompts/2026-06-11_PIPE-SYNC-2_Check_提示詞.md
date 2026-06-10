# PIPE-SYNC-2 Check（C4 Checkout 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 02:08 |
| 任務代號 | PIPE-SYNC-2 Check |
| 觸發 Commit | PIPE-SYNC-2-Check（C4）|
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | C1-C3 執行報告（baton/）|
| 觸發情境 | 所有 Commit ship 完畢，baron 下達 Conformance 驗收指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SYNC-2 / Checkout（C4）
- Plan：baton/2026-06-10_..._plan_v1.md（v1.2）；Tasks：baton/2026-06-11_..._tasks.md；報告：C1/C2/C3

### Conformance 五維度
1. 目標規格（plan §2 U1-U14）逐項對應 C1-C3 報告。
2. 驗收條件（tasks §6.1 六條/§6.2 七條/§6.3 五條）在報告 §5 通過。
3. 不可動（tasks §7）：業務代碼/SPEC 凍結合約欄位/Slides Bypass 全未觸碰。
4. 提示詞稽核：ls prompts/ | grep PIPE-SYNC-2 各階段齊全。
5. msg 完整性：各報告 §8 含 msg 草稿。
> §7.2 整合測試依 plan §8.3 + Q4 顯式豁免（DOC-Refactor、無 code handoff）。

### 收官動作（全綠後）
1. C4 執行報告（含 Conformance 驗收結果三表 + 豁免聲明）→ baton 後隨 C1-C3 一同 mv executions/。
2. baton 歸檔：plan → plans/、tasks → tasks/、C1-C4 報告 → executions/ + git add；**兩長駐真理源 2026-06-01_PIPE* 嚴禁移動與 git add**（195e12b 先例）。
3. 確認 baton 僅剩 README + 兩真理源（+ 非本任務既有檔）。
4. TODO：完成表（C1-C4 待回填）+ active 移除 + 索引 ✅ + git log 全量 hash 自癒。
5. msg → /tmp/PIPE-SYNC-2_C4_msg.txt。

### 停止
- 產出 C4_執行.md + TODO 更新後立即停止；不自發 commit/push、不改已歸檔文件。
