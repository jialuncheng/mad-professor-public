# RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正 — Tasks

> 本文件為 RAG-MULTI-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_plan_v3.md` 計畫產出，含 5 個 Commit（C1–C4 + C5 Checkout 收官）。
> **BE-Refactor、改檢索層 + 提示詞 + settings 常數；不動單篇路徑 / shadow 過濾 / 索引層 / threshold 語意。**

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_rag_multi.py`（multi 保底覆蓋 / cap / 截斷 / 補位 / 混型 / 單篇不變 / 提示詞禁 [N]）|
| **修改檔案** | 3 個 | `settings.py`（廢 `RAG_MULTI_TOP_K`、立 `RAG_MULTI_FLOOR_K`/`RAG_MULTI_MAX_CHUNKS`）/ `rag_retriever.py`（`retrieve_multi_with_context` 每篇保底演算法 + import + top_k→cap override）/ `prompt/ai/ai_character_prompt.txt`（引用段禁 bare [N]）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1（settings 常數）→ C2（retrieve_multi 演算法）→ C3（提示詞禁 [N]）→ C4（單元測試）→ C5（Checkout 收官）|
| **baton 歸檔** | 1 次 | C5 Checkout：`mv` plan v1/v2/v3 → `plans/` + tasks → `tasks/` + C1-C5 執行報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：跨文件 `#hashtag` 多篇 RAG（`retrieve_multi_with_context`）全域 top-k=7 飢餓 → 6 篇被擠成 2 人代表（李宗原 A+B軌 佔 5/7、吳焴倫碩士漏召）；另 LLM 多吐無依據 `[1][2][5]` 引用。
- **解法**：拆 5 commit——
  - **C1 — settings 常數（廢 TOP_K 立保底常數）**：`settings.py` 加 `RAG_MULTI_FLOOR_K`(2)+`RAG_MULTI_MAX_CHUNKS`(15)，C2 消費後廢 `RAG_MULTI_TOP_K`。
  - **C2 — retrieve_multi 演算法（每篇保底覆蓋與防爆 cap）**：`rag_retriever.py` 廢全域 top-k、改 per-paper 保底（`effective_floor = min(floor_k, max(1, cap//N))`、不足全拿、補位池排除已選、N>cap 按最高分截斷）+ `top_k` 參數改 cap override。
  - **C3 — 提示詞禁 [N]（引用標記去噪）**：`ai_character_prompt.txt` 引用段明令禁 bare `[數字]`、只留《文件名》「章節」。
  - **C4 — 單元測試（保底/cap/截斷/補位/混型/單篇）**：新建 `tests/test_rag_multi.py`。
  - **C5 — Checkout 收官（Conformance 驗收與一次性歸檔）**。
- **影響範圍**：BE-Refactor、檢索層 + 提示詞 + settings；**不動單篇 `retrieve_with_context` / shadow 過濾 / 索引層 / threshold**。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理 |
|---|---|---|
| `settings.py` | `L53 RAG_SCORE_THRESHOLD=0.22`、`L59 RAG_MULTI_TOP_K=7` | 無保底/ cap 常數；`RAG_MULTI_TOP_K` 待廢 |
| `rag_retriever.py` | `L7 from settings import RAG_SCORE_THRESHOLD, RAG_MULTI_TOP_K`；`retrieve_multi_with_context` `L251-252` `top_k=RAG_MULTI_TOP_K`、`L286-287` `all_candidates.sort; top_chunks=all_candidates[:top_k]`（純全域 top-k） | 無 per-paper 保底 → 飢餓；`top_k` 參數語意待改 cap override |
| `prompt/ai/ai_character_prompt.txt` | `L17-23` 引用段「標註來源章節…逐一標出」 | 未禁 bare [N] → LLM 自吐 `[1][2][5]` |
| `tests/test_phase2_p2_2_hashtag_routing.py` | 既有 hashtag 路由測試 | 無 multi 保底覆蓋專屬測試 |

---

## §3 觀察問題

### 問題 #1：全域 top-k 飢餓（核心）
- **證據**：`logs/pipeline.log`（2026-06-09 04:04）`[retrieve_multi] papers=6 candidates=21 top_k=7 chosen=`→ 7 格＝李宗原 5（含 shadow 2）/ 黃忠偉 2 / 吳焴倫·林晉羽·Priyal 各 0；`rag_retriever.py:286-287` 純 `all_candidates[:top_k]`。
- **影響**：比較類查詢漏掉有資料的文件（吳焴倫碩士），AI 誤答「只有李宗原有碩士」。

### 問題 #2：LLM 多吐無依據 [N]
- **證據**：`rag_retriever.py:296-300` context 用《title》標來源、**無編號**；`ai_character_prompt.txt:17-23` 叫標來源章節、未禁 [N] → LLM 自吐 `[1][2][5]` 指向虛空。
- **影響**：引用數字對應不到任何來源、UI 無腳註。

---

## §4 設計方案

依 plan v3 §2 U1-U7：

### §4.1 C1 — settings 常數
`settings.py` `RAG_MULTI_TOP_K` 鄰近，新增 `RAG_MULTI_FLOOR_K=int(os.getenv("RAG_MULTI_FLOOR_K","2"))`、`RAG_MULTI_MAX_CHUNKS=int(os.getenv("RAG_MULTI_MAX_CHUNKS","15"))`；**本 commit 保留 `RAG_MULTI_TOP_K`**（C2 消費新常數並廢之、避免中途 import 斷裂）。

### §4.2 C2 — retrieve_multi 每篇保底演算法
重寫 `retrieve_multi_with_context` 選取段（`L286-287` 區）：per-paper 保底 + 全域補位 + cap + N>cap 截斷；`top_k` 參數改 cap override；import 換 `RAG_MULTI_FLOOR_K, RAG_MULTI_MAX_CHUNKS`（去 `RAG_MULTI_TOP_K`）；同步 `settings.py` 移除 `RAG_MULTI_TOP_K`（C2 後無人讀）。

### §4.3 C3 — 提示詞禁 [N]
`ai_character_prompt.txt` 引用段（L17-23）加一行禁 bare `[數字]` 引用、保留《文件名》「章節」。

### §4.4 C4 — 單元測試
新建 `tests/test_rag_multi.py`（mock vector store + 確定化分數），覆蓋 plan §8.1 全部測試項。

### §4.5 C5 — Checkout 收官
Conformance + baton 一次性歸檔 + TODO 結案 + hash。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| C1 廢 `RAG_MULTI_TOP_K` 時序致 import 斷裂 | 🟡 中 | C1 **保留** TOP_K、僅加新常數；C2 同 commit 內「換 import + 移除 TOP_K」一氣呵成、無中途斷裂 |
| C2 演算法邊界（N=3 暴漲 / N>cap / 補位重複） | 🟡 中 | 嚴格照 plan §2 U2 公式 `min(floor_k, max(1, cap//N))` + 補位池排除已選 + N>cap 最高分截斷；C4 逐邊界測試 |
| 既有 multi 測試斷言舊全域 top-k 行為 | 🟡 中 | C2 同 commit 更新 `test_phase2_p2_2_hashtag_routing.py` 受影響斷言（若有）；以新保底語意為準 |
| 單篇路徑誤傷 | 🟢 低 | 改點限 multi、與單篇物理分離；C4 `test_single_path_unchanged` 把關 |
| 提示詞禁 [N] 影響單篇 | 🟢 低 | 共用人設、對所有路徑正向；C4 grep + plan §8.2 步驟 5 驗單篇無退化 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
grep -n 'RAG_MULTI_FLOOR_K\|RAG_MULTI_MAX_CHUNKS' settings.py        # 兩新常數存在
grep -n 'RAG_MULTI_TOP_K' settings.py                                # C1 仍保留（C2 才廢）
venv/bin/python -c "import settings; print(settings.RAG_MULTI_FLOOR_K, settings.RAG_MULTI_MAX_CHUNKS)"  # 2 15
venv/bin/python -m pytest tests/ -q                                  # 不退化
```

### §6.2 C2 驗收
```bash
grep -n 'RAG_MULTI_TOP_K' settings.py rag_retriever.py               # 期望：無命中（已廢）
grep -n 'RAG_MULTI_FLOOR_K\|RAG_MULTI_MAX_CHUNKS\|effective_floor\|min(.*max(1' rag_retriever.py
grep -n 'top_chunks = all_candidates\[:top_k\]' rag_retriever.py     # 期望：無命中（純全域 top-k 已廢）
grep -n '# === \[RAG-MULTI-1 C2 START\]\|# === \[RAG-MULTI-1 C2 END\]' rag_retriever.py  # 各 1
venv/bin/python -m pytest tests/test_phase2_p2_2_hashtag_routing.py -q
```

### §6.3 C3 驗收
```bash
grep -n '禁\|不要\|不可\|\[數字\]\|不得使用\|\[1\]' prompt/ai/ai_character_prompt.txt | grep -i '數字\|\[1\]\|bare'
grep -n '# === \[RAG-MULTI-1 C3' prompt/ai/ai_character_prompt.txt 2>/dev/null || grep -n 'RAG-MULTI-1' prompt/ai/ai_character_prompt.txt
# plan v3 §8.1 點3：共載 explain_prompt 無反向 [N] 指示（執行報告貼結果、無則「無命中（合規）」）
grep -nE '\[1\]|\[N\]|引用' prompt/ai/ai_explain_prompt.txt
```

### §6.4 C4 驗收
```bash
venv/bin/python -m pytest tests/test_rag_multi.py -v                 # 全綠
venv/bin/python -m pytest tests/ -q                                 # 全套件不退化
```

### §6.5 C5 Checkout 驗收
```bash
ls -la .claude-logs/plans/2026-06-09_RAG-MULTI-1_*plan_v1.md .claude-logs/plans/2026-06-09_RAG-MULTI-1_*plan_v2.md .claude-logs/plans/2026-06-09_RAG-MULTI-1_*plan_v3.md
ls -la .claude-logs/tasks/2026-06-09_RAG-MULTI-1_*tasks.md
ls -la .claude-logs/executions/2026-06-09_RAG-MULTI-1_C*_執行.md     # C1-C5
ls .claude-logs/baton/ | grep RAG-MULTI-1 || echo "✅ baton 已清"
```

---

## §7 不可動清單

明確劃定修改邊界。**以下嚴禁任何改動：**

- [ ] `rag_retriever.py::retrieve_with_context`（**單篇路徑**、top_k=5）— 行為 byte 不變。
- [ ] `_get_vector_store` / FAISS 載入 / `RAG_SCORE_THRESHOLD`（L53）門檻語意 — 不改（僅改 top_chunks 選取分配）。
- [ ] **shadow 過濾**——刻意不做（plan U7）；`list_paper_uuids_by_tag` 不加 `_shadow` 排除。
- [ ] `rag_indexer.py` / `rag_processor.py` / embedding 模型 / 向量庫格式 / `paper_manager.py` 寫入 — 零改動。
- [ ] context 格式 `## 摘自文件《{title}》`（`L296-300`）語意 — 不改（僅改「選哪些 chunk」、不改「怎麼排版」）。
- [ ] 母 plan v10 凍結之 P1-P4 合約與五路策略 — 不碰。
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — settings 常數（廢 TOP_K 立保底常數）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `settings.py`（新增 2 常數、保留 `RAG_MULTI_TOP_K`）+ 改前 `.bak`（archive/）。baton 暫存報告不在此列。 |
| **安全性** | 🟢 高 — 純新增常數、C2 才消費、行為等價（除新常數可讀） |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾 |
| **驗收 grep 條件** | 見 §6.1（兩新常數存在 + import 印值 2/15 + TOP_K 仍在 + pytest 不退化）|
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 改前備份 `cp settings.py archive/2026-06-09_RAG-MULTI-1_C1_settings.py.bak`。② 於 `L59 RAG_MULTI_TOP_K` 鄰近、`# === [RAG-MULTI-1 C1 START/END] ===` 包裹內新增：`RAG_MULTI_FLOOR_K = int(os.getenv("RAG_MULTI_FLOOR_K", "2"))  # 每篇保底 chunk 數（cross-doc 覆蓋下限）` 與 `RAG_MULTI_MAX_CHUNKS = int(os.getenv("RAG_MULTI_MAX_CHUNKS", "15"))  # cross-doc context 總 chunk 上限（防 prompt 爆炸）`。③ **本 commit 不刪 `RAG_MULTI_TOP_K`**（C2 消費新常數後同 commit 廢之、避免中途 import 斷裂）。④ 不動 `RAG_SCORE_THRESHOLD`。 |

### C2 — retrieve_multi 演算法（每篇保底覆蓋與防爆 cap）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `rag_retriever.py`（`retrieve_multi_with_context` 選取段重寫 + import）+ `settings.py`（移除 `RAG_MULTI_TOP_K`）+ 2 改前 `.bak`。 |
| **安全性** | 🟡 中 — 改檢索選取演算法、影響跨文件答案；但與單篇物理分離、唯一呼叫點 AI_professor_chat:127 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾（純函式內邏輯 + 常數移除）|
| **驗收 grep 條件** | 見 §6.2（TOP_K 無命中 + effective_floor/公式存在 + 純全域 top-k 已廢 + 標記平衡 + multi 路由測試）|
| **依賴關係** | **依賴 C1**（消費 `RAG_MULTI_FLOOR_K`/`RAG_MULTI_MAX_CHUNKS`）|
| **具體實作細節** | ① 改前備份 rag_retriever.py + settings.py（`archive/2026-06-09_RAG-MULTI-1_C2_*.bak`）。② `rag_retriever.py:7` import 改 `from settings import RAG_SCORE_THRESHOLD, RAG_MULTI_FLOOR_K, RAG_MULTI_MAX_CHUNKS`（**去 `RAG_MULTI_TOP_K`**）。③ `retrieve_multi_with_context`：`L251-252` `if top_k is None: top_k = RAG_MULTI_TOP_K` 改為 **cap override 語意**：`cap = top_k if top_k is not None else RAG_MULTI_MAX_CHUNKS`（參數 `top_k: Optional[int]=None` 簽名保留、語意註解更新為 cap override）。④ **重寫 `L286-287` 選取段**（`# === [RAG-MULTI-1 C2 START/END] ===` 包裹）依 plan v3 §2 U1/U2/U3：<br>　- `N = len(paper_ids)`（tagged 總數；0 候選 paper 自然不貢獻）。<br>　- `effective_floor = min(RAG_MULTI_FLOOR_K, max(1, cap // N))`。<br>　- 按 pid 分組 `all_candidates`、各組**按 score 降序**取前 `effective_floor`（**不足全拿**＝`grp[:effective_floor]`，Q1 邊界）→ `floored`；以 `id(chunk)`/`(pid, score, chunk)` 記已選、供補位去重。<br>　- **N>cap 極端**（`len(floored) > cap`、即 floor 已 =1 仍 1×N>cap）：按各 paper「最高分 chunk」降序排序、取前 `cap` 篇各 1（Q2 截斷序）。<br>　- **全域補位**：`pool = [c for c in all_candidates if c not in floored]` 按 score 降序、補到 `len ≤ cap`（補位池排除已保底、Q2）。<br>　- 合併 `floored + 補位`、**最終按 score 降序**輸出 `top_chunks`（context 格式 `L296-300` 不變）。<br>⑤ `settings.py` 移除 `RAG_MULTI_TOP_K`（C2 後 rag_retriever 不再 import、無人讀）。⑥ `L289-293` `chosen=` log 保留（驗收與診斷用）。⑦ SOP：logging 無新增 `logger.error`（既有 warning 不動）；database 無 DB 操作（無裸 commit）。⑧ 更新既有 `test_phase2_p2_2_hashtag_routing.py` 中若有斷言舊全域 top-k=7 之處（以新保底語意為準）。 |

### C3 — 提示詞禁 [N]（引用標記去噪）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `prompt/ai/ai_character_prompt.txt`（引用段 L17-23 加禁 [N] 指示）+ 改前 `.bak`。 |
| **安全性** | 🟢 高 — 純提示詞文字、共用人設正向、零 runtime 邏輯 |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | 見 §6.3（禁 [數字] 指示存在）|
| **依賴關係** | 無前置（與 C1/C2 正交）|
| **具體實作細節** | ① 改前備份 `cp prompt/ai/ai_character_prompt.txt archive/2026-06-09_RAG-MULTI-1_C3_ai_character_prompt.txt.bak`。② 於 `L17-23 引用源頭` 段末追加一行（`# === [RAG-MULTI-1 C3] ===` 註記或內文標）：「**僅以《文件名》「章節」標註來源；嚴禁輸出 `[1]`、`[2]` 等純數字引用標記（無對應編號清單、屬無效引用）。**」③ 保留既有「標註來源章節 / 逐一標出 / 綜合多段引用 1-2 段」語意不動。④ **（plan v3 §8.1 點3）共載提示詞檢查**：`grep -nE '\[1\]\|\[N\]\|引用' prompt/ai/ai_explain_prompt.txt`（`AI_EXPLAIN_PROMPT_PATH`、`_prepare_final_messages` 共載），確認 explain_prompt **無反向叫用 [N] 的指示**；**若有則一併禁**（避免與 character_prompt 打架），執行報告 §4 貼 grep 結果（無則貼「無命中（合規）」）。⑤ 提示詞為純文字、無 logging/database SOP 適用。 |

### C4 — 單元測試（保底/cap/截斷/補位/混型/單篇）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `tests/test_rag_multi.py`（純新增測試檔、無業務碼改動）。 |
| **安全性** | 🟢 高 — 純測試新增 |
| **可逆性** | 🟢 高 — `git revert C4` 刪測試檔 |
| **驗收 grep 條件** | 見 §6.4（`pytest tests/test_rag_multi.py -v` 全綠 + 全套件不退化）|
| **依賴關係** | **依賴 C2**（測 C2 演算法）+ C3（測提示詞禁 [N]）|
| **具體實作細節** | 新建 `tests/test_rag_multi.py`，mock `RagRetriever._get_vector_store` 回確定化 `similarity_search_with_score`（distinct 分數、避免 tie 不確定），覆蓋 plan v3 §8.1：`test_multi_per_paper_floor`（每篇 ≥ effective_floor）/ `test_multi_floor_underfilled_takes_all`（1 候選取 1）/ `test_multi_small_n_no_floor_balloon`（N=3 cap=15 → floor=2 非 5）/ `test_multi_cap_not_exceeded`（floor×N>cap → ≤ cap）/ `test_multi_n_gt_cap_truncate_by_best`（N>cap 按最高分取前 cap 篇各 1）/ `test_multi_global_fill_excludes_floored`（補位不重複）/ `test_multi_zero_candidate_paper_skipped`（全 < threshold → 0 貢獻）/ `test_multi_cap_override_param`（`top_k=None→MAX_CHUNKS`、傳值當 cap）/ `test_multi_mixed_doctype_small_not_starved`（複用 floor fixture 換 100-chunk book、resume 仍保底）/ `test_single_path_unchanged`（單篇 retrieve_with_context 等價）/ `test_prompt_forbids_bracket_citation`（grep ai_character_prompt 含禁 [數字]）。檔頭 `# === [RAG-MULTI-1 C4] ===`。 |

### C5 — Checkout 收官（Conformance 驗收與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton → `plans/`（plan v1/v2/v3）+ `tasks/`（tasks）+ `executions/`（C1-C5 執行報告）+ `git add`；更新 `TODO.md`（結案 + hash 回填）+ `prompts/INDEX.md`（✅）。**無業務碼改動。** |
| **安全性** | 🟢 高 — 純歸檔 + 狀態更新 |
| **可逆性** | 🟡 中 — git rename 可還原 |
| **驗收 grep 條件** | 見 §6.5（歸檔到位 + baton 清空）|
| **依賴關係** | **依賴 C1-C4 全部落地** |
| **具體實作細節** | ① **Conformance 三維度驗收**：目標規格（plan v3 §2 U1-U7 對照 C1-C4 grep + pytest 全綠）/ tasks §6 全項 / 不可動清單 git 證據（`git diff --stat` 確認僅 settings/rag_retriever/ai_character_prompt/test_rag_multi + .bak、單篇路徑/索引層/threshold 零改）。② SOP 核查彙整（logging：本任務無新增 `logger.error`；database：grep `.commit()` 無裸 commit、合規）。③ **baton 一次性歸檔**：`mv` plan v1/v2/v3 → `plans/`（三版保留作 §1.9 軌跡）、tasks → `tasks/`、C1-C5 執行報告 → `executions/`。④ **TODO 結案**：`## ✅ 已完成` 新增 `### BE-Refactor RAG-MULTI-1` 完成表（C1-C5 + Hash `待 baron 回填`）+ active 移除 + 索引 ✅ + 全量 hash 自癒。⑤ `prompts/INDEX.md` RAG-MULTI-1 狀態 🟡→✅。⑥ C5 執行報告直寫 `executions/`。⑦ msg 草稿寫 `/tmp/RAG-MULTI-1_C5_msg.txt`（Co-Authored-By: Claude Opus 4.8 (1M context)）。⑧ 嚴禁自發 git commit/push。 |

---

## §9 Open Questions

無。（規劃層 Open Questions 已於 plan v3 §9 五項全定案；本 Tasks 階段不再開放。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-MULTI-1 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RAG-MULTI-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動單篇路徑 / shadow 過濾 / 索引層 / threshold；嚴禁跨 Commit 混合；嚴禁自動 git commit/push；C1-C4 嚴禁 mv baton |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；演算法規格在 plan v3 §2、不在本檔重寫 |

### §99.2 Revision 歷程

- v1 校訂 (2026-06-09)：baron 一致性核對——補回 plan v3 §8.1 點3（C3 共載 `ai_explain_prompt.txt` 無反向 [N] 檢查 + §6.3 grep），恢復 tasks↔plan v3 完全一致。
- v1 (2026-06-09)：初版拆分——依 plan v3 拆 5 commit（C1 settings 常數 / C2 retrieve_multi 每篇保底演算法 / C3 提示詞禁 [N] / C4 單元測試 / C5 Checkout 收官）；BE-Refactor、各 Commit 各產執行報告暫存 baton、Checkout 一次性歸檔 plan v1/v2/v3 + tasks + 各報告；不動單篇路徑/索引層/threshold/shadow 過濾。
