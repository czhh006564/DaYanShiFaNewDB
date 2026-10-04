@echo off
echo 🌟 大衍筮法项目 - GitHub 一键推送脚本
echo ================================================

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git检查通过

REM 获取用户输入
set /p GITHUB_USERNAME="请输入您的GitHub用户名: "
set /p REPO_NAME="请输入仓库名称 (默认: dayansifa): "
if "%REPO_NAME%"=="" set REPO_NAME=dayansifa

set /p COMMIT_MESSAGE="请输入提交信息 (默认: 更新代码): "
if "%COMMIT_MESSAGE%"=="" set COMMIT_MESSAGE=更新代码

echo.
echo 📋 配置信息:
echo    GitHub用户名: %GITHUB_USERNAME%
echo    仓库名称: %REPO_NAME%
echo    提交信息: %COMMIT_MESSAGE%
echo.

set /p CONFIRM="确认推送? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo 取消操作
    pause
    exit /b 0
)

echo.
echo 🚀 开始推送过程...
echo.

REM 检查是否已经初始化Git
if not exist ".git" (
    echo 📁 初始化Git仓库...
    git init
    if errorlevel 1 (
        echo ❌ Git初始化失败
        pause
        exit /b 1
    )
    echo ✅ Git仓库初始化完成
    
    echo 🔗 添加远程仓库...
    git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
    if errorlevel 1 (
        echo ❌ 添加远程仓库失败
        pause
        exit /b 1
    )
    echo ✅ 远程仓库添加完成
) else (
    echo ✅ Git仓库已存在
    
    REM 检查远程仓库
    git remote get-url origin >nul 2>&1
    if errorlevel 1 (
        echo 🔗 添加远程仓库...
        git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
        echo ✅ 远程仓库添加完成
    ) else (
        echo ✅ 远程仓库已配置
    )
)

REM 添加所有文件
echo 📦 添加文件到暂存区...
git add .
if errorlevel 1 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo ✅ 文件添加完成

REM 创建提交
echo 💾 创建提交...
git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo ⚠️ 提交创建失败（可能没有更改）
    echo 检查是否有更改...
    git status
    pause
    exit /b 1
)
echo ✅ 提交创建完成

REM 设置主分支
echo 🌿 设置主分支...
git branch -M main
echo ✅ 主分支设置完成

REM 推送到GitHub
echo 🚀 推送到GitHub...
git push -u origin main
if errorlevel 1 (
    echo ❌ 推送失败
    echo.
    echo 💡 可能的解决方案:
    echo 1. 检查网络连接
    echo 2. 确认GitHub用户名和仓库名称正确
    echo 3. 确认GitHub仓库已创建
    echo 4. 检查Git认证配置
    echo.
    echo 🔧 手动推送命令:
    echo git push -u origin main
    pause
    exit /b 1
)

echo.
echo 🎉 推送成功！
echo.
echo 📱 您的项目现在可以在以下地址访问:
echo https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo 🔧 后续操作建议:
echo 1. 在GitHub仓库设置中配置分支保护
echo 2. 启用GitHub Actions (已自动配置)
echo 3. 配置Docker Hub Secrets (如需要)
echo 4. 查看项目的CI/CD流水线状态
echo.

REM 询问是否打开浏览器
set /p OPEN_BROWSER="是否打开GitHub仓库页面? (y/n): "
if /i "%OPEN_BROWSER%"=="y" (
    start https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
)

echo.
echo 📚 更多信息请查看 GITHUB_DEPLOYMENT.md 文件
echo.
pause