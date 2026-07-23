# Mad Professor — TODO（最後更新 2026-07-18，SOP-COMPLY Check 收官）

> 本文件為 **Single Source of Truth**（依 `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §2.1）。
> **任何規劃 / 執行 / hotfix 前必先 view 框架文件**：`.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`
> 對應 template 位於 `.claude-logs/templates/template_plan.md` / `template_execution.md` / `template_hotfix.md`
>
> **狀態 Emoji**（依框架 §2.2）：⬜ 未開始 / 🔵 plan 中 / 🟡 WIP / ✅ done
> **任務生命週期**（依框架 §2.5）：done 後**必須**從下方 active 列表移除、完整表格追加 `archive/TODO_done_archive.md` + 下方索引區新增一行索引 + 同步類別索引。

---

## ✅ 已完成（索引）

> 完整成果表格與註解 → `archive/TODO_done_archive.md`（framework §2.1 雙層結構；hash 區間＝該任務表格首末 commit、依歸檔檔內出現序）。

- ✅ BE-Hotfix FITZ-HOTFIX-4 裸HTML中和與報頭集行號基準修正（`5756219`、1 commit·治 FITZ-ANCHOR 落地後兩樣本 E2E：Medium 技術文 95% 蒸發 + NHK en/zh 側首圖誤殺——**K1** `_neutralize_inline_html` 裸 HTML 標籤反引號中和〔模組層 `_INLINE_TAG_RE`〔`<` 緊跟字母才成標籤·`a<b` 不中〕·逐行 `` ` `` 切段僅偶數段包裹·**反引號守衛**防重包·**行數不變式**·接線 P1 ②' 清洗步、DocAnalyzer 判型前·無旗標〕治裸 `<script>` 致 marked 解析真 script→DOMPurify 連內文移除→31k 字蒸發 / **K2** R8 報頭集**原封行序基準**〔`run_phase3` 於 K3 刪行前呼 `_pristine_header_srcs=_load_header_srcs(…, full_text)` 傳 `_filter_source_figures`〔簽名加 `header_srcs:Optional[set]=None` 兜底〕·`_load_header_srcs`/`_collect_header_srcs` 本體零改〕治 R8 以 sidecar 原封行號掃 K3 位移後 text 致界外圖上移入窗被③誤殺〔行號位移家族第五例〕·whole mode 共用通道一刀修雙語首圖、重立雙語圖片對稱；`image_filter`/`fitz_processor`/`md_cleaner`/`section_engine`/`ingestion_engine`/`rag_indexer`/前端/A 軌零改·11 新測試〔K1 中和+行數不變+Browsers 段落防吞·K2 位移舊誤 DROP vs 新 KEEP+None 兜底·雙語對稱 E2E whole+section〕·1010→1021 passed·2 `.bak`·checkout `待 baron 回填`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor FITZ-ANCHOR LLM錨定前移與fitz幾何整形（`b48961a`…`505ce1e`、3 commits〔C1/C2/checkout〕·三輪 fitz hotfix 打地鼠後 baron 拍板架構轉向——重要性判斷全交 LLM 錨定、fitz 回歸幾何抽文字清垃圾——**U1** `_read_anchor_text` 裸抽前 `LITEDOC_ANCHOR_MAX_PAGES`(=2) 頁原始文字層送 cover-prompt〔零新增呼叫·裸文字天然含 chrome URL·空 fallback md 文首·`_extract_litedoc_metadata` 恢復單參〕/ **U2** `_reinject_title` promote-else-inject〔analyze 前·正規化比對·heading 已在不動/正文 promote+warning/缺席 inject+warning·空跳過〕整類標題誤殺終局保底 / **U3** HOTFIX-3 K2 sidecar 雙端同刀退場〔fitz `_URL_RE`+寫檔塊+`import json`、litedoc `_load_source_hints`+hints 全清·防半殘管線〕/ **U4** `_collect_page` ε 容差同位去重〔`(text,round(size,1))` 群內 `|dx|,|dy|≤settings.FITZ_DEDUP_EPSILON`(=3.0)·廢 HOTFIX-3 精確 key 漏抓 ±0.84pt 描邊·每頁獨立〕/ **U5** `_repeated_band_keys` 比例門檻 `need=max(2,ceil(len(pages)*0.5))`〔防少數頁重複內容誤殺·下限 2 保短件〕/ **U6** `section_engine._title_echo_match` 子字串分支加 `min/max>=0.5`〔防 4 字標題誤吃 88 字 lede〕·`md_cleaner`浮水印本體/K3/image_filter/ingestion_engine/rag_indexer/contracts/A 軌零改·23 新測試〔U4 容差/U5 比例/§3.1 fixture·U1 裸抽/U2 三分支/U3 dead code+publisher via anchor/U6 比值·**§7.2 實體 PDF 端到端**標題經回注存活+14 QA 成對+chrome 剝除〕·993→1010 passed·8 `.bak`·checkout `505ce1e`）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix FITZ-HOTFIX-3 同位重繪去重、chrome線索回收與full_text meta歸零（`8733d98`、1 commit·治日文 NHK 樣本 E2E「標題全滅+publisher 空」+族群掃描 en 側 meta 洩漏——**K1** `fitz_processor._collect_page` 同位重繪去重〔per-page `dedup_key`＝文字+座標+字級·過濾 text-stroke 列印重繪 ×4·防 md_cleaner 浮水印規則≥3 全殺誤殺 NHK 真標題·**每頁獨立不干涉跨頁 R2**〕/ **K2** chrome URL 回收〔`_assemble` 剝除點捕 `_URL_RE`·`parse` 落 `{pdf_file.stem}_source_hints.json` sidecar〕+ litedoc `_load_source_hints` 三級 stem 定位〔避 paper_id `_shadow` 陷阱〕+ `_extract_litedoc_metadata` `hints` 純加法**於 `[:4000]` 截斷後拼接**〔防長文尾接靜默失效·hint 只進 LLM 不寫 md〕補回 publisher / **K3** `_strip_meta_source_lines` full_text 行級 meta 歸零〔雙判據＝sidecar spans ∪ R6 值比對整行相等·複用 engine 正規化源·圖片行歸 R8 不碰·**接線在 echo-strip/R8 前**保 sidecar 行號基準〕一次覆蓋 en_text/whole/is_zh 三消費者·**恢復雙語文字對稱不變式**〔與 HOTFIX-2 圖片對稱成對〕·`md_cleaner`/`image_filter`/`ingestion_engine`/`rag_indexer` 零改·15 新測試〔幾何去重+浮水印放行/截斷窗斷言/K3 雙判據+時序+雙語對稱〕·978→993 passed·4 `.bak`·checkout `5b5f160`）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix FITZ-HOTFIX-2 報頭行界收窄與雙語圖片對稱（`53feed8`、1 commit·治 HOTFIX-1 後 E2E「B 軌大圖不見」——**K1** `_collect_header_srcs` 行界由「全部判型塊 max(end)」收窄為「**meta 型塊** max(end)」〔DocAnalyzer 把正文判 `intro_text`/`other` 撐大行界·v3 實物 hdr_end **119→10**·封面大圖與 Falcon 9 照片獲救〕+ 新增 `_HEADER_META_TYPES` 由 `_META_TYPES` 導出緊鄰定義**防常數漂移**〔與 `mark_meta_lines` 同源〕/ **K2** `_filter_source_figures` 新增 `_load_header_srcs` **三級定位**〔PDF stem 主路→glob 備路→`set()` fail-open；**嚴禁 `paper_id` 拼接**〔影子軌帶 `_shadow` 而實體檔無〕〕並注入 `make_figure_filter` 使**兩通道規則③必同步**〔原文通道原恆停用致 v3 en21 vs zh19 不對稱〕·**恢復雙語圖片對稱不變式**·單檔 litedoc+測試·10 新測試〔含 119 vs 10 對照組/同源守衛/對稱斷言〕·既有 C3 行界測試依 K1 更新契約留痕·968→978 passed·2 `.bak`·checkout `18eb19f`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor FITZ-HOTFIX-1 fitz路標題救回與雜訊通則修復（`e8d57a6`…`e6f3e44`、3 commits·八刀 R1-R8 治 baron 影子 E2E 四缺陷·`processor/fitz_processor.py` R1 圖框內文字排除+**R2 複合 key 救標題**〔列印 PDF 通案：真標題必撞自身頁首 chrome key〕+R3 三級 `###`〔連帶修正 body 字級只由非 band 行決定·既有測試攔下〕+R5 nav link-tiling 剝除〔x 區間聯集·≥3links 且 ≥60%〕/ `ingestion_engine` R6 `meta_values` 純加法〔整行相等非包含·判型成功與 soft-fail 兩路皆套用〕+litedoc **meta 抽取時序前移**+R7 數字短行清理〔markdown 語法守衛·行數不變式〕/ P3 R4 譯題餵 `_title_bare`〔真因＝LLM 回後綴變體致 web_server `endswith` 失配·**該檔 git diff 零**〕+R8 單點行級圖片過濾〔一次覆蓋 is_zh/whole/en_text·立**雙語圖片對稱不變式**〕·§7.2 整合測試 Checkout 補齊〔真實 PDF 八刀端到端〕·920→968 passed·47 新測試·8 `.bak`·checkout `f5a3ec6`）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor PIPE-SYNC-5 PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC（`cc53452`、1 commit〔合併版〕·治理債回灌兩真理源——PIPE-SPEC v8→v9〔§1.2.6 `ingestion_engine` 契約章家族**第 6 員**〔assemble 純函式四鐵律含 figure_filter hook〕+§1.2.6.1 litedoc 借用鏈退場/譯題單一源 + §1.2.2.1 `build_termmap` 事前定案 builder〔廢飛輪早退·三路收斂單一源·全文單一譯法可硬驗收〕+ roster 第 6 員 + 旗標 true 註 + Revision v9〕/ 母 plan U7 攝入現況+U8 roster+§8.5 補三案 ✅+Revision〔就地註解不 bump〕/ design spec F7 **廢長邊軸**改 `area<100000`〔IMG-FILTER 23 圖實測校正回灌·防誤殺 481×369 chart 重踩〕·就地 HTML 註解全包裹·§1.1 四凍結合約與 .bak diff 零差異·pytest 920 passed 零代碼副作用·3 `.bak`·⚠️ baron 將 tasks C1/C2 合併為單一 C1〔Checkout 已更正 §8 防對照困惑〕·⚠️ SPEC/design spec 留 gitignored baton〔審計靠 .bak+執行報告〕·FITZ/LANG-DETECT 留 PIPE-SYNC-6·checkout `9ca13aa`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor LANG-DETECT cover-prompt語言欄與source_lang正名（`c17e183`、1 commit·`pipelines/litedoc_pipeline.py` cover-prompt +`language` ISO 欄〔搭既有 metadata LLM 便車·零多呼叫〕+ `_resolve_source_lang` catch-all 限定合成〔啟發式非 en 維持原判·en 時雙重白名單 `^[a-z]{2,3}$` 拒 zh 前綴〔HOTFIX-1 鎖一 producer 端·與 P3 gate 謂詞同源〕·缺欄退啟發式 100% 等價〕+ P1 單點接點·根治拉丁語系判 en 致 GlobalGlossary 桶污染〔schema 已多語·破在偵測層〕·`classify_source_lang`/`GlobalGlossary` 零改·45 測試〔矩陣 37 案/§7.2 整合 en→it 貫穿 P2 build_termmap 捕參+en 對照〕·875→920 passed·⚠️ Check 首輪攔下 C1 未 commit 後重收官·checkout `2011a63`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-INGEST-FITZ born-digital文字層快速道與連字修復（`3cc3850`…`801f969`、3 commits·`processor/fitz_processor.py` `PDFParser` 第二 impl〔MinerU 同形 .md：字級分群字元權重判正文/座標閱讀序/跨頁頂底帶數字歸一剝除/圖 PNG-JPEG `page_{page_idx}_{xref}` 防衝突/零 `fitz.metadata` AST 守門〕+`median_page_chars`/`pipelines/ligature_repair.py` 雙閘連字修復〔替換前數字縮寫版本號排查+替換後系統字典優先 60 詞兜底·行數不變式〕/litedoc P1 `_ingest_markdown` 中位數閘門〔≥150 走 fitz·fail-open 退 MinerU·flag off byte 等價〕+②'修復步兩來源同享·§7.2 實體 PDF 整合〔修復前行號 sidecar 證行界對齊〕·831→875 passed·`LITEDOC_FITZ_ENABLED` env 關回·checkout `4b7e19a`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor IMG-FILTER 垃圾圖三規則確定性過濾（`de3a475`…`8cfaf5b`、3 commits·`pipelines/image_filter.py` 三規則閉包〔面積 100k/長寬比 4.0/報頭判型行界·stdlib 尺寸解析零 Pillow·fail-open·DROP 審計 log〕/engine `figure_filter` 純加法貫穿〔DROP caption used 標記防孤兒圖說〕/litedoc `_collect_header_srcs` 預掃接線〔行界收窄防誤殺 hero〕·門檻經 23 圖實測校正廢 spec F7 長邊軸〔481×369 KEEP 守門測試〕·§7.2 實體圖檔整合·805→831 passed·`IMG_FILTER_ENABLED` env 關回·checkout `2e03c2c`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor GLOSSARY-TERMMAP 事前定案術語表與glossary旗標開啟（`16a5f09`…`6b5c975`、5 commits·`GlossaryManager.build_termmap` 五路共用 builder〔切塊 census→分流廢早退→只翻未知→定案 upsert〕/三路 `_heal_glossary` 收斂單一源/translator 免括號句/litedoc 摘要型滑窗〔section_engine 純加法〕/旗標末位點火〔新預設 805 passed〕·接收 PIPE-INGEST 缺陷④⑤根治·checkout `0fab08a`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-INGEST litedoc攝入自有化與品質根治（`e7b9e6c`…`ab65208`、3 commits·B 軌自有攝入引擎 `pipelines/ingestion_engine.py`〔零文體字面量·注入式·figure 帶 content〕/C2 litedoc P1 切換借用鏈退場/C3 譯題單一源〔根治扉頁/分頁名/PDF Title 三受害者〕+cover-prompt OCR 自癒+dead code 清理·§7.2 key-changing 整合測試·748→780 passed·術語④⑤/括號移交 GLOSSARY-TERMMAP·checkout `3133333`）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor BRAINSTORM-1 brainstorming問答與視覺伴讀（`3602a42`…`c258af2`、3 commits·vendor superpowers brainstorming 不裝 plugin·C1 問答骨架 SOP+視覺伴讀指引〔溯源 header+spec→template_plan 對照+兩護欄+移除 auto-commit〕/C2 5 腳本+smoke 入 tools〔逐字＝上游·start-server.sh 僅 4 落點行·server.cjs 零編輯·smoke HTTP 200〕/Checkout·畫圖 server smoke 實證·零 .py）→ archive/TODO_done_archive.md
- ✅ BE-Refactor SOP-COMPLY logging與DB_SOP合規清帳（`98f8848`…`0dff639`、4 commits·25 exc_info 補齊+llm 吞例外留痕×AST grep-gate 守衛×paper_manager 13 裸 commit 全清〔自持 7 begin+借用 6 呼叫端協調〕·PROJECT-REVIEW 程式碼品質 #1 + DB SOP §5.2 關閉·745→748 綠燈·checkout `fb3e76a`）→ archive/TODO_done_archive.md
- ✅ BE-Refactor SEC-HARDEN 後端安全縱深加固（`52ebae8`…`3942e20`、5 commits·XFF 可信代理右向左+timing 等化×CORS 白名單×例外遮蔽×主題覆寫守衛·PROJECT-REVIEW #3/#4/#5/#6/#8 全關閉·715→745 綠燈·checkout `e287347`）→ archive/TODO_done_archive.md
- ✅ FE-Refactor SEC-XSS 前端輸出消毒（`d5ef6b6`…`9586866`、4 commits·DOMPurify 樞紐消毒×6 sink+邊角加固·708→715 綠燈）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix SEC-SECRET SESSION_SECRET fail-closed（`a7fa87f`、1 commit·移除硬編碼 fallback 常數×prod 未設/弱<32 拒啟動×dev 臨時隨機×708 綠燈·修 PROJECT-REVIEW 安全 #1 HIGH CWE-798）→ archive/TODO_done_archive.md
- ✅ FE-Refactor TEST-GREEN 前端CSS測試改讀分包（`a4e6e5b`…`3a71293`、2 commits·15 stale 斷言改讀 CSS 分包聯集×705 綠燈基線恢復）→ archive/TODO_done_archive.md
- ✅ FE-Refactor THEME-DEDUP 主題規格凍結與結構去重（`2380420`…`ef16383`、6 commits·26 token/16 選擇器凍結×9 支全正規化×模板+契約腳本）→ archive/TODO_done_archive.md
- ✅ FE-Refactor FE-CSS-GOV CSS 治理與作用域收斂（`32e3a1a`…`6fea7dc`、6 commits·C3/C4/C5 三度 re-scope）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor DOC-SYNC-1 設計文件現況對齊（`c8d6bcb`…`d4ce75a`、2 commits）→ archive/TODO_done_archive.md
- ✅ FE-Refactor FE-PERF-2 前端效能紅線四項實修（`337764e`…`bc2bcc4`、5 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor CONTEXT-1 session載入鏈瘦身與context治理（`1219a87`…`5d3be98`、5 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor RESCUE-1 遺失治理文件挽救（`5701fb0`…`a150915`、6 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor CHECKOUT-GUARD 收官 git-add 白名單鐵律（`81179d8`…`eb2b381`、3 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor FE-PERF-1 前端效能與渲染 SOP 建立（`3ec7b3f`…`c00604b`、3 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor WORKFLOW-5 ClawVM 混合治理 Hook 落地（`6fd2ce2`…`12564be`、7 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（`cbc512a`、1 commit）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor PIPE-SYNC-4 litedoc 與 section_engine 落地回灌母 plan 與 SPEC（`b1012bc`…`72bcb32`、6 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-LITEDOC LiteDocPipeline 策略管線（`b1012bc`…`2a9b2e3`、8 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-SECTION-BASE 共用 section 機制抽取（`e400789`…`b1012bc`、5 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor WORKFLOW-4 StraTA 任務成功率原理移植進文件治理模板（`44659be`…`8892bcd`、4 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC（`e15a7aa`…`f9c261b`、2 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正（`84c0825`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（`67de0d2`、1 commit）→ archive/TODO_done_archive.md
- ✅ FE-Hotfix RAG-12-HOTFIX-1 — 圖片 alt 內 LaTeX 破版（`88578dd`、1 commit）→ archive/TODO_done_archive.md
- ✅ FE-Refactor FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一（`1ecdc5c`…`b727161`、3 commits）→ archive/TODO_done_archive.md
- ✅ FE-Refactor RAG-12 前端 KaTeX 數學渲染（`013371a`…`c1c2a72`、6 commits）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC（`c54327c`…`43ad9c6`、4 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor META-NORM 封面元數據自癒飛輪與動態欄位登記（`ae407ef`…`caf31fa`、7 commits）→ archive/TODO_done_archive.md
- ✅ FE-Hotfix FE-RHYTHM-1 — 閱讀視圖「清單前寬後窄」垂直節奏治本（`3428581`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-4 — P1 空白頁 Vision 檢測（`91ad0b6`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-3d — 字面 `**` 未渲染粗體 + 裸 URL 破版（`7d6170d`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（`a486585`、1 commit）→ archive/TODO_done_archive.md
- ✅ FE-Hotfix PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（`1b8b939`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-3 — 簡報閱讀視圖排版打磨（`3f26d5c`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-2 — alt 破圖 / 母片重複日期 / F4 條列鬆散（`657a703`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-1b — F2 譯題旁路格式修補（`1a2ec98`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-SLIDES-HOTFIX-1 — B 軌簡報三缺陷緊急修補（`f933e54`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-SLIDES SlidePipeline簡報策略管線（`31dab5a`…`eb23bd5`、7 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放（`8893ad1`…`30e024e`、5 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正（`5b9477a`…`e88c304`、5 commits）→ archive/TODO_done_archive.md
- ✅ FE-Hotfix CHAT-EXPORT-HOTFIX-1 — 對話下載在 Dia 卡 8/8 不結束（`17cbf4f`、1 commit）→ archive/TODO_done_archive.md
- ✅ DOC-Refactor WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試（`2e4d4c9`…`6d11f13`、4 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RAG-ASYNC-HOTFIX-3 — zh 來源履歷 P3 改建 per-section rag_sections（`6794331`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RAG-ASYNC-HOTFIX-2 — B 軌補產 rag_tree.json（`300feb1`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RAG-ASYNC-HOTFIX-1 — section_summaries 跨譯 key 對位失效 + dead code（`300feb1`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-RESUME ResumePipeline策略管線（`f3d4e41`…`b0713e7`、9 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-RESUME v9 影子整合與規格同步（`b97958b`…`36db1cf`、7 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-RESUME TILING-HOTFIX-1 — TextTiling Embedding 速率超限 (429) 批次化修復（`702347a`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix PIPE-RESUME SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復（`3d2778a`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Refactor RESUME-P3 B軌履歷翻譯品質重構（`aec1f6f`…`a1d5d7f`、6 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RESUME-P3 HEADING-HOTFIX-1 — B軌履歷標題層級塌陷（`7c8a0da`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RESUME-P3 PARA-HOTFIX-1 — B軌履歷正文段落黏連（`2772822`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix RESUME-P3 META-HOTFIX-1 — B軌履歷 final 缺文件 header（`2ba97fc`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Refactor RAG-ASYNC P4 RAG 索引共用真理源與全 P2 摘要（`195e12b`…`0d73601`、7 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor RESUME-PERF-1 run_phase3 逐 section 翻譯並行化（`b110742`…`be49abe`、3 commits）→ archive/TODO_done_archive.md
- ✅ BE-Hotfix VISION-HOTFIX-1 — Vision 履歷轉錄非確定性（`3d5be32`、1 commit）→ archive/TODO_done_archive.md
- ✅ BE-Refactor MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次（`1f56547`…`01a4e5b`、4 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor MODEL-9-OPT Embedding連線與限流框架優化（`8feaa12`…`61d0f69`、4 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor TRANSLATOR 雙模式原子翻譯器（`1558f79`…`b55219b`、5 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor GLOSSARY-CORE 中央領域術語庫與跨語系一致性（`03d85c8`…`d4c34d5`、7 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor DOMAIN-NORM 領域標準化對齊器（`8d4f75f`…`1559b08`、5 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor API-PERF API 技術審計與效能防呆優化（`5326437`…`703cfaa`、6 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-SCAFFOLD web_server 雙軌派發 scaffolding（`13c1dcb`…`58e1b89`、3 commits）→ archive/TODO_done_archive.md
- ✅ BE-Refactor PIPE-CORE 三層解耦調度骨架（`aa786a1`…`13c1dcb`、4 commits）→ archive/TODO_done_archive.md
- ✅ GOLDEN-BASELINE 黃金基準存盤與退化比對（`3be0b0d`…`c0c64e9`、3 commits）→ archive/TODO_done_archive.md
- ✅ RAG-14-HOTFIX-1 — 緊急熱修復：對話置頂氣泡頂部穿透漏出修復（`a5b193f`、1 commit）→ archive/TODO_done_archive.md
- ✅ RAG-14 多標籤寬鬆格式跨文章 RAG 檢索與對話體驗升級（`6593962`…`595e3d8`、4 commits）→ archive/TODO_done_archive.md
- ✅ FE-AESTHETICS HOTFIX-1 — 前端學術扉頁自癒與排版靠左優化（`bf3c14b`…`452c652`、2 commits）→ archive/TODO_done_archive.md
- ✅ RAG-13-HOTFIX-1 — 緊急熱修復：自訂主題下拉選單捲軸無作用修復（`6598d2d`…`75ab18a`、2 commits）→ archive/TODO_done_archive.md
- ✅ RAG-13 自訂主題動態清單與選單優化（`9e041ed`…`690b04a`、3 commits）→ archive/TODO_done_archive.md
- ✅ FE-AESTHETICS 摘要工具列重構與正文扉頁美化（`3cf8acf`…`6947098`、3 commits）→ archive/TODO_done_archive.md
- ✅ INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新（`264dadc`…`878c7a2`、3 commits）→ archive/TODO_done_archive.md
- ✅ MODEL-10 MinerU 連線優化與運作維護 SOP（`19ddac8`…`17d187b`、3 commits）→ archive/TODO_done_archive.md
- ✅ OPTIMIZE-1 PDF上傳自動無損優化（`b8892be`…`93ab716`、3 commits）→ archive/TODO_done_archive.md
- ✅ WORKFLOW-2 流程模板重構與提示詞自動歸檔（`7a3332f`…`10f9561`、5 commits）→ archive/TODO_done_archive.md
- ✅ TODO-HOTFIX-1 TODO.md 緊急狀態與殘留修復（`a0d1951`…`5f3ef01`、3 commits）→ archive/TODO_done_archive.md
- ✅ WORKFLOW-1 流程簡化與文件治理（`1a0394c`…`8965725`、5 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7d Chat 改造（`8a1a0ec`…`a1adfbc`、5 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7d RAG 改造（`d6cb3df`…`b6622a1`、2 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7d RAG-7 doc_analyzer / md_cleaner 切 section 修正（`e2ed0e4`…`5c182cf`、2 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7? MODEL-9 連線彈性防禦（`dd18922`、1 commit）→ archive/TODO_done_archive.md
- ✅ Phase 4.7? MODEL-3 tiling 三合一優化（`e97ddd2`…`9177930`、3 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7? MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI（`aeb42cb`…`16f62d4`、3 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.X? RAG-1 Phase 2 Hashtag RAG 路由 + 雙語摘要 + Chat Token UI（`26a4439`…`f85b830`、3 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.X? RAG-1 Bug Fix 系列（`9877e54`…`94ed27d`、8 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.X? RAG-1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫（`9977428`…`49fe66a`、3 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.X? LOGGING refactor 統一日誌基建（`011cc8c`…`6e764ea`、3 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7? MODEL-1+2 Embedding 升級（`f415218`…`de649cc`、2 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7? RAG-8/9 翻譯保留排版下游 bug（`3a0c523`…`230ca13`、2 commits）→ archive/TODO_done_archive.md
- ✅ Phase 4.7e Resume 獨立 Pipeline（`ffb3000`…`70889aa`、7 commits）→ archive/TODO_done_archive.md

## 🟡 進行中 / ⬜ 未開始（依優先序）

### 🔴 高優先

- ✅ **GOV-PATH-FIX 校正下游治理檔 stale worktree 路徑**（hotfix·DOC-Refactor·`.claude-logs/hotfixes/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md`）
  - 校正 CONTEXT-1 C2 漏改之 3 下游治理檔殘留已刪除 worktree `hopeful-yalow-902c50`：`template_prompt_for_tasks.md`（工作目錄硬規則對齊 CLAUDE.md §3·元凶）/ `framework §9.1`（重點句去硬編）/ `GOVERNANCE_OVERVIEW.md`（6 導航連結改相對路徑·去死絕對前綴）
  - 驗收：3 活躍源 `grep hopeful-yalow-902c50` 零殘留 + GOVERNANCE_OVERVIEW `file:///`=0 + 4 相對目標實檔可解析；歷史檔依 WORKFLOW_SOP §2 不溯及既往、不動；fix `31f7500` + checkout 收官歸檔（hotfix 規劃書 mv→hotfixes/）；Checkout Hash：`52ebae8`（歸檔檔隨 SEC-HARDEN C1 commit 落地·SEC-HARDEN Check 自癒判定）

- 🔵 **CHAT-STRUCT-1 — 結構化欄位確定性回答（履歷聯絡 #5·選 C）**（**⚠️ 原 plan `.claude-logs/baton/2026-06-08_CHAT-STRUCT-1_結構化欄位確定性回答_plan_v1.md` 已隨舊 worktree 刪除遺失、待獨立重建**〔RESCUE-1 C4 標·見文末遺失清單〕；規格骨架保存於下列子項）
  - #5：履歷 candidate_name/phone/email/domain 只在 DB metadata_json + final_zh header、不入向量 → 「他的 email/電話?」RAG 撈不到（聯絡屬結構化、嵌入效果差、RAG 非對的工具）
  - 解法（選 C）：chat 路由層偵測結構化欄位意圖 → 直接從 paper metadata 取值、確定性模板回答、繞過 RAG；缺欄位明確「未提供」不幻覺；零向量/RAG 召回/schema 變動（純讀 metadata）
  - 狀態：**plan 本體遺失（隨 worktree 刪除）；規格骨架保存於本條目 + RAG-ASYNC #5 溯源 → 從旁證重建（RESCUE-1 B 類·獨立後開）；原 §7 八 OQ〔Q1 意圖機制/Q3 欄位集/Q4 值 pin〕待重建後拍板**
  - 性質：跨 chat 模組（AI_professor_chat + ai_router_prompt）；不依賴 #1/#2/#4（與 P4 向量路正交）

- 🔵 **QUEUE-1 v2 MinerU 雙實例 CFS 物理分流與協同避讓調度**（存活本體 `.claude-logs/baton/2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md`·**RESCUE-1 C1 已救回 + archive `.bak` 審計**）
  - 問題：MinerU 推理層 head-of-line 阻塞——大書（~300 頁）強佔 CPU 推理通道 10-20 分，後續小檔（履歷/論文）即使 Client Queue 拿第一名仍死等
  - 解法：雙 Docker 實例（`mineru-interactive` Port 8000 `cpu_shares:1024` / `mineru-batch` Port 8001 `cpu_shares:128`·相差 8 倍）+ Linux 內核 CFS 權重時間片搶佔 + Client 端動態頁數檢測雙埠路由 + `mineru_SOP_手冊.md` 運維更新
  - 與 PIPE 大改版**正交**（非 v1「Thread-level `sleep(2)` 避讓」；v1 已判**重構性廢除**，見文末遺失清單）
  - 工時：待 plan review（v2 本體存活·可直接進 tasks）
  - 依賴：無

- ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
  - 問題：切換 paper / 重新整理後，SSE chat history reload 功能缺失（API 合約需調整）
  - 工時：待 plan 評估（預估 1-2 commits）
  - 依賴：無


### 🟡 中優先

- ⬜ **RAG-4 前端引用顯示**（Commit 15 plan Q3）
  - footnote / 「參考章節」清單 / 連結回原文段落
  - 工時：2-3 個 commits（前端 markdown 渲染 + 點擊跳轉）
  - 依賴：15-2 已提供 section_path

- ⬜ **RAG-3 score 閾值 0.22 校準**（Commit 15 plan Q4）
  - 跑 1-2 週實際 query、收 B2 `[retrieve raw]` logging 數據
  - 用 `grep '\[retrieve raw\]' logs/*.log` 抽 raw score 分布
  - 依 p10/p50/p90 調整閾值
  - **L2 normalize 後預期區間**：raw score 會顯著拉寬、相關 chunks 落 0.45-0.75、無關 < 0.25
  - **推測閾值升到 0.35-0.45 區間**（B2 預設保留 0.22、待實測決定）
  - 透過 env override 動態調整：`export RAG_SCORE_THRESHOLD=0.40`（不需 commit）
  - 工時：1 個 commit（純調常數預設 + 加註解、本機 env 已可先調）
  - 依賴：等資料累積（不能立刻做）

- ⬜ **CHAT-3b 前端清理 POST /chat/history 殘留**（Commit 17-4 報告新加）
  - 17-1 已刪 saveChatHistory 函式定義、留 marker 註解（`static/index.html` L2422 + L2487 兩個 Phase 4.7d Commit 17-1 marker）
  - 17-4 已移後端 endpoint
  - 前端可清掉 marker 註解 / dead reference
  - 工時：5-10 分鐘、純清理
  - 依賴：無（與 CHAT-5 可一起做）

### 🟢 低優先

- ⬜ **RAG-5 短文合併上限 cap**（Commit 15-1 已知限制 #3）
  - 實測若 chunk 過大（> 20 text items）需加上限
  - 工時：觀察驅動、實際撞到才做
  - 依賴：實測撞到

- ⬜ **RAG-6 `_SHORT_DOC_TYPES` 寫進 HOW_TO_ADD_DOC_TYPE.md**
  - 補說明短文型決策標準
  - 工時：1 個小 commit、純 docs
  - 依賴：無

- ⬜ **CHAT-4 取消進行中對話功能**（Commit 17 plan Q7）
  - 用戶按 Esc / cancel button 中止 stream
  - broker 支援 cancel：`session.cancelled = True` → `_run_stream_background` 檢查
  - 工時：1-2 個 commits
  - 依賴：留 4.7e 之後

- ⬜ **CHAT-5 `paper_manager.save_chat_history` 移除（dead code）**（Commit 17-4 報告盤點發現）
  - 17-4 後 0 業務 caller、變 dead code candidate
  - 工時：5 分鐘、純清理
  - 依賴：無(與 CHAT-3b 可一起做)

### 🔵 候選（待 baron 評估、依 `.claude-logs/model_optimization_blueprint.md`）

- 🔵 **RAG-10 中文 Header Meta Block 軟換行渲染 bug**（user-facing 排版、修法 ~5 行、低風險）

  **問題**：論文 Header 區的「作者 / 日期 / 出處 / DOI / 關鍵字」blockquote 在前端渲染時全擠成一行、無斷行。

  **症狀範例**（Jian Xu et al. 2026-01-26 Wuhan University paper）：
  ```
  > 作者：Jian Xu、Xinxiong Jiang... 日期：2026-01-26 出處：Wuhan University 關鍵字：AI data center...
  ```
  預期：每個欄位獨立一行。

  **根因**：CommonMark / GFM 規範下、blockquote 內連續多行**無空行**時、會被解析為**軟換行（soft break）**、在 HTML `<p>` 內被瀏覽器渲染為**單一空格**。`marked.js` 預設行為符合此規範（已 grep `static/` 確認無 `marked.setOptions({ breaks: true })`）。

  **代碼證據**（grep `processor/md_restore_processor.py` 實測）：
  - `_render_header_en`（L435 簽名、meta_bits L460-L470）：
    ```python
    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **Authors**: {', '.join(...)}")  # ← 行尾無斷行標記
    if date:
        meta_bits.append(f"> **Date**: {date}")
    if venue:
        meta_bits.append(f"> **Venue**: {venue}")
    if doi:
        meta_bits.append(f"> **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")
    ```
  - `_render_header_zh`（L484 簽名、meta_bits L511-L519）：相同 pattern、中文欄位。

  **Markdown 標準斷行語法（三選一）**：
  1. 行尾雙空格 `"  "`（推薦、最低侵入）
  2. 行尾反斜線 `\`
  3. 行之間插入僅有 `>` 的空行

  **修法（推薦從後端產生器修正、不改前端）**：

  在 `_render_header_zh` + `_render_header_en` 兩處 `meta_bits.append(...)` 結尾、每行**字串末尾補兩個半形空格**：

  ```python
  # _render_header_en L460-L470
  meta_bits.append(f"> **Authors**: {', '.join(...)}  ")   # ← 末尾補 "  "
  meta_bits.append(f"> **Date**: {date}  ")
  meta_bits.append(f"> **Venue**: {venue}  ")
  meta_bits.append(f"> **DOI**: {doi}  ")
  meta_bits.append(f"> **Keywords**: {', '.join(keywords)}  ")

  # _render_header_zh L511-L519 同樣處理
  ```

  **為何不用前端 `marked.setOptions({ breaks: true })`**：
  - 全域開啟會把所有 paragraph 內的單換行都變 `<br>`、可能破壞原本應該軟換行的 chunk content 排版（如 PDF 內單句跨行的情況）
  - 從後端修正才是定點打擊、零副作用

  **預估工時**：~30 分鐘（含 pytest）

  **拆 commit**：單一 commit（FIX-1）即可、無依賴

  **新增 pytest**（推薦 2-3 個）：
  - `test_render_header_zh_appends_double_space_for_soft_break`
  - `test_render_header_en_appends_double_space_for_soft_break`
  - `test_rendered_meta_block_has_br_in_html`（mock 過一遍 marked.js 風格的解析、驗證 `<br>` 存在）

  **影響範圍**：
  - 僅影響 `_tiled.json` → 最終 markdown 的 Header 區渲染
  - **不需 backfill**（純前端 markdown 字串差異、既有 paper 重開即生效）
  - 既有 paper 重新前端 load 即修正、無需 vector store 重建

  **依據**：
  - CommonMark §6.7 Blockquote + §6.5 Hard line breaks
  - 修正後 HTML 預期含 `<br>` 而非 inline space

- ⬜ **MODEL-5 Structured Outputs router**（依 model_optimization_blueprint.md §3.2）
  - 升級對話路由器、利用 Gemini SDK Structured Outputs (JSON Schema)
  - Pydantic 聲明 `RouterDecision` 模型、消滅 regex + `json.loads`
  - 改 ai_chat / ai_router 相關檔案
  - 工時：1 commit
  - 依賴：無
  - 解 router 對格式變動的脆弱性

- 🔵 **MODEL-7c Metadata 語意前綴增強**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.3、新增）
  - 在生成 Chunk 文本時、最前端注入全域 Metadata 前綴
    - 範例：`"Candidate: John Doe | DocType: Resume | Section: Employment | [內文]"`
  - 將全域背景與局部細節強制綁定、強化語意特徵、embedding 也吃到 doc-level 語意
  - 工時：0.5 commit
  - 依賴：等 RAG-3 score 校準後評估必要性（可能 MODEL-1+2 已夠用、是否真的需要再評估）
  - **優先度低、純候選**

### 🚫 評估後不做（依 `.claude-logs/model_optimization_blueprint.md` / `.claude-logs/pipeline_decoupling_plan.md`）

以下提案經評估為過早優化 / 失控感 / 場景不符、暫不加入 TODO：

- **Parent-Child Indexing**（雙層檢索）
  - 提案：履歷子經歷小區塊向量化、父區塊回 LLM
  - 不做理由：履歷已切到 ### 公司層級、單份 7-8 chunks、痛點不大；實作複雜（chunk 結構 + retriever 邏輯 + schema 改動）、3-4 commits regression 風險高

- **128 Batching 自適應**（Embedding API 並行）
  - 提案：BATCH_SIZE 32 → 128、聲稱「30-50x 提速」
  - 不做理由：測試機 + < 10 份文件、batch size 增益無感（可能省 10-20 秒）；撞 429 風險上升、效益數字行銷話術不可信（實際提速 2-3x）

- **企業 Proxy（HTTP_PROXY/HTTPS_PROXY）**
  - 提案：受限網絡 / GFW 部署支援
  - 不做理由：個人測試機 + 台灣環境、無 firewall / 翻牆需求；未來若要賣企業客戶再做

- **AUTO Grounding（Gemini 自動聯網）**
  - 提案：Gemini 模型自己判斷何時聯網查 Google
  - 不做理由：論文 / 履歷分析場景需明確控制資料來源；AUTO 模式下 user 不知道答案來自文件還是 Google、UX 失控；應 user 明確 opt-in、不該預設啟用
  - **note**：手動 opt-in 聯網已存在於既有 `#web-search-toggle` 前端 toggle（`static/index.html` + `web_server.py:375 use_web_search` + `llm/client.py:118` Gemini Grounding）、整鏈路已通；不需新增 task 重做

- **Pipeline 解耦重構（pipeline_decoupling_plan.md 全套）**
  - 提案：17+ 檔重寫、`BaseStage` / `Context` / `Observer` / `Strategy` 完整體系
  - 不做理由：過早抽象、Mad Professor 是 2 人 / < 10 文件規模；7e-2 v2 `KNOWN_DOC_TYPES` + `check_doc_type_registry.py` 已解 80% 痛點；重構期 regression 風險巨大、機會成本超過所有收益；候選漸進式小手術（dict lookup parser / 並行 helper / module-level constants）可考慮、但全套重構不做

- **MODEL-6 聯網搜尋自動 Fallback 降級路由**（依 `.claude-logs/ref/model_optimization_blueprint.md` §3.2）
  - 提案：RAG max score < 0.35 時、自動切換 Web Search + Google Grounding
  - 不做理由：跟既有「AUTO Grounding 不做」決策**直接衝突**、本質是 trigger condition 不同的 AUTO Grounding；user 不知道答案來自文件還是 Google、UX 失控；mad-professor 定位是「論文/履歷分析助手」、用戶問問題期望基於文件
  - **未來若要做、改為「手動 opt-in 聯網按鈕」**、用戶按下才聯網 + 回答時明確標 [Google Search]

- **MODEL-7b 中英雙語對齊嵌入**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.2）
  - 提案：中英混雜文件、chunking 前拼接「原文 + 譯文」一起 embed、提高跨語召回
  - 不做理由：**gemini-embedding-2 是多語旗艦模型、跨語對齊本身就比舊 model 強得多**（MODEL-1+2 已內建解決 80%）；拼接後每個 chunk 大小翻倍、API tokens / storage 翻倍、是針對舊 model 的 workaround
  - **未來若 B2 backfill 後跑 1-2 週仍有跨語檢索品質問題、再重新評估**

---

## 索引（依類別）

### RAG（11 項 active）
- ✅ ~~LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放~~（已落地、C1 `8893ad1` + C2 `9849600` + C3 `c5b0c31` + C4 `6c0e8d2` + C5 Checkout 收官；③ retriever 自載咽喉〔_get_vector_store 完全 miss 呼 loader 自載〕+ is_ready loader-aware + 單一共享 RLock〔loader 鎖外防 AB-BA、修正 tasks §4.2 兩鎖隱患〕+ 啟動接線 set_loader + cap 5→100 + 釋放策略〔/content 換篇 gate·F1 + /upload 開關 + 跳過 active_streams + gc〕；治本 API-PERF C3 lazy-load 只載當前 paper 致 retrieve_multi 漏召其餘 tagged 篇〔#cv 只召當前篇〕；非 RAG-MULTI-1/非模型；test_lazyload_multi.py 10 測試〔含 §7.2 整合〕；⚠️ baron E2E 驗 #cv 涵蓋全 6 位）
- ✅ ~~RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正~~（已落地、C1 `5b9477a` + C2 `82b95b1` + C3 `b5f9ce4` + C4 + C5 Checkout 收官；retrieve_multi 廢全域 top-k 飢餓→每篇保底覆蓋〔min(floor_k,max(1,cap//N))+不足全拿+補位排除已選+N>cap最高分截斷〕+ 廢 RAG_MULTI_TOP_K 立 FLOOR_K/MAX_CHUNKS + ai_character_prompt 禁 [N] + test_rag_multi.py 11 測試；治本「6 篇擠成 2 人、吳焴倫碩士漏召」；五路通用；⚠️ shadow 不過濾＝U7 刻意副作用、baron 影子 E2E 驗多人涵蓋）
- ✅ ~~RAG-14 多標籤寬鬆格式跨文章RAG檢索與對話體驗升級~~（已落地、C1 `6593962` + C2 `b8e8770` + Check 收官 + 補漏 `595e3d8`）
- ✅ ~~RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI~~（已落地、P2-1 + P2-2 + P2-3 三 commit、見 ✅ 完成區）
- ✅ ~~RAG-1 Phase 1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫~~（已落地、R1 + R2 + R3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
- ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）
- RAG-3 score 校準（中、等數據）
- RAG-4 前端引用顯示（中）
- RAG-5 合併 cap（低）
- RAG-6 docs（低）
- 🔵 RAG-10 中文 Header meta block 軟換行渲染 bug（候選、修法 ~5 行、user-facing 排版）
- ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
- ✅ ~~RAG-12 LaTeX KaTeX 渲染支援~~（已落地、自託管 KaTeX 0.16.47 + 三階段順序佔位、C1-C6 收官）
- ⚙️ ~~RAG-2 backfill CLI~~（合併到 MODEL-8、見 MODEL 區）
- ✅ ~~RAG-7 doc_analyzer 切 section~~（已落地、拆 RAG-7a `e2ed0e4` + RAG-7b `5c182cf`）
- ✅ ~~RAG-8 md_restore / translate table 渲染 bug~~ `230ca13`
- ✅ ~~RAG-9 markdown `~` 誤判刪除線~~ `3a0c523`

### Chat（3 項 active）
- CHAT-3b 前端清理（中）
- CHAT-4 取消對話（低、留 4.7e 之後）
- CHAT-5 dead code 清理（低）

### MODEL（0 項中優先 / 2 項候選 / 6 項已落地）
- ✅ ~~MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次~~（已落地、C1 `1f56547` + C2 `d7f26be` + C3 `8c5a0eb` + C4 收官；換文字 embedding GA 模型恢復真批次 + task_type 非對稱；config.py embed_documents token-aware 貪婪拆批 + log 正名 embedding_batch_fallback；⚠️ 向量值改變→各環境須 .env 換用 + regen_rag --all 重嵌 + resume 單路 Golden 重捕〔baron 運維〕）
- ✅ ~~MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、合併原 RAG-2）
- ✅ ~~MODEL-1+2 Embedding 2 升級 + L2 正規化 + 短 chunk 過濾~~（已落地、B1 `f415218` + B2 `de649cc`）
- ✅ ~~MODEL-3 短文 Bypass + 公式穿透 + 段落滑動~~（已落地、B1 + B2 + B3 三個 commit、hash 待 push 後回填）
- 🔵 MODEL-5 Structured Outputs router
- 🔵 MODEL-7c Metadata 語意前綴（候選、低優先、等 RAG-3 結果再評估）
- ✅ ~~MODEL-9 連線彈性防禦~~（已落地、`dd18922`）
- ✅ ~~MODEL-9-OPT Embedding連線與限流框架優化~~（已落地、C1 `8feaa12` + C2 `9a44d41` + C3 `e86ced9` + C4 收官；EmbeddingModel Semaphore + retry_call 統一退避 + embed_documents 批次降級；不改向量值/不觸發 Golden 重捕；OQ3 RPM 令牌桶屬上線觀察項）
- ✅ ~~MODEL-10 MinerU 連線優化與運作維護 SOP~~（已落地、C1 `19ddac8` + C2 `991258d` + Check 收官）

### Phase 4.7e Resume Independent Pipeline（全完工）
- ✅ ~~7e-1 v2~~ `1fb2d7b`
- ✅ ~~7e-1 v2 hotfix~~ `eb2164c`
- ✅ ~~7e-2 v2~~ `70889aa`
- 7e-3 v2 端到端驗證（無 commit、純驗證、baron OrcStack 重新上傳 3 份 backfill 後收尾）

### WORKFLOW（✅ 已完成）
- ✅ ~~WORKFLOW-1 流程簡化與文件治理~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-2 流程模板重構與提示詞自動歸檔~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-3 跨 Phase 接縫契約與收官前整合測試~~（已落地、C1 `2e4d4c9` + C2 `386c1ce` + C3 `f14dcd9` + C4 收官；DOC-Refactor 治本 RAG-ASYNC #1 接縫缺陷——WORKFLOW_SOP §7 跨 Phase 接縫契約〔含 worked example〕+ 收官前整合測試〔key-changing transform、Checkout 必驗、顯式豁免〕+ §4.2 A6 / template_plan 升 plan 結構 SSOT / framework §4.1 改引用 template〔消滅 doc-drift〕；自身 DOC 無 handoff 整合測試豁免；plan v1/v2/v3 三版保留作 §1.9 軌跡）
- ✅ ~~WORKFLOW-4 StraTA 任務成功率原理移植進文件治理模板~~（已落地、C1 `44659be` + C2 `0e8cb77` + C3 `757dee6` + C4 收官；DOC-Refactor 移植 StraTA〔2605.06642v1〕四原理進 5 治理模板——U1 prompt_for_run 讀 plan〔conditioning re-inject 策略 z〕/ U2 execution §1 對齊欄 / U3 execution §自評雙軸〔負向防錯 + 正向「推進哪個 U-N」防做白工〕/ U4 template_plan §2.5 條件化多候選〔diverse rollout·高風險才觸發·語意分散〕+ prompt_for_plan 同步 + Q5 stale 校正 / U5 prompt_for_check 減負前移〔維度三/五前移分攤·非省略·聚焦 U-coverage+§7.2〕/ U6 五模板 marker+StraTA 誠實前提註；**WORKFLOW_SOP §4 五維度定義未動**；§7.2 純 DOC 顯式豁免；零業務代碼、640 passed 基線；見 ✅ 完成區）
- ✅ ~~WORKFLOW-5 ClawVM 混合治理 Hook 落地~~（已落地、C1 `6fd2ce2` + C2 `306797a` + C3 `2c14d4a` + C4 `c107bfd` + C5 `6ab46b9` + C6 `37f3ded` + C7 Checkout 收官；ClawVM 論文〔2604.10352v1〕——純文件約束＝discretion 結構性不足、跨出純文件用真實 Hook〔harness enforcement〕；C1 SessionEnd dry-run gate〔裁定不能 block→DIRTY-RESET Observable Fault·連鎖修正 exit 0+JSON 非 exit 2、python3 非 jq〕/ C2 baton 3-Phase 非破壞性寫入〔不可繞過〕/ C3 template Fidelity Floor 三維度〔機器可讀 fidelity_floor:〕/ C4 pre_tool_guard 截斷守衛〔防誤觸·sentinel 可繞過·truncation 8/8〕/ C5 dirty_reset_guard〔僅可觀測·dirty_reset 4/4〕/ C6 settings 掛載樣本+專案級部署 SOP；三道防線威脅模型誠實標註；§7.2 純治理+hook 豁免；零業務代碼；⚠️ baron 各環境手動掛載 .claude/settings.json + 重啟生效；見 ✅ 完成區）

### CONTEXT (✅ 已完成)
- ✅ ~~CONTEXT-1 session 載入鏈瘦身與 context 治理~~（已落地、C1 `1219a87` + C2 `44f6d00` + C3 `3c19213` + C4 `b154478` + C5 checkout 收官；DOC-Refactor 依五文獻稽核〔baton/context_engineering_governance_audit.md 長駐規格源〕——C1 baton wildcard→僅 README（-123KB/session）+ @path 排序原則 / C2 §3/§4 stale worktree→主 repo 雙視圖 / C3 FRAMEWORK §2.1 雙層結構＋check/run 模板雙源 / C4 TODO 1,428→467 行（-67.3%）＋本歸檔檔建立〔byte 逐字+hash 集合全等雙鐵證〕；§7.2 純 DOC 豁免；零業務碼；⚠️ baron 各環境 git pull 後重啟 session 生效）
- ✅ ~~RESCUE-1 遺失治理文件挽救~~（已落地、C1 `5701fb0` + C2 `522002b` + C3 `1df608a` + C4 `d3a6c07` + C5 checkout 收官；DOC-Refactor 治舊 worktree 刪除致 baton git-ignored 文件遺失——U1 QUEUE-1 v2〔MinerU 雙實例 CFS〕救回 + archive `.bak` / U2 PIPE-SPEC v8 依 v7 `.bak`+執行報告+現役 code 重建〔D8.1 逐字守·D5/D5b 非 byte-identical〕/ U3 MODEL-10 殘留 mv→archive / U4-U5 TODO 失效引用總修正+遺失清單審計〔INFRA-2 取代/QUEUE-1 v1 廢除/INFRA-4 正名非遺失〕/ U6 baton 慣例守恆〔archive `.bak` 防再遺失閘門·Q3 本體長駐〕；工作目錄 baron 拍板覆蓋 §3 改主 repo；§7.2 純 DOC 豁免；零業務碼；B 類 CHAT-STRUCT-1/TRANSLATE-BOOK v7 各自後開）

### DOC-SYNC (✅ 已完成)
- ✅ ~~DOC-SYNC-1 設計文件現況對齊~~（已落地、C1 `c8d6bcb` + checkout 收官；DOC-Refactor 清帳版對齊 design/docs 至 `index.html@8e5d1fa`——components 幽靈去毒〔title-meta ⚠️ 未實作 / msg 家族 ⚠️ 半實作 / dropdown-popup v3 勘誤零碰〕+ dom-reference 補 30 真缺 ID〔18 為既載格式盲點〕75/75+Modal 七家族 + token 三檔零差戳；輕量欄位≤160 行、零代碼、四 deviation 誠實裁決；§7.2 純 DOC 豁免；FE-CSS-GOV deep-doc〔ownership map/@layer 原則/theme-guide 契約改寫〕之前置）→ archive/TODO_done_archive.md

### CHECKOUT-GUARD (✅ 已完成)
- ✅ ~~CHECKOUT-GUARD 收官 git-add 白名單鐵律~~（已落地、C1 `81179d8` + C2 `dbd6d24` + checkout 收官；DOC-Refactor 治 FE-PERF-1 收官跨任務混檔——`WORKFLOW_SOP §3` 立「收官 git-add 白名單鐵律〔逐檔·禁 `git add .`/`-A`/`<目錄>`·commit 前 `git diff --cached` staged 自檢〕+ checkout 執行報告鐵律」+§99.2 v6·三模板〔run/check/execution §8 警語 + check 收官第五步自檢/第六步 mandate 報告〕；§2.5 純文件鐵律選定〔hook enforcement 列 backlog〕；§7.2 純 DOC 豁免；零業務碼；**首次 dogfood checkout 執行報告鐵律 + Check 階段當場攔下 C2 未 commit〕**）

### BRAINSTORM (✅ 已完成)
- ✅ ~~BRAINSTORM-1 brainstorming問答與視覺伴讀~~（已落地、C1 `3602a42` + C2 `2113db1` + Checkout 收官；DOC-Refactor vendor superpowers brainstorming〔`obra/superpowers@d884ae0`〕不裝 plugin——C1 新建 sop/ 作業 SOP〔問答骨架 8 步 + 落點 baton/ + 溯源 header + spec→template_plan 對照〔四樣護欄留階段 1〕+ 兩護欄 + 移除 auto-commit〕+ 視覺伴讀指引〔scripts/→.claude-logs/tools/〕/ C2 vendored 5 腳本+smoke 入 tools/〔4 檔逐字＝上游·start-server.sh 僅 4 落點行〔.superpowers/brainstorm→.claude-logs/baton/.brainstorm〕·server.cjs 零編輯·**smoke 實測 HTTP 200 端到端**〕；全文完整根路徑防呆；§7.2 純 DOC+tooling 豁免；零 .py/.bak；⚠️ baron E2E 兩路〔純問答路 spec 落 baton+溯源 header / 視覺伴讀路 server 起+瀏覽器+events+mockup 落 baton gitignored〕）

### SOP-COMPLY (✅ 已完成)
- ✅ ~~SOP-COMPLY logging與DB_SOP合規清帳~~（已落地、C1 `98f8848` + C2 `68987e8` + C3 `0dff639` + checkout 收官；BE-Refactor 實施專案自身 logging/database SOP 清帳——C1 日誌合規〔9 檔 25 處 except 內 logger.error 補 exc_info〔AST 精確·排除 14 續行假陽性+1 非-except 守衛〕+ llm/client:181 吞例外改 warning(exc_info) 留痕 + tests/test_sop_comply_guard.py AST grep-gate 防回歸〕/ C2 自持交易守護〔paper_manager 7 處 with s.begin() 移除顯式 commit·begin 置 session 起始防 autobegin·後讀 u.id/c.id 外移等價〕/ C3 借用交易呼叫端協調〔原子：6 helper 移除 session.commit()〔create_folder 補 flush 保 f.id〕+ web_server 5 folder/tag 端點包 begin〔ValueError→400 保留〕+ 3 測試檔 15 寫入區塊包 begin〔斷言零動〕〕；paper_manager 裸 commit 13→0 全清、745→748 passed；C1/C2 共檔 paper_manager 以 C2 .bak 分離 staging 乾淨分次 ship；範圍外債 tools/regen_rag.py:252 留 baron 拍板）

### SEC-HARDEN (✅ 已完成)
- ✅ ~~SEC-HARDEN 後端安全縱深加固~~（已落地、C1 `52ebae8` + C2 `a5e2bd4` + C3 `bc5d5f4` + C4 `3942e20` + checkout 收官；BE-Refactor 治 PROJECT-REVIEW 安全縱深 5 項——C1 login 加固〔TRUSTED_PROXIES 可信代理閘控·XFF 右向左解析廢最左值封偽造繞過 rate-limit + dummy bcrypt timing 等化〔錯帳號/未設 hash 均跑·認證判定零動〕〕/ C2 CORS 收斂〔CORS_ALLOW_ORIGINS 顯式白名單拒 `*`·methods 實況收斂·不啟用 credentials〕/ C3 例外遮蔽〔broker+主軌/影子軌三 broad-Exception client 出口改通用訊息+exc_info=True·排除 3 處 ValueError 業務驗證〕/ C4 主題覆寫守衛〔BUILTIN_THEMES frozenset·sanitize 後 lower() 命中即 400·write_bytes 前攔截·既有 5 道過濾零弱化〕；tests/test_sec_harden.py 30 測試、715→745 passed；C1 deviation：stale XFF 測試契約同步〔test_api_performance_and_robustness〕；⚠️ 反向代理部署須設 TRUSTED_PROXIES、生產跨源須設 CORS_ALLOW_ORIGINS）

### SEC-SECRET (✅ 已完成)
- ✅ ~~SEC-SECRET SESSION_SECRET fail-closed~~（已落地、hotfix `a7fa87f` + checkout 收官；BE-Hotfix 治 PROJECT-REVIEW 安全 #1 HIGH〔CWE-798 公開硬編碼簽章金鑰致 admin 認證繞過〕——settings.py 移除硬編碼 fallback 常數、未設生成臨時隨機密鑰〔`token_urlsafe(48)`〕+ `SESSION_SECRET_IS_EPHEMERAL` 旗標；web_server.py 生產環境未設 / 過弱〔<32〕金鑰拒絕啟動；新增 test_session_secret_failclosed.py〔3 測試·autouse 防污染 fixture〕；§5 SOP 雙核查合規、全套件 708 passed；review 補強弱金鑰守衛 + 測試污染清理 + 雙檔常數檢查）

### TEST-GREEN (✅ 已完成)
- ✅ ~~TEST-GREEN 前端CSS測試改讀分包~~（已落地、C1 `a4e6e5b` + checkout 收官；6 測試檔新增 CSS 分包聯集源〔`CSS_SURFACE`/`_css_surface()`·sorted glob 決定性〕+ repoint 15 stale 斷言〔pattern 零改寫〕、20 通過測試零回歸；全套件 690→705 passed / 0 failed 綠燈基線恢復；治 FE-CSS-GOV C1 拆檔致測試源與被測物脫節）

### FE-PERF (✅ 已完成)
- ✅ ~~FE-PERF-2 前端效能紅線四項實修~~（已落地、C1 `337764e` + C2 `0de91af` + C3 `b2f21d8` + C4 `8e5d1fa` + checkout 收官；FE-Refactor 實碼落地 Osmani 稽核 FE 包——C1 marked 9.1.6 自託管 / C2 defer+DOMContentLoaded 整包〔零重排〕 / C3 rAF+160ms 串流節流〔四出口收斂·管線零觸碰·node smoke 5/5〕 / C4 字型 preload+scroll passive+content-visibility 記憶尺寸型；U8 相容底線 Safari 18+ 拍板；首次 FE 必讀 SOP 實碼 dogfood；零後端零 golden；⚠️ baron 瀏覽器 E2E 七項）→ archive/TODO_done_archive.md
- ✅ ~~FE-PERF-1 前端效能與渲染 SOP 建立~~（已落地、C1 `3ec7b3f` + C2 `4fb2248` + checkout 收官；DOC-Refactor 以 Osmani《How modern browsers work》稽核〔`baton/frontend_browser_standards_audit.md`〕立 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`〔效能 7 條紅線+渲染正確性陷阱 6 類 hotfix 溯源+驗收檢查表+§99.1 重複防護·120 行〕+ 回填 WORKFLOW_SOP §1.1/§1.4 FE 必讀 SOP+§99.2 v5〔補後端有/前端無之治理不對稱缺口〕；§2.5 sop/ 選定〔workflow-gated 不污染 @path〕；§7.2 純 DOC 豁免；零業務碼；歷史經 pre-fe-rebuild 備份後重寫為乾淨 commit 邊界；稽核 7 條實修屬另案）

### FE-AESTHETICS (✅ 已完成 + 🟡 HOTFIX-1 進行中)
- ✅ ~~FE-AESTHETICS 摘要工具列重構與正文扉頁美化~~（已落地、C1 `3cf8acf` + C2 `b735a94` + Check 收官）
- ✅ ~~FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化~~（已落地、C2-hotfix `bf3c14b` + Check 收官）

### FE-RHYTHM (✅ 已完成)
- ✅ ~~FE-RHYTHM-UNIFY 閱讀視圖垂直節奏統一~~（已落地、C1 `1ecdc5c` + C2 `a9f2c3a` + C3 Checkout 收官；單一 margin-top flow 模型〔基準流 4/非標題→標題 6/標題→* 2/p→清單 1〕取代逐交界補丁、**完全消滅 `:has()`**〔相容 Safari 14+〕、收編 FE-RHYTHM-1、取消擬議 FE-RHYTHM-2、4 主題垂直 margin 移交 base；零 .py、631 passed；⚠️ baron 三軌×四主題視覺 E2E、無 golden 重捕）
- ✅ ~~FE-RHYTHM-1 閱讀視圖「清單前寬後窄」垂直節奏治本~~（已落地、`3428581`；2 條 `:has()` p↔清單交界補丁；後由 FE-RHYTHM-UNIFY 收編為統一 flow 模型）

### RAG-13 (✅ 已完成)
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）

### RAG-13-HOTFIX-1 (✅ 已完成)
- ✅ ~~RAG-13-HOTFIX-1 自訂主題下拉選單捲軸無作用修復~~（已落地、C1 `6598d2d` + Check 收官）

### INFRA (0 項 active)
- 🚫 ~~INFRA-2 PipelineCore第一階段切分與定規~~（**遺失·結案**——原 plan 隨 worktree 遺失、產出物已由 PIPE-SPEC + PIPE-CORE 取代；RESCUE-1 C4、見文末遺失清單）
- ✅ ~~INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新~~（已落地、C1 `264dadc` + C2 `9e05466` + Check 收官）

### QUEUE (1 項 active)
- 🔵 QUEUE-1 v2 MinerU 雙實例 CFS 物理分流（高、存活本體 `.claude-logs/baton/2026-05-29_QUEUE-1_雙實例CFS物理分流與協同避讓調度_plan.md`·RESCUE-1 C1 救回）
- 🚫 ~~QUEUE-1 v1 文件優先權協同避讓調度器~~（**遺失·重構性廢除**——PIPE-SPEC §3.1 審計〔Early-Emit + RAG 異步 + API-PERF Semaphore 覆蓋〕；見文末遺失清單）

### OPTIMIZE (1 項 active)
- ✅ ~~OPTIMIZE-1 PDF 上傳自動無損優化~~（已落地、C1 `b8892be` + C2 `28f098e` + C3 收官）

### GOLDEN-BASELINE (✅ 已完成)
- ✅ ~~GOLDEN-BASELINE 黃金基準存盤與退化比對~~（已落地、OP-1 `3be0b0d` + OP-2 `74d34e8` + Check 收官；PIPE 大改版階段 1 完成）

### PIPE-CORE (✅ 已完成)
- ✅ ~~PIPE-CORE 三層解耦調度骨架~~（已落地、OP-1 `aa786a1` + OP-2 `effb155` + OP-3 `84b9b30` + Check `13c1dcb`；PIPE 大改版階段 1 骨架，`pipelines/` 六模組）

### PIPE-SYNC (✅ 已完成·真理源回灌)
- ✅ ~~PIPE-SYNC-5 PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC~~（已落地、C1 `cc53452`〔合併版·三文件一次回灌〕+ Checkout 收官；治理債——PIPE-SPEC v8→v9〔**§1.2.6 `ingestion_engine` 契約章＝共用真理源家族第 6 員**〔`assemble` 純函式零文體字面量·四鐵律含 figure_filter hook〕+ §1.2.6.1 litedoc 借用鏈退場/譯題單一源 + **§1.2.2.1 `build_termmap` 事前定案 builder**〔五步·廢飛輪早退·三路 _heal_glossary 收斂單一源·全文單一譯法可硬驗收〕+ roster 第 6 員 + `LLM_USE_GLOSSARY_ALIGN` 預設 true 註 + Change Log/Revision v9〕/ 母 plan v10 就地補註〔U7 攝入現況/U8 roster/§8.5 補 PIPE-INGEST·GLOSSARY-TERMMAP·IMG-FILTER 三案 ✅/Revision·沿 PIPE-SYNC-4 不 bump〕/ design spec F7 **廢長邊軸**改 `area<100000`〔IMG-FILTER 23 圖實測校正回灌〕；§1.1 四凍結合約與 .bak diff 零差異、零 .py、pytest 920 passed；⚠️ baron 將 tasks C1/C2 合併為單一 C1、Checkout 已更正 §8 為合併版防對照困惑；⚠️ SPEC/design spec 留 gitignored baton〔審計＝3 `.bak` 改前快照 + 執行報告 delta〕；FITZ/LANG-DETECT 契約回灌留 **PIPE-SYNC-6**）
- ✅ ~~PIPE-SYNC-4 litedoc 與 section_engine 落地回灌母 plan 與 SPEC~~（已落地、C1 master plan v10 回灌〔D1 technical 排除/D2 LiteDoc ✅+順序/D3 三大→家族/D4 順序註/v6〕+ C2 PIPE-SPEC 回灌〔§1.2.5 section_engine 契約章 + §1.2.4 MetaNormalizer 契約章 + §1.1.1 litedoc 旁路 + 家族措辭 + v8;D8.1 §1.3 L140/§3.3 15k/§2 ≥10/四凍結合約未動〕+ C3 HOW_TO_ADD B 軌範式〔頂部 A/B banner + §1.4 裝飾器機制+A/B 對比+U2.1 映射;A 軌 §2-§7 不動〕+ C4 Checkout 收官；共用真理源家族定調〔原始三大 + MetaNormalizer 第 4 + section_engine 第 5〕；§7.2 純 DOC 豁免、零代碼 686 passed；SPEC 本體長駐 baton 不版控、.bak→archive、master plan/HOW_TO_ADD tracked）
- ✅ ~~PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC~~（已落地、C1 SPEC v7〔D1 slides P3 drift/D2 golden A/B 軌/D3 alt LaTeX/D4 is_blank/D6 rag_sections §1.1.2/D7 rag_tree_json/D5〕 + C2 master plan 補註⁸〔§8.5「B 軌另捕」措辭修正〕 + C3 Checkout 收官；slides 路 7 hotfix 回灌兩真理源、四層交接+旁路全對稱〔D6 補 rag_sections 旁路登記〕；§7.2 DOC 豁免、零代碼 640 passed；SPEC 就地版控、master plan v10 plans/）
- ✅ ~~PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC~~（已落地、C1 `c54327c` + C2 `9666b20` + C3 `29f13ca` + C4 Checkout 收官；母 plan 補註⁶〔U1 矛盾/U2 stale/U3 key 母句/U8/U5 指標〕+ SPEC v6〔key 契約凍結/zh 路/§1.3.1 Vision 共用規格/-001 樣例/rag_tree 歸屬/三註〕+ sop 四檔去誤導〔model_recommendations -001🔴/guide 勘誤/doc_type banner+v1v2 歸檔/mineru RELEASE_ON_UPLOAD〕；§7.2 DOC 豁免；PIPE-VISUAL 開 plan 前置完成）

### PIPE-SCAFFOLD (✅ 已完成·階段一建)
- ✅ ~~PIPE-SCAFFOLD web_server 雙軌派發 scaffolding~~（已落地、OP-1 `13c1dcb` + OP-2 `6807a7f` + OP-3 `58e1b89`；旗標惰性插入點 + 影子派發單元 + 兩派發點閘門，A 軌 byte 不動；階段二 Flip 屬 PIPE-FLIP）

### API-PERF (✅ 已完成·PIPE 基建前置)
- ✅ ~~API-PERF API 技術審計與效能防呆優化~~（已落地、C1 `5326437` + C2 `e20054d` + C3 `76e47ed` + C4 `aad3737` + C5 `59e1c56` + C6 收官；U1-U7 並發信號量/nice/LRU/流式上傳/真實 IP/連接池/計時埋點+CLI；PIPE 並發底座就緒）

### DOMAIN-NORM (✅ 已完成·PIPE 共用真理源)
- ✅ ~~DOMAIN-NORM 領域標準化對齊器~~（已落地、C1 `8d4f75f` + C2 `125af97` + C3 `7e7f2a1` + C4 `aeb4fc2` + C5 收官；Domains/DomainMapping 兩表 + DomainNormalizer 內容判定/動態註冊不塞單字/快取防重 + normalize_to_lcc 入口 + LLM_USE_GLOSSARY_ALIGN 旗標預設 False；GLOSSARY-CORE/Translator 共同上游真理源就緒）

### GLOSSARY-CORE (✅ 已完成·PIPE 共用真理源之二)
- ✅ ~~GLOSSARY-CORE 中央領域術語庫與跨語系一致性~~（已落地、C1 `03d85c8` + C2 `9af971f` + C3 `fd0e84f` + C4 `06bf3df` + C5 收官 + C6 `ae705d5` + C7 收官；GlobalGlossary 表聯合唯一約束 + GlossaryManager 級聯查詢/交易外提取/冪等回填 + translate/chat 旗標閘門注入 + manage_glossary CLI；消費 DomainNormalizer LCC；書籍融合待 TRANSLATE-BOOK）

### TRANSLATOR (✅ 已完成·PIPE 共用真理源之三)
- ✅ ~~TRANSLATOR 雙模式原子翻譯器~~（已落地、C1 `1558f79` + C2 `27db830` + C3 `11ea52a` + C4 `2ebda03` + C5 收官；processor/translator.py InjectionContext〔7 欄〕/TranslateMode/Translator〔Prompt Engine 五步 + 雙模式路由 + U4 兜底〕+ contracts GlossaryReadySpec 補 domain_name + client thinking_config 受控擴充〔§4 唯一例外、前向相容〕+ caption 提示詞 + 8 pytest；消費 DomainNormalizer/GlossaryManager；三大真理源全數就緒；plan v10 八輪 review 定稿）

### META-NORM (✅ 已完成·PIPE 共用真理源家族第 4 員)
- ✅ ~~META-NORM 封面元數據自癒飛輪與動態欄位登記~~（已落地、C1 `ae407ef` + C2 `6dd48f8` + C3 `6c37a1d` + C4 `dedd915` + C5 `d2a3db2` + C6 `6bb440e` + C7 收官；解 PIPE-SLIDES 實測 C+D；MetaField/MetaFieldAlias 兩表 + MetaNormalizer 飛輪〔reserved BS1/黑名單 Q9/label BS4/temp=0 Q2〕+ P1 開放抽取/封面放寬接線 + subtitle〔D〕+ 前端通用渲染〔排除集 BS2/排序 BS7〕；§7.2 key-changing 整合正面達標；旗標 LLM_USE_META_NORM 預設 False；⚠️ baron 漸進開+Vision golden 重捕+餵養 CHAT-STRUCT-1）

### IMG-FILTER (✅ 已完成·垃圾圖確定性過濾)
- ✅ ~~IMG-FILTER 垃圾圖三規則確定性過濾~~（已落地、C1 `de3a475` + C2 `f39f8cb` + C3 `8cfaf5b` + Checkout 收官；三規則〔①面積 100k ②長寬比 4.0 ③報頭判型行界〕任一命中 DROP、免 Vision 零 LLM、stdlib 尺寸解析零新依賴；門檻經 23 圖實測校正**廢 spec F7 長邊軸**〔防誤殺 481×369 內容 chart·規則③收窄防誤殺孤兒區 hero 圖〕；engine 純加法 `figure_filter`〔DROP caption `used` 標記防孤兒圖說〕；fail-open+逐張 log 審計+`IMG_FILTER_ENABLED` env 單點關回；§7.2 實體圖檔整合測試；805→831 passed；⚠️ baron 影子 E2E：SpaceX 3 垃圾消失/20 內容全在〔特驗 481 chart+hero〕/log 三筆審計+第二樣本泛化）

### GLOSSARY-TERMMAP (✅ 已完成·事前定案術語表)
- ✅ ~~GLOSSARY-TERMMAP 事前定案術語表與glossary旗標開啟~~（已落地、C1 `16a5f09` + C2 `30684e5` + C3 `83f0503` + C4 `c571c5b` + C5 `6b5c975` + Checkout 收官；`GlossaryManager.build_termmap` 五路共用 builder〔N1 段落切塊→N2 並行 census 只認詞→N3 去重/分流**廢飛輪早退**→N4 只翻未知→N5 定案 upsert 永不吃收割〕、三路 `_heal_glossary` 收斂單一實作源、translator 免括號句〔缺陷④〕、litedoc 摘要型滑窗〔section_engine 純加法 slot_context_fn·前鄰摘要 model_copy 注入·容缺〕、旗標 `LLM_USE_GLOSSARY_ALIGN` 預設 true 末位點火〔env 單點關回〕；§7.2 key-changing 整合測試〔多單元注入完全一致〕；780→805 passed；⚠️ baron 影子 E2E：清 GlobalGlossary 歸零→SpaceX 樣本硬驗收〔全文單一譯法/同字括號 ≤1〕+跨文件累積+slides census 觀察項〔tasks §4.5〕）

### LANG-DETECT (✅ 已完成·cover-prompt 語言欄與 source_lang 正名)
- ✅ ~~LANG-DETECT cover-prompt語言欄與source_lang正名~~（已落地、C1 `c17e183` + Checkout 收官；cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` +`language` ISO 639-1 欄〔搭既有 metadata LLM 便車·零多呼叫〕+ `_resolve_source_lang` catch-all 限定合成〔啟發式非 en〔zh/hans/ja/ko〕維持原判·en 時雙重白名單 `^[a-z]{2,3}$` **拒 zh 前綴**〔HOTFIX-1 鎖一 producer 端強制·與 P3 gate 謂詞同源〕·缺欄退啟發式 100% 等價〕+ P1 單點接點〔正名值單點流入 spec·消費端零改〕；根治拉丁語系判 en 致 GlobalGlossary 桶污染〔schema 已多語·破在偵測層〕·`classify_source_lang`/`GlobalGlossary` git diff 零·45 測試含 §7.2 整合〔en→it 貫穿 P2 build_termmap 捕參+en 對照組不互污〕·875→920 passed；⚠️ Check 首輪 CHECKOUT-GUARD 當場攔下 C1 未 commit、baron 補 commit 後重收官；⚠️ baron 影子 E2E：義文樣本 log `source_lang=it`+SQL 驗 it 桶隔離/英文繁中簡體回歸）

### FITZ-HOTFIX-4 (✅ 已完成·裸 HTML 中和與報頭集行號基準修正)
- ✅ ~~FITZ-HOTFIX-4 裸HTML中和與報頭集行號基準修正~~（已落地、HOTFIX-4 `5756219` + Checkout 收官；治 FITZ-ANCHOR 落地後兩樣本 E2E——**K1** `_neutralize_inline_html` 裸 HTML 標籤反引號中和〔`<` 緊跟字母才成標籤·`a<b` 不中·反引號守衛防重包·行數不變·P1 ②' 清洗步、DocAnalyzer 前·無旗標〕治 Medium 裸 `<script>` → marked 解析真 script → DOMPurify 連內文移除 95% 蒸發 / **K2** R8 報頭集原封行序基準〔K3 刪行前預算 `_pristine_header_srcs` 傳 `_filter_source_figures`〔`header_srcs=None` 兜底〕〕治界外圖上移入窗被③誤殺〔行號位移家族第五例·whole mode 共用通道一刀殺雙語〕、重立雙語圖片對稱；`image_filter`/`fitz_processor`/`md_cleaner`/`section_engine`/`ingestion_engine`/`rag_indexer`/前端/A 軌零改·11 新測試〔K1 中和防吞+行數不變+Browsers 段落·K2 位移舊誤 DROP vs 新 KEEP+雙語對稱 E2E〕·1010→1021 passed·2 `.bak`；⚠️ baron 影子 E2E：Browsers 全文~35k 字/22 標題+`<script>` code 樣式可見、NHK zh/en 首圖雙側回歸、SpaceX 不退化）

### FITZ-ANCHOR (✅ 已完成·LLM 錨定前移與 fitz 幾何整形)
- ✅ ~~FITZ-ANCHOR LLM錨定前移與fitz幾何整形~~（已落地、C1 `b48961a` + C2 `38cb68e` + Checkout 收官；三輪 fitz hotfix 打地鼠後 baron 拍板架構轉向——重要性判斷全交 LLM 錨定、fitz 回歸幾何抽文字清垃圾；**U1** `_read_anchor_text` 裸抽前 2 頁原始文字層送 cover-prompt〔零新增呼叫·裸文字天然含 chrome URL·空 fallback md 文首·單參〕/ **U2** `_reinject_title` promote-else-inject〔analyze 前·heading 已在不動/正文 promote/缺席 inject·空跳過〕整類標題誤殺終局保底 / **U3** HOTFIX-3 K2 sidecar 雙端同刀退場〔生產/消費端 `_URL_RE`+寫檔+`_load_source_hints`+hints 全清〕/ **U4** ε 容差同位去重〔`(text,round(size,1))` 群 `|dx|,|dy|≤3.0pt`·治描邊 ±0.84pt 亞像素〕/ **U5** 比例重複門檻 `max(2,ceil(len(pages)*0.5))`〔防少數頁重複內容誤殺〕/ **U6** echo `min/max>=0.5` 守衛〔防 4 字標題吃 88 字 lede〕；md_cleaner 浮水印本體/K3/image_filter/ingestion_engine/rag_indexer/A 軌零改·23 新測試〔§3.1 fixture+§7.2 實體 PDF 端到端〕·993→1010 passed·8 `.bak`；取代原擬 FITZ-HOTFIX-4、退場 HOTFIX-3 K2 sidecar；⚠️ baron 影子 E2E：NHK 標題經回注存活+publisher=NHK+lede 不被吃）

### FITZ-HOTFIX-3 (✅ 已完成·同位重繪去重與chrome線索回收與meta歸零)
- ✅ ~~FITZ-HOTFIX-3 同位重繪去重、chrome線索回收與full_text meta歸零~~（已落地、HOTFIX-3 `8733d98` + Checkout 收官；治日文 NHK 樣本 E2E——**K1** fitz `_collect_page` 逐頁同位去重〔`dedup_key`＝文字+座標+字級·過濾 text-stroke 重繪 ×4·防 md_cleaner 浮水印≥3 全殺誤殺真標題·不越權跨頁 R2〕/ **K2** chrome URL 回收 sidecar〔`{pdf_file.stem}_source_hints.json`·litedoc `_load_source_hints` 三級 stem 定位避 `_shadow` 陷阱·`hints` **截斷後拼接**防長文靜默失效〕補回 publisher / **K3** `_strip_meta_source_lines` full_text 行級 meta 歸零〔sidecar spans ∪ R6 值比對整行相等·**echo-strip/R8 前**保行號·圖片行歸 R8〕恢復雙語文字對稱；`md_cleaner`/`image_filter`/`ingestion_engine`/`rag_indexer` 零改·15 新測試·978→993 passed；⚠️ 既有 C2 時序測試 spy 對齊 hints 純加法簽名；⚠️ baron 影子 E2E：NHK 標題完整+publisher=NHK+浮水印不再命中標題、SpaceX `shadow_en` MARC/JUN 歸零 zh/en 雙零對稱）

### FITZ-HOTFIX-2 (✅ 已完成·報頭行界收窄與雙語圖片對稱)
- ✅ ~~FITZ-HOTFIX-2 報頭行界收窄與雙語圖片對稱~~（已落地、HOTFIX-2 `53feed8` + Checkout 收官；治 HOTFIX-1 後 E2E「B 軌大圖不見」——**K1** 報頭行界只計 meta 型塊〔`_HEADER_META_TYPES` 由 `_META_TYPES` 導出防漂移·v3 hdr_end 119→10·封面大圖與 Falcon 9 獲救·無 meta 塊回 ∅ 規則③自然停用〕/ **K2** `_load_header_srcs` 三級定位 sidecar〔PDF stem 主路/glob 備路/fail-open·**避影子軌 `_shadow` 後綴陷阱**〕+ 注入 `make_figure_filter` 使原文與 tiles 兩通道規則③同步、**恢復雙語圖片對稱不變式**；`image_filter` 三規則本體零改、單檔 litedoc；10 新測試、968→978 passed；⚠️ 既有 IMG-FILTER C3 行界測試依 K1 更新契約〔fixture 之 `other` 型塊正是元凶同類〕；⚠️ baron 影子 E2E：v3 樣本驗封面大圖與 Falcon 9 回歸、頭像/logo/分隔線仍濾、`final_en` 與 `final_zh` 圖片數相等）

### FITZ-HOTFIX-1 (✅ 已完成·fitz 路標題救回與雜訊通則)
- ✅ ~~FITZ-HOTFIX-1 fitz路標題救回與雜訊通則修復~~（已落地、C1 `e8d57a6` + C2 `a666a11` + C3 `e6f3e44` + Checkout 收官；八刀 R1-R8 治 baron 影子 E2E 四缺陷〔標題全滅/雜訊入正文/nav 洩漏/46k 塌 1 section〕+ 雙後綴 + whole/en 繞過 filter——**R2 複合 key 救標題**〔列印 PDF 通案：瀏覽器每頁印 `document.title` chrome 與真標題同文，純文字 key 使真標題必然撞自身頁首被誤殺〕/ R1 圖框內文字排除 / R3 三級 `###`〔**連帶修正 body 字級只由非 band 行決定**·既有回歸測試攔下〕/ R5 nav link-tiling〔x 區間聯集·≥3links 且 ≥60%〕/ R6 `meta_values` 純加法兜底〔整行相等非包含·判型成功與 soft-fail 兩路皆套用〕+ meta 抽取時序前移 / R7 數字短行清理〔markdown 語法守衛·行數不變式〕/ R4 譯題餵 `_title_bare`〔真因＝LLM 回**後綴變體**致 `endswith` 失配·**`web_server.py` git diff 零**〕/ R8 P3 單點過濾覆蓋三消費者 + **雙語圖片對稱不變式**；§7.2 整合測試 Checkout 補齊〔真實 born-digital PDF 八刀端到端〕；920→968 passed、47 新測試；⚠️ 兩處 plan↔代碼落差經 grep 更正留痕；⚠️ baron 影子 E2E：SpaceX 驗標題/三級結構/零雜訊/垃圾圖消失/恰一 `(測試)` + <15k 短文驗 whole 路過濾）

### PIPE-INGEST-FITZ (✅ 已完成·born-digital 文字層快速道)
- ✅ ~~PIPE-INGEST-FITZ born-digital文字層快速道與連字修復~~（已落地、C1 `3cc3850` + C2 `ff7bf3f` + C3 `801f969` + Checkout 收官；`FitzProcessor(PDFParser)` 第二 impl 本地直抽〔MinerU 同形 .md·字級分群字元權重判正文·座標閱讀序·跨頁頂底帶剝除·圖 PNG/JPEG `page_{page_idx}_{xref}` 防衝突·零 `fitz.metadata` AST 守門〕+ 雙閘連字修復〔數字縮寫/版本號排查+系統字典優先兜底集·行數不變式〕+ litedoc P1 中位數閘門〔≥150 走 fitz·fail-open 退 MinerU·`LITEDOC_FITZ_ENABLED` env 關回·flag off byte 等價〕；§7.2 實體 PDF 整合〔修復前行號 sidecar 證行界對齊〕；831→875 passed；⚠️ baron 影子 E2E：SpaceX 驗 fitz 路 log/23 頁全文/連字消失/publisher=a16z/IMG-FILTER 續效+掃描樣本退 MinerU+env 關回實測）

### PIPE-INGEST (✅ 已完成·litedoc 攝入自有化)
- ✅ ~~PIPE-INGEST litedoc攝入自有化與品質根治~~（已落地、C1 `e7b9e6c` + C2 `ca4e0e7` + C3 `ab65208` + Checkout 收官；B 軌自有攝入組裝引擎 `pipelines/ingestion_engine.py`〔零文體字面量·注入式·title 不丟·meta 判型逐塊獨立·figure 帶 content〕、litedoc P1 脫離 A 軌 md_processor/json_processor 借用鏈、P3 譯題單一源＝P1 title〔廢 slot 撈題·根治扉頁/分頁名/PDF /Title 三受害者〕、cover-prompt publisher OCR 自癒+Title Case、dead code 清理；§7.2 key-changing 整合測試；748→780 passed；術語④⑤/括號移交 GLOSSARY-TERMMAP 前後腳；⚠️ baron 影子 E2E 驗結構項〔標題/圖片 ≥19/無 meta 重複/venue=a16z〕）

### PIPE-LITEDOC (✅ 已完成·PIPE 縱向五路第 3 路)
- ✅ ~~PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁）~~（已落地、HOTFIX-1 `cbc512a`；**問題一**標題/Meta 重複→`section_engine.strip_title_echo` 雙剝〔① pre-strip full_text 原文層 exact·en 全模式+zh whole/is_zh / ② post-strip zh_text 補 section 模式·同 slot 譯文 exact〕→扉頁成唯一標題、RAG 不受影響〔rag_sections 早於兩剝定案〕;**問題二**日文/簡體未翻譯→P1 改用 `section_engine.classify_source_lang` 二元「是不是繁中」〔取 tiles 內文樣本跳封面·鎖三〕、非繁回 ja/ko/**hans**/en〔**簡體不給 zh* 字串**·鎖一、四處 startswith("zh") gate 零改不復活〕、偵測器放 section_engine 共用〔book 也用·鎖二〕、一次解 P3 is_zh + P2 section_summaries 雙 gate;只動 litedoc_pipeline+section_engine+測試、18 新測試、全套件 704 passed〔唯一 fail＝既有 LOG_FORMAT flake〕;扉頁保留〔OQ-b·理由 chrome 分層+academic-family 共用 paper-header-meta 結構，非 A 軌 golden 0%〕;⚠️ baron 影子 E2E〔日文/簡體轉繁、標題不重複、真繁中仍 bypass〕+ B 軌走改善豁免不需 A 軌 golden 重捕）
- ✅ ~~PIPE-LITEDOC LiteDocPipeline 策略管線~~（已落地、C1 `b1012bc` + C2 `18e47c1` + C3 `3570476` + C4 `f8940cd` + C5 `424ee93` + C6 `469f982` + C7 `ff16271` + C8 收官；第 3 路 news/web/unknown〔factory fallback〕;academic-lite——P1 MinerU 文字攝入〔非 Vision〕+ DocAnalyzer U2.1 映射 + B 軌原生 cover-prompt〔URL→publisher 解碼〕、P2-P4 **全消費共用真理源**〔section_engine + DomainNormalizer/Glossary/Translator + rag_indexer〕、size-gate〔<15k 一鍵/≥15k section〕+ HTML 扉頁〔render_meta_header_html·C1 純加法補〕+ U5c 雙語標題鏈 + 門檻 ≥10〔**rag_indexer 零改**〕;§7.2 key-changing 整合達標、litedoc 25 + 全套件 686 passed;**首個 section_engine 跨 consumer 驗證**;Q4 technical 排除〔母 plan v10 L72 分歧待 PIPE-SYNC 回灌〕;⚠️ baron 影子 E2E + golden 改善豁免）

### PIPE-SECTION-BASE (✅ 已完成·第 4 共用真理源·section 機制)
- ✅ ~~PIPE-SECTION-BASE 共用 section 機制抽取~~（已落地、C1 `e400789` + C2 `24db977` + C3 `4078a9e` + C4 `6bd8705` + C5 收官；resume 的「遞迴標題樹走訪→逐節點摘要/並行翻譯/排版還原/rag 旁路/meta header」抽成零 doc_type 耦合純函式 `pipelines/section_engine.py`〔§2.5 方案 A·llm/translator/prompt 注入·引擎零 doc_type 字面量·U3.1 meta header 純格式化器零讀 raw_metadata·U3.2 DFS 吃任意子樹〕、resume 改 delegate;行為等價〔RESUME-PERF-1 C1 範式·resume 42 passed〕+ tests/test_section_engine.py 17 測試〔含 base 層 key-changing 整合·堵 RAG-ASYNC-HOTFIX-1〕、全套件 657 passed;§7.2 不豁免達標;Q2 slide 重複不收編留後續;⚠️ 後續 litedoc plan 建於本引擎上）

### PIPE-SLIDES (✅ 已完成·PIPE 縱向五路第 2 路)
- ✅ ~~PIPE-SLIDES-HOTFIX-4 P1 空白頁 Vision 檢測（is_blank 旗標·跳過空白單位）~~（已落地；`_VISION_PROMPT` 基底加 `is_blank` 欄 + 第5條判定〔含封面〕+ `_process` ④ 雙保險跳過〔is_blank 且 title/content 皆空才跳、防誤殺有內容頁、純圖頁 is_blank=false 不跳、舊 golden 無欄向後相容〕;既有三欄全空保留為第二道、與 is_cover 對稱;真因＝Ch37 第16張空白頁 Vision 回非空 figure_description 漏舊判定;RAG/渲染/四路零碰;4 新 pytest、全套件 631 passed;⚠️ 改 Vision prompt → slides golden 併批次重捕、baron E2E 驗第16張不產頁+純圖頁未誤跳）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-3d 字面 `**` 未渲染粗體 + 裸 URL 破版（slide 渲染層清洗）~~（已落地；`pipelines/slide_pipeline.py` 新增 `_render_inline_bold`〔`**X**`→`<strong>` 繞 CommonMark CJK emphasis〕+ `_strip_bare_url_lines`〔剝整行裸 URL、保圖片行/行內 URL〕殿前注入；真因＝B 軌 vs 原稿比對 p27 字面 `**`〔CJK 緊貼〕+ p6/18/27/35 裸 URL 撐版；RAG 零影響〔merged 取原始 zh_content〕；零後端/四路；9 新 pytest + 真 marked 4/4、全套件 627 passed；⚠️ slides golden 併批次、baron E2E p27）
- ✅ ~~PIPE-SLIDES-HOTFIX-3c 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）~~（已落地；`pipelines/slide_pipeline.py` 新增 `_tighten_point_groups`〔連續行首箭頭合併硬換行〔保 `→`、不轉 bullet〕+ 相鄰清單 loose→tight〕殿後注入 `_page_source_md`/`_deliver`；真因＝Vision 每頁吐不同「標題+重點」結構〔頁 A `*` loose / 頁 B `→` 散段落〕節奏不一；RAG 零影響〔merged 取原始 zh_content、未套 tighten〕；零後端/DB/四路；9 新 pytest、全套件 618 passed；⚠️ slides golden 併批次首捕、baron E2E Ch37）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-3b top-level 清單凸排修補（HOTFIX-3 二補完）~~（已落地；`static/index.html` base CSS 單 hunk：HOTFIX-3「二」selector 前置 `#paper-content ul/ol`〔top-level〕、`padding-left:1.5em` 不變；真因＝L79 全域 reset 歸零 top-level ul/ol padding、`list-style:outside` 下第一層 bullet 凸排、HOTFIX-3 二只補巢狀；不動 themes〔四主題 grep 0 命中、結構歸主檔、含自訂主題受益〕；零 .py、全套件 605 passed〔僅 env flake〕；⚠️ baron E2E ALi 第一層不凸排+四主題一致+巢狀未退化）
- ✅ ~~PIPE-SLIDES-HOTFIX-3 簡報閱讀視圖排版打磨（圖序/副標併標題塊/子標題/縮排）~~（已落地；一-a 圖在上 + C 副標併 .slide-head 標題塊〔順帶解 一-b 夾線、用主題 divider 變數〕+ A/B/C 升 h3〔非孤兒 h4〕+ 二 base 巢狀縮排；design/docs 設計對齊、RAG 零改；40 測試、全套件 605 passed；⚠️ slides golden 待 fixture 補齊後首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-2 alt 破圖/母片重複日期/F4 條列鬆散（B+E+F）~~（已落地；B _safe_alt 括號全形根除破圖+圖說洩漏 / E _strip_master_date 母片日期 ≥2 頁洗〔補 dedup 格式變異漏網〕/ F _normalize_paragraph_breaks list-aware〔修 HOTFIX-1 F4 條列鬆散回歸〕；A 撤案、C/D 留 META-NORM；3 測試、全套件 588 passed；⚠️ slides golden 落地後一次首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES-HOTFIX-1b F2 譯題旁路格式修補~~（已落地；裸 str→三欄 dict 對齊 upsert_paper/web_server 契約、影子寫庫復活；同式消費測試堵盲區；全套件 585 passed）
- ✅ ~~PIPE-SLIDES-HOTFIX-1 B 軌簡報三缺陷緊急修補~~（已落地；F1 去標題回聲〔原文層〕+ F2 接譯題〔複用 P3 譯題穿旁路〕+ F4 段落正規化移植 + F3 並列顯式不修；4 回歸測試、全套件 584 passed；⚠️ slides golden 落地後一次首捕）〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕
- ✅ ~~PIPE-SLIDES SlidePipeline簡報策略管線~~（已落地、C1 `31dab5a` + C2 `941eed7` + C3 `f8a24d7` + C4 `4d7684c` + C5 `dbf90bd` + C6 `cb5e2bd` + C7 Checkout 收官；原 PIPE-VISUAL 改名；四 Phase 全落地〔P1 存圖+Vision temp=0+封面+去重 / P2 六步 key=`p{N}_{原文頁標題}` / P3 逐頁並行+alt 對齊雙 Caption 根除 / P4 rag_indexer 四產物〕+ §7.2 key-changing 整合測試正面達標；24 測試、全套件 580 passed；⚠️ baron 影子 E2E + B 軌 golden 另捕〔Q8 改善豁免〕）

### PIPE-RESUME (✅ 已完成·PIPE 縱向五路絞殺第 1 路)
- ✅ ~~PIPE-RESUME ResumePipeline策略管線~~（已落地、C1 `f3d4e41` + C2 `d7edcd9` + C3 `48aa5df` + C4 `8971a19` + C5 `e8a7429` + C6 `fabb114` + C7 收官；`pipelines/resume_pipeline.py` 四 Phase 策略〔P1 Vision 全鏈/P2 LCC+摘要+Glossary 自癒/P3 100% Bypass/P4 RAG ≥3〕+ tests/test_resume_pipeline.py 15 測試；消費 PIPE-CORE ABC/三大真理源/PIPE-SCAFFOLD 影子；baron 拍板擴 PipelineContext pdf_path/owner_id；custom_metadata 硬前置 defer 僅影子 B 軌、不 Flip）
- ✅ ~~PIPE-RESUME v9 影子整合與規格同步~~（已落地、C1 `b97958b` + C2 `e64417a` + C3 `f239721` + C4 `9bbad2d` + C5 `9291c5c` + C6 `4e15905` + C7 收官；raw_metadata 旁路穿線 + P1 影子標題後綴 (測試) + P2 摘要先行步序 + P3 翻譯策略隔離 constraints + C5 影子寫庫保真〔對齊 A 軌 upsert_paper〕+ 廢 self._raw_meta；resume 19 測試、全套件 483 passed；A 軌 byte 不動）
- ✅ ~~TILING-HOTFIX-1 — 緊急熱修復：TextTiling Embedding 速率超限 (429) 批次化修復~~（已落地、`702347a`；`tiling_processor.py:425` 逐筆 embed_query→批次 embed_documents〔1/32 請求+線性退避+順序保證〕；根治 429 阻斷+test_tiling_paragraph 併發 flaky；全套件 484 passed；⚠️ task_type RETRIEVAL_QUERY→DOCUMENT 行為變更、Flip/結案前須重捕 Golden Baseline）
- ✅ ~~SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復~~（已落地、`3d2778a`；3 處移除矛盾交回母提示詞：web_server translated_title 補 (測試) + translator.py:40 STYLE_HINTS 移除公司名 + resume_pipeline.py:109 constraints 改產品-only；全套件 486 passed；⚠️ B軌譯文改變、與 TILING-HOTFIX-1 合併重捕 Golden Baseline；學歷 doubling 殘留歸 RESUME-P3）
- ✅ ~~RESUME-P3 B軌履歷翻譯品質重構~~（已落地、C1 `aec1f6f` + C2 `0efa7e8` + C3 `52e0769` + C4 `6658b48` + C5 `3a30394` + C6 收官；廢 100% Bypass→逐 heading section 翻譯+還原〔pipelines 內重建不耦合 A 軌〕+ 履歷 P1 opt-out TextTiling〔滅 429〕+ resume 停用 U4 + heading 退化 fallback；resume 26 測試、全套件 495 passed；⚠️ 改 B軌輸出、與 TILING/SHADOW 合併重捕 Golden；通用化 chunking 歸 INFRA-3）
- ✅ ~~RESUME-P3 HEADING-HOTFIX-1 標題層級遞迴深度~~ `7c8a0da` / ~~PARA-HOTFIX-1 正文段落空行~~ `2772822` / ~~META-HOTFIX-1 P1 meta 進 final header~~ `2ba97fc`（B軌履歷三件套：標題層級/段落/文件 header）
- ✅ ~~VISION-HOTFIX-1 Vision 轉錄 temperature 確定化~~（已落地 `3d5be32`、`chat_with_images` 加 temperature + ResumeProcessor 傳 0；A軌 pdf2md + B軌 P1 共用、須重捕 resume golden）
- ✅ ~~RESUME-PERF-1 run_phase3 逐 section 翻譯並行化~~（已落地、C1 `b110742` + C2 `d5abdf0` + C3/C4 收官；序列→ThreadPool 受限並行〔保序靠 slot index、限流靠既有 `_api_semaphore`、單 unit 失敗退原文〕；C1 解耦先鎖等價、C2 並行、C3 4 並行測試；行為等價、預估 ~5x；baron 拍板不必等五路）

### RAG-ASYNC (✅ 已完成·PIPE Phase 4 共用真理源)
- ✅ ~~RAG-ASYNC-HOTFIX-3 zh 來源履歷 P3 改建 per-section rag_sections（#4·選 B）~~（已落地、`6794331`；run_phase3 is_zh 分支單一容器→有 section 走 ctx.ingestion.tiles 不翻譯、複用 `_collect_render_slots`+`_collect_rag_sections(translate=False)` 建 per-section〔summary_key=原文 zh path、與 P2/#1 天然對齊〕、無 section 退兜底；不改 zh_text=full_text/en 主路/degraded；resume 42 passed、全套件 535 passed；⚠️ zh 來源 golden 須重捕、en 不需）
- ✅ ~~RAG-ASYNC-HOTFIX-1 section_summaries 跨譯 key 對位失效 + dead code~~（已落地、`300feb1`；#1 P2 原文 key vs P3 譯文 title vs P4 譯後 node_key 三方不一致 → Chapter Summary 永不進 chunk、Strategy B 靜默退化成 A；穿原文標題 path key 貫穿 P2/P3/P4 + 移除 dead `_load_index_meta`〔#3〕+ 補 P3→P4 接縫整合測試；全套件 528 passed）
- ✅ ~~RAG-ASYNC-HOTFIX-2 B 軌補產 rag_tree.json（#2·選 B 完整版）~~（已落地、`300feb1`；rag_indexer 新增 `build_rag_tree`+`_walk_tree`〔key_map key=chunk Header=node_key→`/sections/{i}/content/0` + 巢狀 translated_content〕+ `index()` 寫 `final_{paper}_rag_tree.json` + run_phase4 傳路徑/標題；根治 C4 漏產 rag_tree → 章節引用/paper_title/公式相鄰降級；零改 rag_retriever/ai_core；全套件 532 passed；不衝擊 golden）
- ✅ ~~RAG-ASYNC P4 RAG 索引共用真理源與全 P2 摘要~~（已落地、C1 `195e12b` + C2 `8c76274` + C3 `53755c4` + C4 `a09128e` + C5 `d9b03f4` + C6 `13abdfa` + C7 收官；新建 `processor/rag_indexer.py` B 軌自有索引引擎〔全重寫零 import rag_processor、Strategy B header augment + size-cap 二段子切 + 自實作 is_chunk_meaningful、index() 落庫 byte 相容 ④ 合約〕+ GlossaryReadySpec section_summaries 取代 chapter_summaries + run_phase2 統一六步〔批次產+翻 section_summaries、三安全鎖〕+ run_phase3 旁路封存 ctx.rag_sections + run_phase4 改呼 rag_indexer〔砍 rag_processor 耦合〕+ 母 plan v10/PIPE-SPEC 同步〔含修 §1.3 P3 doc-drift〕；全套件 525 passed；**chunks=1 退化修復、B 軌全鏈零 A 軌依賴**；⚠️ baron 須影子 E2E 驗 chunks 量級 + resume 重捕 Golden；其餘四路 production 隨各自 PIPE-N 跟上）

---

## 🗑️ 2026-06 worktree 刪除遺失清單（RESCUE-1 C4 審計）

> 舊 worktree `hopeful-yalow-902c50` 刪除，致 git-ignored `baton/` 內未收官文件遺失。經 RESCUE-1 權威帳本盤點（tracked 文件曾引用之全部 `baton/<檔名>` 逐一比對磁碟），真遺失文件與處置如下（存活救回者見 RESCUE-1 ✅ 表）：

| 遺失文件 | 性質 | 處置 |
|---|---|---|
| `CHAT-STRUCT-1` plan_v1 | 履歷聯絡欄位確定性回答（#5·選 C） | **重建**（B 類·規格骨架存 active 條目 + RAG-ASYNC #5 溯源、獨立後開） |
| `TRANSLATE-BOOK` plan_v5 + v7 | BookPipeline（第 5 路）並行翻譯與雙語故事板 | **重建**（B 類·第 5 路唯一技術依據、獨立後開） |
| `INFRA-2` plan | PipelineCore 第一階段切分與定規（三文件） | **取代結案**——產出物已由 PIPE-SPEC + PIPE-CORE 涵蓋 |
| `INFRA-3` plan_v1 | chunking 各路 opt-in 通用化 | **backlog**（遠期·五路收完 + A 軌死後、待重建） |
| `QUEUE-1 v1` plan（2026-05-23） | 文件佇列 Thread-level `sleep(2)` 避讓 | **廢除**——PIPE-SPEC §3.1 判「重構性廢除」（Early-Emit + RAG 異步 + API-PERF Semaphore 覆蓋其職能） |
| `YuLun_Wu_CV_chat.md` | baron 診斷匯出 | **放棄**（診斷用、無重建價值） |
| `工作筆記` | 隨手工作日誌 | **放棄**（無實效） |

> **存活救回（非遺失）**：`QUEUE-1 v2`（MinerU 雙實例 CFS·RESCUE-1 C1 救回 + archive `.bak`）／`PIPE-SPEC v8`（RESCUE-1 C2 依 v7 `.bak` + PIPE-SYNC-4 C2 執行報告重建 + archive `.bak`）／`MODEL-10` plan（已收官殘留·RESCUE-1 C3 `mv`→archive）。
> **`INFRA-4`（非遺失·從未撰寫）**：合約轉正旁路收合（`raw_metadata` 旁路 → `spec.meta` 凍結合約），全庫僅**概念引用**（見上方 RESUME-P3 META-HOTFIX-1「轉正屬 INFRA-4 遠期」／ PIPE-SYNC-4 C2「為 INFRA-4 鋪規格」），**權威帳本零 `baton/…INFRA-4…` 檔案路徑** → 屬**尚未撰寫之未來任務**、非遺失。

