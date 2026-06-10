# PIPE-SLIDES C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 03:59 |
| 任務代號 | PIPE-SLIDES C1 |
| 觸發 Commit | C1 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 同意 tasks 規劃，下達 C1 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C1 — Skeleton & Register / BE-Refactor；tasks §8 C1

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP / tasks（§8 C1）/ logging SOP / database SOP

### 執行命令（tasks §8 C1）
① 改前備份 pipelines/__init__.py → archive/2026-06-11_PIPE-SLIDES_C1_pipelines___init__.py.bak
② 新建 pipelines/slide_pipeline.py：`@PipelineFactory.register('slides')` class SlidePipeline(DocumentStrategy) 四方法 stub（合約最小形）+ `rag_char_threshold=3`（新建檔免中段包裹）
③ 修改 pipelines/__init__.py：補 import slide_pipeline（`# === [PIPE-SLIDES C1 START/END] ===` 包裹、C7-hotfix 教訓）
④ 新建 tests/test_slide_pipeline.py：factory._registry 含 'slides' + get_strategy 回 SlidePipeline 非 NullStrategy
- 物理防線：僅三檔；其餘不可動

### 驗收（§6.1）
- grep：register('slides') / __init__ import；pytest 分派測試綠 + 全套件不退化

### TODO 同步
- C1 ✅、C2 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C1_執行.md（暫存、不入版控）；template_execution

### §8 baron 命令
- git add：slide_pipeline.py + test + __init__.py + .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C1_msg.txt

### 停止
- 產出 C1_執行.md 後立即停止；不續 C2、不自發 commit/push
