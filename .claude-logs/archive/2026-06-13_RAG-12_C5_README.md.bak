# Mad Professor

學術論文、新聞、書籍、簡報的 AI 閱讀與問答系統。上傳 PDF 後自動解析、翻譯成繁體中文，並提供基於 RAG 的 AI 導師問答功能。

本專案 Fork 自 [LYiHub/mad-professor-public](https://github.com/LYiHub/mad-professor-public)，在原作者基礎上大規模重構，從桌面應用改為 Web 架構。

---

## 一、專案簡介

Mad Professor 是一套**論文 AI 問答系統**：把一份 PDF 丟進來，系統自動跑完整條 pipeline（解析 → 結構分析 → 翻譯 → 圖說生成 → 摘要 → 向量庫建立），最後讓你用自然語言對這份文件提問，由 AI 導師結合全文 RAG 檢索回答。

**主要功能**

- **多文件類型支援**：學術論文（academic）、書籍（book）、技術文件（technical）、新聞（news）、網頁存檔（web）、簡報（slides）
- **自動翻譯**：全文翻譯成繁體中文，依文件類型套用不同翻譯風格，支援中英切換
- **圖表理解**：Gemini Vision 自動生成圖片說明，整合進 RAG
- **簡報解析**：簡報 PDF 每頁獨立渲染，Vision 辨識內容（不走 MinerU）
- **主題領域偵測**：讀取首頁自動判斷文件主題領域，注入翻譯與摘要以提高術語準確度
- **RAG 問答**：基於 Gemini Embedding 001 的向量檢索
- **AI 導師**：蘇格拉底式啟發、第一性原理、事後驗屍三種引導模式
- **對話紀錄**：問答歷史自動儲存，重啟不遺失
- **單帳號登入**：bcrypt 密碼 + session，可安全部署到公網

---

## 二、系統需求

| 項目 | 需求 |
|---|---|
| 作業系統 | Linux / macOS |
| Python | 3.10 以上 |
| 記憶體 | 約 4 GB |
| MinerU 服務 | 一個可連線的 MinerU PDF 解析服務（自架或雲端） |
| Gemini API | 有效的 Google Gemini API key |

> MinerU 屬外部服務，需另行部署，見〈六、MinerU 服務〉。

---

## 三、快速開始

### 1. 安裝

```bash
git clone https://github.com/jialuncheng/mad-professor-public.git
cd mad-professor-public
git checkout gemini-refactor

bash install.sh
```

`install.sh` 會檢查 Python 版本、建立 `venv/`、安裝 `requirements.txt`，並在 `.env` 不存在時從 `.env.example` 複製一份。腳本可重複執行，不會破壞既有環境。

### 2. 設定 .env

```bash
cp .env.example .env   # install.sh 已自動做過，可略過
```

編輯 `.env`，至少填入：

- `GEMINI_API_KEY` — Gemini API 金鑰
- `MINERU_API_URL` — MinerU 解析服務端點
- `AUTH_USERNAME` — 登入帳號（預設 `admin`；migration 會依此建立 user）
- `AUTH_PASSWORD_HASH` — 登入密碼 hash（見〈五、登入功能〉）
- `SESSION_SECRET` — session 簽章密鑰（見〈五、登入功能〉）

### 3. 初始化資料庫

`install.sh` 已建立 `data/` 並初始化 schema。設好 `.env` 後，再執行 migration 建立 admin user（讀 `.env` 的 `AUTH_USERNAME` / `AUTH_PASSWORD_HASH`）：

```bash
source venv/bin/activate
python -c "from db import init_db; init_db()"   # 建表（idempotent，install.sh 已做過）
python scripts/migrate_to_db.py                 # 建立 admin user（可先加 --dry-run 預覽）
```

### 4. 啟動

```bash
source venv/bin/activate
python web_server.py
```

Web 介面：<http://localhost:8080>

---

## 四、設定詳細說明

所有設定皆透過 `.env`（複製自 `.env.example`）。`.env` 已被 `.gitignore` 忽略，請勿提交。

| 變數 | 必填 | 預設 / 範例 | 用途 |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ 必填 | （無） | Google Gemini API 金鑰。未設定時 LLMClient 無法初始化。 |
| `LLM_TRANSLATE_MODEL` | 可選 | `gemini-3.1-flash-lite` | 翻譯使用的模型。 |
| `LLM_CHAT_MODEL` | 可選 | `gemini-3.1-flash-lite` | 問答對話使用的模型。 |
| `EMBEDDING_MODEL` | 可選 | `gemini-embedding-001` | 向量嵌入模型（文字）。`gemini-embedding-001` 支援批次嵌入，效能優於 `gemini-embedding-2`。 |
| `LLM_DOMAIN_MODEL` | 可選 | 未設定時用 `LLM_CHAT_MODEL` | 主題領域判斷模型。 |
| `LLM_DOC_MODEL` | 可選 | 未設定時用 `LLM_CHAT_MODEL` | doc_analyzer 的 heading fix / structure 分析（後台，建議 Flash）。 |
| `LLM_VISION_MODEL` | 可選 | 未設定時用 `LLM_CHAT_MODEL` | image_caption 與 slides 的 Vision 辨識（後台，建議 Flash）。 |
| `LLM_EXTRA_INFO_MODEL` | 可選 | 未設定時用 `LLM_CHAT_MODEL` | extra_info 章節摘要／問題／公式解析（後台，建議 Flash）。 |
| `DATABASE_URL` | 可選 | `sqlite:///<root>/data/mad-professor.db` | SQLAlchemy DB 連線字串。預設 SQLite，未來可換 PostgreSQL（改成 `postgresql://...`）。 |
| `MINERU_API_URL` | 視部署 | `http://localhost:8000/file_parse` | MinerU 解析 API 端點。 |
| `MINERU_HOST` | 視部署 | `user@localhost` | 透過 ssh/scp 取回圖片用的遠端主機。留空則跳過圖片複製（不影響其餘流程）。 |
| `MINERU_OUTPUT_DIR` | 視部署 | `/home/user/output` | MinerU 在遠端主機上的輸出目錄絕對路徑。留空則跳過圖片複製。 |
| `ENVIRONMENT` | 可選 | `development` | `development` 允許 HTTP；`production` 強制 cookie 走 HTTPS。 |
| `AUTH_USERNAME` | 可選 | `admin` | 登入帳號（單一帳號）。 |
| `AUTH_PASSWORD_HASH` | ✅ 公網必填 | （無） | 密碼 bcrypt hash。留空時無法登入。 |
| `SESSION_SECRET` | ✅ 公網必填 | （無） | Session cookie 簽章密鑰，至少 32 字元隨機字串。留空時用臨時密鑰（重啟即失效）。 |

**模型選擇建議**

設計理念：**面對使用者的回答用 Pro、後台批次處理用 Flash**。Chat／Web search 是使用者直接看到的輸出，品質優先；doc_analyzer／image_caption／slides／extra_info／translate 是離線批次步驟，速度與成本優先，降階對使用者體驗無直接影響。

- `LLM_CHAT_MODEL`：使用者問答（含 Web search grounding）直接使用，建議 **Pro 等級**（如 `gemini-3.1-pro-preview`）。
- `LLM_DOMAIN_MODEL`：只在每份文件呼叫一次、且影響後續術語準確度，建議 Pro 等級（如 `gemini-2.5-pro`）。
- `LLM_TRANSLATE_MODEL`：全文逐段翻譯、量大，建議 **Flash 等級**（如 `gemini-3.1-flash-lite`）。
- `LLM_DOC_MODEL` / `LLM_VISION_MODEL` / `LLM_EXTRA_INFO_MODEL`：後台處理，**留空即沿用 `LLM_CHAT_MODEL`（行為不變）**；設為 Flash 等級可大幅降低 analyze／圖說／摘要耗時與成本。
- `EMBEDDING_MODEL`：建向量庫與查詢必須使用**同一個** embedding 模型；中途更換需重建所有論文向量庫。

---

## 五、登入功能

系統採單帳號登入（帳號預設 `admin`，可用 `AUTH_USERNAME` 變更），密碼以 bcrypt hash 儲存，session 以簽章 cookie 維持。

**1. 產生密碼 hash**

```bash
source venv/bin/activate
python scripts/generate_password_hash.py
```

互動式輸入密碼兩次，將輸出的 hash 貼到 `.env` 的 `AUTH_PASSWORD_HASH`。

**2. 產生 SESSION_SECRET**

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

貼到 `.env` 的 `SESSION_SECRET`。部署到公網時務必重新產生，勿沿用範例值。

**3. development vs production**

- `ENVIRONMENT=development`：本地測試，cookie 不強制 HTTPS，可直接用 `http://localhost:8080`。
- `ENVIRONMENT=production`：上線部署，cookie 強制 `https_only`，必須在 HTTPS 後面跑（見〈九、部署〉）。

> 未設定 `SESSION_SECRET` 或 `AUTH_PASSWORD_HASH` 時，啟動會輸出 WARNING；未設定 hash 時無法登入。

---

## 六、MinerU 服務

PDF（非簡報類型）解析依賴外部 **MinerU** 服務。你需要自行部署一個 MinerU API（參考 [MinerU](https://github.com/opendatalab/MinerU)），本系統透過 HTTP 呼叫其 `/file_parse` 端點取得 Markdown，並透過 ssh/scp 取回解析出的圖片。

**連線資訊（填入 `.env`）**

- `MINERU_API_URL` — 例：`http://10.0.0.5:8000/file_parse`
- `MINERU_HOST` — 例：`user@10.0.0.5`（scp 取圖用；留空則跳過圖片複製）
- `MINERU_OUTPUT_DIR` — 例：`/home/user/mineru/output`（MinerU 端輸出目錄絕對路徑）

**systemd 服務範例**（在 MinerU 主機上，依實際安裝路徑調整）

```ini
# /etc/systemd/system/mineru.service
[Unit]
Description=MinerU PDF parsing API
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/mineru
ExecStart=/home/user/mineru/venv/bin/mineru-api --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mineru
sudo systemctl status mineru
```

> 簡報類型（slides）走 PyMuPDF + Gemini Vision，不需要 MinerU。

---

## 七、Pipeline 階段

`pipeline_core.py` 依序執行下列階段（`analyze`∥`detect_domain`、`translate`∥`image_caption` 為並行）：

| 階段 | 說明 |
|---|---|
| `pdf2md` | PDF 轉 Markdown（一般文件走 MinerU API；簡報走 PyMuPDF + Vision） |
| `analyze` | 標題層級修正 + 文件結構分析（依文件類型套用不同 prompt） |
| `detect_domain` | 讀首頁文字＋截圖，判斷文件主題領域（失敗為 soft fallback，不中止） |
| `md2json` | Markdown 解析為結構化 JSON（章節樹、作者、摘要、圖表） |
| `json_process` | 行級掃描，拆分 figure / table / formula / text 區塊 |
| `tiling` | 依向量相似度切片，合併過小、切分過大的文字塊 |
| `translate` | 分段翻譯為繁體中文，依 doc_type 與 domain 套用風格 |
| `image_caption` | 掃描 `images/`，Gemini Vision 為每張圖生成說明 |
| `md_restore` | 還原成中／英兩份 Markdown，整合 Vision 圖說 |
| `extra_info` | 自下而上生成各章節摘要（news/web/slides 為整份單次摘要） |
| `rag` | 重構樹結構、產生 RAG Markdown、建立 FAISS 向量庫 |

已完成的階段會自動跳過（依輸出檔案存在判斷），重跑時可續處理。

---

## 八、開發者

**專案結構**

```text
web_server.py          ← HTTP 路由、SSE、背景任務、登入
pipeline_core.py       ← 處理階段編排、並行、進度回報
paper_manager.py       ← 論文/對話 DB 存取層、資源載入（DB-backed）
ai_core.py             ← AI 介面（單一生成鎖、論文快取）
AI_professor_chat.py   ← 問答流程、RAG 檢索、決策路由
rag_retriever.py       ← 向量庫檢索
config.py / settings.py← LLMClient、EmbeddingModel、環境設定
db.py                  ← SQLAlchemy engine / session / init_db
models.py              ← ORM 表：User、Paper、Folder、Conversation
llm/                   ← Gemini 訊息格式轉換

processor/
  pdf_processor.py           ← PDF → Markdown（MinerU API）
  slides_processor.py        ← 簡報 PDF → PyMuPDF 渲染 + Vision 解析
  md_cleaner.py              ← 清除控制字元、過濾雜訊行
  doc_analyzer.py            ← 標題修正、文件結構分析
  md_processor.py            ← Markdown → JSON
  json_processor.py          ← JSON 清理
  tiling_processor.py        ← 切片
  translate_processor.py     ← 翻譯（含 doc_type / domain 風格提示）
  image_caption_processor.py ← 圖片 Vision 說明生成
  md_restore_processor.py    ← 還原 Markdown（整合 Vision caption）
  extra_info_processor.py    ← 章節摘要
  rag_processor.py           ← RAG 向量庫建立
  domain_detector.py         ← 首頁主題領域偵測

prompt/
  ai/                  ← 問答 prompt
  translate/           ← 翻譯 prompt
  doc/                 ← 文件分析 prompt（依文件類型分檔）

scripts/
  generate_password_hash.py  ← 產生登入密碼 bcrypt hash
  migrate_to_db.py           ← 一次性 import 腳本（支援 --dry-run / --rollback）

data/                  ← SQLite DB 檔位置（已 gitignore）
```

**資料持久化**

- 論文 metadata、對話歷史、使用者：DB（`data/mad-professor.db`，SQLite + SQLAlchemy）
- PDF / Markdown / 圖片 / 向量庫：檔案系統（`output/{owner_id}/{paper_uuid}/`）
- 已完全廢除舊的 `papers_index.json` 與 `chat_history.json`（改由 DB）

**如何加入新文件類型**

1. 在 `prompt/doc/` 新增 `heading_fix_<type>.txt` 與 `structure_<type>.txt`。
2. 在 `doc_analyzer.py` 的 `HEADING_FIX_PROMPTS` / `STRUCTURE_PROMPTS` 加入對應條目。
3. 在 `web_server.py` 的 `confirm_type` 的 `valid_types` 加入新類型字串。
4. 視需要在 `translate_processor.py` 的 style hint 與 `pipeline_core.py` 的簡化摘要判斷加入該類型。

**如何擴充 LLM model**

模型皆由環境變數注入（見〈四〉），新增模型只需改 `.env`；如需新增「用途」，於 `settings.py` 增一個變數並在對應 processor 取用，不需改動 `LLMClient`。

**log 路徑**

- 終端機只顯示 WARNING / ERROR
- `logs/pipeline.log` — pipeline / paper_manager / processor（DEBUG，輪替）
- `logs/chat.log` — AI_professor_chat / ai_core / rag_retriever（DEBUG，輪替）

---

## 九、部署

**GCP / 公網部署提示**

1. 設定 `ENVIRONMENT=production`，並務必設定強隨機 `SESSION_SECRET` 與 `AUTH_PASSWORD_HASH`。
2. `web_server.py` 預設綁 `0.0.0.0:8080`，建議**不要**直接對外，前面放反向代理負責 TLS。
3. 建議用 systemd 常駐 `python web_server.py`（venv 內），並設定 `Restart=on-failure`。

**Caddy + Let's Encrypt 自動 HTTPS（反向代理建議）**

```caddyfile
# /etc/caddy/Caddyfile
your-domain.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

Caddy 會自動申請並續期 Let's Encrypt 憑證。設定 `ENVIRONMENT=production` 後，session cookie 會強制走 HTTPS，與 Caddy 的 TLS 終結搭配即可。

> SSE 串流（問答、進度）走長連線，反向代理需停用對該路徑的緩衝（Caddy `reverse_proxy` 預設即可，Nginx 需 `proxy_buffering off;`）。

**備份策略**

```bash
# DB（一致性快照，勿直接 cp 含 WAL 的檔）
sqlite3 data/mad-professor.db ".backup 'backup-$(date +%Y%m%d).db'"

# 檔案（PDF / Markdown / 圖片 / 向量庫）
tar czf output-$(date +%Y%m%d).tar.gz output/
```

---

## 十、使用流程

1. 點擊左側「＋ 上傳文件」，選擇 PDF
2. 上傳完成後選擇文件類型（學術論文／書籍／技術文件／簡報／新聞／網頁存檔）
3. 點擊「確認，開始處理」
4. 等待 pipeline 完成後，點擊左側文件進入閱讀
5. 右上角切換中英文；右側輸入框進行 AI 問答

### 已知限制

- MinerU 對複雜子圖排版（如 Fig. 1a/1b/1c）的切割可能不準確
- 圖片被 MinerU 歸到錯誤 section 屬 MinerU 解析限制，無法從程式端完全解決

---

## 十一、本次重構主要改動

相對原專案 [LYiHub/mad-professor-public](https://github.com/LYiHub/mad-professor-public)：

- **Gemini API 取代 DeepSeek**：翻譯、問答、Vision 全面改用 Gemini
- **MinerU API 取代本地 magic-pdf**：PDF 解析改為呼叫外部 MinerU 服務
- **桌面 App → Web 架構**：FastAPI + 純 HTML/JS 前端，REST + SSE
- **登入功能**：單帳號 bcrypt + session，可安全部署公網
- **Pipeline 解耦與並行優化**：階段化編排，`analyze`∥`detect_domain`、`translate`∥`image_caption` 並行
- **主題領域偵測**：首頁自動判斷領域，注入翻譯與摘要提升術語準確度
- **DB 化**：論文 metadata、對話歷史、使用者改用 SQLite + SQLAlchemy，廢除 `papers_index.json` / `chat_history.json`
- **文件閱讀提前**：`md_restore` 完成後內容立即可讀，`rag` 完成後 AI 問答才解鎖
- **Web Search**：可開「搜網」開關，AI 結合 RAG + Google Search 回答，來源連結持久化至 DB
- **LLM model 細分**：後台（doc / vision / extra_info / translate）用 Flash、面對使用者（chat / web search / domain）用 Pro，速度與品質兼顧
- **字元清理**：pdf2md 後 NFKC 正規化（拆解 ligature 連字）、移除桌面版 emotion 殘留
- **套件精簡**：移除程式未使用的 `langchain` meta 套件（保留 langchain-core/-community/-text-splitters）

---

## 授權

Apache License — 詳見 LICENSE 文件。

## 致謝

感謝原專案作者 [LYiHub](https://github.com/LYiHub) 的創意與基礎實作。

感謝以下開源專案：

- [MinerU](https://github.com/opendatalab/MinerU) — PDF 解析引擎
- [Google Gemini](https://ai.google.dev/) — LLM、Vision 與 Embedding
- [LangChain](https://github.com/langchain-ai/langchain) — RAG 向量檢索框架
- [FAISS](https://github.com/facebookresearch/faiss) — 向量相似度搜尋
- [FastAPI](https://github.com/tiangolo/fastapi) — Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM 與 DB 抽象層
