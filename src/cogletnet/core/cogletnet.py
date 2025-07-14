"""
认知网络主要实现
"""

import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import time
from litellm import completion_with_retries
from .vector_store import VectorStore
from .coglets import Coglets
from .mam import MAM
from ..utils.id_generator import vector_id
from ..utils.llm_checker import check_llm_response
from ..utils.logging import setup_logger
from ..config.default_config import DEFAULT_CONFIG, merge_config

logger = setup_logger("CogletNet")

class CogletNet:
    """认知网络实现"""
    
    def __init__(
        self,
        # 基础存储配置
        storage_config: Dict[str, str] = {
            "upstash_url": "",              # Upstash 服务地址
            "upstash_token": "",            # Upstash 访问令牌
            "set_id": None                  # 认知集合ID，不提供则自动生成
        },
        
        # LLM配置
        llm_config: Dict[str, Any] = {
            "model": "gpt-4o-mini",             # LLM模型名称
            "max_retries": 3,               # LLM调用最大重试次数
            "temperature": 0.7              # LLM温度参数
        },
        
        # 记忆机制配置
        memory_config: Dict[str, Any] = {
            "beta": 0.85,                   # 时间衰减系数
            "gamma": 0.3,                   # 访问增强系数
            "b": 0.05,                      # 基础衰减率
            "initial_weight": 0.5,          # 初始权重
            "golden_ratio": 0.618,          # 黄金分割比例
            "top_k": 10                     # 返回结果数量
        },
        
        # 思考过程配置
        thinking_config: Dict[str, Any] = {
            "max_cycles": 5,                # 最大思考循环次数
        },
        
        # 提示词配置
        prompts_config: Dict[str, Optional[str]] = {
            "role": None,                   # 角色定义
            "format": None,                 # 输出格式定义
            "thinking": None,               # 思考指导
            "example": None                 # 示例说明
        }
    ):
        """
        初始化认知网络
        
        Args:
            storage_config: 存储配置
            llm_config: LLM配置
            memory_config: 记忆机制配置
            thinking_config: 思考过程配置
            prompts_config: 提示词配置
        """
        # 1. 验证必要的配置
        if not storage_config["upstash_url"]:
            raise ValueError("未提供 upstash_url")
        if not storage_config["upstash_token"]:
            raise ValueError("未提供 upstash_token")
            
        # 2. 初始化向量存储
        self.vector_store = VectorStore(
            storage_config["upstash_url"],
            storage_config["upstash_token"]
        )
        
        # 3. 初始化认元管理器
        self.coglets = Coglets(
            self.vector_store,
            beta=memory_config["beta"],
            gamma=memory_config["gamma"],
            b=memory_config["b"],
            initial_weight=memory_config["initial_weight"],
            golden_ratio=memory_config["golden_ratio"],
            top_k=memory_config["top_k"]
        )
        
        # 4. 设置LLM参数
        self.model = llm_config["model"]
        self.max_retries = llm_config["max_retries"]
        self.temperature = llm_config["temperature"]
        
        # 5. 设置思考参数
        self.max_think_cycles = thinking_config["max_cycles"]
        
        # 6. 设置认知集合ID
        self.set_id = storage_config["set_id"] or f"coglet_{vector_id()[:8]}"
        self.coglets.create_set(self.set_id, f"认知集合 {self.set_id}")
        
        # 7. 设置提示词
        self.role_prompt = prompts_config["role"]
        self.format_prompt = prompts_config["format"]
        self.thinking_prompt = prompts_config["thinking"]
        self.example_prompt = prompts_config["example"]
        
    def _format_llm_prompt(self, query: str, activated: List[Dict[str, Any]]) -> str:
        """格式化提示词"""
        prompt = f"基于以下认知进行思考并回答：{query}\n\n"
        prompt += "相关认知：\n"
        
        for i, cog in enumerate(activated, 1):
            prompt += f"ID={i}. {cog['content']}\n"
        
        prompt += "\n请基于以上认知进行深入思考并给出见解。在activated_cog_ids中请使用原始的认元序号。\n\n"
        prompt += "请以JSON格式返回结果，格式如下：\n"
        prompt += """{
  "next_thought": "下一轮思考内容",
  "activated_cog_ids": ["实际使用到的认元序号"],
  "log": "思考日志",
  "generated_cog_texts": ["生成的认元文本列表"],
  "function_calls": [{"name": "函数名", "args": {"参数名": "参数值"}}]
}"""
        
        return prompt
        
    def _get_system_prompt(self) -> str:
        """
        获取完整的系统提示词
        
        Returns:
            str: 完整的系统提示词
        """
        return f"{self.role_prompt}\n\n{self.format_prompt}\n\n{self.thinking_prompt}\n\n{self.example_prompt}"
        
    def think(self, input_text: str, set_id: str, round_idx: int = 1) -> Dict[str, Any]:
        """单次思考，返回详细过程"""
        logger.info(f"Start think: input={input_text}, set={set_id}")
        
        # 1. 召回相关认元
        recall_result = self.coglets.recall(set_id, input_text)
        logger.debug(f"Recall result: {recall_result}")
        
        # 2. 获取激活的认元
        activated = recall_result.get("activated", [])
        logger.info(f"Activated count={len(activated)}")
        
        # 3. 格式化提示词
        activated_content = [cog["content"] for cog in activated]
        logger.debug(f"Activated content={activated_content}")
        
        prompt = self._format_llm_prompt(input_text, activated)
        logger.debug(f"Prompt: {prompt}")
        
        # 4. 调用LLM
        try:
            response = completion_with_retries(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_retries=self.max_retries,
                response_format={"type": "json_object"}
            )
            logger.info("LLM call success")
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return {
                "input": input_text,
                "activated": activated_content,
                "prompt": prompt,
                "output": {
                    "next_thought": "",
                    "activated_cog_ids": [],
                    "log": "LLM调用失败",
                    "generated_cog_texts": [],
                    "function_calls": []
                },
                "round": round_idx
            }
        
        # 5. 解析响应
        try:
            result = json.loads(response.choices[0].message.content)
            logger.debug(f"Parsed response: {result}")
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return {
                "input": input_text,
                "activated": activated_content,
                "prompt": prompt,
                "output": {
                "next_thought": "",
                "activated_cog_ids": [],
                    "log": "LLM调用失败",
                "generated_cog_texts": [],
                "function_calls": []
                },
                "round": round_idx
            }
        
        return {
            "input": input_text,
            "activated": activated_content,
            "prompt": prompt,
            "output": result,
            "round": round_idx
        }

    def think_loop(self, input_text: str, set_id: str) -> List[Dict[str, Any]]:
        """思考循环，返回详细过程"""
        results = []
        for idx in range(self.max_think_cycles):
            round_idx = idx + 1
            result = self.think(input_text, set_id, round_idx=round_idx)
            results.append(result)
            if not result["output"].get("next_thought"):
                break
            input_text = result["output"]["next_thought"]
        return results

    def call_function(self, func_call: Dict[str, Any]) -> bool:
        """执行函数调用"""
        logger.info(f"Call function: {func_call}")
        
        func_name = func_call.get("name", "").lower()
        if not func_name:
            logger.warning("函数名称为空")
            return False
            
        if func_name == "x_reply":
            logger.info("执行x_reply函数")
            return True
        else:
            logger.warning(f"未知函数: {func_name}")
            return False

    def _call_llm(self, prompt: str) -> str:
        """
        调用 LLM 生成响应
        
        Args:
            prompt: 输入提示
            
        Returns:
            str: LLM 响应
        """
        # 这里使用 litellm 调用 LLM
        try:
            response = completion_with_retries(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_retries=self.max_retries,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # 确保返回JSON格式
            )
            content = response.choices[0].message.content
            # 确保返回的是有效的JSON字符串
            json.loads(content)  # 验证JSON格式
            return content
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return '{"next_thought": "", "activated_cog_ids": [], "log": "LLM call failed", "generated_cog_texts": [], "function_calls": []}'

if __name__ == "__main__":
    # 使用示例
    import os
    
    # 自定义提示词
    custom_role_prompt = "你是一个专注于技术分析的认知系统，擅长从技术角度分析问题。你必须严格按照指定的JSON格式返回结果。"
    custom_format_prompt = (
        "你必须严格按照以下JSON格式返回结果：\n"
        "{\n"
        '  "next_thought": "下一轮思考内容",\n'
        '  "activated_cog_ids": ["实际使用到的认元ID列表"],\n'
        '  "log": "思考日志",\n'
        '  "generated_cog_texts": ["生成的认元文本列表"],\n'
        '  "function_calls": [{"name": "函数名", "args": {"参数名": "参数值"}}]\n'
        "}"
    )
    custom_thinking_prompt = (
        "在思考过程中，请注意以下几点：\n"
        "1. 关注技术实现细节和架构设计\n"
        "2. 分析技术选型的优缺点\n"
        "3. 考虑性能和可扩展性\n"
        "4. 记录技术决策依据\n"
        "5. 在activated_cog_ids中列出实际用于生成回答的认元ID\n"
        "6. 必须严格按照指定的JSON格式返回结果"
    )
    custom_example_prompt = (
        """示例输入：'微服务架构的优势是什么？'
示例输出：
{
  "next_thought": "这些优势在什么场景下最明显？",
  "activated_cog_ids": ["tech_001", "tech_002"],
  "log": "识别到架构设计主题，需要进一步探讨应用场景",
  "generated_cog_texts": ["微服务架构支持独立部署和扩展", "服务解耦提高了系统灵活性"],
  "function_calls": []
}
"""
    )
    
    # 初始化认知网络
    net = CogletNet(
        storage_config={
            "upstash_url": os.getenv("UPSTASH_URL"),
            "upstash_token": os.getenv("UPSTASH_TOKEN"),
            "set_id": "test_set"  # 可选，不提供则自动生成
        },
        llm_config={
            "model": "4o-mini",  # 使用 4o-mini 模型
            "max_retries": 3,
            "temperature": 0.7
        },
        memory_config={
            "beta": 0.85,
            "gamma": 0.3,
            "b": 0.05,
            "initial_weight": 0.5,
            "golden_ratio": 0.618,
            "top_k": 10
        },
        thinking_config={
            "max_cycles": 5,
        },
        prompts_config={
            "role": custom_role_prompt,
            "format": custom_format_prompt,
            "thinking": custom_thinking_prompt,
            "example": custom_example_prompt
        }
    )
    
    # 执行认知循环
    result = net.think_loop("What is cognitive network?", "test_set")
    
    logger.info(json.dumps(result, ensure_ascii=False, indent=2)) 