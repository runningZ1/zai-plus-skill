# 智能路由系统 - 快速开始指南

> ZAI Plus Skill v2.1 智能路由系统使用手册

## 🚀 快速开始

### 方式1: 使用智能分析工具（推荐）⭐

```bash
# 自动选择最优策略
python smart_analyze.py "<视频URL或文件路径>" "[可选: 分析问题]"
```

### 方式2: 传统方式

```bash
# 本地视频（仅支持Base64）
python analyze_local_video.py "<本地视频路径>" "[可选: 分析问题]"

# URL视频（手动调用executor）
python executor.py chat_completion '{"messages":[{"role":"user","content":"问题","video_url":"URL"}]}'
```

## 📊 三种输入方式对比

### 测试数据（基于实际运行结果）

| 输入方式 | 视频来源 | 文件大小 | 处理时间 | Token消耗 | 推荐度 |
|---------|---------|---------|---------|----------|--------|
| **在线URL** | http://... | 不限 | 26秒 | 38,983 | ⭐⭐⭐⭐⭐ |
| **小文件Base64** | 本地 < 5MB | 1.55 MB | 27秒 | 52,578 | ⭐⭐⭐⭐ |
| **大文件Base64** | 本地 5-100MB | 5.21 MB | 34秒 | 72,828 | ⭐⭐⭐ |

### 结论

- **URL方式最优**: Token节省约25-50%，速度最快
- **小文件可接受**: 适合隐私敏感场景
- **大文件需谨慎**: Token消耗高，建议先上传到云存储

## 🎯 典型使用场景

### 场景1: 分析在线视频（最推荐）

```bash
python smart_analyze.py "http://example.com/video.mp4" "提取视频文案"
```

**优势**:
- ✅ Token最省（约35K-45K）
- ✅ 速度最快（20-30秒）
- ✅ 无需文件操作
- ✅ 无临时文件

### 场景2: 分析本地小视频（隐私友好）

```bash
python smart_analyze.py "D:\Video\small_video.mp4"
```

**系统自动判断**:
- 检测文件大小: 1.55 MB
- 选择策略: BASE64_SMALL
- 预估Token: 40K-60K
- 预估时间: 25-35秒

### 场景3: 分析本地大视频（带警告）

```bash
python smart_analyze.py "D:\Video\large_video.mp4"
```

**系统行为**:
- 检测文件大小: 5.21 MB
- 选择策略: BASE64_LARGE
- ⚠️  警告: 文件较大，Token消耗会较高
- 💡 建议: 上传到云存储后使用URL方式

### 场景4: 超大文件（拒绝处理）

```bash
python smart_analyze.py "D:\Video\huge_video.mp4"
```

**系统行为**:
- 检测文件大小: 150 MB
- ❌ 拒绝处理
- 建议: 上传到云存储（七牛云/阿里云OSS/腾讯云COS）

## ⚙️ 用户偏好配置

### 查看当前配置

```bash
cat user_preferences.json
```

### 配置项说明

```json
{
  "default_strategy": "auto",        // 默认策略
  "auto_fallback": true,             // 失败自动切换
  "max_file_size_mb": 100.0,        // 最大文件大小
  "warn_large_file": true,          // 大文件警告
  "prefer_url": true,               // 优先URL方式
  "strategy_order": [               // 回退策略链
    "url_direct",
    "base64_small",
    "base64_large"
  ]
}
```

### 修改默认策略

```bash
# URL优先模式
python smart_analyze.py --set-strategy url_first

# Base64优先模式
python smart_analyze.py --set-strategy base64_only

# 自动模式（推荐）
python smart_analyze.py --set-strategy auto
```

## 🔄 失败自动切换机制

### 工作原理

```
主策略: URL_DIRECT
  ↓ (网络错误/URL无效)
备选策略1: BASE64_SMALL
  ↓ (文件过大)
备选策略2: BASE64_LARGE
  ↓ (仍然失败)
返回错误: 所有策略都失败
```

### 实际案例

```bash
# 假设URL暂时无法访问
python smart_analyze.py "http://temporary-down.com/video.mp4"

# 系统行为:
# 1. 尝试 URL_DIRECT → 失败（连接超时）
# 2. 🔄 自动切换到 BASE64_SMALL → 成功！
# 3. ✅ 返回分析结果
```

## 📈 性能优化建议

### 1. 优先使用URL方式

**推荐流程**:
```bash
# 1. 上传视频到云存储
# 2. 获取公开访问URL
# 3. 使用URL分析
python smart_analyze.py "https://your-cdn.com/video.mp4"
```

**收益**:
- Token节省: 30-50%
- 速度提升: 15-25%
- 无临时文件

### 2. 控制视频文件大小

**建议**:
- < 5MB: 直接Base64 ✅
- 5-20MB: 考虑压缩或URL方式 ⚠️
- > 20MB: 必须使用URL方式 ❌

### 3. 批量处理优化

```bash
# 批量处理多个URL（Token最优）
for url in url_list.txt; do
  python smart_analyze.py "$url" "分析问题" >> results.txt
done
```

## 🎨 输出格式

### 标准输出

```
============================================================
🚀 智能视频分析系统启动
============================================================

📊 步骤1: 分析输入并制定策略...

📹 输入类型: URL
✅ 选定策略: URL DIRECT

📋 执行计划:
  处理方法: analyze_video_url
  预估时间: 20-30秒
  预估Token: 35,000-45,000
  临时文件: 1 个

============================================================
📊 步骤2: 执行视频分析...
============================================================

============================================================
📊 分析结果
============================================================

### 核心内容
[分析结果...]

============================================================
📈 使用统计
============================================================
- 总Token数: 38,983
- 输入Token数: 38,477
- 输出Token数: 506
```

## 🆚 工具对比

| 工具 | 路由智能 | 自动切换 | 用户配置 | 推荐度 |
|------|---------|---------|---------|--------|
| **smart_analyze.py** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| analyze_local_video.py | ❌ | ❌ | ❌ | ⭐⭐⭐ |
| executor.py (直接调用) | ❌ | ❌ | ❌ | ⭐⭐ |

## 📚 常见问题

### Q1: 如何知道系统选择了哪种策略？

A: 系统会在输出中明确显示：
```
✅ 选定策略: URL DIRECT
```

### Q2: 可以强制使用Base64方式吗？

A: 可以，设置偏好为 `base64_only`:
```bash
python smart_analyze.py --set-strategy base64_only
```

### Q3: 失败切换会增加成本吗？

A: 不会。只有成功的策略才会消耗Token，失败的尝试不计费。

### Q4: URL方式为什么这么快？

A: 因为：
1. 无需读取文件（节省IO时间）
2. 无需Base64编码（节省CPU时间）
3. 传输的数据量更小（节省网络时间）
4. 无需保存临时文件（节省磁盘时间）

### Q5: 如何查看策略对比？

A:
```bash
python smart_analyze.py --compare
```

## 🎉 总结

**推荐使用流程**:

1. **首选**: 使用 `smart_analyze.py`（智能路由）
2. **URL优先**: 在线视频直接使用URL
3. **小文件可接受**: < 5MB本地视频可用Base64
4. **大文件先上传**: > 5MB建议上传到云存储

**关键收益**:
- 🧠 智能决策，无需手动判断
- 💰 Token节省最高50%
- ⚡ 处理速度提升25%
- 🛡️ 失败自动切换，稳定可靠

---

**版本**: v2.1
**更新日期**: 2025-12-11
**文档作者**: ZAI Plus Skill Team
