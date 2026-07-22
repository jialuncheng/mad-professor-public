# FITZ-HOTFIX-3 診斷與 plan 提示詞（2026-07-22）

> 性質：日文樣本 E2E 回饋 → 對話式診斷鏈 → hotfix 規劃落檔（依 §1.2「跟 plan 對應」歸檔）。
> 產出：`baton/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md`（template_hotfix）

---

## baron 指令鏈（逐條、時序）

1. 「原稿 ドジャース 大谷翔平 二刀流復帰戦で先頭打者HR 投げては4勝目.pdf／產出 A Track 道奇隊...v1／B Track 大谷翔平 (測試)_v1——B Track 整個 Meta 應該又是處理得蠻失敗的、分析原因、有需要測試機的 log 或資料直接給指令」——啟動診斷、給 Ohtani_v1 證據包搬運指令
2. 「讀 baton/litedoc_shadow_artifacts/Ohtani_v1」——四步對帳（P1 log title='大谷翔平' publisher='' authors=0／fitz md 無標題＋前 8 行空白／sidecar／A 軌對照含 `authors: Baron` 檔案屬性污染）
3. （丟三份 PDF 進 baton）——源 PDF 第一頁解剖 → **×4 同位重繪實測**（text-stroke 列印產物）→ md_cleaner 浮水印規則（≥3 全殺）誤殺定案；publisher 空＝R2 剝 chrome 丟掉唯一 URL 線索
4. 「把 FITZ-HOTFIX-3 規劃書落 baton／依據 template_hotfix + WORKFLOW_SOP + FRAMEWORK／詳細說明原因／程式碼也加入文件／包含 commit」——本檔落檔指令
5. 「review 下面建議…update plan」——外部 review 肯認；自查抓 K2 尾接截斷真 bug → v2
6. 「還會有其他類似的狀況嗎？」——族群掃描 → SpaceX v3 `shadow_en` 實證 en 側 meta 原文行洩漏（雙語文字不對稱）+ 3 觀察級
7. 「K3 併入 HOTFIX-3」——v3 三刀定稿（K3 行級 meta 歸零、接線於 echo-strip/R8 之前）

## 診斷要點

- 真因 A：NHK 描邊 ×4 → fitz 忠實抽 → 判 h1 ×8 行 → md_cleaner 浮水印（4≥3）全殺 → cover-prompt 撈 tag「大谷翔平」；A 軌活＝MinerU 自帶去重（1<3）；R2 不防＝跨頁 vs 同頁不同物種
- 真因 B：NHK 身份僅存 logo 圖 + 頁尾 URL chrome、R2 正確剝除順帶丟線索 → publisher=''
- 兩刀：K1 `_collect_page` 同位去重（(text,y0,x0,size) 同頁 key）／K2 chrome URL 回收 sidecar + cover-prompt 輸入 hint（md 零污染）
