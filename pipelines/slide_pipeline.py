"""SlidePipeline —— 簡報（slides）策略管線（PIPE 縱向五路絞殺第 2 路、PIPE-SLIDES）。

`@PipelineFactory.register('slides')` 註冊；主幹（Orchestrator）零 doc_type 分支、
僅透過 DocumentStrategy 四方法合約呼叫本策略。

四 Phase 規格（PIPE-SLIDES plan v1〔v1.1〕U1-U11；後續 commit 逐步落地）：
- P1 Ingestion（C2）：每頁整頁存圖（fitz get_pixmap、自建不耦合 A 軌 slides_processor）
  + Vision 忠實轉錄（SPEC §1.3.1：LLM_VISION_TEMPERATURE=0）+ 條件式滾動（預設關）
  + 封面判定（title fallback 檔名、簡報欄走 ctx.raw_metadata 旁路）+ 跨頁統計去重（排除封面）。
- P2 Glossary & Context Prep（C3）：統一六步（section=頁；① 順產 raw_domain、
  ② 順產缺失頁標題；key＝p{頁序}_{原文頁標題}——三方同基準、根除重複標題覆蓋）。
- P3 Translation & Restore（C4）：逐頁並行翻譯（RESUME-PERF-1 範式）+ 圖片 alt 對齊
  （雙 Caption 物理根除、MD-RESTORE slides 部分）+ ctx.rag_sections 旁路 + zh 來源 path
  + 退化 fallback；不渲染 meta header。
- P4 Async RAG（C5）：rag_indexer 共用真理源（四產物、零 A 軌依賴）。

C1（本檔現階段）僅交付：註冊 + 四方法合約 stub + rag_char_threshold=3（U11、
保 'SiC'/'THD' 級短關鍵詞）。strict 合約：未落地 Phase 拋 NotImplementedError、
由 Orchestrator 對齊 NullStrategy 行為攔截（影子 B 軌、線上 0 風險）。
"""
import json
import logging
import re
from pathlib import Path

from pipelines.base_strategy import DocumentStrategy
from pipelines.context import PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory

logger = logging.getLogger(__name__)

# === [PIPE-SLIDES C2 START] P1 常數 ===
# source_lang 啟發式門檻（鏡像 resume：CJK 顯著佔比 → 原文判為中文）。
_CJK_MIN = 20
_CJK_RATIO = 0.2
# Q2 跨頁統計去重：短行（≤20 字）出現於 ≥60% 非封面頁 → 判頁眉頁腳剔除。
_DEDUPE_MAX_LEN = 20
_DEDUPE_PAGE_RATIO = 0.6
# Q1 條件式滾動觸發：頁標題含延續標記、或前頁表格截斷（前頁尾/當頁首皆為 '|' 行）。
_ROLLING_MARKERS = ("(續)", "（續）", "cont'd", "continued")

# Vision 忠實轉錄 prompt（SPEC §1.3.1 鐵律 + U9 cell 禁標題語法）。
_VISION_PROMPT = """你是簡報忠實轉錄器。請將這一頁簡報的內容忠實轉錄為 JSON，嚴格遵守：
1. 嚴禁重組、摘要、補完或改寫——只忠實轉錄頁面上實際出現的文字與結構。
2. markdown_content 用 markdown 保留階層/條列/表格；表格儲存格（cell）內嚴禁使用 ### 等標題語法。
3. 圖表/示意圖/照片：用一兩句話描述放 figure_description 欄，嚴禁混入 markdown_content。
4. 頁面有明確標題放 title；沒有就空字串。
只輸出 JSON：
{"title": "", "markdown_content": "", "figure_description": ""}"""

# 第 1 頁追加封面判定欄（U2）。
_COVER_PROMPT = _VISION_PROMPT + """
此外這是文件第一頁，請追加判定它是否為「封面頁」（標題頁：大標題+作者/公司/日期、無正文內容）：
{"title": "", "markdown_content": "", "figure_description": "", "is_cover": true|false,
 "cover": {"title": "", "company": "", "date": "", "authors": []}}
非封面時 is_cover=false 且 cover 各欄空。"""
# === [PIPE-SLIDES C2 END] ===


@PipelineFactory.register('slides')
class SlidePipeline(DocumentStrategy):
    """簡報策略：Vision 每頁解析、逐頁翻譯、頁級 RAG。"""

    # U11：Vision 短文檔門檻放寬（保 'SiC'/'THD'/'LLC' 級短技術詞；資料庫 SOP ≥3 先例同 resume）
    rag_char_threshold: int = 3

    # === [PIPE-SLIDES C2 START] P1 Vision Ingestion（U1-U4）===
    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：每頁存圖 + Vision 轉錄（temp=0、條件滾動）+ 封面判定 + 統計去重。

        零 A 軌依賴（演算法參照 slides_processor 渲染/裁切/空白跳過、自建）；
        零衍生語境（無 Abstract/LCC/Glossary/翻譯/Embedding）。
        """
        import paper_manager
        import settings

        if not ctx.pdf_path:
            raise ValueError("SlidePipeline.run_phase1 需要 ctx.pdf_path")

        output_dir = Path(paper_manager.paper_dir(
            settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id))
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # ① 渲染（每頁/裁切單位 → jpeg bytes）
        page_images = self._render_pages(ctx.pdf_path)
        logger.info("[PIPE-SLIDES P1] %s 渲染 %d 個頁面單位", ctx.paper_id, len(page_images))

        # ② Vision 並行轉錄（Q1 預設關滾動 → 各單位獨立；第 1 單位帶封面判定）
        from concurrent.futures import ThreadPoolExecutor
        results: list = [None] * len(page_images)
        with ThreadPoolExecutor(max_workers=settings.LLM_MAX_CONCURRENT) as ex:
            futs = {
                ex.submit(self._transcribe_page, img, i == 0, None): i
                for i, img in enumerate(page_images)
            }
            for fut, i in futs.items():
                results[i] = fut.result()

        # ③ Q1 條件式滾動補救：偵測延續標記/表格截斷 → 該頁注入前頁重轉錄（序列、少量）
        for i in range(1, len(results)):
            if self._needs_rolling(results[i - 1], results[i]):
                prev_text = (results[i - 1] or {}).get("markdown_content", "")
                logger.info("[PIPE-SLIDES P1] 頁面單位 %d 觸發滾動重轉錄（注入前頁）", i + 1)
                results[i] = self._transcribe_page(page_images[i], False, prev_text)

        # ④ 空白單位跳過 + 存圖（僅保留單位、檔名=頁序）
        units = []
        for img, r in zip(page_images, results):
            if not r:
                continue
            if not (r.get("title") or r.get("markdown_content")
                    or r.get("figure_description")):
                continue  # 空白頁跳過（A 軌同款）
            n = len(units) + 1
            img_file = f"page-{n:02d}.jpg"
            (images_dir / img_file).write_bytes(img)
            units.append({
                "page": n,
                "title": (r.get("title") or "").strip(),
                "content": (r.get("markdown_content") or "").strip(),
                "figure_description": (r.get("figure_description") or "").strip(),
                "image_file": f"images/{img_file}",
                "is_cover": bool(r.get("is_cover")) and n == 1,
            })

        # ⑤ U2 封面判定 → title / raw_metadata 旁路；非封面 → title fallback 檔名
        title = Path(ctx.pdf_path).stem
        authors: list = []
        if units and units[0]["is_cover"]:
            cover = (results[0] or {}).get("cover") or {}
            if (cover.get("title") or "").strip():
                title = cover["title"].strip()
            authors = [a for a in (cover.get("authors") or []) if isinstance(a, str) and a.strip()]
            ctx.raw_metadata.update({
                k: v for k, v in (
                    ("company", (cover.get("company") or "").strip()),
                    ("date", (cover.get("date") or "").strip()),
                ) if v
            })
        else:
            logger.info("[PIPE-SLIDES P1] %s 無封面、title fallback 檔名", ctx.paper_id)

        # ⑥ U3 跨頁統計去重（排除封面）
        self._dedupe_headers(units)

        # ⑦ source_lang 啟發式（鏡像 resume）+ 影子標題後綴
        all_text = "\n".join(u["content"] for u in units)
        source_lang = self._detect_source_lang(all_text)
        if ctx.paper_id.endswith("_shadow"):
            title = f"{title} (測試)"

        logger.info(
            "[PIPE-SLIDES P1] %s title=%r source_lang=%s units=%d cover=%s",
            ctx.paper_id, title, source_lang, len(units),
            bool(units and units[0]["is_cover"]),
        )
        return IngestionMetadataSpec(
            title=title, authors=authors, source_lang=source_lang, tiles=units,
        )

    # ── P1 私有群 ──
    @staticmethod
    def _render_pages(pdf_path: str) -> list:
        """fitz 逐頁渲染 jpeg bytes（2x、直向 A4 上下裁半、橫向整頁——參照 A 軌、自建）。"""
        import fitz  # 惰性 import
        out = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                rect = page.rect
                mat = fitz.Matrix(2.0, 2.0)
                if rect.width < rect.height * 0.8:   # 直向 → 上下裁半
                    mid = rect.height / 2
                    clips = [fitz.Rect(0, 0, rect.width, mid),
                             fitz.Rect(0, mid, rect.width, rect.height)]
                else:                                 # 橫向 → 整頁一張
                    clips = [rect]
                for clip in clips:
                    out.append(page.get_pixmap(matrix=mat, clip=clip).tobytes("jpeg"))
        return out

    @staticmethod
    def _transcribe_page(img_bytes: bytes, is_first: bool, prev_text) -> dict:
        """單頁 Vision 忠實轉錄（§1.3.1：temperature=LLM_VISION_TEMPERATURE）。

        prev_text 非 None ＝滾動模式（注入前頁內容保跨頁連貫）。解析失敗回 {}（該單位跳過）。
        """
        import settings
        from llm.client import LLMClient
        prompt = _COVER_PROMPT if is_first else _VISION_PROMPT
        if prev_text:
            prompt += f"\n\n（上一頁內容、僅供跨頁延續對齊、勿重複轉錄）：\n{prev_text[:2000]}"
        try:
            out = LLMClient.get_instance().chat_with_images(
                messages=[{"role": "user", "content": prompt}],
                images=[(img_bytes, "image/jpeg")],
                temperature=settings.LLM_VISION_TEMPERATURE,
            )
            m = re.search(r"\{.*\}", out or "", re.DOTALL)
            return json.loads(m.group(0)) if m else {}
        except Exception as e:  # 非致命：壞頁跳過、不阻整份
            logger.warning("[PIPE-SLIDES P1] Vision 轉錄失敗（單位跳過）: %s", e)
            return {}

    @staticmethod
    def _needs_rolling(prev: dict, cur: dict) -> bool:
        """Q1 滾動觸發：當頁標題含延續標記、或前頁尾/當頁首皆為表格列（截斷）。"""
        if not prev or not cur:
            return False
        title = (cur.get("title") or "").lower()
        if any(mk in title for mk in _ROLLING_MARKERS):
            return True
        prev_lines = [ln for ln in (prev.get("markdown_content") or "").splitlines() if ln.strip()]
        cur_lines = [ln for ln in (cur.get("markdown_content") or "").splitlines() if ln.strip()]
        return bool(prev_lines and cur_lines
                    and prev_lines[-1].lstrip().startswith("|")
                    and cur_lines[0].lstrip().startswith("|"))

    @staticmethod
    def _dedupe_headers(units: list) -> None:
        """Q2 跨頁統計去重：短行（≤_DEDUPE_MAX_LEN 字）出現於 ≥60% 非封面頁 → 全數剔除。

        統計與剔除均排除封面頁（封面公司名＝metadata 非雜訊）；剔除清單入 log 供審計。
        """
        body = [u for u in units if not u["is_cover"]]
        if len(body) < 3:   # 頁數過少、統計無意義
            return
        from collections import Counter
        counts = Counter()
        for u in body:
            seen = {ln.strip() for ln in u["content"].splitlines()
                    if ln.strip() and len(ln.strip()) <= _DEDUPE_MAX_LEN}
            counts.update(seen)
        noise = {ln for ln, c in counts.items() if c / len(body) >= _DEDUPE_PAGE_RATIO}
        if not noise:
            return
        logger.info("[PIPE-SLIDES P1] 統計去重剔除 %d 短行: %s", len(noise), sorted(noise))
        for u in body:
            u["content"] = "\n".join(
                ln for ln in u["content"].splitlines() if ln.strip() not in noise)

    @staticmethod
    def _detect_source_lang(text: str) -> str:
        """CJK 顯著佔比 → zh（鏡像 resume 啟發式）。"""
        cjk = len(re.findall(r"[一-鿿]", text or ""))
        total = len(re.findall(r"\S", text or "")) or 1
        return "zh" if (cjk >= _CJK_MIN and cjk / total >= _CJK_RATIO) else "en"
    # === [PIPE-SLIDES C2 END] ===

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 統一六步（section=頁、key=p{N}_{原文頁標題}）（C3 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase2 於 PIPE-SLIDES C3 落地")

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 逐頁翻譯 + alt 對齊還原 + rag_sections 旁路（C4 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase3 於 PIPE-SLIDES C4 落地")

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 rag_indexer 共用真理源接線（C5 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase4 於 PIPE-SLIDES C5 落地")
