#!/usr/bin/env python3
"""
ZAI Plus Skill - 主入口脚本
统一的命令行接口
"""
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analyzers.smart_analyzer import SmartVideoAnalyzer
from src.utils.config_manager import get_config_manager
from tools.check_environment import EnvironmentChecker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def analyze_video(args):
    """视频分析命令"""
    analyzer = SmartVideoAnalyzer()
    result = analyzer.analyze(
        args.input,
        args.question,
        show_plan=not args.no_plan,
        auto_fallback=not args.no_fallback
    )

    if result and "error" not in result:
        return 0
    else:
        return 1


def check_env(args):
    """环境检查命令"""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    return 0 if success else 1


def config_command(args):
    """配置管理命令"""
    manager = get_config_manager()

    if args.action == "show":
        info = manager.get_config_info()
        print("\n=== 当前配置 ===")
        for key, value in info.items():
            print(f"{key}: {value}")

    elif args.action == "set-strategy":
        if not args.value:
            print("错误: 需要提供策略值")
            return 1

        valid_strategies = ["auto", "url_first", "base64_only"]
        if args.value not in valid_strategies:
            print(f"错误: 无效的策略。可选值: {', '.join(valid_strategies)}")
            return 1

        success = manager.set_preference("default_strategy", args.value)
        if success:
            print(f"✅ 默认策略已设置为: {args.value}")
            return 0
        else:
            print("❌ 设置失败")
            return 1

    elif args.action == "reset":
        success = manager.reset_preferences()
        if success:
            print("✅ 配置已重置为默认值")
            return 0
        else:
            print("❌ 重置失败")
            return 1

    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="ZAI Plus Skill - 智谱AI多模态分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析视频
  %(prog)s analyze "http://example.com/video.mp4"
  %(prog)s analyze "D:\\Video\\sample.mp4" -q "提取文案"

  # 环境检查
  %(prog)s check

  # 配置管理
  %(prog)s config show
  %(prog)s config set-strategy auto
  %(prog)s config reset

版本: 2.1.0
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析视频")
    analyze_parser.add_argument("input", help="视频URL或文件路径")
    analyze_parser.add_argument(
        "-q", "--question",
        default="请详细分析这个视频的内容，包括画面、声音、文案、主题等所有信息",
        help="分析问题"
    )
    analyze_parser.add_argument(
        "--no-plan",
        action="store_true",
        help="不显示执行计划"
    )
    analyze_parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="禁用失败自动切换"
    )
    analyze_parser.set_defaults(func=analyze_video)

    # check命令
    check_parser = subparsers.add_parser("check", help="检查运行环境")
    check_parser.set_defaults(func=check_env)

    # config命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument(
        "action",
        choices=["show", "set-strategy", "reset"],
        help="配置操作"
    )
    config_parser.add_argument(
        "value",
        nargs="?",
        help="配置值（仅用于set-strategy）"
    )
    config_parser.set_defaults(func=config_command)

    # version命令
    version_parser = subparsers.add_parser("version", help="显示版本信息")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print("ZAI Plus Skill v2.1.0")
        print("智谱AI多模态分析技能包")
        return 0

    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\n用户中断操作")
            return 130
        except Exception as e:
            logging.error(f"执行失败: {e}")
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
