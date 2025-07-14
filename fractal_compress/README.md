# Fractal Compress v2.0

真正的分形文本压缩库，基于黄金分割比例的分形算法。

## 核心原理

### 分形压缩算法
1. **分割策略**: 当文本超过门限时，按黄金分割比例分割
   - 前 38.2% (1-0.618) 保留在当前层
   - 后 61.8% (0.618) 通过LLM压缩进入下一层

2. **门限计算**: 每层门限 = base_threshold × ratio^level
   - Level 0: 1000 字符
   - Level 1: 618 字符  
   - Level 2: 382 字符
   - Level 3: 236 字符
   - ...

3. **数据结构**: `[[level0], [level1], [level2], ...]`
   - 每层只包含一个字符串
   - 层级索引直接对应压缩深度

## 快速开始

### 基本使用

```python
from fractal_compress import FractalCompressor, PromptManager

# 创建压缩器
compressor = FractalCompressor(
    ratio=0.618,           # 黄金分割比例
    base_threshold=1000,   # level 0 门限
    max_levels=10          # 最大层数
)

# 初始化分形文本结构
fractal_text = [[""]]

# 添加文本并压缩
new_text = "您的长文本内容..."
fractal_text = compressor.compress(fractal_text, new_text)

# 查看结果
print(compressor.visualize_fractal(fractal_text))
```

### 自定义Prompt配置

```python
from fractal_compress import PromptManager

# 创建自定义prompt管理器
prompt_manager = PromptManager({
    "system_prompt": "你是专业的文本压缩助手...",
    "compression_template": "请将以下文本压缩到 {target_length} 字符:\\n{text}",
    "parameters": {
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    "compression_ratio": 0.618
})

# 使用自定义prompt
compressor = FractalCompressor(prompt_manager=prompt_manager)
```

### 渐进式添加文本

```python
# 逐步添加文本，观察分形压缩过程
fractal_text = [[""]]

texts = [
    "第一段文本内容...",
    "第二段文本内容...", 
    "第三段文本内容...",
    # 更多文本...
]

for text in texts:
    fractal_text = compressor.compress(fractal_text, text)
    print(f"添加文本后的层数: {len(fractal_text)}")
    
    # 查看当前状态
    info = compressor.get_fractal_info(fractal_text)
    print(f"总长度: {info['total_length']}")
```

## 核心特性

### 🌀 真正的分形特性
- 每层都遵循相同的0.618分割比例
- 自相似的压缩过程
- 递归的层级结构

### 📊 智能门限管理
- 自动计算每层门限
- 超限自动触发压缩
- 最大层数保护

### 🎯 独立的Prompt管理
- Prompt作为独立数据
- 支持自定义模板
- 动态配置LLM参数

### 📈 详细的统计分析
- 实时压缩统计
- 层级使用情况
- 可视化分形结构

## API 参考

### FractalCompressor

#### 初始化参数
```python
FractalCompressor(
    ratio=0.618,              # 黄金分割比例
    base_threshold=1000,      # Level 0 门限
    max_levels=10,            # 最大层数
    prompt_manager=None       # Prompt管理器
)
```

#### 主要方法

**compress(fractal_text, new_text, prompt_config=None)**
- 执行分形压缩
- 返回更新后的fractal_text

**get_fractal_info(fractal_text)**
- 获取分形结构详细信息
- 包含层级统计和压缩效率

**visualize_fractal(fractal_text)**
- 可视化分形结构
- 返回格式化的显示字符串

### PromptManager

#### 配置结构
```python
{
    "system_prompt": "系统提示词",
    "compression_template": "压缩模板，支持{text}和{target_length}占位符",
    "parameters": {
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    "compression_ratio": 0.618
}
```

#### 主要方法

**get_compression_prompt(text, target_length=None, level=0)**
- 生成压缩提示词
- 自动计算目标长度

**load_from_file(file_path) / save_to_file(file_path)**
- 加载/保存配置文件

**create_custom_template(name, template, parameters)**
- 创建自定义模板

## 使用示例

### 处理长文档

```python
# 读取长文档
with open("long_document.txt", "r") as f:
    content = f.read()

# 分段处理
compressor = FractalCompressor(base_threshold=2000)
fractal_text = [[""]]

# 按段落添加
paragraphs = content.split("\\n\\n")
for para in paragraphs:
    if para.strip():
        fractal_text = compressor.compress(fractal_text, para + "\\n\\n")

# 查看最终结构
print(compressor.visualize_fractal(fractal_text))
```

### 实时内容聚合

```python
# 模拟实时内容流
import time

compressor = FractalCompressor(base_threshold=500)
fractal_text = [[""]]

# 模拟实时添加内容
content_stream = [
    "新闻1: 科技公司发布新产品...",
    "新闻2: 市场分析显示...",
    "新闻3: 专家评论认为...",
    # 更多实时内容
]

for content in content_stream:
    fractal_text = compressor.compress(fractal_text, content)
    
    # 显示当前状态
    info = compressor.get_fractal_info(fractal_text)
    print(f"层数: {info['total_levels']}, 总长度: {info['total_length']}")
    
    time.sleep(1)  # 模拟实时间隔
```

## 安装

```bash
pip install -e .
```

## 环境要求

- Python 3.8+
- litellm
- OpenAI API Key (或其他兼容的LLM API)

## 许可证

MIT License