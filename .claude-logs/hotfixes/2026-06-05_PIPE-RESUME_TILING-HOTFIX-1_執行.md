# PIPE-RESUME TILING-HOTFIX-1 — 執行報告（TextTiling 429 批次化修復）

---

**任務代號**：PIPE-RESUME TILING-HOTFIX-1（BE-Hotfix）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_hotfix.md`（收官後位置）
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Hotfix、全套件 429 flaky 轉綠)

---

## §0 改版規則
- 改版觸發：§1–§8 任一執行條款變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 基準與完成狀態
- **基準**：PIPE-RESUME v9（C1-C7）收官後；`processor/tiling_processor.py:425` 以逐筆 `[embedding_model.embed_query(block) for block in blocks]` 計算分塊 embedding，長文/併發下毫秒內發數十至上百請求 → `429 RESOURCE_EXHAUSTED` 阻斷向量化、並使全套件 `test_tiling_paragraph.py` 偶發 429。
- **完成狀態**：
  1. **就地 bump** `hotfix.md` 4 點（task_type 行為變更+邊界位移 / Golden Baseline 重捕防線 / 指數→線性退避修正 / 根治併發 429 flaky）。
  2. **代碼修改**（僅 `tiling_processor.py:425`、`# === [PIPE-RESUME TILING-HOTFIX-1 START/END] ===` 包裹）：逐筆 `embed_query` → 批次 `embed_documents(blocks)`。
  3. **測試**：tiling 三套件 **15 passed**；全套件 **484 passed / 1 failed（僅 env flake）/ 3 skipped**——**tiling 429 flaky 全數轉綠**。

---

## §2 Commit 表格
| Commit | 內容 | Hash |
|---|---|---|
| TILING-HOTFIX-1 | `tiling_processor.py:425` 逐筆 embed_query → 批次 embed_documents（防 429） | （留空，由 baron 回填） |

---

## §3 變動檔案清單
| 狀態 | 檔案 | 備份 | 說明 |
|---|---|---|---|
| 修改 | `processor/tiling_processor.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_tiling_processor.py.bak` | L425 逐筆→批次 + hotfix 標記包裹（僅此行邏輯） |
| Bump | `hotfix.md`（→ hotfixes/） | — | 4 點審查建議落地 |

---

## §4 真因與修法
### §4.1 真因
`embed_query`（`config.py:148`、`task_type=RETRIEVAL_QUERY`）原生無 429 退避；逐筆列表推導在毫秒內併發數十至上百請求 → 超 Gemini RPM 配額 → 直拋 429、阻斷 RAG。

### §4.2 修法（最小侵入）
```python
# === [PIPE-RESUME TILING-HOTFIX-1 START] ===
block_embeddings = embedding_model.embed_documents(blocks)   # 批次 32、線性退避、順序保證
# === [PIPE-RESUME TILING-HOTFIX-1 END] ===
```
- **請求量 1/32**：`embed_documents`（`config.py:96`）以 `BATCH_SIZE=32`（L103）分批。
- **線性退避**：3 次 `wait = 15*(attempt+1)`（L130-133，15s/30s）+ 重試耗盡退回逐筆（L139-140）。
- **順序保證（正確性前提）**：docstring「依索引順序拼接，保證回傳順序與輸入完全一致」（L99）→ `block_embeddings[i]` 對齊不變、相鄰塊相似度（L428）不錯位。
- **⚠️ 行為變更**：`task_type` 由 `RETRIEVAL_QUERY`→`RETRIEVAL_DOCUMENT`（L154→L115）；向量值略異 → TextTiling 分段邊界**或微幅位移**（對 Document-Blocks 語意更正確）。**Flip/結案前須由 baron 於 MinerU 重捕 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`、容差 D2≥0.95/D3≥0.90）。

---

## §5 測試結果
```bash
$ git status -s
 M processor/tiling_processor.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_tiling_processor.py.bak

$ venv/bin/python -c "import ast; ast.parse(open('processor/tiling_processor.py').read())"
  syntax OK

# tiling 三套件
$ venv/bin/python -m pytest tests/test_tiling_paragraph.py tests/test_tiling_formula.py tests/test_tiling_env_overrides.py -q
  15 passed in 50.54s

# 全套件（429 flaky 轉綠驗證）
$ venv/bin/python -m pytest tests/ -q
  1 failed, 484 passed, 3 skipped in 53.64s
  # 唯一 failed = test_settings_log_format_default_auto（.env LOG_FORMAT=json 環境性、跨所有 commit 恆定、非本 hotfix）
  # tiling 429 flaky 已全數消失（先前 C5-C7 全套件偶發失敗的 test_tiling_paragraph 此次穩定全綠）
```
### §5.1 SOP 一致性核查（BE-Hotfix）
```bash
$ grep -nE "logger\.error|traceback.format_exc" processor/tiling_processor.py | grep -v exc_info=True  → 無不合規命中（合規）
$ grep -nE "\.commit\(\)" processor/tiling_processor.py  → 無裸 commit（合規）
```
（本 hotfix 僅替換 embedding 計算呼叫、無新增 logging/DB 交易。）

---

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| `tiling_processor.py` 僅 L425 邏輯（含標記包裹） | [x] ✅ |
| 過濾演算法 / 相似度計算 / 分段邏輯本體 | [x] ✅ 未動（僅換 embedding 來源呼叫） |
| `config.py`（embed_documents 既有、僅呼叫） | [x] ✅ 未改 |
| 其他 `processor/*` / `pipelines/*` / `web_server.py` | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接
- **baton/ 歸檔**：hotfix.md + 執行.md 一次性 mv → `hotfixes/` + git add。
- **後續防線（重要）**：task_type 位移改變分段 → **PIPE Flip 或本批結案前，baron 須於 MinerU 重捕五路 Golden Baseline**（見 §4.2 / hotfix.md §regression 3）。未重捕前既有黃金基準 diff 會全面誤報。
- **回退**：`git restore processor/tiling_processor.py`（或自 .bak 還原）。

---

## §8 baron 執行命令
```bash
# 1. 搬移已完成（hotfix.md + 執行.md 已移入 hotfixes/）

# 2. git add 清單
git add processor/tiling_processor.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_tiling_processor.py.bak
git add .claude-logs/hotfixes/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_TILING-HOTFIX-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_TILING-HOTFIX-1_msg.txt
```

### §8.2 commit message 草稿
```
fix(tiling): batch compute block embeddings using embed_documents to prevent 429 rate limit

修改 processor/tiling_processor.py 將分塊 embedding 由遍歷 embed_query 改為
批次呼叫 embed_documents，使網路併發數降為 1/32 並承接其線性退避重試保護，
從而根治 TextTiling 在全套件或長文下因 429 Too Many Requests 導致的崩潰與測試 flaky。
本熱修復以大改版註解包裹，完成 hotfix 歸檔與 TODO.md 結案。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 記錄 TILING-HOTFIX-1 代碼修復與驗收，作為 Traceability 審計依據 |
| 用途 | 收官 mv 歸檔 hotfixes/ |
| 權威源 | 本檔 §1–§8 + hotfix.md |
| 約束事項 | 限改 tiling_processor.py:425；嚴禁動演算法/自動 commit |
| 改版規則 | 直接改章節 + §99.2 加 Revision |
| 刪除條件 | 永久保留歸檔 hotfixes/ |

### §99.2 Revision 歷程
- v1 (2026-06-05)：TILING-HOTFIX-1 執行——`tiling_processor.py:425` 逐筆 embed_query → 批次 embed_documents（請求 1/32 + 線性退避 + 順序保證）；hotfix.md 4 點 bump；tiling 三套件 15 passed、全套件 484 passed（429 flaky 全綠、僅剩 env flake）。task_type RETRIEVAL_QUERY→DOCUMENT 行為變更已聲明、Golden Baseline 重捕防線待 baron Flip/結案前執行。
