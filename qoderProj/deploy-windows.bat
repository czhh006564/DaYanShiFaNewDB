@echo off
REM 大衍筮法 Docker 部署脚本 (Windows版本)
echo 🌟 大衍筮法 Docker 部署脚本
echo ===============================

REM 检查Docker是否运行
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行或未安装，请先启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过

REM 停止现有容器
echo 🛑 停止现有容器...
docker stop dayansifa-web >nul 2>&1
docker rm dayansifa-web >nul 2>&1

REM 清理旧镜像
echo 🧹 清理旧镜像...
docker rmi qoderproj-dayansifa-web >nul 2>&1

REM 构建新镜像
echo 🔨 构建Docker镜像...
docker build -f Dockerfile.offline -t dayansifa:latest .
if errorlevel 1 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

echo ✅ 镜像构建成功

REM 运行容器
echo 🚀 启动容器...
docker run -d ^
    --name dayansifa-web ^
    --restart unless-stopped ^
    -p 8080:8080 ^
    -v dayansifa_data:/app/data ^
    -v dayansifa_logs:/app/logs ^
    -v dayansifa_exports:/app/exports ^
    dayansifa:latest

if errorlevel 1 (
    echo ❌ 容器启动失败
    docker logs dayansifa-web
    pause
    exit /b 1
)

echo ✅ 容器启动成功

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查健康状态
echo 🔍 检查服务状态...
curl -s http://localhost:8080/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 服务可能还在启动中，请稍后访问
) else (
    echo ✅ 服务运行正常
)

echo.
echo 🎉 部署完成！
echo.
echo 📱 Web界面: http://localhost:8080
echo 🔗 API健康检查: http://localhost:8080/api/health
echo 📊 统计信息: http://localhost:8080/api/stats
echo.
echo 📚 常用命令:
echo   查看容器状态: docker ps
echo   查看日志: docker logs dayansifa-web
echo   停止服务: docker stop dayansifa-web
echo   重启服务: docker restart dayansifa-web
echo.

REM 询问是否打开浏览器
set /p openBrowser="是否打开浏览器访问应用？(y/n): "
if /i "%openBrowser%"=="y" (
    start http://localhost:8080
)

pause