````markdown
# 2026-07-12 — GOV-PATH-FIX Check 提示詞

> **收到時間**：2026-07-12 21:55（UTC+8）
> **任務代號**：GOV-PATH-FIX Check
> **觸發 commit**：GOV-PATH-FIX-Check（Checkout 收官）
> **相關產出檔案**：.claude-logs/baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md + checkout 執行報告 + baton 歸檔
> **觸發情境**：熱修復執行完畢（fix commit `31f7500` 已落地），baron 下達 Conformance 驗收與 Checkout 收官歸檔指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-12 21:55 | 任務代號 | GOV-PATH-FIX Check | 觸發 Commit | GOV-PATH-FIX-Check |
| 相關產出檔案 | .claude-logs/baton/2026-07-12_GOV-PATH-FIX_stale_worktree_path_hotfix.md |
| 觸發情境 | 熱修復執行完畢，baron 下達 Conformance 驗收與 Checkout 收官歸檔指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成）
寫入 .claude-logs/prompts/2026-07-12_GOV-PATH-FIX_Check_提示詞.md + 更新 INDEX → 回覆「✅ 提示詞已歸檔」後繼續。

你現在扮演 Claude Code，對 GOV-PATH-FIX 執行 Conformance 驗收，全部合規後收官歸檔。

### Conformance 驗收
第一步交叉比對：目標規格（hotfix 規劃）/ 驗收條件（hotfix §5）/ 不可動（歷史檔不溯及既往）+ 特化維度：
1. 提示詞歸檔稽核（hotfix 執行 + Check 收官皆實體存在且 git add）
2. msg.txt 草稿完整性（規劃書 §8）
3. 跨 Commit 累加：100% 覆蓋 3 下游引用檔 stale 路徑、無業務碼改動
第二步：產 Conformance 驗收報告表格；全綠才續收官、不合規即中斷。

### 收官動作（全綠後）
1. TODO：🟡 進行中 條目 → ✅；底部 ## 索引（依類別）標 ✅；雙源 hash 審計（TODO 索引行 + archive/TODO_done_archive.md）回填 GOV-PATH-FIX-hotfix 真實 hash 替換「待 baron 回填」
2. mv baton hotfix 規劃書 → hotfixes/ + 顯式 git add（禁 git add .）
3. ls baton 確認本任務暫存清空（長駐檔不碰）
4. 檢查 prompts 歸檔 + INDEX 皆入 git，漏則 git add
5. commit 前 staged 自檢：git diff --cached --name-only 與宣告改動聯集逐項對比，多/少一檔即停
6. 產 executions/2026-07-12_GOV-PATH-FIX_checkout_執行.md（template_execution；含 Conformance 結果 + 第五步 staged 自檢輸出 + baton 歸檔確認）並 git add

### §8 baron 執行命令
msg 寫 /tmp/GOV-PATH-FIX_Checkout_msg.txt；git add TODO + hotfixes/hotfix + checkout 執行報告 + hotfix 提示詞 + Check 提示詞 + INDEX。

### 停止指令
完成 TODO 更新 + baton 歸檔 + checkout 執行報告後立即停止。嚴禁自發 git commit|push / 改已歸檔 executions/ / 改 hotfixes/ 已歸檔紀錄。
```

---

## 執行結果摘要

- ✅ Conformance 三維度全綠（3 下游檔 stale 路徑 100% 覆蓋·零業務碼·歷史檔不溯及既往）+ baton hotfix 規劃書 mv→hotfixes/ + TODO 結案（hash 自癒 `31f7500`）+ checkout 執行報告產出
- fix commit `31f7500` 已落地；本 checkout 為第二 commit（收官歸檔）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

GOV-PATH-FIX 全案結案（fix `31f7500` + checkout 待 baron 回填）。
````
