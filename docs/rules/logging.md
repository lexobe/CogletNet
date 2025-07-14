# 日志规范

## 1. 日志级别使用规范

### 1.1 ERROR
- 表示严重的错误，导致程序无法继续运行
- 需要立即人工介入处理的问题
- 示例场景：
  - 无法连接到关键服务（如 Upstash）
  - 数据损坏或丢失
  - 关键操作失败

### 1.2 WARNING
- 表示潜在的问题，但程序仍可继续运行
- 需要关注但不需要立即处理的问题
- 示例场景：
  - 重试操作
  - 性能下降
  - 非关键功能失败

### 1.3 INFO
- 表示重要的业务逻辑节点
- 有助于了解程序运行状态的信息
- 示例场景：
  - 服务启动/关闭
  - 重要操作的执行（如批量添加、删除）
  - 配置加载完成

### 1.4 DEBUG
- 用于调试的详细信息
- 开发环境使用，生产环境通常关闭
- 示例场景：
  - 函数调用的参数和返回值
  - 详细的执行步骤
  - 中间状态数据

## 2. 日志格式规范

### 2.1 基本格式
```python
[时间戳][日志级别][模块名] 消息内容
```

### 2.2 消息内容规范
- 使用中文描述具体业务含义
- 包含关键参数信息
- 错误日志需包含错误详情
- 避免无意义的日志

### 2.3 示例
```python
# 好的示例
[2024-03-20 10:30:45][INFO][VectorStore] 添加认元成功: id=abc123
[2024-03-20 10:30:46][ERROR][VectorStore] 连接Upstash失败: 超时(30s)
[2024-03-20 10:30:47][WARNING][VectorStore] 批量操作部分失败: 成功=80, 失败=20

# 不好的示例
[2024-03-20 10:30:45][INFO][VectorStore] Done  # 信息不足
[2024-03-20 10:30:46][ERROR][VectorStore] Error occurred  # 缺少错误详情
```

## 3. 日志使用规范

### 3.1 基本原则
- 每个模块使用独立的日志记录器
- 合理使用日志级别
- 避免重复或冗余的日志
- 敏感信息脱敏处理

### 3.2 代码示例
```python
import logging
from ..utils.log_config import setup_logger

# 创建模块日志记录器
logger = setup_logger("vector_store")

class VectorStore:
    def add_coglet(self, set_id: str, content: str, metadata: dict) -> str:
        try:
            logger.info(f"开始添加认元: set_id={set_id}")
            # ... 处理逻辑 ...
            logger.debug(f"处理元数据: {metadata}")
            # ... 更多处理 ...
            logger.info(f"认元添加成功: id={coglet_id}")
            return coglet_id
        except Exception as e:
            logger.error(f"添加认元失败: {str(e)}", exc_info=True)
            raise
```

### 3.3 日志配置
- 开发环境：DEBUG 级别，控制台输出
- 测试环境：INFO 级别，文件输出
- 生产环境：WARNING 级别，文件输出
- 使用环境变量控制日志级别：
  ```bash
  LOG_LEVEL_vector_store=DEBUG
  LOG_LEVEL_cogletnet=INFO
  ```

## 4. 最佳实践

### 4.1 异常处理
- 捕获异常时记录完整的错误信息和堆栈
- 使用 exc_info=True 参数记录异常堆栈
- 自定义异常需要提供清晰的错误描述

### 4.2 性能考虑
- DEBUG 日志使用 lazy evaluation
- 避免在循环中频繁记录日志
- 批量操作使用汇总日志

### 4.3 安全考虑
- 不记录密码、令牌等敏感信息
- 个人信息需要脱敏处理
- 注意日志文件的权限设置

### 4.4 运维支持
- 日志要包含足够的上下文信息
- 关键操作要有唯一标识符
- 考虑日志的可搜索性 