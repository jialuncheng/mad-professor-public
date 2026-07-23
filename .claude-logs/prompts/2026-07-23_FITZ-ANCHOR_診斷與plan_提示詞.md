# FITZ-ANCHOR 診斷與 plan 提示詞（2026-07-23）

> 性質：HOTFIX-3 落地後 E2E 仍敗 → 深挖診斷 → baron 架構轉向拍板 → 正式 plan 落檔（依 §1.2 歸檔）。
> 產出：`baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`（template_plan、BE-Refactor、無 commit 建議）

---

## baron 指令鏈（逐條、時序）

1. 「失敗、讀 大谷翔平 (測試)_v2.pdf」——v2 對帳：K2 成功（NHK）/K3 成功（meta 零重播）/K1 敗
2. （貼 log）——鐵證：標題 `(3 次)`＝精確 key 收 4→3 卡死閾值；6 個 section 標題 `(4 次)` 一份未收
3. 「大リーグ…這段被吃掉了／這段翻譯濃縮了好幾段／你做逐段翻譯跟格式比對、整份亂七八糟、圖文位置不對」——逐段對照表（lede 被 echo 子字串誤吃〔K3 連鎖〕/「史上初」段被 R2 誤殺剩孤兒/QA Q×4 A×1 攪爛/圖文錯位屬次生）
4. 「你確定這樣改會變好嗎？還有後面的 QA 也是亂七八糟」——scratchpad 子類覆寫離線模擬 K1′+K2′ → before/after 表（標題+section 樹+14 組 QA 全復活）
5. 「我覺得 FITZ 的效果很差、有沒有可能改流程：進 FITZ 前跑一次 LLM 協助判斷 Meta、跟 FITZ 資料比對；litedoc 丟第一頁最多第二頁」——**架構轉向拍板**：重要性判斷交 LLM、fitz 回歸抽文字+清垃圾
6. 「針對上面內容做一個 plan、baton/、依據 template_plan + WORKFLOW_SOP + FRAMEWORK + 上層規劃文件、不用給 commit 建議、把原來的 hotfix 改掉」——本 plan 落檔指令

## 診斷要點

- 病史定性：三輪 hotfix 失手全屬「猜錯重要性」類、除噪類零失手 → 結構性反轉（錨定）而非第四輪打地鼠
- 零新增呼叫之關鍵：既有 cover-prompt **換輸入**（受損 md 文首 → 前 1-2 頁裸文字層）；chrome URL 天然在內 → HOTFIX-3 K2 sidecar 管線退場
- 標題回注 promote-else-inject ＝與哪把刀誤殺無關的終局保底；K1′/K2′ 仍需（QA/section 結構屬正文幾何、錨定不覆蓋）
