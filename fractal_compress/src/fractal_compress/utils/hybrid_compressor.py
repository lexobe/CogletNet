"""
混合压缩器 - 简化版本，基于已有的核心组件实现

结合智能分割(smart_split)和LLM压缩器(LLMTextCompressor)的简洁实现
"""

import time
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

from .text_splitter import smart_split
from .llm_compressor import LLMTextCompressor


@dataclass
class CompressResult:
    """压缩结果"""
    compressed_text: str
    original_part_a: str
    original_part_b: str
    split_ratio: float
    compression_ratio: float
    overall_ratio: float
    model_used: str
    processing_time: float
    success: bool
    actual_a_length: int
    actual_compressed_length: int
    target_compressed_length: int


class HybridCompressor:
    """
    混合压缩器 - 简化版本
    
    使用现有核心组件：
    1. smart_split() - 黄金分割智能文本分割
    2. LLMTextCompressor - 独立LLM压缩工具
    """
    
    def __init__(self, default_model: str = "gpt-4o-mini"):
        """初始化混合压缩器"""
        self.default_model = default_model
        self.llm_compressor = LLMTextCompressor(default_model)
    
    def compress(
        self,
        text: str,
        model: Optional[str] = None,
        language: str = "mixed",
        split_deviation_threshold: float = 0.05,
        max_attempts: int = 3,
        temperature: float = 0.1,
        strategy: str = "precise"
    ) -> CompressResult:
        """
        执行混合压缩
        
        Args:
            text: 输入文本
            model: 模型名称
            language: 语言类型 ("chinese", "english", "mixed")
            split_deviation_threshold: 分割偏差阈值
            max_attempts: 最大压缩尝试次数
            temperature: LLM温度参数
            strategy: 压缩策略
        
        Returns:
            CompressResult: 压缩结果
        """
        start_time = time.time()
        model = model or self.default_model
        
        # 第1步：智能分割（使用 smart_split）
        try:
            part_a, part_b = smart_split(
                text, 
                ratio=0.382,  # 黄金分割比例
                deviation_threshold=split_deviation_threshold,
                language=language
            )
        except Exception as e:
            return self._create_failed_result(model, time.time() - start_time, str(e))
        
        # 计算目标长度
        target_compressed_length = int(len(part_a) * 0.618)
        actual_a_length = len(part_a)
        
        # 第2步：LLM压缩（使用 LLMTextCompressor）
        try:
            compression_result = self.llm_compressor.compress(
                text=part_a,
                target_length=target_compressed_length,
                model=model,
                strategy=strategy,
                max_attempts=max_attempts,
                temperature=temperature,
                strict_length=True
            )
            
            compressed_text = compression_result["text"]
            success = compression_result["success"]
            
        except Exception as e:
            # 使用简单截断作为后备
            compressed_text = part_a[:target_compressed_length] if len(part_a) > target_compressed_length else part_a
            success = False
        
        # 计算结果指标
        actual_compressed_length = len(compressed_text)
        split_ratio = actual_a_length / len(text)
        compression_ratio = actual_compressed_length / actual_a_length if actual_a_length > 0 else 0
        overall_ratio = actual_compressed_length / len(text)
        processing_time = time.time() - start_time
        
        # 验证成功条件
        split_ok = abs(split_ratio - 0.382) < 0.05
        compression_ok = abs(compression_ratio - 0.618) < 0.3
        length_ok = actual_compressed_length <= target_compressed_length
        content_ok = len(compressed_text) > 0
        
        final_success = success and split_ok and compression_ok and length_ok and content_ok
        
        return CompressResult(
            compressed_text=compressed_text,
            original_part_a=part_a,
            original_part_b=part_b,
            split_ratio=split_ratio,
            compression_ratio=compression_ratio,
            overall_ratio=overall_ratio,
            model_used=model,
            processing_time=processing_time,
            success=final_success,
            actual_a_length=actual_a_length,
            actual_compressed_length=actual_compressed_length,
            target_compressed_length=target_compressed_length
        )
    
    def _create_failed_result(self, model: str, processing_time: float, error: str) -> CompressResult:
        """创建失败结果"""
        return CompressResult(
            compressed_text="",
            original_part_a="",
            original_part_b="",
            split_ratio=0,
            compression_ratio=0,
            overall_ratio=0,
            model_used=model,
            processing_time=processing_time,
            success=False,
            actual_a_length=0,
            actual_compressed_length=0,
            target_compressed_length=0
        )


# 便捷函数
def compress_text(
    text: str,
    model: str = "gpt-4o-mini",
    language: str = "mixed",
    strategy: str = "precise"
) -> str:
    """
    快速压缩文本
    
    Args:
        text: 输入文本
        model: 模型名称
        language: 语言类型
        strategy: 压缩策略
    
    Returns:
        str: 压缩后的文本
    """
    compressor = HybridCompressor(default_model=model)
    result = compressor.compress(text, language=language, strategy=strategy)
    return result.compressed_text


def compress_with_details(
    text: str,
    model: str = "gpt-4o-mini",
    language: str = "mixed"
) -> Tuple[str, Dict[str, Any]]:
    """
    压缩文本并返回详细信息
    
    Args:
        text: 输入文本
        model: 模型名称
        language: 语言类型
    
    Returns:
        Tuple[str, Dict]: (压缩文本, 详细信息)
    """
    compressor = HybridCompressor(default_model=model)
    result = compressor.compress(text, language=language)
    
    details = {
        "success": result.success,
        "split_ratio": result.split_ratio,
        "compression_ratio": result.compression_ratio,
        "overall_ratio": result.overall_ratio,
        "processing_time": result.processing_time,
        "original_part_a": result.original_part_a,
        "target_length": result.target_compressed_length,
        "actual_length": result.actual_compressed_length
    }
    
    return result.compressed_text, details