# Phase 3 Commit SHADOW-HOTFIX-2 — 緊急熱修復：B 軌影子標題 (測試) 後綴與履歷公司名翻譯修復

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門修正 PIPE-RESUME **v9 影子（B 軌）** 管線中發現的標題顯示與公司名翻譯問題。
> **範圍鎖定（B 軌唯一）**：本 hotfix **只修 B 軌**（`run_pipeline_shadow` + `pipelines/resume_pipeline.py` + `processor/translator.py`）。A 軌（舊單體 `pipeline_core.py` + `translate_processor.py`）即將隨五路改完整體捨棄、**不在本 hotfix 修復範圍**（baron 拍板：A 軌無修復價值）。
> **修復原則**：**移除 B 軌與母提示詞打架的覆寫**（不加新規則）；只動受災點、嚴禁夾帶新功能或大型重構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **SHADOW-HOTFIX-2** | `待回填` | fix(shadow): append (測試) to translated_title and remove conflicting resume company-keep overrides in B-track |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象一（B 軌標題漏顯後綴）**：上傳履歷 `DeHunt_CTO_Tzung-Yuan_Lee.pdf` 後，B 軌寫入資料庫的標題在前端列表顯示為 `Tzung-Yuan Lee (李宗原)`，漏掉 ` (測試)` 後綴，無法與 A 軌正本在 UI 上肉眼區分。
- **現象二（B 軌公司名未翻 + 學歷原文/譯文重複）**：
  ```
  公司（受災）：VIEWTRIX TECHNOLOGY - Technology Senior Manager, ... （整段未翻、保留英文）
  學歷（受災）：National Chiao Tung University - Ph.D. Candidate, ... （英文原文行）
               Hsinchu, Taiwan 國立交通大學 (National Chiao Tung University) - … 新竹，台灣 (Hsinchu, Taiwan)（原文+譯文重複、地點錯亂）
  期望（= A 軌）：視曜半導體 (VIEWTRIX TECHNOLOGY) - … ／ 國立交通大學 (National Chiao Tung University) …（中文 (原文)、單一行）
  ```
- **受災範圍（B 軌）**：前端影子標籤顯示（`translated_title`）；B 軌履歷（`doc_type='resume'`）內容翻譯（公司/機構名、學歷段）。

### 2. 真因診斷 (Root Cause)
1. **標題漏顯（B 軌）**：影子寫庫端 `web_server.py:run_pipeline_shadow`（v9 C5 區塊 L648-669）中，`Paper.title` 已含 ` (測試)`，但 `Paper.translated_title` 由 `paper_manager.upsert_paper` 從 `metadata['translated_title'].value`（`ctx.raw_metadata` 整包帶入、**乾淨無後綴**）解析寫入（`paper_manager.py:231-233`）；前端顯示**優先取非空 `translated_title`**（`web_server.py:985`），故漏顯 ` (測試)`。

2. **公司未翻 + 學歷重複（B 軌）＝ 指令三層打架**：B 軌履歷翻譯走 `pipelines/resume_pipeline.py::run_phase3` → `processor/translator.py::Translator`，其系統提示詞由 `_build_system_prompt` 五步疊加。**同一條「公司/機構」政策被三層用相反方向講**：

   | 層 | 來源 | 內容 | 方向 |
   |---|---|---|---|
   | ① 母提示詞 | `prompt/translate/content_translate_prompt.txt` L5（A/B 軌共用） | 機構名稱**翻譯**後附原文 | 翻 ✅ |
   | ② STYLE_HINTS | `processor/translator.py:40` `_STYLE_HINTS['resume']` | 公司名**保留原文** | 留 🔴 |
   | ⑤ constraints | `pipelines/resume_pipeline.py:109` `_RESUME_CONSTRAINTS[0]` | 公司名稱**保留原文不翻** | 留 🔴 |

   - **公司沒翻**：②⑤ 在母提示詞之後拼接、覆寫了 L5 → LLM 留英文。
   - **學歷原文+譯文重複**：對「國立交通大學」這種既被 L5 要求翻、又被 ②⑤ 要求留的詞，LLM **兩邊討好 → 同時吐原文行 + 譯文行**（hedging），再被 U4 多行重分行（`translator.py:188`）攪亂地點行 → 怪格式。
   - **為何 A 軌乾淨**：A 軌**無 ⑤ constraints 層**、且逐區塊翻譯（非整檔單發），矛盾較弱、結構保全。

   > **架構註**：② `_STYLE_HINTS['resume']` 是 A 軌 `translate_processor.py:235` 的**逐字複製殘渣**。新引擎設計意圖為「通用規則進母提示詞、文體專屬規則進 ⑤ constraints」，卻把舊 STYLE_HINTS 整套照抄，形成第三個重複管道並與母提示詞反向覆寫。本 hotfix 僅精準移除 resume 上的矛盾內容；「STYLE_HINTS 與 constraints 兩管道是否合一」屬架構債、待 A 軌死後另開任務清理。

   > **⚠️ 修錯檔注意**：B 軌**不經** `translate_processor.py`（A 軌路徑）；修它對 B 軌**完全無效**。

---

## 熱修復修法 (Minimal Hotfix)

**核心原則：移除 B 軌的矛盾覆寫，交回母提示詞 L5（已正確）治理——不加新規則。** 共動 **3 處**。

### 修法一 · `web_server.py` — 影子 `translated_title` 同步加綴 (測試)
於 v9 C5 影子寫庫區塊 `if ctx.raw_metadata:` 分支內補綴：
```diff
                 meta_dict['translated_abstract'] = {
                     'value': _tabs_val, 'source': 'pipeline', 'confidence': 'high',
                 }
+                # 影子標題後綴同步至 translated_title，防止前端列表（優先取 translated_title）漏顯 (測試)
+                if isinstance(meta_dict.get('translated_title'), dict):
+                    _tt_val = meta_dict['translated_title'].get('value')
+                    if _tt_val and not str(_tt_val).endswith(" (測試)"):
+                        meta_dict['translated_title']['value'] = f"{_tt_val} (測試)"
             else:
```
> 防禦性：`translated_title` 不存在／為空時不動作 → `upsert_paper` 寫空 → 前端 fallback 到已帶 ` (測試)` 的 `title`，兩情況皆正確。

### 修法二 · `processor/translator.py:40` — 移除 STYLE_HINTS 殘渣中的「公司名」
公司交回母提示詞 L5 翻譯；職稱、技術名詞仍保留原文（母提示詞未特別管）：
```diff
-    "resume": "文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文。",
+    "resume": "文件為個人履歷（CV），請使用正式商務中文，職稱、技術名詞保留原文。",
```

### 修法三 · `pipelines/resume_pipeline.py:109` — `_RESUME_CONSTRAINTS[0]` 只留履歷專屬（產品）
刪除公司保留規則（交回母提示詞 L5）；產品名保留原文（baron 拍板）：
```diff
 _RESUME_CONSTRAINTS = [
-    "公司名稱、產品名稱保留原文不翻",
+    "產品名稱保留原文（如 iPhone／OLED 等）",
     "Email／電話／URL 原樣保留",
     "專業技能詞（Python/Docker 等）保留英文",
     "專有名詞（如專利、期刊等名稱）保留原文並在中譯中附加對照",
 ]
```
> **不改 `content_translate_prompt.txt`**（已正確、A/B 共用、動它波及 A 軌）；**不改 `translate_processor.py`**（A 軌、棄修）。移除 ②⑤ 後，公司/機構由母提示詞 L5 統一「翻譯 (原文)」、與 A 軌一致；產品名仍保留。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py tests/test_translator.py -q
# 期望：全綠（含下方新增回歸測試）
```
**建議補回歸測試**（`# === [PIPE-RESUME SHADOW-HOTFIX-2 START/END] ===` 包裹）：
- **translated_title 後綴**（`tests/test_resume_pipeline.py`）：影子寫庫場景，`ctx.raw_metadata` **帶 `translated_title`** → 斷言傳入 `upsert_paper` 的 `meta_dict['translated_title']['value']` 結尾為 ` (測試)`。
  *(現有 C6 `test_c5_shadow_write_uses_raw_metadata` 的 FakeOrch 未帶 `translated_title`、走 guard=False，不覆蓋本新行為，故須新增。)*
- **矛盾已移除**：斷言 `rp._RESUME_CONSTRAINTS[0]` **不含**「公司」「保留原文」；`translator._STYLE_HINTS['resume']` **不含**「公司名」（防被改回）。

### 2. 本地 E2E 快速復現與驗證
手動上傳 `DeHunt_CTO_Tzung-Yuan_Lee.pdf`，檢查 **B 軌（測試）** 產物：
1. 前端側邊欄顯示 `Tzung-Yuan Lee (李宗原) (測試)`。
2. 公司名呈「中文 (原文)」：`視曜半導體 (VIEWTRIX TECHNOLOGY) - …`；產品/技術詞（OLED/SoC）維持原文。
3. 學歷段恢復**單一譯文行**（無原文重複、地點不錯亂）：`國立交通大學 (National Chiao Tung University) … ／ 新竹，台灣 (Hsinchu, Taiwan)`。

### 3. 🛡️ Golden Baseline 重捕防線（與 TILING-HOTFIX-1 合併一次）
`_RESUME_CONSTRAINTS` / STYLE_HINTS 改動 = B 軌**譯文內容改變** → 衝擊 D2（譯文相似度 0.95）與 chunk 內容。**與 TILING-HOTFIX-1 的重捕合併、一次完成**（baron 於 MinerU 實跑機）：
```bash
baron@MinerU$ venv/bin/python tools/golden_baseline.py capture --all   # 容差 D2≥0.95 / D3≥0.90
```

> **⚠️ 保留意見（誠實）**：doubling 主因是指令打架（本 hotfix 已移除），但 B 軌 P3 為「100% Bypass 整份單次翻譯 + 原文直寫」（C4 設計）+ U4 重分行，對結構化履歷仍偏脆弱。移除矛盾是高槓桿第一步、**須 E2E 重驗**；若 doubling 仍殘留，屬 B 軌 P3 架構問題（逐區塊翻譯 / md_restore 對齊）、**另開獨立任務**，不在本 hotfix 硬修。

---

## 回退與備案

```bash
# 還原受災檔案（B 軌三處）
git checkout web_server.py processor/translator.py pipelines/resume_pipeline.py
```
