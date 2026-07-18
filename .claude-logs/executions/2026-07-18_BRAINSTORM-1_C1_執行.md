# BRAINSTORM-1 C1 — Brainstorming SOP & Visual Companion 執行報告

---

**任務代號**：BRAINSTORM-1 C1
**執行日期**：2026-07-18
**依據規劃**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md`（v2；Checkout 歸檔更名去 "vendoring"）
**次級參考**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：工作區處於 SOP-COMPLY checkout（`fb3e76a`）之後、BRAINSTORM-1 plan v2 + tasks 已暫存 baton。`.claude-logs/sop/` 無 brainstorming 設計發想規範。
- **完成狀態**：新建兩份文件於 `.claude-logs/sop/`——作業 SOP 手冊 + 視覺伴讀指引（vendored 路徑改指）。全文完整根路徑防呆。**零業務代碼改動、零 .py 觸碰**。
- **與全局策略對齊**：本 commit conditioned on `plan §2` 目標 1（新建作業 SOP，含問答骨架 / 落點 / 溯源 header / spec→template_plan 對照 / 兩護欄 / 移除 auto-commit / 視覺伴讀章）——完全落地、無偏離。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Brainstorming SOP & Visual Companion：新建作業 SOP 手冊 + 視覺伴讀指引（路徑完整根路徑防呆、落點改導、移除 auto-commit） | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md` | — | 問答骨架 + 落點規範 + 溯源 header 樣板 + spec→template_plan 對照 + 兩護欄 + 禁令（不 auto-commit/不裝 plugin/不接執行鏈）+ 視覺伴讀章 + 驗收檢查表 + §0/§99 |
| 新建 | `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md` | — | vendored 自 superpowers visual-companion.md，`scripts/xxx`→`.claude-logs/tools/xxx`、mockup 落點→`.claude-logs/baton/.brainstorm/<session>/` |

> 本 Commit 僅新增檔案、無修改既有內容檔 → **全程零 `.bak`**（對齊 tasks §8 C1 + prompt 備份規則）。

---

## §4 修法說明

### §4.1 `2026-07-18_brainstorming_設計發想作業_SOP_手冊.md` — 新建作業 SOP

蒸餾 superpowers `skills/brainstorming/SKILL.md` 之問答骨架、改寫貼合本專案：

- **§2 問答流程骨架**：8 步（探索 context → 逐一澄清〔一次一題·優先選擇題〕→ 提 2-3 方案權衡 → 分段核准 → 產 spec → 自檢 → baron 核准閘 → 交棒 plan）。
- **§3 落點與溯源**：spec 落 `.claude-logs/baton/<YYYY-MM-DD>_<任務編碼>_design_spec.md`（明文禁 `docs/superpowers/`）+ 溯源 header 樣板（產出工具/時間/情境/參考來源/任務代號）。
- **§4 對照與護欄**：spec→template_plan 欄位對照表〔標明 §3 現況證據 / §4 接縫契約 / §6 不可動清單 / §8 驗證計畫**四樣仍須階段 1 手工長出**〕+ 兩護欄（原料≠plan / 原料必帶溯源 header）。
- **§6 禁令**：不 auto-commit（對齊 `CLAUDE.md §1.3`）/ 不裝 plugin / 不接執行鏈。

### §4.2 `2026-07-18_brainstorming_visual-companion_指引.md` — vendored 視覺伴讀指引

自 superpowers `visual-companion.md` vendored，**路徑改寫**：

```
scripts/start-server.sh    → .claude-logs/tools/start-server.sh
scripts/stop-server.sh     → .claude-logs/tools/stop-server.sh
scripts/frame-template.html→ .claude-logs/tools/frame-template.html
scripts/helper.js          → .claude-logs/tools/helper.js
mockup/session 目錄         → .claude-logs/baton/.brainstorm/<session>/（gitignored）
```

保留判斷框架（視覺型 vs 文字型）、操作流程（啟動/每輪/回饋迴路/迭代/收尾）、內容撰寫指引、檔案依賴表；補註「落點改導僅在 start-server.sh、server.cjs 零編輯」。

---

## §5 測試結果

### §5.1 本地改動狀態確認

```bash
$ git status -s | grep -E "sop/2026-07-18_brainstorming"
?? .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md
?? .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md

$ git status -s | grep -E "\.py$"
（無輸出 → 無 .py 改動）
```

### §5.2 §6.1 C1 驗收 grep（真實輸出）

```bash
$ ls -la .claude-logs/sop/2026-07-18_brainstorming_*
... 設計發想作業_SOP_手冊.md  8.6K
... visual-companion_指引.md  3.6K          # 存在且非空 ✅

$ grep -nE "溯源|template_plan|護欄|baton" 設計發想作業_SOP_手冊.md
4/5/22/25/31/36/47/49/52/56/...             # 關鍵章節齊備 ✅

$ grep -c "\.claude-logs/tools/" visual-companion_指引.md
10                                          # 已改指 ✅（>0）

$ grep -nE "(^|[^.-])scripts/" visual-companion_指引.md
3:> 本文件 vendored 自 superpowers ... 所有 `scripts/xxx` 相對引用改指 ...
# 唯一命中＝來源說明散文（backtick 內佔位 token），非操作路徑；所有操作路徑用 .claude-logs/tools/ ✅

$ grep -nE "^\s*[`(]?(sop|tools)/" 兩檔
無裸 sop//tools/ 起首（合規）✅            # 完整根路徑防呆通過
```

### §5.3 SOP 一致性核查（BE-Refactor / BE-Hotfix 強制）

DOC-Refactor 工作流，無 .py 改動，跳過（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 業務代碼（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`） | [x] ✅ 未觸碰（零 .py） |
| 既有 `.claude-logs/tools/` 5 腳本 | [x] ✅ 未觸碰（本 commit 未動 tools/） |
| `.gitignore` 現有規則 | [x] ✅ 未變更 |
| `CLAUDE.md §1–§5` / `WORKFLOW_SOP §1–§7` / framework 核心規範 | [x] ✅ 未變更（登記為前置留下一輪） |
| `prompts/` 既有歷史檔 | [x] ✅ 未改（僅新增本任務提示詞 + INDEX 同步） |

---

## §自評（策略對齊自我審查）

- **(a) 越界?**：否。僅新增 `.claude-logs/sop/` 兩檔 + 依 prompt 指示同步 TODO/archive/INDEX + 歸檔提示詞；未動業務代碼、未動 tools/、未動核心規範。
- **(b) 無關 / 違規?**：否。兩檔內容全對應 tasks §8 C1 具體實作細節；無冗餘；未 auto-commit（守 §1.3）。
- **(c) 推進哪個 U-N?（正向軸）**：推進 `plan §2` 目標 1（新建作業 SOP + 視覺伴讀指引），為 C2（tools 腳本）與 Checkout（E2E）鋪基。

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `.claude-logs/baton/`，待 Checkout 收官一次性 `mv + git add` 歸檔至 `executions/`，還原 baton/ 只剩 README（＋長駐 plan/tasks 暫存待同批歸檔）。
- **hash 自癒（本輪順帶）**：SOP-COMPLY checkout 之 `待 baron 回填` 佔位符 → 依 git log 回填真實 hash `fb3e76a`（雙源：`TODO.md:16` + `archive/TODO_done_archive.md` checkout 列）。RAG-1/MODEL-8/MODEL-3 之「待 push 後回填」屬舊式佔位、非「待 baron 回填」範圍且需 commit 考古，留置不動。
- **下一步**：tasks.md C2 — Vendored Scripts & Env Redirect（tools 腳本導入與環境變數改導），待 baron 下達獨立提示詞。
- **消化歸檔之 baton 檔**：無（本階段不歸檔）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（本 Commit 僅新增檔案，無備份）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
#    commit 前以 git diff --cached --name-only 自檢 staged 集合＝本清單，多/少一檔即停。
#    ⚠️ baton/ 執行報告與 plan/tasks 嚴禁在此階段 git add（Checkout 才歸檔）。
git add .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
git add .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md

# 3. commit message 草稿（已寫入 /tmp/BRAINSTORM-1_C1_msg.txt）
git commit -F /tmp/BRAINSTORM-1_C1_msg.txt
```

### §8.2 commit message 草稿

（草稿已寫入 `/tmp/BRAINSTORM-1_C1_msg.txt`）

```
DOC-Refactor: BRAINSTORM-1 C1 — Brainstorming SOP & Visual Companion

- 新建 .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
- 新建 .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md
- 蒸餾 superpowers brainstorming 問答骨架、落點改導 baton/、溯源 header、spec→template_plan 對照、兩護欄、移除 auto-commit
- 視覺伴讀指引 scripts/→.claude-logs/tools/、mockup→baton/.brainstorm；全文完整根路徑防呆
- 執行報告暫存 baton/ 不入版控

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 BRAINSTORM-1 C1 的文件新增與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；階段 6 收官時 Conformance 核對原始 plan；核對後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 階段 6 收官 check 提示詞 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存 baton/、Checkout 前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C1 執行唯一源，不重複 tasks 六維度、不重複 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-07-18)：C1 執行完畢產出報告（新建 sop/ 兩檔、零 .bak、零 .py；順帶 hash 自癒 SOP-COMPLY checkout `fb3e76a`）
