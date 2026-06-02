"""PIPE-CORE PipelineFactory 策略工廠（plan v2 U3）。

`doc_type → DocumentStrategy` 註冊/查找機制。未命中一律降級 LiteDoc 路（SPEC §3.3
最後防線）；骨架階段尚無任何具體策略註冊時，回 `NullStrategy` 哨兵（防靜默通過）。

主幹（Orchestrator）只呼叫 `PipelineFactory.get_strategy(doc_type)`，**零 doc_type 字面量分支**。

本檔為 PIPE-CORE OP-2 交付物，**不附任何具體五路策略實作**（五路自行 register）。
"""

from __future__ import annotations

import logging
from typing import Dict, Type

from pipelines.base_strategy import DocumentStrategy, NullStrategy

logger = logging.getLogger(__name__)

# 降級最後防線的 doc_type（SPEC §3.3）
_FALLBACK_DOC_TYPE = "litedoc"


class PipelineFactory:
    """五路策略註冊表 + 查找工廠。"""

    _registry: Dict[str, Type[DocumentStrategy]] = {}

    @classmethod
    def register(cls, doc_type: str):
        """裝飾器註冊：`@PipelineFactory.register('academic')`。"""

        def _deco(strategy_cls: Type[DocumentStrategy]) -> Type[DocumentStrategy]:
            cls.register_strategy(doc_type, strategy_cls)
            return strategy_cls

        return _deco

    @classmethod
    def register_strategy(cls, doc_type: str, strategy_cls: Type[DocumentStrategy]) -> None:
        """顯式註冊一個 doc_type → 策略類。"""
        cls._registry[doc_type] = strategy_cls
        logger.info(f"[factory] 註冊策略 doc_type={doc_type!r} → {strategy_cls.__name__}")

    @classmethod
    def get_strategy(cls, doc_type: str) -> DocumentStrategy:
        """查找策略實例：命中回該策略；未命中降級 LiteDoc；無 LiteDoc 回 NullStrategy 哨兵。"""
        if doc_type in cls._registry:
            return cls._registry[doc_type]()
        if _FALLBACK_DOC_TYPE in cls._registry:
            logger.warning(
                f"[factory] doc_type={doc_type!r} 未註冊，降級 {_FALLBACK_DOC_TYPE}（SPEC §3.3 最後防線）"
            )
            return cls._registry[_FALLBACK_DOC_TYPE]()
        logger.warning(
            f"[factory] doc_type={doc_type!r} 未註冊且無 {_FALLBACK_DOC_TYPE}，回 NullStrategy 哨兵"
        )
        return NullStrategy()
