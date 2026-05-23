# TODO 新增 MODEL 系列候選 — 執行報告

> **基準**：`70889aa`（Phase 4.7e Commit 7e-2 v2 / 已 push）後 TODO `7168 bytes` 版本
> **狀態**：本地改檔完成，**未 commit、未 push**（`.claude-logs/` gitignored）
> **改動範圍**：**只動 `.claude-logs/TODO.md`** + 新增本執行報告；零業務檔改動

---

## §1 改動類型摘要（純新增、不刪資料）

| 改動類型 | 數量 | 細節 |
|---|---|---|
| 新增分組（active 區） | 2 個 | `### 🔵 候選（待 baron 評估）` + `### 🚫 評估後不做` |
| 新增 MODEL 項目 | 5 個 | MODEL-1+2 / MODEL-3 / MODEL-5 / MODEL-9 / MODEL-10 |
| 新增「不做」評估 | 5 條 | Parent-Child Indexing / 128 Batching / 企業 Proxy / AUTO Grounding / Pipeline 解耦重構全套 |
| 新增索引分組 | 1 個 | `### MODEL（5 項候選、待評估）` |
| **刪除資料** | **0** | 既有 ✅ 完成表格（Phase 4.7d Chat / RAG / RAG-7 / Phase 4.7e）+ 既有 active（RAG-1 / 2 / 3 / 4 / 5 / 6 / 8 / 9 + CHAT-3b / 4 / 5）+ 既有索引條目**全部保留**

TODO.md size：`7168 bytes` → `11186 bytes` （+4018 bytes、純新增）

---

## §2 新增 5 個 MODEL 項目

依 baron 提供清單、對齊框架 §2.2 / §2.3 格式（狀態 / 編碼 / 工時 / 依賴 / 來源）：

| 編碼 | 主題 | 工時 | 依賴 | 來源 / 簡述 |
|---|---|---|---|---|
| **MODEL-1+2** | 升級 Gemini Embedding 2 + L2 正規化 + 短 chunk 過濾 | 1 commit（合併、同改 EmbeddingModel） | 無（測試機 + < 10 份、backfill 不是顧慮）| `model_optimization_blueprint.md §1`；text-embedding-001 → gemini-embedding-2（768 維 MRL）+ 降維後手動 normalize + chunk ≥ 10 字過濾；是 RAG-3 score 校準前置 |
| **MODEL-3** | 短文 Fast-path Bypass | 1 commit | 無 | `model_optimization_blueprint.md §2.2`；tiling 內若總字數 < max_length（2500）→ 跳過 TextTiling + Embedding；resume / news / web 受益最大 |
| **MODEL-5** | Structured Outputs router | 1 commit | 無 | `model_optimization_blueprint.md §3.2`；Pydantic + Gemini Structured Outputs (JSON Schema) 取代 regex + json.loads；解 router 對格式變動的脆弱性 |
| **MODEL-9** | 連線彈性防禦（提案第四支柱 4.1/4.2/4.3） | 1 commit | 無 | `model_optimization_blueprint.md §4.1-4.3`；4.1 HTTP timeout（Connect 5s / Read 30s / Total 60s）+ 4.2 連線池 Keep-Alive（共享 httpx.Limits / Client）+ 4.3 全隨機抖動指數退避（jitter exponential backoff）；解 baron 觀察的 Gemini 3 Pro Preview `RemoteProtocolError` + SSE 卡死 |
| **MODEL-10** | MinerU SSH/SCP → HTTP API（容器化前置 / 安全強化、**最低優先**） | 2-3 commits（含 MinerU 端改造）| 先確認 MinerU 是否可改 endpoint | `model_optimization_blueprint.md §4.5`；現狀 shell `scp -r` + OS-level SSH key 不可移植 + 容器化阻塞 + 安全漏洞；改 `/file_parse` endpoint 回 JSON 含 base64 / 簽名 URL；視 Docker 化部署需求決定 |

---

## §3 新增 🚫 不做區（5 項評估後排除、附理由）

對齊 baron 提供之清單、確保未來不被「優化建議」反覆勾起：

| 提案 | 不做理由摘要 |
|---|---|
| **Parent-Child Indexing**（雙層檢索） | 履歷已切到 ### 公司層、單份 7-8 chunks、痛點不大；3-4 commits regression 風險高 |
| **128 Batching 自適應**（Embedding API 並行） | 測試機 + < 10 份文件、batch size 增益無感；撞 429 風險上升、「30-50x 提速」是行銷話術（實際 2-3x） |
| **企業 Proxy（HTTP_PROXY/HTTPS_PROXY）** | 個人測試機 + 台灣環境無 firewall / 翻牆需求；未來賣企業客戶再做 |
| **AUTO Grounding（Gemini 自動聯網）** | 論文 / 履歷分析需明確控制資料來源；AUTO 模式下 UX 失控（user 不知道答案來自文件或 Google）；應 user 明確 opt-in |
| **Pipeline 解耦重構（pipeline_decoupling_plan.md 全套）** | 17+ 檔重寫過早抽象；7e-2 v2 KNOWN_DOC_TYPES + check_doc_type_registry 已解 80% 痛點；漸進式小手術可考慮、但全套重構不做 |

放在 active 列表「🟢 低優先」之後、`---` 分隔線之前、索引之前——讓後續任何「優化提議」都能先 grep 確認是否已被評估排除。

---

## §4 索引更新

`## 索引（依類別）` 新增 1 個分組：

```markdown
### MODEL（5 項候選、待評估）
- 🔵 MODEL-1+2 Embedding 2 升級 + L2 正規化（合併、最高 ROI）
- 🔵 MODEL-3 短文 Fast-path Bypass
- 🔵 MODEL-5 Structured Outputs router
- 🔵 MODEL-9 連線彈性防禦（防斷線：timeout / Keep-Alive / jitter retry）
- 🔵 MODEL-10 MinerU SSH/SCP → HTTP（容器化前置、最低優先）
```

位置：插在 `### Chat (3 項 active)` 與 `### Phase 4.7e Resume Independent Pipeline（全完工）` 之間。既有 `### RAG（8 項 active）` / `### Chat (3 項 active)` / `### Phase 4.7e Resume Independent Pipeline（全完工）` 三個分組全部不動。

---

## §5 端到端驗證計畫（baron 自查 grep 指令清單）

實際在 claude-lab 端跑過、結果如下：

```bash
cd /home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50

# 1. 5 個 MODEL 項目都加進去
grep -nE "MODEL-1\+2|MODEL-3|MODEL-5|MODEL-9|MODEL-10" .claude-logs/TODO.md
# 預期：active 列表 5 行 + 索引 5 行 = 共 10 行（實測：130 / 139 / 147 / 155 / 164 + 218 / 219 / 220 / 221 / 222）✅

# 2. 🔵 候選區存在
grep -n "🔵 候選" .claude-logs/TODO.md
# 預期：1 行（實測：line 128）✅

# 3. 🚫 不做區存在
grep -n "🚫 評估後不做" .claude-logs/TODO.md
# 預期：1 行（實測：line 173）✅

# 4. MODEL-9 防斷線細節（timeout / Keep-Alive / jitter）
grep -nE "timeout|Keep-Alive|jitter|抖動退避" .claude-logs/TODO.md
# 預期：至少 3 行（實測：line 156 timeout / 157 Keep-Alive / 221 索引 jitter retry）✅

# 5. 索引內 MODEL 分組
grep -nA 6 "### MODEL（5 項候選" .claude-logs/TODO.md
# 預期：217 標題 + 218-222 五個 ✅

# 6. 既有資料完全保留（RAG-1 / RAG-8 / RAG-9 / CHAT-3b / 7e-2 v2 跨 active + 索引）
grep -cE "RAG-1|RAG-8|RAG-9|CHAT-3b|7e-2 v2" .claude-logs/TODO.md
# 預期：>= 10 行（實測：14 行）✅
```

**6 個 grep 全通過 ✅**——所有既有資料完整保留、5 個 MODEL 項目正確加入、🚫 不做區建立完成、索引同步。

---

## §6 不可動清單遵守狀態

- [x] 業務檔（`processor/*` / `pipeline_core.py` / `web_server.py` / `static/*`）：未動
- [x] `PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（規範本身）：未動
- [x] `.claude-logs/templates/*.md`：未動
- [x] 既有 plan / 執行 / hotfix 報告：未動
- [x] `.claude-logs/model_optimization_blueprint.md` / `google_latest_models_guide.md`（reference 文件）：未動（只 view 不改）
- [x] DB / 設定檔 / 前端：未動
- [x] commit / push：未動
- [x] **TODO.md 資料丟失**：嚴守「只新增、不刪資料」原則——既有所有 ✅ 完成表格、active 高 / 中 / 低三層、索引 3 分組全部保留

---

## 回退方式

未 commit、直接：
```bash
git checkout .claude-logs/TODO.md   # 還原前一版（11186 → 7168 bytes）
rm .claude-logs/2026-05-22_TODO_新增MODEL候選_執行.md   # 移除本報告
```

或精準 revert MODEL 新增區塊（保留 7e-2 v2 + RAG-8/9 改寫部分）：
```bash
# 開 .claude-logs/TODO.md、刪除「### 🔵 候選」+「### 🚫 評估後不做」兩個分組
# 以及索引內「### MODEL（5 項候選、待評估）」分組
```

---

## 狀態

**本地改檔完成、未 commit、未 push**——`.claude-logs/` 整個目錄不入版控（依 `.gitignore:179`）、本機文件即可。等 baron 過目改寫後的 TODO + §5 驗證 6 個 grep 結果後決定是否進一步動作。
