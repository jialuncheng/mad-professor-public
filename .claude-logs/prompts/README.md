# 提示詞資料庫（Prompt Archive）

本目錄存放 baron 給 Claude / Claude Code 的所有提示詞、為日後檢索、改寫、再利用、回顧決策依據用。

## 1. 觸發時機（必須遵守）

**每次收到 baron 的提示詞、Claude / Claude Code 必須先把該提示詞歸檔到本目錄、再執行內容。**

- 觸發條件：baron 在對話內貼出**完整的提示詞**(含「請執行 XXX 階段...」「請修正...」等任務命令式提示詞)
- **不觸發**：純對話式問答(如「跑 git status」「這個結果對嗎」等簡短查詢)
- 判定原則：**只要 baron 的提示詞含「請...」「執行...」「撰寫...」「修正...」等任務命令、或長度 > 500 字、或內含「═══」「## 第X步」等結構化區塊、就歸檔**

判斷模糊時、優先歸檔（寧多勿少、未來可刪、不可重建）。

## 2. 命名規則

`<日期>_<任務代號>_<簡短描述>.md`

- **日期**：`YYYY-MM-DD`、用提示詞收到當天日期
- **任務代號**：跟 commit message / plan / 執行報告對齊
  - 範例：`MODEL-8_C2` / `MODEL-3_B1` / `RAG-8` / `general`
  - 純對話 / 一般任務無代號用 `general`
- **簡短描述**：5-15 字、空格用底線、不用標點

### 範例

- `2026-05-22_MODEL-8_C1_提示詞.md`
- `2026-05-23_MODEL-8_plan修正_納入Docker章節.md`
- `2026-05-23_general_建立提示詞資料庫.md`

## 3. 檔案格式（嚴格）

每份提示詞檔案的 markdown 結構固定如下；外層用 4 個 backtick、內層提示詞 code block 用 3 個 backtick、避免渲染衝突。

````markdown
# <日期> — <任務代號> 提示詞

> **收到時間**：YYYY-MM-DD HH:MM（時區用 baron 當地、若 AI 無法獲取精確系統時間、請直接向 baron 詢問或使用標準 UTC+8）
> **任務代號**：<例：MODEL-8 C2>
> **觸發 commit**：<例：MODEL-8 C2、或 plan 修正、或 general>
> **相關產出檔案**：<例：.claude-logs/2026-05-22_MODEL-8_C2_執行.md>
> **觸發情境**：<1-2 句說明、為何 baron 給這個提示詞、上下文是什麼>

---

## 完整提示詞

```
（這裡完整貼 baron 給的提示詞、一字不漏、含所有 ═══ 分隔線、code block、註解）
```

---

## 執行結果摘要

- ✅/❌ 完成狀態
- pytest baseline → final
- 改動檔案數
- 是否 commit / push（baron 手動執行情況）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````

### 敏感資訊去識別化（入版控強制）

提示詞內若含以下任一、**寫入歸檔前必須打碼**：

- API keys / tokens（`sk-...` / `AIzaSy...` / Gemini / OpenAI / 任何字串長度 > 20 的 alphanumeric secret）
- 密碼 / passphrase
- 個人 email / 電話 / 地址
- 內部 DB connection string（含密碼部分）
- 雲端帳號 ID / project 數字 ID（若 baron 不想公開）

打碼格式：`<REDACTED_API_KEY>` / `<REDACTED_PASSWORD>` 等明確標記、不留原始字串前綴後綴。

## 4. 索引維護（簡化版、避免 token 膨脹）

本目錄根層另有 `INDEX.md`、每次新增提示詞時、Claude Code 必須**同步更新**。

**簡化規則**（避免每次寫檔花費過多 tokens）：
- **「依時間排序」**：僅保留最新 15 筆；超過 15 筆的舊提示詞**從時間表移除**、但仍在「依任務分類」內保留
- 用最單純的 markdown 列表（不用表格）、避免複雜結構導致 token 膨脹與排版衝突
- 索引內**不寫摘要**、只列連結 + 1 行任務代號 + 1 行日期

INDEX.md 結構：

```markdown
# 提示詞資料庫索引

最後更新：YYYY-MM-DD

## 依任務分類

### MODEL-8 SQLite 物理防線
- `2026-05-22_MODEL-8_C1_提示詞.md` — C1 schema + DAL helper
- `2026-05-22_MODEL-8_C2_提示詞.md` — C2 pipeline 寫入
- `2026-05-22_MODEL-8_C3_提示詞.md` — C3 CLI
- `2026-05-23_MODEL-8_plan修正_6個審查問題.md` — plan v3 修正
- `2026-05-23_MODEL-8_plan修正_納入Docker章節.md` — Docker §5 納入

### MODEL-3 tiling 三合一
- `2026-05-22_MODEL-3_B1_提示詞.md` — B1 短文 Bypass
- `2026-05-22_MODEL-3_B2_提示詞.md` — B2 公式穿透
- `2026-05-22_MODEL-3_B3_提示詞.md` — B3 段落滑動

### 一般 / 工具
- `2026-05-23_general_建立提示詞資料庫.md` — 建立 prompts/ 資料庫骨架

## 依時間排序（最新 15 筆）

- 2026-05-23 — `2026-05-23_general_建立提示詞資料庫.md`
- 2026-05-22 — `2026-05-22_MODEL-8_C3_提示詞.md`
- 2026-05-22 — `2026-05-22_MODEL-8_C2_提示詞.md`
- ... (最多 15 筆、超過則只保留在「依任務分類」)
```

## 5. 不可動清單

- 本目錄內既有檔案：除非 baron 明確要求改寫、否則**不修改**（歷史記錄不可竄改）
- 命名規則 + 檔案格式：嚴格遵守、不偷懶
- 入版控（修正 1 方案 A）：除非 baron 明確指示改回排除、否則維持目前 `.gitignore` 設定
