#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import util.http_util as http_util
import util.github_util as github_util
import requests
import logging
import tomlkit
import json
import os

TRIM_APPNAME = os.getenv('TRIM_APPNAME', 'EasyTier-Lite')
TRIM_APPDEST = os.getenv('TRIM_APPDEST', f'/var/apps/{TRIM_APPNAME}/target')
TRIM_PKGVAR = os.getenv('TRIM_PKGVAR', f'/var/apps/{TRIM_APPNAME}/var')
TRIM_SHARE_DIR = os.getenv('TRIM_SHARE_DIR', f'/var/apps/{TRIM_APPNAME}/shares/{TRIM_APPNAME}')

ET_CONFIG_FILE = f'{TRIM_SHARE_DIR}/config.toml'
ET_CONFIG_INIT_FILE = f'{TRIM_PKGVAR}/.init'
ET_PEER_META_FILE = f'{TRIM_PKGVAR}/peer-txt-meta.json'

CONFIG_COMMENTS = {
    'latency_first': '延迟优先模式，将尝试使用最低延迟路径转发流量，默认使用最短路径',
    'multi_thread': '使用多线程运行时，默认为单线程',
    "multi_thread_count": "使用的线程数，默认为2，仅在多线程模式下有效。取值必须大于2",
    'private_mode': '不允许使用了与本网络不相同的网络名称和密码的节点通过本节点进行握手或中转',
    'enable_kcp_proxy': '使用 KCP 代理 TCP 流，提高在 UDP 丢包网络上的延迟和吞吐量(KCP 代理会优先于 QUIC 代理生效)',
    'enable_quic_proxy': '使用 QUIC 代理 TCP 流，提高在 UDP 丢包网络上的延迟和吞吐量',
    'disable_kcp_input': '不允许其他节点使用 KCP 代理 TCP 流到此节点',
    'disable_quic_input': '不允许其他节点使用 QUIC 代理 TCP 流到此节点',
    'disable_tcp_hole_punching': '禁用TCP打洞功能',
    'disable_udp_hole_punching': '禁用UDP打洞功能',
    'disable_sym_hole_punching': '禁用基于生日攻击的对称NAT (NAT4) UDP 打洞功能，该打洞方式可能会被运营商封锁',
    'use_smoltcp': '为子网代理和 KCP 代理启用smoltcp堆栈',
    'proxy_forward_by_system': '通过系统内核转发子网代理数据包，禁用内置NAT',
    'p2p_only': '仅与已经建立P2P连接的对等节点通信',
    'disable_p2p': '禁用P2P通信，只通过--peers指定的节点转发数据包',
    'enable_exit_node': '允许此节点成为出口节点',
    'enable_encryption': '启用对等节点通信的加密，默认为false，必须与对等节点相同',
    "encryption_algorithm": '密支持：默认"aes-gcm"、"xor"、"chacha20"、"aes-gcm"、"aes-gcm-256"、"openssl-aes128-gcm"、"openssl-aes256-gcm"、"openssl-chacha20"',
    'enable_ipv6': '启用IPv6',
    'disable-ipv6': '不使用IPv6',
    'no_tun': '不创建TUN设备，可以使用子网代理访问节点 ',
    'accept_dns': '启用魔法DNS。使用魔法DNS，您可以使用域名访问其他节点，例如：<hostname>.et.net',
    "relay_all_peer_rpc": "转发所有对等节点的RPC数据包，即使对等节点不在转发网络白名单中。",
    "relay_network_whitelist": "仅转发白名单网络的流量，支持通配符字符串。多个网络名称间可以使用英文空格间隔。",
    "bind_device": "将连接器的套接字绑定到物理设备以避免路由问题",
    'user_stack': '使用用户态网络协议栈代替内核协议栈',
    "mtu": "TUN设备的MTU，默认为非加密时为1380，加密时为1360",
    "default_protocol": "连接到对等节点时使用的默认协议",
    "dev_name": "可自定义TUN接口名称",
    "hostname": "用于标识此设备的主机名",
    "rpc_portal": "用于管理的RPC门户地址",
}

def need_setting(*kwargs):
    need_config = Path(ET_CONFIG_INIT_FILE).exists()
    http_util.http_response_ok({"needConfig": need_config})

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
    http_util.http_response_ok('配置保存成功')

def save_with_comment(data, *kwargs):
    with open(ET_CONFIG_FILE, "r", encoding="utf-8") as f:
        src_doc = tomlkit.parse(f.read())
    if not src_doc["network_identity"]:
        src_doc["network_identity"] = {"network_name": '', "network_secret": ''}
    __deep_merge(src_doc, data)
    # 将原配置的所有内容复制到新文档
    doc = tomlkit.document()
    for key, value in src_doc.body:
        if key == "flags":
            flags_table = tomlkit.table()        
            for fKey, fValue in value.items():
                comment = __get_comment(fKey)                
                if comment and fValue:
                    flags_table.add(tomlkit.comment(comment))
                    pass
                flags_table.add(fKey, fValue)
            doc["flags"] = flags_table
        elif key is not None:
            logging.info(f"key: {key}   --其他-->  value: {value}")
            comment = __get_comment(key)                
            if comment and value:
                doc.add(tomlkit.comment(comment))
            doc.add(key, value)
    # 头部注释
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

    github_proxy = github_util.get_github_proxy();
    for key, item in peer_meta["peers"].items():
        peer = f"{key}"
        # 过滤未启用：空uri
        if peer not in config_peers_set and len(item.get('uri').strip()) > 0:
            peer_uris.append(peer)
    peers = []
    for uri in peer_uris:
        label = uri
        peers.append({'label': label, 'uri': uri})
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

def __get_comment(key):
    if key and key in CONFIG_COMMENTS and CONFIG_COMMENTS[key]:
        return CONFIG_COMMENTS[key]
    return None

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