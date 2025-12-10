#!/usr/bin/env python3
"""
ZAI MCP Tool Executor - 增强版
支持视频URL和Base64格式的视频分析
"""
import json
import sys
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 配置常量
SCRIPT_TIMEOUT = 300  # 脚本执行超时时间（秒）


def load_mcp_config() -> Dict[str, Any]:
    """
    加载MCP配置文件

    Returns:
        Dict: 配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误或缺少必要字段
    """
    config_path = Path(__file__).parent / "mcp_config.json"

    try:
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证必要字段
        if "env" not in config:
            raise ValueError("配置文件缺少 'env' 字段")

        if "Z_AI_API_KEY" not in config.get("env", {}):
            raise ValueError("配置文件中未找到 Z_AI_API_KEY")

        logger.info("配置加载成功")
        return config

    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件JSON格式错误: {e}")
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        raise


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行指定的MCP工具

    Args:
        tool_name: 工具名称
        tool_input: 工具输入参数

    Returns:
        Dict: 执行结果
    """
    try:
        config = load_mcp_config()

        if tool_name == "chat_completion":
            return handle_chat_completion(tool_input, config)
        elif tool_name == "image_understanding":
            return handle_image_understanding(tool_input, config)
        elif tool_name == "text_generation":
            return handle_text_generation(tool_input, config)
        else:
            return {"error": f"不支持的工具: {tool_name}"}

    except Exception as e:
        logger.error(f"执行工具失败: {e}")
        return {"error": str(e)}


def handle_chat_completion(tool_input: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理聊天完成请求

    Args:
        tool_input: 工具输入参数
        config: 配置字典

    Returns:
        Dict: 执行结果
    """
    messages = tool_input.get("messages", [])
    api_key = config.get("env", {}).get("Z_AI_API_KEY", "")

    if not messages:
        return {"error": "缺少 messages 参数"}

    video_base64 = None
    video_url = None
    content = ""

    # 提取视频相关参数
    for msg in messages:
        if "video_base64" in msg:
            video_base64 = msg.pop("video_base64")
            content = msg.get("content", "请分析这个视频")
        elif "video_url" in msg:
            video_url = msg.pop("video_url")
            content = msg.get("content", "请分析这个视频")

    # 根据不同输入类型调用相应处理函数
    if video_base64:
        logger.info("使用Base64格式处理视频")
        return analyze_video_base64(video_base64, content, api_key)
    elif video_url:
        logger.info("使用URL格式处理视频")
        return analyze_video_url(video_url, content, api_key)
    else:
        # 普通文本聊天
        logger.info("处理普通文本聊天")
        return handle_text_chat(messages, tool_input.get("model", "glm-4"), api_key)


def handle_text_chat(messages: list, model: str, api_key: str) -> Dict[str, Any]:
    """
    处理普通文本聊天

    Args:
        messages: 消息列表
        model: 模型名称
        api_key: API密钥

    Returns:
        Dict: 执行结果
    """
    try:
        script_path = Path(__file__).parent / "temp_chat_script.js"

        # 转换消息格式
        messages_json = json.dumps(messages, ensure_ascii=False)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");

async function chat() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{api_key}"}});
    const messages = {messages_json};

    const result = await ai.createCompletions({{
      model: "{model}",
      messages: messages
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

chat();
''')

        # 执行脚本
        result = _execute_node_script(script_path)

        # 清理临时文件
        if script_path.exists():
            os.unlink(script_path)

        return result

    except Exception as e:
        logger.error(f"处理文本聊天失败: {e}")
        return {"error": str(e)}


def handle_image_understanding(tool_input: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理图像理解请求

    Args:
        tool_input: 工具输入参数
        config: 配置字典

    Returns:
        Dict: 执行结果
    """
    image_url = tool_input.get("image_url", "")
    question = tool_input.get("question", "请描述这张图片")
    api_key = config.get("env", {}).get("Z_AI_API_KEY", "")

    if not image_url:
        return {"error": "缺少 image_url 参数"}

    try:
        script_path = Path(__file__).parent / "temp_image_script.js"
        question_escaped = question.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        image_url_escaped = image_url.replace('\\', '\\\\').replace('"', '\\"')

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");

async function analyzeImage() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{api_key}"}});

    const result = await ai.createCompletions({{
      model: "glm-4.6v",
      messages: [{{
        role: "user",
        content: [
          {{
            type: "image_url",
            image_url: {{
              url: "{image_url_escaped}"
            }}
          }},
          {{
            type: "text",
            text: "{question_escaped}"
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

analyzeImage();
''')

        # 执行脚本
        result = _execute_node_script(script_path)

        # 清理临时文件
        if script_path.exists():
            os.unlink(script_path)

        return result

    except Exception as e:
        logger.error(f"处理图像理解失败: {e}")
        return {"error": str(e)}


def handle_text_generation(tool_input: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理文本生成请求

    Args:
        tool_input: 工具输入参数
        config: 配置字典

    Returns:
        Dict: 执行结果
    """
    prompt = tool_input.get("prompt", "")
    model = tool_input.get("model", "glm-4")
    api_key = config.get("env", {}).get("Z_AI_API_KEY", "")

    if not prompt:
        return {"error": "缺少 prompt 参数"}

    messages = [{"role": "user", "content": prompt}]
    return handle_text_chat(messages, model, api_key)


def analyze_video_base64(video_base64: str, content: str, api_key: str) -> Dict[str, Any]:
    """
    使用Base64编码的视频进行分析

    Args:
        video_base64: Base64编码的视频数据
        content: 分析问题
        api_key: API密钥

    Returns:
        Dict: 分析结果
    """
    try:
        script_path = Path(__file__).parent / "temp_base64_script.js"
        base64_file = Path(__file__).parent / "temp_video_base64.txt"

        # 保存Base64数据到文件
        with open(base64_file, 'w', encoding='utf-8') as f:
            f.write(video_base64)

        content_escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");
const fs = require('fs');

async function analyzeVideo() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{api_key}"}});
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
''')

        # 执行脚本
        result = _execute_node_script(script_path)

        # 清理临时文件
        for temp_file in [script_path, base64_file]:
            if temp_file.exists():
                os.unlink(temp_file)

        return result

    except Exception as e:
        logger.error(f"Base64视频分析失败: {e}")
        return {"error": str(e)}


def analyze_video_url(video_url: str, content: str, api_key: str) -> Dict[str, Any]:
    """
    使用视频URL进行分析

    Args:
        video_url: 视频URL
        content: 分析问题
        api_key: API密钥

    Returns:
        Dict: 分析结果
    """
    try:
        script_path = Path(__file__).parent / "temp_url_script.js"

        # 转义特殊字符
        content_escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        video_url_escaped = video_url.replace('\\', '\\\\').replace('"', '\\"')

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");

async function analyzeVideo() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{api_key}"}});

    const result = await ai.createCompletions({{
      model: "glm-4.6v",
      messages: [{{
        role: "user",
        content: [
          {{
            type: "video_url",
            video_url: {{
              url: "{video_url_escaped}"
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
''')

        # 执行脚本
        result = _execute_node_script(script_path)

        # 清理临时文件
        if script_path.exists():
            os.unlink(script_path)

        return result

    except Exception as e:
        logger.error(f"URL视频分析失败: {e}")
        return {"error": str(e)}


def _execute_node_script(script_path: Path) -> Dict[str, Any]:
    """
    执行Node.js脚本

    Args:
        script_path: 脚本文件路径

    Returns:
        Dict: 执行结果
    """
    original_cwd = os.getcwd()

    try:
        os.chdir(Path(__file__).parent)
        logger.info(f"执行脚本: {script_path.name}")

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
                logger.info("脚本执行成功")
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
        return {"error": f"脚本执行超时 (超过 {SCRIPT_TIMEOUT} 秒)"}

    except Exception as e:
        logger.error(f"执行脚本时出错: {e}")
        return {"error": str(e)}

    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: executor.py <tool_name> <tool_input_json>")
        print("\n支持的工具:")
        print("  - chat_completion: 聊天对话和视频分析")
        print("  - image_understanding: 图像理解")
        print("  - text_generation: 文本生成")
        print("\n示例:")
        print('  python executor.py chat_completion \'{"messages":[{"role":"user","content":"你好"}]}\'')
        sys.exit(1)

    tool_name, tool_input_json = sys.argv[1], sys.argv[2]

    try:
        tool_input = json.loads(tool_input_json)
        result = execute_tool(tool_name, tool_input)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except json.JSONDecodeError as e:
        logger.error(f"工具输入JSON格式错误: {e}")
        print(json.dumps({"error": f"JSON格式错误: {e}"}, ensure_ascii=False))
        sys.exit(1)

    except Exception as e:
        logger.error(f"执行失败: {e}")
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
