#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 sbgov.cn 获取 EasyTier 节点列表（需要 cookie 验证）
"""

import requests
import re
import json
import re as re_module


def fetch_sbgov():
    """从 sbgov.cn 获取节点地址列表"""
    url = "http://www.sbgov.cn/api/v1/endpoints/statuses?page=1&pageSize=50"
    
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "host": "www.sbgov.cn",
        "pragma": "no-cache",
        "referer": "http://www.sbgov.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    }
    
    try:
        # 第一次请求获取 cookie
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # 提取 cookie
        cookie_match = re.search(r"document\.cookie = '([^']+)'", html)
        
        if cookie_match:
            cookie = cookie_match.group(1)
            print(f"获取到 cookie: {cookie}")
            
            # 解析 cookie 名称和值
            cookie_parts = cookie.split('=')
            if len(cookie_parts) >= 2:
                cookie_name = cookie_parts[0]
                cookie_value = '='.join(cookie_parts[1:])  # 处理值中可能有的等号
                session.cookies.set(cookie_name, cookie_value)
            
            # 第二次请求（会自动处理重定向）
            response2 = session.get(url, headers=headers, timeout=10)
            response2.raise_for_status()
            
            text = response2.text
            print(f"响应内容前200字符: {text[:200]}")
            
            # 检查是否还需要再次验证 cookie
            max_retries = 3
            for i in range(max_retries):
                cookie_match2 = re.search(r"document\.cookie = '([^']+)'", text)
                if not cookie_match2:
                    break
                    
                cookie2 = cookie_match2.group(1)
                print(f"第 {i+2} 次 cookie 验证: {cookie2[:50]}...")
                
                cookie_parts2 = cookie2.split('=')
                if len(cookie_parts2) >= 2:
                    session.cookies.set(cookie_parts2[0], '='.join(cookie_parts2[1:]))
                
                response_next = session.get(url, headers=headers, timeout=10)
                response_next.raise_for_status()
                text = response_next.text
                print(f"响应前200字符: {text[:200]}")
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"无法解析 JSON，响应内容: {text[:500]}")
                return []
        else:
            print("无法获取 cookie，尝试直接解析")
            try:
                data = json.loads(html)
            except json.JSONDecodeError:
                print("无法解析数据")
                return []
        
        # 提取 group = "αEasyTier公共服务器 点进看详情" 的所有元素
        if not isinstance(data, list):
            print("数据格式不正确")
            return []
        
        addresses = []
        for item in data:
            group = item.get("group", "")
            # 匹配 group 名称
            if "αEasyTier" not in group or "公共服务器" not in group:
                continue
            
            results = item.get("results", [])
            # 最少最近有3次检测健康
            if len(results) < 3:
                continue
            
            # 检查最近3次是否都成功
            if results[-1].get("success") and results[-2].get("success") and results[-3].get("success"):
                name = item.get("name", "")
                # 提取协议部分 tcp:// 或 udp://
                # 处理 "tcp或udp://host:port" 格式，拆分成两个 URI
                if "tcp或udp://" in name or "udp或tcp://" in name:
                    # 提取主机和端口
                    host_port_match = re_module.search(r'[或\|]?(tcp|udp)://([^:]+:\d+)', name)
                    if host_port_match:
                        host_port = host_port_match.group(2)
                        addresses.append(f"tcp://{host_port}")
                        addresses.append(f"udp://{host_port}")
                else:
                    # 使用正则表达式匹配 tcp:// 或 udp://
                    match = re_module.search(r'(tcp://[^\s]+|udp://[^\s]+)', name)
                    if match:
                        address = match.group(1)
                        addresses.append(address)
        
        print(f"排序后内容: {json.dumps(addresses, ensure_ascii=False)}")
        return addresses
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理数据失败: {e}")
        return []


if __name__ == "__main__":
    addresses = fetch_sbgov()
    print("获取到的地址:", addresses)
