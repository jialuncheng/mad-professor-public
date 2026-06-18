# PIPE-SECTION-BASE C3 執行報告 — rag 旁路與 meta header 純格式化器

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SECTION-BASE C3 |
| 執行日期 | 2026-06-18 |
| 依據規劃 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_tasks.md §8 C3` |
| 次級參考 | plan v2 §2 U3.1（Zero Schema Coupling）;RAG-ASYNC-HOTFIX-1 / META-HOTFIX-1 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C3)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C1（`e400789` 摘要簇）+ C2（`24db977` 翻譯與排版還原）已 ship;rag 旁路 + meta header 仍私有於 resume。
- **完成狀態**：`_collect_rag_sections`/`_single_container_sections` 抽入 `section_engine`、`_render_meta_header` **重構為純格式化器**（引擎零讀 metadata）、resume 對應 method 改 delegate;業務代碼僅動 plan 指明兩檔。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U3.1`（meta header 純格式化器·Zero Schema Coupling）+ rag 旁路抽取;無偏離。**深化執行**（審查採納）：`render_meta_header` 不僅「欄位集參數化」、而是引擎**完全不讀 raw_metadata/ctx dict**（收已抽好之 `(Label, Value)` tuples）;欄位抽取 + zh/en label 對照全留 resume 呼叫端;接縫 summary_key=原文標題 path 零位移。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C3 | （待 baron 回填）| BE-Refactor: PIPE-SECTION-BASE C3 — RAG旁路與meta header純格式化器 |

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/section_engine.py` | 修改（追加 C3 簇 3 函式）| **本 commit git add** |
| `pipelines/resume_pipeline.py` | 修改（rag 旁路 + meta header → delegate）| **本 commit git add** |
| `.claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C3_resume_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C3_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C3 ✅ / C4 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C3_執行.md`（本檔）/ C1-C2 報告 / plan / tasks | baton 暫存 | **baton/ 暫存（C5 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-SECTION-BASE C3 ...] ===` 包裹）
- **`section_engine.py` 追加 C3 簇**（3 函式）：
  - `collect_rag_sections(slots, zh_by_index, translate, sink)`（原值搬移、`summary_key`=原文標題 path 保留·RAG-ASYNC-HOTFIX-1）
  - `single_container_sections(text, title)`（**title 參數化**、引擎不讀 ctx、不寫死文體預設「履歷全文」）
  - `render_meta_header(title, items: List[Tuple[str,str]], sep="：")`（**純格式化器**·U3.1：僅產 `# 標題` + `- **Label**{sep}Value` 無序列表、空 value 略過;**零讀 raw_metadata/ctx**）
- **`resume_pipeline.py`**（delegate）：
  - `_collect_rag_sections` / `_single_container_sections`（後者解析 `(ctx.ingestion.title or "履歷全文")` 後傳引擎）改 delegate。
  - `_render_meta_header(ctx, gspec, *, lang)` **保留**（resume 專屬 schema）：負責抽 domain/org/phone/email（en domain 優先 gspec.domain_name）+ zh/en label 對照 + sep → 組 `(Label, Value)` 清單 → 呼 `section_engine.render_meta_header(title, items, sep)`。

關鍵片段（meta header delegate）：
```python
items = [(label["domain"], domain), (label["org"], org),
         (label["phone"], phone), (label["email"], email)]
return section_engine.render_meta_header(title, items, sep)   # 引擎零讀 metadata
```

## §5 測試結果
### §5.1 §6.3 C3 驗收 grep
```
engine C3 函式 3/3;render_meta_header 純簽名（items: List[Tuple[str,str]]）命中
engine 實際讀取 raw_metadata：0（2 命中皆 docstring 字樣）;實際 ctx 變數用法：0 → Zero Schema Coupling ✓
engine summary_key（接縫基準）：2 命中（原文標題 path 保留）
resume 殘留 C3 私有實作：0（僅 delegate）
```
### §5.2 §6.6 SOP 一致性核查（BE-Refactor 強制）
```
logging（engine logger.error / format_exc）：0 命中（合規）
database（engine 裸 commit）：0 命中（合規）
```
### §5.3 行為等價 + 全套件 pytest
```
pytest tests/test_resume_pipeline.py -q → 42 passed
  〔含 test_p3_meta_header_rendered：zh.startswith("# 王小明 (測試)") + "\n- **領域**：IC 設計" + "\n- **機構**：聯詠科技"
    → 純格式化器輸出 byte 等同重構前〕
pytest tests/ -q → 1 failed, 640 passed, 3 skipped（640＝基線維持;唯一 fail＝既有 .env LOG_FORMAT env flake）
```
### §5.4 變動範圍（git）
```
git status -s 業務 .py：僅 pipelines/resume_pipeline.py(M) + pipelines/section_engine.py(M)
diff stat：resume −55 / section_engine +73
```

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| `slide_pipeline.py` 全檔（Q2）| [x] ✅ 未碰 |
| `contracts.py` 四凍結合約 / key 基準 | [x] ✅ 未動（summary_key=原文標題 path 零位移）|
| `rag_indexer.py` P4 消費端 | [x] ✅ 未動 |
| resume 攝入層私有 helper（含 _meta_value）| [x] ✅ 未動（meta header delegate 仍呼 _meta_value 抽欄）|
| A 軌全部 | [x] ✅ 未動 |
| resume final_zh/en 輸出 byte | [x] ✅ 等價（42 測試含 meta_header byte 斷言佐證）|
| DocumentStrategy ABC / factory | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅動 `section_engine.py` + `resume_pipeline.py`（plan 指明兩檔）;slide/contracts/rag_indexer/A 軌零碰（git status 證）。
- **(b) 無關 / 違規?**：否。深化（非偏離）——`render_meta_header` 引擎收 tuples、零讀 metadata（審查 Q4 銳化、plan U3.1）;`single_container_sections` title 參數化去 ctx 耦合;皆貼合方案 A「route-specific 不滲共用層」、行為 byte 等價（meta_header 測試佐證）。符 CLAUDE.md（baton 不 add、不自發 commit）。
- **(c) 推進哪個 U-N?**：U1（共用引擎·rag 旁路簇）+ U3.1（meta header 純格式化器 Zero Schema Coupling）;無做白工。

## §7 銜接
- baton 狀態：C1-C3 報告 + plan + tasks 留 baton（待 C5 一次性歸檔）。
- 下一步：**C4 — 引擎單元測試與接縫整合測試（雙鎖·Q6）**：新建 `tests/test_section_engine.py`（DFS / 批次摘要保序 / 並行 byte 等拍 + 限流 + 退原文 / heading 退化 / meta header 純格式化 / **base 層 P2→P3→P4 key-changing 整合測試**）。引擎三簇（摘要/翻譯還原/rag+meta）至此全抽出、C4 為其織保護網。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）

# 2. git add（業務兩檔 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/section_engine.py pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C3_resume_pipeline.py.bak
git add .claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C3_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿
cat > /tmp/PIPE-SECTION-BASE_C3_msg.txt << 'EOF'
BE-Refactor: PIPE-SECTION-BASE C3 — RAG旁路與meta header純格式化器

- section_engine.py 追加 C3 簇：collect_rag_sections〔summary_key=原文標題 path〕/
  single_container_sections〔title 參數化、引擎不讀 ctx〕/ render_meta_header 純格式化器
  〔收 (Label,Value) tuples、引擎零讀 raw_metadata/ctx·U3.1 Zero Schema Coupling〕。
- resume_pipeline.py 對應 method 改 delegate；_render_meta_header 保留欄位抽取 + zh/en label
  對照（resume 專屬 schema）、渲染交引擎；接縫 summary_key=原文標題 path 零位移。

驗證：resume 42 passed〔含 test_p3_meta_header_rendered byte 斷言〕；全套件 640 passed（基線、
唯一 fail＝既有 .env LOG_FORMAT flake）；engine 實際讀 raw_metadata/ctx＝0（Zero Schema Coupling）；
SOP logging/database 無命中；slide/contracts/rag_indexer/A 軌零碰。baton 未 add、待 C5 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SECTION-BASE_C3_msg.txt
```

## §9 回退方式
`git revert <C3 hash>`（或自 `.bak` 還原 resume_pipeline.py + git revert section_engine C3 區塊）。

---
### 結論
🟢 rag 旁路抽出 + meta header 重構為純格式化器（引擎零讀 metadata·U3.1 Zero Schema Coupling）、resume 改 delegate、行為等價（42 passed 含 byte 斷言）、SOP 合規、640 基線、接縫 key 零位移。**section_engine 三簇全抽出**（摘要/翻譯還原/rag+meta）。下一步 C4 引擎測試 + key-changing 整合測試雙鎖。
