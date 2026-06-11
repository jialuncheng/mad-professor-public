# META-NORM C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 21:40 |
| 任務代號 | META-NORM C3 — P1 Wire（開放抽取與封面放寬接線）|
| 觸發 Commit | C3 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 C2，下達 C3 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C3 / BE-Refactor；tasks §8 C3（plan U6/U7/U7.1/BS1）

### 執行命令（`# === [META-NORM C3 START/END] ===` 包裹）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py：
   - `_COVER_PROMPT` 追加開放 `metadata:{欄名:值}` 抽取（保留 company/date/authors 相容）+ 引導自由列封面所有 metadata
   - run_phase1 ⑤ 封面段：定義 venue/doi=None；旗標 on → `MetaNormalizer.normalize_fields(cover.get("metadata"), context=title)`；pop reserved（title/authors〔字串依 ,;，；\n 切列表〕/venue/doi）回填合約、不入旁路；其餘 canonical 以三欄 dict {value,source,confidence}（HOTFIX-1b 契約）寫 ctx.raw_metadata；旗標 off → 原寫死 company/date 路徑
   - return IngestionMetadataSpec 補 venue=venue/doi=doi
③ tests 追加 2（旗標 on 對齊+reserved 回填+三欄 dict / 旗標 off fallback）
- 物理防線：僅兩檔；SOP §5.2 無裸 commit

### 驗收
- pytest tests/test_slide_pipeline.py + 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0)

### TODO 同步
- C3 ✅、C4 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C3_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：slide_pipeline + test + 2 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C3_msg.txt

### 停止
- 產出 C3_執行.md + TODO 更新後立即停止；不續 C4、不自發 commit/push
