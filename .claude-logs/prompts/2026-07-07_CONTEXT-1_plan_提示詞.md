# 2026-07-07 CONTEXT-1 plan 提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：plan（階段 1 規劃）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-07

---

## 原始提示詞（逐字）

> context_engineering_governance_audit.md
> 針對上面內容做一個plan
> baton/
>
> 依據
> template/template_plan.md
> ref/WORKFLOW_SOP.md
> ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
>
> 不用給commit建議

---

## 上下文（承接對話）

1. baron 給五篇 context engineering / agent 工程文獻（Anthropic effective-context-engineering、Anthropic Agent SDK、LangChain filesystems、Akita RAG-is-dead、HN 討論串），要求評估對本專案文件治理與開發流程之助益 → Claude 產出逐篇對照評估（TODO.md 73% 已完成考古 + `@baton/*.md` wildcard 全載＝context rot 病灶；六階段/baton/反例錨/golden 驗證體系被文獻反向驗證為正解）。
2. baron 要求做成稽核存檔（同 `frontend_css_governance_audit.md` 先例、不開 plan）→ Claude 產出 `baton/context_engineering_governance_audit.md`。
3. baron 自行增補後要求回源驗證 → Claude 修正三處文獻掛名（§2 四大失敗模式恢復文獻③原文四項、§3 刪 Manus 語彙、§8 caching 改標機制事實推導）+ Review 更新註記。
4. baron 詢問 CONTEXT-1 對 baton 的影響 → Claude 澄清：僅改 CLAUDE.md §0 載入行、零刪檔；並完成 baton 10 件暫存檔優先度盤點（A 級不可動 4 件 / B 級已收官殘留 3 件 / C 級待拍板稽核 3 件）。
5. 本提示詞：baron 拍板產 plan，落 baton/，依三份權威源，**不含 commit 建議**（tasks 階段才拆）。

## 產出

- `.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md`
