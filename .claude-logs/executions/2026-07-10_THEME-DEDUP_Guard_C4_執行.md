# THEME-DEDUP C4 — Template & Guard 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | THEME-DEDUP C4 |
| **執行日期** | 2026-07-10 |
| **依據規劃** | `.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md §8 C4` |
| **次級參考** | plan v7（§2.1-7/8）/ theme-guide 凍結規格（§2/§3/§11.3） |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`bf4577c`（C3·已 ship·本輪 hash 自癒回填 TODO）。9 支主題全 conformant → 腳本首跑可全綠的前提成立（tasks §8 C4 依賴）。
- **本次交付**：① `design/docs/theme-template.css`（統一骨架模板）② `.claude-logs/tools/check_css_governance.py`（常駐契約腳本·純標準庫）③ theme-guide §8 改指模板+腳本用法 ④ css-architecture 工具登記。
- **首跑全綠 + 突變負測雙證**（§5）。
- **完成狀態**：§6.5 全綠；**尚未 commit**（baron 手動、見 §8）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | Template & Guard — theme-template.css〔9 段骨架+26 token 佔位+16 選擇器+兩槽+逐段註解〕+ check_css_governance.py〔四類檢查·exit 0/1·--file〕+ 首綠輸出 + docs 連動 | 待回填 |

---

## §3 變動檔案清單

- **新建（入 git·2）**：`design/docs/theme-template.css` / `.claude-logs/tools/check_css_governance.py`
- **修改（入 git·2）**：`design/docs/theme-guide.md`（§8 指模板+機器驗收步驟+進度 C4 ✅）/ `design/docs/css-architecture.md`（§99 工具登記）
- **備份（入 git·2）**：`.claude-logs/archive/2026-07-10_THEME-DEDUP_C4_{theme-guide.md,css-architecture.md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan、tasks、C1-C3 報告。
- **未動**：`static/**` 全部（themes/css/index.html）零 diff、後端零觸。（工作區另有 `executions/2026-07-09_FE-CSS-GOV_checkout_執行.md` 之 M＝baron 先前手動修改、非本 commit 範圍、不入 add 清單。）

---

## §4 修改說明

### (a) theme-template.css（統一骨架模板·落點鐵防線遵守）
- **落 `design/docs/`**（嚴禁 static/themes/——`/api/themes:1286` 掃該目錄任何非內建 .css 入下拉、模板會變假主題；模板頂部註解亦警示複製時機）。
- 內容＝標準 9 段骨架 + 26 token 佔位（色票 `#______`、逐 token 用途註）+ 16 必備選擇器（含 `.ph::before { }` 空槽）+ chrome 覆寫層空 marker + 逐段用途註解 + 驗收指令引導。**模板自身過腳本檢查**（`theme-template` 列例外表空集＝零例外全合規）。

### (b) check_css_governance.py（常駐契約腳本）
- **純標準庫**：`import re / sys / json / pathlib`——零第三方（grep 驗證）。
- **四類確定性檢查**：
  1. **unlayered 鐵律**：主檔系 6 檔（除 print）brace-walk 掃描——頂層規則非 `@layer/@media/@supports/@font-face` 即違規；print+themes+模板反向驗「無 @layer」。
  2. **token 唯一定義**：globals 內重複定義抓取 + 其餘主檔任何 `--x:` 定義＝散落違規（主題 :root 覆寫不在此限）。
  3. **凍結骨架**（9 主題+模板）：26 token **不多不少**（缺/多雙抓）+ 16 必備選擇器全在 + chrome marker 在 + 16 選擇器屬性 ⊆ 白名單∪例外表（**例外表＝theme-guide §4 Q3+§11.3 之機器鏡像·按主題名鍵控**）+ `::before` 槽加裝飾幾何集 + **非必備選擇器（chrome 覆寫）必在 marker 之後**（位置驗證）。
  4. **死碼**：`#demo-bar` 全量=0。
- **介面**：exit 0＝全綠一行摘要；exit 1＝違規逐條清單；`--file <path>` 單檔主題模式（新主題自驗）。

### (c) docs 連動
- theme-guide：§8 Step 1 改「`cp design/docs/theme-template.css …`」+ **步驟 8 機器驗收（必跑·含指令）** + 頂部進度 C4 ✅ + 機器可驗一行。
- css-architecture §99：登記腳本四類檢查/用法/模板落點警示——「任何 AI/人動 CSS 後必跑」。

---

## §5 測試與驗收結果（§6.5·首綠輸出 + 突變負測）

**① 首次全量檢查（EXIT CODE 0·終端原文）**：
```
$ python3 .claude-logs/tools/check_css_governance.py
✅ CSS 契約檢查全綠（全量（主檔系 7 + 主題 9 + 模板 1））：unlayered 鐵律 / token 唯一定義 / 凍結骨架（26 token·16 選擇器·2 槽·白名單+例外表）/ 死碼=0
EXIT CODE: 0
```

**② 突變負面測試（拷 mies 注入 4 種違規 → 應紅·驗腳本真的在驗）**：
```
$ python3 .claude-logs/tools/check_css_governance.py --file <scratchpad>/mutant.css
❌ CSS 契約檢查未過（單檔 …/mutant.css）——5 條違規：
  - mutant: 主題含 @layer（必 unlayered）
  - mutant: #demo-bar 死碼殘留
  - mutant: 缺必備 token ['--ph-border-w']
  - mutant: #paper-content h3 用非白名單屬性「padding」（未登記例外）
  - mutant: #paper-content .figure figcaption 用非白名單屬性「max-width」（未登記例外）
EXIT CODE: 1
```
（第 5 條＝mies 的 figcaption 例外**按主題名鍵控**、檔名非 mies 即不放行——例外表精確性之額外佐證。）

**③ 其他**：`ast.parse` 語法 ✅；import 僅 re/sys/json/pathlib ✅；docs 修改後**迴歸重跑仍全綠** ✅；`static/**` 零 diff ✅。

---

## §6 不可動清單遵守

- [x] `static/**`（themes/css/index.html）／後端——零觸（純新檔+docs）。
- [x] 模板隔離鐵防線——落 design/docs/、未入 static/themes/。
- [x] 腳本純標準庫——零第三方依賴。
- [x] baton 過程檔未 git add；baron 之 FE-CSS-GOV checkout 報告工作區修改未動、不入本 commit。

---

## §7 銜接

- **baton 狀態**：plan / tasks / C1–C3 / 本 C4 報告 暫存（checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ 2 新檔 + 2 docs + 2 `.bak`（6 檔）。
- **hash 自癒（本輪）**：C3 `bf4577c` 回填 TODO。
- **下一步 → checkout — 成果收官歸檔**：Conformance（plan §2 全目標 + §6 重跑〔含腳本全綠〕+ §7 不可動 + 提示詞稽核）→ baton 一次性歸檔（plan/tasks/C0 無報告？**C0 由 baron 直接 commit、無獨立執行報告**〔序位補救於 C1 報告記載〕→ 歸檔 C1–C4 報告 4 份 + plan + tasks）→ TODO 雙層結案 + hash 自癒 + staged 白名單自檢 + checkout 執行報告。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅授權 4+2 檔。(b) 推進 plan §2.1-7/8（防未來不一致之治本雙件套）；突變負測＝腳本可信度非形式交付。

---

## §8 baron 執行命令

```bash
# 1. 備份與新建已完成（§3）

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔）
git add design/docs/theme-template.css
git add .claude-logs/tools/check_css_governance.py
git add design/docs/theme-guide.md design/docs/css-architecture.md
git add .claude-logs/archive/2026-07-10_THEME-DEDUP_C4_theme-guide.md.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C4_css-architecture.md.bak

# 2.5 staged 自檢（期望恰 6 檔；executions/…FE-CSS-GOV_checkout 之 M 屬 baron 自有變更、勿混入）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/THEME-DEDUP_C4_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/THEME-DEDUP_C4_msg.txt
```
