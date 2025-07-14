"""
CogletNet 默认配置文件
"""

DEFAULT_CONFIG = {
    # 存储配置
    "storage_config": {
        "upstash_url": "",  # 必须由用户提供
        "upstash_token": "",  # 必须由用户提供
        "set_id": None  # 可选，不提供则自动生成
    },
    
    # LLM配置
    "llm_config": {
        "model": "gpt-4o-mini",  # 默认使用 gpt-4o-mini
        "max_retries": 3,
        "temperature": 0.7
    },
    
    # 记忆机制配置
    "memory_config": {
        "beta": 0.85,  # 时间衰减系数
        "gamma": 0.3,  # 访问增强系数
        "b": 0.05,  # 基础衰减率
        "initial_weight": 0.5,  # 初始权重
        "golden_ratio": 0.618,  # 黄金分割比例
        "top_k": 10  # 返回结果数量
    },
    
    # 思考过程配置
    "thinking_config": {
        "max_cycles": 5  # 最大思考循环次数
    },
    
    # 提示词配置
    "prompts_config": {
        "role": "你是一个专业的认知分析系统，擅长从输入内容中提取关键信息并生成结构化的思考。你必须严格按照指定的JSON格式返回结果。",
        "format": (
            "你必须严格按照以下JSON格式返回结果：\n"
            "{\n"
            '  "next_thought": "下一轮思考内容",\n'
            '  "activated_cog_ids": ["实际使用到的认元序号"],\n'
            '  "log": "思考日志",\n'
            '  "generated_cog_texts": ["生成的认元文本列表"],\n'
            '  "function_calls": [{"name": "函数名", "args": {"参数名": "参数值"}}]\n'
            "}"
        ),
        "thinking": (
            "在思考过程中，请注意以下几点：\n"
            "1. 认元应当是基于输入内容的抽象性观点与模式总结\n"
            "2. 生成的认元文本应当简洁、清晰、具有普遍性\n"
            "3. 思考日志应当记录重要的推理过程和决策依据\n"
            "4. 函数调用应当明确具体，包含必要的参数\n"
            "5. 在activated_cog_ids中列出实际用于生成回答的认元ID\n"
            "6. 必须严格按照指定的JSON格式返回结果"
        ),
        "example": (
            """示例输入：'人工智能正在改变我们的生活方式'
示例输出：
{
  "next_thought": "这种改变主要体现在哪些具体方面？",
  "activated_cog_ids": [1, 2],
  "log": "识别到技术变革主题，需要进一步探讨具体影响",
  "generated_cog_texts": ["技术变革往往从日常生活开始", "AI的影响具有普遍性和深远性"],
  "function_calls": []
}
"""
        )
    }
}

def merge_config(user_config: dict) -> dict:
    """
    合并用户配置和默认配置
    
    Args:
        user_config: 用户提供的配置
        
    Returns:
        dict: 合并后的配置
    """
    merged = DEFAULT_CONFIG.copy()
    
    for section, values in user_config.items():
        if section in merged:
            if isinstance(merged[section], dict) and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
                
    return merged 