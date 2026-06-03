# GLOSSARY-CORE C1 — Database Schema（資料庫結構與聯合唯一索引）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C1 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C1 + plan v2 §2 U1 |
| **次級參考** | database_SOP / logging_SOP / DOMAIN-NORM（domain LCC 上游） |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`1559b08`（DOC-Refactor: DOMAIN-NORM C5 — Conformance 驗收與收官歸檔）
- **完成狀態**：C1 於 `models.py` 新增 `GlobalGlossary` 表落地 worktree，import + create_all + 唯一約束實測 + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C1 | `待 baron 回填` | BE-Refactor: C1 — Database Schema（資料庫結構與聯合唯一索引） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `models.py` | +39 行（新增 `GlobalGlossary`，`=== [GLOSSARY-CORE C1 START/END] ===` 包裹） | 既有 `Paper`/`Domains`/`DomainMapping` 等表 byte 不動 |
| `.claude-logs/archive/2026-06-03_GLOSSARY-CORE_C1_models.py.bak` | 新增（改前備份） | **納入 git add**（審計存檔） |
| `.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C1_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C7 收官歸檔） |
| `.claude-logs/TODO.md` | C1→✅ / C2→🟡 WIP + DOMAIN-NORM C5 Hash 自癒（`待 baron 回填`→`1559b08`） | — |
| `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git diff --stat` 本 Commit：
```
 models.py | 39 +++++++++++++++++++++++++++++++++++++++
 1 file changed, 39 insertions(+)
```

## §4 修法說明

依 tasks §8 C1，於 `models.py`（`DomainMapping` 之後）新增 `GlobalGlossary` 表，C1 標記包裹：

```python
# === [GLOSSARY-CORE C1 START] ===
class GlobalGlossary(Base):
    __tablename__ = "global_glossaries"
    __table_args__ = (
        UniqueConstraint(
            "source_lang", "target_lang", "term_key", "domain",
            name="uq_glossary_lang_term_domain",
        ),
        Index("ix_glossary_cascade", "source_lang", "target_lang", "domain"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_lang: Mapped[str] = mapped_column(String(16), nullable=False)
    target_lang: Mapped[str] = mapped_column(String(16), nullable=False)
    term_key: Mapped[str] = mapped_column(String(255), nullable=False)
    original_term: Mapped[str] = mapped_column(Text, nullable=False)
    translation: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(16), nullable=False, default="general")
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="auto_extract")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
# === [GLOSSARY-CORE C1 END] ===
```

設計要點：
- **聯合唯一約束**：`(source_lang, target_lang, term_key, domain)` → 物理鎖死同語系同領域單詞唯一譯法（plan U1）。
- **級聯查詢輔助索引** `ix_glossary_cascade`：加速 U2 `WHERE source_lang=? AND target_lang=? AND domain IN (LCC,'general')`。
- **`source` 欄位**：`auto_extract`（管線提取）/ `manual_edit`（人工校正，plan §7 HITL）。
- **複用既有風格**：`Mapped`/`mapped_column`/`server_default=func.now()`/`UniqueConstraint`/`Index` 全對齊既有表；無新 import。
- **建表機制**：`db.py:95 create_all` 模組載入即自動建新表，無需 Alembic。

### §4.1 對 tasks §8 的合理修正（透明標註）
- tasks §8 C1 文字寫 `domain String(3)`，但**通用層代碼值 `"general"` 為 7 字元 > 3**。SQLite 不強制 VARCHAR 長度（可運作），但 PostgreSQL 會截斷致 `"general"` 損毀。故 `domain` 採 **`String(16)`** 容納 LCC(1-3) 與 `"general"` 雙語意。屬定點修正、不影響 LCC 主鍵語意；對齊 DOMAIN-NORM `DEFAULT_LCC="general"`。

## §5 測試結果

### §5.1 §6.1 grep 驗收（真實輸出節錄）
```
$ grep -nE "class GlobalGlossary|term_key|uq_glossary|UniqueConstraint" models.py
282:class GlobalGlossary(Base):
300:            "source_lang", "target_lang", "term_key", "domain",
301:            name="uq_glossary_lang_term_domain",
309:    term_key: Mapped[str] = mapped_column(String(255), nullable=False)
```

### §5.2 import + dir
```
$ venv/bin/python -c "import models; print('GlobalGlossary' in dir(models))"
True
```

### §5.3 in-memory create_all + 唯一約束實測
```
global_glossaries: True
cols: ['created_at','domain','id','original_term','source','source_lang','target_lang','term_key','translation']
unique constraints: [('uq_glossary_lang_term_domain', ['source_lang','target_lang','term_key','domain'])]
唯一約束: ✅ 生效（同 de/zh-tw/riesling/general 寫第二譯法 → IntegrityError）
```
→ 新表掛載、9 欄正確、聯合唯一約束物理生效。

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 452 passed, 3 skipped in 37.35s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json` override 預設 `auto`），與 C1（純 schema 新增）**無關**。

### §5.5 database SOP 一致性核查（WORKFLOW_SOP §5）
- C1 純 ORM schema 宣告、無 `.commit()`/session 操作（交易語意屬 C2）→ 無命中（合規）。
- logging：C1 無 logger 呼叫（無命中，合規）。

## §6 不可動清單遵守

- [x] `models.py` `Paper`/`Domains`/`DomainMapping` 等既有表 — **byte 不動**（`git diff` 僅新增區塊）。
- [x] DOMAIN-NORM `normalize_to_lcc` / `Domains` / `DomainMapping` 結構 — **未觸碰**。
- [x] `rag_retriever.py` / `tiling_processor.py` — **未觸碰**。
- [x] `translate_processor.py` / `pipeline_core.py` / `AI_professor_chat.py` — **未觸碰**（業務接入屬 C3/C4）。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-03_GLOSSARY-CORE_C1_執行.md` 暫存 baton/，待 C7 收官一次性歸檔。
- **下一步**：C2 — Glossary Core & Cascading Retrieval（新建 `processor/glossary_extractor.py`：`query_cascade`（專屬覆寫 general）+ LLM `extract_terms`（交易外）+ `upsert_terms`（INSERT OR IGNORE 冪等））。待 baron 確認 C1 後另行下達 C2 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C1_models.py.bak

# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add models.py
git add .claude-logs/archive/2026-06-03_GLOSSARY-CORE_C1_models.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_GLOSSARY-CORE_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_GLOSSARY-CORE_C1_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C1_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C1_commit_msg.txt

# 4. baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C1_commit_msg.txt
```
