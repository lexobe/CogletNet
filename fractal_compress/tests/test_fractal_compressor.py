"""
分形压缩器测试用例
"""

import pytest
from fractal_compress import FractalCompressor, PromptManager


class TestFractalCompressor:
    """分形压缩器测试类"""
    
    def test_init(self):
        """测试初始化"""
        compressor = FractalCompressor(
            ratio=0.618,
            base_threshold=1000,
            max_levels=10
        )
        
        assert compressor.ratio == 0.618
        assert compressor.base_threshold == 1000
        assert compressor.max_levels == 10
        assert compressor.prompt_manager is not None
        
    def test_get_level_threshold(self):
        """测试层级门限计算"""
        compressor = FractalCompressor(
            ratio=0.618,
            base_threshold=1000
        )
        
        # 测试各层门限
        assert compressor._get_level_threshold(0) == 1000
        assert compressor._get_level_threshold(1) == int(1000 * 0.618)
        assert compressor._get_level_threshold(2) == int(1000 * 0.618 * 0.618)
        
    def test_basic_compression_structure(self):
        """测试基本压缩结构"""
        compressor = FractalCompressor(
            ratio=0.618,
            base_threshold=50,  # 小门限便于测试
            max_levels=3
        )
        
        # 初始状态
        fractal_text = [[""]]
        
        # 添加短文本（不会触发压缩）
        short_text = "短文本"
        result = compressor.compress(fractal_text, short_text)
        
        assert len(result) == 1  # 仍然只有一层
        assert result[0][0] == short_text
        
    def test_fractal_text_structure(self):
        """测试分形文本数据结构"""
        compressor = FractalCompressor()
        
        # 测试空输入
        result = compressor.compress([], "test")
        assert len(result) == 1
        assert result[0][0] == "test"
        
        # 测试现有结构
        fractal_text = [["existing text"]]
        result = compressor.compress(fractal_text, " new text")
        assert result[0][0] == "existing text new text"
        
    def test_get_fractal_info(self):
        """测试分形信息获取"""
        compressor = FractalCompressor(base_threshold=100)
        
        fractal_text = [
            ["Level 0 content with sufficient length to test"],
            ["Level 1 compressed content"]
        ]
        
        info = compressor.get_fractal_info(fractal_text)
        
        assert info["total_levels"] == 2
        assert len(info["level_details"]) == 2
        assert info["total_length"] > 0
        
        # 检查层级详情
        level0_info = info["level_details"][0]
        assert level0_info["level"] == 0
        assert level0_info["threshold"] == 100
        
    def test_visualize_fractal(self):
        """测试分形可视化"""
        compressor = FractalCompressor()
        
        fractal_text = [
            ["Level 0 content"],
            ["Level 1 content"]
        ]
        
        visualization = compressor.visualize_fractal(fractal_text)
        
        assert "分形文本结构可视化" in visualization
        assert "Level 0" in visualization
        assert "Level 1" in visualization
        
    def test_compression_stats(self):
        """测试压缩统计"""
        compressor = FractalCompressor()
        
        # 初始状态
        assert compressor.compression_stats["total_compressions"] == 0
        
        # 模拟压缩统计更新
        compressor._update_compression_stats(0, 100, 60)
        
        assert compressor.compression_stats["total_compressions"] == 1
        assert 0 in compressor.compression_stats["level_usage"]
        
        level_stats = compressor.compression_stats["level_usage"][0]
        assert level_stats["count"] == 1
        assert level_stats["total_original"] == 100
        assert level_stats["total_compressed"] == 60
        
    def test_reset_stats(self):
        """测试统计重置"""
        compressor = FractalCompressor()
        
        # 添加一些统计数据
        compressor._update_compression_stats(0, 100, 60)
        assert compressor.compression_stats["total_compressions"] == 1
        
        # 重置
        compressor.reset_stats()
        assert compressor.compression_stats["total_compressions"] == 0
        assert compressor.compression_stats["level_usage"] == {}
        
    def test_get_config(self):
        """测试配置获取"""
        prompt_manager = PromptManager({"test_key": "test_value"})
        compressor = FractalCompressor(
            ratio=0.7,
            base_threshold=500,
            max_levels=5,
            prompt_manager=prompt_manager
        )
        
        config = compressor.get_config()
        
        assert config["ratio"] == 0.7
        assert config["base_threshold"] == 500
        assert config["max_levels"] == 5
        assert "prompt_config" in config
        assert config["prompt_config"]["test_key"] == "test_value"


class TestPromptManager:
    """Prompt管理器测试类"""
    
    def test_init_default(self):
        """测试默认初始化"""
        pm = PromptManager()
        
        assert "system_prompt" in pm.config
        assert "compression_template" in pm.config
        assert "parameters" in pm.config
        assert pm.config["compression_ratio"] == 0.618
        
    def test_init_custom(self):
        """测试自定义初始化"""
        custom_config = {
            "system_prompt": "Custom system prompt",
            "compression_ratio": 0.5
        }
        
        pm = PromptManager(custom_config)
        
        assert pm.config["system_prompt"] == "Custom system prompt"
        assert pm.config["compression_ratio"] == 0.5
        
    def test_get_compression_prompt(self):
        """测试压缩提示词生成"""
        pm = PromptManager()
        
        text = "This is a test text for compression"
        prompt = pm.get_compression_prompt(text, target_length=20)
        
        assert text in prompt
        assert "20" in prompt
        
    def test_get_compression_prompt_with_level(self):
        """测试带层级的压缩提示词"""
        pm = PromptManager()
        
        text = "Test text"
        prompt_level0 = pm.get_compression_prompt(text, level=0)
        prompt_level1 = pm.get_compression_prompt(text, level=1)
        
        # 更高层级应该有更小的目标长度
        assert prompt_level0 != prompt_level1
        
    def test_get_system_prompt(self):
        """测试系统提示词获取"""
        pm = PromptManager()
        system_prompt = pm.get_system_prompt()
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        
    def test_get_llm_parameters(self):
        """测试LLM参数获取"""
        pm = PromptManager()
        params = pm.get_llm_parameters()
        
        assert "temperature" in params
        assert "max_tokens" in params
        assert "model" in params
        
    def test_update_config(self):
        """测试配置更新"""
        pm = PromptManager()
        
        new_config = {"compression_ratio": 0.5}
        pm.update_config(new_config)
        
        assert pm.config["compression_ratio"] == 0.5
        
    def test_create_custom_template(self):
        """测试自定义模板创建"""
        pm = PromptManager()
        
        template = "Custom template with {text} and {target_length}"
        params = {"temperature": 0.1}
        
        pm.create_custom_template("test_template", template, params)
        
        assert "custom_templates" in pm.config
        assert "test_template" in pm.config["custom_templates"]
        assert pm.config["custom_templates"]["test_template"]["template"] == template
        
    def test_use_custom_template(self):
        """测试使用自定义模板"""
        pm = PromptManager()
        
        # 创建自定义模板
        template = "Custom: {text} -> {target_length}"
        pm.create_custom_template("test", template)
        
        # 使用自定义模板
        pm.use_custom_template("test")
        
        assert pm.config["compression_template"] == template
        
    def test_get_compression_stats(self):
        """测试压缩统计信息"""
        pm = PromptManager()
        
        stats = pm.get_compression_stats(100, 2)
        
        assert stats["original_length"] == 100
        assert stats["base_target_length"] == int(100 * 0.618)
        assert stats["level_adjustment"] == 0.8 ** 2
        assert "expected_ratio" in stats


if __name__ == "__main__":
    pytest.main([__file__])