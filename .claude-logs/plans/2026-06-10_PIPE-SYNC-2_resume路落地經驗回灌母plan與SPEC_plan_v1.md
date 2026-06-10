# PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 PIPE-SPEC · plan v1

> 工作流類別：**DOC-Refactor**（改兩份 baton/ 規格文件 + **sop/ 四檔**、零業務代碼）
> 目的：第 1 路（Resume）落地後累積之 hotfix／重構經驗，回灌 `PIPE plan v10` 與 `PIPE-SPEC` + 連帶修正 sop/ 因架構推進而 stale 的配置權威，使**第 2-5 路引用的真理源乾淨無矛盾**——在開 PIPE-VISUAL plan 之前完成。
> 範式：沿用 RAG-ASYNC C1 / PIPE-RESUME v9 C1 之「就地補註 + HTML 註解包裹標記」同步先例。

---

## §0 改版規則
- 改版觸發：§2 / §9 任一變動 → 直接改章節 + §99.2 加 Revision
- 多輪 review 累積（§1.9）：v1 初稿 → 待 baron 過目 §9 OQ → v2

---

## §1 TL;DR（概要）

Resume 路（第 1 路）自 2026-06-08 上次規格同步（SPEC v5 / 母 plan 補註⁵）後，又落地 **RAG-ASYNC-HOTFIX-1/2/3、VISION-HOTFIX-1、MODEL-11、RESUME-PERF-1** 等工作；逐項比對發現兩份真理源存在 **1 處雙文件矛盾 + 4 處規格缺口 + 3 處樣例/措辭 stale**。其中 **#U1（母 plan resume P3 仍寫 100% Bypass、與 SPEC 已修版直接矛盾）**、**#U3（section_summaries key 契約未凍結——正是 HOTFIX-1 出包的模糊措辭本尊）**、**#U4（zh 來源路徑零規格——HOTFIX-3 真因）**、**#U5（Vision temperature 未入規格——第 2 路 Slides 同為 Vision 解析、直接要照抄）** 不修，第 2-5 路照 spec 實作會重蹈同樣的坑。

**已同步、本任務不重複**（grep 證）：SPEC §1.3 resume「逐 section」（v5）/ raw_metadata 旁路 + (測試) 影子後綴 + C7-C8 hotfix 史（v9 C1）/ section_summaries 六步 + P4 自有索引引擎 + size-cap（SPEC v5 + 母 plan 補註⁵）。

**sop/ 連帶修正（baron 拍板全納入）**：架構推進使 4 檔 stale——`model_recommendations.md` 仍推薦已被 MODEL-11 廢棄的 `gemini-embedding-2`（🔴 主動誤導）、`google_latest_models_guide.md` 多處讚譽與實測矛盾、`doc_type 新增手冊` 整本教 A 軌路（+v1/v2 舊版並存待歸檔）、`mineru_SOP` 缺 `RELEASE_ON_UPLOAD` 配套事實 → U11-U14。templates/ 全查無需更新（流程結構文件、不含架構事實）。

**判定不入本任務**：RAG-MULTI-1 / LAZYLOAD-MULTI-1 程式面（檢索/服務層、非 P1-P4 製程合約；僅 U14 之 RELEASE_ON_UPLOAD 運維事實入 mineru SOP）；CHAT-EXPORT-HOTFIX-1 / WORKFLOW-3（前端 / 流程治理）；repo `docs/HOW_TO_ADD_DOC_TYPE.md`（業務 repo docs 樹、範疇外、baron 另定）。

---

## §2 目標規格

> 改動對象僅兩檔：`baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（下稱**母 plan**）、`baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（下稱 **SPEC**）。

### 🔴 高優先（規格矛盾 / 缺接縫契約、直接影響第 2-5 路）

| # | 規格 | 改哪份 | 來源 |
|---|---|---|---|
| U1 | **修母 plan resume「P3 100% Bypass」雙處殘留**（L71 五路列表 + L257 §8.5 PIPE-RESUME 條目）→「逐 heading section 翻譯 + 退化 fallback」，消除與 SPEC §1.3（v5 已修）的直接矛盾 | 母 plan | RESUME-P3 |
| U2 | **§8.5 RAG-ASYNC 條目狀態自癒**：「⬜ 待建立」→「✅ 已落地」（C1-C7 + HOTFIX-1/2/3），產出欄補實際交付（`processor/rag_indexer.py` / P2 六步 `section_summaries` / `ctx.rag_sections` 旁路 / `final_{paper}_rag_tree.json`）；PIPE-RESUME 條目狀態欄同步註「四 Phase 已落地（C1-C7 + v9 + hotfix 群）、Golden Diff 待 baron 重捕」 | 母 plan | RAG-ASYNC 收官 |
| U3 | **凍結 `section_summaries` key 接縫契約**：SPEC §1.1② 與 §1.4.1（及母 plan §U4 對應句）現僅寫「`Dict[node_key,str]` 對位巢狀樹」——HOTFIX-1 出包的模糊措辭本尊。補凍結三句：**key＝原文標題 path**；**P2 產（`_collect_summary_targets`）/ P3 帶（slot `key`→`summary_key`）/ P4 取（`_walk` 首選 `summary_key`）三方同基準**；**譯後 title 僅供顯示、不作 key**（對齊 WORKFLOW_SOP §7.1 worked example） | SPEC + 母 plan | RAG-ASYNC-HOTFIX-1 |
| U4 | **補 zh 來源（source_lang=zh）路徑規格**：兩文件現只設計 en→zh 主路（HOTFIX-3 真因）。SPEC P3 章補「zh 來源：跳過翻譯（原文≡譯文）、**仍建 per-section `rag_sections`**（summary_key=原文 path、與 P2/P4 key 天然對齊）、無 section 退單一容器兜底」——標註為**五路通用 edge path**（任何路都可能收到 zh 原生文件） | SPEC（母 plan 一句引用） | RAG-ASYNC-HOTFIX-3 |
| U5 | **Vision 解析升格共用規格（SPEC 新增 §1.3.1「Vision 解析共用規格」小節、resume／slides 共用、PIPE-VISUAL 直接引用）**——凍結 resume 落地驗證過的三原則：① **忠實轉錄鐵律**（嚴禁重組/摘要/補完，7e 系列 revert 教訓＋主標題抽取優先序/投遞元資訊排除類噪聲排除原則）；② **確定性參數** `LLM_VISION_TEMPERATURE=0`（忠實轉錄走 greedy、壓抖動、golden 可固定靶）；③ **非確定性殘餘誠實註記**（temp=0 不保證 byte 級重現〔Google 後端 batching/MoE〕→ golden 重捕須清中間快取、比對留容差）。母 plan 不展開、§8.5 PIPE-VISUAL 條目尾加一句指標引 §1.3.1。⚠️ 僅凍結**已落地事實**——Vision 輸出格式為 markdown 轉錄（非 JSON Schema），輸出 Schema 級約束屬 PIPE-VISUAL plan 自定、不在此越權 | SPEC（母 plan 一句指標） | VISION-HOTFIX-1 + 7e v2 |

### 🟡 中優先（凍結合約樣例 / 輸出完整性）

| # | 規格 | 改哪份 | 來源 |
|---|---|---|---|
| U6 | **④ 合約樣例 `embedding_model` stale**：SPEC L146 `"gemini-embedding-2"` → `"gemini-embedding-001"`（真批次 + task_type 非對稱；註 MODEL-11、向量不可混庫） | SPEC | MODEL-11 |
| U7 | **rag_tree.json 產出歸屬明確化**：④ physical_outputs 已列 `tree_json_file`，但 §1.4.1 索引引擎敘述未寫產出者——補「由 B 軌 `rag_indexer.build_rag_tree` 自建（key_map key＝chunk Header＝node_key → `/sections/{i}/content/0` path；節點帶 translated_content/translated_title）」。HOTFIX-2 真因＝輸出清單漏列，不補第 2-5 路照 spec 實作可能再漏 | SPEC | RAG-ASYNC-HOTFIX-2 |
| U8 | **P1 Tiles「交付形狀均勻、產生方式各路自選」措辭精確化**：母 plan U3「五路絕對均勻」與 resume 實作（opt-out TextTiling、以 processed JSON 直當 tiles、P1 零 embedding）有落差——母 plan U3 補一句、SPEC §1.3 resume 行補註；呼應 INFRA-3（通用化 opt-in 機制）排程 | 母 plan + SPEC | RESUME-P3 C1 |

### 🟢 低優先（實作註記、一句帶過；是否納入見 §9 Q2）

| # | 規格 | 來源 |
|---|---|---|
| U9 | P3 編排可**受限並行**（ThreadPool、保序 slot index、限流靠共用 `LLMClient._api_semaphore`、單 unit 失敗退原文）——SPEC §1.2.3.1「翻譯策略＝run_phase3 編排」段補一句，供 Academic/LiteDoc 逐 section 時參照 | RESUME-PERF-1 |
| U10 | resume P3 還原細則三件套：meta header 渲染（P1 meta 入 final 開頭、無序列表）/ 標題層級＝遞迴深度（`min(2+depth,6)`）/ 段落 `\n\n` 正規化（pipe-table-safe）——SPEC §1.3 resume 行尾註 | META/HEADING/PARA-HOTFIX |

### 📚 sop/ 連帶修正（baron 拍板全納入；templates/ 查無需更新）

| # | 規格 | 改哪份 | 來源 |
|---|---|---|---|
| **U11** 🔴 | **`model_recommendations.md` EMBEDDING_MODEL 行更正**（L20）：`gemini-embedding-2` → **`gemini-embedding-001`** + 理由（embedding-2 為多模態交錯模型、SDK `t_contents` 把批次併 1 向量＝假批次、不支援 task_type → 召回非對稱性喪失；MODEL-11 Dev API 探針鋼證）；順帶 L19 `LLM_EXTRA_INFO_MODEL` 行加註「`extra_info` stage B 軌已廢（母 plan U6）、僅 A 軌影子期沿用」。此檔為被引用配置權威（TRANSLATOR plan 引 §1.1）、現為主動誤導 | sop/model_recommendations.md | MODEL-11 |
| **U12** 🟡 | **`google_latest_models_guide.md` 勘誤 banner**：頂部加勘誤框——embedding-2 之「真批次/text embedding 首選」描述與 MODEL-11 實測矛盾（`embeddings=1` 融合 vs `-001 embeddings=3`）；本專案文字 embedding 一律 `gemini-embedding-001`、多模態場景另議；指向 MODEL-11 決策。**不重寫內文**（Google 模型總覽參考性質） | sop/google_latest_models_guide.md | MODEL-11 |
| **U13** 🟡 | **`doc_type 新增手冊 v3` 適用範圍 banner**：頂部加——本手冊為 **A 軌（11-stage `pipeline_core`）專用**、Flip 前仍有效；**B 軌新增 doc_type ＝ `PipelineFactory.register` + `DocumentStrategy` 四方法**（見 PIPE-SPEC §1.3）；全面改寫屬 Flip 後（INFRA-4 時代）。**不重寫內文**。＋**文件治理**：`v1`/`v2` 兩舊版 `mv archive/`（WORKFLOW_SOP §2 過期歸屬、僅留 v3） | sop/doc_type 手冊 v3 + archive/ | PIPE B 軌落地 |
| **U14** 🟢 | **`mineru_SOP_手冊` §6 資源段補一句**：LAZYLOAD-MULTI-1 C4 起、上傳文件時 app 端自動全清向量快取 + `gc.collect()` 騰 RAM 給同 VM MinerU Docker（`RELEASE_ON_UPLOAD`=on、env 可關、活躍 SSE 串流豁免）——app 端配套事實入運維手冊；**母 plan 不重複寫**（取代原 §9 Q5 之「母 plan 帶一句」方案） | sop/mineru_SOP_手冊.md | LAZYLOAD-MULTI-1 C4 |

---

## §3 現況與證據

### §3.1 grep 鋼鐵證據（2026-06-10 實測、行號以當日檔案為準）

**U1 母 plan 矛盾雙處**：
```
母plan L71:  「P3 100% Bypass；P4 ≥3（技能詞保護）」          ← resume 五路列表
母plan L257: 「P3 100% Bypass／P4 ≥3 技能詞保護」              ← §8.5 PIPE-RESUME 條目
SPEC  L133: 「逐 heading section 翻譯 + 退化 fallback」        ← v5 已修（RAG-ASYNC C1 HTML 註解包裹）
→ 兩文件互相矛盾；SPEC §99.2 v5 明載「修 RESUME-P3 doc-drift」但只修了 SPEC、母 plan 漏
```

**U2 §8.5 RAG-ASYNC stale**：
```
母plan L267: | **RAG-ASYNC** | plan | …… | ⬜ 待建立 | — | ……
→ 實際：RAG-ASYNC C1-C7 全落地（TODO ✅ 完成表）+ HOTFIX-1/2/3
```

**U3 key 契約缺口**：
```
grep -c '原文標題 path|summary_key' 母plan SPEC → 0 / 0      ← 兩文件全程零提及
SPEC L65/§1.4.1：「Dict[node_key, str] 對位巢狀樹」           ← HOTFIX-1 鐵證：此措辭不凍結
  「key＝何物 + producer/consumer 同基準」→ P2 原文 key / P3 譯文 title / P4 譯後 node_key
  三方不一致 → Chapter Summary 永不進 chunk、Strategy B 靜默退化（C5 白做）
```

**U4 zh 路徑零規格**：
```
grep 'is_zh|zh 來源|source_lang' 母plan SPEC → 0 命中
→ HOTFIX-3 真因即「plan 只設計 en→zh 主路、未規範 is_zh 路結構化」
```

**U5 Vision temperature 零規格**：
```
grep 'temperature|VISION' 母plan SPEC → 0 命中（業務語意）
→ llm/client.py chat_with_images 未設 temp 時吃 Gemini 預設 ~1.0 → 同 PDF 每次輸出抖動（13126/13233/13281）
→ slides 路同為 Vision 解析、不入規格必重蹈
```

**U6 樣例 stale**：
```
SPEC L146: "embedding_model": "gemini-embedding-2"
→ MODEL-11 已換 gemini-embedding-001（settings.py 預設 + 全 28 篇 index_meta 實測皆 -001）
```

**U7 rag_tree 歸屬**：
```
SPEC L153: "tree_json_file": "rag_tree.json"   ← ④ 合約列了
SPEC §1.4.1：全段無「誰產 rag_tree」            ← HOTFIX-2 真因（RAG-ASYNC plan §U5④ 輸出漏列）
```

**U8 Tiles 措辭**：
```
母plan L40: 「P1 對五種 doc_type 交付絕對均勻的產物：…+ 物理分組 Tiles」
→ resume 實作：_build_tiles opt-out TextTiling（RESUME-P3 C1、源頭滅 429、P1 零 embedding）
```

**U11-U14 sop/ 證據（2026-06-10 grep）**：
```
U11: model_recommendations.md L20: 「EMBEDDING_MODEL | gemini-embedding-2 | gemini-embedding-2 | 2026 最新旗艦多模態嵌入…」
     ← settings.py 預設 + 全 28 篇 index_meta 實測皆已 gemini-embedding-001（MODEL-11）
U12: google_latest_models_guide.md L27/32/114/170 多處推崇 embedding-2（含「圖片+context 送 embedding」構想段）
U13: doc_type 手冊 v3 L286 仍教「修改 pipeline_core._stage_detect_domain」（A 軌 11-stage 路）；
     sop/ 同時存 v1(28.6K)/v2(35.6K)/v3(18.7K) 三版並存
U14: mineru_SOP §6.1 僅有「重啟容器釋放記憶體」、無 app 端 RELEASE_ON_UPLOAD 配套事實
templates/ 全查：流程結構文件、零架構事實耦合 → 無需更新
database/logging SOP：契約未變（session.begin / exc_info）、近五任務全合規 → 無需更新
CACHE_OPTIMIZATION_SOP：markdown prompt-cache 評分規範、與架構無關 → 無需更新
```

### §3.2 已同步項（本任務不重複勞動）
- SPEC v5（2026-06-08）：§1.1② section_summaries 取代 chapter_summary / §1.4.1 chunk 來源與 size-cap / §1.3 resume 逐 section。
- 母 plan 補註⁵（2026-06-08）：§U4 六步 / §U6 措辭精確化。
- v9 C1（2026-06-07）：raw_metadata 旁路登記 / P3 翻譯策略隔離原則（§1.2.3.1）/ P1 影子後綴 / C7-C8 hotfix 史。

### §3.3 範式先例
RAG-ASYNC C1 與 PIPE-RESUME v9 C1 均為「兩檔就地補註 + `<!-- === [任務 C1 START/END] === -->` HTML 註解包裹 + §99.2 Revision + 不 bump 主版本」——本任務沿用同範式（`<!-- === [PIPE-SYNC-2 ...] === -->`）。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

**無**——本任務為純文件規格同步（DOC-Refactor）、無程式碼 handoff。

惟本任務之 **U3 本身即是把一條跨 Phase 接縫契約（section_summaries key）寫進 SPEC**：該契約的 producer/consumer/key 同基準定義以 **WORKFLOW_SOP §7.1 worked example（修正版 RAG-ASYNC #1）為唯一權威源**，SPEC 寫入時逐字對齊、不另創措辭（防二次 drift）。

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| 改壞凍結合約語意（SPEC 為全下游 plan 引用真理源） | 本任務全部為「補註/更正 stale」、不改四合約欄位結構；U6 僅樣例字面值 | HTML 註解包裹標記每處變動、可逐處 revert；§8 驗證清單逐 U 對照 |
| 與既有 v5/補註⁵ 同步內容重複/打架 | §3.2 已盤點既同步項、本任務不觸碰 | §8 grep 驗證無重複段落 |
| 母 plan/SPEC 主版本是否 bump | 沿 RAG-ASYNC C1 先例：就地補註不 bump 主版本（v10/檔名不變）、§99.2 加 Revision | §9 Q1 baron 確認 |
| U5/U4 寫入位置選擇不當致後續難引用 | U5 放 SPEC Vision 解析段（slides 直接引用）；U4 放 P3 章（五路通用 edge path） | §9 Q3 可調 |
| 兩檔在 baton/（不入版控）、改動暫無 git 防護 | DOC-Refactor 改前 .bak 鐵律照常（archive/）；ship 時隨 commit 入庫 | tasks 階段明列 .bak |
| **sop/ 四檔屬已入版控文件**（與 baton 兩檔不同） | U11-U14 改動 ship 即生效於全環境引用 | banner/勘誤式補註不刪舊文；各檔 §99.2 加 Revision；.bak |
| U13 歸檔 v1/v2 致歷史引用斷鏈 | grep 證僅 framework 提及「doc_type_新增手冊」字樣（非鎖版本路徑） | mv archive/ 保留實體、可循 WORKFLOW_SOP §2 找回 |

---

## §6 不可動清單

- [ ] **任何業務代碼（.py / static/）**——本任務零代碼。
- [ ] SPEC 四份凍結合約的**欄位結構**（①②③④ Schema 欄名/型別）——只補註與樣例字面、不增刪欄位。
- [ ] 既已同步段落（§3.2 清單：v5 / 補註⁵ / v9 C1 之 HTML 註解區）——不重寫、不重複。
- [ ] 母 plan §8.5 其餘條目（PIPE-VISUAL/ACADEMIC/LITEDOC/TRANSLATE-BOOK/MD-RESTORE/RESOLVED-SUMMARY/PIPE-FLIP）的規格句——僅動 PIPE-RESUME/RAG-ASYNC 兩條目狀態與 resume 規格句。
- [ ] WORKFLOW_SOP / framework / **templates/ 全部**——非本任務對象（templates 已查無架構耦合）。
- [ ] baton/ 其他檔案（TRANSLATE-BOOK v7 / INFRA-3 / INFRA-4 / CHAT-STRUCT-1 / QUEUE-1 / 工作筆記）。
- [ ] sop/ 之 `database_SOP` / `logging_SOP` / `CACHE_OPTIMIZATION_SOP`——已查無需更新、不碰。
- [ ] U12/U13 之**內文**——僅加 banner/勘誤框、嚴禁重寫手冊與指南本文。
- [ ] repo `docs/HOW_TO_ADD_DOC_TYPE.md`（業務 repo docs 樹、範疇外）。

---

## §7 規格依據（grep 行號 + 來源任務）

- 母 plan：L40（U3 Tiles）/ L48+L62（section_summaries 句）/ L71+L257（resume Bypass 殘留）/ L267（RAG-ASYNC ⬜）/ §99.2 補註⁵
- SPEC：L65（§1.1②）/ L122（§1.2.3.1）/ L132-133（§1.3 表）/ L143-156（④ 合約樣例、L146 embedding_model / L153 tree_json_file）/ §1.4.1 / §99.2 v5
- 來源任務（皆已收官、TODO ✅ 表可溯）：RESUME-P3（C1 opt-out / C3 逐 section）、RAG-ASYNC C1-C7、RAG-ASYNC-HOTFIX-1（`300feb1`）/ -2（`300feb1`）/ -3（`6794331`）、VISION-HOTFIX-1（`3d5be32`）、MODEL-11（C1 `1f56547`）、RESUME-PERF-1（C1 `b110742`/C2 `d5abdf0`）、META `2ba97fc`/HEADING `7c8a0da`/PARA `2772822`
- 接縫契約措辭權威源：`ref/WORKFLOW_SOP.md §7.1`（worked example 修正版 RAG-ASYNC #1）

---

## §8 驗證計畫

### §8.1 文件驗證清單（DOC-Refactor、依 WORKFLOW_SOP §1.3）
逐 U 一條 grep（執行報告貼真實輸出）：
1. U1：`grep -n '100% Bypass' 母plan` → resume 兩處已改（slides 路 L70/L258 之 Bypass **保留不動**——那是 Slides 自己的規格、PIPE-VISUAL plan 再議）。
2. U2：`grep -n 'RAG-ASYNC.*待建立' 母plan` → 無命中；`grep -n 'rag_indexer' 母plan` → §8.5 產出欄有命中。
3. U3：`grep -c '原文標題 path' SPEC 母plan` → 兩檔 ≥1；與 WORKFLOW_SOP §7.1 worked example 三欄逐字對照。
4. U4：`grep -n 'zh 來源\|source_lang' SPEC` → 有命中（P3 章）。
5. U5：`grep -n 'LLM_VISION_TEMPERATURE\|Vision.*確定性' SPEC` → 有命中、明標 resume/slides 共用。
6. U6：`grep -n 'gemini-embedding-001' SPEC` → 有；`grep -n 'gemini-embedding-2' SPEC` → 0。
7. U7：`grep -n 'build_rag_tree\|key_map' SPEC` → §1.4.1 有命中。
8. U8：`grep -n '產生方式\|opt-out' 母plan SPEC` → 各有命中。
9. 通用：HTML 註解 `<!-- === [PIPE-SYNC-2` START/END 成對平衡；兩檔 §99.2 各 +1 Revision；`wc -l` 增量合理（純加註、無大段刪除）。
10. 既同步區不重複：`grep -c 'RAG-ASYNC C1 START' SPEC` 數量不變（不動既有包裹區）。
11. U11：`grep -n 'gemini-embedding-001' sop/model_recommendations.md` → 有；`grep -c 'gemini-embedding-2' 同檔` → 僅存歷史對照欄、建議值欄 0。
12. U12：`grep -n '勘誤\|MODEL-11' sop/google_latest_models_guide.md` → 頂部 banner 有命中；內文 `wc -l` 不減（不重寫）。
13. U13：`grep -n 'A 軌\|PipelineFactory' sop/2026-05-21_doc_type_新增手冊_三軸融合_v3.md` → banner 有命中；`ls sop/ | grep doc_type` → 僅 v3；`ls archive/ | grep doc_type` → v1+v2 共 2。
14. U14：`grep -n 'RELEASE_ON_UPLOAD' sop/2026-05-27_mineru_SOP_手冊.md` → 有命中（§6 段）。

### §8.2 手動驗證（baron）
- 過目兩檔 diff（HTML 註解包裹處）；確認 U3 三句與 WORKFLOW_SOP §7.1 同基準措辭一致；確認 U5 對 PIPE-VISUAL 可直接引用。

### §8.3 §7.2 整合測試豁免聲明
本任務為 DOC-Refactor、無 code handoff → 依 WORKFLOW_SOP §7.2 **顯式申請豁免**跨 Phase 整合測試（同 WORKFLOW-3 先例：立規者自身不適用該規），由 baron 於 §9 Q4 拍板。

---

## §9 Open Questions（待 baron 拍板）

> **全數定案（2026-06-10 baron review 拍板、six/six 結清）**

| # | 問題 | 定案 |
|---|---|---|
| ~~Q1~~ | 版本策略 | **✅ 不 bump**——就地補註 + HTML 註解包裹 + §99.2 Revision（防下游檔名指標斷鏈〔TRANSLATE-BOOK 等引 `_v10.md`〕；14 項皆「同步事實/補缺口」非架構變革、v10 語意正確） |
| ~~Q2~~ | 低優先 U9/U10 納入 | **✅ 納入**（baron「全部都加入」） |
| ~~Q3~~ | U5 Vision 寫入位置 | **✅ SPEC §1.3 表附近新增「§1.3.1 Vision 解析共用規格」小節**＋採 review 補充：除 temp=0 外、一併原則性凍結忠實轉錄鐵律與非確定性殘餘註記（**僅凍已落地事實**、輸出 Schema 級約束留 PIPE-VISUAL——見 U5 校準）；母 plan 僅 §8.5 PIPE-VISUAL 條目尾一句指標、防母 plan 膨脹 |
| ~~Q4~~ | §7.2 整合測試豁免 | **✅ 豁免**（DOC-Refactor、zero-code handoff、無可測代碼實體；對齊 WORKFLOW-3 先例；§8.1 十四條 grep/ls 物理自檢已足、Checkout 報告顯式聲明＋貼真實輸出） |
| ~~Q5~~ | RELEASE_ON_UPLOAD 寫哪 | **✅ 寫 mineru SOP（U14）、母 plan 不重複** |
| ~~Q6~~ | slides 路 Bypass 是否動 | **✅ 不動、原樣保留**——是否吸收 Resume 教訓屬**業務/產品決策**，須待 PIPE-VISUAL POC + Golden Baseline 後在其 plan 內評估；本任務只修「已落地事實 vs 文件」drift、不憑空預判未落地管線 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | Resume 路落地經驗回灌兩份 PIPE 真理源、消除 drift、為 PIPE-VISUAL 鋪乾淨引用基礎 |
| 權威源 | 本檔 §2（U1-U10）；接縫措辭權威源＝WORKFLOW_SOP §7.1 |
| 引用方 | tasks / executions（待產）；PIPE-VISUAL plan（將引用同步後之 SPEC） |
| 不可動唯一源 | §6 |
| 改版觸發 | §2 / §9 變動 |

### §99.2 Revision 歷程
- v1.2 (2026-06-10)：baron review 拍板——**Q1/Q3/Q4/Q6 全數定案**（不 bump / SPEC §1.3.1 小節 / 豁免 / slides Bypass 不動），§9 六題全結清；採 Q3 review 補充擴 U5 為「Vision 解析共用規格三原則」（忠實轉錄鐵律＋temp=0＋非確定性殘餘註記），並校準 review 之「輸出 JSON Schema 約束」建議——resume 落地為 markdown 轉錄、Schema 級約束**不在此越權凍結**、留 PIPE-VISUAL plan 自定（僅凍已落地事實原則）；**plan 全 OQ 結清、可進 tasks**
- v1.1 (2026-06-10)：baron 拍板「全部都加入」——擴 §2 新增 **sop/ 連帶修正 U11-U14**（U11 🔴 model_recommendations EMBEDDING_MODEL 行更正 -001 + extra_info 註 / U12 google_latest_models_guide 勘誤 banner / U13 doc_type 手冊 v3 適用範圍 banner + v1/v2 mv archive/ / U14 mineru_SOP §6 補 RELEASE_ON_UPLOAD 配套句）；templates/ 與 database/logging/CACHE SOP 查無需更新（§3.1 證據 + §6 不可動明列）；§5 補 sop 入版控/歸檔斷鏈風險；§8 補驗證 11-14；**Q2 定案納入 U9/U10、Q5 定案改 U14**（餘 Q1/Q3/Q4/Q6 待拍板）
- v1 (2026-06-10)：初稿——盤點 2026-06-08 上次同步（SPEC v5 / 補註⁵ / v9 C1）後 resume 路全部落地工作 vs 兩真理源，得 5 高（U1 矛盾 / U2 stale / U3 key 契約 / U4 zh 路 / U5 Vision temp）+ 3 中（U6 樣例 / U7 rag_tree 歸屬 / U8 Tiles 措辭）+ 2 低（U9 並行 / U10 還原三件套）；判定 RAG-MULTI-1 / LAZYLOAD-MULTI-1 / CHAT-EXPORT / WORKFLOW-3 不入（非製程合約範疇、僅 Q5 半句例外）；§8.3 申請 §7.2 豁免；六 OQ 待 baron
