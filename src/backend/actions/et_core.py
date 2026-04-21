#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import platform
import shutil
import sys
import time
import zipfile
from pathlib import Path

import actions.services as et_service
import utils.common_util as common_util
import utils.github_util as github_util
import utils.http_util as http_util

TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
TRIM_SHARE_DIR = os.getenv('TRIM_SHARE_DIR', f'/var/apps/{TRIM_APPNAME}/shares/{TRIM_APPNAME}')

ET_BIN_DIR = os.getenv('ET_BIN_DIR', f"{TRIM_APPDEST}/bin")
CONFIG_DIR = os.getenv('CONFIG_DIR', f"{TRIM_SHARE_DIR}/bin")
DATA_DIR = os.getenv('DATA_DIR', f"{TRIM_PKGVAR}/bin")

ET_CONFIG_FILE = f'{CONFIG_DIR}/config.toml'
ET_CONFIG_INIT_FILE = f'{DATA_DIR}/.init'
ET_PEER_META_FILE = f'{DATA_DIR}/peer-txt-meta.json'
ET_PID_FILE = f'{DATA_DIR}/app.pid'
ET_RESTART_FLAG_FILE = f'{DATA_DIR}/.restart'
GITHUB_PROXY_FILE = f"{DATA_DIR}/github_proxy_url.txt"
START_CMD = f"{ET_BIN_DIR}/easytier-core --config-file {ET_CONFIG_FILE}"


def version(*kwargs):
    cmd = f'{ET_BIN_DIR}/easytier-core --version'
    if sys.platform == 'win32':
        cmd = f"{ET_BIN_DIR}/easytier-core.exe --version"
    raw_version = common_util.run_cmd(cmd)
    raw_version = raw_version.replace('easytier-core ', '')
    version = raw_version[:raw_version.index('-')]
    return { 'version': f'v{version}', 'raw_version': raw_version }

def install(data, *kwargs):
    version = data['version']
    if not version:
        http_util.http_response_error('版本不能为空')

    arch = __get_arch()
    platform = 'linux' if sys.platform == 'linux' else ('windows' if sys.platform == 'win32' else 'macos')
    url = f"https://github.com/easyTier/easytier/releases/download/{version}/easytier-{platform}-{arch}-{version}.zip"
    logging.info(f"内核下载地址: {url}")
    zip_file = f'{ET_BIN_DIR}/easytier-{platform}-{arch}-{version}.zip'
    github_util.download_file(url, zip_file)
    unzip_temp_dir = __unzip(zip_file, f'{ET_BIN_DIR}')
    et_service.stop()
    for item in Path(f'{unzip_temp_dir}/easytier-{platform}-{arch}').iterdir():
        shutil.move(str(item), f'{ET_BIN_DIR}/{item.name}')
        logging.info(f"移动: {item.name}")
    Path(zip_file).unlink()
    shutil.rmtree(unzip_temp_dir)
    et_service.start()
    return f'安装{version}版本成功'

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