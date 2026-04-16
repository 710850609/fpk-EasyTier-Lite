#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Build Script for UOS/统信OS - 静态链接 GTK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
GUI_DIR = Path(__file__).parent.absolute()
BUILD_DIR = GUI_DIR / "build"
DIST_DIR = GUI_DIR / "dist"

def run_command(cmd, cwd=None):
    """Execute command"""
    print(f"Execute: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd or str(GUI_DIR),
            capture_output=True, text=True, encoding='utf-8'
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        if result.stdout:
            print(result.stdout)
        return True
    except Exception as e:
        print(f"Command failed: {e}")
        return False

def build_static():
    """Build with static linking"""
    print("=" * 50)
    print("Building static binary for UOS...")
    print("=" * 50)
    
    # Clean
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    # Install dependencies
    print("[1/3] Installing dependencies...")
    run_command("pip install pyinstaller pystray pillow staticx")
    
    # Build with PyInstaller
    print("[2/3] Building with PyInstaller...")
    platform_name = "linux-x64"
    output_name = f"EasyTierLite-Tray-{platform_name}"
    
    icon_path = GUI_DIR / "icon.png"
    if not icon_path.exists():
        icon_path = PROJECT_ROOT / "frontend" / "icon.png"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", output_name,
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--hidden-import", "pystray._appindicator",
        "--hidden-import", "PIL._tkinter_finder",
    ]
    
    if icon_path.exists():
        cmd.extend(["--add-data", f"{icon_path}{os.pathsep}."])
    
    cmd.append(str(GUI_DIR / "stray.py"))
    
    if not run_command(" ".join(cmd)):
        print("[Error] PyInstaller failed")
        return False
    
    # Static link with staticx
    print("[3/3] Static linking with staticx...")
    source = DIST_DIR / output_name
    target = DIST_DIR / f"{output_name}-static"
    
    # Install staticx dependencies
    run_command("apt-get update && apt-get install -y patchelf")
    
    staticx_cmd = f"staticx --strip {source} {target}"
    if not run_command(staticx_cmd):
        print("[Warning] staticx failed, using non-static binary")
        shutil.copy2(source, target)
    
    # Copy to output
    output_dir = PROJECT_ROOT / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    final_target = output_dir / f"{output_name}-uos"
    shutil.copy2(target, final_target)
    
    print("=" * 50)
    print(f"Build complete: {final_target}")
    print("=" * 50)
    return True

if __name__ == "__main__":
    if sys.platform != "linux":
        print("Static build is for Linux only")
        sys.exit(1)
    
    if not build_static():
        sys.exit(1)
