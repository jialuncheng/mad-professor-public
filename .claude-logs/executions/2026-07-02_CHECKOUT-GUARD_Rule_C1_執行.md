# CHECKOUT-GUARD C1 — Rule Authoring 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | CHECKOUT-GUARD C1 |
| **執行日期** | 2026-07-02 |
| **依據規劃** | `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md §8 C1` |
| **次級參考** | `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`（v2、U1/U5）|
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`e79e5ad`（FE-PERF-1 hash 自癒，git log HEAD）。
- **本次改動**：`ref/WORKFLOW_SOP.md §3` 新增兩條鐵律 + §99.2 v6；純文件、零業務代碼。
- **完成狀態**：鐵律已立、§6.1 驗收全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v2 全局策略 z）：落地 plan **U1**（WORKFLOW_SOP §3 收官 git-add 白名單鐵律 + staged 自檢）+ **U5 之 SSOT 部分**（checkout 執行報告鐵律）；U2（三模板落地）屬 C2。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Rule Authoring — `WORKFLOW_SOP §3` 新增「收官 git-add 白名單鐵律」+「checkout 執行報告鐵律」+ §99.2 v6 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git）**：`.claude-logs/ref/WORKFLOW_SOP.md`（§3 +2 鐵律、§99.2 +v6，diff +3 行）
- **備份（入 git·審計）**：`.claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak`（改動前原狀）
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks（皆留 baton）。

---

## §4 修法說明

依 tasks §8 C1：

1. **備份**：`cp WORKFLOW_SOP.md → archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak`。
2. **§3 強制規則**（於「收官歸檔鐵律」後、「跨 Phase 整合測試前置」前）新增兩條：
   - **收官 git-add 白名單鐵律**（L106）：
     > `git add` 一律逐檔顯式列名，嚴禁 `git add .`／`git add -A`／`git add <目錄>`；commit 前必以 `git diff --cached --name-only` 自檢 staged 集合＝該 commit 宣告清單（執行報告 §3+§8 聯集），多/少一檔即停；跨任務未追蹤檔不得混入。反例錨：FE-PERF-1 混檔→`pre-fe-rebuild` 重寫。
   - **checkout 執行報告鐵律**（L107）：
     > checkout 階段必產並保存 `executions/<date>_<任務>_checkout_執行.md`（Conformance 五維度 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit）。
3. **§99.2**（L233）加 `v6 (2026-07-02)：CHECKOUT-GUARD C1……`。
4. **未動** §1/§2/§4–§7 任何文字（五類定義/文書類別/驗證分級/SOP 核查/命名/接縫契約）。

---

## §5 測試結果（§6.1 驗收終端輸出）

```
$ grep -nE "收官 git-add 白名單鐵律|checkout 執行報告鐵律|git diff --cached --name-only" WORKFLOW_SOP.md
106:- 收官 git-add 白名單鐵律：… 嚴禁 git add . ／ -A ／ <目錄> … git diff --cached --name-only 自檢 …   ✅
107:- checkout 執行報告鐵律：… 必產並保存 executions/…_checkout_執行.md …                                ✅

$ grep -n "v6 (2026-07-02)" WORKFLOW_SOP.md
233:- v6 (2026-07-02)：CHECKOUT-GUARD C1——§3 新增兩鐵律 …                                                ✅

$ grep -cE "^### §1\.[1-5]" WORKFLOW_SOP.md
5     # 五類定義 §1.1–§1.5 標題完整、本體零改 ✅

$ git diff --stat   # WORKFLOW_SOP.md | 3 +++（2 鐵律 + v6）；零 .py / 零 static/ ✅
```

- 純 DOC、未動 `.py`/`tests/`，不觸發 pytest 迴歸。

---

## §6 不可動清單遵守

- [x] 業務代碼（`pipeline_core.py`/`web_server.py`/`paper_manager.py`/`processor/*`/`static/*`）— 零改動。
- [x] `WORKFLOW_SOP.md` §1/§2/§4–§7 五類定義/文書類別/驗證分級/SOP 核查/命名/接縫契約 — 未動（§6.1 grep 證五類標題完整）；僅 §3 新增兩鐵律 + §99.2。
- [x] 三模板 — C1 未動（屬 C2）。
- [x] WORKFLOW-5 hook 腳本 — 未碰。
- [x] baton 過程檔 — 未 git add（本報告留 baton）。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / 本 C1 執行報告 暫存 `baton/`，**未 mv、未 git add**（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ `ref/WORKFLOW_SOP.md` + `.bak`。
- **下一步**：**C2 — Template Propagation（三模板落地）**，由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？否——僅 §3 新增兩鐵律 + §99.2、五類定義零改。(b) 推進哪個 U-N？正向推進 U1 + U5 之 SSOT 部分；未做白工。
- **hash 自癒**：git log 掃描，TODO 頂部完成表無 `待 baron 回填` 殘留（FE-PERF-1/WORKFLOW-5 皆已回填），本輪無需補填。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：.claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak

# 2. git add 清單（逐檔顯式；僅 WORKFLOW_SOP + .bak；嚴禁 baton/ 暫存檔·嚴禁 git add .）
git add .claude-logs/ref/WORKFLOW_SOP.md
git add .claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C1_WORKFLOW_SOP.md.bak

# 2.5 commit 前 staged 自檢（dogfood 新鐵律；期望恰為上列 2 檔）
git diff --cached --name-only

# 3. commit message 草稿（寫入 /tmp/CHECKOUT-GUARD_C1_msg.txt）
cat > /tmp/CHECKOUT-GUARD_C1_msg.txt << 'EOF'
DOC-Refactor: CHECKOUT-GUARD C1 — Rule Authoring

WORKFLOW_SOP §3 新增收官 git-add 白名單鐵律與 checkout 執行報告鐵律，從流程層面
根治收官期夾帶他案未追蹤檔之問題，並於 §99.2 記錄 Revision v6。
EOF

# 4. baron 手動執行
git commit -F /tmp/CHECKOUT-GUARD_C1_msg.txt
```
