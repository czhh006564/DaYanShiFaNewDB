# 贡献指南 Contributing Guide

欢迎为大衍筮法项目做出贡献！我们感谢所有形式的贡献，包括代码、文档、建议和错误报告。

## 🤝 贡献方式

### 1. 报告问题
- 使用 [GitHub Issues](../../issues) 报告bug或提出功能请求
- 提供详细的描述和重现步骤
- 包含相关的错误信息和环境信息

### 2. 提交代码
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 3. 改进文档
- 修正错误或改进现有文档
- 添加缺失的文档
- 翻译文档到其他语言

## 📋 开发规范

### 代码标准
- 遵循 PEP 8 Python 代码规范
- 使用类型注解提高代码可读性
- 添加适当的注释和文档字符串
- 保持函数和类的单一职责

### 测试要求
- 为新功能编写单元测试
- 确保所有测试通过
- 保持测试覆盖率在80%以上
- 运行 `python -m pytest test_comprehensive.py` 验证

### 提交信息格式
```
type(scope): description

[optional body]

[optional footer]
```

类型 (type):
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

示例:
```
feat(divination): 添加历史记录功能

- 实现占卜历史保存
- 添加历史记录查询API
- 支持数据导出功能

Closes #123
```

## 🚀 开发环境设置

### 必需工具
- Python 3.8+
- Git
- 现代浏览器（用于Web版本测试）

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/your-username/qoderProj.git
cd qoderProj

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest test_comprehensive.py

# 启动开发服务器
python webserver_v2.py
```

### 代码检查
```bash
# 代码格式化
black .

# 代码检查
flake8 .

# 类型检查
mypy *.py --ignore-missing-imports
```

## 🧪 测试指南

### 运行测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest test_comprehensive.py -v

# 运行覆盖率测试
python -m pytest --cov=. --cov-report=html
```

### 测试分类
- **单元测试**: 测试单个函数和方法
- **集成测试**: 测试模块间的交互
- **功能测试**: 测试完整的用户场景
- **性能测试**: 测试系统性能和响应时间

## 📝 文档贡献

### 文档类型
- **API文档**: 接口说明和示例
- **用户指南**: 使用说明和教程
- **开发文档**: 架构设计和开发指南
- **部署文档**: 安装和部署说明

### 文档格式
- 使用 Markdown 格式
- 包含清晰的标题和结构
- 提供代码示例和截图
- 支持中英文双语

## 🔄 Pull Request 流程

1. **准备工作**
   - 确保与主分支同步
   - 运行所有测试并通过
   - 更新相关文档

2. **创建 PR**
   - 使用清晰的标题和描述
   - 引用相关的 Issue
   - 添加适当的标签

3. **代码审查**
   - 响应审查意见
   - 及时进行必要的修改
   - 保持代码质量

4. **合并条件**
   - 通过所有CI检查
   - 至少一个维护者审查通过
   - 没有冲突

## 🌍 国际化

我们欢迎多语言贡献：
- 界面文本翻译
- 文档翻译
- 帮助信息本地化

支持的语言：
- 中文 (简体/繁体)
- English
- 日本語 (计划中)

## 📞 联系方式

- 通过 GitHub Issues 提问
- 参与 GitHub Discussions
- 关注项目更新

## 🎯 贡献者

感谢所有为本项目做出贡献的开发者！

[![Contributors](https://contrib.rocks/image?repo=your-username/qoderProj)](https://github.com/your-username/qoderProj/graphs/contributors)

## 📜 行为准则

请遵循我们的 [行为准则](CODE_OF_CONDUCT.md)，共同维护一个友好、包容的社区环境。

---

再次感谢您的贡献！🙏