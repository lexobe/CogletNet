#!/usr/bin/env python3
"""
演示如何使用独立的LLM压缩函数进行prompt优化实验
"""

import sys
import os
import json
from dotenv import load_dotenv

# 加载.env文件
load_dotenv('/Users/liuyu/Code/CogletNet/.env')

# 添加包路径
sys.path.insert(0, 'src')

from fractal_compress.utils.enhanced_hybrid_compressor import EnhancedHybridCompressor

def demo_basic_usage():
    """演示基础用法"""
    print("📝 基础LLM压缩功能演示")
    print("=" * 50)
    
    compressor = EnhancedHybridCompressor()
    
    # 测试文本
    test_text = "人工智能技术的快速发展正在深刻改变着社会的各个方面"
    target_length = 15
    
    print(f"原文: {test_text}")
    print(f"原文长度: {len(test_text)}字符")
    print(f"目标长度: {target_length}字符")
    print()
    
    # 调用独立的压缩函数
    result = compressor.compress_text_with_llm(
        text=test_text,
        target_length=target_length,
        language="chinese",
        max_attempts=3
    )
    
    print(f"压缩结果: {result['text']}")
    print(f"压缩长度: {result['compressed_length']}字符")
    print(f"压缩比例: {result['compression_ratio']:.3f}")
    print(f"尝试次数: {result['attempts']}")
    print(f"使用策略: {result['strategy']}")
    print(f"成功状态: {result['success']}")

def demo_custom_templates():
    """演示自定义prompt模板"""
    print("\n🎯 自定义Prompt模板演示")
    print("=" * 50)
    
    compressor = EnhancedHybridCompressor()
    
    # 自定义prompt模板
    custom_templates = {
        "few_shot_precise": """你是一个专业的文本压缩专家。请将以下文本压缩到指定长度。

🎯 压缩规则：
1. 保持核心意思不变
2. 压缩后长度必须 ≤ {target_length} 字符
3. 使用简洁明了的表达

📝 待压缩文本："{text}"
📏 原文长度：{original_length} 字符
🎯 目标长度：≤ {target_length} 字符

请直接输出压缩结果，不要添加任何解释：""",
        
        "strict_length": """严格按照长度要求压缩文本。

原文：{text}
要求：压缩到 {target_length} 字符以内
输出：""",
        
        "ultra_short": """极简压缩：{text} → 最多{target_length}字符"""
    }
    
    test_text = "Quality assurance是software development的关键环节"
    target_length = 12
    
    print(f"原文: {test_text}")
    print(f"目标长度: {target_length}字符")
    print()
    
    # 使用自定义模板
    result = compressor.compress_text_with_llm(
        text=test_text,
        target_length=target_length,
        language="mixed",
        max_attempts=2,
        custom_templates=custom_templates
    )
    
    print(f"压缩结果: {result['text']}")
    print(f"压缩长度: {result['compressed_length']}字符")
    print(f"使用策略: {result['strategy']}")

def demo_custom_examples():
    """演示自定义Few-shot示例"""
    print("\n🔬 自定义Few-shot示例演示")
    print("=" * 50)
    
    compressor = EnhancedHybridCompressor()
    
    # 自定义Few-shot示例
    custom_examples = [
        {
            "original": "人工智能技术在医疗领域的应用前景广阔",
            "original_length": 19,
            "part_a": "人工智能技术在医疗",
            "part_a_length": 9,
            "target_compressed": 5,
            "compressed": "AI医疗应用",
            "compressed_length": 5,
            "explanation": "使用缩写和关键词提取"
        },
        {
            "original": "Environmental protection requires global cooperation",
            "original_length": 51,
            "part_a": "Environmental protection requires",
            "part_a_length": 32,
            "target_compressed": 19,
            "compressed": "Env protection needs",
            "compressed_length": 19,
            "explanation": "缩写+核心概念"
        }
    ]
    
    test_text = "Machine learning算法在金融risk assessment中发挥重要作用"
    target_length = 18
    
    print(f"原文: {test_text}")
    print(f"目标长度: {target_length}字符")
    print()
    
    # 使用自定义示例
    result = compressor.compress_text_with_llm(
        text=test_text,
        target_length=target_length,
        language="mixed",
        custom_examples=custom_examples,
        max_attempts=2
    )
    
    print(f"压缩结果: {result['text']}")
    print(f"压缩长度: {result['compressed_length']}字符")
    print(f"压缩比例: {result['compression_ratio']:.3f}")

def demo_batch_testing():
    """演示批量测试不同参数"""
    print("\n⚡ 批量参数测试演示")
    print("=" * 50)
    
    compressor = EnhancedHybridCompressor()
    
    test_cases = [
        {"text": "Deep learning neural networks", "target": 10, "lang": "english"},
        {"text": "区块链技术改变金融行业", "target": 8, "lang": "chinese"},
        {"text": "Cloud computing提供scalable solutions", "target": 15, "lang": "mixed"}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试 {i}: {case['text']}")
        
        # 测试不同的max_attempts
        for attempts in [1, 3, 5]:
            result = compressor.compress_text_with_llm(
                text=case['text'],
                target_length=case['target'],
                language=case['lang'],
                max_attempts=attempts,
                strict_constraint=True
            )
            
            print(f"  尝试{attempts}次: {result['text']} "
                  f"({result['compressed_length']}字符, {result['strategy']})")
        print()

def main():
    """主函数"""
    print("🚀 独立LLM压缩函数演示")
    print("用于prompt优化实验的完整示例")
    print("=" * 60)
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 未找到 OPENAI_API_KEY")
        return
    
    try:
        # 基础用法演示
        demo_basic_usage()
        
        # 自定义模板演示
        demo_custom_templates()
        
        # 自定义示例演示
        demo_custom_examples()
        
        # 批量测试演示
        demo_batch_testing()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("\n💡 提示：")
        print("1. 修改 custom_templates 来测试新的prompt策略")
        print("2. 调整 custom_examples 来优化Few-shot学习")
        print("3. 改变 max_attempts 和 strict_constraint 来控制行为")
        print("4. 使用不同的 temperature 参数来调整创造性")
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")

if __name__ == "__main__":
    main()