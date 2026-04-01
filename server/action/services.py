#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import util.http_util as http_util
import util.process_util as process_util
import os
import logging

TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
ET_CONFIG_FILE = f'{TRIM_PKGVAR}/config.toml'
ET_CONFIG_INIT_FILE = f'{TRIM_PKGVAR}/.init'
ET_PID_FILE = f'{TRIM_PKGVAR}/app.pid'
START_CMD = f"{TRIM_APPDEST}/easytier-core --config-file {ET_CONFIG_FILE}"


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
    http_util.http_response_ok({'running': running})

def stop(*kwargs):
    pm = _get_process_manager()
    pm.stop()
    http_util.http_response_ok({})

def start(*kwargs):
    pm = _get_process_manager()
    pm.start()
    http_util.http_response_ok({})

def restart(*kwargs):
    pm = _get_process_manager()
    if (pm.status()):
        pm.stop()
    pm.start()
    http_util.http_response_ok({})