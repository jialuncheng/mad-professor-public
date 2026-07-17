import json
import logging
import re
from pathlib import Path
from typing import Tuple, Dict, List, Any, Optional
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from config import EmbeddingModel
from utils.text_utils import load_caption_map

# Phase 4.7d Commit 15-1：短文 doc_type 合併同 section 內 text items
# === doc_type-registry ===
# 新增 doc_type 須評估是否屬於「短文型」（短條列、每 item 文字少、合併
# 後 chunk 不致於過大稀釋 embedding signal）。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
_SHORT_DOC_TYPES = frozenset({'resume', 'slides', 'news', 'web'})

# Phase 4.7? MODEL-8 C1: chunk filter 邏輯版本錨點（依 plan §3.1）
# 對應 MODEL-1+2 B2 _is_chunk_meaningful 過濾邏輯（L35-81）
# 用於 paper_chunks.chunk_filter_version + 未來 index_meta.json
# 未來改動 _is_chunk_meaningful 邏輯時、bump 此字串
CHUNK_FILTER_VERSION = 'B2-2026-05-22'

# Phase 4.7? MODEL-1+2 階段 B2: chunk 過濾規則
# plan §4.2 + §3.6.2 修正 2 markdown 噪聲 + §3.6.4 修正 4 履歷防誤殺
MIN_CHUNK_CONTENT_CHARS = 10
MIN_CHUNK_RESUME_SLIDES = 3  # 修正 4：resume/slides 放寬到 3 字元（保 Python/Docker 等）

# 修正 2：移除非實質字元計算 chunk 字數（純標題 / 分隔線會被過濾）
_MD_NOISE_RE = re.compile(r"[#*_~`\-+>|\[\]\s]")
# 修正 4：純數字（年份、頁碼）過濾
_PURE_DIGIT_RE = re.compile(r"^\d+$")
# 修正 4：合併 email / phone / url 為單一 regex（含結構化資訊保留、不論長度）
_CRITICAL_INFO_RE = re.compile(
    r"([\w.+-]+@[\w-]+\.[\w.-]+"     # email
    r"|\+?\d[\d\s\-]{6,}\d"           # phone（國際電話格式）
    r"|https?://\S+)"                 # url
)


def _is_chunk_meaningful(doc, doc_type: str = "") -> bool:
    """判定 chunk 是否有實質內容值得入向量庫。

    過濾規則（依優先序）：
    1. 空字串 → 過濾
    2. 純數字（如年份「2024」）→ 過濾
    3. 含 email / phone / url 結構化資訊 → 保留（不論長度、修正 4）
    4. doc_type 'resume' / 'slides' → 放寬到 ≥ 3 實質字元（修正 4）
    5. 其他 doc_type → ≥ 10 實質字元

    「實質字元」= 移除 markdown 符號（# * _ ~ ` - + > | [ ] 與空白）後字元數（修正 2）。

    範例：
    - `""` → 過濾（空）
    - `"2024"` → 過濾（純數字）
    - `"PhD"` → 過濾（純標籤、3 字元但非 resume/slides）
    - `"Python"` + doc_type='resume' → 保留（技能詞、≥ 3）
    - `"## Summary\\n---"` → 過濾（11 字元、實質 7 字元、< 10）
    - `"john@example.com"` → 保留（含 email）
    - `"Education content here"` → 保留（≥ 10）

    Args:
        doc: LangChain Document（含 .page_content + .metadata）
        doc_type: 'academic' / 'resume' / 'slides' / ...

    Returns:
        True 保留 / False 過濾
    """
    text = (doc.page_content or "").strip()

    if not text:
        return False

    # 修正 4：含結構化資訊保留（不論長度、優先於純數字判定、避免誤殺長數字電話）
    if _CRITICAL_INFO_RE.search(text):
        return True

    # 修正 4：純數字過濾（短數字如年份「2024」、長數字未匹配 phone regex）
    if _PURE_DIGIT_RE.match(text):
        return False

    # 修正 2：移除 markdown 噪聲後計算實質字元數
    clean_text = _MD_NOISE_RE.sub("", text)

    if doc_type in ("resume", "slides"):
        return len(clean_text) >= MIN_CHUNK_RESUME_SLIDES
    return len(clean_text) >= MIN_CHUNK_CONTENT_CHARS


# Phase 4.7? MODEL-8 C2 修正 4: index_meta.json 寫入（module-level、CLI + RagProcessor 共用）
# 依 plan §3.2 + 修正 4。
def write_index_meta_json(vector_store_path, chunks_total: int, logger=None) -> None:
    """寫 vectors/index_meta.json、為 regen_rag --check mismatch 偵測用。

    依 plan §3.2 + 修正 4（module-level、CLI tools/regen_rag.py + RagProcessor 共用）。

    Args:
        vector_store_path: vectors/ 物理路徑（Path 或 str）
        chunks_total: 寫入 FAISS 的 chunks 數量
        logger: 可選 logger（傳入時印 info、否則靜默）
    """
    from settings import (
        EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS,
        TILING_BYPASS_CHAR_LIMIT, TILING_MAX_LENGTH, TILING_PARAGRAPH_THRESHOLD,
    )
    from datetime import datetime, timezone

    meta = {
        "embedding_model": EMBEDDING_MODEL_NAME,
        "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
        "chunk_filter_version": CHUNK_FILTER_VERSION,
        "tiling_config_signature": {
            "TILING_BYPASS_CHAR_LIMIT": TILING_BYPASS_CHAR_LIMIT,
            "TILING_MAX_LENGTH": TILING_MAX_LENGTH,
            "TILING_PARAGRAPH_THRESHOLD": TILING_PARAGRAPH_THRESHOLD,
        },
        "chunks_total": chunks_total,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rag_processor_version": "MODEL-8-C2",
    }
    meta_path = Path(vector_store_path) / "index_meta.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    if logger:
        logger.info(
            f"[index_meta] 已寫入 {meta_path}（model={EMBEDDING_MODEL_NAME}、"
            f"dim={EMBEDDING_OUTPUT_DIMENSIONS}、chunks={chunks_total}）"
        )


class RagProcessor:
    """RAG 处理器：将 JSON 转换为 Markdown 和符合检索需求的JSON树结构，并生成向量库"""

    def __init__(self, embedder=None):
        """初始化 RAG 处理器"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.embedder = embedder if embedder is not None else EmbeddingModel.get_instance()

    def process(self, input_path: str, output_md_path: str, output_tree_json_path: str,
                vector_store_path: str, images_info_path: str = None,
                doc_type: str = '', paper_db_id: Optional[int] = None) -> Tuple[str, str, str]:
        """处理 JSON 文件，生成 Markdown、JSON以及向量库

        Args:
            input_path: 输入JSON文件路径
            output_md_path: 输出的Markdown文件路径
            output_tree_json_path: 输出的树结构JSON文件路径
            vector_store_path: 向量库存储路径
            images_info_path: Vision 生成的圖片說明檔案路徑（可選）
            doc_type: 文件類型（Phase 4.7d Commit 15-1）；用於 chunk 內容
                Context 前綴與短文 doc_type 合併。預設 '' 行為等效既有。
            paper_db_id: Phase 4.7? MODEL-8 C2（依 plan §3.3）；Paper.id (INT PK)
                供 _write_paper_chunks_to_db 寫入 paper_chunks 表用。
                None → 優雅降級（log warning、跳過 SQL 寫入、可後續 --init 修補、Q13）。

        Returns:
            Tuple[str, str, str]: Markdown文件路径, JSON文件路径, 向量库路径
        """
        self.logger.info(f"开始处理 RAG 数据: {input_path}")
        self.caption_map = load_caption_map(images_info_path) if images_info_path else {}

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                paper_data = json.load(f)

            # 提取摘要并放入 summary 字段
            abstract_content = self._extract_abstract_summary(paper_data.get("sections", []))
            paper_data["abstract"] = {
                "content": abstract_content.get("content", ""),
                "translated_content": abstract_content.get("translated_content", "")
            }
            
            # 移除 sections 中的 abstract 和 references
            paper_data["sections"] = self._filter_sections(paper_data.get("sections", []))
            
            # 重构树结构
            paper_data = self._restructure_tree(paper_data)
            
            # 生成树结构 JSON
            with open(output_tree_json_path, "w", encoding="utf-8") as f:
                json.dump(paper_data, f, ensure_ascii=False, indent=2)

            # 生成 Markdown 文件
            self._generate_markdown(paper_data, output_md_path, doc_type=doc_type)

            # 为 Markdown 文件创建向量库（Phase 4.7? MODEL-1+2 B2：傳 doc_type 供 chunk filter 用）
            # MODEL-8 C2（plan §3.3）：轉發 paper_db_id 供 _write_paper_chunks_to_db 寫入用
            self._create_vector_store(
                output_md_path, vector_store_path,
                doc_type=doc_type, paper_db_id=paper_db_id,
            )

            self.logger.info("RAG 数据处理完成")
            return output_md_path, output_tree_json_path, vector_store_path

        except Exception as e:
            self.logger.error(f"RAG 处理失败: {str(e)}", exc_info=True)
            raise

    def _create_vector_store(self, md_path: str, vector_store_path: str,
                             doc_type: str = '',
                             paper_db_id: Optional[int] = None) -> str:
        """
        为 Markdown 文件创建向量库

        Args:
            md_path: Markdown 文件路径
            vector_store_path: 向量库存储路径
            doc_type: 文件類型（Phase 4.7? MODEL-1+2 B2、傳給 _is_chunk_meaningful
                      決定字元下限：resume/slides ≥ 3、其他 ≥ 10）
            paper_db_id: Phase 4.7? MODEL-8 C2（plan §3.3）；Paper.id (INT PK)。
                FAISS save_local 後寫 paper_chunks 表 + 永遠寫 index_meta.json。
                None → 優雅降級（log warning、跳過 SQL 寫入、Q13）。

        Returns:
            str: 向量库路径
        """
        self.logger.info(f"开始为 Markdown 创建向量库: {md_path}")
        
        # 确保向量库存储路径存在
        vector_store_path_obj = Path(vector_store_path)
        vector_store_path_obj.mkdir(parents=True, exist_ok=True)
        
        # 读取 Markdown 文件
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 使用 Markdown 标题分割文档
        # 按一级标题分割，这些通常是节点的 key
        headers_to_split_on = [("#", "Header")]
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = md_splitter.split_text(content)
        
        self.logger.info(f"分割后得到 {len(docs)} 个文档片段")

        # Phase 4.7? MODEL-1+2 階段 B2: chunk filter（plan §4.2 + §3.6 修正 2/4）
        meaningful_docs = []
        filtered = []
        for d in docs:
            if _is_chunk_meaningful(d, doc_type=doc_type):
                meaningful_docs.append(d)
            else:
                filtered.append(d)

        if filtered:
            # baron 補充二：印前 15 字元便於調試誤殺
            preview = ", ".join(
                f'"{(d.page_content or "")[:15]}..."' for d in filtered[:5]
            )
            suffix = f" ... 共 {len(filtered)} 個" if len(filtered) > 5 else ""
            self.logger.info(
                f"[chunk filter] 過濾 {len(filtered)}/{len(docs)} 個短 chunk "
                f"(doc_type={doc_type!r}、resume/slides ≥{MIN_CHUNK_RESUME_SLIDES} / 其他 ≥{MIN_CHUNK_CONTENT_CHARS}、純數字 + markdown 噪聲過濾): "
                f"{preview}{suffix}"
            )

        # 创建向量存储
        vector_store = FAISS.from_documents(
            documents=meaningful_docs,
            embedding=self.embedder,
            distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
        )
        
        # 保存向量存储
        vector_store.save_local(str(vector_store_path_obj))

        # === MODEL-8 C2 新增（依 plan §3.3 + §3.2、Q12 / Q13）===
        # paper_chunks 寫入：raw_text 物理防線、升 embedding 時不需重 PDF
        if paper_db_id is not None:
            try:
                self._write_paper_chunks_to_db(
                    meaningful_docs, paper_db_id, doc_type
                )
            except Exception as e:
                # Q12: 不 rollback FAISS save_local（不可逆）、log error + 後續 --init 修補
                self.logger.error(
                    f"[paper_chunks] 寫入失敗（不阻塞主流程）: {e}",
                    exc_info=True,
                )
        else:
            # Q13: 優雅降級——測試環境 / 既有 resume pipeline 無 paper_db_id
            self.logger.warning(
                "[paper_chunks] paper_db_id 未提供、跳過寫入 SQLite "
                "(可由 tools/regen_rag.py --init 事後補完)"
            )

        # index_meta.json 永遠寫（版本標記、供 regen_rag --check 用）
        try:
            write_index_meta_json(
                vector_store_path_obj,
                len(meaningful_docs),
                logger=self.logger,
            )
        except Exception as e:
            self.logger.error(
                f"[index_meta] 寫入失敗（不阻塞主流程）: {e}",
                exc_info=True,
            )
        # === MODEL-8 C2 新增 end ===

        self.logger.info(f"向量库创建完成: {vector_store_path_obj}")
        return str(vector_store_path_obj)

    def _write_paper_chunks_to_db(self, docs: List[Any], paper_db_id: int,
                                   doc_type: str) -> None:
        """將 meaningful_docs 批次寫入 paper_chunks 表（C2、依 plan §3.3）。

        依 plan §3.3（含修正 3：rows 無 tiling_method 欄位）+ Q14（translated_text=None）。

        Args:
            docs: list of langchain.Document（FAISS.from_documents 的輸入、meaningful_docs）
            paper_db_id: Paper.id（INT PK）
            doc_type: 'academic' / 'resume' / 'slides' / ...
        """
        from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS
        import paper_manager

        rows = []
        for i, d in enumerate(docs):
            # chunk_key 從 metadata 取（MarkdownHeaderTextSplitter 加注的 Header）
            chunk_key = (d.metadata or {}).get('Header', '') or f"chunk_{i}"
            rows.append({
                "chunk_index": i,
                "chunk_key": chunk_key[:255],  # 防 Header 超長
                "raw_text": d.page_content or '',
                "translated_text": None,  # Q14：本 commit 不填、未來 C4/C5 補 translation cache
                "doc_type": doc_type or '',
                "metadata_json": json.dumps(
                    d.metadata or {}, ensure_ascii=False
                ),
                "embedding_model": EMBEDDING_MODEL_NAME,
                "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
                "chunk_filter_version": CHUNK_FILTER_VERSION,
            })

        n = paper_manager.replace_paper_chunks(paper_db_id, rows)
        self.logger.info(
            f"[paper_chunks] 寫入 {n} 個 chunks "
            f"(paper_db_id={paper_db_id}, "
            f"model={EMBEDDING_MODEL_NAME}, dim={EMBEDDING_OUTPUT_DIMENSIONS})"
        )

    def _extract_abstract_summary(self, sections: List[Dict]) -> Dict[str, str]:
        """提取摘要，同时返回原文和翻译内容"""
        for section in sections:
            if section.get("type") == "abstract":
                content = []
                translated_content = []
                for item in section.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        content.append(item.get("content", ""))
                        translated_content.append(item.get("translated_content", ""))
                return {
                    "content": "\n".join(content),
                    "translated_content": "\n".join(translated_content)
                }
        return {"content": "", "translated_content": ""}

    def _filter_sections(self, sections: List[Dict]) -> List[Dict]:
        """过滤掉 abstract 和 references 类型的章节"""
        filtered_sections = []
        for section in sections:
            if section.get("type") != "abstract" and section.get("type") != "references":
                filtered_sections.append(section)
        return filtered_sections

    def _restructure_tree(self, paper_data: Dict) -> Dict:
        """重构树结构，移除不需要的字段，重新标注索引和层级"""
        # 重新标注节点的 level 和 index
        restructured_sections = self._restructure_sections(paper_data.get("sections", []), level=1)
        
        # 重构后的 paper_data
        restructured_paper = {
            "title": paper_data.get("title", ""),
            "translated_title": paper_data.get("translated_title", ""),
            "summary": paper_data.get("summary", ""),
            "abstract": {
                "content": paper_data.get("abstract", {}).get("content", ""),
                "translated_content": paper_data.get("abstract", {}).get("translated_content", "")
            },
            "sections": restructured_sections
        }
        
        # 根据重构后的树生成 key_map
        restructured_paper["key_map"] = self._generate_key_map(restructured_sections, paper_data.get("title", ""))
        
        return restructured_paper

    def _restructure_sections(self, sections: List[Dict], level: int) -> List[Dict]:
        """递归重构章节，移除不需要的字段，重新标注索引和层级"""
        restructured_sections = []
        
        for i, section in enumerate(sections):
            # 创建新的章节字典，仅保留需要的字段
            new_section = {
                "title": section.get("title", ""),
                "translated_title": section.get("translated_title", ""),
                "level": level,
                "summary": section.get("summary", ""),
                "content": []
            }
            
            # 处理内容，重新标注索引
            content_index = 0
            for item in section.get("content", []):
                if isinstance(item, dict):
                    new_item = {
                        "type": item.get("type", ""),
                        "index": content_index
                    }
                    
                    # 根据内容类型保留相应字段
                    if item.get("type") == "text":
                        new_item["content"] = item.get("content", "")
                        new_item["translated_content"] = item.get("translated_content", "")
                        new_item["questions"] = item.get("questions", "")
                    elif item.get("type") == "figure":
                        src = item.get("src", "")
                        new_item["src"] = src
                        new_item["alt"] = item.get("alt", "")
                        # 優先用原始 caption，沒有則從 images_info.md 補充
                        caption = item.get("caption", "") or item.get("translated_caption", "")
                        if not caption and hasattr(self, "caption_map"):
                            caption = self.caption_map.get(src, "")
                        new_item["caption"] = caption
                        new_item["translated_caption"] = item.get("translated_caption", "") or caption
                        new_item["questions"] = item.get("questions", "")
                    elif item.get("type") == "table":
                        new_item["content"] = item.get("content", "")
                        new_item["caption"] = item.get("caption", "")
                        new_item["translated_caption"] = item.get("translated_caption", "")
                        new_item["questions"] = item.get("questions", "")
                    elif item.get("type") == "formula":
                        new_item["content"] = item.get("content", "")
                        new_item["formula_analysis"] = item.get("formula_analysis", "")
                    
                    new_section["content"].append(new_item)
                    content_index += 1
            
            # 处理子章节
            if "children" in section and section["children"]:
                new_section["children"] = self._restructure_sections(section.get("children", []), level + 1)
            else:
                new_section["children"] = []
            
            restructured_sections.append(new_section)
        
        return restructured_sections

    def _generate_key_map(self, sections: List[Dict], title: str, parent_path="", parent_json_path="") -> Dict[str, str]:
        """
        生成 key_map，关键路径映射表
        """
        key_map = {}
        
        for i, section in enumerate(sections):
            section_title = section.get("title", "")
            
            # 构建语义路径和JSON路径
            section_path = f"{parent_path}/{section_title}" if parent_path else section_title
            current_json_path = f"{parent_json_path}/sections/{i}" if not parent_json_path else f"{parent_json_path}/{i}"
            
            # 添加章节的映射
            section_key = f"{title}/{section_path}/section"
            key_map[section_key] = current_json_path
            
            # 为内容生成键
            for j, item in enumerate(section.get("content", [])):
                content_key = f"{section_key}/{j}/{item.get('type', '')}"
                key_map[content_key] = f"{current_json_path}/content/{j}"
            
            # 处理子章节，传递正确的JSON路径
            if section.get("children"):
                # 创建子章节的JSON路径，确保包含children层级
                children_json_path = f"{current_json_path}/children"
                child_key_map = self._generate_key_map(
                    section.get("children", []),
                    title,
                    section_path,
                    children_json_path
                )
                key_map.update(child_key_map)
        
        return key_map

    def _get_node_by_json_path(self, json_path: str, json_data: Dict) -> Any:
        """根据 JSON 路径获取节点，增强错误处理和日志记录"""
        if not json_path:
            self.logger.warning(f"空JSON路径")
            return None
            
        keys = json_path.strip("/").split("/")
        node = json_data
        
        try:
            for i, key in enumerate(keys):
                if isinstance(node, list):
                    try:
                        key = int(key)
                        if 0 <= key < len(node):
                            node = node[key]
                        else:
                            self.logger.warning(f"索引越界: {key}, 路径: {json_path}, 位置: {i+1}/{len(keys)}")
                            return None
                    except (ValueError, IndexError):
                        self.logger.warning(f"无效的列表索引: {key}, 路径: {json_path}, 位置: {i+1}/{len(keys)}")
                        return None
                elif isinstance(node, dict):
                    if key in node:
                        node = node[key]
                    else:
                        self.logger.warning(f"键不存在: {key}, 路径: {json_path}, 位置: {i+1}/{len(keys)}")
                        return None
                else:
                    self.logger.warning(f"无法继续导航, 节点类型: {type(node)}, 路径: {json_path}, 位置: {i+1}/{len(keys)}")
                    return None
        except Exception as e:
            self.logger.error(f"解析JSON路径时出错: {json_path}, 错误: {str(e)}")
            return None
            
        return node

    def _extract_section_title(self, key: str) -> str:
        """從 key 路徑萃取 section title（去掉 paper_title 前綴 + /section/... 尾段）。

        Phase 4.7d Commit 15-1：給 _generate_md_content Context 前綴用。

        範例：
          'DeHunt Resume/Working Experience/section'
            → 'Working Experience'
          'DeHunt Resume/Working Experience/section/0/text'
            → 'Working Experience'
          'DeHunt Resume/Working Experience/VIEWTRIX/section'
            → 'Working Experience > VIEWTRIX'
        """
        if not key:
            return ''
        parts = key.split('/')
        if len(parts) < 2:
            return ''
        # 去 paper_title (parts[0])
        middle = parts[1:]
        cleaned = []
        _LEAF_MARKERS = ('section', 'text', 'figure', 'table', 'formula')
        for p in middle:
            if p in _LEAF_MARKERS or p.isdigit():
                break
            cleaned.append(p)
        return ' > '.join(cleaned)

    def _try_merge_text_items(self, section: Dict, tree: Dict,
                              doc_type: str, sec_idx: int,
                              ch_idx: Optional[int] = None
                              ) -> Optional[Tuple[str, str]]:
        """嘗試合併 section 內所有 text items 為單一 chunk。
        Phase 4.7d Commit 15-1 D：對短文 doc_type 套用、解 plan §2 問題 #4。

        Returns:
            (merged_key, full_markdown) 或 None（< 2 個 text items / 全空）
        """
        text_items = [i for i in section.get('content', []) if i.get('type') == 'text']
        if len(text_items) <= 1:
            return None  # 只 1 個或更少、不必合併

        pieces = []
        for item in text_items:
            c = (item.get('translated_content') or item.get('content') or '').strip()
            if c:
                pieces.append(c)
        if not pieces:
            return None
        combined = "\n\n".join(pieces)

        section_title = section.get('translated_title') or section.get('title', '')
        paper_title = tree.get('translated_title') or tree.get('title', '')

        # merged_key 走 _merged 後綴避免跟 per-item chunk key 衝突
        if ch_idx is None:
            merged_key = f"{paper_title}/{section_title}/section/_merged"
        else:
            parent = (tree.get('sections') or [{}])[sec_idx]
            parent_title = parent.get('translated_title') or parent.get('title', '')
            merged_key = f"{paper_title}/{parent_title}/{section_title}/section/_merged"

        ctx_section = self._extract_section_title(merged_key)
        md = f"# {merged_key}\n"
        if doc_type or ctx_section:
            md += f"Context: {' > '.join(b for b in (doc_type, ctx_section) if b)}\n\n"
        md += combined
        return (merged_key, md)

    def _item_key(self, paper_title: str, section_title: str,
                  child_title: Optional[str], idx: int, item_type: str) -> str:
        """重建 per-item chunk 的 key（與 _generate_key_map 一致）、用於 merge 後標記跳過。"""
        if child_title is None:
            return f"{paper_title}/{section_title}/section/{idx}/{item_type}"
        return f"{paper_title}/{section_title}/{child_title}/section/{idx}/{item_type}"

    def _generate_markdown(self, tree_structure: Dict, output_path: str,
                           doc_type: str = ''):
        """生成 Markdown 文件，按节点 key 组织内容，并增强错误处理。

        Phase 4.7d Commit 15-1：
        - 加 doc_type 參數、進入 _generate_md_content 傳遞、用於 Context 前綴
        - 短文 doc_type ∈ _SHORT_DOC_TYPES 時、合併同 section 多 text items
          為單一 chunk（plan §2 問題 #4）；merged keys 標記跳過原 per-item 處理
        """
        self.logger.info(f"生成 Markdown 文件: {output_path} (doc_type={doc_type!r})")

        is_short_doc = doc_type in _SHORT_DOC_TYPES
        merged_skip_keys: set = set()

        with open(output_path, "w", encoding="utf-8") as f:
            paper_title = tree_structure.get("title", "")

            # 先检查并记录所有未找到的节点
            missing_nodes = []
            for key, json_path in tree_structure.get("key_map", {}).items():
                node = self._get_node_by_json_path(json_path, tree_structure)
                if not node:
                    missing_nodes.append((key, json_path))

            if missing_nodes:
                self.logger.warning(f"找不到以下节点: {missing_nodes[:10]} {'...' if len(missing_nodes) > 10 else ''}")

            # Phase 4.7d Commit 15-1 D：短文 doc_type 先寫合併 chunk、記錄跳過 keys
            if is_short_doc:
                sections = tree_structure.get('sections') or []
                for sec_idx, section in enumerate(sections):
                    section_title = (section.get('translated_title') or
                                     section.get('title', ''))
                    merged = self._try_merge_text_items(
                        section, tree_structure, doc_type, sec_idx
                    )
                    if merged:
                        _, merged_md = merged
                        f.write(merged_md + "\n\n")
                        for j, item in enumerate(section.get('content', []) or []):
                            if item.get('type') == 'text':
                                merged_skip_keys.add(
                                    self._item_key(paper_title, section_title,
                                                   None, j, 'text')
                                )
                    # 一級 children 也試合併
                    for ch_idx, child in enumerate(section.get('children', []) or []):
                        ch_title = (child.get('translated_title') or
                                    child.get('title', ''))
                        ch_merged = self._try_merge_text_items(
                            child, tree_structure, doc_type, sec_idx, ch_idx
                        )
                        if ch_merged:
                            _, ch_md = ch_merged
                            f.write(ch_md + "\n\n")
                            for j, item in enumerate(child.get('content', []) or []):
                                if item.get('type') == 'text':
                                    merged_skip_keys.add(
                                        self._item_key(paper_title, section_title,
                                                       ch_title, j, 'text')
                                    )

            # 遍历 key_map 生成 Markdown 内容
            for key, json_path in tree_structure.get("key_map", {}).items():
                if key in merged_skip_keys:
                    continue  # Commit 15-1 D：已合併、跳過原 per-item
                node = self._get_node_by_json_path(json_path, tree_structure)

                if not node:
                    # 已在上面记录了，这里不再重复记录
                    continue

                section_title = self._extract_section_title(key)
                md_content = self._generate_md_content(
                    node, key, doc_type=doc_type, section_title=section_title
                )
                if md_content:
                    f.write(md_content + "\n\n")
                else:
                    self.logger.warning(f"无法为节点生成Markdown内容: {key}, 路径: {json_path}")

            self.logger.info(f"Markdown文件生成完成: {output_path}")

    def _generate_md_content(self, node: Dict, key: str,
                             doc_type: str = '',
                             section_title: str = '') -> str:
        """
        生成 Markdown 内容，宽松化条件以处理更多类型的内容。

        Phase 4.7d Commit 15-1：
        - 新增 doc_type / section_title 參數；皆有提供時、chunk 內容開頭加
          一行「Context: {doc_type} > {section_title}」，讓 embedding 拿到
          語意脈絡（解 plan §2 問題 #3）。預設 '' 行為等效既有。
        - 空 summary section 改返回 None 跳過（解 plan §2 問題 #1）。
        """
        md_content = f"# {key}\n"
        # Phase 4.7d Commit 15-1：Context 前綴
        ctx_bits = [b for b in (doc_type, section_title) if b]
        if ctx_bits:
            md_content += f"Context: {' > '.join(ctx_bits)}\n\n"

        # 不同类型的节点生成不同的内容
        if "summary" in node and "/section" in key:
            # Commit 15-1 A：空 summary 跳過（plan §2 問題 #1）
            summary = (node.get('summary') or '').strip()
            if not summary:
                return None
            md_content += summary
            return md_content

        if node.get("type") == "text":
            questions = node.get("questions", "")
            # 首先尝试使用translated_content，如果没有则使用content
            content = node.get("translated_content", "")
            if not content:
                content = node.get("content", "")
            
            if questions or content:
                md_content += f"{questions}\n{content}"
                return md_content
        
        if node.get("type") == "figure":
            questions = node.get("questions", "")
            # 尝试使用translated_caption，如果没有则使用caption
            caption = node.get("translated_caption", "")
            if not caption:
                caption = node.get("caption", "")
                
            if questions or caption:
                md_content += f"{questions}\n{caption}"
                return md_content
            
        if node.get("type") == "table":
            questions = node.get("questions", "")
            # 尝试使用translated_caption，如果没有则使用caption
            caption = node.get("translated_caption", "")
            if not caption:
                caption = node.get("caption", "")
                
            if questions or caption:
                md_content += f"{questions}\n{caption}"
                return md_content
        
        if node.get("type") == "formula":
            formula_content = node.get("content", "")
            formula_analysis = node.get("formula_analysis", "")
            
            if formula_content or formula_analysis:
                md_content += f"{formula_content}\n{formula_analysis}"
                return md_content
        
        # 如果节点是章节而不是内容项
        if "title" in node and "level" in node:
            title = node.get("title", "")
            translated_title = node.get("translated_title", "")
            summary = node.get("summary", "")
            
            if title or translated_title or summary:
                content = ""
                if title:
                    content += f"**{title}**"
                if translated_title and translated_title != title:
                    content += f" ({translated_title})"
                if summary:
                    content += f"\n\n{summary}"
                
                md_content += content
                return md_content
        
        return ""