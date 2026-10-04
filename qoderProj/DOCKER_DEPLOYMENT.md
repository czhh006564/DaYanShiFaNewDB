# 大衍筮法 Docker 部署指南

## 🎯 快速部署

### 方法一：直接运行（推荐）
```bash
# 删除现有容器（如果存在）
docker rm -f dayansifa-web

# 启动新容器
docker run -d \
  --name dayansifa-web \
  --restart unless-stopped \
  -p 8081:8080 \
  -v "${PWD}:/app" \
  -w /app \
  -e PYTHONPATH=/app \
  -e PYTHONUNBUFFERED=1 \
  python:3.9-slim \
  python webserver_v2.py --host=0.0.0.0 --port=8080
```

### 方法二：使用Docker Compose
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法三：使用Windows批处理脚本
```bash
# 运行快速部署脚本
.\docker-run.bat
```

## 📋 部署要求

### 系统要求
- Windows 10/11 或 Linux/macOS
- Docker Desktop 或 Docker Engine
- 至少 2GB 可用内存
- 端口 8081 可用

### 软件版本
- Docker: 20.10+
- Python: 3.9+（容器内自动包含）

## 🚀 部署步骤

### 1. 检查Docker环境
```bash
# 检查Docker版本
docker --version

# 检查Docker运行状态
docker ps
```

### 2. 清理现有容器
```bash
# 停止并删除现有容器
docker stop dayansifa-web 2>/dev/null || true
docker rm dayansifa-web 2>/dev/null || true
```

### 3. 启动新容器
```bash
# 启动大衍筮法容器
docker run -d \
  --name dayansifa-web \
  --restart unless-stopped \
  -p 8081:8080 \
  -v "${PWD}:/app" \
  -w /app \
  -e PYTHONPATH=/app \
  -e PYTHONUNBUFFERED=1 \
  python:3.9-slim \
  python webserver_v2.py --host=0.0.0.0 --port=8080
```

### 4. 验证部署
```bash
# 检查容器状态
docker ps | grep dayansifa-web

# 查看容器日志
docker logs dayansifa-web

# 测试API接口
curl http://localhost:8081/api/health
```

## 🌐 访问应用

### Web界面
- **主页**: http://localhost:8081
- **占卜界面**: http://localhost:8081/index.html

### API接口
- **健康检查**: http://localhost:8081/api/health
- **执行占卜**: POST http://localhost:8081/api/divination
- **获取统计**: http://localhost:8081/api/stats
- **历史记录**: http://localhost:8081/api/history
- **配置信息**: http://localhost:8081/api/config

## 🔧 配置选项

### 环境变量
```bash
-e DAYANSIFA_ENV=production          # 运行环境
-e DAYANSIFA_WEB_SERVER_HOST=0.0.0.0 # 服务器地址
-e DAYANSIFA_WEB_SERVER_PORT=8080    # 服务器端口
-e PYTHONPATH=/app                   # Python路径
-e PYTHONUNBUFFERED=1                # Python输出设置
```

### 端口映射
```bash
-p 宿主机端口:容器端口
-p 8081:8080  # 将容器的8080端口映射到宿主机的8081端口
```

### 数据卷挂载
```bash
-v "${PWD}:/app"                     # 挂载当前目录到容器/app目录
-v dayansifa_data:/app/data          # 持久化数据目录
-v dayansifa_logs:/app/logs          # 持久化日志目录
-v dayansifa_exports:/app/exports    # 持久化导出目录
```

## 📊 监控和管理

### 查看容器状态
```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器详细信息
docker inspect dayansifa-web
```

### 查看日志
```bash
# 查看实时日志
docker logs -f dayansifa-web

# 查看最近100行日志
docker logs --tail 100 dayansifa-web

# 查看指定时间段日志
docker logs --since="2024-01-01T00:00:00" dayansifa-web
```

### 进入容器
```bash
# 进入容器内部
docker exec -it dayansifa-web bash

# 在容器内执行命令
docker exec dayansifa-web python -c "print('Hello from container')"
```

### 重启容器
```bash
# 重启容器
docker restart dayansifa-web

# 停止容器
docker stop dayansifa-web

# 启动容器
docker start dayansifa-web
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
netstat -an | findstr :8081

# 使用不同端口
docker run ... -p 8082:8080 ...
```

#### 2. 容器启动失败
```bash
# 查看错误日志
docker logs dayansifa-web

# 检查容器状态
docker ps -a | grep dayansifa-web
```

#### 3. 无法访问Web界面
```bash
# 检查防火墙设置
# 确认容器正在运行
docker ps | grep dayansifa-web

# 测试本地连接
curl http://localhost:8081/api/health
```

#### 4. Python模块错误
```bash
# 检查文件挂载
docker exec dayansifa-web ls -la /app

# 检查Python路径
docker exec dayansifa-web python -c "import sys; print(sys.path)"
```

### 日志级别
- **INFO**: 正常运行信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **DEBUG**: 调试信息（仅开发环境）

## 🔒 安全建议

### 网络安全
- 不要将容器直接暴露到公网
- 使用反向代理（如Nginx）
- 启用HTTPS加密
- 配置防火墙规则

### 数据安全
- 定期备份数据目录
- 使用安全的数据卷挂载
- 限制容器权限
- 监控异常访问

## 📈 性能优化

### 资源限制
```bash
# 限制内存使用
docker run ... --memory=1g ...

# 限制CPU使用
docker run ... --cpus=1.0 ...
```

### 健康检查
```bash
# 配置健康检查
docker run ... --health-cmd="curl -f http://localhost:8080/api/health" ...
```

## 🎯 最佳实践

1. **使用特定版本标签**而不是`latest`
2. **定期更新基础镜像**以获取安全补丁
3. **监控资源使用情况**
4. **配置日志轮转**防止日志文件过大
5. **使用多阶段构建**减少镜像大小
6. **设置合适的重启策略**

## 📚 相关命令参考

### Docker基础命令
```bash
# 拉取镜像
docker pull python:3.9-slim

# 构建镜像
docker build -t dayansifa:latest .

# 运行容器
docker run -d --name dayansifa-web ...

# 停止容器
docker stop dayansifa-web

# 删除容器
docker rm dayansifa-web

# 删除镜像
docker rmi dayansifa:latest
```

### Docker Compose命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🆘 获取帮助

如果遇到问题，请按以下步骤排查：

1. 检查Docker是否正常运行
2. 查看容器日志：`docker logs dayansifa-web`
3. 验证网络连接：`curl http://localhost:8081/api/health`
4. 检查文件权限和挂载点
5. 参考本文档的故障排除部分

---

**💡 提示**: 首次部署可能需要下载Python基础镜像，请耐心等待。后续启动会很快。

**🎉 享受使用大衍筮法数字化占卜程序！**