# 2026-05-23 — logging-refactor 可行性評估 提示詞

> **收到時間**：2026-05-23（UTC+8）
> **任務代號**：logging-refactor (純評估、無業務代號)
> **觸發 commit**：無（純 plan 階段、僅評估報告）
> **相關產出檔案**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md`
> **觸發情境**：baron 想評估 `logging_refactor_proposal.md` 內提案的可行性、為未來雲原生部署鋪路；本評估純 view / grep、不動業務代碼

---

## 完整提示詞

```
請評估 .claude-logs/ref/logging_refactor_proposal.md 內提案的可行性、產出可行性評估報告。
純 plan 階段、嚴禁修改任何業務代碼、僅 view / grep。
完成後不 commit、不 push。

第一步：讀取規範與提案文件（framework §1.1 / template_plan / logging_refactor_proposal / TODO）
第二步：盤點現況（grep logging.getLogger / basicConfig / RotatingFileHandler / structlog 等）
第三步：產出可行性評估報告（template_plan 8 章節結構、側重評估與決策建議）
  - §1 TL;DR：強烈推薦 / 推薦 / 中性 / 不推薦 / 強烈不推薦
  - §2 提案重點摘要
  - §3 現況盤點（grep 真實證據）
  - §4 提案逐項可行性評估（表格 + 結論）
  - §5 風險與相容性評估
  - §6 拆 commit 建議（若採納）
  - §7 跟 TODO 其他任務優先級對比
  - §8 Open Questions
  - §9 推薦執行順序
第四步：嚴格不可動清單（業務代碼 / TODO / proposal / commit / push 100% 不動）
第五步：評估態度要求（有立場、有結論、不模稜兩可）

評估標準：user-facing 優先 / 工時短風險低優先 / 無依賴優先 / 跟既有 task 重複的不採納 /
第三方 lib 高門檻 / 行銷話術警戒
```

---

## 執行結果摘要

- ✅ 完成狀態：可行性評估報告產出（9 章節、含表格 / Open Questions / commit 拆分）
- 整體結論：**部分採納**（核心 stdout streaming + JSON formatter opt-in 推薦、Trace ID middleware 推薦、ContextVar pipeline 注入 / 第三方 lib 不採納）
- 改動檔案數：1（評估報告）+ 1 歸檔
- 是否 commit / push：未——baron 手動執行

## 後續引用

- 若 baron 決議採納：另開提示詞、把 LOGGING-1 寫進 TODO 候選 / 中優先
