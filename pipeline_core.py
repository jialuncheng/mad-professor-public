from pathlib import Path
import json
import logging
import time
from typing import Optional, Dict, List, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import paper_manager
from processor.pdf_processor import PDFProcessor
from processor.md_cleaner import MarkdownCleaner
from processor.doc_analyzer import DocAnalyzer
from processor.md_processor import MarkdownProcessor
from processor.json_processor import JsonProcessor
from processor.tiling_processor import TilingProcessor
from processor.translate_processor import TranslateProcessor
from processor.md_restore_processor import RestoreProcessor
from processor.extra_info_processor import ExtraInfoProcessor
from processor.rag_processor import RagProcessor
from processor.image_caption_processor import ImageCaptionProcessor
from processor.slides_processor import SlidesProcessor
from processor.domain_detector import DomainDetector
from processor.metadata_extractor import (
    extract_pdf_metadata, extract_metadata_from_first_page_llm,
    create_empty_metadata, fill_from_pdf_metadata, fill_from_llm_page1,
    merge_stage_a, fill_abstract_stage_b,
)

logger = logging.getLogger(__name__)

# 階段清單的唯一權威來源（順序即執行順序）
STAGE_NAMES = [
    "pdf2md", "analyze", "detect_domain", "md2json", "json_process", "tiling",
    "translate", "image_caption", "md_restore", "extra_info", "rag"
]

class PipelineCore:
    """學術論文處理管線（不依賴 Qt，供 Web API 使用）"""

    STAGE_DISPLAY_NAMES = {
        'pdf2md': 'PDF 轉 Markdown',
        'analyze': '文件結構分析',
        'detect_domain': '主題領域偵測',
        'md2json': 'Markdown 轉 JSON',
        'json_process': 'JSON 處理',
        'tiling': '分段處理',
        'translate': '內容翻譯',
        'image_caption': '圖片說明生成',
        'md_restore': '生成 Markdown 文件',
        'extra_info': '提取額外資訊',
        'rag': 'RAG 處理'
    }

    def __init__(self, stages: Optional[List[str]] = None,
                 on_progress: Optional[Callable[[dict], None]] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.on_progress = on_progress  # 進度回調，替代 Qt signal

        self.stage_identifiers = {
            'pdf2md': '',
            'analyze': '_doc_structure',
            'detect_domain': '_domain',
            'md2json': '_structured',
            'json_process': '_processed',
            'tiling': '_tiled',
            'translate': '_translated',
            'image_caption': '_images_info',
            'md_restore': '_restored',
            'extra_info': '_extra_info',
            'rag': '_rag'
        }

        self.available_stages = {
            'pdf2md': self._stage_pdf_to_md,
            'analyze': self._stage_analyze,
            'detect_domain': self._stage_detect_domain,
            'md2json': self._stage_md_to_json,
            'json_process': self._stage_json_process,
            'tiling': self._stage_tiling,
            'translate': self._stage_translate,
            'image_caption': self._stage_image_caption,
            'md_restore': self._stage_md_restore,
            'extra_info': self._stage_extra_info,
            'rag': self._stage_rag
        }
        default_stages = list(STAGE_NAMES)
        self.stages = stages or default_stages

        self.paper_info = {'paper_id': None, 'output_dir': None}
        self._current_stage = None

    # 各 processor 延遲建立並快取：首次存取對應屬性時才實例化，之後重用同一物件
    @property
    def pdf_processor(self):
        if not hasattr(self, '_pdf_processor'):
            self._pdf_processor = PDFProcessor()
        return self._pdf_processor

    @property
    def md_cleaner(self):
        if not hasattr(self, '_md_cleaner'):
            self._md_cleaner = MarkdownCleaner()
        return self._md_cleaner

    @property
    def doc_analyzer(self):
        if not hasattr(self, '_doc_analyzer'):
            self._doc_analyzer = DocAnalyzer()
        return self._doc_analyzer

    @property
    def md_processor(self):
        if not hasattr(self, '_md_processor'):
            self._md_processor = MarkdownProcessor()
        return self._md_processor

    @property
    def json_processor(self):
        if not hasattr(self, '_json_processor'):
            self._json_processor = JsonProcessor()
        return self._json_processor

    @property
    def tiling_processor(self):
        if not hasattr(self, '_tiling_processor'):
            self._tiling_processor = TilingProcessor()
        return self._tiling_processor

    @property
    def translate_processor(self):
        if not hasattr(self, '_translate_processor'):
            self._translate_processor = TranslateProcessor()
        return self._translate_processor

    @property
    def image_caption_processor(self):
        if not hasattr(self, '_image_caption_processor'):
            self._image_caption_processor = ImageCaptionProcessor()
        return self._image_caption_processor

    @property
    def restore_processor(self):
        if not hasattr(self, '_restore_processor'):
            self._restore_processor = RestoreProcessor()
        return self._restore_processor

    @property
    def extra_info_processor(self):
        if not hasattr(self, '_extra_info_processor'):
            self._extra_info_processor = ExtraInfoProcessor()
        return self._extra_info_processor

    @property
    def rag_processor(self):
        if not hasattr(self, '_rag_processor'):
            self._rag_processor = RagProcessor()
        return self._rag_processor

    @property
    def domain_detector(self):
        if not hasattr(self, '_domain_detector'):
            self._domain_detector = DomainDetector()
        return self._domain_detector

    TOTAL_STAGES = len(STAGE_NAMES)

    def _emit_progress(self, stage: str, index: int):
        """發送進度更新"""
        if not self.on_progress:
            return
        # 用固定總數計算進度，避免分階段跑時進度跳到 100%
        all_stages = STAGE_NAMES
        global_index = all_stages.index(stage) + 1 if stage in all_stages else index
        info = {
            'stage': stage,
            'stage_name': self.STAGE_DISPLAY_NAMES.get(stage, stage),
            'index': global_index,
            'total': len(all_stages),
            'progress': int(global_index / len(all_stages) * 100)
        }
        self.on_progress(info)

    def _get_stage_output_path(self, stage: str, paper_dir: Path, paper_name: str):
        identifier = self.stage_identifiers.get(stage, '')
        if stage == 'pdf2md':
            return paper_dir / f"{paper_name}{identifier}.md"
        elif stage == 'md_restore':
            return {
                'en': paper_dir / f"final_{paper_name}_en.md",
                'zh': paper_dir / f"final_{paper_name}_zh.md"
            }
        elif stage == 'rag':
            return {
                'md': paper_dir / f"final_{paper_name}_rag.md",
                'tree_json': paper_dir / f"final_{paper_name}_rag_tree.json",
                'vector_store': paper_dir / "vectors"
            }
        elif stage == 'image_caption':
            return paper_dir / f"{paper_name}{identifier}.md"
        else:
            return paper_dir / f"{paper_name}{identifier}.json"

    def process(self, pdf_path: str, output_dir: Optional[str] = None,
                owner_id: Optional[int] = None,
                existing_paths: Optional[Dict] = None,
                paper_id: Optional[str] = None,
                original_filename: Optional[str] = None) -> Dict:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        root_output_dir = Path(output_dir) if output_dir else pdf_path.parent
        # 路徑統一 output/{owner_id}/{paper_uuid}/
        base_output_dir = (
            root_output_dir / str(owner_id) if owner_id is not None
            else root_output_dir
        )
        base_output_dir.mkdir(exist_ok=True, parents=True)
        self._root_output_dir = root_output_dir
        self._owner_id = owner_id

        _pipe_t0 = time.time()
        _doc_type = (existing_paths or {}).get('_confirmed_doc_type', 'academic')
        self.logger.info(
            f"[pipeline] 開始 pdf={pdf_path} owner={owner_id} doc_type={_doc_type}"
        )

        # ── Metadata Stage A（fitz + LLM 第一頁 + 雙來源比對）──
        # 設計為與 pdf2md 並行；但既有 pipeline 為同步 + ThreadPoolExecutor 架構，
        # 改 async 風險過高（會破壞 web_server run_in_executor），故此處改採
        # 「pdf2md 前序列執行」——Stage A（fitz + 1 次 LLM）相對 MinerU（數分鐘）
        # 極短，序列化對總牆鐘影響可忽略；全程 soft fail，絕不中止 pipeline。
        self._metadata = create_empty_metadata()
        self.logger.info("[metadata] Stage A 開始")
        _sa_t0 = time.time()
        try:
            _t = time.time()
            _pdf_meta = extract_pdf_metadata(pdf_path)
            self.logger.info(
                f"[metadata] fitz 完成 耗時={time.time() - _t:.2f}s "
                f"title={_pdf_meta.get('title')!r} "
                f"authors={_pdf_meta.get('authors')}"
            )
            _t = time.time()
            # Phase 4.7c step 3：依 doc_type 走不同 prompt（resume/technical）
            _llm_meta = extract_metadata_from_first_page_llm(
                pdf_path, doc_type=_doc_type
            )
            self.logger.info(
                f"[metadata] LLM 第一頁完成 耗時={time.time() - _t:.2f}s "
                f"doc_type={_doc_type} "
                f"title={(_llm_meta or {}).get('title')!r} "
                f"candidate_name={(_llm_meta or {}).get('candidate_name')!r}"
            )
            _a = fill_from_pdf_metadata(create_empty_metadata(), _pdf_meta)
            _b = fill_from_llm_page1(create_empty_metadata(), _llm_meta)
            self._metadata = merge_stage_a(_a, _b)
            self.logger.info(
                f"[metadata] Stage A 完成（title="
                f"{self._metadata.get('title', {}).get('value')!r}）"
            )
            self.logger.info(
                f"[metadata] Stage A 合併完成 總耗時={time.time() - _sa_t0:.2f}s "
                f"confidence="
                f"{ {k: v.get('confidence') for k, v in self._metadata.items() if isinstance(v, dict)} }"
            )
        except Exception as e:
            self.logger.warning(f"[metadata] Stage A 失敗（soft，忽略）: {e}")

        self.paper_info['paper_id'] = paper_id if paper_id is not None else pdf_path.stem
        paper_output_dir = base_output_dir / self.paper_info['paper_id']
        paper_output_dir.mkdir(exist_ok=True)
        self.paper_info['output_dir'] = paper_output_dir

        # 支援傳入已有的 output_paths（第二階段繼續處理）
        output_paths = dict(existing_paths) if existing_paths else {}

        self.logger.info(f"[pipeline] 進入 stage loop（stages={self.stages}）")
        i = 0
        while i < len(self.stages):
            stage = self.stages[i]

            # 偵測到 analyze，嘗試與 detect_domain 並行（detect_domain 失敗 soft）
            if stage == 'analyze' and 'detect_domain' in self.stages:
                analyze_done = self._check_stage_exists('analyze', paper_output_dir, self.paper_info['paper_id'], output_paths)
                domain_done = '_domain' in output_paths

                if not analyze_done or not domain_done:
                    self.logger.info("並行執行: analyze + detect_domain")
                    self._emit_progress('analyze', i + 1)

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        futures = {}
                        start_times = {}
                        if not analyze_done:
                            start_times['analyze'] = time.time()
                            futures[executor.submit(
                                self.available_stages['analyze'],
                                pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                            )] = 'analyze'
                        if not domain_done:
                            start_times['detect_domain'] = time.time()
                            futures[executor.submit(
                                self.available_stages['detect_domain'],
                                pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                            )] = 'detect_domain'

                        for future in as_completed(futures):
                            s = futures[future]
                            duration = time.time() - start_times[s]
                            try:
                                result = future.result()
                                if s == 'detect_domain':
                                    output_paths['_domain'] = result or ''
                                else:
                                    output_paths[s] = result
                                self.logger.info(f"階段 {s} 完成")
                                self.logger.info(f"[並行] {s} 完成（耗時 {duration:.1f}s）")
                            except Exception as e:
                                self.logger.error(f"階段 {s} 失敗: {str(e)}")
                                self.logger.error(f"[並行] {s} 失敗（耗時 {duration:.1f}s）: {e}")
                                if s == 'analyze':
                                    raise
                                # detect_domain 失敗：soft fallback，不中止
                                output_paths['_domain'] = ''

                # 跳過 detect_domain（已並行處理）
                if i + 1 < len(self.stages) and self.stages[i + 1] == 'detect_domain':
                    i += 2
                else:
                    i += 1
                continue

            if stage == 'detect_domain':
                i += 1
                continue

            # 偵測到 translate，嘗試與 image_caption 並行
            if stage == 'translate' and 'image_caption' in self.stages:
                translate_done = self._check_stage_exists('translate', paper_output_dir, self.paper_info['paper_id'], output_paths)
                caption_done = self._check_stage_exists('image_caption', paper_output_dir, self.paper_info['paper_id'], output_paths)

                if not translate_done or not caption_done:
                    self.logger.info("並行執行: translate + image_caption")
                    self.logger.info("[stage] translate + image_caption 開始（並行）")
                    self._emit_progress('translate', i + 1)
                    _par_t0 = time.time()

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        futures = {}
                        if not translate_done:
                            futures[executor.submit(
                                self.available_stages['translate'],
                                pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                            )] = 'translate'
                        if not caption_done:
                            futures[executor.submit(
                                self.available_stages['image_caption'],
                                pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                            )] = 'image_caption'

                        for future in as_completed(futures):
                            s = futures[future]
                            try:
                                output_paths[s] = future.result()
                                self.logger.info(f"階段 {s} 完成")
                                self.logger.info(
                                    f"[stage] {s} 完成 耗時="
                                    f"{time.time() - _par_t0:.2f}s（並行）"
                                )
                            except Exception as e:
                                self.logger.error(f"階段 {s} 失敗: {str(e)}")
                                self.logger.error(
                                    f"[stage] {s} 失敗 耗時="
                                    f"{time.time() - _par_t0:.2f}s（並行）: {e}"
                                )
                                if s == 'translate':
                                    raise

                # 跳過 image_caption（已並行處理）
                if i + 1 < len(self.stages) and self.stages[i + 1] == 'image_caption':
                    i += 2
                else:
                    i += 1
                continue

            if stage == 'image_caption':
                i += 1
                continue

            if stage not in self.available_stages:
                self.logger.warning(f"未知的處理階段: {stage}")
                i += 1
                continue

            self._current_stage = stage
            self._emit_progress(stage, i + 1)
            self.logger.info(f"開始運行階段: {stage}")
            self.logger.info(f"[stage] {stage} 開始")
            _stage_t0 = time.time()

            if not self._check_stage_exists(stage, paper_output_dir, self.paper_info['paper_id'], output_paths):
                stage_output = self.available_stages[stage](
                    pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                )
                output_paths[stage] = stage_output
                self.logger.info(f"階段 {stage} 完成")

            self.logger.info(
                f"[stage] {stage} 完成 耗時={time.time() - _stage_t0:.2f}s"
            )

            i += 1

        self._current_stage = None

        final_paths = {}
        if 'md_restore' in output_paths:
            restore_paths = output_paths['md_restore']
            final_paths.update({'article_en': restore_paths['en'], 'article_zh': restore_paths['zh']})
        if 'rag' in output_paths:
            rag_paths = output_paths['rag']
            final_paths.update({
                'rag_md': rag_paths['md'],
                'rag_tree': rag_paths['tree_json'],
                'rag_vector_store': rag_paths['vector_store']
            })
        images_dir = paper_output_dir / "images"
        if images_dir.exists():
            final_paths['images'] = images_dir

        # ── Metadata 最小 Stage B：只補 abstract（看 MinerU markdown）──
        # abstract 在 Stage A 永遠為空（設計：純文字首頁排版不可靠），此處用
        # MinerU 轉出的 markdown 補；規則找不到才 LLM。全程 soft fail。
        self.logger.info("[metadata] Stage B 開始")
        _sb_t0 = time.time()
        try:
            md_path = output_paths.get('pdf2md')
            md_text = None
            if md_path and Path(md_path).exists():
                md_text = Path(md_path).read_text(encoding='utf-8', errors='ignore')
            if md_text:
                fill_abstract_stage_b(self._metadata, md_text)
                self.logger.info(
                    f"[metadata] Stage B 完成（abstract="
                    f"{'有' if self._metadata.get('abstract', {}).get('value') else '無'}）"
                )
        except Exception as e:
            self.logger.warning(f"[metadata] Stage B 失敗（soft，忽略）: {e}")
        self.logger.info(
            f"[metadata] Stage B 完成 abstract="
            f"{'有' if self._metadata.get('abstract', {}).get('value') else '無'} "
            f"耗時={time.time() - _sb_t0:.2f}s"
        )

        if final_paths and self._owner_id is not None:
            self.logger.info(
                f"[pipeline] 準備寫 DB domain={output_paths.get('_domain')!r} "
                f"doc_type={output_paths.get('_confirmed_doc_type', 'academic')!r} "
                f"title={self._metadata.get('title', {}).get('value')!r}"
            )
            paper_manager.upsert_paper(
                self._root_output_dir,
                self._owner_id,
                self.paper_info['paper_id'],
                {k: str(v) for k, v in final_paths.items() if v},
                metadata=self._metadata,
                domain=output_paths.get('_domain'),
                doc_type=output_paths.get('_confirmed_doc_type', 'academic'),
                original_filename=original_filename,
            )
            output_paths['final'] = final_paths
            self.logger.info("[pipeline] DB 寫入完成")

        self.logger.info(
            f"[pipeline] 全部完成 總耗時={time.time() - _pipe_t0:.2f}s"
        )
        return output_paths

    def _check_stage_exists(self, stage: str, paper_dir: Path, paper_name: str, output_paths: dict) -> bool:
        """檢查階段是否已完成，若已完成則更新 output_paths"""
        expected_output = self._get_stage_output_path(stage, paper_dir, paper_name)

        if stage in ['md_restore', 'rag']:
            if all(p.exists() for p in expected_output.values()):
                output_paths[stage] = expected_output
                self.logger.info(f"階段 {stage} 已存在，跳過")
                return True

        elif isinstance(expected_output, Path) and expected_output.exists():
            if stage == 'pdf2md':
                md_path = paper_dir / f'{paper_name}.md'
                output_paths['pdf2md'] = md_path
                self.logger.info(f"階段 {stage} 已存在，跳過")
                return True
            elif stage == 'md2json':
                md_path = output_paths.get('pdf2md')
                if md_path:
                    sidecar = Path(md_path).parent / f'{Path(md_path).stem}_doc_structure.json'
                    if sidecar.exists():
                        output_paths[stage] = expected_output
                        self.logger.info(f"階段 {stage} 已存在，跳過")
                        return True
                    return False
            elif stage == 'image_caption':
                output_paths[stage] = expected_output
                self.logger.info(f"階段 {stage} 已存在，跳過")
                return True
            else:
                output_paths[stage] = expected_output
                self.logger.info(f"階段 {stage} 已存在，跳過")
                return True

        return False


    # ── 各階段方法 ──

    def _stage_pdf_to_md(self, pdf_path, paper_dir, paper_name, output_paths):
        doc_type = output_paths.get('_confirmed_doc_type', 'academic')

        if doc_type == 'slides':
            # 簡報：用 Vision 每頁解析，不走 MinerU
            self.logger.info("簡報類型，使用 Vision 解析")
            parser = SlidesProcessor()
        else:
            # 其他：MinerU 解析
            parser = self.pdf_processor

        markdown_path = parser.parse(str(pdf_path), str(paper_dir))

        if doc_type != 'slides':
            self.md_cleaner.clean(markdown_path)

        return markdown_path

    def _stage_analyze(self, pdf_path, paper_dir, paper_name, output_paths):
        markdown_path = output_paths.get('pdf2md')
        if not markdown_path:
            raise ValueError("未找到 Markdown 文件")
        doc_type = output_paths.get('_confirmed_doc_type', 'academic')
        return self.doc_analyzer.analyze(markdown_path, doc_type)

    def _stage_detect_domain(self, pdf_path, paper_dir, paper_name, output_paths):
        """讀 PDF 第一頁判斷主題領域；永不 raise，失敗回 ''（soft fallback）。

        Phase 4.7d Commit 0：優先從 self._metadata['domain'].value 取（已在
        Stage A LLM page1 call 一次抽到）；空才 fallback DomainDetector
        補跑（極端情境 / 既有 paper 無此鍵的相容性）。保留 stage 結構與
        output_paths['_domain'] 介面以避免破壞既有調用。
        """
        try:
            d = (getattr(self, '_metadata', None) or {}).get('domain', {}).get('value') or ''
            if d:
                self.logger.info(
                    f"[domain] 從 metadata.domain 取得：{d!r}（合併 LLM call）"
                )
                return d
            self.logger.info(
                "[domain] metadata 無 domain，fallback 跑 DomainDetector"
            )
            return self.domain_detector.detect(str(pdf_path)) or ''
        except Exception as e:
            self.logger.warning(f"detect_domain 階段失敗（soft，忽略）: {str(e)}")
            return ''

    def _stage_md_to_json(self, pdf_path, paper_dir, paper_name, output_paths):
        markdown_path = output_paths.get('pdf2md')
        if not markdown_path:
            raise ValueError("未找到 Markdown 文件")
        output_path = self._get_stage_output_path('md2json', paper_dir, paper_name)
        return self.md_processor.process(str(markdown_path), str(output_path))

    def _stage_json_process(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('md2json')
        if not input_path:
            raise ValueError("未找到 JSON 文件")
        output_path = self._get_stage_output_path('json_process', paper_dir, paper_name)
        return self.json_processor.process(str(input_path), str(output_path))

    def _stage_tiling(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('json_process')
        if not input_path:
            raise ValueError("未找到 JSON 文件")
        output_path = self._get_stage_output_path('tiling', paper_dir, paper_name)
        return self.tiling_processor.process(str(input_path), str(output_path))

    def _stage_translate(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('tiling')
        if not input_path:
            raise ValueError("未找到 JSON 文件")
        output_path = self._get_stage_output_path('translate', paper_dir, paper_name)
        doc_type = output_paths.get('_confirmed_doc_type', 'academic')
        domain = output_paths.get('_domain', '')
        return self.translate_processor.process(str(input_path), str(output_path), doc_type=doc_type, domain=domain)

    def _stage_image_caption(self, pdf_path, paper_dir, paper_name, output_paths):
        """Vision 圖片說明生成，與 translate 並行執行"""
        images_dir = paper_dir / "images"
        output_path = self._get_stage_output_path('image_caption', paper_dir, paper_name)
        result = self.image_caption_processor.process(str(images_dir), str(output_path))
        return result

    def _stage_md_restore(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('translate')
        if not input_path:
            raise ValueError("未找到翻譯 JSON 文件")
        paths = self._get_stage_output_path('md_restore', paper_dir, paper_name)
        images_info_path = self._get_stage_output_path('image_caption', paper_dir, paper_name)
        en_path, zh_path = self.restore_processor.process(
            str(input_path), str(paths['en']), str(paths['zh']),
            images_info_path=str(images_info_path) if images_info_path.exists() else None
        )
        return {'en': Path(en_path), 'zh': Path(zh_path)}

    def _stage_extra_info(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('translate')
        if not input_path:
            raise ValueError("未找到翻譯 JSON 文件")
        output_path = self._get_stage_output_path('extra_info', paper_dir, paper_name)
        doc_type = output_paths.get('_confirmed_doc_type', 'academic')
        domain = output_paths.get('_domain', '')
        # === doc_type-registry ===
        # 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
        if doc_type in ('news', 'web', 'slides', 'resume'):
            return self.extra_info_processor.generate_document_summary(
                str(input_path), str(output_path), domain=domain
            )
        return self.extra_info_processor.process(str(input_path), str(output_path), domain=domain)

    def _stage_rag(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('extra_info') or output_paths.get('translate')
        if not input_path:
            raise ValueError("未找到 JSON 文件")
        paths = self._get_stage_output_path('rag', paper_dir, paper_name)
        images_info_path = self._get_stage_output_path('image_caption', paper_dir, paper_name)
        md_path, tree_path, vector_path = self.rag_processor.process(
            str(input_path), str(paths['md']), str(paths['tree_json']), str(paths['vector_store']),
            images_info_path=str(images_info_path) if images_info_path.exists() else None
        )
        return {'md': Path(md_path), 'tree_json': Path(tree_path), 'vector_store': Path(vector_path)}