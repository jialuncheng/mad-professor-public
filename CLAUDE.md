# Claude Code 啟動指引

> 💡 **規範引導（強制）**：每次 session 啟動時、Claude / Claude Code 必須優先閱讀並遵守
> `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` 中的進度控制與**提示詞歸檔規範（§6）**。
> 提示詞歸檔細節見 `.claude-logs/prompts/README.md`。

## 核心規範

1. **plan-execution 雙軌制**：plan 階段嚴禁動業務代碼、只 view / grep
2. **提示詞歸檔（框架 §6）**：先歸檔到 `.claude-logs/prompts/` → 再執行 → 同步 `INDEX.md`
   - 觸發條件：含命令動詞（請執行 / 撰寫 / 修正 / 建立）/ 長度 > 500 字 / 結構化區塊（═══ / ## 第X步）
   - 模糊時優先歸檔
   - 敏感資訊（API key / 密碼 / email / phone）打碼後再寫入
3. **不 commit / push**：auto-classifier 阻擋、由 baron 手動執行
4. **TODO 維護**：依框架 §2.5 任務生命週期、ship 後搬到 ✅ 區（不直接刪、改為刪除線）

## 工作目錄結構

```
.claude-logs/
├── ref/              # 規範文件（入版控、跨環境同步）
├── templates/        # plan / 執行 / hotfix 模板（入版控）
├── prompts/          # 提示詞資料庫（入版控、§6 規範強制歸檔）
├── TODO.md           # 不入版控、本機 SoT
├── *_plan.md         # 不入版控、本機規劃
├── *_執行.md         # 不入版控、本機執行報告
└── *_hotfix.md       # 不入版控、本機緊急修正
```
