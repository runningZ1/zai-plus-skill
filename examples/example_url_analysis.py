#!/usr/bin/env python3
"""
示例: 使用URL分析在线视频
演示如何使用智能路由系统分析在线视频
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

    # 在线视频URL
    video_url = "http://t71hb29vr.hn-bkt.clouddn.com/videos/20250403-%E7%A9%BA%E9%97%B2%E6%97%B6%E9%97%B4%E9%80%82%E5%90%88%E6%8A%A5%E8%80%83%E7%9A%84%E8%AF%81%E4%B9%A6-%E5%B9%B2%E8%B4%A7%E5%88%86%E4%BA%AB-%E7%A7%91.mp4"

    # 分析问题
    question = "用一句话概括这个视频的主要内容"

    print("=" * 60)
    print("示例: URL视频分析")
    print("=" * 60)
    print(f"\n视频URL: {video_url[:80]}...")
    print(f"分析问题: {question}\n")

    # 执行分析
    result = analyzer.analyze(
        video_url,
        question,
        show_plan=True,  # 显示执行计划
        auto_fallback=True  # 启用失败自动切换
    )

    if result:
        # 提取核心内容
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print("\n✅ 分析成功!")
            print(f"\n结果:\n{content}")
        elif "error" in result:
            print(f"\n❌ 分析失败: {result['error']}")
    else:
        print("\n❌ 未返回结果")


if __name__ == "__main__":
    main()
