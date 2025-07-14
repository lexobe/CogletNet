"""
Fractal Compress v2.0 演示程序
真正的分形压缩算法演示
"""

import os
import time
from fractal_compress import FractalCompressor, PromptManager


def demo_basic_fractal():
    """演示基本分形压缩"""
    print("🌀 基本分形压缩演示")
    print("=" * 50)
    
    # 创建压缩器
    compressor = FractalCompressor(
        ratio=0.618,
        base_threshold=300,  # 较小的门限便于演示
        max_levels=5
    )
    
    # 初始化分形文本
    fractal_text = [[""]]
    
    # 模拟逐步添加长文本
    texts = [
        "人工智能技术正在快速发展，深度学习算法在各个领域都取得了突破性进展。",
        "计算机视觉技术使得机器能够理解和分析图像内容，为自动驾驶、医疗诊断等应用提供了技术基础。",
        "自然语言处理技术的进步让机器能够更好地理解人类语言，聊天机器人、机器翻译等应用日趋成熟。",
        "机器学习模型的训练需要大量的数据和计算资源，云计算平台为此提供了强大的支持。",
        "强化学习算法让机器能够通过与环境交互来学习最优策略，在游戏AI、机器人控制等领域表现出色。",
        "神经网络架构的创新推动了AI技术的发展，从CNN到Transformer，每一次突破都带来新的应用可能。"
    ]
    
    for i, text in enumerate(texts):
        print(f"\n📝 添加第 {i+1} 段文本:")
        print(f"内容: {text}")
        
        # 执行压缩
        fractal_text = compressor.compress(fractal_text, text)
        
        # 显示当前状态
        info = compressor.get_fractal_info(fractal_text)
        print(f"当前层数: {info['total_levels']}")
        print(f"总文本长度: {info['total_length']}")
        
        # 检查是否有压缩发生
        if info['total_levels'] > 1:
            print("🔥 分形压缩已激活!")
            
        time.sleep(1)  # 演示停顿
    
    # 显示最终的分形结构
    print("\n" + "=" * 50)
    print("📊 最终分形结构:")
    print(compressor.visualize_fractal(fractal_text))
    
    return fractal_text, compressor


def demo_custom_prompts():
    """演示自定义Prompt配置"""
    print("\n🎯 自定义Prompt配置演示")
    print("=" * 50)
    
    # 创建自定义prompt配置
    custom_config = {
        "system_prompt": (
            "你是一个专业的文本摘要专家，擅长提取核心信息。"
            "请保持压缩后文本的专业性和准确性。"
        ),
        "compression_template": (
            "请将以下技术文档压缩到大约 {target_length} 个字符，"
            "保留所有关键的技术术语和核心概念：\\n\\n{text}\\n\\n"
            "压缩要求：\\n"
            "1. 保留所有技术术语\\n"
            "2. 保持逻辑结构完整\\n"
            "3. 使用简洁的表达方式\\n"
            "4. 直接返回压缩结果"
        ),
        "parameters": {
            "model": "gpt-4o-mini",
            "temperature": 0.2,  # 更低的温度保证一致性
            "max_tokens": 1500
        },
        "compression_ratio": 0.5  # 更激进的压缩
    }
    
    # 创建prompt管理器
    prompt_manager = PromptManager(custom_config)
    
    # 创建使用自定义prompt的压缩器
    compressor = FractalCompressor(
        ratio=0.618,
        base_threshold=200,
        max_levels=4,
        prompt_manager=prompt_manager
    )
    
    # 测试技术文档压缩
    tech_text = """
    分布式系统架构设计需要考虑多个核心要素。首先是可扩展性，系统必须能够水平扩展以应对不断增长的负载。
    其次是容错性，通过冗余设计和故障转移机制确保系统的高可用性。数据一致性是另一个关键挑战，
    需要在CAP理论的约束下找到最适合业务需求的平衡点。负载均衡技术帮助系统合理分配请求，
    提高整体性能。微服务架构模式通过服务解耦实现了更好的模块化和独立部署能力。
    API网关作为统一入口管理所有服务间的通信。消息队列中间件实现了异步处理和系统解耦。
    监控和日志系统提供了系统运行状态的可观测性。容器化技术简化了应用的部署和运维。
    DevOps实践促进了开发和运维的协作效率。
    """
    
    fractal_text = [[""]]
    fractal_text = compressor.compress(fractal_text, tech_text)
    
    print("原始文本长度:", len(tech_text))
    print("\\n压缩结果:")
    print(compressor.visualize_fractal(fractal_text))
    
    return compressor


def demo_progressive_compression():
    """演示渐进式压缩过程"""
    print("\\n⚡ 渐进式压缩过程演示")
    print("=" * 50)
    
    compressor = FractalCompressor(
        ratio=0.618,
        base_threshold=150,  # 很小的门限，快速触发压缩
        max_levels=6
    )
    
    # 模拟新闻聚合场景
    news_items = [
        "科技巨头发布新一代AI芯片，性能提升300%，将用于数据中心和边缘计算。",
        "量子计算研究取得重大突破，新算法可在现有硬件上实现100倍速度提升。",
        "区块链技术在供应链管理中的应用案例增加，多家企业开始试点项目。",
        "5G网络建设进入新阶段，覆盖范围扩大到农村地区，促进数字化转型。",
        "自动驾驶汽车测试里程突破1000万公里，安全性指标持续改善。",
        "机器学习平台推出新功能，降低了AI应用开发的技术门槛。",
        "云计算服务商宣布碳中和计划，承诺2030年实现零碳排放目标。",
        "虚拟现实技术在教育领域的应用扩展，多所学校采用VR教学系统。"
    ]
    
    fractal_text = [[""]]
    
    for i, news in enumerate(news_items):
        print(f"\\n📰 处理第 {i+1} 条新闻:")
        print(f"内容: {news}")
        
        old_levels = len(fractal_text)
        fractal_text = compressor.compress(fractal_text, news)
        new_levels = len(fractal_text)
        
        info = compressor.get_fractal_info(fractal_text)
        
        if new_levels > old_levels:
            print(f"🚀 新增了 {new_levels - old_levels} 个压缩层!")
        
        print(f"当前状态: {new_levels} 层, 总长度 {info['total_length']} 字符")
        
        # 显示每层的状态
        for level_info in info['level_details']:
            status = "🔴" if level_info['over_threshold'] else "🟢"
            print(f"  Level {level_info['level']}: {status} "
                  f"{level_info['text_length']}/{level_info['threshold']} "
                  f"({level_info['utilization']:.1%})")
    
    print("\\n" + "=" * 50)
    print("📈 最终压缩统计:")
    print(compressor.visualize_fractal(fractal_text))
    
    return fractal_text


def demo_real_world_scenario():
    """演示真实世界应用场景"""
    print("\\n🌍 真实应用场景演示")
    print("=" * 50)
    
    # 模拟文档管理系统
    print("场景: 智能文档管理系统")
    print("用途: 实时聚合和压缩大量文档内容")
    
    compressor = FractalCompressor(
        ratio=0.618,
        base_threshold=500,
        max_levels=8
    )
    
    # 模拟不同类型的文档内容
    documents = {
        "技术规范": """
        系统架构采用微服务设计模式，每个服务独立部署和扩展。API网关负责请求路由和认证。
        数据存储使用分布式数据库集群，支持读写分离和自动故障转移。缓存层使用Redis集群
        提供高性能数据访问。消息队列基于Kafka实现异步处理和服务解耦。监控系统集成
        Prometheus和Grafana实现全链路监控。日志收集使用ELK堆栈进行分析和可视化。
        """,
        "项目报告": """
        本季度项目进展顺利，完成了核心功能模块的开发和测试。用户界面优化提升了30%的
        用户体验评分。性能优化减少了50%的响应时间。安全审计发现并修复了8个潜在漏洞。
        代码质量评分从B+提升到A-。团队协作效率通过敏捷开发方法得到改善。预算控制
        良好，实际支出比计划少15%。下一阶段将重点关注功能扩展和用户反馈处理。
        """,
        "市场分析": """
        市场调研显示，目标用户群体对产品功能满意度达到85%。竞争分析表明我们在技术
        创新方面领先主要竞争对手6个月。价格策略需要调整以提高市场份额。客户获取
        成本持续下降，ROI提升40%。品牌认知度在目标市场提高了25%。销售渠道优化
        带来了20%的转化率提升。合作伙伴网络扩展到15个新的区域市场。
        """
    }
    
    fractal_text = [[""]]
    
    for doc_type, content in documents.items():
        print(f"\\n📄 处理文档: {doc_type}")
        print(f"原始长度: {len(content)} 字符")
        
        fractal_text = compressor.compress(fractal_text, f"\\n=== {doc_type} ===\\n{content}")
        
        info = compressor.get_fractal_info(fractal_text)
        print(f"压缩后总长度: {info['total_length']} 字符")
        print(f"当前层数: {info['total_levels']}")
        
        if 'compression_efficiency' in info:
            eff = info['compression_efficiency']
            print(f"整体压缩率: {eff['overall_ratio']:.3f}")
            print(f"节省空间: {eff['space_saved']} 字符")
    
    print("\\n" + "=" * 50)
    print("📊 文档管理系统最终状态:")
    print(compressor.visualize_fractal(fractal_text))
    
    # 展示实际的分层内容
    print("\\n📋 各层内容预览:")
    for level, texts in enumerate(fractal_text):
        if texts and texts[0]:
            print(f"\\nLevel {level}:")
            preview = texts[0][:200] + "..." if len(texts[0]) > 200 else texts[0]
            print(f"  {preview}")
    
    return fractal_text


def main():
    """主演示程序"""
    print("🌀 Fractal Compress v2.0 演示程序")
    print("真正的分形文本压缩算法")
    print("基于黄金分割比例 (0.618) 的分形压缩")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("   LLM压缩功能将无法工作")
        print("   请设置环境变量后重试")
        return
    
    try:
        # 运行各种演示
        demo_basic_fractal()
        demo_custom_prompts()
        demo_progressive_compression()
        demo_real_world_scenario()
        
        print("\\n🎉 所有演示完成!")
        print("\\n💡 核心特点:")
        print("  ✅ 真正的分形算法 (黄金分割比例)")
        print("  ✅ 智能门限管理 (自动触发压缩)")
        print("  ✅ 独立的Prompt配置")
        print("  ✅ 多层递归压缩")
        print("  ✅ 详细的统计分析")
        
    except Exception as e:
        print(f"\\n❌ 演示过程中出现错误: {e}")
        print("   请检查网络连接和API密钥设置")


if __name__ == "__main__":
    main()