````markdown
# 2026-07-11 — SEC-SECRET hotfix 提示詞

> **收到時間**：2026-07-11（UTC+8）
> **任務代號**：SEC-SECRET（BE-Hotfix）
> **觸發 commit**：SEC-SECRET hotfix
> **相關產出檔案**：.claude-logs/baton/2026-07-11_SEC-SECRET_SESSION_SECRET_fail-closed_hotfix.md
> **觸發情境**：PROJECT-REVIEW 安全審查發現 #1 HIGH——SESSION_SECRET 有硬編碼 fallback 常數致認證繞過（預設不安全）。baron 下令針對 web_server.py + settings.py 產一份 fail-closed hotfix 文件（含詳細原因、程式碼、commit），暫存 baton/。

---

## 完整提示詞

```
SESSION_SECRET fail-closed（web_server.py+settings.py）
針對以上面內容做一個hotfix文件
存檔路徑baton/

依據
template_hotfix.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

詳細說明原因
程式碼也加入文件
包含commit
```

---

## 執行結果摘要

- ✅ 產出 hotfix 文件至 baton/（含真因、最小 diff、§5 SOP 核查、commit 草稿）
- pytest baseline：705 passed / 3 skipped / 0 failed（TEST-GREEN 已落地 `3a71293`，綠燈基線）
- 改動檔案（文件產出階段）：1（prompts 歸檔）+ hotfix 文件暫存 baton/；程式碼實檔未動（文件僅記錄 diff）
- commit / push：無（§1.3 由 baron 手動；文件含 commit 草稿）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
