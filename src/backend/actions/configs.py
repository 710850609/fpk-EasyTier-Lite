#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

import tomlkit

from http_dispatcher.dispatcher import HttpResponse

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

def need_setting(*kwargs):
    need_config = Path(ET_CONFIG_INIT_FILE).exists()
    return {"needConfig": need_config}

def save(data, *kwargs):    
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
    if not doc["network_identity"]:
        doc["network_identity"] = {"network_name": '', "network_secret": ''}
    __deep_merge(doc, data)
    # 头部注释
    with open(ET_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    Path(ET_CONFIG_INIT_FILE).unlink(missing_ok=True)


def save_toml(data: str, *kwargs):
    try:
        # 解析配置字符串
        doc = tomlkit.parse(data['toml'])
        with open(ET_CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(doc))
        Path(ET_CONFIG_INIT_FILE).unlink(missing_ok=True)
    except Exception as e:
        logging.error(f"解析配置字符串失败: {e}")
        raise e

def get(*kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
        return doc

def get_toml(*kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def download(*kwargs):    
    tmp_file = copy()
    logging.info(f"{tmp_file}")
    return HttpResponse(file=tmp_file, download_name="config.toml")

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
