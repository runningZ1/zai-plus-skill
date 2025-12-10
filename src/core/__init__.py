"""
核心功能模块
包含执行器和路由器
"""

from src.core.executor import execute_tool
from src.core.router import VideoRouter

__all__ = [
    "execute_tool",
    "VideoRouter",
]
