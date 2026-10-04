# 大衍筮法程序 Docker 镜像
# 使用阿里云镜像源
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.9-slim

# 设置维护者信息
LABEL maintainer="dayansifa-team"
LABEL description="大衍筮法 - 数字化周易占卜程序"
LABEL version="2.0.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DAYANSIFA_ENV=production
ENV DAYANSIFA_WEB_SERVER_HOST=0.0.0.0
ENV DAYANSIFA_WEB_SERVER_PORT=8080

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY *.py ./
COPY *.js ./
COPY *.html ./
COPY *.css ./
COPY *.md ./

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/exports /app/cache

# 设置权限
RUN chmod +x *.py

# 创建非root用户
RUN useradd -m -u 1000 dayansifa && \
    chown -R dayansifa:dayansifa /app
USER dayansifa

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health')" || exit 1

# 暴露端口
EXPOSE 8080

# 默认启动Web版本
CMD ["python", "webserver_v2.py", "--no-browser"]