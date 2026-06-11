# META-NORM C6 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 22:05 |
| 任務代號 | META-NORM C6 — Tests（測試補全）|
| 觸發 Commit | C6 |
| 工作流類別 | BE-Refactor（純測試）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 C5，下達 C6 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C6 / BE-Refactor；tasks §8 C6（§7.2 key-changing 整合）

### 執行命令（`# === [META-NORM C6 START/END] ===` 包裹）
① 改前備份 test_meta_norm.py + test_slide_pipeline.py（2 .bak）
② test_meta_norm.py 新增 `test_c6_key_changing_integration`：
   - 模擬 P1 自提 metadata（{"課程":"LS1005"}）→ MetaNormalizer.normalize_fields（mock LLM 映既有 course、產 alias）
   - 模擬 P4/web_server 消費端：`result.get("course",{}).get("value")`
   - 雙斷言接縫不變式：取值=="LS1005" + raw_key("課程")≠canonical_key("course") 仍對位
   - 三欄 dict 格式斷言 {value,source,confidence}（杜 bare string 退化）
③ test_slide_pipeline.py 檢查 C3/C4 assertions 完整、必要時包裹清理
- 物理防線：僅兩測試檔；嚴禁改業務碼

### 驗收
- pytest test_meta_norm + test_slide_pipeline + 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0)

### TODO 同步
- C6 ✅、checkout 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C6_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：兩測試檔 + 2 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C6_msg.txt

### 停止
- 產出 C6_執行.md + TODO 更新後立即停止；不續 checkout、不自發 commit/push
