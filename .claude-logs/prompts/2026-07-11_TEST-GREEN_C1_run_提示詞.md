# 2026-07-11 — TEST-GREEN C1 提示詞

> **收到時間**：2026-07-11 21:32（UTC+8）
> **任務代號**：TEST-GREEN C1
> **觸發 commit**：TEST-GREEN C1
> **相關產出檔案**：.claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md
> **觸發情境**：baron 確認 TEST-GREEN tasks 規格後，下達 C1（CSS Surface Repoint）階段執行指令——為 6 個測試檔新增 CSS 分包聯集源、repoint 15 個 stale 失敗斷言，目標全套件 705 passed / 0 failed。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-11 21:32 |
| **任務代號** | TEST-GREEN C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md |
| **觸發情境** | baron 確認 tasks 規格，下達 C1 階段執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-11_TEST-GREEN_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-11_TEST-GREEN_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：TEST-GREEN
- **當前 Commit 代號**：C1
- **工作流類別**：FE-Refactor
- **Tasks 路徑**：.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md  # 全局策略依據
.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md  # 本次執行的依據 tasks
.claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md  # 效能渲染 SOP 手冊
tests/test_bug_b2_paper_header_meta.py                 # 修改目標 1
tests/test_bug_f1_frontend_micro_fix.py                # 修改目標 2
tests/test_bug_f3_modal_input_css.py                   # 修改目標 3
tests/test_bug_f5_p2_inconsistencies.py                # 修改目標 4
tests/test_phase2_p2_3_hashtag_token_ui.py             # 修改目標 5
tests/test_rag14_c1_css_and_filter.py                  # 修改目標 6

```

### 🏢 修改邊界與限制（⚠️ 測試防禦邊界）

1. **修改權限**：本任務僅允許修改上述 `tests/` 目錄下的 6 個測試檔案。**嚴禁修改任何業務代碼與網頁前端資產（`static/**`、FastAPI `web_server.py` 等）。**
2. **斷言 Pattern 零改寫**：嚴禁改動任何測試斷言中的 `re.compile` pattern 本體、正/負向語意、期望值或數量門檻。僅允許修改 `pat.search(...)` 等斷言對象以指向新聯集源。
3. **通過測試零回歸**：6 個檔案中現行已通過的 20 個測試（含逐行掃描、JS 與 markdown 等），**其搜尋目標必須維持讀取原 `STATIC_HTML` / `_html()` 不變**，防止非預期的測試狀態受損。
4. **版本控制限制（⚠️ 關鍵限制）**：
   - 本次 C1 Commit 納入 Git 追蹤與 `git add` 的檔案僅有修改後的 6 個測試檔案、以及對應的 6 份 `.bak` 備份檔。
   - 所有暫存於 `baton/` 的過程文件（如 `plan.md`、`tasks.md`、以及本階段產出的執行報告 `_執行.md` 等）在當前階段**嚴禁加入 Git 追蹤**（嚴禁對其使用 `git add`），亦**不得**出現在執行報告 §8 的 `git add` 指令清單中。

### 🛠️ 執行命令與測試源改讀

請依 `tasks.md §8 C1 — CSS Surface Repoint` 具體實作細節進行：
1. **備份**：修改前備份 6 份相關測試檔案：
   ```bash
   cp tests/test_bug_b2_paper_header_meta.py archive/2026-07-11_TEST-GREEN_C1_test_bug_b2_paper_header_meta.py.bak
   cp tests/test_bug_f1_frontend_micro_fix.py archive/2026-07-11_TEST-GREEN_C1_test_bug_f1_frontend_micro_fix.py.bak
   cp tests/test_bug_f3_modal_input_css.py archive/2026-07-11_TEST-GREEN_C1_test_bug_f3_modal_input_css.py.bak
   cp tests/test_bug_f5_p2_inconsistencies.py archive/2026-07-11_TEST-GREEN_C1_test_bug_f5_p2_inconsistencies.py.bak
   cp tests/test_phase2_p2_3_hashtag_token_ui.py archive/2026-07-11_TEST-GREEN_C1_test_phase2_p2_3_hashtag_token_ui.py.bak
   cp tests/test_rag14_c1_css_and_filter.py archive/2026-07-11_TEST-GREEN_C1_test_rag14_c1_css_and_filter.py.bak
   ```
2. **建置 CSS 分包聯集源**：
   - 對於一般測試檔（b2 / f1 / f3 / f5 / phase2），在既有 `STATIC_HTML` 定義後，補上獨立的聯集源 `CSS_SURFACE`：
     ```python
     _CSS_DIR = ROOT / 'static' / 'css'
     CSS_SURFACE = STATIC_HTML + '\n' + '\n'.join(
         f.read_text(encoding='utf-8') for f in sorted(_CSS_DIR.glob('*.css'))
     )
     ```
   - 對於 `rag14` 測試檔，新增 `_css_surface()` 並列 helper：
     ```python
     def _css_surface() -> str:
         css_dir = STATIC_HTML.parent / 'css'
         css = '\n'.join(f.read_text(encoding='utf-8') for f in sorted(css_dir.glob('*.css')))
         return _html() + '\n' + css
     ```
3. **指向聯集源**：
   - 依照 tasks.md §4.1 的「逐檔 repoint 清單」，將 15 個 stale 的失敗斷言搜尋目標由原 `STATIC_HTML` / `_html()` 改讀為新聯集源 `CSS_SURFACE` / `_css_surface()`。
4. **測試與驗證**：執行 tasks.md 內的 §6.1 驗收指令，確保 6 檔重跑共 35 passed 全綠，且全套件跑出 705 passed、3 skipped 且 0 failed 的最終綠燈。核查 `git diff` 確保無任何斷言 Pattern 的文句遭到篡改。

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 Commit 標記為 ✅ 已完成：
     `- ✅ C1 — CSS Surface Repoint（測試源改讀 CSS 分包聯集）`
   - 將下一個 Commit 標記為 🟡 WIP：
     `- 🟡 WIP: checkout — 成果收官歸檔（成果歸檔與移出暫存）`

2. **歷史已提交 Hash 掃描與自愈補填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，將 `TODO.md` 中所有先前已完成任務但仍為 `待 baron 回填` 的佔位符替換為讀取出的真實 Git Commit Hash，保持歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md`（暫存 baton/，不入本階段 git 版控）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

執行報告必須包含：
- 頂部元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / hash 留空 / 狀態）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含備份路徑，注意：`baton/` 下的文件不在此列入備份或 `git add` 說明）
- §4 修改說明（詳細說明聯集源計算方式、15 個失敗斷言 repoint 行號與 f5/rag14 負向斷言安全核查說明）
- §5 測試與驗收結果（貼上實際驗收測試的終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含正式修改的 6 個測試檔與 .bak 備份，嚴禁將 baton/ 暫存檔加入）
git add tests/test_bug_b2_paper_header_meta.py
git add tests/test_bug_f1_frontend_micro_fix.py
git add tests/test_bug_f3_modal_input_css.py
git add tests/test_bug_f5_p2_inconsistencies.py
git add tests/test_phase2_p2_3_hashtag_token_ui.py
git add tests/test_rag14_c1_css_and_filter.py
git add archive/2026-07-11_TEST-GREEN_C1_test_bug_b2_paper_header_meta.py.bak
git add archive/2026-07-11_TEST-GREEN_C1_test_bug_f1_frontend_micro_fix.py.bak
git add archive/2026-07-11_TEST-GREEN_C1_test_bug_f3_modal_input_css.py.bak
git add archive/2026-07-11_TEST-GREEN_C1_test_bug_f5_p2_inconsistencies.py.bak
git add archive/2026-07-11_TEST-GREEN_C1_test_phase2_p2_3_hashtag_token_ui.py.bak
git add archive/2026-07-11_TEST-GREEN_C1_test_rag14_c1_css_and_filter.py.bak

# 3. commit message draft（已寫入 /tmp/TEST-GREEN_C1_msg.txt）
cat > /tmp/TEST-GREEN_C1_msg.txt << 'EOF'
FE-Refactor: TEST-GREEN C1 — CSS Surface Repoint

為 6 個測試檔案新增 CSS 聯集源，並將 15 個 stale 的 CSS 存在性斷言改讀此聯集
以修復測試紅燈。現行通過的 20 個測試續讀原 index.html 源以確保零回歸。
EOF

# 4. baron 手動執行
git commit -F /tmp/TEST-GREEN_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-11_TEST-GREEN_C1_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ 完成（C1 全數落地、待 baron commit）
- pytest baseline → final：六檔 `15 failed / 20 passed` → `35 passed`；全套件 `690 passed / 15 failed / 3 skipped` → **`705 passed / 3 skipped / 0 failed`**
- 改動檔案：6 個測試檔（+6 `.bak` 落 `.claude-logs/archive/`、deviation：根層 `archive/` 不存在、循既有慣例）+ TODO.md / INDEX.md 狀態更新
- 斷言 pattern 零改寫（diff 實證：零 `re.compile` 行增刪）；執行報告暫存 `baton/2026-07-11_TEST-GREEN_C1_執行.md`
- 未 commit / push（依 §1.3 由 baron 手動執行；msg 草稿 `/tmp/TEST-GREEN_C1_msg.txt`）

## 後續引用

- （暫無）
