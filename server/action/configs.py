#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import util.http_util as http_util
import logging
import tomlkit
import os

TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
TRIM_SHARE_DIR = os.getenv('TRIM_SHARE_DIR', f'/var/apps/{TRIM_APPNAME}/shares/{TRIM_APPNAME}')

ET_CONFIG_FILE = f'{TRIM_SHARE_DIR}/config.toml'
ET_CONFIG_INIT_FILE = f'{TRIM_PKGVAR}/.init'

GITHUB_PROXY = "https://ghfast.top"

def need_setting(*kwargs):
    need_config = Path(ET_CONFIG_INIT_FILE).exists()
    http_util.http_response_ok({"needConfig": need_config})

def save(data, *kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
    if not doc["network_identity"]:
        doc["network_identity"] = {"network_name": '', "network_secret": ''}
    __deep_merge(doc, data)
    
    with open(ET_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    Path(ET_CONFIG_INIT_FILE).unlink(missing_ok=True)
    http_util.http_response_ok('配置保存成功')

def save_toml(data: str, *kwargs):
    try:
        # 解析配置字符串
        doc = tomlkit.parse(data['toml'])
        with open(ET_CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(doc))
        Path(ET_CONFIG_INIT_FILE).unlink(missing_ok=True)
        http_util.http_response_ok('配置保存成功')    
    except Exception as e:
        logging.error(f"解析配置字符串失败: {e}")
        http_util.http_response_error(f"配置有误，请检查: {e}")

def get(*kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
    http_util.http_response_ok(doc)

def get_toml(*kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        http_util.http_response_ok(f.read())

def public_peers(*kwargs):
    peer_uris = []
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
        for i in (doc["peer"] or []):
            peer_uris.append(i["uri"])
    config_peers_set = set(peer_uris)
    for i in range(1, 6):
        peer = f'{GITHUB_PROXY}/https://raw.githubusercontent.com/710850609/fpk-EasyTier-Lite/refs/heads/main/peers/peer-{i}.txt'
        if peer not in config_peers_set:
            peer_uris.append(peer)
    peers = []
    for uri in peer_uris:
        label = uri.replace(f'{GITHUB_PROXY}/https://raw.githubusercontent.com/710850609/fpk-EasyTier-Lite/refs/heads/main/peers/peer-', '')
        if (len(label) != len(uri)):
            label = "动态节点" + label.replace('.txt', '')
        peers.append({'label': label, 'uri': uri})
    logging.info(f"{peers}")
    http_util.http_response_ok(peers)

def download(*kwargs):    
    tmp_file = copy()
    logging.info(f"{tmp_file}")
    http_util.http_response_file(tmp_file, filename="et-fnos.toml")

def copy(*kwargs): 
    tmp_file = '/tmp/EasyTier-Lite/config-copy.toml'
    
    # 确保目录存在
    os.makedirs(os.path.dirname(tmp_file), exist_ok=True)
    
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
    # 情况IP
    doc["ipv4"] = ""
    # 设置启用DHCP
    doc["dhcp"] = True

    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    return tmp_file


def __deep_merge(base, override):
    """深度合并两个字典，override 中的值会覆盖 base 中的值"""
    for key, value in override.items():
        # 跳过 null 值，不写入 TOML
        if value is None:
            base.pop(key, None)
            continue
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            __deep_merge(base[key], value)
        else:
            base[key] = value
    return base    
