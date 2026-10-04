#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法 Web 版本服务器 (增强版)
使用Python内置的HTTP服务器运行Web界面
支持API接口、性能监控、错误处理等功能
"""

import os
import sys
import json
import webbrowser
import http.server
import socketserver
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 导入新模块
from config import config
from logger import get_logger
from performance import monitor_performance, get_performance_summary
from dayansifa_v2 import DaYanShiFaV2
from history import history_manager
from i18n import i18n_manager, _
from export_tools import data_exporter


class EnhancedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """增强的HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.diviner = DaYanShiFaV2(use_logging=True, use_caching=True)
        self.logger = get_logger("web_server")
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """设置响应头"""
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
        elif self.path.endswith('.json'):
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理OPTIONS请求"""
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        start_time = time.time()
        
        try:
            if self.path.startswith('/api/'):
                self._handle_api_request()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.logger.error(f"POST请求处理出错: {e}", exc_info=True)
            self._send_error_response(500, "Internal server error", str(e))
        finally:
            duration = time.time() - start_time
            self.logger.info(f"POST {self.path} - {getattr(self, 'response_code', 500)} - {duration:.3f}秒")
    
    def do_GET(self):
        """处理GET请求"""
        start_time = time.time()
        
        try:
            if self.path.startswith('/api/'):
                self._handle_api_request()
            else:
                super().do_GET()
        except Exception as e:
            self.logger.error(f"GET请求处理出错: {e}", exc_info=True)
            self._send_error_response(500, "Internal server error", str(e))
        finally:
            duration = time.time() - start_time
            self.logger.info(f"GET {self.path} - {getattr(self, 'response_code', 200)} - {duration:.3f}秒")
    
    @monitor_performance("api_request")
    def _handle_api_request(self):
        """处理API请求"""
        path_parts = self.path.split('/')
        
        if len(path_parts) < 3:
            self._send_error_response(400, "Invalid API path")
            return
        
        api_endpoint = path_parts[2]
        
        # 路由API请求
        if api_endpoint == 'divination':
            self._handle_divination_api()
        elif api_endpoint == 'config':
            self._handle_config_api()
        elif api_endpoint == 'stats':
            self._handle_stats_api()
        elif api_endpoint == 'health':
            self._handle_health_api()
        elif api_endpoint == 'history':
            self._handle_history_api()
        elif api_endpoint == 'export':
            self._handle_export_api()
        elif api_endpoint == 'language':
            self._handle_language_api()
        else:
            self._send_error_response(404, "API endpoint not found")
    
    def _handle_divination_api(self):
        """处理占卜API请求"""
        if self.command == 'POST':
            # 获取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                question = request_data.get('question', '')
                
                # 执行占卜（不显示控制台输出）
                result = self.diviner.divination(question)
                
                # 格式化响应
                response_data = {
                    "success": True,
                    "data": {
                        "question": result["question"],
                        "hexagram": result["hexagram"],
                        "analysis": result["analysis"],
                        "duration": result["duration"],
                        "timestamp": result["timestamp"].isoformat()
                    }
                }
                
                self._send_json_response(200, response_data)
                
            except json.JSONDecodeError:
                self._send_error_response(400, "Invalid JSON data")
            except Exception as e:
                self.logger.error(f"占卜API处理出错: {e}", exc_info=True)
                self._send_error_response(500, "Divination failed", str(e))
        else:
            self._send_error_response(405, "Method not allowed")
    
    def _handle_config_api(self):
        """处理配置API请求"""
        if self.command == 'GET':
            config_data = {
                "project_info": {
                    "name": config.PROJECT_NAME,
                    "version": config.PROJECT_VERSION,
                    "description": config.PROJECT_DESCRIPTION
                },
                "settings": {
                    "ui_language": config.UI_LANGUAGE,
                    "ui_theme": config.UI_THEME,
                    "max_question_length": config.MAX_QUESTION_LENGTH,
                    "show_process_details": config.SHOW_PROCESS_DETAILS
                }
            }
            self._send_json_response(200, {"success": True, "data": config_data})
        else:
            self._send_error_response(405, "Method not allowed")
    
    def _handle_stats_api(self):
        """处理统计API请求"""
        if self.command == 'GET':
            try:
                diviner_stats = self.diviner.get_statistics()
                performance_stats = get_performance_summary()
                
                stats_data = {
                    "diviner": diviner_stats,
                    "performance": performance_stats,
                    "server_info": {
                        "start_time": datetime.now().isoformat(),
                        "version": config.PROJECT_VERSION
                    }
                }
                
                self._send_json_response(200, {"success": True, "data": stats_data})
            except Exception as e:
                self.logger.error(f"统计API处理出错: {e}", exc_info=True)
                self._send_error_response(500, "Stats retrieval failed", str(e))
        else:
            self._send_error_response(405, "Method not allowed")
    
    def _handle_health_api(self):
        """处理健康检查API请求"""
        if self.command == 'GET':
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": config.PROJECT_VERSION,
                "features": {
                    "caching": config.ENABLE_CACHE,
                    "logging": True,
                    "performance_monitoring": True,
                    "history": True,
                    "i18n": True,
                    "export": True
                }
            }
            self._send_json_response(200, {"success": True, "data": health_data})
        else:
            self._send_error_response(405, "Method not allowed")
    
    def _handle_history_api(self):
        """处理历史记录API请求"""
        try:
            if self.command == 'GET':
                # 获取查询参数
                query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                limit = int(query_params.get('limit', [50])[0])
                offset = int(query_params.get('offset', [0])[0])
                search = query_params.get('search', [None])[0]
                
                # 获取历史记录
                history_records = history_manager.get_history(
                    limit=limit,
                    offset=offset,
                    search_query=search
                )
                
                # 获取统计信息
                statistics = history_manager.get_statistics()
                
                response_data = {
                    "records": history_records,
                    "statistics": statistics,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(history_records)
                    }
                }
                
                self._send_json_response(200, {"success": True, "data": response_data})
                
            elif self.command == 'DELETE':
                # 删除历史记录
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode('utf-8'))
                    session_id = request_data.get('session_id')
                    
                    if session_id:
                        success = history_manager.delete_record(session_id)
                        if success:
                            self._send_json_response(200, {"success": True, "message": "记录已删除"})
                        else:
                            self._send_error_response(404, "记录未找到")
                    else:
                        self._send_error_response(400, "缺少session_id参数")
                else:
                    # 清空所有历史
                    deleted_count = history_manager.clear_history()
                    self._send_json_response(200, {
                        "success": True, 
                        "message": f"已清理 {deleted_count} 条记录"
                    })
            else:
                self._send_error_response(405, "Method not allowed")
                
        except Exception as e:
            self.logger.error(f"历史API处理出错: {e}", exc_info=True)
            self._send_error_response(500, "History API failed", str(e))
    
    def _handle_export_api(self):
        """处理导出API请求"""
        try:
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                export_type = request_data.get('type', 'history')  # history, report, statistics
                format_type = request_data.get('format', 'json')
                
                if export_type == 'history':
                    # 导出历史记录
                    export_path = history_manager.export_history(format_type=format_type)
                    
                elif export_type == 'statistics':
                    # 导出统计报告
                    statistics = history_manager.get_statistics()
                    export_path = data_exporter.export_statistics_report(
                        statistics=statistics,
                        format_type=format_type
                    )
                    
                elif export_type == 'report':
                    # 导出单次占卜报告
                    export_path = data_exporter.export_divination_report(
                        question=request_data.get('question', ''),
                        hexagram=request_data.get('hexagram', []),
                        analysis=request_data.get('analysis', {}),
                        processes=request_data.get('processes', []),
                        duration=request_data.get('duration', 0),
                        format_type=format_type
                    )
                else:
                    self._send_error_response(400, f"不支持的导出类型: {export_type}")
                    return
                
                response_data = {
                    "export_path": export_path,
                    "export_type": export_type,
                    "format": format_type,
                    "timestamp": datetime.now().isoformat()
                }
                
                self._send_json_response(200, {"success": True, "data": response_data})
                
            else:
                self._send_error_response(405, "Method not allowed")
                
        except Exception as e:
            self.logger.error(f"导出API处理出错: {e}", exc_info=True)
            self._send_error_response(500, "Export API failed", str(e))
    
    def _handle_language_api(self):
        """处理语言API请求"""
        try:
            if self.command == 'GET':
                # 获取支持的语言列表
                supported_languages = i18n_manager.get_supported_languages()
                current_language = i18n_manager.current_language
                
                response_data = {
                    "supported_languages": supported_languages,
                    "current_language": current_language
                }
                
                self._send_json_response(200, {"success": True, "data": response_data})
                
            elif self.command == 'POST':
                # 设置语言
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                language = request_data.get('language')
                if language:
                    i18n_manager.set_language(language)
                    response_data = {
                        "language": i18n_manager.current_language,
                        "message": f"语言已设置为: {language}"
                    }
                    self._send_json_response(200, {"success": True, "data": response_data})
                else:
                    self._send_error_response(400, "缺少language参数")
                    
            else:
                self._send_error_response(405, "Method not allowed")
                
        except Exception as e:
            self.logger.error(f"语言API处理出错: {e}", exc_info=True)
            self._send_error_response(500, "Language API failed", str(e))
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """发送JSON响应"""
        self.response_code = status_code
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
        self.end_headers()
        
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error_response(self, status_code: int, message: str, details: str = ""):
        """发送错误响应"""
        self.response_code = status_code
        error_data = {
            "success": False,
            "error": {
                "code": status_code,
                "message": message,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
        }
        self._send_json_response(status_code, error_data)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"[{timestamp}] {format % args}")


class EnhancedWebServer:
    """增强版Web服务器类"""
    
    def __init__(self, port: Optional[int] = None, host: Optional[str] = None):
        self.port = port or config.WEB_SERVER_PORT
        self.host = host or config.WEB_SERVER_HOST
        self.server = None
        self.server_thread = None
        self.logger = get_logger("web_server")
        self.start_time = datetime.now()
    
    def start(self, auto_open: Optional[bool] = None) -> bool:
        """启动服务器"""
        if auto_open is None:
            auto_open = config.WEB_AUTO_OPEN_BROWSER
        
        try:
            # 切换到项目目录
            project_dir = Path(__file__).parent
            os.chdir(project_dir)
            
            # 检查必要文件
            if not self._check_required_files():
                return False
            
            # 创建服务器
            with socketserver.TCPServer((self.host, self.port), EnhancedHTTPRequestHandler) as httpd:
                self.server = httpd
                
                url = f"http://{self.host}:{self.port}"
                self._print_startup_info(url)
                
                # 自动打开浏览器
                if auto_open:
                    self._open_browser(url)
                
                self.logger.info(f"Web服务器启动成功: {url}")
                
                # 启动服务器（这会阻塞直到服务器停止）
                try:
                    httpd.serve_forever()
                    return True  # 正常停止
                except KeyboardInterrupt:
                    self.logger.info("服务器已停止")
                    print("\n\n🛑 服务器已停止")
                    return True
        except OSError as e:
            if e.errno == 48:  # Address already in use
                self.logger.error(f"端口 {self.port} 已被占用")
                print(f"❌ 端口 {self.port} 已被占用，请尝试其他端口")
                return False
            else:
                self.logger.error(f"启动服务器失败: {e}")
                print(f"❌ 启动服务器失败: {e}")
                return False
        except Exception as e:
            self.logger.error(f"服务器运行出错: {e}", exc_info=True)
            print(f"❌ 服务器运行出错: {e}")
            return False
    
    def _check_required_files(self) -> bool:
        """检查必要文件是否存在"""
        required_files = [
            'index.html', 'styles.css', 'app.js',
            'dayansifa-core.js', 'hexagram-database.js'
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.logger.error(f"缺少必要文件: {missing_files}")
            print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
            return False
        
        return True
    
    def _print_startup_info(self, url: str):
        """打印启动信息"""
        project_dir = Path(__file__).parent
        
        print("🌟" + "=" * 60)
        print("🔮 大衍筮法 Web 版本服务器已启动 (增强版)")
        print("=" * 62)
        print(f"📍 服务器地址: {url}")
        print(f"📁 服务目录: {project_dir}")
        print(f"🚀 版本: {config.PROJECT_VERSION}")
        print("=" * 62)
        print("💡 可用功能:")
        print("   - 🎯 传统占卜界面")
        print("   - 🔌 API接口支持")
        print("   - 📊 性能监控")
        print("   - 📝 详细日志")
        print("   - 💾 智能缓存")
        print("=" * 62)
        print("🔗 API端点:")
        print(f"   - POST {url}/api/divination  # 执行占卜")
        print(f"   - GET  {url}/api/config      # 获取配置")
        print(f"   - GET  {url}/api/stats       # 获取统计")
        print(f"   - GET  {url}/api/health      # 健康检查")
        print(f"   - GET  {url}/api/history     # 获取历史")
        print(f"   - POST {url}/api/export      # 导出数据")
        print(f"   - GET  {url}/api/language    # 语言管理")
        print("=" * 62)
        print("💡 使用说明:")
        print("   - 在浏览器中访问上述地址")
        print("   - 按 Ctrl+C 停止服务器")
        print("   - 查看 logs/ 目录获取详细日志")
        print("=" * 62)
    
    def _open_browser(self, url: str):
        """打开浏览器"""
        print("🚀 正在打开浏览器...")
        try:
            webbrowser.open(url)
            print("✅ 浏览器已打开")
            self.logger.info("浏览器已自动打开")
        except Exception as e:
            self.logger.warning(f"无法自动打开浏览器: {e}")
            print(f"⚠️  无法自动打开浏览器: {e}")
            print(f"   请手动在浏览器中访问: {url}")
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            self.logger.info("服务器已停止")
            print("🛑 服务器已停止")


def check_environment() -> bool:
    """检查运行环境"""
    logger = get_logger("environment")
    
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        logger.error(f"Python版本过低: {python_version.major}.{python_version.minor}")
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("   建议使用Python 3.6+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    logger.info(f"Python版本检查通过: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查项目文件
    project_files = {
        'index.html': 'HTML主页面',
        'styles.css': 'CSS样式文件',
        'app.js': '主应用逻辑',
        'dayansifa-core.js': '大衍筮法核心算法',
        'hexagram-database.js': '卦象数据库',
        'config.py': '配置管理',
        'logger.py': '日志管理',
        'performance.py': '性能监控'
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
        logger.error(f"缺少文件: {missing_files}")
        print(f"❌ 缺少文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # 创建必要目录
    for directory in ['logs', 'cache']:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 目录: {directory}")
    
    logger.info("环境检查完成")
    return True


def show_usage():
    """显示使用说明"""
    print(f"""
🌟 大衍筮法 Web 版本启动器 (增强版 v{config.PROJECT_VERSION})

用法:
    python webserver_v2.py [选项]

选项:
    -p, --port PORT     指定端口号 (默认: {config.WEB_SERVER_PORT})
    -H, --host HOST     指定主机地址 (默认: {config.WEB_SERVER_HOST})
    --no-browser        不自动打开浏览器
    --help              显示此帮助信息

示例:
    python webserver_v2.py                    # 使用默认设置
    python webserver_v2.py -p 3000           # 使用端口3000
    python webserver_v2.py -H 0.0.0.0        # 允许外部访问
    python webserver_v2.py --no-browser      # 不打开浏览器

新功能:
    🔌 API接口支持        - 提供RESTful API
    📊 性能监控          - 实时性能统计
    📝 详细日志          - 完整的操作记录
    💾 智能缓存          - 自动结果缓存
    🛡️  错误处理          - 完善的错误处理机制
    """)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description=f'大衍筮法 Web 版本服务器 v{config.PROJECT_VERSION}')
    parser.add_argument('-p', '--port', type=int, default=config.WEB_SERVER_PORT, 
                       help=f'端口号 (默认: {config.WEB_SERVER_PORT})')
    parser.add_argument('-H', '--host', default=config.WEB_SERVER_HOST, 
                       help=f'主机地址 (默认: {config.WEB_SERVER_HOST})')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 启动服务器
    server = EnhancedWebServer(args.port, args.host)
    success = server.start(auto_open=not args.no_browser)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()