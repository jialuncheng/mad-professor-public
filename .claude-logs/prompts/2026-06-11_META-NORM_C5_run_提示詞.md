# META-NORM C5 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 21:55 |
| 任務代號 | META-NORM C5 — Frontend Generic Renderer（前端通用渲染）|
| 觸發 Commit | C5 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 C4，下達 C5 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C5 / BE-Refactor；tasks §8 C5（plan U9/U9.1/U9.2/BS2/BS7）

### 執行命令（`# === [META-NORM C5 START/END] ===` 包裹）
① 改前備份 static/index.html + web_server.py（2 .bak）
② web_server.py：新增 GET `/api/meta-fields`（with SessionLocal/session.begin 查 MetaField、回 canonical_key→{label_zh,label_en,sort_weight} dict）
③ static/index.html：
   - CSS `.paper-dynamic-meta`/`.dynamic-meta-item`/`.meta-label`/`.meta-value`（flex 橫向）
   - `window.metaFields` 全域快取（預載 seed 離線兜底）+ 初始化 fetch `/api/meta-fields` 更新
   - `renderTitleHeader(p)`：遍歷 p.metadata 非排除集（title/authors/venue/doi/translated_abstract/user_tags/abstract/translated_title）→ 依 metaFields label 顯示 → sort_weight→label 字母序排序 → 渲染 `.paper-dynamic-meta` 追加標題下方
- 物理防線：僅兩檔；SOP §5.2 無裸 commit（/api/meta-fields 唯讀 session.begin）

### 驗收
- pytest 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0);FE 手動無 console error

### TODO 同步
- C5 ✅、C6 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C5_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：index.html + web_server + 2 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C5_msg.txt

### 停止
- 產出 C5_執行.md + TODO 更新後立即停止；不續 C6、不自發 commit/push
