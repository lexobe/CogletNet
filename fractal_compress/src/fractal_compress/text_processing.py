"""
Text Processing Module

Intelligent text splitting with language-aware boundary detection.
"""

import re
from typing import Tuple


def split_text(
    text: str,
    ratio: float = 0.382,
    language: str = "auto",
    deviation_threshold: float = 0.1
) -> Tuple[str, str]:
    """
    Split text at optimal position with intelligent boundary detection.
    
    Args:
        text: Input text to split
        ratio: Split ratio (0.0 to 1.0)
        language: Language hint ("chinese", "english", "auto")
        deviation_threshold: Maximum deviation from target ratio
    
    Returns:
        Tuple of (first_part, second_part)
    """
    if not text or not text.strip():
        return "", ""
    
    if not (0.0 <= ratio <= 1.0):
        raise ValueError("Split ratio must be between 0.0 and 1.0")
    
    text_length = len(text)
    target_pos = int(text_length * ratio)
    
    # Detect language if auto
    if language == "auto":
        language = _detect_language(text)
    
    # Get language-specific separators
    separators = _get_separators(language)
    
    # Find optimal split position
    split_pos = _find_optimal_split(
        text, target_pos, separators, deviation_threshold, text_length
    )
    
    # Ensure valid split position
    split_pos = max(1, min(split_pos, text_length - 1))
    
    # Split and clean
    first_part = text[:split_pos].rstrip()
    second_part = text[split_pos:].strip()
    
    return first_part, second_part


def _detect_language(text: str) -> str:
    """Detect text language based on character patterns."""
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    total_chars = chinese_chars + english_chars
    if total_chars == 0:
        return "english"  # Default
    
    chinese_ratio = chinese_chars / total_chars
    
    if chinese_ratio > 0.7:
        return "chinese"
    elif chinese_ratio < 0.3:
        return "english"
    else:
        return "mixed"


def _get_separators(language: str) -> list:
    """Get language-specific separator priority list."""
    if language == "chinese":
        return ["。", "！", "？", "；", "：", "，", "、", "\n", " "]
    elif language == "english":
        return [".", "!", "?", ";", ":", ",", "\n", " "]
    else:  # mixed or auto
        return [
            "。", "！", "？", ".", "!", "?",
            "；", ";", "：", ":", "，", ",", "、",
            "\n", " "
        ]


def _find_optimal_split(
    text: str,
    target_pos: int,
    separators: list,
    deviation_threshold: float,
    text_length: int
) -> int:
    """Find optimal split position using separator hierarchy."""
    max_deviation = int(text_length * deviation_threshold)
    min_pos = max(0, target_pos - max_deviation)
    max_pos = min(text_length, target_pos + max_deviation)
    
    # Try each separator in priority order
    for separator in separators:
        best_pos = _find_best_separator_position(
            text, separator, min_pos, max_pos, target_pos
        )
        if best_pos is not None:
            return best_pos
    
    # Fallback to target position
    return target_pos


def _find_best_separator_position(
    text: str,
    separator: str,
    min_pos: int,
    max_pos: int,
    target_pos: int
) -> int:
    """Find best position for a specific separator."""
    positions = []
    start = min_pos
    
    while start <= max_pos:
        pos = text.find(separator, start)
        if pos == -1 or pos > max_pos:
            break
        
        split_pos = pos + len(separator)
        if min_pos <= split_pos <= max_pos:
            positions.append(split_pos)
        start = pos + 1
    
    if positions:
        # Return position closest to target
        return min(positions, key=lambda x: abs(x - target_pos))
    
    return None