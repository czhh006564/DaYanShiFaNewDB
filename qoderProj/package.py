#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序打包脚本
生成可分发的程序包，支持多种格式和平台
"""

import os
import sys
import zipfile
import tarfile
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 项目信息
PROJECT_NAME = "大衍筮法"
PROJECT_VERSION = "2.0.0"
PROJECT_DESCRIPTION = "数字化周易大衍筮法占卜程序"


class PackageBuilder:
    """打包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        # 确保目录存在
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def clean_build(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        print("✅ 构建目录已清理")
    
    def get_file_list(self) -> List[Path]:
        """获取需要打包的文件列表"""
        include_patterns = [
            "*.py", "*.js", "*.html", "*.css", "*.md",
            "requirements.txt", "Dockerfile", "docker-compose.yml",
            ".github/workflows/*.yml"
        ]
        
        exclude_patterns = [
            "__pycache__", "*.pyc", "*.pyo", 
            "logs/*", "data/*", "exports/*", "cache/*",
            "build/*", "dist/*", ".git*"
        ]
        
        files = []
        
        # 收集所有文件
        for pattern in include_patterns:
            if "/" in pattern:
                # 处理子目录模式
                parts = pattern.split("/")
                base_dir = Path(parts[0])
                file_pattern = "/".join(parts[1:])
                if base_dir.exists():
                    files.extend(base_dir.glob(file_pattern))
            else:
                files.extend(self.project_root.glob(pattern))
        
        # 过滤排除的文件
        filtered_files = []
        for file in files:
            skip = False
            relative_path = file.relative_to(self.project_root)
            
            for exclude in exclude_patterns:
                if exclude.endswith("*"):
                    if str(relative_path).startswith(exclude[:-1]):
                        skip = True
                        break
                elif exclude in str(relative_path):
                    skip = True
                    break
            
            if not skip and file.is_file():
                filtered_files.append(file)
        
        return filtered_files
    
    def create_source_package(self, format_type: str = "zip") -> str:
        """创建源码包"""
        print(f"📦 创建源码包 ({format_type})...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"dayansifa-source-v{PROJECT_VERSION}-{timestamp}"
        
        files = self.get_file_list()
        
        if format_type == "zip":
            package_path = self.dist_dir / f"{package_name}.zip"
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in files:
                    relative_path = file.relative_to(self.project_root)
                    zf.write(file, f"{package_name}/{relative_path}")
                
                # 添加版本信息文件
                version_info = self._get_version_info()
                zf.writestr(f"{package_name}/VERSION.txt", version_info)
        
        elif format_type == "tar.gz":
            package_path = self.dist_dir / f"{package_name}.tar.gz"
            
            with tarfile.open(package_path, 'w:gz') as tf:
                for file in files:
                    relative_path = file.relative_to(self.project_root)
                    tf.add(file, f"{package_name}/{relative_path}")
                
                # 添加版本信息文件
                version_info = self._get_version_info()
                info = tarfile.TarInfo(f"{package_name}/VERSION.txt")
                info.size = len(version_info.encode('utf-8'))
                tf.addfile(info, io.BytesIO(version_info.encode('utf-8')))
        
        else:
            raise ValueError(f"不支持的格式: {format_type}")
        
        print(f"✅ 源码包已创建: {package_path}")
        return str(package_path)
    
    def create_executable_package(self, platform: str = "current") -> Optional[str]:
        """创建可执行程序包"""
        print(f"🔧 创建可执行程序包 ({platform})...")
        
        try:
            import PyInstaller
        except ImportError:
            print("❌ PyInstaller 未安装，跳过可执行程序包创建")
            print("   安装命令: pip install pyinstaller")
            return None
        
        # 创建临时spec文件
        spec_content = self._generate_pyinstaller_spec()
        spec_path = self.build_dir / "dayansifa.spec"
        
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        # 运行PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean", "--noconfirm",
            str(spec_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            
            # 查找生成的可执行文件
            exe_dir = self.project_root / "dist" / "dayansifa"
            if exe_dir.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                package_name = f"dayansifa-executable-v{PROJECT_VERSION}-{platform}-{timestamp}"
                package_path = self.dist_dir / f"{package_name}.zip"
                
                # 打包可执行文件
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file in exe_dir.rglob("*"):
                        if file.is_file():
                            relative_path = file.relative_to(exe_dir)
                            zf.write(file, f"{package_name}/{relative_path}")
                
                print(f"✅ 可执行程序包已创建: {package_path}")
                return str(package_path)
            else:
                print("❌ 未找到生成的可执行文件")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller 执行失败: {e}")
            return None
    
    def create_docker_package(self) -> str:
        """创建Docker包"""
        print("🐳 创建Docker包...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"dayansifa-docker-v{PROJECT_VERSION}-{timestamp}"
        package_path = self.dist_dir / f"{package_name}.tar.gz"
        
        # 包含Docker相关文件
        docker_files = [
            "Dockerfile",
            "docker-compose.yml", 
            "deploy.sh",
            "requirements.txt"
        ]
        
        # 获取所有应用文件
        app_files = self.get_file_list()
        
        with tarfile.open(package_path, 'w:gz') as tf:
            # 添加应用文件
            for file in app_files:
                relative_path = file.relative_to(self.project_root)
                tf.add(file, f"{package_name}/{relative_path}")
            
            # 添加Docker文件
            for docker_file in docker_files:
                file_path = self.project_root / docker_file
                if file_path.exists():
                    tf.add(file_path, f"{package_name}/{docker_file}")
            
            # 添加部署说明
            deploy_readme = self._get_docker_readme()
            info = tarfile.TarInfo(f"{package_name}/DOCKER_README.md")
            info.size = len(deploy_readme.encode('utf-8'))
            tf.addfile(info, io.BytesIO(deploy_readme.encode('utf-8')))
        
        print(f"✅ Docker包已创建: {package_path}")
        return str(package_path)
    
    def _get_version_info(self) -> str:
        """获取版本信息"""
        git_commit = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True
            )
            git_commit = result.stdout.strip()
        except:
            pass
        
        return f"""大衍筮法 - 数字化周易占卜程序
版本: {PROJECT_VERSION}
构建时间: {datetime.now().isoformat()}
Git提交: {git_commit}
Python版本: {sys.version}

项目描述:
{PROJECT_DESCRIPTION}

使用说明:
1. 安装Python 3.6+
2. 安装依赖: pip install -r requirements.txt
3. 运行命令行版本: python dayansifa_v2.py
4. 运行Web版本: python webserver_v2.py
5. 快速启动: python quick_start.py

更多信息请查看README.md文件。
"""
    
    def _get_docker_readme(self) -> str:
        """获取Docker部署说明"""
        return f"""# 大衍筮法 Docker 部署包

版本: {PROJECT_VERSION}
构建时间: {datetime.now().isoformat()}

## 快速开始

### 使用 Docker Compose (推荐)
```bash
docker-compose up -d
```

### 使用 Docker 命令
```bash
# 构建镜像
docker build -t dayansifa:latest .

# 运行容器
docker run -d -p 8080:8080 --name dayansifa dayansifa:latest
```

### 使用部署脚本
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

## 访问应用

- Web界面: http://localhost:8080
- API健康检查: http://localhost:8080/api/health
- API统计信息: http://localhost:8080/api/stats

## 常用命令

```bash
# 查看容器状态
docker ps

# 查看应用日志
docker logs dayansifa

# 进入容器
docker exec -it dayansifa bash

# 停止服务
docker stop dayansifa

# 清理资源
docker rm dayansifa
docker rmi dayansifa:latest
```

## 配置环境变量

- `DAYANSIFA_ENV`: 运行环境 (production, development, testing)
- `DAYANSIFA_WEB_SERVER_HOST`: 服务器主机 (默认: 0.0.0.0)
- `DAYANSIFA_WEB_SERVER_PORT`: 服务器端口 (默认: 8080)
- `DAYANSIFA_ENABLE_CACHE`: 启用缓存 (默认: true)
- `DAYANSIFA_LOG_LEVEL`: 日志级别 (默认: INFO)

更多信息请查看项目文档。
"""
    
    def _generate_pyinstaller_spec(self) -> str:
        """生成PyInstaller spec文件"""
        return f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['quick_start.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('*.html', '.'),
        ('*.css', '.'),
        ('*.js', '.'),
        ('*.md', '.'),
    ],
    hiddenimports=[
        'dayansifa_v2',
        'webserver_v2', 
        'config',
        'logger',
        'performance',
        'history',
        'i18n',
        'export_tools'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dayansifa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dayansifa',
)
"""


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='大衍筮法程序打包工具')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    parser.add_argument('--source', action='store_true', help='创建源码包')
    parser.add_argument('--executable', action='store_true', help='创建可执行程序包')
    parser.add_argument('--docker', action='store_true', help='创建Docker包')
    parser.add_argument('--all', action='store_true', help='创建所有类型的包')
    parser.add_argument('--format', choices=['zip', 'tar.gz'], default='zip', help='源码包格式')
    
    args = parser.parse_args()
    
    builder = PackageBuilder()
    
    # 如果没有指定任何选项，显示帮助
    if not any([args.clean, args.source, args.executable, args.docker, args.all]):
        parser.print_help()
        return
    
    print(f"🌟 {PROJECT_NAME} 打包工具")
    print(f"版本: {PROJECT_VERSION}")
    print("=" * 50)
    
    if args.clean or args.all:
        builder.clean_build()
    
    packages = []
    
    if args.source or args.all:
        package_path = builder.create_source_package(args.format)
        packages.append(package_path)
    
    if args.executable or args.all:
        package_path = builder.create_executable_package()
        if package_path:
            packages.append(package_path)
    
    if args.docker or args.all:
        package_path = builder.create_docker_package()
        packages.append(package_path)
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📦 打包完成！")
    print(f"生成的包数量: {len(packages)}")
    
    for package in packages:
        package_path = Path(package)
        size_mb = package_path.stat().st_size / (1024 * 1024)
        print(f"  📄 {package_path.name} ({size_mb:.1f} MB)")
    
    print(f"\n📁 输出目录: {builder.dist_dir}")


if __name__ == "__main__":
    main()