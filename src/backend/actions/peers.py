#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
from pathlib import Path

import requests
import tomlkit

import utils.check_peers as check_util
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


def check_peers(*kwargs):
    """
    检查节点是否可用
    :param request_data: 请求数据（可选）
    """
    peer_list = public_peers(data = {'refresh': False})
    if (len(peer_list) == 0):
        peer_list = public_peers(data = {'refresh': True})
    # 提取 URI 列表
    peer_uris = [peer['uri'] for peer in peer_list]
    result = check_util.check_peers(ET_BIN_DIR, peer_uris, max_wait_second=6)
    for peer in peer_list:
        if peer['uri'] in result['success']:
            peer['status'] = 1
        else:
            peer['status'] = 0
    return peer_list


def public_peers(data, *kwargs):
    refresh = data and 'refresh' in data and data['refresh'] or False
    peer_meta = __get_public_peers(refresh)
    peer_uris = []
    if Path(ET_CONFIG_FILE).exists():
        try:
            with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
                doc = tomlkit.parse(f.read())
                for i in (doc.get("peer") or []):
                    peer_uris.append(i["uri"])
        except Exception as e:
            logging.error(f"解析配置文件失败: {e}")
            # 配置文件解析失败时，返回空列表，不影响获取公共节点
            pass
    config_peers_set = set(peer_uris)

    for key, item in peer_meta["peers"].items():
        peer = f"{key}"
        # 过滤未启用：空uri
        if peer not in config_peers_set and len(item.get('uri').strip()) > 0:
            peer_uris.append(peer)
    peers = []
    for uri in peer_uris:
        label = uri
        peers.append({'label': label, 'uri': uri})
    return peers


def __get_public_peers(refresh=False):
    if refresh or not Path(ET_PEER_META_FILE).exists():
        return __download_peer_meta()
    else:
        with open(ET_PEER_META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def __download_peer_meta():
    try:
        github_proxy = github_util.get_github_proxy()
        peer_meta_url = f"https://raw.githubusercontent.com/710850609/EasyTier-Lite/refs/heads/main/peers/peer-txt-meta.json"
        if github_proxy and github_proxy != '':
            peer_meta_url = f"{github_proxy}/{peer_meta_url}"
        response = requests.get(peer_meta_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        with open(ET_PEER_META_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        return data
    except Exception as e:
        logging.error(f"获取节点元数据失败: {e}")
        raise    