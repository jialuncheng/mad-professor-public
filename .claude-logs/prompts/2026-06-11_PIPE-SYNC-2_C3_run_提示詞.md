# PIPE-SYNC-2 C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 02:05 |
| 任務代號 | PIPE-SYNC-2 C3 |
| 觸發 Commit | C3 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SYNC-2_..._tasks.md` |
| 觸發情境 | baron 確認 C2 後，下達 C3 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SYNC-2 / C3 — SOP Fix & Archive / DOC-Refactor；tasks §8 C3

### 執行命令（tasks §8 C3）
① 改前備份四檔 → archive/2026-06-11_PIPE-SYNC-2_C3_*.bak（model_recommendations / google_latest_models_guide / doc_type v3 / mineru_SOP）
② U11：model_recommendations.md L20 EMBEDDING_MODEL 建議值 gemini-embedding-2→gemini-embedding-001 + 理由（假批次/無 task_type/MODEL-11）；L19 EXTRA_INFO 行尾註「extra_info stage B 軌已廢、僅 A 軌影子期沿用」
③ U12：google_latest_models_guide.md 頂部勘誤 banner（embedding-2 與 MODEL-11 實測矛盾；文字 embedding 一律 -001）、內文不動
④ U13：doc_type v3 頂部適用範圍 banner（A 軌專用；B 軌＝PipelineFactory.register+四方法、見 PIPE-SPEC §1.3）+ v1/v2 mv → archive/
⑤ U14：mineru_SOP §6 補 RELEASE_ON_UPLOAD 配套句（上傳 app 端全清向量快取+gc 騰 RAM、env 可關、活躍 SSE 豁免）
- 物理防線：僅四 SOP 檔更正 + 舊手冊歸檔；嚴禁動代碼、嚴禁重寫 U12/U13 內文

### TODO 同步
- C3 ✅、C4 🟡 WIP；git log 自癒回填

### 產出
- 執行報告 baton/2026-06-11_PIPE-SYNC-2_C3_執行.md（暫存、不入版控）；§5 貼 §6.3 五條 grep

### §8 baron 命令
- git add：四 sop 檔 + archive renames + 4 .bak + 2 prompts + TODO（嚴禁 baton 文件）；msg → /tmp/PIPE-SYNC-2_C3_msg.txt

### 停止
- 產出 C3_執行.md 後立即停止；不續 C4、不自發 commit/push
