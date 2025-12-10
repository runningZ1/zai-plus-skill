# Base64 视频处理演示

## 概述

本技能支持两种视频输入方式：
1. **video_url** - 在线视频URL
2. **video_base64** - Base64编码的视频数据

## 使用示例

### 1. 使用在线视频URL

```bash
python executor.py chat_completion '{
  "messages": [
    {
      "role": "user",
      "content": "请提取这个视频中的所有文案内容",
      "video_url": "https://example.com/video.mp4"
    }
  ],
  "model": "glm-4.6v"
}'
```

### 2. 使用Base64编码

#### 步骤1: 将视频转换为Base64

```python
import base64

# 读取视频文件
with open("your_video.mp4", "rb") as f:
    video_data = f.read()

# 转换为Base64
video_base64 = base64.b64encode(video_data).decode('utf-8')

# 保存到文件（可选）
with open("video_base64.txt", "w") as f:
    f.write(video_base64)
```

#### 步骤2: 使用Base64调用API

```bash
python executor.py chat_completion '{
  "messages": [
    {
      "role": "user",
      "content": "请提取视频中的文案内容",
      "video_base64": "YOUR_BASE64_DATA_HERE"
    }
  ],
  "model": "glm-4.6v"
}'
```

### 3. 完整工作流程示例

```python
import base64
import json

# 读取视频
with open("D:/Download/video.mp4", "rb") as f:
    video_data = f.read()

# 转换为Base64
video_base64 = base64.b64encode(video_data).decode('utf-8')

# 准备请求
request_data = {
    "messages": [
        {
            "role": "user",
            "content": "请提取视频中的所有文案内容，包括对话、字幕、标题等，按时间顺序整理",
            "video_base64": video_base64
        }
    ],
    "model": "glm-4.6v"
}

# 保存请求到文件
with open("request.json", "w") as f:
    json.dump(request_data, f)

# 运行
import subprocess
result = subprocess.run([
    "python", "executor.py", "chat_completion", 
    json.dumps(request_data)
], capture_output=True, text=True)

print(result.stdout)
```

## 注意事项

### Base64方案限制

1. **文件大小限制**: Base64会增加33%的数据大小，大文件可能超出API限制
2. **模型支持**: GLM-4.6V当前可能不支持直接的Base64视频输入
3. **传输限制**: 大量数据传输可能超时

### 推荐方案

1. **小文件 (< 1MB)**: 可尝试Base64
2. **大文件 (> 1MB)**: 建议上传到云存储并使用URL
3. **最佳实践**: 使用视频转文字工具提取字幕，再使用技能整理

## 实际测试结果

使用5.9MB本地视频测试：
- ✅ Base64转换成功 (813万字符)
- ✅ 执行器支持Base64输入
- ⚠️ GLM-4.6V暂不支持Base64视频直接处理
- 💡 建议使用文本描述 + 在线视频URL

## 替代方案

如果Base64方案不可用，建议：

1. **视频转文字**: 使用剪映、FFmpeg+Whisper等工具
2. **提取字幕**: 从视频平台获取或使用OCR
3. **在线处理**: 上传视频到支持AI分析的平台

