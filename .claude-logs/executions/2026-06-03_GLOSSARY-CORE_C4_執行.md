# GLOSSARY-CORE C4 — Chat Injection（前台問答術語強約束注入）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C4 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C4 + plan v2 §2 U4 |
| **次級參考** | database_SOP / logging_SOP / GLOSSARY-CORE C2（GlossaryManager） |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## ⚠️ 重要：Commit 範圍隔離（baron 22:xx 拍板）

執行 C4 時發現 `AI_professor_chat.py` 工作區**在 C4 之前已存在未提交的 RAG-14 多標籤後端變更**（`parse_query_hashtag`→`parse_query_hashtags`、單標籤→多標籤聯集、`exc_info=True` 補強等；非 GLOSSARY-CORE）。
- **證據**：`.bak`（C4 改前快照）已含 `parse_query_hashtags`（1 命中）；`git show HEAD:AI_professor_chat.py` 無此符號（0 命中、HEAD 為 RAG-1 P2-2 `9ee44f3` 的單標籤版）。
- **baron 拍板**：**只 stage C4 hunks**（我提供分塊清單），RAG-14 既存改動留工作區、不入 C4 commit。
- **落實**：產出 `tmp/GLOSSARY-CORE_C4_chat.patch`（僅 import settings + L333 domain 注入兩塊）；`git apply --cached --check` 通過；dry-run 確認 staged 僅含 C4（5 命中）、**0 RAG-14**。

---

## §1 基準與完成狀態

- **基準 Commit**：`fd0e84f`（BE-Refactor: C3 — Translate Integration & Backfill）
- **完成狀態**：C4 於 `AI_professor_chat.py:329-335` 旗標閘門接入落地 worktree，旗標 ON/OFF/例外 三路徑測試 + py_compile + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C4 | `待 baron 回填` | BE-Refactor: C4 — Chat Injection（前台問答術語強約束注入） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `AI_professor_chat.py` | C4 兩塊：`import settings` + L333 domain 注入段旗標閘門（C4 標記包裹） | **僅 C4 hunks 入 commit**（RAG-14 既存改動隔離、不 stage） |
| `tmp/GLOSSARY-CORE_C4_chat.patch` | C4-only patch（baron 用以精準 stage） | tmp/ untracked、不入 git |
| `.claude-logs/archive/2026-06-03_GLOSSARY-CORE_C4_AI_professor_chat.py.bak` | 改前工作區快照（**含既存 RAG-14**，屬實況存檔） | **納入 git add** |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C4_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C4→✅ / C5→🟡 WIP + C3 Hash 自癒（`待 baron 回填`→`fd0e84f`） | — |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C4_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

> **`.bak` 註記**：依 `.bak` 鐵律「改既有檔前備份工作區」，故快照含當時工作區既有的 RAG-14 改動；此為 C4 改前實況、非 C4 產物。C4 commit 本身僅含 C4 兩塊。

## §4 修法說明

### §4.1 `AI_professor_chat.py` 旗標閘門 Chat 術語注入（C4 標記包裹）
`import settings` + L329-335 `if domain:` 區塊改為：
```python
# === [GLOSSARY-CORE C4 START] ===
glossary_block = ""
if settings.LLM_USE_GLOSSARY_ALIGN:
    try:
        from processor.glossary_extractor import GlossaryManager
        glossary = GlossaryManager().query_cascade('en', 'zh-tw', domain)
        if glossary:
            term_lines = "\n".join(f"- {o} → {t}" for o, t in glossary.items())
            glossary_block = ("\n\n【術語強約束 System constraint】以下專有名詞譯法不可違背，"
                              f"回答時必須與論文譯本完全一致：\n{term_lines}")
    except Exception:
        self.logger.error("[glossary] Chat 術語注入失敗，降級回原行為", exc_info=True)
        glossary_block = ""
character_prompt = character_prompt + f"\n\n當前文件主題：{domain}" + glossary_block
explain_prompt = explain_prompt + f"\n\n當前文件主題：{domain}" + glossary_block
# === [GLOSSARY-CORE C4 END] ===
```
- **旗標 OFF（預設）→ `glossary_block=""`**：`+ f"\n\n當前文件主題：{domain}" + ""` 與既有單行 **byte 等價**。
- **旗標 ON + 命中 → 注入「術語強約束 System constraint」**。
- **前台崩潰防護**：`query_cascade` 單獨 `try/except` graceful degradation——任何 DB 異常僅 `logger.error(exc_info=True)`、`glossary_block` 保持空、退回舊行為，**絕不讓 DB 異常崩潰/阻斷前台問答**。
- 不動 `messages` 組裝（L338）與下游核心。

## §5 測試結果

### §5.1 §6.4 grep 驗收（真實輸出節錄）
```
AI_professor_chat.py:8:import settings  # GLOSSARY-CORE C4
AI_professor_chat.py:342:                if settings.LLM_USE_GLOSSARY_ALIGN:
AI_professor_chat.py:345:                        glossary = GlossaryManager().query_cascade('en', 'zh-tw', domain)
```

### §5.2 py_compile 語法檢查
```
$ venv/bin/python -m py_compile AI_professor_chat.py
compile OK
```

### §5.3 旗標 ON/OFF/例外 三路徑功能測試（_prepare_final_messages、bypass __init__）
```
OFF 含當前文件主題: True | 無術語約束: True          # 旗標 OFF: byte 等價舊行為
ON 含術語約束: True | riesling→雷司令: True           # 旗標 ON + 命中: 注入術語約束
例外降級 含主題: True | 無術語約束(降級): True         # ON + DB 例外: graceful degradation 不崩
ALL OK
```
- 例外路徑印出的 traceback 為 `logger.error(..., exc_info=True)` 的**合規日誌輸出**，方法正常返回降級結果、**未崩潰**。

### §5.4 Commit 範圍隔離驗證（C4-only patch）
```
$ git apply --cached --check tmp/GLOSSARY-CORE_C4_chat.patch        → ✅ 通過
$ git apply --cached ... ; git diff --cached 命中：C4=5 / RAG-14=0  → ✅ 僅 C4
$ git reset -q AI_professor_chat.py                                 → index 還原 HEAD、工作區未動
```

### §5.5 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 45.78s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C4 無關。

### §5.6 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：C4 區無裸 commit（查詢走 GlossaryManager.query_cascade 唯讀）→ 無命中（合規）。
- **logging §5.1**：C4 區 `self.logger.error("[glossary] Chat 術語注入失敗...", exc_info=True)` → 合規。

## §6 不可動清單遵守

- [x] `AI_professor_chat.py` `messages` 組裝（L338）與下游問答核心 — **未動**。
- [x] 旗標閘門**以外**既有 domain 注入邏輯 — 旗標 OFF byte 等價（§5.3 證實）。
- [x] **RAG-14 既存未提交改動 — 隔離不入 C4 commit**（§ Commit 範圍隔離 + §5.4 驗證）。
- [x] `models.py` / `glossary_extractor.py` / `translate_processor.py` / `pipeline_core.py` — **未觸碰**。
- [x] `rag_retriever.py` / `tiling_processor.py` / `normalize_to_lcc` — **未觸碰**。
- [x] 改前 `.bak` 已備。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_GLOSSARY-CORE_C4_執行.md` 暫存 baton/，連同 C1/C2/C3 報告 + plan_v2 + tasks 待 C7 收官一次性歸檔。
- **下一步**：C5 — Hot-Pluggable CLI：新建 `tools/manage_glossary.py`（`--init` / `--test-pipeline --pdf` / `--backfill-existing-papers`）。待 baron 確認 C4 後另行下達。

## §8 baron 執行命令

> ⚠️ **本 Commit 採「只 stage C4 hunks」**（baron 拍板）：`AI_professor_chat.py` 含 C4 之前既存的 RAG-14 多標籤改動，**不可**整檔 `git add`。改用 C4-only patch 精準 stage。

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C4_AI_professor_chat.py.bak

# 2. 精準 stage 僅 C4 兩 hunk（不含 RAG-14；已驗 git apply --cached --check 通過）
git apply --cached tmp/GLOSSARY-CORE_C4_chat.patch
#   驗證：git diff --cached AI_professor_chat.py | grep -c "GLOSSARY-CORE C4"  → 應為 5
#         git diff --cached AI_professor_chat.py | grep -c "parse_query_hashtags" → 應為 0
#   （備援手動法：git add -p AI_professor_chat.py，僅對 import settings 與 GLOSSARY-CORE C4
#     domain 注入兩塊回答 y，對 parse_query_hashtags 等 RAG-14 hunk 回答 n）

# 3. 其餘檔案明確列檔（baton/ 報告不入 git）
git add .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C4_AI_professor_chat.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C4_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C4_執行.md 暫留 baton/，不 add）
# （RAG-14 既存改動留工作區、不 stage、由 baron 後續另行處理）

# 4. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C4_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C4_commit_msg.txt

# 5. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C4_commit_msg.txt
```
