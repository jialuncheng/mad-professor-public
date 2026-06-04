"""PIPE-RESUME ResumePipeline 策略管線（plan_v1、PIPE 縱向五路絞殺第 1 路）。

Resume（履歷）文體的四 Phase 策略插件，繼承 PIPE-CORE `DocumentStrategy`，以
`@PipelineFactory.register('resume')` 註冊；主幹（Orchestrator）零 doc_type 分支、
僅以 `PipelineFactory.get_strategy('resume')` 取得本策略。

四 Phase 對映落地 ABC 抽象方法：
- run_phase1 → IngestionMetadataSpec（P1 Vision 整份解析 + 原文元數據 + 物理分組 Tiles）
- run_phase2 → GlossaryReadySpec（P2 LCC 分類 / 摘要 / Glossary 自癒 / 摘要翻譯）
- run_phase3 → BilingualMarkdownSpec（P3 100% Bypass 翻譯與還原）
- run_phase4 → RagDbSpec（P4 非同步 RAG、門檻 ≥3 技能詞保護）

交付歷程：
- C1（策略骨架與工廠註冊）：註冊插件 + 四方法 stub。
- C2（P1 Ingestion）：實作 run_phase1——全鏈編排 ResumeProcessor（Vision md）+ Metadata
  Stage A + doc_analyzer 雙保險 + md2json/json_process/tiling（產 Tiles），交付
  IngestionMetadataSpec（零 Abstract/LCC/Glossary）。
- C3/C4/C5：P2/P3/P4 實作。

> custom_metadata 硬前置（tasks §9）：P1 履歷專屬欄 phone/email/domain 於凍結合約
> `IngestionMetadataSpec`（extra="forbid"）尚未具備落點前，暫存於本策略實例
> `self._raw_meta` 穿線給 P2；正式接線待上游擴 custom_metadata 後另行授權。
> phone/email 既有 metadata_extractor 無對應欄，C2 以 markdown regex 自足抽取（不動既有檔）。
"""

# === [PIPE-RESUME C1 START] ===
from __future__ import annotations

import logging
from typing import Any, Dict

from pipelines.base_strategy import DocumentStrategy
from pipelines.context import PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory

# === [PIPE-RESUME C2 START] P1 全鏈編排所需既有模組（複用、零改動）===
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple

import paper_manager
import settings
from processor.doc_analyzer import DocAnalyzer
from processor.json_processor import JsonProcessor
from processor.md_processor import MarkdownProcessor
from processor.metadata_extractor import (
    create_empty_metadata,
    extract_metadata_from_first_page_llm,
    extract_pdf_metadata,
    fill_from_llm_page1,
    fill_from_pdf_metadata,
    merge_stage_a,
)
from processor.resume_processor import ResumeProcessor
from processor.tiling_processor import TilingProcessor
# === [PIPE-RESUME C2 END] ===

logger = logging.getLogger(__name__)

# C2-C5 各 Phase 實作前的統一佔位訊息（明示尚未落地之 Phase）。
_NOT_IMPLEMENTED_MSG = (
    "ResumePipeline.{phase} 尚未實作（PIPE-RESUME {commit}）；"
    "本 Commit 僅交付既有 Phase。"
)

# === [PIPE-RESUME C2 START] P1 欄位抽取常數 ===
# Email / 電話 regex（自 Vision markdown 抽取；既有 metadata_extractor 無 phone/email 欄）。
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\-\s()]{6,}\d")
# source_lang 啟發式門檻（CJK 顯著佔比 → 原文判為中文）。
_CJK_MIN = 20
_CJK_RATIO = 0.2
# === [PIPE-RESUME C2 END] ===


@PipelineFactory.register("resume")
class ResumePipeline(DocumentStrategy):
    """Resume 文體四 Phase 策略（C1 骨架 + C2 P1；P2-P4 待 C3-C5）。"""

    # SPEC §3.1：Vision 短文檔（resume/slides）RAG 入庫字數門檻放寬至 3（保 Python/Docker 等技能詞）。
    rag_char_threshold: int = 3

    def __init__(self) -> None:
        # interim 穿線容器（tasks §9 硬前置）：P1 抽出的 phone/email/domain 暫存於此，
        # 供 P2 消費 domain 餵 normalize_to_lcc；待 custom_metadata 正式入合約後改走合約欄。
        self._raw_meta: Dict[str, Any] = {}

    # === [PIPE-RESUME C2 START] P1 Ingestion 全鏈編排 ===
    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：Vision 整份解析 + 原文元數據 + 物理分組 Tiles（合約①）。

        全鏈編排（忠實 PIPE-SPEC §1.1①，複用既有 processor、零改動）：
          ① Metadata Stage A（fitz + LLM 第一頁、soft-fail）→ 原文 Title/candidate_name/domain
          ② pdf2md：ResumeProcessor Vision 整份解析（resume 跳過 md_cleaner）
          ③ analyze：doc_analyzer 雙保險 heading fix（baron Q6）
          ④ md2json → ⑤ json_process → ⑥ tiling → 物理分組 Tiles
        交付 IngestionMetadataSpec（🚫 零 Abstract/LCC/Glossary、零翻譯）。
        phone/email/domain 暫存 self._raw_meta（custom_metadata 硬前置、tasks §9）。
        """
        if not ctx.pdf_path:
            raise ValueError("PIPE-RESUME P1：ctx.pdf_path 缺失，無法定位輸入 PDF")
        pdf_path = Path(ctx.pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PIPE-RESUME P1：PDF 不存在 {pdf_path}")

        # per-paper 輸出目錄：output/{owner_id}/{paper_id}/（shadow 靠 _shadow 後綴物理隔離）
        output_dir = paper_manager.paper_dir(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        paper_name = pdf_path.stem

        # ① Metadata Stage A（soft-fail、不阻斷）
        meta = self._extract_metadata(pdf_path)

        # ② pdf2md：ResumeProcessor Vision 忠實轉錄（複用、resume 不跑 md_cleaner）
        md_path = Path(ResumeProcessor().parse(str(pdf_path), str(output_dir)))
        markdown_text = md_path.read_text(encoding="utf-8")

        # ③ analyze：doc_analyzer 雙保險（resume heading fix；soft-fail）
        try:
            DocAnalyzer().analyze(md_path, "resume")
            markdown_text = md_path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 — 雙保險失敗不阻斷 P1
            logger.warning(
                "[PIPE-RESUME P1] %s analyze 雙保險失敗（soft）: %s",
                ctx.paper_id, exc, exc_info=True,
            )

        # ④⑤⑥ md2json → json_process → tiling（產物理分組 Tiles）
        tiles = self._build_tiles(md_path, output_dir, paper_name)

        # ⑦ 解析交付欄位
        title = self._resolve_title(meta, markdown_text, paper_name)
        source_lang = self._detect_source_lang(markdown_text)
        phone, email = self._extract_contact(markdown_text)
        domain = self._meta_value(meta, "domain") or ""
        # interim 穿線（custom_metadata 硬前置）：供 P2 消費 domain
        self._raw_meta = {"phone": phone, "email": email, "domain": domain}

        spec = IngestionMetadataSpec(
            title=title,
            authors=[],
            venue=None,
            doi=None,
            source_lang=source_lang,
            tiles=tiles,
        )
        logger.info(
            "[PIPE-RESUME P1] %s title=%r source_lang=%s tiles=%d domain=%r "
            "(phone=%s email=%s)",
            ctx.paper_id, title, source_lang, len(tiles), domain,
            bool(phone), bool(email),
        )
        return spec

    # ── P1 私有輔助（全鏈編排各步驟）──

    def _extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Metadata Stage A：fitz + LLM 第一頁雙來源合併（soft-fail → 空 metadata）。"""
        try:
            pdf_meta = extract_pdf_metadata(pdf_path)
            llm_meta = extract_metadata_from_first_page_llm(pdf_path, doc_type="resume")
            a = fill_from_pdf_metadata(create_empty_metadata(), pdf_meta)
            b = fill_from_llm_page1(create_empty_metadata(), llm_meta)
            return merge_stage_a(a, b)
        except Exception as exc:  # noqa: BLE001 — Stage A 全程 soft-fail
            logger.warning(
                "[PIPE-RESUME P1] Metadata Stage A 失敗（soft，空 metadata）: %s",
                exc, exc_info=True,
            )
            return create_empty_metadata()

    def _build_tiles(
        self, md_path: Path, output_dir: Path, paper_name: str
    ) -> List[Dict[str, Any]]:
        """md2json → json_process → tiling，回物理分組 Tiles（tiled JSON 的 sections）。"""
        structured = output_dir / f"{paper_name}_structured.json"
        MarkdownProcessor().process(str(md_path), str(structured))
        processed = output_dir / f"{paper_name}_processed.json"
        JsonProcessor().process(str(structured), str(processed))
        tiled = output_dir / f"{paper_name}_tiled.json"
        TilingProcessor().process(str(processed), str(tiled), doc_type="resume")
        return self._load_tiles(tiled)

    @staticmethod
    def _load_tiles(tiled_path: Path) -> List[Dict[str, Any]]:
        """讀 tiled JSON；dict→取 sections list、list→直接用；失敗回 []（soft）。"""
        try:
            data = json.loads(Path(tiled_path).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[PIPE-RESUME P1] 讀取 tiled JSON 失敗（tiles=[]）: %s",
                exc, exc_info=True,
            )
            return []
        if isinstance(data, dict):
            sections = data.get("sections")
            return sections if isinstance(sections, list) else [data]
        return data if isinstance(data, list) else []

    @staticmethod
    def _meta_value(meta: Dict[str, Any], field: str) -> Optional[Any]:
        """安全取 metadata 欄位 value（三軸融合結構 {field: {value, source, confidence}}）。"""
        v = meta.get(field)
        return v.get("value") if isinstance(v, dict) else v

    def _resolve_title(
        self, meta: Dict[str, Any], markdown_text: str, paper_name: str
    ) -> str:
        """title = candidate_name（最可信）→ markdown 首個 # 行 → title 欄 → paper_name。"""
        cand = self._meta_value(meta, "candidate_name")
        if cand and str(cand).strip():
            return str(cand).strip()
        for line in markdown_text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                return s.lstrip("#").strip() or paper_name
        t = self._meta_value(meta, "title")
        return str(t).strip() if t and str(t).strip() else paper_name

    @staticmethod
    def _detect_source_lang(markdown_text: str) -> str:
        """source_lang 啟發式：CJK 顯著佔比 → 'zh'，否則 'en'（無落地偵測器、保留原語言）。"""
        cjk = sum(1 for ch in markdown_text if "一" <= ch <= "鿿")
        letters = sum(1 for ch in markdown_text if ch.isascii() and ch.isalpha())
        if cjk >= _CJK_MIN and cjk >= letters * _CJK_RATIO:
            return "zh"
        return "en"

    def _extract_contact(self, markdown_text: str) -> Tuple[str, str]:
        """自 markdown regex 抽 phone/email（既有 metadata_extractor 無此二欄）。"""
        email_match = _EMAIL_RE.search(markdown_text)
        phone_match = _PHONE_RE.search(markdown_text)
        email = email_match.group(0) if email_match else ""
        phone = phone_match.group(0).strip() if phone_match else ""
        return phone, email
    # === [PIPE-RESUME C2 END] ===

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 Glossary & Context Prep：LCC / 摘要 / Glossary 自癒 / 摘要翻譯（合約②）。實作見 C3。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase2", commit="C3")
        )

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 Translation & Restore：100% Bypass 乾淨雙語 Markdown（合約③）。實作見 C4。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase3", commit="C4")
        )

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 Async RAG：向量化落庫、門檻 ≥3（合約④，非阻塞）。實作見 C5。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase4", commit="C5")
        )
# === [PIPE-RESUME C1 END] ===
