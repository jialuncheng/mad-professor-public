# RESUME-P3 META-HOTFIX-1 — 緊急熱修復：B軌履歷 final 缺文件 header（P1 Meta 未渲染）

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 RESUME-P3 C3（逐 heading section 還原）後 B軌 final「完全沒有文件開頭 meta header（姓名/領域/電話/Email）」的功能缺口。
> **修復原則**：只在 `run_phase3` 寫出前加一個「組 header」步驟、**讀現有 `ctx.raw_metadata` 旁路 + `ctx.ingestion.title`**，嚴禁夾帶合約重構（合約轉正屬 INFRA-4 遠期任務）或其他無關功能。
> **工作流類別**：BE-Hotfix（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（WORKFLOW_SOP §5）。
> **狀態**：📝 文件階段（plan）。本文件僅產出於 `baton/`，**不動業務代碼**；Run（落地）由 baron 後續獨立提示詞觸發。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **META-HOTFIX-1** | `（待 baron Run 後回填）` | `fix(resume): RESUME-P3 META-HOTFIX-1 — run_phase3 組文件 header 讓 final 含 P1 meta` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：B軌（影子，`doc_type='resume'`）履歷的 `final_zh` / `final_en` **完全沒有文件開頭的 meta header**——沒有候選人姓名 h1、沒有領域/電話/Email 區塊；文件直接從第一個 section（如「工作經歷」=h2）開始。
- **受災範圍**：B軌 `ResumePipeline.run_phase3` 產出的 `final_zh` / `final_en`。P1 由 LLM/regex 特地抽出的姓名、電話、email、領域，對「最終文件」零貢獻。
- **首發來源**：baron 比對渲染結果——**功能缺口、非例外崩潰**。

### 2. 真因診斷 (Root Cause)

P1 抽出的 meta 放兩個地方（grep 鋼證）：
- **`IngestionMetadataSpec.title`**（姓名）——進凍結合約。
- **`ctx.raw_metadata`**（domain/phone/email，含 confidence/source）——走「DB 持久化旁路」（[`context.py:62`](pipelines/context.py:62)、[`resume_pipeline.py:194-196`](pipelines/resume_pipeline.py:194)）。

這條旁路的**設計終點是 DB**：唯一消費點是 [`resume_pipeline.py:332`](pipelines/resume_pipeline.py:332)（P2 讀 domain → LCC、功能性消費）與 [`web_server.py:655-656`](web_server.py:655)（寫 `Paper.metadata_json`）。

而 `run_phase3`（**唯一產出 final markdown 的地方**）讀的是 `ctx.ingestion`（source_lang/tiles）+ `gspec`（lcc/glossary/translated_abstract/domain_name），**從不讀 `ctx.raw_metadata`，也沒有任何「組 header」的步驟**（[`resume_pipeline.py:505-525`](pipelines/resume_pipeline.py:505)）：
```python
if is_zh:               zh_text = full_text
elif sections...:       zh_text = self._restore_sections_markdown(...)
else:                   zh_text = self._translate_whole(...)
en_text = full_text
zh_path.write_text(zh_text, ...)     # ← 直接寫 body、無 header
en_path.write_text(en_text, ...)
```

→ **真因＝渲染缺口**：meta 確實全程掛在 `ctx` 上（旁路可讀），但 `run_phase3` 沒有一行去消費它組成文件 header。RESUME-P3 C3 在 pipelines/ 內重建還原時只做了 body、沒做 header 組裝。

- **定位程式碼**：[`pipelines/resume_pipeline.py:515`](pipelines/resume_pipeline.py:515)（`en_text = full_text` 後、`write_text` 前，缺 prepend header）。

> **與 INFRA-4 的分工**：本 hotfix 是**治標**——直接在 render 端讀現有 raw_metadata 旁路把 meta 組進 final（不動凍結合約）。INFRA-4（遠期、A 軌死後）負責**治本**——把旁路轉正進 `spec.meta`，屆時本 helper 的讀取源由 `ctx.raw_metadata` 改為 `spec.<擴展欄>`。

---

## 熱修復修法 (Minimal Hotfix)

**設計決策**：在 `run_phase3` 寫出前加一個 pipelines/ 私有 helper `_render_meta_header`，讀 `ctx.raw_metadata`（domain/phone/email/organization）+ `ctx.ingestion.title`（姓名）+ `gspec.domain_name`（en 用 LCC 英文領域名），組出文件開頭 header，prepend 到 `zh_text` / `en_text`。

**欄位與格式**（resume 專屬、缺項靜默省略）：
- `# {姓名}`（h1；沿用 `ctx.ingestion.title` 原值、含影子 ` (測試)` 後綴、便於觀察）。
- **無序列表** meta 區塊：`- **領域 / 機構 / 電話 / Email**：值`（zh）｜`- **Domain / Organization / Phone / Email**: 值`（en）。
- **採無序列表（`- `）而非 blockquote**：每欄為獨立 list item、**CommonMark 規範保證各自一行**，不依賴行尾空格、不怕被 strip、根治 RAG-10 類軟換行（baron 2026-06-06 拍板，取代原 blockquote+尾隨空格脆弱方案）。
- **不含摘要**：`translated_abstract` 已於前端 toolbar 從 DB 顯示，且 resume 設計明訂「嚴禁 AI Summary 進正文」；故 header 不放摘要（見「設計待確認」）。

### 改動 1：`pipelines/resume_pipeline.py` 新增私有 helper

```python
    # === [RESUME-P3 META-HOTFIX-1 START] ===
    @staticmethod
    def _render_meta_header(
        ctx: PipelineContext, gspec: "GlossaryReadySpec", *, lang: str
    ) -> str:
        """組文件開頭 meta header：`# 姓名` + 領域/機構/電話/Email 無序列表。

        render 缺口治標（META-HOTFIX-1）：P1 抽的 meta 原本只到 DB（raw_metadata 旁路終點），
        本 helper 在 P3 渲染端**讀同一條現有旁路 ctx.raw_metadata + ctx.ingestion.title**，
        組出文件 header 讓 final 立刻有 meta（不動凍結合約；合約轉正屬 INFRA-4 遠期）。

        - lang='zh'|'en' 控制 label 語言與分隔符；缺項靜默省略；整包空 → 回 ''。
        - meta 採**無序列表（`- `）**：每欄為獨立 list item、CommonMark 規範保證各自一行，
          不依賴行尾空格 / 不怕 strip、根治 RAG-10 類軟換行（取代脆弱的 blockquote+尾隨空格）。
        - 姓名沿用 ctx.ingestion.title 原值（含影子 ' (測試)' 後綴、便於觀察、不另去除）。
        - 讀取源未來由 INFRA-4 從 ctx.raw_metadata 轉為 spec 擴展欄（本 helper 唯一改動點）。
        """
        raw = ctx.raw_metadata or {}
        title = ((ctx.ingestion.title if ctx.ingestion else "") or "").strip()
        domain = ResumePipeline._meta_value(raw, "domain") or ""
        if lang == "en":
            domain = (gspec.domain_name if gspec else "") or domain   # en 優先用 LCC 英文領域名
        org = ResumePipeline._meta_value(raw, "organization") or ""
        phone = ResumePipeline._meta_value(raw, "phone") or ""
        email = ResumePipeline._meta_value(raw, "email") or ""
        label = {
            "zh": {"domain": "領域", "org": "機構", "phone": "電話", "email": "Email"},
            "en": {"domain": "Domain", "org": "Organization", "phone": "Phone", "email": "Email"},
        }[lang]
        sep = "：" if lang == "zh" else ": "
        lines: List[str] = []
        if title:
            lines.append(f"# {title}")
            lines.append("")
        items: List[str] = []
        for key, val in (("domain", domain), ("org", org), ("phone", phone), ("email", email)):
            if str(val).strip():
                items.append(f"- **{label[key]}**{sep}{val}")   # 無序列表：規範保證每欄獨立一行
        if items:
            lines.extend(items)
            lines.append("")
        if not lines:
            return ""
        return "\n".join(lines).rstrip("\n") + "\n\n"
    # === [RESUME-P3 META-HOTFIX-1 END] ===
```

### 改動 2：`run_phase3` 寫出前 prepend header

```diff
         else:
             zh_text = self._translate_whole(full_text, inj, tr, translate=True)
         en_text = full_text

+        # === [RESUME-P3 META-HOTFIX-1 START] prepend 文件 meta header（render 缺口治標、走旁路）===
+        zh_text = self._render_meta_header(ctx, gspec, lang="zh") + zh_text
+        en_text = self._render_meta_header(ctx, gspec, lang="en") + en_text
+        # === [RESUME-P3 META-HOTFIX-1 END] ===
+
         zh_path = paper_manager.article_zh_path(
             settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id
         )
```

**不動清單（嚴守最小侵入）**：
- 標題還原（HEADING-HOTFIX-1 `level=min(2+depth,6)`）/ 段落正規化（PARA-HOTFIX-1）— 不動。
- section body 還原（`_restore_sections_markdown` / `_translate_whole`）— 不動（header 只 prepend、不碰 body）。
- 凍結合約 `IngestionMetadataSpec` / `BilingualMarkdownSpec` — **不動**（治標走旁路、不擴合約）。
- `ctx.raw_metadata` 旁路本體 / P2 domain 消費 / web_server 寫庫 — 不動。
- A軌 `md_restore_processor`（不 import、不耦合）/ 其餘四路 / 母提示詞 / DB Schema — 不動。

---

## 設計待確認（baron 過目時可調，預設如上）

| 點 | 預設 | 備選 |
|---|---|---|
| header 欄位 | 姓名(h1) + 領域 + 機構 + 電話 + Email | 加 LinkedIn/個人網站（若 P1 有抽）|
| 是否含摘要 | **否**（toolbar 已顯示、resume 禁 AI Summary 進正文）| 若要，於 meta 區塊下加 `gspec.translated_abstract` 段 |
| (測試) 後綴 | **保留**（便於觀察、與列表一致）〔baron 2026-06-06 拍板〕| 去除（僅 DB/列表保留）|
| en 領域值 | LCC 英文名（`gspec.domain_name`）fallback raw | 一律用 raw domain（中文）|
| meta 區塊格式 | **無序列表 `- **欄**：值`**（規範保證一欄一行）〔baron 2026-06-06 拍板〕| blockquote + 行尾兩空格 hard break（脆弱、已棄）|

> **baron 決策（2026-06-06）**：① 機構（organization）保留——P1 LLM 確實抽出（golden 實測 `AI Bioelectronic Healthtech`）；② `(測試)` 後綴**不去除**（便於觀察）；③ meta 區塊採**無序列表**（取代脆弱的 blockquote+尾隨空格、根治軟換行）；④ 其餘照預設。
> **⚠️ domain 現況**：P1 抽出的 `domain` 為描述句（如 `半導體 SoC 與 AI 生醫電子技術主管履歷`）、非乾淨標籤；header 照實渲染。若要乾淨標籤須改 P1 domain prompt（另一任務、不在本 hotfix）。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（Run 階段執行）
追加 1 測試至 `tests/test_resume_pipeline.py`（mock Translator、不打真 API）：
- `test_p3_meta_header_rendered`：
  - ctx 設 `ingestion.title="王小明 (測試)"` + `raw_metadata={domain/organization/phone/email}`。
  - `run_phase3` → 讀 `final_zh` 斷言：**(a)** 以 `# 王小明 (測試)` 開頭（沿用 title 原值、後綴保留）；**(b)** 領域/機構/電話/Email 值都在 final；**(c)** 各欄為獨立 list item（`\n- **領域**：` / `\n- **機構**：` / `\n- **電話**：` / `\n- **Email**：` 皆命中、規範保證一欄一行、無軟換行擠段）。
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q     # 期望：全綠（含新測試）
$ venv/bin/python -m pytest tests/ -q                            # 期望：全套件不退化（僅既知 LOG_FORMAT env flake）
```

### 2. 驗收 grep
```bash
grep -n 'RESUME-P3 META-HOTFIX-1' pipelines/resume_pipeline.py            # 期望：START/END 包裹命中
grep -n 'def _render_meta_header' pipelines/resume_pipeline.py              # 期望：1（helper 存在）
grep -n '_render_meta_header(ctx' pipelines/resume_pipeline.py              # 期望：run_phase3 prepend 兩處（zh/en）
grep -n 'md_restore_processor\|RestoreProcessor\|_render_header_en' pipelines/resume_pipeline.py  # 期望：0（不耦合 A軌）
grep -n 'def test_p3_meta_header_rendered' tests/test_resume_pipeline.py    # 期望：1
# SOP — logging / database
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
```

### 3. 本地 E2E 快速復現與驗證（baron 影子上傳）
重跑一份履歷影子 → 開 B軌 `final_zh` 確認：
- 文件開頭出現 `# {候選人姓名}` + 領域/電話/Email 區塊（各欄獨立行、不擠成一行）。
- body（工作經歷等）緊接 header 之後、層級與段落正常（HEADING/PARA 不受影響）。
- 確認姓名不重複（body 無第二個姓名 h1）。

### 4. ⚠️ 行為變更 + Golden 重捕
本 hotfix **在 B軌 `final_zh`/`final_en` 開頭新增 header** → 衝擊 golden D1（結構）/ D2（譯文相似度）。**Flip/結案前須重捕 resume 單路 golden**：
```bash
venv/bin/python tools/golden_baseline.py capture resume --force
```
（與 TILING / SHADOW / RESUME-P3 / HEADING-HOTFIX-1 / PARA-HOTFIX-1 同屬「B軌輸出變更須重捕」一類。）

---

## 回退與備案

```bash
# 單獨回退本 hotfix（保留 C1-C6 + HEADING/PARA-HOTFIX）
git revert <META-HOTFIX-1-hash>

# 若引發更大 Regression、退回 PARA-HOTFIX-1 落地點（待其 hash 回填後填入）
git reset --hard <PARA-HOTFIX-1-hash>
```

---

## 附錄：受影響檔案與包裹標記

| 檔案 | 改動 | 標記 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 新增 `_render_meta_header`（讀 raw_metadata 旁路 + ingestion.title、無序列表一欄一行）+ `run_phase3` prepend zh/en | `# === [RESUME-P3 META-HOTFIX-1 START/END] ===` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_meta_header_rendered` | 同上包裹 |
| `.bak` 備份 | `archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak`（+ 測試檔 .bak）| 改前備份鐵律 |

## §commit baron 執行命令（Run 階段交付參考）
```bash
# 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak

# git add（收官 mv hotfix.md + 執行.md → hotfixes/ 後）
git add pipelines/resume_pipeline.py tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-06_RESUME-P3_META-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_META-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_META-HOTFIX-1_run_提示詞.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_META-HOTFIX-1_執行.md

# commit（msg 草稿 /tmp/RESUME-P3_META-HOTFIX-1_msg.txt）
git commit -F /tmp/RESUME-P3_META-HOTFIX-1_msg.txt
```

### commit message 草稿
```
fix(resume): RESUME-P3 META-HOTFIX-1 — run_phase3 組文件 header 讓 final 含 P1 meta

修改 pipelines/resume_pipeline.py：
1. 新增 pipelines/ 私有 helper _render_meta_header：讀現有 ctx.raw_metadata 旁路（domain/organization/phone/email）+ ctx.ingestion.title（姓名、沿用原值含 (測試)）+ gspec.domain_name（en 領域），組文件開頭 header（# 姓名 + 領域/機構/電話/Email 無序列表、缺項靜默省略、無序列表規範保證一欄一行防軟換行）。
2. run_phase3 寫出前 prepend header 至 final_zh（中文 label）/ final_en（英文 label），讓 P1 抽的 meta 進入最終文件。
不動凍結合約（走現有旁路、合約轉正屬 INFRA-4 遠期）；body 還原（HEADING/PARA hotfix）與 A軌均不動。
修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_meta_header_rendered 驗證 final 含 # 姓名（沿用 title 含 (測試)）+ 領域/機構/電話/Email 且各欄為獨立 list item（一欄一行）。
變更與新增區塊已使用 # === [RESUME-P3 META-HOTFIX-1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
