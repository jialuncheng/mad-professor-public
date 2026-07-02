# CHECKOUT-GUARD C2 — Template Propagation 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | CHECKOUT-GUARD C2 |
| **執行日期** | 2026-07-02 |
| **依據規劃** | `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md §8 C2` |
| **次級參考** | `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`（v2、U2/U5）|
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：C1（`WORKFLOW_SOP §3` 立鐵律，待 baron commit；本 C2 承接於工作樹 C1 之上）。
- **本次改動**：三模板落地 §3 鐵律；純文件、零業務代碼。
- **完成狀態**：三模板已改、§6.2 驗收全綠；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**（plan v2 全局策略 z）：落地 **U2**（三模板 git add 段落註 + check 收官 staged 自檢步驟）+ **U5 之 template 部分**（check mandate checkout 報告）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Template Propagation — run/check/execution §8 加「逐檔·禁廣義 add」+ check 收官新增「commit 前 staged 自檢」步驟 + check mandate `_checkout_執行.md` | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git）**：
  - `.claude-logs/templates/template_prompt_for_run.md`（§8 git add 段 +2 行警語）
  - `.claude-logs/templates/template_prompt_for_check.md`（第二步 git add 註 + 第五步 staged 自檢 + 第六步 mandate 報告，+13 行）
  - `.claude-logs/templates/template_execution.md`（§8 git add 註，+1/-1）
- **備份（入 git·審計）**：archive/`2026-07-02_CHECKOUT-GUARD_C2_template_prompt_for_run.md.bak` / `..._template_prompt_for_check.md.bak` / `..._template_execution.md.bak`（3 份）
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks、C1 執行報告（皆留 baton）。

---

## §4 修法說明

依 tasks §8 C2（三檔改動前各 `cp` 備份）：

1. **`template_prompt_for_run.md §8`**（L124）：git add 清單前加
   > `# ⚠️ 逐檔顯式列名，嚴禁 git add . / git add -A / git add <目錄>（防掃入他任務未追蹤檔；WORKFLOW_SOP §3 收官 git-add 白名單鐵律）` + `# commit 前以 git diff --cached --name-only 自檢`。
2. **`template_execution.md §8`**（L129）：`# git add 清單` 行內加同一警語 + 自檢提示。
3. **`template_prompt_for_check.md`**：
   - 第二步 mv+git add block 開頭加「逐檔·禁廣義 add」註（L160）。
   - **第五步（新）commit 前 staged 自檢**（L193-198）：`git diff --cached --name-only` 對照宣告清單、多/少一檔即停不 commit。
   - **第六步（新）mandate checkout 報告**（L201-203）：收官必產保存 `executions/<date>_<任務>_checkout_執行.md`（Conformance 五維度 + staged 自檢輸出 + baton 歸檔確認 + §8 一行 commit；輕量 Check 慣例；於 checkout commit 一併 git add）。
4. **未動**三模板既有 Conformance 五維度定義 / WORKFLOW-4 U5 減負段 / 三防線 / §1–§7 結構 / L126 Check 報告註。

---

## §5 測試結果（§6.2 驗收終端輸出）

```
$ grep -nE "嚴禁 \`git add \.\`|逐檔顯式列名" template_prompt_for_run.md
124: # ⚠️ 逐檔顯式列名，嚴禁 git add . / -A / <目錄> …           ✅
$ grep -nE "嚴禁 \`git add \.\`|逐檔顯式列名" template_execution.md
129: # git add 清單（⚠️ 逐檔顯式列名，嚴禁 …）                    ✅
$ grep -nE "staged 自檢|git diff --cached --name-only|_checkout_執行.md" template_prompt_for_check.md
193: 第五步：commit 前 staged 自檢 … 197: git diff --cached --name-only
201: 第六步：… checkout 執行報告 … 203: … _checkout_執行.md …       ✅

# 既有結構未動抽驗
$ grep -c "Conformance 驗收流程" template_prompt_for_check.md   → 1  ✅
$ grep -c "防線" template_prompt_for_run.md                     → 4  ✅
$ grep -c "Check 執行報告的 §8 僅保留" template_execution.md      → 1  ✅

$ git diff --stat   # 3 模板〔run +2 / check +13 / execution +1-1〕；零 .py / 零 static/ ✅
```

- 純 DOC、未動 `.py`/`tests/`，不觸發 pytest 迴歸。

---

## §6 不可動清單遵守

- [x] 業務代碼（`pipeline_core.py`/`web_server.py`/`paper_manager.py`/`processor/*`/`static/*`）— 零改動。
- [x] 三模板既有結構（Conformance 五維度定義 / WORKFLOW-4 U5 段 / 三防線 / §1–§7 / L126 註）— 未動（§6.2 grep 證關鍵字數不變）；僅 §8/收官段新增。
- [x] `WORKFLOW_SOP.md` — C2 未動（鐵律本體屬 C1）。
- [x] WORKFLOW-5 hook 腳本 — 未碰。
- [x] baton 過程檔 — 未 git add（本報告留 baton）。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：plan_v1 / tasks / C1 執行報告 / 本 C2 執行報告 暫存 `baton/`，**未 mv、未 git add**（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ 三模板 + 3 `.bak`。
- **下一步**：**checkout — 成果收官歸檔**（Conformance + §7.2 純 DOC 豁免 + baton 一次性歸檔 + TODO 結案 + hash 自癒），由 baron 另下獨立提示詞觸發。
- **§自評（WORKFLOW-4 U3 雙軸）**：(a) 越界？否——僅三模板 §8/收官段新增、既有結構零改。(b) 推進哪個 U-N？正向推進 U2 + U5 template 部分；未做白工。
- **hash 自癒**：git log 掃描，TODO 頂部完成表無 `待 baron 回填` 殘留，本輪無需補填。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（見 §3）：archive/2026-07-02_CHECKOUT-GUARD_C2_template_*.bak（3 份）

# 2. git add 清單（逐檔顯式；僅三模板 + 3 .bak；嚴禁 git add . / baton 暫存檔）
git add .claude-logs/templates/template_prompt_for_run.md
git add .claude-logs/templates/template_prompt_for_check.md
git add .claude-logs/templates/template_execution.md
git add .claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C2_template_prompt_for_run.md.bak
git add .claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C2_template_prompt_for_check.md.bak
git add .claude-logs/archive/2026-07-02_CHECKOUT-GUARD_C2_template_execution.md.bak

# 2.5 commit 前 staged 自檢（dogfood 新鐵律；期望恰為上列 6 檔）
git diff --cached --name-only

# 3. commit message 草稿（寫入 /tmp/CHECKOUT-GUARD_C2_msg.txt）
cat > /tmp/CHECKOUT-GUARD_C2_msg.txt << 'EOF'
DOC-Refactor: CHECKOUT-GUARD C2 — Template Propagation

更新三份模板的 git add 區塊，標明逐檔顯式 add 並嚴禁廣義 add；於 check 模板
新增 commit 前 staged 自檢步驟，並 mandate 收官必須產出與保存 checkout 執行報告。
EOF

# 4. baron 手動執行
git commit -F /tmp/CHECKOUT-GUARD_C2_msg.txt
```
