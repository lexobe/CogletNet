"""
分形压缩器核心实现
"""

import time
from typing import List, Dict, Any, Optional, Callable
from litellm import completion_with_retries
from .prompt_manager import PromptManager
from ..utils import smart_split


class FractalEncode:
    """
    真正的分形压缩器
    
    基于黄金分割比例的分形压缩算法：
    - 当前层超过门限时，按1-ratio保留前部分，ratio部分压缩到下一层
    - 每层门限按 base_threshold * ratio^level 计算
    - 最大支持max_levels层
    - 使用smart_split进行智能文本分割
    """
    
    def __init__(
        self,
        llm_compress: Callable[[str, float], str] = None,
        ratio: float = 0.618,
        base_threshold: int = 1000,
        max_levels: int = 10,
        split_ratio: float = 0.382,  # smart_split的分割比例
        split_threshold: float = 0.1  # smart_split的偏差阈值
    ):
        """
        初始化分形压缩器
        Args:
            llm_compress: 压缩函数，接受文本和压缩比例，返回压缩后的文本
            ratio: 黄金分割比例，默认0.618
            base_threshold: level 0的门限长度
            max_levels: 最大层数限制
            split_ratio: smart_split的分割比例，默认0.382
            split_threshold: smart_split的偏差阈值，默认0.1
        """
        self.llm_compress = self._mock_compress if llm_compress is None else llm_compress
        self.ratio = ratio
        self.base_threshold = base_threshold
        self.max_levels = max_levels
        self.split_ratio = split_ratio
        self.split_threshold = split_threshold

    def encode(self, 
        fractal_text: List[str], 
        new_text: str,
    ) -> List[str]:
        """
        分形编码主函数，将新文本编码到分形文本中

        Args:
            fractal_text: 多层结构的文本数据 ['text1', 'text2', ...]
            new_text: 新输入的文本           
        Returns:
            更新后的fractal_text
        """
        # 确保fractal_text至少有一层
        if not fractal_text:
            fractal_text = [""]
        
        threshold = self._get_level_threshold(0)
        
        while len(new_text) > threshold:
            fractal_text = self._recursive_encode(fractal_text, new_text[:threshold], 0)
            new_text = new_text[threshold:]
        
        if new_text:
            fractal_text = self._recursive_encode(fractal_text, new_text, 0)

        return fractal_text
        
        
    def _recursive_encode(self, fractal_text: List[str], new_text: str, current_level: int) -> List[str]:
        """
        递归编码新文本到分形文本中（使用smart_split智能分割）
        
        Args:
            fractal_text: 分形文本数据
            new_text: 新输入的文本
            current_level: 当前层级

        """
        # 1. 如果current_level >= max_levels，则返回fractal_text
        if current_level >= self.max_levels:
            return fractal_text
        
        # 2. 确保当前层级存在
        while len(fractal_text) <= current_level:
            fractal_text.append("")
            
        # 3. 将new_text作为新文本块添加到当前层级
        fractal_text[current_level] += new_text
        
        # 5. 如果当前层级文本长度小于门限，则直接返回
        if len(fractal_text[current_level]) <= self._get_level_threshold(current_level):
            return fractal_text
        else:
            next_text, local_text = smart_split(
                fractal_text[current_level], 
                ratio=self.split_ratio, 
                deviation_threshold=self.split_threshold
            )
            compressed = self.llm_compress(next_text, self.ratio)
            fractal_text = self._recursive_encode(fractal_text, compressed, current_level + 1)
            fractal_text[current_level] = local_text
            return fractal_text
        
    def _get_level_threshold(self, level: int) -> int:
        return int(self.base_threshold * (self.ratio ** level))
        
    def _mock_compress(self, text: str, compress_ratio: float) -> str:
        """默认的mock压缩函数，简单截断文本"""
        target_length = max(int(len(text) * compress_ratio), 1)
        return text[:target_length]