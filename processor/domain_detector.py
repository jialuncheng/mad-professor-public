"""DomainDetector — 看 PDF 第一頁文字 + 圖判斷主題領域。

Phase 4.7d Commit 0 後降為 fallback：
- 主路徑：metadata_extractor.extract_metadata_from_first_page_llm 已把 domain
  欄位加入單一 page1 LLM call（與 title/authors/... 一起抽）；caller
  （pipeline_core._stage_detect_domain）優先讀 self._metadata['domain'].value。
- fallback：本 class 用於 metadata.domain 為空時補跑（極端情境 / 舊 paper
  metadata_json 無此鍵的相容性）。
- 不刪：保留 class 與 detect() API 介面、設定值、log 行為皆不變。
"""
import logging
import time

import fitz  # PyMuPDF

import settings
from llm.client import LLMClient

DOMAIN_PROMPT = """這是一份文件的第一頁（內含頁面文字與頁面截圖）。
請判斷此文件的「具體主題領域」，回傳一個 10–30 字的短句，要具體、不要泛泛分類。
要求：

指出細分領域與主題，而非僅「新聞」「論文」這類大類
範例：「體育新聞 - 環義自由車賽報導」、「植物分子生物學 - 多重營養逆境調控」、「電力電子技術 - 高壓直流系統架構」
只輸出該短句本身，不要任何前綴、解釋或標點外的內容
若資訊不足無法判斷，只回傳空字串

頁面文字：
{first_page_text}"""


class DomainDetector:
    """讀 PDF 第一頁（文字 + Vision）判斷文件主題領域。失敗一律回空字串。"""

    def __init__(self, llm=None):
        self.llm = llm if llm is not None else LLMClient.get_instance()
        self.logger = logging.getLogger(__name__)

    def detect(self, pdf_path: str) -> str:
        """讀第一頁判斷主題領域；任何失敗回 ''（soft fallback）。"""
        self.logger.info(f"開始偵測 domain: {pdf_path}")
        self.logger.info(f"使用模型: {settings.LLM_DOMAIN_MODEL}")
        self.logger.info(f"[domain] 開始 pdf={pdf_path}")
        doc = None
        try:
            doc = fitz.open(str(pdf_path))
            if len(doc) == 0:
                self.logger.info("結果為空，跳過 domain")
                return ""

            page = doc[0]
            first_page_text = page.get_text() or ""
            first_page_text = first_page_text[:4000]
            img_data = page.get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("jpeg")

            prompt = DOMAIN_PROMPT.replace("{first_page_text}", first_page_text)
            self.logger.info("[domain] 呼叫 LLM")
            _t = time.time()
            result = self.llm.chat_with_image(
                messages=[{"role": "user", "content": prompt}],
                image_data=img_data,
                mime_type="image/jpeg",
                model=settings.LLM_DOMAIN_MODEL,
            )
            self.logger.info(
                f"[domain] LLM 回應 耗時={time.time() - _t:.2f}s "
                f"result={(result or '').strip()!r}"
            )
            domain = (result or "").strip()
            if not domain:
                self.logger.info("結果為空，跳過 domain")
                self.logger.info("[domain] 完成 domain=''")
                return ""
            self.logger.info(f"偵測結果: {domain}")
            self.logger.info(f"[domain] 完成 domain={domain!r}")
            return domain
        except Exception as e:
            self.logger.warning(f"偵測失敗: {e}")
            return ""
        finally:
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass
