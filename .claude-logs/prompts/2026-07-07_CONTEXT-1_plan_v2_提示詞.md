# 2026-07-07 CONTEXT-1 plan v2（九 OQ 定案）提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：plan review 定案（階段 1 收尾、baron 拍板 §9 九 OQ）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-07

---

## 原始提示詞（逐字）

> 評估下面建議
> 如果沒問題
> 更新plan
>
> ### 文獻精神落實評估
> **已完全落實**。該 plan 針對 TODO.md 進行物理瘦身、收斂 baton wildcard 為單一 README 以落實「注意力預算（Attention Budget）」與「按需檢索（Just-in-Time）」；並明文規定載入鏈「靜態優先、動態靠後」之原則以最大化「快取命中率（Prompt Caching）」，完全符合五篇原始文獻之核心治理精神。
>
> ---
>
> ### 針對 Open Questions (Q) 之決策與建議
>
> * **Q1（開工時機）**：**採推薦方案**。授權本案執行時順帶將 `a150915` hash 回填至 TODO.md 佔位符後即刻開工。
> * **Q2（歸檔檔落點與命名）**：**採推薦方案**。落點設為 `archive/TODO_done_archive.md`（tracked），保留 git 追蹤與 grep 可及性。
> * **Q3（TODO 索引行格式）**：**採推薦方案**。`- ✅ <代號> <主題>（<首hash>…<末hash>、N commits）→ archive/TODO_done_archive.md` 格式能最小化 token 且保留完整追溯性。
> * **Q4（wildcard 收斂範圍）**：**採推薦方案**。僅保留 `baton/README.md`，其餘長駐治理文件改由提示詞顯式指路。
> * **Q5（載入排序原則落點）**：**採推薦方案**。將快取優化排序原則寫入 `CLAUDE.md §99.1`「約束事項」中。
> * **Q6（pre_tool_guard 攔截）**：**採推薦方案**。於 TODO.md 寫入 `// BYPASS_TRUNCATION_GUARD` sentinel 標記通行，並在執行報告記載事由。
> * **Q7（FRAMEWORK §2.1 改版）**：**採推薦方案**。將「不另外分檔」改為「雙層表述」以解決物理衝突，並同步修改下游模板。
> * **Q8（整合測試豁免）**：**同意豁免**。純文件與提示詞重構（DOC-Refactor），無業務代碼變更。
> * **Q9（工作目錄與授權）**：**同意授權**。同意於當前專案就地執行，並授權順手將 `CLAUDE.md §3` 指向的工作目錄更新為當前 repo 的實際路徑 `/Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public`。

---

## 上下文（承接對話）

1. plan v1（`baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md`）產出後，baron 逐項拍板 §9 九 OQ、全數採推薦方案並下達「更新 plan」。
2. Claude 評估後兩項技術性銳化（不改決策方向）：**Q6** 經讀 `tools/pre_tool_guard.sh` 實作確認 sentinel 判定對象＝Write/Edit 之 tool_input 內容（非檔案本體）→ 規格化為「夾帶 HTML 註解放行 + 後續小 Edit 移除、TODO 不殘留」；**Q9** baron 給定路徑為 Mac 側 OrbStack 視圖（`/Users/baroncheng/OrbStack/claude-lab/home/...`）、Server session 同目錄實際為 `/home/baroncheng/mad-professor-public` → 正規化為「主 repo 根目錄 + 雙環境視圖對照」，且 grep 發現 CLAUDE.md §4 跨環境表（L123）同引 stale worktree、須一併同步（超出字面授權、plan 內標明待 baron 階段 3 確認）。

## 產出

- `baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md` 就地更新至 §99.2 v2（九 OQ 全 🟢 定案、U1/U2/U5 參數落定、新增 U7 工作目錄修正、Q6/Q9 銳化）
