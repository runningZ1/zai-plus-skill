#!/usr/bin/env python3
"""
智能视频处理路由器
根据输入自动选择最优的视频处理策略，支持失败自动切换
"""
import os
import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ProcessStrategy(Enum):
    """视频处理策略枚举"""
    URL_DIRECT = "url_direct"              # 在线URL直接访问（最优）
    BASE64_SMALL = "base64_small"          # 小文件Base64编码（< 5MB）
    BASE64_LARGE = "base64_large"          # 大文件Base64编码（5-100MB，带警告）
    UPLOAD_RECOMMEND = "upload_recommend"  # 建议上传到云存储（> 100MB）


class VideoRouter:
    """智能视频处理路由器"""

    # 文件大小阈值（MB）
    SMALL_FILE_THRESHOLD = 5.0
    LARGE_FILE_THRESHOLD = 100.0

    # 支持的视频格式
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

    # URL正则匹配
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
        r'(?::\d+)?'  # 可选端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化路由器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or Path(__file__).parent / "user_preferences.json"
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """
        加载用户偏好设置

        Returns:
            Dict: 用户偏好配置
        """
        default_preferences = {
            "default_strategy": "auto",  # auto | url_first | base64_only
            "auto_fallback": True,       # 失败时自动切换策略
            "max_file_size_mb": 100.0,   # 最大文件大小限制
            "warn_large_file": True,     # 大文件警告
            "prefer_url": True,          # 优先使用URL方式
            "strategy_order": [          # 回退策略链
                "url_direct",
                "base64_small",
                "base64_large"
            ]
        }

        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)
                    default_preferences.update(user_prefs)
                    logger.info("用户偏好设置加载成功")
            else:
                # 创建默认配置文件
                self._save_preferences(default_preferences)
                logger.info("创建默认偏好设置")
        except Exception as e:
            logger.warning(f"加载偏好设置失败，使用默认配置: {e}")

        return default_preferences

    def _save_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        保存用户偏好设置

        Args:
            preferences: 偏好配置
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            logger.info("偏好设置保存成功")
        except Exception as e:
            logger.error(f"保存偏好设置失败: {e}")

    def set_default_strategy(self, strategy: str) -> bool:
        """
        设置默认处理策略

        Args:
            strategy: 策略名称 (auto | url_first | base64_only)

        Returns:
            bool: 是否设置成功
        """
        valid_strategies = ["auto", "url_first", "base64_only"]

        if strategy not in valid_strategies:
            logger.error(f"无效的策略: {strategy}, 可选值: {valid_strategies}")
            return False

        self.preferences["default_strategy"] = strategy
        self._save_preferences(self.preferences)
        logger.info(f"默认策略已设置为: {strategy}")
        return True

    def is_url(self, input_str: str) -> bool:
        """
        判断输入是否为URL

        Args:
            input_str: 输入字符串

        Returns:
            bool: 是否为有效URL
        """
        if not input_str:
            return False

        # 使用正则匹配
        if self.URL_PATTERN.match(input_str):
            return True

        # 使用urlparse验证
        try:
            result = urlparse(input_str)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get_file_size_mb(self, file_path: str) -> Optional[float]:
        """
        获取文件大小（MB）

        Args:
            file_path: 文件路径

        Returns:
            Optional[float]: 文件大小（MB），失败返回None
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                size_bytes = path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                return round(size_mb, 2)
        except Exception as e:
            logger.warning(f"获取文件大小失败: {e}")

        return None

    def validate_video_file(self, file_path: str) -> Tuple[bool, str]:
        """
        验证视频文件

        Args:
            file_path: 文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            return False, f"文件不存在: {file_path}"

        if not path.is_file():
            return False, f"路径不是文件: {file_path}"

        # 检查文件格式
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"不支持的文件格式: {path.suffix} (支持: {', '.join(self.SUPPORTED_FORMATS)})"

        # 检查文件大小
        size_mb = self.get_file_size_mb(file_path)
        if size_mb is None:
            return False, "无法获取文件大小"

        max_size = self.preferences.get("max_file_size_mb", 100.0)
        if size_mb > max_size:
            return False, f"文件过大: {size_mb} MB (最大支持 {max_size} MB)"

        return True, ""

    def analyze_input(self, video_input: str) -> Dict[str, Any]:
        """
        分析输入并返回详细信息

        Args:
            video_input: 视频输入（URL或文件路径）

        Returns:
            Dict: 分析结果
        """
        result = {
            "input": video_input,
            "type": None,           # "url" | "file"
            "valid": False,
            "error": None,
            "file_size_mb": None,
            "recommended_strategy": None,
            "fallback_strategies": []
        }

        # 判断输入类型
        if self.is_url(video_input):
            result["type"] = "url"
            result["valid"] = True
            result["recommended_strategy"] = ProcessStrategy.URL_DIRECT
            result["fallback_strategies"] = []  # URL方式无回退

        else:
            result["type"] = "file"

            # 验证文件
            is_valid, error_msg = self.validate_video_file(video_input)
            result["valid"] = is_valid
            result["error"] = error_msg

            if is_valid:
                size_mb = self.get_file_size_mb(video_input)
                result["file_size_mb"] = size_mb

                # 根据文件大小选择策略
                if size_mb <= self.SMALL_FILE_THRESHOLD:
                    result["recommended_strategy"] = ProcessStrategy.BASE64_SMALL
                    result["fallback_strategies"] = []
                elif size_mb <= self.LARGE_FILE_THRESHOLD:
                    result["recommended_strategy"] = ProcessStrategy.BASE64_LARGE
                    result["fallback_strategies"] = []
                else:
                    result["recommended_strategy"] = ProcessStrategy.UPLOAD_RECOMMEND
                    result["fallback_strategies"] = []

        return result

    def route(self, video_input: str, user_question: Optional[str] = None) -> Dict[str, Any]:
        """
        执行智能路由决策

        Args:
            video_input: 视频输入（URL或文件路径）
            user_question: 用户问题（可选）

        Returns:
            Dict: 路由决策结果
        """
        logger.info(f"开始路由分析: {video_input[:100]}...")

        # 分析输入
        analysis = self.analyze_input(video_input)

        # 构建路由决策
        decision = {
            "input_analysis": analysis,
            "strategy": None,
            "execution_plan": None,
            "warnings": [],
            "recommendations": []
        }

        if not analysis["valid"]:
            decision["strategy"] = None
            decision["execution_plan"] = None
            decision["warnings"].append(f"输入无效: {analysis['error']}")
            return decision

        # 根据用户偏好调整策略
        default_strategy = self.preferences.get("default_strategy", "auto")

        if default_strategy == "url_first" and analysis["type"] == "file":
            decision["recommendations"].append(
                "💡 提示: 您设置了URL优先模式，建议将视频上传到云存储后使用URL访问，"
                "这样可以节省约25-50%的Token消耗"
            )

        if default_strategy == "base64_only" and analysis["type"] == "url":
            decision["warnings"].append(
                "⚠️  您设置了Base64优先模式，但输入的是URL。将使用URL模式。"
            )

        # 确定最终策略
        strategy = analysis["recommended_strategy"]
        decision["strategy"] = strategy

        # 添加警告信息
        if strategy == ProcessStrategy.BASE64_LARGE:
            file_size = analysis["file_size_mb"]
            decision["warnings"].append(
                f"⚠️  文件较大({file_size} MB)，处理时间和Token消耗会较高。"
                f"建议上传到云存储后使用URL方式，可节省约30-40%的成本。"
            )

        if strategy == ProcessStrategy.UPLOAD_RECOMMEND:
            decision["warnings"].append(
                f"❌ 文件过大({analysis['file_size_mb']} MB)，超过最大限制。"
            )
            decision["recommendations"].append(
                "建议步骤:\n"
                "1. 将视频上传到云存储（如七牛云、阿里云OSS、腾讯云COS）\n"
                "2. 获取视频的公开访问URL\n"
                "3. 使用URL方式进行分析（推荐）"
            )

        # 构建执行计划
        decision["execution_plan"] = self._build_execution_plan(analysis, strategy)

        logger.info(f"路由决策完成: {strategy.value if strategy else 'None'}")
        return decision

    def _build_execution_plan(
        self,
        analysis: Dict[str, Any],
        strategy: Optional[ProcessStrategy]
    ) -> Optional[Dict[str, Any]]:
        """
        构建执行计划

        Args:
            analysis: 输入分析结果
            strategy: 选定的策略

        Returns:
            Optional[Dict]: 执行计划
        """
        if strategy is None:
            return None

        plan = {
            "strategy": strategy.value,
            "method": None,
            "estimated_time": None,
            "estimated_tokens": None,
            "temp_files": 0
        }

        if strategy == ProcessStrategy.URL_DIRECT:
            plan["method"] = "analyze_video_url"
            plan["estimated_time"] = "20-30秒"
            plan["estimated_tokens"] = "35,000-45,000"
            plan["temp_files"] = 1  # 仅JS脚本

        elif strategy == ProcessStrategy.BASE64_SMALL:
            size_mb = analysis.get("file_size_mb", 0)
            plan["method"] = "analyze_video_base64"
            plan["estimated_time"] = f"{int(20 + size_mb * 2)}-{int(30 + size_mb * 3)}秒"
            plan["estimated_tokens"] = f"{int(40000 + size_mb * 2000)}-{int(55000 + size_mb * 3000)}"
            plan["temp_files"] = 2  # JS脚本 + Base64文件

        elif strategy == ProcessStrategy.BASE64_LARGE:
            size_mb = analysis.get("file_size_mb", 0)
            plan["method"] = "analyze_video_base64"
            plan["estimated_time"] = f"{int(30 + size_mb * 3)}-{int(50 + size_mb * 5)}秒"
            plan["estimated_tokens"] = f"{int(50000 + size_mb * 3000)}-{int(80000 + size_mb * 5000)}"
            plan["temp_files"] = 2

        return plan

    def get_strategy_comparison(self) -> str:
        """
        获取策略对比说明

        Returns:
            str: 对比说明文本
        """
        comparison = """
╔══════════════════════════════════════════════════════════════╗
║              视频处理策略对比                                ║
╠══════════════════════════════════════════════════════════════╣
║ 策略          │ 适用场景        │ Token消耗 │ 速度    │ 优先级 ║
╠══════════════════════════════════════════════════════════════╣
║ URL直接访问   │ 在线视频        │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐⭐ │   1   ║
║ 小文件Base64  │ < 5MB本地视频   │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │   2   ║
║ 大文件Base64  │ 5-100MB本地视频 │ ⭐⭐⭐     │ ⭐⭐⭐     │   3   ║
║ 建议上传      │ > 100MB视频     │ N/A      │ N/A    │   -   ║
╚══════════════════════════════════════════════════════════════╝

💡 推荐策略:
  1. 优先使用在线URL（Token最省、速度最快）
  2. 小文件可直接Base64处理（< 5MB）
  3. 大文件建议上传到云存储后使用URL
  4. 超大文件(> 100MB)必须先上传

⚙️  设置默认策略:
  router.set_default_strategy('url_first')   # URL优先
  router.set_default_strategy('base64_only') # Base64优先
  router.set_default_strategy('auto')        # 自动选择（默认）
"""
        return comparison


def main():
    """演示路由器功能"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    router = VideoRouter()

    # 打印策略对比
    print(router.get_strategy_comparison())

    # 测试案例
    test_cases = [
        "http://example.com/video.mp4",
        "D:\\Video\\small_video.mp4",
        "C:\\Users\\test\\large_video.mp4",
        "/invalid/path/video.mp4"
    ]

    print("\n" + "="*60)
    print("路由测试案例")
    print("="*60 + "\n")

    for test_input in test_cases:
        print(f"📹 输入: {test_input}")
        decision = router.route(test_input)

        print(f"  类型: {decision['input_analysis']['type']}")
        print(f"  有效: {decision['input_analysis']['valid']}")

        if decision['strategy']:
            print(f"  策略: {decision['strategy'].value}")
            plan = decision['execution_plan']
            print(f"  预估时间: {plan['estimated_time']}")
            print(f"  预估Token: {plan['estimated_tokens']}")

        if decision['warnings']:
            for warning in decision['warnings']:
                print(f"  {warning}")

        print()


if __name__ == "__main__":
    main()
