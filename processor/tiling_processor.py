import json
import logging
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from config import EmbeddingModel
from settings import TILING_BYPASS_CHAR_LIMIT, TILING_MAX_LENGTH


# Phase 4.7? MODEL-3 B2: 公式穿透合併支援（依 plan §4.2）
# SOFT_TYPES：可穿透合併（與 text 同 buffer）
SOFT_TYPES_FOR_MERGE = frozenset({'text', 'formula'})
# HARD_BOUNDARY：強制截斷（自身獨立 chunk）
HARD_BOUNDARY_TYPES_FOR_MERGE = frozenset({'table', 'heading', 'image_caption'})


def _join_content(prev_type: str, prev_text: str,
                  next_type: str, next_text: str) -> str:
    """根據兩個節點的 type 決定拼接字元、防禦 inline formula 排版災難。

    依 plan §3.5 修正 1：
    - text + text → "\\n\\n"（段落分隔）
    - text + formula 或 formula + text → " "（保留 inline、單空格）
    - formula + formula → " "（兩公式相鄰）

    避免「The value of $x$ is positive」被強制斷行成 3 個獨立段落。
    """
    if prev_type == 'text' and next_type == 'text':
        return prev_text + "\n\n" + next_text
    # 含 formula 至少一方、用空格
    return prev_text + " " + next_text


class TilingProcessor:
    """
    JSON文件分块处理器
    
    将处理后的JSON文件进行分割合并处理，为翻译阶段做准备
    使用向量相似度计算最佳切分点
    """
    
    def __init__(self, min_length: int = 500, max_length: int = None, window_size: int = 3, step_size: int = 1, embedder=None):
        """
        初始化平铺处理器

        Args:
            min_length: 文本块最小长度
            max_length: 文本块最大长度（修正 5：None → 從 env TILING_MAX_LENGTH 讀預設）
            window_size: 相似度计算窗口大小
            step_size: 滑动窗口步长
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.min_length = min_length
        # Phase 4.7? MODEL-3 修正 5: max_length=None → 從 env 讀預設；顯式傳值仍生效
        self.max_length = max_length if max_length is not None else TILING_MAX_LENGTH
        self.window_size = window_size
        self.step_size = step_size
        self.embedder = embedder if embedder is not None else EmbeddingModel.get_instance()
    
    def process(self, input_path: str, output_path: str, doc_type: str = '') -> Path:
        """
        处理JSON文件，将文本块进行合并分割处理

        Phase 4.7? MODEL-3 B1（依 plan §4.1）:
        - 若總字數 < TILING_BYPASS_CHAR_LIMIT（5000）→ bypass TextTiling
        - 否則 → 既有 _process_sections 流程

        Args:
            input_path: 输入JSON文件路径
            output_path: 输出JSON文件路径
            doc_type: 文件類型（B1 加：未來可做 doc_type 特例、本 commit 僅用於 log）

        Returns:
            Path: 输出文件路径
        """
        self.logger.info(
            f"开始处理JSON文件: 从 {input_path} 到 {output_path} "
            f"(doc_type={doc_type!r})"
        )

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # B1: 估算總字數、決定是否 bypass
        total_chars = self._estimate_total_chars(data)
        if total_chars < TILING_BYPASS_CHAR_LIMIT:
            self.logger.info(
                f"[tiling bypass] doc_type={doc_type!r} 總字數 {total_chars} < "
                f"{TILING_BYPASS_CHAR_LIMIT}、跳過 TextTiling 切割"
            )
            if 'sections' in data:
                self._bypass_sections(data['sections'])
        else:
            if 'sections' in data:
                self.logger.info(
                    f"开始处理文档sections，共 {len(data['sections'])} 个section "
                    f"(總字數 {total_chars})"
                )
                self._process_sections(data['sections'])
                self.logger.info("sections处理完成")

        # 保存处理后的JSON文件
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"处理完成，输出已保存到 {output_file}")
        return output_file

    def _estimate_total_chars(self, data) -> int:
        """估算 sections 內所有 text item 總字數（依 plan §4.1）。

        遞迴處理 children、跳過 abstract / references（同 _process_sections 既有邏輯）。
        """
        total = 0

        def walk(sections):
            nonlocal total
            for s in sections:
                if s.get('type') in ('abstract', 'references'):
                    continue
                for item in s.get('content', []):
                    if isinstance(item, dict) and item.get('type') == 'text':
                        total += len(item.get('content', '') or '')
                if s.get('children'):
                    walk(s['children'])

        walk(data.get('sections', []))
        return total

    def _bypass_sections(self, sections):
        """Bypass 模式：每個 section 內 text/formula 合併、其他原樣 pass-through。

        標記 tiling_method='bypass' 為未來除錯方便。
        遞迴處理 children、跳過 abstract / references。
        """
        for section in sections:
            if section.get('type') in ('abstract', 'references'):
                continue
            if 'content' in section:
                section['content'] = self._bypass_content(section['content'])
            if section.get('children'):
                self._bypass_sections(section['children'])

    def _bypass_content(self, content):
        """單 section 內：合併相鄰 text+formula、保留其他 type 與原始 index。

        依 plan §4.1（含修正 1 / 修正 2）：
        - 修正 1：用 _join_content 差異化拼接、防 inline formula 排版災難
        - 修正 2：保留原始 index、buffer 取被合併的第一個 item 原始 index、
                  non-text 絕不重寫 index（md_restore 依 (index, part) 排序對齊）
        """
        result = []
        buffer = None
        buffer_first_index = None
        buffer_last_appended_type = None  # 修正 1：追蹤最後合進 buffer 的 item 實際 type

        for item in content:
            if not isinstance(item, dict):
                if buffer is not None:
                    buffer['index'] = buffer_first_index
                    result.append(buffer)
                    buffer = None
                    buffer_first_index = None
                    buffer_last_appended_type = None
                result.append(item)
                continue

            item_type = item.get('type')

            if item_type in ('text', 'formula'):
                if buffer is None:
                    buffer = item.copy()
                    buffer_first_index = item.get('index', 0)
                    buffer_last_appended_type = item_type
                    buffer['part'] = 0
                    buffer['tiling_method'] = 'bypass'
                else:
                    # 修正 1：用「最後合進的實際 type」決定拼接、不是 buffer 總 type
                    buffer['content'] = _join_content(
                        buffer_last_appended_type,
                        buffer.get('content', '') or '',
                        item_type,
                        item.get('content', '') or ''
                    )
                    buffer_last_appended_type = item_type
            else:
                # non-text/formula：硬截斷 + 保留原始 index（修正 2）
                if buffer is not None:
                    buffer['index'] = buffer_first_index
                    result.append(buffer)
                    buffer = None
                    buffer_first_index = None
                    buffer_last_appended_type = None
                item_copy = item.copy()
                item_copy['part'] = 0
                # 修正 2：絕不重寫 item_copy['index']、保留原始
                result.append(item_copy)

        if buffer is not None:
            buffer['index'] = buffer_first_index
            result.append(buffer)

        return result
    
    def _process_sections(self, sections: List[Dict[str, Any]]) -> None:
        """
        处理sections列表，递归处理所有section内容，跳过abstract和references
        
        Args:
            sections: section列表
        """
        for section in sections:
            # 跳过abstract和references类型的section
            if section.get('type') in ['abstract', 'references']:
                self.logger.info(f"跳过处理section类型: {section.get('type')}")
                continue
                
            if 'content' in section:
                section['content'] = self._process_content(section['content'])
            
            # 递归处理子section
            if 'children' in section and section['children']:
                self._process_sections(section['children'])
    
    def _process_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理content列表，合并和分割文本块
        
        Args:
            content: content列表
            
        Returns:
            List[Dict[str, Any]]: 处理后的content列表
        """
        # 先检查是否需要合并相邻的小文本块
        content = self._merge_small_text_blocks(content)
        
        # 为每个块添加index和part标记
        for idx, item in enumerate(content):
            item['index'] = idx
            # 如果是未分割的块，part为0
            item['part'] = 0
        
        # 然后检查是否需要分割大文本块
        result = []
        for item in content:
            # B2: SOFT_TYPES (text + formula) > max_length 都走切割（公式罕見、但邊界一致）
            if item.get('type') in SOFT_TYPES_FOR_MERGE and len(item.get('content', '') or '') > self.max_length:
                # 获取原始索引
                original_index = item.get('index', 0)
                
                # 分割大文本块
                if '\n\n' in item['content']:
                    # 使用换行符分割策略
                    elements = item['content'].split('\n\n')
                    split_mode = "delimiter"
                else:
                    # 使用句子分割策略
                    elements = self._split_into_sentences(item['content'])
                    split_mode = "sentence"
                
                # 使用统一的TextTiling算法进行分割
                segments = self._texttiling(elements, split_mode)
                
                # 创建分割后的文本块
                split_blocks = []
                for i, segment_text in enumerate(segments):
                    new_block = item.copy()
                    new_block['content'] = segment_text
                    new_block['index'] = original_index
                    new_block['part'] = i
                    split_blocks.append(new_block)
                
                result.extend(split_blocks)
            else:
                result.append(item)
        
        return result
    
    def _merge_small_text_blocks(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并相邻的小文本块（含 formula 穿透合併）。

        依 plan §4.2 + §3.5 修正 1 + §3.7 修正 3：
        - 修正 1：用 _join_content 差異化拼接（text+formula 用空格、text+text 用 \\n\\n）
        - 修正 3：type=='formula' 無論長度都合進 buffer、不觸發 size-based flush
                  （LaTeX 字元數虛高、不應因「大文本」邏輯截斷上下文）
        - HARD_BOUNDARY_TYPES_FOR_MERGE（table / heading / image_caption）強制截斷

        Phase 4.7? MODEL-3 B2（依 plan §3.7）：
        LaTeX 源碼如「\\sum_{i=0}^{n} \\alpha_i \\cdot \\beta_i」字元數虛高、
        若按 size 判定可能誤觸 flush、把公式跟前後上下文截斷。
        解法：formula 無條件合進 buffer、不走 size 判定。

        Args:
            content: content列表

        Returns:
            List[Dict[str, Any]]: 处理后的content列表
        """
        if not content:
            return content

        result = []
        current_buffer = None
        buffer_last_appended_type = None  # 修正 1：追蹤最後合進 buffer 的實際 type

        for item in content:
            item_type = item.get('type')

            # 修正 3：formula 無條件合併（不走 size 判定）
            if item_type == 'formula':
                text = item.get('content', '') or ''
                if current_buffer is None:
                    current_buffer = item.copy()
                    buffer_last_appended_type = 'formula'
                else:
                    # 修正 1：用最後合進的實際 type 拼接
                    current_buffer['content'] = _join_content(
                        buffer_last_appended_type,
                        current_buffer.get('content', '') or '',
                        'formula', text
                    )
                    buffer_last_appended_type = 'formula'
                continue

            if item_type == 'text':
                text = item.get('content', '') or ''
                if len(text) < self.min_length:
                    # 小 text、合進 buffer
                    if current_buffer is None:
                        current_buffer = item.copy()
                        buffer_last_appended_type = 'text'
                    else:
                        # 修正 1：差異化拼接
                        current_buffer['content'] = _join_content(
                            buffer_last_appended_type,
                            current_buffer.get('content', '') or '',
                            'text', text
                        )
                        buffer_last_appended_type = 'text'
                else:
                    # 大 text、合 buffer 後 emit
                    if current_buffer is not None:
                        current_buffer['content'] = _join_content(
                            buffer_last_appended_type,
                            current_buffer.get('content', '') or '',
                            'text', text
                        )
                        result.append(current_buffer)
                        current_buffer = None
                        buffer_last_appended_type = None
                    else:
                        result.append(item)
            else:
                # 硬邊界（table / heading / image_caption / 其他 unknown type）
                # 為相容、未知 type 也視為 hard boundary
                if current_buffer is not None:
                    result.append(current_buffer)
                    current_buffer = None
                    buffer_last_appended_type = None
                result.append(item)

        if current_buffer is not None:
            result.append(current_buffer)

        return result
    
    def _texttiling(self, elements: List[str], split_mode: str = "sentence") -> List[str]:
        """
        通用的TextTiling算法实现
        
        Args:
            elements: 文本元素列表（可以是句子或分隔符分割的部分）
            split_mode: 分割模式，"sentence"或"delimiter"
            
        Returns:
            List[str]: 分段结果文本列表
        """
        # 如果元素数量不足，直接返回合并后的文本
        if len(elements) < self.window_size + 2:
            combined_text = ' '.join(elements) if split_mode == "sentence" else '\n\n'.join(elements)
            return [combined_text]
        
        # 创建文本块（窗口）
        blocks = []
        for i in range(0, len(elements) - self.window_size + 1, self.step_size):
            window = elements[i:i + self.window_size]
            if split_mode == "sentence":
                blocks.append(' '.join(window))
            else:  # delimiter mode
                blocks.append('\n'.join(window))
        
        # 计算每个块的嵌入向量 - 使用统一的EmbeddingModel
        embedding_model = self.embedder
        block_embeddings = [embedding_model.embed_query(block) for block in blocks]
        
        # 计算相邻块之间的相似度
        similarities = [float(np.dot(block_embeddings[i], block_embeddings[i+1]) / (np.linalg.norm(block_embeddings[i]) * np.linalg.norm(block_embeddings[i+1]) + 1e-8)) 
                        for i in range(len(block_embeddings)-1)]
        
        # 计算深度分数
        depth_scores = [0] * len(elements)
        for i in range(1, len(similarities)-1):
            depth = (similarities[i-1] + similarities[i+1] - 2*similarities[i]) / 2
            depth_scores[i+self.window_size//2] = depth
        
        # 计算阈值
        depth_values = [d for d in depth_scores if d > 0]
        if depth_values:
            mean_depth = np.mean(depth_values)
            std_depth = np.std(depth_values)
            threshold = mean_depth + 0.4 * std_depth
        else:
            threshold = 0
        
        # 找出潜在的边界
        potential_boundaries = [i for i, score in enumerate(depth_scores) if score > threshold]
        
        # 找到最优分段
        segments = []
        start = 0
        
        while start < len(elements):
            optimal_boundary = self._find_optimal_boundary(start, elements, potential_boundaries, depth_scores)
            
            if split_mode == "sentence":
                segment_text = ' '.join(elements[start:optimal_boundary+1])
            else:  # delimiter mode
                segment_text = '\n'.join(elements[start:optimal_boundary+1])
            
            segments.append(segment_text)
            start = optimal_boundary + 1
        
        # 处理最后一个段落如果太小
        if segments and len(segments[-1]) < self.min_length and len(segments) > 1:
            last_segment = segments.pop()
            if split_mode == "sentence":
                segments[-1] += " " + last_segment
            else:  # delimiter mode
                segments[-1] += "\n" + last_segment
        
        return segments
    
    def _find_optimal_boundary(self, start: int, elements: List[str], 
                               potential_boundaries: List[int], depth_scores: List[float]) -> int:
        """
        找到最优的段落边界
        
        Args:
            start: 起始位置
            elements: 元素列表（句子或分隔部分）
            potential_boundaries: 潜在边界列表
            depth_scores: 深度分数列表
            
        Returns:
            int: 最优边界的索引
        """
        current_length = 0
        candidate_boundaries = []
        
        for i in range(start, len(elements)):
            current_length += len(elements[i])
            if self.min_length <= current_length <= self.max_length:
                if i in potential_boundaries:
                    candidate_boundaries.append((i, depth_scores[i]))
            if current_length > self.max_length:
                break
        
        if not candidate_boundaries:
            # 找一个长度接近目标的位置
            target_length = (self.min_length + self.max_length) / 2
            return min(range(start, min(len(elements), start + 10)), 
                      key=lambda i: abs(sum(len(e) for e in elements[start:i+1]) - target_length))
        
        # 选择深度分数最高的边界
        best_boundary = max(candidate_boundaries, key=lambda x: x[1])
        return best_boundary[0]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子（支持中英文）
        
        Args:
            text: 待分割的文本
            
        Returns:
            List[str]: 句子列表
        """
        # 中英文句子结束标志
        sentence_pattern = re.compile(r'(?<=[。！？?!.;；])')
        sentences = [s.strip() for s in re.split(sentence_pattern, text) if s.strip()]
        
        return sentences