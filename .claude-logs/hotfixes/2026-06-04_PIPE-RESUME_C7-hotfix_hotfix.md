# PIPE-RESUME Commit C7-hotfix — 緊急熱修復：ResumePipeline 策略註冊缺失與加載鏈修復

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正前一次 Commit 落地後立即發現的嚴重阻斷性 Bug 或 Regression。
> **修復原則**：只改動受災點程式碼，嚴禁夾帶任何無關的新功能或大型重構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **C7-hotfix** | `待 baron 回填` | fix(pipeline): import resume_pipeline to trigger factory registration |

---

## 阻斷性問題與真因

詳細記錄發生的 Regression 或 Block 問題，以及造成此問題的直接真因：

### 1. 阻斷現象 (Block Issue)
- **現象描述**：啟用影子測試上傳履歷 PDF 時，系統在處理影子論文的 Phase 1 階段崩潰，拋出 `NotImplementedError`，無法正常進行影子比對。
- **受災範圍**：`web_server.py` 的影子派發路徑中，`resume` 文體的處理完全中斷。
- **首發日誌/錯誤堆疊**：
  ```json
  {"timestamp": "2026-06-04 21:50:39,328", "level": "WARNING", "logger": "pipelines.factory", "message": "[factory] doc_type='resume' 未註冊且無 litedoc，回 NullStrategy 哨兵"}
  {"timestamp": "2026-06-04 21:50:39,328", "level": "INFO", "logger": "pipelines.orchestrator", "message": "[orchestrator] run paper=DeHunt_CTO_Tzung-Yuan_Lee_shadow doc_type=resume shadow=True strategy=NullStrategy"}
  {"timestamp": "2026-06-04 21:50:39,329", "level": "ERROR", "logger": "__main__", "message": "影子論文處理失敗（不影響 A 軌正本）: owner=1 DeHunt_CTO_Tzung-Yuan_Lee_shadow - 骨架階段無具體策略（NullStrategy）；具體五路實作屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK plan", "trace_id": "5900caa0", "owner": "baron", "path": "/api/papers/upload", "method": "POST", "exception": {"type": "NotImplementedError", "message": "骨架階段無具體策略（NullStrategy）；具體五路實作屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK plan", "stacktrace": "Traceback (most recent call last):\n  File \"/home/baroncheng/mad-professor-public/web_server.py\", line 633, in run_pipeline_shadow\n    await loop.run_in_executor(None, lambda: Orchestrator().run(ctx))\n  File \"/usr/lib/python3.12/concurrent/futures/thread.py\", line 58, in run\n    result = self.fn(*self.args, **self.kwargs)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/baroncheng/mad-professor-public/web_server.py\", line 633, in <lambda>\n    await loop.run_in_executor(None, lambda: Orchestrator().run(ctx))\n                                             ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/baroncheng/mad-professor-public/pipelines/orchestrator.py\", line 91, in run\n    result = getattr(strategy, runner_name)(ctx)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/baroncheng/mad-professor-public/pipelines/base_strategy.py\", line 59, in run_phase1\n    raise NotImplementedError(self._MSG)\nNotImplementedError: 骨架階段無具體策略（NullStrategy）；具體五路實作屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK plan"}}
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：`pipelines/resume_pipeline.py` 使用 `@PipelineFactory.register('resume')` 裝飾器進行惰性註冊。然而，在系統初始化啟動鏈（包括 `pipelines/__init__.py` 或 `web_server.py`）中，**從未導入 `pipelines.resume_pipeline` 模組**，導致 Python 啟動時該模組未被加載，裝飾器未被執行，註冊表為空。
- **定位程式碼**：[pipelines/__init__.py](file:////Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/pipelines/__init__.py#L1-L32)（缺少對 `resume_pipeline` 的顯式加載）。

---

## 熱修復修法 (Minimal Hotfix)

本修復採取的**最小侵入式**解決方案：

### [pipelines/__init__.py](file:////Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/pipelines/__init__.py) — 最小改動
```diff
@@ -16,2 +16,6 @@
 from pipelines.factory import PipelineFactory
 from pipelines.orchestrator import Orchestrator, OrchestratorError
+
+# === [PIPE-RESUME C7-hotfix START] ===
+from pipelines import resume_pipeline
+# === [PIPE-RESUME C7-hotfix END] ===
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
在開發機上執行 pytest 確保全套件不受影響：
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -v
```

### 2. 本地 E2E 快速復現與驗證
在開發機上執行以下指令，驗證 `PipelineFactory` 內部的註冊表是否已被正確填入 `resume` 策略：
```bash
$ venv/bin/python -c "from pipelines.factory import PipelineFactory; import pipelines; print(PipelineFactory._registry)"
# 期望輸出包含：'resume': <class 'pipelines.resume_pipeline.ResumePipeline'>
```

---

## 回退與備案

```bash
# 退回到最初安全穩定版本的 Commit (C6)
git reset --hard fabb114
```

---

## 銜接與注意事項（架構一致性 + 執行期強制約束）

### 1. 五路一致性（後續任務必遵）
本 hotfix **範圍只修 `resume` 一路、正確**。但 `@PipelineFactory.register(...)` 為惰性註冊（import 時才觸發），故**未來四路（PIPE-VISUAL / PIPE-ACADEMIC / PIPE-LITEDOC / TRANSLATE-BOOK）落地時，每一路都必須在 `pipelines/__init__.py` 補同款 `from pipelines import <xxx>_pipeline`**，否則 runtime `get_strategy('<doc_type>')` 同樣回 `NullStrategy` 並在 P1 拋 `NotImplementedError`（與本次現象一致）。

**收斂建議（後續任務、非本 hotfix 範圍）**：可將五路註冊集中為單一區塊（如新建 `pipelines/_register.py` 統一 import 五路，或於 `__init__.py` 末尾以註解標記的「策略註冊區」統一 import），避免每路各自零散 import 漏網。本 hotfix 不做此收斂（最小侵入原則），僅標記為 PIPE-FLIP / 後續五路任務的架構待辦。

### 2. BE-Hotfix 執行期強制約束（.bak + SOP 核查）
本 hotfix 改動 `pipelines/__init__.py`（`.py` 業務代碼）→ 屬 **BE-Hotfix** 工作流，落地執行期須遵守：
- **`.bak` 備份鐵律**：修改前先 `cp pipelines/__init__.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix_init.py.bak`，並於該 hotfix Run 的 `git add` 清單強制包含此 `.bak`（WORKFLOW_SOP §3 備份鐵律）。
- **SOP 一致性核查**：BE-Hotfix 落地前強制執行 logging + database 核查並貼 grep 結果：
  ```bash
  grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/__init__.py   # 期望：無命中（合規）
  grep -nE "\.commit\(\)" pipelines/__init__.py | grep -v "with .*session.*begin\(\)"      # 期望：無命中（合規）
  ```
  本 hotfix 僅新增一行 `import`、無 `logger` 呼叫、無 DB 操作 → 兩項核查**必為空命中（合規）**，但仍須據實貼出「無命中（合規）」以完成審計閉環。
- **註解包裹**：修改區塊已以 `# === [PIPE-RESUME C7-hotfix START/END] ===` 包裹（見上「熱修復修法」），便於人工審計與未來 Flip 移除。

### 3. 實測驗證紀錄（因果確認）
- **修復前**（現狀、僅 `from pipelines import ...`）：`'resume' in PipelineFactory._registry` → **False** → `get_strategy('resume')` 回 `NullStrategy`（與首發日誌完全吻合）。
- **修復後**（`__init__.py` 加 `from pipelines import resume_pipeline`）：全新子程序跑 web_server 同款 `from pipelines import Orchestrator` → `'resume'` **已註冊** → `get_strategy('resume')` 回 `ResumePipeline`、**無循環 import 錯誤**。
- 結論：本 hotfix **對症、修法正確、實測可解**；baron 套用後線上影子 resume pipeline 即正常分派至 ResumePipeline 四 Phase（P1-P4）。
