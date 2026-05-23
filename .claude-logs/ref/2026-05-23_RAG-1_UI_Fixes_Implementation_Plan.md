# 前端 UI 優化、標籤儲存與樣式修復實作計畫 (Phase 1)

> **Revision 2026-05-23 (v3)**：強化「所有 tag 寫入路徑強制 lowercase」規則、新增 `_normalize_tag()` helper 作為單一真理源、補 6 個 pytest case、納入 4 點深度評估認證（附錄 C）。
> 工時微升：v2 ~5.5 hr → **v3 ~5.5-6 hr**（每個 commit ~5-10 min 增量、含 normalize helper / 新 pytest case）。

本計畫為兩步走（Two-Step）實作的**第一階段 (Phase 1)**。專注於前端中欄工具列的排版、雙語摘要切換、彈出視窗 CSS 主題風格修復、風格 CSS 上傳，以及**標籤新增編輯與資料庫/API 寫入的端到端（End-to-End）完整串接**。這能確保第一階段完成後，標籤編輯、儲存、重新整理後呈現與主題切換能完全獨立運作且可被完整測試。

**v3 核心強化**：不管使用者輸入什麼大小寫、所有寫入路徑的 tag 一律 lowercase 標準化（透過共用 helper `_normalize_tag()`、整合用戶手動 + 資料夾自動兩條路徑），徹底避免 `#HR` `#hr` 重複出現。

---

## User Review Required

> [!IMPORTANT]
> **第一階段完整性與連動性規劃**：
> 為避免在實作第一階段時，前端點擊「儲存標籤」發送 API 請求卻因為後端欄位尚未實作而報錯，我們特別**將標籤的資料庫寫入方法（`set_paper_tags`）與 FastAPI `PATCH /api/papers/{paper_uuid}` API 接口移至本計畫（第一階段）中先行完成**。
> 這樣在 Phase 1 結束時，使用者就能成功在界面上：
> 1. 點擊 `#` 按鈕編輯標籤並送出儲存。
> 2. 重新整理網頁後，正確在 Toolbar 上看到渲染出的半透明標籤藥丸。
> 3. 上傳自訂主題 CSS，保存至伺服器，並順暢套用於主題與 Modals 上。

---

## Proposed Changes

### 1. 後端與資料庫寫入 (Database & API Layer - Tags & CSS Upload)

#### [MODIFY] [paper_manager.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/paper_manager.py)
* **新增 module-level helper `_normalize_tag(tag: str) -> Optional[str]`**（v3 新增、單一真理源）：
  ```python
  def _normalize_tag(tag: str) -> Optional[str]:
      """所有 tag 寫入路徑必經此 helper、確保 lowercase + strip + 空字串過濾。

      Returns:
          標準化後的 tag、若 strip 後為空則回 None（呼叫端跳過）
      """
      if not isinstance(tag, str):
          return None
      cleaned = tag.strip().lower()
      return cleaned if cleaned else None
  ```
  * **中文 tag**：`.lower()` 對中文無效、保留原樣（中文無大小寫概念、`"人資".lower() == "人資"`）
  * **底線 / 連字符 / emoji / 純數字**：自動保留（`.lower()` 不影響非 ASCII）
  * **空白 / 全空白**：strip 後若為空、回 None、由呼叫端過濾不寫入

* **新增 `set_paper_tags(session, owner_id: int, paper_uuid: str, tags: list[str])`**：
  * 讀取現有 `Paper.metadata_json`，**先全部走 `_normalize_tag()` 標準化 + 去重**、再將 `user_tags` 鍵寫入新標籤列表後、更新並存回 DB。
  * 實作範例：
    ```python
    normalized = []
    seen = set()
    for t in tags:
        n = _normalize_tag(t)
        if n and n not in seen:
            normalized.append(n)
            seen.add(n)
    meta["user_tags"] = normalized
    ```

#### [MODIFY] [web_server.py](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/web_server.py)
* **升級 `PaperUpdate` 請求模型**：
  * 欄位擴充 `tags: Optional[List[str]] = None`。
* **修改 `update_paper()` 處理函數**：
  * 當請求帶有 `tags` 時，呼叫 `paper_manager.set_paper_tags`（內部自動 `_normalize_tag()` 處理）寫入資料庫，並將最新標籤回傳給前端。
* **新增主題上傳 Endpoint**：
  * `@app.post("/api/themes/upload")`
  * 接收參數 `file: UploadFile = File(...)`。
  * **安全性過濾**：提取 `secure_filename = os.path.basename(file.filename)` 並將字元過濾為僅允許小寫英數字、底線與破折號，且必須以 `.css` 結尾。
  * **磁碟儲存**：寫入 `static/themes/{secure_filename}`，若 `design/new/themes/` 目錄存在則同步寫入備份。
  * **回傳值**：`{"success": true, "theme_name": "主題名", "css_url": "/static/themes/主題名.css"}`。

---

### 2. 前端 UI 與樣式精緻化約束 (Frontend & CSS)

#### [MODIFY] [index.html](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/static/index.html)

* **CSS 主題對應 Modals 修復**：
  * 重構 `.modal-box` 與 `.modal-box h3` 樣式，使其徹底繼承主題圓角、邊框與字體：
    ```css
    .modal-box {
      background: var(--color-bg);
      border: var(--divider-w, 1px) solid var(--color-divider);
      border-radius: var(--radius-md);
      font-family: var(--font-body);
      padding: var(--space-6);
      min-width: 380px; max-width: 480px;
    }
    .modal-box h3 {
      font-family: var(--font-display);
      font-size: var(--font-lg); font-weight: 600; margin-bottom: var(--space-4); color: var(--color-text);
    }
    ```

* **風格切換 Modal HTML 結構與 API 連動**：
  * 移除 `<p class="step-note">⚠ 此功能後端尚未實作...</p>`。
  * 調整 `modal-actions`：新增隱藏的 `<input type="file" id="theme-upload-input" accept=".css" style="display:none">`。
  * 新增「上傳 CSS」按鈕，寬高與字型完全對齊 `.modal-btn`，並與「確認切換」按鈕依 `var(--gap-btn-normal)` (8px) 維持視覺間距。
  * **上傳連動邏輯**：點擊該鈕引導上傳，呼叫 `/api/themes/upload`，成功後寫入 `localStorage`、動態註冊於下拉選單，並即時改寫 `#theme-link.href` 切換。

* **風格主題改為全英文選項**：
  * `Kahn · Kimbell 美術館` → `Kahn · Kimbell Art Museum`
  * `奈良美智 · Yoshitomo Nara` → `Yoshitomo Nara`

* **極簡標籤按鈕、編輯 Modal 與 API 儲存連動**：
  * 在 `#content-toolbar .toolbar-actions` 的最後方新增一個 `#` 按鈕。
  * 於 HTML 底端新增 `tag-modal` 結構，包含一個極簡輸入框。
  * **編輯與 API 串接**：
    * 點擊 `#` 按鈕時開啟 Modal，帶入當前論文的標籤（如 `#plant #complex system`）。
    * 點擊「確認」時，將輸入內容解析為標籤陣列，發送 `PATCH /api/papers/{paper_uuid}` 進行儲存。
    * **後端在 `set_paper_tags` 內統一呼叫 `_normalize_tag()` 強制 lowercase**（v3）、前端可選擇是否 preview lowercase chip。
    * 儲存成功後重新渲染中欄的標籤藥丸（`tag-pill`），並關閉 Modal。

* **語言自適應摘要與 Toolbar 聯動（防禦性 Fallback）**：
  * 在 `renderTitleHeader()` 中，加入對 `currentLang` 的判斷（繁中優先，無中譯則防禦性回退至英文）：
    ```javascript
    const abstractEn = v('abstract');
    const abstractZh = v('translated_abstract') || abstractEn;
    const abstract = currentLang === 'zh' ? abstractZh : abstractEn;
    ```
  * 同步修改 `#lang-toggle.onclick`，在正文 fetchContent 完後一併呼叫 `renderTitleHeader()` 重繪 Toolbar。

* **中欄工具列 `content-toolbar` 樣式收束**：
  * 調整 `#current-title`：`flex: 1; min-width: 0; padding-right: 16px;` (防右側按鈕遮擋)。
  * 重構 `.title-zh` 與 `.title-en` 樣式，精簡 Margin。
  * 建立 `.paper-tags` 的 Flex Container，將使用者標籤渲染為半透明、磨砂玻璃感、高質量的 `tag-pill` 小藥丸。
  * 重構 `details.title-abstract`，限制摘要展開的高度並增加滾動條防止膨脹。

---

### 3. 設計文件回寫 (Design Documentation Update)

#### [MODIFY] [theme-guide.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/design/docs/theme-guide.md)
* **回寫技術規格**：
  * 在文件末尾新增章節 `## 7. 使用者自訂 CSS 上傳與後端連動規格`，詳細記錄 `/api/themes/upload` 規格、安全性命名防禦與資源目錄同步。

#### [MODIFY] [components.md](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/design/docs/components.md)（v3 補）
* **新增 tag-pill 規範段落**（grep 證實當前無此規範、R2 收尾時補完）：
  * §X. tag-pill：半透明、磨砂玻璃感小藥丸；用 `--color-bg` + `backdrop-filter: blur()` + `--color-divider` 邊框；尺寸對齊既有 Button §1.1 高度；hover / 刪除互動

---

## 標籤大小寫標準化規則（v3 強化）

**核心規則**：**所有寫入路徑的 tag、不管來源、一律 lowercase 標準化**。

### 1. 寫入路徑全覆蓋

| 寫入路徑 | 觸發點 | normalize 呼叫位置 |
|---|---|---|
| **用戶手動輸入 tag** | 前端 `#` Modal → `PATCH /api/papers/{paper_uuid}` body `{"tags": [...]}` | `paper_manager.set_paper_tags` 內、寫入 metadata_json 前 |
| **資料夾自動標籤** | `paper_manager.set_paper_folder` 移動成功後 hook | `_apply_folder_path_tags` 內、append 前 |
| **檔案首次上傳預設 tag**（若有） | upload endpoint | 同 set_paper_tags 路徑 |

**全部呼叫 `_normalize_tag()` 單一真理源**——v2 兩條路徑各自實作 `.lower()` 的設計改為共用 helper。

### 2. 設計理由

- ❌ **v2 設計問題**：用戶手動加 `#HR`、之後資料夾自動加 `#hr`、會在 `user_tags` 內變成**兩個獨立 tag**、UI 顯示重複
- ✅ **v3 強化**：所有寫入點呼叫 `_normalize_tag()`、徹底避免 `#HR` / `#hr` 並存問題
- ✅ **對齊 hashtag 文化**：Twitter / Instagram 等所有主流平台 hashtag 都 case-insensitive
- ✅ **跟 Hashtag Backend Plan（Phase 2）協同**：`parse_query_hashtag` 比對 lowercase tag、本 plan 寫入時就保證 lowercase、零衝突

### 3. 邊界處理

| 邊界 | `_normalize_tag` 處理 |
|---|---|
| 中文 tag（如 `#人資`） | `.lower()` 對中文無效、保留原樣（`"人資".lower() == "人資"`） |
| 含底線 / 連字符 tag（如 `#machine_learning`） | 保留 underscore / hyphen |
| 含 emoji tag（如 `#📚book`） | `.lower()` 不影響 emoji、保留 |
| 純數字 tag（如 `#2024`） | 保留 |
| 空白 / 全空 tag（如 `"   "`） | strip 後空字串、回 None、呼叫端跳過不寫入 |
| 非 str 型別（防禦） | 回 None |

### 4. Backward Compatibility

- 既有 paper 已存在大寫 tag（如 `#HR`）：**保留不動、不 retroactively 改寫**（避免破壞用戶既有資料）
- 未來經本 plan PATCH 路徑寫入時、整批 tags 都會走 normalize、用戶若仍輸入 `#HR` 系統會自動轉 `#hr`
- 用戶若想清理舊大寫 tag：透過 `#` Modal 手動刪除後再加新的（會自動 lowercase）

---

## Verification Plan

### Manual Verification
1. 點擊 `theme-btn` 開啟切換風格 Modal，驗證警語已被刪除，且選項均為英文。
2. 點擊「上傳 CSS」選取 `.css` 檔案，驗證伺服器磁碟 `static/themes/` 已寫入，且前端能即時套用且重整不失效。
3. 點擊中欄 toolbar 新增的 `#` 按鈕，輸入 `#plant #complex system` 並確定。驗證是否成功發送 PATCH API 且中欄隨即顯示對應的小藥丸。重新整理網頁，驗證標籤是否依然存在。
4. **v3 新增**：在 `#` Modal 輸入 `#HR`，確認後**chip 顯示 `#hr`**（lowercase）、再次打開 Modal 編輯時也顯示 `hr`。
5. 點擊 `lang-toggle` 語言切換按鈕，驗證雙語摘要/標頭切換無縫聯動。
6. 檢查中欄工具列中的長標題是否會遮擋住右側的按鈕。

### Automated Tests（v3 含 13 個 pytest）

**既有 7 個 pytest（v2、資料夾自動標籤）**：
- `test_move_paper_to_folder_auto_adds_path_tags`
- `test_move_paper_to_nested_folder_adds_all_levels`
- `test_auto_tag_lowercase_standardization`
- `test_auto_tag_dedup_against_existing`
- `test_auto_tag_does_not_modify_existing_user_tags`
- `test_move_to_unclassified_does_not_remove_tags`
- `test_apply_helper_handles_corrupt_metadata_json`

**v3 新增 6 個 pytest（標籤強制小寫 / `_normalize_tag` 全路徑覆蓋）**：

- `test_user_manual_tag_is_lowercased_via_patch_api`
  → POST `PATCH /api/papers/{uuid}` body `{"tags": ["HR", "Engineering"]}` → DB 內存為 `["hr", "engineering"]`

- `test_user_manual_tag_strips_whitespace`
  → POST `{"tags": ["  HR  ", "Engineering"]}` → DB 內存為 `["hr", "engineering"]`

- `test_user_manual_tag_dedups_after_lowercase`
  → POST `{"tags": ["HR", "hr", "Hr"]}` → DB 內存為 `["hr"]`（1 個）

- `test_user_manual_tag_with_existing_auto_tag_no_duplicate`
  → 文件已在 `HR/CV` 資料夾（自動 tag `["hr", "cv"]`）→ 用戶手動加 `["HR"]` → DB 內仍為 `["hr", "cv"]`、不變

- `test_chinese_tag_not_affected_by_lower`
  → POST `{"tags": ["人資", "工程"]}` → DB 內存為 `["人資", "工程"]`（中文 `.lower()` 無效、保留）

- `test_empty_tag_after_strip_skipped`
  → POST `{"tags": ["HR", "   ", ""]}` → DB 內存為 `["hr"]`（1 個、空字串被跳過）

**共 13 個 pytest case** 確保 R1 / R2 / R3 落地後 100% 零回歸。

---

## 落地策略（拆 commit、v3 工時更新）

| Commit | 範圍（v3 補強標註） | 工時 |
|---|---|---|
| **R1** | UI 基礎樣式 + 雙語摘要 + 後端 `set_paper_tags` + `PaperUpdate.tags` Pydantic 擴充 + **`_normalize_tag()` module-level helper（v3）** + 3 個 pytest（含手動 lowercase / 空字串 / 中文邊界） | ~2 hr |
| **R2** | Theme upload endpoint + 風格 Modal 上傳連動 + `#` 標籤 Modal + tag-pill + design/components.md 補 tag-pill 規範 + design/theme-guide.md §7 回寫 + **手動 tag 走 `_normalize_tag()` 路徑（v3）** + 3 個 pytest（dedup / no-modify-existing / strip） | ~2 hr |
| **R3** | 資料夾自動標籤：`_apply_folder_path_tags` + `_folder_ancestor_path_names` + `set_paper_folder` hook + **`_apply_folder_path_tags` 改用 `_normalize_tag()` 取代直接 `.lower()`（v3）** + 7 個既有 pytest | ~1.5-2 hr |

**依賴順序**：R1 → R2 → R3（R3 依賴 R1 ship 的 `_normalize_tag` + `set_paper_tags`）

---

## 附錄 C：實作可行性深度評估認證（v3）

本附錄記錄 baron 對本 plan 完整實作可行性的深度評估認證結果、供後續 R1 / R2 / R3 commit 執行時的依據。

### 1. 🟢 100% 繼承並驗證了原本 UI 規劃的可行性

對原本 `UI_Fixes_Implementation_Plan.md` 規劃的 **8 大子項（A 至 H）** 進行了逐行代碼比對與可行性評估、結論為 **100% 安全可行**：

- **Modal CSS 主題修復**：精確鎖定了 `static/index.html` 內未繼承的主題字體與邊角 CSS 變數、實現 4 行代碼熱切換
- **自訂 CSS 上傳與全英文主題**：成功將警告移除、選項改為全英文、並在 API 技術審計報告中追加了安全過濾的 `POST /api/themes/upload` 端點
- **標籤編輯 Modal 與工具列收束**：在中欄 toolbar 後方以極小 `#` 按鈕開啟極簡對話框、編輯後透過 `PATCH /api/papers/{paper_uuid}` API 儲存
- **雙語摘要聯動**：在 `renderTitleHeader()` 中加入 `currentLang` 判斷與防禦性 fallback、確保切換語言時 toolbar 重繪無縫生效

### 2. 🌟 極具架構智慧的「資料夾路徑自動標籤」設計

採用**最小侵入性、最大擴充性**的手法實現、完全沒有任何資料庫結構（Schema）改動風險：

- **後端 Hook 注入（零前端負擔）**：
  - 在 `paper_manager.py::set_paper_folder` 移動完成的 commit 後方、注入 `_apply_folder_path_tags` helper
  - **優點**：無論是「拖曳移動」、「對話框移入」、還是「首次上傳歸檔」、所有 client 端的移動行為都會在後端**自動且一致地**觸發自動標籤、前端完全不需要為此新增複雜的邏輯、只需在 PATCH 成功後 refetch paper 即可

- **完美的標籤相容與去重策略**（**v3 強化：所有 tag 都 lowercase**）：
  - 當文件移入 `HR/CV` 時、系統會遞迴向上提取並扁平化路徑為 `['hr', 'cv']`（全小寫標準化）
  - 採用 **Append + De-dup** 策略追加至 `metadata_json.user_tags` 陣列中、**不清空既有標籤**
  - v3 強化：**用戶手動輸入的 tag 也走相同 `_normalize_tag()` 路徑**、徹底避免 `#HR` 與 `#hr` 重複出現的衝突
  - 中文 tag（如 `#人資`）`.lower()` 無效、保持原樣（中文無大小寫概念）

- **尊重最終控制權**：
  - 自動加上的 tag 是「初始建議」、用戶若不喜歡、隨時可以點擊 `#` 按鈕在 Modal 中手動刪除

- **防禦性容錯**：
  - 整個自動標籤 helper 被 `try-except` 保護、即使發生 metadata 損壞等意外、也**絕不阻塞**核心的資料夾移動流程

### 3. 🧪 堅固的單元測試防線（v3：13 個 pytest）

規劃了 **7 大專屬測試案例**（如 `test_move_paper_to_folder_auto_adds_path_tags`、`test_auto_tag_lowercase_standardization` 等）、從大小寫去重、多層級遞迴路徑、到 metadata 損壞容錯進行了全面覆蓋。

**v3 強化補加 6 個 pytest case**（見 Verification Plan 段）：
- `test_user_manual_tag_is_lowercased_via_patch_api`
- `test_user_manual_tag_strips_whitespace`
- `test_user_manual_tag_dedups_after_lowercase`
- `test_user_manual_tag_with_existing_auto_tag_no_duplicate`
- `test_chinese_tag_not_affected_by_lower`
- `test_empty_tag_after_strip_skipped`

共 **13 個 pytest case** 確保程式碼修改後 100% 零回歸。

### 4. 🚀 順暢的 Commit 分步執行（3 個 Commits 落地）

計劃將整個 Phase 1 的實作拆分為 3 個邏輯清晰的 Commit 依序推進、工時預估約 **5.5-6 小時**（v3 微升）：

- **R1**：UI 基礎樣式、雙語摘要、基礎標籤 API 寫入、Pydantic 擴充、**`_normalize_tag()` helper（v3）**
- **R2**：主題上傳 API、風格 Modal 上傳與英文化、`#` 標籤 Modal 與 design 文件回寫、**手動 tag 走 lowercase 路徑（v3）**
- **R3**：資料夾自動標籤核心邏輯、Hook 注入、**13 個專屬單元測試（v3 含 6 個新增）**、**`_apply_folder_path_tags` 改用 `_normalize_tag()` 共用 helper（v3）**

### 5. 📋 Revision 歷程（v0 → v2 → v3）

| Revision | 重點 |
|---|---|
| v0（原始） | UI Fixes 8 子項 + tag 編輯 API |
| v2 | + 資料夾自動標籤（7 pytest）+ Append+De-dup 策略 |
| **v3（本次）** | **+ 全域 lowercase 標準化（`_normalize_tag()` 單一真理源）+ 6 pytest case 補強 + 4 點深度評估認證** |
