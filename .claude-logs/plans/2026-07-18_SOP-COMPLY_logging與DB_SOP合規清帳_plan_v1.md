# SOP-COMPLY logging 與 DB SOP 合規清帳 plan

> 目的：關閉 PROJECT-REVIEW 程式碼品質 #1 及 DB SOP 違規——(A) `except` 區塊內 `logger.error` 丟棄 stack trace（未帶 `exc_info=True`）；(B) `llm/client.py:181` 靜默吞例外（`except Exception: pass`）；(C) `paper_manager.py` 13 處裸 `commit()`（未在 `with session.begin()` 交易守護內）。純後端合規清帳，零功能變更、零 DB schema、零前端。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：三類 SOP 違規（本任務為「實施專案自己的 logging/database SOP」之清帳）：
  - **(A) logging**（framework §4.3.2 / WORKFLOW_SOP §5.1）：**AST 精確解析為 25 處** `except` 區塊內 `logger.error(...)` 未帶 `exc_info=True`、丟棄 traceback（生產除錯最大傷害），分布 9 檔（`AI_professor_chat.py`×5 / `extra_info_processor.py`×5 / `pipeline_core.py`×4 / `ai_core.py`×3 / `rag_retriever.py`×3 / `paper_manager.py`×2 / `rag_processor.py`×1 / `resume_processor.py`×1 / `web_server.py`×1）。**⚠️ 數字校正**：單行 `grep -v exc_info` 得 40 係誤差——其中 **14 處** `exc_info=True` 位於**續行**（多行 call、如 `AI_professor_chat.py:133/356`）為假陽性、已帶 exc_info；另 **1 處** `rag_retriever.py:96` 為非-except 守衛日誌（無 active exception、補之反記 `NoneType: None`）須排除。真違規 = 25。
  - **(B) 吞例外**：`llm/client.py:181` grounding 來源解析 `except Exception: pass` → 靜默丟棄引用來源、零日誌。（註：`:111` 已 `warning`、非吞、不在範圍。）
  - **(C) database**（framework §4.4.1 / WORKFLOW_SOP §5.2）：`paper_manager.py` **13 處**裸 `commit()`（無 rollback 守護）。分兩型：**自持 session**（`with db.SessionLocal() as s: … s.commit()`·7 處：82/274/287/387/415/424/1055）+ **借用 session**（參數傳入、`session.commit()`·6 處：582/623/638/724/748/844）。
- **解法**：
  - (A)：`except` 區塊內 `logger.error(...)` 補 `exc_info=True`（訊息文字保留）；非-except 守衛日誌排除或降 `warning`。
  - (B)：`:181` 改 `logger.warning("grounding source parse failed", exc_info=True)`（不 pass、不中斷串流）。
  - (C)：**自持型**——寫入區包 `with s.begin():`、移除顯式 `s.commit()`（`db.py::init_db` 已示範）；**借用型**——不可機械式套 `with session.begin()`（呼叫端 `SessionLocal` autobegin 後再 begin 會報錯），採**呼叫端協調**（方案 A·OQ3 拍板）：`web_server.py` folder/tag 端點 + **直接呼叫這些 helper 的測試檔**改 `with s.begin():`、helper 內移除 `session.commit()`。
- **影響範圍**：BE-Refactor；`llm/client.py` + `paper_manager.py`（logging + 13 commit）+ 9 檔 logging 點 + `web_server.py` folder/tag 端點（借用型呼叫端）+ **3 測試檔**（`tests/test_paper_tags.py` / `test_normalize_tag.py` / `test_folder_auto_tags.py`·直接呼叫借用型 helper、須同步包 `with s.begin():`）。零功能語意變更、零 DB schema、零前端。

---

## §2 目標規格

達成後最終狀態須滿足以下可檢驗條件：

1. **(A) logging 合規**：所有**位於 `except` 區塊內**的 `logger.error(...)` 均含 `exc_info=True`；`grep -rn "logger.error(" <範圍> | grep -v exc_info` 之剩餘命中**僅**為非-except 守衛日誌（明列白名單）。
2. **(B) 吞例外根除**：`llm/client.py:181` 不再 `except Exception: pass`；改為帶 `exc_info=True` 的 `logger.warning`（grounding 解析失敗有日誌、串流不中斷）。
3. **(C) database 合規**：`paper_manager.py` 裸 `commit()` 全數修正——自持型 7 處包 `with s.begin():`、無裸 commit；借用型 6 處採呼叫端協調（helper 移除 `session.commit()`，`web_server.py` 端點 + 3 直呼測試檔改 `with s.begin():`）。`grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"` **歸零**。**測試零回歸**：3 測試檔（`test_paper_tags.py`/`test_normalize_tag.py`/`test_folder_auto_tags.py`）之 `with SessionLocal() as s: pm.set_paper_*(s,…)` 改為 `with s.begin():`（否則移除內部 commit 後 SessionLocal 關閉自動 rollback、讀回斷言失敗）。
4. **行為等價**：logging 訊息內容與觸發時機不變（僅增 traceback）；DB 寫入結果與既有一致（成功 commit / 失敗改為自動 rollback，語意更安全非改變）。
5. **零回歸**：全套件綠燈基線不退化（現 745 passed）；§5 SOP 一致性核查（logging + database）通過。

### §2.5 候選方案（Diverse Rollout）

僅 (C) 借用型 session commit 修法屬語意分散決策；(A)/(B) 為單一直接修法。

| 方案（限 C 借用型） | 核心做法 | trade-offs |
|---|---|---|
| **方案 A（推薦）呼叫端協調** | web_server folder/tag 端點改 `with s.begin(): paper_manager.create_folder(s, …)`、函式內移除 `session.commit()` | 交易邊界正確歸呼叫端；改動外溢 web_server（可控·端點少）；符合 SOP 精神 |
| 方案 B `begin_nested()` | 借用函式內 `with session.begin_nested():` | 侷限 paper_manager 不外溢；但 SAVEPOINT 語意較重、且外層仍需 commit |
| 方案 C（否決·延後）本任務只修自持型、借用型列 backlog | 借用型不動 | 最小侵入、但 6 處仍違規、DB SOP 未全清 |

- **選定理由（OQ3 拍板＝方案 A）**：交易邊界最清晰、對齊「呼叫端持有 session 生命週期」原則；外溢 `web_server.py` 端點少、可控；**同步修改 3 個直呼 helper 的測試檔**（`with s.begin():`）以維持測試零回歸——不留 backlog、徹底理清交易邊界。
- **否決留痕**：方案 B（begin_nested·SAVEPOINT 語意較重、外層仍需 commit）/ 方案 C（延後借用型·6 處仍違規、DB SOP 未全清）均留底。

---

## §3 現況與證據

- **logging（A）**：AST 精確解析 25 處 `except` 內 `logger.error` 無 `exc_info`（如 `ai_core.py:37/91`、`pipeline_core.py:358/359`、`rag_retriever.py:89`）→ 應補；`rag_retriever.py:96`（非-except 守衛）→ 排除；`AI_professor_chat.py:133/356` 等 14 處 exc_info 在續行→非違規。
- **吞例外（B）**：`llm/client.py:181` `except Exception: pass`（grounding 來源）；`:111` 已 `logging...warning(...)`（不在範圍）。
- **database（C）**：`paper_manager.py` 13 裸 commit；自持型 7（SessionLocal + s.commit）/ 借用型 6（`create_folder`/`update_folder`/`delete_folder`/`_apply_folder_path_tags`/`set_paper_folder`/`set_paper_tags` 之 `session.commit()`）。`db.py::init_db` 已示範 `with session.begin()` 正範式。

### §3.1 grep 鋼鐵證據

```bash
# 單行 grep 得 40（含 14 續行 exc_info 假陽性 + 1 非-except 守衛）；AST 精確解析真違規 = 25
$ ./venv/bin/python -c "import ast … 計 except 內 logger.error 無 exc_info"   # → 25
# 逐檔（真違規）：AI_professor_chat 5 / extra_info_processor 5 / pipeline_core 4 / ai_core 3 /
#   rag_retriever 3 / paper_manager 2 / rag_processor 1 / resume_processor 1 / web_server 1
# 排除：rag_retriever.py:96（非-except 守衛）；AI_professor_chat.py:133/356 等 14 處（exc_info 續行）

$ sed -n '181p' llm/client.py           # except Exception:
$ sed -n '182p' llm/client.py           #     pass  ← 靜默吞

$ grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*begin()"
82/274/287/387/415/424/1055（自持型·SessionLocal+s.commit）
582/623/638/724/748/844（借用型·session 參數）
# 借用型函式簽名：create_folder(session,…) / update_folder / delete_folder /
#   _apply_folder_path_tags / set_paper_folder / set_paper_tags

$ grep -n "with session.begin" db.py    # init_db 正範式（對照基準）
```

---

## §4 跨 Phase 接縫契約

無。本任務單一關注點（SOP 合規），多檔改動但無 Phase/模組間資料 handoff。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 對非-except 的 logger.error 誤加 exc_info（無 active exception → 日誌記 "NoneType: None"） | 🟡 中 | §2 #1 明限「僅 except 區塊內」；tasks 逐點確認 context；非-except 明列白名單排除 |
| (C) 借用型套 `with session.begin()` 撞 autobegin → RuntimeError | 🟡 中 | 採方案 A 呼叫端協調（不在 helper 內 begin）；§9 OQ3 定案 |
| **移除 helper 內部 commit → 3 直呼測試檔未 commit、SessionLocal 關閉 rollback、讀回斷言失敗** | 🟡 中 | **測試檔納入修改範圍**：`test_paper_tags.py`/`test_normalize_tag.py`/`test_folder_auto_tags.py` 之 helper 呼叫改包 `with s.begin():`（§2 #3 / §2.5）；§8 全套件驗零回歸 |
| DB 交易邊界改動致既有寫入行為變化 | 🟡 中 | 語意等價（成功 commit / 失敗改自動 rollback＝更安全）；§8 pytest 覆蓋 folder/tag/chunk 寫入 |
| logging 訊息 str(e) 冗餘（加 exc_info 後 {str(e)} 重複） | 🟢 低 | 保留訊息文字（最小改動）；str(e) 精簡屬選配（§9 OQ2） |
| 多檔改動觸發 regression | 🟡 中 | §8 全套件 pytest + §5 SOP 核查；行為等價原則 |

對齊 framework §4.1 #5。

---

## §6 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] logger.error / warning 的**訊息文字語意與觸發條件**——僅增 `exc_info=True`（及 :181 改 warning），不改訊息意義、不改控制流。
- [ ] **非-except 的 logger.error 守衛日誌**（如 `rag_retriever.py:96`）——非 SOP 違規、不加 exc_info。
- [ ] DB **寫入的業務邏輯與資料內容**——僅改交易守護包裝（commit→begin()），不改寫入什麼。
- [ ] `db.py::init_db` 既有正範式；SEC-SECRET / SEC-HARDEN / SEC-XSS 既有落地。
- [ ] 前端 `static/**`、DB schema、非本清帳範圍之 `.py` 邏輯。
- [ ] `llm/client.py:111`（已 warning、非吞例外、不在範圍）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流分類（改 `.py` 業務邏輯、非緊急 → BE-Refactor） | `CLAUDE.md §2` / `ref/WORKFLOW_SOP.md §1.2` |
| **BE-Refactor 必讀 SOP（本任務即實施對象）** | `sop/2026-05-23_logging_SOP_手冊.md`（§5.1 exc_info）+ `sop/2026-05-23_database_SOP_手冊.md`（§5.2 session.begin） |
| logging/database 規格 | framework §4.3.2 / §4.4.1 |
| plan 結構 SSOT | `templates/template_plan.md` |
| 六階段 / 命名 / §7.2 | `ref/WORKFLOW_SOP.md §3 / §6 / §7.2` |
| 漏洞來源 | PROJECT-REVIEW 程式碼品質 #1 + DB SOP §5.2 |
| 正範式對照 | `db.py::init_db`（`with session.begin()`） |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試回歸**：
  ```bash
  ./venv/bin/python -m pytest tests/ -q     # 期望：綠燈基線不退化（現 745 passed）
  ```
- **§5 SOP 一致性核查（落地前強制、每 commit 執行報告必貼）**：
  ```bash
  # logging：except 區塊內 logger.error 須含 exc_info（剩餘命中僅白名單非-except）
  grep -rn "logger\.error(" <改動檔> | grep -v exc_info
  # database：paper_manager 裸 commit 依拍板範圍歸零/僅剩延後
  grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"
  ```
- **預計新增測試**：DB 交易守護——folder/tag/chunk 寫入成功 commit、模擬中途例外自動 rollback（不留半寫）；（選配）logging 守衛測試以 grep 源碼斷言 except-block logger.error 皆含 exc_info。

### §8.2 手動端到端（E2E）驗證流程（baron）

1. 觸發一個會失敗的處理流程 → server log 出現**完整 traceback**（非僅單行 str(e)）。
2. 聯網問答 grounding 解析異常 → log 有 warning（非靜默）。
3. 建立/移動/刪除資料夾、設標籤 → 功能正常；模擬中途失敗 → 無半寫髒資料。

> §7.2 跨 Phase 整合測試：多檔但單一關注點、無跨 Phase 資料 handoff（§4 標「無」），依 §7.2 不適用；§9 OQ 顯式登記豁免。

---

## §9 Open Questions

> **拍板狀態（2026-07-18，baron review）**：OQ1–OQ6 全數採推薦定案 → execution-ready、可拆 tasks。並依 review 補強兩項掃描發現，回灌 §1/§2/§3（logging 數字 40→**AST 精確 25**、14 續行假陽性 + 1 非-except 守衛排除）+ §1/§2.5/§2 #3/§5（#C 借用型採方案 A、**3 直呼測試檔納入修改範圍** `with s.begin():` 防 rollback 失敗）。

| 開放問題 | 推薦方案（＝拍板結果） | 推薦理由 |
|---|---|---|
| OQ1：(A) 範圍 | **僅 except 區塊內補 exc_info（AST 精確 25 處）；非-except 守衛 + 續行 exc_info 假陽性排除** | 非-except 無 active exception、加 exc_info 記 "NoneType: None" 屬錯 |
| OQ2：logger.error 訊息 `{str(e)}` 冗餘是否一併精簡？ | **保留訊息、僅加 exc_info（最小改動）；str(e) 精簡另案** | 最小侵入、聚焦合規 |
| OQ3：(C) 借用型 6 處處置 | **納入·方案 A 呼叫端協調 + 同步修 3 直呼測試檔（`with s.begin():`）** | 交易邊界正確、外溢少可控、不留 backlog；測試零回歸 |
| OQ4：(B) llm/client:181 → warning vs error？ | **warning + exc_info**（不中斷串流） | grounding 解析失敗屬降級非致命 |
| OQ5：是否加 grep-gate 防回歸？ | **加源碼守衛測試**（except-block logger.error 皆含 exc_info） | 防未來新增違規 |
| OQ6：§7.2 跨 Phase 整合測試豁免 | **顯式豁免** | 多檔但無資料 handoff |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SOP-COMPLY logging/DB SOP 合規清帳的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 SOP-COMPLY tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-18)：初版建立（PROJECT-REVIEW 程式碼品質 #1 + DB SOP §5.2 衍生；logger.error 無 exc_info / llm/client:181 吞例外 / paper_manager 13 裸 commit 分自持 7+借用 6；§7.2 豁免）
- v1.1 (2026-07-18)：baron review 拍板——OQ1–OQ6 全定案、標 execution-ready；補強兩掃描發現〔① logging 數字校正：單行 grep 40→**AST 精確 25**〔14 處 exc_info 續行假陽性〔AI_professor_chat:133/356 等〕+ 1 非-except 守衛〔rag_retriever:96〕排除〕→ §1/§2/§3 / ② #C 借用型方案 A 呼叫端協調**須同步修 3 直呼測試檔**〔test_paper_tags/test_normalize_tag/test_folder_auto_tags 之 `with SessionLocal() as s: pm.set_paper_*(s)` 改包 `with s.begin():`；否則移除 helper 內部 commit 後 SessionLocal 關閉 rollback、讀回斷言失敗〕→ §1/§2 #3/§2.5/§5〕；規格方向未變、僅精準化 + 補測試範圍）
