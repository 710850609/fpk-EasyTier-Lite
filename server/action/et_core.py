#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import util.http_util as http_util
import util.common_util as common_util
import util.github_util as github_util
import action.services as et_service
import logging
import os
import platform
import zipfile
import time
import shutil


TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
TRIM_SHARE_DIR = os.getenv('TRIM_SHARE_DIR', f'/var/apps/{TRIM_APPNAME}/shares/{TRIM_APPNAME}')

ET_CONFIG_FILE = f'{TRIM_SHARE_DIR}/config.toml'
ET_CONFIG_INIT_FILE = f'{TRIM_PKGVAR}/.init'
ET_BIN_DIR = f"{TRIM_APPDEST}/bin"

GITHUB_PROXY = "https://ghfast.top"

def version(*kwargs):
    raw_version = common_util.run_cmd(f'{ET_BIN_DIR}/easytier-core --version')
    raw_version = raw_version.replace('easytier-core ', '')
    version = raw_version[:raw_version.index('-')]
    http_util.http_response_ok({ 'version': f'v{version}', 'raw_version': raw_version })
    # http_util.http_response_ok({ 'version': f'v2.6.0', 'raw_version': raw_version })

def install(data, *kwargs):
    version = data['version']
    if not version:
        http_util.http_response_error('版本不能为空')

    arch = __get_arch()
    url = f"https://github.com/easyTier/easytier/releases/download/{version}/easytier-linux-{arch}-{version}.zip"
    logging.info(f"内核下载地址: {url}")
    zip_file = f'{ET_BIN_DIR}/easytier-linux-{arch}-{version}.zip'
    github_util.download_file(url, zip_file)
    unzip_temp_dir = __unzip(zip_file, f'{ET_BIN_DIR}')
    et_service.stop(http_response=False)
    shutil.copy2(f'{unzip_temp_dir}/easytier-linux-{arch}/easytier-core', f'{ET_BIN_DIR}/easytier-core')
    shutil.copy2(f'{unzip_temp_dir}/easytier-linux-{arch}/easytier-cli', f'{ET_BIN_DIR}/easytier-cli')
    Path(zip_file).unlink()
    shutil.rmtree(unzip_temp_dir)
    et_service.start(http_response=False)
    http_util.http_response_ok(f'安装{version}版本成功')

def __get_arch():
    machine = platform.machine()
    machine = machine.lower()
    arch_map = {
        'amd64': 'x86_64',
        'x86_64': 'x86_64',
        'aarch64': 'aarch64',
        'arm64': 'aarch64',  # macOS 叫 arm64，Linux 叫 aarch64
        'i386': 'x86',
        'i686': 'x86',
        'armv7l': 'armv7',
    }
    return arch_map.get(machine, machine)

def __unzip(zip_file, unzip_dir):    
    unzip_temp_dir = f"{unzip_dir}/{int(time.time())}"
    logging.info(f"解压: {zip_file} -> {unzip_temp_dir}")
    with zipfile.ZipFile(zip_file, 'r') as zf:
        # zf.extractall(unzip_temp_dir)
        for info in zf.infolist():
            # 🔴 关键：统一转换为系统分隔符，再处理
            # zipfile 读取的 filename 可能是 / 或 \，统一用 /
            normalized_path = info.filename.replace('\\', '/')            
            # 构建本地文件系统路径（自动适应 Windows/Unix）
            local_path = os.path.join(unzip_temp_dir, *normalized_path.split('/'))            
            if info.is_dir():
                os.makedirs(local_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with zf.open(info) as src, open(local_path, 'wb') as dst:
                    dst.write(src.read())
    logging.info(f"解压完成: {zip_file} -> {unzip_temp_dir}")
    return unzip_temp_dir