# FITZ-HOTFIX-1 診斷與 plan 提示詞（2026-07-21）

> 性質：對話式診斷鏈（非單發結構化提示詞）；依 §1.2「跟 plan 對應」歸檔。
> 產出：`baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_plan.md`

---

## baron 指令鏈（逐條、時序）

1. 「新的 litedoc 產出結果 `地球是人類的搖籃，而你不能永遠待在搖籃裡。(測試) (測試)_v2.pdf` 還是有問題：標題錯／前面的小圖沒有被處理掉」
2. （附截圖 Snipaste_2026-07-21_19-47-26）「SpaceX & the Sentient Sun／Earth is the cradle.../MARC ANDREESSEN.../JUN 15, 2026 這幾段字都是打開 PDF 就直接可以選的、應該不是圖片」——推翻初判 title-as-image、導向 band 誤殺真因
3. 「Working Back from the Future／The Idiot Index.../The Constellation／The World SpaceX Enables／The Industrial Moon／Compute in the Sky／Mars——文件是有標題的、字體大小明顯不一樣、你解析一下」——導向字級三層階梯 + 圖表黏字搶位診斷
4. 「`America | Tech | Opinion | Culture | Charts` 這一段有可能處理掉嗎？儘量用通則、而不是個案」——導向 link-tiling 規則（R5）
5. （附截圖 Snipaste_2026-07-21_20-18-19）「MARC ANDREESSEN.../JUN 15 這個都出現兩次；53 82 Share 這個為什麼會被放進去」——導向 meta 值比對歸零（R6）+ 數字為主短行（R7）
6. （附截圖 Snipaste_2026-07-21_20-28-50）「如果數字為主短行成立、like 的數字 561 為什麼不會被抓進來？我確認過 like 的數字 561 也是文字」——導向 block 分組運氣診斷（R7 設計依據）
7. 「規劃書落 baton」——本 plan 落檔指令

## 診斷過程要點（session 內實測）

- 本地真跑 FitzProcessor 直抽源 PDF 複現缺陷；成品 PDF fitz 解剖對帳
- 源 PDF 全 23 頁：band 重複 key 字級分布／字級→字元量分布／7 標題座標／圖框內文字判定／link 覆蓋率掃描／block 分組
- 小圖未濾判定為 .202 環境問題（本機同碼複現 filter 有效）、不入刀單
