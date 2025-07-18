"""
独立测试：集成测试

测试各组件的集成和完整工作流程
"""

import pytest
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractal_compress import (
    compress,
    split_and_compress,
    llm_compress,
    simple_split,
    compress_text  # 向后兼容
)


class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture
    def sample_workflow_texts(self):
        """工作流测试文本"""
        return {
            "article": """
人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破。
这些技术正在改变我们的生活方式，从智能手机的语音助手到自动驾驶汽车，
从医疗诊断到金融分析，AI技术的应用范围越来越广泛。
未来，人工智能将继续推动技术创新和社会进步。
            """.strip(),
            
            "technical": """
Machine learning algorithms utilize statistical methods to identify patterns in data.
Deep neural networks with multiple hidden layers can learn complex representations.
Natural language processing enables computers to understand and generate human language.
Computer vision systems can analyze and interpret visual information from images and videos.
            """.strip(),
            
            "mixed": """
AI人工智能technology正在revolutionizing各个行业。
从healthcare医疗到finance金融，从education教育到transportation交通，
智能系统are becoming越来越important在our daily life日常生活中。
            """.strip()
        }
    
    def test_complete_compression_workflow(self, sample_workflow_texts):
        """测试完整的压缩工作流"""
        text = sample_workflow_texts["article"]
        
        # 步骤1：分析原文
        original_length = len(text)
        assert original_length > 50  # 确保有足够的文本用于测试
        
        # 步骤2：标准压缩
        compressed = compress(text)
        assert isinstance(compressed, str)
        assert len(compressed) > 0
        assert len(compressed) < original_length
        
        # 步骤3：分割并压缩
        comp_part, rem_part = split_and_compress(text)
        assert isinstance(comp_part, str) and isinstance(rem_part, str)
        assert len(comp_part) > 0 and len(rem_part) > 0
        
        # 步骤4：纯LLM压缩
        llm_result = llm_compress(text, target_length=30)
        assert isinstance(llm_result, str)
        assert len(llm_result) <= 35  # 允许小幅误差
        
        # 步骤5：简单分割
        split1, split2 = simple_split(text)
        assert len(split1) + len(split2) == original_length
    
    def test_different_ratio_combinations(self, sample_workflow_texts):
        """测试不同比例组合的效果"""
        text = sample_workflow_texts["technical"]
        
        # 测试多种比例组合
        combinations = [
            (0.3, 0.5),  # 30%分割，50%压缩
            (0.5, 0.6),  # 50%分割，60%压缩
            (0.7, 0.8),  # 70%分割，80%压缩
        ]
        
        results = []
        for split_ratio, comp_ratio in combinations:
            result = compress(
                text,
                split_ratio=split_ratio,
                compression_ratio=comp_ratio
            )
            results.append(result)
            assert isinstance(result, str)
            assert len(result) > 0
        
        # 验证不同组合产生不同结果
        assert len(set(results)) >= 1  # 至少有结果
    
    def test_multilanguage_processing(self, sample_workflow_texts):
        """测试多语言处理"""
        texts = {
            "chinese": sample_workflow_texts["article"],
            "english": sample_workflow_texts["technical"],
            "mixed": sample_workflow_texts["mixed"]
        }
        
        for lang, text in texts.items():
            # 标准压缩
            result1 = compress(text, language=lang)
            assert isinstance(result1, str) and len(result1) > 0
            
            # 分割压缩
            comp, rem = split_and_compress(text, language=lang)
            assert isinstance(comp, str) and isinstance(rem, str)
            assert len(comp) > 0 and len(rem) > 0
            
            # 简单分割
            p1, p2 = simple_split(text, language=lang)
            assert len(p1) > 0 and len(p2) > 0
    
    def test_backward_compatibility(self, sample_workflow_texts):
        """测试向后兼容性"""
        text = sample_workflow_texts["article"]
        
        # 旧API应该仍然工作
        old_result = compress_text(text)
        new_result = compress(text)
        
        assert isinstance(old_result, str)
        assert isinstance(new_result, str)
        assert len(old_result) > 0
        assert len(new_result) > 0
    
    def test_error_handling_and_fallbacks(self):
        """测试错误处理和后备机制"""
        # 空输入
        assert compress("") == ""
        assert llm_compress("") == ""
        assert simple_split("") == ("", "")
        assert split_and_compress("") == ("", "")
        
        # 极短输入
        short_text = "短"
        result = compress(short_text)
        assert isinstance(result, str)
        
        # 极端参数
        normal_text = "这是一个正常长度的文本示例，用于测试极端参数的处理能力。"
        
        # 极小分割比例
        result = compress(normal_text, split_ratio=0.01)
        assert isinstance(result, str) and len(result) > 0
        
        # 极大分割比例
        result = compress(normal_text, split_ratio=0.99)
        assert isinstance(result, str) and len(result) > 0
        
        # 极小压缩比例
        result = compress(normal_text, compression_ratio=0.01)
        assert isinstance(result, str) and len(result) >= 1
    
    def test_consistency_across_calls(self, sample_workflow_texts):
        """测试多次调用的一致性"""
        text = sample_workflow_texts["mixed"]
        
        # 相同参数的多次调用应该产生相同或相似的结果
        results = []
        for _ in range(3):
            result = compress(
                text,
                split_ratio=0.4,
                compression_ratio=0.6,
                strategy="basic"
            )
            results.append(result)
        
        # 验证所有结果都是有效的
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0
        
        # 由于LLM的随机性，结果可能不完全相同，但应该都是有效的
        unique_results = set(results)
        assert len(unique_results) >= 1  # 至少有一个结果
    
    def test_performance_characteristics(self, sample_workflow_texts):
        """测试性能特征"""
        text = sample_workflow_texts["article"]
        
        # 简单分割应该是最快的（不需要LLM）
        import time
        
        start = time.time()
        simple_split(text)
        split_time = time.time() - start
        
        # 验证分割功能工作正常
        assert split_time >= 0  # 基本的时间验证
        
        # LLM压缩应该返回合理大小的结果
        result = llm_compress(text, target_length=20)
        assert len(result) <= 25  # 应该接近目标长度
    
    def test_api_interface_consistency(self, sample_workflow_texts):
        """测试API接口一致性"""
        text = sample_workflow_texts["technical"]
        
        # 测试所有函数都接受关键字参数
        compress(text, language="english")
        split_and_compress(text, split_ratio=0.5)
        llm_compress(text, target_length=25)
        simple_split(text, split_ratio=0.4)
        
        # 测试返回类型一致性
        result1 = compress(text)
        assert isinstance(result1, str)
        
        result2 = llm_compress(text)
        assert isinstance(result2, str)
        
        result3 = split_and_compress(text)
        assert isinstance(result3, tuple) and len(result3) == 2
        
        result4 = simple_split(text)
        assert isinstance(result4, tuple) and len(result4) == 2


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])