#!/usr/bin/env python3
"""
Fractal Compress - Quick Start Guide

Modern text compression using golden ratio and LLM.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractal_compress import compress, split_compress, llm_compress, split


def main():
    """Quick start examples for fractal text compression."""
    
    print("🌀 Fractal Text Compression - Quick Start")
    print("=" * 50)
    
    # Sample texts
    texts = {
        "chinese": "人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破，这些技术正在改变我们的生活方式。",
        "english": "Artificial intelligence technology is rapidly advancing, with machine learning and deep learning achieving major breakthroughs that are transforming our daily lives.",
        "mixed": "AI人工智能technology正在快速developing，bringing革命性changes to various industries and applications worldwide."
    }
    
    print("📝 Sample Texts:")
    for lang, text in texts.items():
        print(f"  {lang}: {text[:50]}{'...' if len(text) > 50 else ''}")
    print()
    
    # 1. Basic Compression
    print("🚀 1. Basic Compression (Golden Ratio)")
    for lang, text in texts.items():
        result = compress(text)
        ratio = len(result) / len(text)
        print(f"  {lang:7}: {result}")
        print(f"          Ratio: {ratio:.3f} ({len(result)}/{len(text)} chars)")
    print()
    
    # 2. Custom Ratios
    print("🎯 2. Custom Compression Ratios")
    test_text = texts["mixed"]
    
    ratios = [(0.3, 0.4), (0.5, 0.6), (0.7, 0.8)]
    for split_r, comp_r in ratios:
        result = compress(test_text, split_ratio=split_r, compression_ratio=comp_r)
        print(f"  Split {split_r}, Compress {comp_r}: {result}")
    print()
    
    # 3. Split and Compress
    print("✂️ 3. Split and Compress")
    compressed_part, remaining_part = split_compress(texts["chinese"])
    print(f"  Compressed: {compressed_part}")
    print(f"  Remaining:  {remaining_part}")
    print()
    
    # 4. Direct LLM Compression
    print("🤖 4. Direct LLM Compression")
    lengths = [15, 25, 35]
    for target in lengths:
        result = llm_compress(texts["english"], target_length=target)
        print(f"  Target {target:2d}: {result} ({len(result)} chars)")
    print()
    
    # 5. Text Splitting Only
    print("📏 5. Text Splitting (No Compression)")
    part1, part2 = split(texts["chinese"], ratio=0.4)
    print(f"  Part 1 (40%): {part1}")
    print(f"  Part 2 (60%): {part2}")
    print(f"  Verification: {len(part1) + len(part2)} == {len(texts['chinese'])} ? {len(part1) + len(part2) == len(texts['chinese'])}")
    print()
    
    # 6. Language-Specific Processing
    print("🌍 6. Language-Specific Processing")
    for lang in ["chinese", "english", "auto"]:
        result = compress(texts["mixed"], language=lang)
        print(f"  Language '{lang}': {result}")
    print()
    
    # 7. Different LLM Strategies
    print("🧠 7. Different LLM Strategies")
    strategies = ["precise", "creative", "fast"]
    for strategy in strategies:
        result = llm_compress(texts["english"], target_length=30, strategy=strategy)
        print(f"  {strategy:8}: {result}")
    print()
    
    print("✨ Key Features:")
    print("  • Golden ratio splitting (0.382/0.618)")
    print("  • Intelligent language detection")
    print("  • Boundary-aware text splitting")
    print("  • Multiple LLM strategies")
    print("  • Clean, simple API")
    print()
    
    print("📖 Usage Patterns:")
    print("  compress()      - One-step compression")
    print("  split_compress() - Split and compress first part")
    print("  llm_compress()  - Direct LLM compression")
    print("  split()         - Text splitting only")


if __name__ == "__main__":
    try:
        main()
        print("\n🎉 Quick start completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure to set OPENAI_API_KEY for LLM features")