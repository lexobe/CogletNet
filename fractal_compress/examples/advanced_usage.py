#!/usr/bin/env python3
"""
Advanced Usage Examples

Demonstrates advanced features and use cases.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractal_compress import compress, split_compress, llm_compress, split


def progressive_compression_demo():
    """Demonstrate progressive compression with different ratios."""
    print("📈 Progressive Compression Demo")
    print("-" * 40)
    
    long_text = """
    人工智能技术的快速发展正在深刻改变着我们的社会。从智能手机的语音助手
    到自动驾驶汽车，从医疗诊断到金融分析，AI技术的应用范围越来越广泛。
    机器学习算法能够从大量数据中学习模式，深度学习网络可以处理复杂的
    认知任务。然而，我们也需要考虑AI发展带来的伦理和社会问题，确保
    技术进步能够造福全人类。
    """.strip()
    
    print(f"Original text ({len(long_text)} chars):")
    print(f"  {long_text[:100]}...")
    print()
    
    # Different compression levels
    compression_levels = [
        (0.2, "Aggressive"),
        (0.4, "Moderate"), 
        (0.6, "Conservative"),
        (0.8, "Light")
    ]
    
    for ratio, level in compression_levels:
        result = compress(long_text, compression_ratio=ratio)
        reduction = (1 - len(result) / len(long_text)) * 100
        print(f"  {level:12} ({ratio}): {result}")
        print(f"  {'':12}      Reduction: {reduction:.1f}% ({len(result)} chars)")
        print()


def batch_processing_demo():
    """Demonstrate batch processing of multiple texts."""
    print("🔄 Batch Processing Demo")
    print("-" * 40)
    
    documents = [
        "云计算技术为企业提供了灵活、可扩展的IT基础设施解决方案。",
        "Machine learning algorithms can identify patterns in complex datasets.",
        "Blockchain technology enables secure and transparent transactions.",
        "移动应用开发需要考虑用户体验和性能优化。",
        "Cybersecurity threats are becoming increasingly sophisticated.",
    ]
    
    results = []
    for i, doc in enumerate(documents, 1):
        compressed = compress(doc, split_ratio=0.4, compression_ratio=0.5)
        ratio = len(compressed) / len(doc)
        results.append((doc, compressed, ratio))
        print(f"  Doc {i}: {compressed}")
        print(f"         Original: {len(doc)} → Compressed: {len(compressed)} (ratio: {ratio:.3f})")
        print()
    
    # Summary statistics
    avg_ratio = sum(r[2] for r in results) / len(results)
    print(f"  Average compression ratio: {avg_ratio:.3f}")


def content_summarization_demo():
    """Demonstrate content summarization workflow."""
    print("📄 Content Summarization Demo")
    print("-" * 40)
    
    article = """
    量子计算是一种基于量子力学原理的计算模式，利用量子比特的叠加和纠缠特性
    来处理信息。与传统计算机使用二进制比特不同，量子计算机使用量子比特，
    可以同时处于0和1的叠加状态。这种特性使得量子计算机在某些特定问题上
    具有指数级的计算优势。目前，谷歌、IBM、微软等科技巨头都在积极投入
    量子计算研究，并取得了重要进展。量子计算的应用前景广阔，包括密码学、
    优化问题、药物发现、材料科学等领域。然而，量子计算技术仍面临着
    量子纠错、稳定性等技术挑战，距离大规模商业应用还有一定距离。
    """
    
    print(f"Article ({len(article)} chars):")
    print(f"  {article[:80]}...")
    print()
    
    # Multi-level summarization
    levels = [
        (100, "Detailed Summary"),
        (60, "Brief Summary"),
        (30, "Key Points"),
        (15, "Core Message")
    ]
    
    for target_length, description in levels:
        summary = llm_compress(article, target_length=target_length)
        print(f"  {description:15} ({target_length:2d} chars): {summary}")
    print()


def multilingual_processing_demo():
    """Demonstrate multilingual text processing."""
    print("🌍 Multilingual Processing Demo")
    print("-" * 40)
    
    texts = {
        "Chinese": "深度学习是机器学习的一个分支，通过多层神经网络来学习数据的复杂表示。",
        "English": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to learn complex representations.",
        "Mixed": "Deep learning深度学习使用neural networks神经网络来process处理complex data复杂数据。",
        "Japanese": "深層学習は機械学習の一分野で、多層ニューラルネットワークを使用してデータの複雑な表現を学習します。",
    }
    
    for lang, text in texts.items():
        # Auto-detect language
        auto_result = compress(text, language="auto")
        
        # Try different language hints
        language_codes = {"Chinese": "chinese", "English": "english", "Mixed": "auto", "Japanese": "auto"}
        lang_code = language_codes.get(lang, "auto")
        specific_result = compress(text, language=lang_code)
        
        print(f"  {lang:8}: {text[:50]}...")
        print(f"  Auto    : {auto_result}")
        print(f"  Specific: {specific_result}")
        print()


def pipeline_demo():
    """Demonstrate text processing pipeline."""
    print("🔧 Processing Pipeline Demo")
    print("-" * 40)
    
    raw_text = """
    数据科学是一个跨学科领域，结合了统计学、计算机科学、领域专业知识等
    多个学科。数据科学家使用各种工具和技术来从大量数据中提取有价值的
    见解和知识。这个过程包括数据收集、清理、探索性分析、建模和结果
    解释等步骤。Python和R是数据科学中最常用的编程语言，提供了丰富的
    库和框架支持。机器学习是数据科学的重要组成部分，包括监督学习、
    无监督学习和强化学习等方法。
    """
    
    print(f"Raw text ({len(raw_text)} chars):")
    print(f"  {raw_text[:60]}...")
    print()
    
    # Pipeline: Split → Compress → Further process
    print("Pipeline Steps:")
    
    # Step 1: Split text
    part1, part2 = split(raw_text, ratio=0.6)
    print(f"  1. Split (60/40): Part1={len(part1)}, Part2={len(part2)}")
    
    # Step 2: Compress first part
    compressed1 = llm_compress(part1, target_length=50)
    print(f"  2. Compress Part1: {compressed1}")
    
    # Step 3: Process second part differently
    compressed2 = compress(part2, compression_ratio=0.7)
    print(f"  3. Different processing Part2: {compressed2}")
    
    # Step 4: Combine results
    final_result = f"{compressed1} | {compressed2}"
    total_reduction = (1 - len(final_result) / len(raw_text)) * 100
    print(f"  4. Combined result: {final_result}")
    print(f"     Total reduction: {total_reduction:.1f}%")


def main():
    """Run all advanced usage demonstrations."""
    print("🔬 Fractal Compress - Advanced Usage")
    print("=" * 50)
    print()
    
    progressive_compression_demo()
    print()
    
    batch_processing_demo()
    print()
    
    content_summarization_demo()
    print()
    
    multilingual_processing_demo()
    print()
    
    pipeline_demo()
    print()
    
    print("💡 Advanced Tips:")
    print("  • Use split_compress() for document preprocessing")
    print("  • Combine different strategies for complex workflows")
    print("  • Adjust ratios based on content type and requirements")
    print("  • Language detection works best with 20+ characters")


if __name__ == "__main__":
    try:
        main()
        print("\n🎉 Advanced examples completed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()