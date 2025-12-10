---
name: zai-mcp-server
description: 智谱AI MCP服务器，支持GLM-4.6V等多模态模型，支持视频、图像、文本处理. Use when you need to interact with zai-mcp-server MCP server tools including: chat_completion, image_understanding, text_generation.
---

# Zai-Mcp-Server Skill

This skill provides access to zai-mcp-server MCP server functionality with progressive disclosure for optimal performance.

## Available Tools

### chat_completion

与GLM模型进行对话交互，支持多模态输入（文本、图像、视频）

**Enhanced Input Schema (v2.0):**
```json
{
  "type": "object",
  "properties": {
    "messages": {
      "type": "array",
      "description": "对话消息列表",
      "items": {
        "type": "object",
        "properties": {
          "role": {
            "type": "string",
            "enum": ["user", "assistant", "system"]
          },
          "content": {
            "type": "string",
            "description": "消息内容"
          },
          "video_url": {
            "type": "string",
            "description": "视频URL（可选）"
          },
          "video_base64": {
            "type": "string",
            "description": "Base64编码的视频数据（可选）"
          }
        },
        "required": ["role", "content"]
      }
    },
    "model": {
      "type": "string",
      "default": "glm-4.6v",
      "description": "模型名称，支持glm-4.6v、glm-4.5v、glm-4等"
    },
    "temperature": {
      "type": "number",
      "default": 0.7
    },
    "max_tokens": {
      "type": "integer",
      "default": 2000
    }
  },
  "required": ["messages"]
}
```

**Video Input Options:**
- `video_url`: 在线视频URL（推荐）
- `video_base64`: Base64编码的视频数据
- 两者二选一，不能同时使用

### image_understanding

理解图像内容，支持多模态分析

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "image_url": {
      "type": "string",
      "description": "图像URL或base64编码"
    },
    "question": {
      "type": "string",
      "description": "关于图像的问题"
    }
  },
  "required": ["image_url", "question"]
}
```

### text_generation

纯文本生成任务

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "文本生成提示"
    },
    "model": {
      "type": "string",
      "default": "glm-4"
    },
    "temperature": {
      "type": "number",
      "default": 0.7
    },
    "max_tokens": {
      "type": "integer",
      "default": 2000
    }
  },
  "required": ["prompt"]
}
```

## Usage

This skill uses external execution via `executor.py` to run MCP tools outside Claude context.

### Tool Execution Pattern

1. User requests tool usage
2. Skill validates input parameters
3. `executor.py` executes MCP tool externally
4. Results returned to conversation

### Video Processing

#### Option 1: Online Video URL (Recommended)

```bash
python executor.py chat_completion '{
  "messages": [
    {
      "role": "user",
      "content": "请提取视频中的所有文案内容",
      "video_url": "https://example.com/video.mp4"
    }
  ],
  "model": "glm-4.6v"
}'
```

#### Option 2: Base64 Encoded Video

```python
import base64

# Convert video to Base64
with open("video.mp4", "rb") as f:
    video_base64 = base64.b64encode(f.read()).decode('utf-8')

# Use in request
{
  "messages": [
    {
      "role": "user",
      "content": "请分析这个视频",
      "video_base64": video_base64
    }
  ]
}
```

**Note:** Base64 support depends on model capabilities. GLM-4.6V may not support direct Base64 video input yet.

### Configuration

The skill requires:
- Python 3.8+
- Node.js and npm
- ZhipuAI SDK: `npm install zhipuai-sdk-nodejs-v4`
- MCP package: `pip install mcp`
- Proper MCP server configuration in `mcp_config.json`

### Example Workflows

#### Text Generation
```
User: "写一篇关于AI的文章"
Skill: Uses text_generation tool → Returns generated article
```

#### Image Analysis
```
User: "分析这张图片的内容"
Skill: Uses image_understanding tool → Returns analysis
```

#### Video Analysis (URL)
```
User: "提取这个视频的字幕"
Skill: Uses chat_completion with video_url → Returns transcript
```

## Progressive Disclosure

This skill implements progressive disclosure:
1. **Metadata** (~50 tokens): Tool names and basic info
2. **Tool schemas** (~2k tokens): Loaded when skill triggers
3. **Full MCP specs**: External execution, not loaded into context

## Error Handling

- Invalid tool parameters: Validation error
- MCP server issues: Connection error
- Execution failures: Runtime error with details
- Video processing: Detailed error messages for troubleshooting

## Security Notes

- Tool execution happens outside Claude context
- Input validation prevents injection attacks
- Sensitive data should use environment variables
- Base64 video data is processed in memory only
- Review executor.py for security implications

## Changelog

### v2.0 (2025-12-10)
- ✨ Added Base64 video input support
- 🔄 Updated to GLM-4.6V as default model
- 📝 Enhanced documentation with video processing examples
- 🛠️ Improved error handling and debugging

### v1.0
- Initial release
- Basic chat, image, and text generation support

