#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys
from pathlib import Path

import utils.process_util as process_util

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

if sys.platform == 'win32':
    START_CMD = f"{ET_BIN_DIR}/easytier-core.exe --config-file {ET_CONFIG_FILE}"


# 延迟初始化：使用单例模式
_pm = None

def _get_process_manager():
    """获取 ProcessManager 实例（延迟初始化）"""
    global _pm
    logging.info(f"START_CMD: {START_CMD}")
    logging.info(f"ET_PID_FILE: {ET_PID_FILE}")
    if _pm is None:
        _pm = process_util.ProcessManager(START_CMD, ET_PID_FILE)
    return _pm

def status(*kwargs):
    pm = _get_process_manager()
    running = pm.status()
    return {'running': running}

def stop(*kwargs):
    logging.info('停止ET服务')
    pm = _get_process_manager()
    pm.stop()

def start(*kwargs):
    logging.info('启动ET服务')
    pm = _get_process_manager()
    pm.start()

def restart(*kwargs):
    pm = _get_process_manager()
    logging.info(f"重启ET服务...")
    try:
        if pm.status():
            logging.info(f"停止ET服务...")
            Path(ET_RESTART_FLAG_FILE).touch()
            pm.stop()
        logging.info(f"启动ET服务...")
        pm.start()
        Path(ET_RESTART_FLAG_FILE).touch()
    finally:
        Path(ET_RESTART_FLAG_FILE).unlink(missing_ok=True)