#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法 Web 版本服务器启动脚本
使用Python内置的HTTP服务器运行Web界面
"""

import os
import sys
import webbrowser
import http.server
import socketserver
import threading
import time
from pathlib import Path


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # 设置正确的MIME类型
        if self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
        elif self.path.endswith('.css'):
            self.send_header('Content-Type', 'text/css; charset=utf-8')
        elif self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")


class WebServer:
    """Web服务器类"""
    
    def __init__(self, port=8080, host='localhost'):
        self.port = port
        self.host = host
        self.server = None
        self.server_thread = None
    
    def start(self, auto_open=True):
        """启动服务器"""
        try:
            # 切换到项目目录
            project_dir = Path(__file__).parent
            os.chdir(project_dir)
            
            # 检查必要文件是否存在
            required_files = ['index.html', 'styles.css', 'app.js', 
                            'dayansifa-core.js', 'hexagram-database.js']
            
            missing_files = []
            for file in required_files:
                if not Path(file).exists():
                    missing_files.append(file)
            
            if missing_files:
                print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
                return False
            
            # 创建服务器
            with socketserver.TCPServer((self.host, self.port), CustomHTTPRequestHandler) as httpd:
                self.server = httpd
                
                url = f"http://{self.host}:{self.port}"
                print("🌟" + "=" * 60)
                print("🔮 大衍筮法 Web 版本服务器已启动")
                print("=" * 62)
                print(f"📍 服务器地址: {url}")
                print(f"📁 服务目录: {project_dir}")
                print("=" * 62)
                print("💡 使用说明:")
                print("   - 在浏览器中访问上述地址")
                print("   - 按 Ctrl+C 停止服务器")
                print("   - 确保所有 .js 和 .css 文件都在同一目录")
                print("=" * 62)
                
                # 自动打开浏览器
                if auto_open:
                    print("🚀 正在打开浏览器...")
                    try:
                        webbrowser.open(url)
                        print("✅ 浏览器已打开")
                    except Exception as e:
                        print(f"⚠️  无法自动打开浏览器: {e}")
                        print(f"   请手动在浏览器中访问: {url}")
                
                print("\n🔄 服务器日志:")
                print("-" * 40)
                
                # 启动服务器
                httpd.serve_forever()
                
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"❌ 端口 {self.port} 已被占用，请尝试其他端口")
                return False
            else:
                print(f"❌ 启动服务器失败: {e}")
                return False
        except KeyboardInterrupt:
            print("\n\n🛑 服务器已停止")
            return True
        except Exception as e:
            print(f"❌ 服务器运行出错: {e}")
            return False
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            print("🛑 服务器已停止")


def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("   建议使用Python 3.6+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查项目文件
    project_files = {
        'index.html': 'HTML主页面',
        'styles.css': 'CSS样式文件',
        'app.js': '主应用逻辑',
        'dayansifa-core.js': '大衍筮法核心算法',
        'hexagram-database.js': '卦象数据库'
    }
    
    current_dir = Path(__file__).parent
    missing_files = []
    
    for file, description in project_files.items():
        file_path = current_dir / file
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file} ({description}) - {file_size} bytes")
        else:
            missing_files.append(f"{file} ({description})")
    
    if missing_files:
        print(f"❌ 缺少文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True


def show_usage():
    """显示使用说明"""
    print("""
🌟 大衍筮法 Web 版本启动器

用法:
    python webserver.py [选项]

选项:
    -p, --port PORT     指定端口号 (默认: 8080)
    -h, --host HOST     指定主机地址 (默认: localhost)
    --no-browser        不自动打开浏览器
    --help              显示此帮助信息

示例:
    python webserver.py                    # 使用默认设置
    python webserver.py -p 3000           # 使用端口3000
    python webserver.py -h 0.0.0.0        # 允许外部访问
    python webserver.py --no-browser      # 不打开浏览器
    """)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='大衍筮法 Web 版本服务器')
    parser.add_argument('-p', '--port', type=int, default=8080, help='端口号 (默认: 8080)')
    parser.add_argument('-H', '--host', default='localhost', help='主机地址 (默认: localhost)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，无法启动服务器")
        sys.exit(1)
    
    print("\n✅ 环境检查通过")
    
    # 创建并启动服务器
    server = WebServer(port=args.port, host=args.host)
    
    try:
        success = server.start(auto_open=not args.no_browser)
        if success:
            print("\n🎉 感谢使用大衍筮法 Web 版本！")
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)


if __name__ == "__main__":
    main()