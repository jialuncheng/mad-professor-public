# WORKFLOW-1 v4 第二輪評估報告（Claude Code 篇）

> 本文件為 Claude Code 對 WORKFLOW-1 v4 改版規劃書的第二輪可行性評估。
> 採 v4 §2 拆分式結構（§0 簡頂 + §99 末尾）撰寫、作為拆分式設計的第一個試點。

---

## §0 改版規則（極簡靜態頂部）

- 改版觸發：v4 第二輪 baron 拍板後本報告過期、屆時由 Antigravity 覆核版本取代
- 重複防護：本報告只寫「Claude Code 視角的技術判定」，不重複 v3/v4 規劃書既有內容
- 完整治理規格 → 詳見文末 §99

---

## §1 v4 整體三級結論

### 結論：🟢 全採納

**整體理由（4 句）**：

1. **v4 一次性解決了第一輪的三大歧見**：§0 拆分式設計消除快取殺手、template_specification 避免格式一刀切、模板 D 分級 + 項目 8 把驗證成本控制在合理範圍——三個 P0 決策都落地成可執行設計，不是概念。

2. **baron 提出的 baton 資料夾是本輪最優秀的設計**：比 Antigravity 原提議（寫進 CLAUDE_CODE_ENTRY 破壞快取）更聰明，把動態內容物理隔離到 `baton/` 目錄，靜態文件前綴完整保護。

3. **結構性風險已從「高」降至「低」**：v4 的五類工作流、§99 末尾錨點、被引用方自動掃描、DOC-Refactor 新增，每一項都對齊了第一輪評估發現的盲點（Q11-Q16 全部被 v4 響應）。

4. **唯一殘留的結構性問題**：v4 §8 的「兩方案」呈現讓 baron 多了一個決策點，但 S1-S5 選題設計清晰，第二輪評估後可直接拍板進入落地，不需要 v5。

**baron 真正獲得的好處（v4 vs v3）**：

| 項目 | v3 | v4 | 淨收益 |
|---|---|---|---|
| §0 快取影響 | 🔴 破壞前綴 | 🟢 極簡靜態 3 行 | 每份穩定文件省 ~600 tokens/session |
| 規格文件適配 | 🔴 強制 §11 九章節 | 🟢 template_specification 3 章節 | api_audit 等文件可直接套用 |
| 模板 D 成本 | 🔴 73k tokens/commit | 🟢 25k tokens（核心 3 項） | 一般 commit 節省 ~65% |
| AI 交接摩擦 | 🔴 需 baron 中介 | 🟢 baton/ 資料夾自動傳遞 | 減少 ~2 輪 baron 介入 |
| 純文件改版 | 🔴 無對應工作流 | 🟢 DOC-Refactor 第五類 | WORKFLOW-1 自身可正確分類 |

---

## §2 §8 混合方案 S1-S5 第二輪選擇

### S1：方案 A（10 commit）vs 方案 B（9 commit + WORKFLOW-1-2b）

**我的推薦：方案 B（9 commit + 2b）**

**理由**：

方案 B 的 `WORKFLOW-1-2b` 把「把 §0 從頂部改為拆分式」這個**規則性改動**單獨成一個 commit，讓它原子可逆。方案 A 把這個改動合進 `1-2`（與 template §0 加入混在一起），如果事後 baron 反悔拆分式設計，方案 A 無法單獨回退規則改動。方案 B 雖然多一個 commit，但每個 commit 的語意更純粹，符合既有框架 §1.2「小步快跑、獨立可逆」原則。

方案 A 的優點是 10 個 commit 視覺上清晰、沒有「2b」這種夾縫編號，但語意混濁是真實代價。

**對 Antigravity 推薦的預期**：Antigravity 推薦方案 B，因為 `2b` 是 Antigravity 自己提議的、且在 Antigravity 評估報告 §9 中已明確列出。預計雙方一致，baron 可直接採納方案 B。

---

### S2：baton 資料夾建檔放哪個 commit

**我的推薦：WORKFLOW-1-4（隨 CLAUDE_CODE_ENTRY）**

**理由**：

baton/ 的讀取規則寫在 CLAUDE_CODE_ENTRY.md 內（v4 §6.4：「Step 2 讀 baton/*.md」）。若 baton/ 在 `1-3`（WORKFLOW_SOP）就建立，而 `1-4`（CLAUDE_CODE_ENTRY）才寫入讀取規則，會有一個 commit 區間讓目錄存在但沒有任何文件引用它——令人困惑。

**1-4 建 baton/ 的好處**：
- `CLAUDE_CODE_ENTRY.md` + `baton/README.md` 同一個 commit 建立，讀取規則和目錄同時就位
- commit 語意完整：「新增 Claude Code 入口點，包含 baton 交接機制」
- Rollback 時入口和目錄一起回退，不留孤兒目錄

---

### S3：template_specification.md 章節數

**我的推薦：維持 v4 §3.1（§0 極簡 + §1-§3 + §99）**

**理由**：

v4 §3.1 的極簡 3 章節設計命中了「只給最基礎必要欄位、其他不約束」的要求：

- §1（規格目的與範圍）= 讓讀者知道這份規格管什麼
- §2（核心規格內容）= 完全自由，允許 api_audit 用表格、db_analysis 用 ER diagram 描述、logging SOP 用條列
- §3（不可違反的硬規則）= 讓 Claude Code 執行時有明確的「不可動」邊界

再加 §4、§5 等等會讓 template_specification 跟 template_revision_plan 越來越像，失去存在意義。極簡是刻意設計。

---

### S4：DOC-Refactor 是否拆為 DOC-Refactor + DOC-Hotfix

**我的推薦：不拆**

**理由**：

v4 §7.4 已給出最好的解釋：DOC 類改動通常牽動多份文件（例如 SOP 更新同時影響框架引用），即使單份文件 < 10 行，也通常不是孤立的，仍適合走 DOC-Refactor 最小 plan。

若拆出 DOC-Hotfix，baron 和 Claude Code 的判定負擔會增加一層（現在已有 5 類 + hotfix 2 類 = 7 個判定路徑，再加 1 個是 8 個），收益卻極低——DOC 類的「hotfix」場景（typo 修正、單行補充）直接走 DOC-Refactor 最小 commit（1 個 commit、無需完整 plan）即可處理。

如果真的出現 DOC < 10 行的 typo 場景，在 DOC-Refactor §4.5 加一句：「若改動 < 3 行且無跨文件影響，可直接走最小 commit（無需 _plan.md）」，比新增第六類更輕量。

---

### S5：§99 編號是否合適

**我的推薦：保持 §99**

**理由**：

§99 的跳號設計是**刻意的視覺錨點**，不是 bug：
1. §99 明確傳達「這是文件末尾的永久治理區」——任何讀者看到 §99 都能立刻知道這裡不是主要內容
2. 跟 HTTP 狀態碼 / Unix exit code 的習慣類似，「跳號」本身就是一種 convention（例如 §1xx / §2xx / §9xx 分組）
3. §90 反而更奇怪——看起來像文件有 §1-§90，但實際上沒有

**關於 TOC 工具衝突（見 §5 盲點）**：§99 在 VS Code markdown-toc 等工具中確實會顯示跳號，但 TOC 是視覺工具，不影響 Claude Code 讀取或 GitHub 渲染。功能完整，可以接受。

「文件末尾不編號」的方案（用 `---` + 標題）失去 §99 的錨點一致性——以後在提示詞裡說「讀 §99」就能精準定位，改成無編號就沒有這個能力。

---

## §3 §10 待 AI 評估項目可行性判定

### §10.1 SOP 脫節自動偵測機制

**1. Claude Code 視角下的「靜態掃描常駐指令」是什麼？**

在 Claude Code 生態裡有三種實作方式：

| 方式 | 機制 | 可行性 |
|---|---|---|
| **WORKFLOW_SOP 加 checklist**（最輕量） | 在 §4.2 BE-Refactor / §4.5 DOC-Refactor 執行步驟中加一行：「落地前，grep 正在修改的 .py 檔案，對照 logging_SOP 的 `exc_info=True` / `session.begin` 等關鍵字，確認一致」 | 🟢 零配置、現在就能做 |
| **settings.json PostToolUse hook** | 每次 Edit 工具結束後，觸發一個 bash 腳本比對 SOP 關鍵字 | 🟡 可行，但每次改檔都觸發，噪訊大 |
| **CLAUDE.md 加段常駐規則** | 在 CLAUDE.md 加「每次 BE-Refactor 落地前，必須執行 SOP 一致性核查」 | 🟢 可行，但需 baron 維護 CLAUDE.md |

**2. 「自動觸發脫節警報」的實作方式**

最可行的是**輸出到對話**（最低配置、最高可靠性）：Claude Code 在 plan 或 execution 步驟中主動說「偵測到 paper_manager.py 有 `s.commit()` 裸呼叫，與 database SOP §1 原則 3 衝突，請確認是否修正」。

寫到檔案（如 `sop_conflict_warnings.md`）理論可行，但每次寫都破壞快取、且 baron 可能不會主動看這份檔。

**3. baron 需要的配置**

MVP 版本：**零配置**。只需 WORKFLOW_SOP 加一個 §5「SOP 一致性核查 checklist」段落。

進階版（hook）：
- `settings.json` 加 `PostToolUse` hook，觸發條件為 `tool.type == "write_file" && path.endswith(".py")`
- token 成本：每次 grep ~500 tokens（極低）

**4. 最小可行版本（MVP）實作步驟**

在 `WORKFLOW-1-3`（新增 WORKFLOW_SOP.md）中加入：

```markdown
## §5 SOP 一致性自動核查（BE-Refactor 必跑）

在落地前，執行以下核查（每項 < 5 秒）：

### §5.1 logging SOP 核查
```bash
# 對正在修改的 .py 檔案確認：
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔.py>
# 若用 logger.error：必須含 exc_info=True
```

### §5.2 database SOP 核查
```bash
grep -n "s\.commit()\|session\.commit()" <修改檔.py>
# 若有裸 commit：必須改為 session.begin() 上下文
```

**若發現不一致：暫停落地、在 plan 的「Open Questions」加入衝突點、等 baron 拍板。**
```

這個版本純文字、零配置、可在 WORKFLOW-1-3 一起落地。

**5. 推薦：🟢 立即採納（MVP 文字版）**

MVP 的代價是 WORKFLOW_SOP 多 ~30 行。hook 版（進階）暫緩至有實際需要時再加。

---

### §10.2 快取友善度評分機制

**1. 評分計算邏輯**

「git log diff 位置分析」在技術上可行，但有隱性成本：每次評分都要跑 `git log -1 --follow -p <file>`，對 100+ 份文件跑一遍是 I/O 密集操作。

**更輕量的替代邏輯**：

```bash
# 對每份文件：看最近一次 diff 的起始行位置
last_change_line=$(git log -1 --follow -p "$f" 2>/dev/null \
  | grep "^@@" | tail -1 | grep -oP '\+\K[0-9]+' | head -1)
total_lines=$(wc -l < "$f")
# 若 last_change_line < total_lines * 0.2 → 🔴 警告（在前 20% 有改動）
# 否則 → 🟢
```

成本：每份文件 ~50ms、100 份文件 ~5 秒，可接受。

**2. 評分結果存哪**

推薦新建獨立報告：`.claude-logs/ref/CACHE_FRIENDLINESS_REPORT.md`
- 不混入個別文件的 §99（否則注入本身就破壞那份文件的快取）
- 每次 Antigravity 掃描後更新整份報告
- Claude Code 在 session 開始時可選讀（放讀取序列末尾，低優先）

**3. 觸發點**

最佳觸發：**Antigravity 跑 codebase 掃描時**（不是每次 commit）。因為：
- 每次 commit 觸發 = 頻率太高，快取評分本身的 token 成本積累
- 開新 session 時 = 無法區分「哪些檔案是今天才改動的」
- codebase 掃描 = Antigravity 本來就要讀所有文件，順便評分成本最低

**4. 最小可行版本**

`WORKFLOW-1-10` 新增一個 bash 腳本：`.claude-logs/tools/check_cache_friendliness.sh`

```bash
#!/bin/bash
# 快取友善度掃描（對 .claude-logs/ref/ 所有 .md 文件）
echo "=== Cache Friendliness Report $(date +%Y-%m-%d) ==="
for f in .claude-logs/ref/*.md; do
  last_line=$(git log -1 --follow -p "$f" 2>/dev/null \
    | grep "^@@" | head -1 | grep -oP '\+\K[0-9]+' | head -1)
  total=$(wc -l < "$f" | tr -d ' ')
  if [ -z "$last_line" ]; then
    echo "⬜ UNCHANGED: $f"
  elif [ "$last_line" -lt $(( total * 20 / 100 )) ]; then
    echo "🔴 WARN (top 20%): $f (last change at L$last_line / $total)"
  else
    echo "🟢 OK: $f (last change at L$last_line / $total)"
  fi
done
```

baron 或 Antigravity 可以手動執行，輸出貼入 `CACHE_FRIENDLINESS_REPORT.md`。

**5. 推薦：🟡 試用**

拆分式 §0 + §99 末尾設計已從根本上消除了最大的快取破壞點。評分機制適合在「v4 落地 3 個月後、有足夠的文件修改歷史」時再啟用，現在太早。MVP 腳本可以和 WORKFLOW-1-10 一起落地，先放著，Antigravity 視需要執行。

---

### §10.3 TL;DR 標題 vs § 編號設計

**1. Claude Code Read 工具能否精準跳到指定章節？**

**可以，但有前提**：Read 工具接受 `offset`（起始行）和 `limit`（行數）參數，能精準讀取任意行範圍。問題是 Claude Code 需要**先知道章節的起始行號**才能精準跳讀。

實測（對 v4 規劃書）：
```
全文：628 行 ≈ 4,700 tokens
§2 章節（L89-L147）：58 行 ≈ 435 tokens  
節省：90.7%（若只需讀 §2）
```

但「讀 §2」的前提是知道 §2 在第 89 行。每次閱讀前先 `grep "^## §2" <file>` 取行號 = 額外 ~100 tokens，然後精準讀取 = 節省 ~4200 tokens。**淨收益為正**，值得。

§ 編號（而非 TL;DR 混用）的好處在於：`grep "^## §2"` 的 pattern 一致、不需要記憶「這份文件的 TL;DR 叫什麼」。

**2. 推薦 template_plan.md 章節編號方案**

推薦：**§N 統一編號，TL;DR 改為 §1（保留 TL;DR 語意為子標題）**

```markdown
## §0 來源與審核軌跡（極簡）
...

## §1 TL;DR（概要）        ← 不改 TL;DR 名稱，加 §1 前綴
...

## §2 現況盤點
## §3 問題與證據
## §4 設計方案
## §5 風險評估
## §6 測試計畫
## §7 不可動清單
## §8 Commit 拆分
## §9 開放問題

---

## §99 改版規則與治理規格
```

這樣做：
- 現有歷史 plan 檔案的「## TL;DR」不需改（不溯及既往）
- 新 plan 用 `## §1 TL;DR`，grep pattern 變一致
- 提示詞可以說「只讀 §1-§3」，Claude Code 精準讀取前三章節即可判斷方向

**3. 對既有 plan 檔案的衝擊**

**零衝擊**。「不溯及既往」規則完全適用：
- 歷史 plan 的 `## TL;DR` 不改
- 新 plan 的 `## §1 TL;DR` 也不算破壞，只是新加了 §N 前綴
- 兩種並存不會引發任何系統衝突

**4. 推薦**

在 WORKFLOW-1-2（既有 template 加 §0/§99）時一起把 template_plan.md 的「## TL;DR」改為「## §1 TL;DR（概要）」、其餘章節加 §2-§9 前綴。一個 commit 搞定，不影響歷史。

---

### §10.4 非 .md 檔案命名規則

**1. `.claude-logs/` 未來可能出現的非 .md 檔案**

```bash
find .claude-logs/ -not -name "*.md" -not -type d 2>/dev/null
# → 目前結果：無任何非 .md 檔案
# （.textClipping 已被 baron 清除）
```

**未來可能出現的類型**：

| 類型 | 來源場景 | 預估量 |
|---|---|---|
| `.json` | schema 快照、test fixture、metadata export | 低頻（每季） |
| `.yaml` / `.yml` | CI 配置快照、pipeline config dump | 極低頻 |
| `.txt` | raw text export（如 OCR 結果片段） | 中頻（每月） |
| `.sh` | 工具腳本（如 check_cache_friendliness.sh）| 極低頻 |
| `.textClipping` | macOS 誤建，應 .gitignore 排除 | 應預防 |

**2. 各類型推薦命名規則**

| 類型 | 命名規則 | 範例 |
|---|---|---|
| 任務快照（.json / .yaml）| `YYYY-MM-DD_<任務編碼>_<描述>.<ext>` | `2026-05-24_MODEL-8_schema_snapshot.json` |
| 長期規格（.json）| 無日期前綴（長期生效） | `schemas/paper_schema.json` |
| 工具腳本（.sh）| 無日期前綴，放 `tools/` 子目錄 | `tools/check_cache_friendliness.sh` |
| 臨時導出（.txt）| `YYYY-MM-DD_<來源>_export.txt` | `2026-05-24_RAG-1_ocr_sample.txt` |
| macOS artifacts（.DS_Store、.textClipping）| `.gitignore` 全域排除 | — |

**3. 是否需要 §0 / §99 結構**

**不需要**。非 .md 文件是「資料」或「腳本」，不是「治理文件」：
- JSON/YAML 是結構化資料，治理規則靠 schema 約束
- 腳本由代碼審查（模板 D 項目 8）管理
- §0/§99 是 markdown 文件的治理機制，不適合非文字格式

**4. 具體規則表**

```markdown
## 非 .md 檔案命名規則（.claude-logs/ 適用）

| 規則 | 說明 |
|---|---|
| 任務快照型：加 YYYY-MM-DD 前綴 | 便於按日期找到對應任務的快照 |
| 長期生效型：無日期前綴 | 放各自的子目錄（schemas/ / tools/）|
| 工具腳本：無日期前綴，放 tools/ 子目錄 | 腳本是功能不是紀錄，不需日期 |
| .textClipping / .DS_Store：.gitignore 全域排除 | 防止意外入版控 |
| 嚴禁直接在 .claude-logs/ 根層放裸腳本 | 統一放 tools/ 子目錄 |
```

建議在 WORKFLOW-1-7（命名規則實證）時一起把 `.gitignore` 加入 `*.textClipping` 排除規則。

---

### §10.5 Antigravity 自身快取分析（Claude Code 補充視角）

**此題的 4 個子問題主要由 Antigravity 回答**（Antigravity 能觀察自己的快取行為，Claude Code 無法替代）。以下是 Claude Code 的**跨工具協作補充**：

**v4 流程是否刻意為跨工具快取不共享做優化？**

是的，且優化點是 baton/ 設計：

| 設計決策 | 快取優化效果 |
|---|---|
| 穩定文件讀取順序（framework → SOP → template → 任務）| 兩工具各自建立相同的穩定前綴，cache miss 的文件類型相同 |
| baton/ 動態內容隔離 | 兩工具的 baton/ 讀取都只新增 ~10 行動態內容，不破壞主前綴 |
| §99 Revision 末尾化 | 兩工具讀取任何文件時，前 80% 都是穩定快取前綴 |

**若 baron 同時用 Claude Code + Antigravity，最佳化建議**：

1. **讀取順序對齊**：兩工具的提示詞必須用相同的讀取順序（快取友善排序：framework → WORKFLOW_SOP → SOP → template → 任務規劃書 → TODO → baton）
2. **不在同一個 session 同時啟動**：先跑 Claude Code 建 plan，再跑 Antigravity 驗 commit，保持工作流串行而非並行
3. **baton/ 是唯一應該「讀但不期待快取」的目錄**：兩工具都知道 baton/ 是動態的，不需要特殊處理

---

## §4 六個壓力測試重新實測（A-F）

### 測試 A — 「把按鈕顏色從藍改成綠、就一行 CSS」

- **工作流**：FE-Hotfix（< 10 行 + 純 static/*）
- **讀檔**：CLAUDE_CODE_ENTRY.md → WORKFLOW_SOP §4.3 only
- **回應**：接受，直接執行，產 _hotfix.md
- **v4 新增項目 8 觸發**：🔴 FE-Hotfix 也要稽核 CSS 優先權（dom-reference.md 對齊）
  - 新增動作：確認按鈕顏色不是用 inline style 覆蓋 CSS var，而是修改 CSS 變數或選擇器
- **v4 對齊**：✅

---

### 測試 B — 「重構 paper_manager 快取機制、~80 行」

- **工作流**：BE-Refactor（≥ 10 行 + 純 .py）
- **讀檔**：CLAUDE_CODE_ENTRY.md → baton/ → WORKFLOW_SOP §4.2 → framework → database SOP（快取涉及 session）→ logging SOP
- **回應**：先詢問「快取是 in-memory dict 還是 DB 讀取？」確認後產 _plan.md
- **v4 新增 §10.1 SOP 核查**：在 plan 階段 grep paper_manager.py 內 `s.commit()` 確認無裸 commit
- **v4 對齊**：✅

---

### 測試 C — 「新增 tag 路由 API + UI Modal」

- **工作流**：BE-Refactor(lead) + FE-Refactor(sub)
- **讀檔**：CLAUDE_CODE_ENTRY.md → baton/ → WORKFLOW_SOP §4.1 + §4.2 → database SOP → design/docs/
- **回應**：整合 _plan.md，commit 拆分：BE-1 → BE-2 → FE-1 → FE-2
- **v4 baton/ 效果**：若 Antigravity 已在 baton/ 放 `active_antigravity_to_claudecode_RAG-2_plan.md`，Claude Code 讀到後直接知道目標是 RAG-2_plan.md，省去 baron 中介
- **v4 對齊**：✅

---

### 測試 D — 「順手清理一下 logging 多餘 print」

- **工作流**：模糊 → 主動問
- **回應**：「改動預計幾行？純 .py 還是其他？」
  - < 10 行 + 純 .py → BE-Hotfix，走 WORKFLOW_SOP §4.4
  - ≥ 10 行 → BE-Refactor，走 WORKFLOW_SOP §4.2 + logging SOP
- **v4 對齊**：✅

---

### 測試 E — 「順手把 schema 也改了吧」（越界保護）

- **工作流**：立即退回
- **拒絕話術**：
  > 偵測到越界請求：schema 修改不在 `[執行計劃]` §7 不可動清單範圍（BE-Refactor 默認「無 schema/API 簽名影響」判定）。
  > 依框架 §1.2，本次執行嚴禁觸碰 schema。
  > 建議：請擴充改版規劃書 §5，明確加入 schema 改動範圍，由 baron 確認後另開 commit。
- **v4 對齊**：✅

---

### 測試 F（v4 新增）— 「幫我把 logging SOP 加一節說明 SQL 降噪、改動 ~20 行純 markdown」

- **工作流判定**：DOC-Refactor
  - [判定 1] < 10 行？→ No（~20 行）→ 進入 refactor
  - [判定 2] 主要影響範圍？→ `.claude-logs/ref/2026-05-23_logging_SOP_手冊.md`（.md 文件）→ **DOC-Refactor** ✅
- **讀檔**：CLAUDE_CODE_ENTRY.md → baton/ → WORKFLOW_SOP §4.5 only（不讀 database SOP / design/docs）
- **回應**：接受，產 _plan.md（含 §7 不可動清單：logging SOP §1-§5 既有章節語意不動，僅新增 §6 SQL 降噪）
- **v4 項目 8 觸發**：DOC-Refactor 稽核 §0/§99 拆分式結構、Revision 末尾放置
- **v4 對齊**：✅

---

**五類工作流覆蓋確認**：A-F 六個場景全部正確分流，無漏網。

---

## §5 v4 新盲點（4 個）

### 盲點 1：baton/ 中多個 active 交接棒並存、無優先級機制

**問題描述**：

v4 §6.2 允許 baton/ 內同時存在多個 active_*.md 文件（例如：Antigravity→Claude Code 的 RAG-2 plan 和 Claude Code→Antigravity 的 WORKFLOW-1 commit verify 同時存在）。目前沒有衝突解決規則。

Claude Code 在 CLAUDE_CODE_ENTRY 的「讀 baton/*.md」步驟會讀到兩個 active 交接棒，不知道先做哪個。

**推薦修正**（在 baton/README.md 加一條）：
```markdown
## 衝突規則
- 多個 active 文件同時存在時，依 baron 在提示詞中的明確指示決定優先順序
- 若 baron 未指定，依任務編碼優先級排序：🔴 高優先 > 🟡 中 > 🟢 低
- 若優先級相同，取 **建立時間最新** 的 active 文件
```

---

### 盲點 2：§5「被引用方」自動掃描在多 worktree 場景失效

**問題描述**：

Claude Code Server 的工作環境是 worktree（`.claude/worktrees/hopeful-yalow-902c50/`），但 Antigravity 可能掃描的是 main repo 或另一個 worktree。`被引用方` 的注入依賴「掃描到最新的所有 plan 和執行報告」，若 Antigravity 掃的不是活躍 worktree，會漏掉當前進行中的 plan 引用。

**推薦修正**（在 §5 或 WORKFLOW_SOP 加一條）：
```markdown
## 被引用方掃描範圍
- Antigravity 掃描「被引用方」時，以 baron 指定的 worktree 路徑為基準
- 若未指定，掃 origin/gemini-refactor（main branch）的最新狀態
- WIP worktree 內的引用，只有在 merge 回 main 後才會被自動注入
```

---

### 盲點 3：模板 D 分級制的預設行為未明確文件化

**問題描述**：

v4 §4.3 說「baron 在模板 D 提示詞內明確指定『核心』或『全項』，預設『核心』」。但：
1. 「預設核心」這條規則目前只在 v4 規劃書裡，沒有寫進 CLAUDE_CODE_ENTRY.md 或 WORKFLOW_SOP
2. Antigravity 接到模板 D 提示詞但 baron 忘記標「核心」或「全項」時，應該怎麼做？

若沒有明確文件化，Antigravity 可能：
- 直接跑全部 8 項（浪費 73k tokens）
- 或不跑任何項目（等 baron 補充）

**推薦修正**：在 WORKFLOW_SOP §4 驗證分級章節加：
```markdown
**預設行為**：若提示詞未指定「核心」或「全項」，一律執行核心 3 項。
若在核心 3 項中發現重大問題，主動向 baron 建議升級至全項。
```
這條在 WORKFLOW-1-3（新增 WORKFLOW_SOP）時一起落地。

---

### 盲點 4：§99 跳號在 markdown TOC 工具中的顯示問題

**問題描述**：

VS Code 的 markdown-toc 插件、Doctoc、markdownlint 等工具在處理 §99 時，會生成如下 TOC：

```
- §0 改版規則
- §1 ...
- §2 ...
- §13 v4 跟 v3 的關係
- §99 治理規格（← 視覺跳號，§14-§98 都沒有）
```

這是**視覺問題**，不是功能問題——Claude Code 和 GitHub 渲染完全正常。但對 baron 在本地 VS Code 預覽時略顯奇怪。

**緩解方案（二選一）**：
- A. 在 §99 前加一條注解：`<!-- §99 是治理區塊固定錨點，跳號為刻意設計 -->`（Claude Code 讀到不受影響）
- B. 在 WORKFLOW_SOP §2 文書說明加一句：「§99 為所有文件的治理區塊固定錨點，跳號屬設計規範，非錯誤。」

推薦 B（說明文字比注解更顯眼）。不需要為此改 §99 編號。

---

## §6 自我檢核

- [x] 我有讀 v4 規劃書全 13 章節 + §99？✅（全文 628 行，§0-§13 + §99 逐節讀取）
- [x] 我有對 §8 S1-S5 五個選擇都給推薦？✅（S1→B / S2→1-4 / S3→維持 / S4→不拆 / S5→§99）
- [x] 我有對 §10 五個「待 AI 評估」項目都給可行性判定？✅（10.1→🟢 MVP / 10.2→🟡 試用 / 10.3→§N 統一 / 10.4→具體規則表 / 10.5→跨工具補充）
- [x] 我有重新跑五個壓力測試 + 新增測試 F（DOC-Refactor）？✅（A-F 六個全跑）
- [x] 我有挖出 v4 整合後新出現的盲點？✅（4 個：baton 衝突 / 多 worktree 掃描 / 預設行為未文件化 / §99 TOC 顯示）
- [x] 我採用 v4 §2 拆分式結構撰寫本評估報告？✅（§0 簡頂 3 行 + §99 末尾完整治理規格）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | Claude Code 對 v4 的第二輪可行性評估，提供 S1-S5 選擇、§10 可行性判定、壓力測試實測 |
| 用途 | baron 閱讀以決定 v4 最終拍板；若雙評估一致，直接進入 WORKFLOW-1-1 落地 |
| 權威源 | 本報告對 S1-S5 的 Claude Code 推薦、§10.1-10.5 的技術可行性判定有最高發言權 |
| 引用方 | `2026-05-24_WORKFLOW-1_v4_流程簡化與文件治理_改版規劃書.md` + v3 規劃書 + v3 雙評估報告 |
| 被引用方 | <由 Antigravity 自動掃描注入> |
| 約束事項 | 嚴禁修改業務代碼；嚴禁改動 v3/v4 規劃書和第一輪評估報告；嚴禁 commit/push |
| 改版觸發條件 | Antigravity 第二輪報告出爐後，發現與本報告有結構性衝突 |
| 改版規則 | 新增 Revision 區塊，不重寫既有評估結論 |
| 刪除條件 | WORKFLOW-1 全部 commit ship 後（與 v4 規劃書同步退役） |
| 重複防護 | 本報告不重複 v4 規劃書的設計邏輯，只寫「Claude Code 的技術判定理由」 |

### §99.2 Revision 歷程

- v1 (2026-05-25)：初版，依 v4 規劃書 628 行，完整評估 S1-S5 + §10.1-10.5 + A-F + 4 個新盲點
