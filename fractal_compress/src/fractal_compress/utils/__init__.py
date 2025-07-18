"""
fractal_compress 工具函数包
"""

# 标准API - 推荐使用
from .compressor import (
    compress,
    split_and_compress,
    llm_compress,
    simple_split,
    compress_text  # 向后兼容
)

# 核心组件
from .text_splitter import smart_split
from .llm_compressor import (
    LLMTextCompressor,
    quick_compress,
    compare_strategies
)

# 高级组件（保留用于特殊需求）
from .hybrid_compressor import (
    HybridCompressor,
    CompressResult,
    compress_with_details
)

__all__ = [
    # 标准API（推荐）
    'compress',
    'split_and_compress', 
    'llm_compress',
    'simple_split',
    
    # 向后兼容
    'compress_text',
    
    # 核心组件
    'smart_split',
    'LLMTextCompressor',
    'quick_compress',
    'compare_strategies',
    
    # 高级组件
    'HybridCompressor',
    'CompressResult',
    'compress_with_details'
]