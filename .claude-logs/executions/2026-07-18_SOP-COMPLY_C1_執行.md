# SOP-COMPLY C1 — Logging Hardening（日誌合規補齊）執行報告

> **任務代號**：SOP-COMPLY C1
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C1)
> **落地 Git Hash**：`98f8848`（baron 已 ship·hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md §8 C1` / plan v1.1 §2 #1·#2（OQ1/OQ2/OQ4/OQ5）
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`e287347`（BE-Refactor: SEC-HARDEN checkout — 成果收官歸檔）、分支 `gemini-refactor`。
- **完成狀態**：C1 代碼修改 + 守衛測試全數完成、全套件 **748 passed / 3 skipped / 0 failed**（基線 745 + 新增 3 守衛）；**未 commit / 未 push**（依 CLAUDE.md §1.3 由 baron 手動執行）。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Logging Hardening：9 檔 25 處 except 內 `logger.error` 補 `exc_info=True` + `llm/client.py:181` 吞例外改 warning + AST 守衛測試 | `98f8848` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 補點數 |
|---|---|---|
| `AI_professor_chat.py` | 修改 | 5（L39/214/275/300/315） |
| `processor/extra_info_processor.py` | 修改 | 5（L127/371/472/509/602） |
| `pipeline_core.py` | 修改 | 4（L358/359/410/411） |
| `ai_core.py` | 修改 | 3（L37/91/120） |
| `rag_retriever.py` | 修改 | 3（L89/108/268） |
| `paper_manager.py` | 修改 | 2（L45/55） |
| `processor/rag_processor.py` | 修改 | 1（L519） |
| `processor/resume_processor.py` | 修改 | 1（L166） |
| `web_server.py` | 修改 | 1（L195·broker DB append·即 SEC-HARDEN 期已標之既有債） |
| `llm/client.py` | 修改 | `:181` `except Exception: pass` → `logging.getLogger(__name__).warning("grounding source parse failed", exc_info=True)` |
| `tests/test_sop_comply_guard.py` | 新增 | 3 守衛測試（AST 全域掃描 / 掃描範圍自檢 / grounding 不吞例外） |
| 10 個 `.bak` | 新增（備份） | `.claude-logs/archive/2026-07-18_SOP-COMPLY_C1_*.bak`（上列 10 檔修改前備份·入 git 審計） |
| `.claude-logs/TODO.md` | 修改 | C1 → ✅、C2 → 🟡 WIP、SEC-HARDEN checkout hash 自癒 `e287347` |
| `.claude-logs/prompts/2026-07-18_SOP-COMPLY_C1_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SOP-COMPLY 分類節（補 plan/tasks 條目）+ 時間列剔舊 |

**baton 暫存（嚴禁 git add）**：本執行報告、plan v1、tasks。

`git diff --stat`（業務碼部分·實貼）：

```
 AI_professor_chat.py              | 10 +++++-----
 ai_core.py                        |  6 +++---
 llm/client.py                     |  6 +++++-
 paper_manager.py                  |  4 ++--
 pipeline_core.py                  |  8 ++++----
 processor/extra_info_processor.py | 10 +++++-----
 processor/rag_processor.py        |  2 +-
 processor/resume_processor.py     |  2 +-
 rag_retriever.py                  |  6 +++---
 web_server.py                     |  2 +-
```

---

## §4 真因與修法

### §4.1 真因

- **(A)**：9 檔共 25 處 `except` 區塊內 `logger.error(...)` 未帶 `exc_info=True` → traceback 丟棄、生產除錯僅剩單行 `str(e)`（logging SOP §3 違規·PROJECT-REVIEW 程式碼品質 #1）。AST 精確清單（排除 14 處續行 exc_info 假陽性 + `rag_retriever.py:96` 非-except 守衛）。
- **(B)**：`llm/client.py:181` `_collect_sources` 之 `except Exception: pass` → grounding 來源解析失敗**靜默**丟棄、零日誌。

### §4.2 修法

**(A) 機械補丁（AST end-position 位元組精確插入·訊息文字與控制流零動）**：對 25 處呼叫於收尾 `)` 前插入 `, exc_info=True`（多行呼叫落於末行、trailing-comma 防護）。樣例（`ai_core.py`）：

```diff
-            self.logger.error(f"初始化 RAG 檢索器失敗: {str(e)}")
+            self.logger.error(f"初始化 RAG 檢索器失敗: {str(e)}", exc_info=True)
```

**(B) 吞例外根除（OQ4：warning 不中斷串流·沿用檔內 `:112` 既有風格）**：

```python
                except Exception:
                    logging.getLogger(__name__).warning(
                        "grounding source parse failed", exc_info=True
                    )
```

**(C) grep-gate 守衛（OQ5）**：`tests/test_sop_comply_guard.py` 三測試——① AST 全域掃描（頂層 + processor/ + llm/ + pipelines/ + utils/）斷言 except 內 `logger.error` 違規清單為空；② 掃描範圍自檢（10 檔皆在涵蓋內、防 glob 失效空轉）；③ `_collect_sources` except 區非裸 pass + warning 訊息存在。

### §4.3 範圍外發現（不動·提請 baron）

全域 AST 掃描另見 **`tools/regen_rag.py:252`** 一處 except 內 `logger.error` 無 exc_info——`tools/` 非 plan v1.1 清帳範圍（9 檔清單外、git add 清單無此檔）→ **不動**；守衛測試明文排除 `tools/` 並註記此已知債，是否清理由 baron 另行決定（可併 checkout 前小尾巴或另案）。

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.1 驗收（實貼）

```
$ <AST 掃描·頂層+processor/+llm/+pipelines/+utils/>
違規: 0（全清）

$ grep -n "except Exception:" llm/client.py
111:                except Exception:          ← 既有 warning（不在範圍·不動）
181:                except Exception:          ← 本次修補
$ grep -n "grounding source parse failed" llm/client.py
185:                        "grounding source parse failed", exc_info=True

$ ./venv/bin/python -m pytest tests/test_sop_comply_guard.py -q
...                                                                      [100%]
3 passed in 0.09s
```

### §5.2 全套件（實貼）

```
$ ./venv/bin/python -m pytest tests/ -q
748 passed, 3 skipped, 3 warnings in 54.60s
```

基線 745 passed → **748 passed**（+3 守衛）、0 failed、綠燈不退化。

### §5.3 §6.5 SOP 一致性核查（實貼）

```
$ grep -rn "logger\.error(" <10 改動檔> | grep -v exc_info
AI_professor_chat.py:133 / :356          ← 多行呼叫·exc_info 於續行（既有合規）
rag_retriever.py:96                      ← 非-except 守衛日誌（OQ1 白名單·不動）
rag_retriever.py:139 / rag_processor.py:277/:296 / pipeline_core.py:411/:729 /
web_server.py:175/:195/:806              ← 多行呼叫起始行·exc_info 於末行（AST 實證 0 違規；
                                            其中 :195/:411 為本次補齊、exc_info 落於呼叫末行）

$ grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"
82/274/287/387/415/424/1055（自持 7）+ 582/623/638/724/748/844（借用 6）
```

**判定**：logging——except 區違規 **AST 實證歸零**、單行 grep 殘餘全數為續行假陽性/白名單（守衛測試長駐防回歸）；database——13 裸 commit 原樣（**依拆分屬 C2/C3 範圍**、本 commit 零 DB 改動）。

---

## §6 不可動清單遵守狀態

- [x] **訊息文字語意與控制流零動**——機械插入 `exc_info=True` 於呼叫收尾（diff 抽查實證）；唯一控制流變更＝`:181` pass→warning（tasks 明定）。
- [x] **非-except 守衛日誌不動**——`rag_retriever.py:96` 原樣（grep 實證）；14 處續行 exc_info 假陽性零觸碰。
- [x] **`llm/client.py` 僅動 `:181`**——`:111` 既有 warning 原樣；該檔 diff 僅 `_collect_sources` except 區 6 行。
- [x] DB 寫入邏輯 / `db.py::init_db` / 前端 / DB schema——零觸碰（13 裸 commit 留 C2/C3）。
- [x] SEC-SECRET / SEC-HARDEN / SEC-XSS 既有落地——零觸碰（`test_sec_harden.py` 30 測試續綠）。
- [x] 測試斷言期望值本體——零觸碰（本 commit 未動任何既有測試檔）。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / 本 C1 報告均留 `baton/` 暫存、未 mv 未 git add（收官鐵律遵守）。
- **TODO.md**：C1 → ✅、C2 → 🟡 WIP。
- **歷史 Hash 自癒掃描（雙源）**：`git log` 實證 **SEC-HARDEN checkout 已 ship＝`e287347`** → TODO 索引行 + `archive/TODO_done_archive.md` checkout 佔位符雙源回填；**全庫 `待 baron 回填` 歸零**。
- **下一步**：等 baron 確認 C1 並 commit 後，下達 **C2 — Self-Owned Transaction Guard（自持交易守護·paper_manager 7 處包 `with s.begin():`）** 提示詞。
- **範圍外債留檔**：`tools/regen_rag.py:252`（§4.3·baron 拍板是否清理）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 10 個 .bak）

# 2. git add 清單（僅本次 C1 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add AI_professor_chat.py
git add processor/extra_info_processor.py
git add pipeline_core.py
git add ai_core.py
git add rag_retriever.py
git add processor/rag_processor.py
git add processor/resume_processor.py
git add web_server.py
git add paper_manager.py
git add llm/client.py
git add tests/test_sop_comply_guard.py
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_AI_professor_chat.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_extra_info_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_pipeline_core.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_ai_core.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_retriever.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_resume_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_paper_manager.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_client.py.bak

# 3. commit message 草稿（已寫入 /tmp/SOP-COMPLY_C1_msg.txt）
cat > /tmp/SOP-COMPLY_C1_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY C1 — Logging Hardening（日誌合規補齊）

1. 補齊 9 檔業務程式碼 except 區內共計 25 處 logger.error 的 exc_info=True 參數，以完整保留異常 traceback。
2. 修改 llm/client.py:181 處對 grounding 來源解析的 exception 靜默吞例外，改為 logging.warning(..., exc_info=True) 留痕降級。
3. 建立 tests/test_sop_comply_guard.py，利用 AST 靜態掃描確保全域 except 塊內的 logger.error 接合 exc_info，作為 Grep-gate 防回歸測試。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SOP-COMPLY_C1_msg.txt
```
