# TRANSLATOR C1 — Contract & Context（合約與上下文模型）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | TRANSLATOR C1 |
| **執行日期** | 2026-06-04 |
| **依據規劃** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` §8 C1 |
| **次級參考** | plan v10 §2 U1 / PIPE-SPEC §1.2.3 v3 + §1.1② / PIPE-CORE contracts.py |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`ec32bcb`（docs: archive developer prompts and logs）
- **完成狀態**：C1 新建 `processor/translator.py`（InjectionContext + TranslateMode）+ `pipelines/contracts.py::GlossaryReadySpec` 補 domain_name，落地 worktree，import + frozen/forbid 行為 + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C1 | `待 baron 回填` | BE-Refactor: C1 — Contract & Context（合約與上下文模型） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/translator.py` | **新建**（~48 行：InjectionContext 7 欄 frozen+forbid + TranslateMode） | 純新增、未接線 |
| `pipelines/contracts.py` | `GlossaryReadySpec` 補 `domain_name: Optional[str]=None`（`=== [TRANSLATOR C1 START/END] ===` 包裹） | 既有三合約 byte 不動 |
| `.claude-logs/archive/2026-06-04_TRANSLATOR_C1_contracts.py.bak` | 新建（改前備份） | **納入 git add** |
| `.claude-logs/baton/2026-06-04_TRANSLATOR_C1_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C1→✅ / C2→🟡 WIP + GLOSSARY-CORE C5/C7 Hash 自癒（`待 baron 回填`→`7da39bd`/`d4c34d5`） | — |
| `.claude-logs/prompts/2026-06-04_TRANSLATOR_C1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
 M pipelines/contracts.py
?? processor/translator.py
```

## §4 修法說明

### §4.1 `processor/translator.py`（新建、InjectionContext/TranslateMode 落點）
```python
class TranslateMode(str, Enum):
    NORMAL = "normal"
    DEEP_THINK = "deep_think"

class InjectionContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    lcc: str
    glossary: Dict[str, str]
    zh_summary: Optional[str] = None
    preceding: Optional[str] = None
    constraints: List[str] = []
    domain_name: Optional[str] = None   # LCC 領域英文名（=Domains.name）
    doc_type: Optional[str] = None
```
- 七欄逐字對齊 **PIPE-SPEC §1.2.3 v3**；`text_type`（本次呼叫屬性）為 translate() 獨立參數、**不入合約**。
- **落 `processor/translator.py`**（非 `pipelines/contracts.py`）——遵 plan F 缺口決議，避違 contracts.py「不含 doc_type 業務細節」docstring 與「四份 Phase 合約」範疇。

### §4.2 `pipelines/contracts.py::GlossaryReadySpec` 補 domain_name（C1 標記包裹）
```python
    chapter_summaries: Optional[List[str]] = None
    # === [TRANSLATOR C1 START] ===
    # P2→P3 凍結載體：P2 一次性 lcc→Domains.name 唯讀解析的領域英文名 ...
    domain_name: Optional[str] = None
    # === [TRANSLATOR C1 END] ===
```
- 對齊 **PIPE-SPEC §1.1② v3**；`Optional`+預設 None → **向後相容**（既有建構不傳此欄不受影響）。其他三合約（Ingestion/Bilingual/RagDb）byte 不動。

## §5 測試結果

### §5.1 §6.1 grep 驗收（真實輸出節錄）
```
$ grep -nE "class InjectionContext|class TranslateMode|frozen=True|extra=.forbid|domain_name|doc_type" processor/translator.py
21:class TranslateMode(str, Enum):
32:class InjectionContext(BaseModel):
39:    model_config = ConfigDict(frozen=True, extra="forbid")
46:    domain_name: ...
47:    doc_type: ...
$ grep -n "domain_name" pipelines/contracts.py   → 命中
```

### §5.2 import + 行為驗證（frozen / forbid / 7 欄 / GlossaryReadySpec）
```
TranslateMode: normal deep_think
7 欄位: ['constraints','doc_type','domain_name','glossary','lcc','preceding','zh_summary']
frozen: ✅ 不可變
forbid: ✅ 拒絕未定義欄位（text_type 不入合約）
GlossaryReadySpec domain_name: True
domain_name 預設 None: True
ALL OK
```

### §5.3 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 457 passed, 3 skipped in 43.07s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C1 無關。
- 457 passed 含全部 PIPE-CORE contracts / pipelines 測試，證明 `GlossaryReadySpec` 補 Optional 欄位零破壞。

### §5.4 database SOP 核查
- C1 純型別/合約宣告、無 `.commit()`/session 操作 → 無命中（合規）。

## §6 不可動清單遵守

- [x] A 軌 `pipeline_core.py` / `processor/translate_processor.py` — **未觸碰**。
- [x] `llm/client.py` `_api_semaphore`/retry — **未觸碰**（thinking_config 屬 C3）。
- [x] `models.py` Schema / `Domains` 表 — **未觸碰**。
- [x] `prompt/translate/` 既有檔 — **未觸碰**（caption 屬 C2）。
- [x] PIPE-CORE 其餘三合約（Ingestion/Bilingual/RagDb）— **byte 不動**（僅 GlossaryReadySpec 補欄位）。
- [x] DOMAIN-NORM/GLOSSARY-CORE — **未觸碰**。
- [x] 主 repo 目錄 — 未讀寫；baton/ 報告留暫存、未提前 mv/git add。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-04_TRANSLATOR_C1_執行.md` 暫存 baton/、**不入版控**，待 C5 收官一次性歸檔。
- **下一步**：C2 — Prompt Engine（`Translator` 系統提示詞五步 + 用戶提示詞 + 新建 `caption_translate_prompt.txt`）。待 baron 確認 C1 後另行下達 C2 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-04_TRANSLATOR_C1_contracts.py.bak

# 2. git add 清單（明確列檔、baton/ 報告不入 git）
git add processor/translator.py
git add pipelines/contracts.py
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C1_contracts.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-04_TRANSLATOR_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-04_TRANSLATOR_C1_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/TRANSLATOR_C1_msg.txt）
cat /tmp/TRANSLATOR_C1_msg.txt

# 4. baron 手動執行
git commit -F /tmp/TRANSLATOR_C1_msg.txt
```
