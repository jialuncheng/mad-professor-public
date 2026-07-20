# LANG-DETECT review 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：LANG-DETECT（F4、cover-prompt +language 欄語言偵測）
- **階段**：plan review（v1 → v2 定稿）
- **來源**：baron 轉交外部 review 建議 + 四 OQ 拍板

---

## 提示詞原文（摘錄結論部；含完整代碼掃描過程）

> review 過程含：`run_phase1` L172 附近 meta 使用鏈實查、`_resolve_source_lang(meta, heuristic)` 簽名確認（heuristic＝`classify_source_lang` 回傳值）、`re` 已 import 確認（L90 `re.sub`）、`_LITEDOC_META_SYSTEM_PROMPT` 完整改後文本（Fields 增列 language + Rule 5 keys 清單同步）、白名單邊界枚舉（`IT`→lower 採信／`en-US` len 5 退 en／`Italian` len 7 退 en／`ita` ISO 639-2 三字碼**合法通過**／`zh`/`zho` 拒前綴／空值缺欄退 en）。

### 一、 架構與流程評估 (Architectural & Process Audit)

*   **設計高度安全，影響半徑極小**：「僅在啟發式判定為 `en` (catch-all) 時才採信白名單過濾後的 LLM `language`」是安全的最小信任轉移策略。CJK（繁中、簡中、日文、韓文）判定權威鎖死在 `section_engine.classify_source_lang` 本地端，免受 LLM 輸出波動與幻覺影響。
*   **HOTFIX-1 繁中 Bypass 閘門防護完美封鎖**：§2.2「非繁嚴禁 `zh*` token」以 `not lang.startswith("zh")` 於 producer 端強制攔截，截斷繞過 P3 `startswith("zh")` bypass 閘門的可能性。
*   **語言碼過濾之健壯度提醒**：`re.match(r"^[a-z]{2,3}$", lang)` 精準相容 ISO 639-1（`it`/`de`）與 **ISO 639-2（`ita`/`deu`）**，自動排除 `en-US`/`Italian` 等非標記 token 並降級退 `en`，與 `GlobalGlossary` 表相容。

### 二、 Open Questions 拍板方案 (OQ1 - OQ4)

| 問題 | 拍板方案 | 理由 |
|---|---|---|
| **Q1：LLM 採信範圍** | ✅ **僅啟發式 catch-all `en` 時採信。** | 拉丁語系全落入 `en` 是當前唯一的偵測破口；字元統計確定的 CJK/繁中判定不讓渡給 LLM，保障繁中 bypass 權威零動搖。 |
| **Q2：是否新增 env flag** | ✅ **不新增語言偵測開關。** | 語系合成邏輯已內建雙重安全網，缺欄或格式不符自動降級退回啟發式、與現行行為 100% 等價；不需 `LITEDOC_LANG_DETECT_ENABLED`，符合 YAGNI。 |
| **Q3：語言碼白名單** | ✅ **格式 `^[a-z]{2,3}$` 且拒 `zh` 前綴。** | 完整覆蓋標準 ISO 語言碼、排除多餘綴詞，並於 producer 端延伸強制 HOTFIX-1「非繁零 `zh*` token」限制。 |
| **Q4：既有 en 桶污染詞處理** | ✅ **不追溯清理。** | 本案聚焦攝入偵測層根治；測試期 DB 可重置清空，生產歷史詞條清理屬 GLOSSARY-UI 範疇、非本案前提。 |

---

## 備註

- review 判定：無結構性缺失、無新增規格項；`_resolve_source_lang(meta, heuristic)` 簽名與合成邏輯獲逐行確認。
- 一項實作確認回灌 plan §2.2：白名單 `^[a-z]{2,3}$` 相容 **ISO 639-2 三字碼**（`ita`/`deu` 合法通過、glossary 字串欄相容）——非行為變更、為規格明文化。
- 四 OQ 全數拍板採納 plan v1 推薦方案（無翻案）。
- 產出：plan v1 → v2 定稿（§2/§9/§99.2 對應更新）。
