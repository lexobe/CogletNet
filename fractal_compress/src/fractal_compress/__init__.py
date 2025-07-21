"""
Fractal Text Compression

A modern, clean text compression library using golden ratio splitting and LLM compression.

Example:
    >>> from fractal_compress import compress, split_compress, llm_compress, split
    >>> 
    >>> # Basic compression
    >>> result = compress("Long text here...")
    >>> 
    >>> # Custom ratios
    >>> result = compress(text, split_ratio=0.5, compression_ratio=0.4)
    >>> 
    >>> # Split and compress
    >>> compressed, remaining = split_compress(text)
    >>> 
    >>> # Direct LLM compression
    >>> result = llm_compress(text, target_length=20)
    >>> 
    >>> # Text splitting only
    >>> part1, part2 = split(text, ratio=0.3)
"""

from .core import compress, split_compress, llm_compress, split

__version__ = "1.0.0"
__author__ = "CogletNet Team"

__all__ = [
    "compress",
    "split_compress", 
    "llm_compress",
    "split"
]