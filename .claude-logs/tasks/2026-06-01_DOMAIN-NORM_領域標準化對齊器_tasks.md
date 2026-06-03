# DOMAIN-NORM 領域標準化對齊器 — Tasks

> 本文件為 DOMAIN-NORM 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md` 計畫產出，含 5 個 Commit（C1–C4 實作 + C5 Check 收官）。
> commit / push 由 baron 手動執行（CLAUDE.md §1.3）。
> **收官歸檔鐵律**：C1–C4 執行期所有 plan／tasks／執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 C5（Check）一次性 `mv` + `git add`** 搬移 plan + tasks + 全部 `C*_執行.md`（WORKFLOW_SOP §3）。
> **上游同步確認**：本 plan v2 簽名 `normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode` 與 PIPE master v10 §2 U8（L69）、PIPE-SPEC §1.2.1（L74）**逐字一致**。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `processor/domain_normalizer.py`（DomainNormalizer 對齊器）/ `tests/test_domain_normalizer.py`（4 測試） |
| **修改檔案** | 2 個 | `models.py`（**新增** `Domains` + `DomainMapping` 兩表；既有 `Paper` 等不動）/ `settings.py`（新增 `LLM_USE_GLOSSARY_ALIGN`，預設 False） |
| **目錄初始化** | 0 個 | —（複用既有 `processor/` `tests/`） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1（資料庫表建立）→ C2（對齊器核心）→ C3（單一入口與旗標）→ C4（測試）→ C5（Check 收官） |
| **執行報告** | 5 個 | `baton/2026-06-03_DOMAIN-NORM_C1~C5_執行.md`（套用 template_execution.md、暫存 baton/） |
| **.bak 備份** | 每改既有檔前必備 | C1 改 `models.py` / C3 改 `settings.py` 前產 `.bak`，納入該 Commit git add |
| **baton 歸檔** | 1 次 | **僅 C5 收官**一次性 `mv` plan_v2＋tasks＋C1–C5 執行報告至正式目錄 + `git add` |

> **邊界**：本任務只建「領域 LCC 收斂 + 動態註冊 + 快取」真理源；**不塞任何術語/單字**（單字提取自癒屬 GLOSSARY-CORE 職責）。`detect` 偵測本體、`rag_retriever` 檢索、`Paper` 主欄位皆不動（§7）。

---

## §1 TL;DR（概要）

- **挑戰**：`DomainDetector.detect` 產高自由度 raw 短句（無法當穩定查詢主鍵）；靜態白名單無法為冷門領域擴展；履歷等複合文檔應按實質技能（行銷/AI）而非「resume」類型分類。
- **解法**（逐 Commit、中文括號命名）：
  - **C1 — Database Schema（資料庫表建立）**：`models.py` 新增 `Domains`（lcc_code PK + name 動態註冊表）+ `DomainMapping`（raw→lcc 快取表）。
  - **C2 — Normalizer Core（對齊器核心邏輯）**：`processor/domain_normalizer.py` 實作內容判定（LLM cheap model Temp=0.0）+ 動態註冊（查 Domains 缺則 upsert、不塞單字）+ 快取防重（先查 DomainMapping、命中 0ms）。
  - **C3 — Entry & Feature Flag（單一入口與熱插拔旗標）**：`normalize_to_lcc(raw_domain, context_text=None)->LCCCode` 單一入口 + `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False）；False 時走舊 raw 直注路徑（零風險）。
  - **C4 — Unit Tests（單元測試）**：`tests/test_domain_normalizer.py` 4 測試（內容分類 / 動態註冊不塞單字 / 快取命中 0 API / 旗標 off 保舊行為）。
  - **C5 — Check / Checkout（收官歸檔）**：Conformance 驗收 + 一次性歸檔 plan_v2/tasks/C1–C5 報告。
- **影響範圍**：1 新對齊器 + 2 新表 + 1 env 旗標 + 測試；無既有業務代碼邏輯改動（`detect`/`Paper` 主欄位/`rag_retriever` 不動）；旗標預設 False 線上 0 風險。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀（plan §3 grep，已實地查證） | 待處理 |
|---|---|---|
| `processor/domain_detector.py` | `detect(self, pdf_path: str) -> str` @L39（回傳 raw 短句） | 純讀其輸出餵 normalizer，**偵測本體不動** |
| `processor/translate_processor.py` | L41 `self.domain` / L239 `本文件主題領域：{domain}` 直注 system_prompt | 旗標 False 時此舊路徑保留；本任務不改 translate（接線屬後續路次 plan） |
| `models.py` | `Paper.domain: Mapped[Optional[str]]` @L104；無 `Domains`/`DomainMapping` 表 | C1 新增兩表；`Paper` 主欄位/關係不動 |
| `settings.py` | 無 `LLM_USE_GLOSSARY_ALIGN` | C3 新增（預設 False） |
| `processor/domain_normalizer.py` | 不存在 | C2 新建 |

---

## §3 觀察問題

### 問題 #1：raw 領域短句無法當穩定主鍵 + 靜態白名單不可擴展
- **證據**：plan §3.1——`domain_detector.detect` 回 10-30 字高自由度短句；`models.py L104` domain 為自由文字。
- **影響**：無法穩定查詢/級聯 GLOSSARY-CORE；冷門領域（侏羅紀/古生物）無法自動對齊建獨立領域空間。

### 問題 #2：履歷複合文檔被粗暴歸類「resume」失去實質專業
- **證據**：plan U1——履歷重點在技能（投放/社群→HF、Python/LLM→QA）。
- **影響**：需基於 `context_text` 技能關鍵字判定學科 LCC，而非文檔類型名。

---

## §4 設計方案

> 逐 Commit 落地概要；完整規格見 plan v2 §2（U1–U4）。

- **C1（U2 表）**：`models.py` 新增 `Domains`（`lcc_code: str PK` + `name: str`）+ `DomainMapping`（`raw_key: str PK`〔lowercase+strip〕 + `lcc_code: str` + 可選 `created_at`）；對齊既有 ORM 風格（SQLAlchemy 2.0 `Mapped`）。
- **C2（U1+U2 核心）**：`DomainNormalizer` 內部——① 快取查 `DomainMapping`（raw lowercase+strip 為鍵）命中即回；② 未命中 → LLM（cheap model Temp=0.0、System Instruction 定義 LCC 1-3 字母規則）依 `context_text`/raw 收斂 LCCCode + name；③ 查 `Domains`、缺則 `INSERT OR IGNORE` 動態註冊（**不塞單字**）；④ 寫回 `DomainMapping`；⑤ 回 LCCCode。**LLM 呼叫在 DB 交易外**（database SOP 原則 2）；併發以 PK upsert 冪等；全程 try/except 降級 `"general"`（§7 Q1）。
- **C3（U3+U4）**：`normalize_to_lcc(raw_domain, context_text=None)->LCCCode` 單一入口 + `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False）；False → 直接回傳/沿用 raw（舊行為、不查 DB/不呼 LLM）。
- **C4**：4 pytest（mock LLM）。
- **C5**：Check 收官歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 修改 `models.py`（CLAUDE.md §3 嚴禁清單） | 🟡 中 | plan v2 已 baron 核准；**僅新增** Domains/DomainMapping 兩表，`Paper` 等既有表/欄位/關係零改動；C1 改前 `.bak` |
| DB 交易內含 LLM 呼叫 → SQLite `database is locked` | 🔴 高 | **LLM 收斂呼叫必須在 `session.begin()` 交易外**完成、取得 LCC 後才開短交易寫 Domains/DomainMapping（database SOP 原則 2；C2 實作硬約束） |
| 多人併發為同一新 LCC 寫 Domains → IntegrityError | 🟡 中 | `lcc_code` PK + `INSERT OR IGNORE`/upsert 冪等；try/except 降級 general（§7 Q1） |
| LLM 產非標準/過長 LCC 碼 | 🟢 低 | System Instruction 定義 LCC 規則 + 長度 1-3 字元硬限（§7 Q2） |
| 旗標 False 時舊行為被破壞 | 🔴 高 | C3 確保 False 走原 raw 直注路徑、不查 DB/不呼 LLM；test_feature_flag_off 驗證 |
| 誤改 `detect`/`rag_retriever`/`translate` 本體 | 🔴 高 | §7 不可動；本任務只新增對齊器 + 表 + 旗標，不接線 translate（接線屬後續路次 plan） |
| baton 報告提早 mv/git add | 🔴 高 | C1–C4 全留 baton；唯 C5 收官一次性歸檔 |

---

## §6 測試計畫

> 對齊 plan §6.1；C4 集中建 `tests/test_domain_normalizer.py`（mock LLM，不實打 API）。

### §6.1 C1 驗收（Domains/DomainMapping 表）
```bash
grep -nE "class Domains|class DomainMapping|lcc_code" models.py   # 期望：兩表 + PK 命中
python -c "import models; print('Domains' in dir(models), 'DomainMapping' in dir(models))"
```
### §6.2 C2 驗收（對齊器核心）
```bash
grep -nE "class DomainNormalizer|INSERT OR IGNORE|on_conflict|DomainMapping|Domains|Temperature|temperature" processor/domain_normalizer.py
# 確認：LLM 呼叫在交易外（grep session.begin 與 LLM 呼叫順序人工核）
```
### §6.3 C3 驗收（入口 + 旗標）
```bash
grep -nE "def normalize_to_lcc|context_text|LLM_USE_GLOSSARY_ALIGN" processor/domain_normalizer.py settings.py
```
### §6.4 C4 驗收（測試全綠）
```bash
pytest tests/test_domain_normalizer.py -v
pytest tests/ -q   # 既有測試零迴歸
```

---

## §7 不可動清單

明確劃定修改邊界。**以下嚴禁任何改動：**

- [ ] `processor/domain_detector.py` `detect` 多模態（Vision）與文字提取核心邏輯——只取其 raw 輸出餵 normalizer。
- [ ] `models.py` `Paper` 表既有主欄位與關係屬性——僅可**新增** `Domains` / `DomainMapping` 兩表。
- [ ] `rag_retriever.py` RAG 核心檢索邏輯。
- [ ] `processor/translate_processor.py` 既有 domain 直注路徑（旗標 False 時保留；本任務不接線 translate）。
- [ ] `LLM_USE_GLOSSARY_ALIGN=False` 時的舊行為路徑——確保預設零風險。
- [ ] 主 repo 目錄（worktree 父目錄）。
- [ ] baton/ 暫存文件（C1–C4 期間嚴禁提早 mv/git add；唯 C5 收官一次性歸檔）。

---

## §8 推薦 Commit 拆分

### C1 — Database Schema（資料庫表建立）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `models.py`（**新增** `Domains` + `DomainMapping`，先 `.bak`） |
| **安全性** | 🟢 高 — 純新增兩表、不動既有 `Paper` 等表/欄位/關係；無資料遷移 |
| **可逆性** | 🟢 高 — 還原 `.bak`（新表無既有資料依賴） |
| **驗收 grep 條件** | 見 §6.1（`class Domains`/`class DomainMapping`/`lcc_code` 命中） |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1. `cp models.py .claude-logs/archive/2026-06-03_DOMAIN-NORM_C1_models.py.bak`（納入 git add）。2. 對齊既有 SQLAlchemy 2.0 ORM 風格新增 `class Domains`（`lcc_code: Mapped[str] = mapped_column(String, primary_key=True)` + `name: Mapped[str]`）+ `class DomainMapping`（`raw_key: Mapped[str] primary_key`〔存 lowercase+strip 後的 raw〕+ `lcc_code: Mapped[str]`，可選 FK→Domains.lcc_code + `created_at`）。3. 表名/欄位對齊既有命名慣例（如 `__tablename__`）。4. **不改 `Paper` 等既有表**。5. `init_db()` 既有 `Base.metadata.create_all()` 自動建新表（無需 Alembic）。6. 產 C1 執行報告（baton/）。 |

### C2 — Normalizer Core（對齊器核心邏輯）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `processor/domain_normalizer.py`（核心類，尚不對外接線） |
| **安全性** | 🟢 高 — 純新增模組、不接線既有 pipeline；無 runtime 流量 |
| **可逆性** | 🟢 高 — 刪除新檔即還原 |
| **驗收 grep 條件** | 見 §6.2（DomainNormalizer / 動態註冊 upsert / 快取 / Temp=0.0） |
| **依賴關係** | C1（Domains/DomainMapping 表） |
| **具體實作細節** | 1. `processor/domain_normalizer.py` 定義 `class DomainNormalizer`。2. 內部對齊流程（plan U1+U2）：① `_cache_lookup(raw)`：raw `.lower().strip()` 為鍵查 `DomainMapping`，命中回 lcc（**0ms、零 API**）；② 未命中 → `_llm_classify(raw, context_text)`：cheap model（對齊既有 LLM client 用法）、`temperature=0.0`、System Instruction 定義「回標準 LCC 1-3 字母代碼 + 領域名」（履歷按 context_text 技能判定 HF/QA，禁歸 resume）；③ `_register_domain(lcc, name)`：查 `Domains`，缺則 `INSERT OR IGNORE`（或 SQLAlchemy `on_conflict_do_nothing`）動態註冊、**不塞單字**；④ `_cache_write(raw_key, lcc)` 寫回 `DomainMapping`。3. **交易邊界鐵律**（database SOP 原則 2）：`_llm_classify`（外部 API）**必須在任何 `session.begin()` 之外**完成；DB 寫入用極短交易 `with session.begin():`。4. 全程 `try/except` → 失敗降級回 `"general"`（§7 Q1、不阻斷）。5. logging 依 logging SOP（`logger.error(..., exc_info=True)`；cache hit 印 info）。6. 產 C2 執行報告（baton/）。 |

### C3 — Entry & Feature Flag（單一入口與熱插拔旗標）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/domain_normalizer.py`（補 `normalize_to_lcc` 公開入口）+ `settings.py`（新增 `LLM_USE_GLOSSARY_ALIGN`，先 `.bak`） |
| **安全性** | 🟢 高 — 旗標預設 False、舊行為 100% 保留 |
| **可逆性** | 🟢 高 — 還原 `.bak` + 移除入口 |
| **驗收 grep 條件** | 見 §6.3（`def normalize_to_lcc`/`context_text`/`LLM_USE_GLOSSARY_ALIGN` 命中） |
| **依賴關係** | C2 |
| **具體實作細節** | 1. `cp settings.py .claude-logs/archive/2026-06-03_DOMAIN-NORM_C3_settings.py.bak`（納入 git add）。2. `settings.py` 新增 `LLM_USE_GLOSSARY_ALIGN = os.getenv("LLM_USE_GLOSSARY_ALIGN", "false").lower() in ("1","true","yes")`（對齊既有 env 風格、預設 False）。3. `domain_normalizer.py` 對外暴露 `normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode`（簽名逐字對齊 PIPE-SPEC §1.2.1 / PIPE master v10 L69）：旗標 False → 直接回傳 raw_domain（或既有 general fallback、不查 DB/不呼 LLM、舊行為）；旗標 True → 走 C2 對齊流程（快取→LLM→動態註冊→寫回）。4. `LCCCode` 型別別名（`str` 或 `NewType`）。5. 產 C3 執行報告（baton/）。 |

### C4 — Unit Tests（單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `tests/test_domain_normalizer.py` |
| **安全性** | 🟢 高 — 純測試新增 |
| **可逆性** | 🟢 高 — 刪除測試檔 |
| **驗收 grep 條件** | 見 §6.4（`pytest tests/test_domain_normalizer.py -v` 全綠 + 既有零迴歸） |
| **依賴關係** | C1 + C2 + C3 |
| **具體實作細節** | 1. mock LLM（monkeypatch `_llm_classify` 或 LLM client）回固定 LCC，不實打 API。2. 四測試（plan §6.1）：① `test_domain_normalization_content_based`（「投放/社群」→`HF`、「Python/LLM」→`QA`）；② `test_domain_dynamic_registration`（冷門「侏羅紀/化石/恐龍」→ 自動註冊 `Domains` lcc_code=`QE`/name=`Geology/Paleontology`，且**確認無單字寫入**）；③ `test_domain_mapping_cache_hit`（第二次查詢 0 API、命中 DomainMapping）；④ `test_feature_flag_off_preserves_raw`（`LLM_USE_GLOSSARY_ALIGN=False` 走舊 raw 直注、不查 DB/不呼 LLM）。3. 用 in-memory SQLite 或 tmp DB 隔離（不污染正式 DB）。4. 產 C4 執行報告（baton/）。 |

### C5 — Check / Checkout（Conformance 驗收與收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton/ plan_v2 → `plans/` + tasks → `tasks/` + C1–C5 報告 → `executions/` + `git add`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ |
| **驗收 grep 條件** | `ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ \| grep DOMAIN-NORM`（齊全）；`ls .claude-logs/baton/ \| grep -c DOMAIN-NORM` # 期望：0 |
| **依賴關係** | C1–C4（全部報告已產於 baton/） |
| **具體實作細節** | 1. Conformance 三維度驗收（目標規格 U1-U4 / 測試計畫 / 不可動清單 git 驗證 + 上游同步：簽名對齊 PIPE-SPEC §1.2.1 / PIPE master v10 L69）→ 產 `baton/2026-06-03_DOMAIN-NORM_C5_執行.md`。2. **一次性歸檔**（WORKFLOW_SOP §3）：`mv` plan_v2 baton→`plans/`；`mv` tasks baton→`tasks/`；`mv` C1~C5 `_執行.md` baton→`executions/`。3. `git add` 上述正式檔 + `models.py`/`settings.py`/`processor/domain_normalizer.py`/`tests/test_domain_normalizer.py` + 全部 `.bak` + prompts/INDEX + TODO（**明確列檔、嚴禁 `git add -A`**）。4. **更新 TODO.md**：DOMAIN-NORM 移入 ✅ 已完成表（Hash 待 baron 回填）+ 刪 active 條目 + 索引標 ✅ + 歷史 Hash 自癒。5. 驗收 baton/ 無 DOMAIN-NORM 殘留。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3）。 |

---

## §9 Open Questions

無。（plan v2 §7 之 2 項——LCC 動態產生失敗降級 general（C2 try/except）/ LCC 碼長度限 1-3 字元（C2 System Instruction）——皆已標推薦答案並納入 C2 實作細節；本 tasks 階段不另增規劃層問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 DOMAIN-NORM 的 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` C1–C5 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改 `detect`/`rag_retriever`/`Paper` 主欄位/translate 本體；LLM 呼叫須在 DB 交易外；嚴禁自動 git commit/push；C1–C4 報告嚴禁移動、唯 C5 收官一次性歸檔；修改既有檔前 `.bak` |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；U1–U4 規格唯一源在 plan v2 §2；DomainNormalizer 契約唯一源在 PIPE-SPEC §1.2.1 |

### §99.2 Revision 歷程

- v1 (2026-06-03)：初版拆分，依 plan v2 §2（U1–U4）拆為 5 Commit——C1 Database Schema（Domains/DomainMapping 兩表）/ C2 Normalizer Core（內容判定 + 動態註冊不塞單字 + 快取防重、LLM 呼叫在交易外）/ C3 Entry & Feature Flag（`normalize_to_lcc(raw_domain, context_text=None)` 單一入口 + `LLM_USE_GLOSSARY_ALIGN` 預設 False）/ C4 Unit Tests（4 pytest、mock LLM）/ C5 Check 收官；簽名逐字對齊 PIPE-SPEC §1.2.1 / PIPE master v10 L69；不給 commit 建議；C1/C3 改既有檔前 `.bak`；C1–C4 留 baton、唯 C5 一次性歸檔；§5 標註 DB 交易順序 / 併發 upsert / 旗標零風險三大風險。
