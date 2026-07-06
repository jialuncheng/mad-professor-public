# RESCUE-1 遺失治理文件挽救 plan

> 舊 worktree 刪除致 git-ignored `baton/` 文件遺失。本計畫挽救「依存活證據可機械還原」之文件（QUEUE-1 v2 救回 / PIPE-SPEC v8 重建 / MODEL-10 殘留清理 / TODO 狀態與失效引用總修正），並補上 baton 慣例的唯一防再遺失閘門（archive `.bak` 審計）。純文件治理、零業務代碼。真·重新設計類（CHAT-STRUCT-1 / TRANSLATE-BOOK v7）不在本案、各自獨立後開。
>
> **工作目錄（baron 拍板覆蓋 CLAUDE.md §3）**：廢棄 worktree `hopeful-yalow-902c50` 後，RESCUE-1 之工作目錄改為**主 repo** `~/mad-professor-public/`（分支 `gemini-refactor`）；待救/待清之 QUEUE-1 v2、MODEL-10 與本 plan 已同位於主 repo `baton/`。本案於主 repo `.claude-logs/{baton,archive}` + `TODO.md` 之寫入為 baron 明示授權（見 §9 Q1）。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：先前工作目錄（worktree）被刪除，`baton/*`（除 README 外 git-ignored）內未收官暫存文件隨之遺失。經權威帳本盤點（§3），確認 4 份治理文件遺失、2 份實體仍存活於主 repo baton、1 份（INFRA-4）實為「從未撰寫」非遺失；同時 TODO active 區存有 3 條指向已遺失/已作廢 baton 路徑的失效引用。
- **解法**：將「可依存活證據機械還原」者一次治理——① 救回主 repo baton 仍存活的 **QUEUE-1 v2**；② 以 `C2.bak`(v7) + C2 執行報告 D5-D8.1 重建 **PIPE-SPEC v8**；③ 清理 baton 內已收官的 **MODEL-10** 殘留；④ 總修正 TODO 失效引用與真遺失審計清單。落點維持 baton 慣例，並以 `archive/*.bak` tracked 審計副本作為唯一防再遺失閘門。
- **影響**：僅 `.claude-logs/`（baton / archive / TODO.md）；零 `.py` / 零 `static/` / 零業務代碼 / 零 schema / 零 API；無 runtime 影響。真·重新設計類（CHAT-STRUCT-1 / TRANSLATE-BOOK v7）**不在本案**。

---

## §2 目標規格

本案完成後須達到以下最終狀態（What it should be，可量化檢驗）：

- **U1 QUEUE-1 v2 救回**：`2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md` 留置於主 repo `baton/`（已與本 plan 同位、存活本體 9890 bytes），**逐字保全不竄改**，且於主 repo `archive/` 留一份 tracked `.bak` 審計副本。
- **U2 PIPE-SPEC v8 重建**：依 `archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak`（v7 基底）+ `executions/2026-06-19_PIPE-SYNC-4_C2_執行.md`（D5-D8.1 變更清單）重建 PIPE-SPEC 規格書本體置於 `baton/`，須含：§1.2.5 section_engine 契約章、§1.2.4 MetaNormalizer 契約章、§1.1.1 litedoc 旁路登記、§1.2/§0「共用真理源家族」措辭、§99.2 v8 Revision；D8.1 不改項（§1.3 L140 news/web/未知 + §3.3 15k + §2 ≥10 + 四凍結合約結構）須**逐字守住 .bak 原值**。重建本體另存一份 tracked `.bak` 至 `archive/`。
- **U3 MODEL-10 殘留清理**：`2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md`（已收官任務之 baton 殘留）自主 repo `baton/` 移除，`mv` 至主 repo `archive/`（tracked 審計、不直接刪除）。
- **U4 TODO 狀態與失效引用總修正**：`TODO.md` 達成下列狀態——
  - INFRA-2 標註「原 plan 已隨 worktree 遺失；產出物已由 PIPE-SPEC / PIPE-CORE 取代」並結案歸位（active 區移除）。
  - QUEUE-1（v1）標註「原 plan 已遺失；經 PIPE-SPEC §3.1 審計判定『重構性廢除』」並結案歸位。
  - QUEUE-1 v2 於 active 區新增/校正條目（救回後指向 baton 存活本體，描述 MinerU 雙實例 CFS 物理分流）。
  - INFRA-4 正名為「尚未撰寫之未來任務（合約轉正旁路收合）」，明載**非遺失**。
  - CHAT-STRUCT-1 / TRANSLATE-BOOK v7 / INFRA-3 之失效 baton 路徑引用就地標註「原 plan 已隨 worktree 遺失、待獨立重建」。
- **U5 真遺失清單審計留痕**：於 TODO.md 集中留一份「2026-06 worktree 刪除遺失清單」尾註，列出全部真遺失文件（CHAT-STRUCT-1 / TRANSLATE-BOOK v5+v7 / INFRA-2 / INFRA-3 / QUEUE-1 v1 / YuLun_Wu_CV_chat.md / 工作筆記）及其處置（重建 / 取代 / 廢除 / 放棄），供未來審計。
- **U6 baton 慣例守恆閘門**：U1/U2 救回/重建本體維持 baton 慣例（不直接入版控），但**每份均於 `archive/` 留 tracked `.bak`**，作為下次 worktree 重建時的唯一還原保險；本案不破例改 PIPE-SPEC「長駐 baton 不版控」既有先例。

<!-- === [WORKFLOW-4 C1 U4] === 選用章節：Diverse Rollout 多候選探索 -->
### §2.5 候選方案（Diverse Rollout）（選用）

**單一方案、無多方案需求。** 本案為低風險文件治理：救回/重建對象皆有存活證據（U1 逐字本體、U2 .bak 基底 + 執行報告變更清單），路徑唯一、無語意分散之架構級決策。落點（baton 慣例 + archive .bak）已於前置討論定案（見 §9 Q3）。PIPE-SPEC v8 之「對照現役 source code 校驗」非候選分歧、屬保真手段（見 §9 Q2）。
<!-- === [WORKFLOW-4 C1 U4 END] === -->

---

## §3 現況與證據

### §3.1 grep 鋼鐵證據

**(1) 主 repo baton 仍存活 2 份（QUEUE-1 v2 + MODEL-10），worktree baton 僅 README：**

```bash
ls -la /home/baroncheng/mad-professor-public/.claude-logs/baton/
# -rw-r--r-- 15313 May 27 19:44 2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md
# -rw-r--r--  9890 May 29 15:17 2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md
# -rw-r--r--  3304 Jun 20 06:25 README.md

ls .claude/worktrees/hopeful-yalow-902c50/.claude-logs/baton/
# README.md   ← 僅此一檔
```

**(2) 權威帳本——tracked 文件曾引用之全部 `baton/<檔名>` 比對磁碟，僅 2 份存活：**

```bash
# 列出所有 referenced baton 路徑 → 逐一比對主 repo + 兩 worktree 磁碟
# SURVIVES: 2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md   （已收官殘留）
# SURVIVES: 2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md （待救）
# 其餘未收官 backlog plan 全 absent（真遺失）
```

**(3) 真遺失文件全檔案系統 0 命中（含主 repo + 兩 worktree）：**

```bash
find /home/baroncheng -iname "*CHAT-STRUCT*" -o -iname "*INFRA-2*"   -o -iname "*INFRA-3*" -o -iname "*INFRA-4*" -o -iname "*TRANSLATE-BOOK*plan*"   -o -iname "*YuLun_Wu_CV*"
# （無輸出）

# 旁證——確證其曾為真 baton plan（非杜撰）：
grep -rhoE "baton/[0-9-]*_(TRANSLATE-BOOK|INFRA-3)[^ )）]*" .claude-logs/
# baton/2026-06-01_TRANSLATE-BOOK_書籍並行翻譯與雙語故事板引導_plan_v5.md
# baton/2026-06-01_TRANSLATE-BOOK_書籍並行翻譯與雙語故事板引導_plan_v7.md
# baton/2026-06-05_INFRA-3_…_plan_v1.md
```

**(4) INFRA-4 從未撰寫（帳本零 `baton/...INFRA-4...` 路徑、僅概念引用）：**

```bash
grep -rn "INFRA-4" .claude-logs/executions/
# ...«為 INFRA-4 鋪規格» / «全面改寫屬 INFRA-4» / «轉正屬 INFRA-4 遠期»  ← 皆概念、非檔案
```

**(5) PIPE-SPEC 不 tracked（長駐 baton），最新存活快照為 C2.bak = v7：**

```bash
git ls-files | grep -iE "PIPE-SPEC"
# archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak   ← 最新快照（pre-C2 = v7）
# plans/ 無 PIPE-SPEC 本體；本體長駐 baton、已隨 worktree 遺失

grep -n "§99.2\|v[0-9]+ (2026" archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak | tail -1
# v7 (2026-06-14)：PIPE-SYNC-3 C1 SPEC Sync ...   ← 確認 .bak 為 v7（缺 v8 D5-D8.1）
```

**(6) C2 執行報告完整記錄 D5-D8.1 變更（重建 v8 之語意級依據）：**

```bash
grep -nE "D5b?|D6|D7|D8" executions/2026-06-19_PIPE-SYNC-4_C2_執行.md
# D5 新增 §1.2.5 section_engine 契約章（三簇介面 + 四鐵律）
# D5b 新增 §1.2.4 MetaNormalizer 契約章（normalize_fields 三路分流 + schema）
# D6 §1.1.1 登記 LiteDoc 旁路欄位（date/url/publisher/translated_title）
# D7 「三大共用真理源」→「共用真理源家族」（§1.2 標題 + §0）
# D8 §99.2 加 v8 Revision
# D8.1 §1.3 L140 / §3.3 15k / §2 ≥10 / 四凍結合約結構 未改（grep 證）
```

### §3.2 相關現況（不動之既有狀態）

- **TODO.md active 區三條失效引用**：CHAT-STRUCT-1（指 `baton/2026-06-08_CHAT-STRUCT-1_..._plan_v1.md`，已遺失）/ QUEUE-1（指 `2026-05-23_QUEUE-1_..._plan.md`，已遺失且已判廢除）/ INFRA-2（指 `baton/2026-05-30_INFRA-2_..._plan.md`，已遺失且已被取代）。
- **既有版控先例**（不重訂、本案沿用）：PIPE-SYNC-2 `195e12b`——「真理源本體長駐 baton 不入版控、`.bak` 入 archive 作審計」。
- **既有 .bak 鐵律**（WORKFLOW_SOP §3）：修改既有檔案前產出的 `.bak` 必須入對應 Run 階段 `git add`（審計存檔）。

---

## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則標「無」）

**無。** 本案為純文件治理（DOC-Refactor），無業務代碼、無 Phase/模組間資料 handoff（無 producer/consumer key 交接）。§7.2 收官前跨 Phase 整合測試之豁免申請見 §9 Q4。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 於主 repo 操作違反 CLAUDE.md §3「嚴禁讀寫主 repo」 | 🟡 中 | baron 已拍板覆蓋 §3、指定主 repo 為 RESCUE-1 工作目錄（廢棄 worktree 後）；授權範圍**僅限** `.claude-logs/{baton,archive}` + `TODO.md`，業務碼/工作樹/✅ 已完成表仍嚴禁碰（§6）。詳 §9 Q1。 |
| PIPE-SPEC v8 重建非逐字還原（D5/D5b 新章為重寫） | 🟡 中 | D8.1 不改項逐字守 .bak 原值；D5/D5b/D6 對照**現役 source code**（`pipelines/section_engine.py` / MetaNormalizer / `litedoc_pipeline.py`）+ C2 執行報告校驗、語意忠實。誠實標註非 byte-identical（§9 Q2）。 |
| baton 慣例致 U1/U2 未來再遺失 | 🟡 中 | 以 `archive/*.bak` tracked 審計副本為唯一還原閘門（U6）；不破例入版控（維持 PIPE-SPEC 先例、見 §9 Q3）。 |
| TODO 大幅改寫誤動已收官表格 | 🟢 低 | 僅動 active 區三條 + 補一份審計尾註；頂部 ✅ 已完成表格與既有 hash **零改**；改動以 grep 前後比對驗證（§8）。 |
| 真遺失文件被誤判可救 | 🟢 低 | 已由 §3 權威帳本 + 全檔案系統 find 雙重佐證（0 命中）；本案不嘗試重建真遺失者，僅審計留痕。 |
| 認知負荷 / 與進行中分支衝突 | 🟢 低 | 純 `.claude-logs/` 文件、無進行中業務分支相依；零 runtime。 |

對齊 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

**以下檔案與邏輯在本案中嚴禁任何改動：**

- [ ] 任何 `.py` 業務代碼（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `pipelines/*.py` / `static/*`）——本案零業務碼。
- [ ] 主 repo 業務代碼 / 工作樹 / 任何 `.py` / `static/`——baron 對主 repo 之授權**僅限** `.claude-logs/{baton,archive}` + `TODO.md`（§9 Q1）；授權範圍外之主 repo 一切檔案嚴禁碰。
- [ ] `TODO.md` 頂部 `## ✅ 已完成` 既有表格內容與所有既有 Commit Hash——僅動 active 區與新增審計尾註。
- [ ] PIPE-SPEC v8 之 D8.1 不改項（§1.3 L140 news/web/未知 + §3.3 15k + §2 ≥10 + 四凍結合約結構）——須逐字守 `C2.bak` 原值、不得趁重建竄改。
- [ ] 既有 `archive/` 內所有 `.bak` 與長駐真理源——本案僅**新增**審計副本，不改既有。
- [ ] `.gitignore` 之 `baton/*` 排除規則與 PIPE-SPEC「長駐 baton 不版控」先例——本案不破例（見 §9 Q3）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流類別判定（DOC-Refactor） | `CLAUDE.md §2` / `ref/WORKFLOW_SOP.md §1.3` |
| 工作目錄硬規則（baton 暫存 / 嚴禁讀寫主 repo） | `CLAUDE.md §3` |
| 文件歸屬判定（baton / archive / plans） | `ref/WORKFLOW_SOP.md §2` |
| 六階段觸發鏈 + .bak 鐵律 + baton 暫存鐵律 + 收官歸檔鐵律 | `ref/WORKFLOW_SOP.md §3` |
| DOC-Refactor 驗收（§6.1 驗證清單） | `ref/WORKFLOW_SOP.md §1.3 / §4` |
| 跨 Phase 整合測試與顯式豁免 | `ref/WORKFLOW_SOP.md §7.2` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 任務生命週期 / TODO 維護 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §2` |
| 版控先例（真理源長駐 baton、.bak→archive 審計） | TODO.md PIPE-SYNC-2 `195e12b` |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試基線**：本案零業務代碼改動，pytest 基線**不退化**（沿用既有 704 passed / 唯一既有 LOG_FORMAT env flake）。
  ```bash
  pytest tests/ -v   # 預期：與基線一致、無新增紅燈（非本案驗收主軸）
  ```
- **預計新增測試**：無（純 .md 文件治理、無可單元覆蓋之邏輯）。

### §8.2 手動驗證流程（DOC-Refactor §6.1 驗證清單）

1. **目標檔存在且非空**：`ls -la` 確認主 repo baton 含 QUEUE-1 v2 + PIPE-SPEC v8 本體；主 repo `archive/` 含兩份新 `.bak`。
2. **U1 逐字保全**：QUEUE-1 v2 大小／內容與帳本記錄一致（9890 bytes）、git 歷史旁證無竄改（救援前後本體未變）。
3. **U2 內容完整**：`grep` PIPE-SPEC v8 命中 §1.2.5 / §1.2.4 / §1.1.1 litedoc 旁路 / 「共用真理源家族」/ §99.2 v8；`grep` D8.1 不改項（news/web/未知 + 15k + ≥10）仍在且同 .bak 原值。
4. **U3 殘留清除**：`ls` 確認 baton 不再含 MODEL-10 plan；`archive/` 含其審計副本。
5. **U4 TODO 修正**：`grep -n "INFRA-2\|QUEUE-1\|INFRA-4\|CHAT-STRUCT-1\|TRANSLATE-BOOK\|INFRA-3" TODO.md` 驗證狀態標註到位；頂部 ✅ 表格與既有 hash `git diff` 證零改。
6. **baton 不入版控**：`git check-ignore -v .claude-logs/baton/<QUEUE-1 v2 檔>` 命中排除；`.bak` 於 archive/ 為 tracked（`git status` 可見）。
7. **命名合規**：對照 WORKFLOW_SOP §6（本 plan / archive .bak 日期前綴）。

---

## §9 拍板定案之設計決策 (Decided Questions)

本案經 2026-06-29 審查，§9 開放問題全數由 baron 拍板定案，決策如下：

| 問題 | 決定方案 | 執行細節與合規約束 |
|---|---|---|
| **Q1** 主 repo 操作合規性 | **baron 拍板覆蓋 §3、主 repo 為工作目錄** | 廢棄 worktree `hopeful-yalow-902c50` 後，baron（2026-06-29）明示指定主 repo `~/mad-professor-public/`（`gemini-refactor`）為 RESCUE-1 工作目錄、覆蓋 CLAUDE.md §3；QUEUE-1 v2 已與本 plan 同位於主 repo `baton/`、無需跨環境複製。授權範圍**僅限** `.claude-logs/{baton,archive}` + `TODO.md`，主 repo 業務碼/工作樹仍嚴禁碰（§6）。 |
| **Q2** PIPE-SPEC v8 重建保真度 | **接受重寫、對照現役 code 校驗** | 針對 D5/D5b 契約章，對照現役已落地程式碼（`section_engine.py` / `MetaNormalizer`）進行語意忠實之重建；D8.1 不改項則必須與 `C2.bak` 逐字一致。計畫書中誠實標註非 byte-identical。 |
| **Q3** U1/U2 歸檔落點 | **維持 baton 慣例 + archive `.bak` 審計** | 依據 `195e12b` 先例，主體留置於 git-ignored 的 `baton/`。為防範再次遺失，**強制於 `tasks` 階段將兩份主體之 `.bak` 複製至 `archive/` 並 `git add` 入版控**，作為唯一還原保險。 |
| **Q4** §7.2 整合測試豁免 | **顯式豁免** | 本案為純文件治理（DOC-Refactor），無業務程式碼變動，無資料交接契約，予以顯式豁免。 |
| **Q5** MODEL-10 殘留處置 | **主 repo 就地 `mv` → archive（已授權）** | Q1 授權後，主 repo `baton/` 之 MODEL-10 殘留就地 `mv` 至主 repo `archive/` 並 `git add`（tracked 審計、不直接刪除）；無需再延 baron 手動。屬授權範圍（`.claude-logs/{baton,archive}`）內。 |
| **Q6** TODO 審計清單呈現 | **active 條目就地標註 + 集中尾註** | `TODO.md` 中，active 區失效引用就地加註「原 plan 隨 worktree 遺失」；並於文件末尾新增「2026-06 worktree 刪除遺失清單」集中尾註。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESCUE-1 遺失治理文件挽救的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 RESCUE-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段）；真·重新設計類（CHAT-STRUCT-1 / TRANSLATE-BOOK v7）不在本案 |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義本案技術規格；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md；版控先例引用 PIPE-SYNC-2 |

### §99.2 Revision 歷程

- v1.2 (2026-06-29)：工作目錄校正——廢棄 worktree `hopeful-yalow-902c50`、baron 拍板改主 repo `gemini-refactor` 為 RESCUE-1 工作目錄（覆蓋 CLAUDE.md §3、授權範圍限 `.claude-logs/{baton,archive}`+`TODO.md`）；連動改寫 §1 工作目錄聲明 / U1 留置主 repo baton / U3 主 repo 就地 mv / §5 風險 / §6 不可動 / §9 Q1（複製合規→主 repo 授權）+ Q5（worktree 移轉→主 repo 就地 mv，免延 baron 手動）。
- v1.1 (2026-06-29)：baron 審查拍板——§9 開放問題全數定案為「拍板定案之設計決策」，補齊複製合規、重寫金標、`.bak` 存檔閘門及主 repo 殘留手動清理等約束。
- v1 (2026-06-28)：初版建立——A 類機械救援範圍（U1 QUEUE-1 v2 救回 / U2 PIPE-SPEC v8 重建 / U3 MODEL-10 殘留清理 / U4 TODO 總修正 / U5 真遺失審計 / U6 baton 慣例守恆閘門）+ §3 權威帳本六證 + §9 六 OQ；B 類（CHAT-STRUCT-1 / TRANSLATE-BOOK v7）顯式排除。
