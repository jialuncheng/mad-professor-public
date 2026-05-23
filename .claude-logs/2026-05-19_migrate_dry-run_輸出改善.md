# 2026-05-19 migrate_to_db.py --dry-run 輸出改善

NEVER 修改業務邏輯，只動 dry-run 列印。

## 修改範圍
僅 `scripts/migrate_to_db.py`：
- 改寫 `do_dry_run()`（純輸出/計畫呈現）
- 新增 `_probe_db()`：唯讀探查 DB 現況，**不建檔、不呼叫 init_db**；
  sqlite 檔不存在 → 回 'absent' 且不連線（避免 SQLAlchemy 連線時建空檔）；
  缺 sqlalchemy/dotenv 或連線失敗 → 'unavailable'（視為全新，不報錯）
- 新增 `_count_conversations(src)`：讀 chat_history.json 計數
未更動：`do_migrate`（line 208，含 db.init_db / shutil.move）、`do_rollback`（307）、`main`（340）、
`_load_index`/`_resolve_paper_src`/`_mtime`/models/db。

## dry-run 新輸出涵蓋
① User：username（AUTH_USERNAME）、DB 是否已存在（ok/absent/unavailable 三態）、admin_id、
   AUTH_PASSWORD_HASH 空警告
② 逐筆 paper：序號 / paper_id / title / translated_title / conversations 則數 /
   已 migrated(Yes/No，依 DB 內 paper_uuid 集合) / 移動路徑（已在新位置會標註）
③ Orphan：output/ 內非數字 owner 目錄且不在 papers_index → 列出 + 建議跳過+warning
④ Dangling：papers_index 有但 output/ 無對應目錄 → 列出 + 建議跳過+warning
⑤ 摘要：新增 X papers / X conversations / 搬移 X 目錄 / 跳過 X orphans / X dangling /
   paper_uuid=舊 paper_id 說明 / 預估 ~N 秒（每 paper 0.5s）
⑥ 結尾「未做任何變更。」

## ⑦ paper_uuid 設計一致性確認
do_migrate 內 `Paper(... paper_uuid=pid ...)`（pid = papers_index 的舊 id），
未加 __uuid8 → 與原設計「舊資料相容時 paper_uuid = 舊 paper_id」一致；
路徑為 output/{admin_id}/{舊 paper_id}/。dry-run 輸出已明確標示此規則與路徑樣板。

## ⑧ idempotent
- _probe_db 唯讀，多次跑 dry-run 不改任何狀態、不建 .db。
- admin 已存在 DB → User 段標 "DB 已存在: Yes (id=...)"。
- paper_uuid 已在 DB → 該筆標 "已 migrated: Yes"，且不計入「新增」與「搬移」（與 do_migrate 的 get-or-create idempotent 行為對齊）。
- 已搬移者路徑標「（已在新位置）」。

## 驗證
- py_compile scripts/migrate_to_db.py：通過。
- grep 確認 do_migrate/do_rollback/main 及 init_db()/shutil.move 未更動。
- ⚠ runtime（實跑 --dry-run）此環境缺 sqlalchemy/dotenv 無法執行；_probe_db 已設計為該情況回 'unavailable' 並照常輸出計畫（不崩潰）。使用者於正式 venv 跑：
    python scripts/migrate_to_db.py --dry-run

## 疑慮
1. runtime 未能在此環境驗證（缺 sqlalchemy/dotenv），僅 py_compile 保證語法；_probe_db 對缺套件已 graceful（'unavailable'）。
2. Orphan 偵測排除「全數字」目錄（視為已遷移的 owner 目錄）；若未來 paper_id 出現純數字命名會被誤判為 owner 目錄而漏報為 orphan —— 目前 sanitize_paper_id 來源為檔名，純數字檔名罕見，列為已知邊界。
