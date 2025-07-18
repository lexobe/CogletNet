"""
标准API使用示例 - 展示新的简洁压缩接口
"""

from fractal_compress import (
    compress,
    split_and_compress,
    llm_compress,
    simple_split,
    # 向后兼容
    compress_text
)
import os

def main():
    """标准API示例：体验简洁的压缩功能"""
    
    print("🌀 Fractal Compress 标准API示例")
    print("=" * 45)
    
    # 测试文本
    test_text = "人工智能技术的快速发展正在深刻改变着社会的各个方面，从智能家居到自动驾驶，从医疗诊断到金融服务，AI技术的应用领域越来越广泛。"
    
    print(f"原始文本: {test_text}")
    print(f"原始长度: {len(test_text)} 字符")
    print()
    
    # 1. 标准压缩 - 最简单的接口
    print("🚀 1. 标准压缩（默认黄金分割比例）")
    result1 = compress(test_text)
    print(f"   结果: {result1}")
    print(f"   长度: {len(result1)} 字符")
    print()
    
    # 2. 自定义压缩比例
    print("🎯 2. 自定义压缩比例")
    result2 = compress(
        test_text,
        split_ratio=0.5,      # 50% 分割
        compression_ratio=0.4  # 40% 压缩
    )
    print(f"   结果(0.5/0.4): {result2}")
    print(f"   长度: {len(result2)} 字符")
    print()
    
    # 3. 分割并压缩 - 获取两部分
    print("✂️ 3. 分割并压缩")
    compressed_part, remaining_part = split_and_compress(
        test_text,
        split_ratio=0.6,
        compression_ratio=0.7
    )
    print(f"   压缩部分: {compressed_part}")
    print(f"   剩余部分: {remaining_part}")
    print()
    
    # 4. 纯LLM压缩 - 指定目标长度
    print("🤖 4. 纯LLM压缩")
    result4 = llm_compress(test_text, target_length=25)
    print(f"   结果(目标25字符): {result4}")
    print(f"   实际长度: {len(result4)} 字符")
    print()
    
    # 5. 简单分割 - 不压缩
    print("📝 5. 简单分割（无压缩）")
    part1, part2 = simple_split(test_text, split_ratio=0.4)
    print(f"   第一部分(40%): {part1}")
    print(f"   第二部分(60%): {part2}")
    print(f"   验证: {len(part1) + len(part2)} == {len(test_text)} ? {len(part1) + len(part2) == len(test_text)}")
    print()
    
    # 6. 多语言支持
    print("🌍 6. 多语言支持")
    texts = {
        "中文": "人工智能正在改变世界",
        "English": "AI is transforming the world",
        "混合": "AI人工智能technology正在changing世界"
    }
    
    for lang_type, text in texts.items():
        if "中文" in lang_type:
            language = "chinese"
        elif "English" in lang_type:
            language = "english"
        else:
            language = "mixed"
            
        result = compress(text, language=language)
        print(f"   {lang_type}: {text} -> {result}")
    print()
    
    # 7. 不同策略比较
    print("📊 7. 不同压缩策略")
    short_text = "机器学习算法正在革命性地改变数据分析"
    strategies = ["basic", "precise", "creative"]
    
    for strategy in strategies:
        result = llm_compress(short_text, target_length=15, strategy=strategy)
        print(f"   {strategy}: {result}")
    print()
    
    # 8. 向后兼容
    print("🔄 8. 向后兼容接口")
    old_result = compress_text(test_text)
    print(f"   旧接口结果: {old_result}")
    print()
    
    print("💡 使用技巧:")
    print("   - compress(): 最简单，一键压缩")
    print("   - split_and_compress(): 需要分别处理两部分时使用")
    print("   - llm_compress(): 纯LLM压缩，精确控制长度")
    print("   - simple_split(): 只分割不压缩")
    print("   - 支持自定义 split_ratio 和 compression_ratio")


def advanced_examples():
    """高级用法示例"""
    print("\n" + "=" * 45)
    print("🔬 高级用法示例")
    print("=" * 45)
    
    long_text = """
    人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破。
    这些技术正在改变我们的生活方式，从智能手机的语音助手到自动驾驶汽车，
    从医疗诊断到金融分析，AI技术的应用范围越来越广泛。
    未来，人工智能将继续推动技术创新和社会进步。
    """.strip()
    
    print(f"长文本 ({len(long_text)} 字符):")
    print(f"{long_text[:50]}...")
    print()
    
    # 渐进式压缩 - 不同压缩比例对比
    print("📈 渐进式压缩对比:")
    ratios = [0.3, 0.5, 0.7, 0.9]
    
    for ratio in ratios:
        result = compress(long_text, compression_ratio=ratio)
        print(f"   压缩比{ratio}: {result} ({len(result)}字符)")
    print()
    
    # 分割点对比
    print("✂️ 不同分割点对比:")
    split_ratios = [0.2, 0.4, 0.6, 0.8]
    
    for split_ratio in split_ratios:
        compressed, remaining = split_and_compress(long_text, split_ratio=split_ratio)
        print(f"   分割{split_ratio}: \"{compressed}\" | \"{remaining[:20]}...\"")


if __name__ == "__main__":
    try:
        main()
        advanced_examples()
        print("\n🎉 所有示例运行完成!")
        print("\n📖 更多信息请查看 README.md")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        print("💡 提示: 某些功能需要设置 OPENAI_API_KEY 环境变量")
        import traceback
        traceback.print_exc()