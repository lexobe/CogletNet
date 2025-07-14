"""
CogletNet - 认知网络框架

这个包提供了一个灵活的认知网络实现，用于构建和管理认知系统。

主要功能:
- 认知网络管理 (CogletNet)
- 向量存储 (VectorStore)
- 记忆锚定机制 (MAM)
- 认元管理 (Coglets)

Example:
    >>> from cogletnet import CogletNet
    >>> net = CogletNet(
    ...     storage_config={
    ...         "upstash_url": "your-url",
    ...         "upstash_token": "your-token",
    ...     }
    ... )
    >>> result = net.think("你的输入", "set_id")
"""

from cogletnet.core.cogletnet import CogletNet
from cogletnet.core.vector_store import VectorStore
from cogletnet.core.mam import MAM
from cogletnet.core.coglets import Coglets

__version__ = "0.1.0"

__all__ = [
    'CogletNet',
    'VectorStore',
    'MAM',
    'Coglets',
] 