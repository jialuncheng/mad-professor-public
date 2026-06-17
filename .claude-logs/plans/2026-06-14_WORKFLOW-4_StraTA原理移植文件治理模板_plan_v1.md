# WORKFLOW-4 StraTA 任務成功率原理移植進文件治理模板 — plan

> 將 StraTA（Strategic Trajectory Abstraction、論文 2605.06642v1）提高長程任務成功率的**執行紀律原理**，透過修改文件治理模板固化進「Plan→Tasks→Run→Check」流程。DOC-Refactor、純模板治理、六階段骨架不推翻。

---

## §0 改版規則
- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：StraTA 證明長程任務成功率的關鍵＝**別純反應式**——開局抽顯式固定策略 z、每步 conditioned 於它、探索語意分散的多候選、逐步自我評判「有無 follow 策略 + 有無推進任務」。我們六階段已內建一半（plan=凍結策略 z / 分層 / 真因+hash=長程信用分配），但有**三處可補強**：① Run 不 re-inject 策略（提示詞只讀 tasks、不讀 plan）② 無「逐 commit 雙軸自評」③ 設計多為單線、無條件化多候選。
- **解法**：DOC-Refactor 改 4–5 個模板的**輕量加法**（讀檔加一列 / 執行報告加一節 / plan 加選用章節）——非新增流程階段、非推翻骨架。
  - **U1 conditioning re-inject**：`template_prompt_for_run` 讀檔清單加 `plan.md`（策略 z）。
  - **U2 對齊說明**：`template_execution §1` 加「本 commit conditioned on plan §2 哪個 U-N」欄。
  - **U3 逐 commit 雙軸自評**：`template_execution` 新增 §自評（越界? 無關? **推進哪個 U-N?**〔正向軸防做白工〕）。
  - **U4 條件化多候選**：`template_plan` 加**選用** §候選方案（高風險才列 ≥2 語意分散方案 + trade-offs）+ `template_prompt_for_plan` 同步。
  - **U5 Check 減負前移**：`template_prompt_for_check` 註明不可動/msg 維度由各 Run §自評前移分攤、Check 聚焦跨 commit U-coverage + §7.2（**減負非省略**）。
- **誠實前提**：StraTA 是 **RL 訓練法**（改梯度）；本案移植的是其「執行紀律原理」、**非演算法**（我們不訓練模型）。
- **影響範圍**：100% DOC-Refactor、零業務代碼；改模板 → 影響後續所有任務（向後相容、純加章節/欄位）。
- **不可動清單**：見 §6。

---

## §2 目標規格

達成下列可檢驗最終狀態：

1. **U1（conditioning re-inject·對應 StraTA §4.1 prepend z）**：`template_prompt_for_run` 之「📖 強制讀檔清單」加入 **`plan.md`（全局策略 z）**——現況只列 tasks.md（局部動作）；使每個 Run 同時受「全局策略 + 局部 tasks」雙重約束。
2. **U2（對齊說明）**：`template_execution §1 基準與完成狀態` 加一欄 **「與全局策略對齊」**：本 commit conditioned on `plan §2` 哪個 U-N、有無偏離。
3. **U3（逐 commit 雙軸自評·對應 StraTA §4 critical self-judgment）**：`template_execution` 新增 **§自評（策略對齊自我審查）**，AI 跑完測試後對照 `git diff` 自答三問：
   - (a) **越界?**——是否超出 `tasks §7 不可動清單`/邊界（無效變更）。
   - (b) **無關/違規?**——是否含與任務無關、或違 CLAUDE.md 規範之改動。
   - (c) **推進哪個 U-N?（正向軸）**——本 commit 推進 `plan §2` 哪一個目標；**答不出＝做白工/scope creep 紅旗**。
   有命中 → AI 報告自 flag + 交付前主動清理/還原。
4. **U4（條件化多候選·對應 StraTA §4.2 diverse rollout）**：`template_plan` 新增**選用** §候選方案（Diverse Rollout）——**僅高風險/模糊/架構級決策**列 ≥2 個**語意分散**（非同案變體）方案 + trade-offs（開發難易/對既有碼衝擊/擴充性）+ 選定理由（被否決案留痕作 §1.9 軌跡）；低風險明說單案即可。`template_prompt_for_plan` 撰寫原則 + 結構表同步要求。
5. **U5（Check 減負前移、措辭誠實）**：`template_prompt_for_check` 註明——不可動（維度三）+ msg 完整（維度五）之審計由各 Run §自評（U3）**前移分攤**；Check 因而**減負但非省略**，仍須驗**跨 commit 目標規格 U-coverage** + **§7.2 跨 Phase 整合**（單 commit 自評涵蓋不到者）。
6. **U6（治理）**：各被改模板加版本/Revision；StraTA 原理非演算法之誠實前提註明於受影響模板說明處。

---

## §3 現況與證據

| # | 模板 | 現況 | 缺口 |
|---|---|---|---|
| U1 | `template_prompt_for_run` L58-65 強制讀檔清單 | 列 CLAUDE.md / WORKFLOW_SOP / **tasks.md**；**無 plan.md** | Run 不 re-inject 全局策略 z |
| U2/U3 | `template_execution` 章節（§1/§4/§5/§6/§7/§8/§99） | 有 §6 不可動遵守、§5 測試；**無 §1 對齊欄、無逐 commit 雙軸自評節** | 缺 conditioning 顯式宣告 + self-judgment |
| U4 | `template_plan` §1-§9 | §2 目標規格 / §4 跨Phase接縫 / §9 OQ；**無「設計方案/候選」章節** | 設計單線、無條件化多候選機制 |
| U4 | `template_prompt_for_plan` L82-89「套用模板結構」表 | 列 §1-§7+§99、**與 template_plan 實際 §4 跨Phase接縫/§5 風險/…不一致（stale）** | 結構表 doc-drift（順帶校正、見 §9 Q5）|
| U5 | `template_prompt_for_check` | 五維度驗收全壓 Check | 不可動/msg 維度可前移分攤、Check 措辭未反映 |

### §3.1 grep 鋼鐵證據
```bash
grep -nE "強制讀檔|tasks.md|plan" .claude-logs/templates/template_prompt_for_run.md   # U1：讀清單僅 tasks
grep -nE "^## |^### " .claude-logs/templates/template_execution.md                     # U2/U3：無 §自評
grep -nE "^## |設計方案|候選" .claude-logs/templates/template_plan.md                   # U4：無候選章節
sed -n '82,89p' .claude-logs/templates/template_prompt_for_plan.md                     # U4：結構表 stale
```

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）
**無**。純文件治理、無 code handoff、無資料傳遞物。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| **流程膨脹（過度官僚）** | 🟡 中 | 全為**輕量加法**（讀清單一列 / 報告一節 / plan 選用章節）；U4 多候選**條件化**（高風險才觸發、低風險單案）→ 不增瑣碎任務負擔 |
| 改模板 → 影響後續所有任務 | 🟡 中 | 純**加**章節/欄位、向後相容；既有已歸檔 plan/execution 不溯及；新模板自下個任務生效 |
| 過度比附 RL（StraTA≠我們） | 🟢 低 | §1 明載「移植原理非演算法、不訓練模型」；模板說明同註 |
| 六階段骨架被誤動 | 🟢 低 | §6 鎖死：不新增/刪階段、不改 plan→tasks→run→check 觸發鏈 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1`。

---

## §6 不可動清單
- [ ] **業務代碼 / .py / .html / .css / static** — 零碰（純模板文件）。
- [ ] **六階段強制觸發鏈（WORKFLOW_SOP §3）** — 不新增/刪階段、不改 plan→tasks→run→check 骨架；僅在既有模板內加章節/欄位。
- [ ] **未列入 §2 的其他模板**（template_tasks / template_hotfix / template_specification / template_file_governance / template_prompt_for_tasks / _sop）— 不動。
- [ ] **Conformance 五維度定義本身（WORKFLOW_SOP §4）** — 不重寫；U5 僅在 Check 提示詞註明「前移分攤 + 減負非省略」、不刪維度。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §7 規格依據
| 依據 | 來源 |
|---|---|
| 工作流定義（DOC-Refactor）| `ref/WORKFLOW_SOP.md §1.3` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 六階段 / Conformance 維度 | `ref/WORKFLOW_SOP.md §3 / §4` |
| StraTA 原理來源 | 論文 2605.06642v1 §4.1 策略引導執行 / §4.2 diverse rollout / §4 critical self-judgment |
| 多輪累積補強既有機制 | `CLAUDE.md §1.9`（與 U4 候選留痕互補）|

---

## §8 驗證計畫
### §8.1 自動化
- 純文件、零 .py → 全套件 pytest 維持基線（旁證未誤動代碼）。
- 靜態 grep：各模板新章節/欄位存在（run 讀清單含 plan / execution 含 §自評 / template_plan 含 §候選方案 / prompt_for_check 含前移分攤註）。
### §8.2 手動端到端（E2E）驗證流程
- **試行**：套新模板跑**下一個真實任務**（plan→run→check），觀察：① Run 提示詞確實讀 plan ② execution §自評三問可答（尤 (c) 推進哪個 U-N）③ Check 因前移而減負、仍抓跨 commit 覆蓋。
- 由 baron 於實際任務確認「不增無謂負擔、確實提早攔截 scope creep」。

---

## §9 Open Questions（🟢 baron review 拍板全定案）

| 問題 | 定案 | 理由 |
|---|---|---|
| **Q1** U4 多候選：每個 plan 硬性 vs 高風險才觸發？ | **🟢 高風險/模糊/架構級才觸發；低風險/常規寫明「單一方案、無多方案需求」** | ① 防形式主義/拖延（拼字修復、補 logger 硬湊 2 案＝垃圾 token + 人工審查成本、違 DRY/altitude）② StraTA Farthest-Point 本質＝在**寬決策空間**探不同路；常規修補空間窄、硬多樣化只生「同案變體」、失語意對抗價值 |
| **Q2** U3 自評是否納入正向軸「推進哪個 U-N」？ | **🟢 強制納入（雙軸：負向防錯 + 正向推進）** | 純負向（越界/改錯）漏掉 AI「自主加班」（寫無關但自以為有用的冗餘碼）；強問「這段推進哪個 U-N」＝強語意錨定，答不出即觸發自我評判懲罰、交付前自清，省 baron 人肉審查（StraTA credit-assignment 精神；早攔 INFRA-3 式做白工）|
| **Q3** U5 是否動 `template_prompt_for_check`？措辭？ | **🟢 動（輕量註記）**：「維度三/五已由各 Run 自評前移分攤；Check 聚焦跨 commit 目標規格 U-coverage（總驗收）+ §7.2 跨 Phase 整合、**減負非省略**」；**不重寫 WORKFLOW_SOP §4 維度定義** | ① 收官階段不再人肉重跑「C1 有沒有寫草稿/C2 有沒有改不可動」（Run-level 當下自檢效率最高）② **前移非取消**：Check 仍是最後總閘門、審計「所有 commit 疊加是否 100% 實現全部 U-N」+ 整合 |
| **Q4** U4 候選章節放 template_plan 何處？ | **🟢 §2 目標規格後新增選用 `### §2.5 候選方案（Diverse Rollout）`** | 邏輯連貫（先 §2 列目標 U-N、再 §2.5 探達成路徑與擇優/否決）；被否決案留痕呼應 `CLAUDE.md §1.9 決策軌跡`、防團隊重踩否決坑 |
| **Q5** 順帶校正 `template_prompt_for_plan` 結構表 stale？ | **🟢 順帶校正** | 本案已因 U4 物理改該檔、一併對齊結構表成本極低、徹底解 doc-drift（該表自 WORKFLOW-3 加 §4 跨Phase 後未同步）|
| **Q6** 代號 + commit 前綴確認？ | **🟢 代號 `WORKFLOW-4`、commit 前綴 `DOC-Refactor`** | 沿 WORKFLOW-1/2/3 流程治理序；前綴符 `WORKFLOW_SOP §6` 命名法典 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| **目的** | 定義 StraTA 原理移植進文件治理模板之目標規格，作為 tasks 拆分與執行基準 |
| **用途** | 供 baron 審查 §9 後拆 tasks；Antigravity 階段 3/5 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 WORKFLOW-4 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改業務代碼 / 嚴禁推翻六階段骨架 / 嚴禁重寫 Conformance 維度定義；僅在既有模板加章節/欄位 |
| **改版觸發條件** | §1–§9 規格變動 / baron 拍板 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務收官歸檔、經 baron 同意移 archive/ |
| **重複防護** | StraTA 原理唯一引用源為論文 + 本 plan；六階段定義唯一源在 WORKFLOW_SOP §3、本案不重寫 |

### §99.2 Revision 歷程
- v2 (2026-06-14)：baron review 拍板、§9 六 OQ 全 🟢 定案（Q1 條件化高風險才觸發 / Q2 雙軸自評含正向 / Q3 動 prompt_for_check 減負非省略·不重寫 §4 維度 / Q4 §2.5 候選方案 / Q5 順帶校正 stale 結構表 / Q6 WORKFLOW-4 + DOC-Refactor 前綴）；理由補強（Q2 狙擊自主加班、Q3 前移非取消總閘門仍在）；U1-U6 結構不變、進入可拆 tasks 狀態
- v1 (2026-06-14)：初版（DOC-Refactor；U1 run 讀 plan re-inject / U2 execution §1 對齊欄 / U3 逐 commit 雙軸自評〔含正向軸 推進哪個 U-N〕/ U4 條件化多候選〔高風險才觸發〕/ U5 Check 減負前移〔非省略〕/ U6 治理；六 OQ，核心 Q1 條件化、Q2 正向軸、Q3 Check 措辭；誠實前提：移植原理非 RL 演算法）
