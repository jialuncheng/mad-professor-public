# PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC · tasks

> 依據 plan：`.claude-logs/baton/2026-06-10_PIPE-SYNC-2_resume路落地經驗回灌母plan與SPEC_plan_v1.md`（§99.2 v1.2、U1-U14、§9 六 OQ 全結清）
> 工作流類別：**DOC-Refactor**（零業務代碼；驗收＝§8.1 grep/ls 物理自檢；§7.2 整合測試依 plan §8.3 + Q4 顯式豁免）
> 版控先例（git show 195e12b 考證）：**baton 兩真理源本體不入版控**（`baton/*` gitignored）、commit 僅入 archive/ `.bak` 改前快照作審計；**sop/ 九檔 + archive/ 皆 tracked**、正常 git add。

---

## §0 改版規則
- 改版觸發：§8 拆分或 §6 驗收變動 → 改章節 + §99.2 Revision
- plan 續留 baton、唯 C4 Checkout 一次性歸檔

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 | —（純就地補註；.bak 為審計副本非交付物）|
| **修改檔案** | 6 | 母 plan v10（U1/U2/U3母句/U8母句/U5指標·C1）/ PIPE-SPEC（U3-U10·C2）/ `sop/model_recommendations.md`（U11·C3）/ `sop/google_latest_models_guide.md`（U12·C3）/ `sop/2026-05-21_doc_type_新增手冊_三軸融合_v3.md`（U13 banner·C3）/ `sop/2026-05-27_mineru_SOP_手冊.md`（U14·C3）|
| **檔案搬移** | 2 | doc_type 手冊 v1 + v2 → `archive/`（U13、sop 僅留 v3）|
| **狀態更新** | 2 | TODO.md / prompts/INDEX.md |
| **Commits** | 4 | C1（母 plan）→ C2（SPEC）→ C3（sop 四檔）→ C4（Checkout）|
| **baton 歸檔** | 1 次 | C4 一次性 mv（plan + tasks + C1-C3 執行報告 → plans//tasks//executions/）+ git add |

---

## §1 TL;DR（概要）

Resume 路落地經驗回灌兩份 PIPE 真理源 + sop 連帶修正，4 commit：

- **C1 — 母 plan v10 就地補註（消矛盾與 stale）**：U1 resume Bypass 雙處 / U2 §8.5 RAG-ASYNC·PIPE-RESUME 狀態自癒 / U3 母 plan 句 / U8 U3 措辭 / U5 PIPE-VISUAL 條目尾指標。
- **C2 — PIPE-SPEC 就地補註（凍結缺口規格）**：U3 key 契約 / U4 zh 路 / U5 §1.3.1 Vision 共用小節 / U6 樣例 -001 / U7 rag_tree 歸屬 / U8 resume 行註 / U9 並行句 / U10 還原三件套。
- **C3 — sop 四檔修正與歸檔（配置權威去誤導）**：U11 model_recommendations 🔴 / U12 guide 勘誤 banner / U13 doc_type v3 banner + v1/v2 mv archive / U14 mineru RELEASE_ON_UPLOAD 句。
- **C4 — Checkout 收官（Conformance 與歸檔）**。

---

## §2 現況

plan §3.1 已列全量 grep 證據（行號以 2026-06-10 為準）：母 plan L71/L257 Bypass 矛盾、L267 RAG-ASYNC ⬜、L40 Tiles 措辭；SPEC L65/§1.4.1 key 模糊措辭、L146 embedding-2 樣例、L153 tree_json 無歸屬、zh/Vision/並行/還原 0 命中；sop 四檔 stale 證據；templates/ 與 database/logging/CACHE SOP 查無需更新。

## §3 觀察問題

對齊 plan §2：1 雙文件矛盾（U1）+ 1 狀態 stale（U2）+ 4 規格缺口（U3/U4/U5/U7）+ 3 樣例措辭（U6/U8/U9-U10 註記）+ 4 sop stale（U11-U14）。不修則第 2-5 路照 spec 實作重蹈 HOTFIX-1/2/3 與 MODEL-11 的坑。

## §4 設計方案

### §4.1 C1 — 母 plan v10 就地補註（消矛盾與 stale）
就地編輯 `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`、`<!-- === [PIPE-SYNC-2 C1 START/END] === -->` 包裹各處、§99.2 加補註⁶、不改檔名不 bump（Q1）。

### §4.2 C2 — PIPE-SPEC 就地補註（凍結缺口規格）
就地編輯 `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`、`<!-- === [PIPE-SYNC-2 C2 START/END] === -->` 包裹、§99.2 加 v6。U3 措辭逐字對齊 WORKFLOW_SOP §7.1 worked example（plan §4 凍結、防二次 drift）。

### §4.3 C3 — sop 四檔修正與歸檔（配置權威去誤導）
四檔各自 `<!-- === [PIPE-SYNC-2 C3] === -->`（或 md 註解行）標記 + 各檔 §99.2/版本註 Revision；doc_type v1/v2 `mv` → `archive/`（皆 tracked、git add 捕捉 rename）。

### §4.4 C4 — Checkout 收官
Conformance（plan §2 U1-U14 / §8.1 驗證 1-14 / §6 不可動 / 提示詞稽核 / msg 完整 / **§7.2 豁免顯式聲明**〔plan §8.3+Q4〕）→ baton 一次性歸檔 + TODO 結案 + hash 自癒。

## §5 風險

對齊 plan §5：凍結合約語意（只補註不改欄位結構、HTML 包裹可逐處 revert）/ sop 已入版控 ship 即生效（banner 式不刪舊文）/ U13 歸檔斷鏈（grep 證僅 framework 字樣提及、非鎖版本路徑）/ baton 兩檔不入版控（先例：.bak 入庫作審計、本體留 baton）。

## §6 測試計畫（逐 Commit；對齊 plan §8.1 1-14 條）

### §6.1 C1 驗收（母 plan）
1. `grep -n '100% Bypass' 母plan` → **resume 兩處（原 L71/L257）已改「逐 heading section 翻譯 + 退化 fallback」；slides 兩處（原 L70/L258）原樣保留**（Q6）。
2. `grep -n 'RAG-ASYNC.*待建立' 母plan` → 無命中；`grep -n 'rag_indexer' 母plan` → §8.5 產出欄命中。
3. `grep -c '原文標題 path' 母plan` → ≥1（U3 母 plan 句）。
4. `grep -n '產生方式\|opt-out' 母plan` → U3 段命中（U8）。
5. `grep -n '§1.3.1' 母plan` → §8.5 PIPE-VISUAL 條目尾指標命中（U5）。
6. `grep -c 'PIPE-SYNC-2 C1 START' == END`；§99.2 補註⁶ 存在；`wc -l` 增量合理。

### §6.2 C2 驗收（SPEC）
1. `grep -c '原文標題 path' SPEC` → ≥2（§1.1② + §1.4.1）；與 WORKFLOW_SOP §7.1 worked example 三欄逐字對照（人工）。
2. `grep -n 'zh 來源\|source_lang' SPEC` → P3 章命中（U4）。
3. `grep -n '§1.3.1\|LLM_VISION_TEMPERATURE\|忠實轉錄' SPEC` → Vision 小節三原則命中（U5）。
4. `grep -n 'gemini-embedding-001' SPEC` → 有；`grep -c 'gemini-embedding-2' SPEC` → 0（U6）。
5. `grep -n 'build_rag_tree\|key_map' SPEC` → §1.4.1 命中（U7）。
6. `grep -n 'opt-out' SPEC`（U8 resume 行）/ `grep -n '受限並行' SPEC`（U9）/ `grep -n 'meta header\|遞迴深度' SPEC`（U10）→ 各命中。
7. `grep -c 'PIPE-SYNC-2 C2 START' == END`；`grep -c 'RAG-ASYNC C1 START' SPEC` 數量不變（不動既有包裹區）；§99.2 v6。

### §6.3 C3 驗收（sop 四檔）
1. U11：`grep -n 'gemini-embedding-001' sop/model_recommendations.md` → 建議值欄命中；`grep -n 'extra_info.*已廢\|B 軌已廢' 同檔` → 命中。
2. U12：`grep -n '勘誤\|MODEL-11' sop/google_latest_models_guide.md` → 頂部 banner 命中；內文 `wc -l` 不減。
3. U13：`grep -n 'A 軌\|PipelineFactory' sop/..._v3.md` → banner 命中；`ls .claude-logs/sop/ | grep -c doc_type` → 1（僅 v3）；`ls .claude-logs/archive/ | grep -c 'doc_type_新增手冊'`（不含既有 .bak）→ ≥2。
4. U14：`grep -n 'RELEASE_ON_UPLOAD' sop/2026-05-27_mineru_SOP_手冊.md` → §6 段命中。
5. 四檔各 Revision 註 + 標記平衡。

### §6.4 C4 驗收（Checkout）
plan §2 U1-U14 逐項紅綠燈 + §6.1-§6.3 grep 全貼 + 不可動 + 提示詞稽核（Tasks/C1-C3 run/Check）+ msg 完整 + §7.2 豁免聲明；`ls baton/ | grep PIPE-SYNC-2` → 0 殘留（兩真理源 `2026-06-01_PIPE*` 長駐 baton、不屬本任務歸檔物）。

## §7 不可動清單（對齊 plan §6）

- [ ] 任何業務代碼（.py / static/）。
- [ ] SPEC 四凍結合約**欄位結構**（只補註與樣例字面）。
- [ ] 既同步 HTML 包裹區（RAG-ASYNC C1 / v9 C1）——不重寫不重複。
- [ ] 母 plan §8.5 其餘條目規格句；**slides 路 Bypass 雙處原樣**（Q6）。
- [ ] templates/ 全部；sop/ 之 database/logging/CACHE 三檔。
- [ ] U12/U13 **內文**（僅 banner、嚴禁重寫）。
- [ ] repo `docs/HOW_TO_ADD_DOC_TYPE.md`（範疇外）。
- [ ] baton/ 其他檔案（TRANSLATE-BOOK/INFRA-3/INFRA-4/CHAT-STRUCT-1/QUEUE-1/工作筆記/YuLun_Wu_CV_chat.md 等）。

## §8 推薦 Commit 拆分

### C1 — Master Plan Sync（母 plan 就地補註·消矛盾與 stale）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（就地、不入版控）+ 改前 `.bak` → archive/（入版控、審計）|
| **安全性** | 🟢 高 — 純文件補註；HTML 包裹逐處可識；不碰 slides 規格句 |
| **可逆性** | 🟢 高 — 還原 .bak 或逐包裹區 revert |
| **驗收 grep 條件** | §6.1 全六條 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `cp 母plan → archive/2026-06-11_PIPE-SYNC-2_C1_PIPE_plan_v10.md.bak`。② **U1**：L71 與 L257 兩處「P3 100% Bypass」→「P3 逐 heading section 翻譯 + 退化 fallback」（slides L70/L258 不動）。③ **U2**：§8.5 RAG-ASYNC 條目「⬜ 待建立」→「✅ 已落地（C1-C7 + HOTFIX-1/2/3）」+ 產出欄補 `processor/rag_indexer.py`／P2 六步 `section_summaries`／`ctx.rag_sections` 旁路／`final_{paper}_rag_tree.json`；PIPE-RESUME 條目狀態欄註「四 Phase 已落地（C1-C7+v9+hotfix 群）、Golden Diff 待 baron 重捕」。④ **U3 母句**：§U4（L48）「key 對位巢狀樹」處補「key＝**原文標題 path**、P2 產/P3 帶/P4 取同基準（詳 SPEC §1.4.1）」。⑤ **U8**：§U3（L40）「絕對均勻」句補「均勻者為**交付形狀**；Tiles 產生方式各路自選（resume opt-out TextTiling 先例、通用化歸 INFRA-3）」。⑥ **U5 指標**：§8.5 PIPE-VISUAL 條目尾加「P1 Vision 解析引用 SPEC §1.3.1 共用規格」。⑦ 全部 `<!-- === [PIPE-SYNC-2 C1 START/END] === -->` 包裹 + §99.2 補註⁶ |

### C2 — SPEC Sync（PIPE-SPEC 就地補註·凍結缺口規格）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/2026-06-01_PIPE-SPEC_..._specification.md`（就地、不入版控）+ 改前 `.bak` → archive/ |
| **安全性** | 🟢 高 — 補註/樣例字面、零合約欄位結構變動 |
| **可逆性** | 🟢 高 — 同 C1 |
| **驗收 grep 條件** | §6.2 全七條 |
| **依賴關係** | 建議 C1 後（同主題連續、無硬依賴）|
| **具體實作細節** | ① `.bak` → archive/。② **U3**：§1.1②（L65）與 §1.4.1 補凍結三句——key＝原文標題 path；P2 產（`_collect_summary_targets`）/P3 帶（slot `key`→`summary_key`）/P4 取（`_walk` 首選 `summary_key`）同基準；譯後 title 僅顯示不作 key（逐字對齊 WORKFLOW_SOP §7.1）。③ **U4**：P3 章（§1.2.3.1 後）補「zh 來源（source_lang=zh）：跳過翻譯（原文≡譯文）、仍建 per-section `rag_sections`（summary_key=原文 path、與 P2/P4 天然對齊）、無 section 退單一容器兜底——五路通用 edge path」。④ **U5**：§1.3 表附近新增「**§1.3.1 Vision 解析共用規格（resume/slides 共用）**」三原則：忠實轉錄鐵律（嚴禁重組/摘要/補完 + 噪聲排除原則）/ `LLM_VISION_TEMPERATURE=0` / 非確定性殘餘註記（golden 重捕清快取+容差）；明文「輸出 Schema 級約束屬 PIPE-VISUAL 自定」。⑤ **U6**：L146 樣例 `"gemini-embedding-2"` → `"gemini-embedding-001"` + 行尾註（MODEL-11、向量不可混庫）。⑥ **U7**：§1.4.1 補「rag_tree.json 由 B 軌 `rag_indexer.build_rag_tree` 自建（key_map key＝chunk Header＝node_key → `/sections/{i}/content/0` path、節點帶 translated_content/translated_title）」。⑦ **U8**：§1.3 resume 行 P1 欄補「（opt-out TextTiling、processed JSON 直當 tiles）」。⑧ **U9**：§1.2.3.1 末補「編排得受限並行（ThreadPool、保序 slot index、限流靠共用 `LLMClient._api_semaphore`、單 unit 失敗退原文——RESUME-PERF-1 先例）」。⑨ **U10**：§1.3 resume 行尾註「還原細則：meta header 渲染/標題層級＝遞迴深度/段落 `\n\n` 正規化」。⑩ `<!-- === [PIPE-SYNC-2 C2 START/END] === -->` 包裹 + §99.2 v6 |

### C3 — SOP Fix & Archive（sop 四檔修正與歸檔·配置權威去誤導）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `sop/model_recommendations.md` / `sop/google_latest_models_guide.md` / `sop/2026-05-21_doc_type_新增手冊_三軸融合_v3.md` / `sop/2026-05-27_mineru_SOP_手冊.md`（皆 tracked、正常 git add）+ v1/v2 兩檔 mv → archive/（rename）+ 四檔改前 .bak |
| **安全性** | 🟢 高 — banner/行級更正、不重寫內文；歸檔保實體 |
| **可逆性** | 🟢 高 — .bak + mv 可逆 |
| **驗收 grep 條件** | §6.3 全五條 |
| **依賴關係** | 無前置（與 C1/C2 獨立、可任意序）|
| **具體實作細節** | ① 四檔 `.bak` → archive/。② **U11**：`model_recommendations.md` L20 EMBEDDING_MODEL 行建議值 `gemini-embedding-2`→`gemini-embedding-001` + 理由（多模態交錯/`t_contents` 假批次/無 task_type→召回非對稱喪失；MODEL-11 探針鋼證）；L19 EXTRA_INFO 行尾註「extra_info stage B 軌已廢（母 plan U6）、僅 A 軌影子期沿用」。③ **U12**：`google_latest_models_guide.md` 頂部勘誤 banner（embedding-2 真批次描述與 MODEL-11 實測矛盾；本專案文字 embedding 一律 -001；多模態另議）、內文不動。④ **U13**：v3 頂部適用範圍 banner（A 軌 11-stage 專用、Flip 前有效；B 軌＝`PipelineFactory.register`+`DocumentStrategy` 四方法、見 PIPE-SPEC §1.3；全面改寫屬 Flip 後）+ `mv sop/..._三軸融合.md sop/..._三軸融合_v2.md → .claude-logs/archive/`。⑤ **U14**：`mineru_SOP` §6 補「LAZYLOAD-MULTI-1 C4 起、上傳時 app 端自動全清向量快取+gc 騰 RAM 給同 VM MinerU（`RELEASE_ON_UPLOAD`=on、env 可關、活躍 SSE 豁免）」。⑥ 各檔 Revision 註 + `[PIPE-SYNC-2 C3]` 標記 |

### C4 — Checkout（收官歸檔·Conformance 與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 無業務碼；Conformance + baton 一次性歸檔 + TODO 結案 + hash 自癒 |
| **安全性** | 🟢 高 — 純文件 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.4（U1-U14 紅綠燈 + 全 grep 真實輸出 + §7.2 豁免聲明 + baton 0 殘留）|
| **依賴關係** | 前置 C1-C3 全 commit |
| **具體實作細節** | Conformance 全綠 → `mv baton/2026-06-10_PIPE-SYNC-2_*_plan_v1.md → plans/` + `mv baton/2026-06-11_PIPE-SYNC-2_*_tasks.md → tasks/` + `mv baton/2026-06-1*_PIPE-SYNC-2_C[1-3]_執行.md → executions/` + git add；C4 報告直寫 executions/；TODO 完成表 + active 移除 + 索引 ✅ + 全量 hash 自癒；msg → /tmp。**注意：兩真理源（2026-06-01_PIPE*）長駐 baton、不歸檔不 git add（本體不入版控、.bak 已於 C1/C2 入庫作審計＝195e12b 先例）** |

> **各 Run 執行報告**：C1-C3 各產 `_執行.md`（template_execution、暫存 baton、嚴禁 mv/git add）；C4 一次性歸檔。
> **git add 通則**（各 C §8 baron 命令）：C1/C2＝.bak + TODO + prompts（真理源本體不可 add）；C3＝四 sop 檔 + archive/ renames + .bak + TODO + prompts。

## §9 Open Questions

plan §9 六題全結清（v1.2）；tasks 階段無新增 OQ。

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | PIPE-SYNC-2 commit 拆分與驗收清單 |
| 權威源 | 本檔 §8（依 plan v1〔v1.2〕U1-U14 + Q1-Q6 定案）|
| 引用方 | C1-C4 Run/Checkout 執行報告 |
| 不可動唯一源 | §7（對齊 plan §6）|
| 改版觸發 | §8/§6 變動 |

### §99.2 Revision 歷程
- v1 (2026-06-11)：初稿——4 commit（C1 母 plan / C2 SPEC / C3 sop 四檔+歸檔 / C4 Checkout）+ §0.5 盤點 + §6 逐 commit 驗收（對齊 plan §8.1 1-14）+ §8 六維度表；**版控先例考證**（195e12b：baton 真理源本體不入版控、.bak 入 archive 作審計；sop/archive 皆 tracked）寫入 git add 通則
