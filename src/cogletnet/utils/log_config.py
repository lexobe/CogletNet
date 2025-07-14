"""日志配置模块

此模块提供了统一的日志配置功能，包括：
- 日志格式定义
- 日志级别控制
- 日志处理器配置
"""

import logging
import os
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志格式常量
DEFAULT_FORMAT = '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

@lru_cache(maxsize=None)
def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_str: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称，用于区分不同模块
        level: 日志级别，如果为None则从环境变量获取
        format_str: 日志格式字符串，如果为None则使用默认格式
        date_format: 日期格式字符串，如果为None则使用默认格式
        
    Returns:
        logging.Logger: 配置好的日志记录器
        
    Examples:
        >>> logger = setup_logger("vector_store")
        >>> logger.info("开始处理...")
        [2024-03-20 10:30:45][INFO][vector_store] 开始处理...
    """
    # 获取或创建日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
        
    # 确定日志级别
    if level is None:
        env_var = f"LOG_LEVEL_{name.upper()}"
        level = os.getenv(env_var, "INFO")
        
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    # 创建处理器
        handler = logging.StreamHandler()
    
    # 设置格式化器
        formatter = logging.Formatter(
        format_str or DEFAULT_FORMAT,
        date_format or DEFAULT_DATE_FORMAT
        )
        handler.setFormatter(formatter)
    
    # 配置日志记录器
        logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.propagate = False
    
    return logger

def get_file_logger(
    name: str,
    filename: str,
    level: Optional[str] = None,
    format_str: Optional[str] = None,
    date_format: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置并返回一个文件日志记录器
    
    Args:
        name: 日志记录器名称
        filename: 日志文件路径
        level: 日志级别
        format_str: 日志格式字符串
        date_format: 日期格式字符串
        max_bytes: 单个日志文件的最大大小（字节）
        backup_count: 保留的备份文件数量
        
    Returns:
        logging.Logger: 配置好的文件日志记录器
    """
    logger = logging.getLogger(f"{name}_file")
    
    if logger.handlers:
        return logger
        
    # 确定日志级别
    if level is None:
        env_var = f"LOG_LEVEL_{name.upper()}_FILE"
        level = os.getenv(env_var, "INFO")
        
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        
    # 创建文件处理器
    handler = logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    # 设置格式化器
    formatter = logging.Formatter(
        format_str or DEFAULT_FORMAT,
        date_format or DEFAULT_DATE_FORMAT
    )
    handler.setFormatter(formatter)
    
    # 配置日志记录器
    logger.addHandler(handler)
    logger.setLevel(log_level)
        logger.propagate = False
    
    return logger 