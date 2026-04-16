#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build AppImage for Linux (包含所有依赖)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
GUI_DIR = Path(__file__).parent.absolute()
BUILD_DIR = GUI_DIR / "build_appimage"
APPDIR = BUILD_DIR / "AppDir"

def run_command(cmd, cwd=None):
    print(f"Execute: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or str(GUI_DIR),
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True

def build_appimage():
    """Build AppImage"""
    print("=" * 50)
    print("Building AppImage...")
    print("=" * 50)
    
    # Clean
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)
    APPDIR.mkdir()
    
    # Create AppDir structure
    print("[1/4] Creating AppDir...")
    
    # Desktop entry
    desktop_content = """[Desktop Entry]
Name=EasyTierLite Tray
Exec=AppRun
Icon=icon
Type=Application
Categories=Network;
"""
    (APPDIR / "EasyTierLite-Tray.desktop").write_text(desktop_content)
    
    # AppRun script
    apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/lib/python3.7/site-packages:${PYTHONPATH}"
exec "${HERE}/usr/bin/python3" "${HERE}/usr/bin/stray.py" "$@"
"""
    apprun_path = APPDIR / "AppRun"
    apprun_path.write_text(apprun_content)
    apprun_path.chmod(0o755)
    
    # Copy icon
    icon_src = GUI_DIR / "icon.png"
    if not icon_src.exists():
        icon_src = PROJECT_ROOT / "frontend" / "icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, APPDIR / "icon.png")
    
    # Build with PyInstaller first
    print("[2/4] Building with PyInstaller...")
    run_command("pip install pyinstaller pystray pillow")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "stray",
        "--distpath", str(APPDIR / "usr" / "bin"),
        "--workpath", str(BUILD_DIR / "pyinstaller"),
        "--hidden-import", "pystray._appindicator",
        "--hidden-import", "PIL._tkinter_finder",
        str(GUI_DIR / "stray.py")
    ]
    
    if not run_command(" ".join(cmd)):
        print("[Error] PyInstaller failed")
        return False
    
    # Download appimagetool
    print("[3/4] Downloading appimagetool...")
    appimagetool_url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    appimagetool_path = BUILD_DIR / "appimagetool.AppImage"
    
    run_command(f"curl -L -o {appimagetool_path} {appimagetool_url}")
    run_command(f"chmod +x {appimagetool_path}")
    
    # Build AppImage
    print("[4/4] Creating AppImage...")
    output_name = "EasyTierLite-Tray-x86_64.AppImage"
    output_path = PROJECT_ROOT / "dist" / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use fuse workaround for Docker
    env_vars = "ARCH=x86_64"
    if os.path.exists("/.dockerenv"):
        env_vars += " APPIMAGE_EXTRACT_AND_RUN=1"
    
    cmd = f"{env_vars} {appimagetool_path} {APPDIR} {output_path}"
    if not run_command(cmd):
        print("[Warning] appimagetool failed, trying alternative method")
        return False
    
    print("=" * 50)
    print(f"AppImage created: {output_path}")
    print("=" * 50)
    return True

if __name__ == "__main__":
    if sys.platform != "linux":
        print("AppImage build is for Linux only")
        sys.exit(1)
    
    if not build_appimage():
        sys.exit(1)
