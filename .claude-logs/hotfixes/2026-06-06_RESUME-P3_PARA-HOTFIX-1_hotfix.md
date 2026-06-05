# RESUME-P3 PARA-HOTFIX-1 — 緊急熱修復：B軌履歷正文段落黏連（無段落空行）

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 RESUME-P3 C3（逐 heading section 翻譯還原）+ C2（resume 停用 Translator U4）後 B軌正文「兩段黏在一起」的排版 Regression。
> **修復原則**：只移植 A軌既有的「段落邊界正規化」邏輯進 pipelines/（不耦合 A軌 class）、套用於 text item，嚴禁夾帶任何無關的新功能或大型重構。
> **工作流類別**：BE-Hotfix（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（WORKFLOW_SOP §5）。
> **狀態**：📝 文件階段（plan）。本文件僅產出於 `baton/`，**不動業務代碼**；Run（落地）由 baron 後續獨立提示詞觸發。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **PARA-HOTFIX-1** | `（待 baron Run 後回填）` | `fix(resume): RESUME-P3 PARA-HOTFIX-1 — B軌正文段落邊界正規化 (修兩段黏一起)` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：B軌（影子，`doc_type='resume'`）履歷的雙語 Markdown 中，**正文相鄰段落之間沒有空行、渲染後黏成一團**；同一份文件 A軌輸出則段落之間有正常留白。
- **受災範圍**：B軌 `ResumePipeline.run_phase3` → `_restore_sections_markdown` 產出的 `final_zh` 正文 text。**僅 B軌履歷**；A軌（`md_restore_processor`）不受影響。非崩潰性、但破壞可讀性。
- **首發來源**：baron 肉眼比對 A軌（有留白）vs B軌（黏連）渲染結果——**邏輯型 Regression、非例外崩潰**。

### 2. 真因診斷 (Root Cause)

**Markdown / CommonMark 規範**：段落之間必須有**空行（`\n\n`）**才會被解析為獨立 `<p>`；**單一換行（`\n`）= soft break**，在 HTML 中被渲染為一個空格、視為同一段。

**A軌為什麼有留白**——兩道機制（grep 鋼證）：
- **機制 1**：[`_write_to_md` L585-587](processor/md_restore_processor.py:585)——每寫一塊內容都 `f.write(content + "\n\n")`，塊與塊之間天然補空行。
- **機制 2**：[`_preserve_pipe_table` L629](processor/md_restore_processor.py:629)——每塊 text 跑
  ```python
  text = re.sub(r'(?<!\|)(?<!\n)\n(?![\n\|])', '\n\n', text)
  ```
  把**段內單一 `\n` 全升級為 `\n\n`**（pipe table rows 以 `|` 開頭、由 lookbehind/ahead 保護不被拆散）。

**B軌為什麼黏連**——兩道機制皆無（grep 鋼證）：
- [`_restore_one_section`](pipelines/resume_pipeline.py:555) 對 text item **只 `parts.append(譯文)`、不做任何 `\n` 正規化**。
- [`_restore_sections_markdown`](pipelines/resume_pipeline.py:544) 僅在**不同 part（不同內容項）之間** `"\n\n".join(...)` → 但**同一段譯文字串內部的單 `\n` 原封不動** → CommonMark soft break → 黏一起。
- 且 **RESUME-P3 C2** 為保條列/日期/地點原行結構，已對 resume **停用 Translator U4（`。！？` 斷句重切）** → B軌整條鏈**沒有任何地方**會把單 `\n` 升級為段落空行。

- **定位程式碼**：[`pipelines/resume_pipeline.py:566-571`](pipelines/resume_pipeline.py:566)（`_restore_one_section` 的 text item 分流，缺段落正規化）。

---

## 熱修復修法 (Minimal Hotfix)

**設計決策（baron 拍板）**：把 A軌 `_preserve_pipe_table` 的「pipe-table-safe 單 `\n`→`\n\n`」邏輯**移植為 pipelines/ 私有 helper**（`_normalize_paragraph_breaks`，**不 import、不耦合 A軌 `md_restore_processor` class**，符合 RESUME-P3「pipelines/ 內重建、不耦合即將棄用 A軌」原則），在 `_restore_one_section` 處理 **text item** 時套用。

**範圍界定（與 A軌一致）**：只對 **text** 套用正規化；**formula / figure / table / 純字串 fallback 中的非 text** 保留原結構（A軌亦只對 text item 跑 `_preserve_pipe_table`、formula/figure/table 原樣寫出）。

### 改動 1：`pipelines/resume_pipeline.py` 新增私有 helper（移植 A軌邏輯、不耦合）

```python
    # === [RESUME-P3 PARA-HOTFIX-1 START] ===
    @staticmethod
    def _normalize_paragraph_breaks(text: str) -> str:
        """段落邊界正規化（pipe-table-safe 單 \\n → \\n\\n）。

        移植 A軌 md_restore_processor._preserve_pipe_table 的邏輯至 pipelines/、
        **不耦合 A軌 class**（RESUME-P3「pipelines/ 內重建、不耦合即將棄用 A軌」原則）。
        真因：B軌逐 section 還原只在不同 part 間放 \\n\\n，段內單 \\n 不處理 →
        CommonMark soft break → 兩段黏一起（A軌靠 _write_to_md 補 \\n\\n + 本邏輯升級單 \\n）。

        規則：一般段落單 \\n 升級 \\n\\n（製造段落空行）；pipe table 區塊
        （以 | 開頭連續行）rows 之間單 \\n 保留（否則 table 渲染破碎）。
        """
        import re
        if not text:
            return text
        lines = text.split("\n")
        out_lines: List[str] = []
        in_table = False
        for line in lines:
            is_table_row = bool(re.match(r"^\s*\|", line))
            if is_table_row:
                if not in_table and out_lines and out_lines[-1].strip():
                    out_lines.append("")          # 進 table 前補空行作 paragraph 邊界
                in_table = True
                out_lines.append(line)
            elif in_table:
                in_table = False
                if line.strip():
                    out_lines.append("")          # table 結束補空行作分隔
                out_lines.append(line)
            else:
                out_lines.append(line)
        text = "\n".join(out_lines)
        # table 區塊外一般 paragraph：單 \n 轉 \n\n（避開 | 開頭行）
        text = re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])", "\n\n", text)
        return text
    # === [RESUME-P3 PARA-HOTFIX-1 END] ===
```

### 改動 2：`_restore_one_section` text item 套用（含字串 fallback 分支）

```diff
         for item in sec.get("content", []) or []:
             if isinstance(item, dict):
                 itype = item.get("type")
                 content = item.get("content", "") or ""
                 if itype == "text":
-                    parts.append(self._t(content, inj, tr, "content") if translate else content)
+                    # === [RESUME-P3 PARA-HOTFIX-1 START] text 套用段落邊界正規化（formula/figure/table 不套）===
+                    rendered = self._t(content, inj, tr, "content") if translate else content
+                    parts.append(self._normalize_paragraph_breaks(rendered))
+                    # === [RESUME-P3 PARA-HOTFIX-1 END] ===
                 else:
                     # formula / figure / table 等：保留原文結構、不翻
                     if content:
                         parts.append(content)
             else:
                 # 容錯：content 為純字串 list（md_processor 原始型態）
                 txt = str(item).strip()
                 if txt:
-                    parts.append(self._t(txt, inj, tr, "content") if translate else txt)
+                    # === [RESUME-P3 PARA-HOTFIX-1 START] 字串 fallback 亦為正文、同套正規化 ===
+                    rendered = self._t(txt, inj, tr, "content") if translate else txt
+                    parts.append(self._normalize_paragraph_breaks(rendered))
+                    # === [RESUME-P3 PARA-HOTFIX-1 END] ===
```

**不動清單（嚴守最小侵入）**：
- 標題還原（HEADING-HOTFIX-1 的 `level=min(2+depth,6)`）——不動。
- formula / figure / table 分支——不套正規化（與 A軌一致、保結構）。
- `_translate_whole` / `_t` / C4 退化偵測——不動。
- `run_phase3` 主流程 / `BilingualMarkdownSpec` 合約——不動。
- A軌 `md_restore_processor`（**不 import、不耦合**）/ `translate_processor` / 其餘四路 / 母提示詞 / DB Schema——不動。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（Run 階段執行）
追加 1 測試至 `tests/test_resume_pipeline.py`（mock Translator 回顯、不打真 API）：
- `test_p3_text_paragraph_blank_line_normalized`：
  - text item 含「兩段以單一 `\n` 分隔」+「一個 pipe table（兩 rows 以單 `\n` 分隔）」。
  - 斷言 **(a)** 兩段之間出現 `\n\n`（段落空行升級成功）；**(b)** pipe table 兩 rows 仍以單 `\n` 相連（`| ... |\n| ... |` 未被拆散）。
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q     # 期望：全綠（含新測試）
$ venv/bin/python -m pytest tests/ -q                            # 期望：全套件不退化（僅既知 LOG_FORMAT env flake）
```

### 2. 驗收 grep
```bash
grep -n 'RESUME-P3 PARA-HOTFIX-1' pipelines/resume_pipeline.py                 # 期望：START/END 包裹命中
grep -n 'def _normalize_paragraph_breaks' pipelines/resume_pipeline.py         # 期望：1（helper 存在）
grep -n '_preserve_pipe_table\|md_restore_processor\|RestoreProcessor' pipelines/resume_pipeline.py  # 期望：0（不耦合 A軌）
grep -n 'def test_p3_text_paragraph_blank_line_normalized' tests/test_resume_pipeline.py             # 期望：1
# SOP — logging / database
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
```

### 3. 本地 E2E 快速復現與驗證（baron 影子上傳）
重跑一份履歷影子 → 開 B軌 `final_zh` 確認：
- 工作經歷各段「工作職責 / 各條列說明」之間有**空行留白**、不再黏連。
- 含表格的段落（學歷 table 等）**table 結構不破**（rows 對齊正常）。

### 4. ⚠️ 行為變更 + Golden 重捕
本 hotfix **改變 B軌履歷 `final_zh` 的段落空行結構** → 衝擊 golden D1（雙語 markdown 結構）/ D2（譯文相似度）。**Flip/結案前須重捕 resume 單路 golden**：
```bash
venv/bin/python tools/golden_baseline.py capture resume --force
```
（與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 / HEADING-HOTFIX-1 同屬「B軌輸出變更須重捕」一類。）

---

## 回退與備案

```bash
# 單獨回退本 hotfix（保留 RESUME-P3 C1-C6 + HEADING-HOTFIX-1）
git revert <PARA-HOTFIX-1-hash>

# 若引發更大 Regression、退回 HEADING-HOTFIX-1 落地點（待其 hash 回填後填入）
git reset --hard <HEADING-HOTFIX-1-hash>
```

---

## 附錄：受影響檔案與包裹標記

| 檔案 | 改動 | 標記 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 新增 `_normalize_paragraph_breaks`（移植 A軌邏輯、不耦合）+ `_restore_one_section` text/字串 fallback 套用 | `# === [RESUME-P3 PARA-HOTFIX-1 START/END] ===` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_text_paragraph_blank_line_normalized` | 同上包裹 |
| `.bak` 備份 | `archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak`（+ 測試檔 .bak）| 改前備份鐵律 |

## §commit baron 執行命令（Run 階段交付參考）
```bash
# 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak

# git add（收官 mv hotfix.md + 執行.md → hotfixes/ 後）
git add pipelines/resume_pipeline.py tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_PARA-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_PARA-HOTFIX-1_run_提示詞.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_PARA-HOTFIX-1_執行.md

# commit（msg 草稿 /tmp/RESUME-P3_PARA-HOTFIX-1_msg.txt）
git commit -F /tmp/RESUME-P3_PARA-HOTFIX-1_msg.txt
```

### commit message 草稿
```
fix(resume): RESUME-P3 PARA-HOTFIX-1 — B軌正文段落邊界正規化 (修兩段黏一起)

修改 pipelines/resume_pipeline.py：
1. 新增 pipelines/ 私有 helper _normalize_paragraph_breaks（移植 A軌 _preserve_pipe_table 的 pipe-table-safe 單 \n→\n\n 邏輯、不耦合 A軌 class）。
2. _restore_one_section 處理 text item（含純字串 fallback）時套用段落邊界正規化，使段內單 \n 升級為 \n\n（空行）；formula/figure/table 不套用、pipe table rows 保留原 \n。
修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_text_paragraph_blank_line_normalized 驗證段落單 \n 升級 \n\n、且 pipe table rows 不被拆散。
變更與新增區塊已使用 # === [RESUME-P3 PARA-HOTFIX-1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
