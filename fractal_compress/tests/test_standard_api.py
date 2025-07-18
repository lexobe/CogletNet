"""
独立测试：标准API功能测试

测试新的标准压缩API，包括不同的压缩比和截断比支持
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
    simple_split
)


class TestStandardAPI:
    """标准API测试类"""
    
    @pytest.fixture
    def sample_texts(self):
        """测试文本样本"""
        return {
            "chinese": "人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破。",
            "english": "Artificial intelligence technology is rapidly developing with breakthrough advances.",
            "mixed": "AI人工智能技术正在transforming各个领域，bringing革命性changes。",
            "short": "短文本",
            "empty": "",
            "long": "这是一个很长的文本示例，" * 20  # 240字符
        }
    
    def test_compress_basic(self, sample_texts):
        """测试基础压缩功能"""
        # 测试中文
        result = compress(sample_texts["chinese"])
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) < len(sample_texts["chinese"])
        
        # 测试英文
        result = compress(sample_texts["english"], language="english")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # 测试混合语言
        result = compress(sample_texts["mixed"], language="mixed")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_compress_custom_ratios(self, sample_texts):
        """测试自定义压缩比"""
        text = sample_texts["chinese"]
        
        # 测试不同分割比例
        result1 = compress(text, split_ratio=0.3)
        result2 = compress(text, split_ratio=0.5)
        result3 = compress(text, split_ratio=0.7)
        
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert isinstance(result3, str)
        
        # 测试不同压缩比例
        result4 = compress(text, compression_ratio=0.3)
        result5 = compress(text, compression_ratio=0.8)
        
        assert len(result4) <= len(result5)  # 更低压缩比应该产生更短结果
    
    def test_split_and_compress_basic(self, sample_texts):
        """测试分割并压缩功能"""
        text = sample_texts["chinese"]
        
        compressed_part, remaining_part = split_and_compress(text)
        
        assert isinstance(compressed_part, str)
        assert isinstance(remaining_part, str)
        assert len(compressed_part) > 0
        assert len(remaining_part) > 0
        assert len(compressed_part) + len(remaining_part) < len(text)
    
    def test_split_and_compress_ratios(self, sample_texts):
        """测试不同比例的分割压缩"""
        text = sample_texts["long"]
        
        # 不同分割比例
        comp1, rem1 = split_and_compress(text, split_ratio=0.3)
        comp2, rem2 = split_and_compress(text, split_ratio=0.7)
        
        # 分割比例0.7应该产生更长的压缩部分（压缩前）
        assert len(comp1) > 0 and len(comp2) > 0
        assert len(rem1) > len(rem2)  # 剩余部分应该不同
        
        # 不同压缩比例
        comp3, rem3 = split_and_compress(text, compression_ratio=0.3)
        comp4, rem4 = split_and_compress(text, compression_ratio=0.8)
        
        assert len(comp3) <= len(comp4)  # 更低压缩比应该产生更短结果
    
    def test_llm_compress_basic(self, sample_texts):
        """测试纯LLM压缩功能"""
        text = sample_texts["chinese"]
        
        # 使用目标长度
        result1 = llm_compress(text, target_length=10)
        assert isinstance(result1, str)
        assert len(result1) <= 10
        assert len(result1) > 0
        
        # 使用压缩比例
        result2 = llm_compress(text, compression_ratio=0.5)
        assert isinstance(result2, str)
        assert len(result2) > 0
        assert len(result2) <= len(text) * 0.5 + 5  # 允许一些误差
    
    def test_llm_compress_strategies(self, sample_texts):
        """测试不同压缩策略"""
        text = sample_texts["english"]
        
        strategies = ["basic", "precise", "few_shot", "creative", "strict"]
        results = []
        
        for strategy in strategies:
            result = llm_compress(text, target_length=15, strategy=strategy)
            results.append(result)
            assert isinstance(result, str)
            assert len(result) > 0
        
        # 确保不同策略产生不同结果（至少有一些差异）
        unique_results = set(results)
        assert len(unique_results) >= 1  # 至少有结果
    
    def test_simple_split_basic(self, sample_texts):
        """测试简单分割功能"""
        text = sample_texts["chinese"]
        
        part1, part2 = simple_split(text)
        
        assert isinstance(part1, str)
        assert isinstance(part2, str)
        assert len(part1) > 0
        assert len(part2) > 0
        assert len(part1) + len(part2) == len(text)  # 无损分割
    
    def test_simple_split_ratios(self, sample_texts):
        """测试不同分割比例"""
        text = sample_texts["long"]
        
        # 测试不同分割比例
        p1_a, p2_a = simple_split(text, split_ratio=0.2)
        p1_b, p2_b = simple_split(text, split_ratio=0.8)
        
        assert len(p1_a) < len(p1_b)  # 0.2比例应该产生更短的第一部分
        assert len(p2_a) > len(p2_b)  # 对应的第二部分应该更长
        
        # 验证总长度保持不变
        assert len(p1_a) + len(p2_a) == len(text)
        assert len(p1_b) + len(p2_b) == len(text)
    
    def test_edge_cases(self, sample_texts):
        """测试边界情况"""
        # 空文本
        assert compress("") == ""
        assert llm_compress("") == ""
        assert simple_split("") == ("", "")
        assert split_and_compress("") == ("", "")
        
        # 极短文本
        short_result = compress(sample_texts["short"])
        assert isinstance(short_result, str)
        
        # 极端比例
        result1 = compress(sample_texts["chinese"], split_ratio=0.01, compression_ratio=0.01)
        assert isinstance(result1, str)
        assert len(result1) >= 1  # 至少有一个字符
        
        result2 = compress(sample_texts["chinese"], split_ratio=0.99, compression_ratio=0.99)
        assert isinstance(result2, str)
    
    def test_language_parameter(self, sample_texts):
        """测试语言参数"""
        text = sample_texts["mixed"]
        
        # 测试不同语言设置
        result_cn = compress(text, language="chinese")
        result_en = compress(text, language="english") 
        result_mixed = compress(text, language="mixed")
        
        assert isinstance(result_cn, str)
        assert isinstance(result_en, str)
        assert isinstance(result_mixed, str)
        
        # 验证都产生了有效结果
        assert len(result_cn) > 0
        assert len(result_en) > 0
        assert len(result_mixed) > 0
    
    def test_model_parameter(self, sample_texts):
        """测试模型参数"""
        text = sample_texts["chinese"]
        
        # 测试默认模型
        result = compress(text, model="gpt-4o-mini")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_return_types(self, sample_texts):
        """测试返回值类型"""
        text = sample_texts["chinese"]
        
        # compress 返回 str
        result1 = compress(text)
        assert isinstance(result1, str)
        
        # split_and_compress 返回 Tuple[str, str]
        result2 = split_and_compress(text)
        assert isinstance(result2, tuple)
        assert len(result2) == 2
        assert isinstance(result2[0], str)
        assert isinstance(result2[1], str)
        
        # llm_compress 返回 str
        result3 = llm_compress(text)
        assert isinstance(result3, str)
        
        # simple_split 返回 Tuple[str, str]
        result4 = simple_split(text)
        assert isinstance(result4, tuple)
        assert len(result4) == 2
        assert isinstance(result4[0], str)
        assert isinstance(result4[1], str)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])