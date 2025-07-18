# Fractal Compress

基于黄金分割比例的LLM文本压缩库，提供简洁易用的标准API。

## ✨ 新特性

### 🎯 四个标准函数，覆盖所有需求：

```python
from fractal_compress import compress, split_and_compress, llm_compress, simple_split

# 1. 标准压缩 - 一键压缩，支持自定义比例
result = compress(text, split_ratio=0.4, compression_ratio=0.6)

# 2. 分割并压缩 - 获取压缩部分和剩余部分
compressed_part, remaining_part = split_and_compress(text)

# 3. 纯LLM压缩 - 直接指定目标长度
result = llm_compress(text, target_length=20)

# 4. 简单分割 - 只分割不压缩
part1, part2 = simple_split(text, split_ratio=0.5)
```

### 🔧 核心特性

- **可配置压缩比**: 支持任意 `split_ratio` 和 `compression_ratio`
- **简洁返回值**: 函数直接返回文本，无冗余统计信息
- **多语言支持**: 中文、英文、混合语言智能处理
- **黄金分割优化**: 默认使用 0.382/0.618 黄金分割比例
- **向后兼容**: 保留旧API，平滑升级

## 快速开始

### 安装

```bash
pip install -e .
```

### 基本使用

```python
from fractal_compress import compress, split_and_compress, llm_compress

# 最简单 - 一行代码压缩
result = compress("人工智能技术正在改变世界")
print(result)  # "人工智能"

# 自定义压缩比例
result = compress(
    "AI technology is transforming industries",
    split_ratio=0.5,      # 50% 分割
    compression_ratio=0.4  # 40% 压缩
)

# 分割并处理两部分
compressed_part, remaining_part = split_and_compress(
    "长文本内容...",
    split_ratio=0.6,
    compression_ratio=0.7
)

# 精确控制长度
result = llm_compress("长文本内容", target_length=15)
print(len(result))  # ≤ 15
```

### 高级用法

```python
# 多语言处理
texts = {
    "中文": "人工智能正在改变世界",
    "English": "AI is transforming the world", 
    "混合": "AI人工智能technology正在changing世界"
}

for lang, text in texts.items():
    language = "chinese" if "中文" in lang else "english" if "English" in lang else "mixed"
    result = compress(text, language=language)
    print(f"{lang}: {result}")

# 不同策略比较
strategies = ["basic", "precise", "creative"]
for strategy in strategies:
    result = llm_compress("文本内容", target_length=10, strategy=strategy)
    print(f"{strategy}: {result}")

# 渐进式压缩
ratios = [0.3, 0.5, 0.7, 0.9]
for ratio in ratios:
    result = compress(text, compression_ratio=ratio)
    print(f"压缩比{ratio}: {result}")
```

## 主要特性

### 🎯 精确控制
- 基于黄金分割比例的数学精确性
- 严格的长度约束控制
- 可配置的压缩策略和参数

### 🚀 高性能
- 智能文本分割算法
- 优化的LLM调用策略
- 批量处理和并发支持

### 🔧 易扩展
- 模块化设计
- 可自定义prompt模板
- 支持多种语言和文本类型

### 📊 质量保证
- 置信度评估系统
- 质量分级和验证
- 详细的性能分析

## 使用示例

查看 `examples/simple_example.py` 了解详细使用方法。

## 环境要求

- Python 3.8+
- OpenAI API密钥 (设置环境变量 `OPENAI_API_KEY`)
- 依赖包：litellm, python-dotenv

## 项目结构

```
fractal_compress/
├── src/fractal_compress/
│   └── utils/                      # 核心工具包
│       ├── hybrid_compressor.py    # 混合压缩器 (主要接口)
│       ├── llm_compressor.py       # 独立LLM压缩器
│       └── text_splitter.py        # 智能文本分割工具
├── examples/                       # 使用示例
│   └── simple_example.py
└── tests/                          # 测试文件
    └── test_fractal_compressor.py
```

## API说明

### 🌟 标准API（推荐）
- `compress(text, *, split_ratio=0.382, compression_ratio=0.618, ...)` - 标准压缩
- `split_and_compress(text, *, split_ratio=0.382, compression_ratio=0.618, ...)` - 分割并压缩
- `llm_compress(text, *, target_length=None, compression_ratio=0.618, ...)` - 纯LLM压缩
- `simple_split(text, *, split_ratio=0.382, language="mixed")` - 简单分割

### 🔧 核心组件
- `LLMTextCompressor` - 独立LLM压缩器，支持多种策略
- `smart_split` - 黄金分割智能文本分割
- `quick_compress` - LLM快速压缩
- `compare_strategies` - 策略效果比较

### 🔄 向后兼容
- `compress_text` - 兼容旧版本的压缩函数
- `HybridCompressor` - 高级压缩器类（保留用于特殊需求）

## 参数说明

### 通用参数
- `split_ratio`: 分割比例 (0.0-1.0)，默认 0.382（黄金分割）
- `compression_ratio`: 压缩比例 (0.0-1.0)，默认 0.618（黄金分割）
- `language`: 语言类型 ("chinese", "english", "mixed")
- `model`: LLM模型名称，默认 "gpt-4o-mini"
- `strategy`: 压缩策略 ("basic", "precise", "few_shot", "creative", "strict")

### 特殊参数
- `target_length`: 目标长度（仅 `llm_compress`）
- `max_attempts`: 最大重试次数，默认 3

## 开发团队

CogletNet Team - 专注于认知网络和智能压缩技术研究

## 许可证

MIT License