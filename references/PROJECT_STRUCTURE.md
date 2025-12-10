# ZAI Plus Skill - 项目结构说明

> v2.1 标准化项目结构文档

## 📁 目录结构

```
zai-plus-skill/
├── 📂 src/                          # 源代码目录
│   ├── __init__.py                  # 包初始化文件
│   ├── 📂 core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── executor.py              # MCP工具执行器
│   │   └── router.py                # 智能路由器
│   ├── 📂 analyzers/                # 分析器模块
│   │   ├── __init__.py
│   │   ├── video_analyzer.py        # 视频分析器（Base64方式）
│   │   └── smart_analyzer.py        # 智能分析器（集成路由）
│   └── 📂 utils/                    # 工具模块
│       ├── __init__.py
│       └── config_manager.py        # 配置管理器
├── 📂 config/                       # 配置文件目录
│   ├── mcp_config.json              # MCP服务器配置
│   └── user_preferences.json        # 用户偏好配置
├── 📂 docs/                         # 文档目录
│   ├── QUICK_START.md               # 快速开始指南
│   └── BASE64_USAGE.md              # Base64使用说明
├── 📂 examples/                     # 示例代码目录
│   ├── example_url_analysis.py      # URL视频分析示例
│   ├── example_local_video.py       # 本地视频分析示例
│   └── example_config.py            # 配置管理示例
├── 📂 tools/                        # 工具脚本目录
│   └── check_environment.py         # 环境检查工具
├── 📂 tests/                        # 测试目录（待完善）
│   └── (测试文件)
├── 📂 __pycache__/                  # Python缓存（git忽略）
├── 📄 zai_analyze.py                # 🌟 项目主入口脚本
├── 📄 README.md                     # 项目说明文档
├── 📄 SKILL.md                      # Claude技能定义
├── 📄 requirements.txt              # Python依赖列表
├── 📄 .gitignore                    # Git忽略规则
└── 📄 LICENSE                       # 开源许可证
```

## 📦 模块说明

### 1. src/core/ - 核心功能模块

**executor.py**
- MCP工具执行器
- 负责调用智谱AI API
- 处理不同类型的请求（文本、图像、视频）
- 生成和执行临时Node.js脚本

**router.py**
- 智能路由器
- 自动识别输入类型（URL/文件）
- 选择最优处理策略
- 提供策略对比和建议

### 2. src/analyzers/ - 分析器模块

**video_analyzer.py**
- 传统视频分析器
- 仅支持Base64方式
- 适合本地文件处理

**smart_analyzer.py**
- 智能视频分析器（推荐使用）
- 集成智能路由系统
- 支持URL和Base64两种方式
- 失败自动切换机制

### 3. src/utils/ - 工具模块

**config_manager.py**
- 统一配置管理
- 加载/保存MCP配置
- 管理用户偏好设置
- 提供配置信息查询

### 4. config/ - 配置目录

**mcp_config.json**
```json
{
  "name": "zai-mcp-server",
  "env": {
    "Z_AI_API_KEY": "your-api-key",
    "Z_AI_MODE": "glm-4.6v"
  },
  "tools": [...]
}
```

**user_preferences.json**
```json
{
  "default_strategy": "auto",
  "auto_fallback": true,
  "max_file_size_mb": 100.0,
  "prefer_url": true
}
```

### 5. examples/ - 示例目录

提供三个完整的使用示例：
- URL视频分析
- 本地视频分析
- 配置管理

### 6. tools/ - 工具脚本目录

**check_environment.py**
- 环境检查工具
- 验证Python/Node.js版本
- 检查npm包安装
- 验证配置文件

## 🚀 使用方式

### 方式1: 使用主入口脚本（推荐）

```bash
# 分析视频
python zai_analyze.py analyze "http://example.com/video.mp4"

# 环境检查
python zai_analyze.py check

# 配置管理
python zai_analyze.py config show
python zai_analyze.py config set-strategy auto
```

### 方式2: 作为Python包导入

```python
from src.analyzers.smart_analyzer import SmartVideoAnalyzer
from src.utils.config_manager import get_config_manager

# 创建分析器
analyzer = SmartVideoAnalyzer()
result = analyzer.analyze("video.mp4", "分析问题")

# 获取配置
config = get_config_manager()
api_key = config.get_api_key()
```

### 方式3: 运行示例代码

```bash
# URL分析示例
python examples/example_url_analysis.py

# 本地视频分析示例
python examples/example_local_video.py

# 配置管理示例
python examples/example_config.py
```

## 📋 文件迁移对照表

| 旧文件位置 | 新文件位置 | 说明 |
|-----------|-----------|------|
| executor.py | src/core/executor.py | 核心执行器 |
| video_router.py | src/core/router.py | 智能路由器 |
| analyze_local_video.py | src/analyzers/video_analyzer.py | 视频分析器 |
| smart_analyze.py | src/analyzers/smart_analyzer.py | 智能分析器 |
| check_environment.py | tools/check_environment.py | 环境检查工具 |
| mcp_config.json | config/mcp_config.json | MCP配置 |
| user_preferences.json | config/user_preferences.json | 用户配置 |
| QUICK_START_ROUTER.md | docs/QUICK_START.md | 快速开始 |
| DEMO_BASE64_USAGE.md | docs/BASE64_USAGE.md | Base64说明 |
| (新增) | zai_analyze.py | 主入口脚本 |
| (新增) | src/utils/config_manager.py | 配置管理器 |
| (新增) | examples/*.py | 示例代码 |

## 🔄 向后兼容性

为了保证向后兼容，根目录保留了以下文件：
- executor.py
- video_router.py
- analyze_local_video.py
- smart_analyze.py
- check_environment.py
- mcp_config.json
- user_preferences.json

**建议**: 新代码使用新的目录结构，旧代码逐步迁移。

## 🛠️ 开发指南

### 添加新功能

1. 在适当的模块目录创建新文件
2. 更新对应的`__init__.py`
3. 在`examples/`添加使用示例
4. 更新文档

### 添加新配置项

1. 在`config/user_preferences.json`添加默认值
2. 在`src/utils/config_manager.py`添加getter/setter
3. 更新文档说明

### 运行测试

```bash
# 环境检查
python tools/check_environment.py

# 运行示例
python examples/example_url_analysis.py
```

## 📝 最佳实践

1. **导入规范**
```python
# 推荐：使用绝对导入
from src.core.router import VideoRouter

# 不推荐：使用相对导入（可能出错）
from ..core.router import VideoRouter
```

2. **配置管理**
```python
# 推荐：使用配置管理器
from src.utils.config_manager import get_config_manager
config = get_config_manager()

# 不推荐：直接读取配置文件
with open("config/mcp_config.json") as f:
    config = json.load(f)
```

3. **错误处理**
```python
# 总是捕获和记录异常
try:
    result = analyzer.analyze(video)
except Exception as e:
    logger.error(f"分析失败: {e}")
    raise
```

## 🎯 下一步计划

- [ ] 完善单元测试
- [ ] 添加CI/CD配置
- [ ] 创建Docker镜像
- [ ] 添加更多示例
- [ ] 性能优化和基准测试

## 📮 问题反馈

如有问题或建议，请通过以下方式反馈：
- GitHub Issues
- Email: support@example.com

---

**版本**: v2.1.0
**更新日期**: 2025-12-11
**维护者**: ZAI Plus Skill Team
