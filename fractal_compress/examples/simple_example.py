"""
简单使用示例
"""

from fractal_compress import FractalCompressor

def main():
    """简单示例：体验分形压缩的基本功能"""
    
    print("🌀 Fractal Compress 简单示例")
    print("=" * 40)
    
    # 1. 创建分形压缩器
    compressor = FractalCompressor(
        ratio=0.618,           # 黄金分割比例
        base_threshold=200,    # Level 0 门限（较小便于演示）
        max_levels=5           # 最大5层
    )
    
    # 2. 初始化分形文本结构
    fractal_text = [[""]]     # [[level0], [level1], ...]
    
    # 3. 准备测试文本
    test_text = """
    分形压缩是一种基于黄金分割比例的创新文本压缩方法。它的核心思想是当文本长度超过
    预设门限时，自动按照0.618的比例进行分割：前面38.2%的内容保留在当前层，
    后面61.8%的内容通过LLM压缩后进入下一层。这种设计确保了压缩过程具有分形特性，
    即每一层都遵循相同的分割规则。门限值按照黄金分割比例递减，Level 0为基础门限，
    Level 1为基础门限×0.618，Level 2为基础门限×0.618²，以此类推。
    这种算法特别适合处理需要保持语义完整性的长文本压缩任务。
    """
    
    print(f"原始文本长度: {len(test_text)} 字符")
    print(f"Level 0 门限: {compressor.base_threshold} 字符")
    print()
    
    # 4. 执行分形压缩
    print("🚀 开始分形压缩...")
    fractal_text = compressor.compress(fractal_text, test_text)
    
    # 5. 查看压缩结果
    info = compressor.get_fractal_info(fractal_text)
    print(f"✅ 压缩完成!")
    print(f"层数: {info['total_levels']}")
    print(f"总长度: {info['total_length']} 字符")
    
    if 'compression_efficiency' in info:
        eff = info['compression_efficiency']
        print(f"压缩率: {eff['overall_ratio']:.3f}")
        print(f"节省: {eff['space_saved']} 字符")
    
    # 6. 可视化分形结构
    print("\n📊 分形结构可视化:")
    print(compressor.visualize_fractal(fractal_text))
    
    # 7. 显示各层内容
    print("\n📋 各层内容:")
    for level, texts in enumerate(fractal_text):
        if texts and texts[0]:
            content = texts[0]
            preview = content[:80] + "..." if len(content) > 80 else content
            print(f"Level {level}: {preview}")
    
    return fractal_text


if __name__ == "__main__":
    try:
        main()
        print("\n🎉 示例运行完成!")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        print("提示: 请确保设置了 OPENAI_API_KEY 环境变量")