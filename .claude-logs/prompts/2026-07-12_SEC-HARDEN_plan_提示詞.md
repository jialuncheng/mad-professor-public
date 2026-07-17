````markdown
# 2026-07-12 — SEC-HARDEN plan 提示詞

> **收到時間**：2026-07-12（UTC+8）
> **任務代號**：SEC-HARDEN（BE-Refactor）
> **觸發 commit**：plan（純規劃）
> **相關產出檔案**：.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md
> **觸發情境**：PROJECT-REVIEW 安全審查 LOW/MEDIUM 縱深項（#3 XFF / #4 CORS / #5 str(e) 外洩 / #6 主題覆寫 / #8 timing）——全在 web_server.py 後端。baron 下令開後端安全加固 plan，暫存 baton/。

---

## 完整提示詞

```
XFF trusted-proxy(#3) + CORS(#4) + str(e) 外洩(#5) + 主題覆寫 guard(#6) + timing(#8)
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md

不用給commit建議
```

---

## 執行結果摘要

- ✅ 產出 plan 至 baton/（純規劃、含 §Open Questions、不含 commit 建議）
- ⚠️ 工作流校正：5 項全後端（web_server.py）→ BE-Refactor，必讀 SOP 應為 logging + database SOP（非提示詞所列前端 SOP，plan §7 標注）
- 蒐證：XFF / CORS / str(e) sink / 主題上傳 guard / login timing 逐項 grep
- 改動檔案（plan 階段）：1（prompts 歸檔）+ plan 暫存 baton/
- commit / push：無（plan 階段）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
