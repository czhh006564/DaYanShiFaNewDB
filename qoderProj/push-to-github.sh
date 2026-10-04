#!/bin/bash

# 大衍筮法项目 - GitHub 一键推送脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 大衍筮法项目 - GitHub 一键推送脚本${NC}"
echo "================================================"

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
    echo "Ubuntu/Debian: sudo apt install git"
    echo "macOS: brew install git"
    exit 1
fi

echo -e "${GREEN}✅ Git检查通过${NC}"

# 获取用户输入
read -p "请输入您的GitHub用户名: " GITHUB_USERNAME
read -p "请输入仓库名称 (默认: dayansifa): " REPO_NAME
REPO_NAME=${REPO_NAME:-dayansifa}

read -p "请输入提交信息 (默认: 更新代码): " COMMIT_MESSAGE
COMMIT_MESSAGE=${COMMIT_MESSAGE:-更新代码}

echo
echo -e "${BLUE}📋 配置信息:${NC}"
echo "   GitHub用户名: $GITHUB_USERNAME"
echo "   仓库名称: $REPO_NAME"
echo "   提交信息: $COMMIT_MESSAGE"
echo

read -p "确认推送? (y/n): " CONFIRM
if [[ $CONFIRM != [yY] ]]; then
    echo "取消操作"
    exit 0
fi

echo
echo -e "${BLUE}🚀 开始推送过程...${NC}"
echo

# 检查是否已经初始化Git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📁 初始化Git仓库...${NC}"
    git init
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Git初始化失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Git仓库初始化完成${NC}"
    
    echo -e "${YELLOW}🔗 添加远程仓库...${NC}"
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 添加远程仓库失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 远程仓库添加完成${NC}"
else
    echo -e "${GREEN}✅ Git仓库已存在${NC}"
    
    # 检查远程仓库
    if ! git remote get-url origin &> /dev/null; then
        echo -e "${YELLOW}🔗 添加远程仓库...${NC}"
        git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo -e "${GREEN}✅ 远程仓库添加完成${NC}"
    else
        echo -e "${GREEN}✅ 远程仓库已配置${NC}"
    fi
fi

# 添加所有文件
echo -e "${YELLOW}📦 添加文件到暂存区...${NC}"
git add .
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 添加文件失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 文件添加完成${NC}"

# 创建提交
echo -e "${YELLOW}💾 创建提交...${NC}"
git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ 提交创建失败（可能没有更改）${NC}"
    echo "检查是否有更改..."
    git status
    exit 1
fi
echo -e "${GREEN}✅ 提交创建完成${NC}"

# 设置主分支
echo -e "${YELLOW}🌿 设置主分支...${NC}"
git branch -M main
echo -e "${GREEN}✅ 主分支设置完成${NC}"

# 推送到GitHub
echo -e "${YELLOW}🚀 推送到GitHub...${NC}"
git push -u origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 推送失败${NC}"
    echo
    echo -e "${YELLOW}💡 可能的解决方案:${NC}"
    echo "1. 检查网络连接"
    echo "2. 确认GitHub用户名和仓库名称正确"
    echo "3. 确认GitHub仓库已创建"
    echo "4. 检查Git认证配置"
    echo
    echo -e "${BLUE}🔧 手动推送命令:${NC}"
    echo "git push -u origin main"
    exit 1
fi

echo
echo -e "${GREEN}🎉 推送成功！${NC}"
echo
echo -e "${BLUE}📱 您的项目现在可以在以下地址访问:${NC}"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo
echo -e "${YELLOW}🔧 后续操作建议:${NC}"
echo "1. 在GitHub仓库设置中配置分支保护"
echo "2. 启用GitHub Actions (已自动配置)"
echo "3. 配置Docker Hub Secrets (如需要)"
echo "4. 查看项目的CI/CD流水线状态"
echo

# 询问是否打开浏览器
read -p "是否打开GitHub仓库页面? (y/n): " OPEN_BROWSER
if [[ $OPEN_BROWSER == [yY] ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    elif command -v open &> /dev/null; then
        open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    else
        echo "请手动打开: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    fi
fi

echo
echo -e "${BLUE}📚 更多信息请查看 GITHUB_DEPLOYMENT.md 文件${NC}"
echo