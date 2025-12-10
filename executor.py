#!/usr/bin/env python3
"""
ZAI MCP Tool Executor with Base64 Support
"""
import json, sys, os, subprocess, tempfile
from pathlib import Path

def load_mcp_config():
    config_path = Path(__file__).parent / "mcp_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def execute_tool(tool_name, tool_input):
    config = load_mcp_config()
    if tool_name == "chat_completion":
        return handle_chat_completion(tool_input, config)
    return {"error": "Only chat_completion supported"}

def handle_chat_completion(tool_input, config):
    messages = tool_input.get("messages", [])
    api_key = config.get("env", {}).get("Z_AI_API_KEY", "")
    
    video_base64 = None
    video_url = None
    content = ""
    
    for msg in messages:
        if "video_base64" in msg:
            video_base64 = msg.pop("video_base64")
            content = msg.get("content", "请分析这个视频")
        elif "video_url" in msg:
            video_url = msg.pop("video_url")
            content = msg.get("content", "请分析这个视频")
    
    if video_base64:
        return analyze_video_base64(video_base64, content, api_key)
    elif video_url:
        return analyze_video_url(video_url, content, api_key)
    else:
        return {"error": "需要提供 video_base64 或 video_url"}

def analyze_video_base64(video_base64, content, api_key):
    """使用Base64编码的视频进行分析"""
    try:
        # 创建JS脚本
        script_path = Path(__file__).parent / "temp_base64_script.js"
        with open(script_path, 'w') as f:
            f.write(f'''
const {{ZhipuAI}} = require("zhipuai-sdk-nodejs-v4");

async function analyzeVideo() {{
  try {{
    const ai = new ZhipuAI({{apiKey: "{api_key}"}});
    const videoData = "{video_base64}";
    
    const result = await ai.createCompletions({{
      model: "glm-4.6v",
      messages: [{{
        role: "user", 
        content: "{content}"
      }}],
      stream: false
    }});
    
    console.log(JSON.stringify(result));
  }} catch (error) {{
    console.log(JSON.stringify({{error: error.message}}));
  }}
}}
analyzeVideo();
''')
        
        # 运行脚本
        original_cwd = os.getcwd()
        os.chdir(Path(__file__).parent)
        
        result = subprocess.run(['node', script_path], capture_output=True, text=True, timeout=300)
        
        os.chdir(original_cwd)
        os.unlink(script_path)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                return response
            except json.JSONDecodeError:
                return {"result": result.stdout}
        else:
            return {"error": result.stderr}
            
    except Exception as e:
        return {"error": f"处理失败: {str(e)}"}

def analyze_video_url(video_url, content, api_key):
    """使用视频URL进行分析 - 使用GLM-4.6V官方视频分析格式"""
    try:
        script_path = Path(__file__).parent / "temp_url_script.js"
        # 转义特殊字符防止JavaScript语法错误
        content_escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
        video_url_escaped = video_url.replace('\\', '\\\\').replace('"', '\\"')

        with open(script_path, 'w') as f:
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
    console.log(JSON.stringify({{error: error.message}}));
  }}
}}
analyzeVideo();
''')
        
        original_cwd = os.getcwd()
        os.chdir(Path(__file__).parent)
        
        result = subprocess.run(['node', script_path], capture_output=True, text=True, timeout=300)
        
        os.chdir(original_cwd)
        os.unlink(script_path)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                return response
            except json.JSONDecodeError:
                return {"result": result.stdout}
        else:
            return {"error": result.stderr}
            
    except Exception as e:
        return {"error": f"处理失败: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: executor_base64.py <tool_name> <tool_input_json>")
        sys.exit(1)
    
    tool_name, tool_input_json = sys.argv[1], sys.argv[2]
    tool_input = json.loads(tool_input_json)
    result = execute_tool(tool_name, tool_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
