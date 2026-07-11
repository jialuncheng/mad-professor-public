# THEME-DEDUP C1 — Token & Base Foundation 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | THEME-DEDUP C1 |
| **執行日期** | 2026-07-10 |
| **依據規劃** | `.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md §8 C1` |
| **次級參考** | plan v7（§2.2-A 7 token 凍結名單／§3.4 base 槽）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`6fea7dc`（FE-CSS-GOV checkout·**C5 `9df0028`/checkout `6fea7dc` 已 ship、本輪 hash 自癒回填完畢**）。
- **⚠️ C0 序位 deviation（重要）**：提示詞稱「baron 確認 C0 執行報告後」，但執行期查證 **C0 baseline 尚未 commit**（`git ls-files static/themes/`=4、5 支上傳仍 untracked、git log 無 C0）。依 tasks §8 C1 依賴註「C0（序位；**技術上獨立**）」——C1 僅動 globals/content/css-architecture、**零觸 themes** → 安全先行；序位鐵則管的是「正規化改寫」（C2/C3）。**C2/C3 前 C0 必須先 ship**（msg 已備 `/tmp/THEME-DEDUP_baseline_msg.txt`、TODO 已標 ⚠️）。
- **本次改動**：① globals T3 段 +7 異值結構 token（多數派 default）；② content.css base 承接（h2 填槽 + 4 處讀 token + 新增 .byline）；③ css-architecture §6.1 T3 +7 + §6.4 對照表。
- **零視覺變**：結構性證明（§5）——9 支主題全數自帶 base 承接之全部屬性、unlayered 全蓋。
- **完成狀態**：§6.2 全綠；**尚未 commit**（baron 手動、見 §8）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Token & Base Foundation — globals T3 +7 token〔--pc-pad/--figure-margin-y/--byline-margin-b/--byline-pad-b/--byline-border-w/--figcaption-margin-t/--ph-border-w〕+ content.css 承接〔h2 Group B 直移+4 處讀 token+新增 .byline〕+ css-architecture §6.4 對照表；零視覺變鋪底 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·3）**：`static/css/globals.css`（T3 +7）+ `static/css/content.css`（承接 ×6 處）+ `design/docs/css-architecture.md`（§6.1/§6.4）
- **備份（入 git·3）**：`.claude-logs/archive/2026-07-10_THEME-DEDUP_C1_{globals.css,content.css,css-architecture.md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan、tasks。
- **未動**：`static/themes/*`（**零 diff**·git 驗證）、`static/index.html`、其餘 css、JS、後端。

---

## §4 修改說明

### (a) globals.css — T3 段 +7 異值結構 token
插入位置＝`--content-max-w` 後（同屬 T3 主題覆寫面）；標註「異值結構 token（THEME-DEDUP·主題覆寫）」+ 逐 token 註記異值主題：
```css
--pc-pad: var(--space-6) var(--space-8);   /* kahn 覆 --space-8 單值 */
--figure-margin-y: var(--space-6);         /* mies 覆 --space-5 */
--byline-margin-b: var(--space-6);         /* mies 覆 --space-5 */
--byline-pad-b: var(--space-2);            /* kahn 覆 --space-3、mies 覆 0 */
--byline-border-w: 1px;                    /* mies 覆 0 */
--figcaption-margin-t: var(--space-3);     /* mies 覆 --space-2 */
--ph-border-w: 1px;                        /* kandinsky/nara 覆 2px */
```

### (b) content.css — base 承接（@layer components 內·6 處）
| 處 | 改法 |
|---|---|
| `#paper-content` | +`padding: var(--pc-pad)`（註更新） |
| `#paper-content h2`（原空槽） | 填 `border-bottom: var(--divider-w) solid var(--color-divider); padding-bottom: var(--space-2)`（Group B 同值直移） |
| `.byline`（**新增規則**·置 .figure 前） | `margin-bottom/padding-bottom/border-bottom: var(--byline-*) …solid var(--color-border-strong)`（底線色主題可以白名單 border-color 覆） |
| `.figure`（原註解槽） | 填 `margin: var(--figure-margin-y) 0` |
| `.figure .ph` | +`border: var(--ph-border-w) solid var(--color-divider)` |
| `figcaption`（原註解槽） | 填 `margin-top: var(--figcaption-margin-t)` |

### (c) css-architecture.md
- §6.1 T3 成員 +「異值結構 token ×7（見 §6.4）」。
- **新增 §6.4 主題結構→base/token 對照表**：7 token × default × base 規則 × 各主題覆寫值矩陣 + Group B 直移註 + 「C1 鋪底、C2/C3 卸結構後 token 生效」時序註。

---

## §5 測試與驗收結果（§6.2 + 零視覺變結構證明）

```
① 7 token 定義：grep 各恰 1（globals）                                    ✅
② h2 填槽：border-bottom+padding-bottom = 2                              ✅
③ .byline 新規則存在（content.css）                                       ✅
④ 主題零 diff：git diff --quiet static/themes/ 通過                       ✅
⑤ brace：globals 9/9、content 53→54/54（+1＝新 .byline 規則）             ✅
⑥ 範圍：僅 globals/content/css-architecture；index.html/themes/py 零觸    ✅
⑦ 零視覺變【結構性證明·非宣稱】：腳本逐支逐屬性驗——base 承接之 6 選擇器
   × 全部屬性（padding/border/margin 等），9 支主題**全數自帶同屬性規則**
   → unlayered 恆勝全蓋 base → 視覺 100% 零變                              ✅
   （含 mies .byline border-bottom:0 顯式蓋 base 1px、apple/google 自帶全套）
```

**SOP §4 自評**：
- [x] §2 效能：純加法 CSS + docs、零 JS/管線觸碰。
- [x] §3 渲染正確性：⑦ 結構性證明成立；base 值＝多數派原值（byte 同源 plan §3.2 實測表）。
- ⚠️ 全站 E2E（任一主題外觀零變）：**留 baron 瀏覽器抽驗**（⑦ 已結構性保證；建議抽 kahn+apple 各開一篇）。

---

## §6 不可動清單遵守

- [x] `static/themes/*` 零 diff（C1 鐵防線）；`static/index.html`/JS/後端零觸。
- [x] globals T1/T2 既有 token 未動（僅 T3 加法）；`@layer tokens` 包裹/brace 完好。
- [x] content.css `.slide-head` override（HOTFIX-3）未動；既有規則零改寫（僅填槽/加行）。
- [x] baton 過程檔未 git add。

---

## §7 銜接

- **baton 狀態**：plan / tasks / 本 C1 報告 暫存、未 mv 未 add。
- **git 追蹤**：本 commit ＝ 2 css + 1 docs + 3 `.bak`（6 檔）。
- **hash 自癒（本輪完成）**：FE-CSS-GOV C5 `9df0028` + checkout `6fea7dc` 回填 done_archive（全檔 0 佔位）+ TODO 索引行（`32e3a1a`…`6fea7dc`）。
- **⚠️ 下一步前置**：**baron 先 commit C0 baseline**（5 支上傳原樣；msg `/tmp/THEME-DEDUP_baseline_msg.txt`）→ 再下 C2 提示詞。**C2/C3（正規化改寫）嚴禁先於 C0**（序位鐵則）。
- **下一步 → C2 — Builtin Normalize（內建四支骨架重排與去結構）**：4 內建骨架重排 + 26 token 寫滿 + 卸結構 + 兩槽 + theme-guide 凍結規格重寫。

---

## §8 baron 執行命令

```bash
# 0.（前置·若尚未）commit C0 baseline：
git add static/themes/apple.css static/themes/corbusier.css static/themes/fuller.css static/themes/google.css static/themes/gropius.css
git diff --cached --name-only   # 恰 5 檔
git commit -F /tmp/THEME-DEDUP_baseline_msg.txt

# 1. 備份已完成（§3）：archive/2026-07-10_THEME-DEDUP_C1_*.bak ×3

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔）
git add static/css/globals.css static/css/content.css design/docs/css-architecture.md
git add .claude-logs/archive/2026-07-10_THEME-DEDUP_C1_globals.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C1_content.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C1_css-architecture.md.bak

# 2.5 staged 自檢（期望恰 6 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/THEME-DEDUP_C1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/THEME-DEDUP_C1_msg.txt
```
