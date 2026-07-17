# SEC-HARDEN C3 — Error Masking（例外遮蔽）執行報告

> **任務代號**：SEC-HARDEN C3
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C3)
> **落地 Git Hash**：`bc5d5f4`（baron 已 ship·C4 階段 hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md §8 C3` / plan v1.1 §2 #3（#5 例外遮蔽·排除 ValueError）+ OQ3
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`a5e2bd4`（BE-Refactor: SEC-HARDEN C2 — CORS Restriction）、分支 `gemini-refactor`。
- **完成狀態**：C3 代碼修改 + 測試全數完成、全套件 **739 passed / 3 skipped / 0 failed**（C2 後基線 734 + 新增 5）；**未 commit / 未 push**（依 CLAUDE.md §1.3 由 baron 手動執行）。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | Error Masking：broker + pipeline 主軌/影子軌 broad `Exception` client 出口 → 通用訊息 + `exc_info=True`；排除 3 處 ValueError | `bc5d5f4` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `web_server.py` | 修改 | 3 個 broad `Exception` client-facing sink 遮蔽（broker `error_msg` / 主軌 `processing_tasks['error']` / 影子軌同項）+ 主軌 `logger.error` 補 `exc_info=True` |
| `tests/test_sec_harden.py` | 修改（追加） | +5 測試（3 源碼守衛〔含 ValueError 不可動守衛〕+ broker 行為遮蔽測試 + logging SOP 守衛） |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C3_web_server.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C3 → ✅、C4 → 🟡 WIP、C2 hash 自癒 `a5e2bd4` |
| `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C3_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SEC-HARDEN 分類節追加 + 時間列剔舊（FE-PERF-2 C1 移入分類節保留） |

**baton 暫存（嚴禁 git add）**：本執行報告、C1/C2 執行報告（hash 已自癒）、plan v1、tasks。

`git diff --stat`（實貼·`tests/test_sec_harden.py` 含 C3 追加）：

```
 tests/test_sec_harden.py | 83 +++++++++++++++++++++++++++++++++++++++++++++++-
 web_server.py            | 16 +++++++---
 2 files changed, 94 insertions(+), 5 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因

**#5（LOW）**：3 個 broad `except Exception` 的 client-facing 出口直接夾帶 `str(e)`：
- broker（原 `:168`）：`error_msg = f"(生成失敗) {str(e)[:200]}"` → 廣播給訂閱者 **+ finally 落 DB 聊天歷史**（前端 reload 可見）。
- 主軌 `run_pipeline`（原 `:682`）：`processing_tasks[...]['error'] = str(e)` → status SSE → 前端。
- 影子軌 `run_pipeline_shadow`（原 `:796`）：同上。

`str(e)` 可含檔案路徑 / schema / 堆疊上下文 → 資訊洩漏。（`:1171/:1194/:1258` 之 `HTTPException(detail=str(e))` 捕 `ValueError`＝合法業務驗證訊息、**排除**。）

### §4.2 修法（三 sink 遮蔽 + logging SOP 補齊）

**broker**（廣播 + DB 落歷史雙出口一次覆蓋；既有 `logger.error` 已含 `exc_info=True`）：

```python
    except Exception as e:
        error_msg = "（生成失敗）處理發生錯誤，請稍後再試"
        session.error = str(e)   # server 內部狀態（全檔無讀取點·grep 實證）、保留供除錯
        logger.error(f"[broker] stream error paper={session.paper_uuid}: {e}", exc_info=True)  # 既有
```

**主軌 `run_pipeline`**（status SSE 遮蔽 + 該行 `logger.error` 原無 `exc_info` → 補上）：

```python
                processing_tasks[task_key]['error'] = "處理失敗，請稍後再試"
        logger.error(f"論文處理失敗: owner={owner_id} {paper_id} - {str(e)}", exc_info=True)
```

**影子軌 `run_pipeline_shadow`**（status SSE 遮蔽；既有 `logger.error` 已含 `exc_info=True`）：

```python
                processing_tasks[shadow_key]['error'] = "處理失敗，請稍後再試"
```

- SSE 協定欄位結構零改（僅 error **值來源**改變）。
- 3 處 `ValueError` HTTPException **一字未動**（源碼守衛 `count == 3` 鎖定）。

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.3 驗收 grep（實貼）

```
$ grep -n "processing_tasks\[.*\]\['error'\] = str(e)" web_server.py || echo "已改通用訊息"
已改通用訊息

$ grep -n "exc_info=True" web_server.py
177:            exc_info=True,                     ← broker（既有）
690:        logger.error(f"論文處理失敗: ... - {str(e)}", exc_info=True)   ← 主軌（C3 補齊）
808:            exc_info=True,                     ← 影子軌（既有）
1387:        logger.error("[meta-norm] ...", exc_info=True)               ← 既有
```

### §5.2 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/test_sec_harden.py -q
........................                                                 [100%]
24 passed in 1.22s

$ ./venv/bin/python -m pytest tests/ -q
739 passed, 3 skipped, 3 warnings in 54.74s
```

C2 後基線 734 passed → **739 passed**（+5 遮蔽守衛）、0 failed、綠燈不退化。行為測試 `test_broker_stream_error_masked` 實跑 `_run_stream_background`：注入含敏感路徑之 RuntimeError → 廣播 chunk 與 DB 落歷史均為通用訊息、無 raw 例外；`session.error`（server 內部）保留 raw。

### §5.3 §6.6 SOP 一致性核查（實貼）

```
$ grep -nE "traceback.format_exc|logger\.error|logger\.exception" web_server.py | grep -v exc_info
175:        logger.error(     ← broker 多行呼叫·續行 :177 有 exc_info=True（合規）
195:        logger.error(     ← broker DB append 失敗 log（既有債·非 #5 client-facing sink·C1 起已標）
806:        logger.error(     ← 影子軌多行呼叫·續行 :808 有 exc_info=True（合規）

$ grep -nE "\.commit\(\)" web_server.py | grep -v "with .*session.*begin()"
無命中（合規）
```

**判定**：C3 觸碰之 3 個 sink 對應 `logger.error` **全數含 `exc_info=True`**（主軌一處為本 commit 補齊、grep :690 實證）；`:195` 為既有 DB append 失敗 log（server 端、非 client 出口、非 #5 範圍——全 41 處 `logger.error` 補 exc_info 屬 SOP-COMPLY 另案、plan OQ3 定案）。database SOP 零裸 commit。

---

## §6 不可動清單遵守狀態

- [x] **3 處 `except ValueError` HTTPException（`:1171/:1194/:1258`·行號 C1/C2 後位移）零觸碰**——源碼守衛 `test_valueerror_http_exceptions_preserved`（count == 3）通過。
- [x] **僅改 broad `Exception` client-facing 出口**——`git diff` 實證 `web_server.py` 僅 3 個 except 區塊 hunk；SSE 協定欄位與業務流程零改（僅 error 值來源）。
- [x] login 驗證邏輯 / theme 上傳守衛——零觸碰（C1 已收 / C4 待做）。
- [x] `settings.py`——本 commit 零觸碰（C3 僅改 `web_server.py` + 測試）。
- [x] 前端 `static/**`、DB schema——零觸碰。
- [x] SEC-SECRET / SEC-XSS / SEC-HARDEN C1·C2 既有落地——零觸碰（相關測試全數續綠）。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / C1·C2 報告 / 本 C3 報告均留 `baton/` 暫存、未 mv 未 git add（收官鐵律遵守）。
- **TODO.md**：C3 → ✅、C4 → 🟡 WIP；**C2 hash 自癒回填 `a5e2bd4`**（baron 已 ship C2、git log 實證；C2 報告同步自癒）。
- **歷史 Hash 自癒掃描（雙源）**：`grep "待 baron 回填"` 除本任務註記外僅 1 命中——GOV-PATH-FIX「Checkout Hash」；該 checkout commit **仍未存在**（staged 未 commit）→ 如實保留；`archive/TODO_done_archive.md` 零佔位符。
- **下一步**：等 baron 確認 C3 並 commit 後，下達 **C4 — Theme Overwrite Guard（主題覆寫守衛·#6 大小寫不敏感）** 提示詞（C4 完成後進 checkout 收官）。
- **除錯註**：前端錯誤訊息改通用後，診斷一律看 server log（`logger.error` 完整堆疊、trace_id 可串連）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 1 個 .bak）

# 2. git add 清單（僅本次 C3 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add tests/test_sec_harden.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C3_web_server.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C3_msg.txt）
cat > /tmp/SEC-HARDEN_C3_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C3 — Error Masking（例外遮蔽）

1. 修改 web_server.py 的 broker Exception 串流處理區，將 client 端錯誤訊息替換為通用提示以防例外細節外洩（含 DB 落聊天歷史出口）。
2. 修改主軌 run_pipeline 與影子軌 run_pipeline_shadow 的例外處理區，將 SSE 拋送之 task error 改為通用錯誤訊息。
3. 遵循 logging SOP，在遮蔽 client 出口之處，將完整異常堆疊以 logger.error(..., exc_info=True) 詳實記錄於伺服器日誌（主軌一處原缺 exc_info、本次補齊）。
4. 排除 3 處 ValueError HTTPException 以免破壞正常之業務前端 UX 提示（源碼守衛鎖定 count==3）。
5. 於 tests/test_sec_harden.py 追加 5 個單元測試（源碼守衛 + broker 行為遮蔽驗證），驗證例外遮蔽機制之正確性。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SEC-HARDEN_C3_msg.txt
```
