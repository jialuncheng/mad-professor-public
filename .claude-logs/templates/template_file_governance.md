# [文件名稱]

> 文件總覽：[簡述本文件的目的與用途，一文以蔽之]

---

## §0 改版規則

- 改版觸發：§1–§N 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 核心規範

[在這裡填寫該治理文件的核心內容]

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | [本治理文件要解決的根本問題，Why] |
| **用途** | [本治理文件的實際載入或執行時機，When & How] |
| **權威源** | [本文件所定義之規格的唯一核心條款來源] |
| **引用方** | [本文件所定義之規格會被哪些檔案直接載入或引用] |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | [使用或修改本文件時必須遵守的硬約束，例如嚴禁寫入何種內容] |
| **改版觸發條件** | [什麼情況下必須對本文件進行改版] |
| **改版規則** | [改版時的具體操作限制，例如直接修改條款 + §99.2 登記] |
| **刪除條件** | [什麼情況下可以安全刪除本文件，例如任務全部完成且 baron 同意] |
| **重複防護** | [本文件與其他文件如何界定範疇以防止重複定義或衝突] |
| **Scope（範疇）** | 本文件治理內容之作用域：`session-private`（單 session 暫存、不跨會話）或 `project-shared`（跨會話／跨工具共享真理源）。預設 `project-shared`。供 baton Phase 2 Scope 自檢與歸檔目錄判定。 |
| **Provenance（溯源）** | 本文件內容之來源出處：[產生來源（plan／tasks／baron 指令／上游真理源）＋ 來源 commit hash 或 session]。供 baton Phase 2 Provenance 自檢與 Audit Trail 回溯。 |
| **Fidelity Floor（降級底線）** | Token 緊張時多解析度降級之**下限——降到此層即不得再降**。機器可讀格式（供 hook 解析）：`fidelity_floor: <Full\|Structured\|Pointer>`；可逐類細列如 `Constraint=Structured; 不可動清單=Structured; Evidence=Pointer`。**Cost-Aware**：高重算成本之 evidence（grep 證據／實測輸出／commit hash）標 `no-degrade`、**優先不降級**。 |

> **Fidelity Floor 機器可讀說明**：上欄 `fidelity_floor:` 採 `key=Level` 分號分隔之可解析格式，為後續 hook（如截斷守衛之 Floor 守衛階段）保留機器讀取空間；四 Level 由高至低＝`Full → Compressed → Structured → Pointer`（對齊 ClawVM 多解析度殘留鏈）。
> **Cost-Aware 保留原則**：標 `no-degrade` 之 evidence（grep 證據／實測輸出／commit hash 等重算昂貴者）於降級時**優先保留**，不隨一般內容降級。

### §99.2 Revision 歷程

- v2 (2026-06-27)：WORKFLOW-5 C3——§99.1 治理規格表新增三維度 Scope（session-private／project-shared）／ Provenance（來源溯源＋hash）／ Fidelity Floor（降級底線·機器可讀 `fidelity_floor:` 格式·四 Level 殘留鏈）＋ Cost-Aware 保留原則（grep 證據／實測輸出／commit hash 優先不降級）；對齊 ClawVM 多解析度與 baton Phase 2 自檢
- v1 (2026-05-26)：[建立本文件的初始版本紀錄]
