"""
标准文本压缩库

提供简洁的压缩API，支持可配置的压缩比和截断比
"""

import time
from typing import Optional, Tuple

from .text_splitter import smart_split
from .llm_compressor import LLMTextCompressor


def compress(
    text: str,
    *,
    split_ratio: float = 0.382,
    compression_ratio: float = 0.618,
    model: str = "gpt-4o-mini",
    language: str = "mixed",
    strategy: str = "precise",
    max_attempts: int = 3
) -> str:
    """
    文本压缩函数
    
    Args:
        text: 输入文本
        split_ratio: 分割比例，默认0.382（黄金分割）
        compression_ratio: 压缩比例，默认0.618（黄金分割）
        model: LLM模型名称
        language: 语言类型 ("chinese", "english", "mixed")
        strategy: 压缩策略
        max_attempts: 最大尝试次数
    
    Returns:
        str: 压缩后的文本
    """
    if not text or not text.strip():
        return ""
    
    try:
        # 第1步：文本分割
        part_a, part_b = smart_split(
            text, 
            ratio=split_ratio,
            language=language
        )
        
        # 第2步：计算目标长度
        target_length = int(len(part_a) * compression_ratio)
        if target_length < 1:
            target_length = 1
        
        # 第3步：LLM压缩
        llm_compressor = LLMTextCompressor(default_model=model)
        result = llm_compressor.compress(
            text=part_a,
            target_length=target_length,
            strategy=strategy,
            max_attempts=max_attempts,
            strict_length=True
        )
        
        return result["text"]
        
    except Exception:
        # 失败时返回简单截断
        target_total_length = int(len(text) * split_ratio * compression_ratio)
        return text[:max(1, target_total_length)]


def split_and_compress(
    text: str,
    *,
    split_ratio: float = 0.382,
    compression_ratio: float = 0.618,
    model: str = "gpt-4o-mini",
    language: str = "mixed",
    strategy: str = "precise"
) -> Tuple[str, str]:
    """
    分割并压缩文本，返回压缩部分和未处理部分
    
    Args:
        text: 输入文本
        split_ratio: 分割比例
        compression_ratio: 压缩比例
        model: LLM模型名称
        language: 语言类型
        strategy: 压缩策略
    
    Returns:
        Tuple[str, str]: (压缩部分, 未处理部分)
    """
    if not text or not text.strip():
        return "", ""
    
    try:
        # 分割文本
        part_a, part_b = smart_split(
            text, 
            ratio=split_ratio,
            language=language
        )
        
        # 压缩第一部分
        target_length = int(len(part_a) * compression_ratio)
        if target_length < 1:
            target_length = 1
            
        llm_compressor = LLMTextCompressor(default_model=model)
        result = llm_compressor.compress(
            text=part_a,
            target_length=target_length,
            strategy=strategy,
            max_attempts=3,
            strict_length=True
        )
        
        return result["text"], part_b
        
    except Exception:
        # 失败时返回简单处理
        split_point = int(len(text) * split_ratio)
        part_a = text[:split_point]
        part_b = text[split_point:]
        
        target_length = int(len(part_a) * compression_ratio)
        compressed_a = part_a[:max(1, target_length)]
        
        return compressed_a, part_b


def llm_compress(
    text: str,
    *,
    target_length: Optional[int] = None,
    compression_ratio: float = 0.618,
    model: str = "gpt-4o-mini",
    strategy: str = "precise",
    max_attempts: int = 3
) -> str:
    """
    纯LLM压缩，不进行分割
    
    Args:
        text: 输入文本
        target_length: 目标长度，如果不指定则根据compression_ratio计算
        compression_ratio: 压缩比例（当target_length未指定时使用）
        model: LLM模型名称
        strategy: 压缩策略
        max_attempts: 最大尝试次数
    
    Returns:
        str: 压缩后的文本
    """
    if not text or not text.strip():
        return ""
    
    if target_length is None:
        target_length = int(len(text) * compression_ratio)
    
    target_length = max(1, target_length)
    
    try:
        llm_compressor = LLMTextCompressor(default_model=model)
        result = llm_compressor.compress(
            text=text,
            target_length=target_length,
            strategy=strategy,
            max_attempts=max_attempts,
            strict_length=True
        )
        
        return result["text"]
        
    except Exception:
        # 失败时返回简单截断
        return text[:target_length]


def simple_split(
    text: str,
    *,
    split_ratio: float = 0.382,
    language: str = "mixed"
) -> Tuple[str, str]:
    """
    简单文本分割，不进行压缩
    
    Args:
        text: 输入文本
        split_ratio: 分割比例
        language: 语言类型
    
    Returns:
        Tuple[str, str]: (第一部分, 第二部分)
    """
    if not text or not text.strip():
        return "", ""
    
    try:
        return smart_split(text, ratio=split_ratio, language=language)
    except Exception:
        # 失败时返回简单分割
        split_point = int(len(text) * split_ratio)
        return text[:split_point], text[split_point:]


# 兼容性函数 - 保持向后兼容
def compress_text(
    text: str,
    model: str = "gpt-4o-mini",
    language: str = "mixed",
    strategy: str = "precise"
) -> str:
    """向后兼容的压缩函数"""
    return compress(
        text,
        model=model,
        language=language,
        strategy=strategy
    )