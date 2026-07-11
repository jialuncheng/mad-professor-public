# THEME-DEDUP C2 — Builtin Normalize 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | THEME-DEDUP C2 |
| **執行日期** | 2026-07-10 |
| **依據規劃** | `.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md §8 C2` |
| **次級參考** | plan v7（§2.2 凍結規格／§3.2 異值表）/ `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`f64d15b`（C1·已 ship）；**C0 `2380420` 已 ship**（序位鐵則滿足、C1 報告之 deviation 已解）——本輪 hash 自癒回填 TODO。
- **本次改動**：4 內建主題**全檔重寫**至統一 9 段骨架（26 token 顯式寫滿 + 剝結構 + 色補償 + 兩槽）+ `theme-guide.md` 重寫升格**目錄級凍結規格權威源**。
- **視覺等價**：宣告級 delta 對帳 + 7 token 覆寫值==原結構值（§5·雙重機器驗證）。
- **完成狀態**：§6.3 全綠；**尚未 commit**（baron 手動、見 §8）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | Builtin Normalize — 4 內建統一骨架重排 + 26 token 顯式寫滿〔7 結構 token 各自原值〕+ 剝 9 結構屬性 + 白名單色補償 + 兩槽；theme-guide 重寫為目錄級凍結規格源 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git·5）**：`static/themes/{kahn,kandinsky,mies,nara}.css`（全檔重寫）+ `design/docs/theme-guide.md`（凍結規格重寫）
- **備份（入 git·5）**：`.claude-logs/archive/2026-07-10_THEME-DEDUP_C2_{kahn,kandinsky,mies,nara}.css.bak + theme-guide.md.bak`
- **baton 暫存（嚴禁 git add）**：本執行報告、plan、tasks、C1 報告。
- **未動**：上傳 5 支／`static/css/*`／`static/index.html`／JS／後端——**全零 diff**（git 驗證）。

---

## §4 修改說明

### (a) 4 內建全檔重寫（統一 9 段骨架）
每支：header 註解（原識別保留+C2 註）→ @import → `:root` 26 token → base 字體 → chrome 標題 → `#paper-content` 系 → figure → **裝飾幾何層槽**（kahn 原 `::before` 入槽、其餘 3 支 `{ }` 空規則）→ **進階 chrome 覆寫層 marker**（4 支皆空）。

**7 結構 token 覆寫值（各自原值·視覺等價）**：
| Token | kahn | kandinsky | mies | nara |
|---|---|---|---|---|
| `--pc-pad` | `var(--space-8)` | 6/8 | 6/8 | 6/8 |
| `--figure-margin-y` | 6 | 6 | **5** | 6 |
| `--byline-margin-b` | 6 | 6 | **5** | 6 |
| `--byline-pad-b` | **3** | 2 | **0** | 2 |
| `--byline-border-w` | 1px | 1px | **0** | 1px |
| `--figcaption-margin-t` | 3 | 3 | **2** | 3 |
| `--ph-border-w` | 1px | **2px** | 1px | **2px** |

**剝除結構屬性（每支 9 條）**：h2 `border-bottom`+`padding-bottom`／pc `padding`／byline `margin-bottom`+`padding-bottom`+`border-bottom`／figure `margin`／ph `border`／figcaption `margin-top`——全部由 C1 base 規則 + 上表 token 接手。

**白名單色補償（邊框色不 token 化·base default 之異色者）**：kandinsky `.byline { border-color: var(--color-divider) }`（Bauhaus 純黑、非 default border-strong）；kahn `.ph { border-color: var(--color-border-strong) }`（非 default divider）。

**Q3 例外保留**：kahn figcaption `max-width: 560px`+`margin-inline: auto`、kahn `.ph position: relative`、mies figcaption `max-width: none`。

### (b) theme-guide.md 重寫（目錄級凍結規格源）
§1 核心模型（結構歸 base/值經 token/外觀自由）／§2 26 必備 token（含 7 結構 token+邊框色 border-color 覆寫法）／§3 統一骨架 9 段+16 必備選擇器／§4 屬性白名單（**補登 text-align**+Q2 自由度+Q3 例外登記）／§5 兩可空槽（裝飾 `::before`+chrome marker·Q_chrome 建議 var 不強制）／§6 禁止清單（結構/死碼/@layer）／§7 unlayered 優先級／§8 Step-by-step+checklist（C4 後改指模板）／§9 陷阱／§10 上傳規格（含 served 唯一目錄+design/new stale 標示·Q_mock）。原 §8「THEME-DEDUP 方向」收斂為落地進度註。

---

## §5 測試與驗收結果（§6.3·機器驗證輸出）

```
【宣告級 delta 對帳·vs .bak】
kahn       刪==✅ 加==✅ 值零改寫=✅ token=26/26 槽×2=✅ @layer=0=✅ brace=✅
kandinsky  刪==✅ 加==✅ 值零改寫=✅ token=26/26 槽×2=✅ @layer=0=✅ brace=✅
mies       刪==✅ 加==✅ 值零改寫=✅ token=26/26 槽×2=✅ @layer=0=✅ brace=✅
nara       刪==✅ 加==✅ 值零改寫=✅ token=26/26 槽×2=✅ @layer=0=✅ brace=✅
→ 刪＝計畫 9 條精確吻合／加＝7 token+色補償精確吻合／其餘宣告值 multiset 全等（零改寫）

【7 token × 4 主題覆寫值 == 原結構值】 ✅（視覺等價）
【範圍】僅 4 themes + theme-guide；上傳 5 支/static/css/index.html 全零 diff ✅
【theme-guide 凍結規格命中】26 必備/統一骨架/chrome 覆寫層/text-align = 8 ✅
```

**SOP §4 自評**：
- [x] §3 渲染正確性：雙重機器驗證（delta 對帳 + token 值等價）→ 結構移轉後計算值逐款不變；色補償精確（kandinsky byline 純黑、kahn ph 深灰）。
- [x] 骨架安全：無重複選擇器（plan 已驗）+ chrome/裝飾內容整塊保留 → cascade 不翻轉。
- ⚠️ 瀏覽器 E2E（4 主題 × 閱讀視圖+slide：h2 底線/pc 內距/figure/byline〔mies 無底線〕/figcaption/kahn 天窗光線）：**留 baron 核查**。

---

## §6 不可動清單遵守

- [x] 上傳 5 支／`static/css/*`／`static/index.html`／JS／後端——零 diff。
- [x] Q3 裝飾排版例外（kahn figcaption max-width+margin-inline、.ph position、mies max-width:none）——保留原地。
- [x] themes 無 `@layer`（4 支驗=0）；視覺值零改動（delta 對帳＋token 值等價雙證）。
- [x] baton 過程檔未 git add。

---

## §7 銜接

- **baton 狀態**：plan / tasks / C1 / 本 C2 報告 暫存。
- **git 追蹤**：本 commit ＝ 4 themes + theme-guide + 5 `.bak`（10 檔）。
- **hash 自癒（本輪）**：C0 `2380420`／C1 `f64d15b` 回填 TODO。
- **下一步 → C3 — Uploads Normalize（上傳五支正規化）**：清 `#demo-bar` 死碼 + 補 `--content-max-w`+7 token（值依 C0 baseline 核定）+ 骨架重排 + **apple/google chrome 覆寫整塊原序入槽**；theme-guide 補上傳章 + css-architecture build 狀態。
- **§自評（WORKFLOW-4 U3）**：(a) 越界？否——僅授權 5 檔、上傳零觸。(b) 推進 plan §2.1-2（內建半場）+ §2.1-1/6（凍結規格落地 theme-guide）。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：archive/2026-07-10_THEME-DEDUP_C2_*.bak ×5

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔）
git add static/themes/kahn.css static/themes/kandinsky.css static/themes/mies.css static/themes/nara.css
git add design/docs/theme-guide.md
git add .claude-logs/archive/2026-07-10_THEME-DEDUP_C2_kahn.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C2_kandinsky.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C2_mies.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C2_nara.css.bak .claude-logs/archive/2026-07-10_THEME-DEDUP_C2_theme-guide.md.bak

# 2.5 staged 自檢（期望恰 10 檔）
git diff --cached --name-only

# 3. commit message 草稿（已寫入 /tmp/THEME-DEDUP_C2_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/THEME-DEDUP_C2_msg.txt
```
