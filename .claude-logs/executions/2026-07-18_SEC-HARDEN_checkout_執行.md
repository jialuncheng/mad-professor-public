# SEC-HARDEN checkout — 成果收官歸檔 執行報告

> **任務代號**：SEC-HARDEN checkout（Check 階段·輕量慣例）
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Checkout)
> **落地 Git Hash**：`（留空·由 baron 回填）`
> **執行日期**：2026-07-18
> **依據**：`tasks/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md §4.5/§8 checkout` / WORKFLOW_SOP §3 checkout 執行報告鐵律 + 收官 git-add 白名單鐵律

---

## §1 Conformance 驗收結果（五維度）

### 維度一：plan §2 目標規格（七項）對照落地

| # | 規格項 | 落地實證 | 判定 |
|---|---|---|---|
| 1 | #3 XFF 可信代理閘控·**右向左**解析·嚴禁最左值 | `_resolve_client_ip`（web_server.py:327）reversed 遍歷剝可信代理；`split(",")[0]` 全檔 grep=0；偽造 XFF 輪換仍鎖定（`test_rate_limit_still_locks_with_forged_xff` 端到端） | 🟢 |
| 2 | #4 CORS 顯式清單非 `*`·不啟用 credentials | `allow_origins=settings.CORS_ALLOW_ORIGINS`（:283）·解析層剔 `*`·credentials 未傳參（`test_credentials_not_enabled`） | 🟢 |
| 3 | #5 僅遮 broad Exception 三出口·**排除** 3 處 ValueError | broker/主軌/影子軌全遮通用訊息；`raise HTTPException(status_code=400, detail=str(e))` count==3 源碼守衛鎖定 | 🟢 |
| 4 | #6 內建主題不可覆寫·大小寫不敏感 | `BUILTIN_THEMES` frozenset（:1272）+ `sanitized.lower()` 守衛（:1309·write_bytes 前）；mies/Mies/KAHN/nArA→400 零寫檔 | 🟢 |
| 5 | #8 timing 等化·未設 hash 亦跑 dummy | `_DUMMY_BCRYPT_HASH` 模組常數（cost 12）；錯帳號/未設 hash 均恰一次 bcrypt（spy 計數斷言）；認證判定零動（成功登入測試續綠） | 🟢 |
| 6 | 零回歸·綠燈基線不退化（715） | 遞增綠燈鏈 715→729（C1）→734（C2）→739（C3）→**745 passed / 0 failed**（C4·收官終驗重跑實測） | 🟢 |
| 7 | SOP 合規（#5 新增 logger.error 帶 exc_info·零裸 commit） | C3 主軌 logger.error 補 exc_info=True（:690 grep 實證）；四 commit §6.6 雙核查全貼、database 零命中 | 🟢 |

### 維度二：tasks §6 驗收條件

- §6.1–§6.4 各 commit 驗收 grep 全數命中（各執行報告 §5 實貼）；§6.5 全套件每 commit 遞增綠燈；§6.6 SOP 雙核查每報告實貼。**收官終驗重跑**：`pytest tests/` → **745 passed / 3 skipped / 0 failed**、`pytest tests/test_sec_harden.py` → **30 passed**。🟢

### 維度三：不可動清單（tasks §7）

- login 認證結果判定零動（`ok` 分支 byte 未動·`test_successful_login_unchanged`）🟢
- theme sanitize/traversal/大小限制零弱化（僅插入 if 守衛·`test_existing_filters_not_weakened`）🟢
- 3 處 ValueError HTTPException 零觸碰（count==3 守衛）🟢
- SSE 協定欄位零改（僅 error 值來源）🟢
- SESSION_SECRET fail-closed / 前端 static / DB schema / SEC-SECRET·SEC-XSS 既有落地零觸碰 🟢
- ⚠️ **C1 deviation（提請 baron 確認）**：`tests/test_api_performance_and_robustness.py::test_x_forwarded_for_parsing`（API-PERF C2 產物）原斷言「XFF 最左值取法」＝C1 明令根除之可偽造行為 → 最小幅度同步至新契約（僅該測試·`.bak` 入審計·C1 報告 §4.4）；已隨 `52ebae8` ship＝baron 已實質核可。🟢

### 維度四：提示詞歸檔稽核（7 份實檔）

```
$ ls .claude-logs/prompts/ | grep "SEC-HARDEN"
2026-07-12_SEC-HARDEN_plan_提示詞.md
2026-07-12_SEC-HARDEN_tasks_提示詞.md
2026-07-18_SEC-HARDEN_C1_run_提示詞.md
2026-07-18_SEC-HARDEN_C2_run_提示詞.md
2026-07-18_SEC-HARDEN_C3_run_提示詞.md
2026-07-18_SEC-HARDEN_C4_run_提示詞.md
2026-07-18_SEC-HARDEN_Check_提示詞.md
```
7/7 齊備、全數 git add 入版控、INDEX.md 分類節 + 時間列同步。🟢

### 維度五：commit msg 草稿完整性

- C1–C4 msg 草稿各 Run 產出（`/tmp/SEC-HARDEN_C{1-4}_msg.txt`）、baron 已用以 ship（`52ebae8`/`a5e2bd4`/`bc5d5f4`/`3942e20`·subject 與草稿一致）；checkout msg 已寫 `/tmp/SEC-HARDEN_checkout_msg.txt`（§8）。🟢

**Conformance 總判定：🟢 全綠通過**（§7.2 跨 Phase 整合測試：單一後端模組、無 Phase/模組間資料 handoff → 依 plan OQ6 **顯式豁免**）。

---

## §2 落地 Commit 表格（全案）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Login Hardening（XFF 右向左閘控 + timing 等化） | `52ebae8` |
| C2 | CORS Restriction（顯式白名單·拒 `*`） | `a5e2bd4` |
| C3 | Error Masking（三 broad-Exception 出口遮蔽·排除 ValueError） | `bc5d5f4` |
| C4 | Theme Overwrite Guard（BUILTIN_THEMES·大小寫不敏感） | `3942e20` |
| checkout | 本收官歸檔 | `待 baron 回填` |

---

## §3 歸檔搬移清單（baton → 正式目錄·標準 mv 非 git mv）

| 原位置（baton/） | 歸檔位置 |
|---|---|
| `2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md` | `plans/` |
| `2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md` | `tasks/` |
| `2026-07-18_SEC-HARDEN_C1_執行.md` | `executions/` |
| `2026-07-18_SEC-HARDEN_C2_執行.md` | `executions/` |
| `2026-07-18_SEC-HARDEN_C3_執行.md` | `executions/` |
| `2026-07-18_SEC-HARDEN_C4_執行.md` | `executions/` |

**baton/ 歸檔後現況**（`ls` 實測）：`README.md` + 長駐真理源 `QUEUE-1 v2 plan`／`PIPE-SPEC`（RESCUE-1 Q3 定案長駐不歸檔）+ audit 長駐源 `frontend_css_governance_audit.md`／Osmani PDF（FE-PERF-2 Check 先例「長駐不碰」）——**SEC-HARDEN 暫存檔零殘留**。✅

**Baton README §2 Phase 2 確定性自檢**：Provenance（檔名任務代號+頂部元數據塊齊備）✅ / Schema（template 章節齊備）✅ / Non-destructive（正式目錄無同名既有檔·零覆寫）✅ / Scope（plans/tasks/executions 歸屬正確）✅。

---

## §4 TODO 雙層結案 + 全量 hash 自癒

- **TODO.md**：active 條目移除、✅ 索引區新增 pointer 一行（`52ebae8`…`3942e20`、5 commits）、底部類別索引新增 `### SEC-HARDEN (✅ 已完成)` 節、頂部日期戳更新。
- **archive/TODO_done_archive.md**：追加完整 5-commit 成果表格（含修法依據/動因/三項運維提醒註）。
- **hash 自癒（雙源）**：C1–C4 真實 hash 全量回填 TODO 索引/類別索引/archive 表格/各執行報告；**GOV-PATH-FIX「Checkout Hash」自癒判定**——`git log -- executions/2026-07-12_GOV-PATH-FIX_checkout_執行.md` 實證其歸檔檔隨 **`52ebae8`**（SEC-HARDEN C1 commit）落地 → 佔位符回填 `52ebae8` 並註明；archive 內既有 SEC-XSS checkout hash 自癒（`9586866`·前序未暫存修改）隨本 commit 一併入庫。
- 全庫殘留 `待 baron 回填` 僅 2 處＝**本任務 checkout hash 本身**（TODO 索引行 + archive 表格·baron commit 後回填）。

---

## §5 staged-set 自檢（收官 git-add 白名單鐵律·實貼）

```
$ git diff --cached --name-only
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-18_SEC-HARDEN_C1_執行.md
.claude-logs/executions/2026-07-18_SEC-HARDEN_C2_執行.md
.claude-logs/executions/2026-07-18_SEC-HARDEN_C3_執行.md
.claude-logs/executions/2026-07-18_SEC-HARDEN_C4_執行.md
.claude-logs/executions/2026-07-18_SEC-HARDEN_checkout_執行.md
.claude-logs/plans/2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md
.claude-logs/prompts/2026-07-12_SEC-HARDEN_plan_提示詞.md
.claude-logs/prompts/2026-07-12_SEC-HARDEN_tasks_提示詞.md
.claude-logs/prompts/2026-07-18_SEC-HARDEN_C1_run_提示詞.md
.claude-logs/prompts/2026-07-18_SEC-HARDEN_C2_run_提示詞.md
.claude-logs/prompts/2026-07-18_SEC-HARDEN_C3_run_提示詞.md
.claude-logs/prompts/2026-07-18_SEC-HARDEN_C4_run_提示詞.md
.claude-logs/prompts/2026-07-18_SEC-HARDEN_Check_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/tasks/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md
```

**17 檔＝宣告白名單完全等集**（plan + tasks + 5 執行報告 + 7 提示詞 + INDEX + TODO + archive）、零跨任務混入。跨任務未追蹤檔 `prompts/2026-07-10_PROJECT-REVIEW_審查_提示詞.md` **刻意排除**（白名單鐵律·屬 PROJECT-REVIEW、留待其歸屬任務處理）。✅

---

## §6 §7.2 整合測試豁免

跨 Phase 整合測試：本任務單一後端模組（`web_server.py` + `settings.py` config）、無 Phase/模組間資料 handoff（plan §4 標「無」）→ 依 WORKFLOW_SOP §7.2 + plan OQ6 **顯式豁免**（baron 已拍板）。

---

## §7 銜接與運維提醒

- **全案結案**：PROJECT-REVIEW 安全審查 #3（MEDIUM）/ #4 / #5 / #6 / #8（LOW）全數關閉；`tests/test_sec_harden.py` 30 守衛測試長駐。
- **⚠️ 運維三提醒**：① 反向代理（Docker/Nginx/LB）部署**必須** `.env` 設 `TRUSTED_PROXIES`（否則回退 API-PERF C2 閘道鎖死問題；直連/本機開發不受影響）；② 生產跨源部署須設 `CORS_ALLOW_ORIGINS`（預設僅本機 8080 兩形態）；③ 前端錯誤訊息已通用化、診斷一律看 server log（exc_info 完整堆疊 + trace_id）。
- **baron E2E 建議**（plan §8.2·非阻斷）：直連偽造 XFF 連錯 5 次→第 6 次鎖定；跨源 fetch 無 CORS 放行；觸發處理錯誤→前端通用訊息、log 有堆疊；上傳 `mies.css`→400；錯帳號/錯密碼回應時間無顯著差異。
- **既有債留檔**：`web_server.py:195` broker DB append `logger.error` 無 exc_info（非 client 出口·plan OQ3 歸 SOP-COMPLY 另案）。

---

## §8 baron 執行命令

```bash
# 1. 搬移暫存檔已完成（§3 已列·baton 已淨空 SEC-HARDEN 檔）
# 2. git add 已由 Claude Code 逐檔完成（§5 staged 自檢 17 檔＝宣告清單全等·嚴禁再廣義 add）
# 3. commit message 草稿已寫入 /tmp/SEC-HARDEN_checkout_msg.txt
# 4. baron 手動執行（建議先 git diff --cached --name-only 複核 = §5 清單）：
git commit -F /tmp/SEC-HARDEN_checkout_msg.txt
```

### §8.2 commit message 草稿內容

```
BE-Refactor: SEC-HARDEN checkout — 成果收官歸檔（成果歸檔與移出暫存）

1. Conformance 總驗收通過，完成後端安全加固 5 項防禦（login IP/timing、CORS、error遮蔽、theme guard）。
2. 將暫存於 baton/ 的 plan、tasks、C1-C4 執行報告搬移歸檔至正式目錄。
3. 歸檔與納入版控 7 個階段的 prompts 提示詞及 INDEX.md 索引。
4. TODO.md 進行雙層結案更新（移至已完成索引，archive 追加完成明細表，完成歷史 hash 自動補填，含 GOV-PATH-FIX checkout hash=52ebae8 自癒判定）。
```
