# DOC-SYNC-1 C1 — Docs Truth Sync 執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOC-SYNC-1 C1 |
| **執行日期** | 2026-07-09 |
| **依據規劃** | `.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md §8 C1` |
| **次級參考** | plan v3（U1 勘誤版）/ 對照基準 `static/index.html@8e5d1fa`（唯讀、零 byte 變更） |
| **落地 Hash** | （留空、baron commit 後回填） |
| **狀態** | ✅ 已完成（待 baron commit） |

---

## §1 基準與完成狀態

- **基準 Commit**：`bc2bcc4`（FE-PERF-2 checkout，git log HEAD）。
- **本次改動**：design/docs 5 檔——components 兩款標註、dom-reference 補漏+標註+戳、token 三檔零差戳；**diff +64/-11、增量遠低於 160 上限**。
- **完成狀態**：§6.1 全綠（U1 逐行 0／U2 75/75／戳×5）；**尚未 commit**（baron 手動、見 §8）。
- **與全局策略對齊**：落地 plan v3 U1（兩款標註+dropdown-popup 零碰）/U2（覆蓋率 100%）/U3（同步戳）/Q3（token 戳）；U4 範圍驗證於 §5。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Docs Truth Sync — components 標註（title-meta×2 未實作+msg 家族半實作、dropdown-popup 零碰）+ dom-reference 補 30 真缺 ID（§6.4 Modal 七家族/§4.4 abstract-toolbar/§1 app/§2.2 edit-tags-btn/§9 theme-link）+ 同步戳×2 + token 零差戳×3 | 待回填 |

---

## §3 變動檔案清單

- **修改（入 git、5 檔）**：`design/docs/components.md`（+標註×3 處+頂部戳）/ `design/docs/dom-reference.md`（+47 行：30 條 ID+標註×3 處+戳+§6.4 擴充）/ `design/docs/{color-tokens,spacing,typography}.md`（各 +2 行戳）
- **備份（入 git·5 份）**：`.claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_{components,dom-reference,color-tokens,spacing,typography}.md.bak`（路徑依專案慣例落 `.claude-logs/archive/`）
- **baton 暫存（嚴禁 git add）**：本執行報告、plan_v1、tasks。

---

## §4 修改說明（標註去毒 / 30 ID 分佈 / token 戳）＋ 執行期 deviation 誠實清單

### (a) 標註去毒（U1）
- **components.md**：§7.4 `.title-meta`/`.title-meta-sep` 合併為 ⚠️ 未實作單條（附 `renderTitleHeader:2748` 證據）；resume 分支行內 ⚠️；§8.2 `.msg-ai-actions` 行內 ⚠️ 半實作（`:1063-1098`/`:2405-2406`/注入未接）+ `.msg-copy`/`.msg-regen` 子彈各補「⚠️（注入未接，見上）」。**`.dropdown-popup`（L153/L209）零碰**（diff grep 0 佐證）。
- **dom-reference.md**（deviation ②、同源病灶）：§2.2 current-title 列 title-meta 加（⚠️ 未實作、見 §4.2）；§4.2 結構契約 code block 內 title-meta 行加 HTML 註解 ⚠️；§5.1 `.msg-ai` 結構後加 ⚠️ 半實作說明列。

### (b) dom-reference 補漏（U2）——30 條真缺
- §1 `app`（三欄根 wrapper）；§2.2 `edit-tags-btn`；§4.4 新節 `abstract-toolbar`（FE-AESTHETICS C1 拆出脈絡）；§6.4 補 `help-title`/`confirm-title`/`confirm-cancel-btn` 列 + **新增 theme（5）/tag（5）/action（6）/notice（5）四家族小節**（每 id 一行：用途+JS 綁定行號）；§9 既有列補 `theme-link` id（`:2131`）。

### (c) 戳記（U3/Q3）
- components/dom-reference 頂部同步戳（基準 `@8e5d1fa`）；token 三檔 H1 下零差稽核戳（§4.1(c) 逐字）。

### (d) 執行期 deviation（誠實清單、供 checkout 裁決）
1. **U2 量測修正**：tasks §6.1 抽取器（要求 `` `#id` ``）與檔內既有「裸 `` `id` `` +🔒」慣例不符 → 原「48 缺」中 **18 為格式盲點**（§2.1-2.3/§3.3/§5.2/§6.4 早已記載）；真缺＝**30**、已全補。驗收改用**容錯抽取**（帶#或裸皆計）——與 plan v3 勘誤同族（regex 盲點）、量測目標「差集=0」不變。
2. **dom-reference 同源病灶標註**（超出 U1 字面「components.md」）：§2.2/§4.2/§5.1 三處同樣把 title-meta/msg-actions 寫成現況——同 commit 同措辭一併去毒（U1 目標「去毒」之同源延伸）。
3. **confirm-modal「點 mask 不關閉」stale 更正**：實檔 `data-no-mask-close="false"`（OPTIMIZE-1 C2 解鎖、`index.html:1432` 註解）→ 更正並補 `confirm-cancel-btn` 列。
4. **§6.4 引言「兩個固定 modal」→「七個」**：隨補齊如實修正。

---

## §5 測試與驗收結果（§6.1 終端輸出）

```
U2 覆蓋率（容錯抽取）：已記載且屬實 75 / 75、殘餘漏記 0        ✅
U1 逐行標註：components title-meta/msg-ai-actions/msg-copy/msg-regen 無標註行＝各 0；
             dom-reference title-meta 無標註行＝0               ✅
dropdown-popup：git diff components.md 命中 0（零碰）           ✅
U3/Q3 戳：grep -l 8e5d1fa design/docs/*.md → 5 檔               ✅
增量：dom-reference 426→473（+47 ≤160）                          ✅
範圍：git diff --stat ＝ design/docs 5 檔（+64/-11）、零代碼、index.html 零 byte ✅
```

---

## §6 不可動清單遵守

- [x] 一切代碼/`static/`（index.html 唯讀對照、diff 無其蹤）。
- [x] `.dropdown-popup` 相關行零碰（grep 佐證）。
- [x] token 三檔內容零改（各僅 +2 行戳；值表/token 名未動）。
- [x] theme-guide/principles/其餘 design/docs 5 檔未動（diff --stat 佐證）。
- [x] 既有 27 條深度內容未重寫（僅補列/標註/更正 stale 敘述——後者列 deviation ③④）。
- [x] baton 過程檔未 git add。

---

## §7 銜接（baton 狀態 + 下一步）

- **baton**：plan_v1 / tasks / 本報告 暫存、未 mv 未 add（待 checkout 一次性歸檔）。
- **git 追蹤**：本 commit ＝ 5 檔 + 5 `.bak`。
- **hash 自癒**：FE-PERF-2 checkout 已 ship `bc2bcc4` → TODO 索引行與 done_archive checkout 列已回填（本輪同步）。
- **下一步**：**checkout**（Conformance 對 plan v3 + 四項 deviation 裁決 + 鐵律報告直產 + 雙層結案），由 baron 另下提示詞觸發。
- **§自評**：(a) 越界？四項 deviation 全數為「同 U 目標之量測/同源修正」、逐項標註供裁決；未動任何規劃外檔案。(b) 推進 U1/U2/U3+Q3；未做白工。

---

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）：.claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_*.md.bak ×5

# 2. git add 清單（逐檔顯式；嚴禁 git add . / baton 暫存檔）
git add design/docs/components.md
git add design/docs/dom-reference.md
git add design/docs/color-tokens.md
git add design/docs/spacing.md
git add design/docs/typography.md
git add .claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_components.md.bak
git add .claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_dom-reference.md.bak
git add .claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_color-tokens.md.bak
git add .claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_spacing.md.bak
git add .claude-logs/archive/2026-07-09_DOC-SYNC-1_C1_typography.md.bak

# 2.5 staged 自檢（期望恰 10 檔）
git diff --cached --name-only

# 3. commit message 草稿（寫入 /tmp/DOC-SYNC-1_C1_msg.txt）
cat > /tmp/DOC-SYNC-1_C1_msg.txt << 'EOF'
DOC-Refactor: DOC-SYNC-1 C1 — Docs Truth Sync

同步設計文獻至 2026-07-09 前端現況：components.md 標記 5 個未實作/半實作
類別，dom-reference.md 補齊 30 個真缺 ID（另 18 為既載格式盲點）並擴充
Modal 七家族，token 三檔加零差稽核戳。
EOF

# 4. baron 手動執行
git commit -F /tmp/DOC-SYNC-1_C1_msg.txt
```
