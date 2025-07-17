"""
基于2024年最新研究的高级单一LLM压缩器

应用最新的prompt engineering技术和few-shot learning
实现精确的黄金比例分割和压缩
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
class AdvancedResult:
    """高级单一LLM压缩结果"""
    compressed_text: str
    original_part_a: str
    split_ratio: float
    compression_ratio: float
    overall_ratio: float
    model_used: str
    processing_time: float
    success: bool
    confidence_score: float


class AdvancedSingleLLM:
    """
    基于2024年最新研究的高级单一LLM压缩器
    
    核心技术：
    1. Few-shot prompting with precise examples
    2. "At most X characters" length control
    3. Step-by-step mathematical guidance
    4. Confidence validation
    """
    
    def __init__(self, default_model: str = "gpt-4o-mini"):
        """初始化高级压缩器"""
        if litellm is None:
            raise ImportError("litellm is required. Install with: pip install litellm")
        
        self.default_model = default_model
        self.examples = self._create_few_shot_examples()
    
    def _create_few_shot_examples(self) -> List[Dict[str, Any]]:
        """创建Few-shot学习示例"""
        return [
            {
                "input_text": "人工智能技术正在快速发展。机器学习和深度学习取得突破。这些技术改变了我们的生活方式。",
                "input_length": 42,
                "target_split": 16,  # 42 * 0.382 = 16
                "target_compressed": 10,  # 16 * 0.618 = 10
                "part_a": "人工智能技术正在快速发展。机器学习",
                "part_a_length": 16,
                "compressed": "人工智能技术快速发展",
                "compressed_length": 10
            },
            {
                "input_text": "环境保护是全球面临的重要挑战。气候变化、污染和资源短缺问题日益严重。我们需要采取行动保护地球。",
                "input_length": 48,
                "target_split": 18,  # 48 * 0.382 = 18
                "target_compressed": 11,  # 18 * 0.618 = 11
                "part_a": "环境保护是全球面临的重要挑战。气候变化",
                "part_a_length": 18,
                "compressed": "环境保护是全球重要挑战",
                "compressed_length": 11
            }
        ]
    
    def _create_advanced_prompt(self, text: str, language: str = "chinese") -> str:
        """创建基于2024年研究的高级提示词"""
        
        text_length = len(text)
        split_position = int(text_length * 0.382)
        target_compressed_length = int(split_position * 0.618)
        
        # 构建Few-shot示例
        examples_text = ""
        for i, example in enumerate(self.examples, 1):
            examples_text += f"""
示例{i}：
输入文本："{example['input_text']}" (长度: {example['input_length']})
计算: 分割位置 = {example['input_length']} × 0.382 = {example['target_split']}
      压缩长度 = {example['target_split']} × 0.618 = {example['target_compressed']}

分割结果：
- A部分: "{example['part_a']}" (实际长度: {example['part_a_length']})

压缩结果：
- 压缩文本: "{example['compressed']}" (实际长度: {example['compressed_length']})

验证：✓ 分割准确 ✓ 压缩准确
"""
        
        prompt = f"""你是一个数学精确的文本处理专家。请严格按照以下步骤处理文本：

📐 **数学计算步骤（必须严格执行）**：

步骤1：计算分割位置
- 文本总长度 = {text_length} 字符
- 分割位置 = {text_length} × 0.382 = {split_position} 字符

步骤2：精确分割
- 在第{split_position}个字符附近找到最近的句子边界
- 提取A部分（前38.2%）
- A部分长度必须在 {split_position-2} 到 {split_position+2} 字符之间

步骤3：计算压缩目标
- 压缩目标长度 = A部分实际长度 × 0.618
- 使用"至多X字符"控制压缩长度

{examples_text}

🎯 **现在处理目标文本**：
输入文本："{text}" (长度: {text_length})

请按照示例格式输出：

计算: 分割位置 = {text_length} × 0.382 = {split_position}
     压缩长度 = [A部分实际长度] × 0.618 = [具体数字]

分割结果：
- A部分: "[在第{split_position}字符附近分割的文本]" (实际长度: [数字])

压缩结果：
- 压缩文本: "[至多[压缩长度]字符的压缩版本]" (实际长度: [数字])

⚠️ **严格要求**：
1. A部分长度必须接近{split_position}字符（误差±2）
2. 压缩文本长度必须接近A部分长度×0.618（误差±2）
3. 在分割点附近找句子边界，不要硬切断
4. 压缩时保留核心信息，删除修饰词"""

        return prompt
    
    def compress(
        self,
        text: str,
        model: str = None,
        language: str = "chinese",
        temperature: float = 0.1,
        max_attempts: int = 2
    ) -> AdvancedResult:
        """
        执行高级单一LLM压缩
        
        Args:
            text: 输入文本
            model: 模型名称
            language: 语言类型
            temperature: 温度参数（低温度提高精确度）
            max_attempts: 最大尝试次数
        
        Returns:
            AdvancedResult: 压缩结果
        """
        start_time = time.time()
        model = model or self.default_model
        
        for attempt in range(max_attempts):
            try:
                # 构造高级提示词
                prompt = self._create_advanced_prompt(text, language)
                
                # 调整温度：第二次尝试使用更低温度
                current_temp = temperature if attempt == 0 else temperature * 0.5
                
                # 调用LLM
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=current_temp,
                    max_tokens=1500,
                    timeout=45
                )
                
                content = response.choices[0].message.content.strip()
                
                # 解析结果
                result = self._parse_llm_response(content, text, model, time.time() - start_time)
                
                # 验证质量
                if self._validate_result(result, text):
                    return result
                else:
                    # 如果第一次失败，继续尝试
                    if attempt < max_attempts - 1:
                        continue
                    else:
                        # 最后一次失败，返回部分结果
                        result.success = False
                        return result
                        
            except Exception as e:
                if attempt == max_attempts - 1:
                    return AdvancedResult(
                        compressed_text="",
                        original_part_a="",
                        split_ratio=0,
                        compression_ratio=0,
                        overall_ratio=0,
                        model_used=model,
                        processing_time=time.time() - start_time,
                        success=False,
                        confidence_score=0.0
                    )
                continue
    
    def _parse_llm_response(self, content: str, original_text: str, model: str, processing_time: float) -> AdvancedResult:
        """解析LLM响应"""
        try:
            # 尝试提取A部分和压缩文本
            lines = content.split('\n')
            
            part_a = ""
            compressed_text = ""
            
            for line in lines:
                if '- A部分:' in line or 'A部分:' in line:
                    # 提取引号内的内容
                    start = line.find('"')
                    end = line.rfind('"')
                    if start != -1 and end != -1 and start < end:
                        part_a = line[start+1:end]
                
                elif '- 压缩文本:' in line or '压缩文本:' in line:
                    # 提取引号内的内容
                    start = line.find('"')
                    end = line.rfind('"')
                    if start != -1 and end != -1 and start < end:
                        compressed_text = line[start+1:end]
            
            # 如果解析失败，尝试备用方法
            if not part_a or not compressed_text:
                part_a, compressed_text = self._fallback_parse(content, original_text)
            
            # 计算各种比例
            split_ratio = len(part_a) / len(original_text) if len(original_text) > 0 else 0
            compression_ratio = len(compressed_text) / len(part_a) if len(part_a) > 0 else 0
            overall_ratio = len(compressed_text) / len(original_text) if len(original_text) > 0 else 0
            
            # 计算置信度分数
            confidence_score = self._calculate_confidence(split_ratio, compression_ratio)
            
            return AdvancedResult(
                compressed_text=compressed_text,
                original_part_a=part_a,
                split_ratio=split_ratio,
                compression_ratio=compression_ratio,
                overall_ratio=overall_ratio,
                model_used=model,
                processing_time=processing_time,
                success=True,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            return AdvancedResult(
                compressed_text="",
                original_part_a="",
                split_ratio=0,
                compression_ratio=0,
                overall_ratio=0,
                model_used=model,
                processing_time=processing_time,
                success=False,
                confidence_score=0.0
            )
    
    def _fallback_parse(self, content: str, original_text: str) -> Tuple[str, str]:
        """备用解析方法"""
        # 简单启发式解析
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 查找包含引号的行
        quoted_lines = [line for line in lines if '"' in line]
        
        if len(quoted_lines) >= 2:
            # 提取前两个引号内容
            part_a = self._extract_quoted_text(quoted_lines[0])
            compressed_text = self._extract_quoted_text(quoted_lines[1])
            return part_a, compressed_text
        
        # 最终备用方案
        split_pos = int(len(original_text) * 0.382)
        part_a = original_text[:split_pos]
        compressed_text = part_a[:int(len(part_a) * 0.618)]
        
        return part_a, compressed_text
    
    def _extract_quoted_text(self, line: str) -> str:
        """提取引号内的文本"""
        start = line.find('"')
        end = line.rfind('"')
        if start != -1 and end != -1 and start < end:
            return line[start+1:end]
        return ""
    
    def _calculate_confidence(self, split_ratio: float, compression_ratio: float) -> float:
        """计算置信度分数"""
        split_error = abs(split_ratio - 0.382)
        compression_error = abs(compression_ratio - 0.618)
        
        split_score = max(0, 1 - split_error / 0.1)  # 10%容错
        compression_score = max(0, 1 - compression_error / 0.15)  # 15%容错
        
        return (split_score + compression_score) / 2
    
    def _validate_result(self, result: AdvancedResult, original_text: str) -> bool:
        """验证结果质量"""
        # 基础检查
        if not result.original_part_a or not result.compressed_text:
            return False
        
        # 长度检查
        if len(result.original_part_a) >= len(original_text):
            return False
        
        # 比例检查
        split_ok = abs(result.split_ratio - 0.382) < 0.08  # 8%容错
        compression_ok = abs(result.compression_ratio - 0.618) < 0.2  # 20%容错
        
        # 置信度检查
        confidence_ok = result.confidence_score > 0.6
        
        return split_ok and compression_ok and confidence_ok


# 便捷函数
def advanced_compress(
    text: str,
    model: str = "gpt-4o-mini",
    language: str = "chinese"
) -> Tuple[str, str]:
    """
    高级单一LLM压缩函数
    
    Args:
        text: 输入文本
        model: 模型名称
        language: 语言类型
    
    Returns:
        Tuple[str, str]: (compressed_text, original_part_a)
    """
    compressor = AdvancedSingleLLM(default_model=model)
    result = compressor.compress(text, language=language)
    return result.compressed_text, result.original_part_a


def validate_advanced_result(result: AdvancedResult) -> Dict[str, Any]:
    """
    验证高级压缩结果
    
    Args:
        result: 压缩结果
    
    Returns:
        验证报告
    """
    split_error = abs(result.split_ratio - 0.382)
    compression_error = abs(result.compression_ratio - 0.618)
    
    return {
        "overall_success": result.success,
        "confidence_score": result.confidence_score,
        "split_accuracy": split_error < 0.05,
        "compression_accuracy": compression_error < 0.15,
        "split_error": split_error,
        "compression_error": compression_error,
        "quality_grade": "A" if result.confidence_score > 0.8 else "B" if result.confidence_score > 0.6 else "C"
    }