# PIPE-RESUME SHADOW-HOTFIX-2 — 執行報告（B軌影子標題後綴與履歷公司名翻譯修復）

---

**任務代號**：PIPE-RESUME SHADOW-HOTFIX-2（BE-Hotfix）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_hotfix.md`（v2 三處「移除矛盾」版）
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Hotfix、全套件僅 env flake)

> **流程註**：16:40 baron 首發 Run 提示詞 §2 為舊版（v1：改 A軌 `translate_processor.py` + 加翻譯規則），與現行已核准 hotfix.md（v2 三處）矛盾 → 已 HALTED 呈報；baron 裁示「**照 hotfix.md**」後依 v2 落地。

---

## §0 改版規則
- 改版觸發：§1–§8 任一執行條款變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **基準**：PIPE-RESUME v9（C1-C7）+ TILING-HOTFIX-1 後。B軌履歷翻譯有兩症狀:①影子前端列表漏顯 ` (測試)`（`translated_title` 遮蓋 `title`）；②公司/機構名未翻（`VIEWTRIX TECHNOLOGY`）——因 B軌系統提示詞**三層打架**：母提示詞 `content_translate_prompt.txt` L5「機構翻譯附原文」vs ②`translator.py:40` STYLE_HINTS / ⑤`resume_pipeline.py` `_RESUME_CONSTRAINTS[0]`「公司保留原文」。
- **完成狀態**：B軌**三處「移除矛盾、交回母提示詞」**（核心原則：不加新規則）:
  1. `web_server.py` 影子寫庫 `if ctx.raw_metadata:` 分支補綴 `translated_title` ` (測試)`（防禦 guard）。
  2. `processor/translator.py:40` `_STYLE_HINTS['resume']` 移除「公司名」。
  3. `pipelines/resume_pipeline.py:109` `_RESUME_CONSTRAINTS[0]` 改「產品名保留原文」。
  全變更 `# === [PIPE-RESUME SHADOW-HOTFIX-2 START/END] ===` 包裹。**不改** `translate_processor.py`（A軌棄修）與母提示詞。
- **測試**：resume 21 / translator 8 / (resume_processor+pipe_scaffold) 19 passed；全套件 **486 passed / 1 failed（僅 env flake）/ 3 skipped**。

---

## §2 Commit 表格
| Commit | 內容 | Hash |
|---|---|---|
| SHADOW-HOTFIX-2 | B軌三處移除公司翻譯矛盾 + translated_title 補 (測試) + 2 回歸測試 | （留空，由 baron 回填） |

---

## §3 變動檔案清單
| 狀態 | 檔案 | 備份 | 說明 |
|---|---|---|---|
| 修改 | `web_server.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_web_server.py.bak` | C5 影子區塊 translated_title 補 (測試) |
| 修改 | `processor/translator.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_translator.py.bak` | STYLE_HINTS['resume'] 移除公司名 |
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_resume_pipeline.py.bak` | _RESUME_CONSTRAINTS[0] 改產品-only |
| 修改 | `tests/test_resume_pipeline.py` | （測試檔、未列 .bak） | 補 2 回歸測試 |

---

## §4 真因與修法

### §4.1 真因：指令三層打架（公司沒翻 + 學歷 doubling）
| 層 | 來源 | 內容 | 方向 |
|---|---|---|---|
| ① 母提示詞 | `content_translate_prompt.txt` L5（A/B 共用） | 機構名稱**翻譯**附原文 | 翻 |
| ② STYLE_HINTS | `translator.py:40`（A軌逐字複製殘渣） | 公司名**保留原文** | 留 🔴 |
| ⑤ constraints | `resume_pipeline.py:109` | 公司名稱**保留原文不翻** | 留 🔴 |
②⑤ 在母提示詞後拼接覆寫 L5 → 公司不翻；對「國立交通大學」這類既要翻又要留的詞 → LLM hedging 吐原文+譯文（doubling）。

### §4.2 修法（移除矛盾、交回 L5）
```python
# 修法一 web_server.py（C5 影子寫庫）
# === [PIPE-RESUME SHADOW-HOTFIX-2 START] ===
if isinstance(meta_dict.get('translated_title'), dict):
    _tt_val = meta_dict['translated_title'].get('value')
    if _tt_val and not str(_tt_val).endswith(" (測試)"):
        meta_dict['translated_title']['value'] = f"{_tt_val} (測試)"
# === [PIPE-RESUME SHADOW-HOTFIX-2 END] ===

# 修法二 translator.py:40
"resume": "文件為個人履歷（CV），請使用正式商務中文，職稱、技術名詞保留原文。",  # 移除「公司名」

# 修法三 resume_pipeline.py:109 _RESUME_CONSTRAINTS[0]
"產品名稱保留原文（如 iPhone／OLED 等）",  # 原「公司名稱、產品名稱保留原文不翻」
```
移除 ②⑤ 後，公司/機構由母提示詞 L5 統一「翻譯 (原文)」、與 A軌一致；產品名仍保留。

---

## §5 測試結果

### §5.1 改動狀態 + 語法
```bash
$ git status -s | grep "\.py$"
 M web_server.py
 M processor/translator.py
 M pipelines/resume_pipeline.py
 M tests/test_resume_pipeline.py
$ ast.parse 三業務檔 → 全 OK
```

### §5.2 測試
```
resume_pipeline + translator：29 passed（含 SHADOW-HOTFIX-2 2 新測試）
resume_processor + pipe_scaffold：19 passed
全套件：486 passed, 1 failed（test_settings_log_format_default_auto = .env LOG_FORMAT=json 環境性、跨所有 commit 恆定）, 3 skipped
```
新增回歸測試:
- `test_shadow_write_appends_translated_title_suffix`：raw_metadata 帶乾淨 translated_title → 斷言補綴 ` (測試)`。
- `test_shadow_hotfix2_company_conflict_removed`：斷言 `_RESUME_CONSTRAINTS` 與 `_STYLE_HINTS['resume']` 皆不含「公司」。

### §5.3 SOP 一致性核查（BE-Hotfix）
```bash
$ grep -nE "logger\.error|traceback.format_exc" web_server.py processor/translator.py pipelines/resume_pipeline.py | grep -v exc_info=True
  web_server.py:138/158/583/698  ← 皆既有行、非本 hotfix 改動（本次僅改 C5 translated_title 區塊、未加 logger）
$ grep -nE "\.commit\(\)" <三檔>  → 無裸 commit（合規）
```
- **logging**：本 hotfix 三處變更（dict 補綴 / 字串 / list）無新增 logger.error（合規）；grep 命中之 4 行為既有碼、不在本 hotfix 物理防線內。
- **database**：無裸 commit；寫庫委派既有 upsert_paper（合規）。

---

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| A軌 `pipeline_core.py` / `translate_processor.py` | [x] ✅ byte 不動（棄修） |
| 母提示詞 `content_translate_prompt.txt` | [x] ✅ 不動（A/B 共用、L5 已正確） |
| `translator.py` 雙模式引擎核心 / `_build_system_prompt` 骨架 | [x] ✅ 不動（僅改 _STYLE_HINTS['resume'] 一行字串） |
| `contracts.py` 凍結合約 / `models.py` / `db.py` | [x] ✅ 不動 |
| A軌 `run_pipeline` 本體 | [x] ✅ byte 不動（僅 C5 影子區塊補綴） |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接
- **baton/ 歸檔**：hotfix.md + 執行.md 一次性 mv → `hotfixes/` + git add。
- **⚠️ Golden Baseline（重要）**：B軌譯文內容改變（公司翻譯）→ D2/chunk 受影響；**Flip/結案前須與 TILING-HOTFIX-1 合併一次重捕**（`venv/bin/python tools/golden_baseline.py capture --all`、baron MinerU）。
- **保留意見（誠實）**：學歷地點行錯亂 / doubling 殘留主因 = B軌 P3「100% Bypass 整檔單發 + U4」架構脆弱，**已立 `RESUME-P3` plan 另開任務**，不在本 hotfix 硬修。E2E 重驗後若殘留，轉 RESUME-P3。
- **回退**：`git checkout web_server.py processor/translator.py pipelines/resume_pipeline.py`（或自 .bak 還原）。

---

## §8 baron 執行命令
```bash
# 1. 備份與歸檔已完成（§3 .bak + hotfix.md/執行.md 已 mv→hotfixes/）

# 2. git add 清單
git add web_server.py
git add processor/translator.py
git add pipelines/resume_pipeline.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_web_server.py.bak
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_translator.py.bak
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_resume_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_hotfix.md
git add .claude-logs/hotfixes/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_執行.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_SHADOW-HOTFIX-2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_SHADOW-HOTFIX-2_msg.txt
```

### §8.2 commit message 草稿
```
fix(shadow): append (測試) to translated_title and remove resume company-keep conflict (B-track)

B軌三處移除矛盾、交回母提示詞 L5：①影子寫庫為 translated_title 同步加綴 (測試)
防前端列表漏顯；②translator.py STYLE_HINTS['resume'] 移除「公司名保留原文」；
③resume_pipeline.py _RESUME_CONSTRAINTS[0] 改為僅保留產品名。公司/機構交回母提示詞
統一「翻譯 (原文)」，根治 B軌公司未翻與指令打架。不動 A軌 translate_processor 與母提示詞。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 記錄 SHADOW-HOTFIX-2 B軌三處代碼修復與驗收 |
| 用途 | 收官 mv 歸檔 hotfixes/ |
| 權威源 | 本檔 §1–§8 + hotfix.md |
| 約束事項 | 限改 B軌三處；嚴禁動 A軌/母提示詞/自發 commit |
| 改版規則 | 直接改章節 + §99.2 加 Revision |
| 刪除條件 | 永久保留歸檔 hotfixes/ |

### §99.2 Revision 歷程
- v1 (2026-06-05)：SHADOW-HOTFIX-2 執行——B軌三處移除公司翻譯矛盾（web_server translated_title 補 (測試) / translator.py:40 移除公司名 / resume_pipeline.py:109 改產品-only），交回母提示詞 L5 統一翻譯；補 2 回歸測試；全套件 486 passed（僅 env flake）。16:40 v1 Run 提示詞矛盾經 baron 裁示「照 hotfix.md」後依 v2 落地。學歷 doubling 殘留歸 RESUME-P3；Golden Baseline 與 TILING-HOTFIX-1 合併重捕。
