"""
Test Suite for Fractal Compress API

Clean, comprehensive tests for the new API.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractal_compress import compress, split_compress, llm_compress, split


class TestBasicAPI:
    """Test basic API functionality."""
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return {
            "chinese": "人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破。",
            "english": "Artificial intelligence technology is rapidly advancing with breakthrough achievements.",
            "mixed": "AI人工智能technology正在rapidly发展，bringing革命性changes。",
            "short": "短文本",
            "empty": "",
            "long": "这是一个很长的文本示例，包含多个句子和段落内容。" * 10
        }
    
    def test_compress_basic(self, sample_texts):
        """Test basic compression functionality."""
        # Test with different texts
        for key, text in sample_texts.items():
            if key == "empty":
                assert compress(text) == ""
            else:
                result = compress(text)
                assert isinstance(result, str)
                if text:
                    assert len(result) > 0
                    assert len(result) <= len(text)
    
    def test_compress_custom_ratios(self, sample_texts):
        """Test compression with custom ratios."""
        text = sample_texts["chinese"]
        
        # Test different split ratios
        result1 = compress(text, split_ratio=0.3)
        result2 = compress(text, split_ratio=0.7)
        
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert len(result1) > 0
        assert len(result2) > 0
        
        # Test different compression ratios
        result3 = compress(text, compression_ratio=0.3)
        result4 = compress(text, compression_ratio=0.8)
        
        # Lower compression ratio should produce shorter result
        assert len(result3) <= len(result4)
    
    def test_split_compress(self, sample_texts):
        """Test split_compress functionality."""
        text = sample_texts["chinese"]
        
        compressed, remaining = split_compress(text)
        
        assert isinstance(compressed, str)
        assert isinstance(remaining, str)
        assert len(compressed) > 0
        assert len(remaining) > 0
        assert len(compressed) + len(remaining) < len(text)  # Some compression occurred
    
    def test_llm_compress(self, sample_texts):
        """Test direct LLM compression."""
        text = sample_texts["english"]
        
        # Test with specific target length
        result = llm_compress(text, target_length=20)
        assert isinstance(result, str)
        assert len(result) <= 25  # Allow small deviation
        assert len(result) > 0
        
        # Test with zero target
        result_zero = llm_compress(text, target_length=0)
        assert result_zero == ""
    
    def test_split(self, sample_texts):
        """Test text splitting functionality."""
        text = sample_texts["chinese"]
        
        part1, part2 = split(text)
        
        assert isinstance(part1, str)
        assert isinstance(part2, str)
        assert len(part1) > 0
        assert len(part2) > 0
        assert len(part1) + len(part2) == len(text)  # Lossless splitting
    
    def test_language_parameters(self, sample_texts):
        """Test language parameter handling."""
        text = sample_texts["mixed"]
        
        # Test different language settings
        result_auto = compress(text, language="auto")
        result_chinese = compress(text, language="chinese")
        result_english = compress(text, language="english")
        
        assert isinstance(result_auto, str)
        assert isinstance(result_chinese, str)
        assert isinstance(result_english, str)
        
        # All should produce valid results
        assert len(result_auto) > 0
        assert len(result_chinese) > 0
        assert len(result_english) > 0
    
    def test_edge_cases(self, sample_texts):
        """Test edge cases and error conditions."""
        # Empty text
        assert compress("") == ""
        assert llm_compress("", 10) == ""
        assert split("") == ("", "")
        assert split_compress("") == ("", "")
        
        # Very short text
        short_result = compress(sample_texts["short"])
        assert isinstance(short_result, str)
        
        # Invalid split ratio
        with pytest.raises(ValueError):
            split("test", ratio=-0.1)
        
        with pytest.raises(ValueError):
            split("test", ratio=1.1)


class TestAdvancedFeatures:
    """Test advanced features and parameters."""
    
    def test_compression_strategies(self):
        """Test different LLM compression strategies."""
        text = "Machine learning algorithms are transforming data analysis capabilities worldwide."
        
        strategies = ["precise", "creative", "fast"]
        
        for strategy in strategies:
            result = llm_compress(text, target_length=25, strategy=strategy)
            assert isinstance(result, str)
            assert len(result) > 0
            assert len(result) <= 30  # Allow deviation
    
    def test_model_parameters(self):
        """Test different model parameters."""
        text = "人工智能技术正在改变世界"
        
        # Test with different models (will use default if not available)
        result = compress(text, model="gpt-4o-mini")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_ratio_combinations(self):
        """Test various ratio combinations."""
        text = "这是一个测试文本，用于验证不同比例参数的组合效果。" * 3
        
        combinations = [
            (0.2, 0.3),
            (0.4, 0.5),
            (0.6, 0.7),
            (0.8, 0.9)
        ]
        
        for split_r, comp_r in combinations:
            result = compress(text, split_ratio=split_r, compression_ratio=comp_r)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_multilingual_texts(self):
        """Test processing of different languages."""
        texts = {
            "pure_chinese": "中文文本处理测试内容",
            "pure_english": "English text processing test content",
            "mixed_content": "Mixed中文and英文content测试",
            "with_numbers": "包含123数字和symbols!@#的文本",
            "with_punctuation": "标点符号？！，。；：的处理测试"
        }
        
        for lang_type, text in texts.items():
            result = compress(text)
            assert isinstance(result, str)
            assert len(result) > 0


class TestPerformance:
    """Test performance characteristics."""
    
    def test_length_consistency(self):
        """Test that results are consistent with length constraints."""
        text = "长文本内容测试" * 20
        
        # Multiple runs should produce consistent lengths
        results = []
        for _ in range(3):
            result = llm_compress(text, target_length=30)
            results.append(len(result))
        
        # All results should respect length constraint
        for length in results:
            assert length <= 35  # Allow small deviation
    
    def test_compression_efficiency(self):
        """Test compression efficiency."""
        texts = [
            "短" * 10,
            "中等长度文本" * 5,
            "这是一个相对较长的文本示例" * 10
        ]
        
        for text in texts:
            result = compress(text)
            compression_ratio = len(result) / len(text)
            
            # Should achieve some compression
            assert compression_ratio < 1.0
            # But not over-compress
            assert compression_ratio > 0.1


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_pipeline_workflow(self):
        """Test complete processing pipeline."""
        # Simulate document processing pipeline
        document = """
        数据科学是一个跨学科领域，结合了统计学、计算机科学和领域专业知识。
        数据科学家使用各种工具和技术来从数据中提取见解。这个过程包括
        数据收集、清理、分析和结果解释等步骤。
        """
        
        # Step 1: Split document
        part1, part2 = split(document, ratio=0.6)
        assert len(part1) > 0
        assert len(part2) > 0
        
        # Step 2: Process parts differently
        summary = llm_compress(part1, target_length=30)
        compressed = compress(part2, compression_ratio=0.5)
        
        # Step 3: Verify results
        assert isinstance(summary, str)
        assert isinstance(compressed, str)
        assert len(summary) <= 35
        assert len(compressed) < len(part2)
    
    def test_batch_processing(self):
        """Test batch processing of multiple texts."""
        texts = [
            "文本1：人工智能发展迅速。",
            "Text 2: Machine learning advances.",
            "文本3：Mixed中英文content处理。"
        ]
        
        results = []
        for text in texts:
            result = compress(text, split_ratio=0.4, compression_ratio=0.6)
            results.append(result)
        
        # All results should be valid
        assert len(results) == len(texts)
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])