# Mad Professor — TODO（最後更新 2026-06-02，GOLDEN-BASELINE Check 收官）

> 本文件為 **Single Source of Truth**（依 `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §2.1）。
> **任何規劃 / 執行 / hotfix 前必先 view 框架文件**：`.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`
> 對應 template 位於 `.claude-logs/templates/template_plan.md` / `template_execution.md` / `template_hotfix.md`
>
> **狀態 Emoji**（依框架 §2.2）：⬜ 未開始 / 🔵 plan 中 / 🟡 WIP / ✅ done
> **任務生命週期**（依框架 §2.5）：done 後**必須**從下方 active 列表移除、改寫入頂部 ✅ 已完成表格 + 同步索引。

---

## ✅ 已完成

### DOC-Refactor CHECKOUT-GUARD 收官 git-add 白名單鐵律（FE-PERF-1 混檔→立流程守衛·治廣義 git add 掃入他案 + checkout 漏產報告）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Rule Authoring：`WORKFLOW_SOP §3` 新增兩鐵律〔**收官 git-add 白名單鐵律**〔逐檔顯式·嚴禁 `git add .`/`-A`/`<目錄>`·commit 前 `git diff --cached --name-only` 自檢 staged＝宣告清單·多/少一檔即停·反例錨 FE-PERF-1 混檔〕+ **checkout 執行報告鐵律**〔必產保存 `executions/…_checkout_執行.md` 含 Conformance 五維度+staged 自檢輸出〕〕+ §99.2 v6·五類定義/文書類別/命名/§7 零改 | `81179d8` |
| C2 | Template Propagation：三模板落地——`template_prompt_for_run §8`+`template_execution §8` 加「逐檔·禁廣義 add」+ `template_prompt_for_check` 收官新增「第五步 commit 前 staged 自檢」+「第六步 mandate `_checkout_執行.md`」〔既有 Conformance 五維度/三防線/L126 結構零改·3 .bak〕 | `dbd6d24` |
| checkout | 成果收官：Conformance 五維度全綠〔目標規格 U1-U6 實檔複驗 / tasks §6 grep / 不可動〔零 .py/static·WORKFLOW_SOP §1/§2/§4-7 未動·三模板既有結構未動〕 / 提示詞 plan+Tasks+C1+C2+Check 五份逐檔入 git / msg 草稿〕+ §7.2 純 DOC 顯式豁免 + **首次 dogfood checkout 執行報告鐵律**〔產 `executions/…_checkout_執行.md` 含 staged 自檢輸出·排除 RESCUE-1 未追蹤檔〕+ baton 一次性歸檔 + hash 自癒 | `eb2b381` |

> **修法依據**：`.claude-logs/plans/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`（v2、§9 六 OQ + 範圍補強〔納 run 模板〕+ Q6〔checkout 報告〕全 🟢 定案）
> **動因**：FE-PERF-1 收官期 WORKFLOW-5 未追蹤歸檔被廣義 `git add` 掃入 C1 commit（跨任務混檔）→ 賴 `pre-fe-rebuild` 備份後歷史重寫方淨化；根因＝WORKFLOW_SOP §3 與三模板 §8 未禁廣義 add、無 commit 前 staged 自檢；並附帶治「checkout 輪有時未產執行報告」（template_execution L126 假設存在、template_prompt_for_check 未 mandate 之落差）。
> **§2.5 三候選**：純文件鐵律 + 自檢（選定）vs git pre-commit hook enforcement（否決·列 backlog·再犯再升級）vs 放任（否決·即現狀）。
> **實證流程巧合**：本任務 Check 階段 C2 一度未 commit 即下 checkout → 新鐵律「commit 前 staged 自檢/所有 commit ship 完畢」當場攔下、避免 C2 被 checkout 吞入（dogfood 生效鐵證）。
> **⚠️ baron 運維（非 commit）**：收官 git-add 白名單鐵律 + checkout 執行報告鐵律自即日對**所有工作流**生效；pre-commit hook 強制化列 backlog（plan §9 Q2）。

### DOC-Refactor FE-PERF-1 前端效能與渲染 SOP 建立（Osmani 瀏覽器渲染稽核→立 sop/ 手冊·補 WORKFLOW_SOP FE 必讀 SOP 缺口）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | SOP Authoring：新建 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`〔§2 效能 7 條紅線〔規則+`static/index.html` 反例行號+改法：串流收尾重排/head script defer+自託管/transform 動畫/rAF+passive/字型 preload/Gzip+強快取/KaTeX code-split〕+ §3 渲染正確性陷阱 6 類〔hotfix 溯源 RAG-12-HOTFIX-1/RAG-9/PIPE-SLIDES-HOTFIX-3d/RAG-8/PARA-HOTFIX-1/RAG-10/FE-RHYTHM-UNIFY〕+ §4 驗收檢查表〔對接 template_execution §自評〕+ §5 交叉引用 design/docs+WORKFLOW_SOP §7 + §99.1 重複防護·120 行〕 | `3ec7b3f` |
| C2 | Workflow Backfill：`ref/WORKFLOW_SOP.md` §1.1 FE-Refactor / §1.4 FE-Hotfix「必讀 SOP」由「—」→ 手冊路徑 + §99.2 v5〔五類定義本體/命名/§7 接縫契約零改·§1.3 DOC 列刻意保留「—」·.bak 備份〕 | `4fb2248` |
| checkout | 成果收官：Conformance 五維度全綠〔目標規格 U1-U7 / tasks §6 grep 實檔複驗 / 不可動〔零 .py/static·design/docs 未動·五類定義未動〕 / 提示詞 plan+Tasks+C1+C2+checkout 五份稽核入 git / msg 草稿〕+ §7.2 純 DOC 顯式豁免〔無 code handoff〕+ baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1·C2 執行報告→executions/〕+ TODO 結案 + hash 自癒 | `c00604b` |

> **修法依據**：`.claude-logs/plans/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_plan_v1.md`（v2、§9 六 OQ 全 🟢 定案）
> **動因**：以 Osmani《How modern browsers work》為標準稽核前端（`baton/frontend_browser_standards_audit.md` 8 findings，已補串流 O(n²) 重排）後，補齊治理不對稱缺口——後端有 logging/database 兩份強制 SOP、前端零；並收斂散落各 hotfix 的渲染正確性教訓為可打勾準則。
> **§2.5 三候選**：sop/（選定·workflow-gated 不污染 @path）vs ref/ auto-load（否決）vs design/docs（否決·職責混淆）。
> **§7.2 豁免**：純 DOC-Refactor、無 code handoff（同 WORKFLOW-3/4/5 立規者先例）。
> **commit 邊界（已淨化）**：歷史經 `pre-fe-rebuild` 備份後重寫為乾淨邊界——WORKFLOW-5 歸檔獨立於 C7 `12564be`、FE-PERF-1 C1 `3ec7b3f` 僅含 SOP 手冊、C2 `4fb2248` 僅含 WORKFLOW_SOP 回填；先前「C1 夾帶 WORKFLOW-5 歸檔」之混檔已消除。
> **⚠️ baron 手動 commit（非 Claude）**：checkout `git add` prompts〔Tasks/C1/C2/checkout〕+ TODO + 歸檔文件 → `git commit -F /tmp/FE-PERF-1_checkout_msg.txt`。

### DOC-Refactor WORKFLOW-5 ClawVM 混合治理 Hook 落地（純文件約束→真實 Hook harness enforcement·Baton 3-Phase·Fidelity Floor）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | SessionEnd Dry-Run（阻擋能力實測·gate）：權威裁定 SessionEnd **不能 block**→DIRTY-RESET 走 Observable Fault〔plan §9 Q2 路徑 B〕+ script-level 真測;**附帶修正**：blocking 機制＝exit 0+JSON〔permissionDecision:deny / decision:block〕非 exit 2、環境無 jq→腳本用 python3;throwaway probe 零永久腳本 | `6fd2ce2` |
| C2 | Baton 3-Phase 形式化（baton/README §2）：Staging→Deterministic Validation〔Provenance/Schema/Non-destructive/Scope 四維自檢〕→Scoped Commit + 非破壞性寫入核心鐵律〔唯一不可繞過保證〕+ 對帳 WORKFLOW_SOP §3「Run 嚴禁 mv、Checkout 才歸檔」一次性 mv;§99.2 v2 | `306797a` |
| C3 | Template Fidelity Floor（template_file_governance §99.1）：新增 Scope〔session-private/project-shared〕/ Provenance〔來源+hash〕/ Fidelity Floor〔降級底線·機器可讀 `fidelity_floor:` 格式·四 Level 殘留鏈 Full→Compressed→Structured→Pointer〕三維度 + Cost-Aware no-degrade〔grep 證據/實測輸出/commit hash 優先不降級〕;§99.2 v2 | `2c14d4a` |
| C4 | 截斷守衛腳本（`tools/pre_tool_guard.sh`·PreToolUse）：python3 解析 stdin〔無 jq〕+ exit 0+JSON permissionDecision:deny〔非 exit 2〕+ 保護 plans/sop/ref/CLAUDE.md/TODO.md + >50%且>50行截斷 + `// BYPASS_TRUNCATION_GUARD` 減速帶 + fail-open;`test_hook_guards.sh` truncation 8/8 | `c107bfd` |
| C5 | DIRTY-RESET 守衛腳本（`tools/dirty_reset_guard.sh`·SessionEnd·Observable Fault Only）：觸發＝baton 仍有某任務暫存檔且該任務 TODO Checkout 子項已 ✅〔非「baton 非空」避跨 session 誤報〕·stderr 警告+exit 0·python3·fail-open;test dirty_reset 4/4 | `6ab46b9` |
| C6 | Settings 掛載與部署 SOP（Q1 跨環境同步）：`tools/settings.hooks.sample.json`〔PreToolUse:Write\|Edit→pre_tool_guard / SessionEnd→dirty_reset·$CLAUDE_PROJECT_DIR〕+ baton/README §3 跨環境部署 SOP〔Q1 方案 a：腳本版控 tools/ + 專案級 .claude/settings.json 指針·作用域隔離·強度分級誠實標註〕;§99.2 v3 | `37f3ded` |
| C7 | Checkout 收官：Conformance 五維度全綠〔目標規格 plan §2 三項 / tasks §6.1–§6.6 全綠〔test_hook_guards all = truncation 8 + dirty_reset 4 + hook 真實整合對 ref/WORKFLOW_SOP.md 截斷實測 deny〕 / 不可動全 ✅〔零業務碼/前端〕 / 提示詞 Tasks+C1–C6+Check 入 git〔補 git add 漏掉的 Tasks 提示詞〕 / msg §8〕+ §7.2 純治理+hook 無 handoff 顯式豁免 + baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1–C7 報告→executions/〕+ TODO 結案 + hash 自癒 | `12564be` |

> **修法依據**：`.claude-logs/plans/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_plan.md`（v5、§9 兩 OQ：Q1 跨環境同步採 (a) 腳本版控 / Q2 SessionEnd 動工前實測）
> **動因**：ClawVM 論文（`.claude-logs/baton/2604.10352v1.pdf`）——承認「純文件約束＝discretion」結構性不足，**跨出純文件邊界**用真實 Claude Code Hook（harness enforcement）+ Baton 3-Phase 形式化 + Template Fidelity Floor，治本失憶（DIRTY-RESET）與破壞性截斷（DESTRUCTIVE-WRITE）。
> **C1 gate 連鎖修正**：SessionEnd 不能 block〔權威文件〕→ DIRTY-RESET 降級 Observable Fault；blocking 機制 exit 0+JSON 非 exit 2；環境無 jq→python3——三點回灌 C4/C5 落地。
> **三道防線威脅模型（plan §1 誠實標註）**：Baton 3-Phase＝**不可繞過**〔harness 確定性 validation〕/ 截斷守衛＝防誤觸〔agent 可 sentinel 繞過〕/ DIRTY-RESET＝僅可觀測〔SessionEnd 不能 block〕。
> **§7.2 豁免**：純 DOC-Refactor + 治理 hook 腳本、無業務 Phase handoff（同 WORKFLOW-3/4 立規者先例）。
> **⚠️ baron 運維（非 commit）**：① 各環境一次性將 `settings.hooks.sample.json` 的 hooks 區塊合併進**專案級** `.claude/settings.json`（`.claude/` 被 gitignore、需手動）→ 重啟 session 生效（hook 啟動載入）;② 部署後 `bash .claude-logs/tools/test_hook_guards.sh all` 驗腳本健康;③ 跨環境部署 SOP 見 `baton/README §3`。

### BE-Hotfix PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1 | `pipelines/section_engine.py` 新增四純函式〔`detect_zh_tw`〔二元繁中：有假名/諺文/簡體專有字/ASCII 主導/漢字太少→非繁〕+ `classify_source_lang`〔繁→'zh'、簡→**'hans'**、ja/ko/en;**簡體嚴禁 zh\* 字串**·鎖一〕+ `sample_body_text`〔tiles 文字節點樣本·跳前段封面 0.15·短文兜底·鎖三〕+ `strip_title_echo`〔_title_sim 範式模糊比對·剝首個 ≈title 標題行+byline/日期·cap 3·找不到不誤剝〕〕;`litedoc_pipeline.py` **F2 P1** 改 `classify_source_lang(sample_body_text(tiles))`〔鎖二共用、一次解 P3 is_zh + P2 section_summaries 雙 gate〕+ **F3 P3 雙剝**〔① pre-strip full_text 原文層·en 全模式+zh whole/is_zh exact / ② post-strip zh_text 補 section 模式·同 slot 譯文 exact·rag_sections 早於定案不受影響〕;扉頁保留〔OQ-b〕;`# === [PIPE-LITEDOC-HOTFIX-1 START/END] ===` 包裹 + 2 .bak;18 新測試〔detect/classify〔含鎖一 not startswith zh〕/sample 跳封面/strip/P3 雙剝 whole+section/P1 日文+簡體接線〕、litedoc+section_engine 64 passed、全套件 **704 passed**〔基線 686+18、唯一 fail＝既有 LOG_FORMAT env flake〕;SOP logging〔新增純函式無 logger·既有 warning 皆 exc_info=True〕+database〔無命中〕合規 | `cbc512a` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-19_PIPE-LITEDOC-HOTFIX-1_hotfix.md`
> **動因**：PIPE-LITEDOC 落地後 baron QA 三實件（LLM 知識庫 / 環義 Giro / 大谷 NHK + book 封面 I and Thou）暴露雙缺陷——① 標題/Meta 重複〔body 自身標題 H1 與 P3 HTML 扉頁物理共存、litedoc 無去回聲〕② 日文/簡體未翻譯〔`_detect_source_lang` 只數共用漢字區→日文誤判 zh→P3+P2 雙 gate 跳譯;簡體亦誤 bypass 不轉繁〕。
> **三鎖**：鎖一（簡體不給 `zh*` 字串，四處 `startswith("zh")` gate〔litedoc/section_engine/resume/slide〕零改不復活）/ 鎖二（偵測器放 section_engine 共用，book/academic 同享）/ 鎖三（取 tiles 內文樣本不取封面，解 I and Thou 封面無語境）。
> **設計演進**：F3 由 v1 單剝 full_text（section 模式漏洞）→ baron review 抓出 → 改 pre+post 雙剝（每模式 exact、消 whole 模式譯文發散風險）。
> **blast radius**：問題一純閱讀視圖、RAG 不受污染（扉頁不進 chunk）;問題二連帶 P2 節點摘要、源點 P1 一改解雙 gate。
> **§7.2**：BE-Hotfix 純渲染/偵測層、無新跨 Phase handoff（沿用既有 section_engine key 契約、PIPE-LITEDOC C7 已驗 key-changing）。
> **⚠️ baron 運維（非 commit）**：① 影子重傳大谷 NHK（日文）→ 扉頁/正文/節點摘要皆繁中、`source_lang=ja`;② 簡體樣本→轉繁;③ LLM 知識庫/Giro→標題僅扉頁一處、body 無重複 H1+byline;④ 真繁中件仍 bypass;⑤ B 軌走影子 E2E + 改善豁免、不需 A 軌 golden 重捕（SPEC §1.3.1 / HOTFIX-6 口徑）。

### DOC-Refactor PIPE-SYNC-4 litedoc 與 section_engine 落地回灌母 plan 與 SPEC（PIPE-SECTION-BASE + PIPE-LITEDOC 落地後真理源回灌）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | master plan v10 回灌（就地補註 D1-D4：L72 LiteDoc 排除 technical〔歸深結構家族 academic/book·A 軌證非 FLAT/非 SHORT/有 abstract〕+ §8.5 表 PIPE-LITEDOC ⬜→✅〔C1-C8 hash b1012bc…ff16271·實際先於 academic〕+ §U8 三大→共用真理源**家族**〔roster 補 MetaNormalizer 第 4 / section_engine 第 5、契約見 SPEC §1.2.4/§1.2.5〕+ 絞殺順序實況註 + §99.2 v6;就地補註只增不刪、零業務代碼）| `8c49be8` |
| C2 | PIPE-SPEC 回灌（就地補註 D5-D8.1：**§1.2.5 section_engine 契約章**〔三簇介面+四鐵律〔零 doc_type·接縫 key=原文標題 path·Zero Schema Coupling·restore 不產 rag 副作用〕+consumer〕+ **§1.2.4 MetaNormalizer 契約章**〔normalize_fields 三路分流 BS1/Q9/BS4 + MetaField/MetaFieldAlias schema + LLM 交易外/temp=0 + 為 INFRA-4 鋪規格〕+ §1.1.1 litedoc 旁路登記〔date/url/publisher/translated_title〕+ §1.2/§0 三大→共用真理源家族 + §99.2 v8;**D8.1 §1.3 L140〔news/web/未知〕+ §3.3 15k + §2 ≥10 + 四凍結合約結構未動**;SPEC baton 就地不版控、.bak→archive 審計）| `89e6910` |
| C3 | HOW_TO_ADD B 軌範式（docs/HOW_TO_ADD_DOC_TYPE.md 補頂部 A/B banner + §1.4〔1.4.1 A/B 機制對比表·🚫 嚴禁 pipeline_core.py 硬分支 / 1.4.2 B 軌五步範式〔@register+__init__ import 觸發 + 四 Phase 消費真理源家族 + raw_metadata 旁路 + 接縫 key 同基準 + §7.2 key-changing 整合〕/ 1.4.3 U2.1 DocAnalyzer 安全映射〔扁平短文避 fallback academic·technical 歸深結構〕〕;A 軌既有 §2-§7 章不動、零業務代碼）| `a0ccb0e` |
| C4 | Checkout 收官：Conformance 三維度全綠〔目標規格 D1-D9〔含 D5b〕跨 C1-C3 全覆蓋 / tasks §6 grep〔C1 master plan·C2 SPEC·C3 HOW_TO_ADD 重跑全綠·D8.1 守住〕+ pytest 686 passed〔唯一 fail＝既有 LOG_FORMAT env flake〕/ 不可動〔業務碼/測試/contracts.py 零碰·SPEC §1.3 L140 未動〕/ 提示詞 5 份稽核 / msg §8〕+ **§7.2 純 DOC 顯式豁免**〔無 code handoff〕+ baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1-C4 報告→executions/;SPEC 本體長駐 baton、.bak 已於 C2 入 archive〕+ TODO 結案 + hash 自癒 | `72bcb32` |

> **修法依據**：`.claude-logs/plans/2026-06-19_PIPE-SYNC-4_litedoc與section_engine落地回灌母plan與SPEC_plan_v1.md`（v3、§9 五 OQ 全 🟢 定案）
> **動因**：PIPE-SECTION-BASE（section_engine 共用真理源）+ PIPE-LITEDOC（第 3 路）落地後，master plan v10 / PIPE-SPEC drift——三大共用真理源漏 MetaNormalizer+section_engine、master plan technical 分歧、section_engine/MetaNormalizer 契約缺、litedoc 旁路未登記;HOW_TO_ADD 為 A 軌時代 doc。同 PIPE-SYNC-2/3 對 resume/slides 之回灌。
> **回灌三真理源**：① master plan v10〔D1 technical 排除·D2 LiteDoc ✅+順序·D3 三大→家族·D4 順序實況〕② PIPE-SPEC〔D5 section_engine §1.2.5·D5b MetaNormalizer §1.2.4·D6 litedoc 旁路·D7 家族·D8 v8·D8.1 不改項〕③ HOW_TO_ADD〔D9 B 軌範式+A/B 對比+U2.1 映射〕。
> **共用真理源家族定調**：原始三大（DomainNormalizer/GLOSSARY-CORE/Translator）+ 第 4 MetaNormalizer（META-NORM 飛輪）+ 第 5 section_engine（PIPE-SECTION-BASE）。
> **版控先例**：SPEC 本體長駐 baton 不版控、.bak→archive 作審計（PIPE-SYNC-2 195e12b）;master plan/HOW_TO_ADD tracked 正常入庫。
> **§7.2 豁免**：純 DOC-Refactor、3 真理源 .md、零業務代碼、無 Phase handoff（同 WORKFLOW-3/4 立規者先例）。
> **⚠️ 後續（非本案）**：academic/technical/book 路;slides 重複副本收編。

### BE-Refactor PIPE-LITEDOC LiteDocPipeline 策略管線（PIPE 縱向五路第 3 路·news/web/unknown·首個 section_engine 跨 consumer 驗證）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | section_engine HTML 扉頁 formatter（純加法 `render_meta_header_html`〔paper-header-meta div·zh 、/en , 分隔·byte 對齊 A 軌 md_restore:460-490·Zero Schema Coupling〕、嚴禁碰既有;既有 17+42 不退化、全套件 661）| `b1012bc` |
| C2 | LiteDoc 骨架與三 key 註冊（`@register('litedoc'/'news'/'web')` 三裝飾器 + 四 Phase strict stub + rag_char_threshold=10 + `__init__` import;分派 4 路測試、9 passed、670）| `18e47c1` |
| C3 | P1 MinerU 攝入與 metadata 旁路（PDFProcessor + 強制 md_cleaner + DocAnalyzer **U2.1 映射**〔news/web 原樣·其餘→'web' 防 fallback academic〕+ tiling + **B 軌原生 cover-prompt** 抽 title/authors/date/publisher/url〔**URL→publisher 解碼**〕+ venue 承接 publisher + raw_metadata 旁路;16 passed、677）| `3570476` |
| C4 | P2 六步（①全文摘要 ②normalize_to_lcc ③Glossary 級聯自癒 ④Translator DEEP_THINK + lcc→domain_name ⑤⑥ `section_engine.build_section_summaries`〔key=原文標題 path〕→ GlossaryReadySpec;LLM 全交易外;17 passed、678）| `f8940cd` |
| C5 | P3 size-gate 翻譯與 HTML 扉頁還原（**size-gate**〔<15k 一鍵 translate_whole·≥15k restore_sections_markdown〕+ heading 退化 fallback + **U5c translated_title 三路** + `render_meta_header_html` HTML 扉頁〔zh 譯題/en 原題〕+ collect_rag_sections + zh edge + translated_title 旁路傳 P4;22 passed、683）| `424ee93` |
| C6 | P4 Async RAG（呼共用 `rag_indexer.index(…, 'litedoc', …, title, translated_title)`·**門檻預設 ≥10**〔litedoc 不入 ≥3 tuple·**rag_indexer 零改**〕+ translated_title 讀 P3 旁路 + 四產物 + 異常拋出標 failed 不阻 reading_ready;24 passed、685）| `469f982` |
| C7 | 單元與接縫整合測試（**§7.2 P2→P3→P4 key-changing 整合**：`_KeyChangeTr` 真改 title、斷言 P2 section_summaries key 與 P3 rag_sections summary_key 譯後同基準=原文標題 path、P4 消費同份+下游 match·堵 RAG-ASYNC-HOTFIX-1;純測試、25 passed、686）| `ff16271` |
| C8 | Checkout 收官：5 維度 Conformance 全綠〔U1-U9+U2.1/U5b/U5c 跨 C1-C7 全覆蓋 / tasks §6 grep+pytest 686 / 不可動〔rag_indexer/contracts/其他策略/A 軌零碰〕/ 提示詞 10 份 / msg §8〕+ §7.2 不豁免達標〔C7 key-changing〕+ baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1-C8 報告→executions/〕+ TODO 結案 + hash 自癒 | `2a9b2e3` |

> **修法依據**：`.claude-logs/plans/2026-06-18_PIPE-LITEDOC_litedoc路策略管線_plan_v1.md`（v3、§9 七 OQ 全 🟢 定案）
> **動因**：PIPE 縱向五路第 3 路 litedoc（news/web/unknown）;PIPE-SECTION-BASE（第 4 共用真理源 section_engine）落地後、litedoc 為 resume 以外**首個 consumer**，驗證引擎泛化。
> **設計**：academic-lite——P1 MinerU 文字攝入（非 Vision）、P2-P4 全消費共用真理源（section_engine + DomainNormalizer/Glossary/Translator + rag_indexer）、**零造輪、rag_indexer 零改**。
> **§2.5 方案 A**：P1 metadata 採 B 軌原生 cover-prompt（不耦合即將絞殺的 A 軌 metadata_extractor）。
> **Q4 分歧（顯式聲明）**：technical 排除本路、歸深結構家族（academic/book）;與母 plan v10 L72「litedoc 含 technical」分歧、**待 PIPE-SYNC 回灌**。
> **Q7 銳化**：section_engine C1 純加法補 HTML 扉頁 formatter（update 本 plan 不另開、academic/book/technical 後續共用、消滅未來重造）。
> **⚠️ baron 運維（非 commit）**：`.env LLM_USE_META_NORM=true` 漸進開 + 影子上傳 news/web → 驗 HTML 扉頁 publisher/date、chunks ≥10、unknown fallback;與 A 軌 golden diff（改善豁免）。
> **⚠️ 後續（非本案）**：PIPE-SYNC-4 回灌母 plan（litedoc + technical 分歧 + section_engine formatter）;academic/technical/book 路;slides 重複副本收編。

### BE-Refactor PIPE-SECTION-BASE 共用 section 機制抽取（第 4 共用真理源·litedoc/academic/technical/book 先行）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | section_engine 骨架與摘要機制：新建 `pipelines/section_engine.py` 零 doc_type 耦合純函式引擎·摘要簇〔collect_summary_targets 吃任意子樹 U3.2 / node_content_text / parse_indexed / generate / translate / build_section_summaries·llm+prompt+model 注入〕、resume 摘要簇 5 私有 method 移除改 delegate;行為等價 resume 42 passed、全套件 640 基線、SOP 合規 | `e400789` |
| C2 | 翻譯與排版還原機制：render/restore 簇〔collect_render_slots〔key=原文標題 path·level=min(2+depth,6)〕/ restore_sections_markdown〔ThreadPoolExecutor 並行+保序+單 unit 退原文·max_workers 注入·**回傳 (md,slots,zh_by_index)、引擎不知 rag**〕/ normalize_paragraph_breaks / translate_unit / translate_whole / is_heading_degraded / flatten_sections / own_text_len〕原值搬入、resume 改 delegate + 清 dead import;行為等價 resume 42 passed、640 基線、SOP 合規 | `24db977` |
| C3 | rag 旁路與 meta header 純格式化器：collect_rag_sections〔summary_key=原文標題 path〕/ single_container_sections〔title 參數化、引擎不讀 ctx〕原值搬入 + **render_meta_header 重構為純格式化器**〔收 (Label,Value) tuples、引擎零讀 raw_metadata/ctx·U3.1 Zero Schema Coupling〕、resume 抽欄+lang label 後 delegate;行為等價 resume 42 passed〔含 meta header byte 斷言〕、640 基線、SOP 合規 | `4078a9e` |
| C4 | 引擎單元測試與接縫整合測試〔雙鎖·U5/Q6〕：新建 `tests/test_section_engine.py` 17 測試〔DFS 走訪+子樹 / 批次摘要保序+非致命+zh skip / restore byte 序+並行限流+單 unit 退原文 / heading 退化×3 / meta header 純格式化×3 + **base 層 P2→P3→P4 key-changing 整合**〔_DetTr 真改 title、斷言 summary_key 與 collect_summary_targets key 同基準=原文標題 path·堵 RAG-ASYNC-HOTFIX-1〕〕;純新增測試、全套件 657 passed〔640+17〕 | `6bd8705` |
| C5 | Checkout 收官：5 維度 Conformance 全綠〔目標規格 U1-U6+U3.1+Q6 / tasks §6 grep+pytest 657 / 不可動〔僅 section_engine/resume_pipeline/test 變動·slide/contracts/rag_indexer 零碰·final byte 等價〕/ 提示詞 7 份齊 / msg §8 完整〕+ **§7.2 不豁免達標**〔C4 key-changing 整合 + resume 既有整合雙鎖〕+ baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1-C5 報告→executions/〕+ TODO 結案 + hash 自癒 | `b1012bc` |

> **修法依據**：`.claude-logs/plans/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_plan_v1.md`（v2、§9 六 OQ 全 🟢 定案）
> **動因**：resume 的「遞迴標題樹走訪→逐節點摘要/並行翻譯/排版還原/rag 旁路/meta header」section 機制為 litedoc/academic/technical/book 共同骨幹（`_normalize_paragraph_breaks`/`_translate_whole` 已在 slides 重複一份、litedoc 將成第三份）→ baron 拍板「選二·共用真理源先行」：先抽 base、再做 litedoc。
> **設計（§2.5 方案 A）**：pure-function 模組 + translator/llm/doc_type/prompt 全注入、引擎零 doc_type 字面量；對齊 rag_indexer/domain_normalizer 既有共用真理源範式（非 mixin/base class 繼承耦合）。
> **U3.1 銳化（baron review）**：render_meta_header 收 (Label,Value) tuples、引擎零讀 raw_metadata → 各文體欄位/語系差異全留呼叫端（Zero Schema Coupling）。U3.2：DFS 吃任意子樹供 book 未來 rolling 組合。
> **行為等價鐵證**：RESUME-PERF-1 C1「解耦先鎖等價」範式——每 Run Commit 後 resume 既有 42 測試〔含 RAG-ASYNC-HOTFIX-1 key-changing 整合〕全綠。
> **Q2 不收編**：slide_pipeline 2 份重複副本〔已 ship+golden〕留後續、不在本案。
> **⚠️ 後續（非本案）**：litedoc plan（news/web/unknown、建於本引擎上）；slides 收編。

### DOC-Refactor WORKFLOW-4 StraTA 任務成功率原理移植進文件治理模板

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Plan 側 Diverse Rollout（U4）：`template_plan` §2 後插**選用** `§2.5 候選方案（Diverse Rollout）`〔高風險/模糊/架構級才觸發·≥2 語意分散方案+trade-offs+否決留痕、低風險明說單案〕+ `template_prompt_for_plan` 撰寫原則 #5 多候選 + Q5 stale 校正〔#4 §7→§9 + 「套用模板結構」表對齊 template_plan 實際章 §4 跨Phase/§5 變動風險/§9 OQ/+§2.5、stale 0〕;零業務代碼、640 passed 基線 | `44659be` |
| C2 | Execution 側 Conditioning + 雙軸自評（U1/U2/U3）：`template_prompt_for_run` 強制讀檔清單加 `plan.md`〔U1·全局策略 z re-inject、StraTA §4.1 prepend z;fence 內改行內 marker〕 + `template_execution §1` 加「與全局策略對齊」欄〔U2〕+ §6 後新增 `§自評`〔U3·雙軸：(a)越界?(b)無關/違規?(c)推進哪個 U-N?·正向軸防做白工〕;C2 報告就地 dogfood;零業務代碼、640 passed 基線 | `0e8cb77` |
| C3 | Check 側減負前移（U5）：`template_prompt_for_check` Conformance 維度表後加註——不可動〔維度三〕+ msg〔維度五〕由各 Run §自評〔U3〕前移分攤、Check **減負非省略**、仍為**最後總閘門**·聚焦跨 Commit U-coverage（總驗收）+ §7.2 跨 Phase 整合;**嚴禁重寫 WORKFLOW_SOP §4 五維度定義**〔grep 證不在 diff〕;零業務代碼、640 passed 基線 | `757dee6` |
| C4 | Checkout 收官：5 維度 Conformance 全綠〔目標規格 U1-U6 跨 commit 全覆蓋〔U1/U2/U3=C2·U4=C1·U5=C3·U6=五模板 marker+StraTA 誠實前提註〕/ tasks §6 grep / 不可動〔零業務代碼·WORKFLOW_SOP §4 未動·640 passed〕/ 提示詞 6 份齊 / msg §8 完整〕+ §7.2 純 DOC-Refactor 顯式豁免〔無 code handoff〕+ baton 一次性歸檔〔plan→plans/、tasks→tasks/、C1-C4 報告→executions/〕+ TODO 結案 + 全量 hash 自癒 | `8892bcd` |

> **修法依據**：`.claude-logs/plans/2026-06-14_WORKFLOW-4_StraTA原理移植文件治理模板_plan_v1.md`（v2、U1-U6、§9 六 OQ 全定案）
> **動因**：StraTA（arXiv 2605.06642v1）提高任務成功率四原理——① 固定策略 z 自初始狀態抽樣、每步 conditioning ② 階層 ③ diverse strategy rollout（farthest-point）④ critical self-judgment（逐步：是否依策略 / 是否推進任務）——可移植進文件治理流程治本「Run 偏離 plan 全局策略 / 設計單線無多候選 / 做白工（scope creep）/ Check 人肉重跑」。
> **移植映射（U1-U6）**：U1 run 讀 plan＝conditioning re-inject;U2 execution 對齊欄＝顯式宣告 conditioned-on;U3 §自評雙軸（負向防錯 + **正向「推進哪個 U-N」防做白工**）＝credit assignment;U4 template_plan §2.5 條件化多候選（高風險才觸發·語意分散非同案變體）＝diverse rollout;U5 check 減負前移＝step-level credit assignment 收官聚焦。
> **誠實前提**：移植「文件治理原理」非「RL 演算法本體」;各模板 marker 帶 StraTA 註說明。
> **§7.2 豁免**：純 DOC-Refactor、5 模板 .md、零業務代碼、無 Phase handoff（同 WORKFLOW-3 立規者先例）。

### DOC-Refactor PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC

| Commit | 內容 | Hash |
|---|---|---|
| C1 | SPEC v7 同步（SPEC 真理源回灌：D1 slides P3 drift〔100% Bypass→逐頁翻譯〕/ D2 golden A/B 軌釐清〔§1.3.1〕/ D3 alt LaTeX 跨軌契約〔R3.2〕/ D4 is_blank 頁面類型判定〔§1.3.1 第4原則+§1.2 指回〕/ D6 rag_sections §1.1.2 旁路登記〔對稱 raw_metadata〕/ D7 rag_tree_json 點名 / D5 清洗層一行;bump v7;7 處 grep 全綠、640 passed 基線、零代碼 diff、四凍結合約型別欄位零變動） | `隨 C3`〔SPEC 長駐 baton、就地 git add 於 Checkout〕 |
| C2 | master plan 補註⁸（母 plan 回灌：§8.5「B 軌另捕」措辭修正為「capture 捕 A 軌正本基準/B 軌走 shadow diff + 改善豁免」+ §99.2 補註⁸不 bump 主版本;grep B 軌另捕 0 殘留〔唯一命中 changelog〕、640 passed、零代碼） | `e15a7aa` |
| C3 | Checkout 收官：Conformance 三維度全綠〔目標規格 D1-D7 / tasks §6 grep+pytest / 不可動〔零代碼·contracts.py 未動·其他路次未動〕/ 提示詞五階段稽核 / msg 完整〕+ §7.2 DOC 豁免 + baton 一次性歸檔〔PIPE-SYNC-3 plan/master plan v10→plans/、tasks→tasks/、C1-C3 報告→executions/;SPEC 本體就地 git add〕+ TODO 結案 + hash 自癒 | `f9c261b`〔補做收官·見註〕 |

> **修法依據**：`.claude-logs/plans/2026-06-14_PIPE-SYNC-3_slides路落地經驗回灌母plan與SPEC_plan_v1.md`（v3、D1-D7、§9 六 OQ 全定案）
> **動因**：slides 路 7 次 hotfix（HOTFIX-1~6 + RAG-12-HOTFIX-1）落地後，兩真理源 2 錯誤（D1 SPEC slides P3 仍寫 100% Bypass、D2「B 軌另捕」A/B 軌 golden 混淆）+ 4 缺口 + 1 可選 → 不回灌則 PIPE-ACADEMIC 等下一路被誤導;同 PIPE-SYNC-2 對 resume 之回灌。
> **四層交接稽核結論**：contracts.py 四凍結合約「型別欄位」皆最新（venue/doi/section_summaries/domain_name）無 drift;旁路登記補對稱（raw_metadata §1.1.1 已有 + **rag_sections §1.1.2 本案補**;pdf_path/owner_id 為編排輸入不需登記）。
> **版控先例**：SPEC 本體長駐 baton 不入版控、就地 git add（同 PIPE-SYNC-2 195e12b）;master plan v10 自補註⁷ 已入 plans/ 版控。

### BE-Hotfix PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-6 | **Part A**〔`pipelines/slide_pipeline.py` `# === [PIPE-SLIDES-HOTFIX-6] ===` 包裹〕`_strip_master_date` 加「整頁 content 僅純日期行 → 清空」單頁 pass〔無論幾頁、運行 P1 譯前〕——真因＝HOTFIX-2 ≥2 頁門檻對「Vision 僅單頁吐母片頁尾日期」漏網〔Ch37 都市農業頁 `4/28/2026` 留存、P3 譯重排成 `2026/4/28`、全檔唯一日期行〕;真內容頁日期與其他行並存→`all()` False→不清〔不誤殺時間軸〕、與 HOTFIX-2 正交;**Part B**〔文件回溯更正〕釐清 `capture slides` 捕 A 軌〔PipelineCore/slides_processor〕非 B 軌→B 軌 hotfix 不需 A 軌 golden 重捕、驗證走影子 E2E;8 份 hotfix 文件〔HOTFIX-1/1b/2/3/3c/3d/4/5〕「slides golden 須重捕」誤述加更正 banner 作廢〔原句保留作審計〕+ TODO 14 行 slide-golden 尾註〔含 META-NORM C4 同誤;resume golden 6 行未動·A 軌共用本即正確〕;RAG-12-HOTFIX-1「零 golden 重捕」正確不改;RAG 隔離、四路零碰;SOP logging+database 無命中（合規）;4 新回歸測試〔單頁純日期清空/單頁日期夾內容保留/多頁 HOTFIX-2 不退化/一般不動〕、slide 71 passed、全套件 640 passed〔基線+4、唯一 fail＝既有 .env LOG_FORMAT flake〕 | `84c0825` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-6_hotfix.md`
> **動因**：HOTFIX-5 後 baron 發現 Ch37 都市農業頁殘留母片日期 `2026/4/28`（被翻譯重排）;並釐清 `capture slides` 捕 A 軌、先前 8 份 hotfix 文件「golden 須重捕」為 A/B 軌混淆誤述。
> **⚠️ A 軌 golden 不需重捕**（本改 B 軌、A 軌 slides_processor 未動）;**baron 影子重傳 Ch37**〔無需 golden 重捕〕→ 都市農業頁底不再殘留日期、真內容頁日期未誤殺。

### BE-Hotfix PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（is_blank 跳過放寬 + Vision prompt 釐清）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-5 | `pipelines/slide_pipeline.py`〔`# === [PIPE-SLIDES-HOTFIX-5] ===` 包裹〕P1 `_process` ④ **跳過放寬**：`is_blank 且 title+content 皆空`→**`is_blank 且 markdown_content 空`**〔容許 title/figure_description 非空、安全網＝有實質正文則不跳防誤殺〕+ `_VISION_PROMPT` 第5條釐清〔純過場/章節分隔/裝飾頁即使有「過場/Transition」標題仍 is_blank=true;保留「含真實圖表/資料/條列正文一律 is_blank=false」防誤踢真圖頁〕;真因＝HOTFIX-4 雙保險「title 須空」對 Vision 給了標題之過場頁（Ch37 page-32 生態球）漏網、figure_description 非空使三欄規則亦不跳;過場頁與純圖表頁結構同型〔title+figure_description+無正文〕唯 is_blank 可分;RAG 隔離〔ctx.rag_sections/merged 不碰〕、四路/web_server 零碰、保留三欄全空後盾;SOP logging+database 無命中（合規）;5 新回歸測試〔過場跳/裝飾跳/真圖保留/有正文保留/舊無欄相容〕+ 既有 HOTFIX-4 四測試不退化、slide 67 passed、全套件 636 passed〔基線+5、唯一 fail＝既有 .env LOG_FORMAT flake〕 | `67de0d2` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md`
> **動因**：RAG-12-HOTFIX-1 後 baron 比對 Ch37 發現 page-32 生態球過場頁未踢除;Vision 給了標題「過場投影片 (Transition Slide)」→ HOTFIX-4 跳過條件「is_blank 且 title+content 皆空」不成立 → 漏網。
> **⚠️ golden + baron E2E（非 commit）**：改 Vision prompt → slides golden 須重捕、**搭既有待捕批次**〔HOTFIX-1/1b/2/3/3b/3c/3d/4 + META-NORM C3/C4〕一次首捕;影子重傳 Ch37 → page-32 不產頁、頁序順移、真圖表頁（氮循環/土壤剖面/PCoA）未誤踢。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕

### FE-Hotfix RAG-12-HOTFIX-1 — 圖片 alt 內 LaTeX 破版（renderMarkdownWithMath 抽 math 前保護圖片整段）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-12-HOTFIX-1 | `static/index.html` `renderMarkdownWithMath`〔`// === [RAG-12-HOTFIX-1] ===` 包裹〕新增 imgBlocks + 步驟 1.5 抽 markdown 圖片整段 `![...](...)`→`__IMG_PLACEHOLDER_N__`（同 code 保護手法）+ 步驟 5〔marked.parse 前〕還原；真因＝步驟 4 不分場合抽 `$...$`〔含圖片 alt 內、如氮循環圖 figure_description 之 `$N_2$`/`$\text{NH}_4^+$`〕→ 步驟 7 把 `katex.renderToString` 的 `<span class="katex">`〔含 `"`/`<>`〕回填進 `alt="…"`→引號提前閉合、`<img>` 炸穿、後續 HTML 全吞→「後續排版全部錯誤」+ 圖說直排亂碼；修法使 alt 內 `$` 永不進 math 管線〔留字面、不可見、無害〕、`<img>` 不再被炸；A 軌〔.figure/.ph 不塞 markdown alt〕+ 履歷〔圖說無 LaTeX〕皆正常→證 FE-RHYTHM-UNIFY CSS 無辜；通用解所有文體圖說含 `$`；純前端、零後端/管線/.py、零 golden 重捕；node spike 4/4 PASS〔圖片 LaTeX alt 受保護/正文 math 不受影響/混合僅正文進/一般圖等價〕、全套件 631 passed〔基線維持、唯一 fail＝既有 .env LOG_FORMAT flake〕 | `88578dd` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-14_RAG-12-HOTFIX-1_hotfix.md`
> **動因**：baron 掃 Ch37_Plant-Nutrition_shadow（B 軌簡報）發現「空白頁沒踢除 + 後續排版全部錯誤」；經多輪證據診斷（A 軌/履歷正常證 CSS 無辜、source markdown 結構乾淨證非空白頁結構崩壞）鎖定真因＝氮循環圖(page-30)圖說 alt 含 LaTeX → renderMarkdownWithMath 步驟 7 KaTeX HTML 注入 alt 炸 `<img>` 級聯。
> **⚠️ baron E2E（非 commit）**：重整 Ch37 簡報〔無需重跑管線、final_zh 不變、重整即生效〕→ 氮循環圖正常、其後排版全恢復；正文真 math 仍渲染；A 軌/履歷不受影響。
> **後續未竟**：B2 過場頁（HOTFIX-4 對有標題過場頁抓不到）已開 `PIPE-SLIDES-HOTFIX-5`〔baton 待 Run、改 Vision prompt 須搭 golden 重捕、次要〕。

### FE-Refactor FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一（單一 margin-top flow 模型·完全消滅 :has·收編 FE-RHYTHM-1）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Spike & 模型凍結（垂直節奏 spike）：worktree harness + 碼審驗三假設〔A1 直接子代＝`#paper-content.innerHTML=renderMarkdownWithMath()`(marked 輸出)、`normalizeAcademicHeader` 只改 `.paper-header-meta` 不重構頂層 / A2 巢狀清單〔li 內〕非直接子代、`>`不誤撐 / A3 `:is`/`:not`/`+` Safari 14+·Dia 支援〕+ 凍結模型 9 條〔4 flow + 5 特殊塊〕+ token(4/6/2/1) + 逐 adjacency 互斥/特異度/margin 摺疊證明 + `:has` 可完全消滅結論；零 production diff | `1ecdc5c` |
| C2 | 統一垂直節奏模型落地（atomic 模型替換）：`static/index.html` 移除 FE-RHYTHM-1 兩條 `:has` + 新增 4 條 flow〔`> *+*` 基準流 space-4 / `> :not(:is(h1-4))+:is(h1-4)` 非標題→標題 space-6 區段斷點 / `> :is(h1-4)+*` 標題→其內文 space-2〔含 h→h、取代擬議 FE-RHYTHM-2〕 / `> p+:is(ul,ol)` 標籤→清單 space-1〕+ 特殊塊 margin-top 明列〔.slide-head/.paper-header-meta/.katex-display/.figure 置 flow 後贏 tie 防覆寫〕；4 主題〔kahn/kandinsky/mies/nara〕移除 p/h1/h2/h3 垂直 margin〔保 border/padding/色票/字族〕；5 檔 + 5 .bak 原子；grep 舊 :has 0 / `:has()` 選擇器 0 / 四主題真 margin 殘留 0；零 .py diff、全套件 631 passed〔基線維持、唯一 fail＝既有 `.env LOG_FORMAT` flake〕 | `a9f2c3a` |
| C3 | Checkout 收官：Conformance 五維度〔目標規格 U1-U10〔U8 視覺 E2E 列 baron〕/ tasks §6 grep+pytest / 不可動〔零 .py、chat/正規化層未碰〕/ 提示詞五階段稽核 / msg 草稿完整〕全綠 + §7.2 不適用〔單一前端 CSS、無 code handoff、E2E 為驗收主軸〕+ baton 一次性歸檔〔plan/tasks/C1-C3 報告→plans//tasks//executions/〕+ TODO 結案 + hash 自癒 | `b727161` |

> **修法依據**：`.claude-logs/plans/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_plan_v1.md`（v2、九 OQ 全定案、§9.1 凍結模型；tasks §9 Q-A baron 拍板 C2 atomic）
> **動因**：閱讀視圖垂直間距原由散落主題 CSS + base reset + FE-RHYTHM-1/擬 FE-RHYTHM-2 逐交界補丁治理，根因＝「只用 margin-bottom + L83 reset 歸零清單 margin」之單向偶然 → 清單「前寬後窄」黑洞 + 連續標題過寬 + 同視覺兩機制（`###` vs `X：`）+ 打地鼠;審計確認無硬衝突但疊床架屋 → baron 選一次性統一重構。
> **解法**：單一 margin-top flow 模型（基準流 + 三檔 + 一條最貼）取代逐交界補丁、收編 FE-RHYTHM-1、取消擬議 FE-RHYTHM-2；margin-top 制使清單看「上一個」兄弟＝相鄰選擇器 → **完全消滅 `:has()`**（相容 Safari 14+）;主題垂直 margin 移交 base（principles.md 間距=結構歸 base）。
> **⚠️ baron 運維（非 commit）**：三軌（履歷/論文/簡報）× 四主題（kahn/mies/kandinsky/nara）視覺 E2E〔尤論文連續 h2→h3 貼緊、巢狀清單未誤撐、簡報引擎頁 h→h 與施肥頁 p→list 節奏一致、.slide-head 無雙重間距〕+ chat（`.msg-ai`）不受影響;無 golden 重捕（純 CSS、final_zh byte 不變）。


### FE-Refactor RAG-12 前端 KaTeX 數學渲染（自託管 KaTeX + 三階段順序佔位）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 引入自託管 KaTeX 0.16.47 資產與載入（vendor css/js/20 woff2 + fetch 腳本 + vendor README〔SHA〕+ index.html head；零 .py diff、605 passed、未接線） | `013371a` |
| C2 | 核心渲染管線 `renderMarkdownWithMath` + CSS（三階段順序佔位〔code/`\$`/math〕+ 無 lookbehind texmath 正則 + 步驟7 ESC 還原 + 壞式 `.katex-error` 降級 + `.katex-display` 防禦 CSS;**⚠️ math 佔位改 Unicode PUA 哨兵**〔spike 證 `__MATH__` 被 marked 雙底線咬 `<strong>`〕;端到端 9/9〔真 marked+katex〕、未接線） | `79a8e89` |
| C3 | 接線六處 marked.parse 消費端（paper L2864 + chat 5 處 → renderMarkdownWithMath;函式內步驟6 marked.parse 保留;grep rMWM=7/marked.parse=1;數學渲染 LIVE） | `0ea0cf8` |
| C4 | producer 契約 pytest（`tests/test_latex_preservation.py` 4 測試:formula 塊 `$$\tag`/text 行內 `$P_base$`/_preserve_pipe_table/_write_to_md 逐字;鎖 academic A-rail **RestoreProcessor** 不截斷轉義 `$$`/`$`;零業務碼 diff、609 passed） | `a4b4b3f` |
| C5 | 文件同步（README 前端 vendored 依賴段 + api-integration renderMarkdownWithMath 雙端整合 + dom-reference .katex/.katex-display DOM+CSS+降級;3 .bak、純 .md） | `f3d48eb` |
| C6 | Checkout 收官：Conformance 五維度全綠〔目標規格 U1-U12 / tasks §6 grep+pytest / 不可動業務碼零 diff / 提示詞 8 份 / msg 完整〕+ §7.2 整合〔producer pytest 4 passed 達成 + consumer 同碼 spike 9/9 實證;真瀏覽器 E2E 列 baron 運維〕+ baton 一次性歸檔〔plan v1-v7/tasks/C1-C6 報告;slide 3c/3d 非本任務留 baton〕+ 執行期 deviation 補註 plan/tasks §99.2 | `c1c2a72` |

> **修法依據**：`.claude-logs/plans/2026-06-12_RAG-12_前端KaTeX數學渲染_plan_v7.md`（七輪 review + 三次 spike 實證、無 lookbehind、步驟7 ESC 還原、Unicode PUA 佔位）
> **動因**：含真二維 LaTeX（`\frac`/`\mathrm`/`\tag`）之論文（2601 800VDC 資料中心 / byz 拜占庭 / 2412 TradingAgents）前端呈現字面 `$$`/`$` 原始碼、無法二維排版；Unicode 上下標無法表達分數/積分故必須引入渲染引擎。
> **解法**：自託管 KaTeX 0.16.47（離線/GFW 字型不依賴 CDN）+ 三階段順序佔位整合（code→`\$`→math→還原→marked.parse→KaTeX 回填）；行內 `$` 採 pandoc/texmath 啟發式（開 `$` 後非空白、閉 `$` 後非數字）防貨幣誤渲且不退化 `$i$`/`$3x$`；marked 仍 CDN、不裝 marked-katex-extension。
> **執行期 deviation（已補註 plan/tasks §99.2）**：① math 佔位 `__MATH__`→Unicode PUA 哨兵（marked 雙底線咬粗體）② producer class `AcademicPipeline`→`RestoreProcessor`（grep 實證、與 plan Q7 一致）。
> **⚠️ baron 運維（非 commit）**：瀏覽器 E2E（plan §8.3 八項，尤自託管字型 `/static/vendor/katex/fonts/` 200 + `.katex` DOM + slides 公式頁緊排）；數學段落未翻譯（2601 行 65/67/69 英文）屬正交 backlog（academic 路 translator、Q6 另立）。

### DOC-Refactor PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Master Plan Sync：母 plan v10 就地補註〔U1 resume P3 Bypass 雙處→逐 section〔slides 留·Q6〕/ U2 §8.5 RAG-ASYNC ⬜→✅+PIPE-RESUME 狀態自癒 / U3 key 契約母句 / U8 Tiles 交付形狀措辭 / U5 PIPE-VISUAL §1.3.1 指標〕+ 補註⁶ | `c54327c` |
| C2 | SPEC Sync：PIPE-SPEC 就地補註〔U3 §1.1②+§1.4.1 **key 接縫契約凍結**〔原文標題 path、P2產/P3帶/P4取三方同基準、對齊 WORKFLOW_SOP §7.1〕/ U4 zh 來源五路通用 edge path / U5 **新增 §1.3.1 Vision 解析共用規格**〔忠實轉錄鐵律/temp=0/非確定性註記〕/ U6 樣例 -001 / U7 rag_tree 由 build_rag_tree 自建+四產物完整性 / U8/U9/U10 註〕+ v6；四凍結合約欄位結構零變動 | `9666b20` |
| C3 | SOP Fix & Archive：U11 model_recommendations EMBEDDING 建議值 -2→**-001**🔴+EXTRA_INFO 已廢註 / U12 guide 勘誤 banner〔內文不動〕/ U13 doc_type v3 A 軌 banner+**v1/v2→archive**〔sop 僅留 v3〕/ U14 mineru §6 RELEASE_ON_UPLOAD 配套+v3 | `29f13ca` |
| C4 | Checkout 收官：Conformance 五維度全綠〔U1-U14 / tasks §6 十八條 grep / 不可動〔業務碼/凍結合約/Slides Bypass〕/ 提示詞 5 份 / msg 完整〕+ **§7.2 豁免顯式聲明**〔DOC、無 code handoff、Q4〕+ baton 歸檔〔plan/tasks/C1-C4 報告；兩長駐真理源不動〕 | `43ad9c6` |

> **修法依據**：`.claude-logs/plans/2026-06-10_PIPE-SYNC-2_resume路落地經驗回灌母plan與SPEC_plan_v1.md`（§99.2 v1.2、U1-U14、§9 六 OQ 全結清〔Q1 不 bump/Q2 全納/Q3 §1.3.1/Q4 豁免/Q5 mineru/Q6 slides Bypass 留〕）
> **動因**：第 1 路（Resume）收官後兩真理源 1 矛盾+4 缺口+3 stale、sop 4 檔誤導（model_recommendations 仍推已廢 embedding-2）→ 第 2-5 路照 spec 實作會重蹈 HOTFIX-1/2/3 與 MODEL-11 的坑；**PIPE-VISUAL（第 2 路 Slides）開 plan 前置、現已完成**。
> **版控先例**：兩真理源本體長駐 baton 不入版控、.bak 入 archive 作審計（195e12b）；sop 檔皆 tracked 正常入庫。
> **銜接**：下一步開 PIPE-VISUAL plan（SPEC §1.3.1 Vision 共用規格直接引用；其 plan 核心 OQ＝P3 Bypass 或逐 section、Q6 刻意保留給它）。

### BE-Refactor META-NORM 封面元數據自癒飛輪與動態欄位登記（PIPE 共用真理源家族第 4 員·解 PIPE-SLIDES C+D）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Schema & Flag：`MetaField`/`MetaFieldAlias` 兩表〔繼承 Domains 範式、PK/Unique+FK CASCADE+sort_weight〕+ `LLM_USE_META_NORM`(False) + db.py seed 6 欄〔on_conflict 冪等+session.begin〕；3 測試 | `ae407ef` |
| C2 | MetaNormalizer 自癒飛輪：三路分流〔reserved 映合約標記不入庫不問 LLM·BS1 / 泛用詞黑名單不快取每次 LLM·Q9 / 非黑名單快取查→LLM 比對既有 canonical→on_conflict 註冊+label 提案·BS4〕+ temp=0 保守比對·Q2 + LLM 交易外 + 旗標閘門 + try/except 降級；5 測試 | `6dd48f8` |
| C3 | P1 Wire：`_COVER_PROMPT` 開放 metadata 抽取+封面判定放寬 + run_phase1 旗標 on 呼 normalize_fields→reserved 回填合約不入旁路 + canonical 三欄 dict 寫旁路〔HOTFIX-1b 契約〕、旗標 off 退寫死 + return 補 venue/doi；2 測試 | `6c37a1d` |
| C4 | Subtitle：`_VISION_PROMPT` +subtitle 欄 + units 收 + `_key_title` fallback〔title 空用 subtitle 防 key 漂移〕+ 並行翻譯 4-tuple + EN/ZH 渲染 `### {subtitle}`〔解 D〕；2 測試 | `dedd915` |
| C5 | Frontend Generic Renderer：web_server +GET /api/meta-fields〔唯讀〕+ static/index.html 通用 key-value 渲染器〔window.metaFields seed 兜底+fetch、renderTitleHeader 遍歷非排除集·BS2 + sort_weight/字母序·BS7〕；飛輪 end-to-end 貫通 | `d2a3db2` |
| C6 | Tests：`test_c6_key_changing_integration`〔§7.2：P1 自提『課程』→飛輪 course→消費端取值；接縫不變式 raw≠canonical 對位 + 三欄 dict 杜退化 + alias 寫回〕+ test_slide assertions 審視；45 passed、全套件 601 passed | `6bb440e` |
| C7 | checkout 收官：Conformance 全維度全綠〔U1-U9+U*.1 / §6 C1-C6 測試 / §7.2 整合存在且通過·免豁免 / 不可動 / 提示詞 9 份 / msg 6 份〕+ baton 一次性歸檔〔plan/tasks/C1-C7 報告〕+ TODO 結案 + hash 自癒 | `caf31fa` |

> **修法依據**：`.claude-logs/plans/2026-06-11_META-NORM_封面元數據自癒飛輪與動態欄位登記_plan_v1.md`（v1.2、八 OQ+Q9/Q10 全定案、BS1-BS7 收編）
> **動因**：PIPE-SLIDES 學術簡報實測（Ch37_Plant-Nutrition）暴露 C（封面課程/講師未進結構化 Meta）+ D（小標題塞正文）；baron 構想「LLM 開放抽取 + 二次 LLM 比對既有欄統一」＝DOMAIN-NORM 知識飛輪搬到 metadata 欄名。
> **範式繼承**：DOMAIN-NORM（Domains/DomainMapping + 快取→LLM→on_conflict 動態註冊）/ GLOSSARY-CORE（旗標閘門）；新增僅 MetaField/MetaFieldAlias 兩表 + MetaNormalizer。
> **⚠️ baron 運維（非 commit）**：① `.env` `LLM_USE_META_NORM=true` 漸進開（影子先驗飛輪收斂/誤併/前端顯示）② C3/C4 改 Vision prompt → slides golden 重捕 ③ 綜效：餵養 CHAT-STRUCT-1（backlog #5、意圖路由改查 canonical key）。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕

### FE-Hotfix FE-RHYTHM-1 — 閱讀視圖「清單前寬後窄」垂直節奏治本（base CSS · :has() 交界修正）

| Commit | 內容 | Hash |
|---|---|---|
| FE-RHYTHM-1 | `static/index.html` base CSS（`#paper-content` 區）新增兩條 `:has()`、**僅打「段落↔清單」交界**:`p:has(+ ul/ol){margin-bottom:var(--space-1)}`〔標籤段落貼緊其下清單·收窄過寬〕+ `ul/ol:has(+ p){margin-bottom:var(--space-4)}`〔清單與後續段落/標籤間補留白·補足過窄〕;**巢狀清單**〔後接 `<li>` 非 `<p>`〕**與「清單接標題」**〔後接 `<h>` 非 `<p>`〕**不中、波及最小**;真因＝base 垂直節奏只靠 `margin-bottom`〔`#paper-content p` 無 `margin-top`〕+ `index.html:79` 全域 reset 歸零 `ul/ol` margin、四主題 0 補 → 清單「前有間距〔吃前段 mb〕後無間距〔自身 0、後段無 mt〕」單向黑洞;Vision 把區段標籤吐成純段落緊接清單且交替重複 → 顯「標籤→清單寬、清單→下個標籤窄」反轉〔Ch37 施肥頁〕;**全文體共用閱讀視圖一次治本**〔履歷/論文/書籍/litedoc/簡報〕、**chat（`.msg-ai`）不受影響**、不動 themes;**同時解 #2**〔slide 末條列→下張圖 `<p><img>` 之 `ul:has(+ p)` 補 space-4 → 不黏烤進右上的母片日期;採 (a) 不額外加 CSS、純圖頁邊角暫留〕;`:has()` 相容 Safari 15.4+/Chromium 105+〔Dia OK〕、舊版整條忽略降級現況;grep 兩規則命中 + themes 0 + 零 .py、全套件 631 passed | `3428581` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-13_FE-RHYTHM-1_hotfix.md`
> **代號**：**非 slide 專屬**——由 PIPE-SLIDES QA（Ch37 施肥頁）暴露、但根因在全文體共用 base CSS 之垂直節奏、治本歸此通用代號。
> **動因/根因**：base 只用 margin-bottom 做節奏 + reset 歸零清單 margin → 清單「前寬後窄」單向黑洞（反覆出現、之前擱置）;baron 拍板 A（`:has()` 全域治本、最小 delta、須驗三軌）、否決 B（slide-only wrapper、需管線+重捕）。
> **⚠️ baron 三軌 E2E（非 commit）**：簡報 Ch37 施肥頁〔標籤貼清單、清單後留白〕+ 履歷〔小標+條列節奏〕+ 論文 2601/byz〔**尤巢狀清單未被 `ul:has(+p)` 誤撐**〕+ 四主題逐一 + chat 不受影響;#2 黏字〔前頁條列→下頁圖留白〕;純圖頁邊角暫留、礙眼再補 `img{margin-top}`(b)。
> **無 golden 重捕**（純 CSS、final_zh 不變）。

### BE-Hotfix PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-4 | `pipelines/slide_pipeline.py` P1：`_VISION_PROMPT` 基底加 `is_blank` 欄 + 第 5 條判定指引〔整頁無實質內容/僅裝飾橫條→true、含真實圖表→false;因 `_COVER_PROMPT = _VISION_PROMPT + …` 所有頁含封面皆得〕+ `_process` ④ 單位過濾**雙保險跳過**〔僅當 `is_blank` **且** title/content 皆空才跳——防 Vision 誤判有內容頁被丟;合法純圖頁 `is_blank=false` 不受影響;舊 golden 無 `is_blank`→None falsy→**向後相容不跳**〕;既有「三欄全空」保留為第二道;與既有 `is_cover` 同模式對稱;真因＝Ch37 第 16 張空白投影片〔僅裝飾黑橫條〕無 title/content 但 Vision 回非空 figure_description〔描述空白〕→ 通過舊三欄判定→產空框黑條 reading 頁;**RAG/渲染層/四路零碰**〔只動 P1 prompt + 過濾〕;SOP logging+database 無命中（合規）;is_blank grep 6 + HOTFIX-4 3 命中 + is_cover 未動;4 新 pytest〔空白跳過/雙保險保留有內容/純圖頁保留/舊無欄相容〕、slide 62 passed、全套件 631 passed | `91ad0b6` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md`
> **動因**：baron 比對原稿 `Ch37_Plant-Nutrition.pdf` 第 16 張空白投影片，B 軌仍產空框黑條 reading 頁;現有 P1 空白跳過僅「三欄全空」、Vision 對空白頁回非空 figure_description 漏網。
> **方案抉擇（baron 拍板 A）**：Vision `is_blank` 旗標（看真圖判斷、與 `is_cover` 對稱）;否決 B（figure_description 關鍵詞啟發式·脆/誤殺）、C（像素門檻·難調）。雙保險防誤殺有內容頁。
> **⚠️ golden**：改 Vision prompt → Vision schema 變更 → slides golden 須重捕;**搭既有待重捕批次**（HOTFIX-1/1b/2/3/3b/3c/3d + META-NORM C3/C4）一次首捕、零額外成本。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **⚠️ baron E2E**：影子重傳 Ch37 → 第 16 張不再產 reading 頁、頁序順移;純圖頁（架構圖/照片）未被誤跳。

### BE-Hotfix PIPE-SLIDES-HOTFIX-3d — 字面 `**` 未渲染粗體 + 裸 URL 破版（slide 渲染層清洗）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3d | `pipelines/slide_pipeline.py` 新增 `_render_inline_bold`〔行內 `**X**`→`<strong>X</strong>` raw HTML、**繞過 CommonMark CJK emphasis 失效**——閉合 `**` 前接全形標點、後接中文字非 closer 致字面星號；marked 不 sanitize 原樣輸出〕+ `_strip_bare_url_lines`〔剝除整行純 URL；**行內 URL 與 `![](images/…)` 圖片行保留**〕;`_page_source_md`/`_deliver` 於 `_promote_subheadings` 後注入〔promote→inline_bold→strip_url→normalize→tighten[3c]〕;真因＝B 軌 vs 原稿 Ch37 比對——p27 根圈 `**互利共生**中` 字面星號〔原稿英文 `**bold** ` 後空白無症、翻中 CJK 緊貼才觸發〕、p6/p18/p27/p35 投影片來源/縮圖網址被 Vision 轉錄成整行裸連結 gfm 自動連結 + 超長無斷點撐破 `#paper-content`;**RAG 零影響**〔`rag_sections` content＝原始 `zh_content`〔merged L962〕、未套 3d〕;零後端/DB/models/static/四路;SOP logging+database 無命中（合規）;helper grep 6 + HOTFIX-3d 4;9 新 pytest〔行內粗體/CJK 緊貼/落單 `**` 保留/整行 `**` 升標題/剝整行 URL/行內 URL 保留/圖片行保留/RAG 隔離〔真 P3〕/p27 端到端〕+ 端到端真 marked 4/4、slide 58 passed、全套件 627 passed | `7d6170d` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md`
> **動因**：baron 掃 `植物營養 (Plant Nutrition) (測試).pdf` 40 頁 + 比對原稿 `Ch37_Plant-Nutrition.pdf`，#2 兩類渲染破版（字面 `**`〔p27〕+ 裸 URL〔p6/18/27/35〕、原稿無 B 軌引入）；baron 拍板開為獨立 BE-Hotfix。
> **⚠️ golden**：改 B 軌 final_zh 渲染（`<strong>` + 去 URL 行）→ slides golden 併既有批次〔HOTFIX-1/1b/2/3/3b/3c + META-NORM C3/C4〕一次首捕。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **⚠️ baron E2E**：影子重傳 Ch37 → p27 粗體詞正確顯示無字面 `**`、底部無 biorender 裸連結；p6/p18/p35 無超長裸 URL；圖片/行內連結保留。
> **後續**：`$LaTeX$` 數學渲染屬 RAG-12（已收官、自託管 KaTeX）；「數學段落未翻譯」屬正交 backlog（academic translator）。

### BE-Hotfix PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3c | `pipelines/slide_pipeline.py` 新增私有 `_tighten_point_groups`〔① 連續行首箭頭 `→`/`->` 合併單一段落 + 兩空格硬換行〔`<br>`〕→ tight 群、**箭頭原樣保留為文字不轉 bullet**、群內空行跳過、孤行不變、行中箭頭（連接詞）不碰；② `- * + • / 數字.` 相鄰清單項空行收緊 loose→tight、清單↔標題/圖/段落邊界留白；`\r?` 相容 CRLF〕+ `_page_source_md`/`_deliver` 渲染 body **殿後注入**〔於 `_promote_subheadings`+`_normalize_paragraph_breaks` 之後、硬換行不被 normalize 單 `\n`→`\n\n` 拆回段落〕;真因＝Vision 對「標題+重點群」每頁吐不同結構〔頁 A `*` loose list 母項下大縫·子項貼母項 / 頁 B `###`+`→` 散段落標題貼首項·項目散〕、CSS 對 loose `<p>`/tight `<li>`/散段落給不同 margin → 每頁節奏不一;**RAG 零影響**〔`rag_sections` content＝原始 `zh_content`〔merged L929〕、未套 tighten;slides RAG 走 `ctx.rag_sections` 旁路、不從 final_zh 切〕;零後端/DB/models/static/其餘四路改動;SOP logging+database 皆無命中（合規）;helper grep 3 命中 + HOTFIX-3c 4 命中 + merged 仍原始;9 新 pytest〔箭頭硬換行群/群內空行/行中不碰/孤行不變/loose 收緊/邊界留白/CRLF/RAG 隔離〔真 P3〕/頁 B 端到端〕、slide 49 passed、全套件 618 passed | `a486585` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md`（v3、保 `→` 硬換行版；四輪對話收斂——白名單→texmath 否決→保符號硬換行）
> **動因**：META-NORM/HOTFIX-3 後 baron 掃 `植物營養 (Plant Nutrition) (測試).pdf` 40 頁 + 比對原稿 `Ch37`，發現「標題+重點」兩頁兩種不一致節奏（頁 A 土壤顆粒清單 loose / 頁 B 氮素形態 `→` 散段落）；baron 拍板「保 `→` 原始符號、硬換行收緊」（非轉 bullet、非 CSS 全域 margin 滲論文）。
> **⚠️ golden**：改 B 軌 final_zh 渲染（箭頭群硬換行 + `*` 收緊）→ slides golden 併既有批次〔HOTFIX-1/1b/2/3/3b + META-NORM C3/C4 + 本 3c〕一次首捕。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **⚠️ baron E2E**：影子重傳 Ch37 → 頁 B `NH₄⁺` 標題下三點均勻緊湊群、`→` 原樣保留、群間留白；頁 A 母項/子項節奏均勻、`•` 保留；行中箭頭句維持段落。

### FE-Hotfix PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（HOTFIX-3 二補完）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3b | `static/index.html` base CSS 單 hunk：HOTFIX-3「二：清單縮排」selector 前置 `#paper-content ul, #paper-content ol,`〔`padding-left:1.5em` 不變、含 top-level + 巢狀〕；真因＝L79 全域 reset `ul/ol{padding:0}` 歸零 top-level 縮排、`list-style:outside` 下第一層 bullet marker 溢出到 `#paper-content` 左 padding〔`var(--space-8)`〕外側→凸排（比同頁標題更左），HOTFIX-3 二只補巢狀漏 top-level；**不動 themes**〔四主題 grep 清單 0 命中、縮排=結構歸主檔 principles.md、base 一處含自訂上傳主題受益〕；零 `.py`/零後端/零 RAG；包裹沿用 HOTFIX-3 既有 START/END；grep top-level/巢狀各 1 命中 + themes 仍 0、全套件零 Python diff 維持 605 passed〔僅 .env LOG_FORMAT=json env flake〕 | `1b8b939` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3b_hotfix.md`
> **真因**：`static/index.html:79` 全域 reset `body,...,ul{margin:0;padding:0}` 把 top-level `ul/ol` padding 歸零 + `list-style:outside` → 第一層 bullet 凸排；HOTFIX-3「二」selector 只涵蓋 `ul ul/ol ol/ul ol/ol ul`（巢狀）、漏第一層 `#paper-content ul/ol`。
> **歸屬（為何 base 不 themes）**：四主題 `#paper-content ul/ol/li` grep 0 命中（縮排本由 base L79 reset 單方決定）；縮排=結構歸主檔（`principles.md`）；base 一處含自訂上傳主題受益、放 themes 須改 4 檔且自訂主題永遠漏。與 HOTFIX-3「二」放 base 同一正當性、本 hotfix 僅把 selector 從「只巢狀」擴成「含 top-level」。
> **⚠️ baron E2E**：重整 ALi 簡報 → 第一層 `•` 不凸排（與標題左緣對齊/內縮）+ 巢狀子項未退化 + 四主題逐一一致 + 非 slides 文體清單正常。

### BE-Hotfix PIPE-SLIDES-HOTFIX-3 — 簡報閱讀視圖排版打磨（圖序/副標併標題塊/子標題/縮排）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3 | baron 前端逐頁 QA（Ch37）+ design/docs 設計對齊後 4 項排版修：**一-a** P3 parts 重排〔圖→標題塊→內文〕+ **C** `_slide_head_html` 副標併 `<div class="slide-head">`〔base CSS 底線移整塊下·用主題 `--divider-w` 變數→**順帶解 一-b** h2 夾線〕+ **A/B/C** `_promote_subheadings` 整行 `**X**`→`### X`〔升設計內 h3 非孤兒 h4、`\r?` 相容 CRLF、不產連續空行〕+ **二** base CSS `ul ul{padding-left}`〔結構 fallback、含自訂主題〕；**RAG 零改**〔subtitle 不進 chunk body、`sections.append` 原封不動、test_hf3_rag_sections_unaffected 證〕；不動 4 主題檔；5 既有斷言更新+4 新測試、40 passed、全套件 605 passed | `3f26d5c` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md`（含三盲點修正：\r 相容/不產連續空行/HTML 塊內 markdown 失效註記）
> **設計對齊（design/docs）**：`typography.md` 證 h2 底線是明文設計意圖→一-b 不在 base 蓋、改 C 從根源；A/B/C 升 h3〔h4 未規範=孤兒〕；二 縮排=結構〔principles.md 結構歸主檔、含自訂主題受益〕。
> **動因**：META-NORM 上線後 baron 前端 QA 植物營養簡報，發現圖序/標題夾線/子標題扁平黏連/子項目未縮排 4 項排版問題；經設計意圖核對 + 多輪決策（C 副標併標題塊最還原投影片）+ subtitle 對 RAG 零影響碼證後落地。
> **⚠️ golden**：改 B 軌 final 渲染 → slides golden 全變更〔HOTFIX-1/1b/2 + META-NORM C3/C4 + 本 HOTFIX-3〕落地後一次首捕；**slides fixture 需先補齊**（PaperRead-Lab 缺 `tests/golden_baseline/fixtures/slides.pdf`、入版控被 gitignore 排除）。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **backlog**：h2 border 規則重複 4 主題檔（DRY 債）→ 未來 FE 清理上移 base。

### BE-Hotfix PIPE-SLIDES-HOTFIX-2 — alt 破圖 / 母片重複日期 / F4 條列鬆散（B+E+F）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-2 | `pipelines/slide_pipeline.py` 單檔三點純渲染/清洗（學術簡報 Ch37 逐頁分析）：**B `_safe_alt`**〔alt 內 `][()`→全形、換行→空白；根除 CommonMark `![alt](url)` 之 `]` 提前閉合致破圖+描述洩漏正文（圖密集頁 p29/35/37 缺圖真因；HOTFIX-1 U8 alt 對齊暴露）〕+ **E `_strip_master_date`**〔原稿母片日期欄位 `4/28/2026` 烙進 20/20 頁非內容、P1 純日期行 ≥2 頁直接洗；補 `_dedupe_headers` 格式變異漏網（三變體各 <60% 門檻）〕+ **F `_normalize_paragraph_breaks` list-aware**〔修 HOTFIX-1 F4 回歸：單 `\n` 升級未排除條列致 tight list 炸 loose；負向前瞻補 `- * + • 數字.`〕；A 撤案〔忠實轉錄〕、C/D 留 META-NORM；3 回歸測試、32 passed、全套件 588 passed | `657a703` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md`（baron 拍板 B+E+F、A 撤案）
> **動因**：HOTFIX-1/1b 後 baron 上傳學術簡報 `Ch37_Plant-Nutrition.pdf`（44/38 頁）逐頁分析暴露 B（圖密集頁破圖+圖說洩漏）/ E（母片日期散落）/ F（HOTFIX-1 F4 條列鬆散回歸）。
> **零 Vision prompt 改動**：純渲染/清洗層、與 META-NORM 之 Vision schema 改動風險隔離。
> **⚠️ golden**：B/E/F 改 B 軌 final → slides golden 本 hotfix 後一次首捕（含 HOTFIX-1/1b 變更一次到位）。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **⚠️ baron E2E**：影子重傳 Ch37 → 圖密集頁整頁截圖正常/無破圖/無描述洩漏（B）、各頁無 4/28/2026（E）、條列緊湊（F）。

### BE-Hotfix PIPE-SLIDES-HOTFIX-1b — F2 譯題旁路格式修補（影子寫庫 AttributeError）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1b | 修補 HOTFIX-1 F2 回歸：`raw_metadata['translated_title']` 誤塞裸 str、而 `upsert_paper` L231 `.get('value')` / web_server SHADOW-HOTFIX-2 L714 `['value']` 全鏈期望 metadata_extractor **三欄 dict** → 影子寫庫 AttributeError〔P1-P4 全綠但 Paper row 未建、前端不顯示；A 軌不受影響〕；寫入端改 `{value, source, confidence}` + `run_phase4` 讀取端 dict 取 value〔str 向後相容〕+ test_hf2 格式契約斷言 + **test_hf1b 與 upsert L231 完全同式消費測試**〔堵 HOTFIX-1 測試盲區〕；`# === [PIPE-SLIDES-HOTFIX-1b ...] ===` 包裹 + 2 .bak；29 passed、全套件 585 passed | `1a2ec98` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md`
> **動因**：HOTFIX-1（`f933e54`）commit 後 baron 影子實測 log 爆 `'str' object has no attribute 'get'`（06:45、ALi 件）。
> **流程教訓**：HOTFIX-1 test_hf2 只測 rag_indexer 傳參、未測旁路值格式契約＝盲區；1b 以「與消費端完全同式」測試堵死。
> **⚠️ baron E2E**：影子重傳 → log 無 AttributeError、前端顯示該件且標題=中文譯題+(測試)；golden 維持原計畫＝1b 落地後一次首捕 slides。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕

### BE-Hotfix PIPE-SLIDES-HOTFIX-1 — B 軌簡報三缺陷緊急修補（同句多譯/譯題未接/段落黏連）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1 | `pipelines/slide_pipeline.py` 三點最小修：**F1 `_strip_title_echo`**〔P1 原文層去標題回聲、cap 2、選 C；Vision 忠實轉錄使頁標題同入 title 欄與 content 首行→P3 兩欄各自翻譯→同句雙譯相鄰（實件 p1/p6×3/p8/p16）；title 欄不動 key 契約零影響〕+ **F2 P4 接譯題**〔選 B 零增量 LLM：複用 P3 既有封面譯題穿 raw_metadata 旁路→run_phase4 translated_title+影子 (測試) 綴；償還 C5 暫同取、web_server 零改〕+ **F4 移植 `_normalize_paragraph_breaks`**〔resume PARA-HOTFIX-1 私有重建不跨策略 import；正文裸單 \n soft break 黏段潛伏→pipe-table-safe 升級、zh/en 對稱〕+ **F3 並列密度顯式不修**〔選 C：BM25 受益、頁間零記憶「首次」跨頁無法定義、列觀察項〕；`# === [PIPE-SLIDES-HOTFIX-1 HOTFIX-1 ...] ===` 包裹 + 2 .bak + 4 回歸測試〔回聲剔除/P1 接線/譯題穿線/段落正規化端到端〕；28 passed（既有 24 零紅）、全套件 584 passed | `f933e54` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md`（baron 拍板 1C/2B/3C 不修/4 移植）
> **動因**：PIPE-SLIDES 收官後 baron A/B 軌同件實測（ST 簡報、兩列印實件）——B 軌四大目標全中（雙 Caption 0/標題乾淨/並列/覆蓋全）但餘三缺陷。
> **⚠️ 行為變更 + golden**：F1/F4 改 B 軌 final、F2 改 rag_tree 譯題 → **slides golden 建議本 hotfix 落地後一次首捕**（`golden_baseline.py capture slides --force`、免捕兩次）。〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
> **⚠️ baron E2E**：影子重傳 ST 件 → p1 單一標題/p6 僅 1 次/前端列表顯中文譯題+(測試)/table 不破碎/引用 p{N} 不變。

### BE-Refactor PIPE-SLIDES SlidePipeline簡報策略管線（PIPE 縱向五路第 2 路·原 PIPE-VISUAL 改名）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 骨架與註冊：`@register('slides')` + 四方法 strict stub + `rag_char_threshold=3` + `__init__` import〔C7-hotfix 教訓〕+ 4 分派測試 | `31dab5a` |
| C2 | P1 每頁存圖與視覺解析：fitz 整頁存圖 page-{N}.jpg〔自建零 A 軌 import〕+ Vision temp=0〔§1.3.1、prompt 含 cell 禁 ###〕+ 條件滾動〔Q1 預設關〕+ 封面判定→raw_metadata/title fallback 檔名 + 跨頁統計去重〔Q2 ≥60% 非封面頁+log〕→ IngestionMetadataSpec；6 測試 | `941eed7` |
| C3 | P2 六步與頁 key 契約：統一六步〔①順產 raw_domain / ②順產缺失頁標題回填 / ③LCC(context=摘要) / ④Glossary 級聯·交易外 / ⑤DEEP_THINK 翻摘要雙用 / ⑥批次翻頁摘要〕+ **`page_key()`=`p{N:02d}_{原文頁標題}` 單一實作點** + 三安全鎖；4 測試 | `f8a24d7` |
| C4 | P3 逐頁翻譯與排版還原：三欄並行〔RESUME-PERF-1 範式、單欄退原文〕+ **alt 對齊雙 Caption 物理根除**〔渲染零 *圖表：* 段〕+ _SLIDE_CONSTRAINTS〔Q4〕+ rag_sections 旁路〔summary_key=page_key、同頁合併 Q3 策略側〕+ zh 路 + fallback〔Q5〕+ 不渲染 meta header；5 測試 | `4d7684c` |
| C5 | P4 RAG 接線：run_phase4 呼共用 rag_indexer.index〔同 key 直餵、四產物、≥3、失敗拋出不阻 reading_ready、零 rag_processor〕；四 Phase 全落地；2 測試 | `dbf90bd` |
| C6 | 測試補全（業務碼零改）：**§7.2 key-changing 整合測試**〔真實 P2→P3〔FakeTranslator 真改寫頁標題〕→真實 build_chunk_markdown、雙斷言接縫不變式——HOTFIX-1 類退化必紅〕+ Q2 小樣本邊界 + 合約① forbid 防線；24 測試、全套件 580 passed | `cb5e2bd` |
| C7 | Checkout 收官：Conformance 五維度全綠〔plan U1-U11 / tasks §6.1-§6.6 / 不可動〔A 軌/rag_indexer/合約〕/ 提示詞 8 份稽核 / msg 完整〕+ **§7.2 整合測試存在且通過（正面達標、免豁免）** + 母 plan v10 同步〔§8.5 PIPE-VISUAL→PIPE-SLIDES 改名+✅+Bypass 句更正、補註⁷、**升格 plans/ 入版控**〕+ baton 一次性歸檔 + TODO 結案 + hash 全量自癒 | `eb23bd5` |

> **修法依據**：`.claude-logs/plans/2026-06-11_PIPE-SLIDES_SlidePipeline簡報策略管線_plan_v1.md`（v1.1、八 OQ 全結清：Q1 滾動預設關/Q2 去重 ≥60%/Q3 合併策略側/Q4 constraints/Q5 fallback/Q6 改名/Q7 逐頁定案/Q8 golden 改善豁免）
> **設計基礎**：resume 第 1 路全經驗零學費繼承（六步/旁路/key 契約/並行/四產物/§1.3.1）+ A 軌實件品質模擬（ST 簡報 18 頁）實證三病灶——雙 Caption（`slides_processor.py:155`）/ Vision 零 temperature / 表格 cell 塞 ###——分別以 alt 對齊、temp=0、constraints 根除。
> **接縫契約**：key=`p{頁序:02d}_{原文頁標題}`（頁序物理唯一防 HOTFIX-2 重複標題覆蓋）、P2 產/P3 帶/P4 取三方同基準、`page_key()` 單一實作點；§7.2 整合測試含真 key-changing transform 鎖死。
> **⚠️ baron E2E 運維（非 commit）**：影子上傳 ST 實件 → 圖文對照無「圖表：」段/無頁頂重複總述、toolbar 雙語摘要、重跑兩次輸出穩定（temp=0）、引用「《簡報名》> p{N} 標題」、`#sst` 跨文件；B 軌 golden 另捕（`golden_baseline.py capture slides --force`、與 A 軌 diff 走改善豁免=Q8）。

### BE-Refactor LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `rag_retriever.py` `set_loader` + `_get_vector_store` 完全 miss 自載〔第三層、loader 未設＝現況回 None 向後相容〕+ `is_ready` loader-aware〔U1/U7、防全清繞過〕+ tests/test_lazyload_multi.py 5 測試〔含整合 6 篇只註冊 1〕| `8893ad1` |
| C2 | in-memory cache 併發鎖純硬化·**單一共享 RLock**〔retriever 持鎖、ai_core `_paper_cache` 共用 `retriever._lock`、**loader 呼叫在鎖外防 AB-BA**〕包全 mutation（U8、修正 tasks §4.2 兩鎖之 load_paper_cache↔_get_vector_store 相反鎖序隱患）+ 並發測試〔不死鎖 timeout〕；行為不變、全套件全綠＝回歸網 | `9849600` |
| C3 | `web_server.py` 啟動 lifespan 接線 `set_loader(λ o,p: load_paper_resources)` + `settings.py` `RAG_MAX_CACHE` 5→100（U2/U4 純加法、只動啟動段不碰端點）→ **跨文件修復 LIVE** | `c5b0c31` |
| C4 | 記憶體釋放策略：`_release_caches_except_active`〔全清該 owner、唯一豁免 active_streams done==False、快照 keys 再清、gc、ai_core None 防呆〕+ `/content` 換篇 gate〔F1 語言切換同篇不放〕+ `/upload` 開關〔`RELEASE_ON_UPLOAD`=on 騰 RAM 給 MinerU〕+ ai_core remove_paper docstring 修（U5/U9/P4）+ 3 釋放測試 | `6c0e8d2` |
| C5 | Checkout 收官：Conformance 六維度驗收全綠〔plan v5 U1-U9 / tasks §6 grep+pytest〔10+全套件 556 passed〕/ **§7.2 整合測試〔key=paper_uuid 穩定、key-changing N/A〕** / 不可動〔C3/C4 hunk 不重疊〕/ 提示詞稽核 / msg 完整〕+ baton 一次性 mv 歸檔〔plan v1-v5→plans/ + tasks→tasks/ + C1-C4 報告→executions/〕+ TODO 結案 + hash 全量自癒 | `30e024e` |

> **修法依據**：`.claude-logs/plans/2026-06-09_LAZYLOAD-MULTI-1_跨文件lazyload接縫與記憶體釋放_plan_v5.md`（v1-v5 五版保留作 §1.9 軌跡；v3 為 Antigravity 平行 review 版；五輪收斂：v1 初稿 → v2/v3 Antigravity〔rag_tree handoff / is_ready / DB 安全 / shadow〕→ v4 合併〔baron 釋放決策 + Claude P0 併發鎖 + 校正 DB≠cache 兩層〕→ v5 三軸深 review〔前端 F1 / 資料傳導 / 記憶體 M1〕+ mermaid）
> **真因**：API-PERF C3 廢啟動 preload、chat 端點只 lazy-load 當前 paper → `retrieve_multi` 對未載 tagged 篇 `_get_vector_store` 回 None 靜默跳過 → `#cv 比較` 只召當前篇（log 證 candidates=14 全吳焴倫、其餘 5 篇 0）；**非 RAG-MULTI-1、非模型/regen**（28 篇全 -001、獨立載入都滿分）。
> **治本**：③ retriever 自載咽喉〔一鎖點修單篇/多篇/attach〕+ is_ready loader-aware + 單一共享 RLock〔③ 把寫推進 to_thread worker〕+ 釋放策略〔換篇/上傳全清跳過 active_streams + gc〕；cap 5→100、砍 60min TTL。
> **⚠️ baron E2E 運維（非 commit）**：重啟 → 直接 `#cv 比較這幾位候選人的學歷背景` → 涵蓋全 6 位 + 引用顯《文件名》；log chosen ≥5 種 pid；並發/串流中切篇不斷/語言切換不放/上傳釋放 RAM 降/shadow pid 入 chosen。

### BE-Refactor RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `settings.py` 廢 `RAG_MULTI_TOP_K`、立 `RAG_MULTI_FLOOR_K`(2)/`RAG_MULTI_MAX_CHUNKS`(15)〔C2 後同 commit 廢 TOP_K〕| `5b9477a` |
| C2 | `rag_retriever.py` `retrieve_multi_with_context` 廢全域 top-k 飢餓 → **每篇保底覆蓋**〔`effective_floor = min(RAG_MULTI_FLOOR_K, max(1, cap//N))`、不足全拿、補位池排除已保底、N>cap 按各篇最高分取前 cap 篇各 1〕+ `top_k` 參數改 cap override + import 去 TOP_K；更新既有 hashtag 路由測試 | `82b95b1` |
| C3 | `prompt/ai/ai_character_prompt.txt` 引用段禁 bare `[N]`、只留《文件名》「章節」；共載 `ai_explain_prompt.txt` 已查無反向 [N]〔未改〕| `b5f9ce4` |
| C4 | 新建 `tests/test_rag_multi.py` 11 測試〔保底/不足全拿/小N不暴漲〔min(floor_k,…)〕/cap/N>cap最高分截斷/補位去重/0候選跳過/cap override/混型book不壓resume/單篇不退化/禁[N]〕；真實演算法驗證〔不 mock retrieve_multi 本體〕；全套件 546 passed | `01d1270` |
| C5 | Checkout 收官：Conformance 五維度驗收全綠〔plan v3 U1-U7 / tasks §6 grep+pytest / 不可動 / 提示詞稽核 / msg 完整性〕+ baton 一次性 mv 歸檔〔plan v1/v2/v3→plans/ + tasks→tasks/ + C1-C4 報告→executions/〕+ TODO 結案 + hash 全量自癒 | `e88c304` |

> **修法依據**：`.claude-logs/plans/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_plan_v3.md`（v1/v2/v3 三版保留作 §1.9 軌跡；三輪 review 收斂：v1 初稿 → v2 Antigravity 五項+Q2 公式修正 → v3 self-review 三點收緊）
> **真因（log 鐵證）**：`retrieve_multi_with_context` 全域 top-k=7 飢餓 → 6 篇被擠成 2 人代表（李宗原 A+B軌 佔 5/7、吳焴倫碩士漏召）→ 比較類查詢漏掉有資料文件；另 LLM 多吐無依據 `[1][2][5]` 引用。
> **治本**：每篇保底覆蓋〔保證有候選之 paper 不 0 代表〕+ cap 防爆 + 禁 bare [N]；`retrieve_multi` 無 doc_type = **五路通用**。
> **⚠️ 刻意不做（U7）**：shadow 不過濾（維 B軌可見性）→ 同人 A+B軌 重複代表為設計副作用、非 bug；內容去重列後續。
> **⚠️ baron 運維**：測試機影子 E2E 驗 `#cv 比較` 涵蓋多人（含吳焴倫碩士）、答案無 bare [N]、`grep [retrieve_multi].*chosen` 含先前 0 代表 paper。

### FE-Hotfix CHAT-EXPORT-HOTFIX-1 — 對話下載在 Dia 卡 8/8 不結束（導覽式下載 → fetch+blob）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1 | `static/index.html` `export-btn` handler `onclick=()=>`→`async()=>` + 移除 `window.location.href` 導覽式下載 → **fetch→blob→`<a download>`**〔含 !res.ok/404/catch 錯誤處理、`a.download={paper_id}_chat.md`、`URL.revokeObjectURL`〕、`// === [CHAT-EXPORT-HOTFIX-1 START/END] ===` 包裹、保留空對話防護；真因＝Dia 對「主框架導覽去 attachment URL」收尾異常〔配常駐 SSE〕→ download chip 卡 8/8 不結束，Safari/Chrome 正常；後端 export 端點已證正確〔真 uvicorn+curl content-length 8004/無 chunked/Safari 正常〕→ 非後端非 nginx；fetch+blob 不依賴導覽語意、瀏覽器無關全收尾；FE-Hotfix 僅前端 +26/-2、零 .py、後端零改；3 條靜態 grep 全綠〔location.href.*chat/export 無命中 / createObjectURL 命中 / START/END 各 1〕| `17cbf4f` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-08_CHAT-EXPORT-HOTFIX-1_hotfix.md`
> **變因隔離**：同機同後端，Safari ✅ / Dia ❌ → 唯一變因＝瀏覽器；後端真 wire 測試（curl content-length 8004、無 chunked）反證正確 → 純前端導覽式下載寫法。
> **⚠️ baron 驗收**：Dia + Safari 各下載一次對話 → 皆「下載完成、chip 收尾」、檔名 {paper_id}_chat.md、內容與 Safari 既有下載一致；空對話防護不變。
> **後續（非本 hotfix）**：若其他下載點也用 `window.location.href` 可抽 `downloadViaBlob(url, filename)` helper 統一（本 hotfix 只修對話下載受災點、不夾帶）。

### DOC-Refactor WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `WORKFLOW_SOP.md` 新增 §7 跨 Phase 接縫契約〔§7.1 producer/consumer/key 同基準 + **worked example 三欄表（修正版 RAG-ASYNC #1）** + 反例 / §7.2 收官前整合測試〔含 key-changing transform、純 mock 同 key 不認、Checkout 必驗、顯式豁免〕〕+ §3 強制規則整合測試前置一行 + §4.2 A6〔6 項〕+ §99.1 重複防護 + §0/§99 改版觸發 §1–§7 + §99.2 v4 | `2e4d4c9` |
| C2 | `template_plan.md` 升格 plan 結構 SSOT：新增 §4 跨 Phase 接縫契約〔三欄式範本 + 交叉引用 §7〕+ §5 變動風險與相容性評估〔對齊 framework §4.1 #5〕+ 重編號原 §4-§7→§6-§9 + §0/§99 §1–§9 + §99.2 v2；保留 §2「不寫實作」精煉哲學 | `386c1ce` |
| C3 | `framework §4.1` 計畫檔結構契約 自列八章節 → 改引用 `template_plan.md` 為 plan 結構 SSOT〔保留「不寫程式碼純分析」哲學句 + 接縫契約唯一源引用 §7〕、不刪 §4.2 執行報告契約 + §99.2 v4 | `f14dcd9` |
| C4 | Checkout 收官：Conformance 五維度驗收全綠〔目標規格 U1-U5 / tasks §6 grep / 不可動 / 提示詞稽核 / **整合測試豁免聲明**〕+ baton 一次性 mv 歸檔〔plan v1/v2/v3→plans/ + tasks→tasks/ + C1-C3 報告→executions/〕+ TODO 結案 + hash 全量自癒 | `6d11f13` |

> **修法依據**：`.claude-logs/plans/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_plan_v3.md`（§8 Q6/Q8 定案、v1/v2/v3 三版保留作 §1.9 軌跡）
> **動因/治本**：RAG-ASYNC #1 接縫缺陷——plan 未凍結跨 Phase key 契約 + plan→tasks→6 run→Conformance 全是單元/grep 尺度、無整合測試 → 6 commit + Conformance 五維度全綠仍漏（C5 白做）；另 template_plan↔framework §4.1 長期 doc-drift。
> **三大條款生效**：① WORKFLOW_SOP §7 跨 Phase 接縫契約（plan 必凍結 handoff producer/consumer/key 同基準、附 worked example）② 收官前跨 Phase 整合測試（含 key-changing transform、Checkout Conformance 必驗、顯式豁免）③ template_plan 為 plan 結構唯一 SSOT、framework 改引用（消滅 drift）。
> **整合測試豁免**：WORKFLOW-3 自身 DOC-Refactor + 無 code handoff，依 §7.2 + plan Q2-Q3 顯式豁免、C4 報告明載（立規者自身不適用該規）。
> **v3 重評（「對專案有幫助就做、不拖延」）**：template↔framework drift 升級為 SSOT 根治（非只補佔位、刪 WORKFLOW-4 候選）+ 認知負荷補 worked example；進行中分支以下一 Checkout 為界、硬 gate 顯式豁免維持。

### BE-Hotfix RAG-ASYNC-HOTFIX-3 — zh 來源履歷 P3 改建 per-section rag_sections（#4·選 B）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3 | `pipelines/resume_pipeline.py` `run_phase3` is_zh 分支：`_single_container_sections`→**有 section 時走 `ctx.ingestion.tiles` 不翻譯、複用 `_collect_render_slots`+`_collect_rag_sections(translate=False)` 建 per-section rag_sections**〔text=原文 zh、summary_key=原文標題 path〕、無 section 退單一容器兜底；zh「原文＝譯文」故 summary_key 與 P2 section_summaries key、#1 chunk node_key **天然對齊**（無跨譯落差）；根治 is_zh 路只做 zh_text=full_text、順帶跳過結構化 → rag_sections 單一容器 → zh 履歷 P4 chunk 不依 section 切、size-cap 切任意 token 窗、召回粒度低於 en（不對稱、非崩潰故易忽略）；不改 zh_text=full_text〔final_zh byte 不變〕/en 主路/degraded；`# === [RAG-ASYNC-HOTFIX-3 HOTFIX-3 START/END] ===` 包裹 + 2 .bak + 補 3 測試〔zh per-section / zh 無 section 兜底 / 接 #1 摘要對位〕；resume 42 passed〔en 主路不退化〕、全套件 535 passed（僅 env flake）| `6794331` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md`
> **真因（流程）**：RAG-ASYNC plan v2 只設計 en→zh 主路 per-section chunking、**未規範 is_zh 路結構化**；C6 給 is_zh「單一容器 fallback」（合理但粗、當時聚焦 chunks=1 主修）。治本歸 WORKFLOW-3（各路 edge path 需 plan 規範 + 收官前覆蓋測試）。
> **依賴 #1（已落地）**：用 `_collect_render_slots` 的 slot `key` 與 `_collect_rag_sections` 的 `summary_key`（#1 引入）；zh 路「原文＝譯文」為 #1 修法最乾淨受益者（三 key 天生一致）。
> **⚠️ 行為變更 + 重捕**：改 zh 來源履歷 chunk 邊界（單一容器→per-section）→ 衝擊該類 golden D2/D3；**zh 來源 golden 須重捕**（`tools/golden_baseline.py capture resume --force`、en 不需）。
> **RAG-ASYNC 體檢 5 項收束**：#1/#2/#4 已落地、#3 併入 #1；**#5 聯絡資訊**另立 CHAT-STRUCT-1（plan 待拍板）；degraded en per-section 另議。

### BE-Hotfix RAG-ASYNC-HOTFIX-2 — B 軌補產 rag_tree.json（#2·選 B 完整版）

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-2 | `processor/rag_indexer.py` 新增 `build_rag_tree`+`_walk_tree`（依 P3 ctx.rag_sections 自建完整 rag_tree：**key_map key=B 軌 chunk Header〔=node_key、與 `_walk`/`build_chunk_markdown` 同式〕→`/sections/{i}/content/0`** + 巢狀節點帶 translated_content/translated_title/type=text/index）+ `index()` 加 `rag_tree_path/title/translated_title` 寫 `final_{paper}_rag_tree.json`〔IO try/except `logger.error(exc_info)` 優雅降級不阻斷交付〕+ module 補 `import json`；`pipelines/resume_pipeline.py` `run_phase4` 傳 `paper_manager.rag_tree_path` + `ctx.ingestion.title`；根治 RAG-ASYNC C4 B 軌只產 FAISS+paper_chunks+index_meta、未產 rag_tree.json → `rag_retriever.load_rag_tree` 回 {} → 章節引用/paper_title 前綴/公式相鄰全降級（A 軌有、B 軌無、非崩潰故易忽略）；零依賴 A 軌、**rag_retriever/ai_core 檢索載入端 100% 零改**；`# === [RAG-ASYNC-HOTFIX-2 HOTFIX-2 START/END] ===` 包裹 + 4 .bak + 補 4 測試〔key_map↔chunk Header 不變式 / 節點 translated_content / run_phase4 傳路徑+標題 / **retriever 對接整合「{paper_title}>{section}」非空引用**〕；rag_indexer+resume 57 passed、全套件 532 passed（僅 env flake）| `300feb1` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md`
> **真因（流程）**：RAG-ASYNC plan v2 §U5 ④ 輸出列「FAISS+paper_chunks+index_meta」**漏列 rag_tree.json**（SPEC §1.4 含 tree_json_file）；C4 conformance 只驗 load_vector_store+similarity_search（不需 rag_tree）→ 沒照出。治本歸 WORKFLOW-3（④ 輸出完整性清單 + 收官前整合測試）。
> **依賴**：建於 RAG-ASYNC-HOTFIX-1（#1 node_key 語意已穩定）之上；key_map key＝chunk Header＝node_key 與 #1 summary_key 同源「穩定 key」。
> **邊界（誠實）**：重複葉標題 key_map 後者覆蓋（履歷罕見、根治需 chunk_key 改路徑、與 #1 同源議題另排）；公式相鄰對履歷 inert（academic/book 才生效）。
> **⚠️ 不衝擊 golden**：只新增 rag_tree.json 旁檔、不動 FAISS/chunk → 無需重捕向量；baron 影子 E2E 觀察 references 顯示「《姓名》> 章節」即可。
> **後續分流**：#4 zh per-section（HOTFIX-3 doc 待 Run、依賴 #1）/ #5 聯絡資訊（CHAT-STRUCT-1 plan）。

### BE-Hotfix RAG-ASYNC-HOTFIX-1 — section_summaries 跨譯 key 對位失效 + dead code

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1 | `pipelines/resume_pipeline.py` `_collect_render_slots` title slot 帶**原文標題 path** `key`（加 `path_prefix` 遞迴穿線、slot 翻譯前收集故 text=原文、與 P2 `_collect_summary_targets` node_key 同基準）+ `_collect_rag_sections` 譯後 section 存 `summary_key`（原文 path、譯後 title 另存供顯示）；`processor/rag_indexer.py` `_walk` 以 `summary_key` 首選查節點摘要（無則 fallback node_key/title 向後相容 C3/C4）；移除無 caller dead `_load_index_meta`〔#3〕；根治 RAG-ASYNC C5 section_summaries（原文 key）vs P3 譯後 title（譯文 key）vs P4 譯後 node_key 查找三方不一致 → Chapter Summary 永不進 chunk、Strategy B 靜默退化成 A、C5 白做（非崩潰故影子 chunks≥20 誤判成功）；`# === [RAG-ASYNC-HOTFIX-1 HOTFIX-1 START/END] ===` 包裹 + 4 .bak + 補 3 測試〔跨譯查找 / 無 key fallback / **P3→P4 接縫整合測試（FakeTr 真翻譯+巢狀 path）**〕；rag_indexer+resume 53 passed、全套件 528 passed（僅 env flake）| `300feb1` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md`
> **真因（流程）**：plan v2 §U3/D1 只寫「key 對位巢狀樹」、**未凍結跨 Phase 接縫 key 契約**（key=何物 + P2 產/P3 帶/P4 取須同基準）；C5/C6 各自孤立實作（原文 key/譯文 title）單元皆自洽全綠；**全程無 P2→P3→P4 串接 + 真翻譯器整合測試** → 6 commit + Conformance 五維度全綠仍漏。治本歸 WORKFLOW-3（plan v3 已產）。
> **⚠️ 行為變更 + 重捕**：B 軌履歷召回改變（Chapter Summary 進 chunk）→ 衝擊 golden D2/D3；**Flip/結案前須重捕 resume 單路**（`venv/bin/python tools/golden_baseline.py capture resume --force`）。
> **後續分流（backlog）**：#2 rag_tree（RAG-ASYNC-HOTFIX-2 doc 待 Run）/ #4 zh per-section（HOTFIX-3 doc 待 Run、依賴本 #1 slot key）/ #5 聯絡資訊（CHAT-STRUCT-1 plan）。

### BE-Refactor PIPE-RESUME ResumePipeline策略管線（PIPE 大改版縱向五路絞殺第 1 路）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `pipelines/resume_pipeline.py` 骨架 + `@PipelineFactory.register('resume')` 註冊 + `DocumentStrategy` 四方法 stub + `rag_char_threshold=3` + interim `_raw_meta` 穿線容器 | `f3d4e41` |
| C2 | 實作 `run_phase1` 全鏈 P1 Ingestion（`ResumeProcessor` Vision + Metadata Stage A + `DocAnalyzer` + md2json/json_process/tiling 產 Tiles）→ IngestionMetadataSpec〔title=candidate_name / source_lang 啟發式 / 零 Abstract/LCC/Glossary〕；phone/email/domain 暫存 `_raw_meta`；**baron 拍板**擴 `PipelineContext` 加 pdf_path/owner_id + web_server 影子派發傳值 | `d7edcd9` |
| C3 | 實作 `run_phase2` 四步循序自癒：①`normalize_to_lcc(raw_domain, context_text=履歷全文)` ②LLM 生成原文 `abstract` ③`GlossaryManager` 旗標閘門自癒〔query_cascade→缺詞 extract_terms〔注入摘要+LCC〕→upsert 冪等、LLM 交易外〕④`Translator(DEEP_THINK)`→`translated_abstract` + `lcc→Domains.name` PK 唯讀免交易 → GlossaryReadySpec | `48aa5df` |
| C4 | 實作 `run_phase3`：`InjectionContext(doc_type='resume')` 100% Bypass 整份 `Translator.translate(NORMAL,content)`〔不切 Section/不開 Sliding Window〕+ md_restore 純樣板渲染〔廢除 extra_info、嚴禁 AI Questions/Summary〕→ final_zh/final_en → BilingualMarkdownSpec〔translated_abstract 沿用 P2〕 | `8971a19` |
| C5 | 實作 `run_phase4`：複用 `RagProcessor._create_vector_store`〔`_is_chunk_meaningful` 門檻 ≥3 保技能詞/email/phone/url + FAISS + paper_chunks 批量寫庫 + index_meta〕；Embedding 於交易外、paper_db_id None 優雅降級；異常拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready → RagDbSpec | `e8a7429` |
| C6 | 新建 `tests/test_resume_pipeline.py` 15 測試（策略分派 + P1-P4 契約、mock LLM/Embedding 隔離）；全套件 480 passed | `fabb114` |
| C7 | Conformance 三維度驗收（目標規格 U1-U5 / 測試 §6 / 不可動清單）+ baton/ 一次性歸檔（plan_v1〔保留 _v1〕/tasks/C1-C7 報告）+ 歷史全量 Hash 自癒 + 結案 | `a644e48` |
| C7-hotfix | 緊急熱修復：`pipelines/__init__.py` 補 `from pipelines import resume_pipeline` 觸發 `@register('resume')`——修復 runtime 路徑無人 import 策略致 `get_strategy('resume')` 回 NullStrategy、影子上傳 P1 拋 NotImplementedError 阻斷；factory._registry 含 'resume' 驗證通過、全套件 480 passed | `d2e0af2` |
| C8-hotfix | 緊急熱修復：`web_server.py` `run_pipeline_shadow` 影子完成後補 `paper_manager.upsert_paper` 寫 Paper row——修復影子 P1-P4 全綠生實體檔但 `run_pipeline_shadow` 漏寫庫致 Paper row 未建、`list_papers`(讀 DB) 撈不到、前端不顯示 (測試) 列；校正版 str 絕對路徑 + ctx.bilingual 守衛 + doc_type-agnostic 五路通用；test_pipe_scaffold 5 passed、全套件 480 passed | `b0713e7` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8、四輪對接稽核定稿）
> **PIPE 對齊**：PIPE 縱向五路絞殺**第 1 路**；ResumePipeline 四 Phase（P1 Ingestion / P2 Glossary & Context Prep / P3 Translation & Restore / P4 Async RAG）全落地；消費 DomainNormalizer LCC + GlossaryManager 級聯自癒 + 呼叫 Translator 雙模式；對齊 PIPE-CORE 落地 ABC `run_phase1..4` / 四凍結合約 / PIPE-SCAFFOLD 影子機制。
> **baron 拍板（AskUserQuestion）**：① C2 擴 `PipelineContext` 加 pdf_path/owner_id（首落地隨 PIPE-RESUME、五路共用基建）；② P1 全鏈編排（忠實 PIPE-SPEC §1.1①「Tiles 在 P1 產出」）。
> **defer / Flip 阻擋**：`custom_metadata` 履歷專屬欄暫存 `_raw_meta` 穿線（tasks §9 硬前置）；P1 凍結合約未全域擴 `custom_metadata` 前僅影子 B 軌驗證、不得正式 Flip 線上流量。

### BE-Refactor PIPE-RESUME v9 影子整合與規格同步（PIPE 縱向五路第 1 路·影子保真整合）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Sync System Specs：plan_v1 + 母 plan v10 + PIPE-SPEC 三文件就地同步（`raw_metadata` 旁路欄登記 / P3「翻譯策略隔離原則」/ Phase2 摘要先行步序 / C7-C8 hotfix 史 / P1 影子後綴規格 + Flip Cleanup 待辦）；嚴禁動 Python 業務代碼 | `b97958b` |
| C2 | P1 + Context：`pipelines/context.py` 加 `raw_metadata: Dict[str,Any]={}` 狀態欄 + `run_phase1` 寫入整包原始 meta（含 regex phone/email）+ `_shadow` paper_id → title 加綴 `(測試)`（前端列表肉眼可辨、不入內容） | `e64417a` |
| C3 | P2 步序與讀取對齊：`run_phase2` ①摘要先行→②LCC（跨路統一、功能等價）+ `raw_domain` 改讀 `ctx.raw_metadata`（經 `_meta_value`）+ 廢除 `self._raw_meta` 實例暫存（`ctx.raw_metadata` 為唯一穿線載體） | `f239721` |
| C4 | P3 Business Constraints：模組常數 `_RESUME_CONSTRAINTS`〔公司/產品名保留・Email/電話/URL 原樣・技能詞英文・專利/期刊原文+對照〕+ `run_phase3` `InjectionContext(constraints=…)` 逐路注入共用 Translator（PIPE-SPEC §1.2.3.1 翻譯策略隔離） | `9bbad2d` |
| C5 | Shadow DB Fidelity：`web_server.py` `run_pipeline_shadow` C8-hotfix 影子寫庫 `meta_dict` 改優先讀 `ctx.raw_metadata` 組整包 `metadata_json`（對齊 A 軌 `upsert_paper(self._metadata)` 保真）+ title 沿用 `ctx.ingestion.title`〔含 (測試)〕+ 空值防禦 fallback；無裸 commit、A 軌 byte 不動 | `9291c5c` |
| C6 | Unit Tests：`tests/test_resume_pipeline.py` 修復 C3 遺留 2 個 `_raw_meta` 紅燈（改 `ctx.raw_metadata`）+ 追加 4 v9 契約測試（P1 影子後綴 / P2 摘要先行步序 / P3 constraints 注入 / C5 影子寫庫保真）；resume 19 passed、核心 pipelines 25 passed | `4e15905` |
| C7 | Checkout：Conformance 三維度驗收全綠（目標規格 / tasks §6 pytest+grep〔resume 19 / 目標 44 / 全套件 483 passed〕/ 不可動清單 git 證據）+ SOP 核查 + 提示詞 8 份稽核 + msg 完整性 + baton 一次性歸檔（plan_v1/tasks/C1-C7 報告 → plans//tasks//executions/，母 plan v10/PIPE-SPEC 就地 git add） | `36db1cf` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11、六項 + v10 P2 步序 + v11 表格保留）
> **PIPE 對齊**：原 PIPE-RESUME（C1-C7 已收官、四 Phase 落地）後的**影子保真整合批次**——將 raw_metadata 旁路穿線、P1 影子標題後綴、P2 摘要先行、P3 翻譯策略隔離、C5 影子寫庫保真五者整合；消費既有三大真理源 + PIPE-SCAFFOLD 影子。本批次 C1-C7 為 v9 內部序，與原 PIPE-RESUME C1-C7（上方表）區別。
> **流程註**：C7 驗收時 baron 已逐一 commit C1-C6，依框架 §2.2 回填 git log 實證 hash；C7 自身 `36db1cf`（SHADOW-HOTFIX-2 時自癒回填）。
> **Flip 阻擋（延續）**：P1 影子後綴 + 影子寫庫僅供 B 軌驗證；正式 Flip（PIPE-FLIP）待五路全通 + Golden Diff 0% + custom_metadata 凍結合約全域擴充（母 plan v11 Cleanup 含「移除 P1 影子後綴」）。

### BE-Hotfix PIPE-RESUME TILING-HOTFIX-1 — TextTiling Embedding 速率超限 (429) 批次化修復

| Commit | 內容 | Hash |
|---|---|---|
| TILING-HOTFIX-1 | `processor/tiling_processor.py:425` 分塊 embedding 由逐筆 `[embed_query(b) for b in blocks]` 改批次 `embed_documents(blocks)`〔請求 1/32 + 線性退避 15s/30s + 重試耗盡退回逐筆 + 順序保證〕，根治 TextTiling 長文/併發 429 RESOURCE_EXHAUSTED 阻斷與全套件 `test_tiling_paragraph` 併發 flaky；`# === [PIPE-RESUME TILING-HOTFIX-1 START/END] ===` 包裹僅此行；tiling 三套件 15 passed、全套件 484 passed（429 全綠、僅剩 env flake） | `702347a` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_hotfix.md`
> **⚠️ 行為變更**：`task_type` 由 `RETRIEVAL_QUERY`→`RETRIEVAL_DOCUMENT`（對 Document-Blocks 語意更正確），向量值略異 → TextTiling 分段邊界或微幅位移。**PIPE Flip/結案前 baron 須於 MinerU 重捕五路 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`、容差 D2≥0.95/D3≥0.90），未重捕前既有基準 diff 會全面誤報。
> **flaky 認定修正**：先前 PIPE-RESUME C5–C7 全套件 `test_tiling_paragraph` 偶發失敗的真因即此 429（非純環境性 flaky），本 hotfix 一併根治。

### BE-Hotfix PIPE-RESUME SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復

| Commit | 內容 | Hash |
|---|---|---|
| SHADOW-HOTFIX-2 | B軌三處「移除矛盾、交回母提示詞」：①`web_server.py` 影子寫庫補綴 `translated_title` ` (測試)`〔前端列表優先取 translated_title、防漏顯〕②`processor/translator.py:40` STYLE_HINTS['resume'] 移除「公司名」③`pipelines/resume_pipeline.py:109` `_RESUME_CONSTRAINTS[0]` 改「產品名保留原文」——公司/機構交回母提示詞 `content_translate_prompt.txt` L5 統一「翻譯 (原文)」，消除 ②⑤ 與母提示詞反向覆寫的矛盾（公司沒翻 + doubling 源頭）；不改 `translate_processor.py`（A軌棄修）/母提示詞；`# === [PIPE-RESUME SHADOW-HOTFIX-2 START/END] ===` 包裹 + 補 2 回歸測試；resume 21 / translator 8 / 相關 19 passed、全套件 486 passed（僅 env flake） | `3d2778a` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_hotfix.md`（v2 三處「移除矛盾」版）
> **根因**：B軌履歷翻譯指令三層打架——母提示詞 L5「機構翻譯附原文」vs ②STYLE_HINTS / ⑤constraints「公司保留原文」；②為 A軌 STYLE_HINTS 逐字複製殘渣。移除 ②⑤ 矛盾後公司由 L5 統一翻譯。
> **⚠️ 行為變更 + 重捕**：B軌譯文內容改變 → 衝擊 D2/chunk；**Flip/結案前須與 TILING-HOTFIX-1 合併一次重捕 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`）。
> **保留意見**：學歷地點行錯亂 / doubling 殘留（U4 + 100% Bypass 整檔單發）屬 B軌 P3 架構問題，已立 `RESUME-P3` plan 另開任務、不在本 hotfix 硬修。

### BE-Refactor RESUME-P3 B軌履歷翻譯品質重構

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `resume_pipeline.py::_build_tiles` 履歷 opt-out TextTiling（直接以 JsonProcessor processed JSON 當 tiled、保全 `###` heading 結構、P1 不跑 embedding、源頭滅 429）| `aec1f6f` |
| C2 | `processor/translator.py` translate U4 加 `(ctx.doc_type or '') != 'resume'` 閘門——resume 停用 `。！？` 重切、保條列/日期/地點原行結構；其他文體等價 | `0efa7e8` |
| C3 | `run_phase3` 廢 100% Bypass → 逐 heading section 遞迴翻譯（標題/正文分流）+ pipelines/ 內私有還原（`_restore_sections_markdown`/`_restore_one_section`/`_translate_whole`/`_t`、**不耦合 A 軌**）+ source_lang zh* 不重譯；契約 BilingualMarkdownSpec 不變 | `52e0769` |
| C4 | `run_phase3` heading 退化偵測（`_is_heading_degraded`：heading 數<2 或單一 section 自身文字佔比>85%）→ warning + 降級整檔 `_translate_whole` fallback、保證交付契約 | `6658b48` |
| C5 | `tests/test_resume_pipeline.py` 修 C1 carryover（FakeMd 輸出含 section JSON 對齊 opt-out）+ 追加 5 測試（C1 opt-out / C3 逐 section 分流翻譯+無英文標題殘留 / 無 doubling / C4 單一巨 section fallback / 契約完備）；resume 26 passed、全套件 495 passed | `3a30394` |
| C6 | Checkout：Conformance 三維度驗收全綠（目標規格 U1-U8〔U6 待重捕量測〕/ tasks §6 pytest+grep〔目標 54 passed〕/ 不可動清單 git 證據）+ SOP 核查 + 提示詞 7 份稽核 + baton 一次性歸檔（plan_v1/tasks/C1-C6 報告 → plans//tasks//executions/）+ hash 全量自癒 | `a1d5d7f` |

> **修法依據**：`.claude-logs/plans/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_plan_v1.md`（§99.2 v3、OQ Q1/Q2/Q3/Q4/Q9/Q10 核准）
> **PIPE 對齊**：B軌（影子）P3 翻譯品質重構——廢「100% Bypass 整檔單發」、改逐 `###` heading section 翻譯+結構還原；履歷 P1 opt-out TextTiling（戰術、源頭滅 429）；resume 停用 U4 保行結構；heading 退化 fallback 兜底。消費既有 Translator/InjectionContext，**不耦合即將棄用的 A 軌 translate_processor**。
> **⚠️ 行為變更 + 重捕**：B軌履歷 Markdown 輸出改變（逐 section 重組）→ 衝擊 D2/chunk；**Flip/結案前須與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 合併一次重捕 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`）；U6 對齊度於重捕後 diff 裁決。
> **後續**：通用化各路 chunking opt-in 機制歸 `INFRA-3`（五路收完 + A軌死後）。

### BE-Hotfix RESUME-P3 HEADING-HOTFIX-1 — B軌履歷標題層級塌陷（全 h1、無階層）修復

| Commit | 內容 | Hash |
|---|---|---|
| HEADING-HOTFIX-1 | `pipelines/resume_pipeline.py` `_restore_one_section` 標題層級改由**遞迴深度**推算：`_restore_sections_markdown` 傳起始 `depth=0`、簽名加 `depth:int=0`、廢除恆=1 的 `level` 扁平死欄短路改 `level=min(2+depth,6)`〔頂層 h2、children 遞迴 `depth+1`、上限 h6〕；根治 C3 `_restore_one_section` 因 `level 欄 or heading_level 欄` 短路永取 1 → 全標題塌成 h1、無階層；`# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` 包裹 + 追加 `test_p3_heading_level_by_recursion_depth`〔3 層巢狀全 level=1 仍還原 ##/###/####〕；resume 27 passed、全套件 500 passed（僅 env flake） | `7c8a0da` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md`
> **真因**：processed JSON `level` 欄恆=1（扁平死欄、真實深度在 children 樹與 `heading_level`＝2+樹深度）；C3 `_restore_one_section` 寫 `sec.get("level") or sec.get("heading_level")`，因 `or` 短路先取恆真的 1 → 每標題都 `#`(h1)。改遞迴深度推算後等價 `heading_level` 但不依賴資料欄位。
> **⚠️ 行為變更 + 重捕**：改 B軌 `final_zh` 標題層級（`#`→`##`/`###`/`####`）→ 衝擊 golden D1/D2；**Flip/結案前須重捕 resume 單路**（`venv/bin/python tools/golden_baseline.py capture resume --force`，與 TILING/SHADOW/RESUME-P3 同屬 B軌輸出變更類）。

### BE-Hotfix RESUME-P3 PARA-HOTFIX-1 — B軌履歷正文段落黏連（無段落空行）修復

| Commit | 內容 | Hash |
|---|---|---|
| PARA-HOTFIX-1 | `pipelines/resume_pipeline.py` 新增 pipelines/ 私有 `_normalize_paragraph_breaks`（移植 A軌 pipe-table-safe 單 `\n`→`\n\n` 段落正規化邏輯、**不 import/不耦合 A軌 restore 處理器**）+ `_restore_one_section` text item〔含純字串 fallback〕套用、formula/figure/table 不套、pipe table rows 保留原 `\n`；根治 B軌只在 part 間放 `\n\n`、段內單 `\n` 不處理 → CommonMark soft break → 兩段黏一起（A軌靠 `_write_to_md` 補 `\n\n` + `_preserve_pipe_table` 升級單 `\n`、B軌兩者皆無 + C2 停用 U4）；`# === [RESUME-P3 PARA-HOTFIX-1 START/END] ===` 包裹 + 追加 `test_p3_text_paragraph_blank_line_normalized`〔兩段升 `\n\n` + pipe table rows 不拆散〕；resume 28 passed、全套件 501 passed（僅 env flake） | `2772822` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md`
> **真因**：CommonMark 單 `\n`=soft break（同段）、須 `\n\n`（空行）才分段；A軌有兩道機制（`_write_to_md` 每塊補 `\n\n` + `_preserve_pipe_table` 段內單 `\n`→`\n\n`），B軌 `_restore_one_section` 兩者皆無、且 C2 為 resume 停用 Translator U4 → 全鏈無換行升級 → 正文黏連。
> **⚠️ 行為變更 + 重捕**：改 B軌 `final_zh` 段落空行結構 → 衝擊 golden D1/D2；**Flip/結案前須重捕 resume 單路**（`venv/bin/python tools/golden_baseline.py capture resume --force`，與 TILING/SHADOW/RESUME-P3/HEADING-HOTFIX-1 同屬 B軌輸出變更類）。

### BE-Hotfix RESUME-P3 META-HOTFIX-1 — B軌履歷 final 缺文件 header（P1 Meta 未渲染）修復

| Commit | 內容 | Hash |
|---|---|---|
| META-HOTFIX-1 | `pipelines/resume_pipeline.py` 新增 pipelines/ 私有 `_render_meta_header(ctx, gspec, *, lang)`（讀現有 `ctx.raw_metadata` 旁路 domain/organization/phone/email + `ctx.ingestion.title` 姓名〔含 (測試)〕+ en domain 優先 `gspec.domain_name`，組 `# 姓名` + 領域/機構/電話/Email **無序列表**〔缺項省略、整包空回 ''、list 規範保證一欄一行防 RAG-10 軟換行〕）+ `run_phase3` 寫出前 prepend final_zh〔中文 label〕/final_en〔英文 label〕；根治 P1 抽的 meta 只到 DB（raw_metadata 旁路終點＝web_server 寫庫）、`run_phase3` 渲染端從不讀 → final 無 header 的渲染缺口；不動凍結合約（走現有旁路、轉正屬 INFRA-4 遠期）；`# === [RESUME-P3 META-HOTFIX-1 START/END] ===` 包裹 + 追加 `test_p3_meta_header_rendered`〔# 王小明 (測試) 開頭 + 四欄值 + 各欄獨立 list item〕+ 對齊 2 既有 run_phase3 測試（header prepend carryover）；resume 29 passed、全套件 502 passed（僅 env flake） | `2ba97fc` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md`
> **真因**：P1 抽的 meta（姓名→`IngestionMetadataSpec.title`；domain/phone/email→`ctx.raw_metadata` 旁路）唯一出海口是 DB（P2 讀 domain→LCC、web_server 寫 `metadata_json`）；`run_phase3`（唯一產 final 處）只渲染 section body、從不讀 raw_metadata、無 header 組裝 → P1 meta 對最終文件零貢獻。治標＝render 端讀同一條旁路組 header；治本（旁路轉正 spec.meta）屬 INFRA-4。
> **代號**：原 HEADER-HOTFIX-1 改名 META-HOTFIX-1（避免與 HEADING-HOTFIX-1 視覺混淆）。
> **⚠️ 行為變更 + 重捕**：在 B軌 `final_zh`/`final_en` 開頭新增 meta header → 衝擊 golden D1/D2；**Flip/結案前須重捕 resume 單路**（`venv/bin/python tools/golden_baseline.py capture resume --force`，與 TILING/SHADOW/RESUME-P3/HEADING/PARA 同屬 B軌輸出變更類）。
> **⚠️ domain 現況**：P1 抽出的 `domain` 為描述句（非乾淨標籤）、header 照實渲染；乾淨標籤須改 P1 domain prompt（另一任務）。

### BE-Refactor RAG-ASYNC P4 RAG 索引共用真理源與全 P2 摘要

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Spec Sync：母 plan v10 §U4/§U6 + PIPE-SPEC §1.1②/§1.4.1/§1.3 同步（含修 resume P3「100% Bypass」doc-drift）+ 兩檔 §99.2 Revision；零 Python | `195e12b` |
| C2 | Contract：`contracts.py` GlossaryReadySpec `section_summaries:Dict` 取代 Book 專用 `chapter_summaries:List`（五路通用節點摘要、key 對位巢狀樹）+ 對齊 resume_pipeline/test_pipe_core | `8c76274` |
| C3 | Chunk Build：新建 `processor/rag_indexer.py`（**零 import rag_processor**）Strategy B header augment〔# + Context + Chapter Summary〕+ size-cap 二段子切〔超 EMBEDDING_MAX_TOKENS_PER_ITEM 遞迴子切、子塊重貼前綴〕+ 自實作 is_chunk_meaningful；+`tests/test_rag_indexer.py` 10 測試 | `53755c4` |
| C4 | Vector Persist：`rag_indexer.index()` split→filter→Embedding→FAISS(MAX_INNER_PRODUCT) save_local→paper_chunks〔embedding 交易外、paper_db_id None 降級〕→自寫 index_meta→RagDbSpec；+3 ④ conformance〔B 軌 vector store→rag_retriever.load_vector_store 讀回召回〕 | `a09128e` |
| C5 | P2 Six-Step：`run_phase2` 四步→統一六步：⑤批次產原文 section 摘要〔1 次 LLM〕+ ⑥全文摘要引導批次翻繁中〔1 次〕→ section_summaries；三安全鎖〔批次非 N / 非致命 logger.warning exc_info+extra_fields 不阻 reading_ready / 可量測 performance_metric phase=P2〕；LLM 交易外；+3 測試 | `d9b03f4` |
| C6 | Wire P4：**砍 `from processor.rag_processor import RagProcessor`**；run_phase3 附加封存譯後 section 結構至旁路 `ctx.rag_sections`〔context.py 加旁路欄、不改 final_zh/en 輸出〕；run_phase4 改呼 `rag_indexer.index(rag_sections + section_summaries)` 不再餵 final_zh.md；P4 測試改 mock rag_indexer + run_phase3 旁路測試 | `13abdfa` |
| C7 | Checkout：Conformance 五維度驗收全綠（目標規格 U1-U6 / tasks §6 grep+全套件 525 passed / 不可動清單 git diff 空〔rag_processor/rag_retriever/pipeline_core 零改〕/ 提示詞 9 份 / msg 完整）+ baton 一次性歸檔（plan_v2/tasks/C1-C7 報告 → plans//tasks//executions/）+ hash 全量自癒 | `0d73601` |

> **修法依據**：`.claude-logs/plans/2026-06-07_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_plan_v2.md`（§99.2 v2、§7 定案紀錄 D1-D7、七輪設計討論收斂）
> **PIPE 對齊**：P4 升格為與 P2（DomainNormalizer/GlossaryManager）、P3（Translator）對稱之**共用真理源**——新建 B 軌自有 `rag_indexer`（全重寫、零依賴 A 軌 `rag_processor`）依 P3 結構自生 Strategy B 摘要增強分塊 + size-cap 二段子切；section_summaries 收斂為**統一 P2 六步流程**（全五路通用、單一節點摘要欄、繁中、批次）。
> **根因/修復**：B 軌 P4（PIPE-RESUME C5 暫行首落地）餵 reading-view `final_zh.md`（section 皆 `##`、唯一 `#`＝META header）給只切 `#` 之切塊器 → **chunks=1**（13358 字元塌成 1 塊、RAG 召回崩潰）；C6 改餵 P3 旁路結構化譯後 section（每節點 `#`）→ **chunks 量級回升**。順手修 A 軌 header-only 無 size-cap、書籍大章塌超大 chunk 之潛在弱點。
> **七定案（D1-D7）**：D1 單一 `section_summaries` 欄（section≡chapter 同為文件樹節點）/ D2 繁中·P2 六步 / D3 全重寫零 import·A 軌整檔不碰·通用基建照用 / D4 ctx 旁路（小）·磁碟（book 大）/ D5 size-cap 二段子切 / D6 production 僅 resume 首落地·合約+模組五路通用 / D7 修 §1.3 P3 doc-drift。
> **⚠️ C6 動 context.py（第 3 改檔）**：plan D4 ctx 旁路所需（`arbitrary_types_allowed` 不允許動態屬性）、已 .bak、屬 plan sanctioned 新增旁路欄（同 raw_metadata 先例）。
> **⚠️ baron 運維（非 commit）+ 重捕**：影子上傳履歷驗 chunks 1→≥20 + retrieve 分數分布 + reading_ready 延遲（performance_metric 已埋點）；B 軌輸出變更 → resume 重捕 Golden Baseline。
> **後續（plan §7.2 待調實作參數）**：size-cap token 門檻/overlap、⑥ 批次翻譯拆批門檻；其餘四路 section_summaries production 隨各自 PIPE-N pipeline 跟上。

### BE-Refactor RESUME-PERF-1 run_phase3 逐 section 翻譯並行化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pipelines/resume_pipeline.py` 收集-組裝解耦：新增 `_collect_render_slots`〔遞迴鏡像 DFS pre-order、不翻譯、append title/content/raw slot、title 記 `level=min(2+depth,6)`〕+ 重構 `_restore_sections_markdown`〔collect→**序列**翻譯→按序組裝〕+ 移除無外部引用 `_restore_one_section`；仍序列、輸出 byte 等價〔既有 29 resume 測試全綠為鐵證〕；HEADING/PARA/META 邏輯原值搬移不改；`# === [RESUME-PERF-1 C1] ===` 包裹 | `b110742` |
| C2 | `resume_pipeline.py` 翻譯段序列→`ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)` 受限並行、`{future:index}` 保序回填〔實際 API 併發受**既有** `LLMClient._api_semaphore`(6) 限、不新增鎖〕+ 單 unit future 拋例外→退原文 `slot["text"]`+`logger.warning(event=resume_translate_unit_fallback)` 異常隔離保交付；組裝/退化/zh* 不動；resume 29 passed〔行為等價〕、全套件 504 passed | `d5abdf0` |
| C3 | `tests/test_resume_pipeline.py` 追加 4 並行專屬測試〔`order_byte_equal` 多層 byte 等拍保序 / `concurrency_capped` patch `LLM_MAX_CONCURRENT=2` lock 計數驗峰值 ≤ 2 / `unit_error_isolated` 單 unit 拋例外退原文 spec 仍交付 / `degraded_single_call` 退化 `_translate_whole` calls==1 不並行〕；resume 33 passed、全套件 508 passed | `be49abe`〔併入 C4 收官 commit〕 |
| C4 | Checkout：Conformance 三維度驗收全綠（目標規格 U1-U7〔U2 限流/U3 等價/U4 保序/U5 異常隔離/U6 退化不變 由 C3 測試自證；效能 wall-clock 屬 baron E2E〕/ tasks §6 grep+全套件 508 passed / 不可動清單 git 證據〔C1-C2 僅 resume_pipeline.py、C3 僅 test_resume_pipeline.py〕）+ SOP 核查（logging/database 合規）+ 提示詞 6 份稽核 + msg 完整性 + baton 一次性歸檔（plan_v1/tasks/C1-C4 報告 → plans//tasks//executions/）+ hash 全量自癒 | `be49abe` |

> **修法依據**：`.claude-logs/plans/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（§99.2 v2、§7 OQ Q1-Q7 核准）
> **根因**：B軌 `run_phase3` 逐 heading section 翻譯完全序列（`_restore_one_section` 同步 `_t` + 遞迴序列、無並行原語）；A軌等價結構實測 translate ~315-330s（佔單份 76%），B軌 resume 影子上傳承此瓶頸。
> **解法（兩步降風險）**：C1 先「收集-組裝解耦」（仍序列、既有測試鎖死輸出等價）→ C2 才把中間翻譯段換 ThreadPool（保序靠 slot index、限流靠既有 semaphore、單 unit 失敗退原文）。把「結構是否壞」（C1）與「並行是否亂序」（C2）隔離成兩個獨立可驗證步驟。
> **行為等價**：只改翻譯「執行方式」（序列→並行）、不改輸出內容/順序/層級/段落/header；既有 29 resume 測試全綠 + C3 並行 byte 等拍雙重保證。預估 wall-clock ~5x（~300s→~60-90s、屬 baron E2E 觀測）。
> **時機**：plan Q5 原寫「Flip 前」屬優先序判斷；baron 拍板「不必等五路、現在做」（自包於 resume_pipeline.py、不依賴其餘四路與 A軌）。

### BE-Hotfix VISION-HOTFIX-1 — Vision 履歷轉錄非確定性（每次輸出抖動）修復

| Commit | 內容 | Hash |
|---|---|---|
| VISION-HOTFIX-1 | `settings.py` 新增 `LLM_VISION_TEMPERATURE`（預設 0.0、env 可調）+ `llm/client.py` `chat_with_images` 加可選 `temperature` 參數〔預設 None 向後相容、非 None 才注入 `GenerateContentConfig`〕+ `processor/resume_processor.py` `_analyze_resume` 傳 `temperature=settings.LLM_VISION_TEMPERATURE`(0) → 履歷 Vision 忠實轉錄走 greedy；根治 `chat_with_images` 原未設 temperature→吃 Gemini 預設 ~1.0 高溫採樣致同份 PDF 每次輸出抖動（13126/13233/13281、golden 非固定靶）；`# === [VISION-HOTFIX-1 START/END] ===` 包裹 + 追加 `test_vision_passes_temperature_zero` + `test_chat_with_images_wires_temperature`〔注入+None 向後相容〕；test_resume_processor 16 passed、全套件 504 passed（僅 env flake） | `3d5be32` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md`
> **真因**：`llm/client.py:308` `chat_with_images` 組 `GenerateContentConfig` 未設 temperature → 吃 Gemini 預設 ~1.0（高溫採樣）；忠實轉錄任務卻在隨機採樣 → 同份 PDF 每次輸出不同。切頁救不了（temp 才是槓桿、且切頁砸跨頁結構）。
> **⚠️ 共用 + 重捕**：`ResumeProcessor.parse` = A軌 pdf2md + B軌 P1 共用 → Vision 輸出改變、**A軌 golden + B軌 P1/final 都受影響**；須先 `rm -rf _capture_work/.../golden_resume` 再重捕 resume golden（`--force` 不清中間快取）、自此可重現。
> **⚠️ 誠實限制**：temp=0 不保證 byte 完全相同（Google 後端 batching/浮點/MoE 殘餘非確定）、僅壓抖動。
> **既存 SOP 註**：`resume_processor.py:166` `logger.error` 無 `exc_info=True` 為**前置既存**（非本 hotfix 引入、本 hotfix 只加 temperature 參數未碰錯誤處理）；屬獨立 cleanup 候選。

### BE-Refactor MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `settings.py` 換 `EMBEDDING_MODEL` 預設 `gemini-embedding-2`→`gemini-embedding-001`（文字 embedding GA、支援文字 list 真批次 + task_type）+ 追加 `EMBEDDING_BATCH_MAX_ITEMS`(100 段數軟上限)/`EMBEDDING_BATCH_MAX_TOKENS`(18000 請求 token 硬約束)/`EMBEDDING_MAX_TOKENS_PER_ITEM`(2048 單段上限) 三常數；C2 才消費、`# === [MODEL-11 C1] ===` 包裹 | `1f56547` |
| C2 | `config.py` `embed_documents` 廢 `BATCH_SIZE=32` 固定切分 → **token-aware 貪婪封批**〔`est=max(1,len(text))` 字元上界估值、封批臨界 段數≥`EMBEDDING_BATCH_MAX_ITEMS` 或 累計 token>`EMBEDDING_BATCH_MAX_TOKENS`、殘留 flush、巢狀 `_flush` 保 `_embed_one` 真 fallback〕+ 單段超上限發 `embedding_oversized_item` warning 不截斷 + log 正名 `embedding_429`→`embedding_batch_fallback`+`reason`；`_embed_batch` 校驗/`_embed_one`/`embed_query`/`embed_image` 不動；MODEL-9-OPT C2 頂部過時註解更新〔換 -001 向量改變、須 regen_rag --all + Golden 重捕〕；`# === [MODEL-11 C2] ===` 包裹 | `d7f26be` |
| C3 | `tests/test_embedding_retry.py` mock 實例 model 對齊 -001 + 追加 4 測試〔real_batch_no_fallback 真批次 N→N spy `_embed_one` 0 呼叫保序 / auto_split_preserves_order patch `config.EMBEDDING_BATCH_MAX_ITEMS=2` 拆 2 批保序 / task_type_document_vs_query DOCUMENT vs QUERY / embed_batch_429_falls_back_to_one patch `_embed_batch` 拋 429 退逐筆〕；該檔 8 passed、全套件 499 passed | `8c5a0eb` |
| C4 | Checkout：Conformance 三維度驗收全綠（目標規格 U1-U7〔U6 遷移/U7 Golden 屬 baron 運維〕/ tasks §6 grep+全套件 499 passed / 不可動清單 git 證據〔僅 settings.py+config.py+test_embedding_retry.py〕）+ SOP 核查（logging/database 合規）+ 提示詞 5 份稽核 + msg 完整性 + baton 一次性歸檔（plan_v1/tasks/C1-C4 報告 → plans//tasks//executions/）+ hash 全量自癒 | `01a4e5b` |

> **修法依據**：`.claude-logs/plans/2026-06-06_MODEL-11_Embedding模型換用gemini-embedding-001與真批次_plan_v1.md`（§99.2 v2、§7 OQ Q1-Q8 核准）
> **根因**：`gemini-embedding-2` 為多模態交錯模型——SDK 特例 `t_contents()` 把 `contents=[N 段]` 併成 1 向量 → 批次永遠退逐筆（慢、log 誤標 429）；且不支援 task_type → query/doc 向量同質、RAG 召回非對稱性喪失（品質打折非僅效能）。Dev API 探針鋼證：`gemini-embedding-001 embeddings=3`（真批次）vs `gemini-embedding-2 embeddings=1`（融合）。
> **PIPE 對齊**：基建 embedding 層——換文字 embedding GA 模型恢復真批次 + task_type 非對稱；承 MODEL-9-OPT 韌性框架（`_api_semaphore`/`retry_call`/`_l2_normalize`/768 MRL 不變）。
> **⚠️ 行為變更 + 運維（baron 各環境手動、非 commit）**：① `.env` `EMBEDDING_MODEL=gemini-embedding-001`〔C1 預設換、但 runtime 受 .env override pin〕② `venv/bin/python tools/regen_rag.py --all` 全量重嵌〔向量值改變、新舊不可混庫〕③ `venv/bin/python tools/golden_baseline.py capture resume --force`〔僅 resume 單路重捕、其餘四路無 B 軌免捕〕。
> **流程註**：C4 驗收時 baron 已逐一 commit C1-C3，依框架 §2.2 回填 git log 實證 hash；C4 自身落於 `be49abe`（C3 並行測試亦併入該收官 commit、無獨立 C3 commit）。

### BE-Refactor MODEL-9-OPT Embedding連線與限流框架優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `settings.py` 新增 `EMBEDDING_MAX_CONCURRENT`（預設 5、env 可調）；純新增常數、C2 才消費、行為等價 | `8feaa12` |
| C2 | `config.py` EmbeddingModel 引入 class-level `_api_semaphore=threading.Semaphore(EMBEDDING_MAX_CONCURRENT)` + `embed_query/embed_image/_embed_batch〔新〕/_embed_one` 套 `@retry_call`〔Full Jitter 指數退避〕+ `with semaphore` + 重構 `embed_documents` 批次降級逐筆〔移除手動 time.sleep linear〕+ 429 extra_fields 觀測 log；`_embed_one` fallback retries=2；同步 `tiling_processor.py` 過時退避註解；embed_content 參數/_l2_normalize 不變→向量值不變→不觸發 Golden 重捕 | `9a44d41` |
| C3 | 新建 `tests/test_embedding_retry.py` 4 測試（embed_query 429 退避 / embed_image 503 重試 / embed_documents 批次降級保序+warning / Semaphore 併發上限）；4 passed、全套件 490 passed | `e86ced9` |
| C4 | Checkout：Conformance 三維度驗收全綠（目標規格 / tasks §6 grep+pytest / 不可動清單 git 證據）+ SOP 核查 + 提示詞 5 份稽核 + msg 完整性 + baton 一次性歸檔（plan/tasks/C1-C3 報告 → plans//tasks//executions/）+ hash 全量自癒 | `61d0f69`〔C4 收官併入該 commit〕 |

> **修法依據**：`.claude-logs/plans/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_plan.md`（§99.2 v3、review 5 點補強定稿）
> **PIPE 對齊**：基建韌性層——EmbeddingModel 接入 `llm/retry.py` 統一彈性框架（與 LLMClient 機制一致、各自獨立 Semaphore 避免跨模組死鎖）；根治高頻 Embedding 削爆全域配額連帶拖垮 LLM。**不改向量值、不觸發 Golden Baseline 重捕、可獨立先做**（排序 hotfix → MODEL-9-OPT → RESUME-P3）。
> **OQ3 上線觀察項**：併發鎖 ≠ RPM 限流；預設 5+env 可調+429 log 觀測，撞不過才上 token bucket（非本任務）。

### BE-Refactor TRANSLATOR 雙模式原子翻譯器（PIPE 大改版三大共用真理源之三）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `processor/translator.py` 定義 `InjectionContext`（7 欄 frozen+forbid、逐字對齊 PIPE-SPEC §1.2.3 v3）+ `TranslateMode`（NORMAL/DEEP_THINK）；`pipelines/contracts.py` GlossaryReadySpec 補 `domain_name`（P2→P3 載體、向後相容） | `1558f79` |
| C2 | `Translator` 系統提示詞五步拼接（text_type 路由含 caption / doc_type Style Hints / LCC 注入讀 ctx.domain_name 零 DB / Glossary 強約束含大小寫不敏感 / constraints）+ 用戶提示詞；新建 `prompt/translate/caption_translate_prompt.txt`（保留 Figure/Table 編號） | `27db830` |
| C3 | `settings.LLM_THINKING_BUDGET`（預設 0）+ `TRANSLATE_MODEL` 預設改 `gemini-3.5-flash`；`llm/client.py::chat()` 受控擴充 `thinking_config` 注入（**§4 唯一例外**、前向相容 gating 涵蓋 2.5/3.5/4.0 + try/except 降級、budget=0 byte 等價）；`Translator.translate()` NORMAL/DEEP_THINK 雙模式路由 | `11ea52a` |
| C4 | `Translator.translate()` 末加 U4 多行 `re.sub` 分行容錯；新建 `tests/test_translator.py` 8 pytest（雙模式/style/路由/LCC/glossary/兜底/用戶提示詞）；全套件 465 passed | `2ebda03` |
| C5 | Conformance 三維度驗收（U1-U4 / 測試 §6.1-§6.4 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v10/tasks_v1/C1-C5 報告）+ 結案 | `b55219b` |

> **修法依據**：`.claude-logs/plans/2026-06-01_TRANSLATOR_雙模式原子翻譯器_plan_v10.md`（八輪嚴格交叉 review 定稿）
> **PIPE 對齊**：消費 DomainNormalizer LCC（`Domains.name` 英文領域名）+ GlossaryManager 凍結 Glossary；`InjectionContext`/`TranslateMode` 落 `processor/translator.py`（非 contracts.py）；`thinking_config` 列 §4 唯一受控例外（依 model_recommendations.md §1.1）；旗標 `LLM_USE_GLOSSARY_ALIGN`=False + `LLM_THINKING_BUDGET`=0 時行為等同舊狀、線上 0 風險。
> **三大共用真理源全數就緒**：DOMAIN-NORM / GLOSSARY-CORE / TRANSLATOR。

### BE-Refactor GLOSSARY-CORE 中央領域術語庫與跨語系一致性（PIPE 大改版三大共用真理源之二）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 新增 `GlobalGlossary` 表（`(source_lang,target_lang,term_key,domain)` 聯合唯一約束 + 級聯查詢輔助索引 + source auto_extract/manual_edit）；`Paper` 等既有表 byte 不動 | `03d85c8` |
| C2 | 新建 `processor/glossary_extractor.py` GlossaryManager：`query_cascade`（專屬 LCC 覆寫 general）+ LLM `extract_terms`（**交易外**）+ `upsert_terms`（on_conflict_do_nothing 冪等）；全程 try/except 降級不阻斷 | `9af971f` |
| C3 | `translate_processor.py:237-239` 旗標閘門注入級聯術語表 + `pipeline_core._stage_translate` 尾端**非阻塞**背景回填 hook；旗標 OFF byte 等價舊行為；書籍 ParallelChapterTranslator 融合延後 | `fd0e84f` |
| C4 | `AI_professor_chat.py:329-335` 旗標閘門按 `_domain` LCC `query_cascade` 注入「不可違背 System constraint」；前台崩潰防護 graceful degradation；只 stage C4 hunks 隔離既存 RAG-14 改動 | `06bf3df` |
| C5 | 新建 `tools/manage_glossary.py` 自癒 CLI（`--init` / `--test-pipeline --pdf` 離線閉環 / `--backfill-existing-papers` 歷史 domain→LCC 批次升級）；setup_logging + 批次極短交易防鎖 | `7da39bd` |
| C6 | 新建 `tests/test_glossary_core.py` 5 pytest（唯一約束 / 級聯專屬覆寫 / 書籍融合優先 / Chat 注入 / CLI 回填）；全套件 457 passed | `ae705d5` |
| C7 | Conformance 三維度驗收（U1-U5 / 測試 §6.1-§6.6 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v2/tasks/C1-C7 報告）+ C5 交付物補正 + 結案 | `d4c34d5` |

> **修法依據**：`.claude-logs/plans/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md`
> **PIPE 對齊**：消費上游 DomainNormalizer `normalize_to_lcc` LCC（DOMAIN-NORM 已收官）；translate/chat 跨文獻術語一致性注入 + 知識飛輪自癒回填；旗標 `LLM_USE_GLOSSARY_ALIGN` 預設 False、線上 0 風險。
> **延後項**：書籍並行 `ParallelChapterTranslator` 雙層融合（plan U3 後半）待 TRANSLATE-BOOK 落地後整合（tasks §9）。
> **流程註**：C4 發現既存未提交 RAG-14 多標籤後端改動 → baron 拍板「只 stage C4 hunks」隔離、RAG-14 獨立 commit `595e3d8`。

### BE-Refactor DOMAIN-NORM 領域標準化對齊器（PIPE 大改版三大共用真理源之一）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 新增 `Domains`（lcc_code PK String(3) + name 動態註冊）+ `DomainMapping`（raw_key PK→lcc 快取 + FK）兩表；`Paper` 等既有表 byte 不動 + create_all 自動建表 | `8d4f75f` |
| C2 | 新建 `processor/domain_normalizer.py` DomainNormalizer：快取查→LLM 內容判定（cheap model Temp=0.0、履歷按技能）→動態註冊 Domains（on_conflict_do_nothing 不塞單字）→寫回；**LLM 呼叫在 session.begin() 交易外** + try/except 降級 general | `125af97` |
| C3 | 暴露模組級單一入口 `normalize_to_lcc(raw_domain, context_text=None)->LCCCode`（逐字對齊 PIPE-SPEC §1.2.1 / master v10 L69）+ `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False 走舊 raw 直注、零風險）；惰性單例 | `7e7f2a1` |
| C4 | 新建 `tests/test_domain_normalizer.py` 4 pytest（內容分類 HF/QA + temp=0.0 / 冷門動態註冊 QE 不塞單字 / 快取命中 0 API / 旗標 off 保舊行為）；全套件 452 passed | `aeb4fc2` |
| C5 | Conformance 三維度驗收（U1-U4 / 測試 §6.1-§6.4 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v2/tasks/C1-C5 報告）+ 結案 | `1559b08` |

> **修法依據**：`.claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md`
> **流程校正**：原 18:46 Check 提示詞欲收斂為 4-commit（C4=Check），經 baron 拍板「先補 C4 Unit Tests 再收官」→ 回歸 5-commit（C4=Unit Tests / C5=Check）。
> **PIPE 對齊**：DomainNormalizer 為 GLOSSARY-CORE / Translator 共同上游真理源；簽名凍結對齊 PIPE-SPEC §1.2.1。旗標預設 False、線上 0 風險（接線 translate 屬後續路次 plan）。

### BE-Refactor API-PERF API 技術審計與效能防呆優化（PIPE 大改版基建前置）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `db.py` U6 SQLite 連接池（busy_timeout 5s→30s + QueuePool pool_size=5/max_overflow=10/pool_pre_ping）+ 2 pytest | `5326437` |
| C2 | `web_server.py` U4 1MB 分塊流式上傳（%PDF/415/413/清理 partial）+ U5 login X-Forwarded-For 真實 IP + 3 pytest | `e20054d` |
| C3 | U3 廢 lifespan preload + chat 端點按需 Lazy Load + `ai_core`/`rag_retriever` OrderedDict LRU(上限 5)+gc；`retrieve_*` 演算法 byte 不動 + 2 pytest | `76e47ed` |
| C4 | U1 `PIPELINE_SEMAPHORE`(上限 1) 守 A 軌 run_pipeline + B 軌 run_pipeline_shadow + queued SSE；U2 pdf_processor 子進程 nice 19 soft-fail + 2 pytest | `aad3737` |
| C5 | U7 (phase,stage) 二維鍵 performance_metric 埋點（pipeline_core A 軌映射 + orchestrator P1-P4 附加式）+ pipeline_finished/rag_finished + `scripts/analyze_performance.py` + 2 pytest | `59e1c56` |
| C6 | Conformance 驗收（U1-U7 / 測試 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan_v2/tasks_v3/六報告）+ 結案 | `703cfaa` |

> **修法依據**：`.claude-logs/plans/2026-06-01_API-PERF_API技術審計與效能優化_plan_v2.md`
> **PIPE 對齊**：基建前置——U1 PIPELINE_SEMAPHORE 為 PIPE 廢除 QUEUE-1 Thread-level 避讓並發底座；U7 (phase,stage) 埋點介面前向相容 PIPE Orchestrator P1-P4。C3 另有後續微調 commit `beb8f8a`。

### BE-Refactor PIPE-SCAFFOLD web_server 雙軌派發 scaffolding（PIPE 大改版階段 1·建）

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `settings.SHADOW_LAUNCH_ENABLED`（預設 false）+ `web_server.run_pipeline_shadow` 附加影子單元（`_shadow` 四重隔離 + ` (測試)` 標題 + 委派 Orchestrator）+ upload_paper 派發點一閘門；A 軌 `run_pipeline` 本體 byte-for-byte 不動 | `13c1dcb` |
| OP-2 | confirm_type 派發點二閘門納管 + OP-1/OP-2 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解標記（Flip 下線錨點）+ `tests/test_pipe_scaffold.py`（5 pytest 全綠） | `6807a7f` |
| OP-3 | Conformance 三維度驗收（目標規格 U1-U9 / 測試 5 項 / 不可動清單 A 軌 byte diff）+ baton/ 全量歸檔（plan_v3/tasks_v3/三報告）+ 結案 | `58e1b89` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md`
> **範圍**：僅階段一（建）——影子期雙軌派發 scaffolding 注入（旗標預設 false 惰性插入點、線上 0 風險）；**階段二（移／Flip）屬 PIPE-FLIP plan**（觸發＝五路全通 + Golden Diff 0%）。OP-1 commit `13c1dcb` 同時夾帶 PIPE-CORE Check archival。

### BE-Refactor PIPE-CORE 三層解耦調度骨架（PIPE 大改版階段 1）

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `pipelines/contracts.py` 四凍結合約（IngestionMetadataSpec extra=forbid 保證 R1.1）+ `pipelines/context.py` PipelineContext/PhaseEnum + `tests/test_pipe_core.py`（8 pytest） | `aa786a1` |
| OP-2 | `pipelines/base_strategy.py`（DocumentStrategy ABC + NullStrategy 哨兵）+ `pipelines/factory.py`（註冊/LiteDoc 降級）+ 測試追加（14 pytest） | `effb155` |
| OP-3 | `pipelines/orchestrator.py` 四 Phase DAG 指揮層（宣告式 _PHASES + 交接點驗證 + P4 容錯 + shadow 貫穿）+ 測試追加（20 pytest）+ grep doc_type== 0 命中 | `84b9b30` |
| OP-4 | Conformance 五維度驗收（目標規格 U1-U7 / 測試 20 項 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan_v2/tasks_v2/四報告）+ 結案 | `13c1dcb` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`
> **三層解耦**：合約層（contracts）/ 狀態層（context）/ 策略層（base_strategy+factory）/ 指揮層（orchestrator）；與舊 `pipeline_core.py` 物理共存、零業務代碼改動；五路具體策略屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK；P4 BackgroundTasks 屬 RAG-ASYNC（已留 injectable dispatch_p4）

### GOLDEN-BASELINE 黃金基準存盤與退化比對

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | 新建旁路 CLI `tools/golden_baseline.py` capture 子命令 + `tests/golden_baseline/queries.json` 固定 query set + 五路代表性 fixtures PDF；baron 端 MinerU 實跑 `capture --all` 物理存盤五路三維度黃金快照（D1 雙語 md / D2 rag_tree.json / D3 召回 + SHA-256 manifest） | `3be0b0d` |
| OP-2 | `tools/golden_baseline.py` 新增 `diff` 三維度比對引擎（D1 結構樹 / D2 譯文相似度 0.95 / D3 RAG Jaccard 0.90）+ checksum 防竄改 + 影子雜訊正規化 + 紅綠燈裁決 + 雙格式報告 + `tests/test_golden_baseline.py`（18 pytest 全綠）+ 五路自比對歸零 PASS + 負向竄改 FAIL | `74d34e8` |
| Check | Conformance 三維度驗收（目標規格 U1-U7 / 測試計畫 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan/tasks/OP-1/OP-2/OP-3 報告）+ 結案 | `c0c64e9` |

> **修法依據**：`.claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
> **時序修正**：tasks v1 Checkout 誤置 OP-1 → v2 更正為 OP-1 存盤 / OP-2 Diff 腳本 / OP-3 Checkout 收官（WORKFLOW_SOP §3 baton 暫存鐵律）

### RAG-14-HOTFIX-1 — 緊急熱修復：對話置頂氣泡頂部穿透漏出修復

| Commit | 內容 | Hash |
|---|---|---|
| Hotfix | `static/index.html` 移除 `#chat-messages` padding-top，新增 `.qa-group:first-child` margin-top 完美防置頂穿透 | `a5b193f` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-30_RAG-14_hotfix.md`

### RAG-14 多標籤寬鬆格式跨文章 RAG 檢索與對話體驗升級

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `static/index.html` CSS 4 項（gap / msg-user 滿寬 sticky / msg-ai 滿寬 / qa-group）+ sendMessage × 過濾 + `tests/test_rag14_c1_css_and_filter.py` 新增（4 pytest）| `6593962` |
| C2 | `static/index.html` loadChatHistory forEach qa-group 包裝 + in_progress currentGroup + sendMessage qaGroup 包裝 + `tests/test_rag14_c2_dom_structure.py` 新增（3 pytest）| `b8e8770` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `ebf1b9c` |
| Fix (補) | 補交遺漏的 `AI_professor_chat.py` 後端多標籤分流路由與解析邏輯 | `595e3d8` |

> **修法依據**：`.claude-logs/plans/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_plan_v3.md`

### FE-AESTHETICS HOTFIX-1 — 前端學術扉頁自癒與排版靠左優化

| Commit | 內容 | Hash |
|---|---|---|
| C2-hotfix | Frontend Academic Header Self-Healing（CSS 靠左 + normalizeAcademicHeader JS + test_bug_f1 自癒 + 新建 test_fe_aesthetics_c2_hotfix.py）| `bf3c14b` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `452c652` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-29_FE-AESTHETICS-HOTFIX-1_學術扉頁自癒與靠左排版_hotfix_v1.2.md`

### RAG-13-HOTFIX-1 — 緊急熱修復：自訂主題下拉選單捲軸無作用修復

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `static/index.html` scroll handler ctx-popup 過濾 + `tests/test_rag13_hotfix1_scroll_intercept.py` 新增 | `6598d2d` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `75ab18a` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_hotfix_v1.0.md`

### RAG-13 自訂主題動態清單與選單優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `web_server.py` 新增 `GET /api/themes` + `tests/test_themes_upload.py` fixture GET 掛載 + `test_list_themes_endpoint` | `9e041ed` |
| C2 | `static/index.html` 四項前端變更（setThemes / 分隔線 / loadThemesFromServer / upload handler await）+ `tests/test_bug_f2_theme_dropdown_esc.py` test 更新 | `d842008` |
| Check | Conformance 驗收與 baton/ 全量歸檔收官 | `690b04a` |

> **修法依據**：`.claude-logs/plans/2026-05-29_RAG-13_自訂主題動態清單與選單優化_plan_v3.md`

### FE-AESTHETICS 摘要工具列重構與正文扉頁美化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 後端 `_render_header_en/zh` academic path：dash-list → 階梯式 HTML div 置中對稱排版 + 測試 assertions 更新（59 pytest 全綠） | `3cf8acf` |
| C2 | 前端全棧重構：`#abstract-toolbar` 滿寬摘要容器 + `.paper-header-meta { display:flex }` 螢幕扉頁解鎖 + `renderTitleHeader` JS 重寫 + CSS word-wrap 防禦 + 測試更新（67 pytest 全綠） | `b735a94` |
| Check | Conformance 驗收 + baton/ tasks/C1/C2 全量歸檔 + TODO.md 結案 | `6947098` |

> **修法依據**：`.claude-logs/plans/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md`（v1.3）

### INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pdf_processor.py` backend=pipeline comment lock + `test_backend_parameter_is_pipeline` Case D + `.env.example` VRAM 禁用警告 | `264dadc` |
| C2 | `sop/2026-05-27_mineru_SOP_手冊.md` §1 VRAM 禁用列 + §2.3 CPU 後端紅線規格 + §6.2 VRAM OOM 自愈步驟 + §99.2 v2 Revision | `9e05466` |
| Check | Conformance 驗收 + baton/ 4 份全量 mv 歸檔 + TODO.md 結案 | `878c7a2` |

> **修法依據**：`.claude-logs/plans/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md`

### MODEL-10 MinerU 連線優化與運作維護 SOP

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pdf_processor.py` MINERU_TIMEOUT 防禦性載入 + L76 timeout 動態化 + Priority 2 廢棄 warning + `.env.example` + 3 pytest | `19ddac8` |
| C2 | 新建 `sop/2026-05-27_mineru_SOP_手冊.md`（193 行，§0/§99 治理結構，6 大運維主軸：env 配置 / 超時對策 / SSH Keep-Alive / Priority 2 SCP 備援規格 / cron 清檔 / 容器重啟） | `991258d` |
| Check | Conformance 驗收 + baton/ 六份全量 mv 歸檔（含 SOP → sop/）+ TODO.md 結案 | `17d187b` |

> **修法依據**：`.claude-logs/plans/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md`

### OPTIMIZE-1 PDF上傳自動無損優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `utils/pdf_optimizer.py`（Atomic Overwrite + Logging SOP）+ `tests/test_pdf_optimize.py`（2 tests） | `b8892be` |
| C2 | 後端 is_slides_pdf 刪除 + optimize_pdf_lossless 整合 + doc_type Form 直通 + 前端 Phase-Shift 翻轉 + 3 tests | `28f098e` |
| C3 | Final Archiving and TODO Sync（baton/ 全量 mv 歸檔 + TODO.md 結案） | `93ab716` |

> **修法依據**：`.claude-logs/plans/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md`（v2）

### WORKFLOW-2 流程模板重構與提示詞自動歸檔

| Commit | 內容 | Hash |
|---|---|---|
| WORKFLOW-2-Tasks | Tasks 拆分（baton 暫存，C5 歸檔） | `7a3332f` |
| C1 | R1 五大提示詞模板自愈歸檔防線 | `b3e22c7` |
| C2 | R2 Check Conformance 維度四+五 | `5d7bdda` |
| C3 | R3+R4 SOP 備份暫存鐵律 + §8 重構 | `5a55939` |
| C4 | R5a 歷史 9 份提示詞物理補建 | `10f9561` |
| C5 | R5b INDEX 幽靈自癒 + 全案收官歸檔 | `7a3332f` |

> **修法依據**：`.claude-logs/plans/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`

### TODO-HOTFIX-1 TODO.md 緊急狀態與殘留修復

| Commit | 內容 | Hash |
|---|---|---|
| TODO-HOTFIX-1 | RAG 狀態整理與 RAG-11/12 抽離（RAG 狀態修復） | `a0d1951` |
| TODO-HOTFIX-1b | MODEL-8 進行中殘留清理（MODEL-8 狀態清理） | `2c78f9e` |
| TODO-HOTFIX-1 Check | Conformance 驗收與歸檔收官（第三階段驗收） | `5f3ef01` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md`

### WORKFLOW-1 流程簡化與文件治理

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Bootstrap Core（自動載入核心文件治理基礎） | `1a0394c` |
| C1.5 | Core Spec Align & TODO Bootstrap（核心規格與 TODO 自舉） | `e0c7a17` |
| C2 & C3 | Templates & Overview + Prompt Templates（模板與引導 / 提示詞模板） | `365aa5d` |
| C4 | SOP & Diagnostics（領域 SOP 與診斷目錄） | `ad0be4e` |
| C5 | 收官 (Closure) | `8965725` |

> **修法依據**：`.claude-logs/plans/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`（v11）

### Phase 4.7d Chat 改造（17 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 17-1 | 後端寫 DB + 廢前端 saveChatHistory POST | `8a1a0ec` |
| 17-1b | 切 paper 立即清 chat + SSE 改 asyncio.to_thread | `7452067` |
| 17-2 | stream broker + /chat/attach + /chat/history 加 in_progress | `5394365` |
| 17-3 | 前端 loadChatHistory + EventSource attach | `aed989c` |
| 17-4 | 移除 POST /chat/history endpoint | `a1adfbc` |

### Phase 4.7d RAG 改造（15 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 15-1 | chunk 優化（空 chunk / Context 前綴 / 短文合併） | `d6cb3df` |
| 15-2 | retriever 加 paper_title 引用 + score logging | `b6622a1` |

### Phase 4.7d RAG-7 doc_analyzer / md_cleaner 切 section 修正（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-7a | md_cleaner 偵測 + 移除重複 heading 行（浮水印自動偵測） | `e2ed0e4` |
| RAG-7b | heading_fix_resume.txt prompt + HEADING_FIX_PROMPTS['resume'] 改指 | `5c182cf` |

### Phase 4.7? MODEL-9 連線彈性防禦（1 commit）

| Commit | 內容 | Hash |
|---|---|---|
| MODEL-9 | 新增 `llm/_http_client.py` 共享 httpx.Client 工廠（timeout 5/60/30/60 + Keep-Alive pool）+ LLMClient / EmbeddingModel 注入 + `llm/retry.py` 升級為 Full Jitter (`random(0, min(MAX, base*2^attempt))`) + 7 個 factory pytest + 2 個 retry pytest；R1 graceful shutdown + R2 環境變數 override（`GEMINI_*_TIMEOUT` / `LLM_RETRY_MAX_BACKOFF`） | `dd18922` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-9_連線彈性防禦_plan.md` §4 + baron R1/R2 補充
> **環境變數**：`GEMINI_CONNECT_TIMEOUT=5` / `GEMINI_READ_TIMEOUT=60` / `GEMINI_WRITE_TIMEOUT=30` / `GEMINI_POOL_TIMEOUT=60` / `GEMINI_MAX_KEEPALIVE=20` / `GEMINI_MAX_CONNECTIONS=100` / `GEMINI_KEEPALIVE_EXPIRY=30` / `LLM_RETRY_MAX_BACKOFF=60`

### Phase 4.7? MODEL-3 tiling 三合一優化（3 commits、B1 + B2 + B3）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | 短文 Fast-path Bypass + `_join_content` helper（修正 1 防排版災難）+ `_bypass_content` 保留 index（修正 2 防 md_restore 對齊破裂）+ `TILING_MAX_LENGTH` env（修正 5）+ pipeline_core 傳 doc_type；新增 10 個 pytest | e97ddd2 |
| B2 | `_merge_small_text_blocks` 改寫：`SOFT_TYPES`/`HARD_BOUNDARY` 常數 + 公式穿透合併 + formula 永不 flush（修正 3）；新增 6 個 pytest | abed78d |
| B3 | `_process_content` long_doc_mode + `_PARAGRAPH_SPLIT_RE` regex（修正 4 容錯 `\r\n` / 多餘空白）+ `TILING_PARAGRAPH_THRESHOLD` env + `tiling_method` 標籤完整化（bypass / paragraph / delimiter / sentence / passthrough）；新增 7 個 pytest | 9177930 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-3_短文Bypass_公式穿透_段落滑動_plan.md`（§4.0 + §4.1 + §4.2 + §4.3 + §4.6 + §3.5/3.6/3.7/3.8/3.9 修正 1-5）
> **環境變數**：`TILING_BYPASS_CHAR_LIMIT=5000` / `TILING_MAX_LENGTH=2500` / `TILING_PARAGRAPH_THRESHOLD=30000`（皆預設）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/{vector_store,*_tiled.json}` → 重啟）執行；觀察 `[tiling bypass]` + `tiling_method` 標籤為書籍場景 / RAG-3 校準鋪路。

### Phase 4.7? MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI（3 commits、C1 + C2 + C3）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 加 `PaperChunk` ORM + `Paper.chunks` relationship + `paper_manager.py` 加 3 個 DAL helper（不重做 `get_paper_db_id`、修正 5）+ `processor/rag_processor.py` 加 `CHUNK_FILTER_VERSION` 常數 + `settings.py` 加 `OUTPUT_DIR` env（修正 7、依 db_analysis §5.2）+ `web_server.py:77-78` 改 `from settings import OUTPUT_DIR`（2 行、其他 20+ 處引用不動）；新增 7 個 pytest | aeb42cb |
| C2 | `processor/rag_processor.py` 加 module-level `write_index_meta_json`（修正 4、CLI 共用）+ `RagProcessor._write_paper_chunks_to_db` method + `process` / `_create_vector_store` 加 `paper_db_id` 參數 + `pipeline_core.py::_stage_rag` 加 2-3 行 `paper_db_id` 注入（修正 2、不動 web_server）；新增 5 個 pytest | ab40fdc |
| C3 | `tools/regen_rag.py` 新檔（6 子命令：`--check / --paper / --all / --force / --dry-run / --init`、含 cmd_init 修正 6 完整 pseudo-code 反向導入既有 paper）；新增 7 個 pytest | 16f62d4 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md` v3（§3.1 + §3.2 + §3.3 + §3.3.1 + §3.4 + §3.6 + §5.1 + §6 + §7 + Q1-Q18 + 附錄 A/B）+ `.claude-logs/ref/db_analysis_and_future_extension.md`（§1 + §3.1 + §4 + §5.2 + §5.3）
> **8 個修正**：路徑統一 `vectors/` / paper_db_id 內部注入 / 移除 tiling_method / write_index_meta_json 抽 module-level / 不重做 get_paper_db_id / cmd_init pseudo-code 完整 / OUTPUT_DIR env 化 / Pg-Ready 安撫
> **環境變數**：`OUTPUT_DIR=/app/storage/output`（預設 `_BASE_DIR / "output"`、Docker / K8s 部署用）
> **Backfill 一次性 SOP**：baron OrcStack 端 `git pull && venv/bin/python tools/regen_rag.py --init` 從 `vectors/` FAISS docstore 反向導入既有 paper、未來升 embedding 直接 `--all`、< 5 分/書籍。

### Phase 4.X? RAG-1 Phase 2 Hashtag RAG 路由 + 雙語摘要 + Chat Token UI（3 commits、P2-1 + P2-2 + P2-3）

| Commit | 內容 | Hash |
|---|---|---|
| P2-1 | 雙語摘要管道：`processor/metadata_extractor._ALL_FIELDS` 加 `translated_abstract` + `pipeline_core._stage_translate` 完成後同步寫入 `self._metadata["translated_abstract"]`（source=translate_pipeline / confidence=high、try/except 防禦 / 空值不覆寫）；3 個 pytest | 26a4439 |
| P2-2 | 後端 hashtag RAG 路由：`settings.RAG_MULTI_TOP_K=7` env + `paper_manager.list_paper_uuids_by_tag`（owner-scoped、共用 R2 `_normalize_tag`）+ `paper_manager.parse_query_hashtag`（長標籤優先排序防 `#complex` 攔 `#complex_system`）+ `rag_retriever.retrieve_multi_with_context`（跨 paper 全域 Merge-Sort top-k、L2 normalize 後 cosine 可比）+ `AI_professor_chat.process_query_stream` 入口分流（0/1/多/無 4 路徑、繞 router、單篇路徑 100% 不動）；14 個 pytest | 9ee44f3 |
| P2-3 | 前端 chat hashtag token UI：`static/index.html` chat-input `<textarea>` → `<div contenteditable>` + placeholder hint（Q11 完整版）+ `:empty::before` data-placeholder CSS（§3.3.5-#1）+ `contenteditable="false"` 禁用契約（§3.3.5-#2）+ 全域 grep 替換 `.value` / `.disabled` / textarea autosize（§3.3.5-#3）+ autocomplete dropdown 綁 `#chat-input-area` 容器（§3.3.5-#4）+ Claude `/skill` 風格 hashtag-token + 6 個 JS handler（input / keydown / compositionstart-end / blur / mousedown / × remove）+ design/docs/components.md §11.2 Hashtag Token + dom-reference.md / interaction.md 同步註記；9 個 pytest（含 §3.3.5-#1 / #3 兩個 v2 grep test） | f85b830 |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_Phase2_執行計劃.md` v2（8 章節 + §3.3.5 四點防護補強 + 15 Open Questions Q1-Q15）+ `.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md`（後端全部 Proposed Changes）+ baron 新需求（chat hint + Claude `/skill` 風格 token UI）+ `design/docs/components.md §11.2`（新增）
> **計畫累積**：plan v1 → v2（補 §3.3.5 4 點防護：CSS placeholder / disabled 樣式 / 全域 grep / dropdown 錨點）→ 落地 P2-1/P2-2/P2-3、共 **26 個 pytest**（3 P2-1 + 14 P2-2 + 9 P2-3、含 §3.3.5-#1 / #3 兩個 v2 grep test）
> **核心設計亮點**：
> - **零 schema 變動**：讀 Phase 1 `metadata_json.user_tags` 陣列、共用 `_normalize_tag` 真理源
> - **單篇 / 多篇 分流**：多篇 hashtag 走新 `retrieve_multi_with_context` + 繞 router；單篇 / 無 hashtag 走既有 `_get_rag_context` 路徑、零變動
> - **全域 Merge-Sort**：L2 normalize 後 cosine score 跨 paper 可比、防 prompt 爆炸（top_k=7 env override）
> - **長標籤優先排序**：`sorted(tags, key=len, reverse=True)` 防 `#complex` 攔 `#complex_system`
> - **contenteditable 四點防護**（§3.3.5）：CSS `:empty::before` placeholder / `contenteditable="false"` 禁用契約 / 全域 grep 替換 `.value` / dropdown 容器錨點
> - **中文 IME 防護**（Q12）：`compositionstart/end` + `e.isComposing` 雙重防護、組字中不觸發 autocomplete
> - **跟 Phase 1 解耦**：Phase 1 寫入路徑 100% 不動、Phase 2 純讀 user_tags 陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. **P2-1**：上傳英文 paper → 跑完 pipeline → 切中文、toolbar abstract 顯示中文（不再 fallback 英文）
> 2. **P2-2**：建 3 篇 HR 履歷加 `#hr` tag → 輸入 `#hr 比較這幾篇` → AI 回答含 3 個 paper title 引用、後端 log「matched_papers=3」
> 3. **P2-3**：chat-input 顯示「輸入 # 可加入 hashtag 跨文獻搜尋」placeholder → 輸入 `#` autocomplete dropdown 跳出 → `↓` `Enter` 確認、`#hr` 變藍色 token → `×` / `Backspace` 一次刪掉
> 4. **跨文件問答收官**（baron 需求 3）：`#hr 我的學歷區應該怎麼寫？` → AI 跨 3 份履歷比較 + 統一建議
> **影響範圍**：純 user-facing 功能擴充、無 schema 變動、無 backfill 需求；舊 paper 缺 `translated_abstract` 走前端 R1 子項 F fallback

### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）

| Commit | 內容 | Hash |
|---|---|---|
| BUG-F1 | 前端 micro fix 包 — tag fallback / placeholder 斷行 / export-btn / --content-max-w（Bug 1/3/4/5、5 pytest） | `9877e54` |
| BUG-F2 | theme dropdown + ESC + P2-3 latent fix — dropdownAPI IIFE + TDZ-aware 3 段拆分（Bug 2 + Bug 11、6 pytest） | `ae20559` |
| BUG-F3 | .modal-input CSS — ui-fixes-batch B5 廣義 selector + color-mix 跨主題 focus ring（Bug 7、2 pytest） | `57c71c8` |
| BUG-F4 | P1 critical 4 項 — A1 trackProgress / A2 empty-state / A3 customPrompt / A4 closeBizPopups（9 pytest） | `646afe4` |
| BUG-F5 | P2 inconsistencies — B1 廢 token 替換主 scale + B3 demo-bar dead code + B4 no-op（8 pytest） | `e799687` |
| BUG-F6 | P3 polish — C4 ~43 ticket 註解清理 / C5 marked 改寫 / C7 ⋯→SVG；C3+C6 no-op（7 pytest） | `12428aa` |
| BUG-B1 | 後端 abstract fallback — A 側路 translate_text + B regex 擴中日文「摘要/概要/內容提要/要旨」（Bug 8、28 pytest） | `a35a720` |
| BUG-B2 | 後端 blockquote→list + 前端 paper-header-meta CSS — `>` → `-` list + `<div>` wrap + @media screen（Bug 10、7 pytest、全鏈路收官） | `94ed27d` |

> **修法依據**：`.claude-logs/2026-05-24_RAG-1_前端_Bug_Fix_可行性評估.md` v2/v3 + `.claude-logs/2026-05-24_RAG-1_Bug_Fix_可行性評估.md` v4  
> **收官摘要**：6 前端 + 2 後端 = 8 commits、修 9 / 11 bugs、共 72 pytest 全綠、零迴歸；Bug 6 / Bug 9 延後為 RAG-11 / RAG-12

### Phase 4.X? RAG-1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫（3 commits、R1 + R2 + R3）

| Commit | 內容 | Hash |
|---|---|---|
| R1 | UI Fixes 子項 A/C/F/G 部分：`paper_manager.set_paper_tags` 新增 + `web_server.PaperUpdate.tags` Pydantic 擴充 + PATCH `/api/papers/{paper_uuid}` 整合 tags 處理 + `static/index.html` Modal CSS 補 `--radius-md` / `--font-display`（子項 C）+ `renderTitleHeader` 雙語 abstract fallback（子項 F）+ `#lang-toggle` 切語言後重繪 toolbar（子項 F）+ `#current-title padding-right` + `details.title-abstract max-height: 12rem` 防遮擋 / 防破版（子項 G 部分）；3 個 pytest | 9977428 |
| R2 | UI Fixes 子項 B/D/E/G 剩餘/H + v3 強化全域 lowercase：`paper_manager._normalize_tag()` module-level helper（單一真理源、lowercase + strip）+ `set_paper_tags` 整合 `_normalize_tag` + dedup + `web_server.upload_theme` endpoint（5 道安全過濾）+ `static/index.html` 加 `#` 標籤按鈕 + tag-modal + theme upload UI + tag-pill 半透明磨砂玻璃 + 風格選項英文化（Kahn · Kimbell Art Museum / Yoshitomo Nara）+ 移除「⚠ 後端未實作」警語 + `design/docs/theme-guide.md §7` 寫入 + `design/docs/components.md §11 Tag Pill` 新增 + `api_audit #23` 補完；13 個 pytest | f44a7e6 |
| R3 | 資料夾路徑自動標籤：`paper_manager._folder_ancestor_path_names`（遞迴向 root 取 folder name path、防環 + max_depth=32）+ `_apply_folder_path_tags`（共用 R2 ship 的 `_normalize_tag`、append + de-dup 策略、Q6/Q7 不清舊 tag）+ `set_paper_folder` commit 後 hook（try/except 包覆、不阻塞 core move）；7 個 pytest（HR/CV 基本 / 4 層巢狀 / lowercase / dedup / 未分類保留 / corrupt metadata / 中文 folder） | 49fe66a |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md`（§4.1 + §4.2 + §4.3 + §5 + §6 + §7 + §8 Q1-Q18 + §10）+ `.claude-logs/ref/2026-05-23_RAG-1_UI_Fixes_Implementation_Plan.md` v3（8 大子項 A-H + v3 強化段 + 附錄 C 4 點深度評估認證）+ `.claude-logs/ref/api_audit_and_performance_report.md` #22 + #23 + `design/docs/components.md §2 §6 §11` + `design/docs/theme-guide.md §7`
> **4 輪 review 累積**：v0 原始 UI Plan → v2 整合資料夾自動標籤 + Q1-Q10 決策 → v3 全域 lowercase 強化 + 4 點深度評估認證 → 落地 R1/R2/R3 3 個 commit、共 **23 個 pytest**（3 R1 + 13 R2 + 7 R3）
> **核心設計亮點**：
> - **零 schema 變動**：所有 tag 寫進既有 `metadata_json.user_tags` 陣列
> - **後端 Hook 注入**：所有 client（前端拖拽 / 對話框 / 首次上傳 / CLI）統一觸發、前端零負擔
> - **單一真理源**：`_normalize_tag()` 為所有 tag 寫入路徑唯一 normalize 入口
> - **中文友善**：`.lower()` 對中文無效、`#人資` `#工程` 保留原樣
> - **防禦性容錯**：`_apply_folder_path_tags` `try/except` 包覆、不阻塞 core `set_paper_folder` 移動
> - **Backward compat**：既有大寫 tag 不 retroactively 改寫；既有 R1 `set_paper_tags` 3 個 pytest 重構後仍 passed
> - **跟 Phase 2 解耦**：本 RAG-1 ship `metadata_json.user_tags` 寫入路徑、`.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md` Phase 2（hashtag RAG 路由 + parse_query_hashtag + retrieve_multi_with_context）讀此陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. 移動 paper 到資料夾 HR/CV → 重整、tag-pill 顯示 `#hr #cv`
> 2. 在 `#` Modal 輸入 `#HR #plant 工程` → 儲存後顯示 `#hr #plant #工程`（v3 lowercase + 中文保留 + dedup）
> 3. 從 HR/CV 移回未分類 → 自動 tag `#hr #cv` 保留（Q6/Q7）
> 4. 上傳 .css 主題 → 立即套用 + 重整不失效
> **影響範圍**：純 user-facing UI + 後端 helper、無 schema 變動、無 backfill 需求

### Phase 4.X? LOGGING refactor 統一日誌基建（3 commits、LOGGING-1 + 2 + 3）

| Commit | 內容 | Hash |
|---|---|---|
| LOGGING-1 | `utils/logging_config.py` 新檔（`JSONFormatter` + `ConsoleFormatter` + `setup_logging` + `reset_logging`）+ 補強 1 冪等性 + 補強 2 第三方劫持（`uvicorn` / `uvicorn.access` / `uvicorn.error` / `sqlalchemy.engine`）+ 補強 4 + v3 建議 1 exception 結構化 + v4 建議 1 噪聲分流（SQLAlchemy DEBUG-only / Uvicorn 動態）+ v4 建議 2 ContextVar `default=None` 雙保險 + v4 建議 3 `json.dumps default=str` 降級 + 🔴 v3 陷阱 1 `ConsoleFormatter.asctime` 顯式綁定 + 🔴 v3 陷阱 2 `uvicorn.run(log_config=None)`；`settings.py` 加 5 env（`LOG_LEVEL` / `LOG_DIR` / `LOG_FORMAT` / `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT`）；`web_server.py` 替換 `_setup_logging`；16 個 pytest | 011cc8c |
| LOGGING-2 | `web_server.py` 加 `@app.middleware("http") trace_id_middleware`（在 `auth_guard` decorator 與 `SessionMiddleware add_middleware` 之間、確保 `request.session` 可讀 owner）+ `X-Trace-ID` request/response header + `ContextVar set/reset` 跨 request 隔離（try/finally）+ SSE chat 路徑（`web_server.py:151 asyncio.to_thread`）自動繼承 ContextVar（Python 3.12.3、補強 3 / §4.11）；9 個 pytest | 3e406a1 |
| LOGGING-3 | `tools/regen_rag.py::main` 改用 `from utils.logging_config import setup_logging` 取代 `logging.basicConfig`；CLI 場景對齊 web_server 共用 settings env + Formatter + 噪聲分流 + ContextVar 雙保險；補 1 個 pytest | 6e764ea |

> **修法依據**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md` v4（§4.3 + §4.4 + §4.8-4.19 + §6 + Q1-Q22 + 附錄 v2/v3/v4 對照表）+ `.claude-logs/ref/logging_refactor_proposal.md`
> **4 輪 review 累積**：v0 原始 → v2 補強 4 點 → v3 致命陷阱 2 + 架構優化 2 → v4 生產健壯性 3 點、確保「不缺漏任何已知陷阱」
> **環境變數**：`LOG_LEVEL`（預設 INFO）/ `LOG_DIR`（預設 `_BASE_DIR/logs`）/ `LOG_FORMAT`（預設 `auto`、auto/json/console）/ `LOG_MAX_BYTES`（預設 10MB）/ `LOG_BACKUP_COUNT`（預設 5）/ `ENVIRONMENT`（development / production、控制 auto 切換）
> **Docker 部署**：`docker run -e ENVIRONMENT=production -e LOG_FORMAT=json -e LOG_LEVEL=INFO ...`、web_server + CLI 都自動 JSON output、Loki/ELK 可解析
> **不採納**：第三方 lib `structlog` / `loguru`（Q2）/ background pipeline ContextVar 跨 thread 注入（Q8、用既有 `[MODEL-8] owner=X paper=Y` 串連 90% 場景）

### Phase 4.7? MODEL-1+2 Embedding 升級（2 commits、B1 + B2）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | EmbeddingModel 升級 `gemini-embedding-2` + MRL 768 維 + `_l2_normalize` helper（防禦升級：空值 / 1e-6 / 零向量 → `[0.0]*len`）+ 4 處 embed call 套用 + `EMBEDDING_OUTPUT_DIMENSIONS` env override；新增 10 個 pytest（`tests/test_embedding_normalize.py`）| `f415218` |
| B2 | `rag_processor._is_chunk_meaningful` helper（修正 2 markdown 噪聲 + 修正 4 履歷防誤殺 `resume/slides ≥ 3` + email/phone/url 保留）+ `rag_retriever` raw score logging + `RAG_SCORE_THRESHOLD` env 化（修正 1、預設 0.22）；新增 11 個 pytest（`tests/test_rag_chunk_filter.py`）| `de649cc` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-1+2_Embedding升級_plan.md`（§4.1 + §4.2 + §4.3 + §4.6 + §3.6 修正 1/2/3/4）
> **環境變數**：`EMBEDDING_MODEL_NAME=gemini-embedding-2` / `EMBEDDING_OUTPUT_DIMENSIONS=768` / `RAG_SCORE_THRESHOLD=0.22`（預設）/ `RAG_*_TIMEOUT`（MODEL-9）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/vector_store/` → 重啟）執行；觀察 `[chunk filter]` + `[retrieve raw]` log 為 RAG-3 score 校準鋪路。

### Phase 4.7? RAG-8/9 翻譯保留排版下游 bug（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-9 | `static/index.html` marked.js GFM strikethrough 關閉、避免單 `~` 配對成 `<del>`（履歷 `100~500 人` / `2003/8~ 仍在職` 等 tilde 範圍語法） | `3a0c523` |
| RAG-8 | `processor/md_restore_processor.py` 加 `_preserve_pipe_table()` helper、L683-684 改用 helper 保留 pipe table 結構；+ 6 個 pytest（`tests/test_md_restore_table_preservation.py`） | `230ca13` |

> **修法依據**：`.claude-logs/2026-05-22_RAG-8_RAG-9_合併診斷_plan.md`（§4.1 + §4.2 修法 1）
> **Backfill**：baron OrcStack 端對 < 10 份既有 paper 重跑 md_restore stage、user-facing 驗證可接受（江元杰 `~` 不再撞線 ✅、DeHunt 學歷 table 自然文字流呈現 ✅、HVDC slides table 欄位對齊正確 ✅）。

### Phase 4.7e Resume 獨立 Pipeline（含 1 次 revert+v2 重做）

| Commit | 內容 | Hash |
|---|---|---|
| 7e-1（舊、已 revert） | ResumeProcessor + Vision prompt + chat_with_images（方向走偏：重組摘要） | `ffb3000` |
| 7e-2（舊、已 revert） | resume 走獨立 ResumeProcessor + doc_analyzer 短路 | `fdc2838` |
| Revert 7e-2 | revert 上述 7e-2 | `32563b5` |
| Revert 7e-1 | revert 上述 7e-1 | `ce91665` |
| 7e-1 v2 | ResumeProcessor 重寫、忠實轉錄 + 主標題黑名單對齊手冊 v2 | `1fb2d7b` |
| 7e-1 v2 hotfix | prompt 加投遞元資訊排除 + 主標題抽取優先順序（解黃忠偉 case） | `eb2164c` |
| 7e-2 v2 | pipeline_core 整合 ResumeProcessor + md_cleaner 跳過（保留 doc_analyzer 雙保險 = baron Q6） | `70889aa` |

> **7e-3 v2** 為 baron OrcStack 端到端 backfill 驗證（重新上傳 DeHunt / 黃忠偉 / 江元杰）、無 commit、純驗證活動；驗證滿意後本系列收尾。

---

## 🟡 進行中 / ⬜ 未開始（依優先序）

### 🔴 高優先

- 🟡 **RESCUE-1 遺失治理文件挽救**（`.claude-logs/baton/2026-06-28_RESCUE-1_遺失治理文件挽救_plan_v1.md`）
  - [x] ✅ C1 — Restore Queue v2（還原 QUEUE-1 v2 雙實例排程計畫）〔QUEUE-1 v2 存活本體逐字保全 9890 bytes + archive `.bak` 審計副本;deviation：依 tasks §8 主 repo 就地執行〕
  - [x] ✅ C2 — Rebuild PIPE-SPEC v8（重建共用真理源規格書 v8）〔v7 `.bak` 基底 + C2 執行報告 D5-D8.1 + 對照現役 code 重建;§1.2.5 section_engine + §1.2.4 MetaNormalizer 契約章 + §1.1.1 litedoc 旁路 + 三大→家族 + §99.2 v8;D8.1 逐字守 .bak;誠實標註非 byte-identical〕
  - [x] ✅ C3 — Purge MODEL-10 Residue（清理已收官殘留）〔`mv baton→archive`〔15313 bytes·tracked 審計·不直接刪除〕;baton 無 MODEL-10、archive 含之〕
  - [/] 🟡 WIP: C4 — TODO Reconciliation（TODO 狀態與遺失清單總修正）
  - [ ] ⬜ 未開始: C5 — Checkout（收官與歸檔）
  - 工時：5 個 commits（DOC-Refactor 純文件挽救）
  - 依賴：無（C1-C4 各自獨立，C5 收官）
  - 來源：舊 worktree 刪除致 baton git-ignored 文件遺失；plan v1.2 §9 六 OQ 全定案（工作目錄改主 repo·授權限 `.claude-logs/{baton,archive}`+`TODO.md`）

- 🔵 **CHAT-STRUCT-1 — 結構化欄位確定性回答（履歷聯絡 #5·選 C）**（plan 已產、**待 baron 過目 Open Questions → tasks**；`.claude-logs/baton/2026-06-08_CHAT-STRUCT-1_結構化欄位確定性回答_plan_v1.md`）
  - #5：履歷 candidate_name/phone/email/domain 只在 DB metadata_json + final_zh header、不入向量 → 「他的 email/電話?」RAG 撈不到（聯絡屬結構化、嵌入效果差、RAG 非對的工具）
  - 解法（選 C）：chat 路由層偵測結構化欄位意圖 → 直接從 paper metadata 取值、確定性模板回答、繞過 RAG；缺欄位明確「未提供」不幻覺；零向量/RAG 召回/schema 變動（純讀 metadata）
  - 狀態：**plan 純規格（§7 八項 Open Questions 待拍板，尤 Q1 意圖機制混合/Q3 欄位集/Q4 值 pin）**
  - 性質：跨 chat 模組（AI_professor_chat + ai_router_prompt）；不依賴 #1/#2/#4（與 P4 向量路正交）

- 🔵 **QUEUE-1 文件優先權協同避讓調度器**（`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）
  - PipelineCore 實作 class-level 執行緒安全任務註冊表
  - 依 doc_type 與檔案大小自動計算優先權（1/2/3）
  - 階段迭代頂端實作 should_yield 協同避讓與 sleep(2) 迴圈
  - 確保 try...finally 結構保證註冊解除，無死鎖
  - 新增 tests/test_priority_scheduler.py 驗證協同暫停與恢復
  - 工時：1-2 個 commits
  - 依賴：無

- 🔵 **INFRA-2 PipelineCore第一階段切分與定規**（`.claude-logs/baton/2026-05-30_INFRA-2_PipelineCore第一階段切分與定規_plan.md`）
  - [ ] ⬜ 未開始: 文件一 — 現有架構分析報告（`2026-05-30_INFRA-2_PipelineCore現有架構分析_report.md`）
  - [ ] ⬜ 未開始: 文件二 — 新流程規劃設計說明書（`2026-05-30_INFRA-2_PipelineCore新流程規劃_design.md`）
  - [ ] ⬜ 未開始: 文件三 — 數據接口合約 SPEC（`2026-05-30_INFRA-2_PipelineCore接口合約_specification.md`）
  - 工時：1 個 commit（大改版前置定規規格凍結，無程式碼變動）
  - 依賴：無

- ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
  - 問題：切換 paper / 重新整理後，SSE chat history reload 功能缺失（API 合約需調整）
  - 工時：待 plan 評估（預估 1-2 commits）
  - 依賴：無


### 🟡 中優先

- ⬜ **RAG-4 前端引用顯示**（Commit 15 plan Q3）
  - footnote / 「參考章節」清單 / 連結回原文段落
  - 工時：2-3 個 commits（前端 markdown 渲染 + 點擊跳轉）
  - 依賴：15-2 已提供 section_path

- ⬜ **RAG-3 score 閾值 0.22 校準**（Commit 15 plan Q4）
  - 跑 1-2 週實際 query、收 B2 `[retrieve raw]` logging 數據
  - 用 `grep '\[retrieve raw\]' logs/*.log` 抽 raw score 分布
  - 依 p10/p50/p90 調整閾值
  - **L2 normalize 後預期區間**：raw score 會顯著拉寬、相關 chunks 落 0.45-0.75、無關 < 0.25
  - **推測閾值升到 0.35-0.45 區間**（B2 預設保留 0.22、待實測決定）
  - 透過 env override 動態調整：`export RAG_SCORE_THRESHOLD=0.40`（不需 commit）
  - 工時：1 個 commit（純調常數預設 + 加註解、本機 env 已可先調）
  - 依賴：等資料累積（不能立刻做）

- ⬜ **CHAT-3b 前端清理 POST /chat/history 殘留**（Commit 17-4 報告新加）
  - 17-1 已刪 saveChatHistory 函式定義、留 marker 註解（`static/index.html` L2422 + L2487 兩個 Phase 4.7d Commit 17-1 marker）
  - 17-4 已移後端 endpoint
  - 前端可清掉 marker 註解 / dead reference
  - 工時：5-10 分鐘、純清理
  - 依賴：無（與 CHAT-5 可一起做）

### 🟢 低優先

- ⬜ **RAG-5 短文合併上限 cap**（Commit 15-1 已知限制 #3）
  - 實測若 chunk 過大（> 20 text items）需加上限
  - 工時：觀察驅動、實際撞到才做
  - 依賴：實測撞到

- ⬜ **RAG-6 `_SHORT_DOC_TYPES` 寫進 HOW_TO_ADD_DOC_TYPE.md**
  - 補說明短文型決策標準
  - 工時：1 個小 commit、純 docs
  - 依賴：無

- ⬜ **CHAT-4 取消進行中對話功能**（Commit 17 plan Q7）
  - 用戶按 Esc / cancel button 中止 stream
  - broker 支援 cancel：`session.cancelled = True` → `_run_stream_background` 檢查
  - 工時：1-2 個 commits
  - 依賴：留 4.7e 之後

- ⬜ **CHAT-5 `paper_manager.save_chat_history` 移除（dead code）**（Commit 17-4 報告盤點發現）
  - 17-4 後 0 業務 caller、變 dead code candidate
  - 工時：5 分鐘、純清理
  - 依賴：無(與 CHAT-3b 可一起做)

### 🔵 候選（待 baron 評估、依 `.claude-logs/model_optimization_blueprint.md`）

- 🔵 **RAG-10 中文 Header Meta Block 軟換行渲染 bug**（user-facing 排版、修法 ~5 行、低風險）

  **問題**：論文 Header 區的「作者 / 日期 / 出處 / DOI / 關鍵字」blockquote 在前端渲染時全擠成一行、無斷行。

  **症狀範例**（Jian Xu et al. 2026-01-26 Wuhan University paper）：
  ```
  > 作者：Jian Xu、Xinxiong Jiang... 日期：2026-01-26 出處：Wuhan University 關鍵字：AI data center...
  ```
  預期：每個欄位獨立一行。

  **根因**：CommonMark / GFM 規範下、blockquote 內連續多行**無空行**時、會被解析為**軟換行（soft break）**、在 HTML `<p>` 內被瀏覽器渲染為**單一空格**。`marked.js` 預設行為符合此規範（已 grep `static/` 確認無 `marked.setOptions({ breaks: true })`）。

  **代碼證據**（grep `processor/md_restore_processor.py` 實測）：
  - `_render_header_en`（L435 簽名、meta_bits L460-L470）：
    ```python
    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **Authors**: {', '.join(...)}")  # ← 行尾無斷行標記
    if date:
        meta_bits.append(f"> **Date**: {date}")
    if venue:
        meta_bits.append(f"> **Venue**: {venue}")
    if doi:
        meta_bits.append(f"> **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")
    ```
  - `_render_header_zh`（L484 簽名、meta_bits L511-L519）：相同 pattern、中文欄位。

  **Markdown 標準斷行語法（三選一）**：
  1. 行尾雙空格 `"  "`（推薦、最低侵入）
  2. 行尾反斜線 `\`
  3. 行之間插入僅有 `>` 的空行

  **修法（推薦從後端產生器修正、不改前端）**：

  在 `_render_header_zh` + `_render_header_en` 兩處 `meta_bits.append(...)` 結尾、每行**字串末尾補兩個半形空格**：

  ```python
  # _render_header_en L460-L470
  meta_bits.append(f"> **Authors**: {', '.join(...)}  ")   # ← 末尾補 "  "
  meta_bits.append(f"> **Date**: {date}  ")
  meta_bits.append(f"> **Venue**: {venue}  ")
  meta_bits.append(f"> **DOI**: {doi}  ")
  meta_bits.append(f"> **Keywords**: {', '.join(keywords)}  ")

  # _render_header_zh L511-L519 同樣處理
  ```

  **為何不用前端 `marked.setOptions({ breaks: true })`**：
  - 全域開啟會把所有 paragraph 內的單換行都變 `<br>`、可能破壞原本應該軟換行的 chunk content 排版（如 PDF 內單句跨行的情況）
  - 從後端修正才是定點打擊、零副作用

  **預估工時**：~30 分鐘（含 pytest）

  **拆 commit**：單一 commit（FIX-1）即可、無依賴

  **新增 pytest**（推薦 2-3 個）：
  - `test_render_header_zh_appends_double_space_for_soft_break`
  - `test_render_header_en_appends_double_space_for_soft_break`
  - `test_rendered_meta_block_has_br_in_html`（mock 過一遍 marked.js 風格的解析、驗證 `<br>` 存在）

  **影響範圍**：
  - 僅影響 `_tiled.json` → 最終 markdown 的 Header 區渲染
  - **不需 backfill**（純前端 markdown 字串差異、既有 paper 重開即生效）
  - 既有 paper 重新前端 load 即修正、無需 vector store 重建

  **依據**：
  - CommonMark §6.7 Blockquote + §6.5 Hard line breaks
  - 修正後 HTML 預期含 `<br>` 而非 inline space

- ⬜ **MODEL-5 Structured Outputs router**（依 model_optimization_blueprint.md §3.2）
  - 升級對話路由器、利用 Gemini SDK Structured Outputs (JSON Schema)
  - Pydantic 聲明 `RouterDecision` 模型、消滅 regex + `json.loads`
  - 改 ai_chat / ai_router 相關檔案
  - 工時：1 commit
  - 依賴：無
  - 解 router 對格式變動的脆弱性

- 🔵 **MODEL-7c Metadata 語意前綴增強**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.3、新增）
  - 在生成 Chunk 文本時、最前端注入全域 Metadata 前綴
    - 範例：`"Candidate: John Doe | DocType: Resume | Section: Employment | [內文]"`
  - 將全域背景與局部細節強制綁定、強化語意特徵、embedding 也吃到 doc-level 語意
  - 工時：0.5 commit
  - 依賴：等 RAG-3 score 校準後評估必要性（可能 MODEL-1+2 已夠用、是否真的需要再評估）
  - **優先度低、純候選**

### 🚫 評估後不做（依 `.claude-logs/model_optimization_blueprint.md` / `.claude-logs/pipeline_decoupling_plan.md`）

以下提案經評估為過早優化 / 失控感 / 場景不符、暫不加入 TODO：

- **Parent-Child Indexing**（雙層檢索）
  - 提案：履歷子經歷小區塊向量化、父區塊回 LLM
  - 不做理由：履歷已切到 ### 公司層級、單份 7-8 chunks、痛點不大；實作複雜（chunk 結構 + retriever 邏輯 + schema 改動）、3-4 commits regression 風險高

- **128 Batching 自適應**（Embedding API 並行）
  - 提案：BATCH_SIZE 32 → 128、聲稱「30-50x 提速」
  - 不做理由：測試機 + < 10 份文件、batch size 增益無感（可能省 10-20 秒）；撞 429 風險上升、效益數字行銷話術不可信（實際提速 2-3x）

- **企業 Proxy（HTTP_PROXY/HTTPS_PROXY）**
  - 提案：受限網絡 / GFW 部署支援
  - 不做理由：個人測試機 + 台灣環境、無 firewall / 翻牆需求；未來若要賣企業客戶再做

- **AUTO Grounding（Gemini 自動聯網）**
  - 提案：Gemini 模型自己判斷何時聯網查 Google
  - 不做理由：論文 / 履歷分析場景需明確控制資料來源；AUTO 模式下 user 不知道答案來自文件還是 Google、UX 失控；應 user 明確 opt-in、不該預設啟用
  - **note**：手動 opt-in 聯網已存在於既有 `#web-search-toggle` 前端 toggle（`static/index.html` + `web_server.py:375 use_web_search` + `llm/client.py:118` Gemini Grounding）、整鏈路已通；不需新增 task 重做

- **Pipeline 解耦重構（pipeline_decoupling_plan.md 全套）**
  - 提案：17+ 檔重寫、`BaseStage` / `Context` / `Observer` / `Strategy` 完整體系
  - 不做理由：過早抽象、Mad Professor 是 2 人 / < 10 文件規模；7e-2 v2 `KNOWN_DOC_TYPES` + `check_doc_type_registry.py` 已解 80% 痛點；重構期 regression 風險巨大、機會成本超過所有收益；候選漸進式小手術（dict lookup parser / 並行 helper / module-level constants）可考慮、但全套重構不做

- **MODEL-6 聯網搜尋自動 Fallback 降級路由**（依 `.claude-logs/ref/model_optimization_blueprint.md` §3.2）
  - 提案：RAG max score < 0.35 時、自動切換 Web Search + Google Grounding
  - 不做理由：跟既有「AUTO Grounding 不做」決策**直接衝突**、本質是 trigger condition 不同的 AUTO Grounding；user 不知道答案來自文件還是 Google、UX 失控；mad-professor 定位是「論文/履歷分析助手」、用戶問問題期望基於文件
  - **未來若要做、改為「手動 opt-in 聯網按鈕」**、用戶按下才聯網 + 回答時明確標 [Google Search]

- **MODEL-7b 中英雙語對齊嵌入**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.2）
  - 提案：中英混雜文件、chunking 前拼接「原文 + 譯文」一起 embed、提高跨語召回
  - 不做理由：**gemini-embedding-2 是多語旗艦模型、跨語對齊本身就比舊 model 強得多**（MODEL-1+2 已內建解決 80%）；拼接後每個 chunk 大小翻倍、API tokens / storage 翻倍、是針對舊 model 的 workaround
  - **未來若 B2 backfill 後跑 1-2 週仍有跨語檢索品質問題、再重新評估**

---

## 索引（依類別）

### RAG（11 項 active）
- ✅ ~~LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放~~（已落地、C1 `8893ad1` + C2 `9849600` + C3 `c5b0c31` + C4 `6c0e8d2` + C5 Checkout 收官；③ retriever 自載咽喉〔_get_vector_store 完全 miss 呼 loader 自載〕+ is_ready loader-aware + 單一共享 RLock〔loader 鎖外防 AB-BA、修正 tasks §4.2 兩鎖隱患〕+ 啟動接線 set_loader + cap 5→100 + 釋放策略〔/content 換篇 gate·F1 + /upload 開關 + 跳過 active_streams + gc〕；治本 API-PERF C3 lazy-load 只載當前 paper 致 retrieve_multi 漏召其餘 tagged 篇〔#cv 只召當前篇〕；非 RAG-MULTI-1/非模型；test_lazyload_multi.py 10 測試〔含 §7.2 整合〕；⚠️ baron E2E 驗 #cv 涵蓋全 6 位）
- ✅ ~~RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正~~（已落地、C1 `5b9477a` + C2 `82b95b1` + C3 `b5f9ce4` + C4 + C5 Checkout 收官；retrieve_multi 廢全域 top-k 飢餓→每篇保底覆蓋〔min(floor_k,max(1,cap//N))+不足全拿+補位排除已選+N>cap最高分截斷〕+ 廢 RAG_MULTI_TOP_K 立 FLOOR_K/MAX_CHUNKS + ai_character_prompt 禁 [N] + test_rag_multi.py 11 測試；治本「6 篇擠成 2 人、吳焴倫碩士漏召」；五路通用；⚠️ shadow 不過濾＝U7 刻意副作用、baron 影子 E2E 驗多人涵蓋）
- ✅ ~~RAG-14 多標籤寬鬆格式跨文章RAG檢索與對話體驗升級~~（已落地、C1 `6593962` + C2 `b8e8770` + Check 收官 + 補漏 `595e3d8`）
- ✅ ~~RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI~~（已落地、P2-1 + P2-2 + P2-3 三 commit、見 ✅ 完成區）
- ✅ ~~RAG-1 Phase 1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫~~（已落地、R1 + R2 + R3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
- ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）
- RAG-3 score 校準（中、等數據）
- RAG-4 前端引用顯示（中）
- RAG-5 合併 cap（低）
- RAG-6 docs（低）
- 🔵 RAG-10 中文 Header meta block 軟換行渲染 bug（候選、修法 ~5 行、user-facing 排版）
- ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
- ✅ ~~RAG-12 LaTeX KaTeX 渲染支援~~（已落地、自託管 KaTeX 0.16.47 + 三階段順序佔位、C1-C6 收官）
- ⚙️ ~~RAG-2 backfill CLI~~（合併到 MODEL-8、見 MODEL 區）
- ✅ ~~RAG-7 doc_analyzer 切 section~~（已落地、拆 RAG-7a `e2ed0e4` + RAG-7b `5c182cf`）
- ✅ ~~RAG-8 md_restore / translate table 渲染 bug~~ `230ca13`
- ✅ ~~RAG-9 markdown `~` 誤判刪除線~~ `3a0c523`

### Chat（3 項 active）
- CHAT-3b 前端清理（中）
- CHAT-4 取消對話（低、留 4.7e 之後）
- CHAT-5 dead code 清理（低）

### MODEL（0 項中優先 / 2 項候選 / 6 項已落地）
- ✅ ~~MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次~~（已落地、C1 `1f56547` + C2 `d7f26be` + C3 `8c5a0eb` + C4 收官；換文字 embedding GA 模型恢復真批次 + task_type 非對稱；config.py embed_documents token-aware 貪婪拆批 + log 正名 embedding_batch_fallback；⚠️ 向量值改變→各環境須 .env 換用 + regen_rag --all 重嵌 + resume 單路 Golden 重捕〔baron 運維〕）
- ✅ ~~MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、合併原 RAG-2）
- ✅ ~~MODEL-1+2 Embedding 2 升級 + L2 正規化 + 短 chunk 過濾~~（已落地、B1 `f415218` + B2 `de649cc`）
- ✅ ~~MODEL-3 短文 Bypass + 公式穿透 + 段落滑動~~（已落地、B1 + B2 + B3 三個 commit、hash 待 push 後回填）
- 🔵 MODEL-5 Structured Outputs router
- 🔵 MODEL-7c Metadata 語意前綴（候選、低優先、等 RAG-3 結果再評估）
- ✅ ~~MODEL-9 連線彈性防禦~~（已落地、`dd18922`）
- ✅ ~~MODEL-9-OPT Embedding連線與限流框架優化~~（已落地、C1 `8feaa12` + C2 `9a44d41` + C3 `e86ced9` + C4 收官；EmbeddingModel Semaphore + retry_call 統一退避 + embed_documents 批次降級；不改向量值/不觸發 Golden 重捕；OQ3 RPM 令牌桶屬上線觀察項）
- ✅ ~~MODEL-10 MinerU 連線優化與運作維護 SOP~~（已落地、C1 `19ddac8` + C2 `991258d` + Check 收官）

### Phase 4.7e Resume Independent Pipeline（全完工）
- ✅ ~~7e-1 v2~~ `1fb2d7b`
- ✅ ~~7e-1 v2 hotfix~~ `eb2164c`
- ✅ ~~7e-2 v2~~ `70889aa`
- 7e-3 v2 端到端驗證（無 commit、純驗證、baron OrcStack 重新上傳 3 份 backfill 後收尾）

### WORKFLOW（✅ 已完成）
- ✅ ~~WORKFLOW-1 流程簡化與文件治理~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-2 流程模板重構與提示詞自動歸檔~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試~~（已落地、C1 `2e4d4c9` + C2 `386c1ce` + C3 `f14dcd9` + C4 收官；DOC-Refactor 治本 RAG-ASYNC #1 接縫缺陷——WORKFLOW_SOP §7 跨 Phase 接縫契約〔含 worked example〕+ 收官前整合測試〔key-changing transform、Checkout 必驗、顯式豁免〕+ §4.2 A6 / template_plan 升 plan 結構 SSOT / framework §4.1 改引用 template〔消滅 doc-drift〕；自身 DOC 無 handoff 整合測試豁免；plan v1/v2/v3 三版保留作 §1.9 軌跡）
- ✅ ~~WORKFLOW-4 StraTA 任務成功率原理移植進文件治理模板~~（已落地、C1 `44659be` + C2 `0e8cb77` + C3 `757dee6` + C4 收官；DOC-Refactor 移植 StraTA〔2605.06642v1〕四原理進 5 治理模板——U1 prompt_for_run 讀 plan〔conditioning re-inject 策略 z〕/ U2 execution §1 對齊欄 / U3 execution §自評雙軸〔負向防錯 + 正向「推進哪個 U-N」防做白工〕/ U4 template_plan §2.5 條件化多候選〔diverse rollout·高風險才觸發·語意分散〕+ prompt_for_plan 同步 + Q5 stale 校正 / U5 prompt_for_check 減負前移〔維度三/五前移分攤·非省略·聚焦 U-coverage+§7.2〕/ U6 五模板 marker+StraTA 誠實前提註；**WORKFLOW_SOP §4 五維度定義未動**；§7.2 純 DOC 顯式豁免；零業務代碼、640 passed 基線；見 ✅ 完成區）
- ✅ ~~WORKFLOW-5 ClawVM 混合治理 Hook 落地~~（已落地、C1 `6fd2ce2` + C2 `306797a` + C3 `2c14d4a` + C4 `c107bfd` + C5 `6ab46b9` + C6 `37f3ded` + C7 Checkout 收官；ClawVM 論文〔2604.10352v1〕——純文件約束＝discretion 結構性不足、跨出純文件用真實 Hook〔harness enforcement〕；C1 SessionEnd dry-run gate〔裁定不能 block→DIRTY-RESET Observable Fault·連鎖修正 exit 0+JSON 非 exit 2、python3 非 jq〕/ C2 baton 3-Phase 非破壞性寫入〔不可繞過〕/ C3 template Fidelity Floor 三維度〔機器可讀 fidelity_floor:〕/ C4 pre_tool_guard 截斷守衛〔防誤觸·sentinel 可繞過·truncation 8/8〕/ C5 dirty_reset_guard〔僅可觀測·dirty_reset 4/4〕/ C6 settings 掛載樣本+專案級部署 SOP；三道防線威脅模型誠實標註；§7.2 純治理+hook 豁免；零業務代碼；⚠️ baron 各環境手動掛載 .claude/settings.json + 重啟生效；見 ✅ 完成區）

### CHECKOUT-GUARD (✅ 已完成)
- ✅ ~~CHECKOUT-GUARD 收官 git-add 白名單鐵律~~（已落地、C1 `81179d8` + C2 `dbd6d24` + checkout 收官；DOC-Refactor 治 FE-PERF-1 收官跨任務混檔——`WORKFLOW_SOP §3` 立「收官 git-add 白名單鐵律〔逐檔·禁 `git add .`/`-A`/`<目錄>`·commit 前 `git diff --cached` staged 自檢〕+ checkout 執行報告鐵律」+§99.2 v6·三模板〔run/check/execution §8 警語 + check 收官第五步自檢/第六步 mandate 報告〕；§2.5 純文件鐵律選定〔hook enforcement 列 backlog〕；§7.2 純 DOC 豁免；零業務碼；**首次 dogfood checkout 執行報告鐵律 + Check 階段當場攔下 C2 未 commit〕**）

### FE-PERF (✅ 已完成)
- ✅ ~~FE-PERF-1 前端效能與渲染 SOP 建立~~（已落地、C1 `3ec7b3f` + C2 `4fb2248` + checkout 收官；DOC-Refactor 以 Osmani《How modern browsers work》稽核〔`baton/frontend_browser_standards_audit.md`〕立 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`〔效能 7 條紅線+渲染正確性陷阱 6 類 hotfix 溯源+驗收檢查表+§99.1 重複防護·120 行〕+ 回填 WORKFLOW_SOP §1.1/§1.4 FE 必讀 SOP+§99.2 v5〔補後端有/前端無之治理不對稱缺口〕；§2.5 sop/ 選定〔workflow-gated 不污染 @path〕；§7.2 純 DOC 豁免；零業務碼；歷史經 pre-fe-rebuild 備份後重寫為乾淨 commit 邊界；稽核 7 條實修屬另案）

### FE-AESTHETICS (✅ 已完成 + 🟡 HOTFIX-1 進行中)
- ✅ ~~FE-AESTHETICS 摘要工具列重構與正文扉頁美化~~（已落地、C1 `3cf8acf` + C2 `b735a94` + Check 收官）
- ✅ ~~FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化~~（已落地、C2-hotfix `bf3c14b` + Check 收官）

### FE-RHYTHM (✅ 已完成)
- ✅ ~~FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一~~（已落地、C1 `1ecdc5c` + C2 `a9f2c3a` + C3 Checkout 收官；單一 margin-top flow 模型〔基準流 4/非標題→標題 6/標題→* 2/p→清單 1〕取代逐交界補丁、**完全消滅 `:has()`**〔相容 Safari 14+〕、收編 FE-RHYTHM-1、取消擬議 FE-RHYTHM-2、4 主題垂直 margin 移交 base；零 .py、631 passed；⚠️ baron 三軌×四主題視覺 E2E、無 golden 重捕）
- ✅ ~~FE-RHYTHM-1 閱讀視圖「清單前寬後窄」垂直節奏治本~~（已落地、`3428581`；2 條 `:has()` p↔清單交界補丁；後由 FE-RHYTHM-UNIFY 收編為統一 flow 模型）

### RAG-13 (✅ 已完成)
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）

### RAG-13-HOTFIX-1 (✅ 已完成)
- ✅ ~~RAG-13-HOTFIX-1 自訂主題下拉選單捲軸無作用修復~~（已落地、C1 `6598d2d` + Check 收官）

### INFRA (1 項 active)
- 🔵 INFRA-2 PipelineCore第一階段切分與定規（高、`.claude-logs/baton/2026-05-30_INFRA-2_PipelineCore第一階段切分與定規_plan.md`）
- ✅ ~~INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新~~（已落地、C1 `264dadc` + C2 `9e05466` + Check 收官）

### QUEUE (1 項 active)
- 🔵 QUEUE-1 文件優先權協同避讓調度器（高、`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）

### OPTIMIZE (1 項 active)
- ✅ ~~OPTIMIZE-1 PDF 上傳自動無損優化~~（已落地、C1 `b8892be` + C2 `28f098e` + C3 收官）

### GOLDEN-BASELINE (✅ 已完成)
- ✅ ~~GOLDEN-BASELINE 黃金基準存盤與退化比對~~（已落地、OP-1 `3be0b0d` + OP-2 `74d34e8` + Check 收官；PIPE 大改版階段 1 完成）

### PIPE-CORE (✅ 已完成)
- ✅ ~~PIPE-CORE 三層解耦調度骨架~~（已落地、OP-1 `aa786a1` + OP-2 `effb155` + OP-3 `84b9b30` + Check `13c1dcb`；PIPE 大改版階段 1 骨架，`pipelines/` 六模組）

### PIPE-SYNC (✅ 已完成·真理源回灌)
- ✅ ~~PIPE-SYNC-4 litedoc 與 section_engine 落地回灌母 plan 與 SPEC~~（已落地、C1 master plan v10 回灌〔D1 technical 排除/D2 LiteDoc ✅+順序/D3 三大→家族/D4 順序註/v6〕+ C2 PIPE-SPEC 回灌〔§1.2.5 section_engine 契約章 + §1.2.4 MetaNormalizer 契約章 + §1.1.1 litedoc 旁路 + 家族措辭 + v8;D8.1 §1.3 L140/§3.3 15k/§2 ≥10/四凍結合約未動〕+ C3 HOW_TO_ADD B 軌範式〔頂部 A/B banner + §1.4 裝飾器機制+A/B 對比+U2.1 映射;A 軌 §2-§7 不動〕+ C4 Checkout 收官；共用真理源家族定調〔原始三大 + MetaNormalizer 第 4 + section_engine 第 5〕；§7.2 純 DOC 豁免、零代碼 686 passed；SPEC 本體長駐 baton 不版控、.bak→archive、master plan/HOW_TO_ADD tracked）
- ✅ ~~PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC~~（已落地、C1 SPEC v7〔D1 slides P3 drift/D2 golden A/B 軌/D3 alt LaTeX/D4 is_blank/D6 rag_sections §1.1.2/D7 rag_tree_json/D5〕 + C2 master plan 補註⁸〔§8.5「B 軌另捕」措辭修正〕 + C3 Checkout 收官；slides 路 7 hotfix 回灌兩真理源、四層交接+旁路全對稱〔D6 補 rag_sections 旁路登記〕；§7.2 DOC 豁免、零代碼 640 passed；SPEC 就地版控、master plan v10 plans/）
- ✅ ~~PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC~~（已落地、C1 `c54327c` + C2 `9666b20` + C3 `29f13ca` + C4 Checkout 收官；母 plan 補註⁶〔U1 矛盾/U2 stale/U3 key 母句/U8/U5 指標〕+ SPEC v6〔key 契約凍結/zh 路/§1.3.1 Vision 共用規格/-001 樣例/rag_tree 歸屬/三註〕+ sop 四檔去誤導〔model_recommendations -001🔴/guide 勘誤/doc_type banner+v1v2 歸檔/mineru RELEASE_ON_UPLOAD〕；§7.2 DOC 豁免；PIPE-VISUAL 開 plan 前置完成）

### PIPE-SCAFFOLD (✅ 已完成·階段一建)
- ✅ ~~PIPE-SCAFFOLD web_server 雙軌派發 scaffolding~~（已落地、OP-1 `13c1dcb` + OP-2 `6807a7f` + OP-3 `58e1b89`；旗標惰性插入點 + 影子派發單元 + 兩派發點閘門，A 軌 byte 不動；階段二 Flip 屬 PIPE-FLIP）

### API-PERF (✅ 已完成·PIPE 基建前置)
- ✅ ~~API-PERF API 技術審計與效能防呆優化~~（已落地、C1 `5326437` + C2 `e20054d` + C3 `76e47ed` + C4 `aad3737` + C5 `59e1c56` + C6 收官；U1-U7 並發信號量/nice/LRU/流式上傳/真實 IP/連接池/計時埋點+CLI；PIPE 並發底座就緒）

### DOMAIN-NORM (✅ 已完成·PIPE 共用真理源)
- ✅ ~~DOMAIN-NORM 領域標準化對齊器~~（已落地、C1 `8d4f75f` + C2 `125af97` + C3 `7e7f2a1` + C4 `aeb4fc2` + C5 收官；Domains/DomainMapping 兩表 + DomainNormalizer 內容判定/動態註冊不塞單字/快取防重 + normalize_to_lcc 入口 + LLM_USE_GLOSSARY_ALIGN 旗標預設 False；GLOSSARY-CORE/Translator 共同上游真理源就緒）

### GLOSSARY-CORE (✅ 已完成·PIPE 共用真理源之二)
- ✅ ~~GLOSSARY-CORE 中央領域術語庫與跨語系一致性~~（已落地、C1 `03d85c8` + C2 `9af971f` + C3 `fd0e84f` + C4 `06bf3df` + C5 收官 + C6 `ae705d5` + C7 收官；GlobalGlossary 表聯合唯一約束 + GlossaryManager 級聯查詢/交易外提取/冪等回填 + translate/chat 旗標閘門注入 + manage_glossary CLI；消費 DomainNormalizer LCC；書籍融合待 TRANSLATE-BOOK）

### TRANSLATOR (✅ 已完成·PIPE 共用真理源之三)
- ✅ ~~TRANSLATOR 雙模式原子翻譯器~~（已落地、C1 `1558f79` + C2 `27db830` + C3 `11ea52a` + C4 `2ebda03` + C5 收官；processor/translator.py InjectionContext〔7 欄〕/TranslateMode/Translator〔Prompt Engine 五步 + 雙模式路由 + U4 兜底〕+ contracts GlossaryReadySpec 補 domain_name + client thinking_config 受控擴充〔§4 唯一例外、前向相容〕+ caption 提示詞 + 8 pytest；消費 DomainNormalizer/GlossaryManager；三大真理源全數就緒；plan v10 八輪 review 定稿）

### META-NORM (✅ 已完成·PIPE 共用真理源家族第 4 員)
- ✅ ~~META-NORM 封面元數據自癒飛輪與動態欄位登記~~（已落地、C1 `ae407ef` + C2 `6dd48f8` + C3 `6c37a1d` + C4 `dedd915` + C5 `d2a3db2` + C6 `6bb440e` + C7 收官；解 PIPE-SLIDES 實測 C+D；MetaField/MetaFieldAlias 兩表 + MetaNormalizer 飛輪〔reserved BS1/黑名單 Q9/label BS4/temp=0 Q2〕+ P1 開放抽取/封面放寬接線 + subtitle〔D〕+ 前端通用渲染〔排除集 BS2/排序 BS7〕；§7.2 key-changing 整合正面達標；旗標 LLM_USE_META_NORM 預設 False；⚠️ baron 漸進開+Vision golden 重捕+餵養 CHAT-STRUCT-1）

### PIPE-LITEDOC (✅ 已完成·PIPE 縱向五路第 3 路)
- ✅ ~~PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁）~~（已落地、HOTFIX-1 `cbc512a`；**問題一**標題/Meta 重複→`section_engine.strip_title_echo` 雙剝〔① pre-strip full_text 原文層 exact·en 全模式+zh whole/is_zh / ② post-strip zh_text 補 section 模式·同 slot 譯文 exact〕→扉頁成唯一標題、RAG 不受影響〔rag_sections 早於兩剝定案〕;**問題二**日文/簡體未翻譯→P1 改用 `section_engine.classify_source_lang` 二元「是不是繁中」〔取 tiles 內文樣本跳封面·鎖三〕、非繁回 ja/ko/**hans**/en〔**簡體不給 zh* 字串**·鎖一、四處 startswith("zh") gate 零改不復活〕、偵測器放 section_engine 共用〔book 也用·鎖二〕、一次解 P3 is_zh + P2 section_summaries 雙 gate;只動 litedoc_pipeline+section_engine+測試、18 新測試、全套件 704 passed〔唯一 fail＝既有 LOG_FORMAT flake〕;扉頁保留〔OQ-b·理由 chrome 分層+academic-family 共用 paper-header-meta 結構，非 A 軌 golden 0%〕;⚠️ baron 影子 E2E〔日文/簡體轉繁、標題不重複、真繁中仍 bypass〕+ B 軌走改善豁免不需 A 軌 golden 重捕）
- ✅ ~~PIPE-LITEDOC LiteDocPipeline 策略管線~~（已落地、C1 `b1012bc` + C2 `18e47c1` + C3 `3570476` + C4 `f8940cd` + C5 `424ee93` + C6 `469f982` + C7 `ff16271` + C8 收官；第 3 路 news/web/unknown〔factory fallback〕;academic-lite——P1 MinerU 文字攝入〔非 Vision〕+ DocAnalyzer U2.1 映射 + B 軌原生 cover-prompt〔URL→publisher 解碼〕、P2-P4 **全消費共用真理源**〔section_engine + DomainNormalizer/Glossary/Translator + rag_indexer〕、size-gate〔<15k 一鍵/≥15k section〕+ HTML 扉頁〔render_meta_header_html·C1 純加法補〕+ U5c 雙語標題鏈 + 門檻 ≥10〔**rag_indexer 零改**〕;§7.2 key-changing 整合達標、litedoc 25 + 全套件 686 passed;**首個 section_engine 跨 consumer 驗證**;Q4 technical 排除〔母 plan v10 L72 分歧待 PIPE-SYNC 回灌〕;⚠️ baron 影子 E2E + golden 改善豁免）

### PIPE-SECTION-BASE (✅ 已完成·第 4 共用真理源·section 機制)
- ✅ ~~PIPE-SECTION-BASE 共用 section 機制抽取~~（已落地、C1 `e400789` + C2 `24db977` + C3 `4078a9e` + C4 `6bd8705` + C5 收官；resume 的「遞迴標題樹走訪→逐節點摘要/並行翻譯/排版還原/rag 旁路/meta header」抽成零 doc_type 耦合純函式 `pipelines/section_engine.py`〔§2.5 方案 A·llm/translator/prompt 注入·引擎零 doc_type 字面量·U3.1 meta header 純格式化器零讀 raw_metadata·U3.2 DFS 吃任意子樹〕、resume 改 delegate;行為等價〔RESUME-PERF-1 C1 範式·resume 42 passed〕+ tests/test_section_engine.py 17 測試〔含 base 層 key-changing 整合·堵 RAG-ASYNC-HOTFIX-1〕、全套件 657 passed;§7.2 不豁免達標;Q2 slide 重複不收編留後續;⚠️ 後續 litedoc plan 建於本引擎上）

### PIPE-SLIDES (✅ 已完成·PIPE 縱向五路第 2 路)
- ✅ ~~PIPE-SLIDES-HOTFIX-4 P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）~~（已落地；`_VISION_PROMPT` 基底加 `is_blank` 欄 + 第5條判定〔含封面〕+ `_process` ④ 雙保險跳過〔is_blank 且 title/content 皆空才跳、防誤殺有內容頁、純圖頁 is_blank=false 不跳、舊 golden 無欄向後相容〕;既有三欄全空保留為第二道、與 is_cover 對稱;真因＝Ch37 第16張空白頁 Vision 回非空 figure_description 漏舊判定;RAG/渲染/四路零碰;4 新 pytest、全套件 631 passed;⚠️ 改 Vision prompt → slides golden 併批次重捕、baron E2E 驗第16張不產頁+純圖頁未誤跳）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-3d 字面 `**` 未渲染粗體 + 裸 URL 破版（slide 渲染層清洗）~~（已落地；`pipelines/slide_pipeline.py` 新增 `_render_inline_bold`〔`**X**`→`<strong>` 繞 CommonMark CJK emphasis〕+ `_strip_bare_url_lines`〔剝整行裸 URL、保圖片行/行內 URL〕殿前注入；真因＝B 軌 vs 原稿比對 p27 字面 `**`〔CJK 緊貼〕+ p6/18/27/35 裸 URL 撐版；RAG 零影響〔merged 取原始 zh_content〕；零後端/四路；9 新 pytest + 真 marked 4/4、全套件 627 passed；⚠️ slides golden 併批次、baron E2E p27）
- ✅ ~~PIPE-SLIDES-HOTFIX-3c 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）~~（已落地；`pipelines/slide_pipeline.py` 新增 `_tighten_point_groups`〔連續行首箭頭合併硬換行〔保 `→`、不轉 bullet〕+ 相鄰清單 loose→tight〕殿後注入 `_page_source_md`/`_deliver`；真因＝Vision 每頁吐不同「標題+重點」結構〔頁 A `*` loose / 頁 B `→` 散段落〕節奏不一；RAG 零影響〔merged 取原始 zh_content、未套 tighten〕；零後端/DB/四路；9 新 pytest、全套件 618 passed；⚠️ slides golden 併批次首捕、baron E2E Ch37）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-3b top-level 清單凸排修補（HOTFIX-3 二補完）~~（已落地；`static/index.html` base CSS 單 hunk：HOTFIX-3「二」selector 前置 `#paper-content ul/ol`〔top-level〕、`padding-left:1.5em` 不變；真因＝L79 全域 reset 歸零 top-level ul/ol padding、`list-style:outside` 下第一層 bullet 凸排、HOTFIX-3 二只補巢狀；不動 themes〔四主題 grep 0 命中、結構歸主檔、含自訂主題受益〕；零 .py、全套件 605 passed〔僅 env flake〕；⚠️ baron E2E ALi 第一層不凸排+四主題一致+巢狀未退化）
- ✅ ~~PIPE-SLIDES-HOTFIX-3 簡報閱讀視圖排版打磨（圖序/副標併標題塊/子標題/縮排）~~（已落地；一-a 圖在上 + C 副標併 .slide-head 標題塊〔順帶解 一-b 夾線、用主題 divider 變數〕+ A/B/C 升 h3〔非孤兒 h4〕+ 二 base 巢狀縮排；design/docs 設計對齊、RAG 零改；40 測試、全套件 605 passed；⚠️ slides golden 待 fixture 補齊後首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-2 alt 破圖/母片重複日期/F4 條列鬆散（B+E+F）~~（已落地；B _safe_alt 括號全形根除破圖+圖說洩漏 / E _strip_master_date 母片日期 ≥2 頁洗〔補 dedup 格式變異漏網〕/ F _normalize_paragraph_breaks list-aware〔修 HOTFIX-1 F4 條列鬆散回歸〕；A 撤案、C/D 留 META-NORM；3 測試、全套件 588 passed；⚠️ slides golden 落地後一次首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-1b F2 譯題旁路格式修補~~（已落地；裸 str→三欄 dict 對齊 upsert_paper/web_server 契約、影子寫庫復活；同式消費測試堵盲區；全套件 585 passed）
- ✅ ~~PIPE-SLIDES-HOTFIX-1 B 軌簡報三缺陷緊急修補~~（已落地；F1 去標題回聲〔原文層〕+ F2 接譯題〔複用 P3 譯題穿旁路〕+ F4 段落正規化移植 + F3 並列顯式不修；4 回歸測試、全套件 584 passed；⚠️ slides golden 落地後一次首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES SlidePipeline簡報策略管線~~（已落地、C1 `31dab5a` + C2 `941eed7` + C3 `f8a24d7` + C4 `4d7684c` + C5 `dbf90bd` + C6 `cb5e2bd` + C7 Checkout 收官；原 PIPE-VISUAL 改名；四 Phase 全落地〔P1 存圖+Vision temp=0+封面+去重 / P2 六步 key=`p{N}_{原文頁標題}` / P3 逐頁並行+alt 對齊雙 Caption 根除 / P4 rag_indexer 四產物〕+ §7.2 key-changing 整合測試正面達標；24 測試、全套件 580 passed；⚠️ baron 影子 E2E + B 軌 golden 另捕〔Q8 改善豁免〕）

### PIPE-RESUME (✅ 已完成·PIPE 縱向五路絞殺第 1 路)
- ✅ ~~PIPE-RESUME ResumePipeline策略管線~~（已落地、C1 `f3d4e41` + C2 `d7edcd9` + C3 `48aa5df` + C4 `8971a19` + C5 `e8a7429` + C6 `fabb114` + C7 收官；`pipelines/resume_pipeline.py` 四 Phase 策略〔P1 Vision 全鏈/P2 LCC+摘要+Glossary 自癒/P3 100% Bypass/P4 RAG ≥3〕+ tests/test_resume_pipeline.py 15 測試；消費 PIPE-CORE ABC/三大真理源/PIPE-SCAFFOLD 影子；baron 拍板擴 PipelineContext pdf_path/owner_id；custom_metadata 硬前置 defer 僅影子 B 軌、不 Flip）
- ✅ ~~PIPE-RESUME v9 影子整合與規格同步~~（已落地、C1 `b97958b` + C2 `e64417a` + C3 `f239721` + C4 `9bbad2d` + C5 `9291c5c` + C6 `4e15905` + C7 收官；raw_metadata 旁路穿線 + P1 影子標題後綴 (測試) + P2 摘要先行步序 + P3 翻譯策略隔離 constraints + C5 影子寫庫保真〔對齊 A 軌 upsert_paper〕+ 廢 self._raw_meta；resume 19 測試、全套件 483 passed；A 軌 byte 不動）
- ✅ ~~TILING-HOTFIX-1 — 緊急熱修復：TextTiling Embedding 速率超限 (429) 批次化修復~~（已落地、`702347a`；`tiling_processor.py:425` 逐筆 embed_query→批次 embed_documents〔1/32 請求+線性退避+順序保證〕；根治 429 阻斷+test_tiling_paragraph 併發 flaky；全套件 484 passed；⚠️ task_type RETRIEVAL_QUERY→DOCUMENT 行為變更、Flip/結案前須重捕 Golden Baseline）
- ✅ ~~SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復~~（已落地、`3d2778a`；3 處移除矛盾交回母提示詞：web_server translated_title 補 (測試) + translator.py:40 STYLE_HINTS 移除公司名 + resume_pipeline.py:109 constraints 改產品-only；全套件 486 passed；⚠️ B軌譯文改變、與 TILING-HOTFIX-1 合併重捕 Golden Baseline；學歷 doubling 殘留歸 RESUME-P3）
- ✅ ~~RESUME-P3 B軌履歷翻譯品質重構~~（已落地、C1 `aec1f6f` + C2 `0efa7e8` + C3 `52e0769` + C4 `6658b48` + C5 `3a30394` + C6 收官；廢 100% Bypass→逐 heading section 翻譯+還原〔pipelines 內重建不耦合 A 軌〕+ 履歷 P1 opt-out TextTiling〔滅 429〕+ resume 停用 U4 + heading 退化 fallback；resume 26 測試、全套件 495 passed；⚠️ 改 B軌輸出、與 TILING/SHADOW 合併重捕 Golden；通用化 chunking 歸 INFRA-3）
- ✅ ~~RESUME-P3 HEADING-HOTFIX-1 標題層級遞迴深度~~ `7c8a0da` / ~~PARA-HOTFIX-1 正文段落空行~~ `2772822` / ~~META-HOTFIX-1 P1 meta 進 final header~~ `2ba97fc`（B軌履歷三件套：標題層級/段落/文件 header）
- ✅ ~~VISION-HOTFIX-1 Vision 轉錄 temperature 確定化~~（已落地 `3d5be32`、`chat_with_images` 加 temperature + ResumeProcessor 傳 0；A軌 pdf2md + B軌 P1 共用、須重捕 resume golden）
- ✅ ~~RESUME-PERF-1 run_phase3 逐 section 翻譯並行化~~（已落地、C1 `b110742` + C2 `d5abdf0` + C3/C4 收官；序列→ThreadPool 受限並行〔保序靠 slot index、限流靠既有 `_api_semaphore`、單 unit 失敗退原文〕；C1 解耦先鎖等價、C2 並行、C3 4 並行測試；行為等價、預估 ~5x；baron 拍板不必等五路）

### RAG-ASYNC (✅ 已完成·PIPE Phase 4 共用真理源)
- ✅ ~~RAG-ASYNC-HOTFIX-3 zh 來源履歷 P3 改建 per-section rag_sections（#4·選 B）~~（已落地、`6794331`；run_phase3 is_zh 分支單一容器→有 section 走 ctx.ingestion.tiles 不翻譯、複用 `_collect_render_slots`+`_collect_rag_sections(translate=False)` 建 per-section〔summary_key=原文 zh path、與 P2/#1 天然對齊〕、無 section 退兜底；不改 zh_text=full_text/en 主路/degraded；resume 42 passed、全套件 535 passed；⚠️ zh 來源 golden 須重捕、en 不需）
- ✅ ~~RAG-ASYNC-HOTFIX-1 section_summaries 跨譯 key 對位失效 + dead code~~（已落地、`300feb1`；#1 P2 原文 key vs P3 譯文 title vs P4 譯後 node_key 三方不一致 → Chapter Summary 永不進 chunk、Strategy B 靜默退化成 A；穿原文標題 path key 貫穿 P2/P3/P4 + 移除 dead `_load_index_meta`〔#3〕+ 補 P3→P4 接縫整合測試；全套件 528 passed）
- ✅ ~~RAG-ASYNC-HOTFIX-2 B 軌補產 rag_tree.json（#2·選 B 完整版）~~（已落地、`300feb1`；rag_indexer 新增 `build_rag_tree`+`_walk_tree`〔key_map key=chunk Header=node_key→`/sections/{i}/content/0` + 巢狀 translated_content〕+ `index()` 寫 `final_{paper}_rag_tree.json` + run_phase4 傳路徑/標題；根治 C4 漏產 rag_tree → 章節引用/paper_title/公式相鄰降級；零改 rag_retriever/ai_core；全套件 532 passed；不衝擊 golden）
- ✅ ~~RAG-ASYNC P4 RAG 索引共用真理源與全 P2 摘要~~（已落地、C1 `195e12b` + C2 `8c76274` + C3 `53755c4` + C4 `a09128e` + C5 `d9b03f4` + C6 `13abdfa` + C7 收官；新建 `processor/rag_indexer.py` B 軌自有索引引擎〔全重寫零 import rag_processor、Strategy B header augment + size-cap 二段子切 + 自實作 is_chunk_meaningful、index() 落庫 byte 相容 ④ 合約〕+ GlossaryReadySpec section_summaries 取代 chapter_summaries + run_phase2 統一六步〔批次產+翻 section_summaries、三安全鎖〕+ run_phase3 旁路封存 ctx.rag_sections + run_phase4 改呼 rag_indexer〔砍 rag_processor 耦合〕+ 母 plan v10/PIPE-SPEC 同步〔含修 §1.3 P3 doc-drift〕；全套件 525 passed；**chunks=1 退化修復、B 軌全鏈零 A 軌依賴**；⚠️ baron 須影子 E2E 驗 chunks 量級 + resume 重捕 Golden；其餘四路 production 隨各自 PIPE-N 跟上）

