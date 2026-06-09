# RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正 plan v1

> 修正跨文件 #hashtag 多篇 RAG（`rag_retriever.retrieve_multi_with_context`）之「全域 top-k 飢餓」——比較類查詢漏掉有資料的文件；併修 LLM 多吐無依據 `[N]` 引用標記。純規格、不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：跨文件 `#cv 比較這幾個人` 查詢，`retrieve_multi_with_context` 用**全域 top-k=7** 把所有 paper 的 chunk 混排取前 7 → **6 篇履歷被擠成 2 人代表**（log 鐵證 `chosen` 7 個：李宗原 5〔A軌+B軌(測試)重複〕+ 黃忠偉 2、**吳焴倫/林晉羽/Priyal 各 0**）→ 吳焴倫的「碩士」chunk 是 21 個候選之一卻排不進前 7 → AI 從未看到 → 誤答「只有李宗原有碩士」。另 LLM 輸出 `[1][2][5]` 學術式引用標記、但 context 無編號、UI 無腳註 → 指向虛空。
- **解法**：① **修法 A·每篇保底覆蓋**——`retrieve_multi` 改「per-paper 保底取 N chunk + 全域補位 + 防 prompt 爆炸 cap」、保證每篇有候選的 paper 都被代表；② **問題 2·禁 bare [N]**——提示詞明令只用《文件名》「章節」標來源、禁輸出 `[數字]` 引用。`retrieve_multi` **無 doc_type 參數 → 五路天生通用**、單篇路徑不動。
- **影響**：`rag_retriever.py::retrieve_multi_with_context`（演算法）+ `prompt/ai/ai_character_prompt.txt`（引用指示）+ 可能 `settings.py`（新增 cap 常數）；**不動單篇 `retrieve_with_context`、不動 shadow 過濾（刻意保留、維 B軌可見性）、不動 embedding/索引層**。
- **不可動清單**：見 §6。

---

## §2 目標規格

> 「最終狀態」目標、可量化檢驗；不含 commit 拆分（屬 tasks 階段）。

- **U1 每篇保底覆蓋**：跨文件檢索時，**每個有 ≥1 個通過門檻候選的 paper，至少貢獻 floor_k 個 chunk 進 context**（floor_k 由 §9 Q1 定）。0 候選（全 < `RAG_SCORE_THRESHOLD`）之 paper 可不貢獻。
- **U2 防 prompt 爆炸 cap**：context 總 chunk 數有上限 cap（由 §9 Q2 定）；篇數多到 `floor_k × N > cap` 時，**每篇仍盡量保底（必要時降 floor_k 至 1）**、全域補位填滿 cap，不無限膨脹。
- **U3 全域品質保留**：保底覆蓋後，**剩餘名額仍按全域分數降序補位**（高分 chunk 不因保底而被犧牲）；維持 L2-normalize cosine 排序語意不變。
- **U4 五路通用**：改動限於 doc-type-agnostic 的 `retrieve_multi_with_context`（無 `doc_type` 參數、唯一呼叫點 `AI_professor_chat.py:127`）→ **resume/visual/academic/litedoc/book 五路一體適用、無 per-route 特例**；跨 doc-type 混合查詢（如 resume + book）下，**保底覆蓋使小文件〔履歷 5 chunk〕不被大文件〔書 845 chunk〕全域壓制**。
- **U5 禁 bare [N] 引用**：`ai_character_prompt.txt` 引用段明令「**只用《文件名》「章節」標來源、禁止輸出 `[1]`/`[2]` 等純數字引用標記**」（context 無編號、此類標記指向虛空）；保留可見來源《title》「section」。
- **U6 單篇路徑零退化**：`retrieve_with_context`（單篇、top_k=5）行為 byte 不變；既有單篇 RAG 測試全綠。
- **U7 不過濾 shadow（刻意）**：`_shadow`（測試）paper **維持在檢索集內、不排除**——baron 拍板：過濾掉會使 B軌改壞無人察覺、shadow 須維持可見性。（其衍生「同人 A+B軌 重複代表」之處置見 §9 Q4。）

---

## §3 現況與證據

- **`rag_retriever.py`**：
  - `retrieve_multi_with_context`（`L214`）：`L286-287` `all_candidates.sort(...); top_chunks = all_candidates[:top_k]`——**純全域 top-k、無 per-paper 保底**；`top_k=RAG_MULTI_TOP_K`（`settings.py:59` 預設 **7**）。
  - `L296-300` context 格式：`## 摘自文件《{title}》\n{chunk}`——**無 [N] 編號**。
  - `L289-293` 已有 `chosen=[(score,pid)...]` log（本次診斷即靠它）。
  - 單篇 `retrieve_with_context`（`L122`、top_k=5）與 multi **完全分離**；`retrieve_multi` **唯一呼叫點** `AI_professor_chat.py:127`。
- **`prompt/ai/ai_character_prompt.txt`**：`L17-23`「引用源頭…明確標註來源章節…逐一標出」——**叫標來源章節、但未禁 [N] 數字** → LLM 自行多吐 `[1][2][5]`。
- **log 鐵證**（2026-06-09 04:04）：
  ```
  [retrieve_multi] papers=6 candidates=21 top_k=7
  chosen=[(0.695,'..._shadow'),(0.669,'李宗原'),(0.653,'李宗原'),(0.647,'..._shadow'),
          (0.645,'黃忠偉'),(0.616,'黃忠偉'),(0.614,'李宗原')]
  → 7 格：李宗原 5（含 shadow 2）/ 黃忠偉 2 / 吳焴倫·林晉羽·Priyal 各 0
  ```

### §3.1 grep 鋼鐵證據
```bash
grep -n 'top_chunks = all_candidates\[:top_k\]\|RAG_MULTI_TOP_K\|摘自文件《' rag_retriever.py
grep -n 'RAG_MULTI_TOP_K' settings.py                                   # 預設 7
grep -n '引用源頭\|標註來源章節\|逐一標出' prompt/ai/ai_character_prompt.txt
grep -rn 'retrieve_multi_with_context' AI_professor_chat.py             # 唯一呼叫點:127
grep -n 'def retrieve_with_context\|def retrieve_multi_with_context' rag_retriever.py  # 單篇/多篇分離
```

---

## §4 跨 Phase 接縫契約

**無。** 本任務為**單模組改動**（`rag_retriever.retrieve_multi_with_context` + 一支提示詞），不跨 ≥2 Phase、無 producer→consumer 資料 handoff（檢索層只**讀取**既有 vector store、不新增跨 Phase 傳遞物）。依 `WORKFLOW_SOP §7` 觸發判準 → 不適用接縫契約、亦不觸發 §7.2 收官前跨 Phase 整合測試（驗證見 §8、以多 paper 檢索測試覆蓋）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **prompt 爆炸**（per-paper floor × N papers 太大、context 過長） | 🟡 中 | U2 cap 上限 + floor 自適應降級（§9 Q2）；保留全域補位不超 cap |
| **單篇路徑誤傷** | 🟢 低 | 改動限 `retrieve_multi`、與 `retrieve_with_context` 物理分離（§3 證）；U6 + 既有單篇測試把關 |
| **跨來源向量庫相容**（A軌 rag_processor / B軌 rag_indexer / 混 embedding 模型） | 🟡 中 | 本次**不解模型一致性**（屬運維 `regen_rag --all`、已修）；保底覆蓋假設各 paper 向量同模型可比——**前提是 regen 一致**；§9 Q1 不改變此前提 |
| **五路 chunk 量懸殊**（book 845 vs resume 5） | 🟢 低（反而有利） | per-paper 保底**正是**讓小文件不被大文件全域壓制的解；book 不會吃掉全部名額 |
| **不過濾 shadow → 同人 A+B軌 雙倍代表** | 🟡 中 | baron 刻意保留 shadow 可見性（U7）；衍生「同一人出現兩次」之內容去重與否列 §9 Q4 由 baron 拍板（非本 plan 預設） |
| **citation 改提示詞影響其他路徑** | 🟢 低 | `ai_character_prompt` 為共用人設、單篇/多篇皆吃；「禁 [N]、留《title》「章節」」對所有路徑都正向、不退化 |

---

## §6 不可動清單

- [ ] `rag_retriever.py::retrieve_with_context`（**單篇路徑**、top_k=5）— 行為 byte 不變。
- [ ] `_get_vector_store` / FAISS 載入 / `RAG_SCORE_THRESHOLD` 門檻語意 — 不改（僅改 top_chunks 選取分配）。
- [ ] **shadow 過濾**——刻意**不做**（U7、維 B軌可見性）；`list_paper_uuids_by_tag` 不加 `_shadow` 排除。
- [ ] `rag_indexer.py` / `rag_processor.py` / embedding 模型 / 向量庫格式 — 零改動（檢索層問題、非索引層）。
- [ ] 母 plan v10 凍結之 P1-P4 合約與五路策略 — 不碰（本任務在下游檢索層）。
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 全域 top-k 飢餓現場（log chosen 5/7 李宗原） | `logs/pipeline.log`（2026-06-09 04:04 `[retrieve_multi]`）|
| 待改：跨文件多篇檢索 | `rag_retriever.py::retrieve_multi_with_context`（L214-300）|
| 待改：引用指示 | `prompt/ai/ai_character_prompt.txt`（L17-23）|
| top_k 常數 | `settings.py:59`（`RAG_MULTI_TOP_K`）|
| 五路通用基準（resume/visual/academic/litedoc/book） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（五路縱向絞殺）+ `pipelines/factory.py` 註冊 |
| 原 multi 設計脈絡 | `.claude-logs/...RAG-1_Phase2_執行計劃.md §3.2.3`（全域 Merge-Sort top-k）|
| BE 工作流 SOP | `ref/WORKFLOW_SOP.md §1.2` + logging/database SOP |

---

## §8 驗證計畫

### §8.1 自動化單元測試（BE-Refactor、pytest）
- **既有**：`pytest tests/ -v`（單篇 RAG / 既有 multi 測試全綠、U6 把關）。
- **預計新增**（mock 多 paper vector store、確定化分數）：
  - `test_multi_per_paper_floor`：N 篇各有候選 → 每篇 ≥ floor_k 進 context（重現吳焴倫場景：低分但有資料的 paper 不再 0 代表）。
  - `test_multi_cap_not_exceeded`：篇數大到 floor×N > cap → 總 chunk ≤ cap、floor 自適應降級仍盡量覆蓋。
  - `test_multi_global_fill_after_floor`：保底後剩餘名額按全域分數補位（高分不被犧牲）。
  - `test_multi_zero_candidate_paper_skipped`：某 paper 全 < threshold → 該 paper 0 貢獻（不硬塞雜訊）。
  - `test_single_path_unchanged`：`retrieve_with_context` 行為等價（U6）。
  - `test_prompt_forbids_bracket_citation`：grep `ai_character_prompt.txt` 含「禁 [數字] 引用」指示（U5）。
  - **（§9 Q5）** 跨 doc-type 覆蓋測試：mock resume(5 chunk)+book(845 chunk) → 保底使 resume 仍被代表。

### §8.2 手動端到端（E2E）驗證流程（baron 測試機）
1. `#cv 哪幾位有碩士以上學位？` → 答案**涵蓋多人**（含吳焴倫慕尼黑碩士、林晉羽等）、不再只有李宗原。
2. 抓 `grep "[retrieve_multi].*chosen" logs` → `chosen` 應**含 YuLun_Wu_CV 等先前 0 代表的 paper**。
3. 答案**不再出現 bare `[1][2][5]`**、來源以《文件名》「章節」呈現（U5）。
4. 單篇問答（無 #）→ 與改動前一致（U6）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1 保底策略** | **per-paper 保底 floor_k=2 + 全域補位**（每篇有候選者先各取 top-2、再按全域分數補滿 cap）；非純 round-robin、非比例制 | floor=2 對「比較」夠用（學歷+一段經歷）；全域補位保留高分品質；比 round-robin 簡單、比比例制可預測 |
| **Q2 top_k / cap** | `RAG_MULTI_TOP_K` 由「全域 7」改**保底制**：新增 `RAG_MULTI_FLOOR_K`(預設 2) + `RAG_MULTI_MAX_CHUNKS`(預設 ~15) cap；context 總數 = `min(floor_k×N 補到 cap, cap)`；floor×N>cap 時 floor 降至 1 | 名額隨篇數自適應（7 對 6 篇太小）；cap 防 prompt 爆炸（呼應原 §3.3 prompt 爆炸顧慮）；env 可調 |
| **Q3 citation [N] 禁用** | **併入本 plan**（U5）：`ai_character_prompt.txt` 加「禁 [數字]、只用《文件名》「章節」」一句 | 與 multi 修正同屬「跨文件答案品質」、一起驗收最省事；改動極小、低風險 |
| **Q4 同人 A+B軌 重複代表**（shadow 不過濾下） | **本 plan 不處理、僅標註殘留**；列為後續（待 PIPE-FLIP 或內容級去重另議） | baron 已拍板不過濾 shadow（維 B軌可見性）；內容去重（同 paper_id 去 `_shadow` 後合併）是另一設計、不混入本次；先標清楚「同人可能出現兩次」 |
| **Q5 五路驗證範圍** | **補一個跨 doc-type 測試**（resume+book mock、§8.1）；E2E 仍以 resume `#cv` 為主 | retrieve_multi 無 doc_type 分支、邏輯天生通用；補一個混型測試證明「小文件不被大文件壓制」即足、不需五路各跑一遍 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-MULTI-1（跨文件多篇檢索覆蓋 + 引用修正）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 RAG-MULTI-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含 commit 拆分（屬 tasks 階段）；不動單篇路徑 / shadow 過濾 / 索引層；改動限檢索層 + 提示詞 |
| **改版觸發條件** | §1–§9 任一規格條款變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 檢索演算法唯一改點 `retrieve_multi_with_context`；引用指示唯一源 `ai_character_prompt.txt`；五路通用性靠 doc-type-agnostic、不在各路重寫 |

### §99.2 Revision 歷程

- v1 (2026-06-09)：初版建立。修法 A（每篇保底覆蓋 + cap）+ 問題 2（禁 bare [N]）；**刻意不做 shadow 過濾**（baron 拍板·維 B軌可見性）；五路通用（retrieve_multi 無 doc_type 分支）；§9 五項 Open Questions（保底策略/top_k cap/citation/同人去重/五路驗證）；不含 commit 拆分。
