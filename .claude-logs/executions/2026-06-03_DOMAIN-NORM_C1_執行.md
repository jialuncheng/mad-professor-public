# DOMAIN-NORM C1 — Database Schema（資料庫表建立）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOMAIN-NORM C1 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` §8 C1 |
| **次級參考** | plan v2 §2 U2 / database_SOP / PIPE-SPEC §1.2.1 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`703cfaa`（DOC-Refactor: API-PERF C6 — Conformance 驗收與收官歸檔）
- **完成狀態**：C1 代碼修改已落地 worktree，pytest 驗證通過（除既有環境性失敗 1 項），**未 commit / 未 push**（待 baron 手動）。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C1 | `待 baron 回填` | BE-Refactor: DOMAIN-NORM C1 — Database Schema (資料庫表建立) |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `models.py` | +52 行（新增 `Domains` + `DomainMapping` 兩表，`=== [DOMAIN-NORM C1 START/END] ===` 包裹） | 既有 `Paper` 等表 byte 不動 |
| `.claude-logs/archive/2026-06-03_DOMAIN-NORM_C1_models.py.bak` | 新增（改前備份） | 納入 git add（審計存檔） |
| `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C1_執行.md` | 本報告 | **暫存 baton/，不入 git**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C1→✅ / C2→🟡 WIP + C6 Hash 自癒（`待 baron 回填`→`703cfaa`） | — |
| `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git diff --stat` 本 Commit 相關：
```
 models.py | 52 ++++++++++++++++++++++++++++++++++++++++++++++++++++
```

## §4 修法說明

依 tasks §8 C1 具體實作細節，於 `models.py` 末尾（`PaperChunk` 之後）新增兩 ORM 表，並以 C1 包裝標記框住，便於後續審計：

```python
# === [DOMAIN-NORM C1 START] ===
class Domains(Base):
    __tablename__ = "domains"
    lcc_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    mappings: Mapped[list["DomainMapping"]] = relationship(
        back_populates="domain", passive_deletes=True
    )


class DomainMapping(Base):
    __tablename__ = "domain_mappings"
    __table_args__ = (Index("ix_domain_mappings_lcc_code", "lcc_code"),)
    raw_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    lcc_code: Mapped[str] = mapped_column(
        ForeignKey("domains.lcc_code", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    domain: Mapped["Domains"] = relationship(back_populates="mappings")
# === [DOMAIN-NORM C1 END] ===
```

設計要點：
- **`Domains`**：`lcc_code` PK（String(3)，對齊 plan §7 Q2 LCC 1-3 字元硬限）+ `name`；docstring 明示「僅存領域空間、嚴禁塞術語/單字」（plan v2 U2 鐵律，與 GLOSSARY-CORE 物理隔離）。
- **`DomainMapping`**：`raw_key` PK（存 lowercase+strip 正規化後的 raw）+ `lcc_code`（FK→domains.lcc_code，`ondelete="RESTRICT"` 防孤兒）+ 索引；快取命中 0ms/零 API。
- **複用既有風格**：`Mapped`/`mapped_column`/`server_default=func.now()`/`relationship` 全對齊既有四表慣例；無新 import。
- **建表機制**：`db.py:95 Base.metadata.create_all(bind=engine)` 模組載入即自動建新表，無需 Alembic（對齊 db.py:7 註解「首版 schema，無需 Alembic」）。

## §5 測試結果

### §5.1 §6.1 grep 驗收（真實輸出）
```
$ grep -nE "class Domains|class DomainMapping|lcc_code" models.py
230:class Domains(Base):
234:    - lcc_code: Library of Congress Classification 代碼（1-3 字母，PK）...
244:    lcc_code: Mapped[str] = mapped_column(String(3), primary_key=True)
255:class DomainMapping(Base):
260:    - lcc_code: 該 raw 對齊到的 LCC 代碼（FK → domains.lcc_code）。
266:        Index("ix_domain_mappings_lcc_code", "lcc_code"),
270:    lcc_code: Mapped[str] = mapped_column(
271:        ForeignKey("domains.lcc_code", ondelete="RESTRICT"), nullable=False
```

### §5.2 python import + dir 檢測
```
$ venv/bin/python -c "import models; print('Domains' in dir(models), 'DomainMapping' in dir(models))"
True True
```

### §5.3 in-memory create_all 新表掛載驗證
```
$ venv/bin/python -c "<create_all sqlite:///:memory: + inspect>"
tables: ['conversations', 'domain_mappings', 'domains', 'folders', 'paper_chunks', 'papers', 'users']
domains: True | domain_mappings: True
domains cols: ['created_at', 'lcc_code', 'name']
domain_mappings cols: ['created_at', 'lcc_code', 'raw_key']
```
→ 新表成功掛載；既有 6 表（users/papers/folders/conversations/paper_chunks + 新 domains/domain_mappings）齊全。

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 448 passed, 3 skipped in 38.01s
```
- 唯一失敗 `tests/test_logging_config.py::test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json` override 預設 `auto`），與 C1（純 models.py schema 新增）**無關**，非本次迴歸。
- 448 passed 含全部 models / DB 相關測試，證明 C1 對既有 schema 零破壞。

### §5.5 database SOP 一致性核查（WORKFLOW_SOP §5）
- C1 純 ORM schema 宣告，**無任何 `.commit()` / `session` 操作**（交易語意屬 C2）。
```
$ grep -nE "\.commit\(\)" models.py | grep -v "with .*session.*begin\(\)"
（無命中，合規）
```
- logging 核查：C1 無 logger 呼叫（無命中，合規）。

## §6 不可動清單遵守

- [x] `processor/domain_detector.py` `detect` — **未觸碰**。
- [x] `models.py` `Paper` 表既有主欄位與關係 — **byte 不動**（`git diff` 僅新增區塊，無既有行變更）。
- [x] `rag_retriever.py` — **未觸碰**。
- [x] `processor/translate_processor.py` — **未觸碰**。
- [x] 主 repo 目錄（worktree 父目錄）— **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-03_DOMAIN-NORM_C1_執行.md` 暫存 baton/，連同 plan_v2 / tasks 待 C5 收官一次性歸檔。
- **下一步**：C2 — Normalizer Core（`processor/domain_normalizer.py`：快取查→LLM 收斂 Temp=0.0→動態註冊 INSERT OR IGNORE→寫回；LLM 呼叫須在 DB 交易外）。待 baron 確認 C1 後另行下達 C2 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-03_DOMAIN-NORM_C1_models.py.bak

# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add models.py
git add .claude-logs/archive/2026-06-03_DOMAIN-NORM_C1_models.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_DOMAIN-NORM_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_DOMAIN-NORM_C1_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/DOMAIN-NORM_C1_msg.txt）
cat /tmp/DOMAIN-NORM_C1_msg.txt

# 4. baron 手動執行
git commit -F /tmp/DOMAIN-NORM_C1_msg.txt
```
