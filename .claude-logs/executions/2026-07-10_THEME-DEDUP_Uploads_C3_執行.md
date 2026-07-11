# THEME-DEDUP C3 — Uploads Normalize 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | THEME-DEDUP C3 |
| **執行日期** | 2026-07-10 |
| **依據規劃** | `.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md §8 C3` |
| **次級參考** | plan v7（§3.0 上傳稽核／§2.2-F chrome 槽）/ theme-guide 凍結規格（C2 立） |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`0fd4ca6`（C2·已 ship·本輪 hash 自癒回填 TODO）；比對基線＝C0 `2380420`。
- **執行期發現與簡化**：5 支上傳**檔內段序已天然符合 9 段骨架**（拷貝自同代模板）→ **免全檔重排**、改手術式操作（清死碼/補 token/剝結構/補償/插槽）——churn 最小化。
- **⚠️ 執行期 scope 精修（視覺等價鐵律優先·依 framework §7 優先級 #1「不可動清單絕對遵守」自裁、無需中斷）**：預審發現上傳帶**內建沒有的白名單外結構**且 base 無法重現其樣式——剝除即視覺回歸。處置＝**保留 + 登記**（theme-guide §11.3·C4 腳本例外依據）：① 全 5 支 pre-FE-RHYTHM 節奏 margin（h1/h2/h3/p·同值）② fuller dashed 底線 ×2（base 為 solid）+ `font-feature-settings`（候選白名單）③ apple/google `.ph border-radius`。**structure=0 於上傳＝「可剝盡剝 + 遺留顯式登記」**、非絕對零。
- **完成狀態**：§6.4 全綠（獨立 delta 對帳）；**尚未 commit**（baron 手動、見 §8）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | Uploads Normalize — 5 支清 `#demo-bar` 死碼 + 26 token 補齊〔值==baseline〕+ 剝可剝結構 + 補償色 + 兩槽〔apple/google chrome 段原樣入槽〕+ 遺留登記 theme-guide §11 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·7）**：`static/themes/{apple,corbusier,fuller,google,gropius}.css` + `design/docs/{theme-guide,css-architecture}.md`
- **備份（入 git·7）**：`.claude-logs/archive/2026-07-10_THEME-DEDUP_C3_{5 主題,theme-guide.md,css-architecture.md}.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan、tasks、C1/C2 報告。
- **未動**：內建 4 支／`static/css/*`／`static/index.html`／JS／後端——**全零 diff**（git 驗證）。

---

## §4 修改說明

### (a) 死碼清理（C2 同法·審計腳本+斷言）
`#demo-bar` 系規則塊 + 前置註解整段移除：apple×6 塊（26 宣告）/google×6（25）/corbusier×4（22）/fuller×4（22）/gropius×4（22）；全 5 支 `#demo-bar` 殘留=0。

### (b) Token 補齊（8 個/支 → 各 26·值依 C0 baseline grep 核定·視覺等價）
| Token | apple/google | corbusier | fuller | gropius |
|---|---|---|---|---|
| `--content-max-w` | **760px**（＝原 `max-width` 同值·剝該行） | 760px | 760px | 760px |
| `--pc-pad` | 6/8（=default） | 6/8 | 6/8 | 6/8 |
| `--figure-margin-y` | 6 | 6 | 6 | 6 |
| `--byline-margin-b` | **5** | 6 | 6 | 6 |
| `--byline-pad-b` | **0** | **3** | 3 | 3 |
| `--byline-border-w` | **0**（無底線） | **var(--divider-w)** | 1px（規格齊備·自帶 dashed 保留） | 1px |
| `--figcaption-margin-t` | 3 | 3 | 3 | 3 |
| `--ph-border-w` | 1px | var(--divider-w) | var(--divider-w) | var(--divider-w) |

### (c) 結構剝除與補償
- **剝**（base+token 可重現者）：pc padding+max-width／h2 border-bottom+padding-bottom／byline 三行／figure margin／ph border／figcaption margin-top——apple/google/corbusier/gropius 各 10 條；**fuller 8 條**（h2/byline 之 dashed border-bottom 保留·base solid 不可重現）。
- **白名單色補償**：apple/google `.ph { border-color: var(--color-border) }`（淡框·非 base default divider）；corbusier `.byline { border-color: var(--color-divider) }`。
- **保留+登記**（§1 精修·theme-guide §11.3 表）：節奏 margin ×5 支／fuller dashed×2+tnum／apple/google ph border-radius／figcaption 寬度約束（Q3 既例）。

### (d) 兩槽
- 裝飾層：5 支皆補 `#paper-content .figure .ph::before { }` 空規則（figcaption 後）。
- chrome 槽：**apple/google 既有 chrome 覆寫段（figcaption 後至檔尾）前插 marker、塊內容逐宣告零改寫**（delta 對帳證）；corbusier/fuller/gropius 檔尾補空 marker。

### (e) docs
- `theme-guide.md`：新增 **§11 自訂/上傳主題**（§11.1 unlayered 三保證／§11.2 chrome 槽規範〔建議 var 不強制〕／**§11.3 遺留登記表**〔契約腳本例外依據〕／§11.4 新上傳建議）+ 進度 C3 ✅。
- `css-architecture.md` §6.4：更新為 C2/C3 已落地現況 + 指向 §11.3 唯一登記表。

---

## §5 測試與驗收結果（§6.4·獨立 delta 對帳輸出）

```
apple      剝==✅ 加==✅ 其餘零改寫=✅ token=26/26 ::before=✅ marker=✅ 死碼=0 ✅ brace=✅ (demo-bar 宣告清除 26)
google     剝==✅ 加==✅ 其餘零改寫=✅ token=26/26 ::before=✅ marker=✅ 死碼=0 ✅ brace=✅ (25)
corbusier  剝==✅ 加==✅ 其餘零改寫=✅ token=26/26 ::before=✅ marker=✅ 死碼=0 ✅ brace=✅ (22)
fuller     剝==✅ 加==✅ 其餘零改寫=✅ token=26/26 ::before=✅ marker=✅ 死碼=0 ✅ brace=✅ (22)
gropius    剝==✅ 加==✅ 其餘零改寫=✅ token=26/26 ::before=✅ marker=✅ 死碼=0 ✅ brace=✅ (22)
→ 剝==計畫（fuller 少 2＝dashed 保留）／加==8 token+補償／其餘宣告值 multiset 全等
  （**含 apple/google chrome 塊逐宣告零改寫**＝「嚴禁改一字」機器證）
8 token × 5 支覆寫值 == C0 baseline 原結構值 ✅（視覺等價）
範圍：僅 5 上傳+2 docs；內建 4 支/static/css/index.html 全零 diff ✅
```

**SOP §4 自評**：
- [x] §3 渲染正確性：獨立 delta 對帳 + token 值==baseline 雙證；遺留（節奏 margin/dashed）原樣保留＝視覺零變。
- [x] chrome 鐵律：apple/google 覆寫段逐宣告零改寫（multiset 證）、僅前插 marker。
- ⚠️ 瀏覽器 E2E：**留 baron 核查**——重點 apple/google（chrome 覆寫選單/對話框/訊息泡完好）+ fuller（h2/byline 虛線仍在）+ 任一支內文間距。

---

## §6 不可動清單遵守

- [x] 內建 4 支／`static/css/*`／`static/index.html`／JS／後端——零 diff。
- [x] apple/google chrome 覆寫內容——**零改寫**（機器證）、僅整塊歸槽。
- [x] 視覺值零改動——可剝者 token 值==baseline；不可重現者保留+登記（§11.3）。
- [x] themes 無 `@layer`；baton 過程檔未 git add。

---

## §7 銜接

- **baton 狀態**：plan / tasks / C1 / C2 / 本 C3 報告 暫存。
- **git 追蹤**：本 commit ＝ 5 主題 + 2 docs + 7 `.bak`（14 檔）。
- **hash 自癒（本輪）**：C2 `0fd4ca6` 回填 TODO。
- **下一步 → C4 — Template & Guard（統一模板與常駐契約腳本）**：`design/docs/theme-template.css` + `tools/check_css_governance.py`（純標準庫·四類檢查·**例外表＝theme-guide §11.3**）+ 首綠輸出入報告 + theme-guide Step-by-step 指模板。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅授權 7 檔。(b) 推進 plan §2.1-2（上傳半場·9 支全 conformant〔遺留顯式登記〕）；scope 精修有 framework 優先級依據 + 機器證、非擅自。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-10_THEME-DEDUP_C3_*.bak ×7

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔）
git add static/themes/apple.css static/themes/corbusier.css static/themes/fuller.css static/themes/google.css static/themes/gropius.css
git add design/docs/theme-guide.md design/docs/css-architecture.md
git add .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_apple.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_corbusier.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_fuller.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_google.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_gropius.css.bak
git add .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_theme-guide.md.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C3_css-architecture.md.bak

# 2.5 staged 自檢（期望恰 14 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/THEME-DEDUP_C3_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/THEME-DEDUP_C3_msg.txt
```
