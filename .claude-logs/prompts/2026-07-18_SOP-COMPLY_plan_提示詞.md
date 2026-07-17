````markdown
# 2026-07-18 — SOP-COMPLY plan 提示詞

> **收到時間**：2026-07-18（UTC+8）
> **任務代號**：SOP-COMPLY（BE-Refactor）
> **觸發 commit**：plan（純規劃）
> **相關產出檔案**：.claude-logs/baton/2026-07-12_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md
> **觸發情境**：PROJECT-REVIEW 程式碼品質 #1（logging SOP 違規·logger.error 丟棄 stack trace）+ llm/client.py:181 靜默吞例外 + paper_manager.py 13 處裸 commit（DB SOP 違規）。baron 下令開 SOP 合規清帳 plan，暫存 baton/。

---

## 完整提示詞

```
41 處 logger.error 補 exc_info + llm/client.py:181 吞例外 + 13 處裸 commit
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給commit建議
```

---

## 執行結果摘要

- ✅ 產出 plan 至 baton/（純規劃、含 §Open Questions、不含 commit 建議）
- 蒐證：logger.error 無 exc_info 清點（SEC-HARDEN C3 後重抓）/ llm/client.py 吞例外 / paper_manager 裸 commit
- 改動檔案（plan 階段）：1（prompts 歸檔）+ plan 暫存 baton/
- commit / push：無（plan 階段）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
