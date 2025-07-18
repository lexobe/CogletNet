#!/usr/bin/env python3
"""
独立的LLM文本压缩工具
专门用于prompt优化实验和研究
"""

import litellm
import time
from typing import Dict, List, Any, Optional

class LLMTextCompressor:
    """
    独立的LLM文本压缩器
    
    专门设计用于prompt优化实验，提供：
    - 灵活的prompt模板系统
    - 可自定义的Few-shot示例
    - 多策略压缩尝试
    - 详细的结果分析
    """
    
    def __init__(self, default_model: str = "gpt-4o-mini"):
        self.default_model = default_model
        self.default_templates = self._create_default_templates()
        self.default_examples = self._create_default_examples()
    
    def _create_default_templates(self) -> Dict[str, str]:
        """创建默认prompt模板"""
        return {
            "basic": """请将以下文本压缩到{target_length}字符以内：

原文：{text}
目标长度：≤{target_length}字符

压缩结果：""",
            
            "precise": """你是一个专业的文本压缩专家。请严格按照要求压缩文本。

📝 原文："{text}"
📏 原文长度：{original_length}字符
🎯 目标长度：≤{target_length}字符
📊 压缩比例：{compression_ratio:.1%}

要求：
1. 保持核心意思
2. 长度必须≤{target_length}字符
3. 表达简洁准确

直接输出压缩结果：""",
            
            "few_shot": """以下是文本压缩示例，请学习压缩技巧：

{examples}

现在请压缩以下文本：
原文："{text}" (长度: {original_length})
目标长度：≤{target_length}字符

压缩结果：""",
            
            "creative": """创造性文本压缩任务：

原文：{text}
挑战：用≤{target_length}字符表达相同意思
技巧：可以使用缩写、同义词、重新表述

输出：""",
            
            "strict": """严格长度控制压缩：

输入：{text}
输出要求：≤{target_length}字符
规则：超出长度视为失败

输出："""
        }
    
    def _create_default_examples(self) -> List[Dict[str, Any]]:
        """创建默认Few-shot示例"""
        return [
            {
                "original": "人工智能技术在医疗诊断领域的应用越来越广泛",
                "target": 12,
                "compressed": "AI在医疗诊断应用广",
                "strategy": "缩写+关键词"
            },
            {
                "original": "Machine learning algorithms improve data analysis",
                "target": 20,
                "compressed": "ML algorithms enhance data analysis",
                "strategy": "缩写+同义词"
            },
            {
                "original": "Cloud computing提供scalable infrastructure solutions",
                "target": 18,
                "compressed": "云计算提供可扩展基础设施",
                "strategy": "翻译+核心概念"
            }
        ]
    
    def compress(
        self,
        text: str,
        target_length: int,
        model: Optional[str] = None,
        strategy: str = "precise",
        max_attempts: int = 3,
        temperature: float = 0.1,
        custom_template: Optional[str] = None,
        custom_examples: Optional[List[Dict]] = None,
        strict_length: bool = True
    ) -> Dict[str, Any]:
        """压缩文本"""
        model = model or self.default_model
        start_time = time.time()
        
        template = custom_template if custom_template else self.default_templates.get(strategy, self.default_templates["precise"])
        examples = custom_examples if custom_examples else self.default_examples
        
        for attempt in range(max_attempts):
            try:
                prompt = self._build_prompt(template, text, target_length, strategy, examples)
                
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=min(800, target_length * 4),
                    timeout=30
                )
                
                compressed = response.choices[0].message.content.strip()
                compressed = self._clean_output(compressed)
                
                if strict_length and len(compressed) > target_length:
                    compressed = self._smart_truncate(compressed, target_length)
                
                if self._validate_quality(compressed, text, target_length, strict_length):
                    return {
                        "text": compressed,
                        "original_text": text,
                        "original_length": len(text),
                        "compressed_length": len(compressed),
                        "target_length": target_length,
                        "compression_ratio": len(compressed) / len(text) if len(text) > 0 else 0,
                        "attempts": attempt + 1,
                        "strategy": strategy,
                        "temperature": temperature,
                        "model": model,
                        "processing_time": time.time() - start_time,
                        "success": True,
                        "length_constraint_satisfied": len(compressed) <= target_length,
                        "prompt": prompt
                    }
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    fallback = text[:target_length] if len(text) > target_length else text
                    return {
                        "text": fallback,
                        "original_text": text,
                        "original_length": len(text),
                        "compressed_length": len(fallback),
                        "target_length": target_length,
                        "compression_ratio": len(fallback) / len(text) if len(text) > 0 else 0,
                        "attempts": attempt + 1,
                        "strategy": "fallback",
                        "temperature": temperature,
                        "model": model,
                        "processing_time": time.time() - start_time,
                        "success": False,
                        "error": str(e),
                        "length_constraint_satisfied": len(fallback) <= target_length
                    }
                continue
        
        fallback = text[:target_length] if len(text) > target_length else text
        return {
            "text": fallback,
            "original_text": text,
            "original_length": len(text),
            "compressed_length": len(fallback),
            "target_length": target_length,
            "compression_ratio": len(fallback) / len(text) if len(text) > 0 else 0,
            "attempts": max_attempts,
            "strategy": "fallback",
            "temperature": temperature,
            "model": model,
            "processing_time": time.time() - start_time,
            "success": False,
            "length_constraint_satisfied": len(fallback) <= target_length
        }
    
    def _build_prompt(self, template: str, text: str, target_length: int, strategy: str, examples: List[Dict]) -> str:
        """构造prompt"""
        original_length = len(text)
        compression_ratio = target_length / original_length if original_length > 0 else 0
        
        examples_text = ""
        if strategy == "few_shot":
            examples_text = self._format_examples(examples)
        
        try:
            return template.format(
                text=text,
                target_length=target_length,
                original_length=original_length,
                compression_ratio=compression_ratio,
                examples=examples_text
            )
        except KeyError:
            return f"请将以下文本压缩到{target_length}字符以内：\n\n{text}\n\n压缩结果："
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """格式化示例文本"""
        formatted = ""
        for i, example in enumerate(examples[:2], 1):
            formatted += f"""示例{i}：
原文："{example['original']}" (长度: {len(example['original'])})
目标：≤{example['target']}字符
压缩："{example['compressed']}" (长度: {len(example['compressed'])})
技巧：{example.get('strategy', '核心提取')}

"""
        return formatted
    
    def _clean_output(self, text: str) -> str:
        """清理LLM输出"""
        # 移除各种引号
        quote_pairs = [('"', '"'), ("'", "'"), ('"', '"'), (''', ''')]
        for start_quote, end_quote in quote_pairs:
            if text.startswith(start_quote) and text.endswith(end_quote):
                text = text[1:-1]
                break
        
        # 移除常见前缀
        prefixes = ["压缩结果：", "输出：", "结果：", "答案：", "压缩："]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        return text.strip()
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断到指定长度"""
        if len(text) <= max_length:
            return text
        
        # 尝试在标点符号处截断
        punctuation = ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';']
        for i in range(max_length - 1, max(0, max_length - 10), -1):
            if i < len(text) and text[i] in punctuation:
                return text[:i + 1]
        
        # 尝试在空格处截断
        for i in range(max_length - 1, max(0, max_length - 5), -1):
            if i < len(text) and text[i] == ' ':
                return text[:i]
        
        return text[:max_length]
    
    def _validate_quality(self, compressed: str, original: str, target_length: int, strict_length: bool) -> bool:
        """验证压缩质量"""
        if not compressed or len(compressed) == 0:
            return False
        
        if strict_length and len(compressed) > target_length:
            return False
        
        if len(compressed) >= len(original):
            return False
        
        return True
    
    def batch_test(self, test_cases: List[Dict[str, Any]], strategies: List[str] = None, model: str = None) -> Dict[str, Any]:
        """批量测试不同策略和参数"""
        strategies = strategies or ["basic", "precise", "few_shot"]
        results = {}
        
        for strategy in strategies:
            results[strategy] = []
            for case in test_cases:
                result = self.compress(
                    text=case["text"],
                    target_length=case["target"],
                    model=model,
                    strategy=strategy,
                    max_attempts=2
                )
                results[strategy].append(result)
        
        # 计算统计信息
        stats = {}
        for strategy, strategy_results in results.items():
            success_count = sum(1 for r in strategy_results if r["success"])
            avg_compression = sum(r["compression_ratio"] for r in strategy_results) / len(strategy_results)
            avg_time = sum(r["processing_time"] for r in strategy_results) / len(strategy_results)
            
            stats[strategy] = {
                "success_rate": success_count / len(strategy_results),
                "avg_compression_ratio": avg_compression,
                "avg_processing_time": avg_time,
                "total_cases": len(strategy_results)
            }
        
        return {
            "results": results,
            "statistics": stats,
            "total_cases": len(test_cases),
            "strategies_tested": strategies
        }

# 便捷函数
def quick_compress(text: str, target_length: int, strategy: str = "precise") -> str:
    """快速压缩文本"""
    compressor = LLMTextCompressor()
    result = compressor.compress(text, target_length, strategy=strategy)
    return result["text"]

def compare_strategies(text: str, target_length: int) -> Dict[str, str]:
    """比较不同策略的压缩效果"""
    compressor = LLMTextCompressor()
    strategies = ["basic", "precise", "few_shot", "creative", "strict"]
    results = {}
    
    for strategy in strategies:
        result = compressor.compress(text, target_length, strategy=strategy, max_attempts=1)
        results[strategy] = result["text"]
    
    return results