# PIPE-SLIDES Check（C7 Checkout 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 05:34 |
| 任務代號 | PIPE-SLIDES Check |
| 觸發 Commit | PIPE-SLIDES-Check（C7）|
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | C1-C6 執行報告（baton/）|
| 觸發情境 | 所有 Commit ship 完畢，baron 下達 Conformance 驗收指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / Checkout（C7）；Plan/Tasks/C1-C6 報告皆 baton

### Conformance 五維度
1. 目標規格（plan §2 U1-U11）逐項對應 C1-C6 報告。
2. 驗收條件（tasks §6.1-§6.6）grep/pytest 通過記錄。
3. 不可動（A 軌 / rag_indexer / 合約結構 全未觸碰）。
4. 提示詞稽核：ls prompts/ | grep PIPE-SLIDES 各階段齊全。
5. msg 完整性：各報告 §8 含草稿。
> §7.2 整合測試已實作且通過（key-changing transform、正面合規）。

### 收官動作（全綠後）
1. **母 plan v10 同步**（備份後就地）：§8.5 PIPE-VISUAL→PIPE-SLIDES 改名 + 狀態 ✅（C1-C7）+ 產出回填；L70/L258 slides「P3 100% Bypass」→「P3 逐頁翻譯與排版還原」；HTML `<!-- === [PIPE-SLIDES C7 START/END] === -->` 包裹 + §99.2 補註⁷。
2. TODO：完成表（C1-C7 待回填）+ active 移除 + 索引 ✅ + git log 全量 hash 自癒。
3. baton 歸檔：plan→plans/ + tasks→tasks/ + C1-C7 報告→executions/ + **修改後之母 plan→plans/ + git add**（baron 本次明令、改變 195e12b 慣例——母 plan 升格入版控）；**PIPE-SPEC 仍長駐 baton 嚴禁動**。
4. 確認 baton 僅剩 README + PIPE-SPEC（+ 非本任務既有檔）。
5. msg → /tmp/PIPE-SLIDES_C7_msg.txt。

### 停止
- 產出 C7_執行.md + TODO 更新後立即停止；不自發 commit/push、不改已歸檔文件。
