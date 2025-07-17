"""
增强混合压缩器 - 结合代码分割和高级LLM压缩技术

借鉴AdvancedSingleLLM的Few-shot prompting和数学指导
确保严格的长度约束，压缩文本不超过目标长度
"""

import os
import time
import json
from typing import Dict, Any, Tuple, List, Optional, Callable
from dataclasses import dataclass
from .text_splitter import smart_split

try:
    import litellm
except ImportError:
    print("Warning: litellm not installed. Please install with: pip install litellm")
    litellm = None


@dataclass
class EnhancedHybridResult:
    """增强混合压缩结果"""
    compressed_text: str
    original_part_a: str
    original_part_b: str
    split_ratio: float
    compression_ratio: float
    overall_ratio: float
    model_used: str
    processing_time: float
    success: bool
    confidence_score: float
    target_a_length: int
    target_compressed_length: int
    actual_a_length: int
    actual_compressed_length: int
    length_constraint_satisfied: bool
    compression_attempts: int


class EnhancedHybridCompressor:
    """
    增强混合压缩器
    
    结合了以下技术：
    1. 代码精确分割（从HybridCompressor）
    2. Few-shot prompting（从AdvancedSingleLLM）
    3. 数学指导和示例（从AdvancedSingleLLM）
    4. 严格长度约束控制
    5. 多步骤验证和重试机制
    """
    
    def __init__(self, default_model: str = "gpt-4o-mini"):
        """初始化增强混合压缩器"""
        if litellm is None:
            raise ImportError("litellm is required. Install with: pip install litellm")
        
        self.default_model = default_model
        self.few_shot_examples = self._create_few_shot_examples()
        self.enhanced_templates = self._create_enhanced_templates()
    
    def _create_few_shot_examples(self) -> List[Dict[str, Any]]:
        """创建Few-shot学习示例（从AdvancedSingleLLM借鉴）"""
        return [
            {
                "original": "人工智能技术正在快速发展，机器学习和深度学习领域取得了重大突破。",
                "original_length": 32,
                "part_a": "人工智能技术正在快速发展，机器学习",
                "part_a_length": 16,
                "target_compressed": 10,  # 16 * 0.618 = 9.888 ≈ 10
                "compressed": "人工智能技术快速发展",
                "compressed_length": 10,
                "explanation": "删除了'正在'、'机器学习'等词，保留核心概念"
            },
            {
                "original": "环境保护是当今社会面临的重要挑战，气候变化和污染问题日益严重。",
                "original_length": 30,
                "part_a": "环境保护是当今社会面临的重要挑战",
                "part_a_length": 15,
                "target_compressed": 9,  # 15 * 0.618 = 9.27 ≈ 9
                "compressed": "环境保护是重要挑战",
                "compressed_length": 9,
                "explanation": "删除了'当今社会面临的'，保留核心信息"
            },
            {
                "original": "The rapid advancement of artificial intelligence is transforming various industries.",
                "original_length": 78,
                "part_a": "The rapid advancement of artificial intelligence",
                "part_a_length": 44,
                "target_compressed": 27,  # 44 * 0.618 = 27.192 ≈ 27
                "compressed": "AI advancement transforms",
                "compressed_length": 21,
                "explanation": "Used abbreviation 'AI' and simplified sentence structure"
            }
        ]
    
    def _create_enhanced_templates(self) -> Dict[str, str]:
        """创建增强的压缩模板"""
        return {
            "few_shot_precise": """你是一个数学精确的文本压缩专家。请严格按照以下示例和规则进行压缩。

📐 **数学规则**：
- 压缩比例：输出文本长度 / 输入文本长度 = 0.618
- 严格长度约束：输出文本长度 ≤ {target_length} 字符
- 优先选择长度刚好等于目标长度的压缩结果

🎯 **Few-shot示例**：

{examples}

💡 **压缩策略**：
1. 删除形容词和副词（"很"、"非常"、"正在"等）
2. 简化复合词（"人工智能"→"AI"、"机器学习"→"ML"）
3. 去除连接词（"并且"、"同时"、"然而"等）
4. 保留核心名词和动词
5. 确保语义完整性

🔧 **当前任务**：
输入文本："{text}"
输入长度：{original_length} 字符
目标长度：{target_length} 字符（压缩比例 0.618）
严格要求：输出长度 ≤ {target_length} 字符

请输出压缩结果（不要添加任何解释）：""",

            "strict_length": """请将以下文本压缩到最多{target_length}个字符。

⚠️ **严格要求**：
- 输出长度必须 ≤ {target_length} 字符
- 不能超过这个长度限制
- 尽可能接近{target_length}字符但不超过

原文（{original_length}字符）：{text}

压缩目标：最多{target_length}字符
输出：""",

            "ultra_short": """极限压缩任务：将文本压缩到{target_length}字符以内。

原文：{text}
限制：≤{target_length}字符
只保留最核心的信息："""
        }
    
    def compress(
        self,
        text: str,
        model: str = None,
        language: str = "chinese",
        split_deviation_threshold: float = 0.05,
        max_compression_attempts: int = 5,
        strict_length_constraint: bool = True
    ) -> EnhancedHybridResult:
        """
        执行增强混合压缩
        
        Args:
            text: 输入文本
            model: 模型名称
            language: 语言类型
            split_deviation_threshold: 分割偏差阈值
            max_compression_attempts: 最大压缩尝试次数
            strict_length_constraint: 是否严格执行长度约束
        
        Returns:
            EnhancedHybridResult: 压缩结果
        """
        start_time = time.time()
        model = model or self.default_model
        
        # 第1步：精确分割（使用现有的smart_split）
        try:
            # 映射语言代码到smart_split接受的格式
            smart_split_language = {
                "zh": "chinese",
                "en": "english", 
                "mixed": "mixed"
            }.get(language, "mixed")
            
            part_a, part_b = smart_split(
                text, 
                ratio=0.382, 
                deviation_threshold=split_deviation_threshold,
                language=smart_split_language
            )
        except Exception as e:
            return self._create_failed_result(model, time.time() - start_time, str(e))
        
        # 计算目标长度
        target_a_length = int(len(text) * 0.382)
        target_compressed_length = int(len(part_a) * 0.618)
        actual_a_length = len(part_a)
        
        # 第2步：增强LLM压缩
        compressed_result = self.compress_text_with_llm(
            part_a, 
            target_compressed_length, 
            model, 
            language,
            max_attempts=max_compression_attempts,
            strict_constraint=strict_length_constraint
        )
        
        compressed_text = compressed_result["text"]
        compression_attempts = compressed_result["attempts"]
        
        # 计算最终结果
        actual_compressed_length = len(compressed_text)
        split_ratio = actual_a_length / len(text)
        compression_ratio = actual_compressed_length / actual_a_length if actual_a_length > 0 else 0
        overall_ratio = actual_compressed_length / len(text)
        processing_time = time.time() - start_time
        
        # 长度约束满足检查
        length_constraint_satisfied = actual_compressed_length <= target_compressed_length
        
        # 计算置信度分数
        confidence_score = self._calculate_confidence(
            split_ratio, compression_ratio, length_constraint_satisfied
        )
        
        # 验证成功条件
        split_ok = abs(split_ratio - 0.382) < 0.05
        compression_ok = abs(compression_ratio - 0.618) < 0.2
        length_ok = length_constraint_satisfied if strict_length_constraint else True
        content_ok = len(compressed_text) > 0
        
        success = split_ok and compression_ok and length_ok and content_ok
        
        return EnhancedHybridResult(
            compressed_text=compressed_text,
            original_part_a=part_a,
            original_part_b=part_b,
            split_ratio=split_ratio,
            compression_ratio=compression_ratio,
            overall_ratio=overall_ratio,
            model_used=model,
            processing_time=processing_time,
            success=success,
            confidence_score=confidence_score,
            target_a_length=target_a_length,
            target_compressed_length=target_compressed_length,
            actual_a_length=actual_a_length,
            actual_compressed_length=actual_compressed_length,
            length_constraint_satisfied=length_constraint_satisfied,
            compression_attempts=compression_attempts
        )
    
    def compress_text_with_llm(
        self, 
        text: str, 
        target_length: int, 
        model: str = "gpt-4o-mini",
        language: str = "mixed",
        max_attempts: int = 5,
        strict_constraint: bool = True,
        custom_templates: Dict[str, str] = None,
        custom_examples: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        独立的LLM文本压缩函数，专门用于prompt优化实验
        
        Args:
            text: 待压缩文本
            target_length: 目标长度
            model: LLM模型名称
            language: 语言类型 ("chinese", "english", "mixed")
            max_attempts: 最大尝试次数
            strict_constraint: 是否严格控制长度
            custom_templates: 自定义prompt模板
            custom_examples: 自定义Few-shot示例
            
        Returns:
            Dict包含压缩结果、尝试次数、使用策略等信息
        """
        # 使用自定义模板或默认模板
        templates = custom_templates if custom_templates else self.enhanced_templates
        examples = custom_examples if custom_examples else self.few_shot_examples
        
        strategies = ["few_shot_precise", "strict_length", "ultra_short"]
        
        for attempt in range(max_attempts):
            # 根据尝试次数选择策略
            if attempt < 2:
                strategy = "few_shot_precise"
                temperature = 0.05  # 极低温度
            elif attempt < 4:
                strategy = "strict_length"
                temperature = 0.1
            else:
                strategy = "ultra_short"
                temperature = 0.15
            
            try:
                # 构造Few-shot示例（支持自定义示例）
                examples_text = self._format_few_shot_examples_custom(language, examples)
                
                # 选择模板
                template = templates.get(strategy, templates["few_shot_precise"])
                
                # 构造prompt
                if strategy == "few_shot_precise":
                    prompt = template.format(
                        examples=examples_text,
                        text=text,
                        original_length=len(text),
                        target_length=target_length
                    )
                else:
                    prompt = template.format(
                        text=text,
                        original_length=len(text),
                        target_length=target_length
                    )
                
                # 调用LLM
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=min(800, target_length * 3),
                    timeout=30
                )
                
                compressed = response.choices[0].message.content.strip()
                
                # 清理输出
                compressed = self._clean_output(compressed)
                
                # 严格长度检查
                if strict_constraint and len(compressed) > target_length:
                    # 如果超长，尝试截断到合适的边界
                    compressed = self._truncate_to_boundary(compressed, target_length)
                
                # 验证结果质量
                if self._validate_compression_quality(compressed, text, target_length):
                    return {
                        "text": compressed,
                        "attempts": attempt + 1,
                        "strategy": strategy,
                        "temperature": temperature,
                        "original_length": len(text),
                        "compressed_length": len(compressed),
                        "compression_ratio": len(compressed) / len(text) if len(text) > 0 else 0,
                        "success": True
                    }
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    # 最后一次尝试失败，返回简单截断
                    fallback = text[:target_length] if len(text) > target_length else text
                    return {
                        "text": fallback,
                        "attempts": attempt + 1,
                        "strategy": "fallback"
                    }
                continue
        
        # 所有尝试都失败
        fallback_text = text[:target_length] if len(text) > target_length else text
        return {
            "text": fallback_text,
            "attempts": max_attempts,
            "strategy": "fallback",
            "temperature": 0.15,
            "original_length": len(text),
            "compressed_length": len(fallback_text),
            "compression_ratio": len(fallback_text) / len(text) if len(text) > 0 else 0,
            "success": False
        }
    
    def _format_few_shot_examples(self, language: str) -> str:
        """格式化Few-shot示例（原始方法）"""
        return self._format_few_shot_examples_custom(language, self.few_shot_examples)
    
    def _format_few_shot_examples_custom(self, language: str, examples: List[Dict]) -> str:
        """格式化Few-shot示例（支持自定义示例）"""
        examples_text = ""
        
        # 根据语言筛选示例
        relevant_examples = []
        for example in examples:
            if language == "chinese" and any('\u4e00' <= c <= '\u9fff' for c in example["original"]):
                relevant_examples.append(example)
            elif language == "english" and not any('\u4e00' <= c <= '\u9fff' for c in example["original"]):
                relevant_examples.append(example)
            elif language == "mixed":
                relevant_examples.append(example)
        
        # 如果没有相关示例，使用所有示例
        if not relevant_examples:
            relevant_examples = examples
        
        for i, example in enumerate(relevant_examples[:2], 1):  # 最多使用2个示例
            examples_text += f"""
示例{i}：
原文："{example['original']}" (长度: {example['original_length']})
A部分："{example['part_a']}" (长度: {example['part_a_length']})
目标长度：{example['target_compressed']} (= {example['part_a_length']} × 0.618)
压缩结果："{example['compressed']}" (长度: {example['compressed_length']})
策略：{example['explanation']}
✓ 长度约束满足：{example['compressed_length']} ≤ {example['target_compressed']}

"""
        
        return examples_text
    
    def _clean_output(self, text: str) -> str:
        """清理LLM输出"""
        # 移除引号
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # 移除可能的前缀
        prefixes = ["压缩结果：", "输出：", "结果：", "答案："]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text.strip()
    
    def _truncate_to_boundary(self, text: str, max_length: int) -> str:
        """截断到合适的边界"""
        if len(text) <= max_length:
            return text
        
        # 尝试在句子边界截断
        boundaries = ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';']
        
        for i in range(max_length - 1, max(0, max_length - 10), -1):
            if i < len(text) and text[i] in boundaries:
                return text[:i + 1]
        
        # 如果找不到合适的边界，在字符边界截断
        return text[:max_length]
    
    def _validate_compression_quality(self, compressed: str, original: str, target_length: int) -> bool:
        """验证压缩质量"""
        # 基础检查
        if not compressed or len(compressed) == 0:
            return False
        
        # 长度检查
        if len(compressed) > target_length:
            return False
        
        # 内容检查（不能和原文完全一样）
        if compressed == original:
            return False
        
        # 合理性检查（不能太短）
        if len(compressed) < target_length * 0.3:
            return False
        
        return True
    
    def _calculate_confidence(self, split_ratio: float, compression_ratio: float, length_ok: bool) -> float:
        """计算置信度分数"""
        # 分割准确性
        split_error = abs(split_ratio - 0.382)
        split_score = max(0, 1 - split_error / 0.1)
        
        # 压缩准确性
        compression_error = abs(compression_ratio - 0.618)
        compression_score = max(0, 1 - compression_error / 0.2)
        
        # 长度约束满足
        length_score = 1.0 if length_ok else 0.5
        
        # 综合分数
        confidence = (split_score * 0.3 + compression_score * 0.4 + length_score * 0.3)
        
        return round(confidence, 3)
    
    def _create_failed_result(self, model: str, processing_time: float, error: str) -> EnhancedHybridResult:
        """创建失败结果"""
        return EnhancedHybridResult(
            compressed_text="",
            original_part_a="",
            original_part_b="",
            split_ratio=0,
            compression_ratio=0,
            overall_ratio=0,
            model_used=model,
            processing_time=processing_time,
            success=False,
            confidence_score=0.0,
            target_a_length=0,
            target_compressed_length=0,
            actual_a_length=0,
            actual_compressed_length=0,
            length_constraint_satisfied=False,
            compression_attempts=0
        )


# 便捷函数
def enhanced_hybrid_compress(
    text: str,
    model: str = "gpt-4o-mini",
    language: str = "chinese",
    strict_length: bool = True
) -> Tuple[str, str]:
    """
    增强混合压缩快速函数
    
    Args:
        text: 输入文本
        model: 模型名称
        language: 语言类型
        strict_length: 是否严格执行长度约束
    
    Returns:
        Tuple[str, str]: (compressed_text, original_part_a)
    """
    compressor = EnhancedHybridCompressor(default_model=model)
    result = compressor.compress(
        text, 
        language=language, 
        strict_length_constraint=strict_length
    )
    return result.compressed_text, result.original_part_a


def validate_enhanced_result(result: EnhancedHybridResult) -> Dict[str, Any]:
    """
    验证增强混合压缩结果
    
    Args:
        result: 压缩结果
    
    Returns:
        验证报告
    """
    split_error = abs(result.split_ratio - 0.382)
    compression_error = abs(result.compression_ratio - 0.618)
    
    # 质量等级
    if result.success and result.confidence_score > 0.8:
        quality_grade = "A"
    elif result.success and result.confidence_score > 0.6:
        quality_grade = "B"
    elif result.success:
        quality_grade = "C"
    else:
        quality_grade = "F"
    
    return {
        "overall_success": result.success,
        "confidence_score": result.confidence_score,
        "split_accuracy": split_error < 0.05,
        "compression_accuracy": compression_error < 0.2,
        "length_constraint_satisfied": result.length_constraint_satisfied,
        "split_error": split_error,
        "compression_error": compression_error,
        "quality_grade": quality_grade,
        "compression_attempts": result.compression_attempts,
        "length_efficiency": result.actual_compressed_length / result.target_compressed_length if result.target_compressed_length > 0 else 0
    }