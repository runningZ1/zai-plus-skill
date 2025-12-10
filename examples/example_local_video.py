#!/usr/bin/env python3
"""
示例: 分析本地视频文件
演示如何使用智能路由系统分析本地视频
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analyzers.smart_analyzer import SmartVideoAnalyzer


def main():
    """主函数"""
    # 创建智能分析器
    analyzer = SmartVideoAnalyzer()

    # 本地视频路径（请替换为实际路径）
    video_path = "D:\\Video\\sample_video.mp4"

    # 分析问题
    question = "请详细描述这个视频的内容"

    print("=" * 60)
    print("示例: 本地视频分析")
    print("=" * 60)
    print(f"\n视频路径: {video_path}")
    print(f"分析问题: {question}\n")

    # 系统会自动:
    # 1. 检测文件大小
    # 2. 选择最优策略 (小文件Base64 或 大文件Base64)
    # 3. 如果文件过大，会提示上传到云存储

    # 执行分析
    result = analyzer.analyze(
        video_path,
        question,
        show_plan=True,  # 显示执行计划
        auto_fallback=True  # 启用失败自动切换
    )

    if result:
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print("\n✅ 分析成功!")
            print(f"\n结果:\n{content}")

            # 显示Token统计
            if "usage" in result:
                usage = result["usage"]
                print(f"\n📊 Token统计:")
                print(f"  总Token: {usage.get('total_tokens', 0):,}")
                print(f"  输入Token: {usage.get('prompt_tokens', 0):,}")
                print(f"  输出Token: {usage.get('completion_tokens', 0):,}")
        elif "error" in result:
            print(f"\n❌ 分析失败: {result['error']}")

            # 显示建议
            if "recommendations" in result:
                print("\n💡 建议:")
                for rec in result["recommendations"]:
                    print(f"  {rec}")
    else:
        print("\n❌ 未返回结果")


if __name__ == "__main__":
    main()
