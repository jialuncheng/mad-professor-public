# PIPE-SLIDES C6 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 05:30 |
| 任務代號 | PIPE-SLIDES C6 |
| 觸發 Commit | C6 |
| 工作流類別 | BE-Refactor（純測試）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 確認 C5 後，下達 C6 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C6 — Unit & Integration Tests / 純測試；tasks §8 C6（plan §8.1）

### 執行命令（tasks §8 C6）
① 改前備份 tests/test_slide_pipeline.py（1 .bak）
② 補全 plan §8.1 缺口測試（`# === [PIPE-SLIDES C6 START/END] ===` 包裹）
③ **§7.2 跨 Phase 整合測試**：P2→P3→P4 串接、FakeTranslator **真改寫頁標題**（key-changing transform）→ 斷言下游 chunk 對位取得正確頁摘要（p{N}_ 前綴 key 同基準不變式）
- 物理防線：**嚴禁改 slide_pipeline.py 或共用元件**；測試發現業務 bug → 暫停回報 baron

### 驗收（§6.6）
- `pytest tests/test_slide_pipeline.py -v` 全綠 + key-changing 整合通過 + 全套件不退化

### TODO 同步
- C6 ✅、C7 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C6_執行.md（暫存、不入版控）

### §8 baron 命令
- git add：test + 1 .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C6_msg.txt

### 停止
- 產出 C6_執行.md 後立即停止；不續 C7、不自發 commit/push
