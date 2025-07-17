"""
Fractal Compress - 真正的分形文本压缩

基于黄金分割比例的分形压缩算法，使用LLM进行智能文本压缩。
"""

from .core.fractal_compressor import FractalEncode
from .core.prompt_manager import PromptManager

__version__ = "0.2.0"
__author__ = "CogletNet Team"

__all__ = [
    "FractalEncode",
    "PromptManager",
]