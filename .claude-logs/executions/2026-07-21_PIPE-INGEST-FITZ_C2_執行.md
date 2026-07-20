# PIPE-INGEST-FITZ C2 — Ligature Repair（連字修復純函式）執行報告

---

**任務代號**：PIPE-INGEST-FITZ C2
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md` §8 C2
**上游 plan**：同名 `_plan.md`（v2、六 OQ 拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §1 基準與完成狀態

- 基準 commit：`3cc3850`（PIPE-INGEST-FITZ C1、baron 已 ship）
- 完成狀態：代碼與測試已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- 純加法零接線：`grep -rn "ligature_repair" pipelines/litedoc_pipeline.py processor/` → **零命中**（全鏈 runtime 零變化）

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor（Fitz 直抽處理器） | `3cc3850` |
| C2 | Ligature Repair（連字修復純函式） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `pipelines/ligature_repair.py` | 新增 | `repair_ligatures` 純函式 + 雙閘 + lazy 字集（139 行） |
| `tests/test_ligature_repair.py` | 新增 | 22 測試（正修/雙閘守門/行數不變式/字典兜底） |

（全新檔、無 `.bak`；baton 暫存之 plan/tasks/報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

**真因**：部分 PDF 字型 ToUnicode 表把連字字形（ﬁ/ﬂ/ﬀ/ﬃ/ﬄ）映到錯誤碼位（常見 `1`/`;`）——`Pro1les`/`;rst`/`de1ning`。任何抽取法（fitz 直抽或外部解析服務）皆現、換工具修不好，須文字層獨立正規化。

**修法（`repair_ligatures(text) -> str` 純函式、雙閘防線）**：

1. **窗口鎖定**：regex `(?:(?<=[a-z])[1;](?=[a-z])|^[1;](?=[a-z]))`——僅「小寫×異常字元×小寫」與「詞首異常字元×小寫」（如 `;rst`）兩形態進入候選流程；大寫語境（`M1`）、非 ASCII（中文行）天然不命中。
2. **第一閘（替換前正則排查）**：token 剝殼（僅剝 `([{"'` 詞頭與 `)]}"'.,:!?` 詞尾包覆符、輸出原樣保留）後，核心詞匹配 `^\d+(?:st|nd|rd|th|s)?$`（數字縮寫 `1st`/`2nd`/`10s`）或 `^[vV]\d+(?:\.\d+)*$`（版本號 `v1`/`v1.2`）→ 一律不碰，杜絕 `1st→fist`/`v1→vfi` 類誤殺。
3. **候選替換**：對每個窗口逐一嘗試 `fi/fl/ff/ffi/ffl`；多窗口 token 以深度上限 3 的遞迴逐一修畢。
4. **第二閘（替換後詞形檢查）**：替換結果必須 `isalpha()` 且落在字集內方採信——字集＝**系統字典 `/usr/share/dict/words` 優先**（存在才讀、lazy 一次快取、讀取失敗 warning + `exc_info=True` 降級）**∪ 內建常見連字兜底集**（60 詞、零第三方依賴）；輕量詞形放寬僅「複數 s 退單數再查」。任一閘不過 → 保留原樣（fail-open：誤殺比漏修貴）。
5. **行數不變式**：`text.split("\n")` 逐行 `re.sub(r"\S+", ...)` 行內替換後 `"\n".join`——嚴禁增刪行、下游判型 sidecar 行索引基準零汙染。

## §5 測試結果

```
tests/test_ligature_repair.py 22 passed in 0.57s
（正修 5 / 雙閘守門 12〔含 1st/2nd/3rd/4th/10s/v1/v1.2/v12.3.4 參數化〕/
 行數不變式 2 / 字典兜底 3〔缺席 monkeypatch/系統字典優先+lazy 快取/讀取失敗降級〕）

全套件：869 passed, 3 skipped, 3 warnings in 52.99s   ← C1 後基線 847 + 22、零回歸
```

驗收 grep（§6.2 全項）：

```
grep -n "def repair_ligatures" pipelines/ligature_repair.py
  130:def repair_ligatures(text: str) -> str:
grep -n "words" pipelines/ligature_repair.py
  55:_SYSTEM_DICT_PATH = Path("/usr/share/dict/words")（+ 兜底集/快取邏輯）
grep -rn "ligature_repair" pipelines/litedoc_pipeline.py processor/ → 零命中（C2 零接線）
```

SOP 一致性核查（§6.4）：

```
logging：grep logger.error/exception/traceback.format_exc → 無命中（合規）；
         唯一 logger.warning（字典讀取降級）含 exc_info=True ✅
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/md_cleaner.py` — byte 不動（連字修復獨立新模組、`git status` 無此檔）
- [x] `pipelines/litedoc_pipeline.py` — 零接線（C3 才接）
- [x] 零第三方字典/NLP 依賴（系統字典為 OS 檔案、非套件；缺席走內建兜底）
- [x] 行數不變式（測試斷言鎖定）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / C1 / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）**（消費 C1 `FitzProcessor`/`median_page_chars` + C2 `repair_ligatures`、settings 三常數、§7.2 整合測試）；待 baron ship C2 後另下 C3 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（本 commit 全新增檔、無須備份）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add pipelines/ligature_repair.py
git add tests/test_ligature_repair.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST-FITZ_C2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST-FITZ_C2_msg.txt
```
