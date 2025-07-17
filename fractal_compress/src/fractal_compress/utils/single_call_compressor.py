"""
单次 LLM 调用的文本分割和压缩工具

通过一次 LLM API 调用，使用 function calling 完成：
1. 按黄金比例分割文本 (0.382/0.618)  
2. 压缩前半部分到原长度的 0.618 倍
3. 返回压缩文本和原始前半部分
"""

import os
import time
import json
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass

try:
    import litellm
except ImportError:
    print("Warning: litellm not installed. Please install with: pip install litellm")
    litellm = None


@dataclass
class SingleCallResult:
    """单次调用压缩结果"""
    compressed_text: str
    original_part_a: str
    model_used: str
    processing_time: float
    function_call_success: bool
    raw_response: str = ""


class SingleCallCompressor:
    """
    单次 LLM 调用压缩器
    
    在一次 API 调用中完成文本分割和压缩，使用 function calling 返回结果
    """
    
    def __init__(self, default_model: str = "gpt-3.5-turbo"):
        """
        初始化压缩器
        
        Args:
            default_model: 默认模型名称
        """
        if litellm is None:
            raise ImportError("litellm is required. Install with: pip install litellm")
        
        self.default_model = default_model
        self.function_schema = self._create_function_schema()
        self.system_prompts = self._create_system_prompts()
    
    def _create_function_schema(self) -> Dict[str, Any]:
        """创建 function calling 的 schema 定义"""
        return {
            "name": "return_compressed_text",
            "description": "返回按黄金比例分割并压缩后的文本结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "compressed": {
                        "type": "string",
                        "description": "压缩后的文本 (前0.382部分压缩到原长度的0.618倍)"
                    },
                    "original": {
                        "type": "string", 
                        "description": "原始的前0.382部分文本"
                    }
                },
                "required": ["compressed", "original"]
            }
        }
    
    def _create_system_prompts(self) -> Dict[str, str]:
        """创建系统提示词模板"""
        return {
            "chinese": """你是一个严格的文本处理机器人。你必须完全按照数学计算执行任务，不得有任何偏差。

🎯 **强制任务**：
1. 将文本按字符数精确分割为 38.2% : 61.8%
2. 压缩前38.2%部分到其长度的61.8%

📐 **强制执行步骤**：

**步骤1**: 计算分割点
- 总长度 = 字符数
- 分割点 = 总长度 × 0.382（四舍五入到整数）
- 在分割点±3字符内找句子边界，无边界则强制在分割点切断

**步骤2**: 强制分割
- A部分 = 文本[0:分割点]
- A部分长度必须接近总长度×0.382
- 如果A部分=原文，则任务失败

**步骤3**: 强制压缩A部分
- 目标长度 = A部分长度 × 0.618（四舍五入）
- 删除修饰词、连接词、重复内容
- 保留主要动词、名词、核心信息
- 压缩文本长度必须接近目标长度

**步骤4**: 验证并返回
- 验证：A部分长度 ≈ 原文×0.382
- 验证：压缩长度 ≈ A部分×0.618
- 如果不符合，重新计算

🚨 **绝对禁止**：
- A部分等于原文
- 压缩文本比A部分长
- 忽略数学计算要求
- 主观判断分割点

🔧 **强制要求**：
- A部分字符数 = 原文字符数 × 0.382 (±5%)
- 压缩字符数 = A部分字符数 × 0.618 (±10%)
- 必须使用return_compressed_text函数返回结果""",

            "english": """You are a professional text processing assistant. Please strictly follow these steps:

🔢 **Step 1: Calculate Split Point**
- Calculate total text length
- Split position = total length × 0.382
- Find nearest sentence boundary (period, question mark, exclamation, line break)

📚 **Step 2: Split Text**
- Part A: Content from start to split point (approximately 38.2%)
- Part B: Remaining content (don't return, only for validation)

🗜️ **Step 3: Compress Part A**
- Compress part A to 61.8% of its original length
- Target length = Part A length × 0.618
- Preserve core information, remove redundancy
- Ensure semantic integrity and logical clarity

📤 **Step 4: Return Results**
Use return_compressed_text function:
- compressed: compressed part A (about 61.8% of A's length)
- original: original part A (about 38.2% of total text)

⚠️ **Important**:
- Must actually split text, part A cannot equal original text
- Split ratio must be close to 38.2% : 61.8%
- Compressed text must be significantly shorter than original part A""",

            "mixed": """你是专业的文本处理助手。严格执行以下步骤：

🎯 **核心任务**：
1. 按黄金比例 38.2% : 61.8% 分割文本
2. 压缩前38.2%部分到其长度的61.8%

📐 **精确步骤**：
1. 计算分割点：文本长度 × 0.382
2. 在分割点附近找句子边界
3. 提取A部分（约38.2%原文）
4. 压缩A部分到原A长度的61.8%

📊 **验证标准**：
- A部分长度 ≈ 原文长度 × 0.382
- 压缩文本长度 ≈ A部分长度 × 0.618
- 最终压缩文本 ≈ 原文长度 × 0.236

使用 return_compressed_text 返回：
- compressed: 压缩文本
- original: 原始A部分

务必确保分割和压缩都正确执行！"""
        }
    
    def compress(
        self,
        text: str,
        model: str = None,
        language: str = "mixed",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> SingleCallResult:
        """
        执行单次调用压缩
        
        Args:
            text: 输入文本
            model: 模型名称
            language: 语言类型 ("chinese", "english", "mixed")
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            SingleCallResult: 压缩结果
        """
        start_time = time.time()
        model = model or self.default_model
        
        if language not in self.system_prompts:
            raise ValueError(f"Unsupported language: {language}")
        
        # 计算预期的分割和压缩长度
        text_length = len(text)
        expected_a_length = int(text_length * 0.382)
        expected_compressed_length = int(expected_a_length * 0.618)
        
        # 构造消息
        messages = [
            {
                "role": "system",
                "content": self.system_prompts[language]
            },
            {
                "role": "user", 
                "content": f"""🔥 **强制数学任务**

📊 **精确计算**：
- 原文总长度: {text_length} 字符
- 分割点位置: {int(text_length * 0.382)} 字符处
- A部分必须长度: {expected_a_length} 字符 (误差范围: ±{max(1, int(expected_a_length * 0.05))})
- 压缩后必须长度: {expected_compressed_length} 字符 (误差范围: ±{max(1, int(expected_compressed_length * 0.1))})

📝 **原文内容**：
{text}

🎯 **执行指令**：
1. 在第{int(text_length * 0.382)}个字符附近分割文本
2. A部分长度必须在{expected_a_length-max(1, int(expected_a_length * 0.05))}到{expected_a_length+max(1, int(expected_a_length * 0.05))}字符之间
3. 压缩文本长度必须在{expected_compressed_length-max(1, int(expected_compressed_length * 0.1))}到{expected_compressed_length+max(1, int(expected_compressed_length * 0.1))}字符之间

⚠️ **如果不符合数学要求，任务失败！**"""
            }
        ]
        
        # 构造 function calling 参数
        tools = [
            {
                "type": "function",
                "function": self.function_schema
            }
        ]
        
        try:
            # 调用 LLM
            response = litellm.completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "return_compressed_text"}},
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            # 解析 function call 结果
            if (response.choices[0].message.tool_calls and 
                len(response.choices[0].message.tool_calls) > 0):
                
                tool_call = response.choices[0].message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                
                return SingleCallResult(
                    compressed_text=function_args.get("compressed", ""),
                    original_part_a=function_args.get("original", ""),
                    model_used=model,
                    processing_time=processing_time,
                    function_call_success=True,
                    raw_response=str(response.choices[0].message.content or "")
                )
            else:
                # 备用：从普通响应中提取
                content = response.choices[0].message.content or ""
                return SingleCallResult(
                    compressed_text="",
                    original_part_a="",
                    model_used=model,
                    processing_time=processing_time,
                    function_call_success=False,
                    raw_response=content
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            raise RuntimeError(f"LLM compression failed: {str(e)}")
    
    def compress_with_callback(
        self,
        text: str,
        callback: callable = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        使用回调函数的压缩方法
        
        Args:
            text: 输入文本
            callback: 回调函数，接收 (compressed, original) 参数
            **kwargs: 传递给 compress 的其他参数
            
        Returns:
            Tuple[str, str]: (compressed_text, original_part_a)
        """
        result = self.compress(text, **kwargs)
        
        if callback:
            callback(result.compressed_text, result.original_part_a)
        
        return result.compressed_text, result.original_part_a


class ModelComparison:
    """模型性能对比工具"""
    
    def __init__(self, compressor: SingleCallCompressor = None):
        self.compressor = compressor or SingleCallCompressor()
        self.results: List[Dict[str, Any]] = []
    
    def compare_models(
        self,
        text: str,
        models: List[str],
        languages: List[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        对比多个模型的压缩效果
        
        Args:
            text: 测试文本
            models: 模型列表
            languages: 语言设置列表
            **kwargs: 其他参数
            
        Returns:
            对比结果列表
        """
        if languages is None:
            languages = ["mixed"]
        
        results = []
        
        for model in models:
            for language in languages:
                try:
                    result = self.compressor.compress(
                        text=text,
                        model=model,
                        language=language,
                        **kwargs
                    )
                    
                    # 计算指标
                    original_len = len(result.original_part_a)
                    compressed_len = len(result.compressed_text)
                    compression_ratio = compressed_len / original_len if original_len > 0 else 0
                    
                    results.append({
                        "model": model,
                        "language": language,
                        "success": result.function_call_success,
                        "compression_ratio": compression_ratio,
                        "processing_time": result.processing_time,
                        "original_length": original_len,
                        "compressed_length": compressed_len,
                        "compressed_preview": result.compressed_text[:100] + "..." if len(result.compressed_text) > 100 else result.compressed_text,
                        "original_preview": result.original_part_a[:100] + "..." if len(result.original_part_a) > 100 else result.original_part_a
                    })
                    
                except Exception as e:
                    results.append({
                        "model": model,
                        "language": language,
                        "success": False,
                        "error": str(e),
                        "compression_ratio": 0,
                        "processing_time": 0
                    })
        
        self.results = results
        return results
    
    def get_best_model(self, metric: str = "compression_ratio") -> Dict[str, Any]:
        """获取最佳模型"""
        if not self.results:
            raise ValueError("No comparison results available")
        
        successful_results = [r for r in self.results if r.get("success", False)]
        
        if not successful_results:
            raise ValueError("No successful results to compare")
        
        if metric == "processing_time":
            return min(successful_results, key=lambda x: x[metric])
        else:
            return max(successful_results, key=lambda x: x[metric])
    
    def export_results(self, filename: str):
        """导出结果到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)


# 便捷函数
def quick_compress(
    text: str,
    model: str = "gpt-3.5-turbo",
    language: str = "mixed"
) -> Tuple[str, str]:
    """
    快速压缩函数
    
    Args:
        text: 输入文本
        model: 模型名称
        language: 语言类型
        
    Returns:
        Tuple[str, str]: (compressed_text, original_part_a)
    """
    compressor = SingleCallCompressor(default_model=model)
    return compressor.compress_with_callback(text, language=language)


def compare_models_quick(
    text: str,
    models: List[str] = None
) -> List[Dict[str, Any]]:
    """
    快速模型对比
    
    Args:
        text: 测试文本
        models: 模型列表
        
    Returns:
        对比结果
    """
    if models is None:
        models = ["gpt-3.5-turbo", "gpt-4"]
    
    compressor = SingleCallCompressor()
    comparison = ModelComparison(compressor)
    return comparison.compare_models(text, models)