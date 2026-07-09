# FE-CSS-GOV checkout — 成果收官歸檔 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | FE-CSS-GOV checkout |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `tasks.md §8 checkout` + `WORKFLOW_SOP §3 checkout 執行報告鐵律` + CHECKOUT-GUARD 白名單鐵律 |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 收官完成（待 baron commit checkout） |

---

## §1 基準與完成狀態

- **已 ship**：C1 `32e3a1a` / C2 `a49fb28` / C3 `0fbafeb` / C4 `c0b53ab`（baron 已手動 commit）。
- **待 baron commit**：C5（scope map·8 檔·見 C5 報告 §8）→ 然後 checkout（本報告 §8）。
- **收官動作**：Conformance 五維度全綠 + baton 一次性歸檔（plan/tasks/C1–C5 報告）+ TODO 雙層結案 + C3/C4 hash 自癒 + staged 白名單自檢。
- **§7.2 豁免**：純 FE-Refactor CSS/docs、無跨 Phase code handoff → plan Q6 顯式豁免。

---

## §2 Conformance 五維度驗收結果

**維度 1 — 目標規格（plan §2 U2–U5 跨 commit 覆蓋）**：
```
U2 層化：globals @layer 宣告=1 / print+themes ^@layer=0（unlayered 恆勝）        ✅
U3 作用域：#sidebar-bottom .sb-row 殘留=0（E 類收斂）/ css-architecture §5 五類表  ✅
U4 主題：4 themes @layer=0（unlayered）/ demo-bar 死碼=0                          ✅
U5 token：13 T2 全留 globals（作法2 零遷移）/ css-architecture §6 Token 歸屬     ✅
```
（U1 拆檔 C1 已 ship 驗訖；U6 docs 配套隨各 commit 落地。）

**維度 2 — tasks §6 驗收**：§6.1–§6.5 各 commit 執行報告已貼實測；checkout 重跑核心不變式全綠（見維度 1 + 維度 3）。

**維度 3 — 不可動（四鐵防線）**：
```
index.html 自 C1(32e3a1a) 後 diff=0（C2–C5 零觸 JS/HTML）                        ✅
DOM id 守恆=75（C1 保留、C2–C5 未動）                                            ✅
JS 渲染管線 renderMarkdownWithMath 定義=1（完好）                                ✅
27+ JS 契約 class：.sb-row/.collapsed 等零改名（C5 僅卸 CSS 選擇器前綴）          ✅
7 css brace 全平衡（globals9/layout30/sidebar65/content53/chat47/overlays28/print10）✅
D 類跨欄共用語意 class（.title/.toolbar-actions/.h-title）未動（正當 ID-scope）    ✅
```

**維度 4 — 提示詞稽核**：7 份歸檔齊備（plan/Tasks/C1–C5 run），INDEX 同步；C3/C4/C5 條目已補 re-scope 實況。

**維度 5 — msg 草稿**：C5 `/tmp/FE-CSS-GOV_C5_msg.txt` 備妥；checkout msg 見 §8。

**三度執行期 re-scope 裁決（誠實記錄·baron 逐一拍板准）**：C3〔死碼+契約·結構去重外溢 THEME-DEDUP〕/ C4〔零遷移·語意分區+消費地圖〕/ C5〔併 C6/C7·唯 .sb-row 收斂+作用域白名單全量表〕——共性＝85 行審計未看清 chrome CSS 結構良好；grep 反證後誠實縮版、交付真價值、零 false-premise churn。

---

## §3 baton 歸檔確認（3-Phase·非破壞性）

| 檔 | baton → 正式目錄 | 非破壞性 |
|---|---|---|
| plan_v1 | → `plans/2026-07-09_FE-CSS-GOV_…_plan_v1.md` | ✅ 無同名 |
| tasks | → `tasks/2026-07-09_FE-CSS-GOV_…_tasks.md` | ✅ 無同名 |
| C1–C5 執行報告（5） | → `executions/2026-07-09_FE-CSS-GOV_{Split_C1,Layer_C2,Theme_C3,Tokens_C4,Scope_C5}_執行.md` | ✅ 無同名 |
| **長駐不歸檔** | `baton/frontend_css_governance_audit.md`（治理定案源·RESCUE-1 Q3 慣例長駐） | 保留 baton |

`ls baton/ | grep FE-CSS-GOV` = 空（已還原 baton 為僅長駐源 + 他任務）。

---

## §4 TODO 雙層結案 + hash 自癒

- **完整成果表**：`archive/TODO_done_archive.md` 頂部新增 FE-CSS-GOV 六列表格（C1–checkout）+ 修法依據/動因/三度 re-scope/§7.2/不可動/THEME-DEDUP 續集註。
- **一行式索引**：TODO `## ✅ 已完成（索引）` 新增 `✅ FE-Refactor FE-CSS-GOV …（32e3a1a…checkout 待回填、6 commits·C3/C4/C5 三度 re-scope）`。
- **active 移除**：TODO 🔴 高優先 FE-CSS-GOV 區塊移除（THEME-DEDUP ⬜ stub 保留為續集）。
- **hash 自癒**：C1 `32e3a1a`/C2 `a49fb28`/C3 `0fbafeb`/C4 `c0b53ab` 已回填；C5+checkout 待 baron commit 後回填（2 處 `待 baron 回填`）。

---

## §5 staged 白名單自檢（CHECKOUT-GUARD 鐵律）

> **兩段式 commit**（baron 依序執行）：先 C5（per-commit·8 檔）→ 後 checkout（治理歸檔·18 檔）。兩者 staged 集合**互斥**（css-architecture.md 屬 C5 §5 變更、不入 checkout）。

**checkout commit 宣告集合（18 檔·全為治理歸檔·零業務碼零 .bak）**：
```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/prompts/INDEX.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_plan_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_Tasks_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C1_run_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C2_run_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C3_run_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C4_run_提示詞.md
.claude-logs/prompts/2026-07-09_FE-CSS-GOV_C5_run_提示詞.md
.claude-logs/plans/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md
.claude-logs/tasks/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_Split_C1_執行.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_Layer_C2_執行.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_Theme_C3_執行.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_Tokens_C4_執行.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_Scope_C5_執行.md
.claude-logs/executions/2026-07-09_FE-CSS-GOV_checkout_執行.md
```
baron commit 前執行 `git diff --cached --name-only`，須**完全等於**上列 18 檔（多一少一即停）。

---

## §6 不可動清單遵守

- [x] 收官純治理歸檔（TODO/prompts/plans/tasks/executions）+ hash 自癒；零業務碼、零 static/ 觸碰。
- [x] baton 非破壞性歸檔（無覆寫·目標無同名）；長駐 audit 源保留。
- [x] CHECKOUT-GUARD：checkout 集合逐檔顯式、與 C5 互斥、`git diff --cached` 自檢。

---

## §7 銜接

- **收官後續集**：**THEME-DEDUP**（TODO ⬜ stub·主題結構去重·C3 外溢）＝唯一結構續集；token（C4）/作用域（C5）架構已定案、無新外溢。
- **消化 baton 映射**：plan_v1→plans/`0fbafeb 前` / tasks→tasks/ / C1–C5 報告→executions/（本 checkout commit 一次性 git add）。

---

## §8 baron 執行命令（兩段式：先 C5、後 checkout）

```bash
# ── ① 先 commit C5（per-commit·見 C5 報告 §8·8 檔）──
git add static/css/sidebar.css design/docs/css-architecture.md design/docs/dom-reference.md design/docs/components.md
git add .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_sidebar.css.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_css-architecture.md.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_dom-reference.md.bak .claude-logs/archive/2026-07-09_FE-CSS-GOV_C5_components.md.bak
git diff --cached --name-only    # 自檢＝8 檔
git commit -F /tmp/FE-CSS-GOV_C5_msg.txt

# ── ② 後 commit checkout（治理歸檔·18 檔·逐檔顯式）──
git add .claude-logs/TODO.md .claude-logs/archive/TODO_done_archive.md .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-07-09_FE-CSS-GOV_plan_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_Tasks_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_C1_run_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_C2_run_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_C3_run_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_C4_run_提示詞.md .claude-logs/prompts/2026-07-09_FE-CSS-GOV_C5_run_提示詞.md
git add .claude-logs/plans/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md .claude-logs/tasks/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md
git add .claude-logs/executions/2026-07-09_FE-CSS-GOV_Split_C1_執行.md .claude-logs/executions/2026-07-09_FE-CSS-GOV_Layer_C2_執行.md .claude-logs/executions/2026-07-09_FE-CSS-GOV_Theme_C3_執行.md .claude-logs/executions/2026-07-09_FE-CSS-GOV_Tokens_C4_執行.md .claude-logs/executions/2026-07-09_FE-CSS-GOV_Scope_C5_執行.md .claude-logs/executions/2026-07-09_FE-CSS-GOV_checkout_執行.md
git diff --cached --name-only    # 自檢＝18 檔（§5 清單）
git commit -F /tmp/FE-CSS-GOV_checkout_msg.txt
```

commit message 草稿（`/tmp/FE-CSS-GOV_checkout_msg.txt`）：
```
FE-Refactor: FE-CSS-GOV checkout — 成果收官歸檔

Conformance 五維度全綠、baton 一次性歸檔（plan/tasks/C1–C5 執行報告）、
TODO 雙層結案與 C3/C4 hash 自癒。C3/C4/C5 三度執行期 re-scope 均誠實記錄。
```
