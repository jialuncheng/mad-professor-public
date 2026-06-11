# META-NORM Check（C7 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 22:35 |
| 任務代號 | META-NORM Check |
| 觸發 Commit | C7（checkout）|
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | C1-C6 執行報告（baton/）|
| 觸發情境 | C1-C6 ship 完畢，baron 下達 Conformance 驗收與 C7 歸檔收官指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / Checkout（C7）；Plan/Tasks/C1-C6 報告皆 baton

### Conformance 驗收（C7 報告填）
- U1-U9 規格完整實現 / §6 測試計畫 C1-C6 pytest+grep 全綠 / §7.2 key-changing 整合（C6 存在且通過、含三欄 dict 契約）/ 不可動 C1-C6 全 ✅ / 提示詞稽核 / msg 完整

### 收官動作（全綠後）
1. TODO：完成表（C1-C7 待回填）+ active 移除 + 索引 ✅ + git log 全量 hash 自癒
2. baton 歸檔：plan→plans/ + tasks→tasks/ + C1-C7 報告→executions/ + git add
3. 驗證 baton 僅剩 README + PIPE-SPEC 長駐
4. C7 報告 §8 msg → /tmp/META-NORM_C7_msg.txt

### 停止
- 產出 C7 報告 + TODO 更新 + baton 移出後立即停止；不自發 commit/push
