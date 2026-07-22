# FITZ-HOTFIX-2 診斷與 plan 提示詞（2026-07-22）

> 性質：E2E 回饋 → 對話式診斷鏈 → plan 落檔（依 §1.2「跟 plan 對應」歸檔）。
> 產出：`baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md`（初以 template_plan 落檔、baron 更正後改套 **template_hotfix**、原 _plan.md 已刪）

---

## baron 指令鏈（逐條、時序）

1. 「SpaceX 與有知覺的太陽 (測試)_v3.pdf／SpaceX 與有意識的太陽_v3.pdf——E2E 的結果、B Track 有一張大圖不見了、其他你跟原稿比對」——啟動 E2E 比對（文字面八刀全勝；缺圖鎖定 hero 1456×1442 + 500×333）
2. 「需要我再把測試機的資料或 log 搬回來放在 baton 做深入的分析嗎？」——同意搬證據（四樣：img-filter log／新 sidecar／雙語 final md／fitz md+processed）
3. （貼指令報錯）placeholder 修正 → 免改直貼版命令
4. 「讀 baton/litedoc_shadow_artifacts」——四預言對帳（log ③×5 vs R8 ①×3／hdr_end=119／en21 vs zh19／tiles 19）
5. 「甲、乙都看不懂」——版面圖白話重講（唯一差別＝封面大圖去留）
6. （附截圖 Snipaste_2026-07-22_14-25-09＝封面大圖本尊）「我一直提出的不就是這張圖嗎？不然還有哪張圖？」——確認 hero 身份 + 出示第二張缺圖（Falcon 9 降落駁船照片）
7. 「就定甲」——banner 保留拍板、本 plan 落檔指令

## 診斷要點（session 內實測）

- 真因：規則③ hdr_end＝max(end) over 全部判型 blocks、DocAnalyzer 判型至 line 119 → 行界涵蓋前 1/3 篇
- 伴生：R8 未傳 header_srcs → 規則③只殺 zh/tiles 路 → 雙語不對稱（en21/zh19）
- 甲案模擬（真 sidecar）：hdr_end 119→10、兩張圖獲救、垃圾①②兜底照殺
