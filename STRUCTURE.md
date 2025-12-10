# ZAI Plus Skill - 项目结构说明

## 📁 标准 Skill 目录结构

```
zai-plus-skill/
├── SKILL.md                         # [必需] Skill 入口文件
│   ├── YAML frontmatter             # 元数据：name, description, allowed-tools
│   └── Markdown instructions        # 核心指令
│
├── [可选资源]
│   ├── scripts/                     # 可执行脚本 (Python/Bash)
│   │   ├── analyze_local_video.py   # 本地视频分析
│   │   ├── smart_analyze.py         # 智能分析（带路由）
│   │   ├── video_router.py          # 视频路由器
│   │   ├── zai_analyze.py           # 主入口脚本
│   │   └── executor.py              # MCP 执行器
│   │
│   ├── references/                  # 参考文档 (需时加载)
│   │   ├── COMPLETION_REPORT.md     # 项目完成报告
│   │   ├── DEMO_BASE64_USAGE.md     # Base64 使用演示
│   │   ├── PROJECT_STRUCTURE.md     # 项目结构详解
│   │   ├── QUICK_START_ROUTER.md    # 路由器快速开始
│   │   ├── README_IMPROVEMENTS.md   # README 改进说明
│   │   ├── REORGANIZATION_SUMMARY.md # 重组总结
│   │   └── analysis_result.txt      # 示例分析结果
│   │
│   └── assets/                      # 输出资源 (模板、图片等)
│
├── [项目特定目录]
│   ├── src/                         # 源代码模块
│   │   ├── analyzers/               # 分析器模块
│   │   ├── core/                    # 核心功能
│   │   └── utils/                   # 工具函数
│   │
│   ├── config/                      # 配置文件
│   │   ├── mcp_config.json          # MCP 服务器配置
│   │   └── user_preferences.json    # 用户偏好设置
│   │
│   ├── docs/                        # 用户文档
│   │   ├── BASE64_USAGE.md          # Base64 使用说明
│   │   └── QUICK_START.md           # 快速开始指南
│   │
│   ├── examples/                    # 示例代码
│   │   ├── example_config.py        # 配置管理示例
│   │   ├── example_local_video.py   # 本地视频示例
│   │   ├── example_url_analysis.py  # URL 分析示例
│   │   └── README.md                # 示例说明
│   │
│   └── tools/                       # 工具脚本
│       └── check_environment.py     # 环境检查工具
│
├── README.md                        # 项目说明文档
├── LICENSE                          # 开源许可证
├── requirements.txt                 # Python 依赖
└── .gitignore                       # Git 忽略规则
```

## 📊 目录功能说明

### 核心文件
- **SKILL.md**: Skill 的入口文件，包含元数据和核心指令

### 可选资源目录
- **scripts/**: 可执行的 Python/Bash 脚本
- **references/**: 参考文档，按需加载
- **assets/**: 静态资源（模板、图片等）

### 项目特定目录
- **src/**: 源代码模块
- **config/**: 配置文件
- **docs/**: 用户文档
- **examples/**: 示例代码
- **tools/**: 辅助工具

## 🔄 整理变更

### 移动的文件
1. **Python 脚本** → `scripts/`
   - analyze_local_video.py
   - smart_analyze.py
   - video_router.py
   - zai_analyze.py
   - executor.py

2. **参考文档** → `references/`
   - COMPLETION_REPORT.md
   - DEMO_BASE64_USAGE.md
   - PROJECT_STRUCTURE.md
   - QUICK_START_ROUTER.md
   - README_IMPROVEMENTS.md
   - REORGANIZATION_SUMMARY.md
   - analysis_result.txt

3. **工具脚本** → `tools/`
   - check_environment.py

### 删除的重复文件
- 根目录的 `mcp_config.json` (保留 `config/mcp_config.json`)
- 根目录的 `user_preferences.json` (保留 `config/user_preferences.json`)

## ✅ 结构优势

1. **清晰分层**: 核心文件、可选资源、项目特定目录分离
2. **易于维护**: 相同类型的文件集中管理
3. **符合标准**: 遵循 Claude Skill 规范
4. **扩展性强**: 便于添加新的脚本、文档和资源

---

**整理日期**: 2025-12-11
**版本**: 2.1.0
