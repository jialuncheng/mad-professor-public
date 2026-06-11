# META-NORM C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 20:30 |
| 任務代號 | META-NORM C1 — Schema & Flag（登記表與旗標）|
| 觸發 Commit | C1 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 tasks 拆分，下達 C1 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C1 / BE-Refactor；tasks §8 C1（plan U1/U2/U5）

### 執行命令（`# === [META-NORM C1 START/END] ===` 包裹）
① 改前備份 models.py + settings.py + db.py（3 .bak）
② models.py：新增 `MetaField`（canonical_key PK / label_zh/en / category / source / sort_weight / created_at / aliases relationship cascade）+ `MetaFieldAlias`（raw_key PK / canonical_key FK ondelete=CASCADE onupdate=CASCADE / created_at / meta_field relationship）；既有表 byte 不動
③ settings.py：`LLM_USE_META_NORM = os.getenv(..., "false").lower()=="true"`（預設 False）
④ db.py：init_db() create_all 後 seed 6 欄（course/instructor/organization/date/venue/doi、含 label/sort_weight）用 `sqlite_insert().on_conflict_do_nothing()` + `with session.begin()`（交易安全冪等）
⑤ 新建 tests/test_meta_norm.py：表結構/欄位/PK/FK CASCADE + seed 6 欄存在 + label/sort_weight 正確
- 物理防線：僅四檔；SOP §5.2 無裸 commit（db.py seed 走 session.begin()）

### 驗收
- pytest tests/test_meta_norm.py + 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0)

### TODO 同步
- C1 ✅、C2 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C1_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：models/settings/db/test + 3 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C1_msg.txt

### 停止
- 產出 C1_執行.md + TODO 更新後立即停止；不續 C2、不自發 commit/push
