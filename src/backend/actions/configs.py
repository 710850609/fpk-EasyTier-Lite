#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

import tomlkit

from http_dispatcher.dispatcher import HttpResponse
from utils import run_configs


def need_setting(*kwargs):
    flag_file = run_configs.et_init_flag_file()
    need_config = Path(flag_file).exists()
    return {"needConfig": need_config}

def save(data, *kwargs):
    et_config_file = run_configs.et_config_file()
    with open(et_config_file, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
    if not doc["network_identity"]:
        doc["network_identity"] = {"network_name": '', "network_secret": ''}
    __deep_merge(doc, data)
    # 头部注释
    with open(et_config_file, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    flag_file = run_configs.et_init_flag_file()
    Path(flag_file).unlink(missing_ok=True)


def save_toml(data: str, *kwargs):
    try:
        # 解析配置字符串
        doc = tomlkit.parse(data['toml'])
        et_config_file = run_configs.et_config_file()
        with open(et_config_file, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(doc))
        flag_file = run_configs.et_init_flag_file()
        Path(flag_file).unlink(missing_ok=True)
    except Exception as e:
        logging.error(f"解析配置字符串失败: {e}")
        raise e

def get(params, *kwargs):
    file_name = params.get('fileName') if params else None
    et_config_file = run_configs.et_config_file(file_name)
    with open(et_config_file, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())
        return doc

def get_toml(*kwargs):
    et_config_file = run_configs.et_config_file()
    with open(et_config_file, "r", encoding="utf-8") as f:
        return f.read()

def download(*kwargs):    
    tmp_file = copy()
    logging.info(f"{tmp_file}")
    return HttpResponse(file=tmp_file, download_name="config.toml")

def copy(*kwargs): 
    tmp_file = '/tmp/EasyTier-Lite/config-copy.toml'
    
    # 确保目录存在
    os.makedirs(os.path.dirname(tmp_file), exist_ok=True)

    et_config_file = run_configs.et_config_file()
    with open(et_config_file, "r", encoding="utf-8") as f:
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
