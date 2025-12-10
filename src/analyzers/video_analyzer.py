#!/usr/bin/env python3
"""
本地视频分析工具 - 增强版
支持本地视频文件的智能分析，使用智谱AI GLM-4.6V模型
"""
import base64
import json
import sys
import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 配置常量
MAX_VIDEO_SIZE_MB = 100  # 最大视频文件大小（MB）
SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
SCRIPT_TIMEOUT = 600  # 脚本执行超时时间（秒）


class VideoAnalyzer:
    """视频分析器类"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化视频分析器

        Args:
            config_path: 配置文件路径，默认为当前目录下的 mcp_config.json
        """
        self.config_path = config_path or Path(__file__).parent / "mcp_config.json"
        self.api_key = None
        self.temp_files = []  # 跟踪临时文件以便清理

        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.api_key = config.get("env", {}).get("Z_AI_API_KEY", "")

            if not self.api_key:
                raise ValueError("配置文件中未找到 Z_AI_API_KEY")

            logger.info("配置加载成功")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            raise

    def _validate_video_file(self, video_path: str) -> Path:
        """
        验证视频文件

        Args:
            video_path: 视频文件路径

        Returns:
            Path: 验证后的路径对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或文件过大
        """
        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        if not video_file.is_file():
            raise ValueError(f"路径不是文件: {video_path}")

        # 检查文件扩展名
        if video_file.suffix.lower() not in SUPPORTED_FORMATS:
            logger.warning(f"文件格式 {video_file.suffix} 可能不被支持")

        # 检查文件大小
        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            raise ValueError(
                f"视频文件过大: {file_size_mb:.2f} MB (最大支持 {MAX_VIDEO_SIZE_MB} MB)"
            )

        logger.info(f"视频文件验证通过: {video_path} ({file_size_mb:.2f} MB)")
        return video_file

    def _encode_video_to_base64(self, video_path: Path) -> str:
        """
        将视频文件编码为Base64

        Args:
            video_path: 视频文件路径

        Returns:
            str: Base64编码的视频数据
        """
        try:
            logger.info("开始读取和编码视频文件...")
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')

            logger.info(f"Base64编码完成 (长度: {len(video_base64)} 字符)")
            return video_base64

        except Exception as e:
            logger.error(f"编码视频文件失败: {e}")
            raise

    def _create_analysis_script(self, content: str) -> Path:
        """
        创建临时分析脚本

        Args:
            content: 问题或分析需求

        Returns:
            Path: 脚本文件路径
        """
        script_path = Path(__file__).parent / "temp_video_analysis.js"
        self.temp_files.append(script_path)

        # 转义特殊字符
        content_escaped = (
            content.replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '')
        )

        script_content = f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");
const fs = require('fs');

async function analyzeVideo() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{self.api_key}"}});

    // 从文件读取Base64数据
    const videoBase64 = fs.readFileSync('temp_video_base64.txt', 'utf-8');

    const result = await ai.createCompletions({{
      model: "glm-4.6v",
      messages: [{{
        role: "user",
        content: [
          {{
            type: "video_url",
            video_url: {{
              url: `data:video/mp4;base64,${{videoBase64}}`
            }}
          }},
          {{
            type: "text",
            text: "{content_escaped}"
          }}
        ]
      }}]
    }});

    console.log(JSON.stringify(result));
  }} catch (error) {{
    console.log(JSON.stringify({{
      error: error.message,
      stack: error.stack,
      code: error.code || 'UNKNOWN'
    }}));
  }}
}}

analyzeVideo();
'''

        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.info(f"分析脚本创建成功: {script_path}")
            return script_path

        except Exception as e:
            logger.error(f"创建分析脚本失败: {e}")
            raise

    def _save_base64_data(self, video_base64: str) -> Path:
        """
        保存Base64数据到临时文件

        Args:
            video_base64: Base64编码的视频数据

        Returns:
            Path: 临时文件路径
        """
        base64_file = Path(__file__).parent / "temp_video_base64.txt"
        self.temp_files.append(base64_file)

        try:
            with open(base64_file, 'w', encoding='utf-8') as f:
                f.write(video_base64)
            logger.info(f"Base64数据已保存到临时文件: {base64_file}")
            return base64_file

        except Exception as e:
            logger.error(f"保存Base64数据失败: {e}")
            raise

    def _execute_analysis(self, script_path: Path) -> Dict[str, Any]:
        """
        执行分析脚本

        Args:
            script_path: 脚本文件路径

        Returns:
            Dict: 分析结果
        """
        original_cwd = os.getcwd()

        try:
            os.chdir(Path(__file__).parent)
            logger.info("正在调用AI分析视频...")

            result = subprocess.run(
                ['node', str(script_path)],
                capture_output=True,
                text=True,
                timeout=SCRIPT_TIMEOUT
            )

            os.chdir(original_cwd)

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    logger.info("AI分析完成")
                    return response
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败: {e}")
                    return {"result": result.stdout}
            else:
                error_msg = result.stderr or "未知错误"
                logger.error(f"脚本执行失败: {error_msg}")
                return {"error": error_msg}

        except subprocess.TimeoutExpired:
            logger.error(f"脚本执行超时 (超过 {SCRIPT_TIMEOUT} 秒)")
            return {"error": f"分析超时 (超过 {SCRIPT_TIMEOUT} 秒)"}

        except Exception as e:
            logger.error(f"执行分析脚本时出错: {e}")
            return {"error": str(e)}

        finally:
            os.chdir(original_cwd)

    def _cleanup(self) -> None:
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    os.unlink(temp_file)
                    logger.debug(f"已删除临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"清理临时文件失败 {temp_file}: {e}")

        self.temp_files.clear()

    def analyze(
        self,
        video_path: str,
        question: str = "请详细分析这个视频的内容，包括画面、声音、文案、主题等所有信息"
    ) -> Optional[Dict[str, Any]]:
        """
        分析本地视频文件

        Args:
            video_path: 视频文件路径
            question: 分析问题或需求

        Returns:
            Dict: 分析结果，失败时返回None
        """
        try:
            # 1. 验证视频文件
            video_file = self._validate_video_file(video_path)

            # 2. 编码为Base64
            video_base64 = self._encode_video_to_base64(video_file)

            # 3. 保存Base64数据
            self._save_base64_data(video_base64)

            # 4. 创建分析脚本
            script_path = self._create_analysis_script(question)

            # 5. 执行分析
            result = self._execute_analysis(script_path)

            return result

        except Exception as e:
            logger.error(f"分析视频失败: {e}")
            return {"error": str(e)}

        finally:
            # 6. 清理临时文件
            self._cleanup()


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化分析结果

    Args:
        result: 分析结果字典

    Returns:
        str: 格式化后的文本
    """
    if "error" in result:
        return f"❌ 分析失败: {result['error']}"

    try:
        # 提取主要内容
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            reasoning = message.get("reasoning_content", "")

            output = ["=" * 60, "📊 分析结果", "=" * 60, ""]

            if reasoning:
                output.extend(["### 分析推理过程", reasoning, ""])

            if content:
                output.extend(["### 核心内容", content, ""])

            # 添加使用统计
            if "usage" in result:
                usage = result["usage"]
                output.extend([
                    "",
                    "=" * 60,
                    "📈 使用统计",
                    "=" * 60,
                    f"- 总Token数: {usage.get('total_tokens', 0)}",
                    f"- 输入Token数: {usage.get('prompt_tokens', 0)}",
                    f"- 输出Token数: {usage.get('completion_tokens', 0)}",
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
        print("用法: python analyze_local_video.py <视频路径> [问题]")
        print("\n示例:")
        print('  python analyze_local_video.py video.mp4')
        print('  python analyze_local_video.py video.mp4 "提取视频中的所有文案"')
        sys.exit(1)

    video_path = sys.argv[1]
    question = (
        sys.argv[2] if len(sys.argv) > 2
        else "请详细分析这个视频的内容，包括画面、声音、文案、主题等所有信息"
    )

    try:
        analyzer = VideoAnalyzer()
        result = analyzer.analyze(video_path, question)

        if result:
            print("\n" + format_result(result))
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
