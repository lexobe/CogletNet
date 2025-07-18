"""
Fractal Compress - 真正的分形文本压缩

基于黄金分割比例的分形压缩算法，使用LLM进行智能文本压缩。
"""

# 标准API（推荐使用）
from .utils import (
    compress,
    split_and_compress,
    llm_compress,
    simple_split
)

# 核心组件和向后兼容
from .utils import (
    smart_split,
    compress_text,
    LLMTextCompressor,
    quick_compress,
    compare_strategies
)

__version__ = "0.3.0"
__author__ = "CogletNet Team"

__all__ = [
    # 标准API（推荐）
    "compress",
    "split_and_compress", 
    "llm_compress",
    "simple_split",
    
    # 核心组件
    "smart_split",
    "LLMTextCompressor",
    "quick_compress",
    "compare_strategies",
    
    # 向后兼容
    "compress_text"
]