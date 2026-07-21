# PIPE-SYNC-5 review 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-SYNC-5（PIPE-INGEST＋GLOSSARY-TERMMAP 回灌母 plan v10→v11、PIPE-SPEC v8→v9、含 F7 門檻更正）
- **階段**：plan review（v1 → v2 定稿）
- **來源**：baron 轉交外部 review 建議 + 五 OQ 拍板

---

## 提示詞原文（結論部）

### 一、 架構與流程評估 (Architectural & Process Audit)

*   **回灌決策非常合理且必要**：修正「已落地程式碼契約」與「早期治理文件」之 doc-drift 落差，防範後續任務（PIPE-ACADEMIC 等）依賴偏置。
*   **就地補註與 Revision 策略成熟**：沿 PIPE-SYNC-2/3/4 之 `<!-- [PIPE-SYNC-5 Dn] -->` 就地 HTML 註解、不 bump 檔名、加 Revision，實證為「零變動四凍結合約結構」最安全方案。
*   **F7 門檻更正防誤導**：主動更正 design_spec 作廢門檻（廢長邊軸、修 `area < 100000`），避免重踩「481×369 圖表誤殺」坑。

### 二、 Open Questions 拍板方案 (OQ1 - OQ5)

| 問題 | 拍板方案 | 理由 |
|---|---|---|
| **Q1：是否納入 FITZ / LANG-DETECT** | ✅ **不納入，留待 PIPE-SYNC-6。** | 單一職責與原子增量；FITZ/LANG-DETECT 剛落地、契約獨立；分批回灌避免 commit 膨脹與檢索失焦。 |
| **Q2：母 plan 版本標號碰撞處理** | ✅ **沿 PIPE-SYNC-4 範式，不 bump 檔名，僅加 Revision 一行與就地補註。** | 歷史編號碰撞依 SOP 不溯及；v10 屬批次標籤非嚴格 SemVer，保原名助歷史 trace。 |
| **Q3：`ingestion_engine` 契約章編號** | ✅ **獨立 §1.2.6（家族第 6 員、與 section_engine 平級）。** | 攝入組裝與 section 機制職責正交、平級並列最符 SPEC 模組化結構，便於後續管線單獨引用。 |
| **Q4：IMG-FILTER 是否需獨立 SPEC 章** | ✅ **不需要。** | 契約面僅為 `ingestion_engine.assemble` 之 `figure_filter` 注入參數（已併入 D1）；三規則門檻屬實作常數、不應膨脹介面規格書。 |
| **Q5：`build_termmap` 回灌落點** | ✅ **§1.2.2 GLOSSARY-CORE 內新增一段「事前定案 builder」。** | 事前定案是自癒演算法自然演進（取代舊收割法）、內聚同章保脈絡完整、防碎片化。 |

---

## 備註

- review 判定：無結構性缺失、無新增規格項；回灌決策/就地補註策略/F7 更正三點獲肯認。
- 五 OQ 全數拍板採納 plan v1 推薦方案（無翻案、無新增回灌項）。
- 產出：plan v1 → v2 定稿（§9 OQ 標拍板 + §99.2 v2；§1–§8 規格本體無異動）。
