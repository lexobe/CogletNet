"""
提示词管理器 - 管理LLM压缩的提示词配置
"""

import json
from typing import Dict, Any, Optional


class PromptManager:
    """
    提示词管理器
    
    将prompt作为独立的数据进行管理，支持动态配置和模板化。
    """
    
    def __init__(self, prompt_config: Optional[Dict[str, Any]] = None):
        """
        初始化提示词管理器
        
        Args:
            prompt_config: 提示词配置字典
        """
        self.config = prompt_config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认提示词配置"""
        return {
            "system_prompt": (
                "你是一个专业的文本压缩助手，需要将给定的文本压缩到指定长度，"
                "同时保持核心信息和语义完整性。"
            ),
            "compression_template": (
                "请将以下文本压缩到约 {target_length} 个字符：\n\n"
                "{text}\n\n"
                "要求：\n"
                "1. 保持核心信息和关键概念\n"
                "2. 保持语言的流畅性和可读性\n"
                "3. 尽量达到目标长度\n"
                "4. 直接返回压缩后的文本，不要添加额外说明\n"
            ),
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 2000,
                "model": "gpt-4o-mini"
            },
            "compression_ratio": 0.618  # 目标压缩比例
        }
        
    def get_compression_prompt(
        self, 
        text: str, 
        target_length: Optional[int] = None,
        level: int = 0
    ) -> str:
        """
        生成压缩提示词
        
        Args:
            text: 需要压缩的文本
            target_length: 目标长度，如果不指定则根据压缩比例计算
            level: 当前压缩层级（可用于调整压缩策略）
            
        Returns:
            str: 格式化后的提示词
        """
        if target_length is None:
            target_length = int(len(text) * self.config["compression_ratio"])
            
        # 根据层级调整压缩策略
        if level > 0:
            # 更深层级使用更激进的压缩
            target_length = int(target_length * (0.8 ** level))
            
        return self.config["compression_template"].format(
            text=text,
            target_length=target_length
        )
        
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.config["system_prompt"]
        
    def get_llm_parameters(self) -> Dict[str, Any]:
        """获取LLM调用参数"""
        return self.config["parameters"].copy()
        
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            new_config: 新的配置字典
        """
        self.config.update(new_config)
        
    def load_from_file(self, file_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            file_path: 配置文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.config.update(config)
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {e}")
            
    def save_to_file(self, file_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {e}")
            
    def create_custom_template(
        self, 
        template_name: str, 
        template: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        创建自定义模板
        
        Args:
            template_name: 模板名称
            template: 模板内容
            parameters: 模板参数
        """
        if "custom_templates" not in self.config:
            self.config["custom_templates"] = {}
            
        self.config["custom_templates"][template_name] = {
            "template": template,
            "parameters": parameters or {}
        }
        
    def use_custom_template(self, template_name: str) -> None:
        """
        使用自定义模板
        
        Args:
            template_name: 模板名称
        """
        if "custom_templates" not in self.config:
            raise ValueError("没有自定义模板")
            
        if template_name not in self.config["custom_templates"]:
            raise ValueError(f"模板 '{template_name}' 不存在")
            
        template_config = self.config["custom_templates"][template_name]
        self.config["compression_template"] = template_config["template"]
        
        if template_config["parameters"]:
            self.config["parameters"].update(template_config["parameters"])
            
    def get_compression_stats(self, original_length: int, level: int) -> Dict[str, Any]:
        """
        获取压缩统计信息
        
        Args:
            original_length: 原始文本长度
            level: 压缩层级
            
        Returns:
            压缩统计信息
        """
        base_target = int(original_length * self.config["compression_ratio"])
        adjusted_target = int(base_target * (0.8 ** level))
        
        return {
            "original_length": original_length,
            "base_target_length": base_target,
            "adjusted_target_length": adjusted_target,
            "compression_ratio": self.config["compression_ratio"],
            "level_adjustment": 0.8 ** level,
            "expected_ratio": adjusted_target / original_length
        }