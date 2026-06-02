# GOLDEN-BASELINE 黃金基準存盤與退化比對 — Tasks

> 本文件為 GOLDEN-BASELINE 的 **OP-N 執行階段拆分清單**（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md` 計畫產出，含 3 個 OP 執行階段。
> **本任務不拆分 Git Commit**，改以「OP-N 執行階段」推進；commit / push 由 baron 手動執行（CLAUDE.md §1.3）。
> **收官歸檔鐵律**：OP-1／OP-2 執行期所有 plan／tasks／執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 OP-3（Checkout）一次性 `mv` + `git add` 歸檔**（WORKFLOW_SOP §3 baton 暫存鐵律 + 收官歸檔鐵律）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`（本檔）＋`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md`（已歸檔） |
| **修改檔案** | 2 個 | `.claude-logs/TODO.md` / `.claude-logs/prompts/INDEX.md` |
| **狀態更新** | 2 個 | `TODO.md` GOLDEN-BASELINE 條目 OP 順序更正（🟡 WIP） / `prompts/INDEX.md` 登記修正提示詞 |
| **執行階段** | 3 個 | OP-1（五路黃金基準物理存盤）→ OP-2（自動化 Regression Diff 比對腳本）→ OP-3（Checkout / 收官歸檔） |
| **執行報告** | 3 個 | `baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md` / `OP-2_執行.md` / `OP-3_執行.md`（各 OP 執行時產出、套用 template_execution 模板、暫存 baton/） |
| **baton 歸檔** | 1 次 | **僅 OP-3 收官**一次性 `mv` 計畫＋tasks＋三份 OP 執行報告至正式目錄 + `git add` |

> **OP 產出物（執行期落地、非本 tasks 階段產出）**：`tools/golden_baseline.py`（capture + diff 雙子命令）／`tests/golden_baseline/fixtures/*.pdf`（五路固定資料集）／`tests/golden_baseline/golden/<doc_type>/{D1,D2,D3,manifest.json}`（凍結黃金快照）／`report/golden_baseline/<doc_type>_<ts>/{diff_report.json,diff_report.md}`（Diff 報告）／`tests/test_golden_baseline.py`（比對引擎單元測試）。

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 大改版以「影子並行縱向五路絞殺」漸進落地，每打通一路必須證明「排版 0% 退化、譯文 0% Regression、RAG 召回不劣化」才准 Flip；但目前**無任何客觀基準**——舊單體產物未凍結、無 Diff 工具、無量化判準，「0% 退化」無從驗收（plan v2 §1）。
- **解法**：原子化拆為 3 個 OP 執行階段——**OP-1** 建立 `golden_baseline.py capture` 子命令並對五路代表性文檔在舊單體跑完整流程、凍結三維度黃金快照 + SHA-256 manifest；**OP-2** 建立 `golden_baseline.py diff` 子命令與比對引擎（D1 結構樹／D2 譯文相似度／D3 RAG Jaccard）+ 紅綠燈裁決 + 雙格式報告 + `tests/test_golden_baseline.py`；**OP-3** Checkout 收官，一次性歸檔 plan / tasks / 三份 OP 執行報告並 `git add`。
- **影響範圍**：100% 新增工具與測試基建 + 文件治理；**零業務代碼改動**（`pipeline_core.py` / `rag_retriever.py` / `web_server.py` / `models.py` 全程只讀，見 §7）。
- **不可動清單**：見 §7。
- **時序修正**：原 v1 將 Checkout 誤置 OP-1（導致 OP-2/OP-3 未產出之報告無從搬移、違反 baton 暫存鐵律），本版更正——Checkout 移至最尾端 OP-3，OP-1/OP-2 執行期一律暫存 baton/。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `tools/golden_baseline.py` | 不存在 | 須新建 capture（OP-1）+ diff（OP-2）雙子命令 |
| `tests/golden_baseline/` | 不存在 | 須新建 fixtures（五路 PDF）+ golden（凍結三維度產物）+ manifest（OP-1） |
| `report/golden_baseline/` | 不存在 | Diff 報告輸出目錄（OP-2 執行時動態產生） |
| `tests/test_golden_baseline.py` | 不存在 | 比對引擎單元測試（OP-2） |
| `pipeline_core.py` | 既有 11-stage，`_get_stage_output_path L191-209` 產物路徑 | 純讀其產物（`final_*_zh/en.md` L197-198 / `rag_tree.json` L203 / `vectors/` L204），零改動 |
| `rag_retriever.py` | `retrieve_with_context L92` 單篇召回入口 | D3 召回基準純呼叫，零改動 |
| `.claude-logs/baton/..._plan_v2.md`／`..._tasks.md`／`OP-*_執行.md` | 全程暫存 baton/ | OP-3 收官才一次性 `mv` 歸檔 + `git add` |

---

## §3 觀察問題

### 問題 #1：無客觀退化基準，「0% 退化才 Flip」無法驗收
- **證據**：plan v2 §1 TL;DR「目前無任何客觀基準可比對——舊單體產物未凍結存盤、無 Diff 工具、無量化判準」。
- **影響**：五路絞殺每路打通後無從證明排版/譯文/RAG 是否退化，Flip 決策失去物理依據。

### 問題 #2：LLM 翻譯與 embedding 具非確定性，純字串比對不可行
- **證據**：plan v2 §7 Q2「LLM 翻譯與 embedding 具非確定性，純字串 100% 相等不切實際」。
- **影響**：Diff 引擎須採相似度/重疊度門檻（D2 ≥0.95 / D3 ≥0.90）+ 正規化（剝 `_shadow`／` (測試)`／時間戳），否則偽陽性氾濫。

### 問題 #3：黃金快照若被竄改，比對結果失真
- **證據**：plan v2 §2 U2「每份黃金快照附 SHA-256 checksum 清單（manifest.json），比對時驗證未被竄改」。
- **影響**：須在 diff 流程前置 checksum 校驗閘，不符即拒絕比對（plan v2 §2.5.2 步驟 2）。

### 問題 #4（v1 時序悖論）：Checkout 誤置首階段，違反 baton 暫存鐵律
- **證據**：WORKFLOW_SOP §3「baton/ 暫存鐵律：Run 階段產出的執行報告與 plan，嚴禁在 Run 階段 mv 移動或 git add」+「收官歸檔鐵律：baton/ 下所有暫存文件，必須且僅能在最後 Check 階段一次性 mv + git add 歸檔」。
- **影響**：v1 將歸檔放 OP-1，OP-2/OP-3 尚未產出的執行報告無從被搬移、且提早入版控破壞 Traceability；本版更正將 Checkout 移至最尾端 OP-3。

---

## §4 設計方案

> 逐 OP 列出落地設計概要；完整規格見 plan v2 §2（U1–U7）/ §6（驗證計畫）。

### §4.1 OP-1 — 五路黃金基準物理存盤（capture 子命令）
建立 `golden_baseline.py capture` 子命令，依 plan v2 §2.5.1 流程：載入五路固定資料集 PDF → 呼叫舊單體 A 軌 `PipelineCore`（`shadow=False`）跑完整 11-stage → 收集三維度產物（D1 雙語 md / D2 rag_tree.json / D3 fixed query set × `retrieve_with_context` top-k chunk+score）→ 計算 SHA-256 寫 `manifest.json` → 防覆寫閘（已存在且無 `--force` 則 ABORT）→ 凍結寫入 `tests/golden_baseline/golden/<doc_type>/`。五路 fixtures PDF 與 fixed query set（每路 3–5 條）一併入版控。執行報告暫存 baton/。

### §4.2 OP-2 — 自動化 Regression Diff 比對腳本（質量防線）
建立 `golden_baseline.py diff` 子命令 + 比對引擎，依 plan v2 §2.5.2 流程：黃金快照存在性檢查 → manifest checksum 校驗 → 跑候選產物 → 正規化（剝 `_shadow`／` (測試)`／時間戳）→ 三維度 Diff（D1 結構樹 / D2 譯文相似度門檻 0.95 / D3 RAG Jaccard 門檻 0.90）→ 三維度彙總紅綠燈裁決（PASS / FAIL / IMPROVEMENT_PENDING_REVIEW）→ 輸出 `diff_report.json` + `diff_report.md` 至 `report/golden_baseline/<doc_type>_<ts>/`。同步建立 `tests/test_golden_baseline.py` 驗證三維度比對、正規化等價、判斷分支。執行報告暫存 baton/。

### §4.3 OP-3 — Checkout / 收官歸檔（一次性 Traceability 交接）
**唯一**的歸檔階段。一次性將 baton/ 暫存的 plan / tasks / 三份 OP 執行報告 `mv` 至正式目錄並 `git add`：plan → `plans/`（強制保留 `_v2`）、tasks → `tasks/`、OP-1/OP-2/OP-3 執行報告 → `executions/`。同步將 TODO.md 三項 OP 狀態更新為 ✅。OP-3 自身執行報告先產於 baton/、於本階段最後一併 `mv`。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| OP-1 capture 為「跑舊單體」而誤動 `pipeline_core.py` 主鏈 | 🔴 高 | 嚴格只 `shadow=False` 呼叫既有 `process`，零改其本體與產物路徑（§7） |
| D2/D3 門檻數值（0.95/0.90）未經實測、產生偽陽性 | 🟡 中 | 先設保守起始門檻，OP-2 後跑「自比對歸零」實測 variance 校準（plan v2 §6.2 步驟 2、§7 Q2，最終數值待 baron 核准） |
| golden 快照與 fixtures PDF 體積大、入 Git 版控膨脹 | 🟡 中 | plan v2 §7 Q1 已列為 Open Question；book 取節選（2-3 章邊界）；是否改 Git LFS 待 baron 拍板（OP-1 執行前確認） |
| baton 暫存文件提早 `mv`/`git add`（重蹈 v1 覆轍） | 🔴 高 | OP-1/OP-2 執行報告嚴禁移動，**僅 OP-3 收官**一次性歸檔（§0.5 + §4.3 + WORKFLOW_SOP §3） |
| 新建 `tools/golden_baseline.py` 的 logging 未遵守 SOP | 🟢 低 | 執行 OP-1/OP-2 時 Python logging 依 `sop/2026-05-23_logging_SOP_手冊.md`（`logger.error` 須 `exc_info=True`） |

---

## §6 測試計畫

### §6.1 OP-1 驗收

```bash
# 五路黃金快照三維度產物 + manifest 齊全
ls -la tests/golden_baseline/fixtures/          # 五路代表性 PDF
for d in academic book slides resume litedoc; do
  echo "== $d =="; ls tests/golden_baseline/golden/$d/   # D1/D2/D3 + manifest.json
done
# capture 防覆寫閘：無 --force 重跑須 ABORT
python tools/golden_baseline.py capture academic 2>&1 | grep -iE "exist|abort|防覆寫"
# baton 暫存鐵律：OP-1 執行報告仍在 baton/、未入版控
ls .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md
git status -s .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md   # 應無輸出（gitignored）
```

### §6.2 OP-2 驗收

```bash
# 比對引擎單元測試全綠
pytest tests/test_golden_baseline.py -v
# 自比對歸零（工具無偽陽性）：舊系統對同檔 diff 三維度應 PASS
python tools/golden_baseline.py diff academic 2>&1 | grep -iE "PASS|verdict"
# 報告雙格式產出
ls report/golden_baseline/*/ | grep -E "diff_report\.(json|md)"
# 既有測試零迴歸
pytest tests/ -q
```

### §6.3 OP-3 驗收

```bash
# plan / tasks / 三份報告皆已自 baton/ 歸檔至正式目錄
ls -la .claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md
ls -la .claude-logs/tasks/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md
ls .claude-logs/executions/2026-06-02_GOLDEN-BASELINE_OP-{1,2,3}_執行.md
# baton/ 對應暫存已清空
ls .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_* 2>&1 | grep -q "No such file" && echo "baton 已清空（合規）"
# git 已追蹤正式檔
git status -s .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本任務全程嚴禁任何改動：**

- [ ] **`pipeline_core.py` 舊單體 11-stage 與 `_get_stage_output_path`（L191-209）** — capture 只**讀取**其產物，嚴禁為存盤改動主鏈或產物路徑。
- [ ] **`rag_retriever.py` `retrieve_with_context`（L92）簽名與檢索演算法** — D3 召回只呼叫既有入口取結果，不改檢索邏輯。
- [ ] **既有 `delete_paper` / `list_papers` / `get_paper` API** — 影子候選清理沿用既有 API，零改動。
- [ ] **`models.py` 既有 Schema** — 本任務資料全落檔案系統（`tests/golden_baseline/` 與 `report/`），不新增任何 DB 表/欄位。
- [ ] **`web_server.py` 業務代碼** — 不碰；本任務為離線工具旁路，不注入任何 runtime 主鏈 hook。
- [ ] **主 repo 目錄（worktree 父目錄）** — 嚴禁讀寫；唯一合法工作目錄 `.claude/worktrees/hopeful-yalow-902c50/`。
- [ ] **固定資料集 `tests/golden_baseline/fixtures/*.pdf` 與已凍結 `golden/`** — OP-1 凍結後嚴禁無 baron 核准變更（`--force`），否則跨路次基準失準。
- [ ] **baton/ 暫存文件（OP-1/OP-2 期間）** — 嚴禁提早 `mv` / `git add`，僅 OP-3 收官一次性歸檔。

---

## §8 推薦執行階段拆分

### OP-1 — 五路黃金基準物理存盤（建立 Golden Baseline）

| 維度 | 內容 |
|---|---|
| **執行範圍** | 新建 `tools/golden_baseline.py`（`capture` 子命令）＋ `tests/golden_baseline/fixtures/<doc_type>.pdf`（五路）＋ `tests/golden_baseline/golden/<doc_type>/{D1 雙語 md, D2 rag_tree.json, D3 fixed_queries+召回結果, manifest.json}` |
| **安全性** | 🟢 高 — 僅涉及基準存檔與 capture 腳本編寫，舊單體只讀調用、業務代碼零改動 |
| **可逆性** | 🟢 高 — 刪除 `tools/golden_baseline.py` 與 `tests/golden_baseline/` 即完全還原 |
| **驗收 grep/執行 條件** | 見 §6.1（五路 golden 三維度 + manifest 齊全、capture 防覆寫閘 ABORT、OP-1 報告仍暫存 baton/） |
| **依賴關係** | 無（首階段） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md`（套用 template_execution 模板、**暫存 baton/、不移動**） |
| **具體實作細節** | 1. **挑五路代表性 PDF**（plan v2 §2 U1）：academic 學術論文（含 Section/References/公式）、book 書籍**節選 2-3 章**（含 Sliding Window 邊界，§7 Q5）、slides 簡報（含圖片 Caption）、resume 履歷（含技能詞 Go/C++/AI）、litedoc 短文（news/web，含 15k 閥門前後）；置入 `tests/golden_baseline/fixtures/`。2. **實作 `capture` 子命令**依 plan v2 §2.5.1：① 載入 fixtures PDF（缺檔 FAIL FAST）；② 呼叫舊單體 `PipelineCore(...).process(...)`（`shadow=False`，**只讀調用、不改本體**）跑完整 11-stage（回傳 FAILED 即終止並記 stage）；③ 收 D1（讀 `final_*_zh.md`/`final_*_en.md`）、D2（讀 `final_*_rag_tree.json`）、D3（對 fixed query set 逐條呼叫 `rag_retriever.retrieve_with_context` 記 top-k chunk+score；任一維度缺漏 FAIL）；④ 計算各檔 SHA-256 寫 `manifest.json`；⑤ **防覆寫閘**：該 doc_type golden 已存在且無 `--force` → ABORT。3. **fixed query set**（每路 3–5 條）以 JSON/py 常數入版控，凍結。4. 執行 `capture --all` 物理存盤五路。5. logging 依 logging SOP（`exc_info=True`）。6. 產 `OP-1_執行.md` 貼五路 `ls` + manifest 內容證明，**留 baton/ 不移動**。 |

### OP-2 — 自動化 Regression Diff 比對腳本開發（質量防線）

| 維度 | 內容 |
|---|---|
| **執行範圍** | `tools/golden_baseline.py`（新增 `diff` 子命令 + 三維度比對引擎 + 正規化 + 紅綠燈裁決）＋ `tests/test_golden_baseline.py`（比對引擎單元測試）＋ `report/golden_baseline/<doc_type>_<ts>/{diff_report.json, diff_report.md}`（執行時動態產出） |
| **安全性** | 🟢 高 — 僅涉及 Diff 比對腳本與單元測試編寫，業務代碼零改動 |
| **可逆性** | 🟢 高 — 刪除 `diff` 子命令、`tests/test_golden_baseline.py` 與 `report/golden_baseline/` 即還原 |
| **驗收 grep/執行 條件** | 見 §6.2（`pytest tests/test_golden_baseline.py -v` 全綠、自比對歸零 PASS、報告雙格式產出、既有 `pytest tests/` 零迴歸） |
| **依賴關係** | OP-1（黃金快照已存盤） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md`（套用 template_execution 模板、**暫存 baton/、不移動**） |
| **具體實作細節** | 1. **實作 `diff` 子命令**依 plan v2 §2.5.2：① 黃金快照存在性檢查（無 → FAIL FAST「請先 capture」）；② manifest checksum 校驗（不符 → FAIL「基準被竄改、拒比對」）；③ 取候選產物（首版可對**舊系統自身**再跑驗證工具歸零；新核心 `shadow=True` 候選待 PIPE-CORE 落地後接入）；④ 正規化候選與黃金（剝 `_shadow`／` (測試)`／時間戳雜訊）。2. **三維度比對引擎**：D1 排版結構樹（heading 階層／table 行列數／list 項數／image alt；節點增刪或 alt 不符 = 退化）；D2 譯文逐 Section 相似度（token 級 ratio，< **0.95** 或 Section 數不符 = 退化）；D3 RAG 召回 top-k chunk Jaccard 重疊度（< **0.90** 或命中縮減 = 退化）。3. **紅綠燈裁決**（plan v2 §2.5.2 步驟 6）：三維度全 PASS → 綠燈 `verdict=PASS`；任一 FAIL 且屬已知改善 → `IMPROVEMENT_PENDING_REVIEW`（待 baron）；任一 FAIL 且為退化 → 紅燈 `verdict=FAIL`。4. **報告雙格式**：`diff_report.json`（機器可讀）+ `diff_report.md`（人類可讀），輸出 `report/golden_baseline/<doc_type>_<ts>/`。5. **`tests/test_golden_baseline.py`**：D1 結構樹（相同→0、heading/table/alt 差→退化）、D2 相似度（相同→1.0、Section 不符/低相似→FAIL）、D3 Jaccard（相同→1.0、命中縮減→FAIL）、正規化等價（含 `_shadow`/` (測試)`/時間戳→正規化後等價）、判斷分支（缺基準 fail fast / checksum 拒比 / 紅綠燈彙總 / improvement 豁免）。6. **門檻校準**：跑「自比對歸零」實測 variance，門檻數值最終待 baron 核准（plan v2 §7 Q2）。7. 產 `OP-2_執行.md` 貼 pytest 輸出 + 自比對 verdict + 報告 `ls`，**留 baton/ 不移動**。 |

### OP-3 — Checkout / 收官歸檔（一次性 Traceability 交接）

| 維度 | 內容 |
|---|---|
| **執行範圍** | `mv` baton/ 暫存 plan → `plans/`（保留 `_v2`）、tasks → `tasks/`、OP-1/OP-2/OP-3 執行報告 → `executions/`；對全部歸檔正式檔 `git add`；同步 TODO.md 三項 OP 狀態 → ✅ |
| **安全性** | 🟢 高 — 純文件搬移與版控追蹤，業務代碼零改動、零 runtime 影響 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ 即完全還原 |
| **驗收 grep/執行 條件** | 見 §6.3（plans/tasks/executions 三目錄歸檔齊全、baton/ 已清空、`git status -s` 已追蹤） |
| **依賴關係** | OP-1 + OP-2（兩階段執行報告皆已產於 baton/） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-3_執行.md`（套用 template_execution 模板），於本階段最後一併 `mv` 至 `executions/` |
| **具體實作細節** | 1. 先產 `OP-3_執行.md`（暫存 baton/），記錄收官歸檔清單與 diff stat。2. **一次性歸檔搬移**（WORKFLOW_SOP §3 收官歸檔鐵律）：<br>`mv .claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md .claude-logs/plans/`（**保留 `_v2`**）<br>`mv .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md .claude-logs/tasks/`<br>`mv .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-3_執行.md .claude-logs/executions/`。3. `git add` 上述全部正式檔（plans/tasks/executions）。4. **更新 TODO.md**：GOLDEN-BASELINE 三項 OP `⬜/🟡` → `✅`，依框架 §2.5 將任務移入頂部 ✅ 已完成表格（落地 Hash 待 baron 回填）。5. 驗收 §6.3 grep（baton/ 清空 + 正式目錄齊全 + git 已追蹤）。6. **嚴禁** `git commit` / `git push`（CLAUDE.md §1.3，baron 手動）。 |

---

## §9 Open Questions

無。（plan v2 §7 之 5 項 Open Questions——存放位置/Git LFS、D2/D3 門檻數值、改善判定權、多篇召回、book 節選——皆已於計畫審核中標註推薦答案，由 baron 於各 OP 執行前最終拍板；本 tasks 階段不另增規劃層問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GOLDEN-BASELINE 任務的 OP-N 執行階段拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 OP 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` 三份 OP 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 OP 混合不同階段產物；嚴禁自動 `git commit` / `git push`；OP-1/OP-2 執行報告嚴禁移動、僅 OP-3 收官一次性歸檔 |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；三維度存盤/比對規格唯一源在 plan v2 §2；四份合約唯一源在 PIPE-SPEC；工作流規格一律引用 WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-02)：**Checkout 時序修正**——baron 指出 v1 將收官歸檔誤置 OP-1，導致 OP-2/OP-3 未產出之執行報告無從搬移、且違反 WORKFLOW_SOP §3 baton 暫存鐵律與收官歸檔鐵律。重編三階段：OP-1 五路黃金基準物理存盤（capture）／OP-2 自動化 Regression Diff 比對腳本（diff + tests）／OP-3 Checkout 收官（一次性 `mv` + `git add` 歸檔 plan/tasks/三報告 + TODO ✅）；OP-1/OP-2 執行期一律暫存 baton/ 不移動。同步更新 §0.5 成果盤點、§3 新增問題 #4、§5 新增「提早歸檔」風險、§6 三 OP 驗收、§7 新增 baton 暫存不可動條目。
- v1 (2026-06-02)：初版拆分完成，依 plan v2 §2（U1–U7）/ §6 拆為 3 個 OP（OP-1 Checkout / OP-2 存盤 / OP-3 Diff 腳本）；不拆 Git commit、不給 commit 建議。**（時序錯誤，已由 v2 廢除）**
