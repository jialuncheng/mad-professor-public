# LANG-DETECT C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）執行報告

---

**任務代號**：LANG-DETECT C1
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md` §8 C1
**上游 plan**：同名 `_plan.md`（v2、四 OQ 拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §1 基準與完成狀態

- 基準 commit：`4b7e19a`（PIPE-INGEST-FITZ checkout、baron 已 ship）
- 完成狀態：代碼與測試已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 工作區自檢：`git status -s`（排除 .claude-logs）＝恰為本 commit 2 檔

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Language Field & Source-Lang Resolution（語言欄與 source_lang 合成） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改 | prompt +language 欄與規則（L72-89）+ P1 接點（L203）+ `_resolve_source_lang`（L394-408） |
| `tests/test_litedoc_pipeline.py` | 修改 | +45 測試（契約 1／矩陣參數化 37／端到端 2／§7.2 整合 1 大案） |
| `.claude-logs/archive/2026-07-21_LANG-DETECT_C1_litedoc_pipeline.py.bak` | 備份 | 改前備份（隨本 commit git add） |
| `.claude-logs/archive/2026-07-21_LANG-DETECT_C1_test_litedoc_pipeline.py.bak` | 備份 | 改前備份（隨本 commit git add） |

（baton 暫存之 plan/tasks/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

**真因**：`classify_source_lang` 只吐 `{zh,hans,ja,ko,en}`、拉丁語系全落 catch-all `en` → 義文詞以 `en` 寫入 `GlobalGlossary`（聯合鍵含 source_lang）、污染英文命名空間。schema 已多語、破的是偵測層。

**修法（三點、單語意單元）**：

1. **`_LITEDOC_META_SYSTEM_PROMPT`**：Fields 增列 `language (str: ISO 639-1 two-letter code of the document's main body language, e.g. en/it/de/fr/ja)`；新 Rule 5「judge by the main body language of the text (not the title or URL); use \"\" if unsure」；原 Rule 5 keys 清單改 Rule 6、補 `language`。既有五欄規則零動、**零多一次 LLM 呼叫**（搭既有 metadata 便車、temp=0）。
2. **`_resolve_source_lang(meta, heuristic)`（新 staticmethod）**：`heuristic != "en"` → 直接維持原判（zh/hans/ja/ko 字元證據確定、LLM 不得翻案——繁中 bypass 權威不動搖）；`heuristic == "en"` → `str(meta.get("language") or "").strip().lower()` 過**雙重白名單**——格式 `^[a-z]{2,3}$`（ISO 639-1/2、含三字碼 `ita`/`deu`）**且 `not lang.startswith("zh")`**（HOTFIX-1 鎖一契約於 producer 端強制、封鎖 `zh`/`zh-tw`/`zho` 類值繞過 P3 翻譯 gate）→ 通過採信、未過退 `en`。缺欄／怪值／非字串一律退 `en`＝**與現行 100% 等價**。
3. **P1 接點**：`run_phase1` 於 `classify_source_lang` 後單行 `source_lang = self._resolve_source_lang(meta, source_lang)`（meta 於前段已取得、零重排）；正名值單點流入 `IngestionMetadataSpec.source_lang`、P2 glossary 分桶／P3 gate 消費端零改自然生效。

## §5 測試結果

```
tests/test_litedoc_pipeline.py：95 passed（50 既有 + 45 新增）in 0.71s
全套件：920 passed, 3 skipped, 3 warnings in 54.11s   ← 基線 875 + 45、零回歸
```

新增測試：
- `test_lang_prompt_contract_has_language_field`（prompt 契約三斷言）
- `test_lang_resolve_non_catchall_keeps_heuristic`（矩陣①：4 啟發式 × 6 LLM 值＝24 案全維持原判）
- `test_lang_resolve_catchall_whitelist_matrix`（矩陣②：13 案——`it`/`de`/`fr`/`ita`/`deu` 採信、`IT`/` fr ` 正規化採信、`zh`/`zh-tw`/`zho` 拒前綴、`Chinese`/`italian`/`en-US`/`a`/空/缺欄/`123` 退 `en`）
- `test_lang_p1_end_to_end_italian`（spec.source_lang=="it" 且非 zh 前綴）
- `test_lang_p1_missing_language_field_byte_equivalent`（缺欄退 `en`＝現行等價安全網）
- `test_seam_lang_p1_to_p2_glossary_bucket_integration`（**§7.2**、key-changing＝語系 token `en`→`it`：P1 真 run_phase1 正名 → spec 值直通 P2 真 run_phase2（旗標開）→ 捕參斷言 `build_termmap` 收到 `source_lang=="it"`＋`target_lang=="zh-tw"`＋P3 gate 謂詞不 bypass；**對照組**英文文件全鏈仍 `en`、跨文件不互污）

驗收 grep（§6.1 全項）：

```
litedoc_pipeline.py L72-89 prompt language 欄+Rule 5/6 ✅
L203 接點 / L395 定義（_resolve_source_lang 兩處）✅
L406 白名單拒 zh 前綴（與 L591 P3 gate `is_zh = source_lang.startswith("zh")` 謂詞同源）✅
git diff --stat pipelines/section_engine.py models.py → 零 diff ✅（偵測器原職/schema 零改）
```

SOP 一致性核查（§6.2）：

```
logging：grep logger.error/exception/traceback.format_exc → 無命中（合規；本 commit 零新增日誌點）
database：grep "\.commit()" → 無命中（合規：零 DB）
```

## §6 不可動清單遵守狀態

- [x] `pipelines/section_engine.py` `classify_source_lang`／`detect_zh_tw` — byte 不動（git diff 零、原職不兼差）
- [x] `models.py` `GlobalGlossary` — byte 不動
- [x] P3 gate／P2 glossary 消費端簽名 — 零改（單點正名自然生效）
- [x] cover-prompt 既有五欄規則 — 零動（僅增列）
- [x] 零第三方偵測套件、零新偵測器、零多呼叫、零 env flag（Q2 拍板）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C_CHECKOUT — 收官歸檔**；待 baron ship C1 後另下 checkout 提示詞。
- baron 影子 E2E（收官後、plan §8.2）：義文樣本 log `source_lang=it`＋SQL 驗 glossary `it` 桶；英文／繁中／簡體回歸；`SELECT DISTINCT source_lang FROM global_glossary` 驗桶隔離。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、2 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_LANG-DETECT_C1_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_LANG-DETECT_C1_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/LANG-DETECT_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/LANG-DETECT_C1_msg.txt
```
