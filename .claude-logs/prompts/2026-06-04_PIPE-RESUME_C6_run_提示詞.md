`````markdown
# 2026-06-04 — PIPE-RESUME C6 Run 提示詞

> **收到時間**：2026-06-04 20:13（UTC+8）
> **任務代號**：PIPE-RESUME C6
> **觸發 commit**：C6（單元測試 — 策略分派與四 Phase 契約）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C6_執行.md`
> **觸發情境**：baron 確認 C5 已手動提交（Checkout 含 C1-C5、四 Phase 全落地），下達 C6 執行指令——新建 `tests/test_resume_pipeline.py`，mock LLM/Embedding 隔離，驗證策略分派 + P1-P4 四 Phase 契約（P1 無 Abstract/LCC/Glossary、P2 LCC/摘要/Glossary 自癒/Domains.name、P3 100% Bypass + doc_type='resume' + translated_abstract 沿用、P4 ≥3 過濾 + email/phone/url 保留 + RAG 失敗不阻 reading_ready）。產報告暫存 baton/、同步 TODO.md（C6 ✅ / C7 WIP + Hash 自癒）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-04 20:13` |
| **任務代號** | `PIPE-RESUME C6` |
| **觸發 Commit** | `C6` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | baron 確認 C5 已手動提交，下達 C6 執行指令（當前 Checkout Commit 含 C1 至 C5）。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_PIPE-RESUME_C6_run_提示詞.md`（依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行、超 15 刪最舊）。
3. 回覆「✅ 提示詞已歸檔：...」後續執行。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit。

### 📋 任務資訊
- **任務編碼**：`PIPE-RESUME` / **當前 Commit**：`C6` / **工作流**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令與代碼修改規則
依 tasks §8 C6 新增測試檔。物理防線（§7）/ 測試防線（§6.6 + §6.7）/ 文件防線（§1.3）/ 檔頭尾 `# === [PIPE-RESUME C6 START/END] ===` 包裹。
**單元測試實作要求**：
- mock LLM/Embedding（monkeypatch/mock 隔離、嚴禁實打 API）。
- 策略分派：get_strategy('resume')→ResumePipeline、主幹無 doc_type 分支。
- P1：run_phase1 回 IngestionMetadataSpec、title=candidate_name、不含 Abstract/LCC/Glossary。
- P2：normalize_to_lcc cache 0 API / raw 空 fallback 'general'；GlossaryReadySpec 含 abstract/translated_abstract/domain_name(Domains PK 檢索)；缺詞自癒注入摘要+LCC prompt context；Glossary 凍結後 P3 不重複自癒。
- P3：100% Bypass（不切 Section/不開 Sliding Window）、InjectionContext.doc_type=='resume'、BilingualMarkdownSpec 沿用 P2 translated_abstract。
- P4：_is_chunk_meaningful resume ≥3（保 Python/Docker）、email/phone/url 保留、純數字/markdown 噪聲過濾；RAG 失敗 reading_ready 不受影響。

### 💾 備份規則
純新增測試檔、無須備份。

### 🔄 同步更新 TODO.md（必做、即時）
C6 → ✅（待 baron 回填）；C7 → 🟡 WIP；歷史 Hash 自癒（含 C5 hash 回填）。

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C6_執行.md`（暫存 baton/、不入版控）；套用 template_execution。

### 📝 §8 baron 執行命令
git add tests/test_resume_pipeline.py；msg 寫 /tmp/PIPE-RESUME_C6_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出 C6_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`tests/test_resume_pipeline.py`（策略分派 + P1-P4 四 Phase 契約、mock LLM/Embedding）
- 測試：新測試全綠 + 全套件防 Regression
- 報告：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C6_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C5（P4，四 Phase 全落地）。本階段 C6 單元測試；下一步 C7 Checkout 收官由 baron 另行下達。
`````
