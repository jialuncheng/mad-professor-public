# CHAT-EXPORT-HOTFIX-1 Hotfix 文件撰寫提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 |
| 任務代號 | CHAT-EXPORT-HOTFIX-1 |
| 工作流類別 | FE-Hotfix（doc-only 階段）|
| 觸發情境 | baron 回報「對話下載在 Dia 瀏覽器卡 8/8 KB 不結束、Safari 正常」，要求撰寫 hotfix 文件 |

---

## 正文（原始提示詞摘要）

### 病灶（baron 提供 + Claude 診斷確認）
- Dia（The Browser Company Chromium AI 瀏覽器）對「主框架導覽去 attachment URL」收尾與 Safari/Chrome 不同 → 配上常駐 SSE，download chip 卡 8/8 不關。
- Safari 用既有 navigation 語意正常收尾 → 後端無誤（Claude 真 uvicorn + curl -v 實測 content-length 正確、無 chunked）。
- 結論：不是後端、不是 nginx，是前端 `static/index.html:2812` 的 `window.location.href` 導覽式下載寫法。

### 修法
- fetch → blob → `<a download>`（不依賴導覽語意、完整緩衝後 blob URL 觸發、瀏覽器無關 Dia/Safari/Chrome 全收尾）。

### 要求
- 依 `template_hotfix.md` + `WORKFLOW_SOP.md` + `framework`。
- 詳細說明原因；程式碼以 diff 寫進文件；含 commit 草稿。
- 存 baton/（doc-only、實檔不動、Run 待 baron）。
