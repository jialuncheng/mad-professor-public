`````markdown
# 2026-06-06 — RESUME-P3 META-HOTFIX-1 Run（P1 Meta 渲染進文件 header·落地）提示詞

> **收到時間**：2026-06-06 13:21（UTC+8）
> **任務代號**：RESUME-P3 META-HOTFIX-1（BE-Hotfix 落地執行）
> **觸發 commit**：META-HOTFIX-1
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md`
> **觸發情境**：baron 確認 META-HOTFIX-1 計畫（代號由 HEADER 改 META 避免與 HEADING 混淆、meta 採無序列表）後下達執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 13:21 | 任務 RESUME-P3 META-HOTFIX-1 | 觸發 Commit META-HOTFIX-1 | 依據 hotfix.md |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-P3_META-HOTFIX-1_run_提示詞.md + 更新 INDEX（補條目 + 時間排序首行、超 15 刪最舊）。

你扮演 Claude Code，執行單一 Commit META-HOTFIX-1（BE-Hotfix）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP

### 具體實作（# === [RESUME-P3 META-HOTFIX-1 START/END] === 包裹）
1. 備份 resume_pipeline.py + test_resume_pipeline.py → .bak。
2. pipelines/resume_pipeline.py：
   - 新增 @staticmethod _render_meta_header(ctx, gspec, *, lang)：讀 ctx.raw_metadata（domain/organization/phone/email）+ ctx.ingestion.title（姓名、保留 (測試)）；lang=='en' domain 優先 gspec.domain_name；組 `# 姓名` + **無序列表** `- **領域/機構/電話/Email**：值`（zh）/`- **Domain/...**: val`（en）；缺項省略；整包空回 ''；結尾 \n\n。
   - run_phase3 寫出前 prepend：zh_text = _render_meta_header(ctx,gspec,lang="zh")+zh_text；en_text 同（lang="en"）。
3. tests/test_resume_pipeline.py：追加 test_p3_meta_header_rendered（title="王小明 (測試)" + raw_metadata{domain/organization/phone/email}；斷言 (a) # 王小明 (測試) 開頭 (b) 四欄標籤值都在 (c) 各欄獨立 list item `\n- **領域**：` 等）。
4. 不動：HEADING/PARA 實作 / _restore_sections_markdown / 凍結合約 / A軌不耦合 / 其餘四路 / 母提示詞 / DB。

### 三道防線
- 物理：僅 2 檔；測試：grep（META-HOTFIX-1 包裹 / _render_meta_header / A軌不耦合=0 / 新測試）+ pytest + SOP；文件：commit 由 baron。

### 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
頂部 ✅ 完成區追加 META-HOTFIX-1（hash 待回填）；git log 回填殘留佔位符（含 PARA-HOTFIX-1）。

### 產出 + 收官歸檔（hotfix 一次性）
baton/2026-06-06_RESUME-P3_META-HOTFIX-1_執行.md（template_execution）→ 收官 mv hotfix.md + 執行.md → hotfixes/；§8 git add 清單 + msg（/tmp/RESUME-P3_META-HOTFIX-1_msg.txt）。

### 🛑 停止
產報告 + 搬移後立即停止；不動未列代碼、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（新增 _render_meta_header + run_phase3 prepend zh/en）+ test_resume_pipeline.py（追加 1 測試）+ 2 .bak
- 驗收：grep（包裹 / helper / A軌不耦合 0 / 新測試）+ pytest + SOP
- 收官：hotfix.md + 執行.md mv → hotfixes/
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

P1 meta（姓名/領域/機構/電話/Email）經 run_phase3 組無序列表 header 進 final；走現有 raw_metadata 旁路（治標）；INFRA-4 之後讀取源轉 spec.meta（治本）；改 B軌輸出 → 須 `capture resume --force` 重捕 golden（baron 運維）。
`````
