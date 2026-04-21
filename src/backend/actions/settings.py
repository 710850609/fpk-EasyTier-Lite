#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

import utils.http_util as http_util
from http_dispatcher.dispatcher import HttpException

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

def save_github_mirror(data, *kwargs):
    url = data['url'] or ''
    try:
        cfg_path = Path(GITHUB_PROXY_FILE)
        cfg_path.write_text(url.strip())
        http_util.http_response_ok('保存成功')
    except Exception as e:
        logging.error(f"保存代理配置失败: {e}")
        raise HttpException(f"保存代理配置失败: {e}") from e

def github_mirrors(*kwargs):
    try:
        selected = ''
        cfg_path = Path(GITHUB_PROXY_FILE);
        if cfg_path.exists():
            content = cfg_path.read_text().strip()
            # 去除空行
            lines = [l.strip() for l in content.split('\n') if l.strip()]
            selected = lines[0] if lines else ""
        sources = [
            { "value": "", "label": "不使用"},
            { "value": "https://gh-proxy.org", "label": "gh-proxy.org"},
            { "value": "https://ghfast.top", "label": "ghfast.top"},
            { "value": "https://ghproxy.net", "label": "ghproxy.net"},
            { "value": "https://gh.llkk.cc", "label": "gh.llkk.cc"},
            { "value": "https://gh.felicity.ac.cn", "label": "gh.felicity.ac.cn"},
        ]
        return { 'selected': selected, 'sources': sources }
    except Exception as e:
        logging.warning(f"读取代理配置失败: {e}")
        raise HttpException(f"读取代理配置失败: {e}") from e
