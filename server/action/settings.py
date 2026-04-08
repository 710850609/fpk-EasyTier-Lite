#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import util.http_util as http_util
import logging
import os


TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
TRIM_SHARE_DIR = os.getenv('TRIM_SHARE_DIR', f'/var/apps/{TRIM_APPNAME}/shares/{TRIM_APPNAME}')

ET_CONFIG_FILE = f'{TRIM_SHARE_DIR}/config.toml'
ET_CONFIG_INIT_FILE = f'{TRIM_PKGVAR}/.init'
ET_BIN_DIR = f"{TRIM_APPDEST}/bin"

GITHUB_PROXY_FILE = f"{TRIM_APPDEST}/github_proxy_url.txt";

def save_github_mirror(data, *kwargs):
    url = data['url']
    if not url:
        http_util.http_response_error(f"请输入代理地址")
        return
    try:
        cfg_path = Path(GITHUB_PROXY_FILE)
        cfg_path.write_text(url.strip())
    except Exception as e:
        logging.error(f"保存代理配置失败: {e}")
        http_util.http_response_error(f"保存代理配置失败：{e}")
        return

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
            "https://ghfast.top",
            "https://gh.llkk.cc",
            "https://gh-proxy.org",
        ]
        http_util.http_response_ok({ 'selected': selected, 'sources': sources })
    except Exception as e:
        logging.warning(f"读取代理配置失败: {e}")
        http_util.http_response_error(f"读取代理配置失败：{e}")
