#!/usr/bin/env python3
"""
智能视频分析工具 - 集成路由器
自动选择最优处理策略，支持失败自动切换
"""
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from video_router import VideoRouter, ProcessStrategy
from analyze_local_video import VideoAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SmartVideoAnalyzer:
    """智能视频分析器 - 集成路由和自动切换"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化智能分析器

        Args:
            config_path: 配置文件路径
        """
        self.router = VideoRouter(config_path)
        self.analyzer = VideoAnalyzer(config_path)
        self.executor_path = Path(__file__).parent / "executor.py"

    def analyze(
        self,
        video_input: str,
        question: str = "请详细分析这个视频的内容，包括画面、声音、文案、主题等所有信息",
        show_plan: bool = True,
        auto_fallback: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        智能分析视频

        Args:
            video_input: 视频输入（URL或文件路径）
            question: 分析问题
            show_plan: 是否显示执行计划
            auto_fallback: 失败时自动切换策略

        Returns:
            Dict: 分析结果
        """
        logger.info("="*60)
        logger.info("🚀 智能视频分析系统启动")
        logger.info("="*60)

        # 步骤1: 路由决策
        logger.info("\n📊 步骤1: 分析输入并制定策略...")
        decision = self.router.route(video_input, question)

        # 显示分析结果
        analysis = decision['input_analysis']
        print(f"\n📹 输入类型: {analysis['type'].upper()}")

        if analysis['type'] == 'file' and analysis['file_size_mb']:
            print(f"📦 文件大小: {analysis['file_size_mb']} MB")

        if not analysis['valid']:
            print(f"\n❌ 输入无效: {analysis['error']}")
            return {"error": analysis['error']}

        # 显示策略
        strategy = decision['strategy']
        print(f"\n✅ 选定策略: {strategy.value.upper().replace('_', ' ')}")

        # 显示警告
        if decision['warnings']:
            print("\n⚠️  警告信息:")
            for warning in decision['warnings']:
                print(f"  {warning}")

        # 显示推荐
        if decision['recommendations']:
            print("\n💡 建议:")
            for rec in decision['recommendations']:
                print(f"  {rec}")

        # 如果推荐上传，直接返回
        if strategy == ProcessStrategy.UPLOAD_RECOMMEND:
            return {
                "error": "文件过大，请先上传到云存储",
                "recommendations": decision['recommendations']
            }

        # 显示执行计划
        if show_plan and decision['execution_plan']:
            plan = decision['execution_plan']
            print(f"\n📋 执行计划:")
            print(f"  处理方法: {plan['method']}")
            print(f"  预估时间: {plan['estimated_time']}")
            print(f"  预估Token: {plan['estimated_tokens']}")
            print(f"  临时文件: {plan['temp_files']} 个")

        # 步骤2: 执行分析
        print("\n" + "="*60)
        logger.info("📊 步骤2: 执行视频分析...")
        print("="*60 + "\n")

        result = None
        tried_strategies = []

        # 尝试执行主策略
        try:
            result = self._execute_strategy(video_input, question, strategy)
            tried_strategies.append(strategy.value)

            # 检查结果是否有错误
            if result and "error" in result:
                raise Exception(result["error"])

        except Exception as e:
            logger.error(f"❌ 策略 {strategy.value} 执行失败: {e}")

            # 自动切换策略
            if auto_fallback and self.router.preferences.get("auto_fallback", True):
                result = self._try_fallback_strategies(
                    video_input,
                    question,
                    strategy,
                    tried_strategies
                )
            else:
                return {"error": str(e), "tried_strategies": tried_strategies}

        return result

    def _execute_strategy(
        self,
        video_input: str,
        question: str,
        strategy: ProcessStrategy
    ) -> Optional[Dict[str, Any]]:
        """
        执行指定策略

        Args:
            video_input: 视频输入
            question: 分析问题
            strategy: 处理策略

        Returns:
            Dict: 分析结果
        """
        logger.info(f"正在使用策略: {strategy.value}")

        if strategy == ProcessStrategy.URL_DIRECT:
            return self._analyze_url(video_input, question)

        elif strategy in [ProcessStrategy.BASE64_SMALL, ProcessStrategy.BASE64_LARGE]:
            return self.analyzer.analyze(video_input, question)

        else:
            raise ValueError(f"不支持的策略: {strategy}")

    def _analyze_url(self, video_url: str, question: str) -> Dict[str, Any]:
        """
        使用URL方式分析

        Args:
            video_url: 视频URL
            question: 分析问题

        Returns:
            Dict: 分析结果
        """
        try:
            # 构建命令参数
            tool_input = {
                "messages": [{
                    "role": "user",
                    "content": question,
                    "video_url": video_url
                }],
                "model": "glm-4.6v"
            }

            tool_input_json = json.dumps(tool_input, ensure_ascii=False)

            # 执行executor.py
            result = subprocess.run(
                [sys.executable, str(self.executor_path), "chat_completion", tool_input_json],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.executor_path.parent
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                error_msg = result.stderr or "未知错误"
                return {"error": error_msg}

        except subprocess.TimeoutExpired:
            return {"error": "分析超时"}
        except Exception as e:
            return {"error": str(e)}

    def _try_fallback_strategies(
        self,
        video_input: str,
        question: str,
        failed_strategy: ProcessStrategy,
        tried_strategies: list
    ) -> Optional[Dict[str, Any]]:
        """
        尝试回退策略

        Args:
            video_input: 视频输入
            question: 分析问题
            failed_strategy: 失败的策略
            tried_strategies: 已尝试的策略列表

        Returns:
            Dict: 分析结果
        """
        print(f"\n🔄 主策略失败，尝试回退方案...")

        # 定义回退策略链
        fallback_chain = {
            ProcessStrategy.URL_DIRECT: [],  # URL失败无回退
            ProcessStrategy.BASE64_SMALL: [],
            ProcessStrategy.BASE64_LARGE: [ProcessStrategy.BASE64_SMALL]
        }

        fallback_strategies = fallback_chain.get(failed_strategy, [])

        for fallback in fallback_strategies:
            if fallback.value in tried_strategies:
                continue

            print(f"\n🔄 尝试备选策略: {fallback.value.upper().replace('_', ' ')}")
            tried_strategies.append(fallback.value)

            try:
                result = self._execute_strategy(video_input, question, fallback)

                if result and "error" not in result:
                    print(f"✅ 备选策略执行成功！")
                    return result
                else:
                    print(f"❌ 备选策略也失败了: {result.get('error', '未知错误')}")

            except Exception as e:
                logger.error(f"备选策略 {fallback.value} 执行失败: {e}")
                continue

        # 所有策略都失败
        return {
            "error": "所有策略都失败了",
            "tried_strategies": tried_strategies
        }

    def set_default_strategy(self, strategy: str) -> bool:
        """
        设置默认策略

        Args:
            strategy: 策略名称

        Returns:
            bool: 是否设置成功
        """
        return self.router.set_default_strategy(strategy)

    def show_strategy_comparison(self) -> None:
        """显示策略对比"""
        print(self.router.get_strategy_comparison())


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化分析结果

    Args:
        result: 分析结果字典

    Returns:
        str: 格式化后的文本
    """
    if "error" in result:
        output = [f"\n❌ 分析失败: {result['error']}"]

        if "tried_strategies" in result:
            output.append(f"\n已尝试的策略: {', '.join(result['tried_strategies'])}")

        if "recommendations" in result:
            output.append("\n💡 建议:")
            for rec in result["recommendations"]:
                output.append(f"  {rec}")

        return "\n".join(output)

    try:
        # 提取主要内容
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            reasoning = message.get("reasoning_content", "")

            output = ["\n" + "="*60, "📊 分析结果", "="*60, ""]

            if reasoning:
                output.extend(["### 分析推理过程", reasoning, ""])

            if content:
                output.extend(["### 核心内容", content, ""])

            # 添加使用统计
            if "usage" in result:
                usage = result["usage"]
                output.extend([
                    "",
                    "="*60,
                    "📈 使用统计",
                    "="*60,
                    f"- 总Token数: {usage.get('total_tokens', 0):,}",
                    f"- 输入Token数: {usage.get('prompt_tokens', 0):,}",
                    f"- 输出Token数: {usage.get('completion_tokens', 0):,}",
                ])

            return "\n".join(output)
        else:
            return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.warning(f"格式化结果失败: {e}")
        return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║           智能视频分析工具 v2.0                              ║
╠══════════════════════════════════════════════════════════════╣
║ 功能: 自动选择最优处理策略，支持失败自动切换                ║
╚══════════════════════════════════════════════════════════════╝

用法:
  python smart_analyze.py <视频URL或文件路径> [问题] [选项]

示例:
  # 分析在线视频
  python smart_analyze.py "http://example.com/video.mp4"

  # 分析本地视频
  python smart_analyze.py "D:\\Video\\sample.mp4" "提取视频文案"

  # 查看策略对比
  python smart_analyze.py --compare

  # 设置默认策略
  python smart_analyze.py --set-strategy url_first

支持的策略:
  - auto          自动选择（默认，推荐）
  - url_first     优先URL方式
  - base64_only   仅使用Base64方式
""")
        sys.exit(1)

    # 处理特殊命令
    if sys.argv[1] == "--compare":
        analyzer = SmartVideoAnalyzer()
        analyzer.show_strategy_comparison()
        sys.exit(0)

    if sys.argv[1] == "--set-strategy" and len(sys.argv) >= 3:
        strategy = sys.argv[2]
        analyzer = SmartVideoAnalyzer()
        success = analyzer.set_default_strategy(strategy)
        if success:
            print(f"✅ 默认策略已设置为: {strategy}")
        else:
            print(f"❌ 设置失败，请检查策略名称")
        sys.exit(0 if success else 1)

    # 常规分析
    video_input = sys.argv[1]
    question = (
        sys.argv[2] if len(sys.argv) > 2
        else "请详细分析这个视频的内容，包括画面、声音、文案、主题等所有信息"
    )

    try:
        analyzer = SmartVideoAnalyzer()
        result = analyzer.analyze(video_input, question)

        if result:
            print(format_result(result))
        else:
            print("❌ 分析失败: 未返回结果")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n用户中断操作")
        sys.exit(130)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
