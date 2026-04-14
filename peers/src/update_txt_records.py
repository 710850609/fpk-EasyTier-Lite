#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 dynv6 TXT 记录
使用 dynv6 REST API v2 管理 TXT 记录
"""

import json
import sys
import os
from pathlib import Path
import urllib.request
import urllib.error

# dynv6 API 配置
API_BASE = "https://dynv6.com/api/v2"
# 从环境变量获取 Token，如果没有则使用默认值（需要替换）
DYNV6_TOKEN = os.environ.get("DYNV6_TOKEN")
if not DYNV6_TOKEN and Path("DYNV6_TOKEN.txt").exists():
    print("环境变量未设置，尝试从 DYNV6_TOKEN.txt 读取 Token")
    DYNV6_TOKEN = Path("DYNV6_TOKEN.txt").read_text().strip()
if not DYNV6_TOKEN:
    print("错误: 请设置 DYNV6_TOKEN 环境变量或 DYNV6_TOKEN.txt 文件")
    sys.exit(1)


def api_request(method, endpoint, data=None):
    """发送 API 请求"""
    url = f"{API_BASE}{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {DYNV6_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if data:
            data_bytes = json.dumps(data).encode('utf-8')
        else:
            data_bytes = None
        
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers=headers,
            method=method
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return -1, str(e)


def get_zones():
    """获取所有 zones"""
    status, response = api_request("GET", "/zones")
    if status == 200:
        return json.loads(response)
    else:
        print(f"获取 zones 失败: {status} - {response}")
        return []


def get_records(zone_id):
    """获取 zone 下的所有记录"""
    status, response = api_request("GET", f"/zones/{zone_id}/records")
    if status == 200:
        return json.loads(response)
    else:
        print(f"获取 records 失败: {status} - {response}")
        return []


def find_zone_and_record(domain, zones):
    """查找域名对应的 zone 和记录"""
    # 从域名中提取可能的 zone
    parts = domain.replace('txt://', '').split('.')
    name = ".".join(parts[:len(parts)-3])
    for i in range(len(parts) - 1):
        possible_zone = '.'.join(parts[i:])
        
        # 在 zones 中查找
        for zone in zones:
            if zone.get('name') == possible_zone:
                zone_id = zone.get('id')
                records = get_records(zone_id)
                
                # 查找 TXT 记录
                for record in records:
                    if record.get('type') == 'TXT' and record.get('name') == name:
                        return zone_id, name, record
                
                return zone_id, name, None
    
    return None, None


def delete_txt_record(zone_id, record_id):
    """删除 TXT 记录"""
    status, response = api_request(
        "DELETE",
        f"/zones/{zone_id}/records/{record_id}"
    )
    
    if status in [200, 204]:
        return True
    else:
        print(f"  删除失败: {status} - {response}")
        return False


def add_txt_record(zone_id, name, value):
    """添加 TXT 记录"""
    data = {
        "name": name,
        "type": "TXT",
        "data": value,
        # "ttl": 60
    }
    
    status, response = api_request(
        "POST",
        f"/zones/{zone_id}/records",
        data
    )
    
    if status in [200, 201]:
        return True
    else:
        print(f"  添加失败: {status} - {response}")
        return False



def update_txt_record(zone_id, record_id, name, value):
    """添加 TXT 记录"""
    data = {
        "name": name,
        "type": "TXT",
        "data": value,
        # "ttl": 60
    }
    
    status, response = api_request(
        "PATCH",
        f"/zones/{zone_id}/records/{record_id}",
        data
    )
    
    if status in [200, 201]:
        return True
    else:
        print(f"  更新失败: {status} - {response}")
        return False


def process_peer(domain, peer_info, zones):
    """处理单个 peer 的 TXT 记录"""
    status = peer_info.get("status", 0)
    uri = peer_info.get("uri", "")
    
    print(f"处理: {domain} (status={status}, uri={uri})")
    
    # 查找 zone 和现有记录
    zone_id, name, existing_record = find_zone_and_record(domain, zones)
    
    if zone_id is None:
        print(f"  未找到对应的 zone，跳过")
        return False
    
    has_record = existing_record is not None
    has_txt = existing_record is not None and existing_record.get('data') == uri
    
    if status == 0:
        # status = 0: 如果有 TXT 记录则删除
        if has_txt:
            print(f"  存在 TXT 记录，准备删除...")
            if delete_txt_record(zone_id, existing_record.get('id')):
                print(f"  已删除 TXT 记录: {domain}")
                return True
            return False
        else:
            print(f"  无 TXT 记录，跳过")
            return True
            
    elif status == 1:
        # status = 1: 如果没有 TXT 记录则添加
        if has_txt:
            print(f"  已存在 TXT 记录，跳过")
            return True
        else:
            if uri:
                if not has_record:
                    print(f"  未匹配 TXT 记录，准备添加...")
                    if add_txt_record(zone_id, name, uri):
                        print(f"  已添加 TXT 记录: {domain} -> {uri}")
                        return True
                elif not has_txt:
                    print(f"  未匹配 TXT 记录，准备更新... {existing_record.get('data')}")
                    if update_txt_record(zone_id, existing_record.get('id'), name, uri):
                        print(f"  已更新 TXT 记录: {domain} -> {uri}")
                        return True
                return False
            else:
                print(f"  URI 为空，跳过")
                return False
    
    return False


def update():
    # 检查 Token
    if DYNV6_TOKEN == "your_token_here":
        print("错误: 请设置 DYNV6_TOKEN 环境变量")
        print("示例: export DYNV6_TOKEN=your_actual_token")
        sys.exit(1)
    
    # 读取 peer-txt-meta.json
    json_path = Path(__file__).parent.parent / "peer-txt-meta.json"
    
    if not json_path.exists():
        print(f"文件不存在: {json_path}")
        sys.exit(1)
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    peers = data.get("peers", {})
    
    print(f"共 {len(peers)} 个 peer 需要处理")
    print("=" * 60)
    
    # 获取所有 zones
    zones = get_zones()
    if not zones:
        print("获取 zones 失败，退出")
        sys.exit(1)
    
    print(f"找到 {len(zones)} 个 zones")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for domain, peer_info in peers.items():
        if process_peer(domain, peer_info, zones):
            success_count += 1
        else:
            fail_count += 1
        print()
    
    print("=" * 60)
    print(f"处理完成: 成功 {success_count}, 失败 {fail_count}")


if __name__ == "__main__":
    update()
