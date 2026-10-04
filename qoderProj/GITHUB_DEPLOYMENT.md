# GitHub 部署和使用指南

## 🚀 将项目推送到GitHub

### 准备工作

#### 1. 安装Git
如果您的系统还没有安装Git，请按照以下步骤安装：

**Windows:**
- 访问 https://git-scm.com/download/win
- 下载并安装Git for Windows
- 安装完成后重启终端

**macOS:**
```bash
# 使用Homebrew安装
brew install git

# 或使用Xcode命令行工具
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

#### 2. 配置Git
```bash
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"
```

#### 3. 在GitHub上创建仓库
1. 登录GitHub (https://github.com)
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息：
   - **Repository name**: `dayansifa` 或 `qoderProj`
   - **Description**: `大衍筮法 - 数字化周易占卜程序`
   - **Visibility**: Public 或 Private
   - **Initialize**: 不要勾选任何初始化选项
5. 点击 "Create repository"

### 本地Git初始化和推送

#### 1. 在项目目录中初始化Git
```bash
# 进入项目目录
cd C:\Users\admin\Desktop\qoderProj

# 初始化Git仓库
git init

# 添加远程仓库（替换YOUR_USERNAME为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/dayansifa.git
```

#### 2. 添加和提交文件
```bash
# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "feat: 初始提交 - 大衍筮法数字化占卜程序

- 实现传统大衍筮法算法
- 提供命令行和Web两种版本
- 包含完整的六十四卦数据库
- 支持Docker容器化部署
- 完整的CI/CD流水线配置"
```

#### 3. 推送到GitHub
```bash
# 推送到主分支
git branch -M main
git push -u origin main
```

## 🔧 GitHub功能配置

### 1. 启用GitHub Actions
推送代码后，GitHub Actions会自动运行，但您需要配置一些Secrets：

1. 进入您的GitHub仓库
2. 点击 "Settings" 标签
3. 在左侧菜单中选择 "Secrets and variables" → "Actions"
4. 添加以下Secrets（如果需要Docker Hub部署）：
   - `DOCKER_USERNAME`: 您的Docker Hub用户名
   - `DOCKER_PASSWORD`: 您的Docker Hub访问令牌

### 2. 配置分支保护
1. 在仓库设置中选择 "Branches"
2. 点击 "Add rule"
3. 设置分支名称模式为 `main`
4. 启用以下选项：
   - "Require a pull request before merging"
   - "Require status checks to pass before merging"
   - "Require up-to-date branches before merging"

### 3. 启用Issues和Projects
1. 在仓库设置的 "General" 部分
2. 确保 "Issues" 和 "Projects" 已启用

## 📋 日常开发工作流

### 1. 创建功能分支
```bash
# 创建并切换到新分支
git checkout -b feature/新功能名称

# 进行开发...

# 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 推送分支
git push origin feature/新功能名称
```

### 2. 创建Pull Request
1. 在GitHub仓库页面点击 "Compare & pull request"
2. 填写PR描述和相关信息
3. 等待CI检查通过和代码审查
4. 合并到主分支

### 3. 版本发布
```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🐳 Docker Hub集成（可选）

### 1. 创建Docker Hub仓库
1. 访问 https://hub.docker.com
2. 创建新仓库，名称如：`yourusername/dayansifa`

### 2. 配置自动构建
GitHub Actions已配置自动构建，当代码推送时会：
- 自动构建Docker镜像
- 推送到Docker Hub
- 支持多架构构建（amd64, arm64）

## 📊 监控和维护

### 1. GitHub Insights
- 查看提交历史和贡献者统计
- 监控Issues和Pull Requests
- 分析代码频率和活跃度

### 2. GitHub Actions
- 监控CI/CD流水线状态
- 查看构建日志和测试结果
- 管理部署状态

### 3. Dependabot（依赖更新）
GitHub会自动检测依赖更新并创建PR。

## 🌟 GitHub特性利用

### 1. GitHub Pages（可选）
可以配置GitHub Pages来托管项目文档：
1. 在仓库设置中找到 "Pages"
2. 选择源分支（如 `gh-pages`）
3. 配置自定义域名（可选）

### 2. GitHub Discussions
启用Discussions功能来进行社区讨论：
1. 在仓库设置中启用 "Discussions"
2. 创建不同类别的讨论话题

### 3. GitHub Sponsors（可选）
如果项目发展良好，可以启用赞助功能。

## 🎯 最佳实践

### 1. 提交信息规范
- 使用规范的提交信息格式
- 包含clear的描述和相关Issue引用
- 使用语义化版本控制

### 2. 分支策略
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 3. 文档维护
- 保持README.md更新
- 及时更新API文档
- 维护变更日志

## 🔗 有用的链接

- [Git文档](https://git-scm.com/doc)
- [GitHub文档](https://docs.github.com/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Docker Hub文档](https://docs.docker.com/docker-hub/)

---

完成以上步骤后，您的大衍筮法项目就成功部署到GitHub了！🎉