# Examples / 示例代码

本目录包含ZAI Plus Skill的使用示例代码。

## 📝 示例列表

### 1. URL视频分析示例
**文件**: `example_url_analysis.py`

演示如何使用智能路由系统分析在线视频。

**运行方式**:
```bash
python examples/example_url_analysis.py
```

**特点**:
- ✅ Token消耗最低（约35K-45K）
- ✅ 速度最快（20-30秒）
- ✅ 推荐用于在线视频分析

---

### 2. 本地视频分析示例
**文件**: `example_local_video.py`

演示如何分析本地视频文件，系统会自动根据文件大小选择最优策略。

**运行方式**:
```bash
python examples/example_local_video.py
```

**特点**:
- 自动检测文件大小
- 智能选择处理策略
- 显示Token统计信息
- 提供优化建议

---

### 3. 配置管理示例
**文件**: `example_config.py`

演示如何管理用户配置和自定义处理策略。

**运行方式**:
```bash
python examples/example_config.py
```

**功能**:
- 查看当前配置
- 修改默认策略
- 调整文件大小限制
- 重置配置

---

## 🎯 使用建议

### 初学者
1. 先运行 `example_url_analysis.py` 了解基本用法
2. 尝试 `example_local_video.py` 体验本地文件处理
3. 使用 `example_config.py` 学习配置管理

### 进阶用户
- 修改示例代码，适配你的业务场景
- 参考示例代码编写自己的应用
- 结合配置管理实现个性化需求

## 📚 更多资源

- [快速开始指南](../docs/QUICK_START.md)
- [项目结构说明](../PROJECT_STRUCTURE.md)
- [完整文档](../README.md)

---

**提示**: 运行示例前，请确保已完成环境配置：
```bash
python tools/check_environment.py
```
