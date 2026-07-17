# SOP-COMPLY C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）執行報告

> **任務代號**：SOP-COMPLY C3
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C3)
> **落地 Git Hash**：`0dff639`（baron 已 ship·Check 階段 hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md §8 C3` / plan v1.1 §2 #3（借用型·方案 A 呼叫端協調·OQ3）
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`68987e8`（SOP-COMPLY C2 — Self-Owned Transaction Guard）、分支 `gemini-refactor`。
- **完成狀態**：C3 原子改動（helper + 呼叫端 + 測試三合一）完成、全套件 **748 passed / 3 skipped / 0 failed**（零退化）；**`paper_manager.py` 裸 commit 歸零＝database SOP §5.2 全清**；**未 commit / 未 push**。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | Borrow-Session Transaction Coordination（原子）：6 helper 移除 `session.commit()` + web_server 5 端點包 `with s.begin():` + 3 測試檔 15 寫入區塊包 begin | `0dff639` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `paper_manager.py` | 修改 | 6 借用 helper 移除 `session.commit()`（`create_folder`〔+`session.flush()` 保 log f.id〕/ `update_folder` / `delete_folder` / `_apply_folder_path_tags` / `set_paper_folder` / `set_paper_tags`） |
| `web_server.py` | 修改 | 5 端點（4 session 區塊）改 `with db.SessionLocal() as s, s.begin():`——POST /api/folders、PATCH /api/folders/{id}、DELETE /api/folders/{id}、PATCH /api/papers/{uuid}〔涵蓋 set_paper_folder + set_paper_tags 兩呼叫點〕 |
| `tests/test_paper_tags.py` | 修改 | 4 寫入區塊 with 行加 `, s.begin()`（斷言本體零動） |
| `tests/test_normalize_tag.py` | 修改 | 3 寫入區塊同上 |
| `tests/test_folder_auto_tags.py` | 修改 | 8 寫入區塊同上 |
| 5 個 `.bak` | 新增（備份） | `.claude-logs/archive/2026-07-18_SOP-COMPLY_C3_*.bak`·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C3 → ✅、checkout → 🟡 WIP |
| `.claude-logs/prompts/2026-07-18_SOP-COMPLY_C3_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SOP-COMPLY 分類節追加 |

**baton 暫存（嚴禁 git add）**：本執行報告、C1/C2 報告、plan v1、tasks。

`git diff --stat`（實貼）：

```
 paper_manager.py               |  9 +++------
 tests/test_folder_auto_tags.py | 16 ++++++++--------
 tests/test_normalize_tag.py    |  6 +++---
 tests/test_paper_tags.py       |  8 ++++----
 web_server.py                  | 14 ++++++++++----
 5 files changed, 28 insertions(+), 25 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因

`paper_manager.py` 6 個借用型 helper（session 由參數傳入）內含 `session.commit()`——① 無 rollback 守護；② 交易邊界埋在 helper 內、呼叫端無法組合多個寫入為單一交易；③ 不可在 helper 內機械套 `with session.begin()`（呼叫端 autobegin 後再 begin 會 `InvalidRequestError`）→ 採 **方案 A 呼叫端協調**（OQ3 拍板）。

### §4.2 修法（原子三合一）

**① helper 移除 commit（交易邊界移交呼叫端）**——樣例 `create_folder`：

```python
    session.add(f)
    session.flush()   # 取得自增 f.id 供 log 與回傳消費、不提交交易
    logger.info(f"建立資料夾: owner={owner_id} id={f.id} {name}")
    return f
```

其餘 5 處純刪 `session.commit()`（log 與回傳零動）。`set_paper_folder` 之「core move + 自動標籤」由原兩段 commit 併呼叫端單一交易（任一失敗全 rollback＝更安全；`_apply_folder_path_tags` 失敗不阻塞之 try/except 原樣保留）。

**② web_server 呼叫端包 begin**——樣例 `create_folder` 端點：

```python
    with db.SessionLocal() as s, s.begin():
        try:
            f = paper_manager.create_folder(s, current_user.id, req.name, ...)
            return paper_manager._folder_to_dict(f)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
```

- `except ValueError → HTTPException 400` **保留**：ValueError 於 begin 內拋出 → 自動 rollback → 仍 400（tasks §4.3 明定語意）。
- `PATCH /api/papers/{uuid}` 之 folder+tags 兩 helper 併單一交易（成功一次 commit）。

**③ 3 測試檔 15 寫入區塊**——with 行機械加 `, s.begin()`（腳本逐點斷言「下一行為 `pm.set_paper_*` 直呼」防誤包唯讀區塊；斷言期望值本體零動）：

```python
    with db_mod_p.SessionLocal() as s, s.begin():
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)
```

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.3 驗收 grep（實貼）

```
$ grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"
0（全清）    ← 13 裸 commit 全數清帳（C2 自持 7 + C3 借用 6）

$ begin 命中：web_server.py 4 區塊（涵蓋 5 呼叫點）/ test_paper_tags 4 / test_normalize_tag 3 / test_folder_auto_tags 8
```

### §5.2 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/test_paper_tags.py tests/test_normalize_tag.py tests/test_folder_auto_tags.py -q
..................                                                       [100%]
18 passed in 0.22s

$ ./venv/bin/python -m pytest tests/ -q
748 passed, 3 skipped, 3 warnings in 54.49s
```

**748 passed / 0 failed 零退化**——自動標籤（test_folder_auto_tags 8 案）與手動標籤（test_paper_tags/test_normalize_tag）全數續綠＝「移除 helper commit 後寫入仍持久化」實證（plan §5 rollback 風險已由測試包 begin 規避）。

### §5.3 §6.5 SOP 一致性核查（實貼）

```
$ grep -rn "logger\.error(" paper_manager.py web_server.py | grep -v exc_info
web_server.py:175 / :195 / :806    ← 多行呼叫起始行·exc_info 於續行（C1 已清·AST 守衛 test_sop_comply_guard 續綠實證 0 違規）

$ grep -nE "\.commit\(\)" paper_manager.py web_server.py | grep -v "with .*session.*begin()"
無命中（合規）    ← database SOP §5.2 全清
```

---

## §6 不可動清單遵守狀態

- [x] **僅改 Session 包裹與 commit 移除**——diff 28+/25- 全落於交易邊界；寫入業務邏輯（欄位/驗證/CASCADE/normalize）byte 未動；唯一增行＝`create_folder` 之 `session.flush()`（保 log f.id、語意等價）。
- [x] **測試斷言期望值本體零動**——僅 with 行加 `, s.begin()`（機械腳本含「下一行必為 helper 直呼」防護斷言）；18 測試期望值原樣通過。
- [x] **原子鐵律**——helper + 呼叫端 + 測試三者同本 commit（分則紅燈）。
- [x] `db.py::init_db` / C1·C2 既有落地 / SEC-* 落地——零觸碰（守衛與 sec 測試全續綠）。
- [x] 前端 `static/**`、DB schema——零觸碰。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / C1·C2 報告（hash 已自癒 `98f8848`/`68987e8`）/ 本 C3 報告均留 `baton/` 暫存。
- **TODO.md**：C3 → ✅、checkout → 🟡 WIP。
- **歷史 Hash 自癒掃描（雙源）**：HEAD＝`68987e8`（C2）、無新 commit；雙源佔位符 **0**（前輪已全清）。
- **下一步**：C1–C3 三項實作全數完成（logging 25+1 / DB 13 全清）。等 baron 確認 C3 並 commit 後，下達 **checkout — 成果收官歸檔** 提示詞。
- **checkout 待辦備忘**：① `prompts/2026-07-18_SEC-HARDEN_Check_提示詞.md` 有 commit 後執行摘要回填（建議併入 checkout 白名單帶入）；② 範圍外債 `tools/regen_rag.py:252`（C1 報告 §4.3·baron 拍板）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 5 個 .bak）

# 2. git add 清單（僅本次 C3 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add paper_manager.py
git add web_server.py
git add tests/test_paper_tags.py
git add tests/test_normalize_tag.py
git add tests/test_folder_auto_tags.py
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_paper_manager.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_paper_tags.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_normalize_tag.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_folder_auto_tags.py.bak

# 3. commit message 草稿（已寫入 /tmp/SOP-COMPLY_C3_msg.txt）
cat > /tmp/SOP-COMPLY_C3_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）

1. 移除 paper_manager.py 中 6 個借用 Session 的 helper 函數內的 session.commit()，將交易邊界控制權回歸呼叫端（create_folder 補 session.flush() 保留 log 之自增 f.id、不提交交易）。
2. 修改 web_server.py 中的 5 處資料夾/標籤 API 路由（4 個 session 區塊），以 with s.begin(): 包裹事務呼叫；except ValueError→400 保留、begin 內拋出自動 rollback。
3. 修改 test_paper_tags.py、test_normalize_tag.py 與 test_folder_auto_tags.py 三檔單元測試中對 pm.set_paper_* 函數的直呼（15 處寫入區塊），包裹 with s.begin(): 防止因 helper 內移除 commit 而在 Session 關閉時自動 rollback。
4. paper_manager.py 裸 commit 自此歸零（database SOP §5.2 全清）。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SOP-COMPLY_C3_msg.txt
```
