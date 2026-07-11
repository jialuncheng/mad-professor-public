# 2026-07-12 — SEC-XSS Check 提示詞

> **收到時間**：2026-07-12 05:10（UTC+8）
> **任務代號**：SEC-XSS Check（checkout 收官）
> **相關產出檔案**：TODO 雙層結案 + baton 歸檔（plan/tasks/C1–C3 報告）+ `executions/2026-07-12_SEC-XSS_checkout_執行.md`
> **觸發情境**：C1–C3 ship 完畢、baron 下達 Conformance 驗收與 checkout 收官——五維度（plan §2 U1-U7 對照／tasks §6 守衛+全套件遞增綠燈／不可動〔佔位管線·靜態 sink·data-tip/SVG·後端〕／提示詞歸檔+版控稽核／msg 草稿）→ 全綠後 TODO 結案+hash 自癒 → baton 歸檔 → baton 乾淨檢驗 → checkout 報告直產（staged 白名單自檢）→ §8 指令 → 停。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-12 05:10 |
| **任務代號** | SEC-XSS Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton/ C1–C3 執行報告 |
| **觸發情境** | C1、C2、C3 ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）

你現在扮演 Claude Code，對 SEC-XSS 執行 Conformance 驗收、全合規後收官歸檔 checkout。

### ✅ Conformance：五維度（目標規格 U1-U7／tasks §6 守衛+全套件綠燈遞增／不可動〔佔位管線/靜態 sink/模板按鈕/後端〕／提示詞歸檔+版控稽核〔untracked 者本階段 add〕／msg 草稿）→ 驗收報告（🟢 收官／🔴 停）

### 🗃️ 收官：TODO 更新+hash 自癒（git log 回填 C1-C3）→ baton 歸檔（plan/tasks/C1-C3 → plans//tasks//executions/ + 逐檔 add）→ baton 乾淨檢驗 → checkout 報告直產 executions/（Conformance 總驗+staged 自檢）

### 📝 §8 checkout commit 指令（逐檔 add·禁廣義；msg /tmp/SEC-XSS_checkout_msg.txt）
### 🛑 停止：完成後立即停；嚴禁自發 commit/push、改歸檔目錄
````

---

## 執行結果摘要

- ⚠️ 提示詞 §8 漏列 `2026-07-12_SEC-XSS_plan_提示詞.md`（實存 untracked）→ add 清單補入；TODO 結案依 framework §2.5 雙層結構（同 THEME-DEDUP/FE-CSS-GOV 先例）
- ✅ Conformance 五維度全綠 → TODO 雙層結案 + C1-C3 hash 自癒 → baton 歸檔（5 檔）→ checkout 報告直產
- SEC-XSS 全案結案（PROJECT-REVIEW 安全 #2 stored XSS 關閉）

## 後續引用

無（全案完結）。
