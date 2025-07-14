## 1、项目结构
CogletNet/
├── src/
│   └── cogletnet/
│       ├── __init__.py                 # 版本号和公共API导出
│       ├── core/
│       │   ├── __init__.py            # 核心模块导出
│       │   ├── cogletnet.py           # 主要认知网络实现
│       │   ├── coglets.py             # 认元管理
│       │   ├── mam.py                 # 记忆锚定机制
│       │   └── vector_store.py        # 向量存储实现
│       ├── utils/
│       │   ├── __init__.py            # 工具函数导出
│       │   ├── id_generator.py        # ID生成工具
│       │   ├── llm_checker.py         # LLM检查工具
│       │   └── logger.py              # 日志配置
│       ├── exceptions/
│       │   ├── __init__.py            # 异常类导出
│       │   ├── coglet_errors.py       # 认元相关异常
│       │   ├── llm_errors.py          # LLM相关异常
│       │   └── vector_errors.py       # 向量存储相关异常
│       └── types/
│           ├── __init__.py            # 类型定义导出
│           ├── coglet_types.py        # 认元相关类型
│           └── vector_types.py        # 向量相关类型
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # pytest配置和通用fixture
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_cogletnet.py         # 认知网络测试
│   │   ├── test_coglets.py           # 认元管理测试
│   │   ├── test_mam.py               # MAM测试
│   │   └── test_vector_store.py      # 向量存储测试
│   └── utils/
│       ├── __init__.py
│       ├── test_id_generator.py       # ID生成测试
│       └── test_llm_checker.py        # LLM检查测试
├── docs/
│   ├── api/
│   │   ├── core.md                    # 核心模块API文档
│   │   ├── utils.md                   # 工具模块API文档
│   │   └── exceptions.md              # 异常类文档
│   ├── guides/
│   │   ├── getting_started.md         # 入门指南
│   │   ├── basic_usage.md            # 基础用法
│   │   └── advanced_usage.md         # 高级用法
│   └── examples/
│       ├── basic_examples.md          # 基础示例
│       └── advanced_examples.md       # 高级示例
├── examples/
│   ├── __init__.py
│   ├── basic_usage.py                 # 基础使用示例
│   ├── advanced_usage.py              # 高级使用示例
│   └── custom_integration.py          # 自定义集成示例
├── pyproject.toml                     # 项目配置和构建设置
├── setup.py                           # 包安装配置
├── setup.cfg                          # 工具配置
├── requirements/
│   ├── base.txt                       # 基础依赖
│   ├── dev.txt                        # 开发依赖
│   └── docs.txt                       # 文档依赖
├── .gitignore                         # Git忽略配置
├── .pre-commit-config.yaml            # pre-commit钩子配置
├── README.md                          # 项目说明
├── CHANGELOG.md                       # 版本变更记录
├── CONTRIBUTING.md                    # 贡献指南
└── LICENSE                            # 开源协议

## 2、核心文件说明

### cogletnet.py - 认知网络主要实现
认知网络的核心控制器，负责协调整个系统的运行。

主要功能：
1. 认知循环（Think Loop）的实现
   - 单次思考过程控制（think）
   - 多轮思考循环管理（think_loop）
   - 思考阈值和最大循环次数控制
2. LLM交互管理
   - 系统提示词组织（role_prompt, format_prompt, thinking_prompt, example_prompt）
   - LLM调用和响应处理
   - 结果解析和函数调用
3. 认知状态管理
   - 认元集合管理
   - 认知过程记录
   - 函数调用处理

关键方法：
```python
class CogletNet:
    def __init__(self,
        # 基础存储配置
        upstash_url: str,              # Upstash 服务地址
        upstash_token: str,            # Upstash 访问令牌
        set_id: Optional[str] = None,  # 认知集合ID，不提供则自动生成
        
        # LLM配置
        model: str = "4o-mini",        # LLM模型名称
        max_retries: int = 3,          # LLM调用最大重试次数
        temperature: float = 0.7,      # LLM温度参数
        
        # 记忆机制配置
        memory_config: Dict[str, Any] = {
            "beta": 0.85,               # 时间衰减系数
            "gamma": 0.3,               # 访问增强系数
            "b": 0.05,                  # 基础衰减率
            "initial_weight": 0.5,      # 初始权重
            "golden_ratio": 0.618,      # 黄金分割比例
            "top_k": 10                 # 返回结果数量
        },
        
        # 思考过程配置
        max_think_cycles: int = 5,     # 最大思考循环次数
        think_threshold: float = 0.7,  # 思考阈值
        
        # 提示词配置
        role_prompt: Optional[str] = None,     # 角色定义
        format_prompt: Optional[str] = None,   # 输出格式定义
        thinking_prompt: Optional[str] = None, # 思考指导
        example_prompt: Optional[str] = None   # 示例说明
    )

    def think(self, input_text: str, set_id: str) -> Dict[str, Any]:
        """
        单次思考过程
        返回：{
            "next_thought": str,          # 下一轮思考内容
            "activated_cog_ids": list,    # 激活的认元ID列表
            "log": str,                   # 思考日志
            "generated_cog_texts": list,  # 生成的新认元文本
            "function_calls": list        # 函数调用列表
        }
        """

    def think_loop(self, input_text: str, set_id: str, max_iterations: int = 5) -> List[Dict[str, Any]]:
        """
        循环思考过程
        返回思考过程的完整记录列表
        """

    def _format_llm_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """格式化提示词"""

    def _get_system_prompt(self) -> str:
        """获取完整的系统提示词"""

    def call_function(self, func_call: Dict[str, Any]) -> Any:
        """执行函数调用"""
```

特点：
1. 完整的配置参数
   - LLM相关配置（模型、重试、温度等）
   - 记忆机制参数（衰减系数、增强系数等）
   - 提示词模板（角色、格式、思考、示例）

2. 标准化的输出格式
   - 结构化的思考结果
   - 完整的认知过程记录
   - 清晰的函数调用接口

3. 灵活的扩展性
   - 可自定义提示词模板
   - 可配置思考参数
   - 支持函数调用机制

### coglets.py - 认元管理
认元（Coglet）的生命周期管理，处理认元的创建、存储、检索和更新。

主要功能：
1. 认元基本操作
   - 创建和注册新认元
   - 更新认元内容和元数据
   - 删除和清理认元
2. 认元集合管理
   - 集合的创建和维护
   - 批量操作支持
3. 认元检索和激活
   - 相似度搜索
   - 权重更新
   - 记忆激活

关键方法：
```python
class Coglets:
    def __init__(self,
        vector_store: VectorStore,
        mam: MAM,
        config: dict = None
    )
    def create_set(self, set_id: str, description: str = "") -> bool
    def add(self, set_id: str, content: str, metadata: dict = None) -> str
    def get(self, coglet_id: str) -> dict
    def update_weight(self, coglet_id: str, current_time: datetime = None) -> bool
    def recall(self, set_id: str, query: str) -> dict
```

### mam.py - 记忆锚定机制
实现记忆的权重计算和激活选择机制。

主要功能：
1. 权重计算
   - 时间衰减处理
   - 访问频率影响
   - 基础衰减控制
2. 记忆激活
   - 黄金分割比例选择
   - 阈值控制
   - 激活优先级

关键方法：
```python
class MAM:
    def __init__(self,
        beta: float = 0.85,      # 时间衰减系数
        gamma: float = 0.3,      # 访问增强系数
        b: float = 0.05,         # 基础衰减率
        initial_weight: float = 0.5,  # 初始权重
        golden_ratio: float = 0.618   # 黄金分割比例
    )
    def calculate_weight(self, current_weight: float,
                        last_access_time: datetime,
                        current_time: datetime,
                        access_count: int = 0) -> float
    def select_activated_memories(self, memories: list,
                                sort_by: str = 'weight') -> list
```

### vector_store.py - 向量存储实现
向量数据的存储和检索实现，基于 Upstash 向量数据库。

主要功能：
1. 向量操作
   - 向量的存储和检索
   - 批量向量操作
   - 元数据管理
2. 相似度搜索
   - 语义相似度计算
   - Top-K 检索
3. 集合管理
   - 集合的创建和维护
   - 集合的清理和重置

关键方法：


## 3、模块依赖关系

```
CogletNet (认知网络)
  ├── Coglets (认元管理)
  │     ├── VectorStore (向量存储)
  │     └── MAM (记忆锚定)
  └── LLM Service (语言模型)
```

- CogletNet 作为顶层控制器，协调其他模块的工作
- Coglets 负责认元的管理，依赖 VectorStore 和 MAM
- VectorStore 提供底层存储能力
- MAM 提供记忆机制的核心算法
