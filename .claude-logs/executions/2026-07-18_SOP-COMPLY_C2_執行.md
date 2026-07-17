# SOP-COMPLY C2 — Self-Owned Transaction Guard（自持交易守護）執行報告

> **任務代號**：SOP-COMPLY C2
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C2)
> **落地 Git Hash**：`68987e8`（baron 已 ship·hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md §8 C2` / plan v1.1 §2 #3（自持型）
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`e287347`（SEC-HARDEN checkout）、分支 `gemini-refactor`。**⚠️ C1 尚未 ship**——工作區同時含 C1（10 檔）與 C2（`paper_manager.py`）變更、兩者共檔 `paper_manager.py` → **分次 commit 序列見 §8（必讀）**。
- **完成狀態**：C2 代碼修改完成、全套件 **748 passed / 3 skipped / 0 failed**（C1 後基線持平、零退化）；**未 commit / 未 push**。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Self-Owned Transaction Guard：`paper_manager.py` 7 處自持型 session 包 `with s.begin():`、移除顯式 `s.commit()` | `68987e8` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `paper_manager.py` | 修改 | 7 處自持型交易守護（`ensure_admin` L74 / `upsert_paper` L247 / `delete_paper` L284 / `append_chat_message` L385 / `save_chat_history` L405 / `delete_conversations` L424 / `replace_paper_chunks` L1049·改後行號） |
| `.claude-logs/archive/2026-07-18_SOP-COMPLY_C2_paper_manager.py.bak` | 新增（備份） | 修改前備份（＝**C1 完成態快照**·分次 staging 關鍵·§8）·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C2 → ✅、C3 → 🟡 WIP |
| `.claude-logs/prompts/2026-07-18_SOP-COMPLY_C2_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SOP-COMPLY 分類節追加 |

**baton 暫存（嚴禁 git add）**：本執行報告、C1 執行報告、plan v1、tasks。

`git diff --stat`（實貼·C2 部分）：

```
 paper_manager.py | 58 ++++++++++++++++++++++++++++----------------------------
 1 file changed, 29 insertions(+), 29 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因

`paper_manager.py` 7 處自持型 session（`with db.SessionLocal() as s: … s.commit()`）無 rollback 守護——中途例外時交易懸置 / 半寫風險（database SOP 原則 3 違規）。

### §4.2 修法（比照 `db.py::init_db` 正範式·防 autobegin 衝突）

**5 處直改複合 with**（body 無 commit 後讀取）——`upsert_paper` / `delete_paper` / `save_chat_history` / `delete_conversations` / `replace_paper_chunks`：

```python
    with db.SessionLocal() as s, s.begin():
        ...寫入區（顯式 s.commit() 移除）...
```

**2 處內層 begin + 後讀外移**（body 有 commit 後屬性讀取）：

- `ensure_admin`：`created` 旗標讓 log（含 commit 後才有的 `u.id`）移出交易區：

```python
    with db.SessionLocal() as s:
        with s.begin():
            u = s.query(User).filter_by(...).one_or_none()
            created = u is None
            if created:
                u = User(...)
                s.add(u)
        if created:
            logger.info(f"建立 admin user: {u.username} (id={u.id})")
        return (u.id, u.username)
```

- `append_chat_message`：`cid = c.id` 移至 begin 區後（session 內·expire-on-commit 自動 refresh）。

**設計要點**：① `s.begin()` 一律置於 session 起始、query 之前——避免 SQLAlchemy 2.0 autobegin（先 query 再 begin 會 `InvalidRequestError`·plan §5 風險已規避）；② begin 區僅含 DB 讀寫（重活如 upsert 的 title 解析 / json.dumps 本就在 session 外·極短交易原則）；③ commit 後屬性讀取（`u.id`/`c.id`）留在 session 內、行為等價；④ 成功自動 commit / 失敗自動 rollback＝語意更安全非改變。

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.2 驗收 grep（實貼）

```
$ grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"
583/624/639/725/749/845    ← 恰為借用型 6 處（C3 原子範圍·本 commit 嚴禁動）

$ grep -n "with s.begin()\|with db.SessionLocal() as s, s.begin()" paper_manager.py
74 / 247 / 284 / 385 / 405 / 424 / 1049    ← 自持 7 處全命中
```

### §5.2 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/ -q
748 passed, 3 skipped, 3 warnings in 52.66s
```

C1 後基線 748 passed → **748 passed**、0 failed、零退化（folder/tag/chunk/chat 寫入測試全數續綠＝交易守護行為等價實證）。

### §5.3 §6.5 SOP 一致性核查（實貼）

```
$ grep -rn "logger\.error(" paper_manager.py | grep -v exc_info
無命中（合規）

$ grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"
583/624/639/725/749/845（僅剩借用 6·依拆分屬 C3）
```

---

## §6 不可動清單遵守狀態

- [x] **僅改 7 處自持型**——diff 29+/29- 全落於 7 函式之交易包裝；寫入業務邏輯與資料內容 byte 級等價（僅包裝與 commit 移除、`ensure_admin`/`append_chat_message` 之後讀外移屬等價重排）。
- [x] **借用型 6 處零觸碰**——`session.commit()` L583/624/639/725/749/845 原樣（grep 實證·C3 原子範圍）。
- [x] `db.py::init_db` 正範式 / web_server 呼叫端 / 3 測試檔——零觸碰。
- [x] 前端 `static/**`、DB schema——零觸碰。
- [x] SEC-* 既有落地 + C1 落地（exc_info L45/55 含於檔內、未動）——零觸碰。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / C1 報告 / 本 C2 報告均留 `baton/` 暫存。
- **TODO.md**：C2 → ✅、C3 → 🟡 WIP。
- **歷史 Hash 自癒掃描（雙源）**：`git log` HEAD 仍 `e287347`——**C1 尚未 ship**（C1 hash 註記維持「待 baron ship」）；雙源 `待 baron 回填` 佔位符 **0**（前輪已全清）。
- **下一步**：baron 依 §8 序列 ship C1 → C2 後，下達 **C3 — Borrow-Session Transaction Coordination（原子：6 helper 移除 commit + web_server 5 端點 + 3 測試檔包 begin）** 提示詞。

---

## §8 baron 執行命令（⚠️ C1/C2 共檔分次 commit 序列·必依序）

> **背景**：C1 未 ship、C1（exc_info L45/55）與 C2（交易守護）都改了 `paper_manager.py`——現行工作區該檔＝C1+C2 疊加態。直接跑 C1 的 `git add paper_manager.py` 會把 C2 混入 C1 commit（違反原子性）。**C2 的 `.bak` 恰為 C1 完成態快照**、用它分離 staging：

```bash
# ── Step 0：保存 C2 完成態（現行工作區版本）──
cp paper_manager.py /tmp/SOP-COMPLY_pm_after_C2.py

# ── Step 1：ship C1（paper_manager 還原至 C1 完成態再 add）──
cp .claude-logs/archive/2026-07-18_SOP-COMPLY_C2_paper_manager.py.bak paper_manager.py
# （執行 C1 報告 §8 之 git add 清單：10 業務檔 + tests/test_sop_comply_guard.py + 10 個 C1 .bak）
git commit -F /tmp/SOP-COMPLY_C1_msg.txt

# ── Step 2：ship C2（回到 C2 完成態）──
cp /tmp/SOP-COMPLY_pm_after_C2.py paper_manager.py
git add paper_manager.py
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C2_paper_manager.py.bak

# commit message 草稿（已寫入 /tmp/SOP-COMPLY_C2_msg.txt）
cat > /tmp/SOP-COMPLY_C2_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY C2 — Self-Owned Transaction Guard（自持交易守護）

1. 將 paper_manager.py 中的 7 處自持型 Session 區塊改包 with s.begin(): 上下文管理器以自動守護交易。
2. 移除這 7 處自持型 session 的顯式 s.commit()。
3. 遵循 database SOP，確保 begin() 區段只包含資料庫寫入操作（極短交易原則）；ensure_admin/append_chat_message 之 commit 後屬性讀取（u.id/c.id）留於 session 內自動 refresh、行為等價。
EOF
git commit -F /tmp/SOP-COMPLY_C2_msg.txt

# （每次 commit 前建議 git diff --cached --name-only 自檢 = 各自宣告清單）
```
