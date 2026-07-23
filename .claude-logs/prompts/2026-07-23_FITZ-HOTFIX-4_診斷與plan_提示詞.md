# FITZ-HOTFIX-4 診斷與 plan 提示詞（2026-07-23）

> 性質：兩樣本 E2E 回饋 → 對話式診斷鏈 → 設計定調 → hotfix 規劃落檔（依 §1.2 歸檔）。
> 產出：`baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md`（template_hotfix）

---

## baron 指令鏈（逐條、時序）

1. 「檢查 B Track 道奇大谷…v3、近乎完美只剩第一張圖被丟棄、其他你跟後面翻譯比對是不是都沒缺」——29/29 完整性比對全勝；首圖鎖定規則③（1280×720、①②無罪）
2. （log 貼證）`DROP 規則③ page_0_9` 定讞——要 sidecar_v3 → 行界理論值 6、圖在行 8「不該中」的矛盾
3. （sidecar_v3／md_v3／processed_v3／final_zh・en_v3／tiled_v3 逐檔搬證）——en 側定讞＝**R8 以 sidecar 原封行號掃 K3 位移後 text**（行號基準位移家族第五例）；zh 側本地重演全放行、列追蹤項 C
4. 「原稿 How modern browsers work…B Track 現代瀏覽器…翻譯過後資料完全不對大幅缺失」——95% 蒸發案：管線無罪（final_zh 22 標題 35,863 字完整）、死因＝裸 `<script>` 吞文＋消毒移除；列印稿斷詞「處理」＝鐵證；途中自查更正兩輪 grep 假訊號（`-E` 配 `\|` 壞語法／`head -16` 截斷）
5. 「專案屬性就是處理 PDF、碰到 HTML 標籤應該就要當一般文字處理」——**K1 設計定調**（原則級授權）
6. 「針對以上內容做一個 hotfix 文件、baton/、依 template_hotfix + WORKFLOW_SOP + FRAMEWORK、詳細說明原因、程式碼也加入文件、包含 commit」——本檔落檔指令

## 診斷要點

- K1：fitz 文字層抽取使 Medium inline-code 樣式蒸發 → 裸角括號 → 前端 HTML 解析把 `<script>` 後文全吞進 script、DOMPurify 連內文移除；`<link>`/`<img>` 靜默拔除之洞列印稿可見。修法＝P1 清洗步包反引號（還原 inline-code 樣貌、行數不變式、反引號守衛、扉頁 div 下游注入天然豁免）
- K2：報頭集改「原封基準」單一源——P3 進場（K3 前）預算、傳參給 R8；`_load_header_srcs` 本體零改、簽名純加法
- 追蹤項 C：Ohtani zh 側首圖、待兩條 log 定讞
