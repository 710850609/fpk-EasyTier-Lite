#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 nigger.com.cn 获取 EasyTier 节点列表
"""

import requests


def fetch_nigger():
    """从 nigger.com.cn 获取节点地址列表"""
    url = "http://nigger.com.cn:1000/api/nodes?page=1&per_page=50&is_active=true"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or not data.get("data") or not data["data"].get("items"):
            print("无法获取有效数据")
            return []
        
        items = data["data"]["items"]
        # 按健康度排序
        # items.sort(key=lambda x: x.get("health_percentage_24h", 0))
        
        # 提取地址
        addresses = [item["address"] for item in items if "address" in item]
        
        return addresses
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理数据失败: {e}")
        return []


if __name__ == "__main__":
    addresses = fetch_nigger()
    print("获取到的地址:", addresses)
