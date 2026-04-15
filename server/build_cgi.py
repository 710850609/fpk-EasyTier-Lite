#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyTier-Lite Server 多平台打包脚本
支持: Windows(x64), Linux(x64/arm64), 统信UOS(x64/arm64)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SERVER_DIR = Path(__file__).parent.absolute()
BUILD_DIR = SERVER_DIR / "build"
DIST_DIR = SERVER_DIR / "dist"

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    print(f"执行: {cmd}")
    try:
        # Windows 使用 utf-8 编码
        encoding = 'utf-8' if sys.platform == "win32" else None
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding=encoding, errors='replace')
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True

def clean_build():
    """清理构建目录"""
    print("[1/5] 清理构建目录...")
    for dir_name in ["build", "dist"]:
        dir_path = SERVER_DIR / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  删除 {dir_name}")

def install_deps():
    """安装依赖"""
    print("[2/5] 安装依赖...")
    deps = ["pyinstaller", "tomlkit", "requests"]
    mirror = "-i https://pypi.tuna.tsinghua.edu.cn/simple"
    # 使用 --break-system-packages 绕过系统保护（Python 3.11+）
    return run_command(f"pip install {' '.join(deps)} {mirror} --break-system-packages")

def get_platform_name():
    """获取平台名称"""
    system = sys.platform
    machine = os.uname().machine if hasattr(os, 'uname') else 'unknown'
    
    if system == "win32":
        return "windows-x64"
    elif system == "linux":
        if "arm" in machine.lower() or "aarch64" in machine.lower():
            return "linux-arm64"
        return "linux-x64"
    elif system == "darwin":
        return "macos-x64"
    return f"{system}-{machine}"

def build_executable():
    """构建可执行文件"""
    print("[3/5] 开始打包...")
    
    platform_name = get_platform_name()
    output_name = f"cgi"
    
    # 根据平台选择分隔符
    separator = ";" if sys.platform == "win32" else ":"
    
    # PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 单文件
        "--clean",    # 清理缓存
        "--name", output_name,
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(SERVER_DIR),
        "--hidden-import", "tomlkit",
        "--hidden-import", "requests",
        "--hidden-import", "action.config",
        "--hidden-import", "action.et_core",
        "--hidden-import", "action.monitor",
        "--hidden-import", "action.peers",
        "--hidden-import", "action.services",
        "--hidden-import", "action.settings",
        "--hidden-import", "action.windows",
        "--hidden-import", "util.check_peers",
        "--hidden-import", "util.common_util",
        "--hidden-import", "util.et_util",
        "--hidden-import", "util.github_util",
        "--hidden-import", "util.http_util",
        "--hidden-import", "util.process_util",
        "--add-data", f"{SERVER_DIR}/action{separator}action",
        "--add-data", f"{SERVER_DIR}/util{separator}util",
        str(SERVER_DIR / "cgi.py")
    ]
    
    # Windows 特定选项
    if sys.platform == "win32":
        cmd.extend(["--console"])
    
    result = run_command(" ".join(cmd), cwd=str(SERVER_DIR))
    return result, output_name

def copy_output(output_name):
    """复制输出文件"""
    print("[4/5] 复制输出文件...")
    
    # 确定可执行文件扩展名
    ext = ".exe" if sys.platform == "win32" else ""
    source = DIST_DIR / f"{output_name}{ext}"
    
    # 创建输出目录
    output_dir = PROJECT_ROOT / "EasyTier-Lite" / "app" / "ui"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    if source.exists():
        target = output_dir / f"cgi{ext}"
        shutil.copy2(source, target)
        print(f"  复制到: {target}")
        return True
    else:
        print(f"  未找到: {source}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("EasyTier-Lite Server 多平台打包")
    print(f"当前平台: {get_platform_name()}")
    print("=" * 50)
    
    # 检查 Python
    if sys.version_info < (3, 8):
        print("[错误] 需要 Python 3.8+")
        sys.exit(1)
    
    # 执行构建步骤
    clean_build()
    
    if not install_deps():
        print("[错误] 依赖安装失败")
        sys.exit(1)
    
    result, output_name = build_executable()
    if not result:
        print("[错误] 打包失败")
        sys.exit(1)
    
    if not copy_output(output_name):
        print("[错误] 复制文件失败")
        sys.exit(1)
    
    print("=" * 50)
    print("打包完成!")
    print(f"输出: EasyTier-Lite/app/bin/EasyTierLite-Server")
    print("=" * 50)

if __name__ == "__main__":
    main()
