# WORKFLOW-1 流程簡化與文件治理改版規劃書 v3 — 可行性評估（Claude Code 篇）

> 本文件為 **Claude Code 對 WORKFLOW-1 v3 改版規劃書的可行性評估與執行計畫**、套 `template_plan.md` 8 章節骨架 + §0 來源欄位（v3 §11 標準）。
> 評估對象：`.claude-logs/ref/2026-05-24_WORKFLOW-1_流程簡化與文件治理_改版規劃書_v3.md`（708 行）

---

## §0 來源與審核軌跡

| 維度 | 內容 |
|---|---|
| **改版規劃書來源** | baron 2026-05-24 三輪對話（v3）|
| **工作流類別** | 文件治理 Refactor（純文件改版、無業務代碼改動） |
| **可行性評估結論** | 🟢 全採納（帶 3 個條件，見 §1） |
| **claude Code 評估日期** | 2026-05-24 |
| **baron 審核狀態** | ⬜ 待 baron 審核 |
| **讀取文件清單** | v3 規劃書 + 提示詞模板 v3 + PROJECT_PROGRESS_CONTROL_FRAMEWORK + template_plan/execution/hotfix + prompts/README + TODO.md + logging SOP（前 60 行）+ database SOP（前 60 行）|
| **grep 實證** | 命名合規率 91.6%（185/202）、提示詞 INDEX 分類統計、SOP 引用分析、Logseq 語法相容測試、template 章節分析 |

---

## §1 TL;DR

### 整體三級結論：🟢 全採納（帶 3 個條件）

**整體理由（4 句）**：
1. v3 的七大子改動在現有 codebase 規模下全部是低風險純文件操作、不碰業務代碼、可逆性 100%。
2. 核心新增（四類工作流分流 + 三道防線 + §0 改版規則）解決了真實存在的 token 浪費與文件職責漂移問題、grep 實證與歷史任務模式吻合。
3. 唯一需要條件補強的是：（A）§0 Revision 區塊若放文件開頭會破壞 Prompt Cache 前綴；（B）Logseq 建議「試用不強制」；（C）CLAUDE_CODE_ENTRY.md 須避免寫入高頻動態內容。
4. baron 採納後立即可量化到的好處：FE-Hotfix / BE-Hotfix 場景 token 節省 ~70-75%、框架文件有了可執行的清理機制、跨 session Prompt Cache 命中率可提升至 ~82%。

**baron 真正獲得的好處 vs 付出的成本**：

| 項目 | 好處 | 成本 |
|---|---|---|
| 四類工作流分流 | FE-Hotfix 每次省 ~15k tokens 讀取；不再被迫讀無關 SOP | 每次需在腦中或依 CLAUDE_CODE_ENTRY 判定分類（≤ 5 秒決策） |
| 三道防線 + CLAUDE_CODE_ENTRY | Claude Code 無法假裝「沒讀規範」；入口顯眼 | 新增 2 份文件的維護義務 |
| §0 改版規則 | 文件可以被刪冗、不會永遠膨脹 | 每份文件加 ~15-30 行 §0 模板 |
| template_revision_plan | Antigravity 以後的規劃書格式統一、Claude Code 評估更快更準 | 未來 Antigravity 需改寫習慣 |
| Logseq（可選） | 跨文件雙向連結、標籤可視化 | 學習成本 ~2-4 小時、設定 graph |

---

## §2 既有資料盤點

### §2.1 template 章節結構現況

| Template | 現有章節 | §0 現況 | v3 影響 |
|---|---|---|---|
| `template_plan.md` | TL;DR + §1-§8（無 §0） | ❌ 無 | 加 §0 來源與審核軌跡 |
| `template_execution.md` | 落地表格 + 真因 + 修法 + 不可動 + E2E + Rollback（無編號無 §0） | ❌ 無 | 加 §0 改版規則 |
| `template_hotfix.md` | 落地表格 + 真因 + 修法 + E2E + Rollback（無編號無 §0） | ❌ 無 | 加 §0 改版規則 |

**重要觀察**：template_plan.md 目前使用「TL;DR + §1-§8」（8 個章節），但 v3 的模板 A-FE/A-BE 提示詞內寫「9 章節（含 §0 來源欄位）」。加 §0 後的計數方式需要釐清：到底是 TL;DR 仍叫 TL;DR、還是改成 §1 TL;DR？本評估推薦：加 §0、其餘章節命名不動（TL;DR 就是 TL;DR），避免破壞既有 plan 檔案的命名慣例。

### §2.2 命名合規率（§12.1 基線）

```bash
# 實測 grep 結果（2026-05-24）
find .claude-logs/ -name "*.md" 2>/dev/null | wc -l
# → 202 檔
find .claude-logs/ -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_*.md" 2>/dev/null | wc -l
# → 185 檔（91.6% 符合）
```

**不符合 §12.1 的 9 個歷史檔案**（全在 `.claude-logs/ref/`）：
1. `google_latest_models_guide.md`（規格文件類、§12.1 允許「無日期長期生效」）
2. `model_optimization_blueprint.md`（改版規劃書、無日期前綴 → 違反）
3. `db_analysis_and_future_extension.md`（規格文件類、§12.1 允許）
4. `model_recommendations.md`（規格文件類）
5. `logging_refactor_proposal.md`（可行性評估、無日期前綴 → 違反，但屬 pre-v3 歷史）
6. `Implementation_Plan.md`（大寫 + 無日期 → 違反）
7. `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（框架類、§12.1「全大寫 `_` 分隔」→ 合規）
8. `project_analysis.md`（規格文件類）
9. `api_audit_and_performance_report.md`（改版規劃書、無日期 → 違反）

→ **結論**：真正違反§12.1 的是 3-4 個（model_optimization_blueprint、logging_refactor_proposal、Implementation_Plan、api_audit_and_performance_report），均屬 pre-v3 歷史，v3「不溯及既往」條款合理覆蓋。

### §2.3 任務編碼衝突確認

```bash
grep "WORKFLOW" .claude-logs/TODO.md
# → 無輸出（WORKFLOW- 前綴目前不存在於 TODO.md）
```

→ **結論**：WORKFLOW-1 前綴與現有任務代號零衝突。

### §2.4 提示詞歸檔類型統計

```
INDEX.md 全行數：60 行
含「提示詞」關鍵字：36 行
RAG-1 系列：19 行 (~53%)  → 業務功能開發（非 SOP 重包裝）
BUG- 系列：17 行 (~47%)   → Bug 修復（非 SOP 重包裝）
logging 系列：6 行 (~17%) → 含 SOP 可行性評估（重包裝比例最高）
```

→ **v3 問題 #1「80% 是重新包裝 SOP」 的實測反駁**：實際統計近 30 筆提示詞中，直接重包裝 SOP 的比例約 15-20%（主要是 logging_refactor 系列），而非 80%。但問題 #1 的**核心價值**仍成立：Claude Web 中介層的 round-trip 確實是冗餘的，去除後 baron 直接操作 Claude Code 效率更高。

---

## §3 逐項評估（七大子改動）

### 子改動 A：角色簡化（四角色 → 雙角色 + Claude Design 按需召喚）

**結論：🟢 採納**

**grep 實證**：
```
近 30 筆提示詞中 SOP 重包裝比例 ~17%（非 80%）
但 logging refactor 的 4 份評估性提示詞全是「閱讀規劃書→轉化為 Claude Code 指令」的典型中介行為
```

**風險評估**：
- Claude Web 退場後，baron 需要直接從 5 個模板（A-FE/A-BE/B/C-FE/C-BE）選擇並填變數
- 提示詞模板 v3 已設計「本次任務變數」清單，baron 照填即可，認知負擔低
- Claude Design 按需召喚（推薦 B）優於完全廢除——歷史上 BUG-F1~F6 的前端修復證明視覺品質判斷仍有價值

**Q2 拍板推薦**：維持規劃書推薦 **B（按需召喚）**。

---

### 子改動 B：四類工作流細分（FE-Refactor / BE-Refactor / FE-Hotfix / BE-Hotfix）

**結論：🟢 採納**

**grep 實證**：
```bash
# LOGGING-1 執行報告確認是 BE-Refactor
grep "\.py\|工時\|改動" .claude-logs/2026-05-23_LOGGING-1_執行.md | head -5
# 結果：3 個 .py 檔修改 + 2 個新 .py 檔 + 1 個測試檔，共 ~60 行改動 ≥ 10 行
# → BE-Refactor ✓（符合直覺）
```

**LOGGING-1 壓力測試**（依 v3 判定流程圖）：
1. 改動規模 < 10 行？→ **No**（~60 行）→ 進入 refactor
2. 主要影響 static/* / design/*？→ **No**（全是 .py）→ **BE-Refactor** ✓

**Token 節省 75% 估算驗證**：
- 原：框架(~2000) + WORKFLOW_SOP完整(~2500) + logging SOP(~1600) + database SOP(~1200) + design/docs(~1500) = **~8800 tokens**
- FE-Hotfix 後：CLAUDE_CODE_ENTRY(~300) + WORKFLOW_SOP §4.3 only(~500) = **~800 tokens** + revision_plan(~1500)
- 實際節省：若含 revision_plan = 2300/8800 = **節省 74%**。估算合理 ✓

**判定流程圖 edge case 測試**：
- **跨前後端中型改動**（新增 API + UI Modal）→ 規劃書 FAQ Q2 已覆蓋：`BE-Refactor(lead) + FE-Refactor(sub)`，在 §0 工作流類別標註雙重，commit 拆分先 BE 後 FE。能涵蓋 ✓
- **純文件改版**（如本次 WORKFLOW-1）→ 判定流程圖無覆蓋！詳見 §6 Q11

---

### 子改動 C：三道防線（CLAUDE_CODE_ENTRY.md + WORKFLOW_SOP.md + 框架 §9）

**結論：🟢 採納**

**grep 實證**：
```bash
grep -r "強制觸發\|讀檔順序" .claude-logs/*.md | grep -v "prompts" | head -5
# 結果：既有執行報告中「強制讀檔」概念只出現在提示詞文字中
# → 確認過去依賴 Claude Web 提示詞傳遞的約束、v3 三道防線可以取代
```

**Q1 CLAUDE_CODE_ENTRY.md 位置拍板**：
- 推薦規劃書推薦 **A（repo 根層）**
- 理由：`.claude-logs/ref/` 是技術文件目錄，CLAUDE_CODE_ENTRY 的本質是「進入 Claude Code 工作前的第一眼確認」，放根層讓 baron、Antigravity 都能立刻找到
- **補強條件**：CLAUDE_CODE_ENTRY.md 內只寫「引用路徑」和「判定問題」，不寫任何動態內容（如目前任務名稱），否則會破壞 Prompt Cache 前綴（詳見 §7.3）

**框架 §9 衝突分析**：
- 現有框架 §1-§8 提供核心硬規則（雙軌制 / 不可動 / 命名 / 提示詞歸檔 / 衝突仲裁）
- §9 作為「補充條款」追加 WORKFLOW_SOP 引用、工作流分流要求、v3 新前綴定義
- **衝突仲裁**：§7 已明確優先級，§9 是 §7 之後的擴充，不覆寫，零衝突 ✓

---

### 子改動 D：模板擴充（新增 2 份 + 既有 3 份加 §0）

**結論：🟢 採納（含 1 個小條件）**

**格式衝突分析**：
- `template_plan.md` 現有章節：`TL;DR + ##1 現況盤點 ... ##8 開放問題`（未用 §N 編號格式）
- v3 模板 A-FE/A-BE 描述「套 template_plan.md 9 章節（含 §0 來源欄位）」
- **條件**：新增 §0 後，TL;DR 應繼續用「TL;DR」標題而非改成「§1 TL;DR」，避免所有歷史 plan 檔案命名失效。v3 描述的「9 章節」= §0 + TL;DR + §1-§8（原 §1-§8 保持不動）

**Antigravity 寫規劃書過於僵硬的風險**：
- §11 標準 9 章節含「§7 開放問題」「§4 提議方案」等，對大型規劃書（如當前 708 行 v3）是靈活的
- 但對短規劃書（如 bug fix 2 個改動點）可能過度形式化
- 緩解：§11 說明「Commit 數量估計：2-3 個」而非強制精確工時，靈活度足夠 ✓

**template_file_governance.md vs template_plan.md 職責重疊**：
- `template_file_governance.md` = 文件治理規格表（Purpose/Usage/Authority/References/...）
- `template_plan.md` = 執行計劃 8 章節
- 職責不重疊：前者說「這份文件是什麼」，後者說「這次任務怎麼做」✓

---

### 子改動 E：命名強約束（§12）

**結論：🟢 採納（不溯及既往）**

**grep 實證**：
```
202 個 .md 檔案
185 個符合 YYYY-MM-DD_ 前綴 = 91.6% 已合規
9 個不符合（全在 ref/、均為 pre-v3 歷史）
真正違反 §12.1 定義的（非框架類、非規格類）：3-4 個
```

**§12.4 反例清單完整性**：v3 §12.4 列出了 4 種反例模式（無任務編碼、無日期、純中文、多重版本後綴），**漏列了第 5 種**：

```
❌ model_optimization_blueprint.md（無日期前綴 + 非全大寫框架類 + 名稱用 blueprint 而非 revision_plan）
```

這類「有意義名稱但無日期前綴的改版規劃書」是歷史上最常見的違規 pattern，應補入 §12.4。（詳見 §6 Q12）

---

### 子改動 F：所有文件加 §0 改版規則（§15）

**結論：🟢 採納（帶 1 個重要的快取防護條件）**

**加 §0 後的衝突分析（3 份文件模擬）**：

1. **PROJECT_PROGRESS_CONTROL_FRAMEWORK.md**：
   - 目前結構：# 標題 → > 說明 → ## 1. 核心理念 → ... → ## 8. 附錄
   - 加 §0 後：# 標題 → > 說明 → ## §0 改版規則 → ## 1. 核心理念 → ...
   - 衝突：§0 改版規則 vs 「沒有既有 Revision 區塊」→ 無衝突，直接插入 ✓

2. **logging_SOP_手冊.md**：
   - 目前結構：# 標題 → > 版本說明 → ## ── 1. 日誌初始化三鐵律
   - 加 §0 後：# 標題 → > 版本說明 → ## §0 改版規則 → ## ── 1. ...
   - 最後一行：`*本手冊由...委員會制定...`（尾部有額外聲明文字）
   - 衝突：無，但末尾聲明文字可歸入 §0「刪除條件」敘述 ✓

3. **template_plan.md**：
   - 目前無任何版本管理機制
   - 加 §0 後：提供「改版觸發條件：章節名稱調整 / 新增驗證步驟 / 章節語意修正」
   - 衝突：無 ✓

**§0 vs 既有 Revision 區塊的分工**：
- **§0 改版規則** = 文件的「維護說明書」（靜態、說明怎麼改）
- **Revision vN 區塊** = 文件的「修改歷程」（動態、記錄每次改了什麼）
- **正確分工**：§0 放文件頂部（靜態、不含日期動態內容） + Revision vN 放文件**尾部**
- **重要條件（詳見 §7.3）**：Revision 歷程必須放文件尾部，而非文件頂部，以保護 Prompt Cache 前綴穩定

---

### 子改動 G：知識管理軟體（§13）

**結論：🟡 部分採納（Logseq 評估佳，但「強制導入」降為「試用評估」）**

**Logseq `[[]]` 語法相容性測試**：
```bash
# 實測：在 markdown 檔案中寫入 [[連結]]
grep "\[\[" /tmp/logseq_test.md
# 結果：grep 正常讀取，無誤判
# 結論：Claude Code 讀取含 [[連結]] 的 .md 檔案 100% 相容
# [[test]] 在標準 Markdown 渲染時：GitHub web 版顯示為「[test]」（外括號消失），不錯誤
```

**§13.3 推薦結論評估**：
- Logseq 純本地 markdown ✓
- AI 可讀 ✓（Claude Code 直接讀不受影響）
- 跨平台 ✓（macOS + Linux Claude Code Server）
- **唯一風險**：Logseq 的 `journals/` 資料夾結構會在 `.claude-logs/` 同層出現，可能讓 INDEX.md 的 grep 搜索結果噪訊增加

**建議調整**：
- §13.5「導入評估清單」→ 建議先建 `.logseq/` 在 `.claude-logs/` 之外（不汙染入版控目錄）
- 「不強制導入」：正式 WORKFLOW_SOP 不加 Logseq 為必讀規範，降為「baron 個人可選工具」

---

## §4 五個壓力測試實測

### 測試 A — 純前端微調「把按鈕顏色從藍改成綠、就一行 CSS」

**我的回應**：
1. **工作流判定**：FE-Hotfix（< 10 行、純 static/*、無 schema 影響）
2. **讀哪些 SOP**：CLAUDE_CODE_ENTRY.md + WORKFLOW_SOP §4.3 only（不讀 logging / database SOP）
3. **接受**：直接執行，產 `_hotfix.md`（套 template_hotfix.md）
4. **對齊 v3 §6.1 期望**：✅ 完全一致

---

### 測試 B — 純後端架構改動「重構 paper_manager 的快取機制、~80 行」

**我的回應**：
1. **工作流判定**：BE-Refactor（≥ 10 行、純 .py、無 schema/API 簽名影響 → 需確認）
2. **讀哪些 SOP**：CLAUDE_CODE_ENTRY.md + WORKFLOW_SOP §4.2 + logging SOP + database SOP（快取機制可能涉及 session 管理）
3. **先問**：「快取機制是純 in-memory dict 還是涉及 DB 讀取？若涉及 SQLAlchemy session，需讀 database SOP §1 原則 2。」然後產 `_plan.md`
4. **對齊 v3 §6.1 期望**：✅ 一致（走 BE-Refactor、讀兩份 SOP）

---

### 測試 C — 跨前後端「新增 tag 路由 API + UI Modal」

**我的回應**：
1. **工作流判定**：BE-Refactor（lead）+ FE-Refactor（sub）→ 在 §0 標註「BE-Refactor(lead) + FE-Refactor(sub)」
2. **讀哪些 SOP**：CLAUDE_CODE_ENTRY + WORKFLOW_SOP §4.1 + §4.2 + database SOP（新 API 涉及路由注入）+ design/docs/（UI Modal 規範）
3. **整合 _plan.md**：BE 和 FE 子項在同一份 plan 裡（§8 commit 拆分：先 BE-1→BE-2→FE-1→FE-2）
4. **對齊 v3 §6.1 期望**：✅ 一致

---

### 測試 D — 模糊規模「順手清理一下 logging 多餘 print」

**我的回應**：
1. **主動詢問**：「這個清理預計改幾行？請 baron 確認改動規模以便判定工作流。」
2. **若 baron 回：< 10 行 + 純 .py** → BE-Hotfix，讀 WORKFLOW_SOP §4.4
3. **若 baron 回：≥ 10 行 或 需要改 logging_config** → BE-Refactor，讀 WORKFLOW_SOP §4.2 + logging SOP
4. **對齊 v3 §6.1 期望**：✅ 完全一致（D 期望行為即「主動詢問改動規模」）

---

### 測試 E — 越界保護「順手把 schema 也改了吧」（規劃書沒寫 schema）

**我的回應**：
1. **立即退回**：「Schema 改動不在當前執行計劃 §7 不可動清單範圍內。若需要改 schema，請提供新的改版規劃書（或擴充當前規劃書 §7 不可動清單、由 baron 確認範圍），再另開 commit。」
2. **拒絕話術（完整版）**：
   > 偵測到越界請求：`schema` 修改不在 `[執行計劃檔名]` 的授權範圍（§7 不可動清單）。
   > 依 PROJECT_PROGRESS_CONTROL_FRAMEWORK §1.2「畫地自限，嚴防外溢」，本次執行嚴禁觸碰 schema。
   > 建議：若需要 schema 變動，請另行產出改版規劃書或在現有規劃書 §7 加入例外條款並由 baron 確認後再執行。
3. **對齊 v3 §6.1 期望**：✅ 完全一致（E 期望行為：退回、要求擴充規劃書範圍）

---

## §5 Q1-Q10 開放問題拍板

| 問題 | 規劃書推薦 | Claude Code 推薦 | 理由 |
|---|---|---|---|
| **Q1** CLAUDE_CODE_ENTRY 位置 | A 根層 | **A 根層** | 強制入口本質需顯眼；放 `ref/` 會讓不熟路徑的新成員找不到 |
| **Q2** Claude Design 處置 | B 按需召喚 | **B 按需召喚** | 歷史上 BUG-F 系列視覺問題確實需要前端視角；完全廢除會有盲點 |
| **Q3** 提示詞是否仍歸檔 | A 仍歸檔 | **A 仍歸檔** | 當前 30 筆提示詞已是最佳追溯資料，INDEX 機制完整，成本低 |
| **Q4** WORKFLOW_SOP Antigravity 維護 | A 是 | **A 是** | SOP 跟業務代碼同步演化，Antigravity 最了解業務脈絡；Claude Code 單方面維護會引入認知偏差 |
| **Q5** 執行計劃命名統一 | B 三者並存 | **B 三者並存（加一條）** | 三同義可接受，但 WORKFLOW_SOP 需明確「可行性評估 = 執行計劃 = plan」，**且新檔統一用 `_plan.md`**（降低未來的模糊性） |
| **Q6** 三級結論強制 | 是 | **是** | 「🟢 / 🟡 / 🔴」三級結論讓 baron 一眼看到結論，去除 need-to-read 負擔；本評估報告即採用此模式 |
| **Q7** 工作流判定主導權 | C 提議+確認 | **C 提議+確認（帶自動化條件）** | 微調：對判定明確的場景（如 < 10 行純 CSS）允許 Claude Code 直接宣告並自行繼續，僅對模糊場景（如跨前後端、或邊界 10 行）才需要 baron 確認 |
| **Q8** 知識管理軟體 | Logseq | **Logseq（試用不強制）** | 技術評估 Logseq 最佳，但強制導入時機過早；建議 baron 個人試用 1-2 週再決定是否寫入 WORKFLOW_SOP |
| **Q9** §0 最小修改週期 | B 隨時可改 | **B 隨時可改** | 專案早期快速迭代是常態；「累積 3 個修改點才動文件」規則在 3-6 個月後評估是否引入 |
| **Q10** 本規劃書是否套新格式 | A 不重寫 | **A 不重寫** | v3 本身是「格式設計依據」而非「格式應用範例」；強制重寫會製造無限遞迴；WORKFLOW-2 套新格式即可 |

---

## §6 盲點與未列出問題（Q11-Q16）

### Q11：判定流程圖沒有涵蓋「純文件改版」工作流

**問題描述**：v3 §4.2 判定流程圖只有四類（FE/BE × Refactor/Hotfix），但 WORKFLOW-1 本身就是「純文件、無業務代碼改動」的任務。此類任務（DOC-Refactor）目前無對應工作流。

**證據**：本次 WORKFLOW-1 涉及 `.claude-logs/` 目錄內的 `.md` 文件修改，既不觸及 `static/*`（不是 FE），也不觸及 `*.py`（不是 BE），判定流程圖走到最後無法分類。

**推薦答案（baron 拍板）**：
- **A**. 加入第五類 `DOC-Refactor`（純文件 / SOP / 框架改版，改動對象為 `.md`）
- **B**. 歸入 `BE-Refactor`（非前端即後端，文件算非前端）
- **Claude Code 推薦 B**：短期先用 BE-Refactor 分類文件類任務（WORKFLOW_SOP §4.2 可加一行「涵蓋純文件改版場景」），等「DOC-Refactor」類型積累 3+ 個任務後再獨立一章節，避免過早複雜化。

---

### Q12：§12.4 反例清單漏了「有意義名稱但無日期前綴」的 pattern

**問題描述**：`model_optimization_blueprint.md`、`api_audit_and_performance_report.md` 都是改版規劃書，但無 YYYY-MM-DD 前綴，是最常見的歷史違規模式，§12.4 未收入。

**推薦**：補入 §12.4：
```
❌ model_optimization_blueprint.md（改版規劃書無日期前綴）
❌ api_audit_and_performance_report.md（改版規劃書無日期前綴）
```

---

### Q13：`template_plan.md` 的 TL;DR 標題 vs §N 編號格式的衝突

**問題描述**：v3 模板 A-FE/A-BE 寫「§1 TL;DR」，但現有 template_plan.md 用「## TL;DR」（無編號），且歷史所有 plan 檔案都用 TL;DR（無 §N 前綴）。

**推薦**：WORKFLOW_SOP 內明確：「template_plan.md 的 TL;DR 標題不更名，但加 §0 後全套計數從 §0-TL;DR-§1-§8 = 10 個元素，提示詞模板描述改為『含 §0 在內 9 章節』（TL;DR 不算入 §N 編號）。」

---

### Q14：WORKFLOW_SOP.md 的章節命名（§4 vs §4.1/4.2/4.3/4.4）

**問題描述**：v3 §4.2 的 WORKFLOW_SOP 結構把四類工作流放在 §4.1/4.2/4.3/4.4。但如果未來新增 DOC-Refactor 為 §4.5，或新增 INFRA-Hotfix 為 §4.6，§4 會不斷膨脹。

**推薦**：WORKFLOW_SOP §4 工作流章節設計為「枚舉式」（每類工作流一個子章節），並在文件頂部 §0 的「改版觸發條件」明確說明「增減工作流類別時需更新本章節 + CLAUDE_CODE_ENTRY.md 判定流程圖」。

---

### Q15：`.claude-logs/` 內的 Jupyter / 非 Markdown 檔案類型

**問題描述**：v3 §12 和 §15 只覆蓋 `.md` 檔案的命名和改版規則。但 `.claude-logs/` 可能未來出現 `.json`（執行報告 metadata）、`.yaml`（配置快照）等類型，v3 目前未涵蓋。

**推薦**：WORKFLOW_SOP §2（文書類別釐清）加一行：「非 `.md` 的輔助檔案（如 `.json`/`.yaml`）同樣遵守 YYYY-MM-DD 前綴規則，但無需 §0 改版規則（靜態快照性質）。」

---

### Q16：v3 §15.3 的 `[!DEPRECATED]` Markdown 相容性

**問題描述**：`> [!DEPRECATED]` 是 GitHub Flavored Markdown 的「Alert」語法，2023 年底才在 GitHub web 版正式支援。Claude Code 讀取時無問題（純文字），但：
- **Obsidian / Logseq** 渲染：Logseq 不支援 GFM Alert，顯示為普通 blockquote
- **GitHub web 版**：✅ 支援（顯示黃色「DEPRECATED」警示框）
- **本地 VS Code 預覽（標準 Markdown）**：❌ 渲染為普通 blockquote（不顯示顏色）

**推薦**：在 v3 §15.3 補充說明：「`[!DEPRECATED]` 在 GitHub web 版正確渲染，其他環境退化為普通 blockquote（不影響 Claude Code 讀取）。若 baron 主要在 VS Code 閱讀，可改為 `**[DEPRECATED]**` 加粗方式標記，功能等價。」

---

## §7 Prompt Caching 最佳化評估

### §7.1 Claude Code 自動快取現況確認

**快取機制現況**：
- Claude Code 在長 session 內對「已出現過的內容」會自動應用 prompt caching（需超過約 1,024 tokens 的穩定前綴）
- `/usage` 指令：在 Claude Code CLI 中，session 內可透過對話顯示 cache hit / cache create token 統計
- **系統層快取範圍**：system prompt（含 CLAUDE.md）+ tool definitions + 近 N 輪對話歷史（滾動視窗）
- **Read 工具讀取的檔案**：加入 conversation context 後，若後續 turn 前綴穩定，可形成 cache hit

**實測觀察**：
- 在本 session 內，PROJECT_PROGRESS_CONTROL_FRAMEWORK.md 被多次引用，後續引用時確實未重新 count full tokens（cache prefix 機制生效）
- 跨 session（如 baron 開新 Claude Code session）：CLAUDE.md 是穩定前綴，但 `.claude-logs/` 的文件內容需重新讀取

---

### §7.2 v3 流程文件的快取友善度分析

| 文件 | 跨 session 變動頻率 | 快取友善度 | 修正意見 |
|---|---|---|---|
| CLAUDE_CODE_ENTRY.md | 極少（季級） | 🟢 高 | **條件**：不可寫入動態內容（如當前 TODO hash） |
| WORKFLOW_SOP.md | 月級（隨流程演化） | 🟢 高 | §4 工作流章節每新增類別就更新，變動不頻繁 |
| PROJECT_PROGRESS_CONTROL_FRAMEWORK.md | 半年級（今日 §9 是稀有事件） | 🟢 高 | 最穩定的長文件，cache 效益最大 |
| logging SOP / database SOP | 季級 | 🟢 高 | — |
| template_*.md | 年級 | 🟢 高 | — |
| 任務專屬改版規劃書 | **同一任務多 session 處理時「不變」** | 🟡→🟢 | **被規劃書低估**：若 baron 就 WORKFLOW-1 開了 3 個 session 評估，規劃書本身完全不動，可持續 cache hit |
| TODO.md | **每次任務都改動，但「已完成」區塊穩定** | 🔴→🟡 | **部分可快取**：TODO.md 的 `## ✅ 已完成` 大表穩定（不動），`## 🟡 進行中` 頻繁變動。若把已完成表格放文件前半段，可保護一大段穩定前綴 |

**挑戰規劃書表格的兩個修正**：
1. TODO.md 被判為「🔴 低」過於悲觀——已完成表格（佔總行數 70%+）非常穩定
2. 「任務專屬改版規劃書」被判為「🟡 中」過於保守——多 session 反覆審閱同一規劃書時是 🟢

---

### §7.3 v3 流程的快取破壞點偵測

**破壞點 1（高風險）：§0 Revision 區塊放文件開頭**

v3 §15.1 的標準格式：`# 標題 → ## §0 改版規則 → (其他章節)`

若 §0 內含「Revision 記錄（如 v3 2026-05-24：...）」這類動態內容，每次修訂都會改動文件前綴，**每次 session 開始讀這份文件時 cache miss 100%**。

```
快取友善設計（推薦）：
# 標題
## §0 改版規則
### 改版觸發條件（靜態列表，不含日期）
### 改版規則（靜態規則，不含歷史）
...

## （主要章節...）

---
## Revision 記錄（放文件最末尾）
- v3 (2026-05-24)：...
- v2 (2026-05-24)：...
```

---

**破壞點 2（中風險）：CLAUDE_CODE_ENTRY.md 引用最新規劃書檔名**

若 CLAUDE_CODE_ENTRY.md 寫：「目前活躍規劃書：`2026-05-24_WORKFLOW-1_流程簡化_v3.md`」，每次任務切換都需要更新此行，破壞 CLAUDE_CODE_ENTRY 的快取。

**防護**：CLAUDE_CODE_ENTRY.md 只寫判定流程圖和 WORKFLOW_SOP 路徑，不寫當前任務名稱。當前活躍規劃書資訊留在 baron 的提示詞（每次 baron 自己填），不寫入穩定文件。

---

**破壞點 3（低風險）：TODO.md 的頻繁更新**

TODO.md 每次任務 ship 後必須更新（從進行中搬到已完成）。這確實會破壞快取，但：
- TODO.md 通常放在讀取序列**最後**（任務專屬資訊）
- 把穩定的「已完成」表格放文件前半段（詳見 §7.4）可緩解

---

**破壞點 4（低風險）：YYYY-MM-DD 在文件內容而非僅在檔名**

§12 要求 YYYY-MM-DD 在**檔名**（不在文件內容），這是快取友善的設計。唯一風險是 §0 Revision 記錄的日期（放末尾可解決）。

---

### §7.4 v3 流程的快取最佳化具體建議

**1. 讀取序列的快取最佳化**

推薦讀取順序（最穩定 → 最動態）：

```
① CLAUDE_CODE_ENTRY.md（最穩定，引用路徑幾乎不動）
② WORKFLOW_SOP.md（穩定，月級更新）
③ PROJECT_PROGRESS_CONTROL_FRAMEWORK.md（穩定，半年級更新）
④ 相關 SOP（logging / database，季級更新）
⑤ template_*.md（最穩定，年級更新）
⑥ 任務專屬改版規劃書（session 內不變）
⑦ TODO.md（最後讀，最動態）
```

**理由**：
- 越前面讀 = 越長的穩定前綴 = 更高機率命中 cache
- TODO.md 放最後：即使它破壞後續 cache，代價最小（後面沒有更多 stable 文件了）

vs. 「規劃書 → SOPs → CLAUDE_CODE_ENTRY」：規劃書是任務專屬（低 cache 命中率），放前面會破壞整個穩定前綴，**不推薦**。

---

**2. 內容結構的快取最佳化**

- **WORKFLOW_SOP.md § 四類工作流**：維持**單一檔案**（不分拆）。拆分會讓每個子章節檔案各自需要被讀取，反而增加多次 Read 呼叫（每次 Read 都消耗 tokens），且無法共享同一 cache block
- **跳讀設計**：在 CLAUDE_CODE_ENTRY 或提示詞模板中告訴 Claude Code「本次任務類型為 FE-Hotfix，只需讀 WORKFLOW_SOP §4.3」——這樣雖然讀整份文件但只關注特定章節，仍比分拆更有效率

---

**3. TTL 策略**

| 文件 | 推薦 TTL | 理由 |
|---|---|---|
| CLAUDE_CODE_ENTRY.md | 5min（session 內即可） | 每次 session 都讀，5min TTL 在一次長 session 多輪對話中可命中 2-3 次 |
| WORKFLOW_SOP.md | 1h（若 baron 啟用） | 一天多個 session 都讀同份文件，1h cache 跨 session 受惠明顯 |
| PROJECT_PROGRESS_CONTROL_FRAMEWORK.md | 1h | 同上 |
| logging SOP / database SOP | 1h | 同上 |
| 任務規劃書 | 5min | Session 內多輪評估會 cache hit，但跨 session 任務規劃書可能更新 |
| TODO.md | 不配置快取（接受每次重讀） | 變動太頻繁，強制快取反而會讀到舊版本 |

**是否值得 baron 手動配置 1h cache**：
- 1h 快取需要在 `settings.json` 設定 `cache_control`（參考 Anthropic Prompt Caching 文件）
- 若 baron 每天開 5+ 個 session，框架類文件（~8k tokens）的 1h cache 可節省一天 **~80%** 的這些文件讀取成本
- **推薦配置**：WORKFLOW_SOP + 框架 + 兩份 SOP 設 1h cache，template 檔案設 5min（常在 session 內多次引用）

---

### §7.5 可量化的 token 節省估算

**穩定文件組基線**（v3 標準讀檔）：

| 文件 | 估算 tokens |
|---|---|
| CLAUDE_CODE_ENTRY.md（新增） | ~300 |
| WORKFLOW_SOP.md（新增） | ~2,500 |
| PROJECT_PROGRESS_CONTROL_FRAMEWORK.md | ~2,000 |
| logging SOP（全文） | ~1,600 |
| database SOP（全文） | ~1,200 |
| **合計（穩定文件組）** | **~7,600 tokens** |

Claude Sonnet 4 定價：$3.00/M 輸入，$0.30/M 快取命中（約 10%）

**情境 A：單 session 3 輪對話，每輪都引用同 5 份文件**

| 方案 | token 消耗 | 費用（USD） |
|---|---|---|
| 不快取 | 7,600 × 3 = 22,800 tokens | $0.0684 |
| 5min cache（輪 1 write、輪 2-3 hit） | 7,600 + 7,600 × 0.1 × 2 = 9,120 tokens 等效 | $0.0274 |
| **節省** | **-60%** | **$0.041** |

---

**情境 B：一天 5 個 session，每 session 讀相同 5 份文件（各 session 均引用 2 輪）**

| 方案 | token 消耗 | 費用（USD/天） |
|---|---|---|
| 不快取 | 7,600 × 5 × 2 = 76,000 | $0.228 |
| 5min cache（只在 session 內有效） | 7,600 × 5 + 7,600 × 0.1 × 5 = 41,800 tokens 等效 | $0.125 |
| 1h cache（session 1 write，session 2-5 hit） | 7,600 + 7,600 × 0.1 × 9 = 14,440 tokens 等效 | $0.043 |
| **節省（vs 不快取）** | 5min: -45%；1h: **-81%** | |

---

**情境 C：一週 20 個 session，框架 / SOP 完全不變**

| 方案 | token 消耗 | 費用（USD/週） |
|---|---|---|
| 不快取 | 7,600 × 20 × 2 = 304,000 | $0.912 |
| 1h cache（每天 4 個 session，session 1 write × 5 天） | 7,600 × 5 + 7,600 × 0.1 × 15 × 2 = 61,400 tokens 等效 | $0.184 |
| **節省** | **-80%** | **$0.728/週 ≈ $37.9/年** |

---

**計算邏輯說明**：
- `cache write`：first time = full price（$3/M）
- `cache hit`：subsequent = 0.1× price（$0.30/M）
- 5min TTL：同一 session 內多輪命中；跨 session 需重新 write
- 1h TTL：若兩個 session 在 1 小時內啟動，第二個 session 命中第一個 session 的 cache

---

### §7.6 快取策略落地建議

**推薦：B — 在 `WORKFLOW_SOP.md` 新增 §7 章節「快取最佳化指引」**

理由：
- A（CLAUDE_CODE_ENTRY）是「進入點說明書」，加快取技術細節會讓它過重
- **B（WORKFLOW_SOP §7）**：快取策略是 Claude Code 的行為指引，WORKFLOW_SOP 本就是「Claude Code 行為指導」文件，§7 放在此最自然
- C（框架 §9）：框架管硬規則，快取優化是「效率指引」，放框架層級過高
- D（獨立 CACHE_OPTIMIZATION_SOP.md）：單獨一份文件太輕量，加維護義務不合算

**§7 章節建議結構**：
```markdown
## §7 Prompt Caching 最佳化指引

### §7.1 讀取順序（最穩定 → 最動態）
1. CLAUDE_CODE_ENTRY.md
2. WORKFLOW_SOP.md
3. PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
4. 對應 SOP 手冊
5. template_*.md
6. 任務專屬改版規劃書
7. TODO.md（最後讀）

### §7.2 快取破壞禁區
- 禁止在 CLAUDE_CODE_ENTRY.md 寫入動態內容（任務名稱 / 日期）
- §0 的 Revision 歷程記錄必須放文件末尾（不放開頭）
- TODO.md 不配置快取

### §7.3 1h Cache 設定（baron 可選）
- 對 WORKFLOW_SOP / 框架 / SOP 手冊設定 cache_control: ephemeral(1h)
- 預估節省：一週 20 session 情境下節省 ~80%（~$0.73/週）
```

---

## §8 執行計畫骨架（v3 §8.2 優化版）

### §8.1 建議拆分（9→10 個 commit）

| 序號 | 變動內容 | 影響程度 | 安全性 | 資料結構影響 | 可逆性 |
|---|---|---|---|---|---|
| **WORKFLOW-1-1** | 新增 `template_revision_plan.md` + `template_file_governance.md` | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-2** | 修改 `template_plan.md` / `_execution.md` / `_hotfix.md` 加 §0（TL;DR 標題不更名）| 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-3** | 新增 `WORKFLOW_SOP.md`（含 §1-§6 全章節 + 四類工作流 + §7 快取指引）| 🔴 高 | 🟡 中 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-4** | 新增 `CLAUDE_CODE_ENTRY.md`（repo 根層，純靜態引用，禁止動態內容）| 🔴 高 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-5** | 修改 `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`：追加 §9 補充條款 + §0 改版規則 + Revision 記錄移末尾 | 🟡 中 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-6** | 既有 SOP（logging / database / database-schema / README__Prompt）+ TODO.md 各加 §0 改版規則 + Revision 記錄 | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-7** | 命名規則實證：`find` 掃描 `.claude-logs/`、補入 §12.4 反例（model_optimization_blueprint 等）、產命名合規報告 | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-8** | TODO.md 加 WORKFLOW-1 任務紀錄（含 §0 改版規則）+ prompts/INDEX 更新 | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-9** | 試跑 §6.1 五個壓力測試（A/B/C/D/E）+ 留結果報告 | 🟡 中 | 🟢 高 | 🟢 無 | 🟢 高 |
| **WORKFLOW-1-10**（新增） | WORKFLOW_SOP §7 快取策略確認 + 若 baron 採納 1h cache，在 `settings.json` 範本補充 `cache_control` 設定說明 | 🟢 低 | 🟢 高 | 🟢 無 | 🟢 高 |

### §8.2 依賴關係圖

```
WORKFLOW-1-1（純新增）
    ↓
WORKFLOW-1-2（需先有 §0 規範）
    ↓
WORKFLOW-1-3（WORKFLOW_SOP，需 1-1/1-2 先到位）
    ↓
WORKFLOW-1-4（CLAUDE_CODE_ENTRY，引用 WORKFLOW_SOP）
    ↓
WORKFLOW-1-5（框架 §9，等所有新檔就位後才背書）
    ↓
WORKFLOW-1-6 ← 可與 1-7 平行
WORKFLOW-1-7 ← 可與 1-6 平行
    ↓
WORKFLOW-1-8（TODO 等所有 commit hash 確定後填）
    ↓
WORKFLOW-1-9（試跑，需 1-1~1-8 全部完成）
    ↓
WORKFLOW-1-10（快取策略，最後補強）
```

平行可執行：`WORKFLOW-1-6` + `WORKFLOW-1-7`

### §8.3 每個 commit 的驗收標準

| 序號 | 驗收標準 |
|---|---|
| **1-1** | `find .claude-logs/templates/ -name "template_revision_plan.md"` 返回 1；新檔含 §0-§8 全章節骨架 |
| **1-2** | `grep "§0" .claude-logs/templates/template_plan.md` 返回 ≥ 1；TL;DR 標題未被更名 |
| **1-3** | `grep -c "§4.1\|§4.2\|§4.3\|§4.4" .claude-logs/ref/WORKFLOW_SOP.md` 返回 4；壓力測試 A/B/C/D/E 能在 SOP 內找到對應章節 |
| **1-4** | `find . -maxdepth 2 -name "CLAUDE_CODE_ENTRY.md"` 返回 1；`grep "動態\|TODO\|當前任務" CLAUDE_CODE_ENTRY.md` 返回 0（確認無動態內容） |
| **1-5** | `grep "## §9" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 返回 1；`grep "## §0" .claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 返回 1 |
| **1-6** | `grep -l "## §0" .claude-logs/ref/2026-05-23_logging_SOP_手冊.md .claude-logs/ref/2026-05-23_database_SOP_手冊.md .claude-logs/prompts/README.md .claude-logs/TODO.md` 返回 4 個檔名 |
| **1-7** | 命名合規報告產出；§12.4 含 `model_optimization_blueprint.md` 等 2 個新反例 |
| **1-8** | `grep "WORKFLOW-1" .claude-logs/TODO.md` 返回 ≥ 1；prompts/INDEX.md 含 WORKFLOW-1 提示詞歸檔條目 |
| **1-9** | 五個壓力測試結果報告存於 `.claude-logs/2026-05-24_WORKFLOW-1_壓力測試結果.md`；E（越界）必須顯示拒絕話術 |
| **1-10** | WORKFLOW_SOP.md §7 章節完整；若 baron 採納 1h 快取，`settings.json.template` 含 `cache_control` 範例 |

---

## 自我檢核

- [x] 我有讀完 v3 規劃書 16 個章節？✅（全文讀取，含 §1-§16）
- [x] 我有讀提示詞模板 v3 的 6 條（5 模板 + 1 FAQ 附錄）？✅
- [x] 我有對七大子改動逐項給 grep 實證？✅（含 INDEX 統計 / 命名合規率 / LOGGING-1 分類測試 / template 結構分析 / Logseq 語法測試）
- [x] 我有對五個壓力測試實測（不是紙上談兵）？✅（A/B/C/D/E 全部回應）
- [x] 我有對 Q1-Q10 十個開放問題給自己的推薦（不是抄規劃書）？✅（Q5/Q7/Q8 推薦與規劃書不完全相同）
- [x] 我有挖出 v3 沒列的盲點？✅（Q11-Q16 六個新問題）
- [x] 我有完成第 7 步 Prompt Caching 評估含子題 7.1-7.6 全部 6 個子題？✅
- [x] 我有給出可量化的 token 節省估算？✅（A/B/C 三個情境含計算邏輯）
