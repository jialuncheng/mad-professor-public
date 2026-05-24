# Phase 4.7e Commit 7e-1c hotfix — 執行報告（prompt 加「投遞元資訊」排除 + 主標題優先順序）

> 基準：7e-1 v2 改動（5 個檔、本地未 commit）
> 完成：**只動 `prompt/doc/resume_vision.txt`、+48 行**
> 等 baron 重跑 vision test 對黃忠偉確認後再 commit

---

## Commit Hash

**尚未 commit**——hotfix 等 baron 確認黃忠偉 case 解決。

| # | Hash | Subject |
|---|---|---|
| 7e-1c | _（pending）_ | fix(resume): prompt 加「投遞元資訊」排除 + 主標題抽取優先順序（hotfix 黃忠偉 case） |

---

## diff stat（uncommitted）

```
 prompt/doc/resume_vision.txt | 48 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 48 insertions(+)
```

**改動 surface area**：單檔、純 prompt 增補、零 code change、零 test change。

---

## 真因

7e-1 v2 在 OrcStack 跑 vision test 6 份履歷實測：

| 履歷 | 結果 |
|---|---|
| DeHunt_CTO_Tzung-Yuan_Lee | ✅ 成功 |
| CV_Chinyu_Lin_2308 | ✅ 成功 |
| YuLun_Wu_CV | ✅ 成功 |
| 江元杰 | ✅ 成功 |
| Priyal_Shah_CV | ⚠ API 暫斷（3 次 retry RemoteProtocolError、非 prompt 失敗） |
| **黃忠偉** | ❌ `PDFParseError "first_line='光聚晶電聯合股份有限公司'"` |

**重要修正**：「光聚晶電」**是黃忠偉履歷的投遞目標公司（應徵抬頭）、不是工作經歷的公司**。黃忠偉履歷 PDF 第一頁頂端有「應徵公司：光聚晶電聯合股份有限公司」這種抬頭、Vision 把它當主標題了。

→ 7e-1 v2 prompt 弱點**不是「人名抽取順序」**（已有 5 級 fallback）、**而是「未明列『投遞元資訊』（應徵對象 / 收件人）必須排除」**。validate 階段雖然不在 RESUME_TITLE_BLACKLIST 內（公司名不在黑名單）、所以擋不下；但 Vision 本來就不該抽公司名當主標題。

---

## 修法摘要

在 `prompt/doc/resume_vision.txt` 「主標題規則」段（既有規則最底、原 line 26）後、「絕對禁止」表格（原 line 27）前、新增**兩個 ## 子段落**：

### 新段落 1: `## 排除履歷的「投遞元資訊」（不是候選人本身內容）`

明列 5 類投遞抬頭必須排除：

| 投遞元資訊類型 | 範例 |
|---|---|
| 應徵公司 / 職位 | `應徵公司：XX 股份有限公司`、`應徵職位：XX` |
| 信件式收件人 | `Dear HR Manager`、`To: HR Department` |
| 投遞日期 | `履歷投遞日期：2024/11/22`、`Date of Application` |
| 第一頁頂端非候選人公司 | 公司 logo / 公司全名在 PDF 頂端、但不是候選人服務過 |
| 文件抬頭 | `Resume` / `履歷表`（既有規則延伸） |

明確指示：「**不抽進 markdown 輸出（直接忽略整段抬頭）**、絕對不能當主標題 `#`」。

### 新段落 2: `## 主標題抽取優先順序`

5 級 fallback：

1. 「個人資料 / Personal Info / Basic Info / Contact / 個人基本資料」section 內「姓名」欄位
2. 字級最大、靠近頁面中上區的自然人姓名（且不是抬頭、不是公司名）
3. 「Education / 學歷」section 內提及的人名
4. Email signature / 聯絡資訊區域內人名
5. PDF 檔名包含人名（僅供參考、需與內容對照）

附 4 個區塊：

- **判斷原則**：候選人姓名必須是自然人、不是組織 / 公司 / 機構
- **Vision 看 PDF 時的常見錯誤模式**：3 種（把最大視覺元素當主標題 / 最近工作當開頭 / 文件標題列當主標題）
- **黃忠偉履歷實測 case**：顯式範例「PDF 頂端是『應徵公司：光聚晶電』抬頭、底下『個人資料』section 內才是『姓名：黃忠偉』、正確 `#` = `# 黃忠偉`」
- **極端 fallback**：人名真的找不到時用 PDF 檔名 → 通用詞 → 「Candidate」、validate 會 log warning

---

## 不可動清單（已遵守）

- [x] `processor/resume_processor.py`：未動（v2 既有 validate 已能擋下黑名單、邊界 case 改由 prompt 預防）
- [x] `llm/client.py`：未動
- [x] `tests/test_resume_processor.py`：未動（無新測試需求、prompt-only fix）
- [x] `tools/test_resume_vision.py`：未動
- [x] `pipeline_core.py` / `doc_analyzer.py` / 任何其他 processor：未動
- [x] DB / 前端 / web_server：未動
- [x] commit / push：未動

---

## 驗證結果（claude-lab 端）

```bash
git status -s
# M prompt/doc/resume_vision.txt   ← 唯一改動

venv/bin/pytest tests/ -q
# 143 passed, 3 skipped（與 7e-1 v2 baseline 完全一致、零回歸）

git diff --stat prompt/doc/resume_vision.txt
# 1 file changed, 48 insertions(+)
```

---

## 端到端驗證（給 baron 跑 OrcStack）

### Step 1：重跑 6 份 vision test

```bash
rm -rf .claude-logs/_phase_4_7e_outputs
venv/bin/python tools/test_resume_vision.py 2>&1 | tee /tmp/v2c_vision_test.log
```

### Step 2：檢查所有 6 份主標題（必須全是自然人姓名）

```bash
for d in DeHunt_CTO_Tzung-Yuan_Lee 黃忠偉 江元杰 CV_Chinyu_Lin_2308 YuLun_Wu_CV Priyal_Shah_CV; do
  echo "--- $d ---"
  head -1 .claude-logs/_phase_4_7e_outputs/$d/$d.md 2>/dev/null
done
```

預期：

| 履歷 | 預期主標題 |
|---|---|
| DeHunt_CTO_Tzung-Yuan_Lee | `# Tzung-Yuan Lee (李宗原)` |
| **黃忠偉** | **`# 黃忠偉`**（**hotfix 重點**：非「光聚晶電聯合股份有限公司」）|
| 江元杰 | `# 江元杰 (Steven Chiang)` 或 `# 江元杰` |
| CV_Chinyu_Lin_2308 | `# Chin-Yu Lin 林晉羽` |
| YuLun_Wu_CV | `# 吳焴倫` |
| Priyal_Shah_CV | `# Priyal Shah (李思雅)` 或 `# Priyal Shah`（若 API 仍斷則 PDFParseError）|

### Step 3：黃忠偉特別檢查——投遞抬頭被移除

```bash
echo "=== 黃忠偉前 30 行（檢查光聚晶電是否被移除）==="
head -30 .claude-logs/_phase_4_7e_outputs/黃忠偉/黃忠偉.md 2>/dev/null

echo ""
echo "=== 黃忠偉 markdown 內是否還包含「應徵」/「光聚晶電」？==="
grep -nE "應徵|光聚晶電" .claude-logs/_phase_4_7e_outputs/黃忠偉/黃忠偉.md 2>/dev/null
```

預期：
- 前 30 行第一行 = `# 黃忠偉`
- 中文 section 名（個人資料 / 學歷 / 工作經歷 / 自傳 / 求職條件 / 語文能力 等）原樣保留
- grep 結果**為空**——或者「光聚晶電」只在工作經歷的某個位置出現（**不是頂端、不是主標題**）；若黃忠偉真的有「應徵：光聚晶電」原樣 metadata 抬頭被完全移除是最理想

### Step 4：其他 5 份不受影響

特別檢查 DeHunt + 江元杰仍正確（v2 已驗 ✅、hotfix 不該破壞）：
- DeHunt：FOCALTECH / NOVATEK 仍被補抽為 ###
- 江元杰：plain text 公司（河洛 / 大昌瑞台）仍被補抽

### Step 5：structure_check warnings

- 理想：6 份全部「✓ 無 warnings」
- 可接受：Priyal_Shah_CV API 斷線（非 prompt 失敗、本 hotfix 無關）

---

## 已知風險

| 風險 | 等級 | 說明 |
|---|---|---|
| Vision 仍偶爾失準（如把投遞日期當「履歷年份」抽進輸出） | 🟡 中 | 「投遞元資訊」判別需 LLM 推理、邊界 case 多；可能需 1-2 輪 prompt 迭代加更具體範例 |
| 「應徵公司」也可能是候選人真的服務過的公司（罕見、但 prompt 可能誤判） | 🟢 低 | prompt 強調「投遞抬頭」位置上下文（PDF 第一頁最頂端、字級大、但不是工作經歷區段內）；下游 md_cleaner 7a + heading_fix 仍有雙保險 |
| Priyal_Shah API 暫斷無解 | 🟢 低（非 prompt 問題） | retry 已 3 次、若 API 不穩 baron 端只能重跑；若仍斷需查 GEMINI_API_KEY 配額 |
| 黃忠偉 hotfix 後可能換出其他 case | 🟡 中 | 投遞元資訊偵測加強可能誤刪某些罕見 layout 的真實內容；6 份樣本實測為主要驗證手段 |
| 極端 fallback（檔名 / Candidate）尚未實測 | 🟢 低 | 6 份樣本都不會觸發；prompt 文字明列、validate 不阻擋 |

---

## 後續

- baron 跑 vision test 6 份：
  - 全部成功（或 Priyal_Shah API 仍斷但不算 prompt 失敗）+ 黃忠偉主標題 = `# 黃忠偉` + 投遞抬頭被移除 → **commit 7e-1c hotfix**
  - 仍失準 → 再迭代 prompt（如加更多投遞抬頭範例、加 few-shot）
- commit 後可繼續 7e-2 pipeline 整合（baron Q6: doc_analyzer 不短路、Q7: md_cleaner 跳過 resume）

---

## 回退方式

未 commit、直接：
```bash
git checkout prompt/doc/resume_vision.txt
```

---

## 狀態

**本地改檔完成、未 commit、未 push**——等 baron 重跑 vision test 確認：
1. 黃忠偉主標題 = `# 黃忠偉`
2. 黃忠偉 markdown 內「應徵公司：光聚晶電」抬頭被移除
3. 其他 5 份不受影響（特別 DeHunt / 江元杰 / CV_Chinyu_Lin / YuLun_Wu）

確認後 commit `7e-1c hotfix` → 進 7e-2 pipeline 整合。
