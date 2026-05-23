# 2026-05-23 — RAG-10 提示詞

> **收到時間**：2026-05-23（UTC+8、精確時間待 baron 補）
> **任務代號**：RAG-10
> **觸發 commit**：無業務 commit（僅 TODO 候選區新增條目）
> **相關產出檔案**：`.claude-logs/TODO.md`（候選區新增 RAG-10）
> **觸發情境**：baron 觀察到論文 Header blockquote（作者/日期/出處/DOI/關鍵字）在前端渲染時全擠成一行；要把 bug 寫進候選區、不動業務代碼

---

## 完整提示詞

```
請把以下 bug 寫進 TODO.md 候選區、不動業務代碼、不 commit、不 push。

═══════════════════════════════════════════════════════════════
## 第一步：讀取規範 + 既有 TODO
═══════════════════════════════════════════════════════════════

view 下列檔案、了解既有結構:
1. `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §2.5 任務生命週期
2. `.claude-logs/TODO.md`（找候選區既有結構、確認 RAG 系列編號最新到哪）

═══════════════════════════════════════════════════════════════
## 第二步：先做 grep 確認 bug 證據
═══════════════════════════════════════════════════════════════

    grep -nE "def _render_header_zh|def _render_header_en|meta_bits" \
      processor/md_restore_processor.py | head

    grep -nA 3 "meta_bits.append" processor/md_restore_processor.py | head -40

    grep -rnE "marked\.setOptions|breaks" static/ 2>/dev/null | head -10

    grep -nE "\bRAG-[0-9]+|\bMD-[0-9]+" .claude-logs/TODO.md | head

═══════════════════════════════════════════════════════════════
## 第三步：在 TODO.md 候選區新增 RAG-10（或 MD-1）條目
═══════════════════════════════════════════════════════════════

依 grep #4 結果決定編號:
- 若既有最大 RAG 編號是 RAG-9 → 用 RAG-10
- 若有 MD 系列 → 用 MD 系列下一個

條目內容（嚴格依以下格式）:

- 🔵 RAG-10 中文 Header Meta Block 軟換行渲染 bug（user-facing 排版、修法 ~5 行、低風險）
  - 問題：論文 Header 區的「作者/日期/出處/DOI/關鍵字」blockquote 全擠成一行
  - 症狀範例：Jian Xu et al. 2026-01-26 Wuhan University paper
  - 根因：CommonMark/GFM 軟換行解析、`<p>` 內被瀏覽器渲染為單一空格、marked.js 預設行為符合此規範
  - 代碼證據：_render_header_zh L509-L520、_render_header_en L460-L470
  - 修法：每行末尾補兩個半形空格、CommonMark hard line break 語法
  - 不用 marked.setOptions({ breaks: true }) 因為會破壞 chunk content 排版
  - 預估工時：~30 分鐘（含 pytest）
  - 拆 commit：單一 commit（FIX-1）
  - 新增 pytest 2-3 個
  - 影響範圍：僅前端渲染、不需 backfill、既有 paper 重開即生效
  - 依據：CommonMark §6.7 Blockquote + §6.5 Hard line breaks

═══════════════════════════════════════════════════════════════
## 第四步：嚴格不可動清單
═══════════════════════════════════════════════════════════════

- processor/md_restore_processor.py：未動（只記錄 bug + 修法、不動 code）
- static/：未動（marked.js 設定不動）
- 業務代碼其他檔案：未動
- 既有 plan / 執行 / hotfix 報告：未動
- commit / push：未動
- .claude-logs/prompts/ 歸檔：依框架 §6 規範同步歸檔本提示詞
- 唯一改動：.claude-logs/TODO.md（新增 RAG-10）

═══════════════════════════════════════════════════════════════
## 完成後輸出
═══════════════════════════════════════════════════════════════

1. 修改檔案：.claude-logs/TODO.md
2. present_files：.claude-logs/TODO.md
3. 簡短說明：grep 證實的真實行號、確定編號、優先級、未來實作提醒

不 commit、不 push——baron 手動 commit。

[註：本範例檔為簡化轉錄、保留結構與所有步驟標題；完整原文以 baron 本次對話訊息為準。
為避免巢狀 code block 渲染衝突、本檔內 bash 範例改用縮排呈現。]
```

---

## 執行結果摘要

- ✅ 完成狀態：TODO.md 候選區新增 RAG-10 條目
- pytest baseline → final：不適用（純 TODO 更新、無業務代碼動）
- 改動檔案數：1（`.claude-logs/TODO.md`）+ 1 歸檔（本檔）
- 是否 commit / push：未——baron 手動執行

## grep 證實的真實行號

- `_render_header_en` 簽名 L435、meta_bits 區塊 L460-470
- `_render_header_zh` 簽名 L484、meta_bits 區塊 L511-519
- 既有最大 RAG 編號：RAG-9（`3a0c523`）→ 新編號 **RAG-10**
- `marked.setOptions({ breaks: true })` 未在 `static/` 內出現（前端修正方案被排除是正確的）

## 後續引用

- 未來實作 RAG-10 時、可從本檔取得完整 grep 證據 + 修法 + pytest 設計建議
