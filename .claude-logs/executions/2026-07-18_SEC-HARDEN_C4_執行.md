# SEC-HARDEN C4 — Theme Overwrite Guard（主題覆寫守衛）執行報告

> **任務代號**：SEC-HARDEN C4
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C4)
> **落地 Git Hash**：`3942e20`（baron 已 ship·Check 階段 hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md §8 C4` / plan v1.1 §2 #4（#6 大小寫不敏感）+ OQ4
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`bc5d5f4`（BE-Refactor: SEC-HARDEN C3 — Error Masking）、分支 `gemini-refactor`。
- **完成狀態**：C4 代碼修改 + 測試全數完成、全套件 **745 passed / 3 skipped / 0 failed**（C3 後基線 739 + 新增 6）；**未 commit / 未 push**（依 CLAUDE.md §1.3 由 baron 手動執行）。**C1–C4 四項實作全數完成、僅餘 checkout 收官。**

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | Theme Overwrite Guard：模組級 `BUILTIN_THEMES` frozenset + sanitize 後 `lower()` 命中即 400（`write_bytes` 前攔截）+ 測試追加 | `3942e20` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `web_server.py` | 修改 | 模組級 `BUILTIN_THEMES` frozenset（`:1272`）+ `upload_theme` sanitize 後守衛（`:1309-1310`·`write_bytes` 前） |
| `tests/test_sec_harden.py` | 修改（追加） | +6 測試（frozenset 完整性 / mies→400 不寫檔 / 4 大小寫變體→400 / 非內建照常上傳 / 既有過濾不弱化〔非 .css·413〕/ 守衛位序源碼守衛） |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C4_web_server.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C4 → ✅、checkout → 🟡 WIP、C3 hash 自癒 `bc5d5f4` |
| `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C4_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SEC-HARDEN 分類節追加 + 時間列剔舊（FE-PERF-2 C2 移入分類節保留） |

**baton 暫存（嚴禁 git add）**：本執行報告、C1–C3 執行報告（hash 已自癒 `52ebae8`/`a5e2bd4`/`bc5d5f4`）、plan v1、tasks。

`git diff --stat`（實貼·`tests/test_sec_harden.py` 含 C4 追加）：

```
 tests/test_sec_harden.py | 86 +++++++++++++++++++++++++++++++++++++++++++++++-
 web_server.py            | 13 ++++++++
 2 files changed, 98 insertions(+), 1 deletion(-)
```

---

## §4 真因與修法

### §4.1 真因

**#6（LOW）**：`upload_theme`（`/api/themes/upload`）既有 5 道過濾（副檔名 / sanitize / 大小 / 路徑強制 / traversal 檢查）**均不防與內建主題同名**——上傳 `mies.css` 直達 `target.write_bytes(content)` 覆寫內建 CSS 系統資產；大小寫不敏感檔案系統（macOS APFS 預設）下 `Mies.css` 同樣覆寫 `mies.css`。

### §4.2 修法（純新增守衛、既有 5 道過濾零弱化）

模組級名單（`upload_theme` 路由前·與 `list_themes` 內建清單同源對齊）：

```python
BUILTIN_THEMES = frozenset({"mies", "kahn", "kandinsky", "nara"})
```

sanitize 後（空名檢查後）、大小檢查與 `write_bytes` 前插入：

```python
    if sanitized.lower() in BUILTIN_THEMES:
        raise HTTPException(status_code=400, detail="不可覆寫內建主題")
```

- **大小寫不敏感**：`sanitized.lower()` 命中即拒（`Mies` / `KAHN` / `nArA` 全攔）。
- **fail-fast 位序**：置於讀取檔案內容之前、`write_bytes` 之前——命中即 400、**零寫檔**（源碼守衛斷言 guard 位置 < write_bytes 位置）。
- 既有非內建名（含 5 支已上傳自訂主題）行為不變（OQ4：使用者內容同 admin 覆寫可接受、僅擋內建 4 名）。

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.4 驗收 grep（實貼）

```
$ grep -n "BUILTIN_THEMES\|不可覆寫內建" web_server.py
1272:BUILTIN_THEMES = frozenset({"mies", "kahn", "kandinsky", "nara"})
1309:    if sanitized.lower() in BUILTIN_THEMES:
1310:        raise HTTPException(status_code=400, detail="不可覆寫內建主題")
```

### §5.2 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/test_sec_harden.py -q
..............................                                           [100%]
30 passed in 1.20s

$ ./venv/bin/python -m pytest tests/ -q
745 passed, 3 skipped, 3 warnings in 54.26s
```

C3 後基線 739 passed → **745 passed**（+6 主題守衛）、0 failed、綠燈不退化。行為測試直呼 `upload_theme`（`BASE_DIR` monkeypatch 至 tmp）：`mies.css` 與 4 個大小寫變體 → 400「不可覆寫內建主題」且 themes 目錄零寫檔；`My_Custom_Theme.css` 照常成功；非 `.css` 400 / 超 100KB 413 既有過濾續效。

### §5.3 §6.6 SOP 一致性核查（實貼）

```
$ grep -nE "traceback.format_exc|logger\.error|logger\.exception" web_server.py | grep -v exc_info
175:        logger.error(     ← broker 多行呼叫·續行 :177 有 exc_info=True（合規）
195:        logger.error(     ← broker DB append 失敗 log（既有債·非本任務範圍·C1 起已標·SOP-COMPLY 另案）
806:        logger.error(     ← 影子軌多行呼叫·續行 :808 有 exc_info=True（合規）

$ grep -nE "\.commit\(\)" web_server.py | grep -v "with .*session.*begin()"
無命中（合規）
```

**判定**：C4 **新增 0 個 `logger.error`**（守衛走 HTTPException、無新增日誌呼叫；logging SOP 無新增違規）；database SOP 零裸 commit（本 commit 不涉 DB 寫入）。

---

## §6 不可動清單遵守狀態

- [x] **既有檔名 sanitize + 路徑 traversal 檢查 + 大小限制（邏輯本體）零弱化**——`git diff` 實證 `upload_theme` 僅插入一個 if 區塊、既有 5 道過濾行 byte 未動；`test_existing_filters_not_weakened`（非 .css→400 / 超大→413）通過。
- [x] **僅於 `write_bytes` 前新增內建同名檢查**——`test_guard_placed_before_write_bytes` 源碼位序守衛通過。
- [x] login 驗證邏輯 / CORS / broker·pipeline 例外遮蔽——零觸碰（C1–C3 已收、相關 24 測試續綠）。
- [x] `settings.py`——本 commit 零觸碰。
- [x] 前端 `static/**`（含 `static/themes/` 實體檔案）、DB schema——零觸碰（測試寫檔全在 tmp_path）。
- [x] SEC-SECRET / SEC-XSS / SEC-HARDEN C1–C3 既有落地——零觸碰（相關測試全數續綠）。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / C1–C3 報告 / 本 C4 報告均留 `baton/` 暫存、未 mv 未 git add（收官鐵律遵守）。
- **TODO.md**：C4 → ✅、checkout → 🟡 WIP；**C3 hash 自癒回填 `bc5d5f4`**（baron 已 ship C3、git log 實證；C3 報告同步自癒）。
- **歷史 Hash 自癒掃描（雙源）**：`grep "待 baron 回填"` 除本任務註記外僅 1 命中——GOV-PATH-FIX「Checkout Hash」；該 checkout commit **仍未存在**（staged 未 commit）→ 如實保留；`archive/TODO_done_archive.md` 零佔位符。
- **下一步**：C1–C4 四項實作全數完成（PROJECT-REVIEW #3/#8/#4/#5/#6 全關閉）。等 baron 確認 C4 並 commit 後，下達 **checkout — 成果收官歸檔** 提示詞（Conformance 五維度 + baton 一次性 mv 歸檔 + TODO 雙層結案 + staged 白名單自檢；含 C1 deviation〔stale XFF 測試契約同步〕提請確認）。
- **運維提醒彙整（checkout 時併入）**：① 反向代理部署須設 `TRUSTED_PROXIES`（C1）；② 生產跨源部署須設 `CORS_ALLOW_ORIGINS`（C2）；③ 前端錯誤訊息已通用化、診斷看 server log（C3）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 1 個 .bak）

# 2. git add 清單（僅本次 C4 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add tests/test_sec_harden.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C4_web_server.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C4_msg.txt）
cat > /tmp/SEC-HARDEN_C4_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C4 — Theme Overwrite Guard（主題覆寫守衛）

1. 新增模組級 BUILTIN_THEMES 唯讀集，收錄 mies, kahn, kandinsky, nara 四個內建主題名。
2. 於主題上傳處理器之寫檔（write_bytes）前新增檔名大小寫不敏感比對守衛，命中時以 400 狀態拒絕上傳。
3. 防範大小寫變體（例如 Mies）在不區分大小寫之檔案系統中覆寫內建主題 CSS 資產；既有 5 道安全過濾零弱化。
4. 於 tests/test_sec_harden.py 追加 6 個單元測試，驗證內建主題覆寫攔截機制（含大小寫變體、非內建照常上傳、既有過濾不弱化、守衛位序）。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SEC-HARDEN_C4_msg.txt
```
