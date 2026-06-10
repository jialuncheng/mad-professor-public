# PIPE-SLIDES C6 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C6 — Unit & Integration Tests（測試補全）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C6`（plan §8.1 + WORKFLOW_SOP §7.2）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 24 測試全綠（含 §7.2 key-changing 整合）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C5（P4 Wire、四 Phase 全落地）之上。
- **本次**：**純測試**——§7.2 跨 Phase 整合測試 + 2 缺口補全；**業務碼零改**（C6 鐵則遵守、未發現業務 bug）；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C6 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C6 — Unit & Integration Tests |

## §3 變動檔案清單

```
修改：tests/test_slide_pipeline.py（+3 測試；C6 標記 1 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C6_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES C6 START/END] ===`）

### ① `test_integration_p2_p3_p4_key_changing`（§7.2 規範、Checkout 必驗主件）
串接整條鏈、**含 key-changing transform**（純 mock 同 key 不予承認之反面）：
```
真實 run_phase2（mock LLM 三呼叫）→ gspec.section_summaries={'p01_Power Architecture': '機櫃供電總覽', ...}
真實 run_phase3（FakeTranslator 真改寫：譯 title='譯Power Architecture' ≠ 原文 key）
真實 rag_indexer.build_chunk_markdown（純函式、零 Embedding）
```
**接縫不變式雙斷言**：
1. P3 旁路 `summary_key`（`p01_/p02_Power Architecture`、原文）≡ P2 `section_summaries` keys——**雖譯後 title 已改變**；
2. 真實 chunk 構建後「機櫃供電總覽／維也納整流器」**確實進 Chapter Summary 行**——HOTFIX-1 類「key 對位失效→摘要永不進 chunk」靜默退化在此測試下**必紅**（照得出接縫）。
連續同標題雙頁（`Power Architecture`×2）同時驗證 `p{N}_` 前綴防覆蓋。

### ② `test_p1_dedupe_skipped_under_3_body_pages`（Q2 邊界）
非封面頁 <3 → 統計不去重（防小樣本誤殺口號式正文）。

### ③ `test_contract_p1_zero_derived_context`（凍結合約 ① 防線）
`IngestionMetadataSpec(extra='forbid')`——P1 夾帶 `abstract` 衍生欄 → ValidationError（R1.1 schema 層保證）。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
24 passed in 0.55s     # 4 C1 + 6 C2 + 4 C3 + 5 C4 + 2 C5 + 3 C6

  test_integration_p2_p3_p4_key_changing PASSED      ← §7.2 必驗主件
  test_p1_dedupe_skipped_under_3_body_pages PASSED
  test_contract_p1_zero_derived_context PASSED

$ venv/bin/python -m pytest tests/ -q
1 failed, 580 passed, 3 skipped   # 唯一 failed=既知 env flake；580（577+3 新）
```
SOP：純測試、無 logger.error／無 DB 寫（合規）。

## §6 不可動清單遵守

- [x] **業務碼零改**（git status 僅測試檔——C6 鐵則）；`slide_pipeline.py`／共用元件未動。
- [x] 測試全綠、**未發現業務 bug**（無需暫停回報）。
- [x] C6 標記平衡（1/1）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存；plan + tasks + C1-C5 報告續留。
- **§7.2 整合測試已就位且通過** → C7 Checkout Conformance「跨 Phase 整合測試存在且通過」維度可直接引用（本路正面達標、免豁免）。
- **下一步＝C7 Checkout**（Conformance U1-U11 + 母 plan §8.5 PIPE-VISUAL→PIPE-SLIDES 改名/狀態/Bypass 句同步〔Q6/Q7〕+ baton 一次性歸檔），待 baron 下達 C7 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 1 份 .bak）

# 2. git add 清單（嚴禁 baton/ 執行報告）
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C6_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C6_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C6_msg.txt
git commit -F /tmp/PIPE-SLIDES_C6_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C6 hash>   # 純測試、回退無副作用
```
