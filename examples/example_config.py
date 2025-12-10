#!/usr/bin/env python3
"""
示例: 自定义配置和策略
演示如何自定义配置和使用不同策略
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analyzers.smart_analyzer import SmartVideoAnalyzer
from src.utils.config_manager import get_config_manager


def main():
    """主函数"""
    # 获取配置管理器
    config_manager = get_config_manager()

    print("=" * 60)
    print("示例: 配置管理和策略选择")
    print("=" * 60)

    # 1. 查看当前配置
    print("\n1️⃣ 当前配置信息:")
    info = config_manager.get_config_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 2. 修改默认策略
    print("\n2️⃣ 设置默认策略为 'url_first':")
    success = config_manager.set_preference("default_strategy", "url_first")
    if success:
        print("  ✅ 设置成功")
    else:
        print("  ❌ 设置失败")

    # 3. 修改文件大小限制
    print("\n3️⃣ 设置最大文件大小为 50MB:")
    config_manager.set_preference("max_file_size_mb", 50.0)
    print("  ✅ 设置成功")

    # 4. 查看策略对比
    print("\n4️⃣ 查看策略对比:")
    analyzer = SmartVideoAnalyzer()
    analyzer.show_strategy_comparison()

    # 5. 重置配置
    print("\n5️⃣ 是否重置配置为默认值? (y/n)")
    choice = input("  > ")
    if choice.lower() == 'y':
        config_manager.reset_preferences()
        print("  ✅ 配置已重置")
    else:
        print("  ⏭️  跳过重置")

    print("\n" + "=" * 60)
    print("配置管理示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
