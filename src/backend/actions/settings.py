#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path

import utils.http_util as http_util
from http_dispatcher.dispatcher import HttpException
from utils import run_configs


def save_github_mirror(data, *kwargs):
    url = data['url'] or ''
    try:
        github_proxy_file = run_configs.github_proxy_file()
        cfg_path = Path(github_proxy_file)
        cfg_path.write_text(url.strip())
        http_util.http_response_ok('保存成功')
    except Exception as e:
        logging.error(f"保存代理配置失败: {e}")
        raise HttpException(f"保存代理配置失败: {e}") from e

def github_mirrors(*kwargs):
    try:
        github_proxy_file = run_configs.github_proxy_file()
        selected = ''
        cfg_path = Path(github_proxy_file)
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
