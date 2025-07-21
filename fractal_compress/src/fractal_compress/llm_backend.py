"""
LLM Backend Module

Clean interface for LLM-based text compression.
"""

from typing import Optional

try:
    import litellm
except ImportError:
    litellm = None


def compress_with_llm(
    text: str,
    target_length: int,
    model: str = "gpt-4o-mini",
    language: str = "auto",
    strategy: str = "precise",
    max_attempts: int = 3
) -> str:
    """
    Compress text using LLM to target length.
    
    Args:
        text: Input text to compress
        target_length: Target length in characters
        model: LLM model name
        language: Language hint
        strategy: Compression strategy
        max_attempts: Maximum retry attempts
    
    Returns:
        Compressed text
    """
    if not text or not text.strip():
        return ""
    
    if target_length <= 0:
        return ""
    
    if litellm is None:
        # Fallback: simple truncation
        return _fallback_compress(text, target_length)
    
    # Build prompt based on strategy
    prompt = _build_compression_prompt(text, target_length, language, strategy)
    
    # Try compression with retries
    for attempt in range(max_attempts):
        try:
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 + (attempt * 0.1),  # Increase temp on retry
                max_tokens=min(800, target_length * 4),
                timeout=30
            )
            
            compressed = response.choices[0].message.content.strip()
            compressed = _clean_llm_output(compressed)
            
            # Ensure length constraint
            if len(compressed) > target_length:
                compressed = _smart_truncate(compressed, target_length)
            
            # Validate result
            if _validate_compression(compressed, text, target_length):
                return compressed
                
        except Exception:
            if attempt == max_attempts - 1:
                return _fallback_compress(text, target_length)
            continue
    
    return _fallback_compress(text, target_length)


def _build_compression_prompt(
    text: str,
    target_length: int,
    language: str,
    strategy: str
) -> str:
    """Build compression prompt based on strategy."""
    
    if strategy == "creative":
        return f"""创造性压缩以下文本到{target_length}字符以内：

原文：{text}
目标：≤{target_length}字符
要求：保持核心信息，可以使用缩写、同义词替换

压缩结果："""

    elif strategy == "fast":
        return f"""快速压缩：{text}

目标长度：{target_length}字符
输出："""

    else:  # precise (default)
        return f"""请精确压缩以下文本：

原文："{text}"
原文长度：{len(text)}字符
目标长度：≤{target_length}字符

要求：
1. 保持核心信息完整
2. 长度严格控制在{target_length}字符以内
3. 保持语言流畅性

直接输出压缩结果："""


def _clean_llm_output(text: str) -> str:
    """Clean LLM output text."""
    # Remove common prefixes
    prefixes = ["压缩结果：", "输出：", "结果：", "答案：", "压缩："]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Remove quotes
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    
    return text.strip()


def _smart_truncate(text: str, max_length: int) -> str:
    """Intelligently truncate text to max length."""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at sentence boundaries
    sentence_endings = ["。", "！", "？", ".", "!", "?"]
    for i in range(max_length - 1, max(0, max_length - 20), -1):
        if i < len(text) and text[i] in sentence_endings:
            return text[:i + 1]
    
    # Try to truncate at word boundaries
    for i in range(max_length - 1, max(0, max_length - 10), -1):
        if i < len(text) and text[i] in [" ", "，", ","]:
            return text[:i]
    
    # Hard truncate
    return text[:max_length]


def _validate_compression(compressed: str, original: str, target_length: int) -> bool:
    """Validate compression result."""
    if not compressed or len(compressed) == 0:
        return False
    
    if len(compressed) > target_length:
        return False
    
    if len(compressed) >= len(original):
        return False
    
    # Must have reasonable content
    if len(compressed) < max(1, target_length * 0.1):
        return False
    
    return True


def _fallback_compress(text: str, target_length: int) -> str:
    """Fallback compression using simple truncation."""
    if len(text) <= target_length:
        return text
    
    return _smart_truncate(text, target_length)