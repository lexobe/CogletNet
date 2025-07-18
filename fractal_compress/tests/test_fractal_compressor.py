"""
分形压缩器测试用例
"""

import pytest
from fractal_compress.utils import EnhancedHybridCompressor, LLMTextCompressor, smart_split


class TestTextSplitter:
    """文本分割器测试类"""
    
    def test_smart_split_basic(self):
        """测试基本分割功能"""
        text = "这是一个测试文本，用于验证分割功能"
        part_a, part_b = smart_split(text, ratio=0.4)
        
        assert len(part_a) + len(part_b) == len(text)
        assert abs(len(part_a) / len(text) - 0.4) < 0.1


class TestEnhancedHybridCompressor:
    """增强混合压缩器测试类"""
    
    def test_init(self):
        """测试初始化"""
        compressor = EnhancedHybridCompressor(default_model="gpt-4o-mini")
        assert compressor.default_model == "gpt-4o-mini"
    
    def test_compress_text_with_llm(self):
        """测试LLM压缩功能"""
        compressor = EnhancedHybridCompressor()
        
        # 使用mock函数测试，避免实际API调用
        result = compressor.compress_text_with_llm(
            text="测试文本",
            target_length=5,
            max_attempts=1,
            custom_templates={"few_shot_precise": "简单模板: {text} -> 压缩到{target_length}字符"}
        )
        
        assert "text" in result
        assert "success" in result
        assert result["original_length"] == 4


class TestLLMTextCompressor:
    """独立LLM压缩器测试类"""
    
    def test_init(self):
        """测试初始化"""
        compressor = LLMTextCompressor(default_model="gpt-4o-mini")
        assert compressor.default_model == "gpt-4o-mini"
        assert len(compressor.default_templates) == 5
        assert len(compressor.default_examples) == 3
    
    def test_build_prompt(self):
        """测试prompt构建"""
        compressor = LLMTextCompressor()
        
        prompt = compressor._build_prompt(
            template="压缩: {text} 到 {target_length}字符",
            text="测试文本",
            target_length=5,
            strategy="basic",
            examples=[]
        )
        
        assert "测试文本" in prompt
        assert "5" in prompt
    
    def test_clean_output(self):
        """测试输出清理"""
        compressor = LLMTextCompressor()
        
        # 测试引号移除
        assert compressor._clean_output('"测试文本"') == "测试文本"
        assert compressor._clean_output("'测试文本'") == "测试文本"
        
        # 测试前缀移除
        assert compressor._clean_output("压缩结果：测试文本") == "测试文本"
        assert compressor._clean_output("输出：测试文本") == "测试文本"
    
    def test_smart_truncate(self):
        """测试智能截断"""
        compressor = LLMTextCompressor()
        
        # 测试标点符号截断
        text = "这是一个测试。另一个句子"
        result = compressor._smart_truncate(text, 7)
        assert result == "这是一个测试。"
        
        # 测试直接截断
        result = compressor._smart_truncate("测试文本", 2)
        assert result == "测试"
    
    def test_validate_quality(self):
        """测试质量验证"""
        compressor = LLMTextCompressor()
        
        # 测试成功案例
        assert compressor._validate_quality("压缩", "原始文本", 10, True) == True
        
        # 测试失败案例
        assert compressor._validate_quality("", "原始文本", 10, True) == False
        assert compressor._validate_quality("原始文本", "原始文本", 10, True) == False
        assert compressor._validate_quality("超长的压缩结果", "原始文本", 5, True) == False


if __name__ == "__main__":
    pytest.main([__file__])