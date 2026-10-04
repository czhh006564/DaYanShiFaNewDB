@echo off
echo 🌟 大衍筮法 Docker 快速部署
echo ===============================

REM 检查Docker
docker --version
if errorlevel 1 (
    echo ❌ Docker未运行，请启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker检查通过

REM 停止现有容器
echo 🛑 清理现有容器...
docker stop dayansifa-web 2>nul
docker rm dayansifa-web 2>nul

REM 使用Python基础镜像直接运行
echo 🚀 启动大衍筮法容器...
docker run -d ^
    --name dayansifa-web ^
    --restart unless-stopped ^
    -p 8080:8080 ^
    -v "%cd%":/app ^
    -w /app ^
    -e PYTHONPATH=/app ^
    -e PYTHONUNBUFFERED=1 ^
    python:3.9-slim ^
    python webserver_v2.py --host=0.0.0.0 --port=8080

if errorlevel 1 (
    echo ❌ 容器启动失败
    pause
    exit /b 1
)

echo ✅ 容器启动成功

echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

echo.
echo 🎉 部署完成！
echo.
echo 📱 Web界面: http://localhost:8080
echo 🔗 API健康检查: http://localhost:8080/api/health
echo.
echo 💡 提示：如果访问失败，请等待1-2分钟让容器完全启动
echo.
pause