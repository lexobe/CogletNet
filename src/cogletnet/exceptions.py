"""
CogletNet 自定义异常
"""

class CogletNetError(Exception):
    """CogletNet 基础异常类"""
    pass

class ConfigurationError(CogletNetError):
    """配置错误"""
    pass

class StorageError(CogletNetError):
    """存储操作错误"""
    pass

class LLMError(CogletNetError):
    """LLM 调用错误"""
    pass

class CogletError(CogletNetError):
    """认元操作错误"""
    pass 