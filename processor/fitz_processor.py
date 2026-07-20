"""born-digital PDF 文字層直抽處理器（PyMuPDF）。

PIPE-INGEST-FITZ C1：`PDFParser` 的第二個 impl——有完整文字層的 PDF
免繞外部解析服務，由 fitz 本地直抽文字＋圖、按座標組出與既有解析路
同形狀的 .md（`\n\n` 段落分隔、標準 `#`/`##` 標題、`![](images/<fname>)`）。

同形 .md 硬契約（下游 cleaner / analyzer / 攝入引擎來源無關之基準）：
- 段落以 `\n\n` 分隔；標題用標準 `#` / `##`（層級由字級分群推導）。
- 圖檔僅 PNG/JPEG 落地（`image_filter` stdlib 尺寸解析僅覆蓋此二格式），
  命名 `page_{page_idx}_{xref}.{ext}` 保跨頁唯一、防衝突覆寫。
- 區塊按座標（y, x）排序組閱讀序；跨頁重複之頂／底 band 行（URL 戳記、
  頁碼、日期戳等列印頁首尾）剝除。
- 全程零 `fitz.metadata` 讀取——meta 一律由下游正文分析取得、零檔案屬性依賴。

失敗語意依 ABC 契約：pdf 不存在 raise FileNotFoundError、解析錯誤統一
raise PDFParseError；圖檔抽取為 best-effort（單圖失敗跳過、不阻斷）。
"""
import logging
import re
import statistics
from pathlib import Path
from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF

from processor.pdf_parser import PDFParser, PDFParseError

logger = logging.getLogger(__name__)

# 圖檔僅此二格式落地（extract_image 之 ext 值；jpg/jpeg 同族）
_ALLOWED_IMAGE_EXTS = {"png", "jpeg", "jpg"}

# 頁首/頁尾 band 佔頁高比例（列印雜訊多落於此極窄邊帶）
_HEADER_BAND_RATIO = 0.08
_FOOTER_BAND_RATIO = 0.92

# 標題行長度上限（超長行即使字級大也視為正文、防大字級段落誤判標題）
_HEADING_MAX_CHARS = 150

# 字級分群的正文噪音容差（僅明顯大於正文字級者列入標題候選）
_HEADING_SIZE_MARGIN = 1.0


def median_page_chars(pdf_path: str) -> float:
    """每頁純文字字元數中位數（文字層閘門輔助）。

    born-digital 網頁列印每頁遠超門檻、掃描件為 0——鴻溝巨大。
    開檔/解析異常自然上拋、由呼叫端 fail-open 處置（本函式不吞）。
    """
    with fitz.open(pdf_path) as doc:
        counts = [len(page.get_text("text").strip()) for page in doc]
    if not counts:
        return 0.0
    return float(statistics.median(counts))


def _repetition_key(text: str) -> str:
    """跨頁重複偵測 key：數字歸一（頁碼/日期逐頁變動、去數字後同形）。"""
    return re.sub(r"\d+", "#", text.strip())


class FitzProcessor(PDFParser):
    """PDF → Markdown 的 fitz 直抽 impl（born-digital 文字層快速道）。"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    # ── 對外介面（ABC 契約）──

    def parse(self, pdf_path: str, output_dir: str) -> Path:
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF 不存在: {pdf_path}")
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = out_dir / f"{pdf_file.stem}.md"

        try:
            with fitz.open(pdf_path) as doc:
                pages = [self._collect_page(doc, page) for page in doc]
                chunks = self._assemble(doc, pages, out_dir)
        except (PDFParseError, FileNotFoundError):
            raise
        except Exception as exc:
            self.logger.error(
                "[fitz_processor] 解析失敗 %s: %s", pdf_path, exc, exc_info=True
            )
            raise PDFParseError(f"fitz 解析失敗: {exc}") from exc

        markdown_path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
        self.logger.info(
            "[fitz_processor] 直抽完成 %s → %s（%d 區塊）",
            pdf_file.name, markdown_path.name, len(chunks),
        )
        return markdown_path

    # ── 第一趟：逐頁收集行/圖項目 ──

    def _collect_page(self, doc: fitz.Document, page: fitz.Page) -> Dict[str, Any]:
        """收集單頁文字行（含座標/字級/block 歸屬）與圖項目。"""
        height = float(page.rect.height) or 1.0
        lines: List[Dict[str, Any]] = []
        raw = page.get_text("dict")
        for b_idx, block in enumerate(raw.get("blocks", [])):
            if block.get("type") != 0:  # 僅文字 block；圖走 get_images 統一座標
                continue
            for line in block.get("lines", []):
                text = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
                if not text:
                    continue
                x0, y0, _x1, y1 = line["bbox"]
                size = max(float(s.get("size", 0.0)) for s in line.get("spans", []))
                lines.append({
                    "text": text,
                    "size": size,
                    "x0": float(x0),
                    "y0": float(y0),
                    "block": b_idx,
                    "in_band": (y0 < height * _HEADER_BAND_RATIO
                                or y1 > height * _FOOTER_BAND_RATIO),
                })

        images: List[Dict[str, Any]] = []
        seen_xrefs = set()
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            rects = page.get_image_rects(xref)
            if not rects:
                continue
            images.append({
                "xref": xref,
                "x0": float(rects[0].x0),
                "y0": float(rects[0].y0),
            })
        return {"lines": lines, "images": images, "index": page.number}

    # ── 第二趟：全文分析 + 組裝 ──

    def _assemble(
        self, doc: fitz.Document, pages: List[Dict[str, Any]], out_dir: Path
    ) -> List[str]:
        repeated = self._repeated_band_keys(pages)
        h1_size, h2_size = self._heading_sizes(pages)
        images_dir = out_dir / "images"

        chunks: List[str] = []
        for page_data in pages:
            items: List[Tuple[float, float, str]] = []  # (y0, x0, markdown)

            # 圖項目：extract 落地後以座標插入閱讀序（best-effort）
            for img in page_data["images"]:
                fname = self._extract_image(
                    doc, img["xref"], page_data["index"], images_dir
                )
                if fname:
                    items.append((img["y0"], img["x0"], f"![](images/{fname})"))

            # 文字項目：剝頁首尾 → 標題獨立成塊 / 同 block 連續正文行併段
            para_lines: List[str] = []
            para_pos: Tuple[float, float] = (0.0, 0.0)
            para_block = None

            def flush():
                nonlocal para_lines, para_block
                if para_lines:
                    items.append((para_pos[0], para_pos[1], " ".join(para_lines)))
                para_lines = []
                para_block = None

            for line in sorted(
                page_data["lines"], key=lambda l: (l["y0"], l["x0"])
            ):
                if line["in_band"] and _repetition_key(line["text"]) in repeated:
                    continue  # 跨頁重複之列印頁首尾
                level = self._heading_level(line, h1_size, h2_size)
                if level:
                    flush()
                    items.append((line["y0"], line["x0"], f"{'#' * level} {line['text']}"))
                    continue
                if para_block is not None and line["block"] != para_block:
                    flush()
                if not para_lines:
                    para_pos = (line["y0"], line["x0"])
                    para_block = line["block"]
                para_lines.append(line["text"])
            flush()

            items.sort(key=lambda it: (it[0], it[1]))
            chunks.extend(md for _y, _x, md in items)
        return chunks

    def _repeated_band_keys(self, pages: List[Dict[str, Any]]) -> set:
        """頂/底 band 內、以數字歸一 key 出現於 ≥2 頁者＝列印頁首尾。"""
        if len(pages) < 2:
            return set()
        page_hits: Dict[str, set] = {}
        for page_data in pages:
            for line in page_data["lines"]:
                if line["in_band"]:
                    key = _repetition_key(line["text"])
                    page_hits.setdefault(key, set()).add(page_data["index"])
        return {key for key, hit in page_hits.items() if len(hit) >= 2}

    def _heading_sizes(self, pages: List[Dict[str, Any]]) -> Tuple[float, float]:
        """字級分群：正文字級＝眾數；明顯大於正文的前兩群→ #（最大）/ ##（次級）。"""
        char_weight: Dict[float, int] = {}
        for page_data in pages:
            for line in page_data["lines"]:
                key = round(line["size"], 1)
                char_weight[key] = char_weight.get(key, 0) + len(line["text"])
        if not char_weight:
            return (0.0, 0.0)
        # 正文字級＝承載字元數最多的字級（正文以字量壓倒標題、抗頻次平手）
        body = max(char_weight, key=char_weight.get)
        candidates = sorted(
            (s for s in char_weight if s > body + _HEADING_SIZE_MARGIN),
            reverse=True,
        )
        h1 = candidates[0] if candidates else 0.0
        h2 = candidates[1] if len(candidates) > 1 else 0.0
        return (h1, h2)

    @staticmethod
    def _heading_level(line: Dict[str, Any], h1: float, h2: float) -> int:
        if len(line["text"]) > _HEADING_MAX_CHARS:
            return 0
        size = round(line["size"], 1)
        if h1 and size >= h1:
            return 1
        if h2 and size >= h2:
            return 2
        return 0

    def _extract_image(
        self, doc: fitz.Document, xref: int, page_idx: int, images_dir: Path
    ) -> str:
        """抽單圖落地（僅 PNG/JPEG、`page_{page_idx}_{xref}.{ext}`）；失敗跳過。"""
        try:
            info = doc.extract_image(xref)
            ext = str(info.get("ext", "")).lower()
            if ext not in _ALLOWED_IMAGE_EXTS:
                self.logger.info(
                    "[fitz_processor] 跳過非 PNG/JPEG 圖 xref=%d ext=%s", xref, ext
                )
                return ""
            images_dir.mkdir(parents=True, exist_ok=True)
            fname = f"page_{page_idx}_{xref}.{ext}"
            (images_dir / fname).write_bytes(info["image"])
            return fname
        except Exception as exc:  # noqa: BLE001 — 單圖 best-effort、不阻斷全文
            self.logger.warning(
                "[fitz_processor] 圖檔抽取失敗 xref=%d（跳過）: %s",
                xref, exc, exc_info=True,
            )
            return ""
