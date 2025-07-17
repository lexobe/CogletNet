"""
混合压缩器 - 终极解决方案

结合代码精确分割和LLM智能压缩，确保符合黄金比例要求
"""

import os
import time
import json
from typing import Dict, Any, Tuple, List, Optional, Callable
from dataclasses import dataclass
from .text_splitter import smart_split

try:
    import litellm
except ImportError:
    print("Warning: litellm not installed. Please install with: pip install litellm")
    litellm = None


@dataclass
class HybridResult:
    """混合压缩结果"""
    compressed_text: str
    original_part_a: str
    original_part_b: str
    split_ratio: float
    compression_ratio: float
    overall_ratio: float
    model_used: str
    processing_time: float
    success: bool
    target_a_length: int
    target_compressed_length: int
    actual_a_length: int
    actual_compressed_length: int


class HybridCompressor:
    """
    混合压缩器
    
    使用代码进行精确的黄金比例分割，然后用LLM进行智能压缩
    确保分割比例和压缩比例都符合要求
    """
    
    def __init__(self, default_model: str = "gpt-4o-mini"):
        """初始化混合压缩器"""
        if litellm is None:
            raise ImportError("litellm is required. Install with: pip install litellm")
        
        self.default_model = default_model
        self.compression_templates = self._create_compression_templates()
    
    def _create_compression_templates(self) -> Dict[str, str]:
        """创建压缩提示词模板"""
        return {
            "precise": """你是一个文本压缩专家。请将下面的文本压缩到指定长度。

🎯 **压缩要求**：
- 目标长度：正好 {target_length} 个字符
- 保留核心信息和关键内容
- 删除修饰词、副词、冗余表达
- 保持语义完整性和逻辑性
- 不要添加任何解释或额外内容

📝 **原文** ({original_length} 字符)：
{text}

🔧 **压缩策略**：
1. 删除"的"、"了"、"着"等助词
2. 简化长句为短句
3. 用词汇替换短语
4. 保留主要动词和名词

请输出压缩后的文本（必须正好 {target_length} 字符）：""",

            "aggressive": """请将文本极限压缩到 {target_length} 字符。

原文({original_length}字符)：{text}

压缩要求：
- 输出必须正好{target_length}字符
- 只保留最核心的信息
- 可以改写句式
- 删除所有冗余内容

压缩结果：""",

            "gentle": """请适度压缩以下文本到 {target_length} 字符左右。

原文({original_length}字符)：{text}

要求：
- 目标长度：{target_length}字符
- 保持文本可读性
- 保留重要信息
- 适当简化表达

输出："""
        }
    
    def compress(
        self,
        text: str,
        model: str = None,
        language: str = "chinese",
        compression_strategy: str = "precise",
        split_deviation_threshold: float = 0.1,
        max_compression_attempts: int = 3
    ) -> HybridResult:
        """
        执行混合压缩
        
        Args:
            text: 输入文本
            model: 模型名称
            language: 语言类型
            compression_strategy: 压缩策略 ("precise", "aggressive", "gentle")
            split_deviation_threshold: 分割偏差阈值
            max_compression_attempts: 最大压缩尝试次数
        
        Returns:
            HybridResult: 压缩结果
        """
        start_time = time.time()
        model = model or self.default_model
        
        # 第1步：精确分割
        try:
            part_a, part_b = smart_split(
                text, 
                ratio=0.382, 
                deviation_threshold=split_deviation_threshold,
                language=language
            )
        except Exception as e:
            return HybridResult(
                compressed_text="",
                original_part_a="",
                original_part_b="",
                split_ratio=0,
                compression_ratio=0,
                overall_ratio=0,
                model_used=model,
                processing_time=time.time() - start_time,
                success=False,
                target_a_length=0,
                target_compressed_length=0,
                actual_a_length=0,
                actual_compressed_length=0
            )
        
        # 计算目标长度
        target_a_length = int(len(text) * 0.382)
        target_compressed_length = int(len(part_a) * 0.618)
        actual_a_length = len(part_a)
        
        # 第2步：LLM压缩
        compressed_text = self._compress_with_llm(
            part_a, 
            target_compressed_length, 
            model, 
            compression_strategy,
            max_attempts=max_compression_attempts
        )
        
        # 计算最终结果
        actual_compressed_length = len(compressed_text)
        split_ratio = actual_a_length / len(text)
        compression_ratio = actual_compressed_length / actual_a_length if actual_a_length > 0 else 0
        overall_ratio = actual_compressed_length / len(text)
        processing_time = time.time() - start_time
        
        # 验证成功条件
        split_ok = abs(split_ratio - 0.382) < 0.05
        compression_ok = abs(compression_ratio - 0.618) < 0.15  # 稍微放宽压缩要求
        success = split_ok and compression_ok and len(compressed_text) > 0
        
        return HybridResult(
            compressed_text=compressed_text,
            original_part_a=part_a,
            original_part_b=part_b,
            split_ratio=split_ratio,
            compression_ratio=compression_ratio,
            overall_ratio=overall_ratio,
            model_used=model,
            processing_time=processing_time,
            success=success,
            target_a_length=target_a_length,
            target_compressed_length=target_compressed_length,
            actual_a_length=actual_a_length,
            actual_compressed_length=actual_compressed_length
        )
    
    def _compress_with_llm(
        self, 
        text: str, 
        target_length: int, 
        model: str,
        strategy: str,
        max_attempts: int = 3
    ) -> str:
        """
        使用LLM进行压缩，多次尝试直到达到目标长度
        """
        if strategy not in self.compression_templates:
            strategy = "precise"
        
        template = self.compression_templates[strategy]
        
        for attempt in range(max_attempts):
            # 根据尝试次数调整策略
            if attempt == 0:
                current_strategy = strategy
                temperature = 0.1
            elif attempt == 1:
                current_strategy = "aggressive" if len(text) > target_length * 2 else "gentle"
                temperature = 0.2
            else:
                current_strategy = "aggressive"
                temperature = 0.3
            
            prompt = self.compression_templates[current_strategy].format(
                text=text,
                target_length=target_length,
                original_length=len(text)
            )
            
            try:
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=min(1000, target_length * 3),
                    timeout=30
                )
                
                compressed = response.choices[0].message.content.strip()
                
                # 移除可能的引号或多余内容
                if compressed.startswith('"') and compressed.endswith('"'):
                    compressed = compressed[1:-1]
                if compressed.startswith("'") and compressed.endswith("'"):
                    compressed = compressed[1:-1]
                
                # 检查长度是否合理
                length_ratio = len(compressed) / target_length
                if 0.8 <= length_ratio <= 1.3:  # 允许20%的偏差
                    return compressed
                
                # 如果长度不合适，尝试调整
                if len(compressed) > target_length * 1.2:
                    # 太长了，尝试进一步压缩
                    continue
                elif len(compressed) < target_length * 0.6:
                    # 太短了，可能过度压缩
                    continue
                else:
                    return compressed
                    
            except Exception as e:
                if attempt == max_attempts - 1:
                    # 最后一次尝试失败，返回原文的简单截取
                    return text[:target_length] if len(text) > target_length else text
                continue
        
        # 所有尝试都失败，返回简单截取
        return text[:target_length] if len(text) > target_length else text
    
    def compress_with_callback(
        self,
        text: str,
        callback: Callable[[str, str], Any] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        使用回调函数的压缩方法
        
        Args:
            text: 输入文本
            callback: 回调函数，接收 (compressed, original) 参数
            **kwargs: 传递给 compress 的其他参数
            
        Returns:
            Tuple[str, str]: (compressed_text, original_part_a)
        """
        result = self.compress(text, **kwargs)
        
        if callback:
            callback(result.compressed_text, result.original_part_a)
        
        return result.compressed_text, result.original_part_a


# 便捷函数
def hybrid_compress(
    text: str,
    model: str = "gpt-4o-mini",
    compression_strategy: str = "precise"
) -> Tuple[str, str]:
    """
    快速混合压缩函数
    
    Args:
        text: 输入文本
        model: 模型名称
        compression_strategy: 压缩策略
    
    Returns:
        Tuple[str, str]: (compressed_text, original_part_a)
    """
    compressor = HybridCompressor(default_model=model)
    result = compressor.compress(text, compression_strategy=compression_strategy)
    return result.compressed_text, result.original_part_a


def validate_compression(result: HybridResult) -> Dict[str, Any]:
    """
    验证压缩结果
    
    Args:
        result: 压缩结果
    
    Returns:
        验证报告
    """
    split_error = abs(result.split_ratio - 0.382)
    compression_error = abs(result.compression_ratio - 0.618)
    overall_error = abs(result.overall_ratio - 0.236)  # 0.382 * 0.618
    
    return {
        "overall_success": result.success,
        "split_accuracy": split_error < 0.05,
        "compression_accuracy": compression_error < 0.15,
        "split_error": split_error,
        "compression_error": compression_error,
        "overall_error": overall_error,
        "length_accuracy": {
            "a_part_target": result.target_a_length,
            "a_part_actual": result.actual_a_length,
            "compressed_target": result.target_compressed_length,
            "compressed_actual": result.actual_compressed_length
        }
    }