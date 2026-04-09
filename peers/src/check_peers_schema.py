#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测 TCP/UDP 地址连通性
"""

import socket
import sys
import time
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import json

# 设置 Windows 终端 UTF-8 编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')


def test_tcp_connection(host: str, port: int, timeout: int = 3) -> dict:
    """测试 TCP 连接"""
    result = {"success": False, "latency": None, "error": None}
    
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # 尝试连接
        sock.connect((host, port))
        elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
        
        result["success"] = True
        result["latency"] = round(elapsed, 2)
        sock.close()
        
    except socket.timeout:
        result["error"] = "连接超时"
    except socket.gaierror:
        result["error"] = "无法解析主机名"
    except ConnectionRefusedError:
        result["error"] = "连接被拒绝"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def test_udp_connection(host: str, port: int, timeout: int = 3) -> dict:
    """测试 UDP 连接（UDP 是无连接的，只能测试是否能发送数据）"""
    result = {"success": False, "latency": None, "error": None}
    
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # 尝试解析主机名
        try:
            ip = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
        except socket.gaierror:
            result["error"] = "无法解析主机名"
            return result
        
        # 发送一个空数据包
        sock.sendto(b"", (ip, port))
        elapsed = (time.time() - start_time) * 1000
        
        # UDP 是无连接的，发送成功就认为"可用"
        result["success"] = True
        result["latency"] = round(elapsed, 2)
        sock.close()
        
    except socket.timeout:
        result["error"] = "发送超时"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def parse_peer_url(url: str) -> dict:
    """解析 peer URL"""
    # 处理 tcp://host:port 和 udp://host:port 格式
    match = re.match(r'^(tcp|udp)://([^:]+):(\d+)$', url.strip(), re.IGNORECASE)
    if match:
        return {
            "protocol": match.group(1).upper(),
            "host": match.group(2),
            "port": int(match.group(3)),
            "original": url.strip()
        }
    return None


def check_peer(peer_info: dict, timeout: int = 3) -> dict:
    """检测单个 peer"""
    protocol = peer_info["protocol"]
    host = peer_info["host"]
    port = peer_info["port"]
    
    if protocol == "TCP":
        result = test_tcp_connection(host, port, timeout)
    else:
        result = test_udp_connection(host, port, timeout)
    
    return {
        "address": peer_info["original"],
        "protocol": protocol,
        "host": host,
        "port": port,
        **result
    }


def main():
    peer_list_path = r"../peers/peer-list.txt"
    peer_meta_path = r"../peers/peer-meta.json"
    timeout = 3  # 超时时间（秒）
    max_workers = 10  # 并发线程数
    
    # 读取 peer 列表
    try:
        with open(peer_list_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {peer_list_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)
    
    # 解析所有 peer
    peers = []
    for line in lines:
        peer_info = parse_peer_url(line)
        if peer_info:
            peers.append(peer_info)
    
    if not peers:
        print("没有找到有效的 peer 地址")
        sys.exit(0)
    
    print("=" * 60)
    print("    EasyTier Peer 连通性检测结果")
    print("=" * 60)
    print()
    
    results = []
    
    # 并发检测
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_peer = {
            executor.submit(check_peer, peer, timeout): peer 
            for peer in peers
        }
        
        for future in as_completed(future_to_peer):
            result = future.result()
            results.append(result)
            
            address = result["address"]
            status_icon = "✓" if result["success"] else "✗"
            status_text = "连通" if result["success"] else "不通"
            
            if result["success"]:
                latency_str = f"({result['latency']}ms)"
                print(f"检测: {address:<45} {status_icon} {status_text} {latency_str}")
            else:
                error_str = f"[{result['error']}]" if result["error"] else ""
                print(f"检测: {address:<45} {status_icon} {status_text} {error_str}")
    
    # 统计结果
    connected = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print()
    print("=" * 60)
    print("统计:")
    print(f"  连通: {len(connected)} / {len(results)}")
    print(f"  不通: {len(failed)} / {len(results)}")
    print("=" * 60)
    
    # 输出可用的地址
    if connected:
        print()
        print("可用的地址列表:")
        available_peers = []
        indexs = { "tcp": 0, "udp": 0 }
        for r in sorted(connected, key=lambda x: x["latency"] if x["latency"] else float('inf')):
            latency_str = f" ({r['latency']}ms)" if r["latency"] else ""
            print(f"  {r['address']}{latency_str}")
            
            schema = r["protocol"].lower()
            indexs[schema] += 1
            # 使用相对路径，基于项目根目录
            file_path = f"/peers/{schema}-{indexs[schema]}.txt"
            file_relative_path = f"..{file_path}"
            os.makedirs(os.path.dirname(file_relative_path), exist_ok=True)

            with open(file_relative_path, 'w', encoding='utf-8') as f:
                f.write(r['address'])
            available_peers.append({ "url": r['address'], "txt": file_path })
        with open(peer_meta_path, 'w', encoding='utf-8') as f:
            json.dump(available_peers, f, ensure_ascii=False, indent=2)
    
    # 输出不可用的地址
    if failed:
        print()
        print("不可用的地址列表:")
        for r in failed:
            error_str = f" [{r['error']}]" if r["error"] else ""
            print(f"  {r['address']}{error_str}")


if __name__ == "__main__":
    main()
