"""
ZAI Plus Skill - 智谱AI多模态分析技能包
支持文本、图像、视频的智能分析
"""

__version__ = "2.1.0"
__author__ = "ZAI Plus Skill Team"
__description__ = "智谱AI多模态分析技能包，支持智能路由和自动策略选择"

from src.core.router import VideoRouter
from src.analyzers.smart_analyzer import SmartVideoAnalyzer

__all__ = [
    "VideoRouter",
    "SmartVideoAnalyzer",
]
