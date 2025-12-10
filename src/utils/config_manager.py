#!/usr/bin/env python3
"""
配置管理模块
统一管理所有配置文件的加载和保存
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """统一配置管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录，默认为项目根目录的config文件夹
        """
        if config_dir is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.mcp_config_path = self.config_dir / "mcp_config.json"
        self.user_prefs_path = self.config_dir / "user_preferences.json"

        # 缓存配置
        self._mcp_config = None
        self._user_prefs = None

    def load_mcp_config(self) -> Dict[str, Any]:
        """
        加载MCP配置

        Returns:
            Dict: MCP配置字典
        """
        if self._mcp_config is not None:
            return self._mcp_config

        try:
            if not self.mcp_config_path.exists():
                raise FileNotFoundError(f"MCP配置文件不存在: {self.mcp_config_path}")

            with open(self.mcp_config_path, 'r', encoding='utf-8') as f:
                self._mcp_config = json.load(f)

            # 验证必要字段
            if "env" not in self._mcp_config:
                raise ValueError("MCP配置文件缺少 'env' 字段")

            if "Z_AI_API_KEY" not in self._mcp_config.get("env", {}):
                raise ValueError("MCP配置文件中未找到 Z_AI_API_KEY")

            logger.info("MCP配置加载成功")
            return self._mcp_config

        except json.JSONDecodeError as e:
            raise ValueError(f"MCP配置文件JSON格式错误: {e}")
        except Exception as e:
            logger.error(f"加载MCP配置失败: {e}")
            raise

    def load_user_preferences(self) -> Dict[str, Any]:
        """
        加载用户偏好配置

        Returns:
            Dict: 用户偏好字典
        """
        if self._user_prefs is not None:
            return self._user_prefs

        default_prefs = {
            "default_strategy": "auto",
            "auto_fallback": True,
            "max_file_size_mb": 100.0,
            "warn_large_file": True,
            "prefer_url": True,
            "strategy_order": [
                "url_direct",
                "base64_small",
                "base64_large"
            ]
        }

        try:
            if self.user_prefs_path.exists():
                with open(self.user_prefs_path, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)
                    default_prefs.update(user_prefs)
                    logger.info("用户偏好配置加载成功")
            else:
                # 创建默认配置文件
                self.save_user_preferences(default_prefs)
                logger.info("创建默认用户偏好配置")

            self._user_prefs = default_prefs
            return self._user_prefs

        except Exception as e:
            logger.warning(f"加载用户偏好失败，使用默认配置: {e}")
            self._user_prefs = default_prefs
            return self._user_prefs

    def save_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        保存用户偏好配置

        Args:
            preferences: 用户偏好字典

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.user_prefs_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            logger.info("用户偏好配置保存成功")
            self._user_prefs = preferences
            return True
        except Exception as e:
            logger.error(f"保存用户偏好失败: {e}")
            return False

    def get_api_key(self) -> str:
        """
        获取API密钥

        Returns:
            str: API密钥
        """
        config = self.load_mcp_config()
        return config.get("env", {}).get("Z_AI_API_KEY", "")

    def get_model_name(self, default: str = "glm-4.6v") -> str:
        """
        获取模型名称

        Args:
            default: 默认模型名称

        Returns:
            str: 模型名称
        """
        config = self.load_mcp_config()
        return config.get("env", {}).get("Z_AI_MODE", default)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        获取用户偏好设置项

        Args:
            key: 配置项键名
            default: 默认值

        Returns:
            Any: 配置项值
        """
        prefs = self.load_user_preferences()
        return prefs.get(key, default)

    def set_preference(self, key: str, value: Any) -> bool:
        """
        设置用户偏好项

        Args:
            key: 配置项键名
            value: 配置项值

        Returns:
            bool: 是否设置成功
        """
        prefs = self.load_user_preferences()
        prefs[key] = value
        return self.save_user_preferences(prefs)

    def reset_preferences(self) -> bool:
        """
        重置用户偏好为默认值

        Returns:
            bool: 是否重置成功
        """
        default_prefs = {
            "default_strategy": "auto",
            "auto_fallback": True,
            "max_file_size_mb": 100.0,
            "warn_large_file": True,
            "prefer_url": True,
            "strategy_order": [
                "url_direct",
                "base64_small",
                "base64_large"
            ]
        }
        return self.save_user_preferences(default_prefs)

    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置信息摘要

        Returns:
            Dict: 配置信息
        """
        try:
            api_key = self.get_api_key()
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "未配置"

            return {
                "mcp_config_path": str(self.mcp_config_path),
                "user_prefs_path": str(self.user_prefs_path),
                "api_key_masked": masked_key,
                "model_name": self.get_model_name(),
                "default_strategy": self.get_preference("default_strategy"),
                "auto_fallback": self.get_preference("auto_fallback"),
                "max_file_size_mb": self.get_preference("max_file_size_mb")
            }
        except Exception as e:
            return {"error": str(e)}


# 全局配置管理器实例
_global_config_manager = None


def get_config_manager() -> ConfigManager:
    """
    获取全局配置管理器实例（单例模式）

    Returns:
        ConfigManager: 配置管理器实例
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


if __name__ == "__main__":
    # 测试配置管理器
    logging.basicConfig(level=logging.INFO)

    manager = ConfigManager()

    print("\n=== 配置信息 ===")
    info = manager.get_config_info()
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\n=== 用户偏好 ===")
    prefs = manager.load_user_preferences()
    print(json.dumps(prefs, indent=2, ensure_ascii=False))
