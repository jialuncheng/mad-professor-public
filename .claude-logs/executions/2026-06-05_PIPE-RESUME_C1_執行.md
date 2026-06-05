# PIPE-RESUME C1 — Sync System Specs 執行報告

---

**任務代號**：PIPE-RESUME C1（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C1
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：plan_v1 已至 §99.2 v11（六項 + v10 P2 步序 + v11 表格保留、設計定稿）；但**上游母 plan v10 與 PIPE-SPEC 尚未登記** v9 整合（raw_metadata 穿線 / P3 翻譯隔離 / Phase2 摘要先行 / C7-C8 史 / Flip Cleanup）。
- **完成狀態**：C1 純文件同步三份核心規格——**PIPE-SPEC → v4**（§1.1.1 `PipelineContext.raw_metadata` 旁路欄 + §1.2.3.1 翻譯策略隔離原則）；**母 plan → v11**（六項登記 + Phase2 摘要先行 + Flip Cleanup 待辦 + successor pipelines 參照）；**plan_v1**（§7.1 上游同步列由「待落地」標為「✅ 已於 C1 落地（規格層）」）。**零 Python/前端/業務代碼改動**；baton/ 三份主文件**不入 Git**（依指令、僅 .bak + 報告 + TODO + prompts git add）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 同步三份核心規格文件（PIPE-SPEC v4 / 母 plan v11 / plan_v1 §7.1）寫入 raw_metadata 穿線 / P3 翻譯隔離 / P2 摘要先行 / C7-C8 史 / Flip Cleanup | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C1_specification.md.bak` | §1.1.1 raw_metadata 旁路欄 + §1.2.3.1 翻譯隔離原則 + §99.2 v4 |
| 修改 | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v10.md.bak` | §99.2 v11（六項整合登記）|
| 修改 | `.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v1.md.bak` | §7.1 上游同步列標為 ✅ 已落地（規格層）|

> ⚠️ **Git 控制**：baton/ 三份主文件本階段**不 git add**（Checkout 統一歸檔）；僅 `git add` 三份 `.bak`（archive/）+ 執行報告 + TODO + prompts。三份 `.bak` 須在 C1 `git add` 清單（§8）。

---

## §4 修法說明

### §4.1 `PIPE-SPEC`（→ v4、純擴充不動四凍結合約）
- **§1.1.1 `PipelineContext.raw_metadata`**：四份凍結合約承「Phase 接力結構化欄位」；完整原始 metadata（論文 Title/Author/出處/DOI + 履歷 phone/email/domain + confidence/source）走 `PipelineContext.raw_metadata: Dict[str,Any]={}` 旁路欄供 `Paper.metadata_json`、對齊 A 軌 `upsert_paper(self._metadata)` 保真；取代 custom_metadata-in-Spec、非凍結合約欄（屬狀態層可變欄、同 pdf_path/owner_id）。
- **§1.2.3.1 翻譯策略隔離原則**：共用 `Translator` 引擎 + 各路 `run_phase3` 自建 `InjectionContext.constraints` 逐路注入業務規則（`_build_system_prompt` 末段「【額外譯文約束】」）；禁各路 fork prompt/核心。
- **§99.2 v4** 登記。

### §4.2 `母 plan v10`（→ §99.2 v11）
登記六項：C7/C8-hotfix 史 + successor pipelines `__init__.py` import 提醒；`raw_metadata` 穿線（引 PIPE-SPEC §1.1.1）；P3 翻譯隔離（引 §1.2.3.1）；**Phase 2 步序定為①摘要→②LCC→③Glossary 自癒→④翻摘要**（跨路統一）；**Flip Cleanup 待辦：移除 `run_phase1` `_shadow` 影子標題後綴**；§8.5 RAG-ASYNC「首落地隨 PIPE-RESUME」經 C5/影子驗證。純規格同步、不動 §1-§8。

### §4.3 `plan_v1`（§7.1 上游同步標記）
§7.1 Cleanup 清單「上游同步」列：「待落地」→「✅ 已於 v9 tasks C1 落地（規格層）：PIPE-SPEC v4 + 母 plan v11；`PipelineContext.raw_metadata` 程式碼新增屬 C2」。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
# baton/ 三份主文件（gitignore、不入 git）；以下為 git 追蹤之變動：
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v1.md.bak
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v10.md.bak
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_specification.md.bak
# （prompts/ + TODO.md 改動另計；無任何 .py/前端變動）
```

### §5.2 §6.1 驗收（三檔同步 grep）
```bash
# PIPE-SPEC：raw_metadata/翻譯策略隔離/§1.1.1/§1.2.3.1/v4 → 3 命中
# 母 plan：raw_metadata/C7-hotfix/C8-hotfix/Flip Cleanup/摘要先行/v11 → 5 命中
# plan_v1 §7.1「已於 v9 tasks C1 落地」→ 1 命中
```
業務代碼零改動：`git status` 無 `.py`/`static`/`.html`（✅ 純文件）。

### §5.3 SOP 一致性核查（BE-Refactor）
**純文件異動（三份 Markdown 規格）、無 `.py` 改動、不涉資料庫呼叫與 logger，跳過（合規）**。

### §5.4 全套件防 Regression
C1 純文件、不改任何 Python → 無 Regression 風險（既有 480 passed 狀態不受影響）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 任何 Python 程式碼（`pipelines/` / `web_server.py` / `processor/*` 等） | [x] ✅ 未觸碰 |
| 前端 `static/*` | [x] ✅ 未觸碰 |
| baton/ 三份主文件**入 Git** | [x] ✅ 未 git add（留 Checkout） |
| 其他目錄檔案 | [x] ✅ 未動（僅改 baton/ 三份指定 Markdown）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：三份主規格文件就地改於 baton/（PIPE-SPEC/母 plan 為其本身既有 baton 位、不隨本批次 mv）；C1 執行報告暫存 baton/、待 C7 收官歸檔 executions/。
- **下一步**：tasks.md C2 — P1 + Context（`pipelines/context.py` 加 `raw_metadata` + `run_phase1` 寫入 + 影子後綴）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無（C1 為首 commit）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 三份 .bak）

# 2. git add 清單（baton/ 三主文件不入 git，僅 add 備份檔與執行報告）
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v1.md.bak
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_plan_v10.md.bak
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C1_specification.md.bak
git add .claude-logs/baton/2026-06-05_PIPE-RESUME_C1_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C1_msg.txt
```

> ⚠️ **註（baton gitignore）**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C1_執行.md` 屬 `baton/*` gitignore 範圍——上方 `git add` 對其可能為 no-op（被 ignore）。依 WORKFLOW_SOP §3 baton 鐵律，執行報告本應留 baton/ 至 C7 Checkout 才歸檔；此處依本 commit 提示詞 §8 列出，baron 可視 gitignore 行為決定是否強制加入。**baton/ 三份主規格文件確定不 add。**

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C1 — Sync System Specs (同步三份核心規格文件)

同步大改版計畫 plan_v10、重構架構規格書 specification 及 resume plan v1，
寫入 C7/C8 歷史、raw_metadata 穿線、P3 翻譯策略隔離、P2 摘要先行流程異動，
並登記 Revision v9-v11 及 §7.1 Cleanup 清單以對齊最新設計。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C1 三份規格文件同步與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官時 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C1 限改 3 份規格文件、嚴禁改 Python/前端；baton 主文件不 git add；嚴禁自動 commit |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C1 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C1 執行完畢——同步 PIPE-SPEC（→v4：§1.1.1 raw_metadata 旁路欄 + §1.2.3.1 翻譯隔離原則）+ 母 plan（→v11：六項整合 + Phase2 摘要先行 + Flip Cleanup）+ plan_v1（§7.1 上游同步標 ✅）。純文件、零 Python 改動、baton 主文件不入 git；三份 .bak 備份。
