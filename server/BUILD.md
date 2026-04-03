# EasyTier-Lite Server 多平台构建指南

## 支持的平台

| 平台 | 架构 | 说明 |
|------|------|------|
| Windows | x64 | Windows 10/11 |
| Linux | x64 | 通用 Linux |
| Linux | arm64 | ARM64 架构 |
| 统信UOS | x64 | 国产操作系统 |
| 统信UOS | arm64 | 国产操作系统 ARM版 |

## 构建方法

### 方法一：本地构建（推荐）

在各平台上直接运行构建脚本：

```bash
# Linux/Mac
python3 server/build.py

# Windows
python server/build.py
```

### 方法二：交叉编译

#### 1. Windows 构建（在 Linux 上交叉编译）

安装 mingw-w64：
```bash
# Ubuntu/Debian
sudo apt-get install mingw-w64

# 使用 Docker 构建
docker run --rm -v $(pwd):/app -w /app/server \
  docker.io/cdrx/pyinstaller-windows:latest \
  python build.py
```

#### 2. Linux ARM64 构建（在 x64 上交叉编译）

```bash
# 安装 QEMU
sudo apt-get install qemu-user-static binfmt-support

# 使用 Docker 构建
docker run --rm --platform linux/arm64 -v $(pwd):/app -w /app/server \
  python:3.11-slim \
  bash -c "pip install pyinstaller tomlkit requests && python build.py"
```

### 方法三：GitHub Actions 自动构建

创建 `.github/workflows/build.yml`：

```yaml
name: Build Multi-Platform

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        arch: [x64]
        include:
          - os: ubuntu-latest
            arch: arm64
            platform: linux/arm64
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pyinstaller tomlkit requests
    
    - name: Build
      run: |
        cd server
        python build.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: EasyTierLite-Server-${{ matrix.os }}-${{ matrix.arch }}
        path: EasyTier-Lite/app/bin/
```

## 统信UOS 特定说明

### 在统信UOS 上本地构建

```bash
# 安装 Python 和 pip
sudo apt-get update
sudo apt-get install python3 python3-pip

# 安装依赖
pip3 install pyinstaller tomlkit requests -i https://pypi.tuna.tsinghua.edu.cn/simple

# 构建
cd server
python3 build.py
```

### 统信UOS 打包为 deb 包

创建 `debian/` 目录结构，使用 `dpkg-buildpackage` 打包。

## 输出文件

构建完成后，可执行文件位于：
```
EasyTier-Lite/app/bin/EasyTierLite-Server
```

## 注意事项

1. **Windows**: 构建后的 `.exe` 文件需要在 Windows 上运行
2. **Linux ARM64**: 需要在 ARM64 设备或使用 QEMU 模拟器构建
3. **统信UOS**: 基于 Debian，构建方法与 Linux 相同
4. **单文件**: PyInstaller 打包为单文件，启动时会解压到临时目录

## 常见问题

### Q: 如何在 Windows 上构建 Linux 版本？
A: 使用 WSL2 或 Docker 容器。

### Q: ARM64 构建失败？
A: 确保在 ARM64 设备上构建，或使用 QEMU 模拟器。

### Q: 文件太大？
A: 使用 UPX 压缩：
```bash
upx --best dist/EasyTierLite-Server
```
