#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sys
from pathlib import Path
from typing import Union, Optional

from backend.http_dispatcher.dispatcher import HttpException
from utils import check_peers
from utils import process_util
from utils import run_configs
from utils.process_util import ProcessManager

# 延迟初始化：使用单例模式
_pm = {}

def _get_process_manager(profile:str = None) -> Union[ProcessManager]:
    """获取 ProcessManager 实例（延迟初始化）"""
    global _pm
    pm_key = 'default' if profile is None else profile
    cur_pm = _pm.get(pm_key)
    if cur_pm is None:
        pid_file = run_configs.et_pid_file(profile)
        cur_pm = process_util.ProcessManager(pid_file)
        _pm[pm_key] = cur_pm
    return cur_pm

def status(profile:str = None, *kwargs):
    pm = _get_process_manager(profile)
    running = pm.status()
    return {'running': running}

def stop(profile:str = None, *kwargs):
    logging.info('停止ET服务')
    pm = _get_process_manager(profile)
    pm.stop()

def start(profile:str = None, *kwargs):
    logging.info('启动ET服务')
    config_file = run_configs.et_config_file(profile)
    if not Path(config_file).exists():
        raise HttpException(f"不存在配置文件，请先确认配置")
    core_dir = run_configs.core_dir()
    ext = '.exe' if sys.platform == 'win32' else ''
    rpc_port = check_peers.get_available_port()
    cmd = f"{core_dir}/easytier-core{ext} --config-file {config_file} --rpc-portal 0.0.0.0:{rpc_port}"
    logging.info(f"启动命令: {cmd}")
    pm = _get_process_manager(profile)
    pm.start(cmd)


def restart(profile:str = None, *kwargs):
    pm = _get_process_manager(profile)
    logging.info(f"重启ET服务...")
    # restart_flag_file = run_configs.et_restart_flag_file()
    # try:
    if pm.status():
        logging.info(f"停止ET服务...")
        # Path(restart_flag_file).touch()
        pm.stop()
    logging.info(f"启动ET服务...")
    start()
        # Path(restart_flag_file).touch()
    # finally:
        # Path(restart_flag_file).unlink(missing_ok=True)

def start_all(*kwargs):
    start(*kwargs)

def stop_all(*kwargs):
    stop(*kwargs)

def _get_start_cmd(profile:str = None) -> Optional[str]:
    config_file = run_configs.et_config_file(profile)
    if not Path(config_file).exists():
        logging.info(f"配置文件不存在，跳过生成启动命令: {config_file}")
        return None
    core_dir = run_configs.core_dir()
    ext = '.exe' if sys.platform == 'win32' else ''
    rpc_port = check_peers.get_available_port()
    return f"{core_dir}/easytier-core{ext} --config-file {config_file} --rpc-portal 127.0.0.1:{rpc_port}"
