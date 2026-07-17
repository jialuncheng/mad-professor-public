# SOP-COMPLY logging 與 DB SOP 合規清帳 — Tasks

> 本文件為 SOP-COMPLY 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md`（v1.1 execution-ready）產出，含 4 個 Commit（C1 → C2 → C3 → checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_sop_comply_guard.py`（grep-gate 源碼守衛·OQ5） |
| **修改檔案** | 13 個 | logging（`AI_professor_chat.py` / `processor/extra_info_processor.py` / `pipeline_core.py` / `ai_core.py` / `rag_retriever.py` / `processor/rag_processor.py` / `processor/resume_processor.py` / `web_server.py` / `paper_manager.py`）+ `llm/client.py`（吞例外）+ DB（`paper_manager.py`〔已列〕 / `web_server.py`〔已列〕）+ 測試（`tests/test_paper_tags.py` / `tests/test_normalize_tag.py` / `tests/test_folder_auto_tags.py`） |
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` baton plan + tasks + C1-C3 執行報告 → `plans/` + `tasks/` + `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：實施專案自己的 logging/database SOP 清帳——(A) 25 處 `except` 內 `logger.error` 缺 `exc_info` / (B) `llm/client.py:181` 吞例外 / (C) `paper_manager.py` 13 裸 commit（自持 7 + 借用 6）。
- **解法（4 commit·按 SOP 域拆）**：
  - **C1 — Logging Hardening（日誌合規補齊）**：25 處 `except` 內 `logger.error` 補 `exc_info=True`（9 檔）+ `llm/client.py:181` `except: pass` → `logger.warning(exc_info=True)` + 新增 grep-gate 守衛測試。
  - **C2 — Self-Owned Transaction Guard（自持交易守護）**：`paper_manager.py` 7 處自持型 `with SessionLocal() as s: … s.commit()` → 寫入區包 `with s.begin():`、移除顯式 commit。
  - **C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）**：6 借用 helper 移除 `session.commit()` + `web_server.py` 5 端點包 `with s.begin():` + 3 直呼測試檔包 `with s.begin():`（**原子·三者同 commit**）。
  - **checkout — 成果收官歸檔**。
- **影響範圍**：BE-Refactor；13 檔（9 logging + llm/client + paper_manager + web_server + 3 測試）+ 1 新測試；零功能語意變更、零 DB schema、零前端。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 |
|---|---|---|
| 9 檔（AI_professor_chat 等） | 25 處 `except` 內 `logger.error(...)` 無 `exc_info` | (A) 丟棄 traceback |
| `llm/client.py:181` | `except Exception: pass`（grounding 解析） | (B) 靜默吞例外 |
| `paper_manager.py` | 7 自持（82/274/287/387/415/424/1055）+ 6 借用（582/623/638/724/748/844）裸 commit | (C) 無 rollback 守護 |
| `web_server.py` | 5 端點（1174/1193/1212/1236/1241）`with SessionLocal() as s: pm.<helper>(s,…)` 依賴 helper 內部 commit | (C) 借用型呼叫端 |
| 3 測試檔 | `with SessionLocal() as s: pm.set_paper_*(s,…)` 依賴 helper 內部 commit + 讀回斷言 | (C) 移除內部 commit 後失敗 |

---

## §3 觀察問題

### 問題 #1（A）：except 內 logger.error 丟 traceback
- **證據**：AST 精確 25 處（`ai_core.py:37/91`、`pipeline_core.py:358/359`、`AI_professor_chat.py`×5 等）；排除 `rag_retriever.py:96`（非-except 守衛）+ 14 處 exc_info 續行假陽性。

### 問題 #2（B）：llm/client.py:181 吞例外
- **證據**：`llm/client.py:181` `except Exception: pass`（`:111` 已 warning、排除）。

### 問題 #3（C）：13 裸 commit（自持 + 借用）
- **證據**：`paper_manager.py` 7 自持 + 6 借用；借用 helper 由 `web_server.py` 5 端點（1174/1193/1212/1236/1241）+ 3 測試檔直呼；`db.py::init_db` 為 `with session.begin()` 正範式。

---

## §4 設計方案

### §4.1 C1 — Logging Hardening（日誌合規補齊）
- 9 檔 25 處 `except` 內 `logger.error(msg)` → `logger.error(msg, exc_info=True)`（訊息文字不動）。逐檔（AST 清單）：`AI_professor_chat.py`×5 / `extra_info_processor.py`×5 / `pipeline_core.py`×4 / `ai_core.py`×3 / `rag_retriever.py`×3 / `paper_manager.py`×2 / `rag_processor.py`×1 / `resume_processor.py`×1 / `web_server.py`×1。**排除** `rag_retriever.py:96`（非-except 守衛）+ 續行 exc_info 假陽性。
- `llm/client.py:181` `except Exception: pass` → `except Exception: logger.warning("grounding source parse failed", exc_info=True)`（不中斷串流）。
- 新增 `tests/test_sop_comply_guard.py`：AST 掃描斷言「`except` 內 `logger.error` 皆含 `exc_info`」（防回歸·OQ5）。

### §4.2 C2 — Self-Owned Transaction Guard（自持交易守護）
- `paper_manager.py` 7 處 `with db.SessionLocal() as s: … s.commit()` → 寫入區包 `with s.begin():`、移除顯式 `s.commit()`（比照 `db.py::init_db`）。逐處確認寫入邊界正確（begin 區僅含寫入、不含第三方 API/CPU 密集，對齊 database SOP §極短交易）。

### §4.3 C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調·原子）
- `paper_manager.py` 6 借用 helper（`create_folder`/`update_folder`/`delete_folder`/`_apply_folder_path_tags`/`set_paper_folder`/`set_paper_tags`）**移除 `session.commit()`**（交易邊界移交呼叫端）。
- `web_server.py` 5 端點（L1174/1193/1212/1236/1241）：`with s.begin(): f = paper_manager.<helper>(s,…)`（既有 `except ValueError → HTTPException 400` 保留：ValueError 於 begin() 內拋出 → 自動 rollback → 上拋 → 仍 400）。
- 3 測試檔（`test_paper_tags.py` / `test_normalize_tag.py` / `test_folder_auto_tags.py`）：`with SessionLocal() as s: pm.set_paper_*(s,…)` → `with s.begin():` 包裹（否則移除內部 commit 後 SessionLocal 關閉 rollback、讀回斷言失敗）。
- **原子鐵律**：helper commit 移除 + 呼叫端 + 測試三者**同一 commit**（分則測試紅燈）。

### §4.4 checkout — 成果收官歸檔
- `mv` baton plan/tasks/C1-C3 執行報告 → 正式目錄；逐檔 `git add`。
- 產 `executions/2026-07-18_SOP-COMPLY_checkout_執行.md`（Conformance 五維度 + staged 自檢 + §5 SOP 核查彙整 + §7.2 豁免）。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| 對非-except / 續行 exc_info 誤加 | 🟢 低（已界定） | C1 依 AST 25 清單逐點；守衛測試防回歸 |
| C3 移除 helper commit → 測試 rollback 失敗 | 🟡 中（已規避） | 測試 3 檔與 helper/端點**同 commit**包 `with s.begin():` |
| begin() 撞 autobegin RuntimeError | 🟡 中 | 呼叫端協調（helper 內不 begin）；C3 全套件驗 |
| DB 交易邊界改動致寫入行為變化 | 🟡 中 | 語意等價（成功 commit / 失敗自動 rollback）；§8 folder/tag/chunk 測試覆蓋 |
| 多檔改動 regression | 🟡 中 | 每 commit 全套件 pytest + §6 SOP 核查 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
./venv/bin/python -c "<AST 掃描>"   # 期望：except 內 logger.error 無 exc_info = 0（排除白名單）
grep -n "except Exception:" llm/client.py; grep -n "grounding source parse failed" llm/client.py   # 期望：:181 改 warning
./venv/bin/python -m pytest tests/test_sop_comply_guard.py -q
```

### §6.2 C2 驗收
```bash
grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"   # 期望：僅剩借用 6 處（C3 前）
grep -n "with s.begin()" paper_manager.py   # 期望：自持 7 處命中
```

### §6.3 C3 驗收
```bash
grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"   # 期望：0（全清）
grep -n "with s.begin()" web_server.py tests/test_paper_tags.py tests/test_normalize_tag.py tests/test_folder_auto_tags.py   # 期望：呼叫端+測試命中
```

### §6.4 全套件迴歸（每 commit）
```bash
./venv/bin/python -m pytest tests/ -q     # 期望：綠燈基線不退化（現 745 passed + 守衛）
```

### §6.5 §5 SOP 一致性核查（BE-Refactor·每 commit 執行報告必貼）
```bash
grep -rn "logger\.error(" <改動檔> | grep -v exc_info     # logging
grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"   # database
```

---

## §7 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] logger.error / warning 的**訊息文字語意與觸發條件**——僅增 `exc_info=True`（及 :181 改 warning）；不改控制流。
- [ ] **非-except 守衛日誌**（`rag_retriever.py:96`）+ 續行 exc_info 假陽性——不動。
- [ ] DB **寫入的業務邏輯與資料內容**——僅改交易守護包裝（commit→begin()）。
- [ ] `db.py::init_db` 正範式；SEC-SECRET / SEC-HARDEN / SEC-XSS 既有落地。
- [ ] `llm/client.py:111`（已 warning）；前端 `static/**`、DB schema、非本清帳範圍之邏輯。
- [ ] 測試斷言**期望值本體**——僅改 session 交易邊界（包 `with s.begin():`）。

---

## §8 推薦 Commit 拆分

### C1 — Logging Hardening（日誌合規補齊）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `AI_professor_chat.py` / `processor/extra_info_processor.py` / `pipeline_core.py` / `ai_core.py` / `rag_retriever.py` / `processor/rag_processor.py` / `processor/resume_processor.py` / `web_server.py` / `paper_manager.py` / `llm/client.py`（各 +`.bak`）+ `tests/test_sop_comply_guard.py`（新增）；baton C1 報告嚴禁列入 git |
| **安全性** | 🟢 高 — 純日誌參數增補 + 一處吞例外改 warning、零控制流變更 |
| **可逆性** | 🟢 高 — `git revert C1`；`.bak` |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 依 §4.1 AST 25 清單，各 `except` 內 `logger.error(msg)` 補 `, exc_info=True`（訊息不動）；② `llm/client.py:181` `except Exception: pass` → `logger.warning("grounding source parse failed", exc_info=True)`；③ 建 `tests/test_sop_comply_guard.py` AST 守衛（except 內 logger.error 皆含 exc_info）；④ 改檔先產 `.bak`；⑤ §6.1+§6.4+§6.5 貼執行報告 |

### C2 — Self-Owned Transaction Guard（自持交易守護）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `paper_manager.py`（+`.bak`）、`tests/test_sop_comply_guard.py`（選配追加 DB 守衛）；baton C2 報告嚴禁列入 |
| **安全性** | 🟢 高 — 機械式交易守護、`db.py` 已示範範式 |
| **可逆性** | 🟢 高 — `git revert C2`；`.bak` |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 無前置（與 C1 獨立） |
| **具體實作細節** | ① `paper_manager.py` 7 處自持（82/274/287/387/415/424/1055）：寫入區包 `with s.begin():`、移除顯式 `s.commit()`；② 確認 begin 區僅含寫入（無第三方 API/CPU 密集·database SOP 極短交易）；③ `.bak`；④ §6.2+§6.4+§6.5 |

### C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `paper_manager.py`（+`.bak`）、`web_server.py`（+`.bak`）、`tests/test_paper_tags.py`（+`.bak`）、`tests/test_normalize_tag.py`（+`.bak`）、`tests/test_folder_auto_tags.py`（+`.bak`）；baton C3 報告嚴禁列入 |
| **安全性** | 🟡 中 — 跨 helper/端點/測試協調；交易邊界移交呼叫端 |
| **可逆性** | 🟢 高 — `git revert C3`（原子）；`.bak` |
| **驗收 grep 條件** | 見 §6.3 |
| **依賴關係** | 前置 C2（自持先清、避免混淆剩餘 commit 計數）；**原子**：helper+端點+測試同 commit |
| **具體實作細節** | ① `paper_manager.py` 6 借用 helper（create_folder/update_folder/delete_folder/_apply_folder_path_tags/set_paper_folder/set_paper_tags）**移除 `session.commit()`**；② `web_server.py` L1174/1193/1212/1236/1241 → `with s.begin(): f = paper_manager.<helper>(s,…)`（`except ValueError → HTTPException 400` 保留）；③ `test_paper_tags.py`/`test_normalize_tag.py`/`test_folder_auto_tags.py` 之 `with SessionLocal() as s: pm.set_paper_*(s,…)` → `with s.begin():` 包裹；④ 五檔先產 `.bak`；⑤ §6.3+§6.4+§6.5（database SOP：paper_manager 裸 commit 歸零）|

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：plan → `plans/`、tasks → `tasks/`、C1-C3 + checkout 執行報告 → `executions/`；狀態：`TODO.md`（🟡→✅ 雙層結案）、`prompts/INDEX.md`（已於 tasks 登記） |
| **安全性** | 🟢 高 — 純文件搬移 + 狀態更新 |
| **可逆性** | 🟢 高 — 文件層 `git revert` / `mv` 復位 |
| **驗收 grep 條件** | baton 歸檔後僅剩既有長駐真理源；`git diff --cached --name-only` = 宣告白名單 |
| **依賴關係** | 前置 C1/C2/C3 全綠 |
| **具體實作細節** | ① 產 `executions/2026-07-18_SOP-COMPLY_checkout_執行.md`（Conformance 五維度 + staged 自檢實貼 + §5 SOP 核查彙整〔logging exc_info 全補 / paper_manager 裸 commit 歸零〕+ §7.2 純後端無 handoff 豁免）；② `mv`（**禁 `git mv`**）baton plan/tasks/C1-C3 報告；③ 逐檔顯式 `git add`（plan + tasks + 4 執行報告 + 全 `.bak` + `tests/test_sop_comply_guard.py` + `TODO.md` + `prompts/INDEX.md` + SOP-COMPLY 提示詞），**禁 `git add .`/`-A`/`<目錄>`**；④ commit 前 `git diff --cached --name-only` 自檢＝宣告清單；⑤ TODO 雙層結案；⑥ 附一行 commit 指令（baron 手動） |

---

## §9 Open Questions

無。（plan v1.1 §9 OQ1–OQ6 已於 baron review 全數拍板結案：僅 except 內補 exc_info〔AST 25〕/ 訊息保留 / 借用型方案 A 呼叫端協調+修 3 測試 / llm:181 warning / 加 grep-gate 守衛 / §7.2 豁免。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SOP-COMPLY 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 SOP-COMPLY executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務邏輯本體與 DB schema；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-18)：初版拆分完成（依 plan v1.1；4 commit＝C1 Logging Hardening〔25 exc_info + llm:181 吞例外 + grep-gate 守衛〕/ C2 Self-Owned Transaction Guard〔7 自持包 begin〕/ C3 Borrow-Session Transaction Coordination〔6 helper 移除 commit + web_server 5 端點 + 3 測試包 begin·原子〕/ checkout；每 commit §6.5 SOP 核查；§7.2 純後端豁免）
