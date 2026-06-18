# === [PIPE-LITEDOC C2] ===
"""LiteDocPipeline 策略管線（PIPE 縱向五路第 3 路：news / web / unknown）。

`@PipelineFactory.register('litedoc'/'news'/'web')` 三 key 註冊；unknown doc_type 經 factory
`_FALLBACK_DOC_TYPE='litedoc'` 自動承接（SPEC §3.3 最後防線）。主幹（Orchestrator）零 doc_type 分支。

本路為 academic-lite：P1 MinerU+md_cleaner 文字攝入（非 Vision）、P2-P4 全消費已落地共用真理源
（`section_engine` / DomainNormalizer / GlossaryManager / Translator / rag_indexer），不重造機制。

C2 範圍：骨架與三 key 註冊——四 Phase 為 strict stub（拋 NotImplementedError）；
P1-P4 具體實作屬後續 C3-C6（plan U2-U6）。
"""

from __future__ import annotations

import logging

from pipelines.base_strategy import DocumentStrategy
from pipelines.context import PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory

# === [PIPE-LITEDOC C3 START] P1 攝入所需 ===
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import paper_manager
import settings
from processor.doc_analyzer import DocAnalyzer
from processor.json_processor import JsonProcessor
from processor.md_cleaner import MarkdownCleaner
from processor.md_processor import MarkdownProcessor
from processor.pdf_processor import PDFProcessor
from processor.tiling_processor import TilingProcessor
from processor import meta_normalizer
# === [PIPE-LITEDOC C3 END] ===

logger = logging.getLogger(__name__)

# === [PIPE-LITEDOC C3 START] 啟發式常數 + 原生 metadata cover-prompt（方案 A、不耦合 A 軌）===
_CJK_MIN = 20
_CJK_RATIO = 0.2
_META_INPUT_CHARS = 4000   # metadata 抽取只看文首（標題/作者/出處集中於此）

# B 軌原生文字 metadata 抽取（plan §2.5 方案 A）：含 URL→組織名解碼指引，輸出純 JSON。
_LITEDOC_META_SYSTEM_PROMPT = (
    "You are a document metadata extractor. Analyze the provided text from the beginning of a "
    "news article or web document and extract metadata as a JSON object.\n"
    "Fields: title (str), authors (list of str), date (str, e.g. 2026-06-19), "
    "publisher (str: news outlet / publishing organization), url (str if present).\n"
    "Rules:\n"
    "1. If a URL is present and the publisher is not explicitly stated, decode the publisher from the "
    "URL domain (e.g. cnn.com -> CNN, nytimes.com -> The New York Times).\n"
    "2. Missing fields: use \"\" for strings and [] for authors. Do NOT invent values.\n"
    "3. Return ONLY a valid JSON object with keys title, authors, date, publisher, url. "
    "No markdown fences, no commentary."
)


def _strip_json_fence(text: str) -> str:
    """剝除 LLM 輸出的 ```json ... ``` 圍欄（容錯、不耦合 A 軌）。"""
    s = (text or "").strip()
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()
# === [PIPE-LITEDOC C3 END] ===


@PipelineFactory.register("litedoc")
@PipelineFactory.register("news")
@PipelineFactory.register("web")
class LiteDocPipeline(DocumentStrategy):
    """第 3 路策略：news / web / unknown（fallback）。

    `rag_char_threshold=10`：litedoc 為長篇散文型、非 Vision 短文（slides/resume ≥3），
    走一般文檔門檻 ≥10（對齊 master plan v10 L183、rag_indexer `is_chunk_meaningful` 預設）。
    """

    rag_char_threshold: int = 10

    _STUB_MSG = (
        "LiteDocPipeline C2 骨架階段——四 Phase 具體實作屬 PIPE-LITEDOC C3-C6"
        "（P1 MinerU 攝入 / P2 六步 / P3 size-gate 翻譯 / P4 Async RAG）"
    )

    # === [PIPE-LITEDOC C3 START] P1 MinerU 攝入與 metadata 旁路 ===
    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：MinerU 文字攝入 + 原文元數據 + 物理分組 Tiles（合約①）。

        全鏈（plan U2/U3、消費既有 processor、零改）：
          ① pdf2md：PDFProcessor（MinerU）→ ② 強制 md_cleaner 清洗
          ③ analyze：DocAnalyzer（**U2.1 doc_type 映射**：news/web 原樣、其餘→'web' 扁平 prompt、
             防 doc_analyzer fallback academic 深層論文結構分析）
          ④⑤⑥ md2json → json_process → tiling → 物理分組 Tiles
          ⑦ B 軌原生文字 LLM 抽 metadata（含 URL→publisher 解碼）→ venue 承接 publisher、
             date/url/organization 走 ctx.raw_metadata 旁路（meta_normalizer 正規化欄名）。
        交付 IngestionMetadataSpec（🚫 零 Abstract/LCC/Glossary、零翻譯）。
        """
        if not ctx.pdf_path:
            raise ValueError("PIPE-LITEDOC P1：ctx.pdf_path 缺失，無法定位輸入 PDF")
        pdf_path = Path(ctx.pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PIPE-LITEDOC P1：PDF 不存在 {pdf_path}")

        output_dir = paper_manager.paper_dir(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        paper_name = pdf_path.stem

        # ① pdf2md：MinerU 文字解析（非 Vision）
        md_path = Path(PDFProcessor().parse(str(pdf_path), str(output_dir)))
        # ② 強制 md_cleaner（非 resume/slides 跳過；浮水印/純數字行清理）
        MarkdownCleaner().clean(md_path)
        markdown_text = md_path.read_text(encoding="utf-8")

        # ③ analyze：DocAnalyzer + U2.1 映射（soft-fail）
        analyzer_doc_type = ctx.doc_type if ctx.doc_type in ("news", "web") else "web"
        try:
            DocAnalyzer().analyze(md_path, analyzer_doc_type)
            markdown_text = md_path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 — analyze 失敗不阻斷 P1
            logger.warning(
                "[PIPE-LITEDOC P1] %s analyze 失敗（soft、doc_type=%s）: %s",
                ctx.paper_id, analyzer_doc_type, exc, exc_info=True,
            )

        # ④⑤⑥ md2json → json_process → tiling（產物理分組 Tiles）
        tiles = self._build_tiles(md_path, output_dir, paper_name, ctx.doc_type)

        # ⑦ metadata：B 軌原生文字抽取（方案 A）
        meta = self._extract_litedoc_metadata(markdown_text)
        title = self._resolve_title(meta, markdown_text, paper_name)
        source_lang = self._detect_source_lang(markdown_text)
        publisher = str(meta.get("publisher") or "").strip()

        if ctx.paper_id.endswith("_shadow"):
            title = f"{title} (測試)"

        # 旁路：合約無欄之 date/url/organization 走 ctx.raw_metadata（meta_normalizer 正規化欄名、
        # 旗標 LLM_USE_META_NORM；publisher 另由 venue 承接、不重複入旁路）。INFRA-4 後收合。
        raw_fields = {
            k: str(meta.get(k) or "").strip()
            for k in ("date", "url", "organization")
            if str(meta.get(k) or "").strip()
        }
        normalized = meta_normalizer.normalize_fields(raw_fields, context=title) if raw_fields else {}
        ctx.raw_metadata = {
            key: {"value": val, "source": "litedoc_p1", "confidence": "medium"}
            for key, val in normalized.items()
        }
        if publisher:
            ctx.raw_metadata["publisher"] = {
                "value": publisher, "source": "litedoc_p1", "confidence": "medium",
            }

        spec = IngestionMetadataSpec(
            title=title,
            authors=[str(a) for a in (meta.get("authors") or []) if str(a).strip()],
            venue=publisher or None,   # venue 承接 publisher（現成合約欄）
            doi=None,
            source_lang=source_lang,
            tiles=tiles,
        )
        logger.info(
            "[PIPE-LITEDOC P1] %s title=%r source_lang=%s tiles=%d publisher=%r authors=%d",
            ctx.paper_id, title, source_lang, len(tiles), publisher, len(spec.authors),
        )
        return spec

    # ── P1 私有輔助 ──
    def _build_tiles(
        self, md_path: Path, output_dir: Path, paper_name: str, doc_type: str
    ) -> List[Dict[str, Any]]:
        """md2json → json_process → TextTiling（litedoc 不 opt-out、news/web 短文跑 tiling 無妨）。"""
        structured = output_dir / f"{paper_name}_structured.json"
        MarkdownProcessor().process(str(md_path), str(structured))
        processed = output_dir / f"{paper_name}_processed.json"
        JsonProcessor().process(str(structured), str(processed))
        tiled = output_dir / f"{paper_name}_tiled.json"
        TilingProcessor().process(str(processed), str(tiled), doc_type=doc_type)
        return self._load_tiles(tiled)

    @staticmethod
    def _load_tiles(tiled_path: Path) -> List[Dict[str, Any]]:
        """讀 tiled JSON；dict→取 sections list、list→直接用；失敗回 []（soft）。"""
        try:
            data = json.loads(Path(tiled_path).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("[PIPE-LITEDOC P1] 讀取 tiled JSON 失敗（tiles=[]）: %s", exc, exc_info=True)
            return []
        if isinstance(data, dict):
            sections = data.get("sections")
            return sections if isinstance(sections, list) else [data]
        return data if isinstance(data, list) else []

    def _extract_litedoc_metadata(self, markdown_text: str) -> Dict[str, Any]:
        """B 軌原生文字 cover-prompt（方案 A）抽 title/authors/date/publisher/url + URL→組織解碼。

        soft-fail → 空 dict（不阻斷 P1）。temp=0 求確定性轉錄。
        """
        from llm.client import LLMClient  # 惰性 import 避免模組載入期重量級依賴

        head = (markdown_text or "")[:_META_INPUT_CHARS]
        if not head.strip():
            return {}
        messages = [
            {"role": "system", "content": _LITEDOC_META_SYSTEM_PROMPT},
            {"role": "user", "content": head},
        ]
        try:
            out = LLMClient.get_instance().chat(
                messages=messages, temperature=0.0, stream=False, model=settings.LLM_DOMAIN_MODEL,
            )
            data = json.loads(_strip_json_fence(out))
            return data if isinstance(data, dict) else {}
        except Exception as exc:  # noqa: BLE001 — 非致命：空 metadata、不阻斷
            logger.warning("[PIPE-LITEDOC P1] metadata 抽取失敗（soft、空）: %s", exc, exc_info=True)
            return {}

    def _resolve_title(
        self, meta: Dict[str, Any], markdown_text: str, paper_name: str
    ) -> str:
        """title = metadata.title → markdown 首個 # 行 → paper_name。"""
        t = str(meta.get("title") or "").strip()
        if t:
            return t
        for line in markdown_text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                return s.lstrip("#").strip() or paper_name
        return paper_name

    @staticmethod
    def _detect_source_lang(markdown_text: str) -> str:
        """source_lang 啟發式：CJK 顯著佔比 → 'zh'，否則 'en'。"""
        cjk = sum(1 for ch in markdown_text if "一" <= ch <= "鿿")
        letters = sum(1 for ch in markdown_text if ch.isascii() and ch.isalpha())
        if cjk >= _CJK_MIN and cjk >= letters * _CJK_RATIO:
            return "zh"
        return "en"
    # === [PIPE-LITEDOC C3 END] ===

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 Glossary & Context Prep（C4 實作）。"""
        raise NotImplementedError(self._STUB_MSG)

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 Translation & Restore（C5 實作）。"""
        raise NotImplementedError(self._STUB_MSG)

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 Async RAG（C6 實作）。"""
        raise NotImplementedError(self._STUB_MSG)
# === [PIPE-LITEDOC C2 END] ===
