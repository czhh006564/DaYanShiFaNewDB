@echo off
echo 🔧 Git 配置脚本
echo ====================

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git已安装

echo.
echo 📝 配置Git用户信息
echo.

set /p GIT_NAME="请输入您的姓名 (如: 张三): "
set /p GIT_EMAIL="请输入您的邮箱 (如: zhangsan@example.com): "

echo.
echo 🔧 正在配置Git...

git config --global user.name "%GIT_NAME%"
git config --global user.email "%GIT_EMAIL%"

echo ✅ Git配置完成
echo.
echo 📋 当前配置:
git config --global user.name
git config --global user.email

echo.
echo 🎉 现在可以运行 push-to-github.bat 推送代码了！
pause