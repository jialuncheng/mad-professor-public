# DOMAIN-NORM C4 — Unit Tests（單元測試）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOMAIN-NORM C4 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` §8 C4 + plan v2 §6.1 |
| **次級參考** | tests/test_paper_chunks_schema.py（fixture pattern）/ logging_SOP / database_SOP |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

> **流程校正紀錄**：baron 於 2026-06-03 18:46 的「Check」提示詞原將 C4 重定義為 Check 收官（4-commit 收斂）。經本 session 在不可逆歸檔前提出偏差旗標（plan v2 §6.1 承諾的 4 pytest 未落地），**baron 拍板「先補 C4 Unit Tests 再收官」**，回歸原 tasks v1 規劃（C4=Unit Tests / C5=Check）。本報告即 C4 Unit Tests 落地；Check 收官順延為 C5（待 baron 另行下達）。

---

## §1 基準與完成狀態

- **基準 Commit**：`7e7f2a1`（BE-Refactor: DOMAIN-NORM C3 — Entry & Feature Flag）
- **完成狀態**：C4 新建 `tests/test_domain_normalizer.py`（4 pytest 全綠）落地 worktree，全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C4 | `待 baron 回填` | test: DOMAIN-NORM C4 — DomainNormalizer 單元測試 (4 pytest) |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `tests/test_domain_normalizer.py` | **新建**（約 165 行、4 測試 + fixture + MockLLM） | 純測試新增；無修改任何業務代碼 |
| `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C4_執行.md` | 本報告 | **暫存 baton/，不入 git**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C4→✅ / C5→🟡 WIP + C3 Hash 自癒（`待 baron 回填`→`7e7f2a1`） | — |

- **備份**：純新建檔案、無修改既有檔，故無 `.bak`。
- **包裝標記**：無修改既有原始碼，故無 `=== [DOMAIN-NORM C4 START/END] ===` 標記。
- **提示詞歸檔**：本 C4 承 18:46 Check 提示詞重導，提示詞紀錄存於 `prompts/2026-06-03_DOMAIN-NORM_Check_提示詞.md`（含偏差說明）。

`git status -s`：
```
?? tests/test_domain_normalizer.py
```

## §4 修法說明

依 tasks §8 C4 + plan v2 §6.1，新建 `tests/test_domain_normalizer.py`，對齊 `tests/test_paper_chunks_schema.py` 的 file-based SQLite + FK ON fixture pattern。

### §4.1 fixture + mock（LLM 不實打 API、DB 隔離）
```python
@pytest.fixture
def session_factory():
    # file-based 臨時 SQLite + PRAGMA foreign_keys=ON + create_all → 回 sessionmaker
    ...

class _MockLLM:
    # 可程式化回傳；記錄 chat 呼叫次數以驗證快取命中、記錄 temperature
    def chat(self, messages, temperature=0.5, stream=True, model=None):
        self.calls += 1; self.last_temperature = temperature; return self.response
```
- `DomainNormalizer(llm=mock, session_factory=test_factory)` 依賴注入 → 完全隔離正式 DB / API。

### §4.2 四測試（plan v2 §6.1）
| # | 測試 | 驗證點 |
|---|---|---|
| 1 | `test_domain_normalization_content_based` | 投放/社群→`HF`、Python/LLM→`QA`（raw 短句相異避快取碰撞）；且 `temperature == 0.0` |
| 2 | `test_domain_dynamic_registration` | 冷門「古生物→QE」自動註冊 `Domains`；斷言 Domains 僅一筆 + `{lcc_code,name,created_at}` 三欄（**物理上不可能塞單字**）；`DomainMapping` 快取一筆 |
| 3 | `test_domain_mapping_cache_hit` | 首查 `llm.calls==1`；再查同 raw `llm.calls` **仍為 1**（命中快取、0 API） |
| 4 | `test_feature_flag_off_preserves_raw` | 旗標 off → `normalize_to_lcc` 原樣回傳 raw + `_normalizer_singleton is None`（不建 LLM/DB）；反向驗證旗標 on 委派對齊器 |

## §5 測試結果

### §5.1 C4 四測試全綠（真實輸出）
```
$ venv/bin/python -m pytest tests/test_domain_normalizer.py -v
tests/test_domain_normalizer.py::test_domain_normalization_content_based PASSED [ 25%]
tests/test_domain_normalizer.py::test_domain_dynamic_registration       PASSED [ 50%]
tests/test_domain_normalizer.py::test_domain_mapping_cache_hit          PASSED [ 75%]
tests/test_domain_normalizer.py::test_feature_flag_off_preserves_raw    PASSED [100%]
============================== 4 passed in 0.39s ===============================
```

### §5.2 修正紀錄（透明）
- 初版 test 1 失敗：兩子例共用 raw `"某人履歷"` → 同快取鍵，第二查命中快取回 HF 而非 QA。
- 修法：兩子例改用相異 raw（`"行銷企劃履歷"` / `"軟體工程師履歷"`）→ 通過。此亦反證快取鍵設計正確（鍵於 raw 短句、非 context）。

### §5.3 全套件零迴歸（+4 新測試）
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 56.95s
```
- 452 passed = C4 前 448 + 本次新增 4，**淨增 4、零既有迴歸**。
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json` override 預設 `auto`），與 C4 無關。

## §6 不可動清單遵守

- [x] `models.py` `Paper` 表 — **未觸碰**（測試僅 import `Domains`/`DomainMapping`）。
- [x] `processor/domain_detector.py` / `rag_retriever.py` / `processor/translate_processor.py` — **未觸碰**。
- [x] `processor/domain_normalizer.py` / `settings.py` — **未觸碰**（C4 純測試、不改被測模組）。
- [x] 僅**新增** `tests/test_domain_normalizer.py`，無改任何業務代碼。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_DOMAIN-NORM_C4_執行.md` 暫存 baton/，連同 C1/C2/C3 報告 + plan_v2 + tasks 待 C5 收官一次性歸檔。
- **下一步**：C5 — Check / Checkout：三維度 Conformance 驗收（U1-U4 / 測試 §6.1-§6.4 / 不可動清單）+ 一次性 mv plan_v2/tasks/C1-C5 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒。待 baron 下達 C5 收官提示詞。

## §8 baron 執行命令

```bash
# 1. 本 Commit 無修改既有檔，故無備份
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add tests/test_domain_normalizer.py
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_DOMAIN-NORM_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_DOMAIN-NORM_C4_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/DOMAIN-NORM_C4_msg.txt）
cat /tmp/DOMAIN-NORM_C4_msg.txt

# 4. baron 手動執行
git commit -F /tmp/DOMAIN-NORM_C4_msg.txt
```
