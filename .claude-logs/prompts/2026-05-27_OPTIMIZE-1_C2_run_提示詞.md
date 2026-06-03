# 2026-05-27 — OPTIMIZE-1 C2 Run 提示詞

> **收到時間**：2026-05-27 14:34
> **任務代號**：OPTIMIZE-1 C2
> **觸發 Commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-05-27_OPTIMIZE-1_C2_執行.md`
> **觸發情境**：baron 確認 C1 成功落地後，下達 C2 執行指令

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-27 14:34` |
| **任務代號** | `OPTIMIZE-1 C2` |
| **觸發 Commit** | `C2` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` |
| **觸發情境** | `baron 確認 C1 成功落地後，下達 C2 執行指令` |

你現在扮演 Claude Code，請執行 C2 — Integrate 1-Step Upload in Web Server & Frontend（整合一字步上傳端點與前台 UI）。

任務編碼：OPTIMIZE-1
當前 Commit 代號：C2
工作流類別：BE-Refactor
Tasks 路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md

強制讀檔清單：
- CLAUDE.md
- .claude-logs/ref/WORKFLOW_SOP.md
- .claude-logs/sop/2026-05-23_logging_SOP_手冊.md
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md（§8 C2 實作細節）

三大防線：
1. 物理防線：僅允許修改 web_server.py 與 static/index.html；waiting_confirm HTML + showConfirmModal 骨架不可動
2. 測試防線：orb pytest tests/ -v（穿透 OrbStack VM）+ 手動 E2E 驗收
3. 文件防線：嚴禁自發 commit/push

備份規則：
cp web_server.py .claude-logs/archive/2026-05-27_OPTIMIZE-1_C2_web_server.py.bak
cp static/index.html .claude-logs/archive/2026-05-27_OPTIMIZE-1_C2_index.html.bak
（兩個 .bak 必須在 §8 git add 清單中）

TODO.md 更新：C2 改為 ✅；C3 改為 🟡 WIP；掃描 git log 自愈「待 baron 回填」

產出：
- .claude-logs/baton/2026-05-27_OPTIMIZE-1_C2_執行.md（暫存 baton/）
- 套用 template_execution.md
- §8 baron 執行命令（git add 清單 + commit message 至 /tmp/OPTIMIZE-1_C2_msg.txt）

嚴禁：C3 執行 / 修改未列入 C2 的代碼 / git commit/push
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

- 下一步：baron 驗收 C2 後，下達 OPTIMIZE-1 C3 提示詞（收官歸檔）

> 本文件為 OPTIMIZE-1 C2 Run 提示詞歸檔，記錄 baron 下達 C2 執行指令（後端 is_slides_pdf 刪除 + optimize_pdf_lossless 整合 + 前端 Phase-Shift 事件翻轉）的完整意圖。
