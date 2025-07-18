"""
独立测试：核心组件测试

测试text_splitter和llm_compressor的核心功能
"""

import pytest
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractal_compress.utils.text_splitter import smart_split
from fractal_compress.utils.llm_compressor import LLMTextCompressor, quick_compress, compare_strategies


class TestTextSplitter:
    """文本分割器测试"""
    
    @pytest.fixture
    def sample_texts(self):
        return {
            "chinese": "人工智能技术正在快速发展。机器学习和深度学习领域取得了重大突破。这些技术正在改变我们的生活方式。",
            "english": "Artificial intelligence technology is rapidly developing. Machine learning and deep learning have achieved major breakthroughs. These technologies are changing our way of life.",
            "mixed": "AI人工智能technology正在快速developing。ML机器学习和deep learning深度学习取得breakthrough突破。",
            "short": "短文本。",
            "no_punctuation": "这是一个没有标点符号的长文本示例内容",
            "long": "这是一个很长的文本示例，包含多个句子和段落。" * 10
        }
    
    def test_basic_split(self, sample_texts):
        """测试基础分割功能"""
        text = sample_texts["chinese"]
        part1, part2 = smart_split(text)
        
        assert isinstance(part1, str)
        assert isinstance(part2, str)
        assert len(part1) > 0
        assert len(part2) > 0
        assert len(part1) + len(part2) <= len(text)  # 可能有微小的空白处理差异
    
    def test_different_ratios(self, sample_texts):
        """测试不同分割比例"""
        text = sample_texts["long"]
        
        ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
        results = []
        
        for ratio in ratios:
            part1, part2 = smart_split(text, ratio=ratio)
            results.append((len(part1), len(part2)))
            
            # 验证比例大致正确（允许一些偏差）
            expected_len1 = len(text) * ratio
            actual_ratio = len(part1) / len(text)
            assert abs(actual_ratio - ratio) < 0.2  # 允许20%偏差
        
        # 验证比例递增时第一部分长度大致递增
        part1_lengths = [r[0] for r in results]
        for i in range(1, len(part1_lengths)):
            assert part1_lengths[i] >= part1_lengths[i-1] - 10  # 允许小幅波动
    
    def test_different_languages(self, sample_texts):
        """测试不同语言处理"""
        # 中文
        p1, p2 = smart_split(sample_texts["chinese"], language="chinese")
        assert len(p1) > 0 and len(p2) > 0
        
        # 英文
        p1, p2 = smart_split(sample_texts["english"], language="english")
        assert len(p1) > 0 and len(p2) > 0
        
        # 混合
        p1, p2 = smart_split(sample_texts["mixed"], language="mixed")
        assert len(p1) > 0 and len(p2) > 0
    
    def test_deviation_threshold(self, sample_texts):
        """测试偏差阈值"""
        text = sample_texts["chinese"]
        
        # 小偏差阈值应该更精确
        p1_strict, p2_strict = smart_split(text, deviation_threshold=0.01)
        p1_loose, p2_loose = smart_split(text, deviation_threshold=0.3)
        
        assert len(p1_strict) > 0 and len(p2_strict) > 0
        assert len(p1_loose) > 0 and len(p2_loose) > 0
    
    def test_edge_cases(self, sample_texts):
        """测试边界情况"""
        # 空文本
        p1, p2 = smart_split("")
        assert p1 == "" and p2 == ""
        
        # 极短文本
        p1, p2 = smart_split("短")
        assert isinstance(p1, str) and isinstance(p2, str)
        
        # 无标点文本
        p1, p2 = smart_split(sample_texts["no_punctuation"])
        assert len(p1) > 0 and len(p2) > 0
    
    def test_parameter_validation(self):
        """测试参数验证"""
        text = "测试文本内容"
        
        # 无效比例
        with pytest.raises(ValueError):
            smart_split(text, ratio=-0.1)
        
        with pytest.raises(ValueError):
            smart_split(text, ratio=1.1)
        
        # 无效偏差阈值
        with pytest.raises(ValueError):
            smart_split(text, deviation_threshold=0.0001)
        
        with pytest.raises(ValueError):
            smart_split(text, deviation_threshold=0.6)
        
        # 无效语言
        with pytest.raises(ValueError):
            smart_split(text, language="invalid")


class TestLLMCompressor:
    """LLM压缩器测试"""
    
    @pytest.fixture
    def sample_texts(self):
        return {
            "chinese": "人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破",
            "english": "Artificial intelligence technology is rapidly developing with breakthrough advances",
            "mixed": "AI人工智能technology正在快速developing，bringing革命性changes",
            "short": "短文本",
            "long": "这是一个很长的文本示例，包含多个句子和段落内容。" * 5
        }
    
    def test_basic_compression(self, sample_texts):
        """测试基础压缩功能"""
        compressor = LLMTextCompressor()
        text = sample_texts["chinese"]
        
        result = compressor.compress(text, target_length=20)
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "success" in result
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0
        assert len(result["text"]) <= 20
    
    def test_different_strategies(self, sample_texts):
        """测试不同压缩策略"""
        compressor = LLMTextCompressor()
        text = sample_texts["english"]
        target_length = 25
        
        strategies = ["basic", "precise", "few_shot", "creative", "strict"]
        results = {}
        
        for strategy in strategies:
            result = compressor.compress(text, target_length=target_length, strategy=strategy)
            results[strategy] = result
            
            assert isinstance(result, dict)
            assert "text" in result
            assert len(result["text"]) > 0
            assert len(result["text"]) <= target_length + 5  # 允许小幅超出
    
    def test_different_target_lengths(self, sample_texts):
        """测试不同目标长度"""
        compressor = LLMTextCompressor()
        text = sample_texts["long"]
        
        target_lengths = [5, 10, 20, 30, 50]
        
        for target_length in target_lengths:
            result = compressor.compress(text, target_length=target_length)
            
            assert isinstance(result, dict)
            assert len(result["text"]) > 0
            assert len(result["text"]) <= target_length + 5  # 允许小幅误差
    
    def test_batch_test(self, sample_texts):
        """测试批量测试功能"""
        compressor = LLMTextCompressor()
        
        test_cases = [
            {"text": sample_texts["chinese"], "target": 15},
            {"text": sample_texts["english"], "target": 20},
            {"text": sample_texts["mixed"], "target": 18}
        ]
        
        batch_result = compressor.batch_test(test_cases, strategies=["basic", "precise"])
        
        assert isinstance(batch_result, dict)
        assert "results" in batch_result
        assert "statistics" in batch_result
        assert len(batch_result["results"]) == 2  # 两个策略
    
    def test_quick_compress_function(self, sample_texts):
        """测试快速压缩函数"""
        text = sample_texts["chinese"]
        result = quick_compress(text, target_length=15)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= 15 + 5  # 允许小幅误差
    
    def test_compare_strategies_function(self, sample_texts):
        """测试策略比较函数"""
        text = sample_texts["english"]
        results = compare_strategies(text, target_length=20)
        
        assert isinstance(results, dict)
        assert len(results) > 0
        
        for strategy, result in results.items():
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_custom_parameters(self, sample_texts):
        """测试自定义参数"""
        compressor = LLMTextCompressor()
        text = sample_texts["chinese"]
        
        # 测试不同温度
        result1 = compressor.compress(text, target_length=20, temperature=0.1)
        result2 = compressor.compress(text, target_length=20, temperature=0.5)
        
        assert isinstance(result1, dict) and isinstance(result2, dict)
        assert len(result1["text"]) > 0 and len(result2["text"]) > 0
        
        # 测试不同最大尝试次数
        result3 = compressor.compress(text, target_length=20, max_attempts=1)
        assert isinstance(result3, dict)
        assert len(result3["text"]) > 0
    
    def test_edge_cases(self, sample_texts):
        """测试边界情况"""
        compressor = LLMTextCompressor()
        
        # 空文本
        result = compressor.compress("", target_length=10)
        assert result["text"] == ""
        
        # 极短目标长度
        result = compressor.compress(sample_texts["chinese"], target_length=1)
        assert len(result["text"]) >= 1
        
        # 目标长度大于原文
        short_text = "短文本"
        result = compressor.compress(short_text, target_length=100)
        assert len(result["text"]) <= len(short_text)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])