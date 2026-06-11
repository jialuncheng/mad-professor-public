# META-NORM C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 21:30 |
| 任務代號 | META-NORM C2 — MetaNormalizer Flywheel（自癒飛輪）|
| 觸發 Commit | C2 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 C1，下達 C2 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C2 / BE-Refactor；tasks §8 C2（plan U3/U4/Q9/BS1/BS4/BS5）

### 執行命令（`# === [META-NORM C2 START/END] ===` 包裹）
① 改前備份 tests/test_meta_norm.py（1 .bak）
② 新建 `processor/meta_normalizer.py`（繼承 DomainNormalizer 範式）：
   - `RESERVED_MAPPING`（title/作者/venue/期刊/doi… → 凍結合約欄）+ `GENERIC_KEYS` 黑名單（date/time/name/title/class/type/status/id/no/code/user）
   - MetaNormalizer：`_normalize_key`(.strip().lower())/`_cache_lookup`(MetaFieldAlias 唯讀)/`_llm_classify`(比對既有 MetaField 全集、LLM_DOMAIN_MODEL、temp=0、交易外)/`_register_and_cache`(session.begin + on_conflict_do_nothing 註冊 MetaField+label提案；黑名單不寫 alias)/`normalize_fields` 分流（reserved→映射不入庫不問 LLM；黑名單→不查快取直接 LLM；非黑名單→快取查→未命中 LLM+註冊）；try/except 降級回 raw 原樣 logger.error(exc_info)
   - 模組級公開 `normalize_fields` + 旗標 LLM_USE_META_NORM（False 直回原樣）
③ tests 追加 4 測試（flow 快取/LLM/註冊 / reserved 不入庫 / generic 黑名單不讀寫快取 / flag off 0 DB）
- 物理防線：僅兩檔；SOP §5.1 logger.error 帶 exc_info、§5.2 無裸 commit（LLM 交易外）

### 驗收
- pytest tests/test_meta_norm.py + 全套件不退化;grep format_exc/logger.error(帶 exc_info)/裸 commit(0)

### TODO 同步
- C2 ✅、C3 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C2_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：meta_normalizer + test + 1 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C2_msg.txt

### 停止
- 產出 C2_執行.md + TODO 更新後立即停止；不續 C3、不自發 commit/push
