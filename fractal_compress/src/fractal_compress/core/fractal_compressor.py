"""
分形压缩器核心实现
"""

import time
from typing import List, Dict, Any, Optional
from litellm import completion_with_retries
from .prompt_manager import PromptManager


class FractalEncode:
    """
    真正的分形压缩器
    
    基于黄金分割比例的分形压缩算法：
    - 当前层超过门限时，按1-ratio保留前部分，ratio部分压缩到下一层
    - 每层门限按 base_threshold * ratio^level 计算
    - 最大支持max_levels层
    """
    
    def __init__(
        self,
        ratio: float = 0.618,
        base_threshold: int = 1000,
        max_levels: int = 10,
        prompt_manager: Optional[PromptManager] = None
    ):
        """
        初始化分形压缩器
        
        Args:
            ratio: 黄金分割比例，默认0.618
            base_threshold: level 0的门限长度
            max_levels: 最大层数限制
            prompt_manager: 提示词管理器
        """
        self.ratio = ratio
        self.base_threshold = base_threshold
        self.max_levels = max_levels
        self.prompt_manager = prompt_manager or PromptManager()
       

    def encode(self, 
        fractal_text: List[List[str]], 
        new_text: str,
    ) -> List[List[str]]:
        """
        分形编码主函数，将新文本编码到分形文本中

        Args:
            fractal_text: 多层结构的文本数据 [[level0], [level1], ...]
            new_text: 新输入的文本
            current_level: 当前层级            
        Returns:
            更新后的fractal_text
        """
        # 1. 超长截断
        while len(new_text) > self.get_threshold(0):
            fractal_text = self._recursive_compress(fractal_text, new_text[:self.get_threshold(0)], 0)
            new_text = new_text[self.get_threshold(0):]
        
        fractal_text = self._recursive_encode(fractal_text, new_text, 0)

        return fractal_text

        
    def _recursive_encode(self, fractal_text: List[List[str]], new_text: str, current_level: int) -> List[List[str]]:
        """
        递归编码新文本到分形文本中
        
        Args:
            fractal_text: 分形文本数据
            new_text: 新输入的文本
            current_level: 当前层级

        """
        # 1. 如果current_level >= max_levels，则返回fractal_text
        if current_level >= self.max_levels:
            return fractal_text
        
        # 2. 将new_text添加到level current_level
        fractal_text[current_level] += new_text
        
        # 3. 如果current_level的文本长度小于门限，则直接返回fractal_text
        if len(fractal_text[current_level]) < self.get_threshold(current_level):
            return fractal_text
        else:
            # 4. 如果current_level的文本长度超过门限，则进行分形压缩
            base, up = self._llm_compress(fractal_text[current_level])
            fractal_text[current_level] = base
            self._recursive_compress(fractal_text, up, current_level + 1)
            return fractal_text
        return fractal_text
        
    def _get_level_threshold(self, level: int) -> int:
        """
        计算指定层级的门限
        
        Args:
            level: 层级号
            
        Returns:
            该层级的门限长度
        """
        return int(self.base_threshold * (self.ratio ** level))
        
        
    def _llm_compress(self, text: str, level: int) -> str:
        """
        使用LLM压缩文本
        
        Args:
            text: 要压缩的文本
            level: 当前压缩层级
            
        Returns:
            压缩后的文本
        """
        # 生成压缩提示词
        prompt = self.prompt_manager.get_compression_prompt(text, level=level)
        system_prompt = self.prompt_manager.get_system_prompt()
        llm_params = self.prompt_manager.get_llm_parameters()
        
        # 调用LLM
        response = completion_with_retries(
            model=llm_params.get("model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=llm_params.get("temperature", 0.7),
            max_tokens=llm_params.get("max_tokens", 2000),
            max_retries=3
        )
        
        return response.choices[0].message.content.strip()
    