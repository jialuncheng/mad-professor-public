# RESUME-P3 HEADING-HOTFIX-1 — 緊急熱修復：B軌履歷標題層級塌陷（全 h1、無階層）

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正 RESUME-P3 C3（逐 heading section 翻譯還原）落地後發現的標題層級 Regression。
> **修復原則**：只改動受災點 `_restore_one_section` / `_restore_sections_markdown` 的層級推算邏輯，嚴禁夾帶任何無關的新功能或大型重構。
> **工作流類別**：BE-Hotfix（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（WORKFLOW_SOP §5）。
> **狀態**：📝 文件階段（plan）。本文件僅產出於 `baton/`，**不動業務代碼**；Run（落地）由 baron 後續獨立提示詞觸發。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HEADING-HOTFIX-1** | `（待 baron Run 後回填）` | `fix(resume): RESUME-P3 HEADING-HOTFIX-1 — B軌標題層級改由遞迴深度推算 (修標題塌陷全 h1)` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：B軌（影子，`doc_type='resume'`）履歷的雙語 Markdown 中，**所有 `###` 標題全部塌成同一個最大級（h1）、完全沒有層級**。
  - 範例（baron 前端截圖）：頂層段落「**工作經歷**」與其底下的公司條目「**AI 生物電子健康科技 (AI Bioelectronic Healthtech) - CTO (2025/08 ~ 至今)**」渲染成**同樣巨大**的標題，公司條目本應是「工作經歷」的子層（較小），卻與之並列同大。
  - 直觀症狀：**「標題過大、只有一個層級」**——整份履歷的章節階層被壓平。
- **受災範圍**：B軌 `ResumePipeline.run_phase3` 產出的 `final_zh`（逐 section 重組譯文）。**僅 B軌履歷**；A軌（`md_restore_processor`，正確讀 `heading_level`）不受影響。非崩潰性、但嚴重破壞可讀性與排版正確性。
- **首發來源**：baron 肉眼比對 B軌前端渲染結果（無 traceback——此為**邏輯型 Regression**、非例外崩潰）。

### 2. 真因診斷 (Root Cause)

- **定位程式碼**：[`pipelines/resume_pipeline.py:562`](pipelines/resume_pipeline.py:562)（`_restore_one_section`，RESUME-P3 C3 新建）
  ```python
  level = int(sec.get("level") or sec.get("heading_level") or 1)
  ...
  parts.append(f"{'#' * max(1, min(level, 6))} {zh_title}")
  ```

- **技術細節（兩層真因）**：

  **(A) `level` 欄位是恆等於 1 的「扁平死欄」**
  md2json / json_process 產出的 section JSON 中，章節的**真實巢狀深度是靠 `children` 樹狀結構**表達，而 `level` 欄位**不分深淺、一律寫死 1**。實測 dump（academic processed JSON、與 resume 同一套 processor）鋼證：

  | 真實階層（樹深度）| `level` 欄 | `heading_level` 欄 | 範例標題 |
  |---|---|---|---|
  | 頂層（depth 0）| **1** | **2** | `II. SOLID STATE TRANSFORMER...` |
  | 子層（depth 1）| **1** | **3** | `A. Overall Architecture` |
  | 孫層（depth 2）| **1** | **4** | `1) High-Level Control` |

  → `level` 欄對所有節點都是 1；`heading_level` 才帶真實深度，且**恰好 = 2 + 樹深度**。

  **(B) `or` 短路求值「永遠取到 1」**
  `sec.get("level") or sec.get("heading_level") or 1` —— Python `or` 短路：
  - `sec.get("level")` 回 `1`（truthy）→ **立即回傳、永遠不會走到 `heading_level`**。
  - 結果：每個 section 的 `level` 都被算成 `1` → 全部渲染成 `#`（h1）→ **全標題等大、單一層級**。
  - 作者其實已意識到 `heading_level` 的存在（寫進了 fallback 鏈），但**把它排在恆真的 `level` 之後**，被短路擋死、形同未用。

- **為何 C3 漏掉**：RESUME-P3 C3「在 pipelines/ 內重建還原邏輯、不耦合 A軌 `md_restore_processor`」時，自行撰寫 `_restore_one_section`，沿用了 processed JSON 看似合理的 `level` 欄位，未察覺該欄為扁平死欄（真實深度在 `heading_level` 與樹結構）。A軌 `md_restore_processor` 走的是 `heading_level`，故無此症。

---

## 熱修復修法 (Minimal Hotfix)

**設計決策（baron 拍板）**：**不依賴任何資料欄位**（`level` 已證實不可靠、`heading_level` 雖正確但同樣是「信任外部資料」），改由 **`_restore_one_section` 的遞迴深度 `depth` 直接推算**標題層級。

**推算規則**：
- 頂層 section → **h2**（`##`）。理由：候選人姓名為文件 h1（由 md_restore 樣板另行渲染、不在本 section 樹內），故章節從 h2 起算。
- 每下潛一層 `children` → 層級 **+1**（h3、h4…）。
- 上限 **h6**（Markdown / HTML 標題上限）。
- 公式：`level = min(2 + depth, 6)`，`depth` 由 `_restore_sections_markdown` 以 `0` 起算、逐層 `+1` 傳入。

**等價性佐證**：上表 `heading_level == 2 + 樹深度`，故本遞迴深度公式**在資料正確時與 `heading_level` 完全等價**，但**不再依賴該欄位是否被正確填寫**——即使未來 processor 改版漏填 `heading_level`，層級仍由結構保證正確。

### `pipelines/resume_pipeline.py` — 最小改動（`# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` 包裹）

**改動點 1：`_restore_sections_markdown` 起始 depth=0 傳入**
```diff
     def _restore_sections_markdown(
         self, sections: List[Dict[str, Any]], inj: "InjectionContext",
         tr: "Translator", translate: bool,
     ) -> str:
         """逐 section 遞迴：標題/正文分流翻譯 + 按 level 還原 Markdown，重組為單一字串。"""
         parts: List[str] = []
         for sec in sections or []:
             if isinstance(sec, dict):
-                self._restore_one_section(sec, inj, tr, translate, parts)
+                # === [RESUME-P3 HEADING-HOTFIX-1 START] 頂層 section 由 depth=0 起算（→ h2）===
+                self._restore_one_section(sec, inj, tr, translate, parts, depth=0)
+                # === [RESUME-P3 HEADING-HOTFIX-1 END] ===
         return ("\n\n".join(p for p in parts if p)).strip() + "\n"
```

**改動點 2：`_restore_one_section` 簽名加 `depth`、層級改遞迴深度推算、遞迴 children 時 depth+1**
```diff
     def _restore_one_section(
         self, sec: Dict[str, Any], inj: "InjectionContext", tr: "Translator",
-        translate: bool, parts: List[str],
+        translate: bool, parts: List[str], depth: int = 0,
     ) -> None:
         """單一 section：還原標題（# * level）+ 逐 content item 分流，遞迴 children。"""
         title = (sec.get("title") or "").strip()
         if title:
-            level = int(sec.get("level") or sec.get("heading_level") or 1)
+            # === [RESUME-P3 HEADING-HOTFIX-1 START] ===
+            # 標題層級改由「遞迴深度」推算，不再讀資料欄位。
+            # 真因：processed JSON 的 level 欄恆=1（扁平死欄），原 `sec.get("level") or
+            # sec.get("heading_level")` 因 or 短路永遠取到 1 → 全標題塌成 h1、無階層。
+            # 深度推算：頂層 section = h2（候選人名為 h1、另由 md_restore 樣板渲染），
+            # 每下潛一層 children +1、上限 h6；等價於資料正確時的 heading_level（= 2 + 深度），
+            # 但不依賴該欄位是否被正確填寫（結構保證階層）。
+            level = min(2 + depth, 6)
+            # === [RESUME-P3 HEADING-HOTFIX-1 END] ===
             zh_title = self._t(title, inj, tr, "title") if translate else title
-            parts.append(f"{'#' * max(1, min(level, 6))} {zh_title}")
+            parts.append(f"{'#' * level} {zh_title}")

         for item in sec.get("content", []) or []:
             if isinstance(item, dict):
                 itype = item.get("type")
                 content = item.get("content", "") or ""
                 if itype == "text":
                     parts.append(self._t(content, inj, tr, "content") if translate else content)
                 else:
                     # formula / figure / table 等：保留原文結構、不翻
                     if content:
                         parts.append(content)
             else:
                 # 容錯：content 為純字串 list（md_processor 原始型態）
                 txt = str(item).strip()
                 if txt:
                     parts.append(self._t(txt, inj, tr, "content") if translate else txt)

         for child in sec.get("children", []) or []:
             if isinstance(child, dict):
-                self._restore_one_section(child, inj, tr, translate, parts)
+                # === [RESUME-P3 HEADING-HOTFIX-1 START] children 下潛一層 depth+1 ===
+                self._restore_one_section(child, inj, tr, translate, parts, depth=depth + 1)
+                # === [RESUME-P3 HEADING-HOTFIX-1 END] ===
```

**不動清單（嚴守最小侵入）**：
- `content` item 分流（text / formula / figure / table）邏輯——不動。
- `_translate_whole` / `_t` / C4 退化偵測（`_is_heading_degraded` / `_flatten_sections` / `_own_text_len`）——不動（它們不發標題、不受 depth 影響）。
- `run_phase3` 主流程 / `BilingualMarkdownSpec` 合約——不動。
- A軌 `md_restore_processor` / `translate_processor`、其餘四路、母提示詞、DB Schema——不動。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（Run 階段執行）
追加 1 個遞迴深度層級測試至 `tests/test_resume_pipeline.py`（mock Translator、不打真 API）：
- `test_p3_heading_level_by_recursion_depth`：建一個 3 層巢狀 section（頂/子/孫，每節 `level=1`、`heading_level` 故意填錯或缺）→ 斷言 `_restore_sections_markdown` 輸出的標題前綴為 `## ` / `### ` / `#### `（h2/h3/h4），證明**層級來自遞迴深度、不受資料欄位影響**、且**至少兩個不同層級**（防回歸到單一層級）。
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q     # 期望：全綠（含新測試）
$ venv/bin/python -m pytest tests/ -q                            # 期望：全套件不退化（僅既知 LOG_FORMAT env flake）
```

### 2. 驗收 grep
```bash
grep -n 'RESUME-P3 HEADING-HOTFIX-1' pipelines/resume_pipeline.py   # 期望：START/END 包裹命中
grep -n "sec.get(\"level\")" pipelines/resume_pipeline.py            # 期望：0（恆=1 死欄讀取已移除）
grep -n 'depth=depth + 1\|depth: int = 0\|min(2 + depth' pipelines/resume_pipeline.py  # 期望：遞迴深度推算命中
# SOP — logging（logger.error 須 exc_info）/ database（無裸 commit）
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
```

### 3. 本地 E2E 快速復現與驗證（baron 影子上傳）
重跑一份履歷影子 → 開 B軌 `final_zh` 確認：
- 「工作經歷」「學歷」「技能」等頂層段落 = `##`（h2）。
- 公司條目（AI 生物電子健康科技 - CTO…）= `###`（h3、明顯小於 h2）。
- **至少兩個層級、公司條目小於其所屬章節** → 階層回復、不再全 h1。

### 4. ⚠️ 行為變更 + Golden 重捕
本 hotfix **改變 B軌履歷 `final_zh` 的標題層級（`#` → `##`/`###`/`####`）** → 衝擊 golden D1（雙語 markdown 結構）/ D2（譯文相似度，標題行字數不變但 `#` 數變）。**Flip/結案前須重捕 resume 單路 golden**：
```bash
venv/bin/python tools/golden_baseline.py capture resume --force
```
（其餘四路無 B軌、免捕；與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 同屬「B軌輸出變更須重捕」一類。）

---

## 回退與備案

```bash
# 單獨回退本 hotfix（保留 RESUME-P3 C1-C6）
git revert <HEADING-HOTFIX-1-hash>

# 若引發更大 Regression、退回 hotfix 前最後穩定點（RESUME-P3 C6 = a1d5d7f）
git reset --hard a1d5d7f
```

---

## 附錄：受影響檔案與包裹標記

| 檔案 | 改動 | 標記 |
|---|---|---|
| `pipelines/resume_pipeline.py` | `_restore_sections_markdown`（depth=0 起算）+ `_restore_one_section`（簽名 +depth、`level=min(2+depth,6)`、children depth+1）| `# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_heading_level_by_recursion_depth` | 同上包裹 |
| `.bak` 備份 | `archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_resume_pipeline.py.bak`（+ 測試檔 .bak）| 改前備份鐵律 |

> **Run 階段交付清單（baron 後續觸發）**：改 2 檔 + 2 `.bak` + 追加 1 測試 + 全套件 pytest + SOP grep + hotfix.md/執行報告歸檔 hotfixes/ + TODO ✅ + msg 寫 `/tmp`，baron 手動 commit。
