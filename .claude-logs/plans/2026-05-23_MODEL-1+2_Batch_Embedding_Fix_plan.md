# Phase 4.7? Commit MODEL-1+2-Fix — Plan：修正 gemini-embedding-2 批次聚合 Bug 與 Translate 並行化優化

> 本文件為**純分析與設計計畫**，在計畫獲得確認前，**嚴禁修改任何業務代碼與配置**（可修改此 Markdown 計畫本身）。

---

## TL;DR

- **問題與挑戰**：
  1. **RAG 向量化極慢**：使用 `tools/regen_rag.py --all --force` 批次重建向量庫時，發生 `[WARNING] 批次 1 失敗（批次回傳數量不符: 期望 32 實得 1），退回逐筆模式`，使 RAG 階段退化為緩慢的單筆循序網路請求。
  2. **翻譯階段（Translate）絕對效能瓶頸**：履歷分析總耗時高達 `368s` ~ `451s`（約 6-7.5 分鐘），其中 `translate` 單一階段便佔用了 **63% ~ 70%** 的時間（如 `DeHunt_CTO` 翻譯耗時 **287.35s**），成為系統最嚴重的卡頓點。
- **核心根因**：
  1. **SDK 批次聚合 Bug**：在 `google-genai` SDK 中，`contents` 傳入純字串列表會被自動合併為一個單一的 `Content` 物件，導致後端只回傳 1 個聚合向量。
  2. **翻譯採循序同步阻塞設計**：`TranslateProcessor` 內對所有章節標題、子標題、正文段落與圖表說明，全部採用 `for` 迴圈進行**序列化同步 LLM 調用**。一個段落耗時 4-5 秒，50 個段落即產生 250 秒的實打實等待，高配額的企業級 API 優勢完全被序列化等待抵消。
- **設計解法**：
  - **解法一（RAG 批次）**：將批次中的每個字串顯式包裝為 `types.Content(parts=[types.Part(text=t)])` 繞過 SDK 聚合 Bug，恢復 32 點並行。
  - **解法二（翻譯並行）**：利用 `ThreadPoolExecutor` 對**標題翻譯**進行全收集並行處理；並對**各大章節內容**進行分章並行翻譯，各章節內部的段落依然保持循序，以保留 `previous_translation` 上下文一致性。
- **影響範圍**：修改 `config.py`（向量化）與 `processor/translate_processor.py`（並行翻譯），不影響任何資料庫 Schema 或外部 API 簽名。
- **優化預估**：
  - RAG 向量化時間縮短 **10~20 倍**（從 8 秒降至 <0.5 秒）。
  - 翻譯耗時縮短 **7~10 倍**（從 280 秒暴降至 **30~40 秒** 內）。

---

## 1. 現況盤點

關鍵程式碼邏輯與呼叫鏈位置：

- **[config.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/config.py)**：
  - `EmbeddingModel.embed_documents(self, texts: list) -> list` [L96-L146]：負責執行 RAG 重建時的批次向量化。
- **[processor/translate_processor.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/processor/translate_processor.py)**：
  - `translate_titles(self, data)` [L69-L83]：循序翻譯主標題與所有子章節標題。
  - `translate_content(self, data)` [L171-L174]：循序呼叫 `translate_section_content`。
  - `translate_section_content(self, sections)` [L176-L204]：遞迴並循序遍歷所有章節內的文字 block 與圖表 caption。

---

## 2. 觀察到的問題與證據

### 問題 #1：`gemini-embedding-2` 批次嵌入回傳數量不符 (實得 1)

- **證據**：執行向量重建時，日誌輸出警告：
  ```
  [WARNING]  2026-05-23 17:03:23,051 - config - 批次 1 失敗（批次回傳數量不符: 期望 32 實得 1），退回逐筆模式
  ```
  這是因為新版 `google-genai` SDK 中的 `t_contents` 轉換器會將純字串列表 `['text1', 'text2']` 聚合為單一 `Content` 物件，導致後端只回傳 1 個向量。

### 問題 #2：翻譯階段循序同步阻塞，吃掉 70% 整體時間

- **證據**：測試機真實執行日誌：
  ```text
  [INFO] 2026-05-23 18:12:29,207 - [stage] DeHunt_CTO_Tzung-Yuan_Lee extra_info 開始
  [INFO] 2026-05-23 18:12:29,202 - [stage] Priyal_Shah_CV translate 完成 耗時=263.66s（並行）
  [INFO] 2026-05-23 18:12:32,931 - [stage] Priyal_Shah_CV extra_info 完成 耗時=6.95s
  [INFO] 2026-05-23 18:12:32,931 - [stage] Priyal_Shah_CV rag 開始
  [INFO] 2026-05-23 18:12:38,487 - [stage] DeHunt_CTO_Tzung-Yuan_Lee extra_info 完成 耗時=9.28s
  [INFO] 2026-05-23 18:12:38,487 - [stage] DeHunt_CTO_Tzung-Yuan_Lee rag 開始
  [INFO] 2026-05-23 18:12:40,657 - [stage] Priyal_Shah_CV rag 完成 耗時=7.73s
  [INFO] 2026-05-23 18:12:43,317 - [pipeline] Priyal_Shah_CV 全部完成 總耗時=368.50s
  [INFO] 2026-05-23 18:12:51,295 - [pipeline] DeHunt_CTO_Tzung-Yuan_Lee 全部完成 總耗時=451.12s
  ```
  在 `logs/*.log` 中**完全沒有出現任何 Rate limit 429 限制**的退避紀錄。這鐵證如山地表明，速度慢不是因為配額不足，而是因為正文段落被 sequential 方式一個一個發送，累積產生了將近 5 分鐘的無謂網路等待。

---

## 3. 設計方案

### 3.1 改造 `config.py` — 繞過 SDK 批次聚合 Bug

- **目標**：手動將批次中的純字串包裝為 `types.Content(parts=[types.Part(text=t)])` 列表。
- **關鍵代碼設計**：
  ```python
  formatted_contents = [
      types.Content(parts=[types.Part(text=t)])
      for t in batch
  ]
  result = self.client.models.embed_content(
      model=self.model,
      contents=formatted_contents,
      config=types.EmbedContentConfig(
          task_type="RETRIEVAL_DOCUMENT",
          output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
      )
  )
  ```

### 3.2 改造 `translate_processor.py` — 雙層並行翻譯優化

#### 1. 標題翻譯並行化（Title Parallelization）
收集主標題與所有遞迴章節、子章節標題，丟入 `ThreadPoolExecutor` 進行多線程並行翻譯，最後一次性回填。
```python
def translate_titles(self, data):
    from concurrent.futures import ThreadPoolExecutor
    tasks = []
    # 遞迴收集主標題與所有子章節標題任務...
    # 使用 ThreadPoolExecutor(max_workers=10) 並行發送
    # 將結果回填回原字典
```

#### 2. 正文大章節並行化（Section Parallelization）
不同大章節（例如「工作經歷」、「教育背景」）之間是完全獨立的，使用 `ThreadPoolExecutor` 並行分配處理。每個大章節內部的段落翻譯依然維持**循序進行**，這能完美保留原有章節內前後句翻譯一致性的 `previous_translation` 參考機制。
```python
def translate_content(self, data):
    if "sections" not in data:
        return
    from concurrent.futures import ThreadPoolExecutor
    non_abstract_sections = [s for s in data["sections"] if s.get("type") != "abstract"]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(self.translate_section_content, [section])
            for section in non_abstract_sections
        ]
        for future in futures:
            future.result() # 阻塞等待所有大章節並行完工
```

---

## 4. 變動風險與相容性評補

- **相容性衝擊 (Breaking Changes)**：無。`TranslateProcessor` 的輸入與輸出格式 100% 不變，對管線下游的 `RestoreProcessor` 及資料庫寫入透明。
- **性能正向衝擊**：由於用戶為 GCP 企業帳戶產出的 API Key，享有高達數百 RPM 的超高配額，因此多線程並行能夠 100% 吃滿帶寬。翻譯時間預計能降到 **30秒內**，帶來萬分顯著的流暢體驗。

---

## 5. 測試計畫與端到端（E2E）驗證計畫

### 5.1 自動化單元測試

- **既有測試執行**：
  ```bash
  venv/bin/pytest tests/test_embedding_normalize.py -v
  ```
- **測試並行翻譯正確性**：
  我們已在 [scripts/test_parallel_translate.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/scripts/test_parallel_translate.py) 中實作了完整的 Mock 測試，在脫機環境下進行多章節與標題的並行翻譯檢驗，確保回填架構無誤。

### 5.2 手動 E2E 驗證流程

1. 更新測試機代碼。
2. 上傳一份履歷（例如：`DeHunt_CTO_Tzung-Yuan_Lee.pdf`）。
3. 觀察終端機日誌輸出：
   - 預期：`[translate] 開始並行翻譯 N 個標題...`
   - 預期：`[translate] 開始分章節並行翻譯 M 個章節內容...`
   - 檢視 `[pipeline] 全部完成 總耗時=...` 應由原本的 450 秒降至 **30~50 秒** 內，且履歷結構、中文翻譯完整無缺。

---

## 6. 不可做 / 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `translate_processor.py` 內單段翻譯中的 `previous_translation` 上下文邏輯（維持段落一致性，不可打破）。
- [ ] 既有 RAG 檢索分數閾值與評估參數配置（維持原狀）。

---

## 7. 推薦 Commit 拆分與順序

| 序號 | 預期變動內容 | 預估工時 |
|---|---|---|
| **MODEL-1+2-Fix** | 實作 `config.py` 的顯式 Content 包裝與 `translate_processor.py` 雙層並行優化，跑過 pytest 確保全綠 | 1.5 小時 |
