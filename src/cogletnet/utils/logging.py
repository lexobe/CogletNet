"""
日志配置模块
"""

import logging
import os
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，如果不指定则从环境变量获取
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
        
    # 设置日志级别
    if level is None:
        # 从环境变量获取日志级别
        env_level = os.getenv(f"LOG_LEVEL_{name}", "INFO")
        level = getattr(logging, env_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 创建控制台处理器
        handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
    
    # 添加处理器
        logger.addHandler(handler)
    
    return logger 