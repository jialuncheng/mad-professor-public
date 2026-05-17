from pathlib import Path
import json
import logging
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

logger = logging.getLogger(__name__)

class PipelineCore:
    """學術論文處理管線（不依賴 Qt，供 Web API 使用）"""

    STAGE_NAMES = {
        'pdf2md': 'PDF 轉 Markdown',
        'analyze': '文件結構分析',
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
            'md2json': self._stage_md_to_json,
            'json_process': self._stage_json_process,
            'tiling': self._stage_tiling,
            'translate': self._stage_translate,
            'image_caption': self._stage_image_caption,
            'md_restore': self._stage_md_restore,
            'extra_info': self._stage_extra_info,
            'rag': self._stage_rag
        }
        default_stages = ['pdf2md', 'analyze', 'md2json', 'json_process', 'tiling', 'translate', 'image_caption', 'md_restore', 'extra_info', 'rag']
        self.stages = stages or default_stages

        self.pdf_processor = PDFProcessor()
        self.md_cleaner = MarkdownCleaner()
        self.doc_analyzer = DocAnalyzer()
        self.md_processor = MarkdownProcessor()
        self.json_processor = JsonProcessor()
        self.tiling_processor = TilingProcessor()
        self.translate_processor = TranslateProcessor()
        self.image_caption_processor = ImageCaptionProcessor()
        self.restore_processor = RestoreProcessor()
        self.extra_info_processor = ExtraInfoProcessor()
        self.rag_processor = RagProcessor()

        self.paper_info = {'paper_id': None, 'output_dir': None}
        self._current_stage = None

    TOTAL_STAGES = 10  # pdf2md, analyze, md2json, json_process, tiling, translate, image_caption, md_restore, extra_info, rag

    def _emit_progress(self, stage: str, index: int):
        """發送進度更新"""
        if not self.on_progress:
            return
        # 用固定總數計算進度，避免分階段跑時進度跳到 100%
        all_stages = ['pdf2md', 'analyze', 'md2json', 'json_process',
                      'tiling', 'translate', 'image_caption', 'md_restore', 'extra_info', 'rag']
        global_index = all_stages.index(stage) + 1 if stage in all_stages else index
        info = {
            'stage': stage,
            'stage_name': self.STAGE_NAMES.get(stage, stage),
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
                existing_paths: Optional[Dict] = None) -> Dict:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        base_output_dir = Path(output_dir) if output_dir else pdf_path.parent
        base_output_dir.mkdir(exist_ok=True, parents=True)

        self.paper_info['paper_id'] = pdf_path.stem
        paper_output_dir = base_output_dir / self.paper_info['paper_id']
        paper_output_dir.mkdir(exist_ok=True)
        self.paper_info['output_dir'] = paper_output_dir

        # 支援傳入已有的 output_paths（第二階段繼續處理）
        output_paths = dict(existing_paths) if existing_paths else {}

        i = 0
        while i < len(self.stages):
            stage = self.stages[i]

            # 偵測到 translate，嘗試與 image_caption 並行
            if stage == 'translate' and 'image_caption' in self.stages:
                translate_done = self._check_stage_exists('translate', paper_output_dir, self.paper_info['paper_id'], output_paths)
                caption_done = self._check_stage_exists('image_caption', paper_output_dir, self.paper_info['paper_id'], output_paths)

                if not translate_done or not caption_done:
                    self.logger.info("並行執行: translate + image_caption")
                    self._emit_progress('translate', i + 1)

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
                            except Exception as e:
                                self.logger.error(f"階段 {s} 失敗: {str(e)}")
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

            if not self._check_stage_exists(stage, paper_output_dir, self.paper_info['paper_id'], output_paths):
                stage_output = self.available_stages[stage](
                    pdf_path, paper_output_dir, self.paper_info['paper_id'], output_paths
                )
                output_paths[stage] = stage_output
                self.logger.info(f"階段 {stage} 完成")
            elif stage == 'pdf2md' and '_doc_type_detection' not in output_paths:
                # pdf2md 被跳過時，從 sidecar 讀取文件類型偵測結果
                md_path = output_paths.get('pdf2md')
                if md_path:
                    sidecar = Path(md_path).parent / f'{Path(md_path).stem}_doc_structure.json'
                    if sidecar.exists():
                        import json as _json
                        structure = _json.loads(sidecar.read_text(encoding='utf-8'))
                        doc_type = structure.get('document_type', 'academic')
                        output_paths['_doc_type_detection'] = {
                            'doc_type': doc_type,
                            'confidence': 'high',
                            'reason': '從已存在的分析結果載入'
                        }
                        self.logger.info(f"從 sidecar 載入文件類型: {doc_type}")

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

        if final_paths:
            self._update_global_index(base_output_dir, final_paths)
            output_paths['final'] = final_paths

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

    def _update_global_index(self, base_output_dir: Path, final_paths: Dict) -> None:
        paper_manager.update_papers_index(
            base_output_dir,
            self.paper_info['paper_id'],
            {k: str(v) for k, v in final_paths.items() if v}
        )

    # ── 各階段方法（與 pipeline.py 相同，只是移除 Qt 依賴） ──

    def _stage_pdf_to_md(self, pdf_path, paper_dir, paper_name, output_paths):
        markdown_path = self.pdf_processor.process(str(pdf_path), str(paper_dir))
        self.md_cleaner.clean(markdown_path)
        # 偵測文件類型，結果暫存供前端確認
        detection = self.doc_analyzer.detect_type(markdown_path)
        output_paths['_doc_type_detection'] = detection
        return markdown_path

    def _stage_analyze(self, pdf_path, paper_dir, paper_name, output_paths):
        markdown_path = output_paths.get('pdf2md')
        if not markdown_path:
            raise ValueError("未找到 Markdown 文件")
        doc_type = output_paths.get('_confirmed_doc_type', 'academic')
        return self.doc_analyzer.analyze(markdown_path, doc_type)

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
        return self.translate_processor.process(str(input_path), str(output_path))

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
        en_path, zh_path = self.restore_processor.process(
            str(input_path), str(paths['en']), str(paths['zh'])
        )
        return {'en': Path(en_path), 'zh': Path(zh_path)}

    def _stage_extra_info(self, pdf_path, paper_dir, paper_name, output_paths):
        input_path = output_paths.get('translate')
        if not input_path:
            raise ValueError("未找到翻譯 JSON 文件")
        output_path = self._get_stage_output_path('extra_info', paper_dir, paper_name)
        return self.extra_info_processor.process(str(input_path), str(output_path))

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