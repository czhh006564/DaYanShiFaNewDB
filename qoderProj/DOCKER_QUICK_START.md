# 大衍筮法 Docker 部署快速指南

## 🎯 当前状态
✅ **Docker容器已成功运行！**

- 容器名称: `dayansifa-web`
- 访问地址: http://localhost:8081
- 容器状态: 运行中
- 基础镜像: `python:3.9-slim`

## 🌐 快速访问
- **Web界面**: http://localhost:8081
- **API健康检查**: http://localhost:8081/api/health
- **统计信息**: http://localhost:8081/api/stats
- **历史记录**: http://localhost:8081/api/history

## 🚀 可用部署方式

### 1. 直接Docker命令（当前使用）
```bash
docker run -d --name dayansifa-web --restart unless-stopped \
  -p 8081:8080 -v "${PWD}:/app" -w /app \
  -e PYTHONPATH=/app -e PYTHONUNBUFFERED=1 \
  python:3.9-slim python webserver_v2.py --host=0.0.0.0 --port=8080
```

### 2. Windows批处理脚本
```cmd
.\docker-run.bat
```

### 3. Docker Compose
```bash
# 直接运行方式（推荐）
docker-compose up -d

# 构建方式
docker-compose --profile build up -d dayansifa-web-build
```

### 4. Linux部署脚本
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

## 📊 容器管理

### 查看状态
```bash
# 查看运行中的容器
docker ps | grep dayansifa

# 查看容器详细信息
docker inspect dayansifa-web
```

### 查看日志
```bash
# 实时日志
docker logs -f dayansifa-web

# 最近日志
docker logs --tail 100 dayansifa-web
```

### 控制容器
```bash
# 停止容器
docker stop dayansifa-web

# 启动容器
docker start dayansifa-web

# 重启容器
docker restart dayansifa-web

# 删除容器
docker rm -f dayansifa-web
```

## 🔧 配置说明

### 端口映射
- 宿主机端口: `8081`
- 容器端口: `8080`
- 访问地址: http://localhost:8081

### 数据挂载
- 应用代码: `当前目录 → /app`
- 数据目录: `dayansifa_data → /app/data`
- 日志目录: `dayansifa_logs → /app/logs`
- 导出目录: `dayansifa_exports → /app/exports`

### 环境变量
- `PYTHONPATH=/app`: Python模块路径
- `PYTHONUNBUFFERED=1`: 实时输出日志
- `DAYANSIFA_ENV=production`: 生产环境模式

## 🛠️ 故障排除

### 1. 端口冲突
如果8081端口被占用，可以修改端口：
```bash
docker run ... -p 8082:8080 ...
```

### 2. 容器无法启动
检查错误日志：
```bash
docker logs dayansifa-web
```

### 3. 无法访问Web界面
检查容器是否运行：
```bash
docker ps | grep dayansifa-web
```

测试API接口：
```bash
curl http://localhost:8081/api/health
```

## 📈 扩展功能

### 数据持久化
使用Docker卷保存数据：
```bash
docker run ... -v dayansifa_data:/app/data ...
```

### 负载均衡
使用nginx反向代理：
```bash
docker-compose --profile production up -d
```

### 监控告警
配置健康检查：
```bash
docker run ... --health-cmd="curl -f http://localhost:8080/api/health" ...
```

## 🎉 完成！

Docker部署已经完成，现在可以：

1. 🌐 **访问Web界面**: 在浏览器中打开 http://localhost:8081
2. 🎯 **开始占卜**: 点击"开始占卜"按钮体验大衍筮法
3. 📊 **查看历史**: 访问历史记录页面查看之前的占卜结果
4. 🔌 **使用API**: 通过API接口集成到其他应用中

**祝你使用愉快！** 🎊